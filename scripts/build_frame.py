#!/usr/bin/env python3
"""Enumerate the sampling frame (raw listing) for the comsoc rationality study.

Writes data/frame_raw.csv: one row per listed item with venue, venue_type, year,
track, title, authors, url, doi, abstract (if the source provides one) and a
keyword pre-filter flag. Eligibility screening (LLM, title+abstract) is a
separate step and is recorded in data/frame_screened.csv.

Sources (see protocol/sampling_protocol.md, section 2):
  AAMAS  ifaamas.org proceedings contents pages
  IJCAI  ijcai.org/proceedings/{year}
  AAAI   ojs.aaai.org issue archive, volumes 35-39
  EC     Crossref API (ACM DL not reachable from this environment)
  COMSOC comsoc-community.org/proceedings/{year}
  SCW, GEB, JET, MSS  Crossref API by ISSN

Usage: python3 scripts/build_frame.py [--years 2021-2025] [--out data/frame_raw.csv]
"""
import argparse, csv, hashlib, html, json, re, sys, time, urllib.parse, urllib.request

UA = "comsoc-rationality-review/0.1 (research sampling script)"
VENUE_TYPE = {"AAMAS": "AIconf", "IJCAI": "AIconf", "AAAI": "AIconf", "EC": "EC",
              "COMSOC": "COMSOC", "SCW": "Journal", "GEB": "Journal", "JET": "Journal", "MSS": "Journal"}
ISSN = {"SCW": "0176-1714", "GEB": "0899-8256", "JET": "0022-0531", "MSS": "0165-4896"}
EC_PROC = {2020: "10.1145/3391403", 2021: "10.1145/3465456", 2022: "10.1145/3490486",
           2023: "10.1145/3580507", 2024: "10.1145/3670865", 2025: "10.1145/3736252"}
AAAI_VOL = {2020: 34, 2021: 35, 2022: 36, 2023: 37, 2024: 38, 2025: 39}

# Title keyword pre-filter, applied to AI conferences and EC only.
KEYWORDS = re.compile(r"""\b(vot|elect|ballot|approv|committee|multi-?winner|single-?winner|winner|
  participatory|budget|liquid|delegat|proxy|candidat|district|gerrymand|manipulat|brib|
  control(ling)?\ (of\ )?election|condorcet|borda|plurality|majorit|social\ choice|social\ welfare\ function|
  preference\ aggregat|aggregat\w*\ (of\ )?(ordinal\ )?preferences|rank\ aggregat|tournament|apportion|
  proportional|representation|consensus|collective\ decision|referend|poll|chamberlin|monroe|
  kemeny|copeland|schulze|\bstv\b|runoff|run-off|instant-runoff|quorum|jury|single-peaked|single-crossing|
  distortion|metric\ (voting|social)|peer\ (selection|review)|sortition|deliberat)""", re.I | re.X)

EXCL_TRACK = re.compile(r"extended abstract|\[short|blue sky|demo|doctoral|jaamas|keynote|survey|journal track|"
                        r"sister conference|early career|student abstract|senior member|new faculty|eaai|"
                        r"best papers|invited|tutorial|competition", re.I)
EXCL_TITLE = re.compile(r"^(correction|erratum|corrigendum|retraction|editorial|introduction to|"
                        r"preface|book review|comment on|reply to|obituary|in memoriam)\b", re.I)


def get(url, tries=4):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as e:  # network errors: back off and retry
            if k == tries - 1:
                raise RuntimeError(f"cannot reach {url}: {e}")
            time.sleep(2 ** (k + 1))


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def aamas(year):
    base = f"https://www.ifaamas.org/Proceedings/aamas{year}/"
    h = get(base + "forms/contents.htm")
    rows, track = [], ""
    # Walk through section headers (<strong>...</strong>) and paper links in order.
    for m in re.finditer(r'<strong>(.*?)</strong>|<a href="\.\./pdfs/(p\d+)\.pdf"[^>]*>(.*?)</a>(.*?)</p>', h, re.S):
        if m.group(1) is not None:
            t = clean(m.group(1))
            if t and len(t) < 120:
                track = t
            continue
        pid, title, rest = m.group(2), clean(m.group(3)), m.group(4)
        authors = "; ".join(clean(a) for a in re.split(r"<br>", re.sub(r"<i>.*?</i>", "", rest, flags=re.S))[1:] if clean(a))
        rows.append(dict(venue="AAMAS", year=year, track=track, title=title, authors=authors,
                         url=base + f"pdfs/{pid}.pdf", doi="", abstract="", start=int(pid[1:])))
    # The PDF file name gives the start page; length = next start - start. Session headings do not
    # separate full papers from extended abstracts in every year (2023: posters; 2025: no headings),
    # so papers shorter than 6 pages are marked as extended abstracts.
    starts = sorted({r["start"] for r in rows})
    nxt = dict(zip(starts, starts[1:] + [None]))
    for r in rows:
        n = nxt[r.pop("start")]
        r["pages"] = "" if n is None else n - int(re.search(r"p(\d+)\.pdf", r["url"]).group(1))
        if r["pages"] != "" and r["pages"] < 6:
            r["track"] = (r["track"] + " [short: extended abstract]").strip()
    return rows


def ijcai(year):
    url = f"https://www.ijcai.org/proceedings/{year}/"
    h = get(url)
    rows, track = [], ""
    for m in re.finditer(r'section_title">\s*<h3>([^<]*)</h3>|<a class="title" href="(/proceedings/\d+/\d+)">(.*?)</a>\s*<div class="authors">(.*?)</div>', h, re.S):
        if m.group(1) is not None:
            track = clean(m.group(1)); continue
        rows.append(dict(venue="IJCAI", year=year, track=track, title=clean(m.group(3)),
                         authors="; ".join(clean(a) for a in re.findall(r">([^<]+)</a>", m.group(4))),
                         url="https://www.ijcai.org" + m.group(2), doi="", abstract=""))
    return rows


def aaai_issues():
    out = {}
    for p in range(1, 15):
        try:
            h = get(f"https://ojs.aaai.org/index.php/AAAI/issue/archive/{p}", tries=1)
        except RuntimeError as e:
            if "404" in str(e):  # past the last archive page
                break
            raise
        found = re.findall(r'<a class="title" href="https://ojs.aaai.org/index.php/AAAI/issue/view/(\d+)">\s*(.*?)\s*</a>\s*<div class="series">\s*(.*?)\s*</div>', h, re.S)
        if not found:
            break
        for iid, title, series in found:
            mv = re.search(r"Vol\. (\d+)", series)
            if mv:
                out.setdefault(int(mv.group(1)), []).append((iid, clean(title)))
    return out


def aaai(year, issues):
    rows = []
    for iid, ititle in issues.get(AAAI_VOL[year], []):
        h = get(f"https://ojs.aaai.org/index.php/AAAI/issue/view/{iid}")
        for m in re.finditer(r'<a id="article-\d+" href="([^"]+)">(.*?)</a>.*?<div class="authors">(.*?)</div>', h, re.S):
            rows.append(dict(venue="AAAI", year=year, track=ititle, title=clean(m.group(2)),
                             authors=clean(m.group(3)).replace(", ", "; "), url=m.group(1), doi="", abstract=""))
    return rows


def crossref(params):
    items, cursor = [], "*"
    while True:
        q = dict(params, rows="1000", cursor=cursor)
        d = json.loads(get("https://api.crossref.org/works?" + urllib.parse.urlencode(q)))["message"]
        items += d["items"]
        if not d["items"] or len(items) >= d["total-results"]:
            return items
        cursor = d["next-cursor"]


def cr_row(venue, year, it, track=""):
    au = "; ".join(f"{a.get('given', '')} {a.get('family', '')}".strip() for a in it.get("author", []))
    return dict(venue=venue, year=year, track=track, title=clean((it.get("title") or [""])[0]), authors=au,
                url="https://doi.org/" + it["DOI"], doi=it["DOI"], abstract=clean(it.get("abstract", "")))


def ec(year):
    pref = EC_PROC[year] + "."
    meta = json.loads(get("https://api.crossref.org/works/" + EC_PROC[year]))["message"]
    its = crossref({"query.container-title": meta["title"][0],
                    "filter": f"prefix:10.1145,type:proceedings-article,from-pub-date:{year-1}-06-01,until-pub-date:{year+1}-06-30"})
    return [cr_row("EC", year, it) for it in its if it["DOI"].lower().startswith(pref)]


def journal(venue, year):
    its = crossref({"filter": f"issn:{ISSN[venue]},type:journal-article,from-pub-date:{year-1}-01-01,until-pub-date:{year+1}-12-31"})
    rows = []
    for it in its:
        y = it.get("issued", {}).get("date-parts", [[None]])[0][0]
        if y == year:
            rows.append(cr_row(venue, year, it))
    return rows


def comsoc(year):
    h = get(f"https://comsoc-community.org/proceedings/{year}/")
    rows, track = [], ""
    for m in re.finditer(r'<h2>([^<]*)</h2>|<li><p>\s*(.*?)<br>\s*<strong>(.*?)</strong>.*?href="([^"]+\.pdf)"', h, re.S):
        if m.group(1) is not None:
            track = clean(m.group(1)); continue
        rows.append(dict(venue="COMSOC", year=year, track=track, title=clean(m.group(2)),
                         authors=re.sub(r"\s*,\s*|\s+and\s+", "; ", clean(m.group(3))).strip("; "),
                         url="https://comsoc-community.org" + m.group(4), doi="", abstract=""))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", default="2021-2025")
    ap.add_argument("--venues", default="AAMAS,IJCAI,AAAI,EC,COMSOC,SCW,GEB,JET,MSS")
    ap.add_argument("--out", default="data/frame_raw.csv")
    a = ap.parse_args()
    y0, y1 = map(int, a.years.split("-"))
    venues = a.venues.split(",")
    rows, issues = [], None
    for y in range(y0, y1 + 1):
        for v in venues:
            try:
                if v == "AAMAS": r = aamas(y)
                elif v == "IJCAI": r = ijcai(y)
                elif v == "AAAI":
                    issues = issues or aaai_issues(); r = aaai(y, issues)
                elif v == "EC": r = ec(y)
                elif v == "COMSOC":
                    if y % 2 == 0: continue  # biennial: no edition in even years
                    r = comsoc(y)
                else: r = journal(v, y)
            except RuntimeError as e:
                sys.exit(f"STOP: listing unreachable for {v} {y}: {e}")
            if not r:
                sys.exit(f"STOP: listing for {v} {y} parsed to zero items; check source")
            print(f"{v} {y}: {len(r)} items", file=sys.stderr)
            rows += r
    for r in rows:
        r["venue_type"] = VENUE_TYPE[r["venue"]]
        # Stable ID: does not depend on enumeration order.
        key = re.sub(r"[^a-z0-9]", "", r["title"].lower()) + "|" + r["url"]
        r["paper_id"] = f"{r['venue']}-{r['year']}-{hashlib.sha1(key.encode()).hexdigest()[:8]}"
        r["excluded_format"] = int(bool(EXCL_TRACK.search(r["track"]) or EXCL_TITLE.search(r["title"])
                                        or "(extended abstract)" in r["title"].lower()))
        r["kw_pass"] = int(r["venue_type"] not in ("AIconf", "EC") or bool(KEYWORDS.search(r["title"])))
    cols = ["paper_id", "venue", "venue_type", "year", "track", "pages", "title", "authors", "url", "doi",
            "excluded_format", "kw_pass", "abstract"]
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, restval=""); w.writeheader(); w.writerows(rows)
    print(f"wrote {len(rows)} rows to {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
