# Language Workbook v1 Build Trigger

This branch exists to run the production-candidate workbook build in a pull-request context so its GitHub Actions run, logs, release artifact, and generated PDFs can be inspected before merge.

## Quality rebuild

Trigger the second release run after the first artifact was rejected for Urdu linguistic defects and excessive Arabic/French question concentration. The replacement run must use `build_language_workbooks_v1_quality.py` and pass the v2 corpus-quality gates before merge.
