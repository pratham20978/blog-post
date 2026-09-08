# Ledger format

`research/ledger.md`, one file per post. Written during research, read during drafting, checked during the gate.

---

## Format

```markdown
# Source ledger — <slug>

## Sources

| ID | Tier | Source | URL | Accessed |
|---|---|---|---|---|
| S1 | T1 | Jacobson, "Congestion Avoidance and Control", SIGCOMM 1988 | https://... | 2026-09-08 |
| S2 | T1 | RFC 5681, TCP Congestion Control | https://... | 2026-09-08 |
| S3 | T2 | Linux kernel docs, tcp.rst | https://... | 2026-09-08 |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | Slow start doubles the window each RTT until the threshold | S2 §3.1 | — |
| L02 | Loss is interpreted as congestion regardless of cause | S1, S2 | design assumption of the 1988 model |
| L07 | Throughput scales with the inverse square root of loss rate | S4 | steady state, single flow, no delay variation |

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
