export const meta = {
  name: 'comsoc-adjudicate',
  description: 'Pass C: adjudicate items where coding passes A and B disagree',
  phases: [{ title: 'Adjudicate', detail: 'one agent per paper with disagreements' }],
}
const prompt = p => `You are the adjudicator for a coding study. Two coders (A and B) independently coded one academic paper with a codebook and disagree on some items.
1. Read the codebook at ${args.codebook}.
2. Read the codings ${args.out}/A/${p.id}.json and ${args.out}/B/${p.id}.json.
3. Read the paper text at ${p.text} as far as needed to decide; check the evidence both coders cite.
Items in disagreement (top-level keys of the JSON template): ${p.items.join(', ')}.
For each of these keys decide the correct value under the codebook. You may choose A's value, B's value, or a third value if both are wrong. Keep the same structure as in the template for that key (for C6.<TYPE> give the whole object for that type; for C1, C2.2 and C8.1 give the whole object including lists). Every quote must be verbatim from the text, at most 12 words.
Write ONE JSON object to ${args.out}/C/${p.id}.json of the form {"paper_id": "${p.id}", "decisions": {"<key>": {"value": <object for that key>, "chosen": "A"|"B"|"other", "reason": "<one sentence>"}}}. Check it parses with python3 -c "import json;json.load(open('${args.out}/C/${p.id}.json'))".
Do not open any other file and do not search the web. Return one line: paper_id and "ok" or the problem.`
await pipeline(args.papers, p => agent(prompt(p), { label: `C:${p.id}`, phase: 'Adjudicate' }))
return 'done'
