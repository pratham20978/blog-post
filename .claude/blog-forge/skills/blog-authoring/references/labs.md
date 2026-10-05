# Runnable labs

Load this in the brief of every post, to grade its lab and run the probe, and again whenever a post needs downloadable code, commands, data, or captured output.

## Two axes: grade and ladder

Every lab sits on two axes, the way every post has a tier and a difficulty.

- **Grade, G0–G3,** is what it takes to *run* the lab. It sets what the author must show, label and
  record. Decide it in the brief, before research: a lab that cannot run here changes what the post
  can claim, and so what must be researched.
- **Ladder, E1–E5,** is what the reader *does* with it: reproduce, inspect, predict, diagnose,
  extend. The post's tier sets how far up the ladder it goes.

About a lab, say "grade" and "rung", never "tier". Tier is the post's depth (L1–L4), and older series
used "Tier A/B/C" for labs with meanings that conflict. See [Legacy tier letters](#legacy-tier-letters).

## Environment grades

| Grade | Name | What it takes to run | Examples |
|---|---|---|---|
| **G0** | By hand | Nothing is executed. Every number is worked on the page, evaluated from a closed form, or cited. | every *Image Processing by Hand* part; a derivation; relational algebra worked on paper |
| **G1** | Runs anywhere | Any laptop with no service, no root and no special hardware: the standard library, a compiler already present, or a pinned user-space environment (`uv`, CPU wheels). Public downloads are allowed, and the README gives their size. | a queue model in plain Python; probe counts in Python or C; a Laya trace in CPU PyTorch; SQLite or DuckDB over a file |
| **G2** | Local service | A process the reader starts and stops without root, bound to localhost or to a socket in a scratch directory. | PostgreSQL from `initdb` and `pg_ctl`; a primary and a standby on one host; Patroni with etcd; pgBouncer; a Citus coordinator and two workers on one host; a local MinIO; Hadoop or Kafka in single-node mode from release tarballs and a JDK tarball |
| **G3** | Needs access | Something a laptop in user space cannot provide: hardware (a GPU, several GPUs, several machines), privileges (root, Docker, Kubernetes, `tc netem`, sysctl, huge pages), or a paid, credentialed or gated service. | one NVIDIA GPU; a multi-GPU node; three hosts with a real network between them; a Kubernetes operator; a managed cloud database; an early-access API |

A lab's grade is the grade of its most demanding file. A lab may mix grades: a G1 model beside an
unrun G3 harness is normal, and the README's file table says which file is which. A G3 README names
the resource, as in `G3 · needs one NVIDIA GPU`.

The grade describes the lab for its reader. Whether *this* build machine can run it is a separate
question, and the probe answers it. A GPU lab is G3 even on a machine that has a GPU, and there it
needs no access request. The grade also belongs to the lab, not to the topic: Hadoop is G2 in
single-node mode, and G3 only when the post needs several real nodes.

### What each grade obliges

Obligations accumulate: a G2 lab also meets everything G1 requires.

- **At every grade: no invented numbers.** A number the article presents as measured came from a
  file in this lab that was executed. Any other number carries a ledger key and the words that say
  where it came from: *documented*, *reported by*, *computed from the published config*, or *model
  inputs*. A labelled model may carry the worked example when a shipped file computes it, the
  figures import it, and each caption says "model inputs". Exercise answers follow the same rule.
- **G0.** Put an `> [!IMPORTANT]` notice before `## Why this matters` saying nothing was executed
  and how every number was obtained. Name any private arithmetic cross-check in that notice, and do
  not ship it. No timings and no measured curves. When the post has no `lab/`, add
  `**Lab grade:** G0 — <reason>` to `manifest.md`. The ladder lives in `## Try it yourself`.
- **G1.** The author ran it on the build machine. It ships captured output (`expected-output.*`,
  `captures.*` or a results JSON), a provenance line (ISO date, OS, CPU, runtime, every pinned
  version), and the tolerance a reader's run must meet. For example: "probabilities to four
  decimals; logits may differ in the fifth, because CPUs add numbers in different orders."
- **G2.** Use a fresh, disposable environment on a real disk that listens only on localhost or a
  socket. Never use the shared lab server or a live service, and make the runner refuse a target
  that looks lived-in. The provenance line adds the server version and every non-default setting. A
  `> [!WARNING]` names each step that stops, crashes or reconfigures the service. Cleanup returns
  the machine to where it started. When a distributed topic runs on one host, say what one host
  cannot show: no real partition, one shared clock, and failures limited to `kill -9`, `SIGSTOP`
  and `pg_ctl -m immediate`. Never present a one-host result as a network result.
- **G3, captured.** The lab ran on the arranged resource. The provenance line names the hardware,
  drivers and instance exactly. The recorded output ships, so a reader without the resource can
  still do E1 and E2 from it.
- **G3, not captured,** because the request was declined, is pending, or the need was found late.
  Ship the harness syntax-checked, with every path that does not need the resource exercised. Ship
  `results-schema.json` defining what a run writes, empty on purpose. Mark the README
  `**Executed:** no` or `partly` and add `## What was and was not executed`. Label every affected
  number in the article as documented, never measured. Where the teaching allows it, add a G1 core
  (a labelled model) so the worked example and the required rungs still run. List the harness in
  `access.md` under `## Capture backlog`.

## Probe the build machine

Run the probe in the brief for a standalone post, and while drafting the plan for a series. Re-run
it at the start of every series member and compare it with `access.md`: a machine that gained a GPU
or lost disk space changes what the plan can promise. The probe is read-only. It installs nothing,
never runs `sudo`, and connects to no service, including the shared lab server.

```bash
uname -srm; (. /etc/os-release && echo "$PRETTY_NAME")
echo "cpus=$(nproc)"; free -g | awk '/^Mem:/ {print "ram_total=" $2 "G ram_available=" $7 "G"}'
df -h "$HOME" | awk 'NR==2 {print "disk_free=" $4 " on " $6}'
lspci 2>/dev/null | grep -iE 'vga|3d controller|display' | sed 's/^[^ ]* /gpu: /'
command -v nvidia-smi >/dev/null && nvidia-smi -L || echo "nvidia_gpu=none"
echo "groups=$(id -nG)"   # membership only: a sudo group does not mean the agent may use it
d=unusable; for s in /var/run/docker.sock "${XDG_RUNTIME_DIR:-/nonexistent}/docker.sock"; do
  test -w "$s" && d="usable ($s)"; done; echo "docker=$d"
for t in gcc make cmake meson ninja bison flex java go rustc uv psql podman kubectl; do
  command -v "$t" >/dev/null && echo "$t=yes" || echo "$t=no"; done | paste -sd' '
for h in zlib.h readline/readline.h openssl/ssl.h zstd.h lz4.h event.h yaml.h; do
  test -e "/usr/include/$h" && echo "$h=yes" || echo "$h=no"; done | paste -sd' '
```

Read the GPU line for the vendor. An integrated AMD display controller is not an NVIDIA GPU, and a
`/dev/kfd` node proves nothing on its own. Add a line only for something a planned lab needs; the
probe is not an inventory. Keep its output in `access.md` as a dated snapshot.

## Set it up yourself, or ask

The owner is asked only for what the agent cannot arrange itself. **Set it up yourself, without
asking,** when all six of these hold:

1. It installs only under `$HOME` (for example `~/.cache/<lab>`) or the post's scratch directory.
2. It needs no root, no group change, and no kernel, sysctl or service-manager change.
3. It needs no account, credential, payment, gated download, or licence accepted on the owner's behalf.
4. Deleting one directory undoes it.
5. It leaves headroom: it needs less than the probe's available RAM minus 2 GiB, and less than half the free disk.
6. It is a new, disposable instance, never the shared lab server, the canery stack, or production MinIO.

That covers most labs: `uv` environments and CPU wheels; `cmake`, `meson` and `ninja` from pip inside
a venv; a PostgreSQL release built from its tarball; extensions built with `pgxs`; a missing library
such as libevent built from source into a user prefix; static binaries such as etcd, a local MinIO,
Prometheus and DuckDB; a JDK tarball; several servers on different ports. Record each one in
`access.md` under `## Self-provisioned`, with how to undo it.

**Ask** only when all three of these are true:

- **Load-bearing.** The worked example, a key figure, or a point the post settles depends on
  behaviour only that environment produces.
- **No honest substitute.** Every user-space substitute (instances on one host, a labelled model, a
  documented T1–T3 capture) would turn that measured claim into a documented one, or teach
  something false.
- **Not self-providable.** The probe shows the resource missing, and at least one of the six
  conditions above fails.

If the first is false, build at the lower grade and say nothing. If the second is false, use the
substitute and name it in the README. Never ask for root to save time. Never ask again for something
the owner declined, unless the owner reopens it.

## Access requests

Raise one request per missing resource per series, listing every part that needs it, never one per
part. Show it in exactly this form:

```markdown
**Access request AR-<nn>: <resource, five words>** (<parts, or "this post">)

- **Need:** <the resource, its minimum spec, and for how long>
- **Why quality needs it:** <the load-bearing claim, figure or worked example that stays documented instead of measured without it>
- **Probe found:** <the probe line that shows it missing>
- **Smallest arrangement:** <the cheapest concrete way to provide it; the exact command when the owner runs one>
- **If declined:** <the grade it drops to, what ships instead, which claims become documented, which rungs lose execution>
- **Answer:** `grant`, `decline` or `later`
```

A filled example, from the NVIDIA series:

```markdown
**Access request AR-01: one NVIDIA GPU** (parts 3, 4, 5, 8, 9, 10)

- **Need:** one NVIDIA GPU with about 1 GB free, its driver, and a CUDA build of PyTorch; one short session per part (Part 3's two scripts take about two minutes).
- **Why quality needs it:** Part 3 settles whether `nvidia-smi` reads 100% on a GPU that is mostly idle, and only `util_probe.py` on hardware can settle it; without it the post reports both published readings and does not choose.
- **Probe found:** `nvidia_gpu=none` (the only display controller is an integrated AMD APU).
- **Smallest arrangement:** SSH access to one rented single-GPU instance per session; nothing on this machine changes.
- **If declined:** each part ships a G1 labelled model for its worked example and its G3 harness unrun with an empty `results-schema.json`; measured claims become documented ones; E4 runs on the model.
- **Answer:** `grant`, `decline` or `later`
```

**When to raise it.**

- **Series:** in the Checkpoint S message, after the part list. Each part's `**Lab:**` line in
  `plan.md` names its request and its grade under either answer.
- **Standalone post:** in the brief, after the tier and difficulty lines. A brief that carries a
  request stops for the answer before research. This is the only time the brief is a stop.
- **Series planned before these rules** (it has no `access.md`): at the start of its next member,
  run the probe, create `access.md`, and raise every request the series' remaining parts need,
  before that member's research. Unrun harnesses from earlier parts go into its capture backlog.
  A brief that says "look for a model instead" is the old default, not an answer from the owner.
- **Found later:** a build that the six conditions cannot fix, or a resource that disappeared, is
  raised at the next checkpoint. It is never absorbed as a silent downgrade.

**What the answers mean.**

- `grant`: the owner arranges it. Re-run the probe, or reach the resource, before use. Capture on
  it, and mark the request `fulfilled`.
- `decline`: build the fallback the request promised, and do not ask again.
- `later`, or no answer: build the fallback now and keep the harness in the capture backlog. When
  access arrives, capture and publish the result as an expansion: re-run the gate and bump `updated`.

A request never blocks the rest of the plan, and its "If declined" line is binding: the build may
not drop further than it promised.

### Recording: `access.md`

Record the probe and every request in `access.md`. For a series it lives at
`posts/<series-slug>/access.md`, beside `plan.md` and `context.md`; for a standalone post at
`posts/<slug>/access.md`. It is a private build artifact: never linked, never uploaded. Read it with
`plan.md` and `context.md` before every member. The context's lab bullet names the lab and its
grade, and points here.

```markdown
# Lab access — <series or post title>

## Probe — <YYYY-MM-DD>

<the probe's output, unedited>

## Requests

| ID | Need | Parts | Raised | Answer | Answered | Grade as built |
|---|---|---|---|---|---|---|
| AR-01 | <resource> | <parts> | <checkpoint, date> | <grant, decline, later, fulfilled> | <date> | <e.g. G1 model + G3 harness unrun> |

## Self-provisioned

| What | Where | For | Undo |
|---|---|---|---|
| <e.g. PostgreSQL 16.2 from the pgserver wheel, contrib built with pgxs> | <`~/.cache/blog-pg-lab`> | <parts> | <shared and live: remove only when the series closes> |

## Capture backlog

| Part | Files | Waiting on | Then |
|---|---|---|---|
| <n> | <`lab/<harness>.py`> | <AR-nn> | run, fill `results.json`, expand the post |
```

## The exercise ladder

Every lab carries a ladder, and the reader climbs it in order. Each rung trains a different skill,
and E4 is the one that prepares a reader to be on call for the system. Every exercise has a
**self-check**: a criterion the reader can mark right or wrong alone. It can be a number with a
tolerance, an invariant, a test on the output, or a named cause with the observation that proves
it. "Compare with a colleague" and "think about why" are not self-checks.

| Rung | Name | The reader ... | Self-check |
|---|---|---|---|
| **E1** | Reproduce | runs the one obvious path and gets the article's numbers | matches the shipped capture or the article within the stated tolerance, with the provenance line printed |
| **E2** | Inspect | finds and reads one intermediate the article describes but does not print in full, using the tool the article taught | a named value or invariant, stated before the answer |
| **E3** | Predict | changes one named input, **writes the prediction first**, then runs it | direction and rough size against the author's run, with the reason from the article's model; a right number for the wrong reason fails |
| **E4** | Diagnose | meets a fault injected into the disposable environment and finds its cause | symptom, cause, the one observation that proves it, and the fix with a check that it held |
| **E5** | Extend | builds what the article did not: a new measurement, a variant, the method on new input | an acceptance test the result must pass; there is no single answer |

The tier sets the highest rung a post must ship. Rungs below it are never skipped, and higher rungs
are welcome.

| Tier | Must ship | Exercises |
|---|---|---|
| L1 | E1–E2 (E3 recommended) | 2–3 |
| L2 | E1–E3 | 3–4 |
| L3 | E1–E4 | 4–6 |
| L4 | E1–E5 | 5–8 |

Ship at most two exercises per rung: this is a ladder, not a problem set. Difficulty changes the
answer, not the rungs. A beginner answer shows every step; an advanced answer gives the criterion
and the key observation.

**The ladder at each grade.**

- **G0:** pen and paper, in `## Try it yourself`. E1 redoes the worked example to its intermediate
  values. E2 reads a quantity off a figure or table. E3 predicts a changed input by hand. E4 finds a
  planted error in a worked computation. E5 carries the method to a new case.
- **G1–G2:** as in the table. E4's faults stay inside the disposable environment (a killed process,
  a full scratch disk, a wrong setting), and the answer includes the recovery.
- **G3:** E1 and E2 must work from the recorded output or the G1 core, without the resource. A rung
  that needs the resource says so in its heading: `(needs G3: one NVIDIA GPU)`. When nothing was
  captured, every required rung needs a path at G2 or below, and a G3-only rung is an extra.

**Format.** Put the ladder in `lab/README.md` under `## Exercises`, or in `## Try it yourself` for a
G0 post:

```markdown
### E3 — Predict: <what changes>

<the task in two to four sentences: the file, the input, the command>

**Self-check:** <what the reader marks themselves against>

<details><summary>Answer</summary>

<the answer and why, with the value the author's own run produced>

</details>
```

Every E1–E4 answer comes from the author's own run, or is worked by hand at G0. E5's answer block is
optional. In the article, `## Try it yourself` keeps two or three exercises that can be answered from
the article alone, each labelled with its rung, and ends by pointing to the full ladder under Lab
downloads.

## Legacy tier letters

Published labs keep their letters and are not edited. New parts of those series state the grade
and, for continuity, the old letter: `**Grade:** G3 · needs one NVIDIA GPU (this series' Tier B)`.

| Series | Old label | Meant | Grade |
|---|---|---|---|
| nvidia-stack | Tier A | no GPU | G1 as built (plain Python, wheels read over HTTP); the plan's "CUDA development container" route would be G3 here, because Docker is unusable |
| nvidia-stack | Tier B | one NVIDIA GPU | G3 · needs one NVIDIA GPU |
| nvidia-stack | Tier C | multi-GPU or datacenter | G3 · needs <n> GPUs and <interconnect> |
| foundational-architectures, frontier-models | Tier A | standard library only | G1 |
| foundational-architectures, frontier-models | Tier B | CPU PyTorch in a pinned `uv` environment | G1, with the download size in the README |
| frontier-models | Jev with TypeSafe early access | credentialed, per-token API | G3 · needs API credentials |
| postgresql-foundations | the shared real-server lab | PostgreSQL 16.2 from the pgserver wheel, contrib via pgxs | G2 |
| search-algorithms, diffusion-models | stdlib Python, one C lab | counts and identities | G1 |
| image-processing | "nothing is executed" | by hand | G0 |

"Tier B" is G3 in one series and G1 in two others. Read the grade, never the letter.


## Choose one file or several

Prefer one file when it can run by itself and remain readable. Split only when files have genuinely different responsibilities or tools require the split.

Use multiple files for combinations such as:

- `README.md` — grade, what was executed, provenance, prerequisites, run order, expected result, the exercise ladder, cleanup; start it from `assets/lab-readme-template.md`
- `run.py`, `run.sh`, or equivalent — the single obvious entry point
- `schema.sql` or `setup.sql` — disposable database setup
- `requirements.txt`, `pyproject.toml`, or package manifest — dependencies
- a small input fixture — only when the experiment needs it
- `expected-output.txt`, `.json`, or `.md` — stable captured output worth comparing

A multi-file lab requires `README.md`, and every graded lab carries one, because the grade and the ladder live there. Keep the directory shallow unless the language or build tool requires nesting.

## Quality rules

- Make the lab reproduce one teaching outcome from the article. Do not turn it into a second product.
- Use deterministic inputs or document unavoidable variation.
- Give one obvious run path and include cleanup when the lab creates resources.
- Default to a disposable/local environment. Never target production services or destructive operations by default.
- Keep credentials out. Do not include `.env`, tokens, keys, cookies, database dumps with private data, or machine-specific absolute paths.
- Exclude caches, virtual environments, compiled objects, build directories, dependency vendor trees, logs, and unrelated files.
- Add comments for non-obvious decisions, not line-by-line narration.
- Syntax-check every source file. Run everything the grade allows on this machine; what could not run follows [What each grade obliges](#what-each-grade-obliges).

## Publication contract

Every publishable file receives its own manifest row and download link:

```markdown
| Placeholder | File | Suggested object key | Purpose |
|---|---|---|---|
| LAB_01 | `lab/README.md` | `labs/<slug>/README.md` | setup and run order |
| LAB_02 | `lab/run.py` | `labs/<slug>/run.py` | runnable experiment |
```

Use versioned object keys when changing an already published file. Upload to the public MinIO `media` bucket, producing URLs under `https://minio.canery.in/media/`.

Set an accurate `Content-Type`. When the upload workflow supports object metadata, set `Content-Disposition: attachment; filename="<name>"` so clicking the article link downloads the file instead of rendering it in the browser.

### The whole-lab archive

A lab with more than one file may also ship as one zip, so a reader downloads it in one click and
the owner uploads one object. Build it from the post folder, with exactly the lab's publishable
files and nothing else:

```bash
cd posts/<series-slug>/<slug> && rm -f lab-<slug>.zip && zip -r -X lab-<slug>.zip lab -x '*/__pycache__/*' '*.pyc' '*/.*'
```

- Name it `lab-<slug>.zip`, keep it in the post folder beside `blog.md`, and upload it to the
  bucket root, so its URL is `https://minio.canery.in/media/lab-<slug>.zip`. Write that final URL in
  `blog.md` from the start; it is not a `LAB_XX` placeholder, and `urls.txt` does not list it.
- Link it once, as the last line under `### Lab downloads`, for example
  `- [Complete lab](https://minio.canery.in/media/lab-<slug>.zip) — every file above in one zip.`
  Links that point every per-file line at the archive (an archive-only section) are also valid.
- Add an `ARCHIVE` row to the lab table in `manifest.md` so the upload checklist names it; the
  validator and `fill_urls.py` read only `LAB_XX` rows, so this row is for the owner.
- **Rebuild the zip after any change to `lab/`.** The validator opens the local archive and fails
  the post when it is missing a lab file, holds anything outside the lab, or holds an older copy of
  a file. It links at most one archive, and it only warns when the zip is not in the post folder.

Put all download links at the end of `blog.md`, inside the final References section:

```markdown
## References

### Lab downloads

- [`README.md`](LAB_01) — prerequisites, run order, expected output, and cleanup.
- [`run.py`](LAB_02) — runs the experiment described in the Implementation section.

### Sources
```

The body may link to `#lab-downloads`. It must not link to `lab/run.py` or another local path. Keep the explanation and core example in the article; downloads are for execution and reproduction.
