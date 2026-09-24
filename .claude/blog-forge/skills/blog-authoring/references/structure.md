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

Show enough inline code for the reader to understand the mechanism. If the runnable implementation needs a separate file, place it in `lab/` and point the body to `[Lab downloads](#lab-downloads)`. Put the actual file links only in the final References section. Never link a relative local lab, notebook, script, or source file.

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
This remains the final H2. When a lab exists, begin it with `### Lab downloads`, followed by one link and one purpose per downloadable file. Put research sources under `### Sources` or the existing source groups after the downloads. Include only sources actually used and an access date for anything that can change. Every target must be public; a ledger entry or local file path is not reader-facing.

---

## Website and downloadable-lab boundary

The website contains the rendered contents of `blog.md`. Images and the explicitly listed lab files live in public MinIO object storage. The outline, research ledger, manifest, social copy, prompts, caches, secrets, and editable diagram sources stay private.

The article must remain understandable without downloading the lab: keep definitions, reasoning, expected behavior, and the core example in `blog.md`. The lab can carry full programs, setup automation, small datasets, captured output, and exercises. At publish time every image and lab link must be resolved.

If a lab exists, the final section begins like this:

```markdown
## References

### Lab downloads

- [`run.py`](LAB_01) — runs the experiment and prints the measured result.
- [`schema.sql`](LAB_02) — creates the disposable database objects used by the experiment.

### Sources
```

Number placeholders in manifest order. `fill_urls.py` replaces each with its public `https://minio.canery.in/media/...` URL. Do not mention private build artifacts as a place to find more detail.

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
