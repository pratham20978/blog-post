<!--
Lab README template (blog-forge). Copy to posts/<slug>/lab/README.md; the rules are in
references/labs.md. Keep the three header lines exactly as written: the validator reads
the **Grade:** line, and the checklist reads **Executed:** and **Provenance:**. Delete every section marked (if ...) that does
not apply, and delete this comment.
-->

# Lab — <post title>

- **Grade:** <G1 · runs anywhere | G2 · local service | G3 · needs <resource>>
- **Executed:** <yes | partly | no> · <YYYY-MM-DD> · <the build machine, or the arranged resource>
- **Provenance:** <OS, CPU, RAM, disk; runtime and every pinned version; for G2 the server version and every non-default setting; for G3 the hardware, drivers and instance>

<Two to four sentences: which teaching outcome of the article this reproduces, the one entry point,
and what it writes. Say whether the article's numbers come from this run, from a labelled model
("model inputs"), or from the article's sources.>

## Files

| File | Grade | Executed | What it is |
|---|---|---|---|
| `README.md` | — | — | this file: grade, setup, run order, exercises, cleanup |
| `<run.py>` | G<n> | yes | the entry point |
| `<expected-output.txt>` | — | — | the run the article quotes, to compare with yours |
| `<results-schema.json>` | — | — | (if a G3 file was not run) what a run writes; empty on purpose |

## What you need

| | |
|---|---|
| Hardware | <"any laptop", or the minimum, e.g. "one NVIDIA GPU with about 1 GB free"> |
| Software | <runtime and pinned versions, and how to get each without root> |
| Privileges | <"none: no root, no Docker, nothing outside this folder and <scratch dir>", or the G3 resource> |
| Disk, network, time | <download sizes, first-run fetches, wall-clock time> |

## Run

```bash
<one obvious path: setup first, then the entry point>
```

> [!WARNING]
> (G2 and G3) <each step that stops, crashes or reconfigures a service>. Point this at a throwaway
> environment, never at anything you care about.

## What to expect

<what a correct run prints, excerpted; which values must match exactly, which may vary, by how
much, and why>

## What was and was not executed

(if **Executed** is partly or no)

- `<file>` was run; its output is `<file>`.
- `<file>` was syntax-checked. <The paths exercised without the resource, and how.> <What needs
  the resource and has not been run.> `results-schema.json` defines exactly what a run writes and is
  empty on purpose: no number here is invented.

## The provenance line

(G3, or any lab whose numbers depend on the machine) A number from this lab is publishable only
with the line the entry point prints first:

```text
Captured <UTC time> on <hardware>, <driver and runtime versions>, <software versions>, <instance>.
```

## Exercises

Do them in order. Each exercise has a self-check you can mark yourself against, with the answer
hidden below it. This is an <L3> post, so the lab ships E1 to E<4>.

### E1 — Reproduce: <the article's headline number>

<what to run, and what to compare it with>

**Self-check:** <matches `<capture>` within <tolerance>, and the provenance line printed>

<details><summary>Answer</summary>

<the values the author's run produced, and what a mismatch usually means>

</details>

### E2 — Inspect: <the intermediate>

<where to look, and with which tool from the article>

**Self-check:** <the named value or invariant you should find>

<details><summary>Answer</summary>

<the value, and how to read it>

</details>

### E3 — Predict: <the one change>

<the change. Write your prediction (direction, rough size, reason) before you run it.>

**Self-check:** <direction and size within <range>, for the reason the article gives>

<details><summary>Answer</summary>

<the author's run, and the reason>

</details>

### E4 — Diagnose: <the symptom> <add "(needs G3: <resource>)" only when it does>

<how to inject the fault inside the disposable environment, and what you will see>

**Self-check:** <symptom, cause, the observation that proves it, the fix and the check that it held>

<details><summary>Answer</summary>

<all four, and how to put the environment back>

</details>

### E5 — Extend: <what to build>

<the extension, and its limits>

**Self-check:** <the acceptance test your result must pass>

## Safety and cleanup

- <what the lab touches, and what it never contacts: no live service, no shared lab server, no
  production storage>
- <what it writes, and where>

```bash
<the commands that return the machine to where it started>
```