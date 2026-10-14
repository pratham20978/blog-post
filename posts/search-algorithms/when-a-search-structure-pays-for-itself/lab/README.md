# Lab — Hash Map, Sorted Array or Tree? When Each Pays for Itself

- **Grade:** G1 · runs anywhere (one Python file, standard library only)
- **Executed:** yes · 2026-10-14 · AMD Ryzen 7 5825U laptop, Ubuntu 26.04.1, no GPU
- **Provenance:** Linux 7.0.0-38-generic x86_64, AMD Ryzen 7 5825U (16 logical CPUs), 14 GB RAM; CPython 3.14.4; no third-party packages

This lab counts every number in the article, in one unit: a comparison is one call to the
function that compares two keys, whatever it returns. `pays_for_itself.py` is the one entry
point. On part 1's 16 keys it runs a scan, a closed-interval binary search and a top-down merge
sort with a counting comparison, carries a line-for-line Python port of `java.util.TreeMap`'s
insert, lookup and navigation methods, and inserts 16 keys with one shared hash into CPython's
own `dict`. It then scales the break-even from 16 keys to 2²⁰ and prices writes. Every count and
figure in the article comes from the `captures.json` this script wrote on the machine above;
facts about libraries and papers come from the article's sources.

The `TreeMap` port was checked, privately, against the real `java.util.TreeMap` from Temurin JDK
25.0.4.1 with a counting comparator: comparisons per insert, both tree shapes and their colours,
`get`, `floorKey(60)`, `subMap(40, true, 70, true)` and the insert of 50 all matched. That Java
harness is not part of the lab.

## Files

| File | Grade | Executed | What it is |
|---|---|---|---|
| `README.md` | — | — | this file: grade, setup, run order, exercises, cleanup |
| `pays_for_itself.py` | G1 | yes | the entry point: `worked`, `scale`, `writes`, `flood` or `all` |
| `notebook.ipynb` | G1 | yes | this README with a runnable cell under each step and exercise; built from it, never edited |
| `captures.json` | — | — | the author's run, machine-readable; every figure in the article reads it |
| `expected-output.txt` | — | — | the same run as printed, to compare with yours |

## What you need

| | |
|---|---|
| Hardware | any laptop |
| Software | Python 3.10 or later, standard library only. The shipped run used CPython 3.14.4; CPython 3.10.20 and 3.12.15 gave identical counts |
| Privileges | none: no root, no network, nothing outside this folder |
| Disk, network, time | under 100 KB; no download; the full `all` run took about 2 s |

## Run

```bash
python3 pays_for_itself.py all --out mine.json     # every stage, about 2 s
python3 pays_for_itself.py worked --out mine.json  # or one stage at a time
```

Each stage adds its own section to the file it writes; `all` rewrites the whole file. Without
`--out` the script writes `captures.json`, so pass `--out mine.json` to keep the shipped run for
comparison. Two options change the inputs: `scale --max-exp K` runs the break-even up to 2ᴷ keys
(default 20), and `writes --write-price P` prices one write (a shift, a store, a rotation or a
colour flip) at P comparisons instead of the default pair, 1 and 0.1.

## What to expect

The first line is the provenance of your run. Then, excerpted from the author's run:

```text
worked: scan hit avg 8.5 (miss 16); binary hit avg 3.375 max 5, miss avg 4.118 max 5; 61 probes [47, 74, 61]
worked: merge sort worst 49 (order [3, 53, 28, 79, 14, 68, 42, 91, 9, 61, 35, 85, 21, 74, 47, 97]), exact mean 45.6889, sample mean 45.700 [37..49] over 20000; floor ceil(log2 16!) = 45 (log2 16! = 44.250)
worked: break-even hits_worst_sort             q* = 9.561 -> ahead from lookup 10
worked: TreeMap insert 50 -> 5 comparisons, 0 rotations, 0 flips, 0 shifts, height after 6; floor(60) = 53 in 5; subMap[40,70] [42, 47, 53, 61, 68] in 11 comparisons
scale: n= 1048576 sort worst  19922945 (random        -) binary hit 19.000 miss 20.000 q* hits  38.00 misses 19.00 (2 lg n - 2 = 38)
writes: n= 65536 write price 1.0: array insert 32785.0, lookup 15.00 -> wins below 50.0% writes (1.00 per read); TreeMap insert 19.50 (1.00 rot, 1.00 flips), lookup 15.50 -> wins below 99.94% writes (1770.5 per read); scan 32768.5
flood: colliding insert __eq__ calls [0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 11, 12, 13, 14, 15] total 128; lookup 61 10, 97 16, absent 16
```

**Exact on any machine:** every `worked`, `scale` and `writes` number. They are counts of
deterministic algorithms on fixed inputs; the sample of 20,000 merge sorts uses
`random.Random(2026)` and the random orders in `scale` use `random.Random(1987)`.

**Exact on CPython 3.10 to 3.14:** the `flood` counts, identical on 3.10.20, 3.12.15 and 3.14.4.
They depend on CPython's `dict` (its probe sequence, its first table size and when it grows), so
another implementation, such as PyPy, or a future CPython can give different totals. The script
replays the probe sequence from the 3.14 constants and prints whether the replay matches your
interpreter. The last `flood` line prints `siphash13` on Python 3.11 and later and `siphash24`
before; that name is the only line that differed between the three versions.

## Exercises

Do them in order. Each has a self-check you can mark yourself against, with the answer from the
author's run hidden below it. This is an L2 post, so the lab ships E1 to E3.

### E1 — Reproduce: the 10th lookup

Run `python3 pays_for_itself.py worked --out mine.json`. Find the line that says when sorting 16
keys with a worst-case merge sort catches up with scanning, and the three numbers it is built from.

**Self-check:** q\* = 9.561, ahead from lookup 10, from a sort of 49 and lookups of 8.5 against
3.375; your provenance line printed first.

<details><summary>Answer</summary>

`worked: break-even hits_worst_sort q* = 9.561 -> ahead from lookup 10`. The sort is 49
comparisons (`merge sort worst 49`), a successful scan averages 8.5 and a successful
closed-interval binary search 3.375, so the sort is repaid after 49 / (8.5 − 3.375) = 9.561
lookups. Every one of these numbers is a count, so yours must match exactly. If they do not, the
script was edited: compare its SHA-1 with the shipped file's.

</details>

### E2 — Inspect: why 128 and not 120

Sixteen keys with one shared hash should cost 0 + 1 + … + 15 = 120 comparisons if every key met
every earlier key once. CPython's `dict` paid 128. In `mine.json`, read `flood → colliding →
insert_eq_calls` and `extra_vs_model`, then work out which inserts paid more than the model and
how big the table was at each of them.

**Self-check:** the inserts that paid one extra comparison, counted from 1, and the table sizes
(in slots) during those inserts.

<details><summary>Answer</summary>

Inserts 4 to 11 each paid one extra comparison: `extra_vs_model` is
`[0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0]`. During inserts 4 to 6 the table has 8 slots,
and during inserts 7 to 11 it has 16; insert 11 looks its key up in the 16-slot table before the
table grows to 32. With every hash equal to 42, the probe sequence in the 8-slot table is slots
2, 4, 5, 2, 3, 0, … and in the 16-slot table 10, 4, 5, 10, 3, 0, …: the fourth probe returns to
the first key's slot and compares that key a second time. In the 32-slot table the first 16
probes are all different, so inserts 12 to 16 match the model. `replay_probes(16)` in the script
reproduces the whole list from those rules.

</details>

### E3 — Predict: the break-even at 16.8 million keys

The article's model says sorting is repaid after about 2 log₂ n − 2 successful lookups. Write
down your prediction for n = 2²⁴, then run
`python3 pays_for_itself.py scale --max-exp 24 --out mine.json`.

**Self-check:** within 1 of the printed `q* hits` at n = 16777216, for the reason the article
gives: the sort costs about log₂ n scans and each lookup saves half a scan.

<details><summary>Answer</summary>

2 × 24 − 2 = 46. The run prints `q* hits 46.00` and `misses 23.00` at n = 16777216: the sort
costs 385,875,969 comparisons and each successful lookup saves 8,388,608.5 − 23.0 = 8,388,585.5.

</details>

### E3 — Predict: a cheaper shift

At 65,536 keys, with a write priced like a comparison, the sorted array beats plain appending
up to 1.00 write per read. Predict the limit if a write costs a quarter of a comparison, then run
`python3 pays_for_itself.py writes --write-price 0.25 --out mine.json`.

**Self-check:** within 10% of the printed `per read` figure for the array at n = 65536, because an
insert's cost is almost all shifts while a lookup's saving does not change.

<details><summary>Answer</summary>

About 4: each insert now costs about n/2 × 0.25 while each lookup still saves about n/2, so the
array can afford 1 / 0.25 = 4 writes per read. The run prints `3.99 per read` for the array. The
red-black tree barely moves, from 1,770.5 to 1,926.7, because its insert is mostly comparisons.

</details>

## Safety and cleanup

- The script reads nothing but itself, opens no network connection and starts no service.
- It writes one file: `captures.json`, or the file named by `--out`.

```bash
rm -f mine.json
```
