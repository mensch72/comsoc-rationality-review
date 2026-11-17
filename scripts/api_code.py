#!/usr/bin/env python3
"""Code papers (passes A/B) or adjudicate disagreements (pass C) with one API request per paper,
through OpenRouter (https://openrouter.ai/api/v1). Replaces the agentic coding of scripts/code_workflow.js
for the main run, to cut token use (protocol section 5, amendment of checkpoint 2).

The API key is injected by the environment's network proxy; no key is read from the environment.

Subcommands
  code   --model M --ids IDS.txt --texts DIR --codebook FILE --out DIR [--sync | --batch]
  adjudicate --model M --disagree DIS.json --a DIR --b DIR --texts DIR --codebook FILE --out DIR [--sync | --batch]
  collect --batch-id ID --out DIR [--kind code|adjudicate]      fetch a finished batch and write files
Every request is logged to OUT/_requests.csv with token use and cost as reported by OpenRouter.
"""
import argparse, concurrent.futures as cf, csv, json, os, re, sys, time, urllib.request, urllib.error

API = "https://openrouter.ai/api/v1"

CODE_INSTRUCTIONS = """You are a research assistant coding one academic paper with a codebook.
Apply the codebook below strictly as written to the paper text that follows it. The paper text was extracted from a PDF; it includes appendices where the PDF has them.
Every quote must be copied verbatim from the paper text and be at most 12 words. Give locations as section and page where visible.
Return ONLY one JSON object that follows the codebook's output template, with "paper_id" set to the given id and "codebook_version" as in the codebook. No text before or after the JSON."""

ADJ_INSTRUCTIONS = """You are the adjudicator for a coding study. Two coders (A and B) independently coded one academic paper with the codebook below and disagree on some items.
For each listed key, decide the correct value under the codebook: A's value, B's value, or a third value if both are wrong. Keep the structure of the output template for that key (for C6.<TYPE> give the whole object for that type; for C1, C2.2 and C8.1 the whole object including lists). Every quote must be verbatim from the paper text, at most 12 words.
Return ONLY one JSON object of the form {"paper_id": "...", "decisions": {"<key>": {"value": <object for that key>, "chosen": "A"|"B"|"other", "reason": "<one sentence>"}}}. No text before or after the JSON."""


def http(method, path, body=None, tries=6):
    for k in range(tries):
        try:
            req = urllib.request.Request(API + path, method=method, headers={"Content-Type": "application/json"},
                                         data=json.dumps(body).encode() if body is not None else None)
            with urllib.request.urlopen(req, timeout=600) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:300]
            if e.code in (429, 500, 502, 503, 504) and k < tries - 1:
                time.sleep(min(120, 5 * 2 ** k)); continue
            raise RuntimeError(f"HTTP {e.code}: {msg}")
        except (urllib.error.URLError, TimeoutError) as e:
            if k < tries - 1:
                time.sleep(min(120, 5 * 2 ** k)); continue
            raise


def extract_json(text):
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        i, j = text.find("{"), text.rfind("}")
        return json.loads(text[i:j + 1])


def code_body(pid, text, codebook, max_tokens):
    return {"max_tokens": max_tokens, "messages": [
        {"role": "system", "content": CODE_INSTRUCTIONS + "\n\n=== CODEBOOK ===\n" + codebook},
        {"role": "user", "content": f"paper_id: {pid}\n\n=== PAPER TEXT ===\n{text}"}]}


def adj_body(pid, text, codebook, a, b, keys, max_tokens):
    return {"max_tokens": max_tokens, "messages": [
        {"role": "system", "content": ADJ_INSTRUCTIONS + "\n\n=== CODEBOOK ===\n" + codebook},
        {"role": "user", "content": f"paper_id: {pid}\nKeys in disagreement: {', '.join(keys)}\n\n=== CODING A ===\n{json.dumps(a)}\n\n"
                                    f"=== CODING B ===\n{json.dumps(b)}\n\n=== PAPER TEXT ===\n{text}"}]}


def log(out, row):
    path = os.path.join(out, "_requests.csv")
    new = not os.path.exists(path)
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["paper_id", "model", "mode", "prompt_tokens", "completion_tokens", "reasoning_tokens", "cost", "status"])
        if new:
            w.writeheader()
        w.writerow(row)


def save(out, pid, model, mode, resp):
    u = resp.get("usage") or {}
    status = "ok"
    try:
        content = resp["choices"][0]["message"]["content"]
        obj = extract_json(content)
        json.dump(obj, open(os.path.join(out, pid + ".json"), "w"), indent=1)
    except Exception as e:
        status = f"parse error: {str(e)[:80]}"
        open(os.path.join(out, pid + ".raw.txt"), "w").write(json.dumps(resp)[:200000])
    log(out, dict(paper_id=pid, model=model, mode=mode, prompt_tokens=u.get("prompt_tokens"),
                  completion_tokens=u.get("completion_tokens"),
                  reasoning_tokens=(u.get("completion_tokens_details") or {}).get("reasoning_tokens"),
                  cost=u.get("cost"), status=status))
    return status


def run(items, model, out, sync, kind):
    """items: list of (pid, body)."""
    os.makedirs(out, exist_ok=True)
    if sync:
        def one(it):
            pid, body = it
            try:
                return pid, save(out, pid, model, "sync", http("POST", "/chat/completions", dict(body, model=model)))
            except Exception as e:
                log(out, dict(paper_id=pid, model=model, mode="sync", status=f"error: {str(e)[:100]}"))
                return pid, f"error: {e}"
        with cf.ThreadPoolExecutor(6) as ex:
            for pid, st in ex.map(one, items):
                print(pid, st, file=sys.stderr)
    else:
        b = http("POST", "/batches", {"endpoint": "/v1/chat/completions", "model": model,
                                      "requests": [{"custom_id": pid, "body": body} for pid, body in items]})
        json.dump(dict(batch_id=b["id"], model=model, kind=kind, n=len(items)), open(os.path.join(out, f"_batch_{b['id']}.json"), "w"))
        print(b["id"], b["status"])


def collect(batch_id, out, kind):
    while True:
        b = http("GET", f"/batches/{batch_id}")
        if b["status"] in ("completed", "failed", "expired", "cancelled"):
            break
        print(b["status"], b["request_counts"], file=sys.stderr); time.sleep(60)
    print(b["status"], b["request_counts"], b.get("usage"))
    for r in b.get("results") or []:
        if r.get("response") and r["response"].get("status_code") == 200:
            save(out, r["custom_id"], b["model"], "batch", r["response"]["body"])
        else:
            log(out, dict(paper_id=r["custom_id"], model=b["model"], mode="batch", status=f"error: {str(r.get('error'))[:100]}"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["code", "adjudicate", "collect"])
    ap.add_argument("--model"); ap.add_argument("--ids"); ap.add_argument("--texts"); ap.add_argument("--codebook")
    ap.add_argument("--out", required=True); ap.add_argument("--disagree"); ap.add_argument("--a"); ap.add_argument("--b")
    ap.add_argument("--batch-id"); ap.add_argument("--kind", default="code")
    ap.add_argument("--sync", action="store_true"); ap.add_argument("--max-tokens", type=int, default=24000)
    a = ap.parse_args()
    if a.cmd == "collect":
        return collect(a.batch_id, a.out, a.kind)
    cb = open(a.codebook).read()
    if a.cmd == "code":
        ids = [l.strip() for l in open(a.ids) if l.strip()]
        items = [(pid, code_body(pid, open(os.path.join(a.texts, pid + ".txt"), errors="replace").read(), cb, a.max_tokens)) for pid in ids]
    else:
        dis = json.load(open(a.disagree))
        items = []
        for pid, keys in dis.items():
            A = json.load(open(os.path.join(a.a, pid + ".json"))); B = json.load(open(os.path.join(a.b, pid + ".json")))
            text = open(os.path.join(a.texts, pid + ".txt"), errors="replace").read()
            items.append((pid, adj_body(pid, text, cb, A, B, keys, a.max_tokens)))
    run(items, a.model, a.out, a.sync, a.cmd)


if __name__ == "__main__":
    main()
