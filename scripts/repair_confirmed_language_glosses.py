import csv
import io
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REPAIRS = {
    "urdu_top1000.csv": {
        52: {"front": "ہم", "meaning": "we; us", "pos": "pronoun"},
        59: {"front": "اب", "meaning": "now; at present", "pos": "adverb"},
    },
    "french_top1000.csv": {
        2: {"front": "avoir", "meaning": "to have; to possess; to have to; to be [age] in age expressions; asset/possession (noun)"},
        21: {"front": "pouvoir", "meaning": "can; to be able to; power; authority"},
        22: {"front": "dire", "meaning": "to say; to tell; statement/saying (noun)"},
        51: {"front": "bon", "meaning": "good; right/correct; fine; okay; voucher/coupon (noun)"},
        55: {"front": "penser", "meaning": "to think; to consider; to think about", "pos": "verb"},
    },
}


def field(back, name):
    m = re.search(rf"(?m)^{re.escape(name)}:\s*(.+)$", back)
    return m.group(1).strip() if m else None


def replace_field(back, name, value):
    pattern = rf"(?m)^({re.escape(name)}:\s*).+$"
    if not re.search(pattern, back):
        raise ValueError(f"Missing {name} field")
    return re.sub(pattern, lambda m: m.group(1) + value, back, count=1)


def repair_file(filename, specs):
    path = ROOT / filename
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows or set(rows[0]) != {"Front", "Back"}:
        raise ValueError(f"Unexpected schema: {filename}")

    seen = []
    for row in rows:
        rank_text = field(row["Back"], "Rank")
        if rank_text is None:
            continue
        rank = int(rank_text)
        if rank not in specs:
            continue
        spec = specs[rank]
        if row["Front"].strip() != spec["front"]:
            raise ValueError(f"{filename} rank {rank}: expected {spec['front']!r}, found {row['Front']!r}")
        before_meaning = field(row["Back"], "Meaning")
        row["Back"] = replace_field(row["Back"], "Meaning", spec["meaning"])
        before_pos = field(row["Back"], "Part of speech")
        if "pos" in spec:
            row["Back"] = replace_field(row["Back"], "Part of speech", spec["pos"])
        seen.append({
            "rank": rank,
            "front": spec["front"],
            "before_meaning": before_meaning,
            "after_meaning": spec["meaning"],
            "before_pos": before_pos,
            "after_pos": spec.get("pos", before_pos),
        })

    if {x["rank"] for x in seen} != set(specs):
        raise ValueError(f"{filename}: not all requested repairs were found")

    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=["Front", "Back"], lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    path.write_text(buf.getvalue(), encoding="utf-8")
    return seen


def main():
    report = {"repairs": {}, "gate": "PASS"}
    for filename, specs in REPAIRS.items():
        report["repairs"][filename] = repair_file(filename, specs)
    out = ROOT / "audit" / "confirmed_language_gloss_repairs.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
