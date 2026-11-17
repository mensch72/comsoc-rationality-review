#!/usr/bin/env python3
"""Check that evidence quotes in codings occur verbatim (up to whitespace, case, hyphenation and
ligatures) in the paper text. Reports per coding the number of quotes found / checked and lists misses.
Usage: python3 scripts/check_quotes.py CODING_DIR TEXT_DIR [--verbose]
"""
import glob, json, os, re, sys, unicodedata


def norm(s):
    s = unicodedata.normalize("NFKC", s).lower()
    s = re.sub(r"-\s*\n\s*", "", s)              # hyphenation at line breaks
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"[^a-z0-9]+", " ", s)             # drop punctuation and maths symbols
    return re.sub(r"\s+", " ", s).strip()


def quotes(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k.startswith("quote") and isinstance(v, str):
                yield v
            else:
                yield from quotes(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from quotes(v)


def main():
    cdir, tdir = sys.argv[1], sys.argv[2]
    verbose = "--verbose" in sys.argv
    tot = hit = 0
    for p in sorted(q for q in glob.glob(os.path.join(cdir, "*.json")) if not os.path.basename(q).startswith("_")):
        pid = os.path.basename(p)[:-5]
        text = norm(open(os.path.join(tdir, pid + ".txt"), errors="replace").read())
        d = json.load(open(p))
        qs = [q for q in quotes(d) if q.strip() and "none found" not in q.lower()]
        miss = [q for q in qs if norm(q) and norm(q) not in text]
        tot += len(qs); hit += len(qs) - len(miss)
        print(f"{pid}: {len(qs) - len(miss)}/{len(qs)} quotes found")
        if verbose:
            for q in miss:
                print("   MISS:", q[:100])
    print(f"TOTAL {hit}/{tot} = {hit / max(tot, 1):.3f}")


if __name__ == "__main__":
    main()
