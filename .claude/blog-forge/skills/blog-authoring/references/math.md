# Math in Markdown

Load this when the post has equations. CS education posts usually do: complexity bounds, probability, linear algebra, information theory, queueing.

---

## Delimiters

The blog renders with KaTeX. GitHub renders with MathJax. Both accept the same delimiters, so write once:

| Form | Syntax |
|---|---|
| Inline | `$O(n \log n)$` |
| Inline, safe | ``` $`O(n \log n)`$ ``` |
| Block | `$$ ... $$` |
| Block, alternate | a fenced ` ```math ` block |

Use the backtick-wrapped inline form when the expression contains `_` or `[` `]`, because the Markdown parser can grab those before the math renderer sees them and the equation silently breaks.

Do not use `\(...\)` or `\[...\]`. GitHub does not document them and support elsewhere varies.

Do not use `\label` and `\eqref`. Auto-numbering is not available. If an equation needs a number, write it by hand:

```markdown
$$
T(n) = 2T(n/2) + O(n) \tag{1}
$$
```

Then refer to it as "equation (1)" in prose.

---

## The two rules that matter

**1. Define every symbol on first use.**

Not: "where $\alpha$ is the smoothing factor". That is a name, not a definition.
Instead: "$\alpha$ is the smoothing factor, between 0 and 1. Higher values weight recent samples more, so the estimate reacts faster and is noisier."

For anything with more than about four symbols, add a table before the equations:

| Symbol | Meaning | Units |
|---|---|---|
| $W$ | congestion window | bytes |
| $R$ | round-trip time | seconds |
| $p$ | loss probability | dimensionless |

The table is also what lets a reader come back three months later and still parse the post.

**2. Every equation is followed by a plain sentence saying what it means.**

$$
\text{throughput} \approx \frac{MSS}{R\sqrt{p}}
$$

Throughput falls off with the square root of loss rate, so a link with 1% loss carries roughly a third of the traffic of one with 0.1% loss, holding round-trip time constant.

The equation is for the reader who thinks in symbols. The sentence is for everyone else, including the symbol reader six months from now.

---

## How much math to include

Include the math that changes what the reader can do. Cut the math that only proves you know it.

| Include | Skip or collapse |
|---|---|
| The result, and what it implies | Every algebraic step to reach it |
| The recurrence and its solution | The full induction proof |
| The bound and where it is tight | Asymptotic edge cases nobody hits |
| The assumption that makes it fail | Restating standard identities |

Long derivations go in a collapsible block so the main line stays readable:

```markdown
<details>
<summary>Deriving the bound</summary>

Full working here.

</details>
```

---

## Connecting math back to the worked example

The strongest move in a CS education post: use the same numbers from the worked example when you present the general form.

If the worked example used an array of size 4 growing to 16, then when the amortised analysis appears, substitute those same values back in and show the general result produce 12 copies, which the reader already counted by hand. The abstraction stops being a separate thing to trust and becomes a compression of something they already did.

---

## Complexity notation

Be precise, because sloppy notation here is the most common factual error in CS writing.

- $O$ is an upper bound, $\Theta$ is tight, $\Omega$ is a lower bound. Do not write $O$ when you mean $\Theta$.
- Say which operation and which case: "$O(n)$ worst-case lookup" not "$O(n)$".
- Amortised, expected, and worst-case are three different claims. Name which one.
- State the model when it matters: comparison model, RAM model, cache-oblivious.

Any complexity claim that is not standard textbook material needs a ledger entry with a source.

---

## Accessibility

KaTeX and MathJax emit real text and MathML, so screen readers can read equations. Rendering math as an image breaks that and breaks search. Only use an image if the expression genuinely cannot be expressed in LaTeX, which is rare.
