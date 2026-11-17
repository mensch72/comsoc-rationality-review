#!/usr/bin/env python3
"""Render final codings as a readable Markdown document (one section per paper, codes with evidence),
plus a blank CSV form for blind hand-coding.
Usage: python3 scripts/render_codings.py FINAL_DIR IDS.csv OUT.md BLANK.csv
IDS.csv needs a column paper_id; bibliographic data come from data/frame_raw.csv and data/retrieval.csv.
"""
import csv, json, os, sys

ITEMS = [("C0", "Eligibility"), ("C1", "Paper type"), ("C2.1", "Name of input"), ("C2.2", "Input format"),
         ("C2.3", "Held attitude present"), ("C2.4", "Input vs held attitude"), ("C3.1", "Strategic voters analysed"),
         ("C3.2", "Sincerity stated"), ("C3.3", "Reason for sincerity"), ("C4.1", "Utility link"),
         ("C4.2", "Dichotomous preferences explained"), ("C5.1", "Welfare-type criteria in results"),
         ("C5.2", "Object of welfare evaluation"), ("C7.1", "Strategic asymmetry"), ("C7.2", "Reason for asymmetry"),
         ("C8.1", "Solution concept"), ("C8.2", "Concept named"), ("C9.1", "Claims beyond results"),
         ("C9.2", "Assumptions behind claims"), ("C10.1", "Explicit procedural reading")]


def cell(s):
    return str(s or "").replace("|", "\\|").replace("\n", " ")


def value(d):
    if "codes" in d:
        return ", ".join(d["codes"]) or "–"
    if "types" in d:
        return f"{', '.join(d['types'])} (primary {d.get('primary', '')})"
    return d.get("code") or d.get("value") or ""


def main(final, ids, out, blank):
    fr = {r["paper_id"]: r for r in csv.DictReader(open("data/frame_raw.csv"))}
    rt = {r["paper_id"]: r for r in csv.DictReader(open("data/retrieval.csv"))}
    pids = [r["paper_id"] for r in csv.DictReader(open(ids))]
    L = []
    for pid in pids:
        d = json.load(open(os.path.join(final, pid + ".json")))
        b, r = fr[pid], rt.get(pid, {})
        L += [f"## {pid}: {b['title']}", "",
              f"{b['authors']}. {b['venue']} {b['year']}. " + (f"DOI [{b['doi']}](https://doi.org/{b['doi']}). " if b["doi"] else ""),
              f"Version coded: {r.get('version_type', '')}, <{r.get('fulltext_url', '')}>. {r.get('version_note', '')}", "",
              "| Item | Code | Location | Quote | Note |", "|---|---|---|---|---|"]
        for key, label in ITEMS:
            e = d.get(key) or {}
            if key == "C9.1" and e.get("claims"):
                q = " / ".join(f"{c.get('quote', '')} ({c.get('loc', '')})" for c in e["claims"])
                L.append(f"| {key} {label} | {cell(value(e))} | | {cell(q)} | {cell(e.get('note'))} |")
            else:
                L.append(f"| {key} {label} | {cell(value(e))} | {cell(e.get('loc'))} | {cell(e.get('quote'))} | {cell(e.get('note'))} |")
            if key == "C5.2":  # stakeholders after welfare items
                for t, s in (d.get("C6") or {}).items():
                    if (s or {}).get("present", "").upper().startswith("Y"):
                        L.append(f"| C6 {t} | behav {cell(s.get('behav'))} ({cell(s.get('behav_stated'))}); info {cell(s.get('info'))} ({cell(s.get('info_stated'))}) "
                                 f"| {cell(s.get('loc_behav'))}; {cell(s.get('loc_info'))} | {cell(s.get('quote_behav'))} / {cell(s.get('quote_info'))} | {cell(s.get('note'))} |")
        adj = d.get("adjudication") or {}
        if adj:
            L += ["", "Adjudicated (pass C): " + "; ".join(f"{k} → {v.get('chosen')} ({v.get('reason')})" for k, v in adj.items())]
        L.append("")
    open(out, "w").write("\n".join(L))
    with open(blank, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["paper_id", "item", "your_code", "location", "quote", "note"])
        for pid in pids:
            for key, _ in ITEMS:
                w.writerow([pid, key, "", "", "", ""])
            for t in ["VOT", "CAN", "ORG", "DIS", "BRI", "DES", "OTH"]:
                w.writerow([pid, f"C6.{t} present/behav/behav_stated/info/info_stated", "", "", "", ""])


if __name__ == "__main__":
    main(*sys.argv[1:5])
