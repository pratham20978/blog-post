# Manifest — multiple-comparisons-fwer-fdr

Upload each file to the public MinIO `media` bucket under its suggested key, then put the URLs in `urls.txt` in this order (images first, then lab files) and swap them in with `scripts/fill_urls.py`, or send them to me. A re-rendered file keeps its name and key: upload it over the old object, then purge that URL in Cloudflare (`media/*` is served immutable).

## Images

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover-multiple-comparisons-fwer-fdr.png | placed | template cover in the series house layout, built by `_cover.py`: Figure 2 reduced to its argument, BH's last crossing at rank 94 in tangerine (the one use) against Bonferroni's flat line at rank 2; no external generator (`assets/cover-prompt.md` stays as the alternative) | — | — | blog/multiple-comparisons-fwer-fdr/cover-v1.png | The 200 smallest of 3,170 gene p-values on a log scale against two 5% rules: Benjamini–Hochberg's rising line keeps 94 of them, Bonferroni's flat line keeps 2 |
| FIG_01 | assets/fig-01-hedenfalk-histogram.png | chart | measured data, bins computed in code | — | original (our analysis and our simulations) | blog/multiple-comparisons-fwer-fdr/fig-01-v1.png | Histogram of 3,170 p-values in bins of 0.05: 606 in the first bin, the rest near a flat floor of about 107 per bin |
| FIG_02 | assets/fig-02-rejection-lines.png | plot | 300 points on a log axis, past the chart budget | — | original (our analysis and our simulations) | blog/multiple-comparisons-fwer-fdr/fig-02-v1.png | Sorted p-values for ranks 1 to 300 on a log axis, with the Bonferroni, Holm, BH, BY and Storey boundary lines and their crossings at 2, 94 and 162 |
| FIG_03 | assets/fig-03-pi0-smoother.png | plot | data plus smoother curves | — | original (our analysis and our simulations) | blog/multiple-comparisons-fwer-fdr/fig-03-v1.png | π0(λ) against λ from 0 to 1 for the Hedenfalk p-values, with three smoothing-spline recipes ending at 0.6758, 0.6699 and 0.6635 |
| FIG_04 | assets/fig-04-which-error-rate.png | mermaid | branching decision, house theme, top to bottom | — | original (our analysis and our simulations) | blog/multiple-comparisons-fwer-fdr/fig-04-v1.png | Decision flowchart: claims that stand alone lead to Holm; lists lead to BH, BY or Storey by dependence; post-hoc analyses lead to counting forks |
| FIG_05 | assets/fig-05-fdr-vs-correlation.png | chart | measured simulation, five points per line | — | original (our analysis and our simulations) | blog/multiple-comparisons-fwer-fdr/fig-05-v1.png | Line chart of false discovery rate against correlation 0 to 0.5: Storey rises from 0.050 to 0.272, BH falls from 0.0335 to 0.026, BY stays near 0.003 |
| FIG_06 | assets/fig-06-fdp-distribution.png | chart | measured distribution, two small multiples | — | original (our analysis and our simulations) | blog/multiple-comparisons-fwer-fdr/fig-06-v1.png | Two histograms of BH's false discovery proportion: tightly spread below 0.1 at correlation 0, a spike at 0 and a long tail past 0.3 at correlation 0.5 |
| FIG_07 | assets/fig-07-worst-case-law.png | placed | slot geometry against the BH line; Mermaid cannot draw it | — | original (our analysis and our simulations) | blog/multiple-comparisons-fwer-fdr/fig-07-v1.png | Five rows of events: in event Ek, exactly k null p-values fall in the k-th slot of width α/m, which happens with probability α/k and makes BH reject k |
| FIG_08 | assets/fig-08-forking-layers.png | placed | layer stack with counts | — | original (our analysis and our simulations) | blog/multiple-comparisons-fwer-fdr/fig-08-v1.png | Four stacked layers of choices with their counts: outcome times 3, stopping time times 2, conditions times 4, model times 4, giving 96 tests |
| FIG_09 | assets/fig-09-sns-reproduction.png | chart | measured rates against published ones, seven rows | — | original (our analysis and our simulations) | blog/multiple-comparisons-fwer-fdr/fig-09-v1.png | Dot plot of seven scenarios comparing the paper's false-positive rates with ours: close on every row, 61.4% against 60.7% for all four choices |
| FIG_10 | assets/fig-10-freedman-screen.png | chart | measured distribution, two small multiples | — | original (our analysis and our simulations) | blog/multiple-comparisons-fwer-fdr/fig-10-v1.png | Two histograms of the overall F test's p-value on a log axis: spread near 1 for the full fit, concentrated between 10^-5 and 10^-2 after screening |

## Lab downloads

| Placeholder | Local file | Suggested object key | Purpose |
|---|---|---|---|
| LAB_01 | lab/multiplicity.py | blog/multiple-comparisons-fwer-fdr/lab-v1/multiplicity.py | the entry point |
| LAB_02 | lab/data/hedenfalk.csv | blog/multiple-comparisons-fwer-fdr/lab-v1/data/hedenfalk.csv | the data with provenance |
| LAB_03 | lab/README.md | blog/multiple-comparisons-fwer-fdr/lab-v1/README.md | setup, run order, exercises |
| LAB_04 | lab/requirements.txt | blog/multiple-comparisons-fwer-fdr/lab-v1/requirements.txt | pinned versions |
| LAB_05 | lab/notebook.ipynb | blog/multiple-comparisons-fwer-fdr/lab-v1/notebook.ipynb | the README as a runnable notebook |
| LAB_06 | lab/captures/full.txt | blog/multiple-comparisons-fwer-fdr/lab-v1/captures/full.txt | the full-budget capture the post quotes |
| LAB_07 | lab/captures/quick.txt | blog/multiple-comparisons-fwer-fdr/lab-v1/captures/quick.txt | the quick-budget capture |
| LAB_08 | lab/captures/results-full.json | blog/multiple-comparisons-fwer-fdr/lab-v1/captures/results-full.json | full-budget numbers, machine-readable |
| LAB_09 | lab/captures/results-quick.json | blog/multiple-comparisons-fwer-fdr/lab-v1/captures/results-quick.json | quick-budget numbers, machine-readable |

`lab-multiple-comparisons-fwer-fdr.zip` bundles the nine lab files; it is not linked from the post (a draft cannot link both the files and an archive). Upload it and link it instead of the nine files after publishing if you prefer one download.

## Earlier parts named in the post (plain text, add links when live)

- *p-Values and Power: How Wrong Can a Significant Result Be?* (Part 5): the Level line and "The problem".
- *The Sampling Distribution* (Part 2): the Level line (Monte Carlo standard errors).
- Regression is named only as "later in this series" (Part 13), in "Why does a screened regression look significant?".
