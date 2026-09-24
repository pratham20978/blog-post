# Depth tiers and word budget

The tier decides the budget. The budget decides the outline. The outline decides the draft.

Never write toward a word count. Write each section to the point where it has said its thing, then check the total. A post that lands at 2,600 words when L2 was planned is an L1 post, and that is a correct outcome, not a failure.

---

## Tiers

| Tier | Words | Body sections | Figures | Cadence |
|---|---|---|---|---|
| L1 Primer | 2,000–3,000 | 1–2 | 3–5 | daily |
| L2 Standard | 3,000–5,000 | 2–4 | 5–8 | daily default |
| L3 Deep dive | 5,000–7,500 | 4–5 | 8–12 | weekly |
| L4 Pillar | 7,500–10,000 | 5–6 | 12–18 | monthly |

Figure budget is roughly one per 500–700 words. Below that ratio the post reads as a wall of text. Above it, figures start repeating each other.

---

## Budget allocation

Percentages of total words. Multiply by the tier midpoint to get a target per section.

| Section | Share |
|---|---|
| Insights + who this is for | 3% |
| Why this matters | 4% |
| The problem | 8% |
| Worked example | 15% |
| Intuition | 10% |
| Body sections (all) | 35% |
| The math | 10% |
| Implementation | 8% |
| Limitations and common mistakes | 5% |
| Key takeaways + references | 2% |

When a post has no math or no code, redistribute that share into body sections, not into the front matter sections. The opening does not get longer just because the post does.

**Worked example: L2 at 4,000 words**

| Section | Target |
|---|---|
| Insights + who | 120 |
| Why this matters | 160 |
| The problem | 320 |
| Worked example | 600 |
| Intuition | 400 |
| 3 body sections | 1,400 (≈465 each) |
| The math | 400 |
| Implementation | 320 |
| Limitations | 200 |
| Takeaways + refs | 80 |

Put these numbers in `outline.md` next to each heading. During drafting, check each section against its target when it is finished. Over by more than about 40% means the section is doing two jobs and should split. Under by more than 40% means there was less to say than expected, and the honest move is to shrink the tier rather than inflate the section.

---

## Choosing the tier

Ask three questions at brief time.

**How many distinct things must the reader learn?** One concept is L1. A concept plus its mechanism is L2. A concept plus mechanism plus formal treatment plus implementation is L3. A whole subsystem is L4.

**Does the topic have a real worked example that fits in one screen?** If yes, L1 or L2 works. If the smallest honest example needs a page, the post is L3 or larger.

**Who can read it?** Difficulty — `beginner`, `intermediate`, or `advanced` — is a separate axis from tier, decided by the prerequisites the post assumes rather than by its length. State both at brief time: an L1 primer on memory ordering is advanced, and an L4 pillar on how a row reaches disk can be beginner-friendly the whole way.

If the user does not say, propose a tier and a difficulty with their reasons and name the adjacent option, so overruling costs one word.

---

## The padding test

Run this before the gate. For each section, answer: what can the reader do after this section that they could not do before?

If the answer repeats another section's answer, one of them is padding. Cut the weaker one.

Common padding patterns to watch for, all of which read fine in isolation:

- A "background" section that restates the problem section
- A "why this is important" paragraph inside a body section, when there is already a Why this matters section
- Restating the worked example in symbols and calling it a new section
- A summary paragraph at the end of every section, when Key takeaways already exists
- Listing three variants of the same idea when one plus a sentence would do

---

## Expanding a post later

Posts grow. The point of the tier system is that growth is additive and local.

Protocol:

1. Read the existing `blog.md` and `outline.md`.
2. Name the target: a specific section, or a new body section.
3. Check the ledger. New depth usually needs new sources. If it does, run blog-research for that sub-topic only and append to the ledger.
4. Write only that section. Do not touch neighbouring prose.
5. Add figures if the new material crosses the figure ratio.
6. Update `tier` and `reading_minutes` in frontmatter.
7. Re-run the gate on the whole file, because a new section can duplicate an old one.

Never regenerate the whole post to expand it. The existing prose has been reviewed; regenerated prose has not, and the reader-facing quality silently resets.

---

## When to split instead of expand

Signals that a topic is a series rather than one post. Any one of them is enough:

- Expanding would push the post past about 10,000 words
- The outline has two sections that could each carry their own Insights
- The prerequisites for the second half are the conclusions of the first half
- More than about 18 figures

The decision itself, the tier and difficulty of each part, and the format of
`posts/<series-slug>/plan.md` plus its living `context.md` belong to
`references/series-planning.md`. Read it before proposing a split.
