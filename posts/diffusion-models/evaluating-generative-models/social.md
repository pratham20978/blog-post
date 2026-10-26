---
social_schema: 2
canonical_url: "https://canery.in/blogs/evaluating-generative-models"
---

# Social publishing package — evaluating-generative-models

## LinkedIn post

FID is the headline score for image generators: lower is better, and papers are ranked by it. On ImageNet, StyleGAN-XL and DiT-XL/2 were reported at FID 2.26 and 2.27. In the largest human study of generative models, people got 15.3% of real-or-fake judgements wrong on the first and 28.6% on the second.

FID compares only the average and the covariance of an ImageNet classifier's features. Measured in a toy whose true distribution is known exactly:

→ One number, two failures. A generator that drops every faint crescent and one that adds grain to every image both scored FD 3.6221.
→ FD can be zero for broken images. A generator built to the real mean and spread scores exactly 0 while half its values are wrong.
→ Two numbers split the tie. Precision 0.817 against 0.0005, recall 0.394 against 1.000.
→ Four samples can fool recall. Under strong guidance, k-NN recall bounced back to 0.725 because four stray samples had huge neighbourhoods; coverage fell to 0.266.
→ FD depends on N. A perfect generator scored 0.0736 at 1,000 samples, worse than a grainy one at 4,000.

The toy's sizes are mechanism, not scale; published results are quoted with their model, dataset and protocol.

Part 9 of the Diffusion Models series.

## LinkedIn first comment

What FID measures, what it hides, and what to report beside it, with a numpy lab that runs in under a minute.

Read the full article on Canery: https://canery.in/blogs/evaluating-generative-models

## Instagram caption

FID ranks image generators with one number. That number cannot say whether a model lost quality or lost variety.

Swipe through two generators with opposite failures and the same score, a generator that scores a perfect 0 with broken images, the two numbers that split the tie, four samples that fool recall, why the score moves with sample count, and what people see that FID does not.

Every measured number comes from a lab you can run on a laptop in under a minute; published results are quoted with their setup.

Link in bio.

#generativeai #machinelearning #deeplearning #diffusionmodels #fid #computervision #aievaluation

## Shared feed order

1. `assets/social/feed-01-one-number-two-failures.png` — two crescent generators with opposite failures receive the same Fréchet distance
2. `assets/social/feed-02-fd-can-be-zero.png` — the worked example: a generator with the real mean and spread scores FD 0 while half its values are wrong
3. `assets/social/feed-03-all-fid-keeps.png` — the FID pipeline reduces each set to a mean and a covariance of 2,048 Inception features
4. `assets/social/feed-04-two-numbers-split-the-tie.png` — precision, recall and coverage separate the two generators FID tied
5. `assets/social/feed-05-four-samples-fool-recall.png` — under rising guidance, k-NN recall rebounds at w = 7.5 because four stray samples have huge balls; coverage keeps falling
6. `assets/social/feed-06-fd-depends-on-n.png` — FD is biased upward by about K/N, so scores at different sample counts do not compare
7. `assets/social/feed-07-same-fid-not-the-same-images.png` — two ImageNet models reported at near-equal FID were mistaken for real at very different rates in a large human study
8. `assets/social/feed-08-read-the-article.png` — the five things FID hides, and the call to read the article

## Instagram Story

Not produced: this part ships feed cards only, as Part 8 did at the owner's request (2026-10-19), so there are no Story frames, Story CTA or link sticker to post.

### Story order

None.

## Asset metadata

### feed-01-one-number-two-failures

- File: `assets/social/feed-01-one-number-two-failures.png`
- Title: One number, two failures
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: two crescent generators with opposite failures receive the same Fréchet distance
- Technical source: Which failures does one number hide? (Same score, opposite failures); Figure 3; lab failures stage
- Visual structure: lockup and counter; serif title; deck; two rows of four 8×8 sample tiles, each row labelled with its defect and its FD in large orange type at right; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 08 · One number, two failures. · The arithmetic inside FID scores these two crescent generators exactly equal. One lost half the variety; one adds grain to all. · DROPS EVERY FAINT CRESCENT · FD 3.6221 · ADDS GRAIN TO EVERY PIXEL · FD 3.6221 · Same score to four decimals. A single distance cannot say whether a model lost quality or lost variety. · EVALUATING GENERATIVE MODELS · CANERY.IN
- Alt text: Two rows of 8x8 crescent samples, one with only strong crescents and one grainy, both scored FD 3.6221
- Long description: Cover card. Four samples from a crescent-world generator that drops every faint crescent, and four from one that adds pixel grain to every image (pixel noise 0.347 against 0.100 for real images, grain tuned to 0.3319). Both receive a Fréchet distance of 3.6221 on the 64 pixel values against a 32,768-image training set, 4,096 samples each. The takeaway: one distance cannot say whether a model lost quality or lost variety.
- Keywords: FID, Fréchet distance, generative model evaluation, mode dropping, image fidelity, diffusion models
- Canonical URL: https://canery.in/blogs/evaluating-generative-models

### feed-02-fd-can-be-zero

- File: `assets/social/feed-02-fd-can-be-zero.png`
- Title: FD can be zero for broken images
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the worked example: a generator with the real mean and spread scores FD 0 while half its values are wrong
- Technical source: Worked example; Figure 1; lab worked stage
- Visual structure: two number lines, real contrasts above and the moment-matched generator below, each under the same bell curve; filled dots near a real value, hollow orange dots farther than 0.05; summary line and FD = 0 at the bottom right
- Visible-text transcript: Canery.in · 02 / 08 · FD can be zero for broken images. · Reduce each image to its crescent's strength: faint 0.5 or strong 1.0. FD compares only the mean and the spread of those numbers. · EIGHT REAL CRESCENTS · A GENERATOR BUILT TO MATCH THEM · mean 0.75 · spread 0.2525 in both rows · FD = 0 · Same bell, FD = 0, yet 4 of its 8 values sit more than 0.05 from any real crescent (hollow orange). · EVALUATING GENERATIVE MODELS · CANERY.IN
- Alt text: Eight real crescent strengths and eight generated ones under the same bell curve; four generated values fall between the real clusters
- Long description: The article's worked example. Real crescent contrasts 0.45, 0.50, 0.50, 0.55, 0.95, 1.00, 1.00, 1.05 (mean 0.7500, spread 0.2525) and a generator built to the same mean and spread: 0.35, 0.50, 0.60, 0.65, 0.85, 0.90, 1.00, 1.15. In one dimension the Fréchet distance is the squared mean gap plus the squared spread gap, so it is exactly 0, although 4 of the 8 generated values lie more than 0.05 from any real value.
- Keywords: Fréchet distance, FID, worked example, mean and variance, distribution matching, generative models
- Canonical URL: https://canery.in/blogs/evaluating-generative-models

### feed-03-all-fid-keeps

- File: `assets/social/feed-03-all-fid-keeps.png`
- Title: All FID keeps is two summaries
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the FID pipeline reduces each set to a mean and a covariance of 2,048 Inception features
- Technical source: What does FID compute on real images?; Figure 2; ledger L01–L03, L21; lab failures stage for the takeaway
- Visual structure: six stacked boxes joined by short lines: images, resize to 299 × 299, Inception-v3, 2,048 features per image, mean + covariance per set, one distance (FID, highlighted orange); a count line below; takeaway
- Visible-text transcript: Canery.in · 03 / 08 · All FID keeps is two summaries. · Real and generated images pass through an ImageNet classifier. Each set is then reduced to the mean and covariance of its features. · images · any size · resize · 299 × 299 · Inception-v3 · ImageNet classifier · 2,048 features · per image · mean + covariance · per set · one distance · FID · each set becomes 2,048 means and 2,098,176 distinct covariances · In crescent world, a Gaussian blob with the data's mean and covariance scored FD 0.0158, level with the perfect generator's 0.0143. · EVALUATING GENERATIVE MODELS · CANERY.IN
- Alt text: FID pipeline as six steps: resize to 299 x 299, Inception-v3, 2,048 features, mean and covariance per set, one distance
- Long description: FID resizes every image to 299 × 299, passes it through Inception-v3 (an ImageNet classifier), keeps 2,048 pool3 features per image, and reduces each set to a mean vector and a covariance matrix: 2,048 means and 2,098,176 distinct covariances. The Fréchet distance between the two summaries is the score. In the lab's crescent world, a Gaussian blob with the training set's mean and covariance scored FD 0.0158, beside the perfect generator's 0.0143, although 25.4% of its images show a crescent strength no real image has.
- Keywords: FID pipeline, Inception-v3, pool3 features, covariance matrix, Fréchet distance, image generation metrics
- Canonical URL: https://canery.in/blogs/evaluating-generative-models

### feed-04-two-numbers-split-the-tie

- File: `assets/social/feed-04-two-numbers-split-the-tie.png`
- Title: Two numbers split the tie
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: precision, recall and coverage separate the two generators FID tied
- Technical source: Which failures does one number hide? (Precision, recall, density and coverage); Figure 3; lab failures stage
- Visual structure: two blocks, Drops faint and Grainy, each with its FD in orange and three horizontal bars for precision, recall and coverage with values at right; a perfect-generator baseline line; takeaway
- Visible-text transcript: Canery.in · 04 / 08 · Two numbers split the tie. · Precision asks whether samples look real. Recall and coverage ask whether the real variety is there. Same FD, opposite answers. · Drops faint · FD 3.6221 · PRECISION 0.817 · RECALL 0.394 · COVERAGE 0.504 · Grainy · FD 3.6221 · PRECISION 0.0005 · RECALL 1.000 · COVERAGE 0.0005 · a perfect generator: precision 0.807 · recall 0.826 · coverage 0.971 · Report fidelity and diversity separately, each read against a real-against-real baseline, never against 1.0. · EVALUATING GENERATIVE MODELS · CANERY.IN
- Alt text: Precision, recall and coverage bars: the faint-dropper scores 0.82, 0.39, 0.50; the grainy one near 0, 1, 0
- Long description: Both generators have FD 3.6221. The faint-dropper: precision 0.817, recall 0.394, coverage 0.504. The grainy generator: precision 0.0005, recall 1.000, coverage 0.0005. A perfect generator does not score 1: precision 0.807, recall 0.826, coverage 0.971, so each must be read against a real-against-real baseline. Precision and recall use k = 3 nearest neighbours, density and coverage k = 5.
- Keywords: precision and recall, density and coverage, k-nearest neighbours, fidelity, diversity, generative model evaluation
- Canonical URL: https://canery.in/blogs/evaluating-generative-models

### feed-05-four-samples-fool-recall

- File: `assets/social/feed-05-four-samples-fool-recall.png`
- Title: Four samples can fool recall
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: under rising guidance, k-NN recall rebounds at w = 7.5 because four stray samples have huge balls; coverage keeps falling
- Technical source: Which failures does one number hide? (Turning a quality dial); Figure 5; lab guidance stage
- Visual structure: line chart against guidance weight w from 1 to 7.5: coverage (blue) falling, recall (orange) falling then rising at 7.5, faint share (dotted grey) falling to zero; an orange note at top right with a leader to the recall line; takeaway
- Visible-text transcript: Canery.in · 05 / 08 · Four samples can fool recall. · Turn guidance up and the faint crescents vanish. At w = 7.5 recall jumps back to 0.725, as if the variety had returned. · w = 7.5: 4 stray faint samples, ball radius 2.92 against 0.93 · RECALL · COVERAGE · FAINT SHARE (TRUTH) · 1.0 · 0.5 · 0.0 · 1 · 1.5 · 2 · 3 · 4 · 5 · 7.5 · guidance weight w · Recall credited 99.6% of real faint images; coverage, which puts the balls around real images, found a sample near 0.3% of them. · EVALUATING GENERATIVE MODELS · CANERY.IN
- Alt text: Recall, coverage and faint share against guidance weight: recall rebounds to 0.725 at w = 7.5 while coverage falls to 0.266
- Long description: Part 8's guided samples from crescent world's exact model, re-scored. As the guidance weight rises from 1 to 7.5, the faint share falls from 52.9% to 0.1%, coverage falls from 0.984 to 0.266, and recall falls from 0.666 to 0.544 at w = 5, then rises to 0.725. At w = 7.5 only 4 of 4,096 samples are faint; their k-NN balls have a median radius of 2.92 against 0.93, so recall credits 99.6% of real faint images, while coverage finds a sample near only 0.3% of them.
- Keywords: k-NN recall, coverage, classifier-free guidance, mode collapse, outliers, generative model metrics
- Canonical URL: https://canery.in/blogs/evaluating-generative-models

### feed-06-fd-depends-on-n

- File: `assets/social/feed-06-fd-depends-on-n.png`
- Title: FD depends on how many samples
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: FD is biased upward by about K/N, so scores at different sample counts do not compare
- Technical source: Why don't FIDs compare across papers?; Figure 6; lab bias stage
- Visual structure: four labelled horizontal bars of mean FD: perfect at N = 1,000, grain 0.07 at N = 4,000 (both values orange), perfect at 4,000 and at 64,000; takeaway
- Visible-text transcript: Canery.in · 06 / 08 · FD depends on how many samples. · A perfect generator never scores zero: its FD falls roughly like 1/N, fitted as 0.0007 + 59.9/N in crescent world. · FD OF 24 REPEATS, AVERAGED · perfect generator, N = 1,000 · 0.0736 · grain 0.07, N = 4,000 · 0.0457 · perfect generator, N = 4,000 · 0.0174 · perfect generator, N = 64,000 · 0.0011 · The perfect generator at 1,000 samples scores worse than a grainy one at 4,000. Compare FIDs only at the same N. · EVALUATING GENERATIVE MODELS · CANERY.IN
- Alt text: Bars of mean FD: a perfect generator scores 0.0736 at 1,000 samples, worse than a grainy one at 4,000
- Long description: Crescent world, 24 repeats per point against a 262,144-image reference. The perfect generator's mean FD is 0.0736 at N = 1,000, 0.0174 at 4,000 and 0.0011 at 64,000, fitted as 0.0007 + 59.9/N on N of 2,000 or more. A slightly grainy generator (grain 0.07) scores 0.0457 at 4,000, better than the perfect generator at 1,000. FID scores compare only at equal N.
- Keywords: FID bias, sample size, FID infinity, estimator bias, generative model benchmarking, Fréchet distance
- Canonical URL: https://canery.in/blogs/evaluating-generative-models

### feed-07-same-fid-not-the-same-images

- File: `assets/social/feed-07-same-fid-not-the-same-images.png`
- Title: Same FID, not the same images
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: two ImageNet models reported at near-equal FID were mistaken for real at very different rates in a large human study
- Technical source: Why this matters; What can't the Inception network see?; Figure 7; ledger L29, L31 (Stein et al., NeurIPS 2023)
- Visual structure: two boxes with each model's reported FID; two horizontal bars of human error rate, DiT-XL/2 in orange; a source line; takeaway
- Visible-text transcript: Canery.in · 07 / 08 · Same FID, not the same images. · Two ImageNet models tied on FID. In the largest human study of generative models, people were asked to tell their images from real. · IMAGENET 256 × 256 · FID AS REPORTED BY EACH PAPER'S AUTHORS · StyleGAN-XL · FID · 2.26 · DiT-XL/2 · FID · 2.27 · SHARE OF REAL-OR-FAKE JUDGEMENTS PEOPLE GOT WRONG · StyleGAN-XL · 15.3% · DiT-XL/2 · 28.6% · chance is 50% · Stein et al., NeurIPS 2023: 41 models, 207,000 judgements · People were fooled nearly twice as often by DiT-XL/2. FID, on an ImageNet classifier's features, saw a tie. · EVALUATING GENERATIVE MODELS · CANERY.IN
- Alt text: StyleGAN-XL and DiT-XL/2 with reported FIDs of 2.26 and 2.27, and human error rates of 15.3% and 28.6%
- Long description: Quoted from Stein et al. (NeurIPS 2023): on ImageNet at 256 × 256, StyleGAN-XL and DiT-XL/2 were reported by their authors at FID 2.26 and 2.27. In Stein et al.'s human study (41 models, more than 1,000 paid participants, 207,000 real-or-fake judgements, chance 50%), people got 15.3% of judgements wrong on StyleGAN-XL and 28.6% on DiT-XL/2. Re-scored under one protocol, the two FIDs were 2.91 and 2.80.
- Keywords: FID, human evaluation, StyleGAN-XL, DiT, ImageNet, generative model benchmarks
- Canonical URL: https://canery.in/blogs/evaluating-generative-models

### feed-08-read-the-article

- File: `assets/social/feed-08-read-the-article.png`
- Title: What one number hides
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: the five things FID hides, and the call to read the article
- Technical source: Key takeaways; Limitations and common mistakes
- Visual structure: a white panel listing five headings with one-line explanations; takeaway; orange CTA footer with the URL
- Visible-text transcript: Canery.in · 08 / 08 · What one number hides. · FID, the headline score for image generators, measured against precision, coverage, sample count and people, in a toy you can run. · Which failure · lost quality or lost variety: one number cannot say · Beyond two moments · a Gaussian blob with the right moments scores like perfect · Sample count · biased upward by roughly K/N · The pipeline · resizing, JPEG and code move it more than models differ · What people see · and the prompt, which it never reads · Read FID beside precision, coverage and a check by people. · READ IT AT CANERY.IN/BLOGS/EVALUATING-GENERATIVE-MODELS
- Alt text: List of what FID hides: which failure, anything beyond two moments, sample count, the pipeline, and what people see
- Long description: Call-to-action card. FID cannot say whether a model lost quality or variety; it is blind beyond the mean and covariance of its features; it is biased upward by roughly K/N in the sample count; resizing, JPEG and implementation move it by more than published models differ; and its ImageNet features miss what people see and never read the prompt. Read FID beside precision, coverage and a check by people.
- Keywords: FID limitations, generative model evaluation, precision recall coverage, human evaluation, diffusion models
- Canonical URL: https://canery.in/blogs/evaluating-generative-models
