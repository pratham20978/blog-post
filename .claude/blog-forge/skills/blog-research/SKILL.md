---
name: blog-research
description: Find and verify sources for a technical blog post, then record every factual claim in a traceable ledger. Use this whenever a post needs papers, standards, RFCs, official documentation, benchmark numbers, complexity bounds, dates, version numbers, or any claim the writer would otherwise state from memory. Trigger when the user asks to research a topic, gather sources, check a claim, find papers, or when blog-authoring reaches its research phase. Also use before writing any post that makes numeric or historical claims — writing first and sourcing later produces claims nobody can check.
license: MIT
metadata:
  version: "0.3"
---

# Blog Research

Find sources good enough that a hostile reader who knows the topic cannot find an unsupported claim.

Output is a **claim ledger**, not a pile of links. The ledger is what the draft is written against and what the quality gate checks against.

---

## 1. Why this is a separate skill

Writing from memory feels faster and produces articles with wrong numbers in them. Model memory is confidently wrong about exactly the things this blog is about: version numbers, benchmark results, publication dates, which RFC says what, whether a bound is tight.

So the order is fixed. Sources first, ledger second, prose third. A post whose ledger is empty is not ready to draft.

---

## 2. Search procedure

### Step 1 — Read the subject playbook

`blog-authoring/references/subject-playbooks.md` names the canonical sources for the subject. Networking starts at RFCs. Databases start at papers plus Postgres docs. Start there, not at a general web search.

### Step 2 — Query ladder

Six rungs, run in order. Each rung is a different kind of query, not a rephrasing of the last one.

#### Rung 1 — the literature sweep

**Mandatory, and it runs before any general web search.** No other rung starts until it has. A post that skipped this rung is sourced from documentation and practitioner blogs, and it reads like it. If the topic also has a defining document — an RFC number, a spec section, a standard — find that in the same pass; it is the canonical source and it sits alongside the papers, not instead of them.

**Find the survey first.** Search `<topic> survey` and `<topic> review` on Google Scholar, sorted by citation count. A good survey hands you the map of the field and a pre-filtered bibliography its authors already spent months assembling, which is worth more than ten separate searches. Read its taxonomy section before you decide what the post is even about.

**Query the databases that index research**, not a general search engine. Each is good at something the others are not:

| Database | What it is for |
|---|---|
| Google Scholar | Breadth across every venue, citation counts, and the "Cited by" graph |
| arXiv | The newest work, often a year ahead of the venue. Unreviewed |
| Semantic Scholar | A structured citation graph, influential-citation ranking, and a free API for walking it |
| DBLP | The authoritative venue and publication record for CS — the place to check whether an arXiv preprint was ever actually published |
| ACM Digital Library, IEEE Xplore | The paywalled venues of record, and where the canonical DOI lives |
| USENIX, PMLR, OpenReview, IACR ePrint | Open proceedings — free full text for systems, ML, crypto and theory work |
| Papers with Code | Reproductions and leaderboards. Evidence about a claim, never the claim |
| Lab publication pages | Google Research, Google DeepMind, Meta AI (FAIR), Microsoft Research, NVIDIA Research, OpenAI, Anthropic, Allen AI |

The lab pages matter more than they look. A lab's own publication page is where the system paper, the model card and the errata live, and for a system the post is describing it is frequently the primary source — there is no third-party paper about a proprietary system. Go to the publication page, not the launch announcement. Per-database traps are in `references/source-tiers.md`.

**Chase citations one hop in both directions**, from the two most central papers the sweep turned up. Backward through their reference lists, to find what they are built on and what the original result actually said — the version everyone repeats is usually a compression that dropped a condition. Forward through Scholar's "Cited by" or Semantic Scholar's citation list, to find the correction, the failed replication, and the method that superseded it. Forward chasing is how you discover that a result was overturned, and it is the step that is always skipped. One hop each way is enough; two is a literature review.

**Record venue, year, identifier and peer-review status at the moment you record the source.** Not later. Later never happens, and reconstructing a venue from a half-remembered title costs more than writing it down would have.

#### The remaining rungs

2. **The mechanism.** How the thing actually works, in the primary source.
3. **The numbers.** Benchmarks, measurements, complexity results, with their setup.
4. **The disagreement.** What is contested, superseded, or was wrong in the original. Search for critiques, errata, follow-up papers, and "considered harmful" style responses.
5. **The practice.** What implementations actually do, which often differs from the spec.
6. **The teaching angle.** How good explainers have framed it. Framing only, never facts.

Rung 4 is the one that separates a real article from a summary, and it is the one that gets skipped. Do not skip it.

### Step 3 — Scale to the tier

| Tier | Sources | Searches | Peer-reviewed or standard sources | Scholarly databases queried |
|---|---|---|---|---|
| L1 | 4–8 | 5–8 | 2 | 2 |
| L2 | 8–15 | 8–14 | 4 | 3 |
| L3 | 15–25 | 14–22 | 7 | 4 |
| L4 | 25–40 | 20–30 | 10 | 4 |

The last two columns are floors the quality gate counts, not targets. A source counts toward the peer-reviewed or standard column when its Status is `peer-reviewed` or `standard` **and** its Identifier is not `—`; an uncited preprint and a vendor doc do not count, however good they are.

Search each distinct sub-topic separately. One combined query returns shallow results for all of them.

#### When the topic genuinely has no literature

Some topics have none, and no amount of searching will produce papers that were never written: a tooling how-to, one vendor's undocumented behaviour, an operational practice nobody has studied. Manufacturing citations to fill the count is worse than missing it — a padded bibliography is a lie about where the post's confidence comes from.

Write a `## Literature note` in the ledger instead: one short paragraph saying the topic has no research literature, what you searched to establish that, and what the post rests on in its place — official docs, source code, our own measurements. Its presence downgrades the paper-count gate from an error to a warning. **This is the only acceptable way to come in under the paper floor.**

### Step 4 — Fetch, do not trust snippets

A search snippet is not a source. Fetch the page or the paper before recording a claim from it. Snippets routinely strip the condition that makes a claim true.

While reading a paper that will carry a section, inspect its figures and captions. Record only a
figure that directly explains a planned teaching point; do not inventory every image in the
paper. For each candidate, record the paper's figure number, what section and claim it serves,
the official source URL, and the explicit licence or permission. The format is in
`references/ledger-format.md`. Blog Visuals makes the final relevance decision and handles
extraction.

### Step 5 — Stop condition

Stop when new searches return sources you have already seen, and every planned section has enough to be written honestly. Not when a count is hit.

---

## 3. Source tiers

Full detail and per-subject source lists in `references/source-tiers.md`. Summary:

| Tier | What | Usable for |
|---|---|---|
| T1 | Peer-reviewed papers, standards, RFCs, established textbooks | any claim |
| T2 | Official docs and specs, man pages, vendor architecture manuals | any claim about that system |
| T3 | Primary source code, release notes, changelogs, issue trackers | behaviour claims |
| T4 | Respected practitioner writing | framing and intuition only, never facts |
| T5 | Everything else: content farms, SEO blogs, forum answers, AI-generated pages | not citable |

The T4 line is strict. A well-known blog explaining a concept beautifully is a good model for how to explain it. It is not a source for what is true. Trace the claim to where the blog got it.

---

## 4. The ledger

Written to `research/ledger.md`. Format is defined in `references/ledger-format.md`.

Every row is: claim, tier, source, URL, access date, and a paraphrase in our own words.

The Sources table also carries **Venue, Year, Identifier and Status** for each source — Status being one of `peer-reviewed`, `preprint`, `standard`, `official-docs`, `source` or `practitioner`, defined in `references/ledger-format.md` and enforced by the gate — and the ledger carries a **`## Search log`** — one row per query actually run, with what it returned. Those columns and that log are what make the literature sweep auditable rather than claimed.

Two rules that keep it useful:

**Paraphrase, never store quotes.** If the ledger holds quoted text, that text tends to end up in the draft. Write what the source establishes, in your own words, at the point of recording.

**One row per claim, not per source.** A paper that supports four claims gets four rows. This is what makes the gate checkable.

---

## 5. Claim flagging in the draft

While drafting, any sentence containing a number, date, version, standard name, complexity bound, or named result carries a ledger key in a comment:

```markdown
Throughput falls with the square root of loss rate. <!-- L07 -->
```

The validator collects these and checks each key exists in the ledger. Strip them at publish, or leave them; they are HTML comments and do not render.

---

## 6. Copyright

Hard limits, not preferences.

- **No verbatim reproduction.** Paraphrase everything. If an exact phrase is genuinely load-bearing, keep it under fifteen words, and use at most one such quote per source.
- **Reuse only a directly relevant, rights-cleared paper figure.** Record its exact figure number, source URL, and licence or permission. Citation alone is not permission. Do not collect every image, and do not generate or redraw a lookalike when reuse rights are unclear.
- **No structural copying.** Do not follow another article's section order and headings with reworded content. That is reproduction with extra steps.
- **Check the licence on any found image.** Only public domain, a licence that permits this use, documented permission, or our own work. Otherwise cut it.

---

## 7. Honest reporting

- Numbers get their setup: hardware, dataset, version, configuration. A benchmark without them means nothing.
- A single paper is not a settled result. Say "one study found" when that is what happened.
- If sources disagree, say so in the post and cite both. Disagreement is interesting; hiding it is a defect.
- If a search fails to establish something, write around it. Never fill a gap from memory.
- Preprints get labelled as preprints.
- Anything that changes over time gets an access date.

---

## 8. Note on the platform

This runs at authoring time, in the editor. The blog platform itself has its own retrieval constraints; they do not apply here. Nothing this skill uses ends up in the backend.
