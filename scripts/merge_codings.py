#!/usr/bin/env python3
"""Merge passes A, B and C into final codings (protocol section 5).

prepare: from A/B disagreements (scripts/agreement.py output) build the per-paper list of top-level
         keys to adjudicate -> adjudication args JSON for scripts/adjudicate_workflow.js.
merge:   final coding = pass A, with each adjudicated key replaced by pass C's decision. Keys where
         A and B agree are taken from A (A and B agree on the code; A's evidence is kept).
Usage:
  python3 scripts/merge_codings.py prepare DISAGREE.json TEXT_DIR CODEBOOK OUTDIR > adj_args.json
  python3 scripts/merge_codings.py merge OUTDIR FINAL_DIR
"""
import glob, json, os, sys


def top_key(item):
    if item.startswith("C1."):
        return "C1"
    if item.startswith("C6."):
        return ".".join(item.split(".")[:2])
    return item.split(":")[0]


def prepare(dis, tdir, codebook, out):
    d = json.load(open(dis))
    papers = [dict(id=pid, text=os.path.join(tdir, pid + ".txt"),
                   items=sorted({top_key(x["item"]) for x in v})) for pid, v in sorted(d.items())]
    print(json.dumps(dict(codebook=codebook, out=out, papers=papers)))


def merge(out, final):
    os.makedirs(final, exist_ok=True)
    n = 0
    for p in sorted(glob.glob(os.path.join(out, "A", "*.json"))):
        pid = os.path.basename(p)[:-5]
        a = json.load(open(p))
        cpath = os.path.join(out, "C", pid + ".json")
        log = {}
        if os.path.exists(cpath):
            c = json.load(open(cpath))
            for key, dec in c.get("decisions", {}).items():
                if key.startswith("C6."):
                    a.setdefault("C6", {})[key.split(".")[1]] = dec["value"]
                else:
                    a[key] = dec["value"]
                log[key] = dict(chosen=dec.get("chosen"), reason=dec.get("reason"))
        a["adjudication"] = log
        json.dump(a, open(os.path.join(final, pid + ".json"), "w"), indent=1)
        n += 1
    print(f"merged {n} codings into {final}")


if __name__ == "__main__":
    if sys.argv[1] == "prepare":
        prepare(*sys.argv[2:6])
    else:
        merge(*sys.argv[2:4])
