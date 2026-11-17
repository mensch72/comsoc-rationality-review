# Checkpoint 2: status after the pilot, the freeze and the hand-check set

## Done

**Frame.** 22,012 items were listed. 18,818 remained after removing ineligible formats, and 3,294 of those passed the keyword pre-filter.

**Screening.** LLM screening on title and abstract classified 710 items as include or unsure.

- Two screening agents classified with uniform reasons instead of reading the titles. Their batches were redone or screened by hand: `data/frame_screened.csv` has a `screen_method` column.
- Recall check: 0 of 300 titles rejected by the keyword filter were eligible. The 95 % upper bound for missed eligible papers is about 1 % of 15,097, i.e. up to about 150 papers.

**Sample.** 150 papers, drawn with seed `comsoc-rationality-2026-11-17`.

- **Allocation:** AI conferences 43, COMSOC 33, EC 24, journals 50.
- **Unavailable:** 18 drawn papers had no reachable legal open version, so they were replaced:

  | Venue | Unavailable |
  |---|---|
  | MSS | 9 |
  | SCW | 5 |
  | JET | 2 |
  | GEB | 1 |
  | EC | 1 |

  The reasons were: no open version found; Elsevier, SSRN or ACM refusing this environment; or a repository answering with a bot check, which we did not circumvent.
- **Duplicate:** 1 paper (the same work in EC 2025 and GEB 2025).
- **Ineligible on full text:** 7 of the 22 coded papers so far (C0). This rate (32 %) means that screening on titles let through many borderline papers: ML rank aggregation, sports tournaments, sortition, domain recognition, truth discovery, allocation.
  - The frame counts N_h therefore overstate the eligible population.
  - Population weights will be corrected by the eligibility rate observed in the coded sample, per venue type.

**Codebook.** Frozen as v1.0 after a 10-paper pilot; see `pilot_report.md`.

**Hand-check set.** 15 papers, with passes A, B and C done.

- The codes and evidence are in `data/handcheck/handcheck_codes.md`.
- A blank form for coding blind is in `data/handcheck/handcheck_blank_form.csv`.
- All 248 quotes in the final codings occur verbatim in the texts.

## Reliability on the hand-check set (A vs B, n = 15, before adjudication)

| Item | Agreement | κ | Comment |
|---|---|---|---|
| C2.4 input vs held attitude | 0.60 | 0.39 | Unreliable as a 5-way code |
| O1 (C2.4 collapsed: relation stated or not) | 0.80 | 0.61 | Outcome measure for RQ1 |
| C9.2 assumptions behind claims | 0.53 | 0.21 | Unreliable |
| O3 (claim resting on an unstated assumption) | 0.73 | 0.48 | Outcome measure for RQ3 |
| C3.2, C3.3, C4.1, C4.2, C5.2, C7.1 | 0.87–0.93 | 0.75–0.90 | |
| C5.1, C3.1, C8.2 | 1.00 | 1.00 | |

The disagreements are systematic, not random. Pass B (smaller model) codes "not stated" more often:

- O3: 11 of 15 papers by B vs 7 of 15 by A.
- O1: 8 of 15 "stated" by B vs 10 of 15 by A.

The adjudicator (pass C) runs on the same model as pass A and sided with A in most cases. The final codes are therefore close to A's. **This direction is the main open question for the hand-check:** whether a human reader agrees more with A or with B decides whether the adjudicator should change, for example to a third model or to adjudication by the researcher.
