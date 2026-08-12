# wordfreq attribution

The final Urdu continuation verification workflow may use `wordfreq` only as a supplemental corpus-ranking signal after exhausting the primary CLE Urdu top-5000 frequency pool. Supplemental entries are admitted only when they also have a CFILT IWN-En `Direct` Urdu↔English WordNet semantic mapping.

`wordfreq` is by Robyn Speer and provides multi-source word-frequency estimates. Project: `rspeer/wordfreq`. The repository identifies the software as Apache-licensed and frequency data as including Creative Commons Attribution-ShareAlike 4.0 material; see the upstream project for full source-specific licensing and attribution details.

Recommended software citation from the upstream project:

Robyn Speer. (2022). *rspeer/wordfreq: v3.0* (v3.0.2). Zenodo. DOI: 10.5281/zenodo.7199437.

This repository does not copy or publish a wordfreq wordlist. The library is queried during verification to rank a small supplemental set of already independently validated Urdu lexical entries.
