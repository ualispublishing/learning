# Reading Curriculum Task List

This is the **active operational queue**. Historical calibration/review work belongs in git history and audit artifacts; do not infer current state from old unchecked items.

## Arabic — COMPLETE / APPROVED

- [x] A1–C2: 360 passages / 3,600 questions / 3,600 linked answers.
- [x] Final Arabic review through Pass 12 = `PASS`; formal final approval = `true`.
- [x] Zero current final-approval blockers.

Do not reopen Arabic unless canonical Arabic content is deliberately changed.

## French — ACTIVE

### A1 — GENERATED / INTEGRITY PASS / CLOSED TO ROUTINE REGENERATION

- [x] Units 01–10 / sequences 1–60 generated.
- [x] 60 passages / 600 questions / 600 linked answers.
- [x] Every Unit P06 checkpoint has zero deliberately new lexical targets.
- [x] Generation-integrity closeout = `PASS` with 100 deliberate targets and no remaining integrity failures.
- [x] Current A1 canonical blob: `0493a2fa13e51b5997db05e91cdea4d8dc5e647b`.

A1 has not yet gone through the final language-wide multi-pass French approval audit; do not broadly regenerate it.

### A2 — ACTIVE

- [x] Unit 01 / sequences 1–6.
- [x] Unit 02 / sequences 7–12.
- [x] Unit 03 / sequences 13–18.
- [x] Unit 04 / sequences 19–24; first run failed closed on exact `perdre` visibility, then passed after a natural exact-form repair.
- [x] Unit 05 / sequences 25–30; passed all guards first run.
- [x] Unit 06 / sequences 31–36; first run rejected duplicate target `place`, then passed with fresh `visite` replacing it.
- [x] All completed A2 units: 6 passages / 60 Q / 60 A / 10 new targets / zero-new P06 each.
- [x] Current A2 canonical blob after Unit 06: `9abd3006e264234e6b5ff2f7c9d37e56cf807fa9`.
- [ ] Unit 07 / sequences 37–42: generate as one guarded batch against the live Unit-06 blob.
- [ ] Review Unit-06 targets one pair per P01–P05 where natural; keep P06 zero-new-target.
- [ ] Check every proposed Unit-07 new target against A1 and all prior A2 deliberate targets before writing.
- [ ] Continue A2 in coherent six-passage guarded batches to 60 passages.

A2 Unit 01 targets: `retard`, `conseil`, `erreur`, `expliquer`, `essayer`, `possible`, `réparer`, `éviter`, `rendez-vous`, `découvrir`.

A2 Unit 02 targets: `raison`, `résultat`, `décision`, `information`, `important`, `différent`, `habitude`, `expérience`, `choix`, `idée`.

A2 Unit 03 targets: `oublier`, `clé`, `perdre`, `retrouver`, `recevoir`, `envoyer`, `vérifier`, `payer`, `numéro`, `carte`.

A2 Unit 04 targets: `projet`, `équipe`, `réunion`, `responsable`, `programme`, `dossier`, `demande`, `réponse`, `service`, `contact`.

A2 Unit 05 targets: `médecin`, `patient`, `douleur`, `santé`, `hôpital`, `accident`, `soin`, `urgence`, `risque`, `danger`.

A2 Unit 06 targets: `voyage`, `train`, `route`, `départ`, `hôtel`, `chambre`, `retour`, `visite`, `plan`, `avion`.

Remaining French levels:

- [ ] A2: 24 passages remain after Unit 06.
- [ ] B1: 60 passages.
- [ ] B2: 60 passages.
- [ ] C1: 60 passages.
- [ ] C2: 60 passages.

Production policy:

- generation-first, full multi-pass audit at the completed French corpus milestone;
- A2 standard passages use the 140–220-word planning band and controlled lexical load;
- fail closed on lexical-source drift, cross-level target duplication, canonical blob drift, schema failure, linkage failure, invisible deliberate review, reader-facing contamination, or sequence collision;
- do not mutate the root validated lexical CSV merely to simplify passage production.

## Urdu — QUEUED

- [x] A1 sequences 1–6 exist in `reading/urdu/a1/passages.jsonl`.
- [ ] A1 sequences 7–60.
- [ ] A2–C2: 60 passages each.

Keep Urdu unchanged while French is active unless explicitly reprioritized.

## Throughput rules

- Work in coherent unit/batch scopes, not passage-by-passage workflows.
- One live-state/collision check + one guarded script + one relevant validation run per batch.
- Full multi-pass audit is a final-stage operation, not a per-generation-batch tax.
- Fail closed on source drift or invariant failure, then repair the same batch rather than weakening the guard.
- Serialize writers to the same canonical/audit artifact.

## Immediate next task

**Generate French A2 Unit 07 / sequences 37–42 against canonical A2 blob `9abd3006e264234e6b5ff2f7c9d37e56cf807fa9`. Keep Arabic sealed.**
