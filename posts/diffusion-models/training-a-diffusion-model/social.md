---
social_schema: 2
canonical_url: "https://canery.in/blogs/training-a-diffusion-model"
---

# Social publishing package — training-a-diffusion-model

## LinkedIn post

Stable Diffusion's last training step is supposed to be pure noise. It still carries 6.8% of the image's amplitude.

In a 4×4 patch that leak is invisible: 0.04 noise standard deviations in the patch's mean. In Stable Diffusion's 16,384-value latent it is 1.42, large enough for a network to learn to read. The sampler then starts from true noise, and the model reads "average brightness" from every start. With a perfect denoiser on that schedule, the lab's 16,384-value toy images keep 35% of their brightness spread, and more sampling steps converge on that wrong answer instead of away from it.

The endpoint is one of five decisions fixed before a diffusion model's first gradient step:

→ The schedule decides which noise levels training visits and how often. Resolution moves it: an image four times wider needs every log-SNR shifted down by 2.8.
→ The endpoint must be pure noise. Lin et al.'s rescale moves the middle of the schedule from ᾱ = 0.64 to 0.617 and the last step to exactly zero.
→ The target, ε, x₀ or v, shares one minimiser but not one amplifier. An ε-network's error reaches the clean image multiplied by 90 at log-SNR −9; v never multiplies an error by more than one.
→ The loss weighting decides which noise levels the network gets right. In the lab, SNR weighting starved the noisiest levels, and its samplers blew up in 80 of 84 evaluations.
→ The EMA decay is a half-life. 0.9999 means 6,931 steps, and after 5,000 steps 61% of that average is still the random initialisation.

Every measured number comes from a CPU lab whose toy dataset has an exact denoiser, so each error is measured against the best any network could do. Published results are quoted with their setup.

Part 5 of the Diffusion Models series.

## LinkedIn first comment

Schedule, endpoint, target, weighting and EMA: five config lines fixed before step one, and what each one costs.

Read the full article on Canery: https://canery.in/blogs/training-a-diffusion-model

## Instagram caption

Stable Diffusion's last training step keeps 6.8% of the image's amplitude. That small leak pulls generated brightness toward the middle.

Swipe through the leak in samples, why it hides in a 4×4 patch and shows in a 16,384-value latent, why more steps can't fix it, the four-line fix, what each prediction target amplifies, and what a loss weighting really buys.

Every number was measured in a lab you can run on a laptop CPU, or is quoted from its paper with the setup.

Link in bio.

#diffusionmodels #machinelearning #deeplearning #generativeai #stablediffusion #modeltraining #computervision

## Shared feed order

1. `assets/social/feed-01-the-last-step-is-not-noise.png` — the same starting noise through the rescaled schedule and through Stable Diffusion's: varied brightness against grey
2. `assets/social/feed-02-the-leak-lives-in-the-mean.png` — the leaked mean in noise standard deviations, from 16 to 16,384 values
3. `assets/social/feed-03-more-steps-cannot-fix-it.png` — brightness spread kept from 25 to 200 sampling steps: the flaw is a fixed point
4. `assets/social/feed-04-the-fix-is-four-lines.png` — Lin et al.'s rescale in four lines of code, and what it moves
5. `assets/social/feed-05-same-answer-different-amplifier.png` — how ε, x₀ and v outputs amplify an error into the clean-image estimate
6. `assets/social/feed-06-a-weighting-is-a-budget.png` — measured error at both ends of the noise range for three weightings
7. `assets/social/feed-07-read-the-article.png` — the five decisions and the CTA

## Instagram Story

- CTA: Five decisions you make before a diffusion model's first training step, each tested in a lab you can run — tap the link.
- Link sticker label: Read the article
- Link sticker URL: https://canery.in/blogs/training-a-diffusion-model

### Story order

1. `assets/social/story-01-the-last-step-is-not-noise.png` — Overlay: Same noise. One schedule keeps 35% of the brightness.
2. `assets/social/story-02-the-leak-lives-in-the-mean.png` — Overlay: 0.04 s.d. in a 4×4 patch. 1.42 in SD's latent.
3. `assets/social/story-03-an-ema-is-a-half-life.png` — Overlay: 0.9999 is a 6,931-step half-life.
4. `assets/social/story-04-read-the-article.png` — Overlay: Five decisions before step one. Link above.

## Asset metadata

### feed-01-the-last-step-is-not-noise

- File: `assets/social/feed-01-the-last-step-is-not-noise.png`
- Title: Stable Diffusion's last step isn't pure noise
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: the same starting noise through the rescaled schedule and through Stable Diffusion's: the shapes are right, the brightness is pulled to the middle
- Technical source: article section "Why must the last step be pure noise?", Figure 6, ledger L07, lab captures (leak, 16,384 pixels)
- Visual structure: lockup and counter; serif headline; deck with the last training input; two rows of six crescent tiles from the same starting noise, rescaled above and Stable Diffusion's below, each with its mean brightness; an orange-tinted box with the spread kept; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 07 · Stable Diffusion's last · step isn't pure noise. · Its last training input is 0.068·x₀ + 0.998·ε. Train on · that and even a perfect denoiser pulls brightness to the middle. · SAME NOISE · LAST STEP PURE NOISE (RESCALED) · −0.09 · +0.19 · −0.50 · −0.35 · +0.10 · −0.02 · SAME NOISE · STABLE DIFFUSION'S SCHEDULE · −0.04 · +0.08 · −0.21 · −0.15 · +0.04 · −0.01 · brightness spread kept: 35.4% · rescaled: 85.1% with 50 steps, toward 100% with more · The flaw is the schedule's endpoint, not the network: · measured with an exact denoiser at 16,384 pixels. · TRAINING A DIFFUSION MODEL · CANERY.IN
- Alt text: Two rows of crescent samples from the same noise: varied brightness with a pure-noise last step, near-uniform grey under Stable Diffusion's
- Long description: Twelve 128×128 crescent images generated by an exact denoiser with a 50-step deterministic sampler from the same six starting noises. Top row, the zero-terminal-SNR rescaled schedule: mean brightness −0.09, +0.19, −0.50, −0.35, +0.10 and −0.02. Bottom row, Stable Diffusion's schedule: −0.04, +0.08, −0.21, −0.15, +0.04 and −0.01, each pulled toward zero. Over 4,000 samples, Stable Diffusion's schedule keeps 35.4% of the data's brightness spread and the rescaled one 85.1% with 50 steps, approaching 100% with more. The shapes are right in both rows and the denoiser is exact, so the schedule's endpoint is the cause.
- Keywords: Stable Diffusion, noise schedule, zero terminal SNR, signal leak, brightness, diffusion training, exact denoiser
- Canonical URL: https://canery.in/blogs/training-a-diffusion-model

### feed-02-the-leak-lives-in-the-mean

- File: `assets/social/feed-02-the-leak-lives-in-the-mean.png`
- Title: The leak lives in the mean
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: averaging n values shrinks the noise in their mean by √n but leaves the leaked signal alone, so the same leak is invisible in a 4×4 patch and readable in a latent
- Technical source: article section "Worked example", Figure 2, ledger L05 and L07
- Visual structure: headline and deck; four horizontal bars, one per size (16, 256, 4,096 and 16,384 values), each the leaked mean in noise standard deviations, with a dashed marker at one standard deviation; the 16,384 bar in orange; takeaway
- Visible-text transcript: Canery.in · 02 / 07 · The leak lives · in the mean. · The last step keeps 6.8% of the image's amplitude. Averaging · n values shrinks the noise in their mean by √n, not the signal. · 16 · part 1's 4×4 patch · 0.04 s.d. · 256 · 16×16 · 0.18 s.d. · 4,096 · 64×64 · 0.71 s.d. · 16,384 · SD's 4×64×64 latent · 1.42 s.d. · 1 noise s.d. · The same leaked mean is 0.04 noise s.d. in a 4×4 patch · and 1.42 s.d. in Stable Diffusion's 16,384-value latent. · TRAINING A DIFFUSION MODEL · CANERY.IN
- Alt text: Bars of the leaked mean in noise standard deviations: 0.04 at 16 values, 0.18 at 256, 0.71 at 4,096 and 1.42 at 16,384
- Long description: The series' 4×4 crescent patch has mean −0.1625. Stable Diffusion's last step multiplies it by 0.068265, leaking −0.0111 into the mean of the input, while the noise in a mean of n values has standard deviation 0.9977/√n. Holding that mean fixed, the leak is 0.04 noise standard deviations at 16 values, 0.18 at 256, 0.71 at 4,096 and 1.42 at 16,384, the size of Stable Diffusion's 4×64×64 latent for a 512×512 image. A dashed marker shows one standard deviation. A signal that large is one a network can learn to read.
- Keywords: signal leak, terminal SNR, latent, averaging, square root of n, Stable Diffusion, noise schedule
- Canonical URL: https://canery.in/blogs/training-a-diffusion-model

### feed-03-more-steps-cannot-fix-it

- File: `assets/social/feed-03-more-steps-cannot-fix-it.png`
- Title: More sampling steps can't fix it
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the flawed schedule converges on the closed form's 0.357 as steps grow, while the rescaled schedule's shortfall shrinks toward 1
- Technical source: article section "What the leak does, with a perfect denoiser", Figure 7, lab captures (leak step sweep)
- Visual structure: headline and deck; a line chart of spread kept at 25, 50, 100 and 200 steps: an orange line rising from 0.726 to 0.964 for zero terminal SNR, and a dark line flat at 0.355 to 0.357 for Stable Diffusion's schedule on a dashed closed-form line; takeaway
- Visible-text transcript: Canery.in · 03 / 07 · More sampling steps · can't fix it. · Fraction of the data's brightness spread that samples keep, · for 25 to 200 deterministic sampling steps. · 0.00 · 0.25 · 0.50 · 0.75 · 1.00 · closed form 0.357 · 0.355 · 0.356 · 0.357 · 0.357 · 0.726 · 0.857 · 0.927 · 0.964 · 25 · 50 · 100 · 200 · SAMPLING STEPS · 16,384 PIXELS · EXACT DENOISER · ZERO TERMINAL SNR · STABLE DIFFUSION'S SCHEDULE · A training/sampling mismatch is a fixed point. After the · rescale, what is left is ordinary sampler error. · TRAINING A DIFFUSION MODEL · CANERY.IN
- Alt text: Line chart of brightness spread kept from 25 to 200 steps: Stable Diffusion's schedule flat at 0.357, the rescaled one rising to 0.964
- Long description: Measured with an exact denoiser at 16,384 pixels on a draw of 1,000 samples, sampling deterministically with 25, 50, 100 and 200 steps. Under Stable Diffusion's schedule the samples keep 0.355, 0.356, 0.357 and 0.357 of the data's brightness spread, converging on the closed-form 0.357 drawn as a dashed line: more steps approach the wrong answer more precisely. Under the zero-terminal-SNR rescale they keep 0.726, 0.857, 0.927 and 0.964, approaching 1 as the sampler's own error shrinks.
- Keywords: sampling steps, DDIM, terminal SNR, fixed point, noise schedule, sampler error, diffusion model
- Canonical URL: https://canery.in/blogs/training-a-diffusion-model

### feed-04-the-fix-is-four-lines

- File: `assets/social/feed-04-the-fix-is-four-lines.png`
- Title: The fix is four lines
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Lin et al.'s rescale keeps the first √ᾱ, sends the last to zero and barely moves the middle; three follow-on changes make it usable
- Technical source: article sections "Worked example" and "What the fix costs", ledger L09, L11, L12 and L16
- Visual structure: headline and deck; a white code panel with four lines of Python; three labelled results: the middle of the schedule, the last step, and what to change next; takeaway
- Visible-text transcript: Canery.in · 04 / 07 · The fix is · four lines. · Lin et al.: keep √ᾱ at the first step, move it to zero at · the last, and rescale every step between linearly. · r = abar.sqrt() · r0, rT = r[0], r[-1] · r = (r - rT) * r0 / (r0 - rT) · abar = r ** 2 · IN THE MIDDLE · ᾱ = 0.640 → 0.617 · AT THE LAST STEP · ᾱ = 0.00466 → 0 · THEN · predict v, start at t = T, sample via x₀ · It barely moves the middle of the schedule and makes · the last training input pure noise. · TRAINING A DIFFUSION MODEL · CANERY.IN
- Alt text: Four lines of Python that rescale a noise schedule, moving ᾱ from 0.640 to 0.617 mid-schedule and from 0.00466 to zero at the last step
- Long description: Lin et al.'s zero-terminal-SNR rescale as four lines of code: take the square root of ᾱ, note its first and last values, shift and stretch so the first value is kept and the last becomes zero, and square back. On Stable Diffusion's schedule the series' running noise level ᾱ = 0.640 moves only to 0.617, while the last step's ᾱ goes from 0.00466 to exactly zero. Then the model predicts v, the sampler starts at t = T, and sampling goes through x₀, because an ε-based conversion divides by zero at the new last step.
- Keywords: zero terminal SNR, noise schedule, rescale, Lin et al., v-prediction, trailing timesteps, PyTorch
- Canonical URL: https://canery.in/blogs/training-a-diffusion-model

### feed-05-same-answer-different-amplifier

- File: `assets/social/feed-05-same-answer-different-amplifier.png`
- Title: ε, x₀ or v: same answer, new amplifier
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the three targets share a minimiser but multiply an output error by different amounts on its way into the clean-image estimate
- Technical source: article section "Which target should the network predict?", Figure 9 and the amplification table in "The math", ledger L31
- Visual structure: headline and deck; a log-scale chart of amplification against log-SNR from −10 to 10: a dark ε line falling from about 100, a flat blue x₀ line at 1, an orange v line at or below 1; a dot marking ×90 at λ = −9; takeaway
- Visible-text transcript: Canery.in · 05 / 07 · ε, x₀ or v: same · answer, new amplifier. · How much an output error grows on its way into the · clean-image estimate a sampler uses, by target. · 0.01 · 0.1 · 1 · 10 · 100 · −10 · −5 · 0 · 5 · 10 · LOG-SNR λ ← NOISIER · CLEANER → · ε output · x₀ output · v output · ×90 at λ = −9 · v never amplifies an error by more than one, and it · survives a zero-SNR last step, where ε divides by zero. · TRAINING A DIFFUSION MODEL · CANERY.IN
- Alt text: Log-scale curves of error amplification against log-SNR: ε reaches ×90 at λ = −9, x₀ stays at 1, and v never exceeds 1
- Long description: Amplification of an output error into the clean-image estimate, against log-SNR λ from −10 (noisier) to 10 (cleaner) on a log scale. An ε-network's error is multiplied by e^(−λ/2), which is 90 at λ = −9 and falls below 1 for positive λ. An x₀-network's error passes through unchanged, a flat line at 1. A v-network's error is multiplied by √(1−ᾱ), never more than 1. v also survives a zero-SNR last step, where converting from ε divides by zero.
- Keywords: prediction target, epsilon prediction, x0 prediction, v-prediction, log-SNR, error amplification, diffusion training
- Canonical URL: https://canery.in/blogs/training-a-diffusion-model

### feed-06-a-weighting-is-a-budget

- File: `assets/social/feed-06-a-weighting-is-a-budget.png`
- Title: A loss weighting is a capacity budget
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: one network cannot win at every noise level; each weighting buys accuracy at one end with error at the other, and SNR weighting starves the levels samplers start from
- Technical source: article section "Which noise levels should win the loss?", Figure 11, lab captures (weighting runs)
- Visual structure: headline and deck; a table with columns for the weighting, the excess error at λ = −9, the excess error at λ = +9 and the median sample distance, for constant, Min-SNR-5 and SNR weighting, with the exact denoiser's own error as a reference row; a note on the sample metric; takeaway
- Visible-text transcript: Canery.in · 06 / 07 · A loss weighting is · a capacity budget. · Excess error over the exact denoiser at the two ends of · the noise range: x₀-network, three seeds, 40,000 steps. · WEIGHTING · λ = −9 · NOISIEST · λ = +9 · CLEANEST · SAMPLES · constant · 0.0014 · 0.0105 · 0.105 · Min-SNR-5 · 0.15 · 0.0028 · 0.098 · SNR (ε-loss) · 1.25 · 0.0036 · blew up · exact denoiser's error · 0.55 · 0.0001 · samples: median sliced distance to the data, lower is better; · two independent draws of the data score 0.063. · One network can't win everywhere. SNR weighting starved · the noise levels every sampler starts from. · TRAINING A DIFFUSION MODEL · CANERY.IN
- Alt text: Table of measured error at both ends of the noise range for three loss weightings: SNR weighting's noisiest-level error is 1.25 and its samples blew up
- Long description: Excess error over the exact denoiser for an x₀-predicting network after 40,000 steps, three seeds. Constant weighting: 0.0014 at λ = −9, the noisiest level, and 0.0105 at λ = +9, the cleanest, with samples at a median sliced distance of 0.105 from the data. Min-SNR-5: 0.15 and 0.0028, samples at 0.098. SNR weighting, the plain ε-loss's weighting: 1.25 and 0.0036, and its samplers blew up in 80 of 84 evaluations. The exact denoiser's own error is 0.55 at λ = −9 and 0.0001 at λ = +9, and two independent draws of the data score 0.063.
- Keywords: loss weighting, Min-SNR, SNR weighting, diffusion training, noise levels, capacity, exact denoiser
- Canonical URL: https://canery.in/blogs/training-a-diffusion-model

### feed-07-read-the-article

- File: `assets/social/feed-07-read-the-article.png`
- Title: Decide before step one
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: the five decisions in one list, and where to read the article
- Technical source: Key takeaways; ledger L07; lab captures (schedules)
- Visual structure: headline and deck; a white panel of five headed lines, one per decision; takeaway; orange CTA footer with the article URL
- Visible-text transcript: Canery.in · 07 / 07 · Decide before · step one. · Five training decisions, each tested in a lab you · can run on a laptop. · Schedule · its endpoints and density; resolution shifts it · Endpoint · SD's last step keeps 6.8% of the image's amplitude · Target · an ε error grows ×90 at λ = −9; v's never grows · Weighting · it decides which noise levels the network gets right · EMA · a decay of 0.9999 is a 6,931-step half-life · Each is one config line, fixed before the first gradient · step and paid for in every step after. · READ IT AT CANERY.IN/BLOGS/TRAINING-A-DIFFUSION-MODEL
- Alt text: A list of five training decisions, from schedule and endpoint to target, weighting and EMA, each with one fact, and the article link
- Long description: A closing card listing the five decisions fixed before a diffusion model's first gradient step. Schedule: its endpoints and density decide which noise levels exist, and resolution shifts it. Endpoint: Stable Diffusion's last step keeps 6.8% of the image's amplitude. Target: an ε-network's error grows 90 times at log-SNR −9 on its way into the clean image, and v's never grows. Weighting: it decides which noise levels the network gets right. EMA: a decay of 0.9999 is a 6,931-step half-life. Each is one config line, fixed before the first step and paid for in every step after. The call to action reads: read it at canery.in/blogs/training-a-diffusion-model.
- Keywords: diffusion model training, noise schedule, terminal SNR, prediction target, loss weighting, EMA
- Canonical URL: https://canery.in/blogs/training-a-diffusion-model

### story-01-the-last-step-is-not-noise

- File: `assets/social/story-01-the-last-step-is-not-noise.png`
- Title: Stable Diffusion's last step isn't noise
- Platforms: Instagram Story
- Role: cover
- Dimensions: 1080×1920
- Narrative beat: the paired samples recomposed for a vertical frame, each with its brightness
- Technical source: article section "Why must the last step be pure noise?", Figure 6, lab captures (leak, 16,384 pixels)
- Visual structure: lockup and counter; serif headline; two-line deck; two rows of four crescent tiles from the same noise, rescaled above and Stable Diffusion's below, each with its mean brightness; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 04 · Stable Diffusion's last · step isn't noise. · A perfect denoiser on its schedule · keeps 35% of the data's brightness spread. · SAME NOISE · LAST STEP PURE NOISE (RESCALED) · −0.09 · +0.19 · −0.50 · −0.35 · SAME NOISE · STABLE DIFFUSION'S SCHEDULE · −0.04 · +0.08 · −0.21 · −0.15 · The endpoint, not the network, · pulls every image to the middle. · TRAINING A DIFFUSION MODEL · CANERY.IN
- Alt text: Four crescents from the same noise in two rows: brightness from −0.50 to +0.19 when rescaled, squeezed to −0.21 to +0.08 under SD
- Long description: Eight 128×128 crescent images generated by an exact denoiser from the same four starting noises. Top row, the zero-terminal-SNR schedule: mean brightness −0.09, +0.19, −0.50 and −0.35. Bottom row, Stable Diffusion's schedule: −0.04, +0.08, −0.21 and −0.15, the same shapes with their brightness pulled toward the middle. Over 4,000 samples, Stable Diffusion's schedule keeps 35% of the data's brightness spread. The endpoint, not the network, causes it.
- Keywords: Stable Diffusion, terminal SNR, signal leak, noise schedule, brightness, exact denoiser
- Canonical URL: https://canery.in/blogs/training-a-diffusion-model

### story-02-the-leak-lives-in-the-mean

- File: `assets/social/story-02-the-leak-lives-in-the-mean.png`
- Title: The leak lives in the mean
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: the leak in noise standard deviations at four sizes, in a vertical frame
- Technical source: article section "Worked example", Figure 2, ledger L05 and L07
- Visual structure: lockup and counter; headline; deck; four bars for 16, 256, 4,096 and 16,384 values with a dashed marker at one noise standard deviation; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 04 · The leak lives · in the mean. · Average n values: the noise in · their mean shrinks by √n. · 16 · part 1's 4×4 patch · 0.04 s.d. · 256 · 16×16 · 0.18 s.d. · 4,096 · 64×64 · 0.71 s.d. · 16,384 · SD's 4×64×64 latent · 1.42 s.d. · 1 noise s.d. · Hidden in a 4×4 patch, · readable in a 4×64×64 latent. · TRAINING A DIFFUSION MODEL · CANERY.IN
- Alt text: Four bars of the leaked mean: 0.04 noise s.d. in a 4×4 patch, rising to 1.42 in Stable Diffusion's 16,384-value latent
- Long description: The same leaked mean measured against the noise in a mean of n values: 0.04 standard deviations at 16 values (the series' 4×4 patch), 0.18 at 256, 0.71 at 4,096 and 1.42 at 16,384, the size of Stable Diffusion's 4×64×64 latent. The noise in a mean shrinks as √n while the leaked signal does not, so a leak hidden in a small patch becomes readable in a latent.
- Keywords: signal leak, terminal SNR, latent, averaging, Stable Diffusion, noise schedule
- Canonical URL: https://canery.in/blogs/training-a-diffusion-model

### story-03-an-ema-is-a-half-life

- File: `assets/social/story-03-an-ema-is-a-half-life.png`
- Title: An EMA decay is a half-life
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: an EMA initialised at random keeps the random start with weight β^t; with 0.9999 it dominates early and fades late
- Technical source: article section "What does the EMA buy, and how long should it be?", Figure 13, ledger L49, lab captures (weighting runs)
- Visual structure: lockup and counter; headline; deck; a white panel with the decay and half-life, then two blocks, after 5,000 and after 40,000 steps, each with the initialisation's share in orange and the measured sample distance; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 04 · An EMA decay · is a half-life. · Half of a 0.9999 average's weight · sits on the last 6,931 steps. · EMA DECAY 0.9999 · HALF-LIFE 6,931 STEPS · after 5,000 steps · 61% of it is the random start · samples 6.3× further from the data than raw · after 40,000 steps · 1.8% of it is the random start · distance 0.25 against raw 0.14 · Match the average to the run, · or use a power-function EMA. · TRAINING A DIFFUSION MODEL · CANERY.IN
- Alt text: EMA decay 0.9999: after 5,000 steps 61% of it is the random start and samples sit 6.3× further from the data; after 40,000, 1.8%
- Long description: An exponential moving average with decay 0.9999 has a half-life of 6,931 steps: half its weight sits on the last 6,931 steps. Initialised from the random starting weights, it still gives them weight 0.9999 to the power t. After 5,000 steps that is 61%, and in the lab's nine stable runs the average's samples were 6.3 times further from the data than the raw weights'. After 40,000 steps it is 1.8%, and the median sample distance was 0.25 against 0.14 for the raw weights. Match the average to the run's length, or use a power-function EMA.
- Keywords: EMA, exponential moving average, half-life, EDM2, power-function EMA, weight averaging
- Canonical URL: https://canery.in/blogs/training-a-diffusion-model

### story-04-read-the-article

- File: `assets/social/story-04-read-the-article.png`
- Title: Decide before step one
- Platforms: Instagram Story
- Role: cta
- Dimensions: 1080×1920
- Narrative beat: what the article covers, and where the link is
- Technical source: the article's section list
- Visual structure: lockup and counter; headline; deck; an orange-tinted panel listing five numbered topics; takeaway; orange CTA footer pointing to the link sticker
- Visible-text transcript: Canery.in · 04 / 04 · Decide before · step one. · Five decisions, each tested in · a lab you can run on a laptop. · 1 · the schedule: endpoints and density · 2 · the endpoint: the leak in the mean · 3 · the target: ε, x₀, v and capacity · 4 · the weighting: a capacity budget · 5 · the EMA, and how training scales · The full article is on Canery. · LINK IN THE STICKER ABOVE
- Alt text: A numbered list of the article's five topics, from the schedule and the leak to targets, weighting and the EMA, with a link pointer
- Long description: The closing Story frame lists what the article covers: the schedule's endpoints and density, the endpoint and the leak in the mean, the prediction target (ε, x₀ or v) and network capacity, the loss weighting as a capacity budget, and the EMA with how training scales. Each decision was tested in a lab you can run on a laptop. The call to action points to the link sticker above.
- Keywords: diffusion models, training, noise schedule, prediction target, loss weighting, EMA
- Canonical URL: https://canery.in/blogs/training-a-diffusion-model
