import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

import stanza

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
AUDIT = READING / "audit"
AUDIT.mkdir(parents=True, exist_ok=True)

LANGS = {"arabic": "ar", "french": "fr", "urdu": "ur"}
AR_DIAC = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")


def norm(text, language):
    text = unicodedata.normalize("NFC", text or "").strip().replace("ـ", "")
    text = re.sub(r"^[^\w\u0600-\u06ff]+|[^\w\u0600-\u06ff]+$", "", text, flags=re.UNICODE)
    if language in ("arabic", "urdu"):
        text = AR_DIAC.sub("", text)
    else:
        text = text.replace("’", "'").replace("‘", "'").casefold()
    return text


def load_lexicon(language):
    forms = {}
    for line in (READING / "lexicons" / f"{language}.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        key = row["match_form"]
        forms[key] = min(forms.get(key, 10**9), row["rank"])
    return forms


def load_passages(language):
    return [json.loads(line) for line in (READING / language / "a1" / "passages.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]


def rank_for(word, language, lex):
    candidates = {norm(word.text, language), norm(word.lemma, language)}
    ranks = [lex[x] for x in candidates if x and x in lex]
    return min(ranks) if ranks else None


def main():
    pipelines = {}
    for language, code in LANGS.items():
        stanza.download(code, processors="tokenize,pos,lemma", verbose=False)
        pipelines[language] = stanza.Pipeline(code, processors="tokenize,pos,lemma", use_gpu=False, verbose=False)

    full = {"method": {
        "tokenizer_lemmatizer": "Stanza tokenization/POS/lemmatization",
        "inventory": "derived validated rank 1-3000 reading lexicons",
        "a1_planning_core": "rank <= 500 plus proper nouns/numerals",
        "important_caveat": "planning-core coverage is lexical-control evidence, not proof of individual learner mastery",
        "instructional_target": 0.97,
        "fluency_target": 0.985
    }, "languages": {}, "overall_gate": "PASS"}

    for language, code in LANGS.items():
        lex = load_lexicon(language)
        passages = load_passages(language)
        lang_rows = []
        for p in passages:
            doc = pipelines[language](p["text"])
            counted = []
            unsupported = Counter()
            outside = Counter()
            band_counts = Counter()
            for sent in doc.sentences:
                for word in sent.words:
                    if word.upos in {"PUNCT", "SYM"}:
                        continue
                    surface = norm(word.text, language)
                    if not surface:
                        continue
                    special = word.upos in {"PROPN", "NUM"}
                    rank = rank_for(word, language, lex)
                    counted.append((word.text, word.lemma, word.upos, rank, special))
                    if special:
                        band_counts["proper_or_number"] += 1
                    elif rank is None:
                        band_counts["outside_3000"] += 1
                        outside[f"{word.text} | lemma={word.lemma}"] += 1
                    elif rank <= 500:
                        band_counts["rank_1_500"] += 1
                    elif rank <= 1000:
                        band_counts["rank_501_1000"] += 1
                        unsupported[f"{word.text} | lemma={word.lemma} | rank={rank}"] += 1
                    elif rank <= 2000:
                        band_counts["rank_1001_2000"] += 1
                        unsupported[f"{word.text} | lemma={word.lemma} | rank={rank}"] += 1
                    else:
                        band_counts["rank_2001_3000"] += 1
                        unsupported[f"{word.text} | lemma={word.lemma} | rank={rank}"] += 1
            n = len(counted)
            inventory = sum(1 for _, _, _, rank, special in counted if special or rank is not None) / n if n else 0
            core = sum(1 for _, _, _, rank, special in counted if special or (rank is not None and rank <= 500)) / n if n else 0
            target = 0.985 if p["sequence"] == 6 else 0.97
            p_gate = "PASS" if core >= target else "REVIEW_REQUIRED"
            if p_gate != "PASS":
                full["overall_gate"] = "REVIEW_REQUIRED"
            lang_rows.append({
                "id": p["id"],
                "sequence": p["sequence"],
                "passage_type": p["passage_type"],
                "stored_word_count": p["word_count"],
                "nlp_word_count": n,
                "inventory_3000_coverage": round(inventory, 4),
                "a1_planning_core_coverage": round(core, 4),
                "required_planning_core_coverage": target,
                "band_counts": dict(band_counts),
                "top_rank_gt_500_tokens": unsupported.most_common(30),
                "top_outside_3000_tokens": outside.most_common(30),
                "new_target_count": len(p["new_lexical_targets"]),
                "new_target_ids": [x["id"] for x in p["new_lexical_targets"]],
                "planning_gate": p_gate
            })
        full["languages"][language] = {
            "passage_count": len(passages),
            "passages": lang_rows,
            "pass_count": sum(x["planning_gate"] == "PASS" for x in lang_rows),
            "review_count": sum(x["planning_gate"] != "PASS" for x in lang_rows)
        }

    (AUDIT / "a1_unit01_coverage_audit.json").write_text(json.dumps(full, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(full, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
