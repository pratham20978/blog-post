---
title: "Evaluating Generative Models: What FID Measures and Hides"
slug: evaluating-generative-models
date: 2026-10-21
updated: 2026-10-21
summary: "FID compares the mean and covariance of Inception features of real and generated images. It cannot tell lost variety from lost quality, and it moves with N."
tags: [machine-learning, generative-model, diffusion-model, evaluation-metrics, fid, precision-recall]
category: machine-learning
series: diffusion-models
series_position: 9
tier: L2
difficulty: intermediate
prerequisites: ["Part 1 of this series", "the mean and standard deviation of a list of numbers"]
reading_minutes: 23
cover_image: "COVER"
canonical_url: "https://canery.in/blogs/evaluating-generative-models"
---

![Real and moment-matched crescent contrasts on number lines beside two crescent sample sets that share the same FD of 3.6221](COVER)

> [!NOTE]
> **Insights** — Fréchet Inception Distance (FID) summarises real and generated images by the average and covariance of 2,048 features from an ImageNet classifier, and reports how far apart the two summaries are. It cannot say whether a model lost quality or variety, it is blind to everything beyond those two statistics and to whatever the classifier never learned to notice, and it moves with sample count and with how images are resized and saved. Compare FIDs only under one protocol, beside precision, coverage and a human or prompt-aware check.

**Level:** intermediate · **You need:** Part 1 of this series (What a Diffusion Model Actually Does), the mean and standard deviation of a list of numbers · **Time:** ~23 min

**Jump to:** [worked example](#worked-example) · [what FID computes](#what-does-fid-compute-on-real-images) · [hidden failures](#which-failures-does-one-number-hide) · [comparing papers](#why-dont-fids-compare-across-papers) · [what Inception misses](#what-cant-the-inception-network-see) · [math](#the-math) · [implementation](#implementation)

> [!IMPORTANT]
> Numbers this post calls **measured** come from its lab: crescent world, 8×8 images whose true distribution is known exactly, with every metric computed on the 64 pixel values rather than on Inception features. Read the toy's sizes as mechanism, not scale. Results **quoted** from papers carry their model, dataset and protocol.

## Why this matters

On ImageNet at 256×256 pixels, StyleGAN-XL and DiT-XL/2 were reported at FID 2.26 and 2.27, a tie. <!-- L31 --> In the largest human study of generative models, people shown one image at a time and asked whether it was real got 15.3% of their judgements wrong on StyleGAN-XL and 28.6% on DiT-XL/2. <!-- L29 --> <!-- L31 --> The diffusion model fooled them nearly twice as often. A team choosing between the two by FID would have been choosing on noise, while the difference its users would see went unmeasured.

## The problem

Rating one generated image is easy for a person. Rating a generator is not, because a generator is a distribution: the question is whether the set of images it produces looks like the set of real ones, and no generated image has a correct answer to compare it with. Three properties matter. **Fidelity**: each image looks real. **Diversity**, or coverage: the set spans the real variety, every pose and kind, not just the commonest. **Novelty**: the images are not copies of training images. <!-- L47 --> A useful evaluation tells you which of the three a model got wrong.

FID, introduced in 2017 and still the primary metric for ranking generative models, answers with one distance between summaries of the two sets. <!-- L49 --> <!-- L01 --> One distance has to fold three properties into one number, so something inside it decides how much each counts.

The second difficulty is scale. Saving the real FFHQ face images as JPEG at a common library's default quality gives an FID of 21 against the same images saved losslessly, while a strong generator, StyleGAN2, scores about 3, and recent methods differ from each other by less than 1. <!-- L23 --> A file-format choice moves the number more than twenty times further than the gaps it is used to rank.

## Worked example

Shrink every image to one number: how strong its crescent is. In crescent world, the toy this series uses, a real crescent is either faint, at contrast 0.5, or strong, at 1.0, half and half. Here are eight real contrasts:

0.45, 0.50, 0.50, 0.55, 0.95, 1.00, 1.00, 1.05

Their mean is 6.00 / 8 = 0.75. Their spread, the standard deviation, comes from the squared distances to the mean: 0.30² + 0.25² + 0.25² + 0.20² = 0.255 on each side, 0.51 in all, so the variance is 0.51 / 8 = 0.06375 and the spread its square root, 0.2525.

For one number, the Fréchet distance (FD) between two bell curves is the squared gap between their means plus the squared gap between their spreads:

$$
\mathrm{FD} = (m_r - m_g)^2 + (s_r - s_g)^2
$$

Here $m_r$ and $s_r$ are the real mean and spread, and $m_g$ and $s_g$ the generator's. FD is zero only when the two bell curves coincide. Now score three generators, each making eight crescents:

| Generator | Its eight contrasts | Mean | Spread | Mean term | Spread term | FD | Within 0.05 of a real contrast |
|---|---|---|---|---|---|---|---|
| strong only | 0.95 1.00 1.00 1.05, twice | 1.0000 | 0.0354 | 0.0625 | 0.0471 | **0.1096** | 8 of 8 |
| all too faint | 0.35 0.40 0.40 0.45 0.85 0.90 0.90 0.95 | 0.6500 | 0.2525 | 0.0100 | 0 | **0.0100** | 6 of 8 |
| moment matched | 0.35 0.50 0.60 0.65 0.85 0.90 1.00 1.15 | 0.7500 | 0.2525 | 0 | 0 | **0** | 4 of 8 |

Take the first row by hand. Its mean is 1.00; four values sit 0.05 away and four sit on it, so its variance is 4 × 0.0025 / 8 = 0.00125 and its spread 0.0354. The mean term is (0.75 − 1.00)² = 0.0625, the spread term (0.2525 − 0.0354)² = 0.0471, and FD = 0.1096. The second row is every real value minus 0.1, which costs only the mean term. The third was built to match the real mean and spread, the first two statistical moments, hence its name: its distances to 0.75 are 0.40, 0.25, 0.15 and 0.10 on each side, whose squares again sum to 0.51. Figure 1 puts all three on number lines.

![Number lines of eight real crescent contrasts and three generators, with each generator's mean, spread and Fréchet distance](FIG_01)
*Figure 1. FD ranks the moment-matched generator first, with a perfect 0, although half its contrasts lie more than 0.05 from any real one; the strong-only generator, whose every value is real, comes last.*

The strong-only generator lost half the variety and kept every image right. The moment matcher kept the variety's mean and spread and got half its images wrong: two sit in the gap where no real crescent lives and two outside the real range. A distance built from means and spreads cannot tell which failure it sees, and here it prefers the broken images.

## Intuition

Read FD as a moving cost. Replace each set by the bell-shaped cloud with the same centre and spread; FD is the cheapest way to turn one bell into the other, where shifting the centre costs the squared distance moved and stretching or squeezing costs the squared change in width. <!-- L01 --> It is a sound distance between bells, and blind to anything a bell cannot draw: two clusters, the gap between them, a lump that should not be there.

For many features, think of a census that records each question's average answer and how every pair of answers varies together. It would call two towns identical if those numbers matched, even if one held only middle-aged couples and the other only students and retirees. FID is such a census of images, with 2,048 questions. The analogy breaks in FID's favour on one point: matching every average and pairwise covariance across 2,048 features is demanding, so a generator that manages it has learned a lot. It breaks against FID on another: the questions were chosen by a network trained to name ImageNet's 1,000 object classes, and whatever it never learned to ask about is invisible. <!-- L03 --> <!-- L25 -->

Opposite failures also land in one place. Dropping a mode moves the centre and shrinks the spread; adding noise to every image widens it. Both are costs of reshaping the bell, and FD adds them up.

## What does FID compute on real images?

Figure 2 shows the computation. Every image, real or generated, is resized to 299 × 299 pixels and passed through Inception-v3, a convolutional network trained to classify photographs into ImageNet's 1,000 classes. FID keeps the network's last pooling layer: 2,048 numbers per image, the "pool3 features". <!-- L01 --> <!-- L03 --> <!-- L21 --> For each set it computes a mean vector of 2,048 numbers and a 2,048 × 2,048 covariance matrix, the table of how every pair of features varies together, and takes the Fréchet distance between the two. Lower is better; zero means identical summaries. Heusel and colleagues kept only these two statistics for practical reasons, and treated the features as Gaussian because a Gaussian is the least committal distribution with a given mean and covariance. <!-- L02 -->

![FID pipeline: real and generated images resized to 299 px, Inception-v3 pool3 features, means and covariances, one Fréchet distance](FIG_02)
*Figure 2. Everything FID knows about 50,000 images is 2,048 means and 2.1 million distinct covariances; the orange tags mark the five protocol choices that move the score without changing the model.*

The comparison runs in a feature space because distance on raw pixels misreads images: shift a photograph by one pixel and it looks the same, yet moves far in pixel space. <!-- L48 --> The real set is the **reference**. For class-conditional ImageNet models it is the whole training set against 50,000 generated images, and careful papers re-score every model with one codebase because implementation details move the number. <!-- L04 --> <!-- L38 --> For text-to-image models it is usually 30,000 images from the COCO dataset, with images generated from their captions. <!-- L35 -->

Three relatives come up beside FID. The Inception Score, its predecessor, never looks at real images, so a model that memorises a small subset of its training images still scores well. <!-- L05 --> The Kernel Inception Distance (KID) keeps the features but uses a kernel distance that assumes no bell shape and has an unbiased estimator. <!-- L16 --> FD_DINOv2 keeps the Fréchet distance but swaps Inception-v3 for DINOv2, a network trained without labels on a larger, more varied image collection. <!-- L30 --> Each changes one box in Figure 2; none adds a second number.

## Which failures does one number hide?

### Same score, opposite failures

The lab builds five generators in crescent world at full size: 8 × 8 images of four crescents, each faint or strong, with random brightness and slight pixel noise. A training set of 32,768 images is the reference, each generator makes 4,096 images, and FD is computed on the 64 pixel values. One generator is perfect: fresh draws from the true distribution. One copies training images. One drops every faint crescent. One adds grain to every pixel, turned up until its FD equals the faint-dropper's. One is a Gaussian blob with the training set's mean and covariance. Figure 3 shows their samples and scores.

![8x8 samples from five generators with FD, precision, recall and coverage: drops-faint and grainy tie at FD 3.6221](FIG_03)
*Figure 3. Same FD, opposite failures: precision, recall and coverage tell the faint-dropper from the grainy generator and expose the Gaussian blob, and nothing here sees the copier. Measured, 4,096 samples per generator.*

The faint-dropper and the grainy generator tie at FD 3.6221. Every faint-dropper image is a correct crescent, with half the variety gone; the grainy generator keeps the variety, with 3.5 times the real pixel noise in every image (0.347 against 0.100). The Gaussian blob scores 0.0158, level with the perfect generator's 0.0143, though a quarter of its images (25.4%, against 0.4% for real images) show a crescent strength no real image has. The copier scores 0.0133, better than perfect: FD cannot tell a new image from a returned one, a question this series takes up later.

Papers show the same at full scale. On FFHQ faces, two StyleGAN configurations scored FID 16.9 and 16.7, though one made good faces with less variety and the other nearly all broken ones; <!-- L09 --> GANs on MNIST and CelebA failed the same two opposite ways at near-equal FIDs. <!-- L07 -->

### Precision, recall, density and coverage

Separating the failures takes two numbers. Improved precision and recall draw a ball around every sample, reaching its third-nearest neighbour in the same set. **Precision** is the share of generated samples inside some real sample's ball, a fidelity score; **recall** is the share of real samples inside some generated sample's ball, a diversity score. <!-- L08 --> **Density** and **coverage** use only the real samples' balls, with five neighbours: density counts the real balls holding each generated sample, divided by five, and coverage is the share of real samples whose own ball holds a generated sample. <!-- L11 -->

The difference shows when one generated sample sits far from the rest: its ball must reach its third-nearest neighbour, so it is huge, and recall credits every real sample inside. <!-- L12 --> Figure 4 shows this on one number, with two neighbours.

![Number line of real and generated contrasts with k-NN balls: one stray generated sample's wide ball lifts recall to 100%](FIG_04)
*Figure 4. Recall puts the balls around generated samples, so one isolated sample can claim a whole missing mode; coverage puts them around real samples and does not move.*

A generator making only strong crescents scores precision 1.0, recall 0.5, density 1.5 and coverage 0.5. Add one stray, too-faint sample at 0.25: its two nearest generated neighbours are strong, so its ball has radius 0.71 and swallows all five faint real values. Recall jumps to 1.0, as if the faint mode were covered; coverage stays at 0.5, because no faint real value's small ball reaches 0.25.

In crescent world the tied pair separate at once: the faint-dropper scores precision 0.817, recall 0.394 and coverage 0.504; the grainy generator, precision and coverage 0.0005 (two samples in 4,096) and recall 1.000. The Gaussian blob's precision is 0.006 and its coverage 0.018. Read these against the perfect generator, which does not score 1: precision 0.807, recall 0.826, density 0.967, coverage 0.971. Two identical 64-dimensional Gaussians gave the same picture when density and coverage were introduced: precision 0.68, recall 0.67, density 1.06, coverage 0.97. <!-- L13 --> The copier matches the perfect generator on all four: none of them sees copying.

### Turning a quality dial

Guidance is the clearest dial that trades variety for fidelity in a diffusion model; few-step distillation, the subject of Part 7 of this series, Few-Step Diffusion and Distillation: 20 Steps Into 1, can make the same trade. Part 8, Controlling Diffusion Models: Guidance, ControlNet, LoRA, explains guidance; here, a larger weight w makes samples follow their class more strongly. Figure 5 re-scores Part 8's guided samples from crescent world's exact model.

![FD, precision, recall, density and coverage against guidance weight: recall falls then rebounds at w = 7.5, coverage keeps falling](FIG_05)
*Figure 5. Recall rebounds at w = 7.5 because four stray faint samples have huge balls; coverage keeps falling. Measured: the exact model, 4,096 samples per weight.*

FD rises from 0.0298 at w = 1 to 9.1318 at 7.5, since with an exact model guidance only costs, and coverage falls from 0.984 to 0.266 as faint crescents vanish (from 52.9% of samples to 0.1%). Precision holds near 0.81 until over-saturated crescents appear, then falls to 0.671. Recall falls from 0.666 to 0.544 at w = 5, then jumps to 0.725 at 7.5. At that weight only four of 4,096 samples are still faint, and because their nearest neighbours are all strong, their balls have a median radius of 2.92 against 0.93 for a typical sample. Those four balls hold 99.6% of the real faint images: Figure 4's stray sample, four times over. Coverage finds a generated sample inside the balls of only 0.3% of them.

Published curves agree. Raising classifier guidance above 1 traded recall for precision on ImageNet, with FID best in between. <!-- L39 --> And the best setting depends on the metric: for EDM2's small 512×512 ImageNet model, FID preferred guidance 1.4 and FD_DINOv2 preferred 1.9, each rating the other's choice a poor one. <!-- L37 -->

## Why don't FIDs compare across papers?

FD computed from N samples is biased upward: averaged over many runs it exceeds the true value, by an amount that shrinks roughly like 1/N, and no unbiased estimator of FID exists. <!-- L15 --> <!-- L19 --> Figure 6 shows it in the lab. Against a 262,144-image reference, with 24 repeats at each N, a perfect generator scores 0.0736 at N = 1,000, 0.0174 at 4,000 and 0.0011 at 64,000; a slightly grainy one (grain 0.07) scores 0.0923, 0.0457 and 0.0300.

![FD against 1/N for a perfect and a slightly grainy generator: straight lines whose intercepts are 0.0007 and 0.0291](FIG_06)
*Figure 6. FD is biased upward by about K/N, so only scores at the same N compare; reading each line at 1/N = 0 estimates the score with unlimited samples. Measured, 24 repeats per point.*

So scores compare only at the same N: the perfect generator at 1,000 samples scores worse than the grainy one at 4,000. A straight line in 1/N, read at 1/N = 0, estimates the score with unlimited samples, which Chong and Forsyth call FID-infinity; one implementation fits 15 sample counts from 5,000 to 50,000. <!-- L19 --> <!-- L20 --> Here the lines read 0.0007 and 0.0291. Equal N is not always enough, because the slope K depends on the generator: in the lab the two slopes are close, 59.9 and 63.7, but Bińkowski and colleagues built a 2,048-dimensional example in which even 50,000 samples reliably rank two models backwards. <!-- L18 --> Between CIFAR-10's training and test images, real against real, FID was still falling from about 8.1 at 10,000 samples, while KID had settled at zero by 2,000. <!-- L17 -->

The pipeline moves FID too. The same real FFHQ images resized to 299 pixels with two filters from one library differ by FID 0.64; with the fixed-width filters in the PyTorch and TensorFlow FID code, by 4.3; unfiltered, by 7.4. <!-- L21 --> <!-- L22 --> When a training set had been stored as JPEG, compressing the generated images the same way improved one model's FID from 4.00 to 3.48 without touching the model. <!-- L24 --> And the code matters: StyleGAN-XL and DiT-XL/2, reported by their authors at 2.26 and 2.27, scored 2.91 and 2.80 when Stein and colleagues re-ran both under one protocol, so both moved by more than half a point and their order reversed. <!-- L31 --> Compare FIDs only within one table, or recompute them with the same code, sample count, reference set, resizing and file format. <!-- L38 -->

## What can't the Inception network see?

FID sees only what its features encode. In the lab, swap the 64 pixels for five "detector" features, how much of each crescent an image shows plus its brightness, and recompute: the grainy generator's FD falls from 3.6221 to 0.0145, level with the perfect generator's 0.0106, while the faint-dropper's rises to 5.4698. Grain the features do not encode is no longer an error.

Inception's features encode ImageNet's classes. They sit one linear step from its class scores, and a map of what FID responds to on FFHQ faces lights up seat belts, suits and bow ties, not faces. <!-- L25 --> Resampling generated images to match the real set's predicted ImageNet classes cut FID by about 10%; matching every such incidental feature cut it by 63% to 72% on four datasets with no visible change, and fooled KID too. <!-- L26 --> <!-- L27 --> A face generator pre-trained on ImageNet reached StyleGAN2's FID while people rated it worse. <!-- L28 --> Nor are the features Gaussian: on COCO-30K they fail three standard normality tests outright. <!-- L35 -->

People see something else again. Stein and colleagues ran the largest human evaluation of generative models: 41 models on four datasets, more than 1,000 paid participants, 207,000 judgements of whether an image was real or generated. A model's **human error rate** is the share of those judgements people got wrong; chance is 0.5. <!-- L29 --> Figure 7 is their main result.

![Stein et al.'s human error rate for 41 models ordered by FID on four datasets: error rate does not rise as FID improves](FIG_07)
*Figure 7. Human error rate on models ranked by FID, better FID to the right; if FID tracked realism, each panel would rise. Reproduced unchanged from Stein et al., "Exposing flaws of generative model evaluation metrics and their unfair treatment of diffusion models" (NeurIPS 2023), Figure 2, [arXiv:2306.04675](https://arxiv.org/abs/2306.04675), licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).*

No panel rises steadily. No common metric correlated strongly with human error rate; Inception-based scores ranked GANs above diffusion models people found more realistic, and DINOv2 in place of Inception-v3 restored the agreement. <!-- L30 --> Within one network, FD, FD-infinity and KID rank models almost identically: the network decides, not the formula. <!-- L33 --> One point cuts the other way. DiT-XL/2 sampled at guidance 4.0 instead of 1.5 scored FID 17.24 under Stein's protocol and the highest human error rate of the eleven ImageNet models, 0.330: the most realistic images, the least varied within each class. <!-- L32 --> A person judging one image at a time cannot see variety, so human inspection does not replace a coverage number either. <!-- L46 -->

Text-to-image models raise a question FID never asks: does the image show the prompt? On 100 COCO captions and nine models, ranking models by FID correlated −0.900 with experts' rankings, and PickScore, a model trained on people's choices, 0.917. Its authors blame guidance: higher weights make vivid images people prefer, further from COCO's photographs. <!-- L42 --> <!-- L43 --> Prompt agreement needs its own score, such as CLIPScore: 2.5 times the cosine similarity of the image's and the prompt's CLIP embeddings, floored at zero. <!-- L44 -->

## The math

| Symbol | Meaning |
|---|---|
| $\mu_r$, $\mu_g$ | mean feature vectors of the real and generated sets, length $d$ (2,048 for FID) |
| $\Sigma_r$, $\Sigma_g$ | their $d \times d$ covariance matrices |
| $N$ | number of samples in a set |

$$
\mathrm{FD} = \lVert \mu_r - \mu_g \rVert^2 + \mathrm{Tr}\left(\Sigma_r + \Sigma_g - 2\,(\Sigma_r \Sigma_g)^{1/2}\right) \tag{1}
$$

The first term is the squared distance between the centres; the trace term is the cost of reshaping one covariance into the other. <!-- L01 --> With one feature, $\Sigma_r = s_r^2$ and $\Sigma_g = s_g^2$, the trace term is $s_r^2 + s_g^2 - 2 s_r s_g = (s_r - s_g)^2$, so equation (1) is the worked example's formula: $0.0625 + 0.0471 = 0.1096$ for the strong-only generator. Any generator with the real mean and covariance scores zero, whatever else is wrong, as Jayasumana and colleagues also show. <!-- L36 -->

<details>
<summary>Computing the square root</summary>

$\Sigma_r \Sigma_g$ is not symmetric, so a general matrix square root can return small imaginary parts. Only the trace is needed: the sum of the square roots of the eigenvalues of $\Sigma_r \Sigma_g$. Since $\Sigma_r \Sigma_g = \Sigma_r^{1/2} \left(\Sigma_r^{1/2} \Sigma_g \Sigma_r^{1/2}\right) \Sigma_r^{-1/2}$ when $\Sigma_r$ is invertible, those are the eigenvalues of the symmetric, positive semi-definite $\Sigma_r^{1/2} \Sigma_g \Sigma_r^{1/2}$, which a symmetric solver returns real and non-negative.

</details>

The estimate from $N$ samples carries a bias that falls with $N$, with $K$ depending on the generator: <!-- L19 -->

$$
E[\mathrm{FD}_N] \approx \mathrm{FD}_\infty + \frac{K}{N} \tag{2}
$$

The lab's fit for the perfect generator, $0.0007 + 59.9/N$, predicts 0.0157 at $N$ = 4,000, against 0.0174 measured.

## Implementation

The arithmetic fits in a few lines of numpy. The lab's `evaluate.py` adds crescent world and every experiment above; see [Lab downloads](#lab-downloads).

```python
import numpy as np

def frechet(mu1, s1, mu2, s2):
    # trace of (s1 s2)^(1/2) via the symmetric s1^(1/2) s2 s1^(1/2): real eigenvalues, no clean-up
    w, v = np.linalg.eigh(s1)
    r1 = (v * np.sqrt(np.clip(w, 0, None))) @ v.T
    tr_cross = np.sqrt(np.clip(np.linalg.eigvalsh(r1 @ s2 @ r1), 0, None)).sum()
    return ((mu1 - mu2) ** 2).sum() + np.trace(s1) + np.trace(s2) - 2 * tr_cross

def fd(real, fake):              # rows are images, columns are features
    return frechet(real.mean(0), np.cov(real, rowvar=False), fake.mean(0), np.cov(fake, rowvar=False))

def dist(a, b):
    return np.sqrt(np.maximum((a ** 2).sum(1)[:, None] + (b ** 2).sum(1)[None] - 2 * a @ b.T, 0))

def radius(a, k):                # each sample's distance to its k-th nearest neighbour in its own set
    return np.sort(dist(a, a), 1)[:, k]          # column 0 is the sample itself

def prdc(real, fake, k_pr=3, k_dc=5):
    in_real = dist(fake, real) <= radius(real, k_pr)[None]    # fake j inside real i's ball
    in_fake = dist(real, fake) <= radius(fake, k_pr)[None]    # real i inside fake j's ball
    in_real5 = dist(fake, real) <= radius(real, k_dc)[None]
    return {"precision": in_real.any(1).mean(), "recall": in_fake.any(1).mean(),
            "density": in_real5.sum() / (k_dc * len(fake)), "coverage": in_real5.any(0).mean()}
```

`np.cov` divides by N − 1 where the worked example divided by N, a difference that vanishes at FID's sample counts. In practice, fix one pipeline before comparing anything: an anti-aliased resize such as clean-fid's, lossless files, one sample count and one reference set for every model. <!-- L21 --> <!-- L23 --> Report precision and coverage beside FID, each against a real-against-real baseline, and for text-to-image models add a prompt-agreement score and a human or preference-model check.

## Limitations and common mistakes

> [!WARNING]
> **Common mistake: comparing your FID with a number in someone else's paper.** Sample count, reference set, resize filter, file format and code each move the score by more than the gaps between published models: StyleGAN-XL and DiT-XL/2 moved by over half a point and swapped places when re-scored under one protocol. <!-- L31 --> Recompute every baseline in your own pipeline, or compare only within one table.

- **Reading precision and recall as if 1.0 were normal.** A perfect generator scored 0.807 and 0.826 in the lab, and identical 64-dimensional Gaussians 0.68 and 0.67; measure a real-against-real baseline first. <!-- L13 -->
- **Trusting recall to catch mode loss.** One isolated sample can claim a whole missing mode, as at w = 7.5; coverage cannot be fooled that way. <!-- L12 -->
- **Optimising against FID.** Matching ImageNet class statistics lowers FID without better images, so tune on one metric and report another. <!-- L27 -->
- **Using FID for prompt following.** It never reads the prompt, and on COCO captions it ranked models nearly backwards against experts. <!-- L42 -->
- **Expecting any of these numbers to catch copying.** The copier scored like the perfect generator throughout, and no published memorisation metric yet separates copying from other failures. <!-- L34 -->
- **Reading the toy's sizes as typical.** On 64 raw pixels, grain moves every sample away from every real neighbour; in a learned feature space it matters less. The toy shows mechanism; the papers show scale.

## Key takeaways

- FID measures only the mean and covariance of 2,048 Inception features, so a Gaussian blob with the right moments, or a copier, scores like a perfect generator.
- One distance cannot say whether variety or quality was lost: a generator missing half its modes and one adding grain to every image tied at FD 3.6221 in the lab; precision, recall, density and coverage separate them, and coverage is the one a stray sample cannot fool.
- FID is biased upward by roughly K/N and moved by resizing, file format and code, so scores compare only within one protocol.
- Inception's ImageNet features decide what counts as an error; they miss much of what people see and never read the prompt, so pair FID with people, a better feature network or a prompt-agreement score.

## Try it yourself

These can be answered from the article alone. The full exercise ladder, with the lab's own run as the answer key, is in the lab's README under [Lab downloads](#lab-downloads).

### E1 — Reproduce: the all-too-faint generator

Compute the mean, the spread, both terms and the FD of the worked example's "all too faint" row by hand.

**Self-check:** FD = 0.0100 exactly, with a spread term of zero.

<details><summary>Answer</summary>

The mean is 5.20 / 8 = 0.65. Every value is a real value minus 0.1, so the spread stays 0.2525; the mean term is (0.75 − 0.65)² = 0.0100 and the spread term 0. Shifting a whole distribution costs only the mean term.

</details>

### E3 — Predict: a faint-only generator

Before computing, predict the FD and the within-0.05 count for a generator making only faint crescents: 0.45, 0.50, 0.50, 0.55, twice.

**Self-check:** FD 0.1096 and 8 of 8, because it is the strong-only generator mirrored about the real mean.

<details><summary>Answer</summary>

Its mean is 0.50 and its spread 0.0354, so the terms are (0.75 − 0.50)² = 0.0625 and (0.2525 − 0.0354)² = 0.0471: FD = 0.1096, the strong-only score, and all 8 values are real ones. FD cannot say which half of the variety went missing.

</details>

## References

### Lab downloads

- [`README.md`](LAB_01) — the lab's grade, what was executed, provenance, run order, and the E1–E3 exercise ladder.
- [`evaluate.py`](LAB_02) — crescent world, every generator and every metric in this post (FD, KID, precision, recall, density, coverage), in numpy.
- [`requirements.txt`](LAB_03) — the pinned numpy version.
- [`captures.json`](LAB_04) — the author's run, machine-readable, which every measured figure was drawn from.
- [`expected-output.txt`](LAB_05) — the same run as printed, to compare against your own.
- [`notebook.ipynb`](LAB_06) — the README with a runnable cell under each step and exercise.
- [Complete lab](https://minio.canery.in/media/lab-evaluating-generative-models.zip) — every file above in one zip.

### Sources

**Survey**

1. Borji. [Pros and Cons of GAN Evaluation Measures: New Developments](https://doi.org/10.1016/j.cviu.2021.103329). Computer Vision and Image Understanding, 2022.

**FID and its estimators**

2. Heusel, Ramsauer, Unterthiner, Nessler & Hochreiter. [GANs Trained by a Two Time-Scale Update Rule Converge to a Local Nash Equilibrium](https://arxiv.org/abs/1706.08500) (introduces FID). NeurIPS 2017.
3. Bińkowski, Sutherland, Arbel & Gretton. [Demystifying MMD GANs](https://arxiv.org/abs/1801.01401) (introduces KID). ICLR 2018.
4. Chong & Forsyth. [Effectively Unbiased FID and Inception Score and Where to Find Them](https://doi.org/10.1109/CVPR42600.2020.00611). CVPR 2020.
5. Parmar, Zhang & Zhu. [On Aliased Resizing and Surprising Subtleties in GAN Evaluation](https://doi.org/10.1109/CVPR52688.2022.01112) (clean-fid). CVPR 2022.

**Fidelity and diversity**

6. Sajjadi, Bachem, Lucic, Bousquet & Gelly. [Assessing Generative Models via Precision and Recall](https://arxiv.org/abs/1806.00035). NeurIPS 2018.
7. Kynkäänniemi, Karras, Laine, Lehtinen & Aila. [Improved Precision and Recall Metric for Assessing Generative Models](https://arxiv.org/abs/1904.06991). NeurIPS 2019.
8. Naeem, Oh, Uh, Choi & Yoo. [Reliable Fidelity and Diversity Metrics for Generative Models](https://proceedings.mlr.press/v119/naeem20a.html). ICML 2020.
9. Dhariwal & Nichol. [Diffusion Models Beat GANs on Image Synthesis](https://arxiv.org/abs/2105.05233). NeurIPS 2021.

**Feature networks and people**

10. Kynkäänniemi, Karras, Aittala, Aila & Lehtinen. [The Role of ImageNet Classes in Fréchet Inception Distance](https://arxiv.org/abs/2203.06026). ICLR 2023.
11. Stein, Cresswell, Hosseinzadeh, Sui, Ross, Villecroze, Liu, Caterini, Taylor & Loaiza-Ganem. [Exposing flaws of generative model evaluation metrics and their unfair treatment of diffusion models](https://arxiv.org/abs/2306.04675). NeurIPS 2023.
12. Jayasumana, Ramalingam, Veit, Glasner, Chakrabarti & Kumar. [Rethinking FID: Towards a Better Evaluation Metric for Image Generation](https://doi.org/10.1109/CVPR52733.2024.00889). CVPR 2024.
13. Karras, Aittala, Lehtinen, Hellsten, Aila & Laine. [Analyzing and Improving the Training Dynamics of Diffusion Models](https://arxiv.org/abs/2312.02696) (EDM2; the FD_DINOv2 comparison is in Appendix A.5 of arXiv v2). CVPR 2024.

**Text-to-image**

14. Hessel, Holtzman, Forbes, Le Bras & Choi. [CLIPScore: A Reference-free Evaluation Metric for Image Captioning](https://doi.org/10.18653/v1/2021.emnlp-main.595). EMNLP 2021.
15. Kirstain, Polyak, Singer, Matiana, Penna & Levy. [Pick-a-Pic: An Open Dataset of User Preferences for Text-to-Image Generation](https://arxiv.org/abs/2305.01569). NeurIPS 2023.
