from __future__ import annotations

from pathlib import Path
import textwrap

SCRIPT = Path(__file__).with_name("apply_urdu_c1_unit07.py")


def normalize_handoff_replacement_order(source: str) -> str:
    lines = source.splitlines()
    exact = [i for i, line in enumerate(lines) if '"**Urdu C1 Unit 7 / sequence 37** using' in line]
    generic = [i for i, line in enumerate(lines) if '"Unit 7 / sequence 37":"Unit 8 / sequence 43"' in line]
    if len(exact) != 1 or len(generic) != 1:
        raise SystemExit(f"FAIL CLOSED: handoff replacement rules not uniquely found: exact={exact}, generic={generic}")
    line = lines.pop(exact[0])
    if not line.rstrip().endswith(","):
        line += ","
    generic = [i for i, item in enumerate(lines) if '"Unit 7 / sequence 37":"Unit 8 / sequence 43"' in item]
    lines.insert(generic[0], line)
    return "\n".join(lines) + "\n"


def install_lexical_collision_repair(source: str) -> str:
    if "def repair_known_target_collision(existing):" in source:
        return source
    marker = "def validate_passages(existing):\n"
    if marker not in source:
        raise SystemExit("FAIL CLOSED: validate_passages marker missing")
    helper = textwrap.dedent('''
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

    ''')
    source = source.replace(marker, helper + marker, 1)
    old = '    ids = [p["id"] for p in existing]\n    if seqs == list(range(1,37)):\n'
    new = '    ids = [p["id"] for p in existing]\n    baseline_targets = existing[:-6] if seqs == list(range(1,43)) and ids[-6:] == EXPECTED_IDS else existing\n    repair_known_target_collision(baseline_targets)\n    if seqs == list(range(1,37)):\n'
    if old not in source:
        raise SystemExit("FAIL CLOSED: main frontier marker missing")
    return source.replace(old, new, 1)


def main() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    source = normalize_handoff_replacement_order(source)
    source = install_lexical_collision_repair(source)
    SCRIPT.write_text(source, encoding="utf-8")
    print("Prepared Urdu C1 Unit 7 canonicalizer with guarded lexical collision repair")


if __name__ == "__main__":
    main()
