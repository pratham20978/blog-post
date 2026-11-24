# Outline — multiple-comparisons-fwer-fdr (Part 9)

**Title (proposed):** Multiple Comparisons: FWER, FDR, and Tests You Didn't Count (59 chars; the plan's title, with "the" dropped to fit 60)
**Tier:** L3 — five things to learn (the two error rates, four procedures, dependence, the FDP's spread, uncounted tests); the worked example (3,170 p-values, five rules) fits one screen as a table plus one figure. Adjacent: L4 if the reader also needs Hochberg, Hommel and closed testing in depth.
**Difficulty:** advanced — assumes Part 5's type I error, p-values and power, and simulation with MCSE (Part 2). Adjacent: intermediate if the math section moved into `<details>`.
**Budget:** 6,500 words (plan estimate), 10 figures (ceiling 12). Lab G1, E1–E4.
**Four-point angle:** reconcile (by hand ↔ statsmodels ↔ SciPy ↔ the paper's published counts; R is the owner's private check), condition (independence, PRDS, arbitrary), measure (FWER, FDR, FDP spread with MCSE), read the output (q-values, adjusted p-values, library defaults). **Corrects:** "FDR 5% means 5% of my discoveries are false."

## Sections

| # | Heading (role) | Words | Job — what the reader can do after it | Figures | Keys |
|---|---|---|---|---|---|
| 0 | Insights + Level line | 200 | knows the answer: FWER for any-error claims, FDR for lists, BH needs a dependence condition, and the uncounted tests defeat both | — | — |
| 1 | 606 genes pass p < 0.05, and about 106 of them are noise (why-this-matters) | 260 | sees the cost of uncorrected testing on real data | FIG_01 | L10 |
| 2 | Which error rate a correction promises to hold (the-problem) | 520 | states V, R, FWER, FDP and FDR precisely, and 1 − (1 − α)^m | — | L02 |
| 3 | Four corrections on 3,170 breast-cancer genes (worked example) | 975 | runs Bonferroni, Holm, BH, BY and Storey's q-value by hand and reads the counts 2, 2, 94, 0, 162; reconciles with statsmodels, SciPy and the paper (q-values within one gene; BH gap reported) | FIG_02, FIG_03 | L09–L12, L14–L16 |
| 4 | FWER guards the worst list; FDR guards the average one (intuition) | 650 | picks the error rate from the claim being made; reads BH as "estimated false share ≤ q" | FIG_04 | L01, L02 |
| 5 | Does Benjamini–Hochberg keep 5% when the tests are correlated? | 500 | knows PRDS, measures FDR per procedure as ρ rises, sees Storey's adaptive q-values break | FIG_05 | L03, L04, L08, L13 |
| 6 | What does "FDR 5%" promise about the one list you have? | 450 | reads the FDP distribution: mean ~3%, yet P(FDP > 10%) ≈ 9% at ρ = 0.5 | FIG_06 | L07 |
| 7 | When does Benjamini–Hochberg fail, and what does Benjamini–Yekutieli cost? | 400 | knows the worst case (43.2% at m = 3,170), why it is contrived, and that BY finds 0 Hedenfalk genes | FIG_07 | L05, L06 |
| 8 | How many tests did a one-analysis study run? | 500 | counts researcher degrees of freedom; reproduces SNS's 60.7% (ours 61.6%) and sees the coding fork | FIG_08, FIG_09 | L21, L22, L25 |
| 9 | Why does a screened regression look significant? | 400 | measures Freedman's screen: noise F significant ~94% after screening at 0.25 | FIG_10 | L23, L24 |
| 10 | Why the step-up line controls the expected share (the-math) | 650 | follows the BH proof sketch, the BY factor, π0(λ) and the q-value formula | — | L03, L05, L09 |
| 11 | The five rules in thirty lines of NumPy (implementation) | 520 | runs the code and knows each library's default (R holm, statsmodels hs, SciPy adjusted p, qvalue version drift) | — | L14, L15, L18–L20 |
| 12 | Limitations and common mistakes | 325 | avoids: FDR as "my list's share", q-values under correlation, correcting only reported tests, two-sided PRDS, threshold ties | — | L07, L08, L26 |
| 13 | Key takeaways | 130 | — | — | — |
| 14 | Try it yourself | — | three exercises with answers | — | — |
| 15 | References (Lab downloads, Sources) | — | — | — | — |

Sum ≈ 6,480 words.

## Figure plan

| Placeholder | Section | Communicates | Route | Why (route) | Draft caption |
|---|---|---|---|---|---|
| FIG_01 | 1 | Hedenfalk p-value histogram over the null floor π0 = 0.67 | chart | measured data, 20 bins computed in code | The flat floor is what nulls produce; the spike near 0 is the signal, and the floor's height is π0. |
| FIG_02 | 3 | sorted p-values (log scale, ranks 1–300) with the Bonferroni, Holm, BH, BY and Storey boundaries and their crossings | plot | 300 points on a log axis; past the chart budget | Each rule is a line; it rejects up to the last p-value under its line (step-up) or the first one above it (step-down). |
| FIG_03 | 3 | π0(λ) against λ for both grids with the 3-df smoother; 0.676 (paper) vs 0.670 (qvalue 2.x) vs 0.664 (1.x) | plot | data plus a smoother curve | π0 is read off a smoothed curve, and the tuning moves it in the third decimal. |
| FIG_04 | 4 | which question maps to which rule (any false claim → Holm; a list → BH under independence/PRDS, BY otherwise; q-values with large m and weak dependence; uncounted tests → pre-specify) | mermaid | graph-shaped decision with branches; house theme, top to bottom | Pick the error rate from the claim, then the rule from the dependence. |
| FIG_05 | 5 | FDR of BH, BY and Storey (and FWER of Holm) against ρ = 0, 0.1, 0.2, 0.3, 0.5, MCSE bars | chart | measured simulation, five points per line | BH stays under q·π0 as correlation rises; Storey's estimated π0 lets its FDR climb past 5%. |
| FIG_06 | 6 | FDP histograms for BH at ρ = 0 and ρ = 0.5 with FDR and q marked | chart | measured distribution, two small multiples | Same FDR, different promise: correlated tests make most lists clean and a few very dirty. |
| FIG_07 | 7 | the worst-case joint law: with probability α/k exactly k null p-values land in the k-th slot ((k−1)α/m, kα/m], so each event triggers BH | placed | geometry of slots against the BH line; Mermaid cannot draw it | Each slot catches BH once, and their probabilities add up to α·Σ1/k. |
| FIG_08 | 8 | the four forks as layers: 3 outcomes × 2 stopping points × 4 condition comparisons × 4 model tests = 96 tests per sample | placed | layer stack with counts | One study, one reported test, 96 tests underneath. |
| FIG_09 | 8 | SNS Table 1 rates against our reproduction ± MCSE, with the effect-coding variant | chart | measured, 7 rows, horizontal bars | Our reading of their design lands within about a point of every row. |
| FIG_10 | 9 | histogram of second-pass F-test p-values from pure noise (log axis), 0.05 marked | chart | measured distribution | After screening at 0.25, the refitted regression's F test calls noise significant in about 94% of datasets. |

## Term map (new terms only)

| Term | First section | What | Why | When |
|---|---|---|---|---|
| family-wise error rate (FWER) | 2 | P(at least one false rejection) | the error a confirmatory claim needs | any single false claim is costly |
| false discovery proportion (FDP) | 2 | false rejections ÷ rejections in one study (0 if none) | the quantity people think FDR is | judging one list |
| false discovery rate (FDR) | 2 | the expected FDP over repetitions | what BH controls | screening long lists |
| step-down / step-up procedure | 3 | sorted p-values compared with rising thresholds, stopping at the first pass or failure from the top / bottom | Holm vs BH mechanics | reading adjusted p-values |
| adjusted p-value | 3 | smallest level at which a test would be rejected by the procedure | what libraries return | comparing with α |
| π0 | 3 | share of true nulls among the m tests | Storey's adaptive gain | large m, weak dependence |
| q-value | 3 | smallest FDR at which the test is called significant | Storey's per-test summary | reading genomics output |
| PRDS | 5 | positive regression dependence on the subset of true nulls | BH's dependence condition | correlated one-sided tests |
| adaptive procedure | 5 | a rule that estimates π0 from the data | why q-values gain and can break | strong correlation |
| researcher degrees of freedom / forking paths | 8 | analysis choices made after seeing data | the uncounted tests | any single "planned" analysis |

## Lab (G1 · runs anywhere · E1–E4 · access: none)

- `lab/multiplicity.py`: one file; stages `procedures` (by hand, matched to statsmodels 0.15.0 and SciPy 1.18.1, and to the paper's counts), `dependence` (ρ sweep, five procedures), `adversarial` (exact + one simulated check), `forking` (SNS), `freedman`, `all`; `--quick` budget. Streams `SeedSequence([stage, sub, seed])`; R from target MCSE.
- `lab/data/hedenfalk.csv`: index, stat, p (3,170 rows) with a provenance header (qvalue 2.15.0, LGPL; Storey & Tibshirani 2003; Hedenfalk et al. 2001). Recomputing p from the 317,000 null statistics fetches `hedenfalk.RData` from GitHub with its SHA-256 (013b681c…e383), optional.
- `lab/README.md`, `lab/captures/` (full and quick budgets), `lab/requirements.txt` (pinned).
- E1 reproduce the counts; E2 inspect q = π0 × BH-adjusted p and the tie at p(2) = 5/317,000 (Bonferroni's threshold to the last bit); E3 predict FDR and P(FDP > 10%) at ρ = 0.3 before running; E4 diagnose `--fault stepdown` (BH run as a step-down rule) caught by the reconciliation on `--quick`.
- Probe from the owner (2026-11-18): 16 CPUs, 3 GiB RAM available, no NVIDIA GPU, Docker unusable, uv present. The dependence stage works in chunks of 500 replicates (about 13 MB each).
