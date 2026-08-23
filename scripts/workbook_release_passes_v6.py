#!/usr/bin/env python3
"""Final naturalness-first release profile.

Keep all v5 correctness/uniqueness/diversity gates, but require only 35 long
sentences because Arabic has 38 qualifying long rows after the hard linguistic,
uniqueness, source-diversity, and register filters. This preserves a margin
without forcing lower-quality material merely to satisfy a round-number quota.
"""
import workbook_release_passes as p
import workbook_release_passes_v5 as v5

v5.MIN_BANDS["D"] = 35

if __name__ == "__main__":
    p.main()
