#!/usr/bin/env python3
"""Final staged workbook release profile.

Keeps the v3 pass logic, but uses a source-capacity-aware progression mix:
270 very short, 370 short/medium, 320 medium/long, 40 long sentences.
The global 30% question target, 1,000/1,000 target/English uniqueness,
Arabic register filter, Urdu controlled corpus, and contributor cap remain unchanged.
"""
import sys
import workbook_release_passes as p

p.BAND_TOTALS = {"A": 270, "B": 370, "C": 320, "D": 40}
p.QUESTION_BAND_CAP = {"A": 135, "B": 185, "C": 125, "D": 5}

if __name__ == "__main__":
    p.main()
