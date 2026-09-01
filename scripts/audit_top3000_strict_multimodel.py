#!/usr/bin/env python3
"""Strict learner-facing audit for the legacy rank-1001..3000 vocabulary continuations.

The root ``*_top3000.csv`` files are legacy continuation decks: each contains
2,000 cards for ranks 1001..3000, while ``*_top1000.csv`` contains ranks
1..1000.  This audit intentionally does not trust historical "verified" text
inside card metadata as evidence of correctness.

For every continuation card it:
- validates structure/rank/uniqueness and exact expected input blob identity;
- extracts the learner-facing Meaning field;
- independently translates the headword to English with Marian/OPUS-MT and
  M2M100;
- compares candidate meanings against both translations in both directions
  with an English NLI model;
- separately flags learner-unfriendly dictionary dumps, rare/offensive senses,
  and excessively broad glosses;
- emits a complete machine-readable audit and explicit review queue.

No card is rewritten by this program.  A model flag is triage evidence, not an
edit authorization or native-speaker certification.
"""
from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]

SOURCE_CONFIG = {
    "arabic": {
        "path": "arabic_top3000.csv",
        "expected_blob": "f6c110b34b6ed9a441798f6bbdf82a377e35018a",
        "marian": "Helsinki-NLP/opus-mt-ar-en",
        "m2m_src": "ar",
    },
    "french": {
        "path": "french_top3000.csv",
        "expected_blob": "ba7db6ffba39d6bed3e5862ac2142d8a45fb25cd",
        "marian": "Helsinki-NLP/opus-mt-fr-en",
        "m2m_src": "fr",
    },
    "urdu": {
        "path": "urdu_top3000.csv",
        "expected_blob": "cd63bc1f8211bb077369d59b934abb09888cd498",
        "marian": "Helsinki-NLP/opus-mt-ur-en",
        "m2m_src": "ur",
    },
}
M2M_MODEL = "facebook/m2m100_418M"
NLI_MODEL = "cross-encoder/nli-MiniLM2-L6-H768"
RANK_RE = re.compile(r"(?m)^Rank:\s*(\d+)\s*$")
MEANING_RE = re.compile(r"(?m)^Meaning:\s*(.+?)\s*$")
POS_RE = re.compile(r"(?m)^Part of speech:\s*(.+?)\s*$")
ROOT_RE = re.compile(r"(?m)^Root:\s*(.+?)\s*$")

# These do not automatically make a definition wrong.  They signal that a raw
# dictionary sense inventory may have leaked into a learner flashcard.
DICTIONARY_DUMP_RE = re.compile(
    r"\b(?:ellipsis of|contraction of|obsolete|archaic|dated|rare|historical|"
    r"taxonomic|genus|species|chiefly|slang|vulgar|offensive|derogatory)\b",
    re.I,
)
OFFENSIVE_RE = re.compile(
    r"\b(?:faggot|fag\b|poof\b|retard(?:ed)?\b|nigger\b|chink\b|spic\b)\b",
    re.I,
)


def git_blob(path: str) -> str:
    proc = subprocess.run(
        ["git", "rev-parse", f"HEAD:{path}"], capture_output=True, text=True, check=False
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Could not resolve git blob for {path}: {proc.stderr.strip()}")
    return proc.stdout.strip()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_rows(language: str) -> Tuple[List[dict], dict]:
    cfg = SOURCE_CONFIG[language]
    rel = cfg["path"]
    path = ROOT / rel
    actual_blob = git_blob(rel)
    if actual_blob != cfg["expected_blob"]:
        raise RuntimeError(
            f"{language}: source blob changed; expected {cfg['expected_blob']} got {actual_blob}. "
            "Rebind the audit deliberately instead of silently auditing a moving target."
        )

    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != ["Front", "Back"]:
            raise RuntimeError(f"{language}: expected Front,Back schema, got {reader.fieldnames}")
        raw = list(reader)

    if len(raw) != 2000:
        raise RuntimeError(f"{language}: expected 2000 continuation cards, got {len(raw)}")

    seen = set()
    rows: List[dict] = []
    for expected_rank, card in enumerate(raw, 1001):
        front = (card.get("Front") or "").strip()
        back = card.get("Back") or ""
        rm = RANK_RE.search(back)
        mm = MEANING_RE.search(back)
        pm = POS_RE.search(back)
        rootm = ROOT_RE.search(back)
        if not front:
            raise RuntimeError(f"{language}: blank Front at expected rank {expected_rank}")
        if front in seen:
            raise RuntimeError(f"{language}: duplicate Front {front!r} at rank {expected_rank}")
        seen.add(front)
        if rm is None or int(rm.group(1)) != expected_rank:
            raise RuntimeError(
                f"{language}: rank mismatch at row {expected_rank}; parsed={rm.group(1) if rm else None}"
            )
        if mm is None or not mm.group(1).strip():
            raise RuntimeError(f"{language}: missing Meaning at rank {expected_rank}")

        meaning = mm.group(1).strip()
        parts = [x.strip() for x in meaning.split(";") if x.strip()]
        learner_flags: List[str] = []
        if OFFENSIVE_RE.search(meaning):
            learner_flags.append("offensive_or_slur_sense")
        if DICTIONARY_DUMP_RE.search(meaning):
            learner_flags.append("lexicographic_or_rare_sense_marker")
        if len(parts) > 4:
            learner_flags.append("too_many_semicolon_senses")
        if len(meaning) > 180:
            learner_flags.append("overlong_gloss")
        if meaning.count("(") >= 4:
            learner_flags.append("parenthetical_dictionary_dump")

        rows.append(
            {
                "language": language,
                "rank": expected_rank,
                "target": front,
                "english": meaning,
                "part_of_speech": pm.group(1).strip() if pm else "",
                "root": rootm.group(1).strip() if rootm else "",
                "learner_flags": learner_flags,
            }
        )

    return rows, {
        "path": rel,
        "git_blob": actual_blob,
        "sha256": sha256_file(path),
        "rows": len(rows),
        "rank_range": [1001, 3000],
    }


def batched(seq: Sequence[str], size: int) -> Iterable[Sequence[str]]:
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def translate_marian(texts: Sequence[str], model_name: str, batch_size: int) -> List[str]:
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    print(f"Loading Marian {model_name}", flush=True)
    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    model.eval()
    out: List[str] = []
    with torch.inference_mode():
        for n, batch in enumerate(batched(texts, batch_size), 1):
            enc = tok(list(batch), return_tensors="pt", padding=True, truncation=True, max_length=96)
            gen = model.generate(**enc, max_new_tokens=48, num_beams=1, do_sample=False)
            out.extend(tok.batch_decode(gen, skip_special_tokens=True))
            if n % 10 == 0:
                print(f"  Marian {min(n * batch_size, len(texts))}/{len(texts)}", flush=True)
    del model, tok
    gc.collect()
    return [x.strip() for x in out]


def translate_m2m(texts: Sequence[str], src_lang: str, batch_size: int) -> List[str]:
    import torch
    from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

    print(f"Loading M2M100 for {src_lang}->en", flush=True)
    tok = M2M100Tokenizer.from_pretrained(M2M_MODEL)
    tok.src_lang = src_lang
    model = M2M100ForConditionalGeneration.from_pretrained(M2M_MODEL)
    model.eval()
    forced = tok.get_lang_id("en")
    out: List[str] = []
    with torch.inference_mode():
        for n, batch in enumerate(batched(texts, batch_size), 1):
            enc = tok(list(batch), return_tensors="pt", padding=True, truncation=True, max_length=96)
            gen = model.generate(
                **enc, forced_bos_token_id=forced, max_new_tokens=48, num_beams=1, do_sample=False
            )
            out.extend(tok.batch_decode(gen, skip_special_tokens=True))
            if n % 10 == 0:
                print(f"  M2M100 {min(n * batch_size, len(texts))}/{len(texts)}", flush=True)
    del model, tok
    gc.collect()
    return [x.strip() for x in out]


def meaning_alternatives(text: str) -> List[str]:
    # Each semicolon-separated learner sense gets a fair independent comparison.
    # Cap pathological dictionary dumps so one card cannot dominate NLI runtime.
    parts = [x.strip() for x in text.split(";") if x.strip()]
    alts: List[str] = []
    for x in [text.strip(), *parts[:8]]:
        if x and x not in alts:
            alts.append(x)
    return alts


def nli_scores(rows: Sequence[dict], a: Sequence[str], b: Sequence[str], batch_size: int):
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    print(f"Loading NLI {NLI_MODEL}", flush=True)
    tok = AutoTokenizer.from_pretrained(NLI_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(NLI_MODEL)
    model.eval()

    pairs: List[Tuple[str, str]] = []
    meta: List[Tuple[str, int, int, int]] = []
    for idx, row in enumerate(rows):
        alts = meaning_alternatives(row["english"])
        for source, trans in (("a", a[idx]), ("b", b[idx])):
            for alt_idx, alt in enumerate(alts):
                pairs.append((alt, trans)); meta.append((source, idx, alt_idx, 0))
                pairs.append((trans, alt)); meta.append((source, idx, alt_idx, 1))
        pairs.append((a[idx], b[idx])); meta.append(("models", idx, 0, 0))
        pairs.append((b[idx], a[idx])); meta.append(("models", idx, 0, 1))

    probs: List[float] = []
    with torch.inference_mode():
        for start in range(0, len(pairs), batch_size):
            chunk = pairs[start : start + batch_size]
            enc = tok(
                [p for p, _ in chunk], [h for _, h in chunk],
                return_tensors="pt", padding=True, truncation=True, max_length=192,
            )
            logits = model(**enc).logits
            # This cross-encoder's config uses label 1 for entailment, matching the
            # already validated LANG-WB audit implementation.
            ps = torch.softmax(logits, dim=-1)[:, 1]
            probs.extend(float(x) for x in ps.cpu())
            if (start // batch_size + 1) % 25 == 0:
                print(f"  NLI {min(start + batch_size, len(pairs))}/{len(pairs)}", flush=True)

    lookup: Dict[Tuple[str, int, int], Dict[int, float]] = {}
    for m, p in zip(meta, probs):
        source, idx, alt_idx, direction = m
        lookup.setdefault((source, idx, alt_idx), {})[direction] = p

    def sym(source: str, idx: int, alt_idx: int = 0) -> float:
        d = lookup[(source, idx, alt_idx)]
        return min(d.get(0, 0.0), d.get(1, 0.0))

    sa: List[float] = []
    sb: List[float] = []
    sm: List[float] = []
    for idx, row in enumerate(rows):
        n = len(meaning_alternatives(row["english"]))
        sa.append(max(sym("a", idx, j) for j in range(n)))
        sb.append(max(sym("b", idx, j) for j in range(n)))
        sm.append(sym("models", idx))

    del model, tok
    gc.collect()
    return sa, sb, sm


def semantic_status(sa: float, sb: float, sm: float) -> Tuple[str, str]:
    if sa >= 0.75 and sb >= 0.75:
        return "CONFIRMED_EQUIVALENT", "Both independent translations strongly match a candidate sense."
    if max(sa, sb) >= 0.75 and sm >= 0.65 and min(sa, sb) >= 0.40:
        return "MINOR_OR_MODEL_VARIANCE", "At least one strong candidate match and broad translator agreement."
    if sa < 0.45 and sb < 0.45 and sm >= 0.65:
        return "MEANINGFUL_DIFFERENCE_LIKELY", "Translators agree with each other but not with the listed meaning."
    if sm < 0.40:
        return "MODEL_DISAGREEMENT", "Translation models disagree; do not edit without adjudication."
    return "NEEDS_ADJUDICATION", "Mixed semantic evidence; explicit adjudication required."


def audit(language: str, output_dir: Path, batch_size: int, limit: int) -> None:
    cfg = SOURCE_CONFIG[language]
    rows, source = read_rows(language)
    if limit:
        rows = rows[:limit]
    texts = [r["target"] for r in rows]

    a = translate_marian(texts, cfg["marian"], batch_size)
    b = translate_m2m(texts, cfg["m2m_src"], batch_size)
    if len(a) != len(rows) or len(b) != len(rows):
        raise RuntimeError("translation output length mismatch")
    sa, sb, sm = nli_scores(rows, a, b, max(24, batch_size * 2))

    output_dir.mkdir(parents=True, exist_ok=True)
    results: List[dict] = []
    status_counts: Dict[str, int] = {}
    learner_flag_counts: Dict[str, int] = {}
    for i, row in enumerate(rows):
        status, rationale = semantic_status(sa[i], sb[i], sm[i])
        status_counts[status] = status_counts.get(status, 0) + 1
        for flag in row["learner_flags"]:
            learner_flag_counts[flag] = learner_flag_counts.get(flag, 0) + 1
        rec = {
            **row,
            "source_git_blob": source["git_blob"],
            "marian_model": cfg["marian"],
            "marian_translation_en": a[i],
            "m2m_model": M2M_MODEL,
            "m2m_translation_en": b[i],
            "candidate_vs_marian_bidirectional_entailment": round(sa[i], 6),
            "candidate_vs_m2m_bidirectional_entailment": round(sb[i], 6),
            "translator_interagreement_bidirectional_entailment": round(sm[i], 6),
            "machine_status": status,
            "machine_rationale": rationale,
        }
        results.append(rec)

    jsonl = output_dir / f"{language}_top3000_strict_audit.jsonl"
    with jsonl.open("w", encoding="utf-8") as f:
        for rec in results:
            f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")

    review_status = {"MEANINGFUL_DIFFERENCE_LIKELY", "MODEL_DISAGREEMENT", "NEEDS_ADJUDICATION"}
    queue = [r for r in results if r["machine_status"] in review_status or r["learner_flags"]]
    # Strongest machine mismatches first, then learner-gloss risks, then mixed/model-disagreement rows.
    order = {"MEANINGFUL_DIFFERENCE_LIKELY": 0, "NEEDS_ADJUDICATION": 1, "MODEL_DISAGREEMENT": 2,
             "MINOR_OR_MODEL_VARIANCE": 3, "CONFIRMED_EQUIVALENT": 4}
    queue.sort(key=lambda r: (order.get(r["machine_status"], 9), -len(r["learner_flags"]), r["rank"]))

    queue_path = output_dir / f"{language}_top3000_review_queue.csv"
    fields = [
        "language", "rank", "target", "english", "part_of_speech", "root",
        "machine_status", "learner_flags", "marian_translation_en", "m2m_translation_en",
        "candidate_vs_marian_bidirectional_entailment",
        "candidate_vs_m2m_bidirectional_entailment",
        "translator_interagreement_bidirectional_entailment", "machine_rationale",
    ]
    with queue_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for rec in queue:
            row = dict(rec)
            row["learner_flags"] = "|".join(rec["learner_flags"])
            w.writerow(row)

    strong = [r for r in results if r["machine_status"] == "MEANINGFUL_DIFFERENCE_LIKELY"]
    summary = {
        "schema": "top3000-strict-multimodel-audit-v1",
        "language": language,
        "source": source,
        "rows_checked": len(rows),
        "expected_full_rows": 2000,
        "is_full_run": len(rows) == 2000,
        "models": {"translator_1": cfg["marian"], "translator_2": M2M_MODEL, "nli": NLI_MODEL},
        "machine_status_counts": dict(sorted(status_counts.items())),
        "learner_flag_counts": dict(sorted(learner_flag_counts.items())),
        "review_queue_rows": len(queue),
        "strong_machine_mismatch_rows": len(strong),
        "safe_auto_corrections": 0,
        "boundary": (
            "This is exhaustive machine triage over the continuation rows. It is not native-speaker certification, "
            "and no row may be rewritten solely from one model result."
        ),
        "outputs": {"full_jsonl": jsonl.name, "review_queue_csv": queue_path.name},
    }
    (output_dir / f"{language}_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)


def aggregate(directory: Path, output: Path) -> None:
    summaries = []
    for p in sorted(directory.rglob("*_summary.json")):
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if obj.get("schema") == "top3000-strict-multimodel-audit-v1":
            summaries.append(obj)
    if len(summaries) != 3:
        raise RuntimeError(f"Expected 3 language summaries, found {len(summaries)}")
    aggregate_obj = {
        "schema": "top3000-strict-multimodel-audit-aggregate-v1",
        "languages": {x["language"]: x for x in summaries},
        "rows_checked": sum(x["rows_checked"] for x in summaries),
        "review_queue_rows": sum(x["review_queue_rows"] for x in summaries),
        "strong_machine_mismatch_rows": sum(x["strong_machine_mismatch_rows"] for x in summaries),
        "safe_auto_corrections": 0,
        "all_full_runs": all(x["is_full_run"] for x in summaries),
        "boundary": "No candidate content was changed by this audit.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(aggregate_obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(aggregate_obj, ensure_ascii=False, indent=2), flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--language", choices=sorted(SOURCE_CONFIG))
    ap.add_argument("--output-dir", type=Path, default=Path("audit-out"))
    ap.add_argument("--batch-size", type=int, default=24)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--aggregate-dir", type=Path)
    ap.add_argument("--aggregate-output", type=Path)
    args = ap.parse_args()
    if args.aggregate_dir:
        if not args.aggregate_output:
            ap.error("--aggregate-output is required with --aggregate-dir")
        aggregate(args.aggregate_dir, args.aggregate_output)
        return
    if not args.language:
        ap.error("--language is required unless aggregating")
    audit(args.language, args.output_dir, args.batch_size, args.limit)


if __name__ == "__main__":
    main()
