# Source ledger — distributions-as-generative-stories

Series `statistics-for-data-scientists`, Part 1. Research run 2026-10-24, inline (no agents). Every
row was read at the URL given unless the Source cell says otherwise. Numbers the post calls
**measured** come from the lab (`lab/stories.py`, `captures.json`) and carry no key here; every
quoted fact, date, version and named result does.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S1 | T1 | Clarke, R. D., "An application of the Poisson distribution" (one page, read in full from the publisher's first-page image) | Journal of the Institute of Actuaries 72(3):481 | 1946 | 10.1017/S0020268100035435 | peer-reviewed | https://doi.org/10.1017/S0020268100035435 | 2026-10-24 |
| S2 | T1 | Greenwood, M. & Yule, G. U., "An inquiry into the nature of frequency distributions representative of multiple happenings with particular reference to the occurrence of multiple attacks of disease or of repeated accidents" (not read: JSTOR blocks fetchers and no open copy exists; cited for attribution, its table taken from S3 and S4) | Journal of the Royal Statistical Society 83(2):255–279 | 1920 | 10.2307/2341080 | peer-reviewed | https://doi.org/10.2307/2341080 | 2026-10-24 |
| S3 | T1 | Böhning, D., "Zero-inflated Poisson models and C.A.MAN: a tutorial collection of evidence" (author copy; Fig. 3 prints the Greenwood–Yule counts) | Biometrical Journal 40(7):833–843 | 1998 | 10.1002/(SICI)1521-4036(199811)40:7<833::AID-BIMJ833>3.0.CO;2-O | peer-reviewed | http://www.personal.soton.ac.uk/dab1f10/tutor.pdf | 2026-10-24 |
| S4 | T1 | Sah, B. K. & Sahani, S. K., "Generalised Poisson-new linear-exponential distribution" (Tables 2 and 5 print the Greenwood–Yule counts) | Mathematical Models in Engineering 10(4):241 | 2024 | 10.21595/mme.2024.24258 | peer-reviewed | https://www.extrica.com/article/24258 | 2026-10-24 |
| S5 | T1 | Bortkiewicz, L. von, *Das Gesetz der kleinen Zahlen*, Teubner, Leipzig, §11–12, pp. 22–25 (public-domain scan, University of California copy) | B. G. Teubner (book) | 1898 | 10.48520/1543508614348 | peer-reviewed | https://archive.org/details/dasgesetzderklei00bortrich | 2026-10-24 |
| S6 | T2 | `vcd` package, dataset `VonBort` (Von Bortkiewicz horse kicks, 280 rows, after Andrews & Herzberg 1985), via Rdatasets CSV and documentation | Rdatasets / R package vcd | 2026 | — | official-docs | https://vincentarelbundock.github.io/Rdatasets/doc/vcd/VonBort.html | 2026-10-24 |
| S7 | T1 | Bates, G. E. & Neyman, J., "Contributions to the theory of accident proneness. II. True or false contagion" (DTIC public-domain scan, read in full) | University of California Publications in Statistics 1(10):255–276 | 1952 | DTIC ADA311362 | peer-reviewed | https://archive.org/details/DTIC_ADA311362 | 2026-10-24 |
| S8 | T1 | Coly, S., Yao, A.-F., Abrial, D. & Charras-Garrido, M., "Distributions to model overdispersed count data" (review; §1–2 read) | Journal de la Société Française de Statistique 157(2):39–63 | 2016 | numdam JSFS_2016__157_2_39_0 | peer-reviewed | https://www.numdam.org/item/JSFS_2016__157_2_39_0/ | 2026-10-24 |
| S9 | T1 | Le Cam, L., "An approximation theorem for the Poisson binomial distribution" (§1 and Theorem 1 read) | Pacific Journal of Mathematics 10(4):1181–1197 | 1960 | 10.2140/pjm.1960.10.1181 | peer-reviewed | http://msp.org/pjm/1960/10-4/pjm-v10-n4-p11-s.pdf | 2026-10-24 |
| S10 | T1 | Clauset, A., Shalizi, C. R. & Newman, M. E. J., "Power-law distributions in empirical data" (arXiv v2, the published version) | SIAM Review 51(4):661–703 | 2009 | 10.1137/070710111; arXiv:0706.1062v2 | peer-reviewed | https://arxiv.org/abs/0706.1062 | 2026-10-24 |
| S11 | T1 | Kleiber, C. & Zeileis, A., "Visualizing count data regressions using rootograms" | The American Statistician 70(3):296–303 | 2016 | 10.1080/00031305.2016.1173590; arXiv:1605.01311 | peer-reviewed | https://arxiv.org/abs/1605.01311 | 2026-10-24 |
| S12 | T1 | Mitzenmacher, M., "A brief history of generative models for power law and lognormal distributions" (survey; author copy) | Internet Mathematics 1(2):226–251 | 2004 | 10.1080/15427951.2004.10129088 | peer-reviewed | https://www.eecs.harvard.edu/~michaelm/postscripts/im2004a.pdf | 2026-10-24 |
| S13 | T1 | Limpert, E., Stahel, W. A. & Abbt, M., "Log-normal distributions across the sciences: keys and clues" (author copy on Stahel's ETH page) | BioScience 51(5):341–352 | 2001 | 10.1641/0006-3568(2001)051[0341:LNDATS]2.0.CO;2 | peer-reviewed | https://stat.ethz.ch/~stahel/lognormal/bioscience.pdf | 2026-10-24 |
| S14 | T1 | Broido, A. D. & Clauset, A., "Scale-free networks are rare" | Nature Communications 10:1017 | 2019 | 10.1038/s41467-019-08746-5 | peer-reviewed | https://www.nature.com/articles/s41467-019-08746-5 | 2026-10-24 |
| S15 | T1 | Alstott, J., Bullmore, E. & Plenz, D., "powerlaw: a Python package for analysis of heavy-tailed distributions" (CC0) | PLoS ONE 9(1):e85777 | 2014 | 10.1371/journal.pone.0085777 | peer-reviewed | https://doi.org/10.1371/journal.pone.0085777 | 2026-10-24 |
| S16 | T1 | Gelman, A., Carlin, J. B., Stern, H. S., Dunson, D. B., Vehtari, A. & Rubin, D. B., *Bayesian Data Analysis*, 3rd ed. (authors' electronic edition, errors fixed to 2025-02-20): §2.7, §17.2, Appendix A | CRC Press (book) | 2013 | 10.1201/b16018 | peer-reviewed | http://www.stat.columbia.edu/~gelman/book/BDA3.pdf | 2026-10-24 |
| S17 | T1 | Grinstead, C. M. & Snell, J. L., *Introduction to Probability*, 2nd ed. (GNU FDL version of 2006): §5.2 | American Mathematical Society (book) | 1997 | ISBN 978-0-8218-0749-1 | peer-reviewed | https://math.dartmouth.edu/~prob/prob/prob.pdf | 2026-10-24 |
| S18 | T2 | SciPy 1.18.0 documentation, `scipy.stats.nbinom` | SciPy | 2026 | — | official-docs | https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.nbinom.html | 2026-10-24 |
| S19 | T2 | SciPy 1.18.0 documentation, `scipy.stats.t` | SciPy | 2026 | — | official-docs | https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.t.html | 2026-10-24 |
| S20 | T2 | statsmodels 0.15.0 documentation, `statsmodels.discrete.discrete_model.NegativeBinomial` | statsmodels | 2026 | — | official-docs | https://www.statsmodels.org/stable/generated/statsmodels.discrete.discrete_model.NegativeBinomial.html | 2026-10-24 |
| S21 | T2 | R 4.5.2 documentation, `dnbinom` (package stats), read with `help()` on the build machine | R Core Team | 2025 | — | official-docs | https://stat.ethz.ch/R-manual/R-patched/library/stats/html/NegBinomial.html | 2026-10-24 |
| S22 | T2 | MASS 7.3.65 documentation, `rnegbin` and `glm.nb`, read with `help()` on the build machine | CRAN package MASS | 2025 | — | official-docs | https://cran.r-project.org/package=MASS | 2026-10-24 |
| S23 | T2 | boot 1.3.32 documentation, dataset `coal` (dates of coal-mining disasters; source Hand et al. 1994, after Jarrett 1979), and the Rdatasets CSV | CRAN package boot | 2024 | — | official-docs | https://vincentarelbundock.github.io/Rdatasets/doc/boot/coal.html | 2026-10-24 |
| S24 | T2 | VGAM 1.1-13 documentation, dataset `V1` (Clarke's table, the imputed 7, and a summary of Shaw & Shaw 2019) | CRAN package VGAM | 2025 | — | official-docs | https://www.rdocumentation.org/packages/VGAM/versions/1.1-13/topics/V1 | 2026-10-24 |
| S25 | T4 | Shaw, L. P. & Shaw, L. F., "The flying bomb and the actuary" (abstract only: Wiley 403 and a Cloudflare wall on the magazine site) | Significance 16(5):12–17 | 2019 | 10.1111/j.1740-9713.2019.01315.x | practitioner | https://doi.org/10.1111/j.1740-9713.2019.01315.x | 2026-10-24 |

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | OpenAlex | title.search for the five key sources: Clarke 1946, Greenwood & Yule 1920, Clauset et al., Kleiber & Zeileis, Bortkiewicz 1898 | DOIs for all five; CSN and K&Z open on arXiv; Bortkiewicz has a digitised-book DOI; Clarke and G&Y not open; also Jäntschi 2025 (Symmetry), which turned out to be about Poisson intervals |
| 2 | 1 | Google Scholar | overdispersion count data review | Coly et al. 2016 (JSFdS, open), Barron 1992, Richards 2008; Coly taken as the survey of overdispersed count distributions |
| 3 | 1 | Google Scholar | negative binomial gamma Poisson mixture overdispersion heterogeneity review | Lloyd-Smith 2007, Xekalaki's encyclopedia entry; nothing Coly does not cover |
| 4 | 1 | Google Scholar | generative models power law lognormal distributions history | Mitzenmacher 2004 (Internet Mathematics), the survey of generative mechanisms; Montebruno et al. 2019 on firm sizes |
| 5 | 2 | Google Scholar | Le Cam inequality Poisson approximation binomial total variation | Le Cam 1960 (PJM), Hodges & Le Cam 1960, Steele 1994 (Monthly), Chen 1975 |
| 6 | 4 | Google Scholar | accident proneness contagion negative binomial cannot distinguish | Arbous & Kerrich 1951, Gurland 1959, Xekalaki 1983, Rood 1978 on the contagion/heterogeneity problem |
| 7 | 2 | Cambridge Core | DOI landing page for Clarke 1946 | a one-page note whose first-page image is the whole paper; read in full |
| 8 | 1 | Crossref | works/10.2307/2341080 | G&Y 1920 metadata: JRSS 83(2), p. 255, March 1920; no full-text link |
| 9 | 1 | archive.org | advanced search for JRSS 1920 (three queries) | volume 83 not digitised; the Digital Library of India scans start at vol. 89 (1926) |
| 10 | 1 | Google Scholar | allintitle: inquiry into the nature of frequency distributions representative of multiple happenings | a citation record only; no open copy |
| 11 | 1 | Web search | Greenwood Yule 1920 multiple happenings munition workers pdf | no copy; surfaced the Greenwood & Woods 1919 report at Wellcome |
| 12 | 1 | Wellcome Collection | catalogue works x5jsacz6 and rw2a8gj4 | Greenwood & Woods 1919 and Greenwood 1918 reports, closed stores, not digitised |
| 13 | 3 | PMC | Gurland 1959, AJPH, PMC1372954 | proof-of-work and reCAPTCHA wall; Europe PMC 403; blocked, not read |
| 14 | 3 | Google Scholar | "Greenwood and Yule" 647 women accidents shells; "Greenwood and Yule" "high explosive" shells | the table is reproduced in Böhning 1998, Sah & Sahani 2024, Cummings 2019, Shaban 1981, Sankaran 1970 |
| 15 | 3 | Author copy (Biometrical Journal) | Böhning 1998, tutor.pdf | Fig. 3 prints 447, 132, 42, 21, 3, 2; text gives the single-Poisson chi-square |
| 16 | 3 | Extrica | Sah & Sahani 2024 | Tables 2 and 5 print 447, 132, 42, 21, 3, 2 (last class 5+) with mean 0.4652241 |
| 17 | 3 | SSRN | Polson 2026, abstract 7267001 | 403, blocked |
| 18 | 2 | JSTOR | stable/2341080 | page needs JavaScript; blocked |
| 19 | 2 | archive.org | title: "gesetz der kleinen zahlen" | three public-domain scans; §11–12, pp. 22–25 read from the UC copy; the 14 x 20 table transcribed |
| 20 | 3 | Rdatasets | vcd VonBort CSV and documentation | 280 corps-years after Andrews & Herzberg 1985; agrees with our transcription in all 280 cells |
| 21 | 4 | archive.org | DTIC ADA311362 metadata and text | Bates & Neyman 1952, Part II, "True or false contagion"; read in full |
| 22 | 1 | Project Euclid | Feller 1943; Hodges & Le Cam 1960; Le Cam 1986 PDFs | Incapsula wall; blocked; Feller's point taken from Bates & Neyman and from Coly et al. |
| 23 | 2 | MSP | Pacific J. Math. 10(4), issue page and file p11 | Le Cam 1960, Theorem 1 |
| 24 | 1 | numdam | JSFS_2016__157_2_39_0 | Coly et al. 2016, read §1–2 |
| 25 | 2 | Author copy (ETH) | Stahel's lognormal page | Limpert et al. 2001, read in full |
| 26 | 1 | arXiv | 0706.1062v2 and 1605.01311 by identifier | CSN 2009 and K&Z 2016, read |
| 27 | 1 | arXiv | API: ti:"flying bomb"; ti:rootogram; abs:"power law" AND lognormal AND "log-log" | no flying-bomb preprint; K&Z; a 2026 CSN application to Bitcoin UTXO values |
| 28 | 2 | Author copy (Harvard) | Mitzenmacher 2004 | read §2, §5, §5.1, §6 |
| 29 | 4 | Nature Communications | Broido & Clauset 2019 | read; lognormal at least as good as the power law for 88% of networks |
| 30 | 5 | PLoS ONE | Alstott et al. 2014 | the powerlaw package's Fit and distribution_compare |
| 31 | 5 | SciPy and statsmodels documentation | scipy.stats.nbinom, scipy.stats.t, statsmodels NegativeBinomial | parameterisations; SciPy 1.18.0, statsmodels 0.15.0 |
| 32 | 5 | R help (local) | dnbinom; MASS rnegbin and glm.nb; boot coal | size, mu and theta conventions; coal provenance (Hand et al. 1994, Jarrett 1979) |
| 33 | 6 | Author copy (Columbia) | BDA3 electronic edition | §17.2 overdispersed models as mixtures; Appendix A on the t |
| 34 | 6 | Author copy (Dartmouth) | Grinstead & Snell, GFDL edition | §5.2 exponential, gamma and the Poisson count |
| 35 | 4 | OpenAlex | forward: cites:Clarke 1946 (74 works), and filtered by bomb, London, V-1, clustering | Shaw & Shaw 2019 (Significance), Le Comber et al. 2019 (V-2 sites), Orton 2006 (archaeology) |
| 36 | 4 | Wiley | Shaw & Shaw 2019 full text (pdfdirect, full, and the magazine site) | 403 and Cloudflare; abstract only, via OpenAlex |
| 37 | 4 | rdocumentation.org | VGAM V1 | the 7 is imputed from Clarke's total; Shaw & Shaw found hits denser in south London |
| 38 | 4 | OpenAlex | forward: cites:Greenwood & Yule 1920 filtered by proneness, contagion, heterogeneity (102 works) | Arbous & Kerrich 1951; Nagin & Paternoster 2000 restate it as heterogeneity against state dependence |
| 39 | 4 | OpenAlex | forward: cites:CSN 2009 with lognormal in the title (39 works) | the lognormal alternative recurs: river flows, magnetic storms, citation counts, a preferential-attachment paradox |
| 40 | 1 | Semantic Scholar | DOI:10.1137/070710111 | 10,044 citations, 1,133 influential; lists the year as 2007 (the arXiv date), not the 2009 venue |
| 41 | 3 | Rdatasets | boot coal CSV | 191 dates from 1851 to 1962 |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | Clarke studied 144 square kilometres of south London cut into 576 squares of a quarter square kilometre; 537 flying bombs fell in the area over the period | S1 | his selected area and period only |
| L02 | Clarke chose the area because the expected density of hits was very nearly constant across it | S1 | stated by Clarke as the reason for the choice |
| L03 | Clarke wrote because people repeatedly asserted during the attack that impacts were grouped in clusters | S1 | — |
| L04 | Observed squares with 0, 1, 2, 3, 4 and 5-or-more hits: 229, 211, 93, 35, 7, 1; Poisson expectation with m = 537/576: 226.74, 211.39, 98.54, 30.62, 7.14, 1.57 | S1 | Clarke's table |
| L05 | Clarke's chi-square was 1.17 on 4 degrees of freedom with P = 0.88; he read the fit as giving no support to clustering | S1 | — |
| L06 | Clustering would have shown too many squares with many hits and with none, and too few in between | S1 | Clarke's own statement of the alternative |
| L07 | Clarke was an actuary (F.I.A.) at the Prudential Assurance Company | S1 | — |
| L08 | The 5-or-more square holds 7 hits, imputed from Clarke's total of 537 | S1, S24 | arithmetic on Clarke's table; VGAM documents the imputation |
| L09 | Shaw and Shaw (2019) found hits denser in south London than across the wider region, so the density was not uniform over the whole area attacked | S24, S25 | read through VGAM's summary and the abstract; the full text was not reachable |
| L10 | Bortkiewicz tabulated deaths by horse kick in 14 Prussian army corps (the Guard, I to XI, XIV, XV) over 1875 to 1894 | S5 p. 24 | — |
| L11 | Bortkiewicz's famous 200 corps-years exclude the Guard and corps I, VI and XI, whose composition deviated from the norm (the Guard 134 infantry companies and 40 cavalry squadrons, XI three divisions, I 30 and VI 25 squadrons against a norm of 20) | S5 p. 24 and footnote | his stated reason |
| L12 | For the 200 corps-years: 109, 65, 22, 3, 1 corps-years with 0 to 4 deaths, against his expected 108.7, 66.3, 20.2, 4.1, 0.6 and 0.1 for 5 or more | S5 p. 25 | — |
| L13 | For all 280 corps-years: 144, 91, 32, 11, 2 with 0 to 4 deaths | S5 p. 24 | his frequency table; variance and mean computed by us |
| L14 | Bortkiewicz judged the agreement of theory with experience to leave nothing to be desired in both cases | S5 p. 25 | — |
| L15 | The vcd VonBort data (after Andrews & Herzberg 1985) match our transcription of the 1898 table in all 280 cells | S6 | — |
| L16 | Greenwood and Yule's table: 647 women working on high-explosive shells over five weeks had 447, 132, 42, 21, 3 and 2 accidents for 0 to 5 | S2, S3 Fig. 3, S4 Table 2 | the original was not read; two independent reproductions agree |
| L17 | Greenwood and Yule (1920) were the first to combine the Poisson with another distribution as a mixture | S8 §1 | as stated by the review |
| L18 | Greenwood and Yule (rates that vary between people, "false" contagion) and Eggenberger and Pólya (1923, true contagion) reached the same distribution, a Poisson mixed with a Pearson type III (gamma) | S8 §1–2 | — |
| L19 | Feller pointed out that the two routes give the same distribution; Gurland concluded that true and false contagion cannot always be told apart from the data alone | S8 §1–2 | via the review; Feller 1943 not read |
| L20 | The Greenwood–Yule–Newbold scheme assumes people differ in proneness, past accidents do not change future chances, and chances are constant in time | S7 §1 | — |
| L21 | For one period of observation, the proneness mixture and Pólya's contagion scheme give the same negative binomial (Lundberg 1940, Feller), so the two are indistinguishable | S7 §1 and eq. (74)ff | contagion model with all individuals starting from the same count |
| L22 | With two or more consecutive periods the joint distributions differ, so the models can be told apart except in one exceptional parameter case | S7 §8 | — |
| L23 | The negative binomial also arises as a Poisson number of clusters with logarithmically distributed sizes | S8 §2 | — |
| L24 | Negative binomial parameters can be estimated from the mean and the variance-to-mean ratio; mean-and-variance estimators lose efficiency in some regions of the parameter space (Anscombe 1950) | S8 §2 | — |
| L25 | The negative binomial is a Poisson whose mean is gamma distributed; its variance always exceeds its mean, and it tends to the Poisson as the gamma concentrates | S16 §2.7, §17.2 | — |
| L26 | The t distribution is a normal whose variance is drawn from a scaled inverse-chi-square (inverse-gamma) distribution | S16 §17.2, App. A | — |
| L27 | These overdispersed mixture versions can never be underdispersed: same mean, higher variance | S16 §17.2 | — |
| L28 | In a Poisson process the gaps are exponential and memoryless, the sum of n gaps has a gamma density with parameters lambda and n, and the count in an interval is Poisson | S17 §5.2 | constant rate, independent gaps |
| L29 | Le Cam's Theorem 1: the summed absolute difference between the Poisson-binomial and the Poisson with the same mean is at most twice the sum of the squared probabilities | S9 Theorem 1 | independent trials |
| L30 | Many small independent effects give a normal when they add and a lognormal when they multiply (the multiplicative central limit theorem); Galton's board shows the first, Kapteyn's 1903 machine the second | S13 | effects small and independent |
| L31 | Gibrat's law of proportionate effect is a multiplicative process; the central limit theorem on the logs makes its outcome approximately lognormal; McAlister described the lognormal in 1879 | S12 §5 | log factors i.i.d. with finite variance |
| L32 | A lognormal has finite mean and variance, yet its CCDF on log–log axes can look nearly straight over several orders of magnitude when sigma is large | S12 §2 | — |
| L33 | Adding a lower reflecting barrier to a multiplicative process turns the lognormal into a power law; Champernowne's example (halve with probability 2/3, double with probability 1/3, a minimum income m) gives Pr[X at least x] = m/x | S12 §5.1 | equilibrium |
| L34 | Least-squares fits to log–log histograms give substantially inaccurate exponents and say nothing about whether the data follow a power law; the practice goes back to Pareto | S10 abstract, §3 | — |
| L35 | Looking roughly straight on a log–log plot is necessary but not sufficient for a power law; samples of 100 from a power law, a lognormal and an exponential all look straight in CSN's Fig. 4.1a | S10 §4 | — |
| L36 | CSN's recipe: fit alpha by maximum likelihood with xmin chosen to minimise the Kolmogorov–Smirnov distance; a bootstrap goodness-of-fit p-value rejects the power law at p of 0.1 or less; likelihood-ratio tests compare alternatives | S10 Box 1, §3–5 | — |
| L37 | Of CSN's 24 data sets, the lognormal was ruled out only for HTTP connections; telling lognormal from power law is extremely hard, and when tests are inconclusive one must look for a mechanistic argument | S10 §6 | — |
| L38 | Across nearly 1,000 networks the lognormal fit at least as well as the power law for 88%, and only 4% met the strongest scale-free criteria | S14 | their evidence categories |
| L39 | Even a clearly identified distribution is weak evidence for telling generating mechanisms apart | S14 introduction | — |
| L40 | The powerlaw package's Fit picks xmin by the minimum Kolmogorov–Smirnov distance, and distribution_compare runs the likelihood-ratio comparison | S15 | — |
| L41 | A rootogram draws observed counts as bars and expected counts as a curve on a square-root scale; the hanging form hangs each bar from the expected curve so deviations line up on the axis; Kleiber and Zeileis recommend it as the default, and Tukey's warning limits sit at plus and minus 1 | S11 §2.1, §5 | — |
| L42 | SciPy's nbinom(n, p) counts failures before n successes; with mean mu, p = n/(n+mu); with variance mu + alpha mu^2, p = mu/sigma^2 and n = mu^2/(sigma^2 − mu) | S18 Notes | SciPy 1.18.0 |
| L43 | SciPy's t is the standardised t with df degrees of freedom; loc and scale shift and scale it | S19 Notes | SciPy 1.18.0 |
| L44 | statsmodels' NegativeBinomial with loglike_method nb2 has variance mu + alpha mu^2 | S20 | statsmodels 0.15.0 |
| L45 | R's dnbinom takes size (the gamma mixing shape) and mu, with prob = size/(size+mu) and variance mu + mu^2/size | S21 Details | R 4.5.2 |
| L46 | MASS's rnegbin and glm.nb call the same parameter theta: variance mu + mu^2/theta | S22 | MASS 7.3.65 |
| L47 | The coal data are the dates of 191 explosions in British coal mines that killed ten or more, from 15 March 1851 to 22 March 1962 (Hand et al. 1994, after Jarrett 1979) | S23 | — |
| L48 | Most studies claiming power laws relied on visual appraisal rather than a quantitative test | S10 §4 | as surveyed by CSN |
| L49 | Clarke's flying bombs were V-1s, fired at London during the summer of 1944 | S24, S25 | VGAM's documentation of Clarke's data, and the Shaws' abstract; Clarke's note says only "the flying-bomb attack on London" |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S10 | Fig. 4.1a | log–log trap / L35 | shows three different families all looking straight | SIAM copyright; arXiv non-exclusive licence only | https://arxiv.org/abs/0706.1062 | do not reuse; our own figure draws the same point from the lab |
| F2 | S11 | Fig. 1 | rootogram styles / L41 | defines standing, hanging and suspended rootograms | ASA / Taylor & Francis copyright; arXiv non-exclusive licence only | https://arxiv.org/abs/1605.01311 | do not reuse; our rootograms are drawn from the lab |
| F3 | S13 | Fig. 2 | sums and products / L30 | Galton's board beside Kapteyn's multiplicative machine | AIBS copyright; author copy only | https://stat.ethz.ch/~stahel/lognormal/bioscience.pdf | do not reuse; our figure simulates both from the same effects |
| F4 | S5 | p. 24 table | Bortkiewicz's selection / L11 | the corps-by-year grid with the footnote that drops four corps | public domain (1898) | https://archive.org/details/dasgesetzderklei00bortrich | not needed: German typesetting; our figure plots the same counts against the Poisson |
| F5 | S3 | Fig. 3 | Greenwood–Yule counts / L16 | observed counts against two fits | Wiley copyright | http://www.personal.soton.ac.uk/dab1f10/tutor.pdf | do not reuse; our rootogram shows the same counts |
| F6 | S14 | Fig. 4 | log–log trap / L38 | evidence categories across networks | CC BY 4.0 | https://www.nature.com/articles/s41467-019-08746-5 | not needed: one number carries the point |

## Open questions

- Greenwood and Yule's 1920 paper was not read (JSTOR blocks fetchers; no open copy, no
  digitised volume 83). The counts come from two independent printed reproductions (S3, S4) and
  agree with Cummings' (2019) total of 301 accidents among 647 women. The post does not quote G&Y's
  own fitted values or conclusions.
- Bortkiewicz's expected values for all 280 corps-years (143.1, 92.1, 33.3, 8.9, 2.0, 0.6) sit far
  closer to a per-corps Poisson mixture (143.5, 91.7, 33.2, 9.0, 2.1, 0.5) than to a single
  Poisson(0.70) (139.0, 97.3, 34.1, 8.0, 1.4, 0.2), and his effective dispersion 0.73 equals the
  within-corps variance 0.728. His §5 formulas were not decoded, so the post does not describe his
  method for that case.
- Shaw and Shaw (2019) was read only through its abstract and VGAM's summary; the post states only
  the denser-in-south-London finding.
- Feller (1943) was not read (Project Euclid wall). The identifiability point rests on Bates and
  Neyman (1952) and Coly et al. (2016), which both attribute it to Lundberg and Feller.
- Böhning's single-Poisson chi-square of 115.35 on 4 df was not reproduced (our six-cell value with
  5 pooled into the last class is 103.1); the grouping and estimate behind his value are not
  stated. The post quotes neither.
- The coal-mining rate change is read off the data (123 explosions before 1 January 1890, 68 from
  then to 1962); the post attributes no cause to it.
