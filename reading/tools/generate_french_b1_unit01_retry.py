#!/usr/bin/env python3
"""Retry B1 Unit 01 with corrected repository-relative reading paths."""
from pathlib import Path
import generate_french_b1_unit01 as base

REPO=Path(__file__).resolve().parents[2]
base.A1=REPO/'reading'/'french'/'a1'/'passages.jsonl'
base.A2=REPO/'reading'/'french'/'a2'/'passages.jsonl'
base.CANON=REPO/'reading'/'french'/'b1'/'passages.jsonl'
base.SCHEMA=REPO/'reading'/'schema'/'passage.schema.json'
base.main()
