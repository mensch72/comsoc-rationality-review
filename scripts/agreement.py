#!/usr/bin/env python3
"""Inter-coder agreement between coding passes A and B (protocol section 5).

Reads one JSON coding per paper from DIR_A and DIR_B (files <paper_id>.json), flattens each into
item-level categorical values, and reports per item: n, % agreement, Cohen's kappa with a bootstrap
95% CI over papers (2000 resamples, fixed seed), and the prevalence of the modal code.
Multi-select items are split into one binary item per category. Stakeholder attributes (C6.*) are
compared only on papers where both coders mark the type present.

Also writes the list of disagreements per paper (for adjudication pass C).
Usage: python3 scripts/agreement.py DIR_A DIR_B --out agreement.csv --disagree disagreements.json
"""
import argparse, csv, glob, json, os, random
from collections import Counter, defaultdict

SINGLE = ["C0", "C1.primary", "C2.3", "C2.4", "C3.1", "C3.2", "C3.3", "C4.1", "C4.2", "C5.1", "C5.2",
          "C7.1", "C7.2", "C8.2", "C9.1", "C9.2", "C10.1"]
MULTI = {"C1.types": ["AX", "AL", "SB", "EQ", "WD", "SI", "EM", "OT"],
         "C2.2": ["RANK", "WEAK", "APPR", "DICH", "CARD", "PAIR", "OTH"],
         "C8.1": ["DOM", "NE", "SPE", "BNE", "ITER", "DEV", "BND", "COAL", "OTH"]}
TYPES = ["VOT", "CAN", "ORG", "DIS", "BRI", "DES", "OTH"]
ATTRS = ["behav", "behav_stated", "info", "info_stated"]


def code_of(d, item):
    if item == "C1.primary":
        return (d.get("C1") or {}).get("primary", "")
    return ((d.get(item) or {}).get("code") or "").strip().upper()


def multi_of(d, item):
    if item == "C1.types":
        return {c.upper() for c in (d.get("C1") or {}).get("types", [])}
    return {c.upper() for c in (d.get(item) or {}).get("codes", [])}


def flatten(d):
    """Map a coding to {item: value}; value None means 'not compared for this paper'."""
    f = {}
    for it in SINGLE:
        f[it] = code_of(d, it).upper() or "MISSING"
    for it, cats in MULTI.items():
        s = multi_of(d, it)
        for c in cats:
            f[f"{it}:{c}"] = "1" if c in s else "0"
    c6 = d.get("C6") or {}
    for t in TYPES:
        e = c6.get(t) or {}
        f[f"C6.{t}.present"] = (e.get("present") or "N").upper()[:1]
        for a in ATTRS:
            f[f"C6.{t}.{a}"] = (e.get(a) or "").upper() or "MISSING"
    return f


def kappa(pairs):
    n = len(pairs)
    if n == 0:
        return None
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n ** 2
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir_a"); ap.add_argument("dir_b")
    ap.add_argument("--out", required=True); ap.add_argument("--disagree", required=True)
    a = ap.parse_args()
    A = {os.path.basename(p)[:-5]: json.load(open(p)) for p in glob.glob(os.path.join(a.dir_a, "*.json"))}
    B = {os.path.basename(p)[:-5]: json.load(open(p)) for p in glob.glob(os.path.join(a.dir_b, "*.json"))}
    ids = sorted(set(A) & set(B))
    FA, FB = {i: flatten(A[i]) for i in ids}, {i: flatten(B[i]) for i in ids}
    items = list(FA[ids[0]].keys())
    rng = random.Random(20261117)
    rows, disagree = [], defaultdict(list)
    for it in items:
        per = []
        for i in ids:
            if it.startswith("C6.") and not it.endswith(".present"):
                t = it.split(".")[1]
                if not (FA[i][f"C6.{t}.present"] == "Y" and FB[i][f"C6.{t}.present"] == "Y"):
                    continue
            per.append((i, FA[i][it], FB[i][it]))
        if not per:
            continue
        pairs = [(x, y) for _, x, y in per]
        k = kappa(pairs)
        boots = []
        for _ in range(2000):
            s = [pairs[rng.randrange(len(pairs))] for _ in pairs]
            kb = kappa(s)
            if kb is not None:
                boots.append(kb)
        boots.sort()
        lo, hi = (boots[int(.025 * len(boots))], boots[int(.975 * len(boots)) - 1]) if boots else ("", "")
        modal = Counter(v for p in pairs for v in p).most_common(1)[0]
        label = ("unreliable" if k < 0.40 else "moderate" if k < 0.60 else "substantial") if k is not None else ""
        if all(x == y for x, y in pairs) and len({x for x, _ in pairs}) == 1:
            label = "no variation"
        rows.append(dict(item=it, n=len(pairs), agree=round(sum(x == y for x, y in pairs) / len(pairs), 3),
                         kappa=round(k, 3), ci_lo=round(lo, 3) if lo != "" else "", ci_hi=round(hi, 3) if hi != "" else "",
                         modal_code=modal[0], modal_prev=round(modal[1] / (2 * len(pairs)), 3), label=label))
        for i, x, y in per:
            if x != y:
                disagree[i].append(dict(item=it, A=x, B=y))
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    json.dump(disagree, open(a.disagree, "w"), indent=1)
    print(f"papers compared: {len(ids)}; items: {len(rows)}; papers with disagreements: {len(disagree)}")


if __name__ == "__main__":
    main()
