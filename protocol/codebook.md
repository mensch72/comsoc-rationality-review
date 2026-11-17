# Codebook: modelling choices in papers on voting

Version: **1.0 (frozen after pilot)**.

## Purpose and general rules

This codebook records how a paper describes:

- the inputs to a voting rule,
- the behaviour and information of the agents involved,
- the claims the paper draws from its results.

All codes are descriptive. No code is better or worse than another, and many papers legitimately leave items blank because the item does not apply to them.

- **Code what the paper says.** Do not code what the authors probably meant, or what is standard in the literature. If something follows unambiguously from the formal model but is not said in words, use the code IMPLICIT where the item offers it.
- **Scope.** Read the full text supplied, including appendices that are part of the same file. Footnotes count.
- **Evidence.** Every code except NA needs:
  - `loc`: section number or name, and page, if visible;
  - `quote`: at most 12 consecutive words copied verbatim from the paper.

  For a "not stated" code, use `quote: "none found"` and list in `loc` the sections you checked (at least: model or preliminaries section, introduction, conclusion).
- **NA.** Use NA only when the condition given for the item holds. Record the reason in `note`.
- **Doubt.** If two codes fit equally well, pick the one listed first and write one sentence in `note`.

Terms used below:

- **Submitted input.** The object the rule takes as its argument. Examples: ballot, vote, reported ranking, approval set, bid.
- **Held attitude.** Anything the paper attributes to agents independently of what they submit. Examples: preferences, utilities, valuations, opinions, types, ideal points.

---

## C0. Eligibility on full text

| Code | Meaning |
|---|---|
| ELIG | The main object is a procedure aggregating several agents' inputs into a collective decision by voting, or strategic or computational aspects of such a procedure |
| INELIG | Otherwise (e.g. fair division, matching, ML rank aggregation, survey). Give the reason in `note` |

If INELIG, stop coding.

## C1. Paper type

`C1.types`: multi-select, all that apply to at least one main result.
`C1.primary`: the one type that the largest share of the main results belongs to.

| Code | Meaning |
|---|---|
| AX | Axiomatic: characterisations, (in)compatibility of properties, which rules satisfy which properties |
| AL | Algorithmic or complexity: algorithms, running times, hardness, parameterised complexity, approximation algorithms for computing outcomes |
| SB | Strategic behaviour: incentives of some agent to act in a particular way (manipulation, control, bribery, strategic candidacy, strategyproofness), as a property or as a computational problem |
| EQ | Equilibrium analysis: existence, characterisation or properties of equilibria of a game |
| WD | Welfare or distortion: performance of rules against an objective (social welfare, distortion, price of anarchy, approximation of an optimum) |
| SI | Simulation on synthetic data |
| EM | Empirical or experimental: real-world data, or behavioural experiments with human participants |
| OT | Other (conceptual, modelling proposal). Describe in `note` |

## C2. Inputs and their relation to held attitudes

**C2.1 Name of the input.** The term(s) the paper uses for the argument of the rule, verbatim (e.g. "preference profile", "ballots", "votes", "approval ballots"). Free text.

**C2.2 Format of the input.** Multi-select:

| Code | Meaning |
|---|---|
| RANK | Strict rankings |
| WEAK | Weak orders |
| APPR | Approval sets |
| DICH | Inputs described as dichotomous preferences |
| CARD | Cardinal scores, utilities or valuations |
| PAIR | Pairwise comparisons or a majority relation |
| OTH | Other. Describe in `note` |

**C2.3 Held attitude present.** Does the paper refer to any held attitude of voters, i.e. something voters have that is not defined as what they submit? Y / N.

**C2.4 Relation between input and held attitude.** Choose one:

| Code | Use when |
|---|---|
| DIST | The paper treats the submitted input and the held attitude as separate objects: separate notation, or text saying that what is submitted may differ from what is held |
| IDJ | The paper states that the submitted input equals the held attitude, **and** gives a reason (e.g. the rule is strategyproof on the domain; agents have no incentive or information to misreport; the paper studies inputs as given) |
| IDS | The paper states that the submitted input equals the held attitude, without a reason (e.g. "we assume voters vote sincerely") |
| IDU | The input is described as a held attitude (e.g. "preferences", "utilities") and the rule is applied to it directly, with no statement about submission or reporting |
| ONE | The input is described only as something submitted (ballots, votes), and the paper does not refer to any held attitude (C2.3 = N) |

## C3. Sincerity

**C3.1 Strategic voters analysed.** Does any analysis in the paper consider voters submitting an input that differs from their held attitude?

| Code | Meaning |
|---|---|
| ALL | Every main analysis does |
| SOME | Some analyses do, others do not |
| NONE | No analysis does |

In experiments with human participants who choose their inputs freely, code ALL unless an analysis assumes the inputs equal the held attitudes.

**C3.2 Statement for the non-strategic analyses.** For the analyses where voters are not modelled as strategic, does the paper state that voters submit their held attitude?

| Code | Meaning |
|---|---|
| STATED | Yes, in words |
| NOT-STATED | No such statement found |
| NA | C2.4 = ONE, or C3.1 = ALL |

**C3.3 Reason given**, if C3.2 = STATED. Choose one:

| Code | Meaning |
|---|---|
| SP | The rule or the domain is strategyproof |
| INC | An argument about incentives or information (e.g. large electorates, little information) |
| EMP | Empirical evidence |
| CONV | Citation of convention or prior work only |
| PROC | The paper says it studies the rule as a function of submitted inputs |
| OTH | Other. Describe in `note` |
| NONE | No reason given |
| NA | C3.2 ≠ STATED |

## C4. Link to utilities

**Applicability.** C4.1 applies if C2.2 includes RANK, WEAK, APPR, DICH or PAIR **and** the paper uses, for voters, any of: utility, welfare, satisfaction, cost, distortion, intensity of preference. Costs or budgets of other agents (e.g. a briber's costs) do not count. Otherwise NA.

**C4.1 Link specified.**

| Code | Meaning |
|---|---|
| SPEC | The paper defines how utilities relate to the input (e.g. utilities consistent with the ranking; approve iff utility above a threshold; utility 1 for approved, 0 otherwise; a metric or spatial model generating both) |
| PART | Some relation is mentioned but not defined (e.g. "voters approve candidates they like") |
| NOTSPEC | Utility-type notions are used without a stated relation to the input |
| NA | Applicability condition not met |

**C4.2 Dichotomous preferences.** If the paper uses "dichotomous preferences" or an equivalent term: is it stated what the two classes represent in terms of utility or of a richer preference?

| Code | Meaning |
|---|---|
| Y | Yes (e.g. "utility 1 for approved, 0 otherwise"; "the approval set is the top indifference class") |
| N | No |
| NA | The term is not used |

## C5. Welfare and voter-oriented claims

**C5.1 Criteria in results.** Does any definition used in a result, any formal result, or any simulation or experiment evaluate outcomes or rules by one of these criteria?

- social welfare,
- efficiency, including Pareto efficiency,
- voter satisfaction or utility,
- representation of voters or groups,
- proportionality, presented as fairness to voters or groups (e.g. justified representation),
- distortion.

Code Y / N. Statements that appear only in the abstract, introduction or conclusion are coded under C9.1, not here.

**C5.2 Object of evaluation**, if C5.1 = Y. Choose one:

| Code | Meaning |
|---|---|
| HELD | Evaluated on held attitudes defined separately from the input (e.g. distortion against cardinal utilities) |
| INPUT-STATED | Evaluated on the input, and the paper states that the input equals the held attitude (C2.4 ∈ {IDJ, IDS}) |
| INPUT-REPORTED | Evaluated on the input, and the paper says explicitly that this is welfare etc. with respect to the submitted inputs |
| INPUT-UNSTATED | Evaluated on the input, with no statement relating it to held attitudes |
| NA | C5.1 = N |

## C6. Stakeholders

For each type below, first code `present` (Y/N). A type is present only if the formal model contains at least one agent of that type who takes an action in the model, whether chosen strategically or fixed.

- Candidates that serve only as alternatives to be chosen are not present.
- An organiser is present only if they choose something in the model (control actions, agenda, maps, the rule as part of the analysis).
- Mentioning a type's interests outside the model does not make it present.

| ID | Type |
|---|---|
| VOT | Voters, including delegates and proxies in liquid democracy, and voters acting as manipulators |
| CAN | Candidates, or proponents of alternatives or projects |
| ORG | Organiser, chair or election authority, including the controlling agent in control problems |
| DIS | District designer |
| BRI | Briber or external manipulator who is not a voter |
| DES | Rule or mechanism designer, only when the paper models the designer's choice or objective explicitly |
| OTH | Another acting agent that fits none of the types above. Name it in `note` |

For each present type, code the following.

**`behav`**: how the type acts.

| Code | Meaning |
|---|---|
| STRAT | Chooses actions to pursue its own objective (optimises, best-responds, deviates profitably) |
| NONSTRAT | Actions are fixed by the model (e.g. sincere, truthful, exogenous) |
| MIXED | Strategic in some analyses and not in others |
| NS | Not specified |

**`behav_stated`**: whether the behaviour is said.

| Code | Meaning |
|---|---|
| EXPLICIT | Said in words |
| IMPLICIT | Only inferable from the formal model |
| NA | `behav` = NS |

**`info`**: what the type is assumed to know about others' held attitudes or inputs.

| Code | Meaning |
|---|---|
| COMPLETE | Knows them fully |
| PARTIAL | Knows some of them, a signal, poll or prior |
| NONE | Knows nothing about them |
| NS | Not specified |
| NA | `behav` = NONSTRAT |

**`info_stated`**: EXPLICIT / IMPLICIT / NA (NA if `info` ∈ {NS, NA}).

Evidence is required for `behav` and for `info`.

## C7. Differences in modelled behaviour across types

**C7.1** Among the present types, is at least one modelled as STRAT while another is modelled as NONSTRAT (in the same analysis)?

| Code | Meaning |
|---|---|
| Y | Yes. Name the types in `note` |
| N | No |
| NA | Fewer than two types present, by the C6 definition |

**C7.2** If C7.1 = Y: is a reason given for modelling the types differently?

| Code | Meaning |
|---|---|
| REASON | An argument is given |
| CITE | Only a citation to prior work |
| NONE | No reason given |
| NA | C7.1 ≠ Y |

## C8. Solution concept

Applies if any type is STRAT or MIXED; otherwise NA.

**C8.1** Multi-select:

| Code | Meaning |
|---|---|
| DOM | Dominant strategies or strategyproofness |
| NE | Nash equilibrium, pure or mixed |
| SPE | Subgame-perfect equilibrium or backward induction |
| BNE | Bayes–Nash or ex-post equilibrium |
| ITER | Iterative voting or best-response dynamics |
| DEV | Existence of an action that achieves a given agent's or coalition's goal, studied as a decision or optimisation problem (e.g. manipulation, control, bribery, districting) |
| BND | Bounded-rationality or heuristic behaviour (level-k, poll-based heuristics) |
| COAL | Coalitional concepts (strong equilibrium, core) |
| OTH | Other. Name it in `note` |

**C8.2** Is the solution concept named explicitly? Y / N, or NA if C8.1 is NA.

## C9. Claims beyond the formal results

**C9.1** Does the abstract, introduction or conclusion make claims about any of:

- what the results mean for real decisions or institutions,
- voters' well-being or fairness towards them,
- which rule should be used?

Code Y / N. If Y, list up to three such claims as quotes, with `loc`.

**C9.2** If C9.1 = Y: for the claims listed, identify the modelling assumptions that are needed for each claim to follow from the formal results, for example:

- how inputs relate to held attitudes,
- how utilities relate to ordinal inputs,
- which agents are strategic,
- what agents know,
- other.

Count an assumption as needed only if, without it, the claim would not follow from the formal results. For example, a claim about voters' welfare drawn from results on submitted inputs needs a statement relating inputs to held attitudes. Do not list assumptions that apply to all modelling, such as that the model approximates reality.

For each needed assumption, record whether the paper states it. Then code:

| Code | Meaning |
|---|---|
| ALL-STATED | Every needed assumption is stated |
| SOME-UNSTATED | At least one needed assumption is not stated. Name it in `note` |
| UNCLEAR | Cannot be determined from the text |
| NA | C9.1 = N |

## C10. Explicit procedural reading

**C10.1** Does the paper state that it studies the rule only as a function of submitted inputs, or that it takes no position on how inputs relate to held attitudes? Y / N.

---

## Output template (one JSON object per paper)

```json
{
  "paper_id": "",
  "codebook_version": "1.0",
  "C0":  {"code": "", "loc": "", "quote": "", "note": ""},
  "C1":  {"types": [], "primary": "", "loc": "", "quote": "", "note": ""},
  "C2.1": {"value": "", "loc": "", "quote": ""},
  "C2.2": {"codes": [], "loc": "", "quote": "", "note": ""},
  "C2.3": {"code": "", "loc": "", "quote": "", "note": ""},
  "C2.4": {"code": "", "loc": "", "quote": "", "note": ""},
  "C3.1": {"code": "", "loc": "", "quote": "", "note": ""},
  "C3.2": {"code": "", "loc": "", "quote": "", "note": ""},
  "C3.3": {"code": "", "loc": "", "quote": "", "note": ""},
  "C4.1": {"code": "", "loc": "", "quote": "", "note": ""},
  "C4.2": {"code": "", "loc": "", "quote": "", "note": ""},
  "C5.1": {"code": "", "loc": "", "quote": "", "note": ""},
  "C5.2": {"code": "", "loc": "", "quote": "", "note": ""},
  "C6": {
    "VOT": {"present": "", "behav": "", "behav_stated": "", "info": "", "info_stated": "",
            "loc_behav": "", "quote_behav": "", "loc_info": "", "quote_info": "", "note": ""},
    "CAN": {}, "ORG": {}, "DIS": {}, "BRI": {}, "DES": {}, "OTH": {}
  },
  "C7.1": {"code": "", "loc": "", "quote": "", "note": ""},
  "C7.2": {"code": "", "loc": "", "quote": "", "note": ""},
  "C8.1": {"codes": [], "loc": "", "quote": "", "note": ""},
  "C8.2": {"code": "", "loc": "", "quote": ""},
  "C9.1": {"code": "", "claims": [{"loc": "", "quote": ""}], "note": ""},
  "C9.2": {"code": "", "loc": "", "quote": "", "note": ""},
  "C10.1": {"code": "", "loc": "", "quote": "", "note": ""}
}
```
