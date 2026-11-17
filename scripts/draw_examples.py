#!/usr/bin/env python3
"""Draw the anonymised examples of claims resting on unstated assumptions for the note (post hoc).
Papers with O3 = 1 are ordered by SHA-256(SEED + "|examples|" + paper_id); the first five with
claims beyond the formal results (C9.1 = Y) are printed with their claims and the coders' notes."""
import csv, hashlib, json
SEED = "comsoc-rationality-2026-11-17|examples"
S = {r["paper_id"]: r for r in csv.DictReader(open("data/sample_final.csv"))}
def g(d, k): return (d.get(k) or {}).get("code")
o3 = []
for p in S:
    d = json.load(open(f"data/codings/final/{p}.json"))
    if g(d, "C9.2") == "SOME-UNSTATED" or (g(d, "C5.1") == "Y" and g(d, "C5.2") == "INPUT-UNSTATED"):
        o3.append((p, d))
o3.sort(key=lambda x: hashlib.sha256((SEED + "|" + x[0]).encode()).hexdigest())
print(len(o3), "papers with O3 = 1")
for p, d in [x for x in o3 if g(x[1], "C9.1") == "Y"][:5]:
    print("##", p, d["C1"]["primary"], S[p]["title"])
    print("   C9.2 note:", d["C9.2"].get("note", ""))
    for c in d["C9.1"].get("claims", []):
        print("   claim:", c.get("loc"), "|", c.get("quote"))
