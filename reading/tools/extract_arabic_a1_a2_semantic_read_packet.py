#!/usr/bin/env python3
import json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = {
    "a1": ROOT / "reading" / "arabic" / "a1" / "passages.jsonl",
    "a2": ROOT / "reading" / "arabic" / "a2" / "passages.jsonl",
}
OUT = ROOT / "reading" / "audit" / "arabic_a1_a2_semantic_read_packet_2026-08-23.md"

def blob(p):
    return subprocess.check_output(["git", "hash-object", str(p)], text=True).strip()

def load(p):
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]

def one_line(s):
    return " ".join(str(s or "").split())

def main():
    lines = ["# Arabic A1/A2 final semantic/adversarial read packet", ""]
    for level, path in FILES.items():
        rows = load(path)
        lines += [f"# {level.upper()} — 60 passages", f"Blob: `{blob(path)}`", ""]
        for r in rows:
            lines.append(f"## {r['id']} — {one_line(r.get('title'))}")
            lines.append(f"TEXT: {one_line(r.get('text'))}")
            for q in r.get("questions", []):
                a = next((a for a in r.get("answer_key", []) if a.get("question_id") == q.get("id")), {})
                tids = ",".join(q.get("target_ids", []) or [])
                lines.append(f"{q.get('id')} [{q.get('type')}] targets={tids or '-'} :: {one_line(q.get('prompt'))} => {one_line(a.get('answer'))}")
            lines.append("")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")

if __name__ == "__main__":
    main()
