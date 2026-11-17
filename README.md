# How voting papers state rationality assumptions: a coding study

A small systematic coding study of recent papers on voting in social choice and computational social choice (2021–2025). It asks how papers state:

- the relation between preferences and ballots,
- the strategic level and information of each stakeholder,
- the assumptions behind welfare and real-world claims.

## Status

**Coding complete.** 150 eligible papers coded (passes A and B) and adjudicated (pass C). Results are in `results/`, the dataset in `data/dataset.xlsx`, and the note in `note/`. See `protocol/checkpoint3.md`.

**Open:** the human hand-check of 15 papers (`data/handcheck/handcheck_blank_form.csv`).

## Layout

| Path | Content |
|---|---|
| `protocol/sampling_protocol.md` | Population, frame, sources, screening, allocation, coding procedure, outcome measures |
| `protocol/codebook.md` | Codebook v1.0 (frozen after the pilot) |
| `scripts/build_frame.py` | Enumerates the frame from the venue listings |
| `scripts/draw_sample.py` | Seeded stratified draw, allocation, weights |
| `scripts/finalize_sample.py`, `scripts/api_code.py`, `scripts/merge_codings.py`, `scripts/check_quotes.py`, `scripts/analyze.py` | Final sample with replacements, API coding and adjudication, merge, quote check, analysis |
| `data/` | Frame, screening decisions, sample, retrieval log, codings (A, B, C, final), calibration case, `dataset.xlsx`. PDFs are never committed |
| `results/` | Outcome estimates, breakdowns, reliability, coder sensitivity, replacements |
| `note/` | The note for the community (HTML source and PDF) |

## Reproducing the frame and the draw

Enumerate the frame from the venue listings:

```bash
python3 scripts/build_frame.py --years 2021-2025 --out data/frame_raw.csv
```

Screening adds a `screen` column, which gives `data/frame_screened.csv`. Then draw the sample:

```bash
python3 scripts/draw_sample.py
```

After coding, produce the final sample, merge the passes and run the analysis:

```bash
python3 scripts/finalize_sample.py
```

```bash
python3 scripts/analyze.py
```
