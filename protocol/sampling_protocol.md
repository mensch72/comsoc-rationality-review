# Sampling and coding protocol

Status: **v0.2. Checkpoint 1 passed (2026-11-17).**

Decisions at checkpoint 1:

- Crossref is the listing source for EC and the four journals.
- The calibration paper stays in the frame.
- The allocation (floor of 20 per venue type), the borderline defaults in §2.3 and the use of different models for passes A and B are approved as proposed.
- The orchestration should be whichever option is cheaper.
- Elsevier full texts are reached only through author versions; see §3.
Seed (fixed, recorded): `SEED = "comsoc-rationality-2026-11-17"`.

## 1. Research questions

For recent papers on collective decisions by voting:

- **RQ1.** How often is the relation between what voters hold (preferences, utilities) and what they submit (ballots) stated?
- **RQ2.** How often are each stakeholder type's strategic level and information stated?
- **RQ3.** How often do papers make welfare or real-world claims that depend on assumptions the paper does not state?
- **RQ0 (counter-position).** How many papers are purely procedural: they treat the rule as a map from submitted inputs to outcomes and make no welfare or real-world claim? Such papers are reported as not at fault, and are excluded from the denominators of RQ1 and RQ3 where the question does not apply.

## 2. Population and frame

**Population.** Research papers whose main object is a procedure that aggregates the inputs of several agents into a collective decision by voting, or the strategic or computational aspects of such a procedure. This includes single-winner and multi-winner voting, approval-based committees, participatory budgeting, liquid democracy and delegation, strategic candidacy, districting, and manipulation, control and bribery. Excluded: fair division, matching, and the borderline classes listed in §2.3 unless decided otherwise at checkpoint 1.

**Frame years.** The last five complete years: 2021–2025.

**Frame venues and listing sources.**

| Venue | Venue type | Listing source used | Reachable (probed 2026-11-17) | Tracks or items in frame |
|---|---|---|---|---|
| AAMAS | AI conference | ifaamas.org/Proceedings/aamas{Y}/forms/contents.htm | yes | Main-track full papers. Excludes extended abstracts, Blue Sky, demos, doctoral consortium, JAAMAS track, keynotes. Session headings do not separate extended abstracts reliably (2023: poster sessions; 2025: no headings). An item is therefore treated as an extended abstract if it is shorter than 6 pages, measured from the start pages in the PDF file names |
| IJCAI | AI conference | ijcai.org/proceedings/{Y}/ | yes | Main track and special tracks with full papers (e.g. AI for Good). Excludes survey, journal, sister-conference, early-career, doctoral consortium, demo tracks |
| AAAI | AI conference | ojs.aaai.org issue archive, Vol. 35–39 | yes | Technical and special tracks. Excludes student abstracts, demos, senior-member and new-faculty talks, EAAI, doctoral consortium |
| ACM EC | EC conference | **Crossref API** (ACM DOI prefixes 10.1145/3465456, 3490486, 3580507, 3670865, 3736252) | dl.acm.org returns **403** to this environment; Crossref yes | All papers, including abstract-only entries (§3) |
| COMSOC workshop | Workshop | comsoc-community.org/proceedings/{Y} | yes; **biennial: 2021, 2023, 2025 only** | Presentations and posters |
| Social Choice and Welfare | Journal | **Crossref API**, ISSN 0176-1714 | Springer site redirects; Crossref yes | Research articles |
| Games and Economic Behavior | Journal | **Crossref API**, ISSN 0899-8256 | sciencedirect.com returns **403**; Crossref yes | Research articles |
| Journal of Economic Theory | Journal | **Crossref API**, ISSN 0022-0531 | sciencedirect.com returns **403**; Crossref yes | Research articles |
| Mathematical Social Sciences | Journal | **Crossref API**, ISSN 0165-4896 | sciencedirect.com returns **403**; Crossref yes | Research articles |

dblp is behind a bot challenge, and OpenAlex and Semantic Scholar rate-limit this environment (HTTP 429), so none of them is used. Crossref is the DOI registration agency's record of what the publisher registered. It is a different access route to the same listing, not a different listing. **This substitution needs approval at checkpoint 1.**

**Smoke test (2023, raw items before screening).**

| Venue | Items |
|---|---|
| AAMAS | 528 |
| IJCAI | 851 |
| AAAI | 2,021 |
| EC | 162 |
| COMSOC | 72 |
| SCW | 50 |
| GEB | 170 |
| JET | 140 |
| MSS | 60 |

The EC 2023 Crossref list (162) was checked against the conference's own accepted-papers page (ec23.sigecom.org), which also lists 162. The 16 titles that are not identical differ only in wording between the accepted and the final version. Journal counts are lower than issue counts because articles are assigned by first publication date.

**Year assignment.** Conferences and the workshop: the edition year. Journals: the year of Crossref's `issued` date, which is the earliest of print and online publication.

**Calibration paper.** Heitzig, Simmons and Constantino (2024), *Social Choice and Welfare*, [doi:10.1007/s00355-024-01524-3](https://doi.org/10.1007/s00355-024-01524-3), stays in the frame like any other paper, as decided at checkpoint 1. It is also coded separately as the calibration case. If it is drawn, the sample codes and the calibration codes come from the same procedure and are reported as such.

### 2.1 Unit and duplicates

The unit is a **venue appearance**. A workshop paper that later appears at a conference is one unit in the COMSOC stratum and one unit in the conference stratum. If the same work is drawn in two strata, the later draw is replaced from its own stratum and the event is recorded. Within one stratum, duplicates (same normalised title, overlapping authors) are merged.

### 2.2 Eligibility screening (before the draw)

1. **Enumeration.** All items from the sources above, with title, authors and track, plus an abstract where the source provides one (Crossref often does; AAMAS, IJCAI and COMSOC listings do not).
2. **Keyword pre-filter** (AI conferences and EC only, which are large and mostly off-topic). A title passes if it matches the regular expressions in `scripts/build_frame.py:KEYWORDS`. SCW, COMSOC, GEB, JET and MSS are not pre-filtered: every item goes to step 3.
   - **Recall check.** An LLM screens a seeded random sample of 300 titles that failed the pre-filter. The estimated number of eligible papers missed is reported. If the estimated recall is below 95 %, the keyword list is extended and the step is rerun.
3. **Screening by title and abstract.** One LLM pass (a smaller model at low effort, in batches of 100 titles) assigns *include*, *exclude* or *unsure*, using the definitions in §2 and the decisions in §2.3. *Include* and *unsure* both enter the frame. An *unsure* paper that is drawn is checked against the full text. If it turns out ineligible, it is replaced and recorded as "ineligible on full text", which is a separate count from "unavailable".
4. All screening decisions are saved in `data/frame_screened.csv`.

### 2.3 Borderline classes (default decision, to confirm at checkpoint 1)

| Class | Default |
|---|---|
| Judgment aggregation | exclude, unless the paper's main application is voting on candidates or alternatives |
| Rank aggregation for ML or IR (e.g. search results, ensembles) | exclude, because nobody makes a collective decision |
| Peer selection and peer review by vote | include |
| Tournament solutions | include if framed as choosing from a majority relation; exclude if framed as sports scheduling |
| Apportionment and seat allocation | include |
| Opinion dynamics and deliberation without a voting rule | exclude |
| Arrovian or abstract preference aggregation (social welfare functions) | include |
| Surveys, position papers, errata, comments, replies | exclude |

## 3. Versions and open access

Only legally open versions are used, in this order of preference:

1. **The venue's own open version.** AAMAS, IJCAI, AAAI and COMSOC are always open, so this applies to every paper from those venues.
2. **The publisher's open-access version** of the journal or EC paper, identified from Crossref's `license` field (CC-BY and similar) or the publisher's OA page.
3. **arXiv.** Found by title search through the arXiv API. The match is confirmed by title similarity ≥ 0.9 and at least one shared author. The latest version is used, and its date is recorded.
4. **Author pages, SSRN, RePEc, HAL or an institutional repository.** Found by web search.

No paywall is circumvented: no shadow libraries, no institutional proxies, and no automated solving of bot challenges.

For each paper we record the URL used, the version type (`venue`, `publisher-OA`, `arXiv vN (date)`, `author`, `SSRN`, …) and whether the title matches the published title. If an EC paper is abstract-only in the proceedings, the full working paper it links to is coded.

**Probe of full-text availability (2023, 24 voting-related EC and journal titles).**

- An exact-title arXiv search found a version for 12 of the 24.
- Crossref lists a Creative Commons licence for 7 of the 24.
- Springer open-access PDFs can be downloaded from this environment.
- Elsevier open-access articles cannot: sciencedirect.com returns 403, and api.elsevier.com needs an API key.
- Before web search, 13 of the 24 were obtainable: 6 of 9 EC papers and 7 of 15 journal papers.

A free Elsevier API key was tried. It is recognised, but it is refused access to the full-text service from this environment ("Requestor configuration settings insufficient"). Elsevier journals (GEB, JET, MSS) are therefore reached only through author versions.

Step 4 (web search for author pages, SSRN and RePEc) is therefore essential for the journals. The replacement rate in the journal stratum is the main open-access risk.

**Unavailable.** If none of steps 1–4 gives a full text, the paper is recorded as unavailable and replaced by the next paper of the same stratum in the seeded order. **Replacements are reported per venue, together with the reason.** This is a known source of bias: papers that are open may differ from papers that are not.

PDFs are stored only in a temporary cache outside the repository and are never committed. Full-text extraction uses `pdftotext` in reading order. `-layout` was dropped because it interleaves two-column pages.

## 4. Stratified draw

**Strata.** Venue type × year:

- AI conferences (AAMAS, IJCAI, AAAI)
- EC
- COMSOC workshop
- Journals (SCW, GEB, JET, MSS)

COMSOC has no 2022 or 2024 edition, which gives 18 non-empty strata.

**Size.** n = 150.

**Allocation.**

1. Every venue type gets a floor of 20 papers. Otherwise EC would get only a handful under proportional allocation.
2. The remaining 70 papers are allocated proportionally to the number of eligible papers per venue type, rounded by the largest-remainder method.
3. Within each venue type, papers are spread over the years proportionally to the eligible counts, with at least 1 per non-empty stratum.

If a stratum has fewer eligible papers than allocated, all of them are taken and the surplus goes to the other years of the same venue type.

**Order within a stratum.** Papers are sorted by `SHA-256(SEED + "|" + paper_id)`. The first n_h papers form the sample, and the following ones form the replacement queue, in order. This order does not depend on the Python version.

**Weights.** w_h = N_h / n_h, where N_h counts the eligible papers in the frame. The design effect of the floor allocation is computed and reported. The ±8 pp target (simple random sampling, p = 0.5: 1.96·√(0.25/150) ≈ 0.080) widens accordingly. Per venue type, precision is about ±16 to ±22 pp.

**Pilot set.** 10 eligible papers from the 2020 editions of AAMAS, IJCAI, AAAI and EC, and 2020 issues of the four journals. These are outside the frame years. There was no COMSOC workshop in 2020. The papers are drawn with the same hashing under the seed `SEED + "|pilot"`.

**Hand-check set.** After coding, 15 papers are drawn from the sample with the seed `SEED + "|handcheck"`, stratified by venue type (4/4/3/4), without regard to the codes.

## 5. Coding procedure

- **Codebook.** `protocol/codebook.md`. Version 0.1 is a draft. It is revised after the pilot and then frozen as v1.0, with a hash recorded in this file. No changes are made after freezing. Any later clarification is logged and does not alter codes already assigned.
- **Blinding.** Coders receive only the codebook and the paper text. They do not receive the research questions, this protocol, the commissioning researcher's background or prior, or other coders' outputs.
- **Pass A and Pass B.** Two independent LLM coding runs per paper, each in a fresh context, each returning the JSON template of the codebook. Pass A uses the larger model and pass B a different, smaller model, to reduce correlated errors.
- **Pass C (adjudication).** A third run sees the paper, the codebook and both codings for items where A and B disagree only. It chooses one of the two codes, or a third code with a reason, and records the evidence.
- **Reliability.** Cohen's κ per item is computed on A vs B, before adjudication. Each item is also reported with its percentage agreement and the prevalence of its modal code, because κ is unstable at extreme prevalence.
  - Items with κ < 0.40 are reported as **unreliable**. They are kept in the dataset and their proportions are reported with that label.
  - Items with 0.40 ≤ κ < 0.60 are reported as moderate.
  - Multi-select items: κ per category. Stakeholder matrix: κ for presence, then κ per attribute on the papers where both coders marked the type present.
  - κ confidence intervals: bootstrap over papers, 2,000 resamples.
- **Calibration case.** The frozen codebook is applied in the same A/B/C fashion to the calibration paper and its supplement.

## 6. Outcome measures (pre-specified)

Let E be the set of eligible coded papers. Definitions refer to codebook item IDs.

- **O0 (procedural, no claims):** C5.1 = N and C9.1 = N. Reported as a share of E. These papers count as not at fault on O1 and O3.
- **O1 (preference–ballot relation stated):** C2.4 ∈ {DIST, IDJ, IDS}.
  - Denominator: papers with C2.4 ≠ ONE.
  - Also reported: the split IDJ vs IDS, i.e. whether a reason is given.
- **O2 (stakeholder specification):** for each stakeholder type *s* present, the share with behaviour stated explicitly (C6.s.behav_stated = EXPLICIT), and the share with information stated explicitly (C6.s.info_stated = EXPLICIT) among the strategic ones.
- **O2b (asymmetry):** the share with C7.1 = Y, and among those the share with C7.2 = REASON.
- **O3 (claims resting on unstated assumptions):** 1 if C9.2 = SOME-UNSTATED, or if C5.1 = Y and C5.2 = INPUT-UNSTATED.
  - Denominator: E.
  - Also reported conditional on making any welfare or interpretive claim (C5.1 = Y or C9.1 = Y).
- **O4 (sincerity):** among papers with C3.2 applicable, the shares *stated* and *stated with a reason* (C3.3 ≠ NONE).
- **O5 (utility link):** among papers with C4.1 applicable, the share SPEC; and C4.2 for papers using dichotomous preferences.

**Estimation.** Population estimates are design-weighted, with 95 % CIs from a stratified bootstrap (2,000 resamples). Breakdowns by venue type and by primary paper type (C1.primary) give unweighted sample proportions with Wilson 95 % CIs, and the per-type n.

## 7. Limitations recorded in advance

- **LLM coders.** A and B are two runs of a language model, possibly the same model. Their errors may be correlated, so κ between them measures consistency rather than validity. The 15-paper human hand-check is the only check against a human reading.
- **Open-access bias.** See §3.
- **The commissioning researcher's prior** may have shaped the codebook despite the neutral wording. The pilot revisions are logged so that readers can judge.
- **Judgement-heavy items** (C9.2, C5.2) are expected to have lower κ.
- **Keyword pre-filter.** Recall is estimated, not guaranteed.
