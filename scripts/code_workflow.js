export const meta = {
  name: 'comsoc-code-papers',
  description: 'Code papers with the codebook: independent passes A (default model) and B (smaller model)',
  phases: [{ title: 'Code', detail: 'pass A and pass B per paper, blind to each other' }],
}
const prompt = (p, pass) => `You are a research assistant coding one academic paper with a codebook.
1. Read the codebook at ${args.codebook} completely.
2. Read the full text of the paper at ${p.text}. It is plain text extracted from a PDF; read all of it (in chunks if it is long), including appendices.
3. Apply the codebook strictly as written. Every quote must be copied verbatim from the text file and be at most 12 words. Give locations as section and page where visible.
4. Write your coding as ONE JSON object following the codebook's output template to ${args.out}/${pass}/${p.id}.json, with "paper_id": "${p.id}" and "codebook_version" as in the codebook. Then check it parses: python3 -c "import json;json.load(open('${args.out}/${pass}/${p.id}.json'))".
Do not open any other file, do not search the web, and do not look at any other coding. Return one line: the paper_id and "ok" or the problem.`
await pipeline(args.papers, p => parallel(args.passes.map(pass => () =>
  agent(prompt(p, pass), { label: `${pass}:${p.id}`, phase: 'Code', ...(pass === 'B' ? { model: 'sonnet' } : {}) }))))
return 'done'
