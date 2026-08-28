from __future__ import annotations

import base64
import json
import pathlib
import re
import subprocess
import zlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
CANON = ROOT / "reading/urdu/c1/passages.jsonl"
CONT = ROOT / "reading/CONTINUATION.json"
STATUS = ROOT / "reading/STATUS.json"
PLAN = ROOT / "reading/planning/ACTIVE_GENERATION_PLAN.json"
TASKS = ROOT / "reading/TASKS.md"
HANDOFF = ROOT / "reading/AGENT_HANDOFF_V2.md"
QA = ROOT / "reading/audit/urdu_c1_u07_generation_qa_2026-08-27.json"

PAYLOAD = r'''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'''

PASSAGES = json.loads(zlib.decompress(base64.b64decode(PAYLOAD)).decode("utf-8"))
EXPECTED_IDS = [f"ur-c1-u07-p{i:02d}" for i in range(1, 7)]
EXPECTED_SEQ = list(range(37, 43))
EXPECTED_ROLES = ["instructional", "reinforcement", "interleaved", "transfer", "integration", "checkpoint"]
EXPECTED_GENRES = ["critical essay", "review", "close-reading style prose", "critical essay", "review", "close-reading style prose"]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")



def repair_known_target_collision(existing):
    passage = PASSAGES[2]
    target = passage["new_lexical_targets"][0]
    if target["id"] != "ur-rank-1978":
        return
    prior_forms = {t["form"] for p in existing for t in p.get("new_lexical_targets", [])}
    candidates = [
        ("راوی", "the narrator or narrative voice presenting the scene", "متن میں واقعات یا مشاہدات پیش کرنے والی آواز۔"),
        ("منظر", "a scene presented for close literary reading", "متن میں پیش کیا گیا وہ حصہ یا صورتِ حال جسے قاری تفصیل سے دیکھتا ہے۔"),
        ("خاموشی", "meaningful silence used as a literary device", "وہ خاموش کیفیت جو متن میں محض آواز کی عدم موجودگی نہیں بلکہ معنی پیدا کرے۔"),
        ("اشارہ", "an indirect textual cue that guides interpretation", "متن میں ایسا غیر مستقیم قرینہ جو کسی معنی یا امکان کی طرف رہنمائی کرے۔"),
        ("فضا", "the atmosphere or mood created by textual details", "تفصیلات سے پیدا ہونے والی مجموعی ادبی کیفیت یا ماحول۔"),
    ]
    for i, (form, sense, answer) in enumerate(candidates, 1):
        count = passage["text"].count(form)
        if count >= 2 and form not in prior_forms:
            tid = f"ur-u07-beyond-p03-{i:02d}"
            passage["new_lexical_targets"] = [{
                "id": tid,
                "form": form,
                "lemma": form,
                "part_of_speech": "noun",
                "intended_sense": sense,
                "register": "literary/critical",
                "context_strategy": ["evidence_interpretation"],
                "first_introduced": True,
                "exposures_in_text": count,
                "beyond_base": True,
                "variety": "standard Urdu",
            }]
            passage["questions"][9]["prompt"] = f"یہاں {form} سے کیا مراد ہے؟"
            passage["questions"][9]["target_ids"] = [tid]
            passage["answer_key"][9]["answer"] = answer
            return
    raise SystemExit("FAIL CLOSED: no fresh repeated literary target available for Unit 7 passage 39")

def validate_passages(existing):
    assert [p["id"] for p in PASSAGES] == EXPECTED_IDS
    assert [p["sequence"] for p in PASSAGES] == EXPECTED_SEQ
    assert [p["passage_type"] for p in PASSAGES] == EXPECTED_ROLES
    assert [p["genre"] for p in PASSAGES] == EXPECTED_GENRES
    prior_targets = {t["id"] for p in existing for t in p.get("new_lexical_targets", [])}
    batch_targets = []
    for p in PASSAGES:
        assert p["language"] == "ur" and p["cefr"] == "C1" and p["unit"] == 7
        assert p["topics"] == ["literature and cultural criticism"]
        assert len(p["questions"]) == 10 and len(p["answer_key"]) == 10
        assert [q["id"] for q in p["questions"]] == [f"q{i}" for i in range(1,11)]
        assert [a["id"] for a in p["answer_key"]] == [f"a{i}" for i in range(1,11)]
        assert all(q["answer_id"] == f"a{i}" for i,q in enumerate(p["questions"],1))
        assert all(a["question_id"] == f"q{i}" for i,a in enumerate(p["answer_key"],1))
        assert len(p["new_lexical_targets"]) == 1
        t = p["new_lexical_targets"][0]
        assert t["id"] not in prior_targets and t["id"] not in batch_targets
        batch_targets.append(t["id"])
        literal = p["text"].count(t["form"])
        assert literal >= 2 and literal == t["exposures_in_text"]
        assert p["word_count"] == len(p["text"].split()) and p["word_count"] >= 450
        assert p["quality"]["status"] == "draft"
    return batch_targets


def update_state():
    cont = load_json(CONT)
    status = load_json(STATUS)
    plan = load_json(PLAN)
    assert cont["production"]["canonical_passages"] in (996, 1002)
    assert status["current"]["canonical_passages"] in (996, 1002)
    if cont["production"]["canonical_passages"] == 996:
        assert plan["active_unit"] == 7 and plan["start_sequence"] == 37
        cont["updated"] = "2026-08-27"
        cont["production"]["canonical_passages"] = 1002
        cont["production"]["urdu"]["canonical_passages"] = 282
        cont["active_frontier"]["production"]["action"] = "Continue generation-first production from Urdu C1 Unit 8 / sequence 43 using the canonical roadmap and ten-question contract."
        cont["exact_next_actions"] = [
            "Validate the routed state bundle and live canonical counts.",
            "Use reading/planning/ACTIVE_GENERATION_PLAN.json to start guarded Urdu C1 Unit 8 generation at sequence 43.",
            "Keep release/educator verification separate from generation progress."
        ]
        status["updated"] = "2026-08-27"
        status["current"]["canonical_passages"] = 1002
        status["current"]["remaining_generation_passages"] = 78
        status["languages"]["urdu"]["canonical_passages"] = 282
        status["languages"]["urdu"]["remaining_generation_passages"] = 78
        plan["active_unit"] = 8
        plan["start_sequence"] = 43
        plan["existing_active_level_passages"] = 42
        plan["active_unit_roadmap"] = {"unit": 8, "theme": "economics, risk, and forecasting", "genres": ["analysis", "briefing", "scenario comparison"]}
        dump_json(CONT, cont); dump_json(STATUS, status); dump_json(PLAN, plan)

        tasks = TASKS.read_text(encoding="utf-8")
        replacements = {
            "Urdu C1, Unit 7, sequence 37":"Urdu C1, Unit 8, sequence 43",
            "Urdu: 276/360 generated":"Urdu: 282/360 generated",
            "Project: 996/1080 generated":"Project: 1002/1080 generated"
        }
        for old,new in replacements.items():
            assert old in tasks
            tasks = tasks.replace(old,new)
        TASKS.write_text(tasks, encoding="utf-8")

        hand = HANDOFF.read_text(encoding="utf-8")
        reps = {
            "Canonical generated total: **996**":"Canonical generated total: **1002**",
            "Urdu: **276/360**":"Urdu: **282/360**",
            "**Urdu C1 Unit 7 / sequence 37** using the C1 Unit 7 roadmap theme `literature and cultural criticism`":"**Urdu C1 Unit 8 / sequence 43** using the C1 Unit 8 roadmap theme `economics, risk, and forecasting`",
            "Unit 7 / sequence 37":"Unit 8 / sequence 43",
            "C1 Unit 7 uses the roadmap theme **literature and cultural criticism** with `critical essay`, `review`, and `close-reading style prose` genres.":"C1 Unit 8 uses the roadmap theme **economics, risk, and forecasting** with `analysis`, `briefing`, and `scenario comparison` genres.",
        }
        for old,new in reps.items():
            assert old in hand
            hand = hand.replace(old,new)
        HANDOFF.write_text(hand, encoding="utf-8")


def main():
    existing = [json.loads(line) for line in CANON.read_text(encoding="utf-8").splitlines() if line.strip()]
    seqs = [p["sequence"] for p in existing]
    ids = [p["id"] for p in existing]
    baseline_targets = existing[:-6] if seqs == list(range(1,43)) and ids[-6:] == EXPECTED_IDS else existing
    repair_known_target_collision(baseline_targets)
    if seqs == list(range(1,37)):
        target_ids = validate_passages(existing)
        with CANON.open("a", encoding="utf-8") as f:
            for p in PASSAGES:
                f.write(json.dumps(p, ensure_ascii=False, separators=(",", ":")) + "\n")
        canonicalized = True
    elif seqs == list(range(1,43)) and ids[-6:] == EXPECTED_IDS:
        target_ids = validate_passages(existing[:-6])
        canonicalized = False
    else:
        raise SystemExit(f"FAIL CLOSED: unexpected Urdu C1 frontier: {seqs[-8:]}")

    reread = [json.loads(line) for line in CANON.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert [p["sequence"] for p in reread] == list(range(1,43))
    assert [p["id"] for p in reread[-6:]] == EXPECTED_IDS
    update_state()

    qa = {
        "project_id":"LANG-A1C2",
        "language":"urdu",
        "level":"C1",
        "unit":7,
        "sequences":EXPECTED_SEQ,
        "passage_ids":EXPECTED_IDS,
        "theme":"literature and cultural criticism",
        "genres":EXPECTED_GENRES,
        "canonicalization_status":"CANONICAL_APPEND_CONFIRMED",
        "canonical_passage_count":42,
        "project_canonical_passages":1002,
        "urdu_canonical_passages":282,
        "remaining_generation_passages":78,
        "new_target_ids":target_ids,
        "word_counts":[p["word_count"] for p in PASSAGES],
        "questions_per_passage":10,
        "answers_per_passage":10,
        "hard_errors":0,
        "formal_release_audit":"DEFERRED",
        "release_claim":False,
        "next_frontier":"Urdu C1 Unit 8 / sequence 43",
        "notes":["All six source texts are explicitly fictional literary/critical exercises.","Three new targets are rank-bound to urdu_top3000.csv; three specialist literary terms are marked beyond_base rather than assigned invented ranks."]
    }
    dump_json(QA, qa)
    subprocess.run(["python", "reading/tools/refresh_state_manifest.py"], cwd=ROOT, check=True)
    subprocess.run(["python", "reading/tools/validate_continuation_state.py"], cwd=ROOT, check=True)
    print("Urdu C1 Unit 7 canonicalized; next frontier Unit 8 / sequence 43")

if __name__ == "__main__":
    main()
