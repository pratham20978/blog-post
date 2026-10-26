# Asset manifest — distributions-as-generative-stories

Series `statistics-for-data-scientists`, part 1. **Status: local draft assets ready for upload.** Upload the
eleven PNGs and the ten lab files to the public `media` bucket under the object keys below, write the
resulting URLs to `urls.txt` in table order (COVER, FIG_01–FIG_10, then LAB_01–LAB_10), then run
`fill_urls.py`. Upload the lab zip separately, to the bucket root (see **Lab files**). Nothing has been
published, so every key is new; the figure names carry the slug because the bucket is flat.

Every figure is our own analysis, drawn from the lab's `captures.json` by `assets/_figs.py` (Figure 1 by
`assets/_mermaid.py` from its `.mmd`, the cover by `assets/_cover.py`). The `source` route was considered
first for every paper-backed figure (ledger, **Figure candidates**). Clauset, Shalizi and Newman's
Fig. 4.1a, Kleiber and Zeileis's Fig. 1, Limpert, Stahel and Abbt's Fig. 2 and Böhning's Fig. 3 are
directly relevant but carry no reuse licence beyond arXiv's non-exclusive one or the publisher's
copyright (F1–F3, F5). Bortkiewicz's 1898 table is public domain but is German typesetting with no
comparison drawn (F4), and Broido and Clauset's CC BY Fig. 4 is not needed: one number carries the point (F6).

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover-distributions-as-generative-stories.png | placed | template cover in the series house layout, built by `_cover.py`: Greenwood and Yule's counts with the Poisson and the negative binomial, the tangerine used once; a template build, not an external generator | — | — | cover-distributions-as-generative-stories.png | Bars of 647 women's accident counts on a square-root scale, with a dashed Poisson curve and a tangerine negative binomial curve |
| FIG_01 | assets/fig-01-story-map-distributions-as-generative-stories.png | mermaid | Q3: 11 nodes with a labelled edge each, and two families whose branches cross; the post's one map of every story | — | — | fig-01-story-map-distributions-as-generative-stories.png | Map of generative stories: Bernoulli to binomial to Poisson, gaps to exponential and gamma, effects to normal and lognormal, mixtures |
| FIG_02 | assets/fig-02-two-poisson-tallies-distributions-as-generative-stories.png | chart | Q1: published counts (ledger L04, L12) against expected counts computed by the lab | — | — | fig-02-two-poisson-tallies-distributions-as-generative-stories.png | Hanging rootograms of Clarke's 576 squares and Bortkiewicz's 200 corps-years against the Poisson; every bar ends inside ±1 |
| FIG_03 | assets/fig-03-coal-gaps-distributions-as-generative-stories.png | chart | Q1: a real dated record (ledger L47) with gaps and simulated exponential records measured by the lab | — | — | fig-03-coal-gaps-distributions-as-generative-stories.png | Coal explosions 1851 to 1962: the cumulative count bends near 1890, and pooled gaps run longer than an exponential predicts |
| FIG_04 | assets/fig-04-sums-and-products-distributions-as-generative-stories.png | plot | Q4: simulated distributions from one set of draws, three panels of small multiples | — | — | fig-04-sums-and-products-distributions-as-generative-stories.png | Histograms of the same twelve random effects added, multiplied and logged: symmetric sum, right-skewed product, symmetric log |
| FIG_05 | assets/fig-05-accidents-two-fits-distributions-as-generative-stories.png | chart | Q1: published counts (ledger L16) against two fitted models from the lab | — | — | fig-05-accidents-two-fits-distributions-as-generative-stories.png | Rootograms of Greenwood and Yule's accident counts: the Poisson misses three classes beyond ±1, the negative binomial none |
| FIG_06 | assets/fig-06-gamma-behind-the-fit-distributions-as-generative-stories.png | plot | Q4: a fitted density with a shaded share, beside a stacked variance bar from theory and simulation | — | — | fig-06-gamma-behind-the-fit-distributions-as-generative-stories.png | Gamma density of the women's accident rates with the top 20% shaded, and the variance split into 0.465 Poisson and 0.227 spread |
| FIG_07 | assets/fig-07-t5-against-normal-distributions-as-generative-stories.png | plot | Q4: exact curves, one panel on a log scale, where the comparison lives | — | — | fig-07-t5-against-normal-distributions-as-generative-stories.png | Unit-variance t5 and normal densities differ visibly only at the peak; on a log scale the t5 tail is 4.3, 56 and 2,316 times higher |
| FIG_08 | assets/fig-08-qq-plots-distributions-as-generative-stories.png | plot | Q4: simulated samples against normal quantiles, two panels | — | — | fig-08-qq-plots-distributions-as-generative-stories.png | Q–Q plots of 1,000 normal and 1,000 unit-variance t5 draws against normal quantiles; the t5 points bend away at both ends |
| FIG_09 | assets/fig-09-lognormal-log-log-distributions-as-generative-stories.png | plot | Q4: a simulated CCDF on log-log axes with a least-squares line over a window | — | — | fig-09-lognormal-log-log-distributions-as-generative-stories.png | A lognormal sample's survival curve on log–log axes: the top 10% fits a straight line with R² 0.991 while the full curve bends |
| FIG_10 | assets/fig-10-floor-makes-a-power-law-distributions-as-generative-stories.png | plot | Q4: exact distributions of a stochastic process with and without a barrier, plus a simulated check | — | — | fig-10-floor-makes-a-power-law-distributions-as-generative-stories.png | Champernowne's walk on log–log axes: with a floor the tail is a straight line of slope −1, without one it curves down |

## Lab files

**Lab grade:** G1 · runs anywhere (NumPy 2.5.4 and SciPy 1.18.1; the full run takes about five seconds).

| Placeholder | File | Suggested object key | Purpose |
|---|---|---|---|
| LAB_01 | `lab/README.md` | `labs/distributions-as-generative-stories/README.md` | grade, provenance, setup, run order, the E1–E4 exercises with answers, cleanup |
| LAB_02 | `lab/stories.py` | `labs/distributions-as-generative-stories/stories.py` | the six stages of the lab; every probability by recurrence, checked against SciPy |
| LAB_03 | `lab/requirements.txt` | `labs/distributions-as-generative-stories/requirements.txt` | the pinned NumPy and SciPy versions |
| LAB_04 | `lab/data/clarke1946_flying_bombs.csv` | `labs/distributions-as-generative-stories/data/clarke1946_flying_bombs.csv` | Clarke's table with its provenance header |
| LAB_05 | `lab/data/bortkiewicz1898_horse_kicks.csv` | `labs/distributions-as-generative-stories/data/bortkiewicz1898_horse_kicks.csv` | the 280 corps-years transcribed from the 1898 scan |
| LAB_06 | `lab/data/greenwood_yule1920_accidents.csv` | `labs/distributions-as-generative-stories/data/greenwood_yule1920_accidents.csv` | Greenwood and Yule's counts as two reproductions print them |
| LAB_07 | `lab/data/coal_disasters_1851_1962.csv` | `labs/distributions-as-generative-stories/data/coal_disasters_1851_1962.csv` | dates of 191 coal-mine explosions, from R's boot package |
| LAB_08 | `lab/captures.json` | `labs/distributions-as-generative-stories/captures.json` | the author's run, machine-readable, with the author's R cross-check; every measured figure reads it |
| LAB_09 | `lab/expected-output.txt` | `labs/distributions-as-generative-stories/expected-output.txt` | the author's run as printed |
| LAB_10 | `lab/notebook.ipynb` | `labs/distributions-as-generative-stories/notebook.ipynb` | the README with a runnable cell under each step and exercise |
| ARCHIVE | `lab-distributions-as-generative-stories.zip` | `lab-distributions-as-generative-stories.zip` (bucket root) | every lab file in one zip, with the `data` folder in place; its final URL is already written in `blog.md` |

Keep the `data/` prefix in the four CSV keys so the zip and the individual files agree. Upload with an
accurate `Content-Type` (`text/markdown`, `text/x-python`, `text/plain`, `text/csv`, `application/json`,
`application/x-ipynb+json`) and, where the upload path supports object metadata,
`Content-Disposition: attachment; filename="<name>"`.

## Series links to add

None. Part 1 is the series root: it names no other part of the series, and later parts appear only as
"later in this series", with no number or title.

## Checks the gate cannot make, and their results

- Every PNG was opened and read after its last render. Fixed on the way: a ±1 label on the x-axis
  (Figures 2, 5), two identical legend swatches for different marks (Figure 3), a label crossing the mean
  line and one colour meaning two things (Figure 6), label plates cutting gaps in curves and a gridline
  (Figure 7), notes printed over notes (Figure 8), ASCII hyphens for minus signs (Figures 4, 9), and Monte
  Carlo noise at the last simulated point (Figure 10, fixed with ten times the walkers in the lab).
- `_overlap.py`: 0 issues on Figures 2–10. Its reports on Figure 1 are the known Mermaid false positive
  (every edge label measured at one origin), and its one report on the cover is the known one for
  consecutive serif title lines; both PNGs were checked by eye.
- `lint_visuals.py`: 0 text overflows. Its ten arrow reports are all on Figure 1's Mermaid edges, which
  it cannot parse; every edge lands on its node in the PNG.
- `_figs.py` asserts every number the article quotes against `captures.json` before it draws.

## Owner actions

- The `data-science` category does not exist in the live database yet; creating it is a production write
  at publish time. blog-forge's category list gained `data-science` with this part (roadmap decision 10).
- Upload the PNGs, the ten lab files and the zip, then fill `urls.txt` and run `fill_urls.py`.
