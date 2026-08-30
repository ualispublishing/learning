# LANG-WB native / near-native sign-off

## Language reviewed

- [ ] Arabic
- [ ] French
- [ ] Urdu

## Reviewer confirmation

- [ ] I am a native speaker or a near-native expert with a qualification basis stated in the submitted sign-off record.
- [ ] I reviewed the **complete learner-facing current master workbook**, not only a sample or automated report.
- [ ] I independently judged meaning/translation fidelity, grammar/morphology, spelling/orthography, naturalness/idiom/register, learner appropriateness, and relevant script/punctuation details.
- [ ] I did not treat automated checks, language-model output, or earlier editorial passes as a substitute for my human review.

## Structured worksheet

- [ ] I used or otherwise fully covered the 1,000 vocabulary and 1,000 sentence items for this language.
- [ ] If I used the generated ledger, I ran `python scripts/validate_lang_wb_native_review_ledger.py <language>` against my completed worksheet.
- [ ] Any FAIL/HOLD item is documented rather than silently converted to PASS.

## Candidate binding

- [ ] My sign-off uses the current candidate identifiers, preferably from `audit/language-workbooks/v1.0/native-review-ledgers/CANDIDATE_BINDINGS.json` generated for the candidate I reviewed.
- [ ] I did not copy stale hashes from an older sign-off.
- [ ] This PR does **not** modify the reviewed master workbook, release manifest, source companion CSVs, or sentence-decision data. If the candidate changes, I understand the sign-off must be rebound/reviewed as required.

## Outcome

- [ ] PASS — full required scope completed, with no known defect or unresolved hold remaining.
- [ ] FAIL — one or more identified defects remain and are documented.
- [ ] HOLD — one or more items cannot yet be confidently adjudicated and are documented.

## Submission

- [ ] I added a **new immutable JSON record** under `audit/language-workbooks/v1.0/native-signoffs/` using `FINAL_NATIVE_SIGNOFF_TEMPLATE.json`.
- [ ] The filename begins with the same declared language plus `_`: `arabic_`, `french_`, or `urdu_`.
- [ ] `review_completed_utc` is the real timezone-aware completion time of this review.
- [ ] I have not modified, renamed, or deleted any previously committed sign-off record; a later outcome is submitted as another new file.
- [ ] I expect CI to validate this addition on the pull request before merge.

### If the committer is not the linguistic reviewer

- [ ] The reviewer authored the submitted human-review fields; the committer did not fill or reinterpret them on the reviewer's behalf.
- [ ] The reviewer identity/qualification stored inside the JSON remains the authoritative reviewer identity; the GitHub commit author is not being presented as the linguistic reviewer.
- [ ] The returned record was preserved unchanged in substance. If the reviewer supplied a SHA-256 checksum, it was checked before submission.
- [ ] Any incomplete, malformed, stale, FAIL, or HOLD review was **not** upgraded to PASS by the maintainer.

A valid single-language submission may still leave the overall LANG-WB release on human-review HOLD while the other languages are pending. That is expected; the all-language promotion gate passes only when Arabic, French, and Urdu each have a valid latest PASS bound to the current candidate.
