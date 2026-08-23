# Language Workbook v1 Final Quality Build

Run the staged v3 linguistic-quality workbook pipeline in pull-request context. The prior external Urdu corpus was rejected; this build must use the controlled Urdu corpus and balanced Arabic/French selection.

Pass order: canonical vocabulary integrity -> 3,000-sentence selection -> full corpus audit plus stratified samples -> 42-PDF build from the approved corpus -> structural/render preflight -> final release cross-gate audit. Every pass is time-boxed and must pass before the next pass proceeds.
