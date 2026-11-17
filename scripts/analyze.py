#!/usr/bin/env python3
"""Outcome measures (protocol section 6), weighting, confidence intervals and the dataset spreadsheet.

Inputs:  data/sample_final.csv, data/allocation.csv, data/codings/final/*.json, data/codings/{A,B}/*.json,
         data/ineligible_fulltext.csv, data/retrieval.csv, data/frame_raw.csv, data/sample_skipped.csv
Outputs: results/outcomes.csv          weighted population estimates with stratified-bootstrap 95% CIs
         results/by_venue_type.csv     unweighted proportions with Wilson 95% CIs
         results/by_paper_type.csv     same, by primary paper type (C1.primary)
         results/stakeholders.csv      O2 per stakeholder type
         results/reliability.csv       A vs B per item (scripts/agreement.py) on eligible sample papers
         results/replacements.csv      unavailable / ineligible / duplicate per venue
         data/dataset.xlsx             one row per paper: bibliography, version, codes, evidence
"""
import csv, glob, json, math, os, random, subprocess, sys
from collections import Counter, defaultdict

random.seed(20261117)
os.makedirs("results", exist_ok=True)
g = lambda d, k: ((d.get(k) or {}).get("code") or "").upper()

sample = list(csv.DictReader(open("data/sample_final.csv")))
# realised n_h (differs from data/allocation.csv where a stratum spilled over, see scripts/finalize_sample.py)
n_real = Counter(r["stratum"] for r in sample)
alloc = {r["stratum"]: (int(r["N_h"]), n_real[r["stratum"]]) for r in csv.DictReader(open("data/allocation.csv"))}
final = {p: json.load(open(f"data/codings/final/{p}.json")) for p in (r["paper_id"] for r in sample)}
VT = {r["paper_id"]: r["venue_type"] for r in sample}

# ---------- eligibility rate per venue type (all papers coded on full text, eligible or not) ----------
# C0 decision per coded paper: A and B agree -> that code; otherwise pass C's decision.
frame = {r["paper_id"]: r for r in csv.DictReader(open("data/frame_raw.csv"))}
def c0(d, p):
    alt = f"data/codings/B_C0_stop/{p}.json"   # pass B as first run (stopped at C0) for papers re-run after adjudication
    path = alt if d == "B" and os.path.exists(alt) else f"data/codings/{d}/{p}.json"
    return g(json.load(open(path)), "C0")
coded_all = sorted(os.path.basename(x)[:-5] for x in glob.glob("data/codings/A/*.json"))
C0 = {}
for p in coded_all:
    a, b = c0("A", p), c0("B", p)
    if a == b:
        C0[p] = a
    else:
        C0[p] = g({"C0": json.load(open(f"data/codings/C/{p}.json"))["decisions"]["C0"]["value"]}, "C0")
el = defaultdict(lambda: [0, 0])
for p in coded_all:
    vt = frame[p]["venue_type"]
    el[vt][1] += 1
    el[vt][0] += C0[p] == "ELIG"
erate = {vt: e / n for vt, (e, n) in el.items()}
c0_pairs = [(c0("A", p), c0("B", p)) for p in coded_all]

# ---------- outcome measures per paper (None = not applicable) ----------
def O0(d): return int(g(d, "C5.1") == "N" and g(d, "C9.1") == "N")
def O1(d): c = g(d, "C2.4"); return None if c in ("ONE", "") else int(c in ("DIST", "IDJ", "IDS"))
def O1_reason(d): c = g(d, "C2.4"); return None if c not in ("IDJ", "IDS") else int(c == "IDJ")
def O1_dist(d): c = g(d, "C2.4"); return None if c in ("ONE", "") else int(c == "DIST")
def O3(d): return int(g(d, "C9.2") == "SOME-UNSTATED" or (g(d, "C5.1") == "Y" and g(d, "C5.2") == "INPUT-UNSTATED"))
def O3_cond(d): return O3(d) if (g(d, "C5.1") == "Y" or g(d, "C9.1") == "Y") else None
def O3_welfare_input(d): return None if g(d, "C5.1") != "Y" else int(g(d, "C5.2") == "INPUT-UNSTATED")
def O3_claims(d): return None if g(d, "C9.1") != "Y" else int(g(d, "C9.2") == "SOME-UNSTATED")
def O4(d): return None if g(d, "C3.2") in ("NA", "") else int(g(d, "C3.2") == "STATED")
def O4_reason(d): return None if g(d, "C3.2") in ("NA", "") else int(g(d, "C3.2") == "STATED" and g(d, "C3.3") not in ("NONE", "NA", ""))
def O5(d): return None if g(d, "C4.1") in ("NA", "") else int(g(d, "C4.1") == "SPEC")
def O5_dich(d): return None if g(d, "C4.2") in ("NA", "") else int(g(d, "C4.2") == "Y")
def O2b(d): return None if g(d, "C7.1") in ("NA", "") else int(g(d, "C7.1") == "Y")
def O2b_reason(d): return None if g(d, "C7.1") != "Y" else int(g(d, "C7.2") == "REASON")
def procedural_explicit(d): return int(g(d, "C10.1") == "Y")
# post hoc (added after the results, at the researcher's request): non-strategic voters without a stated reason, of all papers
def O4_unjust_all(d): return 0 if g(d, "C3.2") in ("NA", "") else 1 - O4_reason(d)

MEASURES = [
    ("O0", "Purely procedural: no welfare-type criteria in results and no claims beyond results", O0),
    ("O1", "Relation between submitted input and held preferences stated (DIST, IDJ or IDS), of papers referring to held preferences", O1),
    ("O1a", "Input and held preferences explicitly distinguished (DIST)", O1_dist),
    ("O1b", "Reason given, among papers stating that input equals preferences", O1_reason),
    ("O3", "Welfare-type or interpretive claim resting on an unstated assumption (all eligible papers)", O3),
    ("O3c", "O3 among papers making welfare-type results or claims beyond results", O3_cond),
    ("O3w", "Welfare-type criteria evaluated on inputs without stated relation to preferences, among papers with such criteria", O3_welfare_input),
    ("O3i", "Some assumption needed for claims beyond results unstated, among papers making such claims", O3_claims),
    ("O4", "Sincerity stated, among papers with non-strategic analyses and held preferences", O4),
    ("O4r", "Sincerity stated with a reason (same denominator)", O4_reason),
    ("O4u", "Post hoc: voters non-strategic in some analysis, without a stated reason (all eligible papers)", O4_unjust_all),
    ("O5", "Link between ordinal/approval inputs and utilities specified, where utility-type notions are used", O5),
    ("O5d", "Meaning of dichotomous preferences stated, where the term is used", O5_dich),
    ("O2b", "Some stakeholder strategic while another is not, among papers with two or more acting types", O2b),
    ("O2br", "Reason given for that difference", O2b_reason),
    ("P", "Paper states an explicitly procedural reading (C10.1)", procedural_explicit),
]

eligible = [r for r in sample if g(final[r["paper_id"]], "C0") == "ELIG"]
if len(eligible) != len(sample):
    print(f"WARNING: {len(sample) - len(eligible)} sample papers are not ELIG in final codings", file=sys.stderr)

# weights: N_h estimated eligible = N_h(frame) * eligibility rate of the venue type
def weight(r):
    N, n = alloc[r["stratum"]]
    return N * erate.get(r["venue_type"], 1.0) / n


def wmean(rows, f):
    num = den = 0.0
    for r in rows:
        v = f(final[r["paper_id"]])
        if v is None:
            continue
        w = weight(r); num += w * v; den += w
    return (num / den) if den else None


def boot(rows, f, B=2000):
    by = defaultdict(list)
    for r in rows:
        by[r["stratum"]].append(r)
    est = []
    for _ in range(B):
        res = [x for st in by.values() for x in (random.choice(st) for _ in st)]
        m = wmean(res, f)
        if m is not None:
            est.append(m)
    est.sort()
    return est[int(.025 * len(est))], est[int(.975 * len(est)) - 1]


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0, c - h), min(1, c + h)


def fmt(x):
    return "" if x is None else round(x, 3)


rows = []
for key, label, f in MEASURES:
    vals = [f(final[r["paper_id"]]) for r in eligible]
    n = sum(v is not None for v in vals); k = sum(v for v in vals if v is not None)
    est = wmean(eligible, f); lo, hi = boot(eligible, f) if n else (None, None)
    rows.append(dict(measure=key, label=label, n=n, k=k, unweighted=fmt(k / n if n else None),
                     weighted=fmt(est), ci_lo=fmt(lo), ci_hi=fmt(hi)))
with open("results/outcomes.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)


def domain_table(keyf, path):
    out = []
    groups = sorted({keyf(r) for r in eligible})
    for key, label, f in MEASURES:
        for gname in groups:
            vals = [f(final[r["paper_id"]]) for r in eligible if keyf(r) == gname]
            n = sum(v is not None for v in vals); k = sum(v for v in vals if v is not None)
            lo, hi = wilson(k, n)
            out.append(dict(measure=key, group=gname, n=n, k=k, p=fmt(k / n if n else None), ci_lo=fmt(lo), ci_hi=fmt(hi)))
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)


domain_table(lambda r: r["venue_type"], "results/by_venue_type.csv")
domain_table(lambda r: (final[r["paper_id"]].get("C1") or {}).get("primary", "").upper() or "NA", "results/by_paper_type.csv")

# ---------- O2 per stakeholder type ----------
st_rows = []
for t in ["VOT", "CAN", "ORG", "DIS", "BRI", "DES", "OTH"]:
    pres = [final[r["paper_id"]]["C6"][t] for r in eligible
            if ((final[r["paper_id"]].get("C6") or {}).get(t) or {}).get("present", "").upper().startswith("Y")]
    strat = [s for s in pres if (s.get("behav") or "").upper() in ("STRAT", "MIXED")]
    beh = Counter((s.get("behav") or "").upper() for s in pres)
    bexp = sum((s.get("behav_stated") or "").upper() == "EXPLICIT" for s in pres)
    iexp = sum((s.get("info_stated") or "").upper() == "EXPLICIT" for s in strat)
    ins = sum((s.get("info") or "").upper() == "NS" for s in strat)
    st_rows.append(dict(type=t, present=len(pres), strat_or_mixed=len(strat), nonstrat=beh.get("NONSTRAT", 0), behav_ns=beh.get("NS", 0),
                        behav_explicit=bexp, behav_explicit_share=fmt(bexp / len(pres) if pres else None),
                        info_explicit_among_strategic=iexp, info_explicit_share=fmt(iexp / len(strat) if strat else None),
                        info_not_specified_among_strategic=ins))
with open("results/stakeholders.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(st_rows[0].keys())); w.writeheader(); w.writerows(st_rows)

# ---------- reliability on eligible sample papers ----------
import shutil, tempfile
tmp = tempfile.mkdtemp()
for d in ("A", "B"):
    os.makedirs(os.path.join(tmp, d))
    for r in eligible:
        shutil.copy(f"data/codings/{d}/{r['paper_id']}.json", os.path.join(tmp, d))
subprocess.run([sys.executable, "scripts/agreement.py", os.path.join(tmp, "A"), os.path.join(tmp, "B"),
                "--out", "results/reliability.csv", "--disagree", os.path.join(tmp, "dis.json")], check=True)
# derived-measure agreement
A = {r["paper_id"]: json.load(open(f"data/codings/A/{r['paper_id']}.json")) for r in eligible}
Bc = {r["paper_id"]: json.load(open(f"data/codings/B/{r['paper_id']}.json")) for r in eligible}


def kappa(pairs):
    n = len(pairs); po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n ** 2
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


der = []
for key, label, f in MEASURES:
    pairs = [(f(A[p]), f(Bc[p])) for p in A]
    pairs = [(str(a), str(b)) for a, b in pairs]
    der.append(dict(item="derived:" + key, n=len(pairs), agree=round(sum(a == b for a, b in pairs) / len(pairs), 3),
                    kappa=round(kappa(pairs), 3)))
der.append(dict(item="C0 (all coded papers)", n=len(c0_pairs), agree=round(sum(a == b for a, b in c0_pairs) / len(c0_pairs), 3),
                kappa=round(kappa(c0_pairs), 3)))
with open("results/reliability_derived.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(der[0].keys())); w.writeheader(); w.writerows(der)

# ---------- replacements per venue ----------
sk = list(csv.DictReader(open("data/sample_skipped.csv")))
rep = Counter((s["venue"], s["reason"].split(":")[0].split(" of ")[0]) for s in sk)
with open("results/replacements.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["venue", "reason", "count"])
    for (v, rsn), c in sorted(rep.items()):
        w.writerow([v, rsn, c])
with open("results/eligibility_rate.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["venue_type", "eligible", "coded", "rate"])
    for vt, (e, n) in sorted(el.items()):
        w.writerow([vt, e, n, round(e / n, 3)])

# ---------- dataset spreadsheet ----------
from openpyxl import Workbook
from openpyxl.styles import Font
ITEMS = ["C0", "C1", "C2.1", "C2.2", "C2.3", "C2.4", "C3.1", "C3.2", "C3.3", "C4.1", "C4.2", "C5.1", "C5.2",
         "C7.1", "C7.2", "C8.1", "C8.2", "C9.1", "C9.2", "C10.1"]
retr = {r["paper_id"]: r for r in csv.DictReader(open("data/retrieval.csv"))}
wb = Workbook(); ws = wb.active; ws.title = "papers"
head = ["paper_id", "venue", "venue_type", "year", "stratum", "replacement", "title", "authors", "doi", "url_used", "version", "version_note", "weight"]
for it in ITEMS:
    head += [f"{it}", f"{it}_loc", f"{it}_quote", f"{it}_note"]
for t in ["VOT", "CAN", "ORG", "DIS", "BRI", "DES", "OTH"]:
    head += [f"C6.{t}.{a}" for a in ("present", "behav", "behav_stated", "info", "info_stated", "evidence")]
head += [k for k, _, _ in MEASURES] + ["adjudicated_items"]
ws.append(head)
for c in ws[1]:
    c.font = Font(bold=True)
for r in sample:
    p = r["paper_id"]; d = final[p]; fr = frame[p]; rt = retr.get(p, {})
    row = [p, r["venue"], r["venue_type"], r["year"], r["stratum"], r.get("replacement"), fr["title"], fr["authors"], fr["doi"],
           rt.get("fulltext_url"), rt.get("version_type"), rt.get("version_note"), round(weight(r), 3)]
    for it in ITEMS:
        e = d.get(it) or {}
        if it == "C1":
            v = f"{','.join(e.get('types', []))} (primary {e.get('primary', '')})"
        elif "codes" in e:
            v = ",".join(e.get("codes", []))
        elif it == "C2.1":
            v = e.get("value", "")
        else:
            v = e.get("code", "")
        q = e.get("quote", "")
        if it == "C9.1" and e.get("claims"):
            q = " / ".join(f"{c.get('quote', '')} [{c.get('loc', '')}]" for c in e["claims"])
        row += [v, e.get("loc", ""), q, e.get("note", "")]
    for t in ["VOT", "CAN", "ORG", "DIS", "BRI", "DES", "OTH"]:
        s = (d.get("C6") or {}).get(t) or {}
        ev = "; ".join(x for x in [f"{s.get('loc_behav', '')}: {s.get('quote_behav', '')}", f"{s.get('loc_info', '')}: {s.get('quote_info', '')}"] if x.strip(": "))
        row += [s.get("present", ""), s.get("behav", ""), s.get("behav_stated", ""), s.get("info", ""), s.get("info_stated", ""), ev]
    row += [f(d) for _, _, f in MEASURES] + [", ".join((d.get("adjudication") or {}).keys())]
    ws.append(row)
ws2 = wb.create_sheet("outcomes")
for i, r in enumerate(rows):
    if i == 0:
        ws2.append(list(r.keys()))
    ws2.append(list(r.values()))
ws3 = wb.create_sheet("readme")
for line in ["One row per sampled paper (n=150). Codes follow protocol/codebook.md v1.0; *_loc is the location and *_quote a verbatim quote (<=12 words) as evidence.",
             "Final codes = pass A where A and B agree, pass C (adjudication) where they disagree; see adjudicated_items.",
             "Coding was done by language models (Claude Opus 5.5 pass A and adjudication, Claude Sonnet 5.5 pass B) under the supervision of the commissioning researcher.",
             "weight = estimated eligible papers in the stratum / sampled papers in the stratum. Measures O* are 1/0, empty where not applicable (protocol section 6).",
             "PDFs are not redistributed; url_used gives the legally open version that was coded."]:
    ws3.append([line])
wb.save("data/dataset.xlsx")
print("eligibility rates:", {k: round(v, 3) for k, v in erate.items()})
for r in rows:
    print(f"{r['measure']:5s} n={r['n']:3d} unweighted={r['unweighted']} weighted={r['weighted']} [{r['ci_lo']}, {r['ci_hi']}]")
