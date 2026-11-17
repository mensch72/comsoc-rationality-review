#!/usr/bin/env python3
"""Apply the replacement rule (protocol sections 2.1, 3 and 4) and write the final sample.

For each stratum, papers are visited in seeded order (data/sample_order.csv). A paper is taken if a
legal open full text was retrieved, it is not a duplicate of a paper already taken in another stratum,
and it was not found ineligible on full text (data/ineligible_fulltext.csv, from codebook item C0).
Visiting stops when n_h papers are taken. Papers skipped on the way are recorded with the reason.

Inputs:  data/sample_order.csv, data/allocation.csv, data/retrieval.csv, data/duplicates.csv,
         data/ineligible_fulltext.csv (optional)
Outputs: data/sample_final.csv (taken papers), data/sample_skipped.csv (skipped with reason),
         and a per-venue table of replacements on stdout.
"""
import csv, os
from collections import Counter, defaultdict

order = list(csv.DictReader(open("data/sample_order.csv")))
alloc = {r["stratum"]: int(r["n_h"]) for r in csv.DictReader(open("data/allocation.csv"))}
retr = {r["paper_id"]: r for r in csv.DictReader(open("data/retrieval.csv"))}
dups = {r["paper_id"]: r["duplicate_of"] for r in csv.DictReader(open("data/duplicates.csv"))}
inel = {}
if os.path.exists("data/ineligible_fulltext.csv"):
    inel = {r["paper_id"]: r["reason"] for r in csv.DictReader(open("data/ineligible_fulltext.csv"))}

by = defaultdict(list)
for r in order:
    by[r["stratum"]].append(r)


def exhausted(st, target):
    """True if stratum st cannot supply `target` usable papers from its full frame list."""
    ok = sum(1 for r in by[st] if r["paper_id"] in retr and retr[r["paper_id"]]["status"] == "ok"
             and r["paper_id"] not in dups and r["paper_id"] not in inel)
    untried = sum(1 for r in by[st] if r["paper_id"] not in retr)
    return untried == 0 and ok < target


# Protocol section 4: a stratum with fewer eligible papers than allocated gives its surplus to the other
# years of the same venue type: to the year with the largest N_h (ties: earliest year), repeatedly.
target = dict(alloc)
N = {r["stratum"]: int(r["N_h"]) for r in csv.DictReader(open("data/allocation.csv"))}
for st in sorted(target):
    while exhausted(st, target[st]):
        ok = sum(1 for r in by[st] if retr.get(r["paper_id"], {}).get("status") == "ok"
                 and r["paper_id"] not in dups and r["paper_id"] not in inel)
        surplus = target[st] - ok; target[st] = ok
        vt = st.rsplit("-", 1)[0]
        others = sorted((s for s in target if s.rsplit("-", 1)[0] == vt and s != st and not exhausted(s, target[s] + 1)),
                        key=lambda s: (-N[s], s))
        target[others[0]] += surplus
        print(f"spill-over: {st} has {ok} usable papers; {surplus} moved to {others[0]}")
alloc = target
taken, skipped, short = [], [], []
for st, lst in sorted(by.items()):
    lst.sort(key=lambda r: int(r["rank"]))
    k = 0
    for r in lst:
        if k == alloc[st]:
            break
        pid = r["paper_id"]
        rr = retr.get(pid)
        if rr is None:
            short.append(st)  # next candidate not yet tried: retrieval must be run for it
            break
        reason = ("duplicate of " + dups[pid]) if pid in dups else \
                 ("ineligible on full text: " + inel[pid]) if pid in inel else \
                 None if rr["status"] == "ok" else "unavailable: " + (rr["version_note"] or "no open version")[:120]
        if reason:
            skipped.append(dict(paper_id=pid, stratum=st, venue=r["venue"], rank=r["rank"],
                                original_in_sample=r["in_sample"], reason=reason))
            continue
        k += 1
        taken.append(dict(r, replacement=int(r["in_sample"] == "0"), **{f: rr[f] for f in
                     ("version_type", "fulltext_url", "version_note", "pdf_pages")}))

fields = list(taken[0].keys())
with open("data/sample_final.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(taken)
with open("data/sample_skipped.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["paper_id", "stratum", "venue", "rank", "original_in_sample", "reason"])
    w.writeheader(); w.writerows(skipped)

print(f"taken {len(taken)} / {sum(alloc.values())}; strata needing more retrieval: {sorted(set(short)) or 'none'}")
c = Counter((s["venue"], s["reason"].split(":")[0].split(" of ")[0]) for s in skipped)
print("skipped by venue and reason:")
for k in sorted(c):
    print(f"  {k[0]:7s} {k[1]:28s} {c[k]}")
print("replacements taken by venue:", dict(Counter(t["venue"] for t in taken if t["replacement"])))
