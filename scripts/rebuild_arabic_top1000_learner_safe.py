#!/usr/bin/env python3
"""Rebuild learner-facing Arabic Top-1000 backs conservatively.

Ranking/front inventory comes from the already validated precision candidate.
CALIMA remains a morphology validator, not a learner-facing dictionary.
English learner meanings use the repository's original learner deck as a semantic
baseline, with explicit rank-specific overrides for high-risk function words,
homographs, and known analyzer ambiguities.
"""
from __future__ import annotations

import csv
import io
import re
import subprocess
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "audit" / "arabic_top1000_precision_candidate.csv"
SOURCE = ROOT / "audit" / "al_said_2023_msa1000.csv"
REPORT = ROOT / "audit" / "arabic_top1000_learner_safety_report.txt"
LEGACY_REF = "17a41bf4247cbabddf6011d4f699e224af2b833f"
DIAC = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
RANK_RE = re.compile(r"(?m)^Rank:\s*(\d+)\s*$")
POS_RE = re.compile(r"(?m)^Published POS:\s*(.+?)\s*$")
ROOT_RE = re.compile(r"(?m)^\s*Root:\s*([^\n]+)$")
EN_RE = re.compile(r"(?m)^EN:\s*(.+?)\s*$")


def norm_ar(text: str) -> str:
    return DIAC.sub("", unicodedata.normalize("NFC", text or "").replace("ـ", "")).strip()


def clean_meaning(text: str) -> str:
    x = (text or "").strip()
    x = x.replace(" / ", "; ").replace("/", "; ")
    x = re.sub(r"\s*;\s*", "; ", x)
    x = re.sub(r"\s+", " ", x).strip(" ;")
    return x


# Rank-specific learner meanings. These override any automated or historical gloss.
# They cover function words, known homographs, source-vocalization bundles and rows
# where an isolated morphological analyzer is especially likely to choose the wrong sense.
OVERRIDE = {
    1: "in; at",
    2: "that; to (subordinator: أَنْ / أَنَّ)",
    3: "from; who; whom",
    4: "on; upon; over",
    5: "no; not",
    6: "to; toward",
    7: "this (masculine singular)",
    8: "was; were; be (past form of كان)",
    9: "if (إِنْ); indeed; certainly (إِنَّ)",
    10: "what; that which",
    11: "to him; for him; he has",
    12: "I",
    13: "about; from; away from",
    14: "that (masculine singular)",
    15: "with; together with",
    16: "with him; by him; with it; by it",
    17: "is; is being; will be (يكون)",
    18: "did not (past negation with the jussive)",
    19: "you (singular; masculine or feminine when unvocalized)",
    20: "yes/no question particle; is/are/do/does/did...?",
    21: "who; which; that (feminine singular relative pronoun)",
    22: "is not; are not; was not (ليس, negative copular verb)",
    23: "but; however (لَكِنْ / لَكِنَّ)",
    24: "all; every; each; eat! (كُلّ / كُلْ)",
    25: "this (feminine singular)",
    26: "O...!; vocative particle",
    27: "who; which; that (masculine singular relative pronoun)",
    28: "he; it (masculine)",
    29: "indeed; certainly; already (لَقَدْ)",
    31: "what?",
    32: "well; okay; fine (حسنًا)",
    34: "here",
    37: "after; later; afterwards",
    38: "which; any; whichever",
    40: "there; over there",
    41: "with; at; in the possession of",
    42: "now",
    43: "or",
    44: "if; when",
    45: "yes; indeed",
    48: "she; it (feminine)",
    51: "between; among; clarified/explained (بَيْن / بَيَّن)",
    52: "already; indeed; may; might (قَدْ)",
    54: "only; just",
    55: "will not",
    56: "until; up to; even",
    62: "for the sake of; because of; yes/indeed in أَجَلْ",
    64: "during; throughout; through",
    69: "as; just as; as well as",
    71: "when",
    72: "how?",
    73: "we",
    74: "first; foremost",
    78: "other than; not; except; changed (غَيْر / غَيَّر)",
    81: "more; most",
    83: "very; very much",
    84: "other; another (آخَر); last; final (آخِر)",
    85: "will; shall (future marker)",
    89: "also; too",
    90: "that (feminine singular)",
    92: "why?",
    93: "or (أَمْ); mother (أُمّ)",
    98: "likewise; also; in that way",
    101: "yesterday",
    102: "where; in which; whereas",
    104: "since; for (a period); ago",
    105: "perhaps; maybe",
    106: "where?",
    109: "come on!; let's go!",
    110: "if; if only; even if (لَوْ)",
    112: "thanks; thank you",
    115: "at; with; by; near",
    116: "better; best; preferable",
    123: "without; below; short of; recorded/wrote down (دُون / دَوَّن)",
    127: "hello; welcome",
    130: "special; particular; especially (خاصة)",
    131: "in front of; before",
    133: "around; about; concerning; changed/converted (حَوْل / حَوَّل)",
    136: "except; unless; only (إلّا)",
    142: "really; truly",
    143: "O...! (formal masculine vocative introducer أيها)",
    148: "sorry; regretful",
    151: "side; aspect; beside; alongside",
    160: "who; those who (masculine plural relative pronoun)",
    161: "no; certainly not (كَلَّا); both (masculine, كِلَا)",
    167: "first; former; feminine of أول / one of two in certain constructions",
    182: "outside; external to",
    188: "inside; within",
    194: "therefore; thus; for that reason",
    198: "leave!; let!; allow! (دع)",
    204: "Allah; God",
    224: "despite; in spite of (رغم)",
    230: "so that; in order that",
    231: "how many?; how much?",
    235: "always",
    238: "in what; concerning what; while/insofar as (فيما)",
    241: "ever; never (with negation); at all",
    248: "loss; absence; losing (فَقْد)",
    264: "under; below",
    267: "toward; about; approximately",
    269: "must; necessarily; inevitably (لا بُدَّ)",
    276: "morning; in the morning",
    281: "because; because of the fact that (لأن)",
    288: "then; therefore; in that case (إذن)",
    292: "attention/emphasis particle أَلَا; or أَلَّا = that not",
    299: "from/of what; from/of which (مِن + ما)",
    326: "like this; thus; in this way",
    336: "as for; whereas; either (depending on vocalization/context)",
    338: "at all; absolutely",
    339: "completely; entirely; exactly",
    347: "how...!; what a...! (exclamative ما)",
    353: "these",
    373: "especially; particularly",
    383: "possessor of; having; with (ذو)",
    386: "when (لَمَّا); not yet / when used with negation; for what/to what (لِمَا)",
    417: "hopes; wishes; asks/request politely (يرجو)",
    423: "opposite; مقابل; in exchange for; counterpart",
    442: "task; mission; assignment",
    443: "more; additional amount; further",
    455: "foreign; external; exterior (feminine adjective/noun use)",
    457: "modern; recent; new (adjective حديث)",
    458: "noon; midday (ظُهْر)",
    460: "as if; as though",
    467: "league; round/periodic competition; periodic (depending on use)",
    475: "indicating; pointing out; noting (مشيرًا)",
    489: "sky; heaven (سماء); source POS annotation is anomalous",
    492: "all together; altogether; everyone",
    503: "throughout; during; all through",
    505: "when?",
    507: "during; while",
    521: "tomorrow",
    536: "pain (أَلَم); did...not? / interrogative combination أَلَمْ depending on vocalization",
    589: "any; whichever; which (feminine form أية)",
    601: "currently; at present",
    626: "together",
    632: "one of (feminine); one of two",
    633: "above; over",
    634: "except; other than; apart from",
    648: "sure; certain; confident",
    673: "subsequent; later; following; followed/caught up with",
    680: "whatever; no matter what",
    695: "woman",
    700: "still is; continues to be (لا يزال)",
    710: "when; since; as; because (إذ, context-dependent)",
    724: "welcome!; hello! (أهلًا)",
    738: "behind; beyond; after",
    750: "equal; alike; whether...or; equally",
    756: "really; indeed; actually",
    768: "around; approximately; about",
    786: "approximately; roughly",
    802: "soon; shortly; nearby (قريبًا, context-dependent)",
    824: "major; greater; largest (feminine كبرى)",
    842: "current; ongoing",
    854: "Lord; master; owner (رَبّ); perhaps/many a (رُبَّ)",
    865: "recently; lately",
    868: "again; anew; once again",
    873: "middle; central; intermediate (أوسط)",
    884: "after; following; commented/followed up (عَقِب / عَقَّب)",
    887: "dinner; evening meal (عَشَاء)",
    907: "only; merely; nothing but",
    927: "according to; in accordance with (commonly وَفْقًا لِـ)",
    965: "side; direction; aspect; from the standpoint of",
    969: "crazy; insane",
    971: "present; existing; available; found",
}

# Critical meanings must be present after rebuilding; these are learner-safety tripwires.
CRITICAL = {
    1: ["in"], 4: ["on"], 6: ["to"], 22: ["not"], 23: ["but"],
    32: ["well"], 45: ["yes"], 83: ["very"], 89: ["also"], 112: ["thank"],
    127: ["hello"], 133: ["around"], 148: ["sorry"], 194: ["therefore"],
    269: ["must"], 281: ["because"], 326: ["thus"], 347: ["exclamative"],
    353: ["these"], 460: ["as if"], 500: ["speech"], 503: ["throughout"],
    550: ["results"], 626: ["together"], 634: ["except"], 700: ["still"],
    710: ["when"], 785: ["oil"], 798: ["sleep"], 852: ["treatment"],
    927: ["according to"],
}


def legacy_map() -> dict[str, str]:
    raw = subprocess.check_output(
        ["git", "show", f"{LEGACY_REF}:arabic_top1000.csv"], cwd=ROOT
    ).decode("utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(raw)))
    out: dict[str, str] = {}
    collisions: dict[str, list[str]] = {}
    for r in rows:
        front = norm_ar(r.get("Front", ""))
        m = EN_RE.search(r.get("Back", "") or "")
        if not front or not m:
            continue
        meaning = clean_meaning(m.group(1))
        if front in out and out[front] != meaning:
            collisions.setdefault(front, [out[front]]).append(meaning)
        else:
            out[front] = meaning
    # Keep only unambiguous historical semantic baselines. Rank-specific ambiguity is
    # handled in OVERRIDE instead of silently selecting one historical sense.
    for word in collisions:
        out.pop(word, None)
    return out


def safe_roots(back: str) -> list[str]:
    roots = []
    for value in ROOT_RE.findall(back):
        value = value.strip()
        if not value or value.startswith("—"):
            continue
        if value not in roots:
            roots.append(value)
    return roots


def main() -> None:
    with CANDIDATE.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    with SOURCE.open(encoding="utf-8", newline="") as f:
        source_rows = list(csv.DictReader(f))
    legacy = legacy_map()

    problems: list[str] = []
    matched_legacy = 0
    overridden = 0
    fallback = 0
    rebuilt = []

    if len(rows) != 1000 or len(source_rows) != 1000:
        problems.append(f"row count candidate={len(rows)} source={len(source_rows)}")

    forbidden_fragments = [
        "+he;it", "+it;him", "+me", "+you", "it;they;she+", "he;it+",
        "you_[", "[def.", "[indef.", "<verb>", "the+", "and+", "for +",
    ]

    for i, row in enumerate(rows, 1):
        front = norm_ar(row.get("Front", ""))
        old_back = row.get("Back", "") or ""
        rank_match = RANK_RE.search(old_back)
        if not rank_match or int(rank_match.group(1)) != i:
            problems.append(f"rank {i}: bad candidate rank metadata")
        pos_match = POS_RE.search(old_back)
        pos = pos_match.group(1).strip() if pos_match else source_rows[i-1].get("pos_codes", "")

        if i in OVERRIDE:
            meaning = OVERRIDE[i]
            overridden += 1
        elif front in legacy:
            meaning = legacy[front]
            matched_legacy += 1
        else:
            # Last-resort fallback: use stem-level/manual candidate sense lines, but strip
            # morphology formatting. The safety audit below will reject artifacts.
            senses = []
            for line in old_back.splitlines():
                m = re.match(r"^\d+\.\s+[^:]+:\s*(.+)$", line.strip())
                if m:
                    senses.append(clean_meaning(m.group(1).replace("+", " ")))
            meaning = "; ".join(dict.fromkeys(x for x in senses if x))
            fallback += 1

        meaning = clean_meaning(meaning)
        if not meaning:
            problems.append(f"rank {i} {front}: empty learner meaning")

        roots = safe_roots(old_back)
        lines = [f"Rank: {i}", "", f"Meaning: {meaning}", "", f"Published POS: {pos}"]
        if roots:
            lines += ["", "Root: " + " / ".join(roots)]
        lines += [
            "", "Sources:",
            f"- Al-Said (2023), Table 4 — rank {i} and source POS/vocalization inventory",
            "- CALIMA-MSA r13 via CAMeL Tools — morphology/root cross-check only",
            "- Learner-safety semantic review — clean English meaning; raw analyzer glosses are not exposed",
        ]
        new_back = "\n".join(lines)

        for frag in forbidden_fragments:
            if frag in new_back:
                problems.append(f"rank {i} {front}: forbidden morphology artifact {frag!r}")
        if "+" in meaning or "[" in meaning or "]" in meaning or "<" in meaning or ">" in meaning:
            problems.append(f"rank {i} {front}: non-learner morphology markup in meaning {meaning!r}")
        for required in CRITICAL.get(i, []):
            if required.casefold() not in meaning.casefold():
                problems.append(f"rank {i} {front}: critical meaning missing {required!r}: {meaning!r}")

        rebuilt.append({"Front": front, "Back": new_back})

    # Preserve only the intentional duplicate spelling ما at ranks 10 and 347.
    seen: dict[str, list[int]] = {}
    for i, r in enumerate(rebuilt, 1):
        seen.setdefault(r["Front"], []).append(i)
    unexpected = {w: ranks for w, ranks in seen.items() if len(ranks) > 1 and not (w == "ما" and ranks == [10, 347])}
    if unexpected:
        problems.append(f"unexpected duplicate fronts: {unexpected}")

    with CANDIDATE.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["Front", "Back"], lineterminator="\n")
        w.writeheader(); w.writerows(rebuilt)

    report = [
        f"rows={len(rebuilt)}",
        f"rank_order_preserved={len(rebuilt) == 1000}",
        f"learner_meaning_overrides={overridden}",
        f"legacy_semantic_matches={matched_legacy}",
        f"candidate_fallbacks={fallback}",
        f"problems={len(problems)}",
        "policy=raw CALIMA gloss is never exposed directly to learners",
        "policy=ranking and front inventory remain fixed",
        *problems,
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(REPORT.read_text(encoding="utf-8"))
    if problems:
        raise SystemExit("Learner-safety rebuild failed")


if __name__ == "__main__":
    main()
