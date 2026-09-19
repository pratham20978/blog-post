# Post structure

The section order is fixed. What varies by tier is how many body sections there are and how long each runs.

Rationale in one line: answer first for the skimmer, concrete before abstract for the learner, formal last for the specialist. The evidence for the middle part is the worked-example effect and concreteness fading; the evidence for the first part is that most readers scan rather than read.

---

## The order

| # | Section | Required | Job |
|---|---|---|---|
| 0 | frontmatter | yes | machine-readable metadata, drives tags and search |
| 1 | Page title | yes | rendered by the page shell; do not repeat it in Markdown |
| 2 | `## Insights` | yes | the answer, in the first 100 words |
| 3 | Who this is for | yes | difficulty, prerequisites, reading time |
| 4 | `## Why this matters` | yes | the hook, one real problem |
| 5 | `## The problem` | yes | define it precisely, before any solution |
| 6 | `## Worked example` | yes | one concrete case with real numbers |
| 7 | `## Intuition` | yes | what is really happening, in plain words |
| 8 | body sections | 1–6 | the actual teaching, tier-dependent |
| 9 | `## The math` | when relevant | formal treatment |
| 10 | `## Implementation` | when relevant | working code |
| 11 | `## Limitations and common mistakes` | yes | honest failure modes |
| 12 | `## Key takeaways` | yes | 3–5 bullets |
| 13 | `## Try it yourself` | optional | exercises with hidden answers |
| 14 | `## References` | yes | every source from the ledger that was used |

---

## Section definitions

### Insights
Two to four sentences. Most important takeaway first. Contains the primary keyword naturally, because this text is reused as the meta description and it is what search engines and answer engines extract.

Write it so a reader who reads nothing else has learned one true, useful thing.

Rendered as a GitHub alert so it reads as a distinct block:

```markdown
> [!NOTE]
> **Insights** — Two to four sentences here.
```

Bad: "In this post we will explore how TCP congestion control works."
Good: "TCP slows down when it sees loss, not when it sees congestion. That single design choice, made in 1988, is why your download stalls on a lossy wireless link even when the network has capacity to spare."

The bad one describes the post. The good one is the post's answer.

### Who this is for
One line, not a section body. Difficulty, prerequisites, time.

```markdown
**Level:** intermediate · **You need:** basic probability, big-O notation · **Time:** ~12 min
```

Stating prerequisites lets students know what to review and lets experts know they can skip ahead. Both save the reader time, which is the whole point.

### Why this matters
Two to four sentences. One real situation where this knowledge changes what you do. Not "this is a fundamental concept." A specific moment: a bug you cannot explain, a design choice you keep getting wrong, a number that does not make sense.

### The problem
State the problem precisely before any solution appears. Use real numbers. Name the constraint that makes it hard.

A reader who does not understand the problem cannot evaluate the solution. This section is where most explainers fail, because the author already knows the problem and forgets to state it.

### Worked example
The highest-value section for a learner. One concrete instance, walked step by step, with real numbers rather than symbols.

Rules:
- Numbers before symbols. Always.
- Show intermediate values, not just the answer.
- Keep the example small enough to follow by hand.
- Reuse this same example later in the math section so the reader sees the general form collapse back to something they already followed.

### Intuition
What is actually happening, in plain language. An analogy is allowed but must come with the line where it breaks:

> The sliding window behaves like a conveyor belt. The analogy breaks once you add selective acknowledgement, because a belt cannot have holes in it.

An unqualified analogy teaches a wrong model that is expensive to unlearn.

### Body sections
Between one and six, depending on tier. Each has a single job and a heading that names it. Prefer question-form headings, which help both scanning readers and answer engines: "Why does the window shrink on loss?"

Each body section should be able to state, in one sentence, what the reader can do after it that they could not do before. If it cannot, merge it or cut it.

### The math
Load `math.md` before writing this. Short version: define every symbol on first use, follow every equation with a plain-language sentence, put long derivations in a collapsible block.

### Implementation
Runnable and minimal. Not production code. Comments explain the why, not the what. Always tag the language on the fence.

Show enough inline code for the reader to understand the mechanism. If a useful runnable implementation is longer than about 40 lines, place it in the optional lab and publish that lab to a public GitHub repository. At the first relevant mention, link the public lab, say what it contains, and explain when the reader should use it. Later links may point to specific public GitHub files. Never link a relative local lab, notebook, script, or source file.

### Limitations and common mistakes
The section that separates a real article from a summary. Include:
- where the approach fails
- the mistake people actually make, stated as the mistake
- what to use instead, and when

Use a callout for the sharpest one:

```markdown
> [!WARNING]
> **Common mistake:** ...
```

### Key takeaways
Three to five bullets. Each is a complete claim, not a topic. "Loss is a congestion signal only because of a 1988 assumption" is a takeaway. "Congestion control" is a topic.

### Try it yourself
Optional. Two or three exercises, answers hidden:

```markdown
<details><summary>Answer</summary>

...

</details>
```

### References
Only sources that were actually used. Grouped by tier if there are many. Include the access date for anything that can change. Every target must be a public URL; a ledger entry or local file path is not a reader-facing reference.

---

## Website and public-lab boundary

The website contains the rendered contents of `blog.md` and images uploaded to public storage. A runnable lab may live separately in a public GitHub repository. The outline, research ledger, manifest, social copy, prompts, and editable diagram sources stay private.

The article must remain understandable without opening the lab: keep definitions, reasoning, expected behavior, and the core example in `blog.md`. The lab can carry full programs, setup automation, datasets, captured output, and exercises. Links may point to an article anchor, a public site route, a verified public HTTP(S) page, or the public GitHub lab. At publish time every image and lab link must be resolved.

If a lab exists, introduce it once at the first section that needs runnable code:

```markdown
> [!TIP]
> **Public GitHub lab:** [Open the runnable lab](LAB_REPO). It contains <specific files or experiments>. Use it when you want to <specific task>; the explanation and core example remain in this article.
```

Treat `LAB_REPO` as the GitHub repository root. Use `LAB_REPO/blob/main/<path>` for later draft file links when the public branch is `main`; otherwise use the actual branch in the final URL. `fill_urls.py` replaces the base placeholder after the lab is public. Do not mention private build artifacts as a place to find more detail.

---

## Progressive disclosure

The same post serves a second-year student and a senior engineer. That works only if depth is optional rather than mandatory.

Three tools:
- `<details>` blocks for derivations, proofs, edge cases, long output
- footnotes (`[^1]`) for asides and citations
- a jump-to list at the top for posts over about 4,000 words

The main line stays readable end to end without opening anything.

---

## Formatting rules

- No H1 in `blog.md`; the page shell owns it. Every section is H2. Sub-points are H3. Never skip a level.
- Paragraphs of two to four sentences. One idea each.
- A section that runs past about 400 words gets a subheading or a split.
- Prose for reasoning. Bullets for parallel items. Numbered lists for ordered steps. Tables for comparisons across two or more dimensions.
- Code fences always carry a language tag.
- Callouts: `> [!NOTE]` aside, `> [!TIP]` shortcut, `> [!WARNING]` common mistake, `> [!IMPORTANT]` do not skip this.
