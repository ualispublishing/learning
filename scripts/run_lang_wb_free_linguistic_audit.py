#!/usr/bin/env python3
"""Free, credential-free linguistic verification for LANG-WB v1.0.

This script audits the exact candidate CSVs bound to a Git commit using two
independent open translation model families (Marian/OPUS-MT and M2M100), then
uses an English NLI cross-encoder to determine whether translation differences
are likely meaningful or merely paraphrastic/model variance.

It does NOT create human/native-speaker certification. It produces an
exception queue that can sharply reduce the amount of manual linguistic review.
"""

from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Dict, Iterable, List, Sequence, Tuple

CANDIDATE_COMMIT = "aa9b5d465839edb2ce520133a01d78ed40634c96"
LANGUAGE_CONFIG = {
    "arabic": {
        "marian": "Helsinki-NLP/opus-mt-ar-en",
        "m2m_src": "ar",
    },
    "french": {
        "marian": "Helsinki-NLP/opus-mt-fr-en",
        "m2m_src": "fr",
    },
    "urdu": {
        "marian": "Helsinki-NLP/opus-mt-ur-en",
        "m2m_src": "ur",
    },
}
M2M_MODEL = "facebook/m2m100_418M"
NLI_MODEL = "cross-encoder/nli-MiniLM2-L6-H768"


def git_show_text(commit: str, path: str) -> str:
    proc = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"Could not read {path} from {commit}: {proc.stderr.decode('utf-8', 'replace')}"
        )
    return proc.stdout.decode("utf-8-sig")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_candidate_rows(language: str, commit: str) -> Tuple[List[dict], Dict[str, str]]:
    root = f"completed/languages/workbooks/v1.0/{language}"
    paths = {
        "vocabulary": f"{root}/{language}_vocabulary_1000.csv",
        "sentence": f"{root}/{language}_sentence_bank_1000.csv",
    }
    rows: List[dict] = []
    hashes: Dict[str, str] = {}
    for kind, path in paths.items():
        text = git_show_text(commit, path)
        hashes[path] = sha256_text(text)
        reader = csv.DictReader(io.StringIO(text))
        part = list(reader)
        if len(part) != 1000:
            raise RuntimeError(f"Expected 1000 {kind} rows in {path}, got {len(part)}")
        for row in part:
            rank = int(row["rank"])
            target = (row.get("target") or "").strip()
            english = (row.get("english") or "").strip()
            if not target or not english:
                raise RuntimeError(f"Blank target/english at {language} {kind} rank {rank}")
            rows.append(
                {
                    "language": language,
                    "kind": kind,
                    "rank": rank,
                    "target": target,
                    "english": english,
                    "level": (row.get("level") or "").strip(),
                    "part_of_speech": (row.get("part_of_speech") or "").strip(),
                    "attribution": (row.get("attribution") or "").strip(),
                }
            )
    return rows, hashes


def batched(seq: Sequence[str], size: int) -> Iterable[Sequence[str]]:
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def translate_marian(texts: Sequence[str], model_name: str, batch_size: int) -> List[str]:
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    print(f"Loading Marian model {model_name}", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    model.eval()
    out: List[str] = []
    with torch.inference_mode():
        for n, batch in enumerate(batched(texts, batch_size), start=1):
            encoded = tokenizer(
                list(batch), return_tensors="pt", padding=True, truncation=True, max_length=256
            )
            generated = model.generate(
                **encoded,
                max_new_tokens=96,
                num_beams=1,
                do_sample=False,
            )
            out.extend(tokenizer.batch_decode(generated, skip_special_tokens=True))
            if n % 10 == 0:
                print(f"  Marian translated {min(n * batch_size, len(texts))}/{len(texts)}", flush=True)
    del model, tokenizer
    gc.collect()
    return [x.strip() for x in out]


def translate_m2m(texts: Sequence[str], src_lang: str, batch_size: int) -> List[str]:
    import torch
    from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

    print(f"Loading M2M100 model {M2M_MODEL} for {src_lang}->en", flush=True)
    tokenizer = M2M100Tokenizer.from_pretrained(M2M_MODEL)
    tokenizer.src_lang = src_lang
    model = M2M100ForConditionalGeneration.from_pretrained(M2M_MODEL)
    model.eval()
    out: List[str] = []
    forced = tokenizer.get_lang_id("en")
    with torch.inference_mode():
        for n, batch in enumerate(batched(texts, batch_size), start=1):
            encoded = tokenizer(
                list(batch), return_tensors="pt", padding=True, truncation=True, max_length=256
            )
            generated = model.generate(
                **encoded,
                forced_bos_token_id=forced,
                max_new_tokens=96,
                num_beams=1,
                do_sample=False,
            )
            out.extend(tokenizer.batch_decode(generated, skip_special_tokens=True))
            if n % 10 == 0:
                print(f"  M2M100 translated {min(n * batch_size, len(texts))}/{len(texts)}", flush=True)
    del model, tokenizer
    gc.collect()
    return [x.strip() for x in out]


def english_alternatives(text: str, kind: str) -> List[str]:
    # Vocabulary fields intentionally contain semicolon-separated valid senses.
    # Sentence translations are kept intact.
    if kind != "vocabulary":
        return [text.strip()]
    parts = [p.strip() for p in text.split(";") if p.strip()]
    return parts or [text.strip()]


def nli_equivalence_scores(
    rows: Sequence[dict], marian: Sequence[str], m2m: Sequence[str], batch_size: int
) -> Tuple[List[float], List[float], List[float]]:
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    print(f"Loading NLI adjudicator {NLI_MODEL}", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(NLI_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(NLI_MODEL)
    model.eval()

    # Every candidate/translation comparison is scored in both directions.
    pairs: List[Tuple[str, str]] = []
    meta: List[Tuple[str, int, int, int]] = []
    # meta = (source_model, row_index, alt_index, direction)
    for idx, row in enumerate(rows):
        alts = english_alternatives(row["english"], row["kind"])
        for source_model, translation in (("marian", marian[idx]), ("m2m", m2m[idx])):
            for alt_idx, alt in enumerate(alts):
                pairs.append((alt, translation))
                meta.append((source_model, idx, alt_idx, 0))
                pairs.append((translation, alt))
                meta.append((source_model, idx, alt_idx, 1))
        # Inter-model agreement is also symmetric.
        pairs.append((marian[idx], m2m[idx]))
        meta.append(("models", idx, 0, 0))
        pairs.append((m2m[idx], marian[idx]))
        meta.append(("models", idx, 0, 1))

    entail_probs: List[float] = []
    with torch.inference_mode():
        for start in range(0, len(pairs), batch_size):
            chunk = pairs[start : start + batch_size]
            encoded = tokenizer(
                [p for p, _ in chunk],
                [h for _, h in chunk],
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=256,
            )
            logits = model(**encoded).logits
            probs = torch.softmax(logits, dim=-1)[:, 1]  # config label 1 = entailment
            entail_probs.extend(float(x) for x in probs.cpu())
            if (start // batch_size + 1) % 25 == 0:
                print(f"  NLI scored {min(start + batch_size, len(pairs))}/{len(pairs)} pairs", flush=True)

    per_model: Dict[Tuple[str, int, int], Dict[int, float]] = {}
    for m, prob in zip(meta, entail_probs):
        source_model, row_idx, alt_idx, direction = m
        per_model.setdefault((source_model, row_idx, alt_idx), {})[direction] = prob

    def symmetric(source_model: str, row_idx: int, alt_idx: int = 0) -> float:
        d = per_model[(source_model, row_idx, alt_idx)]
        return min(d.get(0, 0.0), d.get(1, 0.0))

    marian_scores: List[float] = []
    m2m_scores: List[float] = []
    model_scores: List[float] = []
    for idx, row in enumerate(rows):
        alt_count = len(english_alternatives(row["english"], row["kind"]))
        marian_scores.append(max(symmetric("marian", idx, a) for a in range(alt_count)))
        m2m_scores.append(max(symmetric("m2m", idx, a) for a in range(alt_count)))
        model_scores.append(symmetric("models", idx, 0))

    del model, tokenizer
    gc.collect()
    return marian_scores, m2m_scores, model_scores


def classify(eq_a: float, eq_b: float, eq_models: float) -> Tuple[str, str]:
    # High bidirectional entailment from both independent translators is the
    # strongest machine-verification state.
    if eq_a >= 0.75 and eq_b >= 0.75:
        return "CONFIRMED_EQUIVALENT", "Both independent translations bidirectionally entail a listed candidate meaning."
    # One translator may choose a different idiom/sense. If models broadly agree
    # and at least one strongly matches the candidate, this is usually variance.
    if max(eq_a, eq_b) >= 0.75 and eq_models >= 0.65 and min(eq_a, eq_b) >= 0.40:
        return "MINOR_OR_MODEL_VARIANCE", "At least one translation strongly matches; remaining difference is likely paraphrase/model variance."
    # If both independent translators agree with each other but neither entails
    # the candidate, that is the strongest automatic defect signal.
    if eq_a < 0.45 and eq_b < 0.45 and eq_models >= 0.65:
        return "MEANINGFUL_DIFFERENCE_LIKELY", "Independent translators agree with each other but not with the candidate English meaning."
    if eq_models < 0.40:
        return "MODEL_DISAGREEMENT", "The independent translation models disagree; do not treat this as a workbook defect without review."
    return "NEEDS_ADJUDICATION", "Machine evidence is mixed; inspect this row before changing the workbook."


def audit_language(language: str, commit: str, output_dir: Path, batch_size: int, limit: int) -> int:
    if language not in LANGUAGE_CONFIG:
        raise ValueError(language)
    rows, source_hashes = read_candidate_rows(language, commit)
    if limit:
        # Balanced smoke/debug limit: first N from each kind.
        rows = [r for r in rows if r["rank"] <= limit]
    texts = [r["target"] for r in rows]
    cfg = LANGUAGE_CONFIG[language]

    marian = translate_marian(texts, cfg["marian"], batch_size)
    m2m = translate_m2m(texts, cfg["m2m_src"], batch_size)
    if len(marian) != len(rows) or len(m2m) != len(rows):
        raise RuntimeError("Translation output length mismatch")

    nli_batch = max(16, batch_size * 2)
    eq_a, eq_b, eq_models = nli_equivalence_scores(rows, marian, m2m, nli_batch)

    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / f"{language}_free_linguistic_audit.jsonl"
    flags_path = output_dir / f"{language}_flags.csv"
    results: List[dict] = []
    counts: Dict[str, int] = {}

    with jsonl_path.open("w", encoding="utf-8") as jf:
        for i, row in enumerate(rows):
            status, rationale = classify(eq_a[i], eq_b[i], eq_models[i])
            counts[status] = counts.get(status, 0) + 1
            rec = {
                **row,
                "candidate_commit": commit,
                "marian_model": cfg["marian"],
                "marian_translation_en": marian[i],
                "m2m_model": M2M_MODEL,
                "m2m_translation_en": m2m[i],
                "candidate_vs_marian_bidirectional_entailment": round(eq_a[i], 6),
                "candidate_vs_m2m_bidirectional_entailment": round(eq_b[i], 6),
                "translator_interagreement_bidirectional_entailment": round(eq_models[i], 6),
                "machine_status": status,
                "machine_rationale": rationale,
            }
            results.append(rec)
            jf.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")

    flagged_statuses = {"MEANINGFUL_DIFFERENCE_LIKELY", "MODEL_DISAGREEMENT", "NEEDS_ADJUDICATION"}
    with flags_path.open("w", encoding="utf-8", newline="") as f:
        fields = [
            "language", "kind", "rank", "target", "english", "machine_status",
            "marian_translation_en", "m2m_translation_en",
            "candidate_vs_marian_bidirectional_entailment",
            "candidate_vs_m2m_bidirectional_entailment",
            "translator_interagreement_bidirectional_entailment",
            "machine_rationale",
        ]
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for rec in results:
            if rec["machine_status"] in flagged_statuses:
                writer.writerow(rec)

    summary = {
        "schema": "lang-wb-free-linguistic-audit-v1",
        "language": language,
        "candidate_commit": commit,
        "source_sha256": source_hashes,
        "models": {
            "translator_1": cfg["marian"],
            "translator_2": M2M_MODEL,
            "adjudicator": NLI_MODEL,
        },
        "rows_checked": len(rows),
        "expected_full_rows": 2000,
        "is_full_run": len(rows) == 2000,
        "status_counts": counts,
        "flagged_for_manual_or_llm_review": sum(counts.get(x, 0) for x in flagged_statuses),
        "important_boundary": (
            "This is full-corpus machine verification/triage, not native-speaker certification. "
            "Do not auto-edit candidate content solely from a model flag."
        ),
        "outputs": {
            "jsonl": jsonl_path.name,
            "flags_csv": flags_path.name,
        },
    }
    summary_path = output_dir / f"{language}_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    return 0


def aggregate(aggregate_dir: Path, output: Path) -> int:
    summaries = []
    for path in sorted(aggregate_dir.rglob("*_summary.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if data.get("schema") == "lang-wb-free-linguistic-audit-v1":
            summaries.append(data)
    by_language = {x["language"]: x for x in summaries}
    missing = sorted(set(LANGUAGE_CONFIG) - set(by_language))
    status_counts: Dict[str, int] = {}
    rows_checked = 0
    flagged = 0
    for x in summaries:
        rows_checked += int(x.get("rows_checked", 0))
        flagged += int(x.get("flagged_for_manual_or_llm_review", 0))
        for k, v in x.get("status_counts", {}).items():
            status_counts[k] = status_counts.get(k, 0) + int(v)
    result = {
        "schema": "lang-wb-free-linguistic-audit-aggregate-v1",
        "candidate_commit": CANDIDATE_COMMIT,
        "languages_present": sorted(by_language),
        "missing_languages": missing,
        "rows_checked": rows_checked,
        "expected_full_rows": 6000,
        "full_corpus_complete": rows_checked == 6000 and not missing,
        "status_counts": status_counts,
        "flagged_for_manual_or_llm_review": flagged,
        "language_summaries": by_language,
        "release_effect": "Evidence only. Does not create or imply human/native-speaker PASS.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return 0 if result["full_corpus_complete"] else 2


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--language", choices=sorted(LANGUAGE_CONFIG))
    p.add_argument("--candidate-commit", default=CANDIDATE_COMMIT)
    p.add_argument("--output-dir", type=Path, default=Path("audit/lang-wb-free-linguistic-audit"))
    p.add_argument("--batch-size", type=int, default=24)
    p.add_argument("--limit", type=int, default=0, help="Debug only: first N ranks of each kind")
    p.add_argument("--aggregate-dir", type=Path)
    p.add_argument("--aggregate-output", type=Path, default=Path("aggregate_summary.json"))
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.aggregate_dir:
        return aggregate(args.aggregate_dir, args.aggregate_output)
    if not args.language:
        print("--language is required unless --aggregate-dir is used", file=sys.stderr)
        return 2
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    return audit_language(args.language, args.candidate_commit, args.output_dir, args.batch_size, args.limit)


if __name__ == "__main__":
    raise SystemExit(main())
