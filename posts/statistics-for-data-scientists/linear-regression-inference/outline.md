# Outline — linear-regression-inference

Part 13 of *Statistics for Data Scientists*. Private build artifact. Built end to end on 2026-11-28 from the plan's
Part 13 block (the owner's paste with "build" approves the part; no checkpoint stops, as for Parts 1–12).

- **Title:** *Linear Regression by Hand: Every Number in the Summary* (54 characters; the plan's 75-character title is
  over the 60 limit). Keywords in front: linear regression, summary (output).
- **Tier L4 · advanced.** Six distinct things: the table's numbers from the design matrix, the solver's numerical
  accuracy against certified values, the reading of a coefficient (partialling out, omitted variables, interactions and
  centring), collinearity, the two intervals, and which conditions the guarantees need. The smallest honest numerical
  check (Longley, seven parameters) already needs a page.
- **Answers:** what does a regression estimate, where does every number in its output come from, and what may I conclude
  from a coefficient?
- **Corrects:** "Linear regression needs normally distributed variables."
- **Assumes:** Part 8 by title (*Which Statistical Test? The Design Decides, Not the Data*): its sleep t-tests and
  PlantGrowth ANOVA are rebuilt here as regressions. Part 4 by title (*Likelihood: The MLE, Three Tests, and Where χ²
  Fails*): least squares is the Gaussian MLE, which the log-likelihood line uses.
- **Defers:** checking conditions, influence and robust standard errors to a later part of this series; non-normal
  outcomes and grouped data to later parts; causal readings to a later series on causal inference; regularisation and
  prediction to a later series on classical machine learning. No numbers or titles for any of them.
- **Four-point angle:** reconcile (exact rational arithmetic reproduces NIST's 15 digits; every summary number recomputed
  and matched to statsmodels and R), condition (Gauss–Markov conditions; normality only for exactness and prediction
  intervals), measure (slope-interval coverage under six conditions; CI used as a PI; PI tails), read the output
  (statsmodels' and R's summaries line by line, their AIC conventions, default solvers and their failures on Filip).

## Premises checked before drafting (prototype runs, 2026-11-28)

- Exact rational least squares reproduces every certified Longley and Filip coefficient and standard error to all 15
  printed digits. Longley's κ(X)² = 2.3612 × 10^19 equals Wampler's printed 2.361 × 10^19.
- Longley: Householder QR keeps 10.9–13.2 digits, the normal equations 7.2–8.6. Filip: QR 8.55, the normal equations 0,
  Cholesky fails, NumPy's default `lstsq` 0 (rank 10: σ_min/σ_max = 5.66e-16 below 1.82e-14), statsmodels' default 0 with
  a rank warning, R's `lm` drops x^10 (rank 10 of 11). Their residual sums of squares are 28–35% above the minimum.
- The column-scaled condition number predicts the digits; the raw one moves with units. Centring Year lifts the normal
  equations from 7.4 to 10.3 digits; rescaling GNP changes nothing.
- Sleep as regressions: `extra ~ drug` gives Student's t (1.8608, p 0.07919); `+ patient` gives the paired t (4.0621,
  p 0.002833), same coefficient 1.58. PlantGrowth's nested F 4.8461 on 2 and 27.
- Longley's joint tests: no pair of individually non-significant coefficients is jointly significant (GNP and Population
  F 2.61, p 0.13), so the joint-region figure shows the (GNP, Year) trade-off instead of a paradox.
- Coverage: slope interval 94.4–95.5% under skewed predictors and skewed or heavy-tailed errors from n = 5 to 1,000;
  non-constant variance 92% falling to 84%; AR(1) errors with a trend about 59%. PI tails under skewed errors: 0% below,
  5.3–6.4% above.

## Sections and budget (counted words; References add about 1,100)

| Section | Budget | Job | Figures |
|---|---|---|---|
| Insights + Level + Jump to + notice | 300 | the answer: every number from X, the residuals and n − p; QR keeps the certified digits, default solvers fail Filip; a coefficient is a comparison holding the others; normality is the errors' and only for exactness and prediction | |
| Why this matters | 200 | regression tables misread: 2% of 172 papers transparent and correct; 4% tested normality of variables | |
| The problem | 400 | the model and its estimand; the table as an inventory; the three questions; claim corrected | |
| Worked example | 950 | sleep as `extra ~ drug` and `+ patient`: every number by hand; the same 1.58 with SE 0.849 → 0.389; PlantGrowth's factor and nested F | 1 |
| Intuition | 400 | least squares as a projection; residuals orthogonal; n − p as the dimensions left; the shadow analogy and its break | 2 |
| Does it matter how you solve the least squares equations? | 1,050 | NIST's certification; Longley and Filip by QR, normal equations and library defaults; LRE; κ and κ²; scaled κ; Beaton–Rubin–Barone | 3, 4 |
| Where does every number in the summary come from? | 850 | Longley's statsmodels summary line by line; R's; AIC conventions; F against t; the diagnostic block named | 5, 6, 7 |
| What does a coefficient measure? (+ H3 interactions and centring) | 900 | Frisch–Waugh–Lovell on Longley; omitted-variable bias exact in sample; hand-off to causal inference; ToothGrowth interaction with three origins | 8, 9, 11 |
| How much does collinearity cost? | 450 | VIF by hand; SE inflation √VIF; numerical κ against statistical VIF; centring changes one, not the other | 10 |
| Confidence interval or prediction interval? | 400 | VC arm at 1.5 mg; the two formulas; the CI used as a PI covers 6.8% at n = 1,000 | 12 |
| Which conditions carry the weight? | 550 | the correction measured: six conditions × six n; PI tails under skewed errors | 13, 14 |
| The math | 650 | normal equations, QR, H and tr(I − H) = n − p, Var(β̂), t and F, R², intervals, VIF, OVB, the log-likelihood | |
| Implementation | 450 | QR summary in NumPy; library table (defaults, conventions) | |
| Limitations and common mistakes | 400 | normality of variables; normal equations; trusting defaults; no intercept; t of collinear predictors; CI as PI; "holding constant" as causal | |
| Key takeaways | 200 | five claims | |
| Try it yourself | 350 | E1–E3 answerable from the article; the lab carries E4 and E5 | |
| References | ~1,100 | Lab downloads + 29 sources | |

Target about 9,000 counted words (L4: 7,500–10,000).

## Figure plan (14 + cover; every route through the gate in `visual-taxonomy.md`)

| # | Section | One thing it says | Route | Why |
|---|---|---|---|---|
| 1 | Worked example | the same slope, 1.58, with patient-to-patient spread in the residuals (σ̂ 1.90) or removed (0.87) | plot | Q1: the twenty measured values, both fits and their residual SDs |
| 2 | Intuition | ŷ is y's shadow on the column space; the residual is perpendicular; TSS = ESS + RSS with the sleep numbers | placed | Q4: geometry with the worked example's values |
| 3 | Solvers | correct digits per coefficient by method on Longley and Filip; three defaults at zero on Filip | chart | Q1: measured LRE against certified values |
| 4 | Solvers | digits kept against log10 of the column-scaled κ on all eleven StRD datasets, QR near 16 − log κ and the normal equations near 16 − 2 log κ | plot | Q1: measured across datasets with the two reference lines |
| 5 | Summary | how every number is computed from X and y | mermaid | Q3: about 18 nodes and branching paths; hand placement would drop edge labels |
| 6 | Summary | statsmodels' Longley summary with each block mapped to its formula | placed | Q4: the real output annotated |
| 7 | Summary | the joint 95% region for GNP and Year is a thin tilted ellipse: the data fix a combination, not each | plot | Q1: computed ellipse with the individual intervals as its shadows |
| 8 | Coefficient | GNP against employment raw and with the other five partialled out; the slope of the second is the coefficient | plot | Q1: measured residuals |
| 9 | Coefficient | each coefficient with and without Year, the gap equal to Year's coefficient times the auxiliary slope | chart | Q1: computed decomposition |
| 10 | Collinearity | VIF per predictor on a log scale, and κ raw, centred and standardised with the VIFs unchanged | chart | Q1: computed |
| 11 | Interactions | ToothGrowth's six cell means and the fitted lines; the supplement coefficient as the gap at each origin | plot | Q1: measured means and fitted lines |
| 12 | Intervals | the VC arm with the 95% band for the mean and for a new animal; and CI-as-PI coverage against n | plot | Q1: computed bands and simulated coverage |
| 13 | Conditions | slope-interval coverage against n under six conditions, with MCSE bars | plot | Q1: simulated, the correction's evidence |
| 14 | Conditions | prediction-interval misses below and above under normal and skewed errors | plot | Q1: simulated tails |
| cover | — | the summary table's numbers rebuilt | placed | template cover, `_cover.py`, series house layout |

No `source` figure. Wampler's tables (public domain) are text and two of their numbers are quoted; Schmidt and Finan's
Figure 2 and *Regression and Other Stories*' figures have no reuse rights (ledger, Figure candidates).

## Term map

| Term | First section | What | Why here | When it matters |
|---|---|---|---|---|
| design matrix X | The problem | n × p matrix of predictor values with a column of ones | every number is a function of it | always |
| estimand β, estimate β̂ | The problem | the coefficients of the population linear predictor; their least squares estimate | what the table reports | interpreting any coefficient |
| residual, RSS | Worked example | y − ŷ; its sum of squares | σ̂, R², F | always |
| residual degrees of freedom n − p | Worked example | dimensions left after fitting p coefficients | divisor of σ̂² | small n, many predictors |
| dummy (indicator) variable | Worked example | a 0/1 column for a group | the t-test as regression | categorical predictors |
| factor, reference level | Worked example | a categorical predictor coded by k − 1 dummies | ANOVA as regression | any grouping |
| nested models, F test | Worked example | a model and a restriction of it; F compares their RSS | ANOVA, joint tests | dropping several terms |
| projection, hat matrix H | Intuition | the matrix that maps y to ŷ | n − p, leverage later | geometry; leverage |
| normal equations | Solvers | XᵀXβ = Xᵀy | the textbook route | never in floating point for ill-conditioned X |
| QR decomposition (Householder) | Solvers | X = QR, Q orthonormal, R triangular | the stable route | default for least squares |
| condition number κ | Solvers | σ_max/σ_min of X | predicts digits lost | collinear or badly scaled X |
| column-scaled κ | Solvers | κ of X with unit-norm columns | the κ that predicts accuracy | judging a solver |
| log relative error (LRE) | Solvers | −log10 of the relative error | correct digits | software testing |
| certified value | Solvers | NIST's 500-digit result rounded to 15 digits | the test vector | reconciling software |
| pseudoinverse, rank cutoff | Solvers | SVD-based solve that zeroes small singular values | statsmodels and NumPy defaults | near-singular designs |
| standard error σ̂√[(XᵀX)⁻¹]ⱼⱼ | Summary | SD of β̂ⱼ's sampling distribution, estimated | t, p, CI | always |
| R², adjusted R² | Summary | share of TSS explained; penalised for p | fit summary | model comparison (with care) |
| log-likelihood, AIC, BIC | Summary | Gaussian likelihood at the MLE; penalised | model comparison | libraries count parameters differently |
| Omnibus, Jarque–Bera, Durbin–Watson | Summary (named) | residual normality and autocorrelation tests | they sit in the table | a later part; time series |
| conditional association | Coefficient | comparison of units differing in xⱼ only | reading a coefficient | always |
| Frisch–Waugh–Lovell theorem | Coefficient | β̂ⱼ = slope of partialled-out y on partialled-out xⱼ | what "holding fixed" does | collinear predictors |
| omitted-variable bias | Coefficient | β̃ = β̂ + γ̂δ̂ | why coefficients move | causal claims (later series) |
| interaction, centring | Coefficient (H3) | product term; shifting a predictor's origin | main effects move with the origin | any model with interactions |
| variance inflation factor (VIF) | Collinearity | 1/(1 − R²ⱼ) | SE inflation | collinear predictors |
| confidence interval for the mean, prediction interval | Intervals | intervals for x₀ᵀβ and for a new y₀ | different questions | prediction |
| Gauss–Markov conditions | Conditions | linearity, uncorrelated errors with equal variance | what OLS needs | always |

## Series links

- Part 8, *Which Statistical Test? The Design Decides, Not the Data* — the sleep t-tests and PlantGrowth ANOVA (The problem, Worked example).
- Part 4, *Likelihood: The MLE, Three Tests, and Where χ² Fails* — least squares as the Gaussian MLE (Summary, log-likelihood).
- Part 2, *The Sampling Distribution: The CLT and Where n = 30 Fails* — the sleep data's first appearance (Worked example), only if needed.
