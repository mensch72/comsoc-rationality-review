#!/usr/bin/env python3
"""Stratified random draw for the comsoc rationality study.

Input:  data/frame_screened.csv  (frame_raw.csv plus column `screen` in {include, exclude, unsure})
Output: data/sample_order.csv    every eligible paper with stratum, rank within stratum,
                                  in_sample flag (first n_h) and replacement-queue position.
        data/allocation.csv      N_h, n_h, weight per stratum.

Order within a stratum is by SHA-256(SEED + "|" + paper_id): reproducible and independent of
Python version. Allocation: floor per venue type, remainder proportional (largest remainder),
then proportional over years within venue type with at least 1 per non-empty stratum.
See protocol/sampling_protocol.md, section 4.

Usage: python3 scripts/draw_sample.py [--seed SEED] [--n 150] [--floor 20] [--exclude-ids ID,...]
"""
import argparse, csv, hashlib, math
from collections import defaultdict

SEED = "comsoc-rationality-2026-11-17"


def largest_remainder(total, weights, minimum=None):
    """Integer allocation of `total` proportional to `weights` (dict), with optional per-key minimum."""
    minimum = minimum or {k: 0 for k in weights}
    alloc = dict(minimum)
    rest = total - sum(alloc.values())
    assert rest >= 0, "minimums exceed total"
    W = sum(weights.values())
    quotas = {k: rest * weights[k] / W for k in weights}
    for k in weights:
        alloc[k] += math.floor(quotas[k])
    left = total - sum(alloc.values())
    for k in sorted(weights, key=lambda k: quotas[k] - math.floor(quotas[k]), reverse=True)[:left]:
        alloc[k] += 1
    return alloc


def capped(total, sizes, minimum):
    """Proportional allocation capped at stratum size; surplus redistributed."""
    alloc = largest_remainder(total, sizes, minimum)
    while any(alloc[k] > sizes[k] for k in sizes):
        surplus = sum(max(0, alloc[k] - sizes[k]) for k in sizes)
        full = {k for k in sizes if alloc[k] >= sizes[k]}
        for k in full:
            alloc[k] = sizes[k]
        open_ = {k: sizes[k] for k in sizes if k not in full}
        if not open_:
            break
        extra = largest_remainder(surplus, open_)
        for k in extra:
            alloc[k] += extra[k]
    return alloc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", default="data/frame_screened.csv")
    ap.add_argument("--seed", default=SEED)
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--floor", type=int, default=20)
    ap.add_argument("--exclude-ids", default="", help="comma-separated paper_ids removed from the frame")
    ap.add_argument("--out", default="data/sample_order.csv")
    ap.add_argument("--alloc-out", default="data/allocation.csv")
    a = ap.parse_args()

    excl = set(filter(None, a.exclude_ids.split(",")))
    rows = [r for r in csv.DictReader(open(a.frame))
            if r["screen"] in ("include", "unsure") and r["excluded_format"] == "0" and r["paper_id"] not in excl]

    strata = defaultdict(list)
    for r in rows:
        strata[(r["venue_type"], int(r["year"]))].append(r)
    vt_size = defaultdict(int)
    for (vt, _), lst in strata.items():
        vt_size[vt] += len(lst)

    n_vt = capped(a.n, dict(vt_size), {vt: min(a.floor, vt_size[vt]) for vt in vt_size})
    alloc = {}
    for vt in vt_size:
        sizes = {y: len(strata[(v, y)]) for (v, y) in strata if v == vt}
        alloc.update({(vt, y): k for y, k in capped(n_vt[vt], sizes, {y: 1 for y in sizes}).items()})

    out = []
    for key, lst in sorted(strata.items()):
        lst.sort(key=lambda r: hashlib.sha256(f"{a.seed}|{r['paper_id']}".encode()).hexdigest())
        for i, r in enumerate(lst):
            r = dict(r, stratum=f"{key[0]}-{key[1]}", rank=i + 1, in_sample=int(i < alloc[key]),
                     queue_pos=max(0, i + 1 - alloc[key]))
            r.pop("abstract", None)
            out.append(r)

    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    with open(a.alloc_out, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["stratum", "N_h", "n_h", "weight"])
        for key in sorted(strata):
            N, n = len(strata[key]), alloc[key]
            w.writerow([f"{key[0]}-{key[1]}", N, n, round(N / n, 4) if n else ""])
    wts = [len(strata[k]) / alloc[k] for k in strata for _ in range(alloc[k])]
    deff = len(wts) * sum(x * x for x in wts) / sum(wts) ** 2  # Kish design effect from unequal weights
    print(f"n={sum(alloc.values())}, frame N={len(rows)}, Kish deff={deff:.3f}, "
          f"half-width at p=.5: {1.96 * math.sqrt(deff * 0.25 / sum(alloc.values())):.3f}")


if __name__ == "__main__":
    main()
