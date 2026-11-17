# How voting papers state rationality assumptions: a coding study

A small systematic coding study of recent papers on voting in social choice and computational social choice (2021–2025). It asks how papers state:

- the relation between preferences and ballots,
- the strategic level and information of each stakeholder,
- the assumptions behind welfare and real-world claims.

## Status

**Checkpoint 2:** pilot done, codebook frozen (v1.0), sample drawn (150), hand-check set of 15 coded. See `protocol/checkpoint2.md`.

## Layout

| Path | Content |
|---|---|
| `protocol/sampling_protocol.md` | Population, frame, sources, screening, allocation, coding procedure, outcome measures |
| `protocol/codebook.md` | Codebook (v0.1 draft; frozen after the pilot) |
| `scripts/build_frame.py` | Enumerates the frame from the venue listings |
| `scripts/draw_sample.py` | Seeded stratified draw, allocation, weights |
| `data/` | Frame, screening decisions, sample, codes. PDFs are never committed |

## Reproducing the frame and the draw

Enumerate the frame from the venue listings:

```bash
python3 scripts/build_frame.py --years 2021-2025 --out data/frame_raw.csv
```

Screening adds a `screen` column, which gives `data/frame_screened.csv`. Then draw the sample:

```bash
python3 scripts/draw_sample.py
```
