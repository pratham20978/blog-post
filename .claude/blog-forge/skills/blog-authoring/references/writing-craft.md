# Writing craft

Load this while drafting prose. The structure files say what goes where; this one says how to write it.

---

## Voice

Write like a competent engineer explaining something to a colleague who is smart but has not seen this before. Not a textbook. Not a marketing page.

- Short sentences. If a sentence has three clauses, it is two sentences.
- Active voice. "TCP halves the window" beats "the window is halved".
- Second person for instructions, third person for mechanisms.
- Contractions are fine. Exclamation marks are not.
- Say the number. "About 40% slower" beats "significantly slower".

The reader is not impressed by vocabulary. They are impressed by understanding something they did not understand ten minutes ago.

---

## Openings

The first sentence decides whether the post is read. It must contain information, not throat-clearing.

Patterns that work:

| Pattern | Example |
|---|---|
| The surprising fact | "TCP treats packet loss as congestion. On wifi, most loss is not congestion." |
| The failing situation | "Your query takes 40ms on 10,000 rows and 8 seconds on 12,000. Nothing changed but the row count." |
| The wrong mental model | "Most people picture a hash table as an array of buckets. That picture predicts the wrong performance on deletion." |

Patterns that do not work, and why:

- "In this post we will explore..." — describes the post rather than teaching anything
- "X is one of the most fundamental concepts in Y" — true of everything, so it says nothing
- "Have you ever wondered..." — the reader searched for this, they already wondered
- A dictionary definition — the reader can read a definition anywhere

---

## Concrete before abstract

The single most reliable teaching move. Every abstraction gets a concrete instance first.

Not: "The amortised cost of insertion is O(1) because doubling distributes the copy cost."

Instead: start with an array of size 4. Insert 5 items. Show the copy happening on the 5th. Count the total copies for 16 insertions: 4 + 8 = 12 copies across 16 inserts, under one copy per insert. Then generalise.

The concrete version takes more words and teaches more. That trade is always worth it.

Then fade the concreteness deliberately: numeric instance, then symbolic form, then the general statement. Stopping at the concrete case means the reader cannot transfer the idea. Starting at the general one means they never load it in the first place.

---

## Introducing technical terms

Define a term at its first meaningful use, before any later sentence depends on it. A useful introduction answers four questions in place:

1. **What is its exact name?** Use the canonical name and expand an acronym the first time.
2. **What is it?** Name the category: mechanism, metric, data structure, protocol, configuration value, model, or something else.
3. **Why is it used here?** State the job it performs or the problem it solves in this context.
4. **When does it matter?** Tell the reader when to use it, inspect it, tune it, or choose something else.

For example: “Write-ahead logging (WAL) is PostgreSQL's append-only record of changes. PostgreSQL writes WAL before modified data pages so it can recover after a crash. You inspect or tune WAL when working on durability, replication, or sustained write throughput.” The reader now has the name, category, purpose, and conditions where it matters.

If two terms are often confused, state the boundary in the same place. For a command, tool, or setting, name what kind of control it is and what changing it affects. If the explanation is still abstract, follow it immediately with one concrete example.

Do not begin with a glossary dump. Introduce terms where the mechanism first needs them, do not repeat the full definition later, and never make an unpublished artifact or public code repository carry the definition. A public GitHub lab may hold runnable code, but the article explains what that code does, why it is used, and when to run it.

---

## Analogies

Useful and dangerous. The rule: every analogy names its own breaking point in the same paragraph.

> A database index works like a book index: you look up the term and it tells you the page. It breaks down on range queries, because a book index has no useful order between entries and a B-tree does.

An unqualified analogy gets remembered as the mechanism. The reader then reasons from the analogy and gets a wrong answer, and they have no way to know it was wrong.

Also: an analogy that only makes sense once you already understand the topic is not an analogy, it is a restatement. Test it against someone who does not know the topic yet.

---

## Explaining a figure

A figure never stands alone. The pattern is:

1. One sentence saying what the figure shows, before it
2. The figure
3. The caption, saying what to notice
4. Prose after it that uses the figure: "the queue in the middle is the bottleneck because..."

If the paragraph after a figure does not refer to anything in it, either the figure or the paragraph is wrong.

Words and pictures together teach better than either alone, but only when they are next to each other and describe the same thing at the same time. A figure two screens away from its explanation is worse than no figure.

---

## Serving two audiences at once

Students need scaffolding. Experts find the same scaffolding tedious. Both are reading the same file.

Resolution:

| Reader | Path through the post |
|---|---|
| Student | Insights → prerequisites → worked example → intuition → body → math |
| Expert | Insights → skims to body → math → limitations |

So: keep the main line complete for the student, and make everything the expert would skip **skippable at a glance**. Clear H2s, a jump list on long posts, `<details>` for derivations, and a Limitations section that has real content, because that is what an expert reads to decide whether you know the topic.

Never write "as you probably know" or "this should be obvious". It is a small phrase that tells one group they do not belong.

---

## Common mistakes sections

These are the highest-value words in the post and the easiest to write badly.

Bad: "Be careful with off-by-one errors."
Good: "The window size is the number of unacknowledged bytes, not packets. Sizing it in packets works until you hit a path with a smaller MTU, then throughput drops by the MTU ratio and nothing in the logs points at it."

The good version names the mistake, names the condition where it bites, and names the symptom. That is what makes it usable.

Source these from the ledger where possible: real issue trackers, real errata, real postmortems.

---

## Endings

End on the takeaway, not on a farewell. No "hope this helped", no "let me know in the comments", no summary of what the post covered.

The last thing before References is Key takeaways, and each bullet is a claim the reader can carry away and use.

---

## Things to avoid

Specific to generated prose, and the gate looks for them:

- Section-closing summary sentences. Every section ending with "In summary, X is important because..." adds length and no information.
- Tricolon padding: "faster, cheaper, and more reliable" where only one of the three was measured.
- Hedging stacks: "may potentially sometimes lead to". Say what happens, or say it is unknown.
- "It is worth noting that". Either note it or do not.
- Restating the heading as the first sentence of the section.
- Lists of three where two items are real and the third was invented for symmetry.
- Claiming a benefit with no number when the ledger has a number.
