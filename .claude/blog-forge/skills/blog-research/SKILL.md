---
name: blog-research
description: Find and verify sources for a technical blog post, then record every factual claim in a traceable ledger. Use this whenever a post needs papers, standards, RFCs, official documentation, benchmark numbers, complexity bounds, dates, version numbers, or any claim the writer would otherwise state from memory. Trigger when the user asks to research a topic, gather sources, check a claim, find papers, or when blog-authoring reaches its research phase. Also use before writing any post that makes numeric or historical claims — writing first and sourcing later produces claims nobody can check.
license: MIT
metadata:
  version: "0.1"
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

Run these in order. Each rung is a different kind of query, not a rephrasing of the last one.

1. **The canonical source.** The RFC number, the paper title, the spec section. If the topic has a defining document, find it first.
2. **The mechanism.** How the thing actually works, in the primary source.
3. **The numbers.** Benchmarks, measurements, complexity results, with their setup.
4. **The disagreement.** What is contested, superseded, or was wrong in the original. Search for critiques, errata, follow-up papers, and "considered harmful" style responses.
5. **The practice.** What implementations actually do, which often differs from the spec.
6. **The teaching angle.** How good explainers have framed it. Framing only, never facts.

Rung 4 is the one that separates a real article from a summary, and it is the one that gets skipped. Do not skip it.

### Step 3 — Scale to the tier

| Tier | Sources | Searches |
|---|---|---|
| L1 | 4–8 | 5–8 |
| L2 | 8–15 | 8–14 |
| L3 | 15–25 | 14–22 |
| L4 | 25–40 | 20–30 |

Search each distinct sub-topic separately. One combined query returns shallow results for all of them.

### Step 4 — Fetch, do not trust snippets

A search snippet is not a source. Fetch the page or the paper before recording a claim from it. Snippets routinely strip the condition that makes a claim true.

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
- **Never reproduce a figure** from a paper, textbook, documentation site, or another blog. Every figure in our posts is our own redraw. Cite the source of the idea in the caption.
- **No structural copying.** Do not follow another article's section order and headings with reworded content. That is reproduction with extra steps.
- **Check the licence on any found image.** Only public domain, an explicit permissive licence, or our own work. Otherwise cut it.

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
