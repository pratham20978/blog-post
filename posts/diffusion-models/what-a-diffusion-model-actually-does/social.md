---
social_schema: 2
canonical_url: "https://canery.in/blogs/what-a-diffusion-model-actually-does"
---
# Social publishing package — what-a-diffusion-model-actually-does

Private handoff. These assets are not in the image manifest, are not uploaded to MinIO, and are
never referenced from `blog.md`.

## LinkedIn post

A diffusion model has never once been asked to draw a picture.

It is shown an image you deliberately spoiled with a known amount of Gaussian noise, and asked a
single question: which noise did you add? That question has a free answer — you drew the noise
yourself a moment earlier — which is why training a diffusion model needs no labelled data at all.

Three things follow from that, and they are the three things people get wrong:

→ A single denoiser call at high noise returns a blur, and the blur is the *correct* answer. The
function that minimises squared error is the conditional mean: the average of every clean image
consistent with that input. A perfect network would return the same blur.

→ It takes many small steps because an error in the predicted noise is amplified by
√(1−ᾱ)/√ᾱ when you convert it back to an image. At ᾱ = 0.64 that multiplier is 0.75. At
ᾱ = 0.02 it is 7.00, so a 0.20 error arrives as 1.40 — wider than the entire pixel range.

→ The new image comes from the random tensor you start sampling from, not from anything the
network remembers. Two networks trained on non-overlapping halves of a dataset converge on the
same denoiser and, from the same seed, produce the same image — one that is in neither training
set (Kadkhodaie et al., ICLR 2024).

The honest qualification: memorisation is real and measured. Carlini et al. pulled 94 training
images out of Stable Diffusion — from 175 million generations, using the captions of the 350,000
most-duplicated training examples. Duplication in the training data is what predicts replication,
not model size.

Part 1 of a series on diffusion models. The full worked example — 16 real numbers through one
forward step and back — is in the article.

## LinkedIn first comment

The single most useful reframing: "diffusion model" names a system, not a network. The schedule is
fixed constants, the sampler is parameter-free arithmetic, the seed is a random draw, and only the
denoiser was ever trained. When you read that a new model is faster, the first question is which
of those four changed — because a sampler improvement and a denoiser improvement are not
comparable claims.

Read the full article on Canery: https://canery.in/blogs/what-a-diffusion-model-actually-does

## Instagram caption

It never learned to draw. It learned to guess the noise. 🌘

Spoil an image with a known amount of random noise, then ask a network which noise you added. You
already know the answer — you drew it — so the training target is free and nothing needs
labelling.

Swipe for the part that trips everyone up: one denoiser call returns a blur, and the blur is
right. Squared-error training drives the network to the average of every clean image that could
have produced its input. Sharpness comes from taking many small steps, not from the network being
cleverer.

And the new image? It comes from the random seed you start at. Card 6 has the measured numbers on
when that stops being true.

Part 1 of the Diffusion Models series. Link in bio.

#diffusionmodels #machinelearning #deeplearning #generativeai #computervision #ml #aiart #neuralnetworks #datascience #computerscience

## Shared feed order

1. `assets/social/feed-01-trained-only-to-undo-noise.png` — the premise, and the asymmetry between the two directions
2. `assets/social/feed-02-the-answer-key-is-free.png` — the worked example: why the training target costs nothing
3. `assets/social/feed-03-one-call-returns-an-average.png` — why a single call returns a blur, and why the blur is correct
4. `assets/social/feed-04-the-error-multiplier.png` — the arithmetic that forces many small steps
5. `assets/social/feed-05-the-schedule-is-configuration.png` — the schedule as a choice, not a layer
6. `assets/social/feed-06-where-the-new-image-comes-from.png` — novelty, and the measured boundary where it fails
7. `assets/social/feed-07-the-four-moving-parts.png` — the four components, and the call to read

## Instagram Story

- CTA: The full worked example — 16 numbers, one forward step, one reverse step — is in the article. Tap to read part 1.
- Link sticker label: Read the article
- Link sticker URL: https://canery.in/blogs/what-a-diffusion-model-actually-does

### Story order

1. `assets/social/story-01-trained-only-to-undo-noise.png` — Overlay: Trained only to undo noise. So where does a new image come from?
2. `assets/social/story-02-the-answer-key-is-free.png` — Overlay: The target is free — we drew the noise ourselves.
3. `assets/social/story-03-why-not-one-step.png` — Overlay: One step would amplify your worst guess by 7×.
4. `assets/social/story-04-read-the-article.png` — Overlay: Four moving parts. Only one was trained. Read part 1 →

## Asset metadata

### feed-01-trained-only-to-undo-noise

- File: `assets/social/feed-01-trained-only-to-undo-noise.png`
- Title: Trained only to undo noise
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: A diffusion model's forward direction is a closed-form formula with no parameters; the reverse direction is the only thing anyone trains.
- Technical source: Article section "The problem" and Figure 1; the forward equation is ledger claim L04, the closed form in Ho et al. 2020 §2 eq. (4).
- Visual structure: Canery lockup top-left with frame counter top-right; serif headline and setup line; a five-panel horizontal strip of a cell field running from pure grain at ᾱ = 0.012 to a clear crescent at ᾱ = 0.97, arrows between panels and the final panel outlined in tangerine; a scale rule under the strip; a white card holding the forward equation above the reverse expression; takeaway and series label in the footer.
- Visible-text transcript: Canery.in · 01 / 07 · Trained only to undo noise. · It is never shown a picture and asked to draw one. · ᾱ 0.012 · 0.97 · xₜ = √ᾱₜ · x₀ + √(1−ᾱₜ) · ε · forward · closed form · zero parameters · xₜ₋₁ = f( xₜ , t , εθ(xₜ, t) ) · reverse · no closed form · this is the network · Nothing on the first line is learned. Everything anyone trains lives on the second. · WHAT A DIFFUSION MODEL ACTUALLY DOES · CANERY
- Alt text: A crescent emerging from pure noise across five panels, above the closed-form forward equation and the learned reverse step.
- Long description: Five square fields of discrete cells run left to right. The leftmost, labelled ᾱ 0.012, is uniform grain with no visible structure. Each subsequent field has more signal, and the rightmost, labelled 0.97 and outlined in tangerine, shows a clear bright crescent on a dark ground. Below, a white card carries two lines: the forward equation xₜ = √ᾱₜ · x₀ + √(1−ᾱₜ) · ε marked "closed form, zero parameters", and beneath a dividing rule the reverse step xₜ₋₁ = f(xₜ, t, εθ(xₜ, t)) marked in tangerine as "no closed form, this is the network". The takeaway states that nothing on the first line is learned and everything anyone trains lives on the second.
- Keywords: diffusion model, forward process, noise schedule, alpha bar, denoiser, closed form
- Canonical URL: https://canery.in/blogs/what-a-diffusion-model-actually-does

### feed-02-the-answer-key-is-free

- File: `assets/social/feed-02-the-answer-key-is-free.png`
- Title: The answer key is free
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: The training target costs nothing, because the noise is drawn before it is added and then kept.
- Technical source: Article section "Worked example" and Figure 2; the same x₀, ε and ᾱ = 0.64 the article computes.
- Visual structure: Header, then three 4×4 grids of printed values side by side with "+" and "=" between them, each cell shaded by its value; two cells are marked — one in tangerine, one in blue — and traced into two callout boxes beneath; two lines of explanation; footer takeaway.
- Visible-text transcript: Canery.in · 02 / 07 · The answer key is free. · We draw the noise before adding it, so the target needs no labelling. · 0.8 · x₀ · 0.6 · ε · xₜ · 0.48 + 0.84 = 1.32 · brighter than any pixel x₀ had · −0.68 + 0.87 = 0.19 · near-black arrives mid-grey · ᾱₜ = 0.64, so the coefficients are exactly 0.8 and 0.6. · The network is shown xₜ and t. The target is the ε we already hold. · No annotator, no labels — a fresh training pair from any image, at any noise level, forever. · WHAT A DIFFUSION MODEL ACTUALLY DOES · CANERY
- Alt text: Three four-by-four grids of printed values — scaled signal, scaled noise and their sum — with two cells traced through the addition.
- Long description: The first grid holds 0.8 × x₀ with values from 0.76 down to −0.80. The second holds 0.6 × ε with values from 0.87 down to −0.81. The third holds their sum xₜ. Cells are shaded by value, dark for low and light for high. The top-right cell of each grid is ringed in tangerine and traced into a callout reading 0.48 + 0.84 = 1.32, brighter than any pixel x₀ had. A second cell, ringed in blue, is traced into −0.68 + 0.87 = 0.19, a near-black pixel arriving mid-grey. The card states that ᾱₜ = 0.64 makes the coefficients exactly 0.8 and 0.6, and that the target is the ε already held.
- Keywords: epsilon prediction, training target, forward process, self-supervision, alpha bar, worked example
- Canonical URL: https://canery.in/blogs/what-a-diffusion-model-actually-does

### feed-03-one-call-returns-an-average

- File: `assets/social/feed-03-one-call-returns-an-average.png`
- Title: One call returns an average
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: A single denoiser call returns the mean of every clean image consistent with its input, which is why one call gives a blur.
- Technical source: Article section "Why does one call blur and many calls draw?" and Figure 4; ledger claims L16 (MMSE denoiser, Kadkhodaie et al. §2.1) and L17 (Tweedie's formula, Efron 2011 eq. 1.4).
- Visual structure: Header; a noisy 6×6 patch on the left outlined in ink, a bordered group holding four distinct clean 6×6 patches in a 2×2 arrangement, and on the right the arithmetic mean of those four outlined in tangerine with a short arrow into it; a tangerine statement card below; footer takeaway.
- Visible-text transcript: Canery.in · 03 / 07 · One call returns an average. · Many clean patches explain the same noisy one. It cannot pick. · xₜ · ᾱ = 0.09 · vertical · horizontal · diagonal · blob · E[ x₀ | xₜ ] · Squared-error training drives the network to the mean of the candidates, not to one of them. · The blur is not the network being weak. A perfect network would return the same blur. · WHAT A DIFFUSION MODEL ACTUALLY DOES · CANERY
- Alt text: A noisy patch beside four clean patches that could have produced it, and the smeared mean the network is trained to output.
- Long description: On the left, a heavily noised 6×6 cell patch labelled xₜ at ᾱ = 0.09. In the centre, a bordered group of four clean 6×6 patches: a vertical split, a horizontal split, a diagonal split, and a centred blob. On the right, outlined in tangerine and labelled E[x₀ | xₜ], the cell-by-cell arithmetic mean of those four — a soft gradient with none of their edges. A tangerine arrow points from the group into it. The statement card says squared-error training drives the network to the mean of the candidates rather than to any one of them.
- Keywords: conditional mean, MMSE denoiser, Tweedie formula, posterior mean, blur, squared error
- Canonical URL: https://canery.in/blogs/what-a-diffusion-model-actually-does

### feed-04-the-error-multiplier

- File: `assets/social/feed-04-the-error-multiplier.png`
- Title: The error multiplier
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: A prediction error is amplified by √(1−ᾱ)/√ᾱ when converted back into an image, and that factor is worst exactly where a one-step sampler would jump.
- Technical source: Article section "Why does one call blur and many calls draw?" and Figure 5; the multipliers are computed from the article's own rearrangement of the forward equation.
- Visual structure: Header; a white card stating the amplification rule in words and symbols; four rows, one per signal level, each with the ᾱ value on the left, a horizontal bar whose length is proportional to the multiplier, and the multiplier on the right, with the ᾱ = 0.02 row filled and outlined in tangerine; a one-line consequence; footer takeaway.
- Visible-text transcript: Canery.in · 04 / 07 · Why it takes many small steps. · A prediction error is amplified when it is turned back into an image. · an error δ in the predicted noise · lands as √(1−ᾱ)/√ᾱ × δ in the image · ᾱ = 0.96 × 0.20 · ᾱ = 0.64 × 0.75 · ᾱ = 0.25 × 1.73 · ᾱ = 0.02 × 7.00 · At ᾱ = 0.02 a 0.20 error arrives as 1.40 — wider than the pixel range. · Small steps keep the multiplier near 1, and each step re-reads a cleaner image. · WHAT A DIFFUSION MODEL ACTUALLY DOES · CANERY
- Alt text: Four rows of the error multiplier against the signal coefficient, drawn as bars to scale, rising from 0.20 to 7.00.
- Long description: A card states that an error δ in the predicted noise lands as √(1−ᾱ)/√ᾱ × δ in the image. Four rows follow. At ᾱ = 0.96 the bar is very short and the multiplier is ×0.20. At ᾱ = 0.64 it is ×0.75. At ᾱ = 0.25 it is ×1.73. At ᾱ = 0.02 the row is filled in pale tangerine, the bar runs nearly the full width, and the multiplier is ×7.00. Bar lengths are proportional to the multipliers on a common scale. The consequence line notes that a 0.20 error therefore arrives as 1.40, wider than the whole pixel range.
- Keywords: sampling steps, error amplification, signal to noise ratio, ancestral sampling, discretisation error
- Canonical URL: https://canery.in/blogs/what-a-diffusion-model-actually-does

### feed-05-the-schedule-is-configuration

- File: `assets/social/feed-05-the-schedule-is-configuration.png`
- Title: The schedule is configuration
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: The noise schedule is a fixed choice, not a learned layer, and it decides which noise levels the network ever practises on.
- Technical source: Article section "Where does 0.64 come from?" and Figure 3; the curves are evaluated from Ho et al. 2020 §4 (linear) and Nichol & Dhariwal 2021 eq. (17) (cosine); the readout values are computed, ledger claim L15.
- Visual structure: Header; a plotted axis pair with two curves of the signal coefficient against normalised timestep — the linear schedule solid, the cosine schedule dashed — labelled inline where the gap between them is widest; two readout cards below giving the surviving signal at t/T = 0.75 for each; footer takeaway.
- Visible-text transcript: Canery.in · 05 / 07 · The schedule is configuration. · Not a layer. It decides which noise levels the network ever practises. · 0.25 0.50 0.75 1.00 · √ᾱₜ · cosine · linear · t / T = 0 · 1 · linear √ᾱ = 0.058 at t/T = 0.75 · cosine √ᾱ = 0.380 at t/T = 0.75 · The linear schedule spends its last quarter shuffling what is already noise. · WHAT A DIFFUSION MODEL ACTUALLY DOES · CANERY
- Alt text: Signal coefficient against normalised timestep for the linear and cosine schedules, with the surviving signal at three-quarters of the way through.
- Long description: Two curves fall from 1.00 at t/T = 0 to near zero at t/T = 1. The solid dark curve is the DDPM linear schedule with β rising from 1e-4 to 0.02 over 1,000 steps; it falls steeply and is close to the axis for the last third. The dashed blue curve is the cosine schedule with offset 0.008; it stays much higher for most of the range before falling. Two readout cards give the computed surviving signal at t/T = 0.75: √ᾱ = 0.058 for linear, shown in tangerine, against √ᾱ = 0.380 for cosine.
- Keywords: noise schedule, cosine schedule, linear beta schedule, alpha bar, terminal SNR, DDPM
- Canonical URL: https://canery.in/blogs/what-a-diffusion-model-actually-does

### feed-06-where-the-new-image-comes-from

- File: `assets/social/feed-06-where-the-new-image-comes-from.png`
- Title: Where the new image comes from
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Novelty comes from the random seed, and memorisation is a real but conditional failure driven by duplicated training data.
- Technical source: Article section "Where does the new image come from?"; ledger claims L20 and L21 (Carlini et al., USENIX Security 2023 §4), L22 and L23 (Somepalli et al., CVPR 2023 §§7, 9), and L19 (Kadkhodaie et al., ICLR 2024 §2.2).
- Visual structure: Header; one wide tangerine-outlined statistic panel, then two half-width statistic panels side by side, each with a large figure, a one-line meaning, and two lines of exact experimental condition with its citation; a final wide card carrying the disjoint-training-set result with its citation right-aligned; footer takeaway.
- Visible-text transcript: Canery.in · 06 / 07 · Where the new image comes from. · The seed — with a measured exception worth stating precisely. · 94 · training images extracted from Stable Diffusion · from 175,000,000 generations: 500 images for each of the 350,000 MOST-DUPLICATED training captions, then filtered · Carlini et al., USENIX Security 2023 · 1.88% · of 9,000 random-caption generations · matched a training image at SSCD ≥ 0.5, against an index covering under 0.6% of the data · Somepalli, CVPR 2023 · 34.1× · mean duplication of the matches · duplication in the training set is what predicts replication — not model size · same paper · Two networks trained on non-overlapping halves of a dataset converge on the same denoiser and, from the same seed, produce the same image — one in neither training set. · Kadkhodaie et al., ICLR 2024 · Novel by default. Recalled when the data showed it the same picture over and over. · WHAT A DIFFUSION MODEL ACTUALLY DOES · CANERY
- Alt text: Three measured statistics on diffusion memorisation with their exact experimental conditions, above the disjoint-training-set result.
- Long description: The first panel, outlined in tangerine, gives 94 training images extracted from Stable Diffusion, with the condition that this came from 175,000,000 generations — 500 images for each of the 350,000 most-duplicated training captions — then filtered, citing Carlini et al., USENIX Security 2023. The second gives 1.88% of 9,000 random-caption generations matching a training image at SSCD of 0.5 or more, against an index covering under 0.6% of the data, citing Somepalli, CVPR 2023. The third gives 34.1× as the mean duplication of the matched images, noting that duplication rather than model size predicts replication. A final card states that two networks trained on non-overlapping halves of a dataset converge on the same denoiser and produce the same image from the same seed, one in neither training set, citing Kadkhodaie et al., ICLR 2024.
- Keywords: memorisation, data replication, training data extraction, generalization, random seed, LAION duplication
- Canonical URL: https://canery.in/blogs/what-a-diffusion-model-actually-does

### feed-07-the-four-moving-parts

- File: `assets/social/feed-07-the-four-moving-parts.png`
- Title: The four moving parts
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: A diffusion system has four components and only the denoiser was trained — so read the article to see the seams.
- Technical source: Article section "What are the four moving parts?" and Figure 6.
- Visual structure: Header; four numbered rows, each naming a component, its notation and its status, with the denoiser row filled and outlined in tangerine; a tangerine-outlined card holding the article URL split across two lines; footer takeaway.
- Visible-text transcript: Canery.in · 07 / 07 · The four moving parts. · Only one of them was trained. Read part 1 of the series. · ① THE SCHEDULE fixed β₁ … β_T configuration · ② THE TRAINING LOOP corrupt, predict, update runs once, offline · ③ THE DENOISER εθ(xₜ, t) the only trained part · ④ THE SAMPLER xₜ₋₁ from xₜ and ε̂ arithmetic, no parameters · canery.in/blogs/ what-a-diffusion-model-actually-does · Swap the schedule, the sampler or the seed and the same checkpoint still works. · WHAT A DIFFUSION MODEL ACTUALLY DOES · CANERY
- Alt text: The four components of a diffusion system with the denoiser highlighted as the only trained one, above the article link.
- Long description: Four rows list the components of a diffusion system. Row one is the schedule, the fixed β₁ to β_T, marked configuration. Row two is the training loop — corrupt, predict, update — marked as running once, offline. Row three, filled in pale tangerine and outlined, is the denoiser εθ(xₜ, t), marked the only trained part. Row four is the sampler, producing xₜ₋₁ from xₜ and ε̂, marked arithmetic with no parameters. Below, a card gives the article address canery.in/blogs/what-a-diffusion-model-actually-does. The takeaway notes that the schedule, sampler or seed can be swapped and the same checkpoint still works.
- Keywords: diffusion system, denoiser, sampler, noise schedule, training loop, architecture
- Canonical URL: https://canery.in/blogs/what-a-diffusion-model-actually-does

### story-01-trained-only-to-undo-noise

- File: `assets/social/story-01-trained-only-to-undo-noise.png`
- Title: Trained only to undo noise — Story opener
- Platforms: Instagram Story
- Role: cover
- Dimensions: 1080×1920
- Narrative beat: The forward corruption is a formula; the network exists only because it cannot be run backwards.
- Technical source: Article section "The problem" and Figure 1, recomposed for 9:16 as a two-by-two grid rather than a horizontal strip.
- Visual structure: Canery lockup below the Instagram interface zone, frame counter opposite; two-line serif hook; a 2×2 grid of cell fields at four rising signal levels, each labelled with its ᾱ, the last outlined in tangerine; three-line takeaway in the footer.
- Visible-text transcript: Canery.in · 01 / 04 · Trained only to undo noise. · So where does a new image come from? · ᾱ = 0.012 · ᾱ = 0.160 · ᾱ = 0.480 · ᾱ = 0.970 · The forward corruption is a formula. The network exists only because it cannot be run backwards. · WHAT A DIFFUSION MODEL ACTUALLY DOES · CANERY
- Alt text: A crescent emerging from pure noise across four panels of rising signal, recomposed for a vertical Story.
- Long description: Four square fields of discrete cells are arranged two by two. The first, at ᾱ = 0.012, is uniform grain. The second, at ᾱ = 0.160, shows the faintest suggestion of structure. The third, at ᾱ = 0.480, shows a recognisable bright crescent through the grain. The fourth, at ᾱ = 0.970 and outlined in tangerine, shows a clean bright crescent on a dark ground. The takeaway states that the forward corruption is a formula and the network exists only because it cannot be run backwards.
- Keywords: diffusion model, forward process, noise, crescent, alpha bar
- Canonical URL: https://canery.in/blogs/what-a-diffusion-model-actually-does

### story-02-the-answer-key-is-free

- File: `assets/social/story-02-the-answer-key-is-free.png`
- Title: The answer key is free — Story
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: The noise is drawn before it is added, so the training target costs nothing.
- Technical source: Article section "Worked example" and Figure 2; the same x₀, ε and ᾱ = 0.64.
- Visual structure: Header; two 4×4 grids of printed values stacked side by side with a plus sign between, each cell shaded by value and one cell ringed in tangerine in both; a tangerine-outlined card below carrying the traced addition and two lines of explanation; three-line takeaway in the footer.
- Visible-text transcript: Canery.in · 02 / 04 · The answer key is free. · We draw the noise ourselves, so nothing needs labelling. · 0.8 · x₀ · 0.6 · ε · 0.48 + 0.84 = 1.32 · one cell of xₜ, the tensor the network sees. · The target is the ε we already hold. · A fresh training pair from any image, at any noise level, forever. · WHAT A DIFFUSION MODEL ACTUALLY DOES · CANERY
- Alt text: Two four-by-four grids of printed values adding to one cell of the noisy tensor, with the free training target named.
- Long description: The left grid holds 0.8 × x₀ with values from 0.76 down to −0.80; the right grid holds 0.6 × ε with values from 0.87 down to −0.81. Cells are shaded by value, dark for low and light for high. The same cell — second from the left in the top row — is ringed in tangerine in both grids, reading 0.48 and 0.84. A card below carries their sum, 0.48 + 0.84 = 1.32, describes it as one cell of xₜ, the tensor the network sees, and states that the target is the ε already held.
- Keywords: epsilon prediction, training target, self-supervision, worked example, alpha bar
- Canonical URL: https://canery.in/blogs/what-a-diffusion-model-actually-does

### story-03-why-not-one-step

- File: `assets/social/story-03-why-not-one-step.png`
- Title: Why not one step — Story
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: The error multiplier is worst exactly where a one-step sampler would jump, so the steps stay small.
- Technical source: Article section "Why does one call blur and many calls draw?" and Figure 5; multipliers computed from the article's rearrangement of the forward equation.
- Visual structure: Header; a card stating the amplification rule; four rows, each with the ᾱ value, a bar proportional to the multiplier, and the multiplier, with the ᾱ = 0.02 row filled and outlined in tangerine; a consequence line; three-line takeaway in the footer.
- Visible-text transcript: Canery.in · 03 / 04 · Why not just take one step? · Because the error multiplier is worst exactly where you would jump. · error δ in the predicted noise · → √(1−ᾱ)/√ᾱ × δ in the image · ᾱ = 0.96 × 0.20 · ᾱ = 0.64 × 0.75 · ᾱ = 0.25 × 1.73 · ᾱ = 0.02 × 7.00 · A 0.20 error becomes 1.40 — wider than the whole pixel range. · Many small steps keep the multiplier near 1, and each one re-reads a cleaner image than the last. · WHAT A DIFFUSION MODEL ACTUALLY DOES · CANERY
- Alt text: The error multiplier at four signal levels, drawn as bars to scale, rising from 0.20 to 7.00.
- Long description: A card states that an error δ in the predicted noise becomes √(1−ᾱ)/√ᾱ × δ in the image. Four rows follow with bars proportional to the multiplier on a shared scale: ᾱ = 0.96 gives ×0.20, ᾱ = 0.64 gives ×0.75, ᾱ = 0.25 gives ×1.73, and ᾱ = 0.02, filled in pale tangerine, gives ×7.00 with a bar running almost the full width. A line notes that a 0.20 error therefore becomes 1.40, wider than the whole pixel range.
- Keywords: sampling steps, error amplification, signal to noise ratio, one-step generation, sampler
- Canonical URL: https://canery.in/blogs/what-a-diffusion-model-actually-does

### story-04-read-the-article

- File: `assets/social/story-04-read-the-article.png`
- Title: Read the article — Story CTA
- Platforms: Instagram Story
- Role: cta
- Dimensions: 1080×1920
- Narrative beat: Four components, one of them trained — the article walks all four.
- Technical source: Article section "What are the four moving parts?" and Figure 6.
- Visual structure: Header; four rows naming the components with their status, the denoiser row filled and outlined in tangerine; a tangerine-outlined card carrying the call to read and the domain; two-line takeaway pointing at the link sticker.
- Visible-text transcript: Canery.in · 04 / 04 · What a diffusion model actually does. · Part 1 of the Diffusion Models series, on Canery. · ① THE SCHEDULE configuration · ② THE TRAINING LOOP runs once, offline · ③ THE DENOISER the only trained part · ④ THE SAMPLER arithmetic, no parameters · read the article · canery.in · Link in the sticker above — the full worked example is in the post. · WHAT A DIFFUSION MODEL ACTUALLY DOES · CANERY
- Alt text: The four parts of a diffusion system with the denoiser highlighted, above the call to read the article on Canery.
- Long description: Four rows name the components of a diffusion system with their status: the schedule as configuration, the training loop as running once offline, the denoiser as the only trained part, and the sampler as arithmetic with no parameters. The denoiser row is filled in pale tangerine and outlined. Below, a card carries the words "read the article" above the domain canery.in. The footer points the viewer at the link sticker and notes that the full worked example is in the post.
- Keywords: diffusion system, denoiser, sampler, noise schedule, series part one
- Canonical URL: https://canery.in/blogs/what-a-diffusion-model-actually-does
