# Ledger format

`research/ledger.md`, one file per post. Written during research, read during drafting, checked during the gate.

---

## Format

```markdown
# Source ledger — <slug>

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S1 | T1 | Jacobson, "Congestion Avoidance and Control" | ACM SIGCOMM | 1988 | 10.1145/52324.52356 | peer-reviewed | https://... | 2026-09-08 |
| S2 | T1 | RFC 5681, TCP Congestion Control | IETF | 2009 | RFC 5681 | standard | https://... | 2026-09-08 |
| S3 | T2 | Linux kernel docs, tcp.rst | — | 2026 | — | official-docs | https://... | 2026-09-08 |
| S4 | T1 | Mathis et al., "The Macroscopic Behavior of the TCP Congestion Avoidance Algorithm" | ACM SIGCOMM CCR | 1997 | 10.1145/263932.264023 | peer-reviewed | https://... | 2026-09-08 |
| S5 | T1 | Ware et al., "Modeling BBR's Interactions with Loss-Based Congestion Control" | IMC | 2019 | 10.1145/3355369.3355604 | peer-reviewed | https://... | 2026-09-09 |

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | Google Scholar | "congestion control survey" sort:citations | Low and Paganini 2002; gave the 1988–2002 map and 40 pre-filtered references |
| 2 | 1 | DBLP | author:Matthew Mathis | confirmed the 1997 CCR venue for the √p model; the 2011 draft never reached a venue |
| 3 | 1 | Semantic Scholar | Cited by: Jacobson 1988, influential citations only | Mathis 1997, Padhye 1998, and the BBR line from 2016 onward |
| 4 | 4 | Google Scholar | "BBR" fairness OR unfairness "loss-based" 2017..2026 | Ware 2019 (IMC) — BBR starves CUBIC at shallow buffers; the claim needs qualifying |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | Slow start doubles the window each RTT until the threshold | S2 §3.1 | — |
| L02 | Loss is interpreted as congestion regardless of cause | S1, S2 | design assumption of the 1988 model |
| L07 | Throughput scales with the inverse square root of loss rate | S4 | steady state, single flow, no delay variation |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S1 | Figure 4 | Why loss changes the window / L02 | directly shows the state transition discussed in the section | CC BY 4.0 | https://... | send to visual route gate |

## Open questions

- Whether modern Linux still defaults to CUBIC in the target kernel version. Not resolved; the post avoids the claim.
```

---

## Rules

**One row per claim.** A source supporting four claims gets four rows. This is what makes the gate mechanical rather than a judgment call.

**Our words, never theirs.** The claim column is a paraphrase written at recording time. If quoted text sits in the ledger it will leak into the draft.

**The condition column is not optional.** Most technical claims are true under conditions. A bound that holds in steady state, a benchmark on specific hardware, a behaviour in a specific version. The condition is what stops the post from overclaiming, and it is the first thing a knowledgeable reader checks.

**Section references, not just document references.** `S2 §3.1` is checkable. `S2` is not.

**Open questions get recorded.** When research fails to settle something, write it down and write the post around it. This is a feature: a post that says "this is not settled, here is why" is more trustworthy than one that guesses.

**Figure candidates are selective.** Add a row only when a paper figure directly serves a
planned section and would carry information the prose cannot communicate as clearly. Do not list
every figure in each paper. Record the original figure number, relevance, source URL, and explicit
rights basis. If rights cannot be verified, set Decision to `do not reuse`; citation or open
access alone is not a licence. The visual route gate makes the final selection.

**The search log is not optional.** One row per query actually run, with what it returned stated in a clause — "various results" is not a return. It makes the literature sweep auditable, it stops the same query being run twice when research is picked up days later in a new session, and it is what the gate reads to confirm the sweep happened at all. A ledger with fifteen sources and no search log looks like recall dressed up as research.

**Status is one of six values.** `peer-reviewed` · `preprint` · `standard` · `official-docs` · `source` · `practitioner`. Nothing else validates, and the gate errors on an unrecognised value. `standard` is an RFC, an ISO or IEEE document, a POSIX section; `official-docs` is a project's or vendor's own documentation; `source` is primary implementation evidence — code at a permalink, a release note, a changelog; `practitioner` is respected writing carried for framing only, never for a fact. The value maps onto the source tier, so a row marked `practitioner` can never be the only support for a number.

**Status and Identifier travel together.** A source with Status `peer-reviewed` must carry a real identifier. Old papers have DOIs too — ACM and IEEE assigned them retroactively — so a `—` in that column means the paper was not actually located, only mentioned somewhere. `preprint` is not a lesser status and not a reason to leave a source out; it is a label, and it has to be in the ledger so the post can carry it too. A claim resting on a source marked `preprint` says "a preprint reports" in the prose, not "researchers found".

**`## Literature note` — optional, and one condition only.** Write it when the topic genuinely has no research literature: a tooling how-to, one vendor's behaviour, an operational practice nobody has published on. One short paragraph saying so, what was searched to establish it, and what the post rests on instead. It downgrades the tier's peer-reviewed floor from an error to a warning. It is written *after* the sweep, never in place of one, and never to excuse a sweep that was thin.

---

## Keys in the draft

Each claim key appears as an HTML comment next to the sentence that uses it:

```markdown
Loss is treated as a congestion signal regardless of what caused it. <!-- L02 -->
```

The validator collects every `<!-- Lnn -->` in `blog.md` and checks it resolves. It also reports ledger rows that were never used, which usually means either a cut section or a claim that should have been included.

Comments do not render. Leave them in or strip them at publish; either is fine.

---

## What needs a key

- Any number: benchmarks, sizes, latencies, percentages
- Any date or version
- Any complexity bound that is not textbook-standard
- Any named result, algorithm, or theorem attribution
- Any claim about what a specific system does
- Any historical claim about why something was designed a certain way

What does not need a key: definitions, reasoning you show your work for, and worked examples you compute in the post.
