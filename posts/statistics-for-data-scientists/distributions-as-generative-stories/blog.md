---
title: "Distributions as Generative Stories: Let the Process Pick"
slug: distributions-as-generative-stories
date: 2026-10-24
updated: 2026-10-24
summary: "Pick a distribution from the process behind your data, not the histogram: rare independent events give a Poisson, rates that differ a negative binomial."
tags: [data-science, statistics, probability-distributions, poisson-distribution, negative-binomial, overdispersion, power-law]
category: data-science
series: statistics-for-data-scientists
series_position: 1
tier: L3
difficulty: intermediate
prerequisites: ["expectation and variance", "random variables", "Python with NumPy"]
reading_minutes: 28
cover_image: "COVER"
canonical_url: "https://canery.in/blogs/distributions-as-generative-stories"
---

![Bars of 647 women's accident counts on a square-root scale, with a dashed Poisson curve and a tangerine negative binomial curve](COVER)

> [!NOTE]
> **Insights** — Choose a probability distribution by writing down the process that made your numbers, then let the data test that story; the shape of a histogram cannot choose it for you. Bombs falling independently on 576 squares of south London make Poisson counts, and R. D. Clarke's 1946 tally matched the Poisson to within a few squares in every class. <!-- L04 --> Give each worker her own accident rate, drawn from a gamma distribution, and the counts become negative binomial with variance μ + μ²/k, which is how that story explains a variance 1.49 times the mean in Greenwood and Yule's 647 munition workers. <!-- L16 --> And shape hides tails: a Student t with 5 degrees of freedom, scaled to variance 1, puts 56 times the normal's probability beyond four standard deviations.

**Level:** intermediate · **You need:** expectation and variance, random variables, Python with NumPy · **Time:** ~28 min

**Jump to:** [worked example](#worked-example) · [waiting times, sums and products](#what-do-waiting-times-sums-and-products-produce) · [accident counts](#why-do-accident-counts-break-the-poisson) · [tails](#what-cant-a-histogram-show) · [log–log plots](#is-a-straight-line-on-a-loglog-plot-a-power-law) · [math](#the-math) · [implementation](#implementation) · [mistakes](#limitations-and-common-mistakes)

> [!IMPORTANT]
> Numbers this post calls **measured** come from its lab, a NumPy and SciPy script that runs in under ten seconds. Every simulated number carries its Monte Carlo standard error (MCSE), the standard deviation of a simulation's own estimate, and its number of replications R. The historical counts are **quoted** from their papers; the expected counts beside them are computed from those counts.

## Why this matters

Suppose you count support tickets per customer and fit a Poisson model, because counts are "Poisson data". If the variance is really 1.49 times the mean, as it was for Greenwood and Yule's munition workers, every standard error the Poisson model reports is too small by a factor of √1.49 = 1.22, and tests built on those errors reject too often. Or you fit a normal to daily returns because the histogram is bell-shaped. If the data behave like a unit-variance t with 5 degrees of freedom, a move beyond four standard deviations is 56 times likelier than your model says. The family you pick sets the variance, the tail and what the parameters mean, and the evidence most often used to pick it is the weakest evidence you have.

## The problem

You have n numbers: hits per square, accidents per worker, days between events. You want a **probability distribution**, a rule that gives each possible value its probability. Choosing one means choosing a **family**, such as the Poisson or the normal, which is a set of distributions indexed by parameters, and then the parameters. The parameters are the easy half; this series fits them properly later. The family is the hard half.

The common route is to plot a histogram and pick the family whose shape matches, or to fit several families and keep the best goodness-of-fit score. Three facts break that route.

1. **Families agree where data are dense and differ where data are sparse.** A unit-variance t₅ and a normal differ 56-fold beyond four standard deviations. Yet in samples of 100, 69.3% ± 0.3% of t₅ samples hold no point beyond 4 at all (R = 20,000, measured), so the tail that matters never appears.
2. **A fit can reject a family but rarely confirms one.** The negative binomial arises from at least three different processes: rates that differ between people, accidents that raise the chance of the next one, and clusters of random size. <!-- L18 --> <!-- L23 --> A good fit cannot say which one made your data.
3. **A fitted family says nothing about mechanism.** The mechanism tells you which parameter to estimate and what it means, and whether the next period will look like this one.

The data under-determine the family in exactly the places that matter. The missing information is in how the numbers were made. A **generative story** is a step-by-step account of how one observation came to be, precise enough to simulate. "Each of 537 bombs falls in one of 576 equal squares, independently of the others" is a generative story; "the counts look Poisson" is not. The method of this post is to derive the family from the story, then test the story's predictions on the data. Figure 1 maps the stories it derives and the operation that turns each one into the next.

![Map of generative stories: Bernoulli to binomial to Poisson, gaps to exponential and gamma, effects to normal and lognormal, mixtures](FIG_01)
*Figure 1. Each arrow is an operation on a story. The three tangerine moves change one rule: a rate that varies, a variance that varies, or a floor under growth.*

## Worked example

During the V-1 flying-bomb attack on London in the summer of 1944, <!-- L49 --> people repeatedly asserted that the impacts fell in clusters. <!-- L03 --> R. D. Clarke, an actuary at the Prudential Assurance Company, set out to test the claim. <!-- L07 --> He took 144 square kilometres of south London, cut it into 576 squares of a quarter square kilometre each, and counted the 537 bombs that fell in the area over the period studied. <!-- L01 --> He chose the area because the expected density of hits was very nearly constant across it. <!-- L02 -->

**The story.** Each bomb lands in exactly one square, every square is equally likely, and each bomb lands independently of the others. Now look at one square. Each bomb is a **Bernoulli trial** for it, a yes-or-no event with probability p = 1/576. The square's count is the number of successes in n = 537 independent trials with a common p, which is the **binomial distribution**, Binomial(537, 1/576). The chance that a square stays empty is (575/576)⁵³⁷ = 0.39333, so the binomial expects 576 × 0.39333 = 226.56 empty squares.

**The limit.** When n is large and p is small with np held at λ, the binomial approaches the **Poisson distribution**, P(k) = e^(−λ) λᵏ / k!. Here λ = 537/576 = 0.9323. The Poisson gives P(0) = e^(−0.9323) = 0.39365, P(1) = 0.36700, P(2) = 0.17107, P(3) = 0.05316 and P(4) = 0.01239, leaving 0.00272 for five or more. Multiply by 576 and compare:

| Hits per square | 0 | 1 | 2 | 3 | 4 | 5 or more |
|---|---|---|---|---|---|---|
| Observed squares | 229 | 211 | 93 | 35 | 7 | 1 |
| Binomial, expected | 226.56 | 211.59 | 98.62 | 30.59 | 7.10 | 1.55 |
| Poisson, expected | 226.74 | 211.39 | 98.54 | 30.62 | 7.14 | 1.57 |

The Poisson row is Clarke's printed table, digit for digit. <!-- L04 --> The single square in the last class holds the remaining 7 bombs, a number implied by the total of 537 rather than printed. <!-- L08 -->

**How rare is rare?** The binomial and Poisson rows differ by at most 0.20 squares in any class and by 0.55 squares in all. The **total variation distance**, half the summed absolute difference between two probability tables, is 4.8 × 10⁻⁴ (measured). Le Cam's inequality bounds the summed absolute difference by twice the sum of the squared trial probabilities, <!-- L29 --> which puts the total variation distance at most 537/576² = 1.6 × 10⁻³. Each bomb contributes the square of a small chance, which is why a Poisson needs rare events.

**The story's sharpest prediction** is that the variance equals the mean. Clarke's squares have mean 0.9323 and variance 0.9711, with divisor n − 1. Their ratio, the **dispersion index**, is 1.04. Clustering would have pushed it well above 1, with too many crowded squares and too many empty ones and too few in between. <!-- L06 --> Clarke's own chi-square test gave 1.17 on 4 degrees of freedom with P = 0.88, and he found no support for clustering. <!-- L05 --> What a P value means is the subject of a later part of this series; here, read it as "deviations of the size chance alone produces".

Figure 2 draws the comparison as a **hanging rootogram**: each class's observed count is a bar on a square-root scale, hung from the model's expected count, so a perfect fit leaves every bar ending on the zero line. <!-- L41 --> The square root keeps small classes visible next to large ones, and Tukey's warning limits at ±1 mark deviations that chance easily explains.

![Hanging rootograms of Clarke's 576 squares and Bortkiewicz's 200 corps-years against the Poisson; every bar ends inside ±1](FIG_02)
*Figure 2. Every bar ends inside Tukey's ±1 band in both tallies. The Poisson rate in each panel is the sample mean, and nothing else was fitted.*

The right panel comes from 1898, when Ladislaus von Bortkiewicz tabulated deaths by horse kick in 14 corps of the Prussian army from 1875 to 1894. <!-- L10 --> His well-known 200 corps-years show 109, 65, 22, 3 and 1 corps-years with 0 to 4 deaths, against expected values of 108.7, 66.3, 20.2, 4.1 and 0.6. <!-- L12 --> The mean is 0.61 and the variance 0.611, a ratio of 1.002 (measured). Bortkiewicz judged that the agreement left nothing to be desired. <!-- L14 -->

Read his footnote, though. The 200 corps-years exclude the Guard and corps I, VI and XI, whose make-up deviated from the norm: the Guard had 40 cavalry squadrons, XI had three divisions, and I and VI had 30 and 25 squadrons, against a norm of 20. <!-- L11 --> All 14 corps, 280 corps-years, give 144, 91, 32, 11 and 2 <!-- L13 --> with mean 0.70 and variance 0.763, a ratio of 1.09 (measured). Both classic tables met the Poisson's condition, one common rate, partly by selection. Clarke chose an area of nearly constant density, and a 2019 re-analysis by Liam and Luke Shaw found hits denser in south London than across the wider region. <!-- L09 --> Bortkiewicz set aside the corps whose make-up differed.

## Intuition

The process picks the family because the family is just the arithmetic of the process. A count built from many independent chances, each of them small, is Poisson whatever it counts: bombs, kicks, typos per page. The data cannot tell you that; they can only test what the story predicts, and the Poisson predicts two things you can check: variance equal to the mean, and an expected count for every class.

Think of rain on a paved square. Each slab collects drops independently, so drops per slab are Poisson. The analogy breaks exactly where the story breaks: a gutter that drips onto some slabs gives them a higher rate, and a gust that throws drops in sheets makes them arrive together. Both push the variance above the mean, and the accident data below show that they can produce the same counts.

That is the asymmetry this post keeps returning to. Every arrow in Figure 1 is a derivation that runs one way, from story to family. Going back from a family to its story is not unique: the map reaches the negative binomial through rates that vary between people, but contagion and clusters of random size reach it too, and neither appears on the map.

## What do waiting times, sums and products produce?

### Waiting times

A **Poisson process** is the bomb story laid out in time: events arrive at a constant rate λ, independently in disjoint intervals. Its gaps follow the **exponential distribution**, which is memoryless: having waited does not shorten the wait that remains. The wait for the k-th event is the sum of k gaps, a **gamma distribution** with shape k and rate λ, and the count in an interval of length t is Poisson with mean λt. <!-- L28 --> The lab builds a process from exponential gaps alone at rate 3 and recovers Poisson(3) counts in a unit interval, with a total variation distance of 0.0036 at R = 100,000. The wait for the third event averages 0.9999 ± 0.0018 against the gamma's 1.

The story makes a testable prediction about gaps. Their **coefficient of variation (CV)**, the standard deviation divided by the mean, is exactly 1 for an exponential. A real record makes a fair test: the 191 explosions in British coal mines that killed ten or more people between 15 March 1851 and 22 March 1962. <!-- L47 --> The 190 gaps average 213 days with a CV of 1.47. No simulated record of 190 exponential gaps reached that CV in R = 10,000 tries; the largest was 1.36 (measured).

![Coal explosions 1851 to 1962: the cumulative count bends near 1890, and pooled gaps run longer than an exponential predicts](FIG_03)
*Figure 3. One constant rate would draw the dashed straight line on the left. The record has two rates, and pooled gaps are too often long.*

Figure 3 shows why. There were 123 explosions before 1890, about 3.2 a year, and 68 from 1890 to 1962, about 0.94 a year. Within 1851–1889 the gaps have a CV of 1.06, a value that 18.8% ± 0.4% of simulated exponential records of the same length reach. The exponential's condition, one constant rate, held within the first era and failed across the whole record. Mixing exponentials with different rates produces too many long gaps, the same move that will turn Poisson counts into negative binomial ones below.

### Sums and products

The **normal distribution** has its own story: many small independent effects that add. The **central limit theorem (CLT)** says such sums tend to the normal provided no single effect dominates; Galton's board of pins, where each ball is knocked left or right at every row, is the classic demonstration. <!-- L30 --> Multiply the same effects instead and you get the **lognormal distribution**, because the log of a product is a sum of logs, and that sum goes normal. <!-- L30 --> This is Gibrat's law of proportionate effect: growth in proportion to current size, as in the growth of organisms and of incomes. <!-- L31 -->

![Histograms of the same twelve random effects added, multiplied and logged: symmetric sum, right-skewed product, symmetric log](FIG_04)
*Figure 4. One set of draws, three combination rules. Only the rule changed between the left and middle panels.*

In Figure 4 each simulated outcome draws twelve effects between 0.5 and 1.5. Added, they give a symmetric bell with skewness 0.003. Multiplied, the same draws give skewness 4.16, a median of 0.59 against a mean of 1.00, and 69% of outcomes below their mean. The log of the product has skewness −0.11, back to symmetric. The combination rule, add or multiply, decided the family; the effects were identical.

## Why do accident counts break the Poisson?

Greenwood and Yule's most famous table counts accidents to 647 women working on high-explosive shells over five weeks: 447 had none, 132 had one, 42 had two, 21 had three, 3 had four and 2 had five. <!-- L16 --> The mean is 0.4652 and the variance 0.6919, a dispersion index of 1.49. A Poisson with every woman at rate 0.4652 expects 406 women with no accident (447 were observed), 189 with one (132), 6.8 with three (21) and 0.9 with four or more (5). It has too many at both ends and too few in the middle, the signature Clarke looked for in his squares and did not find.

**The story: proneness.** Give each woman i her own accident rate λᵢ, so her count given that rate is Poisson(λᵢ). Across women the rates follow a gamma distribution with shape k and mean μ. The story assumes that an accident does not change a woman's later chances and that her chances stay constant through the period. <!-- L20 --> Greenwood and Yule were the first to combine the Poisson with another distribution this way. <!-- L17 --> Average the Poisson over the gamma and the result is the **negative binomial distribution** with mean μ and variance μ + μ²/k. <!-- L25 --> Variance above the Poisson's is called **overdispersion**. The **law of total variance** splits it in two: Var Y = E[Var(Y | λ)] + Var(E[Y | λ]), which is μ, each woman's own Poisson noise, plus μ²/k, how much the rates differ. Under this story the excess 0.227 is the spread of the rates itself, not noise on top of a Poisson.

**Fitting by moments.** The **method of moments** sets the model's moments equal to the sample's; maximum likelihood comes later in this series. Solve 0.6919 = 0.4652 + 0.4652²/k to get k = 0.955. <!-- L24 --> The negative binomial then expects 442.9, 138.5, 44.4, 14.3, 4.6 and 2.2 women, and the chi-square falls from 103.1 for the Poisson to 4.20. The top classes expect fewer than one woman under the Poisson, so read those chi-squares as measures of discrepancy, not as P values.

![Rootograms of Greenwood and Yule's accident counts: the Poisson misses three classes beyond ±1, the negative binomial none](FIG_05)
*Figure 5. The Poisson leaves bars beyond ±1 at one, three and five-plus accidents; the moment-fitted negative binomial leaves none.*

Figure 6 reads the fitted gamma back as a statement about the 647 women. The median rate is 0.32 accidents per five weeks, below the mean of 0.465, so 63.5% of women sit below the mean rate. The most accident-prone 20%, with rates above 0.75, carry 53% of the expected accidents. A simulation of the story, with R = 20,000 factories of 647 women, measures the two parts of the variance as 0.4650 ± 0.0001 and 0.2264 ± 0.0002, against 0.4652 and 0.2267 from the formula.

![Gamma density of the women's accident rates with the top 20% shaded, and the variance split into 0.465 Poisson and 0.227 spread](FIG_06)
*Figure 6. Most women have low rates and a few have high ones. The tangerine block is the part of the variance a Poisson cannot produce.*

### What the counts cannot tell you

Eggenberger and Pólya reached the same distribution in 1923 from the opposite story: every person starts alike, and each accident raises the chance of the next. This is **contagion**, the "true" kind; differences between people that only imitate it, like proneness, are "false" contagion. <!-- L18 --> For one period of observation the two stories give the same negative binomial, as Lundberg and Feller showed. <!-- L21 --> The lab checks it with a contagion process in which every woman starts at a rate of 0.379 per five weeks and each accident adds 0.397. Its first-period counts are 442.8, 138.5, 44.5, 14.4, 4.7 and 2.2 (R = 10,000), the negative binomial's numbers to within simulation error.

Watch the same women for a second five weeks and the stories part. Contagion raises the expected count to 0.691 ± 0.0004, against an exact 0.692, because accidents have accumulated; proneness keeps it at 0.4653 ± 0.0002. Observations over two or more periods separate the models except in one exceptional case. <!-- L22 --> Greenwood and Yule's single table shows that the women's chances were not all equal. It cannot show which story made them unequal; Gurland reached the same conclusion, that true and false contagion cannot always be told apart from the data alone. <!-- L19 -->

## What can't a histogram show?

The **Student t distribution** has a story that mirrors the gamma–Poisson one: a normal whose variance is itself random, drawn from a scaled inverse-chi-square distribution. <!-- L26 --> Variation in the scale fattens the tails, as variation in the rate fattened the counts. A t with ν degrees of freedom has variance ν/(ν − 2), 5/3 for ν = 5, so dividing by √(5/3) gives a **unit-variance t₅** with the same mean and variance as the standard normal.

![Unit-variance t5 and normal densities differ visibly only at the peak; on a log scale the t5 tail is 4.3, 56 and 2,316 times higher](FIG_07)
*Figure 7. On a linear scale the only visible difference is a taller peak. On a log scale the tails separate by orders of magnitude.*

Figure 7 sets the two side by side. On a linear scale the t₅ is a slightly taller bell, peaking at 0.490 against the normal's 0.399, and beyond 4 both curves sit within a pixel of the axis. On a log scale the tails part: the t₅ is 4.3 times likelier beyond 3 standard deviations, 56.4 times beyond 4 (0.357% against 0.0063%) and 2,316 times beyond 5.

What does a sample show? In R = 20,000 samples of 1,000, 97.2% ± 0.1% of t₅ samples hold a point beyond 4, against 6.0% ± 0.2% of normal samples. At 100 points, 69.3% ± 0.3% of t₅ samples show nothing beyond 4 (exactly 69.9%). A **Q–Q plot**, which draws a sample's sorted values against a family's quantiles, makes the tails visible when they are there: a straight line means the family fits, and ends that bend away mean heavier or lighter tails.

![Q–Q plots of 1,000 normal and 1,000 unit-variance t5 draws against normal quantiles; the t5 points bend away at both ends](FIG_08)
*Figure 8. The same variance, the same mean, and a visible difference only at the ends, where a histogram's bars are nearly empty.*

## Is a straight line on a log–log plot a power law?

A **power law** has a **complementary cumulative distribution function (CCDF)**, P(X ≥ x), proportional to x^(−α) above some threshold, so its CCDF is a straight line of slope −α on log–log axes. The circulating claim runs the implication backwards: draw the CCDF, see a straight line, declare a power law. Most published power-law claims rested on that kind of visual appraisal rather than on a test, <!-- L48 --> often a least-squares slope fitted to a log–log histogram, a practice that goes back to Pareto and gives substantially inaccurate exponents. <!-- L34 -->

![A lognormal sample's survival curve on log–log axes: the top 10% fits a straight line with R² 0.991 while the full curve bends](FIG_09)
*Figure 9. Inside the shaded window the lognormal looks like a power law. Outside it, the same curve bends away.*

Figure 9 shows why the backward step fails. The lab draws 10,000 values from a lognormal with σ = 2.5. Its top 10% span 2.52 decades, and a least-squares line through them has slope −0.918 with R² = 0.991; over R = 1,000 such samples, R² is at least 0.98 in 91.4% ± 0.9% of them. Read as a power law, an exponent of 0.92 means an infinite mean. The lognormal that drew the sample has mean e^(σ²/2) = 22.8. A lognormal's log-density is quadratic in log x, and with a large σ the curve bends so slowly that it looks straight for several orders of magnitude. <!-- L32 --> Clauset, Shalizi and Newman show the same with samples of 100 from a power law, a lognormal and an exponential, all of which look roughly straight. <!-- L35 -->

What actually decides is a procedure. It fits α by maximum likelihood with the threshold chosen to minimise the Kolmogorov–Smirnov distance, rejects the power law when a bootstrap goodness-of-fit p is 0.1 or less, and compares alternatives with likelihood-ratio tests. <!-- L36 --> The Python `powerlaw` package implements it; <!-- L40 --> this series makes it runnable once likelihood arrives. Even done properly, the answer is often "cannot tell". Among the authors' 24 data sets the lognormal was ruled out only once, and they advise looking for a mechanism when tests cannot decide. <!-- L37 --> Across nearly 1,000 networks, a later study found the lognormal fit at least as well as the power law for 88%, and only 4% met its strongest scale-free criteria. <!-- L38 -->

![Champernowne's walk on log–log axes: with a floor the tail is a straight line of slope −1, without one it curves down](FIG_10)
*Figure 10. Same steps, one extra rule. The floor, not the plot, decides between a power law and a lognormal.*

The mechanism is where the process earns its place. Figure 10 runs Champernowne's model of incomes: each step doubles a person's income with probability 1/3 and halves it with probability 2/3. With a floor that income cannot fall below, the equilibrium is a power law: P(X ≥ x) = 1/x at every power of 2. <!-- L33 --> Without the floor, the same steps make an approximately lognormal income, by the CLT on the logs. One rule about the lower boundary decides the family, and no log–log plot can see that rule. Even a distribution identified cleanly is weak evidence about which mechanism produced it. <!-- L39 -->

## The math

| Symbol | Meaning | Units |
|---|---|---|
| $n$, $p$ | number of Bernoulli trials and their common success probability | count, probability |
| $\lambda$ | Poisson mean, or a rate per unit of exposure | events |
| $\mu$, $k$ | negative binomial mean and dispersion: $\operatorname{Var} = \mu + \mu^2/k$ | events, dimensionless |
| $\bar x$, $s^2$ | sample mean and sample variance (divisor $n - 1$) | units of the data |
| $\nu$ | degrees of freedom of a Student t | dimensionless |
| $\sigma$ | standard deviation of $\ln X$ for a lognormal | log units |

**The rare-event limit.** For a count $S$ of $n$ independent trials with probabilities $p_j$:

$$
P(S = k) = \binom{n}{k} p^k (1-p)^{n-k} \;\longrightarrow\; e^{-\lambda}\frac{\lambda^k}{k!} \qquad (n \to \infty,\ p \to 0,\ np = \lambda) \tag{1}
$$

The binomial becomes the Poisson when the trials are many, each chance is small, and their total stays fixed. Le Cam's inequality says how close it already is at finite $n$: <!-- L29 -->

$$
\sum_{k} \left\lvert P(S = k) - e^{-\lambda}\frac{\lambda^k}{k!} \right\rvert \;\le\; 2 \sum_{j} p_j^2 \tag{2}
$$

The error is governed by the squared chances, so halving every $p_j$ while doubling $n$ halves the bound. For Clarke, $\sum_j p_j^2 = 537/576^2 = 0.0016$.

**The gamma–Poisson mixture.** Draw a rate from a gamma with shape $k$ and mean $\mu$, then a Poisson count at that rate:

$$
P(Y = y) = \int_0^\infty e^{-\lambda}\frac{\lambda^y}{y!} \cdot \frac{(k/\mu)^k \lambda^{k-1} e^{-k\lambda/\mu}}{\Gamma(k)}\, d\lambda = \frac{\Gamma(y + k)}{\Gamma(k)\, y!} \left(\frac{k}{k + \mu}\right)^{k} \left(\frac{\mu}{k + \mu}\right)^{y} \tag{3}
$$

Integrating the rate out leaves a negative binomial whose probabilities depend only on the mean and on how spread out the rates were. <!-- L25 --> Its variance comes from the law of total variance:

$$
\operatorname{Var} Y = \operatorname{E}\left[\operatorname{Var}(Y \mid \lambda)\right] + \operatorname{Var}\left(\operatorname{E}[Y \mid \lambda]\right) = \mu + \frac{\mu^2}{k} \tag{4}
$$

The first term is Poisson noise and the second is the variance of the rates, $\mu^2/k$ for a gamma with mean $\mu$ and shape $k$. As $k \to \infty$ the rates stop varying and the Poisson returns. Setting $s^2 = \bar x + \bar x^2/k$ gives the moment estimator:

$$
\hat k = \frac{\bar x^{2}}{s^{2} - \bar x} = \frac{0.4652^2}{0.6919 - 0.4652} = 0.955 \tag{5}
$$

It needs $s^2 \gt \bar x$; with no overdispersion there is nothing for $k$ to measure. Each library names $k$ differently, which is where fits go wrong:

| Library | Call | Relation to $(\mu, k)$ |
|---|---|---|
| SciPy 1.18 | `scipy.stats.nbinom(n, p)` | $n = k$, $p = k/(k + \mu)$, the success probability <!-- L42 --> |
| statsmodels 0.15 | `NegativeBinomial(..., loglike_method="nb2")` | $\alpha = 1/k$, variance $\mu + \alpha\mu^2$ <!-- L44 --> |
| R 4.5 | `dnbinom(x, size, mu = mu)` | `size` $= k$, `prob` $= k/(k + \mu)$ <!-- L45 --> |
| R MASS 7.3 | `glm.nb`, `rnegbin(n, mu, theta)` | $\theta = k$ <!-- L46 --> |

**The t as a mixture.** If $X \mid V \sim \mathcal N(0, V)$ and $\nu/V \sim \chi^2_\nu$, then $X$ is a standard $t_\nu$, <!-- L26 --> and its variance is $\operatorname{E}[V] = \nu \cdot \operatorname{E}[1/\chi^2_\nu] = \nu/(\nu - 2)$. The unit-variance tail beyond four standard deviations is then

$$
P(\lvert X \rvert \gt 4) = 2\, P\!\left(T_5 \gt 4\sqrt{5/3}\right) = 2\, P(T_5 \gt 5.164) = 0.00357 \tag{6}
$$

That is 56.4 times the normal's 0.0000633, and the lab computes it two ways: from a closed form for the t₅ distribution function and from SciPy's standardised `t`, scaled by its `scale` argument, <!-- L43 --> which agree to 10⁻¹⁶.

**Why a lognormal looks straight.** With $\ln X \sim \mathcal N(\mu, \sigma^2)$ and density $f$:

$$
\frac{d \ln f(x)}{d \ln x} = -1 - \frac{\ln x - \mu}{\sigma^2} \tag{7}
$$

The log–log slope steepens by $1/\sigma^2$ per unit of $\ln x$, 0.16 per factor of e at $\sigma = 2.5$. Across the 2.5 decades of Figure 9's window that adds up to about 0.9, a real bend, yet the least-squares line still scores $R^2 = 0.991$: a high $R^2$ does not detect curvature.

## Implementation

The core of the lab fits in a page: Poisson and negative binomial probabilities by recurrence, the moment fit, the rootogram's bar ends, and a check against SciPy's spelling of the negative binomial.

```python
import numpy as np
from scipy import stats


def poisson_pmf(lam, kmax):
    p = np.empty(kmax + 1)
    p[0] = np.exp(-lam)
    for j in range(kmax):
        p[j + 1] = p[j] * lam / (j + 1)          # P(j+1) = P(j) * lam / (j+1)
    return p


def nbinom_pmf(mu, k, jmax):
    p = np.empty(jmax + 1)
    p[0] = (k / (k + mu)) ** k
    for j in range(jmax):
        p[j + 1] = p[j] * (j + k) / (j + 1) * mu / (k + mu)
    return p


def classes(pmf, n, last=5):                     # expected counts for 0..last-1 and last-or-more
    return n * np.append(pmf[:last], 1 - pmf[:last].sum())


x = np.arange(6)
f = np.array([447, 132, 42, 21, 3, 2])           # Greenwood and Yule's 647 women
n = f.sum()
mu = (x * f).sum() / n
s2 = (f * (x - mu) ** 2).sum() / (n - 1)
k = mu**2 / (s2 - mu)                            # moments: s2 = mu + mu^2 / k
pois, nb = classes(poisson_pmf(mu, 40), n), classes(nbinom_pmf(mu, k, 60), n)
print(round(mu, 4), round(s2, 4), round(k, 4))   # 0.4652 0.6919 0.9548
print(pois.round(2).tolist())                     # [406.31, 189.03, 43.97, 6.82, 0.79, 0.08]
print(nb.round(2).tolist())                       # [442.91, 138.55, 44.36, 14.32, 4.64, 2.23]
print((np.sqrt(pois) - np.sqrt(f)).round(2).tolist())  # bar bottoms: [-0.99, 2.26, 0.15, -1.97, -0.84, -1.13]
fit = stats.nbinom(k, k / (k + mu))               # SciPy: n = k, p = k / (k + mu)
print(round(fit.mean(), 4), round(fit.var(), 4))  # 0.4652 0.6919
```

The recurrences avoid computing factorials and gamma functions, and they make each probability's dependence on the last one explicit. The last two lines are the check that matters in practice: a moment fit must return the sample's own mean and variance, so a wrong mapping shows up there before it shows up anywhere else. The full lab adds the binomial and Bortkiewicz's corps, the coal gaps, the sums and products, both accident stories over two periods, the t₅ tails and the log–log experiments, each against SciPy and, privately, R. See [Lab downloads](#lab-downloads).

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** passing μ/(k + μ) as SciPy's `p`. SciPy's negative binomial counts failures before n successes, and `p` is the success probability, k/(k + μ). With the slip, the "fitted" distribution for Greenwood and Yule's data has mean 1.96 and variance 5.98 instead of 0.465 and 0.692, expects 223 women with no accident where 447 had none, and fits worse than the Poisson it replaced (chi-square 397 against 103). Check `fit.mean()` against the sample mean every time.

- **Choosing the family by the best fit score.** A goodness-of-fit test can reject a family, but with data thin in the tails it cannot pick between families that agree in the body. Write the story first, then test what it predicts.
- **Reading a negative binomial fit as proof of heterogeneity.** Contagion, and clusters of random size, give the same one-period counts. <!-- L21 --> <!-- L23 --> Following the same people over a second period can separate the stories. <!-- L22 -->
- **Forgetting what a pooled class hides.** Clarke's "5 and over" square held 7 bombs. Treat it as 5 and the mean falls from 0.9323 to 0.9288.
- **Trusting a Poisson fit that selection produced.** Clarke chose a homogeneous area and Bortkiewicz dropped four corps. A clean fit on a curated subset says the rate was constant there, not everywhere.
- **Using a mixture for underdispersed counts.** A gamma–Poisson or normal-scale mixture keeps the mean and raises the variance, so it can never be underdispersed. <!-- L27 --> Counts with variance below the mean need a different story, such as a binomial with a fixed ceiling.
- **Trusting moments for the dispersion.** Mean-and-variance estimates of k lose efficiency in parts of the parameter space. <!-- L24 --> Maximum likelihood, later in this series, is the standard alternative and comes with a standard error.

## Key takeaways

- Derive a family from the process that made the data and test the story's predictions; a histogram cannot choose between families that agree where data are dense.
- A Poisson is the arithmetic of many rare, independent chances at one common rate; check it by the dispersion index, which Clarke's squares put at 1.04.
- Gamma-distributed rates turn Poisson counts into a negative binomial with variance μ + μ²/k, and the extra variance is the spread of the rates under that story; contagion gives the same one-period counts.
- Tails decide risk, and small samples usually miss them: a unit-variance t₅ is 56 times likelier than the normal beyond four standard deviations, yet 70% of its samples of 100 show nothing beyond 4.
- A straight log–log tail is not evidence of a power law; a lognormal draws one with R² = 0.991, and the mechanism, such as a floor under growth, decides between them.

## Try it yourself

**E1, reproduce.** Using only λ = 537/576, compute Clarke's expected number of squares with exactly 3 hits.

<details><summary>Answer</summary>

576 × e^(−0.9323) × 0.9323³ / 3! = 576 × 0.39365 × 0.81032 / 6 = 30.62, the value Clarke printed. The binomial gives 30.59.

</details>

**E3, predict.** A t with 3 degrees of freedom has variance 3. Scale it to variance 1. Before computing, predict whether its ratio to the normal beyond four standard deviations is above or below t₅'s 56.4, and roughly by how much.

<details><summary>Answer</summary>

Above: fewer degrees of freedom mean a variance that varies more, and heavier tails. The scaled tail is 2 P(T₃ > 4√3) = 2 P(T₃ > 6.93) = 0.0062, so the ratio is 97.3, nearly twice t₅'s. The lab's `tails --df 3` stage reproduces it.

</details>

The lab carries the full ladder, from reproducing every table to diagnosing the SciPy mapping fault above, with self-checks and answers; see [Lab downloads](#lab-downloads).

## References

### Lab downloads

- [`README.md`](LAB_01) — grade, provenance, setup, run order, the E1–E4 exercises with answers, and cleanup.
- [`stories.py`](LAB_02) — every generative story in the article as code, with each probability checked against SciPy.
- [`requirements.txt`](LAB_03) — the pinned NumPy and SciPy versions.
- [`clarke1946_flying_bombs.csv`](LAB_04) — Clarke's 576 squares, with source and the imputed 7 explained; put it in a `data` folder.
- [`bortkiewicz1898_horse_kicks.csv`](LAB_05) — the 280 corps-years transcribed from the 1898 scan, matching R's vcd copy in every cell; <!-- L15 --> put it in a `data` folder.
- [`greenwood_yule1920_accidents.csv`](LAB_06) — the 647 women's accident counts, with the reproductions they come from; put it in a `data` folder.
- [`coal_disasters_1851_1962.csv`](LAB_07) — dates of 191 coal-mine explosions; put it in a `data` folder.
- [`captures.json`](LAB_08) — the author's run, machine-readable, with the R cross-check.
- [`expected-output.txt`](LAB_09) — the author's run as printed, to compare with yours.
- [`notebook.ipynb`](LAB_10) — the README with a runnable cell under each step and exercise.
- [Complete lab](https://minio.canery.in/media/lab-distributions-as-generative-stories.zip) — every file above in one zip, with the `data` folder in place.

### Sources

1. R. D. Clarke. "An application of the Poisson distribution." *Journal of the Institute of Actuaries* 72(3): 481, 1946. https://doi.org/10.1017/S0020268100035435
2. M. Greenwood and G. U. Yule. "An inquiry into the nature of frequency distributions representative of multiple happenings with particular reference to the occurrence of multiple attacks of disease or of repeated accidents." *Journal of the Royal Statistical Society* 83(2): 255–279, 1920. https://doi.org/10.2307/2341080 (table as reproduced in 3 and 4)
3. D. Böhning. "Zero-inflated Poisson models and C.A.MAN: a tutorial collection of evidence." *Biometrical Journal* 40(7): 833–843, 1998. Author's copy: http://www.personal.soton.ac.uk/dab1f10/tutor.pdf
4. B. K. Sah and S. K. Sahani. "Generalised Poisson-new linear-exponential distribution." *Mathematical Models in Engineering* 10(4), 2024. https://doi.org/10.21595/mme.2024.24258
5. L. von Bortkiewicz. *Das Gesetz der kleinen Zahlen*. Teubner, Leipzig, 1898, §11–12. https://archive.org/details/dasgesetzderklei00bortrich
6. `VonBort`, R package vcd, after D. F. Andrews and A. M. Herzberg, *Data*, Springer, 1985. https://vincentarelbundock.github.io/Rdatasets/doc/vcd/VonBort.html (accessed 2026-10-24)
7. G. E. Bates and J. Neyman. "Contributions to the theory of accident proneness. II. True or false contagion." *University of California Publications in Statistics* 1(10): 255–276, 1952. https://archive.org/details/DTIC_ADA311362
8. S. Coly, A.-F. Yao, D. Abrial and M. Charras-Garrido. "Distributions to model overdispersed count data." *Journal de la Société Française de Statistique* 157(2): 39–63, 2016. https://www.numdam.org/item/JSFS_2016__157_2_39_0/
9. L. Le Cam. "An approximation theorem for the Poisson binomial distribution." *Pacific Journal of Mathematics* 10(4): 1181–1197, 1960. https://doi.org/10.2140/pjm.1960.10.1181
10. A. Clauset, C. R. Shalizi and M. E. J. Newman. "Power-law distributions in empirical data." *SIAM Review* 51(4): 661–703, 2009. https://arxiv.org/abs/0706.1062
11. C. Kleiber and A. Zeileis. "Visualizing count data regressions using rootograms." *The American Statistician* 70(3): 296–303, 2016. https://arxiv.org/abs/1605.01311
12. M. Mitzenmacher. "A brief history of generative models for power law and lognormal distributions." *Internet Mathematics* 1(2): 226–251, 2004. https://doi.org/10.1080/15427951.2004.10129088
13. E. Limpert, W. A. Stahel and M. Abbt. "Log-normal distributions across the sciences: keys and clues." *BioScience* 51(5): 341–352, 2001. Author's copy: https://stat.ethz.ch/~stahel/lognormal/bioscience.pdf
14. A. D. Broido and A. Clauset. "Scale-free networks are rare." *Nature Communications* 10: 1017, 2019. https://doi.org/10.1038/s41467-019-08746-5
15. J. Alstott, E. Bullmore and D. Plenz. "powerlaw: a Python package for analysis of heavy-tailed distributions." *PLoS ONE* 9(1): e85777, 2014. https://doi.org/10.1371/journal.pone.0085777
16. A. Gelman, J. B. Carlin, H. S. Stern, D. B. Dunson, A. Vehtari and D. B. Rubin. *Bayesian Data Analysis*, 3rd ed., CRC Press, 2013, §2.7, §17.2 and Appendix A. http://www.stat.columbia.edu/~gelman/book/
17. C. M. Grinstead and J. L. Snell. *Introduction to Probability*, 2nd ed., American Mathematical Society, 1997, §5.2. https://math.dartmouth.edu/~prob/prob/prob.pdf
18. SciPy 1.18 documentation, `scipy.stats.nbinom`. https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.nbinom.html (accessed 2026-10-24)
19. SciPy 1.18 documentation, `scipy.stats.t`. https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.t.html (accessed 2026-10-24)
20. statsmodels 0.15 documentation, `NegativeBinomial`. https://www.statsmodels.org/stable/generated/statsmodels.discrete.discrete_model.NegativeBinomial.html (accessed 2026-10-24)
21. R documentation, `NegBinomial` (package stats). https://stat.ethz.ch/R-manual/R-patched/library/stats/html/NegBinomial.html (accessed 2026-10-24)
22. MASS: support functions and datasets for Venables and Ripley's MASS, `rnegbin` and `glm.nb`. https://cran.r-project.org/package=MASS (accessed 2026-10-24)
23. `coal`, R package boot: dates of coal-mining disasters, after D. J. Hand et al., *A Handbook of Small Data Sets*, 1994, and R. G. Jarrett, *Biometrika* 66, 1979. https://vincentarelbundock.github.io/Rdatasets/doc/boot/coal.html (accessed 2026-10-24)
24. `V1`, R package VGAM 1.1-13: Clarke's flying-bomb data. https://www.rdocumentation.org/packages/VGAM/versions/1.1-13/topics/V1 (accessed 2026-10-24)
25. L. P. Shaw and L. F. Shaw. "The flying bomb and the actuary." *Significance* 16(5): 12–17, 2019. https://doi.org/10.1111/j.1740-9713.2019.01315.x
