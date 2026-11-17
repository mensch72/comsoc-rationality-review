# Pilot report and codebook freeze

## Pilot set

The pilot papers come from the 2020 editions of the frame venues, which are outside the frame years. They were taken in the seeded order (seed `…|pilot`, `data/pilot_order.csv`), skipping papers without an open full text and papers ineligible on full text.

| Rank | Paper | Note |
|---|---|---|
| 1 | AAAI-2020-429f79e2 | |
| 2, 3, 11 | GEB-2020-c4347ca3, GEB-2020-39b4f2fc, SCW-2020-232966d7 | No reachable open version: none found, or the repository answered with a bot check |
| 4–6, 8–10 | SCW-2020-3ce9126a, AAMAS-2020-a97d8031, AAAI-2020-5ed76ce1, IJCAI-2020-66ae0b81, AAMAS-2020-8d22fd28, AAAI-2020-bc793d9b | |
| 7 | JET-2020-9bae8f43 | Working-paper version |
| 12 | MSS-2020-23d57a67 | Coded, but ineligible on full text (C0 = INELIG by both passes). Not counted among the 10 |
| 13 | SCW-2020-b8c44316 | HAL post-print |
| 14 | AAMAS-2020-cfe4e788 | Replaces rank 12 |

A 2-page AAAI student abstract (AAAI-2020-1303e3cc) was found during the pilot. All AAAI tracks named "Student" are now excluded. This exclusion affects only the 2020 pilot frame: in 2021–2025, student papers share an issue with EAAI and were already excluded.

## Agreement, codebook v0.1

Pass A used the larger model and pass B a smaller one. Over 11 papers, 64 items were compared. Items with κ < 1:

| Item | Agreement | κ | Diagnosis | Revision in v1.0 |
|---|---|---|---|---|
| C6.CAN.present | 0.55 | −0.17 | Coders differed on whether candidates that are only alternatives count as "present" | Presence now requires an agent who takes an action in the formal model |
| C6.OTH.present | 0.82 | −0.10 | Same issue | OTH restricted to acting agents that fit no other type |
| C7.1 | 0.64 | 0.46 | N vs NA follows from the presence disagreement | NA tied explicitly to the C6 definition |
| C8.2 | 0.64 | 0.52 | N vs NA when no agent is strategic | NA if C8.1 is NA |
| C5.1 | 0.73 | 0.55 | Coders differed on whether motivation-only statements count | C5.1 covers definitions, results and experiments; narrative claims go to C9.1 |
| C5.2 | 0.73 | 0.63 | Follows from C5.1 | — |
| C8.1:NE, COAL, OTH | 0.82–0.91 | 0.0 | One disagreement each at very low prevalence (the κ paradox) | DEV redefined to include optimisation problems (control, bribery, districting) |
| C4.1 | 0.91 | 0.82 | A briber's costs were read as utilities | Only voters' utility-type notions trigger C4.1 |
| C3.1–C3.3 | 0.91 | 0.82–0.87 | Experiment with free choice: ALL vs SOME | Experiments with free choice are coded ALL |

Agreement was perfect (κ = 1 or no variation) on C0, C1.primary, C2.3, C2.4, C4.2, C7.2, C9.1, C9.2 and C10.1. With only 10 papers, that says little about the main sample. C9.2 was coded SOME-UNSTATED in most pilot papers by both passes. Guidance was therefore added to v1.0 so that only assumptions needed for a claim to follow count, and assumptions generic to all modelling do not.

**Quote check** (`scripts/check_quotes.py`): pass A 154/154 quotes found verbatim in the text, pass B 130/133. The first check found many misses. They came from `pdftotext -layout` interleaving two-column pages, not from the coders. Extraction was switched to reading order.

## Freeze

The codebook was frozen as **v1.0** on 2026-11-17. The SHA-256 of `protocol/codebook.md` begins `a630a2333e399c67`. The v1.0 revisions were not re-piloted, to save cost. Their effect is visible only in the κ values of the main sample.
