#!/usr/bin/env python3
"""Retrieve legally open full texts for sampled papers (protocol section 3).

Order: venue open version (AAMAS, IJCAI, AAAI, COMSOC) -> publisher OA (Crossref CC licence;
Springer PDFs only, since sciencedirect.com and dl.acm.org refuse this environment) -> open
locations listed by OpenAlex for the DOI (repositories, arXiv, publisher OA) -> arXiv title search
(title similarity >= 0.9 and a shared author surname) -> manual URL found by web search
(column `manual_url` in the input, with `manual_version`). Otherwise status = needs_search.

PDFs and extracted text go to --cache (outside the repository; never committed).
Usage: python3 scripts/fetch_fulltext.py IN.csv OUT.csv --cache DIR
"""
import argparse, csv, difflib, json, os, re, subprocess, sys, time, urllib.error, urllib.parse, urllib.request

UA = "comsoc-rationality-review/0.1 (research; open-access retrieval)"


def get(url, binary=False, timeout=90, tries=5):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.read()
                return (data, r.headers.get("Content-Type", "")) if binary else data.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and k < tries - 1:
                time.sleep(int(e.headers.get("Retry-After") or 0) or 10 * 2 ** k)
                continue
            raise


def norm(s):
    return re.sub(r"[^a-z0-9 ]", "", re.sub(r"\s+", " ", s.lower())).strip()


def surnames(authors):
    return {norm(a).split()[-1] for a in re.split(r";|,| and ", authors) if norm(a)}


def venue_pdf(r):
    v, u = r["venue"], r["url"]
    if v in ("AAMAS", "COMSOC"):
        return u
    if v == "IJCAI":
        m = re.search(r'href="(/proceedings/\d+/\d+\.pdf)"', get(u))
        return "https://www.ijcai.org" + m.group(1) if m else None
    if v == "AAAI":
        m = re.search(r'href="https://ojs.aaai.org/index.php/AAAI/article/view/(\d+)/(\d+)"', get(u))
        return f"https://ojs.aaai.org/index.php/AAAI/article/download/{m.group(1)}/{m.group(2)}" if m else None
    return None


def publisher_oa(r):
    if not r.get("doi"):
        return None
    m = json.loads(get("https://api.crossref.org/works/" + urllib.parse.quote(r["doi"])))["message"]
    if not any("creativecommons" in l.get("URL", "") for l in m.get("license", [])):
        return None
    for l in m.get("link", []):
        if l.get("content-type") == "application/pdf" and "springer" in l["URL"]:
            return l["URL"]
    return None


def openalex(r):
    """Open-access PDF locations for the DOI, as listed by OpenAlex (Unpaywall data)."""
    if not r.get("doi"):
        return []
    try:
        w = json.loads(get("https://api.openalex.org/works/doi:" + urllib.parse.quote(r["doi"]), tries=3))
    except Exception:
        return []
    out = []
    for loc in w.get("locations", []):
        if loc.get("is_oa") and loc.get("pdf_url"):
            src = (loc.get("source") or {}).get("display_name") or ""
            kind = ("arXiv" if "arxiv" in loc["pdf_url"] else
                    "publisher-OA" if loc.get("version") == "publishedVersion" else "repository")
            out.append((loc["pdf_url"], kind, f"OpenAlex location: {src}; version={loc.get('version')}"))
    return out


def arxiv(r):
    t = re.sub(r"[^\w ]", " ", r["title"])
    q = urllib.parse.quote(" AND ".join(f"ti:{w}" for w in t.split() if len(w) > 3)[:900])
    time.sleep(3)  # arXiv API etiquette
    feed = get(f"https://export.arxiv.org/api/query?search_query={q}&max_results=10", tries=1)  # API often rate-limited; OpenAlex covers most arXiv versions
    best = None
    for e in re.findall(r"<entry>(.*?)</entry>", feed, re.S):
        title = re.sub(r"\s+", " ", re.search(r"<title>(.*?)</title>", e, re.S).group(1))
        sim = difflib.SequenceMatcher(None, norm(title), norm(r["title"])).ratio()
        names = " ; ".join(re.findall(r"<name>(.*?)</name>", e))
        if sim >= 0.9 and surnames(names) & surnames(r["authors"]):
            aid = re.search(r"<id>http://arxiv.org/abs/(.*?)</id>", e).group(1)
            upd = re.search(r"<updated>(.*?)</updated>", e).group(1)[:10]
            if not best or sim > best[0]:
                best = (sim, aid, upd)
    return best


def extract(pdf_path, txt_path):
    subprocess.run(["pdftotext", "-layout", pdf_path, txt_path], check=True, timeout=180)
    pages = subprocess.run(["pdfinfo", pdf_path], capture_output=True, text=True).stdout
    m = re.search(r"Pages:\s+(\d+)", pages)
    return int(m.group(1)) if m else "", os.path.getsize(txt_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out"); ap.add_argument("--cache", required=True)
    a = ap.parse_args()
    os.makedirs(a.cache, exist_ok=True)
    rows = list(csv.DictReader(open(a.inp)))
    out = []
    for r in rows:
        res = dict(paper_id=r["paper_id"], status="needs_search", version_type="", fulltext_url="",
                   version_note="", text_path="", pdf_pages="", text_bytes="")
        try:
            cands = []
            if r.get("manual_url"):
                cands.append((r["manual_url"], r.get("manual_version", "manual"), r.get("manual_note", "")))
            else:
                if (u := venue_pdf(r)):
                    cands.append((u, "venue", "published version"))
                if not cands and (u := publisher_oa(r)):
                    cands.append((u, "publisher-OA", "published version, CC licence"))
                if not cands:
                    cands += openalex(r)
                if not cands:
                    try:
                        if (b := arxiv(r)):
                            cands.append((f"https://arxiv.org/pdf/{b[1]}", f"arXiv {b[1]}", f"updated {b[2]}; title sim {b[0]:.2f}"))
                    except Exception as e:
                        res["version_note"] = f"arXiv search failed: {str(e)[:80]}"
            errs = []
            for cand in cands:
                try:
                    data, ctype = get(cand[0], binary=True, tries=2)
                    if not data.startswith(b"%PDF"):
                        raise RuntimeError(f"not a PDF ({ctype})")
                except Exception as e:
                    errs.append(f"{cand[0][:60]}: {str(e)[:60]}")
                    continue
                pdf = os.path.join(a.cache, r["paper_id"] + ".pdf")
                txt = os.path.join(a.cache, r["paper_id"] + ".txt")
                open(pdf, "wb").write(data)
                pages, nbytes = extract(pdf, txt)
                res.update(status="ok", version_type=cand[1], fulltext_url=cand[0], version_note=cand[2],
                           text_path=txt, pdf_pages=pages, text_bytes=nbytes)
                break
            if res["status"] != "ok" and errs:
                res["version_note"] = (res["version_note"] + " | tried: " + " ; ".join(errs))[:400]
        except Exception as e:
            res.update(status="error", version_note=str(e)[:200])
        print(r["paper_id"], res["status"], res["version_type"], file=sys.stderr)
        out.append(res)
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)


if __name__ == "__main__":
    main()
