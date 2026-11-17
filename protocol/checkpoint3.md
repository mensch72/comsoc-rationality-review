# Checkpoint 3: coding, adjudication and analysis complete

## Sample

150 eligible papers. To reach them, 194 papers were coded.

| Reason for replacement | Count | By venue |
|---|---|---|
| Ineligible on full text | 39 coded (37 in the sample sequence) | AAMAS 7, SCW 7, EC 6, GEB 4, COMSOC 4, IJCAI 3, AAAI 2, JET 2, MSS 2 |
| No legal open version | 27 | MSS 12, SCW 11, JET 2, GEB 1, EC 1 |
| Duplicate | 1 | GEB |

EC 2022 ran out of usable papers, so its surplus of 1 moved to EC 2023 (protocol §4).

Eligibility rates by venue type, used in the weights: AI conferences 0.78, COMSOC 0.89, EC 0.80, journals 0.76.

## Coding and adjudication

- **Passes.** A (Claude Opus 5.5) and B (Claude Sonnet 5.5). The first 22 sample papers were coded agentically; the rest by single API request in batch mode.
- **Adjudication.** Pass C (Claude Opus 5.5) decided 614 contested items: A 520 (85 %), B 66 (11 %), a third code 28 (5 %).
- **Quotes.** 2,263 of the 2,290 quotes in the final codings (98.8 %) occur verbatim in the texts. Most misses differ only in mathematical symbols lost in extraction.

## Reliability (A vs B, n = 150)

| Label | Items |
|---|---|
| Unreliable (κ < 0.40) | C9.2 (0.39), C2.3 (0.35, but 93 % agreement at 95 % prevalence), derived O3i (0.39), O1b (0.25) |
| Moderate | C2.4 (0.50), C3.2 (0.54), C3.3 (0.45), C7.2 (0.51), C9.1 (0.53), O1 (0.54), O3 (0.43), O4 (0.54) |
| Substantial or better | All other items |

Full figures: `results/reliability.csv`, `results/reliability_derived.csv`.

## Coder sensitivity

B codes "not stated" more often than A, and the adjudicator (the same model as A) mostly sided with A. Main estimates, weighted:

| Measure | Final | A only | B only |
|---|---|---|---|
| O1 | 0.69 | 0.70 | 0.53 |
| O3 | 0.48 | 0.45 | 0.66 |

All measures: `results/coder_sensitivity.csv`.

## API spend for this study

| Item | Cost |
|---|---|
| Adjudication batch | $13.47 |
| **Total spend of this study** | **≈ $48.5** |

## Open

The human hand-check of 15 papers. Its results are not in the note yet.
