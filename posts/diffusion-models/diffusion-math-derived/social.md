---
social_schema: 2
canonical_url: "https://canery.in/blogs/diffusion-math-derived"
---

# Social publishing package — diffusion-math-derived

## LinkedIn post

Every diffusion model you have trained minimises `‖ε − ε̂‖²`. It looks like plain regression. It is a likelihood bound with its weights deleted.

The path from one to the other is five steps, and four of them are exact:

→ Jensen's inequality turns the intractable log-likelihood into a bound, the ELBO.
→ Bayes' rule on each forward step turns that bound into one KL divergence per denoising step: the network's step against the step a "teacher" would take if it knew the clean image.
→ Both sides of every KL are Gaussians with the same variance, so the KL is a squared distance between two means.
→ Writing those means through the noise turns it into `‖ε − ε̂‖²` times a weight.
→ DDPM sets every weight to 1. That is the simple loss — and the only step that is a choice.

On one pixel of the article's worked example, one step's KL is 0.0250 nats: 0.625 times the squared noise error of 0.04. Priced as a clean-image error, a score error or a velocity error, the same mistake is still 0.04 once you convert units. At any one noise level the targets share a minimiser; they differ only in how they trade one noise level against another.

Dropping the weights is measurable. In DDPM's CIFAR-10 results the bound-trained model reached 3.70 bits per dimension and FID 13.51; the simple loss reached 3.75 and FID 3.17. Better samples, worse bound.

The same squared error comes out of denoising score matching, so DDPM, NCSN and the score SDE are one object seen in three coordinate systems.

Part 3 of the Diffusion Models series. Every identity is checked by a standard-library Python script you can download with the article.

## LinkedIn first comment

Your loss value is not a log-likelihood. The simple loss is the bound with its per-step weights replaced by 1.

Read the full article on Canery: https://canery.in/blogs/diffusion-math-derived

## Instagram caption

Your diffusion MSE loss is a likelihood bound in disguise. Each denoising step is scored by a KL between two Gaussians of equal width, and equal widths leave nothing to compare except the centres: a squared error.

Swipe through one pixel's reverse step, one error priced five ways, the weight DDPM dropped, what dropping it costs, and why every published diffusion loss is the same integral with a different weight.

Every number is computed on the article's own worked example or quoted with its setup.

Link in bio.

#diffusionmodels #machinelearning #deeplearning #generativeai #probability #elbo #scorematching

## Shared feed order

1. `assets/social/feed-01-your-mse-is-a-bound.png` — one reverse step on one pixel, teacher against student, KL 0.0250
2. `assets/social/feed-02-precisions-add.png` — the forward posterior as two Gaussian pieces of evidence, precision 5 + 4 = 9
3. `assets/social/feed-03-one-error-five-prices.png` — one +0.20 noise error priced as noise, clean pixel, score, velocity and the bound
4. `assets/social/feed-04-the-weight-ddpm-dropped.png` — DDPM's per-step ELBO weight across 1,000 steps against the simple loss's flat 1
5. `assets/social/feed-05-bound-versus-samples.png` — measured NLL and FID for the bound, hybrid and simple losses on CIFAR-10
6. `assets/social/feed-06-one-loss-many-weightings.png` — published losses as weighting functions over log-SNR
7. `assets/social/feed-07-read-the-article.png` — DDPM, NCSN and the score SDE as one object, and the CTA

## Instagram Story

- CTA: Where does the diffusion MSE loss come from? Five steps, four of them exact — tap the link.
- Link sticker label: Read the article
- Link sticker URL: https://canery.in/blogs/diffusion-math-derived

### Story order

1. `assets/social/story-01-your-mse-is-a-bound.png` — Overlay: Your MSE loss is a likelihood bound.
2. `assets/social/story-02-one-error-five-prices.png` — Overlay: One error, five prices, same minimiser.
3. `assets/social/story-03-noisy-targets-exact-average.png` — Overlay: Noisy targets, exact average: that is the score.
4. `assets/social/story-04-read-the-article.png` — Overlay: Five steps from a likelihood to an MSE. Link above.

## Asset metadata

### feed-01-your-mse-is-a-bound

- File: `assets/social/feed-01-your-mse-is-a-bound.png`
- Title: Your MSE loss is a likelihood bound
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: one denoising step is scored by a KL between two equal-width Gaussians, which is a squared error between their means.
- Technical source: Worked example ("The price"), Figure 1, ledger rows L05 and L07; values from lab/loss_identities.py section 1
- Visual structure: lockup and counter; serif title; two-line deck; the teacher curve (solid) and student curve (dashed) with the 0.0745 gap bracketed above their peaks; a white box with the KL arithmetic; takeaway; footer.
- Visible-text transcript: Canery.in · 01 / 07 · Your MSE loss is a likelihood bound. · One reverse step, one pixel: the teacher knows the clean image, the network does not. Same width, so only the centres differ. · gap 0.0745 · STUDENT · NETWORK · TEACHER · KNOWS x₀ · KL = gap² ÷ (2 × 1/9) = 0.0250 nats · = 0.625 × (noise error)², with (noise error)² = 0.04 · Two Gaussians of equal width: their KL is a squared error between two means. That is where the MSE comes from. · WHERE THE DIFFUSION MSE LOSS COMES FROM · CANERY.IN
- Alt text: Two bell curves of equal width, a teacher's and a network's, 0.0745 apart, with their KL worked out as 0.025 nats.
- Long description: For one pixel with clean value 0.95 and noisy value 0.43 on a coarse diffusion step from signal level 0.80 to 0.64, the forward posterior (the teacher) is a Gaussian with mean 0.6857 and variance 1/9. The network's step (the student) uses its clean-image guess of 0.80 and has the same variance, so its mean is 0.6112. The KL between them is the squared gap 0.0745² divided by 2/9, which is 0.0250 nats, equal to 0.625 times the squared noise error of 0.04.
- Keywords: diffusion model, ELBO, KL divergence, Gaussian, MSE loss, DDPM, variational bound
- Canonical URL: https://canery.in/blogs/diffusion-math-derived

### feed-02-precisions-add

- File: `assets/social/feed-02-precisions-add.png`
- Title: The teacher is two Gaussians, multiplied
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the forward posterior combines evidence from the clean pixel and from the noisy pixel; precisions add.
- Technical source: Worked example ("The teacher"), Figure 1, ledger row L04; lab/loss_identities.py section 1
- Visual structure: header; four density curves (evidence from x₀ in blue, evidence from xₜ in mustard, teacher solid, student dashed); a three-row table of each Gaussian and its precision; takeaway; footer.
- Visible-text transcript: Canery.in · 02 / 07 · The teacher is two Gaussians, multiplied. · Given the clean pixel 0.95 and the noisy pixel 0.43, where was the pixel one step earlier? Two pieces of evidence answer. · gap 0.0745 · STUDENT · NETWORK · TEACHER · KNOWS x₀ · evidence from x₀ N(0.8497, 0.20) precision 5 · evidence from xₜ N(0.4808, 0.25) precision 4 · teacher N(0.6857, 1/9) 5 + 4 = 9 · Precisions add. That is the whole forward posterior, and DDPM's closed form gives the same 0.6857. · WHERE THE DIFFUSION MSE LOSS COMES FROM · CANERY.IN
- Alt text: Two wide Gaussians of evidence combining into a narrower teacher Gaussian, with precisions 5 plus 4 equal to 9.
- Long description: Running the forward process from the clean pixel gives a Gaussian at 0.8497 with variance 0.20 (precision 5). Reading the last forward step backwards from the noisy pixel 0.43 gives a Gaussian at 0.4808 with variance 0.25 (precision 4). Their product is the forward posterior, with precision 9, variance 1/9 and mean 0.6857, the same value DDPM's closed-form posterior gives.
- Keywords: forward posterior, Bayes rule, precision, Gaussian conjugacy, diffusion model, DDPM
- Canonical URL: https://canery.in/blogs/diffusion-math-derived

### feed-03-one-error-five-prices

- File: `assets/social/feed-03-one-error-five-prices.png`
- Title: One error, five prices
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the same prediction error in every common target converts back to one number; only constants differ at a fixed noise level.
- Technical source: Worked example ("One error, five prices"), Figure 2; lab/loss_identities.py section 2
- Visual structure: header; a white table with columns network predicts, squared error, constant, noise units; four rows plus an orange KL row; takeaway; footer.
- Visible-text transcript: Canery.in · 03 / 07 · One error, five prices. · The network misreads the noise by +0.20. Priced as noise, clean pixel, score or velocity, it is the same 0.04 each time. · NETWORK PREDICTS · SQUARED ERROR · × CONSTANT · NOISE UNITS · noise ε 0.0400 × 1 0.0400 · clean pixel x₀ 0.0225 × SNR 1.78 0.0400 · score −ε/0.6 0.1111 × 0.36 0.0400 · velocity v 0.0625 × 0.64 0.0400 · this step's KL 0.0250 = 0.625 × 0.0400 · At one noise level every target has the same minimiser. Targets differ only in how they trade levels off. · WHERE THE DIFFUSION MSE LOSS COMES FROM · CANERY.IN
- Alt text: A table showing a 0.20 noise error as squared errors 0.04, 0.0225, 0.1111 and 0.0625 that all convert to 0.04.
- Long description: At signal level 0.64 a noise error of +0.20 is a squared noise error of 0.04, a clean-pixel squared error of 0.0225 (times SNR 1.78 gives 0.04), a score squared error of 0.1111 (times 0.36 gives 0.04) and a velocity squared error of 0.0625 (times 0.64 gives 0.04). The likelihood bound's KL for this step is 0.025, which is 0.625 times 0.04.
- Keywords: epsilon prediction, v prediction, x0 prediction, score, loss weighting, SNR, diffusion
- Canonical URL: https://canery.in/blogs/diffusion-math-derived

### feed-04-the-weight-ddpm-dropped

- File: `assets/social/feed-04-the-weight-ddpm-dropped.png`
- Title: The weight DDPM dropped
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: inside the bound each step carries its own weight, largest for nearly clean steps; the simple loss sets all of them to 1.
- Technical source: "Why does DDPM throw the weights away?", Figure 5, ledger rows L07, L09 and L12; lab/loss_identities.py section 3
- Visual structure: header; a log-scale curve of the per-step weight across 1,000 steps with three marked points and a flat orange line at 1; an orange box with the 55× ratio; takeaway; footer.
- Visible-text transcript: Canery.in · 04 / 07 · The weight DDPM dropped. · Each step of the bound puts its own weight on the noise error. DDPM's simple loss replaces every one of them with 1. · 1 · 0.1 · 0.01 · 0.001 · t = 2: 0.2727 · t = 349: 0.00497 · t = 1000: 0.0102 · the simple loss: 1 at every step · DDPM step t, 1,000 steps, linear schedule · inside the bound: 55× between largest and smallest · The dropped weights favour nearly clean steps. Setting them to 1 turns those down and trains the harder ones. · WHERE THE DIFFUSION MSE LOSS COMES FROM · CANERY.IN
- Alt text: Log-scale curve of DDPM's per-step bound weight, 0.27 at step 2 falling to 0.005, beside the simple loss's flat 1.
- Long description: Computed from DDPM's published linear schedule (1,000 steps, beta from 0.0001 to 0.02) with reverse variance equal to beta, the weight the bound puts on the squared noise error is 0.2727 at step 2, reaches a minimum of 0.00497 at step 349, and rises to 0.0102 at step 1000, a 55-fold range. The simple loss uses 1 at every step. The curve is computed, not measured.
- Keywords: DDPM, L_simple, ELBO weighting, noise schedule, loss weighting, diffusion training
- Canonical URL: https://canery.in/blogs/diffusion-math-derived

### feed-05-bound-versus-samples

- File: `assets/social/feed-05-bound-versus-samples.png`
- Title: Better bound, worse samples
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: measured on CIFAR-10, the true bound wins on likelihood and loses on FID in two papers.
- Technical source: Figure 6, ledger rows L10 and L42 (Ho et al. 2020 Table 1; Nichol & Dhariwal 2021 Table 2)
- Visual structure: header; two groups of horizontal bar pairs, NLL in bits per dimension and FID, with values; a note not to compare across groups; takeaway; footer.
- Visible-text transcript: Canery.in · 05 / 07 · Better bound, worse samples. · Measured on CIFAR-10 in two papers. Training on the true bound wins on likelihood and loses on image quality. · NLL, BITS/DIM ↓ · FID ↓ · DDPM · CIFAR-10 · true bound 3.70 13.51 · simple loss 3.75 3.17 · IMPROVED DDPM · CIFAR-10 · true bound 2.94 11.47 · hybrid 3.17 3.19 · simple loss 3.26 3.05 · Different setups: compare within a group, not across. · DDPM's best-FID model has the worse bound, 3.75 against 3.70 bits per dimension. The loss value is not a likelihood. · WHERE THE DIFFUSION MSE LOSS COMES FROM · CANERY.IN
- Alt text: Bar pairs of CIFAR-10 likelihood and FID where the bound-trained models score better likelihood but worse FID.
- Long description: DDPM on unconditional CIFAR-10 with a linear schedule and fixed variance: the true bound gives an NLL upper bound of 3.70 bits per dimension and FID 13.51; the simple loss gives 3.75 and FID 3.17. Improved DDPM on CIFAR-10 at 500K iterations, 4,000 steps and a cosine schedule: the bound gives 2.94 and FID 11.47, the hybrid loss 3.17 and 3.19, the simple loss 3.26 and 3.05. The two papers use different setups.
- Keywords: DDPM, Improved DDPM, CIFAR-10, FID, bits per dimension, hybrid loss, likelihood
- Canonical URL: https://canery.in/blogs/diffusion-math-derived

### feed-06-one-loss-many-weightings

- File: `assets/social/feed-06-one-loss-many-weightings.png`
- Title: One loss, many weightings
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: every published diffusion loss is one integral of the noise error over log-SNR with its own weighting function.
- Technical source: "Is every diffusion loss the same loss?", Figure 7, ledger row L24 (Kingma & Gao 2023, Table 1)
- Visual structure: header; a white table of five losses and their weighting formulas; a source note; takeaway; footer.
- Visible-text transcript: Canery.in · 06 / 07 · One loss, many weightings. · Every published diffusion loss is one integral of the noise error over log-SNR. Only the weight in front changes. · LOSS · WEIGHT W(λ) ON THE NOISE ERROR · ELBO 1 · ε-prediction, cosine sech(λ/2) · v-prediction, cosine e^(−λ/2) · EDM N(λ; 2.4, 2.4²)(e^−λ + 0.25) · Min-SNR, γ = 5 sech(λ/2)·min(1, 5e^−λ) · λ = log SNR. Formulas as tabulated by Kingma & Gao, NeurIPS 2023. · Picking a prediction target is picking one of these weights, whether you meant to or not. · WHERE THE DIFFUSION MSE LOSS COMES FROM · CANERY.IN
- Alt text: A table of five diffusion losses and their weighting functions over log signal-to-noise ratio.
- Long description: In log-SNR coordinates the continuous-time ELBO weights the noise error uniformly (weight 1). Epsilon prediction with the cosine schedule has weight sech(λ/2); v-prediction with the cosine schedule has e^(−λ/2); EDM has a Gaussian in λ centred at 2.4 with standard deviation 2.4, times e^(−λ) + 0.25; Min-SNR with γ = 5 has sech(λ/2) times min(1, 5e^(−λ)). The formulas are those tabulated by Kingma and Gao (NeurIPS 2023).
- Keywords: loss weighting, log-SNR, ELBO, v-prediction, EDM, Min-SNR, diffusion objectives
- Canonical URL: https://canery.in/blogs/diffusion-math-derived

### feed-07-read-the-article

- File: `assets/social/feed-07-read-the-article.png`
- Title: Three formulations, one object
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: DDPM, NCSN and the score SDE differ in scale, limit and weight, not in what the network learns; read the full derivation.
- Technical source: "How are DDPM, NCSN and the SDE one object?", Figures 10 and 11, ledger rows L21, L36 and L24
- Visual structure: header; a white panel with four entries (DDPM, NCSN, VP ↔ VE, the loss), each a heading and two mono lines; takeaway; orange CTA footer with the article URL.
- Visible-text transcript: Canery.in · 07 / 07 · Three formulations, one object. · DDPM, NCSN and the score SDE learn the same function of the same noisy input. They differ in scale, limit and weight. · DDPM variance-preserving chain · predicts ε · T → ∞ gives the VP SDE · NCSN variance-exploding ladder · predicts the score · levels → ∞ gives the VE SDE · VP ↔ VE divide x by √ᾱ: σ = 1/√SNR · same information, known scale · the loss ½∫ w(λ) · (noise error)² dλ · ELBO, simple loss, DSM: three weights · The full derivation, on part 1's numbers, with a lab script that checks every identity. · READ IT AT CANERY.IN/BLOGS/DIFFUSION-MATH-DERIVED
- Alt text: Summary panel: DDPM and NCSN become the VP and VE SDEs, related by rescaling, sharing one weighted loss.
- Long description: DDPM is a variance-preserving chain whose network predicts noise; as the step count goes to infinity it becomes the VP SDE. NCSN is a variance-exploding ladder whose network predicts the score; in the limit it becomes the VE SDE. Dividing a VP sample by the square root of the signal coefficient gives a VE sample with noise level one over the square root of the SNR. All of them train on half an integral of a weighted squared noise error over log-SNR, and the ELBO, the simple loss and denoising score matching are three choices of that weight.
- Keywords: DDPM, NCSN, score SDE, variance preserving, variance exploding, denoising score matching, diffusion
- Canonical URL: https://canery.in/blogs/diffusion-math-derived

### story-01-your-mse-is-a-bound

- File: `assets/social/story-01-your-mse-is-a-bound.png`
- Title: Your MSE loss is a likelihood bound
- Platforms: Instagram Story
- Role: cover
- Dimensions: 1080×1920
- Narrative beat: each denoising step is scored by a KL between two equal-width Gaussians, which is a squared error.
- Technical source: Worked example ("The price"), Figure 1, ledger rows L05 and L07
- Visual structure: lockup and counter; serif title; two-line deck; teacher and student curves with the gap bracket; a box with the KL value; takeaway; footer.
- Visible-text transcript: Canery.in · 01 / 04 · Your MSE loss is a likelihood bound. · Each denoising step is scored by a KL between two Gaussians of equal width. · gap 0.0745 · STUDENT · NETWORK · TEACHER · KNOWS x₀ · KL = 0.0250 nats · = 0.625 × (noise error)² · Equal widths leave only the centres to compare: a squared error. · WHERE THE DIFFUSION MSE LOSS COMES FROM · CANERY.IN
- Alt text: Teacher and network bell curves of equal width, 0.0745 apart, with a KL of 0.025 nats.
- Long description: The forward posterior for one pixel (mean 0.6857, variance 1/9) and the network's step (mean 0.6112, same variance) differ only in their centres, by 0.0745. The KL between them is 0.0250 nats, which is 0.625 times the squared noise error.
- Keywords: diffusion model, ELBO, KL divergence, MSE loss, Gaussian
- Canonical URL: https://canery.in/blogs/diffusion-math-derived

### story-02-one-error-five-prices

- File: `assets/social/story-02-one-error-five-prices.png`
- Title: One error, five prices
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: the same error in every target converts back to 0.04; the bound's KL is 0.625 times that.
- Technical source: Worked example ("One error, five prices"), Figure 2
- Visual structure: header; a white panel of four rows with squared error and converted value, then an orange KL row; takeaway; footer.
- Visible-text transcript: Canery.in · 02 / 04 · One error, five prices. · A +0.20 noise error, priced as each target a diffusion network can predict. · noise ε 0.0400 → 0.0400 · clean pixel x₀ 0.0225 → 0.0400 · score 0.1111 → 0.0400 · velocity v 0.0625 → 0.0400 · the bound's KL 0.0250 = 0.625 × 0.04 · Same minimiser at every noise level. Only the weights across levels differ. · WHERE THE DIFFUSION MSE LOSS COMES FROM · CANERY.IN
- Alt text: Four squared errors, 0.04, 0.0225, 0.1111 and 0.0625, each converting to 0.04, and a KL of 0.025.
- Long description: At signal level 0.64, one noise error of +0.20 is 0.04 in noise units, 0.0225 as a clean-pixel error, 0.1111 as a score error and 0.0625 as a velocity error; each converts back to 0.04 by a constant fixed by the noise level. The bound's KL for the step is 0.0250, which is 0.625 times 0.04.
- Keywords: epsilon prediction, v prediction, score, loss weighting, diffusion
- Canonical URL: https://canery.in/blogs/diffusion-math-derived

### story-03-noisy-targets-exact-average

- File: `assets/social/story-03-noisy-targets-exact-average.png`
- Title: Noisy targets, exact average
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: denoising-score-matching targets are noisy, but their average at each noisy value is exactly the score.
- Technical source: "Where does the score come from?", Figure 9, ledger rows L32 and L25; lab/loss_identities.py section 5
- Visual structure: header; a white panel with a legend row, 600 grey dots on three lines, black squares of bin averages, and the orange exact score curve; takeaway; footer.
- Visible-text transcript: Canery.in · 03 / 04 · Noisy targets, exact average. · Each target is a single noise draw. Their average is the score. · ONE NOISY TARGET · THEIR AVERAGE · EXACT SCORE · Regression finds the average of its target. That is why denoising learns a score. · WHERE THE DIFFUSION MSE LOSS COMES FROM · CANERY.IN
- Alt text: Scatter of noisy targets on three lines, with their bin averages lying on the exact score curve.
- Long description: For a toy dataset of three grey levels (−0.85, 0.10, 0.95) noised to signal level 0.64, each training pair's target is minus its noise draw divided by 0.6, so the 600 dots fall on three straight lines, one per clean level. The averages of the targets in each bin, from 6,000 simulated samples, lie on the exact score of the noised data. The data are simulated, not from a trained model.
- Keywords: denoising score matching, score function, Tweedie, regression, diffusion
- Canonical URL: https://canery.in/blogs/diffusion-math-derived

### story-04-read-the-article

- File: `assets/social/story-04-read-the-article.png`
- Title: Five steps from a likelihood to an MSE
- Platforms: Instagram Story
- Role: cta
- Dimensions: 1080×1920
- Narrative beat: the derivation in five steps, four exact and one a choice; read the full article.
- Technical source: "The problem" and the section structure of the article; ledger rows L02, L03, L05, L07 and L09
- Visual structure: header; an orange-tinted panel listing five numbered steps; takeaway; orange CTA pointing at the link sticker.
- Visible-text transcript: Canery.in · 04 / 04 · Five steps from a likelihood to an MSE. · Four are exact. The last one is a choice. · 1 Jensen's inequality: log p(x) ≥ ELBO · 2 Bayes on each forward step · 3 KL of equal-width Gaussians = squared error · 4 write the mean through the noise · 5 drop the weights → the simple loss · The full derivation is on Canery. · LINK IN THE STICKER ABOVE
- Alt text: Five numbered steps from the log-likelihood to the simple diffusion loss, the last marked as the only choice.
- Long description: The steps are Jensen's inequality to obtain the ELBO, Bayes' rule on each forward step to decompose it into per-step KLs, the identity that a KL between equal-variance Gaussians is a squared error between means, rewriting the means through the noise, and dropping the per-step weights to obtain DDPM's simple loss. The first four are exact.
- Keywords: ELBO, diffusion model, derivation, DDPM, simple loss
- Canonical URL: https://canery.in/blogs/diffusion-math-derived
