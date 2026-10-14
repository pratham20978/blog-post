---
name: lab-practice-guide
description: Write a step-by-step practice guide so Pratham can do a blog post's "Try it yourself" exercises and lab by hand, on a temporary setup, written for someone new to the subject. Use when they ask how to do, practise or perform a post's exercises or lab ("tell me step by step", "prepare the lab for me so I can practise", "I am unable to do the exercise"). The guide is a chat reply they type themselves. It never runs the exercise, and never edits the post or its shipped lab.
---

# Lab practice guide

Pratham learns a post by doing its exercises by hand. This skill turns a post's "Try it yourself" section and its `lab/` folder into a guide they can follow in a terminal. Write it for someone new to the subject: they told us "I am new to databases, tell me exactly".

## Hard rules

1. **They run it; you don't.** Read the post, the lab runner, its README, `captures.md`, and memory. Do not start servers, run exercise commands or "quickly verify" a step. They stopped exactly that on 2026-10-10: "I only asked so I can perform the exercise, not you". Checking that a file exists is fine, for example an extension's `.control` file. If a step can't be confirmed without running it, call it a prediction and say what to look for.
2. **Temporary setup only.** Every guide builds a fresh environment in its own folder under `$HOME` and ends by deleting it. Never point a guide at anything real: not the canery stack's Postgres (a Docker container serving the live site) and not `~/.cache/blog-pg-lab/pgdata` (earlier posts' lab data).
3. **Leave the post and its lab alone.** Shipped labs stay at the expert standard (see the `labs-stay-expert-standard` memory). The guide is a separate chat reply; add nothing to `lab/` or `blog.md`. If the audit finds an error in the post, say so in the guide and offer the fix as a separate edit for them to approve. Examples: an answer that names the wrong setting, or a query on the wrong table. Some posts are live.
4. **Same version and same data as the post.** Use the software version the lab used, and copy its data load verbatim from the runner. That way page counts, sizes and row addresses match the post. Say which numbers will differ: ids, log positions, file numbers, timings.

## Before writing: audit every exercise

For each exercise, read four things: the question, its answer, the worked example it builds on, and the lab code for the same step. Then answer:

- **What state does it assume?** If it says "after the lab's vacuums" or builds on the worked example, the guide must replay those steps first, in the same order, with nothing else in between.
- **Can anything change that state behind the reader's back?** Background workers, timed checkpoints, statistics that lag.
- **Does every query the post gives point at the object this exercise uses?**
- **Can a human actually do it?** A two-window exercise needs the first query to run long enough to switch windows and type.
- **Does the answer depend on state the reader can't see?** For example, when the last checkpoint happened.
- **Does a setting need a restart, or apply to one session only?**
- **Will a side effect distort the measurement?** Parallel workers, other open sessions.

Fix each trap in the steps, and tell the reader what the trap is and why the step avoids it. Known traps and the setup template are in `references/postgresql.md`. Read it for any PostgreSQL post, and add to it when a new trap turns up.

## Shape of the guide

1. **Opening.** One short paragraph: what they'll do, that they type everything on a throwaway setup, and any error in the post the audit found.
2. **Part 0 — the ideas you need first.** Every term the exercises use, one line each, in plain words. End with "Read alongside:" and the post's section titles.
3. **Part 1 — set up.**
   - The lines to paste into *every* terminal.
   - Create, start and connect.
   - The exact data load.
   - A warm-up that shows the post's first idea on their own machine.
   - Every action repeated later, as a named block: the full command, and where to type it.
4. **One part per exercise:**
   - The ideas it needs.
   - Numbered steps. Each command goes in its own block, then one line per piece saying what it does.
   - **Predict on paper**, placed before the step that reveals the answer, with the arithmetic laid out.
   - What you should see: a short excerpt, the line to look at, and numbers from the captures. Mark anything you haven't seen confirmed as a prediction.
   - The traps.
   - "Read alongside:" with the post's section titles.
5. **Clean-up.** Stop-and-delete commands, plus any other practice setups still around.
6. **Close.** Ask them to paste any output that doesn't match.

## Writing rules (from their questions)

- **Say where each command goes:** the shell prompt (`~ `) or the tool's prompt (for example `proclab=#`). In multi-window exercises, name the windows A and B and say which window each step uses.
- **Never use a shorthand you haven't defined.** "Run the reset" stopped them until the command and the place to type it were spelled out.
- **Explain every flag the first time it appears.** Use a small table, or one line per flag.
- **Cover shell syntax once, in setup.** `$VAR` reads a variable. `VAR=value`, with no spaces, sets one. In zsh, `echo (VAR)` is an error; they hit it.
- **Use simple English and short sentences.** Define a word before using it. Long is fine; padding isn't.
- **Use they/them for Pratham.**
- **Deliver in chat** unless they ask for a file.

## When they report back

If their output differs from the guide, explain why from how the mechanism works; don't run anything. If their output shows the post is wrong, say what the fix is and ask before editing the post. If it shows a new trap, add it to the references file.
