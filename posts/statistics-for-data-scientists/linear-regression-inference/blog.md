---
title: "Linear Regression by Hand: Every Number in the Summary"
slug: linear-regression-inference
date: 2026-11-28
updated: 2026-11-28
summary: "Every number in a regression summary, rebuilt from the design matrix: QR keeps NIST's certified digits, library defaults fail, and normality barely matters."
tags: [data-science, statistics, linear-regression, regression-inference, numerical-linear-algebra, multicollinearity, prediction-intervals]
category: data-science
series: statistics-for-data-scientists
series_position: 13
tier: L4
difficulty: advanced
prerequisites: ["the t-test and one-way ANOVA", "maximum likelihood", "matrix algebra and Python with NumPy"]
reading_minutes: 42
cover_image: "COVER"
canonical_url: "https://canery.in/blogs/linear-regression-inference"
---

![Correct digits of the worst coefficient for Longley's and Filip's regressions: QR keeps 10.92 and 8.55, the normal equations 7.38 and none, against NIST's 15 certified digits](COVER)

> [!NOTE]
> **Insights** — Every number in a regression summary comes from three things: the design matrix X, the residuals, and the n − p degrees of freedom left after fitting p coefficients; rebuilt from X, Longley's employment regression matches statsmodels and R to 10⁻¹¹. How you solve matters: Householder QR keeps 10.92 of NIST's 15 certified digits where the textbook normal equations keep 7.38, and on NIST's Filip polynomial the normal equations, NumPy's default `lstsq` and statsmodels' default fit keep none. A coefficient compares units that agree on every other predictor, a comparison collinearity can nearly empty: once the other five are held fixed, Longley's GNP keeps a 42nd of its spread. And regression needs no normally distributed variables: with skewed predictors and skewed or heavy-tailed errors the slope's 95% interval covered 93.4% to 95.4% of the time from n = 5 to 1,000, while unequal variance pulled it to 82.9% and dependent errors to 59.0%.

**Level:** advanced · **You need:** the t-test and one-way ANOVA; maximum likelihood; matrix algebra and Python with NumPy · **Time:** ~42 min

**Jump to:** [worked example](#worked-example) · [solvers and certified digits](#does-it-matter-how-you-solve-the-least-squares-equations) · [the summary, line by line](#where-does-every-number-in-the-summary-come-from) · [what a coefficient means](#what-does-a-coefficient-measure) · [interactions](#interactions-and-centring) · [collinearity](#how-much-does-collinearity-cost) · [two intervals](#confidence-interval-or-prediction-interval) · [which conditions matter](#which-conditions-carry-the-weight) · [math](#the-math) · [mistakes](#limitations-and-common-mistakes)

> [!IMPORTANT]
> Numbers this post calls **computed** or **measured** come from its lab: one script, `regression.py`, which solves every model from the design matrix and matches statsmodels 0.15.0 and R 4.5.2 to between 4 × 10⁻¹⁶ and 1.2 × 10⁻¹¹. Every simulated rate prints with its Monte Carlo standard error (MCSE). Published numbers are **quoted**, with their sources.

## Why this matters

A regression table is the statistical output data scientists read most, and one of the most often misread. A review of all 893 articles published in 2013 by twelve clinical psychology journals found 172 that used linear regression: 92% of them were unclear about which assumptions they had checked, 2% were both transparent and correct, and 4% treated normality of the variables, rather than of the errors, as a requirement. <!-- L31 --> The table's arithmetic deserves the same scrutiny. In 1967 Longley showed that many least squares programs of the day returned inaccurate answers to a small economic regression, <!-- L06 --> and on a harder test case published since, three of today's library defaults return no correct digit at all. This part rebuilds every number in the table, checks the arithmetic against certified values, and measures which of the model's conditions those numbers depend on.

## The problem

The eighth part of this series, *Which Statistical Test? The Design Decides, Not the Data*, compared Student's two sleeping drugs with t-tests and three groups of plants with a one-way analysis of variance. Both are special cases of one model, and some teaching material builds the whole catalogue of common tests that way. <!-- L48 --> The **linear model** writes n responses as

$$
y = X\beta + \varepsilon,
$$

where the **design matrix** X has one row per observation and one column per coefficient: a column of ones for the intercept and one column for each predictor, p columns in all. The vector β is the **estimand**. When the mean of y given the predictors really is linear, β holds the coefficients of that conditional mean; when it is not, least squares still estimates the coefficients of the best linear approximation to it. The **least squares estimate** β̂ minimises the residual sum of squares, Σ(yᵢ − xᵢᵀβ̂)², and the errors ε are what the line leaves over.

Every regression routine then prints a **summary table**: per coefficient an estimate, a standard error, a t statistic, a p-value and a confidence interval; for the whole fit a residual standard deviation, R², an adjusted R², an F statistic, a log-likelihood, AIC and BIC; and, in statsmodels, a block of residual diagnostics. Three questions follow. Where does each of those numbers come from, and does it matter how the software computes them? What may a coefficient be read as? And which conditions do the standard errors, the t and the F need? This part corrects one answer to the last question: **"Linear regression needs normally distributed variables."**

## Worked example

Start with numbers already known. R's sleep data, Student's 1908 example, record the extra hours of sleep ten patients gained on each of two drugs. <!-- L43 --> Put the twenty values in a vector y and code the drug with a **dummy variable**, a column that is 0 for drug 1 and 1 for drug 2. The design matrix has two columns, ones and the dummy, so p = 2:

$$
X^\top X = \begin{bmatrix} 20 & 10 \\ 10 & 10 \end{bmatrix}, \qquad X^\top y = \begin{bmatrix} 30.8 \\ 23.3 \end{bmatrix}.
$$

The first row counts all twenty patients and sums all twenty values; the second counts and sums drug 2's ten. Solving the two equations gives an intercept of 0.75, drug 1's mean, and a coefficient of 1.58 on the dummy, the difference between the two drugs' means. Each **residual** is a value minus its group's mean, and their sum of squares, RSS, is 64.886. Two coefficients were fitted from twenty observations, which leaves n − p = 18 **residual degrees of freedom**, so the residual variance is estimated as σ̂² = 64.886/18 = 3.605: the pooled variance of Student's two-sample t-test. Table 1 builds the rest of the summary from those pieces.

| Number | Value | Where it comes from |
|---|---|---|
| coefficient on drug 2 | 1.58 | difference in means, from solving XᵀX b = Xᵀy |
| intercept | 0.75 | drug 1's mean |
| residual sum of squares | 64.886 | Σ(y − ŷ)² |
| residual degrees of freedom | 18 | n − p = 20 − 2 |
| residual standard error σ̂ | 1.899 | √(64.886/18) |
| standard error of the coefficient | 0.849 | σ̂ × √0.2, where 0.2 is the second diagonal entry of (XᵀX)⁻¹ |
| t | 1.861 | 1.58/0.849 |
| p-value | 0.0792 | twice the upper tail of Student's t with 18 df beyond 1.861 |
| 95% confidence interval | −0.204 to 3.364 | 1.58 ± 2.101 × 0.849 |
| R² | 0.161 | 1 − 64.886/77.368, against the total sum of squares about the mean |
| F | 3.463 on 1 and 18 df | t², since one coefficient is tested |

*Table 1. The summary of the regression of extra sleep on a drug dummy, built by hand. Every number is Student's two-sample t-test.*

The diagonal entry 0.2 of (XᵀX)⁻¹ is 1/10 + 1/10, so the standard error σ̂√0.2 is Student's pooled standard error, and t = 1.861 with p = 0.0792 is the unpaired test of the eighth part to the last digit. The regression did not approximate the t-test; it is the t-test.

The design says something the dummy ignores: every patient took both drugs. Add nine more dummy columns, one per patient after the first, and the model compares the drugs within patients. A paired or blocked design can always be analysed this way, with indicators for the pairs. <!-- L38 --> The coefficient on drug 2 stays 1.58, because each patient contributes to both drugs equally and the patient columns carry no information about the drug. Its standard error falls from 0.849 to 0.389, because the patient-to-patient differences that inflated the residuals are now fitted: σ̂ drops from 1.899 to 0.870 and R² rises from 0.161 to 0.912. With 20 − 11 = 9 residual degrees of freedom, t = 4.062 and p = 0.002833: the paired t-test.

![Left: the sleep data by drug with the fitted difference of 1.58 and a residual SD of 1.90 on 18 df. Right: each value minus its patient's mean, with the same slope of 1.58 and a residual SD of 0.87 on 9 df](FIG_01)
*Figure 1. One coefficient, two standard errors. The patient columns change what is left in the residuals, not what the coefficient estimates: the faint lines join each patient's two values, and once the model fits them the spread around the fitted difference falls by more than half.*

A factor works the same way. PlantGrowth, Dobson's 30 plants under a control and two treatments, <!-- L44 --> needs two dummies once the control group is chosen as the **reference level**: the intercept, 5.032, is the control mean, and the two coefficients, −0.371 and 0.494, are the treatment means minus it. One-way analysis of variance asks whether those two coefficients are both zero, and the answer is a comparison of two **nested models**, the full one and the intercept-only one inside it. The intercept-only model leaves 14.258 on 29 degrees of freedom; the factor leaves 10.492 on 27. The F statistic divides the improvement per coefficient spent by the full model's residual variance: [(14.258 − 10.492)/2]/(10.492/27) = 4.846 on 2 and 27 degrees of freedom, p = 0.0159, the eighth part's ANOVA F.

## Intuition

Least squares is a projection. The fitted vector ŷ = Xβ̂ is the point closest to y among all vectors of the form Xb, which together make up the **column space** of X, a flat p-dimensional subspace of the n-dimensional space y lives in. The closest point is the foot of the perpendicular, so the residual vector is at right angles to every column of X: Xᵀ(y − Xβ̂) = 0, which is exactly the system the worked example solved. Figure 2 draws it for the sleep regression with both vectors measured from the mean.

![The sleep regression as a projection: the data vector minus its mean, with squared length 77.37, its projection onto the column space, with squared length 12.48, and the perpendicular residual, with squared length 64.89](FIG_02)
*Figure 2. The fit is the data's shadow on the column space and the residual is perpendicular to it, so the squared lengths add: 77.37 = 12.48 + 64.89, and R² = 12.48/77.37.*

Two summary numbers fall out of the picture. Because the three vectors form a right triangle, the total sum of squares splits into an explained part and a residual part, and R² is the explained share. And because the residual must be perpendicular to all p columns, it has only n − p directions left to vary in; each fitted coefficient removes one. The average squared residual per available direction, RSS/(n − p), is therefore the unbiased estimate of σ², and dividing by n would underestimate it by the factor (n − p)/n, 18/20 here.

The shadow analogy breaks at the coordinates. The shadow itself, the fitted vector, is well defined however the columns of X point. Its coordinates, the coefficients, are not: when two columns point in nearly the same direction, many different combinations of them cast nearly the same shadow, and the data cannot say which one is right. That instability returns twice below, once in the arithmetic and once in the standard errors.

## Does it matter how you solve the least squares equations?

The textbook route forms XᵀX and solves the **normal equations** XᵀXβ̂ = Xᵀy. The route numerical analysts use factors X itself as X = QR, with Q's columns orthonormal and R upper triangular, and solves Rβ̂ = Qᵀy by back substitution; the factorisation is built from Householder reflections. In exact arithmetic the two give the same answer. In double precision, which carries about 16 significant digits, they do not, because forming XᵀX squares the **condition number** κ(X), the ratio of X's largest to smallest **singular value**, the factors by which X stretches vectors along its principal directions. The condition number bounds how much relative errors in the data or the arithmetic can be amplified in the solution, and κ(XᵀX) = κ(X)². Golub and Wilkinson pointed this out in the 1960s, with the advice to work with X rather than XᵀX. <!-- L10 --> Householder QR for least squares had been described by Golub in 1965. <!-- L11 -->

To test a solver you need answers known to more digits than the solver carries. NIST's Statistical Reference Datasets, online since 1999, supply them for linear regression, analysis of variance, nonlinear regression and univariate statistics. <!-- L01 --> The certified values were computed in multiple precision accurate to 500 digits, with the data read in exactly, and rounded to 15 significant digits only at output. <!-- L02 --> Longley's data are the classic case: total employment in the United States for the 16 years 1947 to 1962, against six predictors, the GNP implicit price deflator, GNP, unemployment, the size of the armed forces, the non-institutional population aged 14 and over, and the year. <!-- L05 --> NIST grades them as of higher difficulty because the predictors are nearly collinear. <!-- L04 --> Longley's 1967 study had found that programs written for desk calculators, run on computers carrying about eight digits, needed the program or the data altered before most of them gave accurate answers. <!-- L06 --> Two years later Wampler ran two fifth-degree polynomial problems through more than twenty programs: those using Householder transformations or Gram–Schmidt orthonormalisation were far more accurate than those solving the normal equations by elimination, and some returned coefficients without a single correct significant digit. <!-- L07 --> On the Univac 1108 in double precision, the Householder program averaged 14.6 correct digits on his first problem and the five elimination programs 9.3 to 9.7. <!-- L52 -->

Wampler counted correct digits as minus the base-10 logarithm of a coefficient's relative error, <!-- L08 --> and McCullough's later methodology for testing statistical software made the same count, the **log relative error** (LRE), the standard summary: <!-- L15 --> LRE = −log₁₀(abs(x − c)/abs(c)) for a computed value x against a certified value c, read as the number of correct significant digits. <!-- L16 --> An LRE of 10 means ten digits agree; below 1, none do.

Before scoring any solver, the lab checks the certificate itself. Least squares on data given as decimals has an exact rational solution, and Python's `fractions` module computes it without rounding: for all eleven of NIST's linear datasets, every certified coefficient, standard error and residual standard deviation, 121 values in all, reproduces to all 15 printed digits. Longley's design has κ(X) = 4.86 × 10⁹, so κ(XᵀX) = 2.361 × 10¹⁹, the figure Wampler printed for Longley's XᵀX in 1969. <!-- L09 --> Figure 3 scores ten floating-point solvers against the certified coefficients.

![Correct significant digits of every coefficient against NIST's certified values, by solver, for Longley's 7 coefficients and Filip's 11: QR and SVD solvers keep about 11 digits on Longley and up to 8.55 on Filip; the normal equations keep 7.38 on Longley and none on Filip; NumPy's and statsmodels' defaults keep none on Filip, and R's lm drops x to the tenth](FIG_03)
*Figure 3. On Longley every orthogonal solver keeps about 11 digits of its worst coefficient and the normal equations about 7.4; on Filip the normal equations, two library defaults and R's default fit keep none. Each dot is one coefficient.*

On Longley, Householder QR keeps 10.92 digits of its worst coefficient and the normal equations 7.38 (7.24 by Cholesky, 7.41 through an explicit inverse): three and a half digits lost to squaring. The SVD and complete-orthogonal solvers keep 10.93 to 11.08, statsmodels' default 10.99, and R's `lm` 12.94. The raw condition number overstates the damage: log₁₀ 4.86 × 10⁹ is 9.7, yet QR lost about five digits, not ten. The column scales explain it. The year runs near 1,950, the deflator near 100 and GNP near 400,000, and rescaling one column changes the raw κ without changing what the solvers can recover: with GNP in thousands the raw κ falls to 1.38 × 10⁹ and the normal equations still keep 7.43 digits. The condition number that predicts accuracy is that of X with its columns scaled to unit length, 4.33 × 10⁴ for Longley. Figure 4 tests the rule on all eleven datasets.

![Fewest correct digits over the coefficients against the condition number of the column-scaled design for NIST's eleven linear datasets: QR points lie near the line 15.65 minus log kappa, normal-equation points near 15.65 minus 2 log kappa, and Wampler 1 to 5 share one design but lose digits as their residuals grow](FIG_04)
*Figure 4. QR loses about log₁₀ κ digits and the normal equations about twice that, with κ taken after scaling the columns. Wampler 1 to 5 share one design matrix; the larger their residuals, the more digits QR loses.*

The points follow two lines, 15.65 − log₁₀ κ for QR and 15.65 − 2 log₁₀ κ for the normal equations, where 15.65 is the number of digits double precision represents. The exceptions are informative. LAPACK's error bound for QR and SVD solvers has two terms, one proportional to κ and one to κ² times tan θ, where sin θ is the residual's length over the response's. <!-- L12 --> When the fit is poor the second term dominates even for QR. Wampler 1 to 5 share one design matrix and differ only in the noise added to y; <!-- L47 --> on Wampler 5, whose residual vector is 17.6 times as long as its fitted vector (tan θ = 17.6), QR keeps 5.68 digits and the normal equations, for once, 6.25.

Filip is where the textbook route fails outright. It is an observed dataset of 82 points fitted by a tenth-degree polynomial in one predictor, <!-- L46 --> with κ(X) = 1.77 × 10¹⁵ and κ(XᵀX) = 3.1 × 10³⁰, far past the 4.5 × 10¹⁵ that double precision can resolve. QR keeps 8.55 digits. The normal equations keep none: Cholesky refuses XᵀX as not positive definite, LU returns coefficients with a residual sum of squares 1.33 times the minimum, and the explicit inverse one 16,269 times it. Three library defaults fail too:

- **NumPy's `lstsq`** treats singular values below its cutoff as zero, and since NumPy 2.0 the cutoff defaults to machine precision times max(n, p), <!-- L29 --> 1.8 × 10⁻¹⁴ here. Filip's smallest singular value is 5.7 × 10⁻¹⁶ of its largest, so `lstsq` solves a rank-10 problem and returns a **minimum-norm answer**, the shortest coefficient vector among the many that fit equally well once one direction is discarded: no correct digit, and a residual sum of squares 34.6% above the minimum. Passing `rcond=-1`, machine precision, keeps the column and recovers 5.41 digits.
- **statsmodels' `OLS(y, X).fit()`** solves with the Moore–Penrose **pseudoinverse** by default, <!-- L22 --> a solution built from the singular value decomposition, and zeroes singular values below 10⁻¹⁵ of the largest; <!-- L23 --> it returns the same answer as NumPy, with a warning that the design is rank-deficient. `fit(method="qr")` keeps 8.55 digits.
- **R's `lm`** factors X by a modified LINPACK QR with tolerance 10⁻⁷ and moves columns it judges dependent to the end, reporting them as NA. <!-- L27 --> It drops x¹⁰ and fits a ninth-degree polynomial whose ten coefficients have no correct digit. The dropped term is not negligible: without it the residual sum of squares is 28.4% higher, F = 20.2 on 1 and 71 degrees of freedom, p = 2.7 × 10⁻⁵. With `tol = 1e-10`, `lm` keeps 8.42 digits.

SciPy's `lstsq` uses LAPACK's `gelsd`, a divide-and-conquer SVD driver, by default, <!-- L13 --> with a cutoff at machine precision, <!-- L30 --> and keeps 6.06 digits; its `gelsy` driver, a complete orthogonal factorisation, keeps 7.80. None of this is new. In a 2010 comparison of spreadsheets, only Excel 2007 returned results for Filip, with about seven correct digits; <!-- L21 --> in 2019 NIST's tests found reliable linear regression routines in only two of seven data mining packages; <!-- L19 --> and a 2024 comparison of R and Python libraries on NIST's data recommended R's stats package for linear regression. <!-- L20 --> McCullough and Vinod's survey put the conclusion plainly: users cannot assume their software is accurate. <!-- L18 -->

What do fifteen certified digits mean? Not fifteen digits about the economy. Beaton, Rubin and Barone argued in 1976 that the numerically exact Longley solution was probably not a reasonable estimate, because the accuracy of the data moves the answer more than the arithmetic does. <!-- L14 --> The lab measures their point: perturbing every value of Longley's predictors within half a unit of its last printed digit, 20,000 times, moves the deflator's coefficient by 14% of itself (0.9 stable digits) and the year's by 0.13% (2.9 digits), yet by only 0.5% to 2.4% of each coefficient's standard error. NIST says as much: its digits are for comparing software, not a measure of statistical significance. <!-- L03 --> The certified values test the arithmetic, and sampling error, not rounding, limits what the coefficients say.

## Where does every number in the summary come from?

Figure 5 traces every number in a summary to the design matrix and the response, with Longley's values on each node.

![Flow from the design matrix and response through the QR factorisation, coefficients, residuals and sums of squares to s squared, standard errors, t, R squared, F, the log-likelihood with AIC and BIC, the residual diagnostics and the condition number, each with Longley's value](FIG_05)
*Figure 5. Four paths leave the residuals: the variance estimate and everything scaled by it, the two sums of squares behind R² and F, the likelihood behind AIC and BIC, and the diagnostic statistics.*

statsmodels prints Longley's regression as Figure 6 shows. The lab recomputes every number in it from the design matrix, and the 39 it compares with statsmodels' own attributes, the coefficients, standard errors, t and p values and the fit and diagnostic statistics, agree to 5.6 × 10⁻¹².

![statsmodels' summary of Longley's regression with each block mapped to its formula: R squared, adjusted R squared, F, the log-likelihood, AIC and BIC; the coefficient table; and the residual diagnostics and condition number](FIG_06)
*Figure 6. The summary decoded. Orange marks the two places where statsmodels and R count differently; grey marks what this table reports but a later part, or another series, reads.*

Reading it top to bottom:

- **coef** solves Rβ̂ = Qᵀy, and **std err** is σ̂ times the square root of the diagonal of (XᵀX)⁻¹ = R⁻¹R⁻ᵀ, so XᵀX is never formed. Here σ̂ = 304.854 on 16 − 7 = 9 degrees of freedom.
- **t** is the coefficient over its standard error, **P>|t|** twice the tail of Student's t with 9 degrees of freedom, and the interval is the coefficient ± 2.262 standard errors, 2.262 being that t distribution's 97.5% point. These are exact when the errors are normal; the conditions section measures what they become when they are not.
- **R-squared** is 1 − RSS/TSS = 1 − 836,424/185,008,826 = 0.995479, and **Adj. R-squared** replaces the two sums of squares by their mean squares, 1 − (1 − R²)(n − 1)/(n − p) = 0.992465, which falls when a predictor adds less than its share.
- **F-statistic** is the nested-model F against the intercept-only model, [(TSS − RSS)/6]/σ̂² = 330.29 on 6 and 9 degrees of freedom, p = 4.98 × 10⁻¹⁰: PlantGrowth's calculation with six coefficients tested instead of two.
- **Log-Likelihood** is the Gaussian log-likelihood at its maximum, −(n/2)[log(2π · RSS/n) + 1] = −109.62. Least squares is the Gaussian maximum likelihood estimate, as the fourth part of this series, *Likelihood: The MLE, Three Tests, and Where χ² Fails*, showed, and the variance's MLE divides by n, not n − p.
- **AIC** and **BIC** penalise that log-likelihood by the number of parameters k, as −2ℓ + 2k and −2ℓ + k log n. statsmodels counts the seven coefficients and prints 233.2 and 238.6; R's `logLik` also counts σ, so R prints 235.2 and 241.4. <!-- L24 --> The difference cancels when two models are compared in the same software and misleads when they are not.
- **Omnibus**, **Prob(Omnibus)**, **Skew**, **Kurtosis**, **Jarque-Bera** and **Prob(JB)** test the residuals for normality: Omnibus is SciPy's D'Agostino–Pearson test, Jarque–Bera combines the sample skewness and kurtosis. <!-- L26 --> **Durbin-Watson**, Σ(eₜ − eₜ₋₁)²/Σeₜ², tests for correlation between successive residuals, which matters here because Longley's rows are consecutive years. A later part of this series reads the normality tests; serial correlation belongs to a later series on time series.
- **Cond. No.** is σ_max/σ_min of the unscaled X, 4.86 × 10⁹, and statsmodels adds a note whenever it exceeds 1,000. <!-- L25 --> It is a statement about the arithmetic in the units supplied, not about the data's information.

R prints the same numbers in its own layout, and the lab matches its coefficients, standard errors and fit statistics, AIC and BIC included, to 1.2 × 10⁻¹¹. R divides the residual sum of squares by the residual degrees of freedom, adjusts R² by (n − 1)/(n − p) and forms F from the model mean square over that variance, <!-- L28 --> exactly as above:

```text
Coefficients:
              Estimate Std. Error t value Pr(>|t|)
(Intercept) -3.482e+06  8.904e+05  -3.911 0.003560 **
Deflator     1.506e+01  8.491e+01   0.177 0.863141
GNP         -3.582e-02  3.349e-02  -1.070 0.312681
Unemployed  -2.020e+00  4.884e-01  -4.136 0.002535 **
Armed       -1.033e+00  2.143e-01  -4.822 0.000944 ***
Population  -5.110e-02  2.261e-01  -0.226 0.826212
Year         1.829e+03  4.555e+02   4.016 0.003037 **

Residual standard error: 304.9 on 9 degrees of freedom
Multiple R-squared:  0.9955,	Adjusted R-squared:  0.9925
F-statistic: 330.3 on 6 and 9 DF,  p-value: 4.984e-10
```

The F statistic and the t statistics answer different questions. Each t asks whether one predictor adds anything given the other five; the F asks whether the six together add anything, and together they explain 99.5% of the variation while three of the six t statistics are below 1.1 in absolute value. Figure 7 shows how one coefficient's interval can understate what the data determine.

![The joint 95% confidence region for Longley's GNP and Year coefficients, a thin ellipse tilted downward, with each coefficient's own 95% interval drawn as its shadow on the axes, and the residual-sum-of-squares contour touching the line Year equals zero at GNP plus 0.0720](FIG_07)
*Figure 7. The two estimates correlate −0.80, so the joint region is a tilted ellipse and each interval is only its shadow. Forcing Year's coefficient to zero slides GNP's along the tilt to +0.0720.*

The data pin down a combination of the two coefficients far better than either alone, because GNP and the year rose together: their correlation is 0.995. Tested jointly, the pair gives F = 14.53 on 2 and 9 degrees of freedom (p = 0.0015). The same tilt is why "not significant" on one line is weak evidence of no association. Here the three individually non-significant predictors, the deflator, GNP and population, are jointly non-significant too (F = 1.75, p = 0.23), but only the joint test answers the question about all three.

## What does a coefficient measure?

The careful reading of a coefficient is a comparison: between units that differ by one in that predictor and agree on all the others, the fitted responses differ by the coefficient on average. Reading it instead as the change caused within one unit by changing that predictor is a causal claim that needs assumptions the regression does not supply. <!-- L37 --> Box made the same point in 1966 about regressions on unplanned data, whose error term stands in for every variable left out. <!-- L40 -->

What "holding the others fixed" means in practice has an exact answer, the result Frisch and Waugh proved in 1933 and Lovell extended in 1963, now called the **Frisch–Waugh–Lovell theorem**. <!-- L41 --> Regress y on all the other predictors and keep the residuals; regress the predictor of interest on the same others and keep its residuals; the slope of the first set on the second is that predictor's multiple-regression coefficient, and the standard error follows from the same residuals. Figure 8 does it for Longley's GNP.

![Left: Longley's employment against GNP as recorded, rising with a simple-regression slope of 0.0348. Right: both with the other five predictors partialled out, with slope minus 0.0358, GNP's coefficient, and GNP's remaining spread a 42nd of the original](FIG_08)
*Figure 8. Alone, employment rises with GNP. With the other predictors partialled out, the slope is GNP's coefficient, −0.0358, estimated from the sliver of GNP's variation that the deflator, unemployment, armed forces, population and year do not already explain.*

On its own, GNP has a slope of +0.0348. Partialled out, the slope is −0.0358, and it is estimated from what is left of GNP once the other five predictors and the constant have been fitted: a standard deviation of 2,350 against 99,395 as recorded, 42 times less variation. The coefficient compares years that had unusual GNP for their deflator, unemployment, armed forces, population and date, and there are very few such years.

Leaving a predictor out changes the comparison, and the change has a closed form. The **omitted-variable bias** formula is an identity in the sample: each coefficient of the short regression equals its coefficient in the long regression plus the omitted variable's coefficient times the predictor's slope when the omitted variable is regressed on the included ones. Leave Year out of Longley's model and GNP's coefficient moves from −0.0358 to +0.0720 = −0.0358 + 1,829.15 × 0.0000589; the lab checks the identity to 10⁻¹². Every other coefficient moves too (Figure 9), while R² barely changes, from 0.9955 to 0.9874.

![Each of Longley's coefficients with Year in the model and with Year left out, in units of its standard error: GNP moves from minus 1.1 to plus 2.1, unemployment from minus 4.1 to minus 0.8, armed forces from minus 4.8 to minus 2.6, population from minus 0.2 to minus 1.8 and the deflator from plus 0.2 to minus 0.6](FIG_09)
*Figure 9. Leaving Year out moves every coefficient, each by Year's coefficient times that predictor's slope in the regression of Year on the rest. A model that fits almost as well can tell a different story about every predictor.*

Which coefficients deserve a causal reading is a question of identification, the subject of a later series on causal inference; this formula is where it starts, and Cinelli and Hazlett extend it into a sensitivity analysis for confounders nobody measured. <!-- L42 -->

### How much does collinearity cost?

The partialled-out spread in Figure 8 is the whole story of **collinearity**. Regress predictor j on the other predictors and call that regression's R² the predictor's R²ⱼ. Its **variance inflation factor** (VIF) is 1/(1 − R²ⱼ), and the variance of its coefficient is σ² × VIFⱼ divided by the predictor's sum of squares about its mean: compared with a design in which predictor j is uncorrelated with the rest, its standard error is √VIFⱼ times larger. For Longley's GNP, R²ⱼ = 0.999441 and the VIF is 1,788.5, so the standard error is 42.3 times what an orthogonal design would give, the factor Figure 8 showed as lost spread.

![Left: variance inflation factors of Longley's six predictors on a log scale, from 3.6 for the armed forces to 1,788.5 for GNP. Right: the condition number of the design matrix as recorded, centred and standardised, falling from 4.859 times 10 to the 9 to 110.5 while the VIFs stay identical](FIG_10)
*Figure 10. Five of Longley's six predictors have a VIF above 30. Centring and scaling cut the condition number by a factor of 44 million and leave every VIF unchanged.*

Figure 10 separates two problems that share the word. The condition number is numerical: centring the predictors cuts it from 4.86 × 10⁹ to 5.77 × 10⁵ and standardising them to 110.5, which is why NIST suggests centring when software fails a high-difficulty dataset. <!-- L04 --> The VIFs are statistical: they are identical in all three versions, because centring and scaling re-express the same information. No reparameterisation of the same columns buys precision back; only data in which the predictors move apart, or a question that needs only their combination, does. Collinearity does not bias the coefficients, and predictions inside the range of the data stay precise, since the shadow of the projection picture does not move. Conventional VIF cutoffs, such as 10, are rules of thumb rather than tests: the standard error, which already contains the VIF, is the number to read.

### Interactions and centring

An **interaction** is a product of two predictors, and it lets one predictor's slope depend on the other's value. ToothGrowth records the length of odontoblasts, the cells that grow teeth, in 60 guinea pigs given vitamin C at 0.5, 1 or 2 mg a day, either as orange juice (OJ) or as ascorbic acid (VC). <!-- L45 --> The six cell means are 13.23, 22.70 and 26.06 for OJ and 7.98, 16.77 and 26.14 for VC, so OJ's advantage of 5.25 and 5.93 at the two lower doses vanishes at 2 mg. Fit length on an OJ dummy, the number of doublings of dose, and their product. With doublings counted from 1 mg, the VC line rises 9.08 per doubling, the interaction is −2.665 (SE 1.176): OJ's line rises 2.665 less per doubling. The OJ coefficient is 3.70 (SE 0.96, p = 0.0003). Figure 11 shows what that 3.70 is.

![ToothGrowth's six cell means with 95% intervals and the two fitted lines against dose; the OJ coefficient is drawn as the gap between the lines at each choice of origin: 6.37 at 0.5 mg, 3.70 at 1 mg and 1.04 at 2 mg](FIG_11)
*Figure 11. The OJ coefficient is the gap between the two lines where the other predictor equals zero. Moving the origin moves the gap it reports; the interaction, the change in the gap per doubling, stays −2.665.*

It is the gap between the lines where doublings equals zero. Count doublings from 0.5 mg instead and the same fit reports an OJ coefficient of 6.365 (SE 1.519); count from 2 mg and it reports 1.035 (SE 1.519, p = 0.50). The fitted lines, the interaction and R² are identical in all three. A main effect in a model with an interaction is a comparison at one value of the other predictor, and **centring**, placing that predictor's origin at its mean, makes it the comparison at the average, which is usually the one wanted. <!-- L39 --> Here the doses are balanced on the doubling scale, so 1 mg is the mean. The straight lines are an approximation: against the six cell means they leave a lack-of-fit F of 2.38 on 2 and 54 degrees of freedom (p = 0.10), and with dose as a three-level factor the interaction is F = 4.11 on 2 and 54 (p = 0.022).

## Confidence interval or prediction interval?

A fitted regression answers two different questions about a new point x₀. The **confidence interval for the mean response** covers the average of y at x₀; the **prediction interval** covers one new observation there. Take ToothGrowth's VC arm alone, where length rises in a straight line with doublings of dose: length = 16.96 + 9.08 × doublings from 1 mg, σ̂ = 3.446 on 28 degrees of freedom. At 1.5 mg, a dose no animal received, the fitted mean is 22.27. Its **leverage** h₀ = x₀ᵀ(XᵀX)⁻¹x₀, which measures how far x₀ sits from the centre of the design, is 0.0504. The confidence interval for the mean is 22.27 ± 2.048 × 3.446 × √0.0504, 20.69 to 23.86; the prediction interval for one new animal adds the new animal's own error, ± 2.048 × 3.446 × √1.0504, 15.04 to 29.51, 4.56 times wider.

![The VC arm's 30 animals with the fitted line, a narrow band for the mean and a wide band for one new animal, marked at 1.5 mg; and the coverage of each interval against arm size, with the confidence interval used as a prediction interval falling from 71.8% at 6 animals to 7.8% at 600](FIG_12)
*Figure 12. As the arm grows, the interval for the mean shrinks toward the line and the prediction interval toward ± 1.96σ. Used as a prediction interval, the confidence interval covers fewer new animals the more data it rests on.*

The lab simulates 20,000 studies from the fitted VC model at each of six arm sizes. Both intervals cover what they claim, 94.9% to 95.4% of the time. The confidence interval used as a prediction interval, the mistake the two names invite, covers a new animal 71.8% of the time with 6 animals, 34.1% with the actual 30, and 7.8% with 600, because its width goes to zero while each animal's own variation does not.

## Which conditions carry the weight?

The conditions behind the table come in two layers. If the mean of y is linear in the predictors and the errors are uncorrelated with equal variance and mean zero, least squares is unbiased and has the smallest variance among linear unbiased estimators: the Gauss–Markov property, which needs no normality. <!-- L40 --> If the errors are also normal, the t and F statistics have exactly their t and F distributions at every sample size. Without normality the central limit theorem takes over: the t-test and linear regression are valid in large samples for any error distribution, and the belief that they need normally distributed outcomes is widespread and wrong. <!-- L33 --> Nothing in either layer mentions the distribution of the predictors, or the marginal distribution of y: the model conditions on X, and y is not supposed to be normal, only its errors.

The lab measures the guarantee directly. It simulates y = 1 + 2x + error 20,000 times for each condition and each sample size from 5 to 1,000, fits the line, and counts how often the slope's nominal 95% interval contains 2; the Monte Carlo standard error of a coverage near 95% is 0.15 points.

![Coverage of the slope's nominal 95% interval against sample size under six conditions: normal, skewed predictor and heavy-tailed errors stay between 94.7% and 95.3%; skewed errors with a skewed predictor rise from 93.4% at n = 5 to 95.4%; SD rising with x falls from 92.5% to 82.9%; AR(1) errors fall from 81.8% to 59.0%](FIG_13)
*Figure 13. Every condition on distributions keeps the interval near 95%, even at n = 5. Unequal variance and dependence break it, and more data make the break worse, not better.*

With normal errors coverage is 94.9% to 95.1% at every n, as the exact theory says. A skewed predictor (lognormal x, which makes y skewed too) gives 94.7% to 95.3%: the variables' distributions do not enter. Heavy-tailed errors, Student's t with 3 degrees of freedom, give 94.9% to 95.2%. The hardest distributional case, strongly skewed errors together with a skewed predictor, gives 93.4% at n = 5, 94.7% at 50 and 95.4% at 1,000, but its two-sided coverage hides lopsided tails: the interval misses above 5.3% of the time and below 1.3% at n = 5, and still 3.7% and 1.0% at n = 1,000. The other two conditions are a different kind of failure. When the error SD rises with x, coverage falls from 92.5% at n = 5 to 82.9% at n = 1,000: the classical standard error estimates the wrong quantity, and more data estimate it more precisely. With autocorrelated errors along a trend, coverage falls from 81.8% to 59.0%.

The literature agrees. Normality violations made no noticeable difference in simulations beyond about 10 observations per variable, while the form of the model, extreme observations, constant variance and independence mattered at every sample size; <!-- L34 --> Gaussian models kept reliable p-values across a wide range of non-normal data, except with influential outliers at strict levels. <!-- L35 --> Gelman, Hill and Vehtari rank the assumptions in decreasing order of importance as validity, representativeness, additivity and linearity, independence, equal variance and, last, normality of errors, which barely matters for the line and matters for predicting individual points. <!-- L36 -->

That last clause is where normality does matter at any n. A prediction interval is about one new error, and no averaging rescues its tails. Figure 14 counts a 95% prediction interval's misses.

![Share of new observations falling below and above a 95% prediction interval at n = 10, 30, 100 and 1,000: about 2.5% each with normal errors; with centred exponential errors about 0.3% below and 6.0% above at n = 10 and none below and 5.4% above at n = 1,000](FIG_14)
*Figure 14. With skewed errors the prediction interval's total coverage stays near 95% while both tails are wrong, and no sample size fixes it: the large-n limit is 5.18% above and nothing below.*

With normal errors each tail misses 2.5%. With centred exponential errors the interval misses 0.34% below and 6.04% above at n = 10, and 0.00% below and 5.41% above at n = 1,000; the limit is the exponential's own tail, e^(−2.96) = 5.18% above and nothing below. A one-sided bound built from it would be wrong at every sample size.

So the claim this part set out to correct fails on each count. Regression does not need normally distributed variables; that idea mistakes the outcome's distribution for the errors' and has been corrected in print before. <!-- L32 --> Normal errors make the small-sample t and F exact, and their absence cost the slope's interval at most 1.6 points of coverage here, even at n = 5. They matter at every sample size for prediction intervals. And the conditions that carry the weight are the ones normality tests never check: a linear mean, independent errors and constant variance. Repairing inference when the variance is not constant is the subject of a later part of this series; dependent errors belong to a later series on time series.

## The math

| Symbol | Meaning |
|---|---|
| X | n × p design matrix, including the column of ones |
| β, β̂ | the coefficients and their least squares estimate |
| e = y − Xβ̂ | residuals; RSS = eᵀe |
| σ², σ̂² | the error variance and its estimate RSS/(n − p) |
| Q, R | X = QR, Q n × p with orthonormal columns, R p × p upper triangular |
| H = X(XᵀX)⁻¹Xᵀ | the hat matrix, which maps y to ŷ; hᵢ = Hᵢᵢ is the leverage |
| κ(X) | σ_max/σ_min, the condition number |

**Solving.** The least squares estimate solves the normal equations, and the QR factorisation reduces them to a triangular system:

$$
X^\top X\,\hat\beta = X^\top y, \qquad X = QR \;\Rightarrow\; R\,\hat\beta = Q^\top y. \tag{1}
$$

Substituting X = QR into the normal equations gives RᵀRβ̂ = RᵀQᵀy, and R is invertible when X has full column rank. For the sleep data the first form is the 2 × 2 system of the worked example.

**Why squaring hurts.** With the singular value decomposition X = UΣVᵀ,

$$
X^\top X = V\Sigma^2 V^\top \;\Rightarrow\; \kappa(X^\top X) = \kappa(X)^2. \tag{2}
$$

XᵀX has the squared singular values as its eigenvalues, so its condition number is the square of X's: 2.361 × 10¹⁹ for Longley.

**The divisor n − p.** Residuals are e = (I − H)y, and I − H projects onto the n − p dimensions perpendicular to the columns of X. Under the conditions of Gauss–Markov,

$$
\mathrm{E}(e^\top e) = \sigma^2\,\mathrm{tr}(I - H) = \sigma^2 (n - p). \tag{3}
$$

The trace of a projection is its dimension, so RSS/(n − p) is unbiased for σ². This is a sketch: it uses E(ε) = 0 and Var(ε) = σ²I and nothing about normality. For the sleep data, 64.886/18 = 3.605.

**Standard errors, t and F.** Conditional on X,

$$
\begin{aligned}
\mathrm{Var}(\hat\beta) &= \sigma^2 (X^\top X)^{-1},\\
\mathrm{SE}_j &= \hat\sigma\,\sqrt{[(X^\top X)^{-1}]_{jj}}, \qquad t_j = \hat\beta_j / \mathrm{SE}_j.
\end{aligned} \tag{4}
$$

With normal errors tⱼ follows Student's t with n − p degrees of freedom when βⱼ = 0. For q restrictions that turn the full model into a reduced one,

$$
F = \frac{(\mathrm{RSS}_r - \mathrm{RSS}_f)/q}{\mathrm{RSS}_f/(n - p)}, \tag{5}
$$

which follows the F distribution with q and n − p degrees of freedom under normal errors. With q = 1 it equals t²; with the intercept-only model as the reduced one it is the summary's overall F, 330.29 for Longley.

**Fit statistics.** With TSS the sum of squares of y about its mean,

$$
\begin{aligned}
R^2 &= 1 - \frac{\mathrm{RSS}}{\mathrm{TSS}}, \qquad \bar R^2 = 1 - (1 - R^2)\,\frac{n - 1}{n - p},\\
\ell &= -\frac{n}{2}\left[\log\!\left(\frac{2\pi\,\mathrm{RSS}}{n}\right) + 1\right].
\end{aligned} \tag{6}
$$

R² compares the residual sum of squares with the total; the adjusted version compares their mean squares; ℓ is the Gaussian log-likelihood at the MLE, and AIC = −2ℓ + 2k with k = p in statsmodels and p + 1 in R.

**The two intervals.** At a new point x₀ with leverage h₀ = x₀ᵀ(XᵀX)⁻¹x₀,

$$
\begin{aligned}
\text{mean response:}\quad & x_0^\top\hat\beta \pm t_{0.975,\,n-p}\,\hat\sigma\sqrt{h_0},\\
\text{one new observation:}\quad & x_0^\top\hat\beta \pm t_{0.975,\,n-p}\,\hat\sigma\sqrt{1 + h_0}.
\end{aligned} \tag{7}
$$

The 1 under the second root is the new observation's own error variance; h₀ shrinks with n, the 1 never does. For the VC arm at 1.5 mg, √0.0504 against √1.0504.

**Collinearity and omitted variables.** For predictor j with R²ⱼ from its regression on the others,

$$
\mathrm{Var}(\hat\beta_j) = \frac{\sigma^2}{\sum_i (x_{ij} - \bar x_j)^2\,(1 - R_j^2)}, \qquad \tilde\beta_1 = \hat\beta_1 + \hat\beta_2\,\hat\delta. \tag{8}
$$

The first factor, 1/(1 − R²ⱼ), is the VIF. In the second, β̃₁ is a coefficient of the short regression, β̂₁ and β̂₂ are coefficients of the long one, and δ̂ is the slope of the omitted variable on the included ones; for Longley's GNP, −0.0358 + 1,829.15 × 0.0000589 = 0.0720.

## Implementation

The worked example's summary from the design matrix in NumPy, never forming XᵀX:

```python
import numpy as np
from scipy import stats

drug1 = np.array([0.7, -1.6, -0.2, -1.2, -0.1, 3.4, 3.7, 0.8, 0.0, 2.0])   # Student's ten patients, drug 1
drug2 = np.array([1.9, 0.8, 1.1, 0.1, -0.1, 4.4, 5.5, 1.6, 4.6, 3.4])      # the same patients, drug 2
y = np.r_[drug1, drug2]
X = np.column_stack([np.ones(20), np.r_[np.zeros(10), np.ones(10)]])      # intercept, drug-2 dummy

n, p = X.shape
Q, R = np.linalg.qr(X)                         # Householder QR: X'X is never formed
b = np.linalg.solve(R, Q.T @ y)                # R b = Q'y
e = y - X @ b
rss, tss = e @ e, ((y - y.mean()) ** 2).sum()
s2 = rss / (n - p)                             # the n - p divisor
Rinv = np.linalg.inv(R)
se = np.sqrt(s2 * np.diag(Rinv @ Rinv.T))      # (X'X)^-1 = R^-1 R^-T
t = b / se
pval = 2 * stats.t.sf(np.abs(t), n - p)
half = stats.t.ppf(0.975, n - p) * se
r2 = 1 - rss / tss
print("b", b.round(4), "SE", se.round(4), "t", t.round(4), "p", pval.round(5))
print("95% CI", (b - half).round(4), (b + half).round(4))
print("sigma", round(np.sqrt(s2), 4), "R2", round(r2, 4), "adj", round(1 - (1 - r2) * (n - 1) / (n - p), 4),
      "F", round(((tss - rss) / (p - 1)) / s2, 4))
```

It prints coefficients 0.75 and 1.58, standard errors 0.6004 and 0.8491, t values 1.2492 and 1.8608, p-values 0.2276 and 0.07919, intervals −0.5114 to 2.0114 and −0.2039 to 3.3639, σ̂ 1.8986, R² 0.1613, adjusted R² 0.1147 and F 3.4626: Table 1. The lab's `regression.py` does the same for Longley and Filip, solves NIST's datasets exactly, and runs every measurement in this post; see [Lab downloads](#lab-downloads).

### Reading the library's output

The libraries agree on the formulas and differ in their defaults.

| Task | statsmodels 0.15.0 | R 4.5.2 | NumPy 2.5 and SciPy 1.18 | Watch for |
|---|---|---|---|---|
| solving | `OLS(y, X).fit()`: pseudoinverse, cutoff 10⁻¹⁵; `fit(method="qr")` for QR | `lm()`: LINPACK QR, tolerance 10⁻⁷, NA for a dropped column | `np.linalg.lstsq`: SVD, cutoff ε × max(n, p); `scipy.linalg.lstsq`: `gelsd`, cutoff ε | near rank deficiency the defaults truncate or drop silently, or with one warning |
| the intercept | not added: `sm.add_constant(X)` | added by the formula | a column of ones is up to you | without it R² is measured from zero |
| AIC and BIC | k counts the coefficients | k also counts σ | — | differ by 2 and by log n |
| intervals at x₀ | `get_prediction(x0).summary_frame()`: `mean_ci_*` for the mean, `obs_ci_*` for a new observation | `predict(fit, new, interval = "confidence")` or `"prediction"` | — | the prediction interval is for a single observation |

statsmodels leaves the intercept to the user, <!-- L49 --> and its prediction frame labels the two intervals `mean_ci` and `obs_ci`; <!-- L51 --> R's `predict` takes `interval = "confidence"` or `"prediction"`, the second for a single new observation. <!-- L50 -->

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** testing the predictors or the response for normality before a regression. Their distributions do not enter: a skewed predictor kept the slope's interval at 94.7% to 95.3%, and even strongly skewed errors cost at most 1.6 points of coverage at n = 5. Check instead what does matter at every sample size: a linear mean, independent errors and constant variance, which pulled coverage to 59.0% and 82.9% here.

- **Solving the normal equations, or inverting XᵀX, in floating point.** It squares the condition number: 3.5 digits lost on Longley, all of them on Filip. Use a QR or SVD solver, which every library above provides.
- **Trusting a default near rank deficiency.** On Filip, statsmodels' default and NumPy's `lstsq` returned minimum-norm answers with no correct digit, and R's `lm` dropped a term that F = 20.2 says matters. Read the warning and the NA; rescale or centre the predictors, or use orthogonal polynomials, before raising a tolerance.
- **Forgetting the intercept.** With no column of ones, R² is computed against zero instead of the mean and can look nearly perfect while the residuals grow.
- **Reading a non-significant t among collinear predictors as no association.** The t asks about one predictor given the others; test the group jointly, and read the standard error, which already contains the VIF.
- **Reading "holding the others fixed" as an intervention.** A coefficient compares units in the data; on Longley, leaving out one predictor reversed GNP's sign while R² barely moved.
- **Quoting a main effect from a model with an interaction.** It is a comparison at the other predictor's zero; the OJ coefficient was 6.37, 3.70 or 1.04 depending on where dose was counted from.
- **Using a confidence interval as a prediction interval.** It covered 34.1% of new animals at the design's own size, and fewer the more data it rested on.
- **Over-reading certified digits.** Fifteen digits test the arithmetic; Longley's coefficients are stable to between one and three digits under the rounding of the data themselves.

## Key takeaways

- Every number in a regression summary is a function of X, the residuals and n − p. The sleep regression on a dummy is Student's t-test (t = 1.861), adding patient dummies gives the paired t (4.062), and ANOVA's F is the nested-model F (4.846 for PlantGrowth).
- Solve with QR, not the normal equations. On Longley QR kept 10.92 of NIST's 15 certified digits and the normal equations 7.38; on Filip, the normal equations, NumPy's default `lstsq`, statsmodels' default fit and R's default `lm` kept none.
- A coefficient is a comparison between units that agree on the other predictors. Longley's GNP keeps a 42nd of its spread once they are held fixed, and leaving Year out moves its coefficient from −0.0358 to +0.0720.
- Collinearity is two problems: the condition number, which centring fixes, and the VIF (1,788.5 for GNP), which only new information fixes.
- Regression does not need normal variables. The slope's interval covered 93.4% to 95.4% under skewed predictors and skewed or heavy-tailed errors from n = 5 to 1,000; unequal variance (82.9%) and dependent errors (59.0%) are what break it, and prediction intervals need the error's shape at any n.

## Try it yourself

**E1, reproduce.** From XᵀX = [[20, 10], [10, 10]], Xᵀy = [30.8, 23.3] and RSS = 64.886, compute the coefficient on the drug dummy, σ̂, its standard error and t.

<details><summary>Answer</summary>

**Answer.** The inverse of XᵀX is [[0.1, −0.1], [−0.1, 0.2]] (determinant 100), so b = [0.1 × 30.8 − 0.1 × 23.3, −0.1 × 30.8 + 0.2 × 23.3] = [0.75, 1.58]. σ̂ = √(64.886/18) = √3.6048 = 1.8986, the standard error is 1.8986 × √0.2 = 0.8491, and t = 1.58/0.8491 = 1.861, the lab's and Student's value.

</details>

**E2, inspect.** Longley's design has κ(X) = 4.86 × 10⁹ as supplied and 4.33 × 10⁴ with its columns scaled to unit length. Using the rule of Figure 4, how many correct digits should the normal equations keep, and which condition number did you use?

<details><summary>Answer</summary>

**Answer.** The column-scaled one: rescaling a column changes the raw κ but not what a solver recovers. log₁₀ 4.33 × 10⁴ = 4.64, so the normal equations should keep about 15.65 − 2 × 4.64 = 6.4 digits and QR about 11.0. The lab measured 7.38 and 10.92. With the raw κ, 2 × 9.69 exceeds the digits available and would wrongly predict none.

</details>

**E3, predict.** In the ToothGrowth model the OJ coefficient is 3.70 (SE 0.960) with doublings counted from 1 mg, and the interaction is −2.665 (SE 1.176); in this balanced design the two estimates are uncorrelated. Before computing, predict the OJ coefficient and its standard error with the origin at 1.5 mg: larger or smaller than at 1 mg, and by about how much?

<details><summary>Answer</summary>

**Answer.** Moving the origin by c doublings changes the OJ coefficient by c times the interaction: c = log₂ 1.5 = 0.585, so 3.70 − 2.665 × 0.585 = 2.14, the gap between the lines at 1.5 mg. Its variance adds c² times the interaction's: √(0.960² + 0.585² × 1.176²) = √(0.922 + 0.473) = 1.18, larger than at 1 mg because 1.5 mg is farther from the centre of the doses, and smaller than the 1.519 at 0.5 or 2 mg, which the same formula gives with c = ±1.

</details>

The lab's README has these and two more: a diagnostic exercise in which an earlier draft of the summary reports a better R² from a worse fit, and an extension that adds modified Gram–Schmidt, two ways, to the solver harness and scores it on all eleven of NIST's datasets.

## References

### Lab downloads

- [`README.md`](LAB_01) — grade, provenance, setup, run order, the E1–E5 exercises with answers, and cleanup.
- [`regression.py`](LAB_02) — the seven stages: example, nist, summary, meaning, interaction, intervals and conditions; it downloads NIST's files itself and checks their hashes.
- [`crosscheck.R`](LAB_03) — optional: the same models in base R's `lm`, written to `crosscheck-R.csv`.
- [`crosscheck-R.csv`](LAB_04) — the author's R output, which `regression.py` compares against.
- [`student1908_sleep.csv`](LAB_05) — Student's ten patients on two drugs, with provenance; put it in a `data` folder.
- [`plant_growth.csv`](LAB_06) — Dobson's 30 plants under a control and two treatments, with provenance; put it in a `data` folder.
- [`toothgrowth.csv`](LAB_07) — 60 guinea pigs by vitamin C dose and delivery, with provenance; put it in a `data` folder.
- [`requirements.txt`](LAB_08) — the pinned NumPy, SciPy, statsmodels and pandas versions.
- [`captures.json`](LAB_09) — the author's full run, machine-readable.
- [`captures-quick.json`](LAB_10) — the author's `--quick` run, to compare with yours digit for digit.
- [`expected-output.txt`](LAB_11) — the author's full run as printed.
- [`notebook.ipynb`](LAB_12) — the README with a runnable cell under each step and exercise.
- [Complete lab](https://minio.canery.in/media/lab-linear-regression-inference.zip) — every file above in one zip, with the `data` folder in place.

### Sources

1. NIST. *Statistical Reference Datasets*, NIST Standard Reference Database 140 (J. Filliben and A. Possolo): linear least squares background, certification method, FAQ, and the Longley, Filip, Norris, Pontius, NoInt and Wampler data files. https://doi.org/10.18434/T43G6C (accessed 2026-11-28)
2. J. W. Longley. "An appraisal of least squares programs for the electronic computer from the point of view of the user." *Journal of the American Statistical Association* 62(319): 819–841, 1967. https://doi.org/10.1080/01621459.1967.10500896
3. R. H. Wampler. "An evaluation of linear least squares computer programs." *Journal of Research of the National Bureau of Standards B* 73B(2): 59–90, 1969. https://doi.org/10.6028/jres.073b.009
4. R. H. Wampler. "A report on the accuracy of some widely used least squares computer programs." *Journal of the American Statistical Association* 65(330): 549–565, 1970. https://doi.org/10.1080/01621459.1970.10481103
5. A. E. Beaton, D. B. Rubin and J. L. Barone. "The acceptability of regression solutions: another look at computational accuracy." *Journal of the American Statistical Association* 71(353): 158–168, 1976. https://doi.org/10.1080/01621459.1976.10481507
6. B. D. McCullough. "Assessing the reliability of statistical software: Part I." *The American Statistician* 52(4): 358–366, 1998. https://doi.org/10.1080/00031305.1998.10480597
7. B. D. McCullough and H. D. Vinod. "The numerical reliability of econometric software." *Journal of Economic Literature* 37(2): 633–665, 1999. https://doi.org/10.1257/jel.37.2.633
8. M. G. Almiron, B. Lopes, A. L. C. Oliveira, A. C. Medeiros and A. C. Frery. "On the numerical accuracy of spreadsheets." *Journal of Statistical Software* 34(4), 2010. https://doi.org/10.18637/jss.v034.i04
9. B. D. McCullough, T. Mokfi and M. Almaeenejad. "On the accuracy of linear regression routines in some data mining packages." *WIREs Data Mining and Knowledge Discovery* 9(3): e1279, 2019. https://doi.org/10.1002/widm.1279
10. C. Hill, L. Du, M. Johnson and B. D. McCullough. "Comparing programming languages for data analytics: accuracy of estimation in Python and R." *WIREs Data Mining and Knowledge Discovery* 14(3): e1531, 2024. https://doi.org/10.1002/widm.1531
11. E. Anderson et al. *LAPACK Users' Guide*, 3rd edition. SIAM, 1999: sections 2.3.2 and 4.5. https://netlib.org/lapack/lug/node83.html (accessed 2026-11-28)
12. G. H. Golub. "Numerical methods for solving linear least squares problems." *Numerische Mathematik* 7(3): 206–216, 1965. https://doi.org/10.1007/BF01436075
13. G. H. Golub and J. H. Wilkinson. "Note on the iterative refinement of least squares solution." *Numerische Mathematik* 9(2): 139–148, 1966. https://doi.org/10.1007/BF02166032
14. A. F. Ernst and C. J. Albers. "Regression assumptions in clinical psychology research practice — a systematic review of common misconceptions." *PeerJ* 5: e3323, 2017. https://doi.org/10.7717/peerj.3323
15. M. N. Williams, C. A. G. Grajales and D. Kurkiewicz. "Assumptions of multiple regression: correcting two misconceptions." *Practical Assessment, Research & Evaluation* 18(11), 2013. https://doi.org/10.7275/55hn-wk47
16. T. Lumley, P. Diehr, S. Emerson and L. Chen. "The importance of the normality assumption in large public health data sets." *Annual Review of Public Health* 23: 151–169, 2002. https://doi.org/10.1146/annurev.publhealth.23.100901.140546
17. A. F. Schmidt and C. Finan. "Linear regression and the normality assumption." *Journal of Clinical Epidemiology* 98: 146–151, 2018. https://doi.org/10.1016/j.jclinepi.2017.12.006
18. U. Knief and W. Forstmeier. "Violating the normality assumption may be the lesser of two evils." *Behavior Research Methods* 53(6): 2576–2590, 2021. https://doi.org/10.3758/s13428-021-01587-5
19. A. Gelman, J. Hill and A. Vehtari. *Regression and Other Stories*. Cambridge University Press, 2020: sections 10.2, 10.5, 11.1 and 12.2. https://doi.org/10.1017/9781139161879
20. G. E. P. Box. "Use and abuse of regression." *Technometrics* 8(4): 625–629, 1966. https://doi.org/10.2307/1266635
21. R. Frisch and F. V. Waugh. "Partial time regressions as compared with individual trends." *Econometrica* 1(4): 387–401, 1933. https://doi.org/10.2307/1907330
22. M. C. Lovell. "Seasonal adjustment of economic time series and multiple regression analysis." *Journal of the American Statistical Association* 58(304): 993–1010, 1963. https://doi.org/10.1080/01621459.1963.10480682
23. C. Cinelli and C. Hazlett. "Making sense of sensitivity: extending omitted variable bias." *Journal of the Royal Statistical Society B* 82(1): 39–67, 2020. https://doi.org/10.1111/rssb.12348
24. Student. "The probable error of a mean." *Biometrika* 6(1): 1–25, 1908. https://doi.org/10.1093/biomet/6.1.1
25. E. W. Crampton. "The growth of the odontoblasts of the incisor tooth as a criterion of the vitamin C intake of the guinea pig." *Journal of Nutrition* 33(5): 491–504, 1947. https://doi.org/10.1093/jn/33.5.491
26. R Core Team. R 4.5.2 `datasets` documentation: `ToothGrowth`, `PlantGrowth`, `sleep`. https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/ToothGrowth.html (accessed 2026-11-28)
27. R Core Team. R 4.5.2 source: `lm.fit`, `summary.lm`, `logLik.lm`, `predict.lm` and the `qr` documentation. https://svn.r-project.org/R/tags/R-4-5-2/src/library/stats/R/lm.R (accessed 2026-11-28)
28. statsmodels 0.15.0 source: `regression/linear_model.py`, `tools/tools.py`, `stats/stattools.py`. https://github.com/statsmodels/statsmodels (accessed 2026-11-28)
29. NumPy 2.5.4 `numpy.linalg.lstsq` and SciPy 1.18.1 `scipy.linalg.lstsq` documentation. https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html (accessed 2026-11-28)
30. J. K. Lindeløv. "Common statistical tests are linear models (or: how to teach stats)." Updated 28 June 2019. https://lindeloev.github.io/tests-as-linear/ (accessed 2026-11-28)
