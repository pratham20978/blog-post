# Source ledger — linear-regression-inference

Part 13 of *Statistics for Data Scientists*. Researched 2026-11-28, inline (no agents). Numbers the article calls computed
or measured come from `lab/regression.py` and need no key; every published number, date, attribution, named result and
library convention carries one below. Read in full or at the cited sections: Wampler 1969 (NBS Journal of Research, open),
Almiron et al. 2010 (JSS, sections 3–4), Ernst and Albers 2017 (Europe PMC full text, CC BY), Schmidt and Finan 2018
(the authors' UCL copy: abstract and simulation section), Gelman, Hill and Vehtari's *Regression and Other Stories*
(the authors' free PDF: sections 10.2, 10.5, 11.1, 12.2), the LAPACK Users' Guide sections 2.3.2 and 4.5, and NIST's
StRD pages (certification method, FAQ, background, both data files). Read as source code in the lab's environment:
statsmodels 0.15.0, NumPy 2.5.4 and SciPy 1.18.1 docstrings, R 4.5.2's `lm.fit`, `summary.lm`, `logLik.lm` and the `qr`
help page. Cited for what their abstracts state: Longley 1967, Wampler 1970, Beaton, Rubin and Barone 1976, McCullough
1998, McCullough and Vinod 1999, McCullough, Mokfi and Almaeenejad 2019, Hill et al. 2024, Lumley et al. 2002, Williams
et al. 2013, Knief and Forstmeier 2021, Box 1966, Lovell 1963, Cinelli and Hazlett 2020. Golub 1965, Golub and Wilkinson
1966 and Frisch and Waugh 1933 are cited as Wampler 1969 and Lovell 1963 describe them.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S1 | T1 | NIST, Statistical Reference Datasets, NIST Standard Reference Database 140 (J. Filliben and A. Possolo, DataCite creators): linear least squares background (`lls_info`), certification method (`c-Longley`, `c-Filip`), FAQ, dataset pages, `Longley.dat`, `Filip.dat` and the nine other linear files | National Institute of Standards and Technology | 1999 | 10.18434/T43G6C | standard | https://www.itl.nist.gov/div898/strd/ | 2026-11-28 |
| S2 | T1 | Longley, J. W., "An appraisal of least squares programs for the electronic computer from the point of view of the user" (abstract via OpenAlex) | Journal of the American Statistical Association 62(319):819–841 | 1967 | 10.1080/01621459.1967.10500896 | peer-reviewed | https://doi.org/10.1080/01621459.1967.10500896 | 2026-11-28 |
| S3 | T1 | Wampler, R. H., "An evaluation of linear least squares computer programs" (read in full: sections 1–4, the remarks in section 11, references) | Journal of Research of the National Bureau of Standards B 73B(2):59–90 | 1969 | 10.6028/jres.073b.009 | peer-reviewed | https://nvlpubs.nist.gov/nistpubs/jres/73B/jresv73Bn2p59_A1b.pdf | 2026-11-28 |
| S4 | T1 | Wampler, R. H., "A report on the accuracy of some widely used least squares computer programs" (abstract via OpenAlex) | Journal of the American Statistical Association 65(330):549–565 | 1970 | 10.1080/01621459.1970.10481103 | peer-reviewed | https://doi.org/10.1080/01621459.1970.10481103 | 2026-11-28 |
| S5 | T1 | Beaton, A. E., Rubin, D. B. & Barone, J. L., "The acceptability of regression solutions: another look at computational accuracy" (abstract via OpenAlex) | Journal of the American Statistical Association 71(353):158–168 | 1976 | 10.1080/01621459.1976.10481507 | peer-reviewed | https://doi.org/10.1080/01621459.1976.10481507 | 2026-11-28 |
| S6 | T1 | McCullough, B. D., "Assessing the reliability of statistical software: Part I" (abstract via OpenAlex; its LRE as S8 section 3.1 states it) | The American Statistician 52(4):358–366 | 1998 | 10.1080/00031305.1998.10480597 | peer-reviewed | https://doi.org/10.1080/00031305.1998.10480597 | 2026-11-28 |
| S7 | T1 | McCullough, B. D. & Vinod, H. D., "The numerical reliability of econometric software" (abstract via OpenAlex; the survey for rung 1) | Journal of Economic Literature 37(2):633–665 | 1999 | 10.1257/jel.37.2.633 | peer-reviewed | https://doi.org/10.1257/jel.37.2.633 | 2026-11-28 |
| S8 | T1 | Almiron, M. G., Lopes, B., Oliveira, A. L. C., Medeiros, A. C. & Frery, A. C., "On the numerical accuracy of spreadsheets" (read: sections 3.1, 3.2, 4.3, Table 6) | Journal of Statistical Software 34(4) | 2010 | 10.18637/jss.v034.i04 | peer-reviewed | https://www.jstatsoft.org/article/view/v034i04 | 2026-11-28 |
| S9 | T1 | McCullough, B. D., Mokfi, T. & Almaeenejad, M., "On the accuracy of linear regression routines in some data mining packages" (abstract via OpenAlex; forward chase from S2) | WIREs Data Mining and Knowledge Discovery 9(3):e1279 | 2019 | 10.1002/widm.1279 | peer-reviewed | https://doi.org/10.1002/widm.1279 | 2026-11-28 |
| S10 | T1 | Hill, C., Du, L., Johnson, M. & McCullough, B. D., "Comparing programming languages for data analytics: accuracy of estimation in Python and R" (abstract via OpenAlex; forward chase from S6) | WIREs Data Mining and Knowledge Discovery 14(3):e1531 | 2024 | 10.1002/widm.1531 | peer-reviewed | https://doi.org/10.1002/widm.1531 | 2026-11-28 |
| S11 | T2 | Anderson, E. et al., *LAPACK Users' Guide*, 3rd ed.: section 2.3.2 (least squares drivers) and section 4.5 with its further details (error bounds for linear least squares) | SIAM (online edition at netlib) | 1999 | 10.1137/1.9780898719604 | official-docs | https://netlib.org/lapack/lug/node83.html | 2026-11-28 |
| S12 | T1 | Golub, G. H., "Numerical methods for solving linear least squares problems" (cited as S3 section 4 describes it) | Numerische Mathematik 7(3):206–216 | 1965 | 10.1007/BF01436075 | peer-reviewed | https://doi.org/10.1007/BF01436075 | 2026-11-28 |
| S13 | T1 | Golub, G. H. & Wilkinson, J. H., "Note on the iterative refinement of least squares solution" (cited as S3 remark 6 describes it) | Numerische Mathematik 9(2):139–148 | 1966 | 10.1007/BF02166032 | peer-reviewed | https://doi.org/10.1007/BF02166032 | 2026-11-28 |
| S14 | T1 | Ernst, A. F. & Albers, C. J., "Regression assumptions in clinical psychology research practice — a systematic review of common misconceptions" (read in full, Europe PMC PMC5436580, CC BY) | PeerJ 5:e3323 | 2017 | 10.7717/peerj.3323 | peer-reviewed | https://doi.org/10.7717/peerj.3323 | 2026-11-28 |
| S15 | T1 | Williams, M. N., Grajales, C. A. G. & Kurkiewicz, D., "Assumptions of multiple regression: correcting two misconceptions" (abstract via OpenAlex) | Practical Assessment, Research & Evaluation 18(11) | 2013 | 10.7275/55hn-wk47 | peer-reviewed | https://scholarworks.umass.edu/pare/vol18/iss1/11 | 2026-11-28 |
| S16 | T1 | Lumley, T., Diehr, P., Emerson, S. & Chen, L., "The importance of the normality assumption in large public health data sets" (abstract via OpenAlex) | Annual Review of Public Health 23:151–169 | 2002 | 10.1146/annurev.publhealth.23.100901.140546 | peer-reviewed | https://doi.org/10.1146/annurev.publhealth.23.100901.140546 | 2026-11-28 |
| S17 | T1 | Schmidt, A. F. & Finan, C., "Linear regression and the normality assumption" (read: the authors' UCL copy, abstract and the simulation section) | Journal of Clinical Epidemiology 98:146–151 | 2018 | 10.1016/j.jclinepi.2017.12.006 | peer-reviewed | https://discovery.ucl.ac.uk/10070182/1/Schmidt_UCL_depos_JCE2018.pdf | 2026-11-28 |
| S18 | T1 | Knief, U. & Forstmeier, W., "Violating the normality assumption may be the lesser of two evils" (abstract; CC BY 4.0) | Behavior Research Methods 53(6):2576–2590 | 2021 | 10.3758/s13428-021-01587-5 | peer-reviewed | https://doi.org/10.3758/s13428-021-01587-5 | 2026-11-28 |
| S19 | T1 | Gelman, A., Hill, J. & Vehtari, A., *Regression and Other Stories* (the authors' free PDF, corrections to 18 May 2025): sections 10.2, 10.5, 11.1, 12.2 | Cambridge University Press (book) | 2020 | 10.1017/9781139161879 | peer-reviewed | https://users.aalto.fi/~ave/ROS.pdf | 2026-11-28 |
| S20 | T1 | Box, G. E. P., "Use and abuse of regression" (first page via OpenAlex) | Technometrics 8(4):625–629 | 1966 | 10.2307/1266635 | peer-reviewed | https://doi.org/10.2307/1266635 | 2026-11-28 |
| S21 | T1 | Frisch, R. & Waugh, F. V., "Partial time regressions as compared with individual trends" (cited as S22 describes it) | Econometrica 1(4):387–401 | 1933 | 10.2307/1907330 | peer-reviewed | https://doi.org/10.2307/1907330 | 2026-11-28 |
| S22 | T1 | Lovell, M. C., "Seasonal adjustment of economic time series and multiple regression analysis" (abstract via OpenAlex) | Journal of the American Statistical Association 58(304):993–1010 | 1963 | 10.1080/01621459.1963.10480682 | peer-reviewed | https://doi.org/10.1080/01621459.1963.10480682 | 2026-11-28 |
| S23 | T1 | Cinelli, C. & Hazlett, C., "Making sense of sensitivity: extending omitted variable bias" (abstract via OpenAlex) | Journal of the Royal Statistical Society B 82(1):39–67 | 2020 | 10.1111/rssb.12348 | peer-reviewed | https://doi.org/10.1111/rssb.12348 | 2026-11-28 |
| S24 | T1 | Student, "The probable error of a mean" (as read for Parts 2 and 8: Illustration I) | Biometrika 6(1):1–25 | 1908 | 10.1093/biomet/6.1.1 | peer-reviewed | https://doi.org/10.1093/biomet/6.1.1 | 2026-11-28 |
| S25 | T1 | Crampton, E. W., "The growth of the odontoblasts of the incisor tooth as a criterion of the vitamin C intake of the guinea pig" (metadata via OpenAlex; cited by R's ToothGrowth help) | Journal of Nutrition 33(5):491–504 | 1947 | 10.1093/jn/33.5.491 | peer-reviewed | https://doi.org/10.1093/jn/33.5.491 | 2026-11-28 |
| S26 | T2 | R 4.5.2 `datasets` help pages: `ToothGrowth` (source Bliss 1952; reference Crampton 1947), `PlantGrowth` (Dobson 1983), `sleep` (Student 1908) | R Core Team | 2025 | — | official-docs | https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/ToothGrowth.html | 2026-11-28 |
| S27 | T3 | R 4.5.2 source: `stats::lm.fit` (tol 1e-07, `C_Cdqrls`), `stats:::summary.lm`, `stats:::logLik.lm`; `base::qr` help (LINPACK `dqrdc2`, limited pivoting) | R Core Team | 2025 | — | source | https://svn.r-project.org/R/tags/R-4-5-2/src/library/stats/R/lm.R | 2026-11-28 |
| S28 | T3 | statsmodels 0.15.0 source: `regression/linear_model.py` (`OLS.fit`, `info_criteria`, `condition_number`, `summary`), `tools/tools.py` (`pinv_extended`), `stats/stattools.py` (`omni_normtest`, `jarque_bera`, `durbin_watson`) | statsmodels developers | 2026 | — | source | https://github.com/statsmodels/statsmodels | 2026-11-28 |
| S29 | T3 | NumPy 2.5.4 `numpy.linalg.lstsq` and SciPy 1.18.1 `scipy.linalg.lstsq` docstrings (rcond default and its 2.0 change; default driver `gelsd`) | NumPy and SciPy developers | 2026 | — | source | https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html | 2026-11-28 |
| S30 | T4 | Lindeløv, J. K., "Common statistical tests are linear models (or: how to teach stats)", updated 28 June 2019 (framing only) | personal site | 2019 | — | practitioner | https://lindeloev.github.io/tests-as-linear/ | 2026-11-28 |

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 2 | NIST StRD | the eleven linear least squares data files (`Norris` … `Wampler5`) | all eleven downloaded, 1.3–4.9 kB each; certified values in lines 31–55 of each header |
| 2 | 2 | NIST StRD | index, `general/bkground`, `lls/lls.shtml`, `lls/lls_info`, FAQ, how-to, `c-Longley`, `c-Filip`, `i-Longley`, `v-Longley` | 500-digit certification by Bailey's multiple-precision package, rounded to 15 digits; difficulty grades; centring as the suggested remedy; Longley's variable names |
| 3 | 2 | DataCite | DOI 10.18434/T43G6C | SRD 140, creators Filliben and Possolo, issued 1999; rights point to NIST's licence page |
| 4 | 2 | NIST | open/license page | SRD Act: copyright may be secured on Standard Reference Data, so the lab fetches the files with a checksum instead of shipping them |
| 5 | 1 | OpenAlex | title.search "reliability of statistical software", "accuracy of statistical software", "least squares programs electronic computer", "acceptability of regression solutions" | HTTP 429, search cluster rate-limited all session; DOI lookups still worked |
| 6 | 1 | Crossref | bibliographic "assessing the reliability of statistical software McCullough" | McCullough 1998 (Part I) and 1999 (Part II) |
| 7 | 1 | Crossref | bibliographic "accuracy of least squares computer programs Longley 1967" | Longley 1967; Wampler 1970; Longley and Longley 1997 (Gram–Schmidt vs Householder); Boehm et al. 1976 |
| 8 | 1 | Crossref | bibliographic "acceptability of regression solutions … Beaton Rubin Barone" | empty body (rate-limited); found by DOI in row 10 |
| 9 | 1 | Crossref | bibliographic "accuracy of some widely used least squares computer programs Wampler" | Wampler 1969 in the NBS Journal of Research (open); NBS Technical Note 1126 (1980) |
| 10 | 1 | OpenAlex | DOI lookups: McCullough 1998, Longley 1967, Beaton–Rubin–Barone 1976, McCullough 1999, Wampler 1970 | metadata and abstracts; all five closed access |
| 11 | 2 | NIST Journal of Research | Wampler 1969 full text | correct-digit count, Longley's X'X condition 2.361 × 10^19, Golub–Wilkinson's squaring remark, the Householder programs |
| 12 | 1 | JSS | Almiron et al. 2010 full text | LRE definition and reporting convention; StRD certification restated; McCullough's nine-digit expectation; Filip defeats every spreadsheet but Excel |
| 13 | 3 | netlib | LAPACK Users' Guide nodes 27, 82, 83 | xGELS (QR), xGELSY, xGELSS, xGELSD; the least squares error bound with κ and κ² tan θ |
| 14 | 1 | OpenAlex | DOI lookups: Golub 1965, Golub–Wilkinson 1966, Lawson–Hanson 1995, Almiron 2010, Wampler 1969, Bailey 1995 | metadata; no abstracts for the two Numerische Mathematik papers, so they are cited through Wampler |
| 15 | 4 | PeerJ, then Europe PMC | PeerJ PDF (HTTP 403); Europe PMC search DOI:10.7717/peerj.3323, then fullTextXML PMC5436580 | Ernst and Albers 2017 in full, CC BY: 893 papers, 172 with linear regression, 2% transparent and correct |
| 16 | 4 | OpenAlex | DOI lookups: Lumley 2002, Williams 2013, Frisch–Waugh 1933, Lovell 1963, O'Brien 2007, Marquardt 1970, Cinelli–Hazlett 2020, Box 1966 (a wrong DOI), Crampton 1947, *Regression and Other Stories* | abstracts for six; O'Brien and Marquardt have no abstract and were not read, so neither is cited |
| 17 | 6 | Aalto (Vehtari's page) | *Regression and Other Stories* PDF | sections 10.2 (comparisons), 10.5 (paired designs as regressions), 11.1 (assumptions in order), 12.2 (centring with interactions) |
| 18 | 5 | lab venv | statsmodels 0.15.0 source | `fit(method="pinv")` default; `pinv_extended` rcond 1e-15; AIC and BIC without the scale parameter; the condition-number note above 1,000; the diagnostic block's functions |
| 19 | 5 | R 4.5.2 | `lm.fit`, `summary.lm`, `logLik.lm`, `?qr`, `?ToothGrowth` | tol 1e-07 with `dqrdc2`; σ̂² on the residual df; logLik df p + 1; ToothGrowth's provenance |
| 20 | 4 | Crossref | bibliographic: McCullough–Vinod survey; Box 1966; Lovell's FWL proof; Schmidt–Finan; Knief–Forstmeier; Plackett 1949 | the 1999 JEL survey; Box's DOI 10.2307/1266635; Schmidt and Finan 2018; Knief and Forstmeier 2021; Plackett not used |
| 21 | 4 | OpenAlex | DOI lookups for row 20's hits | abstracts for McCullough–Vinod, Box, Knief–Forstmeier; Schmidt–Finan's open UCL copy |
| 22 | 4 | UCL Discovery | Schmidt and Finan 2018, author copy | normality irrelevant beyond about 10 observations per variable; homoscedasticity and independence matter at any n |
| 23 | 4 | Semantic Scholar | forward chase: papers citing Longley 1967 (100 returned) | McCullough, Mokfi and Almaeenejad 2019 (data mining packages); an iPad accuracy study; most others are collinearity estimators |
| 24 | 4 | Semantic Scholar | forward chase: papers citing McCullough 1998 (180) and Lumley 2002 | Hill et al. 2024 (Python and R libraries on StRD); Lumley's citation list came back empty |
| 25 | 4 | arXiv | all:"normal equations" AND all:"least squares" AND all:accuracy | no results |
| 26 | 5 | lab venv | NumPy 2.5.4 and SciPy 1.18.1 `lstsq` docstrings | NumPy's rcond default became eps × max(M, N) in 2.0; SciPy defaults to `gelsd` |
| 27 | 6 | web | Lindeløv's "tests as linear models" page | live, updated 28 June 2019; framing only |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | NIST's Statistical Reference Datasets (Standard Reference Database 140) supply datasets with certified results so that statistical software can be evaluated objectively; the site dates from 1999 and its data were last updated in 2003 | S1 index | — |
| L02 | NIST computed the certified values in multiple precision accurate to 500 digits with Bailey's package, reading the data exactly, and rounded the results to 15 significant digits only at output | S1 c-Longley, Methodology | linear regression, ANOVA and univariate pages |
| L03 | NIST quotes its results to many digits for comparing software, not to signal statistical significance | S1 FAQ A7, A9 | — |
| L04 | NIST grades Longley and Filip as of higher difficulty; its higher-difficulty linear datasets are multicollinear, and it suggests centring the predictors as one remedy when software fails them | S1 lls_info | difficulty depends on the algorithm |
| L05 | Longley's response is total derived employment; the six predictors are the GNP implicit price deflator (1954 = 100), GNP, unemployment, the size of the armed forces, the non-institutional population aged 14 and over, and the year; 16 observations | S1 i-Longley, Longley.dat | years 1947–1962 |
| L06 | Longley found many least squares programs of the day used methods suited to desk calculators; computers then carried about eight digits, and his economic test data needed the program or the data altered before most programs gave accurate results | S2 abstract | programs tested in 1967 |
| L07 | Wampler ran two fifth-degree polynomial problems through more than twenty least squares programs; those using Householder transformations or Gram–Schmidt orthonormalization were much more accurate than those using elimination, and some reported coefficients with not one correct significant digit | S3 abstract, sections 3–4 | 1960s machines, single and double precision |
| L08 | Wampler counted a coefficient's correct digits as minus the base-10 log of its relative error, a count he says Jordan had used before | S3 section 3 | nonzero true value |
| L09 | Wampler gave the eigenvalue-ratio condition of Longley's 7 × 7 XᵀX as 2.361 × 10^19 | S3 section 2 | — |
| L10 | Golub and Wilkinson pointed out that XᵀX has roughly the square of X's condition number, so it pays to work with X rather than XᵀX | S3 remark 6, S13 | — |
| L11 | The Householder method for least squares was described by Golub (1965) and by Businger and Golub (1965); Wampler's best double-precision program used it | S3 section 4, S12 | — |
| L12 | For QR- or SVD-based least squares in LAPACK, the relative error of the solution is bounded by about p(n)ε(2κ(A)/cos θ + tan θ κ(A)²), with sin θ the residual norm over the response norm | S11 node83 | full-rank overdetermined problems; p(n) modest |
| L13 | LAPACK's driver xGELS uses a QR factorization; xGELSY a complete orthogonal factorization; xGELSS and xGELSD the SVD, with a user cutoff that treats small singular values as zero | S11 node27, node83 | — |
| L14 | Beaton, Rubin and Barone argued that the numerically accurate Longley solution was probably not a reasonable estimate of the coefficients, because data accuracy and model choice move the answer more than the arithmetic | S5 abstract | — |
| L15 | McCullough proposed intermediate-level accuracy tests for statistical software covering estimation, random number generation and distributions, with ways to summarise the results | S6 abstract | — |
| L16 | The log relative error is LRE = −log10(abs(x − c)/abs(c)) for a certified value c ≠ 0 (−log10 abs(x) when c = 0), read as the number of correct significant digits | S8 section 3.1 | — |
| L18 | McCullough and Vinod's survey showed users cannot safely assume econometric software is accurate | S7 abstract | — |
| L19 | Applied to seven data mining packages, NIST's tests found only two with reliable linear regression routines | S9 abstract | packages as of 2019 |
| L20 | A 2024 study of R and Python libraries on NIST's data recommended R's stats package for linear regression | S10 abstract | libraries as of 2024 |
| L21 | In Almiron et al.'s tests, Excel 2007 was the only spreadsheet to return results for Filip, with about seven correct digits | S8 Table 6, section 4.3 | 2008–2009 versions |
| L22 | statsmodels 0.15.0 `OLS.fit` defaults to `method="pinv"`, the Moore–Penrose pseudoinverse; `method="qr"` uses a QR factorization | S28 linear_model.py | — |
| L23 | statsmodels' pseudoinverse zeroes singular values below 1e-15 times the largest, and the fit warns that the design is rank-deficient when its rank check falls short | S28 tools.py, linear_model.py | default rcond |
| L24 | statsmodels' AIC and BIC count the mean parameters only (df_model plus the constant), leaving out the error variance, while R's `logLik.lm` sets df = p + 1; so AIC differs by 2 between them | S28 info_criteria; S27 logLik.lm | Gaussian linear model |
| L25 | statsmodels' condition number is the square root of the largest to smallest eigenvalue ratio of XᵀX, and its summary adds a note when it exceeds 1,000 | S28 condition_number, summary | unweighted OLS |
| L26 | statsmodels' summary computes Omnibus with SciPy's `normaltest` (D'Agostino–Pearson), Jarque–Bera from skewness and kurtosis, and Durbin–Watson as Σ(eₜ − eₜ₋₁)²/Σeₜ² | S28 stattools.py | — |
| L27 | R's `lm` solves by LINPACK's modified `dqrdc2` QR with tolerance 1e-07, moving columns with near-zero norm to the end, which `lm` reports as NA coefficients | S27 lm.fit, `?qr` | default `tol` |
| L28 | R's `summary.lm` divides the residual sum of squares by the residual degrees of freedom, adjusts R² by (n − df.int)/rdf, and forms F from the model mean square over that variance | S27 summary.lm | — |
| L29 | NumPy's `lstsq` treats singular values below rcond times the largest as zero, with rcond defaulting to machine precision times max(M, N) since NumPy 2.0 (previously −1, machine precision) | S29 | NumPy ≥ 2.0 |
| L30 | SciPy's `lstsq` uses LAPACK `gelsd` by default, with `gelsy` and `gelss` as options, and its singular-value cutoff defaults to machine precision | S29 (docstring; `_basic.py`, cond defaults to finfo eps) | SciPy 1.18.1 |
| L31 | Ernst and Albers reviewed all 893 articles of 2013 in twelve clinical psychology journals; 172 used linear regression; 2% of those were both transparent and correct about the assumptions, 92% were unclear, and 4% treated normality of the variables rather than the errors as required | S14 abstract, Tables 3–4 | clinical psychology, 2013 |
| L32 | Williams, Grajales and Kurkiewicz corrected the claim that multiple regression needs normally distributed variables: least squares needs normal errors for trustworthy inference at least in small samples, not normal responses or predictors | S15 abstract | — |
| L33 | Lumley and colleagues: the belief that t-tests and linear regression need normally distributed outcomes is widespread and wrong; in large samples both are valid for any distribution | S16 abstract | large samples |
| L34 | Schmidt and Finan found normality violations made no noticeable difference beyond about 10 observations per variable, while the model form, extreme observations, constant variance and independence mattered at any sample size; in their violated scenario coverage did not improve with n | S17 abstract, simulation section | their simulation designs |
| L35 | Knief and Forstmeier found Gaussian models robust to non-normality over a wide range of conditions, with p-values reliable except for data with influential outliers at strict α | S18 abstract | their simulation designs |
| L36 | Gelman, Hill and Vehtari rank the assumptions in decreasing importance as validity, representativeness, additivity and linearity, independence of errors, equal variance and normality of errors; normality barely matters for estimating the line and matters when predicting individual points | S19 section 11.1 | — |
| L37 | Gelman, Hill and Vehtari read a coefficient as a comparison between units that differ in one predictor and agree on the others; reading it as the change caused within a unit needs causal assumptions | S19 section 10.2 | — |
| L38 | A paired or blocked design can be analysed as a regression with a treatment indicator and indicators for the pairs | S19 section 10.5 | — |
| L39 | Centring the inputs makes each main effect in a model with an interaction a comparison at the other input's average | S19 section 12.2 | — |
| L40 | Box stated the Gauss–Markov property (least squares estimates unbiased with smallest variance among linear unbiased estimates when errors are uncorrelated with equal variance and zero mean) and warned that for unplanned data the error term stands in for latent variables, which is where trouble starts | S20 first page | — |
| L41 | The partialling-out result is the Frisch–Waugh theorem of 1933, which Lovell extended in 1963; it is now called the Frisch–Waugh–Lovell theorem | S21, S22 abstract | — |
| L42 | Cinelli and Hazlett extend the omitted-variable bias formula into sensitivity analysis for unobserved confounders | S23 abstract | — |
| L43 | Student's 1908 Illustration I is the sleep data reused from Parts 2 and 8 | S24, S26 | — |
| L44 | PlantGrowth (30 plants, a control and two treatments) comes from Dobson's 1983 textbook via R | S26 | — |
| L45 | ToothGrowth records odontoblast length in 60 guinea pigs given vitamin C at 0.5, 1 or 2 mg a day as orange juice or ascorbic acid; R cites Bliss (1952) as the source and Crampton (1947) as the study | S26, S25 | — |
| L46 | Filip is NIST's observed dataset by Filippelli: 82 observations fitted by a tenth-degree polynomial in one predictor, graded higher difficulty | S1 Filip.dat | — |
| L47 | NIST's generated Wampler datasets were developed at NBS in the early 1970s; Wampler 1 to 5 share the same x and fifth-degree model and differ in their noise | S1 lls_info, Wampler files | — |
| L48 | Framing only: the common tests (t-tests, ANOVA, correlation) can be taught as special cases of the linear model | S30 | practitioner page |
| L49 | statsmodels' OLS does not include an intercept by default; the user adds one with `add_constant` | S28 (`OLS` docstring) | array interface, no formula |
| L50 | R's `predict.lm` takes `interval = "confidence"` or `"prediction"`, and its prediction intervals are for a single observation at each new case | S27 (`?predict.lm`) | R 4.5.2 |
| L51 | statsmodels' `get_prediction(...).summary_frame()` reports the interval for the mean as `mean_ci_lower`/`mean_ci_upper` and for a new observation as `obs_ci_lower`/`obs_ci_upper` | S28 (`regression/_prediction.py`; columns as printed in the lab's environment) | statsmodels 0.15.0 |
| L52 | On the Univac 1108 in double precision, the Householder program LSTSQ averaged 14.6 correct digits on Wampler's problem Y1 and the five elimination programs 9.3 to 9.7 | S3 Table 4 | 1968 runs, 18-digit double precision |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S3 | Tables 1 and 4 (correct digits by program and algorithm) | Does it matter how you solve? / L07 | historical evidence that elimination lost digits | US government work (public domain) | https://nvlpubs.nist.gov/nistpubs/jres/73B/jresv73Bn2p59_A1b.pdf | not used as an image: the tables are text, and two of their numbers are quoted in prose instead |
| F2 | S17 | Figure 2 (coverage against sample size) | Which conditions carry the weight? / L34 | shows coverage not recovering under heteroskedasticity | Elsevier copyright; author manuscript only | https://discovery.ucl.ac.uk/10070182/1/Schmidt_UCL_depos_JCE2018.pdf | do not reuse; Figure 13 measures our own conditions |
| F3 | S19 | Figures 12.1–12.2 (centring with interactions) | Interactions and centring / L39 | the interaction and centring idea on kid IQ data | personal-use PDF, no reuse | https://users.aalto.fi/~ave/ROS.pdf | do not reuse; Figure 11 uses ToothGrowth |

## Open questions

- NIST's pages disagree on the certified precision: the background page says 16 significant digits, the FAQ and the
  certification page say 15, and the files print 15. Exact rational arithmetic reproduces all 15 printed digits of every
  Longley and Filip coefficient and standard error, so the article says 15.
- `Longley.dat`'s header reads "7 Parameters (B0,B1,...,B7)", which names eight. The model line and the certified table
  have B0 to B6. Not mentioned in the article.
- Wampler's OCR text prints Longley's condition as "2.361 × 10!!1"; the computed κ(X)² is 2.3612 × 10^19, so the exponent
  is 19.
- Whether NIST secured copyright on SRD 140 is not stated on the StRD pages; the data files carry no copyright line. The lab
  therefore downloads both files from NIST and checks a SHA-256 hash rather than redistributing them.
- Hill et al. (2024) recommend R's stats package for linear regression; R's `lm` at its default tolerance drops Filip's x^10
  term. Their abstract does not say how they scored a dropped term, so the article reports both without reconciling them.
- McCullough 1998's own LRE conventions (caps, the zero floor) are known here only through Almiron et al.; the article uses
  Almiron et al.'s statement of the definition.
