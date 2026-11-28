---
social_schema: 2
canonical_url: "https://canery.in/blogs/linear-regression-inference"
---

# Social publishing package — linear-regression-inference

## LinkedIn post

Every number in a regression summary can be rebuilt by hand. Some of them fail when you do.

The thirteenth part of Statistics for Data Scientists recomputes the whole table from the design matrix:

→ The regression on a drug dummy is Student's t-test to the last digit; add patient dummies and it is the paired t.
→ Against NIST's 15 certified digits, Householder QR keeps 10.92 on Longley's data and the textbook normal equations 7.38.
→ On NIST's Filip polynomial, NumPy's default lstsq, statsmodels' default fit and R's default lm keep no correct digit. Each has a one-argument fix.
→ A coefficient is a comparison between units that agree on the other predictors. Longley's GNP keeps a 42nd of its spread once they are held fixed, and its sign flips when Year is left out.
→ Regression does not need normal variables: the slope's 95% interval covered 93.4% to 95.4% with skewed predictors and skewed errors from n = 5 to 1,000. Unequal variance (82.9%) and dependent errors (59.0%) are what break it.

Every number is matched to statsmodels and R, and reproduced by a lab you can rerun.

## LinkedIn first comment

Solve with QR, read the coefficient as a comparison, and check variance and independence before normality.

Read the full article on Canery: https://canery.in/blogs/linear-regression-inference

## Instagram caption

Every number in a regression table, rebuilt by hand. Swipe through the t-test as a regression, NIST's certified digits, the solver defaults that fail, what a coefficient compares, and the conditions that matter more than normality.

Every number comes from a lab you can rerun.

Link in bio.

#statistics #datascience #regression #python #statsmodels #rstats

## Shared feed order

1. `assets/social/feed-01-regression-is-the-t-test.png` — Student's sleep data regressed on a drug dummy: coefficient 1.58, SE 0.849, t = 1.861 on 18 df, p = 0.0792, Student's t-test; with nine patient dummies the same 1.58 has SE 0.389 and t = 4.062 on 9 df, the paired t-test
2. `assets/social/feed-02-fifteen-certified-digits.png` — Exact rational least squares reproduces all 121 certified values of NIST's eleven linear datasets digit for digit; Longley's condition number is 4.86 × 10⁹, and that of XᵀX 2.361 × 10¹⁹, the value Wampler printed in 1969
3. `assets/social/feed-03-qr-not-normal-equations.png` — Correct digits of the worst coefficient: Longley 10.92 by Householder QR and 7.38 by the normal equations; Filip 8.55 by QR and none by the normal equations; NIST certifies 15
4. `assets/social/feed-04-defaults-that-fail.png` — On NIST's Filip polynomial, NumPy's default lstsq and statsmodels' default fit keep no correct digit and R's lm drops x¹⁰ (F = 20.2 says it mattered); rcond=-1, method='qr' and tol = 1e-10 recover 5.41, 8.55 and 8.42 digits
5. `assets/social/feed-05-every-number-traced.png` — Longley's summary recomputed from the design matrix: R-squared 0.995479, adjusted 0.992465, F 330.29, residual SD 304.854 on 9 df, and AIC 233.2 in statsmodels (k = 7) against 235.2 in R (k = 8)
6. `assets/social/feed-06-holding-the-others-fixed.png` — Longley's GNP: slope +0.0348 alone, −0.0358 with the other predictors held fixed, +0.0720 with Year left out; the comparison uses 2,350 of GNP's 99,395 spread, a 42.3rd, the inverse square root of its VIF of 1,788.5
7. `assets/social/feed-07-normality-is-not-the-condition.png` — Coverage of the slope's 95% interval from n = 5 to 1,000: 94.7%–95.3% with a skewed predictor, 94.9%–95.2% with heavy-tailed errors, 93.4%–95.4% with skewed errors and x; down to 82.9% with SD rising with x and 59.0% with autocorrelated errors
8. `assets/social/feed-08-read-the-article.png` — The article's five results in one list, and the call to read it

## Instagram Story

Not produced: this part ships feed cards only, at the owner's request (2026-10-30), so there are no Story frames, Story CTA or link sticker to post.

### Story order

None.

## Asset metadata

### feed-01-regression-is-the-t-test

- File: `assets/social/feed-01-regression-is-the-t-test.png`
- Title: Regression is the t-test
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: Student's sleep data regressed on a drug dummy: coefficient 1.58, SE 0.849, t = 1.861 on 18 df, p = 0.0792, Student's t-test; with nine patient dummies the same 1.58 has SE 0.389 and t = 4.062 on 9 df, the paired t-test
- Technical source: Worked example; Table 1; Figure 1; ledger L38, L43
- Visual structure: lockup and counter; serif title; deck; a panel with the model line, three labelled statistics in ink, a rule, then the paired statistic in blue; takeaway; footer
- Visible-text transcript: Canery.in · extra sleep ~ drug-2 dummy, 20 values · coefficient · 1.58 · the difference in the two drugs' means · standard error · 0.849 · residual SD × √0.2: Student's pooled SE · t on 18 df · 1.861 · p = 0.0792: Student's two-sample t-test · add nine patient dummies: · same 1.58, SE · 0.389 · t = 4.062 on 9 df: the paired t-test · 01 / 08 · Regression is · the t-test. · Student's sleep data on a drug dummy, every · number of the summary built by hand. · Not an approximation: the regression on a · dummy is Student's test to the last digit. · LINEAR REGRESSION BY HAND · CANERY.IN
- Alt text: Card: the sleep data on a drug dummy give coefficient 1.58, SE 0.849, t 1.861 (Student's t-test); with patient dummies SE 0.389, t 4.062 (paired t).
- Long description: Student's 1908 sleep data, twenty values, regressed on a dummy for drug 2. The coefficient is 1.58, the difference between the drugs' means; its standard error is 0.849, the residual standard deviation times the square root of 0.2, which is Student's pooled standard error; t = 1.861 on 18 degrees of freedom with p = 0.0792, Student's two-sample t-test. Adding nine patient dummies keeps the coefficient at 1.58 and shrinks the standard error to 0.389, giving t = 4.062 on 9 degrees of freedom, the paired t-test. Takeaway: the regression on a dummy is Student's test to the last digit.
- Keywords: linear regression, dummy variable, t-test, paired t-test, standard error, Student's sleep data
- Canonical URL: https://canery.in/blogs/linear-regression-inference

### feed-02-fifteen-certified-digits

- File: `assets/social/feed-02-fifteen-certified-digits.png`
- Title: Fifteen digits, certified
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Exact rational least squares reproduces all 121 certified values of NIST's eleven linear datasets digit for digit; Longley's condition number is 4.86 × 10⁹, and that of XᵀX 2.361 × 10¹⁹, the value Wampler printed in 1969
- Technical source: Does it matter how you solve the least squares equations?; ledger L01, L02, L05, L09
- Visual structure: lockup and counter; serif title; deck; a panel with the dataset line, the exact-arithmetic count in tangerine, a rule, then the two condition numbers in ink and blue; takeaway; footer
- Visible-text transcript: Canery.in · NIST's Statistical Reference Datasets · certified in 500-digit arithmetic, printed to 15 · exact rational arithmetic · 121 / 121 · coefficients, standard errors and residual SDs · Longley: 16 years, 6 nearly collinear predictors · condition number of X · 4.86 × 10⁹ · condition number of XᵀX · 2.361 × 10¹⁹ · the value Wampler printed in 1969 · every one of the 15 digits reproduced · 02 / 08 · Fifteen digits, · certified. · Before testing any solver, check the certificate: · least squares on decimals has an exact answer. · All 121 certified values reproduce digit for · digit, with nothing but Python's fractions. · LINEAR REGRESSION BY HAND · CANERY.IN
- Alt text: Card: exact rational arithmetic reproduces 121 of 121 NIST certified values; Longley's condition number is 4.86e9, and XᵀX's 2.361e19.
- Long description: NIST's Statistical Reference Datasets certify regression results computed in 500-digit arithmetic and printed to 15 significant digits. Solving all eleven linear datasets exactly with Python's fractions reproduces 121 of 121 certified coefficients, standard errors and residual standard deviations digit for digit. Longley's data, 16 years and six nearly collinear predictors, give a design matrix with condition number 4.86 × 10⁹; forming XᵀX squares it to 2.361 × 10¹⁹, the value Wampler printed in 1969. Takeaway: all 121 certified values reproduce with nothing but Python's fractions.
- Keywords: NIST StRD, certified values, Longley data, condition number, exact arithmetic, numerical accuracy
- Canonical URL: https://canery.in/blogs/linear-regression-inference

### feed-03-qr-not-normal-equations

- File: `assets/social/feed-03-qr-not-normal-equations.png`
- Title: QR, not the normal equations
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Correct digits of the worst coefficient: Longley 10.92 by Householder QR and 7.38 by the normal equations; Filip 8.55 by QR and none by the normal equations; NIST certifies 15
- Technical source: Does it matter how you solve the least squares equations?; Figures 3 and 4; ledger L10, L16
- Visual structure: lockup and counter; serif title; deck; a panel of four horizontal bars on a 0–15 scale, QR in ink and the normal equations in blue, with the 15-digit line in tangerine; takeaway; footer
- Visible-text transcript: Canery.in · correct digits of the worst coefficient (of 15) · Longley, Householder QR · 10.92 · Longley, normal equations · 7.38 · Filip, Householder QR · 8.55 · Filip, normal equations · 0 · 15 certified · 03 / 08 · QR, not the · normal equations. · Forming XᵀX squares the condition number, · so it doubles the digits the solver loses. · Longley loses 3.5 digits to the textbook route; · Filip loses all of them. · LINEAR REGRESSION BY HAND · CANERY.IN
- Alt text: Card: correct digits of the worst coefficient, Longley 10.92 (QR) and 7.38 (normal equations), Filip 8.55 (QR) and 0 (normal equations).
- Long description: Correct significant digits of the worst coefficient, measured against NIST's 15 certified digits. On Longley's regression, Householder QR keeps 10.92 digits and the normal equations 7.38; on Filip's tenth-degree polynomial, QR keeps 8.55 and the normal equations none. Forming XᵀX squares the condition number, so the normal equations lose about twice as many digits as QR. Takeaway: Longley loses 3.5 digits to the textbook route; Filip loses all of them.
- Keywords: QR decomposition, normal equations, least squares, log relative error, numerical stability, condition number
- Canonical URL: https://canery.in/blogs/linear-regression-inference

### feed-04-defaults-that-fail

- File: `assets/social/feed-04-defaults-that-fail.png`
- Title: Three defaults, zero digits
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: On NIST's Filip polynomial, NumPy's default lstsq and statsmodels' default fit keep no correct digit and R's lm drops x¹⁰ (F = 20.2 says it mattered); rcond=-1, method='qr' and tol = 1e-10 recover 5.41, 8.55 and 8.42 digits
- Technical source: Does it matter how you solve the least squares equations?; Figure 3; ledger L22, L23, L27, L29
- Visual structure: lockup and counter; serif title; deck; a panel with three failing defaults in blue and their causes, a rule, then three fixed calls with their digits in ink; takeaway; footer
- Visible-text transcript: Canery.in · NIST's Filip polynomial, 10th degree, 82 points · NumPy lstsq, default · 0 digits · cutoff 1.8e-14 drops a singular value · statsmodels OLS().fit() · 0 digits · pseudoinverse; warns rank-deficient · R lm, default tol · drops x¹⁰ · F = 20.2 says it mattered · the same calls, fixed (correct digits): · rcond=-1 · 5.41 · method='qr' · 8.55 · tol = 1e-10 · 8.42 · 04 / 08 · Three defaults, · zero digits. · Near rank deficiency the library defaults · truncate or drop, with one warning at most. · Read the warning and the NA: each default · has a one-argument fix. · LINEAR REGRESSION BY HAND · CANERY.IN
- Alt text: Card: on Filip, NumPy lstsq and statsmodels' default keep 0 digits and R's lm drops x¹⁰; rcond=-1, method='qr' and tol 1e-10 give 5.41, 8.55, 8.42.
- Long description: NIST's Filip dataset, 82 points fitted by a tenth-degree polynomial. NumPy's lstsq with its default cutoff, 1.8 × 10⁻¹⁴, discards a singular value and keeps no correct digit; statsmodels' default pseudoinverse fit does the same and warns that the design is rank-deficient; R's lm with its default tolerance drops the x¹⁰ term, which an F test of 20.2 shows mattered. The same calls fixed: rcond=-1 keeps 5.41 digits, method='qr' 8.55 and tol = 1e-10 8.42. Takeaway: read the warning and the NA; each default has a one-argument fix.
- Keywords: numpy lstsq, statsmodels OLS, R lm, rank deficiency, Filip dataset, polynomial regression
- Canonical URL: https://canery.in/blogs/linear-regression-inference

### feed-05-every-number-traced

- File: `assets/social/feed-05-every-number-traced.png`
- Title: Every number, traced
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Longley's summary recomputed from the design matrix: R-squared 0.995479, adjusted 0.992465, F 330.29, residual SD 304.854 on 9 df, and AIC 233.2 in statsmodels (k = 7) against 235.2 in R (k = 8)
- Technical source: Where does every number in the summary come from?; Figures 5 and 6; ledger L24, L28
- Visual structure: lockup and counter; serif title; deck; a panel of six formula-and-value rows, the two AIC rows in tangerine; takeaway; footer
- Visible-text transcript: Canery.in · Longley's summary, recomputed from X · R-squared = 1 − RSS/TSS · 0.995479 · adjusted: (n − 1)/(n − p) · 0.992465 · F, nested in intercept-only · 330.29 · s = √(RSS/(n − p)), 9 df · 304.854 · AIC, statsmodels (k = 7) · 233.2 · AIC, R (k = 8, counts σ) · 235.2 · 05 / 08 · Every number, · traced. · 39 numbers of statsmodels' summary, matched · to 5.6e-12; R's summary to 1.2e-11. · The two libraries agree on every formula · and count AIC's parameters differently. · LINEAR REGRESSION BY HAND · CANERY.IN
- Alt text: Card: Longley's summary from X: R-squared 0.995479, adjusted 0.992465, F 330.29, residual SD 304.854; AIC 233.2 in statsmodels, 235.2 in R.
- Long description: Every number of Longley's regression summary recomputed from the design matrix: R-squared = 1 − RSS/TSS = 0.995479; adjusted R-squared, with the factor (n − 1)/(n − p), 0.992465; the F statistic against the intercept-only model, 330.29; the residual standard deviation √(RSS/(n − p)), 304.854 on 9 degrees of freedom; and AIC, 233.2 in statsmodels, which counts seven parameters, against 235.2 in R, which also counts σ. The lab matches 39 statsmodels numbers to 5.6 × 10⁻¹² and R's summary to 1.2 × 10⁻¹¹. Takeaway: the two libraries agree on every formula and count AIC's parameters differently.
- Keywords: regression output explained, R-squared, adjusted R-squared, F statistic, AIC, statsmodels summary
- Canonical URL: https://canery.in/blogs/linear-regression-inference

### feed-06-holding-the-others-fixed

- File: `assets/social/feed-06-holding-the-others-fixed.png`
- Title: What holding fixed leaves
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Longley's GNP: slope +0.0348 alone, −0.0358 with the other predictors held fixed, +0.0720 with Year left out; the comparison uses 2,350 of GNP's 99,395 spread, a 42.3rd, the inverse square root of its VIF of 1,788.5
- Technical source: What does a coefficient measure?; Figures 8, 9 and 10; ledger L37, L41
- Visual structure: lockup and counter; serif title; deck; a panel with three slopes for GNP, a rule, then the usable spread as a fraction; takeaway; footer
- Visible-text transcript: Canery.in · Longley: employment on GNP · GNP alone · +0.0348 · others held fixed · −0.0358 · the multiple-regression coefficient · Year left out · +0.0720 · omitted-variable bias, exact in the sample · spread of GNP the comparison can use · 2,350 of 99,395 · 1/42.3 · = 1/√VIF, VIF 1788.5 · 06 / 08 · What holding · fixed leaves. · A coefficient compares units that agree on · every other predictor; the data hold few. · Same data, three answers for GNP: the · comparison, not the arithmetic, changed. · LINEAR REGRESSION BY HAND · CANERY.IN
- Alt text: Card: GNP's slope is +0.0348 alone, −0.0358 with the others fixed and +0.0720 with Year left out; it keeps 1/42.3 of its spread, VIF 1788.5.
- Long description: Longley's employment regressed on GNP gives a slope of +0.0348 on its own, −0.0358 with the other five predictors held fixed (the multiple-regression coefficient), and +0.0720 when Year is left out, a change given exactly by the omitted-variable bias formula. Holding the others fixed leaves GNP a standard deviation of 2,350 out of 99,395, one 42.3rd, which is the inverse square root of its variance inflation factor of 1,788.5. Takeaway: same data, three answers for GNP; the comparison, not the arithmetic, changed.
- Keywords: regression coefficient interpretation, Frisch-Waugh-Lovell, omitted variable bias, multicollinearity, VIF, conditional association
- Canonical URL: https://canery.in/blogs/linear-regression-inference

### feed-07-normality-is-not-the-condition

- File: `assets/social/feed-07-normality-is-not-the-condition.png`
- Title: Normal variables? Not needed
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Coverage of the slope's 95% interval from n = 5 to 1,000: 94.7%–95.3% with a skewed predictor, 94.9%–95.2% with heavy-tailed errors, 93.4%–95.4% with skewed errors and x; down to 82.9% with SD rising with x and 59.0% with autocorrelated errors
- Technical source: Which conditions carry the weight?; Figure 13; ledger L32, L33, L34
- Visual structure: lockup and counter; serif title; deck; a panel of five conditions with their coverage ranges, the two failures in blue, and the simulation's size; takeaway; footer
- Visible-text transcript: Canery.in · coverage of the slope's 95% interval, n = 5 to 1,000 · skewed predictor · 94.7% to 95.3% · heavy-tailed errors · 94.9% to 95.2% · skewed errors and x · 93.4% to 95.4% · SD rising with x · down to 82.9% · autocorrelated errors · down to 59.0% · 20,000 simulated datasets per point; MCSE 0.15 points · 07 / 08 · Normal variables? · Not needed. · Normality is about the errors, and it barely · moved coverage even at n = 5. · Unequal variance and dependence break the · interval, and more data make it worse. · LINEAR REGRESSION BY HAND · CANERY.IN
- Alt text: Card: the slope interval covers 93.4–95.4% with skewed x, heavy tails or skewed errors; 82.9% with unequal variance, 59.0% with dependence.
- Long description: Measured coverage of the slope's nominal 95% interval, y = 1 + 2x + error, 20,000 simulated datasets per point and n from 5 to 1,000 (Monte Carlo standard error 0.15 points): a skewed predictor gives 94.7% to 95.3%, heavy-tailed errors 94.9% to 95.2%, strongly skewed errors with a skewed predictor 93.4% to 95.4%. When the error SD rises with x coverage falls to 82.9%, and with autocorrelated errors to 59.0%. Takeaway: unequal variance and dependence break the interval, and more data make it worse.
- Keywords: linear regression assumptions, normality assumption, coverage, heteroskedasticity, autocorrelation, simulation
- Canonical URL: https://canery.in/blogs/linear-regression-inference

### feed-08-read-the-article

- File: `assets/social/feed-08-read-the-article.png`
- Title: Linear regression, by hand
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: The article's five results in one list, and the call to read it
- Technical source: Key takeaways
- Visual structure: lockup and counter; serif title; deck; a panel listing five results, the last two in blue; takeaway; call to action with the canonical URL in tangerine
- Visible-text transcript: Canery.in · by hand · the t-test, the paired t and ANOVA are regressions · arithmetic · QR 10.92 digits, normal equations 7.38 · coefficients · comparisons between units, not interventions · two intervals · a CI used as a PI covers 7.8% at n = 600 · conditions · linearity, independence, constant variance · 08 / 08 · Linear regression, · by hand. · Every number in the summary rebuilt from · the design matrix, and every guarantee measured. · The full walk-through, with the lab, the · notebook and NIST's certified test data. · READ IT AT CANERY.IN/BLOGS/LINEAR-REGRESSION-INFERENCE
- Alt text: Card: the article's five results, from the t-test as a regression to the conditions that matter, with the link to read it.
- Long description: A summary card: the t-test, the paired t and ANOVA are regressions; QR keeps 10.92 digits on Longley where the normal equations keep 7.38; coefficients are comparisons between units, not interventions; a confidence interval used as a prediction interval covers 7.8% of new observations at n = 600; and the conditions that matter are linearity, independence and constant variance. It points to the full article with the lab, the notebook and NIST's certified test data.
- Keywords: linear regression, regression inference, statistics, data science, NIST, Python
- Canonical URL: https://canery.in/blogs/linear-regression-inference
