#!/usr/bin/env python3
from pathlib import Path
import gzip, hashlib, json, urllib.parse

ROOT = Path(".")
A2_PATH = ROOT / "reading/urdu/a2/passages.jsonl"
A1_PATH = ROOT / "reading/urdu/a1/passages.jsonl"
STATUS_PATH = ROOT / "reading/STATUS.json"
CONT_PATH = ROOT / "reading/CONTINUATION.json"
TASKS_PATH = ROOT / "reading/TASKS.md"
HANDOFF_PATH = ROOT / "reading/AGENT_HANDOFF_V2.md"
LEX_AUDIT = ROOT / "reading/audit/urdu_a2_u03_lexical_sense_check_2026-08-24.json"
QUALITY_AUDIT = ROOT / "reading/audit/urdu_a2_u03_quality_pass_2026-08-24.json"

SOURCE_A2_BLOB = "fa03e0e9c18a2f3e5e16d2838743a8502380e258"
PACKET_SHA256 = "6c9057fe7923861071381baa1e5e85908959181560e536d274a6f3cfd0d3d4b3"
PACKET_GIT_BLOB = "00edfd5819e08bf26d18e288b5d3df49fab70ab6"
PACKET_BYTES = 52122

PARTS = [
    ("reading/staging/urdu_a2_u03_p01.jsonl.gz", "0cec7c0c47a39f0ea180cc1fac26e1c30610b2eb", 3229,
     "feed2cf39f9df0746ab69ec7cae5535be55fb22d73d70b6361fdc45ecbc7e93e",
     8599, "f4b0a76d3b275d075dd7a57a3e0f4dd0c669ed64fcf0fd13fd12524b8bc656c8"),
    ("reading/staging/urdu_a2_u03_p02.jsonl.gz", "9463c8352c46af5ee77c9c1f783b1c8a99e1e2ed", 3207,
     "49c28f0d2b59f81c5214b92fc57475283a7f9eb6dfb9d4f504f96487cc8a0b37",
     8556, "7bb1f63496869b13ce9be854987b873b2da198c6434acfba2b5be873ce20d06a"),
    ("reading/staging/urdu_a2_u03_p03.jsonl.gz", "fd78155e54d4475a7cc361b579a8dd23dae359e8", 3190,
     "990e9c38d5d1e8c78af0ff8a9b946f603acc8114262cf685b3a7bda4313aff1e",
     8601, "c0b6dea6f779169aa8537c7979f8961de4ee78eb12562e38aa52aeaaca0453ea"),
    ("reading/staging/urdu_a2_u03_p04.jsonl.gz", "b43eb4b58051839cf1acb0376ab77460de580ca8", 3172,
     "e7aaeb1bc4979558d17142d87babccc2cf063602b27c938be00daab7a6937894",
     8696, "a0223f35ba6b03aa62bdd2e471d2b9c6b8a8c7922ed4b2c7e3782525b22809b1"),
    ("reading/staging/urdu_a2_u03_p05.jsonl.gz", "5db55191d416c3997923fbb2b10746a64592cc13", 3164,
     "59893de88e464c61de8dc0471caa0e14dc68635a515cbeb85f2b533d2b8a808c",
     8878, "2435dd858007e3feb0114c54d7f84602f4ea99f23bdea59a22c54288e3f2869d"),
    ("reading/staging/urdu_a2_u03_p06.jsonl.gz", "22c7ca22d3456c90f1da60249d20a174c221898e", 3097,
     "35b11c954b8bf6545d9d07ff93cb65e1162bb1b3527592a61c11ad3f6f3644b2",
     8792, "7e1d00b0b7c7ceb1fde5a0143b2479afb08968a4ddc49755866f27bab5c1aee9"),
]

EXPECTED_TARGETS = {
    "ur-a2-u03-p01": ["ur-rank-0614", "ur-rank-0883"],
    "ur-a2-u03-p02": ["ur-rank-0705", "ur-rank-0917"],
    "ur-a2-u03-p03": ["ur-rank-0706", "ur-rank-0863"],
    "ur-a2-u03-p04": ["ur-rank-0665", "ur-rank-0924"],
    "ur-a2-u03-p05": [],
    "ur-a2-u03-p06": [],
}
EXPECTED_WORD_COUNTS = {
    "ur-a2-u03-p01": 210, "ur-a2-u03-p02": 212, "ur-a2-u03-p03": 220,
    "ur-a2-u03-p04": 219, "ur-a2-u03-p05": 218, "ur-a2-u03-p06": 216,
}
EXPECTED_ROLES = ["instructional", "reinforcement", "interleaved", "transfer", "integration", "fluency"]
ALLOWED_GENRES = {"personal narrative", "diary", "short interview"}

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def git_blob(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()

def load_jsonl_bytes(data: bytes):
    lines = data.splitlines()
    if not lines:
        return []
    return [json.loads(line.decode("utf-8")) for line in lines]

def fail(msg):
    raise SystemExit(msg)

source = A2_PATH.read_bytes()
if git_blob(source) != SOURCE_A2_BLOB:
    fail(f"source Urdu A2 blob drift: {git_blob(source)} != {SOURCE_A2_BLOB}")
existing = load_jsonl_bytes(source)
if len(existing) != 12 or [r.get("sequence") for r in existing] != list(range(1, 13)):
    fail("source Urdu A2 must contain exactly sequences 1-12")
if existing[-1].get("id") != "ur-a2-u02-p06":
    fail("source Urdu A2 tail is not reviewed Unit 2 fluency passage")

status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
cont = json.loads(CONT_PATH.read_text(encoding="utf-8"))
if status["current"]["canonical_passages"] != 792 or status["languages"]["urdu"]["canonical_passages"] != 72:
    fail("STATUS.json is not at expected 792/72 frontier")
if status["current"]["active_language"] != "urdu" or status["current"]["active_level"] != "A2":
    fail("STATUS.json active language/level drift")
action = cont["active_frontier"]["production"]["action"]
if "Unit 3 / sequence 13" not in action:
    fail("CONTINUATION.json is not at Unit 3 / sequence 13 frontier")
if cont["production"]["canonical_passages"] != 792 or cont["production"]["urdu"]["canonical_passages"] != 72:
    fail("CONTINUATION.json production counts drift")

packet_parts = []
for path_s, expected_blob, cbytes, csha, ubytes, usha in PARTS:
    p = ROOT / path_s
    raw = p.read_bytes()
    if len(raw) != cbytes:
        fail(f"{path_s}: compressed byte count drift")
    if sha256(raw) != csha:
        fail(f"{path_s}: compressed SHA-256 drift")
    if git_blob(raw) != expected_blob:
        fail(f"{path_s}: Git blob drift")
    dec = gzip.decompress(raw)
    if len(dec) != ubytes or sha256(dec) != usha:
        fail(f"{path_s}: decompressed record drift")
    packet_parts.append(dec)

packet = b"".join(packet_parts)
if len(packet) != PACKET_BYTES or sha256(packet) != PACKET_SHA256 or git_blob(packet) != PACKET_GIT_BLOB:
    fail("full reviewed Unit 3 packet hash/size drift")
records = load_jsonl_bytes(packet)
if len(records) != 6:
    fail("Unit 3 packet must contain six records")

introduced = set()
for path in [A1_PATH, A2_PATH]:
    for r in load_jsonl_bytes(path.read_bytes()):
        for t in r.get("new_lexical_targets", []):
            introduced.add(t["id"])

all_new = []
word_counts = {}
targets_by_passage = {}
exposures = {}
questions = answers = 0
for i, r in enumerate(records):
    rid = f"ur-a2-u03-p{i+1:02d}"
    if r.get("id") != rid or r.get("sequence") != 13 + i or r.get("unit") != 3:
        fail(f"{rid}: identity/unit/sequence mismatch")
    if r.get("language") != "ur" or r.get("cefr") != "A2":
        fail(f"{rid}: language/CEFR mismatch")
    if r.get("passage_type") != EXPECTED_ROLES[i]:
        fail(f"{rid}: role mismatch")
    if r.get("genre") not in ALLOWED_GENRES:
        fail(f"{rid}: off-roadmap genre")
    wc = len(r["text"].split())
    if wc != r.get("word_count") or wc != EXPECTED_WORD_COUNTS[rid] or not (140 <= wc <= 220):
        fail(f"{rid}: word-count mismatch/out of A2 generation band")
    word_counts[rid] = wc
    qs, ans = r.get("questions", []), r.get("answer_key", [])
    if len(qs) != 10 or len(ans) != 10:
        fail(f"{rid}: must have exactly 10 questions and 10 answers")
    questions += len(qs); answers += len(ans)
    for n, (q, a) in enumerate(zip(qs, ans), 1):
        if q.get("id") != f"q{n}" or q.get("answer_id") != f"a{n}":
            fail(f"{rid}: question link mismatch at {n}")
        if a.get("id") != f"a{n}" or a.get("question_id") != f"q{n}" or not a.get("answer", "").strip():
            fail(f"{rid}: answer link/empty mismatch at {n}")
    nts = r.get("new_lexical_targets", [])
    ids = [t["id"] for t in nts]
    if ids != EXPECTED_TARGETS[rid]:
        fail(f"{rid}: unexpected deliberate new-target set")
    targets_by_passage[rid] = ids
    exposures[rid] = {}
    for t in nts:
        tid, form = t["id"], t["form"]
        if tid in introduced:
            fail(f"{rid}: target {tid} was already introduced canonically")
        count = r["text"].count(form)
        if count != t.get("exposures_in_text") or count < 2:
            fail(f"{rid}: exposure drift for {tid}")
        if not any(tid in q.get("target_ids", []) for q in qs):
            fail(f"{rid}: target {tid} is not assessed")
        exposures[rid][tid] = count
        all_new.append(tid)
if len(all_new) != 8 or len(set(all_new)) != 8:
    fail("Unit 3 must introduce exactly eight unique deliberate targets")
if records[4]["new_lexical_targets"]:
    fail("Unit 3 P5 must not introduce deliberate new lexical targets")
if records[5]["new_lexical_targets"] or records[5]["speed_training"].get("new_word_policy") != "none" or not records[5]["speed_training"].get("timed"):
    fail("Unit 3 P6 fluency policy mismatch")

result = source + packet
if len(load_jsonl_bytes(result)) != 18:
    fail("post-write Urdu A2 count would not be 18")
A2_PATH.write_bytes(result)
result_blob = git_blob(result)

target_rows = []
for r in records[:4]:
    for t in r["new_lexical_targets"]:
        target_rows.append({
            "id": t["id"], "form": t["form"], "source_rank": t["source_rank"],
            "accepted_sense": t["intended_sense"], "dictionary": "Rekhta Dictionary",
            "url": "https://www.rekhta.org/urdudictionary?keyword=" + urllib.parse.quote(t["form"]),
        })
lex_audit = {
    "schema_version": 1, "project_id": "LANG-A1C2", "language": "ur", "cefr": "A2",
    "unit": 3, "date": "2026-08-24", "status": "PASS_FOR_GENERATION_TARGET_SENSES",
    "scope": "Deliberate learner-facing senses only. This does not validate whole-passage linguistic/pedagogical quality or educator/publication release readiness.",
    "source_lexicon": "reading/lexicons/urdu.jsonl",
    "canonical_freshness_method": "Candidate target IDs were checked against live canonical Urdu A1 and A2 new_lexical_targets; all eight were absent before Unit 3.",
    "targets": target_rows,
    "generation_policy": {"P1_P4_new_targets_per_passage": 2, "P5_new_targets": 0, "P6_new_targets": 0, "P6_new_word_policy": "none"},
    "quality_promotion": False,
}
LEX_AUDIT.parent.mkdir(parents=True, exist_ok=True)
LEX_AUDIT.write_text(json.dumps(lex_audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

quality_audit = {
    "schema_version": 1, "project_id": "LANG-A1C2", "language": "ur", "cefr": "A2", "unit": 3,
    "date": "2026-08-24", "status": "PASS_AFTER_PRECANONICAL_READER_PASS",
    "scope": "Bounded generation-stage reader-first pass for Unit 3 only: naturalness, target-sense clarity, answer grounding/linkage, operational A2 grammar, word-band checks, roadmap role/genre checks, and fluency new-word policy. Formal corpus-wide linguistic, pedagogical, CEFR/coverage, independent/native, and educator-release gates remain pending.",
    "source_canonical_git_blob": SOURCE_A2_BLOB, "source_a2_passages": 12,
    "packet_sha256": PACKET_SHA256, "packet_git_blob": PACKET_GIT_BLOB,
    "result_canonical_git_blob": result_blob, "result_a2_passages": 18,
    "project_passages_after": 798, "urdu_passages_after": 78,
    "unit_sequences": list(range(13, 19)), "passages": 6, "questions": questions, "answers": answers,
    "word_counts": word_counts, "new_target_ids_by_passage": targets_by_passage,
    "new_target_exposures": exposures,
    "lexical_sense_evidence": str(LEX_AUDIT).replace("\\", "/"),
    "reader_first_note": "Reviewed packet includes the prior bounded naturalness correction in P4 ('انہی پرانی کہانیوں میں سے چند ...'); the exact corrected packet is hash-locked above.",
    "checks": {
        "source_blob_guard": True, "packet_hash_guard": True, "six_chunk_hash_guards": True,
        "fresh_target_ids_against_live_urdu_a1_a2": True, "six_passage_role_order": True,
        "roadmap_genres_only": True, "word_band_140_220": True,
        "exactly_10_questions_and_10_answers_each": True, "bidirectional_q_a_links": True,
        "each_new_target_assessed": True, "target_exposure_metadata_recounted": True,
        "p5_has_no_new_deliberate_targets": True, "p6_has_no_new_deliberate_targets": True,
        "p6_new_word_policy_none": True, "post_write_project_and_urdu_counts": True,
    },
    "quality_promotion": False, "educator_release_ready": False,
}
QUALITY_AUDIT.write_text(json.dumps(quality_audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

status["current"]["canonical_passages"] = 798
status["current"]["remaining_generation_passages"] = 282
status["languages"]["urdu"]["canonical_passages"] = 78
status["languages"]["urdu"]["remaining_generation_passages"] = 282
STATUS_PATH.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

cont["production"]["canonical_passages"] = 798
cont["production"]["urdu"]["canonical_passages"] = 78
cont["active_frontier"]["production"]["action"] = (
    "Continue generation-first production from Urdu A2 Unit 4 / sequence 19 using the canonical roadmap and ten-question contract. "
    "Do not reopen Urdu A1 generation unless fresh evidence identifies a concrete defect."
)
old_next = "Use reading/planning/ACTIVE_GENERATION_PLAN.json to start the next guarded Urdu A2 Unit 3 batch at sequence 13."
new_next = "Use reading/planning/ACTIVE_GENERATION_PLAN.json to start the next guarded Urdu A2 Unit 4 batch at sequence 19."
if old_next not in cont["exact_next_actions"]:
    fail("CONTINUATION exact-next-action drift")
cont["exact_next_actions"] = [new_next if x == old_next else x for x in cont["exact_next_actions"]]
CONT_PATH.write_text(json.dumps(cont, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def exact_replace(path: Path, replacements):
    text = path.read_text(encoding="utf-8")
    for old, new in replacements:
        if old not in text:
            fail(f"{path}: expected text not found: {old}")
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")

exact_replace(TASKS_PATH, [
    ("Canonical production frontier: **Urdu A2, Unit 3, sequence 13**.", "Canonical production frontier: **Urdu A2, Unit 4, sequence 19**."),
    ("- Urdu: 72/360 generated; A1 complete, A2 in progress.", "- Urdu: 78/360 generated; A1 complete, A2 in progress."),
    ("- Project: 792/1080 generated.", "- Project: 798/1080 generated."),
])

exact_replace(HANDOFF_PATH, [
    ("- Canonical generated total: **792**.", "- Canonical generated total: **798**."),
    ("- Urdu: **72/360**; A1 generation complete and A2 generation in progress.", "- Urdu: **78/360**; A1 generation complete and A2 generation in progress."),
    ("- Urdu A2 canonical path: `reading/urdu/a2/passages.jsonl`; Units 1-2 currently contain sequences 1-12.",
     "- Urdu A2 canonical path: `reading/urdu/a2/passages.jsonl`; Units 1-3 currently contain sequences 1-18."),
    ("Continue **Urdu A2**, starting from Unit 3 / sequence 13, under:",
     "Continue **Urdu A2**, starting from Unit 4 / sequence 19, under:"),
    ("Unit 3 uses the roadmap theme **past events and memories** with `personal narrative`, `diary`, and `short interview` genres.",
     "Unit 4 uses the roadmap theme **shopping, comparison, and problems** with `review`, `problem-solution narrative`, and `notice` genres."),
    ("Run `python reading/tools/validate_continuation_state.py`; if it passes, resume guarded generation at **Urdu A2 Unit 3 / sequence 13** using the Unit 3 roadmap theme `past events and memories`.",
     "Run `python reading/tools/validate_continuation_state.py`; if it passes, resume guarded generation at **Urdu A2 Unit 4 / sequence 19** using the Unit 4 roadmap theme `shopping, comparison, and problems`."),
])

print(json.dumps({
    "status": "PASS",
    "packet_sha256": PACKET_SHA256,
    "source_blob": SOURCE_A2_BLOB,
    "result_blob": result_blob,
    "project_after": 798,
    "urdu_after": 78,
    "next_unit": 4,
    "next_sequence": 19,
}, ensure_ascii=False))
