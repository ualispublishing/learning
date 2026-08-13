import csv
import io
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    2: ("avoir", "to have; to possess; to have to; to be [age]", "auxiliary verb / verb"),
    51: ("bon", "good; correct; fine/okay; voucher/coupon (noun)", "adjective / noun / interjection"),
}


def field(back, name):
    m = re.search(rf"(?m)^{re.escape(name)}:\s*(.+)$", back)
    return m.group(1).strip() if m else None


def set_field(back, name, value):
    return re.sub(rf"(?m)^({re.escape(name)}:\s*).+$", lambda m: m.group(1) + value, back, count=1)


def main():
    path = ROOT / "french_top1000.csv"
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    changes = []
    for row in rows:
        rank = int(field(row["Back"], "Rank"))
        if rank not in TARGETS:
            continue
        front, meaning, pos = TARGETS[rank]
        if row["Front"].strip() != front:
            raise SystemExit(f"rank {rank}: unexpected front")
        old = field(row["Back"], "Meaning")
        row["Back"] = set_field(row["Back"], "Meaning", meaning)
        row["Back"] = set_field(row["Back"], "Part of speech", pos)
        changes.append({"rank": rank, "front": front, "before": old, "after": meaning, "pos": pos})
    if len(changes) != 2:
        raise SystemExit("Expected exactly two French refinements")
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=["Front", "Back"], lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    path.write_text(buf.getvalue(), encoding="utf-8")
    (ROOT / "audit" / "confirmed_french_gloss_refinement.json").write_text(json.dumps({"changes": changes, "gate": "PASS"}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
