#!/usr/bin/env python3
"""Retry Unit 09 after correcting one grammar-role enum to schema-approved `review`."""
from __future__ import annotations
import generate_french_a2_unit09 as base
for spec in base.SPECS:
    if spec["id"]=="fr-a2-u09-p04":
        spec["grammar"][0]["role"]="review"
base.main()
