#!/usr/bin/env python3
"""Third-model adjudication for strongest LANG-WB machine linguistic flags.

Consumes the first-pass *_flags.csv files and evaluates only rows classified as
MEANINGFUL_DIFFERENCE_LIKELY. A separate multilingual instruction model decides
whether the candidate English is a valid meaning/translation of the source,
explicitly accounting for ambiguity, grammatical notes, idioms, and context.

Evidence only: this does not create native-speaker certification and does not
edit workbook content.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
LABELS = {"VALID", "CONCERN", "UNSURE"}
LANG_NAMES = {"arabic": "Arabic", "french": "French", "urdu": "Urdu"}


def batched(seq: Sequence, size: int) -> Iterable[Sequence]:
    for i in range(0, len(seq), size):
        yield seq[i:i+size]


def load_rows(root: Path) -> List[dict]:
    rows: List[dict] = []
    for language in ("arabic", "french", "urdu"):
        path = root / f"{language}_flags.csv"
        if not path.exists():
            raise FileNotFoundError(path)
        with path.open(encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                if row.get("machine_status") != "MEANINGFUL_DIFFERENCE_LIKELY":
                    continue
                row["language"] = language
                rows.append(row)
    return rows


def prompt_for(row: dict) -> str:
    language = LANG_NAMES[row["language"]]
    kind = row["kind"]
    return f"""You are a careful bilingual lexicography and translation adjudicator.
Language: {language}
Item type: {kind}
Source: {row['target']}
Candidate English: {row['english']}
Independent translation A: {row['marian_translation_en']}
Independent translation B: {row['m2m_translation_en']}

Question: Is the Candidate English a valid meaning or translation of the Source in at least one ordinary, pedagogically reasonable context?

Rules:
- Do NOT mark CONCERN just because another translation is more literal.
- For vocabulary, multiple senses, grammatical notes, gender/number/register notes, and context-dependent senses are allowed.
- For sentences, idiomatic English is allowed if meaning is preserved.
- Pronouns may be context-dependent (he/she/it/that) unless the source fixes the referent.
- Words can be genuinely ambiguous; a valid listed sense should be VALID even if the machine translators picked another sense.
- CONCERN only when the candidate is actually wrong or materially misleading for the source.
- UNSURE when the source is ambiguous enough that you cannot safely decide.

Return exactly one line in this format:
LABEL | short reason | corrected English if CONCERN, otherwise -
where LABEL is exactly VALID, CONCERN, or UNSURE."""


def parse_output(text: str) -> tuple[str, str, str]:
    line = " ".join((text or "").strip().splitlines()).strip()
    parts = [p.strip() for p in line.split("|", 2)]
    label = parts[0].upper() if parts else "UNSURE"
    if label not in LABELS:
        # Tolerate a short preamble while failing conservatively.
        first = next((x for x in LABELS if line.upper().startswith(x)), None)
        label = first or "UNSURE"
    reason = parts[1] if len(parts) > 1 else line
    correction = parts[2] if len(parts) > 2 else "-"
    return label, reason, correction


def run(root: Path, output_dir: Path, batch_size: int) -> int:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    rows = load_rows(root)
    if len(rows) != 180:
        raise RuntimeError(f"Expected 180 strongest first-pass flags, found {len(rows)}")

    print(f"Loading third adjudicator {MODEL}; rows={len(rows)}", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype="auto")
    model.eval()

    results: List[dict] = []
    with torch.inference_mode():
        for start in range(0, len(rows), batch_size):
            chunk = rows[start:start+batch_size]
            prompts = []
            for row in chunk:
                messages = [
                    {"role": "system", "content": "Be conservative, multilingual, concise, and follow the requested output label exactly."},
                    {"role": "user", "content": prompt_for(row)},
                ]
                prompts.append(tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True))
            enc = tokenizer(prompts, return_tensors="pt", padding=True, truncation=True, max_length=768)
            generated = model.generate(
                **enc,
                max_new_tokens=48,
                do_sample=False,
                num_beams=1,
                pad_token_id=tokenizer.eos_token_id,
            )
            new_tokens = generated[:, enc["input_ids"].shape[1]:]
            texts = tokenizer.batch_decode(new_tokens, skip_special_tokens=True)
            for row, text in zip(chunk, texts):
                label, reason, correction = parse_output(text)
                final_status = {
                    "VALID": "CLEARED_VALID_VARIANT",
                    "CONCERN": "POSSIBLE_CONTENT_ISSUE",
                    "UNSURE": "UNRESOLVED",
                }[label]
                results.append({
                    **row,
                    "third_model": MODEL,
                    "third_model_raw": text.strip(),
                    "third_model_label": label,
                    "third_model_reason": reason,
                    "third_model_proposed_correction": correction,
                    "adjudicated_status": final_status,
                })
            print(f"Adjudicated {min(start+batch_size, len(rows))}/{len(rows)}", flush=True)

    output_dir.mkdir(parents=True, exist_ok=True)
    fields = list(results[0].keys())
    with (output_dir / "strongest_flags_adjudicated.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(results)
    with (output_dir / "strongest_flags_adjudicated.jsonl").open("w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")

    per_lang: Dict[str, Dict[str, int]] = {}
    totals: Dict[str, int] = {}
    for r in results:
        lang = r["language"]
        status = r["adjudicated_status"]
        per_lang.setdefault(lang, {})[status] = per_lang.setdefault(lang, {}).get(status, 0) + 1
        totals[status] = totals.get(status, 0) + 1

    summary = {
        "schema": "lang-wb-free-linguistic-third-adjudication-v1",
        "source_first_pass_rows": 6000,
        "strongest_flags_received": len(rows),
        "third_model": MODEL,
        "status_counts": totals,
        "per_language": per_lang,
        "possible_content_issue_rows": [
            {k: r[k] for k in (
                "language", "kind", "rank", "target", "english",
                "marian_translation_en", "m2m_translation_en",
                "third_model_reason", "third_model_proposed_correction"
            )}
            for r in results if r["adjudicated_status"] == "POSSIBLE_CONTENT_ISSUE"
        ],
        "unresolved_rows": [
            {k: r[k] for k in (
                "language", "kind", "rank", "target", "english", "third_model_reason"
            )}
            for r in results if r["adjudicated_status"] == "UNRESOLVED"
        ],
        "important_boundary": "Third-model machine adjudication only; no automatic workbook edits and no native-speaker certification.",
    }
    (output_dir / "third_adjudication_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--first-pass-dir", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--batch-size", type=int, default=6)
    args = p.parse_args()
    return run(args.first_pass_dir, args.output_dir, args.batch_size)

if __name__ == "__main__":
    raise SystemExit(main())
