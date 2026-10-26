---
social_schema: 2
canonical_url: "https://canery.in/blogs/distributions-as-generative-stories"
---

# Social publishing package — distributions-as-generative-stories

## LinkedIn post

Pick a probability distribution by writing down how your numbers were made. The histogram can test that story; it cannot choose it.

The first part of Statistics for Data Scientists checks each story against a historical table or an exact computation:

→ 537 flying bombs on 576 squares of south London make Poisson counts. R. D. Clarke's 1946 table matches the Poisson in every class: variance 0.971 against a mean of 0.932.
→ Bortkiewicz's horse kicks fit the Poisson too, after four corps were set aside. All 280 corps-years give a variance of 0.763 against a mean of 0.70.
→ Give each worker her own accident rate, drawn from a gamma, and the counts become negative binomial. Greenwood and Yule's 647 women: variance 0.692 = 0.465 of Poisson noise + 0.227 from rates that differ.
→ A contagion story produces the same one-period counts. A second five weeks separates them: 0.465 against 0.691.
→ A unit-variance t with 5 degrees of freedom has 56 times the normal's probability beyond four standard deviations, and 70% of its samples of 100 show nothing beyond 4.
→ A lognormal sample draws a straight log–log tail with R² = 0.991. The mechanism, such as a floor under growth, decides between lognormal and power law; the plot cannot.

Every computed number comes from a lab you can download and rerun in under ten seconds.

## LinkedIn first comment

Write the generative story first, then let the data test what it predicts: variance against mean, every class of the table, and the tails.

Read the full article on Canery: https://canery.in/blogs/distributions-as-generative-stories

## Instagram caption

Which distribution fits your data? Ask how the numbers were made. Swipe through bombs on London squares that make Poisson counts, horse kicks that fit only once four corps are set aside, accident rates that make a negative binomial, a contagion story with the same counts, a t with 56 times the normal's tail beyond four standard deviations, and a lognormal that fakes a power law.

Every computed number comes from a lab you can rerun.

Link in bio.

#statistics #datascience #probability #poissondistribution #negativebinomial #overdispersion #python

## Shared feed order

1. `assets/social/feed-01-let-the-process-pick.png` — the bomb story, from one square's chance to the Poisson, and Clarke's table against it
2. `assets/social/feed-02-variance-equals-mean.png` — the hanging rootogram of Clarke's squares and the dispersion index of 1.04
3. `assets/social/feed-03-read-the-footnote.png` — Bortkiewicz's 200 corps-years against all 280, and the four corps he set aside
4. `assets/social/feed-04-rates-that-differ.png` — Greenwood and Yule's counts against the Poisson and the negative binomial, and the variance in two parts
5. `assets/social/feed-05-same-counts-two-stories.png` — proneness and contagion: the same first five weeks, different second five weeks
6. `assets/social/feed-06-56-times-the-tail.png` — the unit-variance t₅ against the normal beyond 3, 4 and 5 standard deviations
7. `assets/social/feed-07-straight-is-not-a-power-law.png` — a lognormal's straight log–log tail, R² 0.991, and its finite mean
8. `assets/social/feed-08-read-the-article.png` — the four stories in one list, and the CTA

## Instagram Story

- CTA: Let the process pick the distribution. Four stories, checked on real data — tap the link.
- Link sticker label: Read the article
- Link sticker URL: https://canery.in/blogs/distributions-as-generative-stories

### Story order

1. `assets/social/story-01-let-the-process-pick.png` — Overlay: 537 bombs, 576 squares: the Poisson predicts every class.
2. `assets/social/story-02-rates-that-differ.png` — Overlay: Variance 0.692 = 0.465 noise + 0.227 from rates that differ.
3. `assets/social/story-03-56-times.png` — Overlay: Same variance, 56 times the tail beyond 4.
4. `assets/social/story-04-read-the-article.png` — Overlay: Distributions as generative stories. Link below.

## Asset metadata

### feed-01-let-the-process-pick

- File: `assets/social/feed-01-let-the-process-pick.png`
- Title: Let the process pick the distribution
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: each bomb lands in one of 576 squares with chance 1/576, so a square's count is Binomial(537, 1/576) and, with many rare chances, Poisson with λ = 0.932; Clarke's observed table matches it
- Technical source: Worked example; Figure 2; ledger L01, L04, L05, L08
- Visual structure: lockup and counter; serif title; deck; a panel with three lines of the story, a table of hits per square with observed and Poisson rows, a line of summary statistics and a source note; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 08 · Let the process pick the distribution. · 537 flying bombs on 576 squares: the story predicts the table before you see it. · each bomb: one square of 576, independently · → a square's count: Binomial(537, 1/576) · → many rare chances: Poisson, λ = 537/576 = 0.932 · hits per square 0 1 2 3 4 5+ · observed 229 211 93 35 7 1 · Poisson 226.7 211.4 98.5 30.6 7.1 1.6 · variance 0.971 · mean 0.932 · chi-square 1.17, P = 0.88 · R. D. Clarke, 1946: 576 squares of a quarter square kilometre in south London; the 5+ square held the remaining 7 bombs · A histogram can test a story. It cannot choose one. · DISTRIBUTIONS AS GENERATIVE STORIES · CANERY.IN
- Alt text: The flying-bomb story from one square's chance to the Poisson, with Clarke's observed squares 229, 211, 93, 35, 7, 1 beside the Poisson's expected counts.
- Long description: Each of 537 flying bombs lands in one of 576 squares of south London with chance 1/576, independently, so one square's count is Binomial(537, 1/576); with many rare chances this is the Poisson with λ = 537/576 = 0.932. R. D. Clarke's 1946 table of squares with 0, 1, 2, 3, 4 and 5 or more hits, 229, 211, 93, 35, 7 and 1, sits beside the Poisson's 226.7, 211.4, 98.5, 30.6, 7.1 and 1.6. The variance is 0.971 against a mean of 0.932, and Clarke's chi-square is 1.17 with P = 0.88. The single square in the last class held the remaining 7 bombs. The takeaway: a histogram can test a generative story, but it cannot choose one.
- Keywords: Poisson distribution, binomial distribution, flying bombs, R. D. Clarke, generative story, probability distribution
- Canonical URL: https://canery.in/blogs/distributions-as-generative-stories

### feed-02-variance-equals-mean

- File: `assets/social/feed-02-variance-equals-mean.png`
- Title: Variance equals mean: the Poisson's signature
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Clarke's squares on a hanging rootogram end inside Tukey's ±1 lines, and the variance-to-mean ratio is 1.04, so the clustering claim gets no support
- Technical source: Worked example, dispersion index and rootogram; Figure 2; ledger L05, L06, L41
- Visual structure: lockup and counter; serif title; deck; a panel with a hanging rootogram of six classes, the expected curve with dots, dashed ±1 lines and class labels, and two lines of notes; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 08 · Variance = mean: the Poisson's signature. · Clarke tested whether the flying bombs clustered. His squares gave it no support. · hanging rootogram: √observed hung from √expected · +1 · −1 · 0 1 2 3 4 5+ · variance / mean = 1.04; clustering would push it above 1 · every bar ends inside Tukey's ±1 lines · The story made a prediction, and the data had a chance to break it. · DISTRIBUTIONS AS GENERATIVE STORIES · CANERY.IN
- Alt text: A hanging rootogram of Clarke's 576 squares against the Poisson; every bar ends inside the ±1 lines, and variance over mean is 1.04.
- Long description: Each class of Clarke's table, 0 to 5 or more hits, is drawn as a bar of square-root observed count hanging from the Poisson's square-root expected count, so a perfect fit leaves every bar ending on the zero line. All six bars end inside Tukey's warning limits at plus and minus 1. The variance-to-mean ratio of the squares is 1.04; clustering, the claim Clarke tested, would have pushed it above 1 with too many crowded and too many empty squares. The takeaway: the Poisson story made a prediction the data could have broken, and it held.
- Keywords: rootogram, dispersion index, Poisson distribution, goodness of fit, overdispersion
- Canonical URL: https://canery.in/blogs/distributions-as-generative-stories

### feed-03-read-the-footnote

- File: `assets/social/feed-03-read-the-footnote.png`
- Title: Read the footnote
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Bortkiewicz's well-known 200 corps-years have variance equal to the mean, but they leave out four corps whose make-up differed; all 280 corps-years give a ratio of 1.09
- Technical source: Worked example, Bortkiewicz paragraph; ledger L10, L11, L12, L13, L02
- Visual structure: lockup and counter; serif title; deck; a panel with two columns of mean, variance and ratio, a footnote naming the corps left out, a line on Clarke's area and a source line; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 08 · Read the footnote. · Bortkiewicz's horse kicks fit the Poisson after four corps were set aside. · the well-known 200 corps-years · 10 corps, 1875–1894 · mean 0.61 · variance 0.611 · ratio 1.00 · all 280 corps-years · 14 corps, 1875–1894 · mean 0.70 · variance 0.763 · ratio 1.09 · left out of the 200: the Guard, with 40 cavalry squadrons; XI, with three divisions; I and VI, with 30 and 25 squadrons, against a norm of 20 · Clarke, too, chose an area of nearly constant density · Bortkiewicz 1898, §12; Clarke 1946 · The Poisson needs one common rate. Both classic fits met it partly by selection. · DISTRIBUTIONS AS GENERATIVE STORIES · CANERY.IN
- Alt text: Bortkiewicz's 200 corps-years with mean 0.61 and variance 0.611 beside all 280 with mean 0.70 and variance 0.763, and the four corps left out.
- Long description: Bortkiewicz's horse-kick deaths in the Prussian army, 1875 to 1894. The well-known 200 corps-years from 10 corps have mean 0.61, variance 0.611 and a ratio of 1.00. All 280 corps-years from 14 corps have mean 0.70, variance 0.763 and a ratio of 1.09. The 200 leave out the Guard, with 40 cavalry squadrons, XI, with three divisions, and I and VI, with 30 and 25 squadrons, against a norm of 20. Clarke likewise chose an area of nearly constant density. The takeaway: the Poisson needs one common rate, and both classic fits met that condition partly by selection.
- Keywords: Bortkiewicz, horse kicks, Poisson distribution, law of small numbers, selection, dispersion
- Canonical URL: https://canery.in/blogs/distributions-as-generative-stories

### feed-04-rates-that-differ

- File: `assets/social/feed-04-rates-that-differ.png`
- Title: Rates that differ make a negative binomial
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Greenwood and Yule's 647 women have too many with no accident and with three for a Poisson; gamma-distributed rates give a negative binomial that fits, and its variance splits into Poisson noise and the spread of rates
- Technical source: Why do accident counts break the Poisson?; Figures 5 and 6; ledger L16, L17, L24, L25
- Visual structure: lockup and counter; serif title; deck; a panel with a table of observed, Poisson and negative binomial counts, a line with k and the chi-squares, and a stacked bar with three labels; takeaway; footer
- Visible-text transcript: Canery.in · 04 / 08 · Rates that differ make a negative binomial. · Give each worker her own accident rate, drawn from a gamma, and recount. · accidents 0 1 2 3 4 5+ · observed 447 132 42 21 3 2 · Poisson 406.3 189.0 44.0 6.8 0.8 0.1 · neg. binom. 442.9 138.5 44.4 14.3 4.6 2.2 · k = 0.955 by moments; chi-square 103.1 → 4.20 · 0.692 variance of a woman's count · 0.227 μ²/k: rates that differ · 0.465 μ: each woman's Poisson noise · 647 women on high-explosive shells, five weeks · Under that story, the extra variance is the spread of the women's rates. · DISTRIBUTIONS AS GENERATIVE STORIES · CANERY.IN
- Alt text: Greenwood and Yule's accident counts against the Poisson and a moment-fitted negative binomial, and the variance 0.692 split into 0.465 and 0.227.
- Long description: Of 647 women working on high-explosive shells, 447, 132, 42, 21, 3 and 2 had 0, 1, 2, 3, 4 and 5 or more accidents in five weeks. A Poisson with the same mean expects 406.3, 189.0, 44.0, 6.8, 0.8 and 0.1; a negative binomial fitted by moments, k = 0.955, expects 442.9, 138.5, 44.4, 14.3, 4.6 and 2.2, and the chi-square falls from 103.1 to 4.20. The variance of a woman's count, 0.692, is 0.465 of Poisson noise, the mean μ, plus 0.227 from rates that differ, μ²/k. The takeaway: under the proneness story, the extra variance is the spread of the women's accident rates.
- Keywords: negative binomial, overdispersion, gamma–Poisson mixture, Greenwood and Yule, accident proneness, method of moments
- Canonical URL: https://canery.in/blogs/distributions-as-generative-stories

### feed-05-same-counts-two-stories

- File: `assets/social/feed-05-same-counts-two-stories.png`
- Title: Same counts, two stories
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: proneness and contagion give the same negative binomial for one period; over a second five weeks contagion raises the mean count to 0.691 while proneness keeps it at 0.465
- Technical source: What the counts cannot tell you; ledger L18, L21, L22; lab accidents stage
- Visual structure: lockup and counter; serif title; deck; a panel with two labelled columns, a row of first-period counts in each, a line on exact against simulated, two large second-period means with captions and a simulation note; takeaway; footer
- Visible-text transcript: Canery.in · 05 / 08 · Same counts, two stories. · A rate per person, or accidents that raise the chance of the next one. · proneness · each woman her own rate · contagion · start at 0.379, +0.397 an accident · first five weeks: women with 0 to 5+ accidents · 442.9 138.5 44.4 14.3 … · 442.8 138.5 44.5 14.4 … · proneness exact, contagion simulated: the same distribution · second five weeks: mean count · 0.465 · rates unchanged · 0.691 · accidents have accumulated · lab simulation: R = 20,000 and 10,000 factories of 647 · One period cannot tell them apart. A second period can. · DISTRIBUTIONS AS GENERATIVE STORIES · CANERY.IN
- Alt text: Proneness and contagion give the same first-period accident counts, but over a second five weeks the mean count is 0.465 against 0.691.
- Long description: Two stories for Greenwood and Yule's accident counts. Proneness gives each woman her own gamma-distributed rate; contagion starts every woman at 0.379 accidents per five weeks and adds 0.397 per accident. For the first five weeks both give the same negative binomial: proneness gives exactly 442.9, 138.5, 44.4 and 14.3 women with 0 to 3 accidents, and a simulation of the contagion process gives 442.8, 138.5, 44.5 and 14.4. Over a second five weeks the mean count stays at 0.465 under proneness and rises to 0.691 under contagion, simulated with 20,000 and 10,000 factories of 647 women. The takeaway: one period cannot tell the stories apart, and a second period can.
- Keywords: contagion, accident proneness, negative binomial, Pólya process, identifiability, simulation
- Canonical URL: https://canery.in/blogs/distributions-as-generative-stories

### feed-06-56-times-the-tail

- File: `assets/social/feed-06-56-times-the-tail.png`
- Title: Same variance, 56 times the tail
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: a t with 5 degrees of freedom scaled to variance 1 puts 0.357% beyond four standard deviations against the normal's 0.0063%, 56.4 times as much, while its peak is only a little taller
- Technical source: What can't a histogram show?; Figure 7; ledger L26; lab tails stage
- Visual structure: lockup and counter; serif title; deck; a panel with two large percentages, three bars of the log tail ratio at 3, 4 and 5 standard deviations with their labels, and two lines of notes; takeaway; footer
- Visible-text transcript: Canery.in · 06 / 08 · Same variance. 56 times the tail. · A t with 5 degrees of freedom, scaled to variance 1, against the normal. · beyond 4 standard deviations · 0.357% · unit-variance t₅ · 0.0063% · normal · beyond 3 ×4.3 · beyond 4 ×56.4 · beyond 5 ×2,316 · bar length: log of the ratio of tail probabilities · peaks: t₅ 0.490, normal 0.399 · samples of 100: 70% show nothing beyond 4 · The tail that sets your risk is the part a small sample usually misses. · DISTRIBUTIONS AS GENERATIVE STORIES · CANERY.IN
- Alt text: Beyond four standard deviations a unit-variance t₅ has 0.357% against the normal's 0.0063%, with tail ratios of 4.3, 56.4 and 2,316 at 3, 4 and 5.
- Long description: A Student t with 5 degrees of freedom, scaled to variance 1, against the standard normal. Beyond four standard deviations the t puts 0.357% of its probability and the normal 0.0063%, a ratio of 56.4; the ratio is 4.3 beyond 3 and 2,316 beyond 5, drawn as bars whose length is the log of the ratio. The peaks differ less: 0.490 against 0.399. In samples of 100, 70% of t₅ samples show nothing beyond 4. The takeaway: the tail that sets your risk is the part a small sample usually misses.
- Keywords: Student t distribution, heavy tails, normal distribution, tail probability, risk
- Canonical URL: https://canery.in/blogs/distributions-as-generative-stories

### feed-07-straight-is-not-a-power-law

- File: `assets/social/feed-07-straight-is-not-a-power-law.png`
- Title: A straight log–log line is not a power law
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the top 10% of 10,000 lognormal draws gives a least-squares line with R² = 0.991 on log–log axes; read as a power law its slope means an infinite mean, while the lognormal's mean is 22.8; a floor under growth is what makes a true power law
- Technical source: Is a straight line on a log–log plot a power law?; Figures 9 and 10; ledger L32, L33, L34, L35
- Visual structure: lockup and counter; serif title; deck; a panel with a schematic log–log plot of the sample's complementary CDF, a shaded top-10% window and a tangerine fitted line, notes on the fit and the mean to the right, and a line on the floor; takeaway; footer
- Visible-text transcript: Canery.in · 07 / 08 · A straight log–log line is not a power law. · A lognormal sample draws a straight tail, with a mean the line says cannot exist. · P(X ≥ x), log scale · x, log scale → · top 10% of 10,000 lognormal draws, σ = 2.5 · R² = 0.991 · slope −0.918 · read as a power law: an infinite mean · true mean: e^(σ²/2) = 22.8 · add a floor to the same growth and the tail becomes a true power law · The mechanism, such as a floor under growth, decides. The plot cannot. · DISTRIBUTIONS AS GENERATIVE STORIES · CANERY.IN
- Alt text: A lognormal sample's survival curve on log–log axes with a straight least-squares line on its top 10%, R² 0.991, slope −0.918, true mean 22.8.
- Long description: 10,000 draws from a lognormal with σ = 2.5, plotted as the share of draws at least x against x on log–log axes. A least-squares line through the top 10% has slope −0.918 and R² = 0.991. Read as a power law, an exponent below 1 means an infinite mean, yet the lognormal that drew the sample has mean e^(σ²/2) = 22.8. Adding a floor to the same multiplicative growth turns the tail into a true power law. The takeaway: the mechanism, such as a floor under growth, decides between a lognormal and a power law; the plot cannot.
- Keywords: power law, lognormal distribution, log-log plot, heavy tails, Clauset Shalizi Newman, Champernowne
- Canonical URL: https://canery.in/blogs/distributions-as-generative-stories

### feed-08-read-the-article

- File: `assets/social/feed-08-read-the-article.png`
- Title: Distributions as generative stories
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: the four stories in one list with one number each, and where to read the full walk-through
- Technical source: Key takeaways; Figures 2, 5, 7 and 9
- Visual structure: lockup and counter; serif title; deck; a panel with four headed items, each with a line of setup and a line of evidence; takeaway; tangerine CTA footer with the canonical URL
- Visible-text transcript: Canery.in · 08 / 08 · Distributions as generative stories. · Each family derived from a process, then tested on real tables or by simulation. · Poisson · 537 bombs, 576 squares · variance / mean = 1.04 · negative binomial · 647 women, rates that differ · 0.692 = 0.465 + 0.227 · Student t₅ · a normal whose variance varies · ×56 beyond 4 sd · power law or lognormal · the mechanism decides · R² 0.991 proves nothing · The full walk-through, every computed number rerun by a script you can download. · READ IT AT CANERY.IN/BLOGS/DISTRIBUTIONS-AS-GENERATIVE-STORIES
- Alt text: Four generative stories with one number each: Poisson 1.04, negative binomial 0.692 = 0.465 + 0.227, t₅ ×56, power law or lognormal.
- Long description: A closing list of the article's four stories. The Poisson: 537 bombs on 576 squares, variance over mean 1.04. The negative binomial: 647 women whose rates differ, variance 0.692 = 0.465 + 0.227. The Student t₅: a normal whose variance varies, 56 times the normal's tail beyond four standard deviations. Power law or lognormal: the mechanism decides, and an R² of 0.991 proves nothing. Each family is derived from a process and tested on real tables or by simulation, with a lab that reruns every computed number. The call to action gives the article's address.
- Keywords: probability distributions, generative story, Poisson, negative binomial, Student t, power law
- Canonical URL: https://canery.in/blogs/distributions-as-generative-stories

### story-01-let-the-process-pick

- File: `assets/social/story-01-let-the-process-pick.png`
- Title: Let the process pick
- Platforms: Instagram Story
- Role: cover
- Dimensions: 1080×1920
- Narrative beat: 537 flying bombs on 576 squares with chance 1/576 each; Clarke's observed squares against the Poisson, class by class
- Technical source: Worked example; Figure 2; ledger L01, L04
- Visual structure: lockup and counter; serif title; deck; a tall panel with a header and six rows of class, observed count and Poisson count, labelled at the foot; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 04 · Let the process pick. · 537 flying bombs, 576 squares, chance 1/576 each. · squares with 0 to 5+ hits · 0 229 226.7 · 1 211 211.4 · 2 93 98.5 · 3 35 30.6 · 4 7 7.1 · 5+ 1 1.6 · observed · Poisson · The story predicts every class of the table. · DISTRIBUTIONS AS GENERATIVE STORIES · CANERY.IN
- Alt text: Clarke's squares with 0 to 5 or more flying-bomb hits, observed 229, 211, 93, 35, 7, 1, beside the Poisson's 226.7, 211.4, 98.5, 30.6, 7.1, 1.6.
- Long description: R. D. Clarke's 1946 table of 576 squares of south London hit by 537 flying bombs, each square with chance 1/576 per bomb. Squares with 0, 1, 2, 3, 4 and 5 or more hits were observed 229, 211, 93, 35, 7 and 1 times, and the Poisson with λ = 537/576 expects 226.7, 211.4, 98.5, 30.6, 7.1 and 1.6. The takeaway: the generative story predicts every class of the table.
- Keywords: Poisson distribution, flying bombs, R. D. Clarke, generative story
- Canonical URL: https://canery.in/blogs/distributions-as-generative-stories

### story-02-rates-that-differ

- File: `assets/social/story-02-rates-that-differ.png`
- Title: 1.49 times the mean
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: the variance of Greenwood and Yule's accident counts, 0.692, is 1.49 times the mean and splits into 0.465 of Poisson noise and 0.227 from rates that differ
- Technical source: Why do accident counts break the Poisson?; Figure 6; ledger L16, L25
- Visual structure: lockup and counter; serif title; deck; a tall panel with a stacked bar, blue below and tangerine above, labelled with its two parts and the total; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 04 · 1.49 times the mean. · Greenwood and Yule's 647 women: their accident counts' variance. · 0.227 · rates that differ · 0.465 · Poisson noise · = 0.692 variance · Rates drawn from a gamma: the counts go negative binomial. · DISTRIBUTIONS AS GENERATIVE STORIES · CANERY.IN
- Alt text: A stacked bar of the accident counts' variance, 0.465 of Poisson noise below and 0.227 from rates that differ above, 0.692 in total.
- Long description: The variance of the accident counts of Greenwood and Yule's 647 women is 0.692, 1.49 times their mean of 0.465. Drawn as a stacked bar, it is 0.465 of Poisson noise, each woman's own luck, plus 0.227 from accident rates that differ between women. The takeaway: with rates drawn from a gamma distribution, the counts are negative binomial.
- Keywords: overdispersion, negative binomial, law of total variance, accident proneness
- Canonical URL: https://canery.in/blogs/distributions-as-generative-stories

### story-03-56-times

- File: `assets/social/story-03-56-times.png`
- Title: 56 times the tail
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: beyond four standard deviations a unit-variance t₅ has 0.357% against the normal's 0.0063%, and 70% of its samples of 100 show nothing there
- Technical source: What can't a histogram show?; Figure 7; lab tails stage
- Visual structure: lockup and counter; serif title; deck; a tall panel with two large percentages and their labels and a definition line; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 04 · 56 times the tail. · Same variance, same mean, different tails. · beyond 4 standard deviations · 0.357% · unit-variance t₅ · 0.0063% · normal · a t with 5 degrees of freedom, scaled to variance 1 · 70% of t₅ samples of 100 show nothing beyond 4. · DISTRIBUTIONS AS GENERATIVE STORIES · CANERY.IN
- Alt text: Beyond four standard deviations, 0.357% for a unit-variance t with 5 degrees of freedom against 0.0063% for the normal, 56 times as much.
- Long description: A Student t with 5 degrees of freedom, scaled to variance 1, and the standard normal share their mean and variance but not their tails. Beyond four standard deviations the t has 0.357% of its probability and the normal 0.0063%, 56 times less. Yet 70% of t₅ samples of 100 show no point beyond 4, so a small sample usually hides the difference.
- Keywords: Student t distribution, heavy tails, tail probability, normal distribution
- Canonical URL: https://canery.in/blogs/distributions-as-generative-stories

### story-04-read-the-article

- File: `assets/social/story-04-read-the-article.png`
- Title: Distributions as generative stories
- Platforms: Instagram Story
- Role: cta
- Dimensions: 1080×1920
- Narrative beat: the method in four steps, and where to read the article
- Technical source: Key takeaways; The problem
- Visual structure: lockup and counter; serif title; deck; a tinted panel with four numbered steps; takeaway; tangerine CTA footer pointing to the link sticker
- Visible-text transcript: Canery.in · 04 / 04 · Distributions as generative stories. · Poisson, negative binomial, t and power law, each from its process. · 1 write how each number was made · 2 derive the family from the story · 3 test what the story predicts · 4 a straight log–log line is not a test · The full walk-through is on Canery. · LINK IN THE STICKER ABOVE
- Alt text: Four steps for choosing a distribution: write how each number was made, derive the family, test its predictions, and distrust log–log lines.
- Long description: The article's method in four steps: write down how each number was made, derive the distribution family from that story, test what the story predicts against the data, and do not treat a straight log–log line as a test of a power law. The call to action points to the link sticker for the full article on Canery.
- Keywords: probability distributions, generative story, statistics, data science
- Canonical URL: https://canery.in/blogs/distributions-as-generative-stories
