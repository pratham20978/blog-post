---
title: "Training a Diffusion Model: The Decisions Before Step One"
slug: training-a-diffusion-model
date: 2026-10-07
updated: 2026-10-07
summary: "Five decisions fixed before a diffusion model's first gradient step: noise schedule, terminal SNR, prediction target, loss weighting and EMA, measured in a lab."
tags: [machine-learning, diffusion-model, generative-model, deep-learning, noise-schedule, model-training]
category: machine-learning
series: diffusion-models
series_position: 5
tier: L4
difficulty: advanced
prerequisites: ["Part 1 of this series", "the forward noising process", "ε-prediction", "a PyTorch training loop"]
reading_minutes: 43
cover_image: "COVER"
canonical_url: "https://canery.in/blogs/training-a-diffusion-model"
---

![Stable Diffusion's schedule ending at log-SNR −5.4, not minus infinity, beside crescents sampled with and without a pure-noise last step](COVER)

> [!NOTE]
> **Insights** — Before the first gradient step you fix five things a diffusion model cannot unlearn: the noise schedule (which noise levels training visits, and how often), its endpoint (whether the last step is pure noise), the prediction target (what the network's output means), the loss weighting (which noise levels win when one network cannot fit them all), and the weight average you sample with (the EMA). Stable Diffusion's schedule keeps 6.8% of the image's amplitude in its supposedly pure-noise last step; measured with an exact denoiser on the lab's toy images, that alone shrinks the brightness spread of 16,384-pixel samples to 35%, and more sampling steps converge on that wrong answer rather than away from it. The other four decisions move error between noise levels instead of removing it, which is why every published gain has to be read together with its setup.

**Level:** advanced · **You need:** Part 1 of this series (What a Diffusion Model Actually Does), the forward noising process and ε-prediction, a PyTorch training loop · **Time:** ~43 min

**Jump to:** [worked example](#worked-example) · [schedule](#what-does-the-noise-schedule-decide) · [terminal SNR](#why-must-the-last-step-be-pure-noise) · [target](#which-target-should-the-network-predict) · [weighting](#which-noise-levels-should-win-the-loss) · [EMA](#what-does-the-ema-buy-and-how-long-should-it-be) · [scaling](#how-does-training-scale) · [math](#the-math) · [implementation](#implementation)

> [!IMPORTANT]
> Numbers this post calls **measured** come from its lab, run on one laptop CPU. The lab uses a toy dataset of crescent images whose ideal denoiser has a closed form, so every error is measured against the best any network could do; its effects are mechanisms to carry over, not magnitudes. Schedule values are computed from the published formulas and match the papers to the last printed digit. Results quoted from papers say so and carry their setup, and an FID is only comparable within one paper's setup.

## Why this matters

Ask Stable Diffusion 2.1 for a "solid black background" and you get dull grey. <!-- L08 --> The prompt, the data and the network are not the problem. The noise schedule, fixed before training started, leaves 6.8% of every image's amplitude in the step that is supposed to be pure noise, and the network learned to use it. <!-- L07 --> Undoing that took a rescaled schedule, a different prediction target, a changed sampler and 50,000 more training steps. <!-- L09 --> <!-- L13 -->

Every decision in this post has that shape. It is one line of a training config (`beta_schedule`, `prediction_type`, `snr_gamma`, `ema_decay`), set before step one and paid for in every step after, and the training loss will not tell you it was wrong. <!-- L25 -->

## The problem

Training a diffusion model repeats one step. Draw a clean example $`x_0`$ from the data, a timestep $t$ and Gaussian noise $\epsilon$. Mix them into the network's input,

$$
x_t = \sqrt{\bar\alpha_t}\,x_0 + \sqrt{1-\bar\alpha_t}\,\epsilon ,
$$

where $`\bar\alpha_t`$ is the share of signal variance left at step $t$. Ask the network for a target, take the squared error, multiply it by a weight, and step the optimiser. Then update a running average of the weights. Part 1 of this series, What a Diffusion Model Actually Does, walks one forward and one reverse step through that formula; this post is about everything in it that is chosen rather than learned.

The quantity every choice is stated in is the **signal-to-noise ratio**, $`\mathrm{SNR}_t = \bar\alpha_t/(1-\bar\alpha_t)`$, or its natural log $`\lambda_t`$, the **log-SNR**. Large positive λ means almost clean; large negative λ means almost pure noise; λ = 0 is the point where signal and noise carry equal variance. Five decisions are fixed before the first step, and Figure 1 marks where each enters:

- **The noise schedule**, the fixed sequence $`\bar\alpha_1 > \dots > \bar\alpha_T`$. It decides which values of λ exist and how often training visits each one.
- **The endpoint**, the SNR at the last step $T$. It decides whether training ever sees what the sampler starts from.
- **The prediction target**: the noise ε, the clean example $`x_0`$, or a mix of the two called v. It decides what the network's output means, and so how its errors grow.
- **The loss weighting** $`w(\lambda)`$, a multiplier per noise level. It decides which noise levels win when the network cannot fit them all.
- **The EMA**, an exponential moving average of the weights. It decides which weights you actually sample with.

A sixth, the model's size and the number of steps, sets how much any of this matters.

![Flowchart of one training step from data, timestep and noise to network, weighted loss, optimiser and EMA, with five decisions marked](FIG_01)

*Figure 1. One training step, with each pre-training decision attached where it acts. The schedule appears twice: it chooses the timestep and it sets the mix. Only the EMA reaches the sampler.*

Three things make these decisions hard. First, one network serves every noise level. If each level had its own network, the weights in the loss would not change the answer at all; they matter only because 1,000 tasks share one set of parameters. <!-- L38 --> Every decision here is about where finite capacity goes. Second, they are coupled: changing the target changes the effective weighting, and changing the schedule changes how often each weight is applied. Third, the loss cannot referee them, because loss values under different formulations are not comparable and need not track sample quality. <!-- L25 --> A recent review organises the whole design space by forward process, reverse process and sampling; <!-- L01 --> this post takes the training half of that map, in the order the decisions bind.

## Worked example

Stable Diffusion v1 trains on 1,000 timesteps whose $`\sqrt{\beta_t}`$ rises in a straight line from $`\sqrt{0.00085}`$ to $`\sqrt{0.012}`$, the schedule its code calls "scaled linear", where $`\beta_t`$ is the variance added at step $t$. <!-- L05 --> Multiplying out $`\bar\alpha_T = \prod_t (1-\beta_t)`$ gives 0.0046601 at the last step, so the last training input is <!-- L07 -->

$$
x_T = 0.068265\,x_0 + 0.997667\,\epsilon .
$$

The step that is supposed to be pure noise still carries 6.8% of the image's amplitude. Its SNR is 0.004682, which looks negligible. Whether it is depends on how many numbers you average.

### Sixteen values: the leak is invisible

Take the series' running example, part 1's 4×4 crescent patch and its noise draw, and push it through that last step:

$$
x_T = \begin{bmatrix} -0.48 & 1.44 & 0.43 & -1.16 \\ 0.90 & -1.32 & -0.29 & 0.64 \\ 1.28 & 0.31 & -1.00 & 0.08 \\ -1.03 & 0.88 & 1.39 & -1.17 \end{bmatrix}
$$

Per pixel the image is gone: the top-left value 0.95 contributes 0.065 against noise of about one. Now average. The patch's mean is −0.1625, so the mean of $`x_T`$ carries $0.068265 \times (-0.1625) = -0.0111$ of signal. The noise in a mean of 16 values has standard deviation $0.9977/\sqrt{16} = 0.249$, so the leak is 0.04 of one standard deviation. No network could read it.

### 16,384 values: the leak becomes a measurement

Stable Diffusion does not denoise 16 numbers. Its latent for a 512×512 image is 4 channels of 64×64, or 16,384 numbers. <!-- L05 --> The same −0.0111 of leaked signal now sits against noise of $0.9977/\sqrt{16{,}384} = 0.0078$ in the mean: 1.42 standard deviations, for a patch only 0.16 below average brightness. An image half a unit brighter than average leaks 0.034, or 4.4 standard deviations. Averaging $n$ numbers divides the noise in their mean by $\sqrt n$ and leaves the signal alone, so for a flat image the mean's SNR is $n$ times the per-pixel SNR.

How much can a network learn from that? Suppose image brightness varies with standard deviation 0.3 around the dataset average. That spread is a model input, the one this post's lab uses, not a measured property of Stable Diffusion's latents. The best estimate of an image's brightness from the mean of its last-step input then explains a fraction

$$
R^2 = \frac{n\,\bar\alpha_T\,(0.3)^2}{n\,\bar\alpha_T\,(0.3)^2 + 1 - \bar\alpha_T}
$$

of the brightness variance: 0.7% at 16 values, 63% at 4,096, and 87% at 16,384. A network trained on this schedule therefore learns to read brightness off its last-step input, because the training data rewards it.

### What the sampler hands it

The sampler starts from pure Gaussian noise, whose mean is zero up to the same 0.0078 jitter. The network reads "average brightness" from every starting point and carries on from there. Follow the sampler's deterministic path with a perfect denoiser and the generated brightness spread shrinks to $`1/\sqrt{1-\bar\alpha_T+n\,\bar\alpha_T\,(0.3)^2}`$ of the data's (the [math section](#the-math) derives it): 99.9% at 16 values, 60.7% at 4,096 and 35.65% at 16,384. With an exact denoiser and a 50-step sampler, the lab measures 97.9%, 60.4% and 35.4%. Figure 2 sets the two sizes side by side.

![Part 1's 4×4 patch at Stable Diffusion's last step, beside the mean's leak rising from 0.04 to 1.42 noise s.d. as values grow to 16,384](FIG_02)

*Figure 2. The same 6.8% leak, seen through averages of different sizes. At 16 values the image's mean is buried; at Stable Diffusion's 16,384 latent values it is 1.4 standard deviations clear of the noise, and a network can learn to read it.*

### The fix, on the same numbers

Lin and colleagues' fix leaves $`\sqrt{\bar\alpha_1}`$ alone, moves $`\sqrt{\bar\alpha_T}`$ to zero, and rescales every value between linearly. <!-- L09 --> For this schedule that is

$$
\sqrt{\bar\alpha'_t} = \left(\sqrt{\bar\alpha_t} - 0.068265\right)\times\frac{0.999575}{0.999575-0.068265}.
$$

The series' running noise level, $`\sqrt{\bar\alpha} = 0.8`$, becomes 0.7854, so $`\bar\alpha`$ moves from 0.64 to 0.617. The middle of the schedule shifts by under 4%, and the end becomes exactly pure noise.

## Intuition

Think of training as one student preparing for a thousand exams with one brain. The schedule is the timetable: which exams exist and how often each is practised. The weighting is the marking scheme: how many points each exam is worth. The target is the answer format the student must write in, and some formats amplify a small slip into a large error. The EMA decides which week's version of the student walks into the exam hall. The endpoint decides whether the first exam on the day, pure noise, is one the student ever practised.

The analogy breaks in two places, and both matter. The exams share one brain, so practising one changes the others: fine-tuning a diffusion model on one band of timesteps improves nearby bands and hurts distant ones. <!-- L39 --> And there is no exam score during training. The loss is the marking scheme itself, so it cannot tell you whether the marking scheme was a good one; only samples can.

## What does the noise schedule decide?

A schedule ultimately sets one number per timestep, the log-SNR $`\lambda_t`$. Two things follow from it. Its endpoints, $`\lambda_1`$ and $`\lambda_T`$, bound which noise levels exist at all. Its slope decides how often training lands near each λ when $t$ is drawn uniformly, so it acts as a sampling density over noise levels. With the loss weighting held fixed, that density changes only how noisy the training estimate is, not what it converges to. <!-- L21 --> In the common case where the weighting is left implicit, as in the plain ε-loss, changing the schedule changes the weighting too.

Figure 3 draws the three schedules most code ships, plus the rescaled one from the worked example.

![Log-SNR against training progress for the linear, cosine and Stable Diffusion schedules and the zero-terminal-SNR rescale](FIG_03)

*Figure 3. Computed from the published formulas. The schedules differ most at the ends: the cosine reaches λ = −19.8, the linear −10.1, and Stable Diffusion stops at −5.4. The rescale lowers λ by less than 0.2 over the first half of the steps, by 1.6 at 90%, and sends the last step to minus infinity.*

DDPM's linear schedule raises β from $`10^{-4}`$ to 0.02, chosen small against data in −1 to 1 while keeping the last SNR low. <!-- L02 --> The cosine schedule was designed because the linear one destroys information faster than necessary; it sets $`\bar\alpha_t`$ from a squared cosine and clips β at 0.999 to avoid a singularity at the end. <!-- L04 --> Stable Diffusion's scaled-linear schedule is the outlier at the noisy end. In the lab's computation the linear schedule crosses SNR = 1 a quarter of the way through its steps, the cosine halfway, and Stable Diffusion's at 35%; their last log-SNRs are −10.1, −19.8 and −5.4.

### Where does training spend its samples?

Recent recipes skip the discrete schedule and draw λ from a chosen distribution. EDM draws the noise level σ log-normally, $`\ln\sigma \sim \mathcal N(-1.2,\ 1.2^2)`$, which puts λ at $`\mathcal N(2.4,\ 2.4^2)`$. <!-- L22 --> <!-- L23 --> Its reasoning is that loss can only be reduced at intermediate noise: at very low noise the task is both difficult and irrelevant, and at very high noise the best answer is the dataset average. <!-- L22 --> SD3 trains a rectified flow, $`z_t = (1-t)\,x_0 + t\,\epsilon`$, and draws $t$ from a logit-normal, which with its defaults puts λ at $`\mathcal N(0,\ 2^2)`$. <!-- L23 --> Figure 4 puts all of them on one axis.

![Densities of training log-SNR under the linear, cosine and SD schedules, EDM's log-normal at 2.4, and SD3's logit-normal at 0 and −2.2](FIG_04)

*Figure 4. Where each recipe draws its training noise levels, computed from the published definitions. Uniform timesteps under a schedule spread samples over a wide λ range; EDM aims at moderately clean images, SD3 at the signal-equals-noise point.*

Which density is best depends on the setup, and the largest comparison makes the point. SD3's authors trained 61 formulations on two datasets and ranked them over 24 combinations of sampler settings, dataset and EMA. Rectified flow with logit-normal sampling ranked first on average (1.54), the classic latent-diffusion ε-loss with the linear schedule 2.88, and EDM's own defaults last (15.58) in that text-to-image latent setting. <!-- L24 --> EDM's defaults were not wrong; they were tuned for another setup.

### Why does resolution move the schedule?

The SNR is a per-pixel ratio, but an image's coarse structure lives in averages over many pixels. Averaging an $s \times s$ window multiplies the SNR by $s^2$, so a schedule tuned at 64×64 hands a 256×256 model noise levels at which its coarse layout is still easy to read. <!-- L28 --> SD3 reaches the same conclusion from a constant image, whose $n$ pixels are $n$ observations of one value. <!-- L27 --> Both fixes shift log-SNR down by twice the log of the resolution ratio. simple diffusion shifts a 64×64 reference schedule to the target resolution: on ImageNet at 256×256 that took FID on the training set from 7.65 to 3.94. <!-- L28 --> SD3 trains and samples at 1024×1024 with a shift factor of 3, which lowers every λ by $2\ln 3 = 2.2$. <!-- L27 --> A preprint reaches the same conclusion from pixel redundancy and shows that scaling the input by a factor $b$ shifts the whole λ curve the same way. <!-- L29 --> Figure 5 shows the effect on one schedule.

![The cosine schedule's log-SNR per pixel and for 4×4 and 16×16 block means, 2.8 and 5.5 higher, beside the schedule shifted down by 2.8](FIG_05)

*Figure 5. One schedule, four views. Averaging a 4×4 block lifts the whole curve by 2.8 in log-SNR, a 16×16 block by 5.5. A schedule shifted down by 2.8 gives a 256-pixel image's coarse structure the noise levels the unshifted schedule gave a 64-pixel image.*

The same arithmetic says the data's scale is part of the schedule. SNR is defined against the data's variance, so latent diffusion rescales its autoencoder's latents to unit standard deviation before diffusing them, and found that the latent scale significantly changes results. <!-- L06 --> That is where Stable Diffusion's 0.18215 comes from. <!-- L05 --> EDM2 standardises its latents to a standard deviation of 0.5 instead, to match its σ_data. <!-- L30 --> Swap the autoencoder and keep the factor, and you have silently changed every noise level.

## Why must the last step be pure noise?

The schedule's endpoint deserves its own decision because it is the one place where training and sampling meet. Lin and colleagues computed it for the three schedules above: $`\sqrt{\bar\alpha_T}`$ is 0.006353 for the linear schedule, $`4.93 \times 10^{-5}`$ for the cosine, and 0.068265 for Stable Diffusion's. <!-- L07 --> Stable Diffusion's terminal SNR is 116 times the linear schedule's. The cosine stays above zero only because of its β clip, and a variance-exploding process, which adds noise without shrinking the signal, cannot reach zero at all. <!-- L10 -->

### What the leak does, with a perfect denoiser

The worked example predicted the damage; the lab measures it without a trained network. Its toy images are four crescent shapes whose brightness varies with standard deviation 0.3, and its denoiser is the exact posterior mean $`E[x_0 \mid x_t]`$, so no learning error can hide anything. A 50-step deterministic DDIM sampler starts from pure noise under Stable Diffusion's schedule. Figure 6 shows what comes out at 128×128, which is 16,384 values like the latent.

![Crescent samples from the data, Stable Diffusion's schedule and the rescaled one at 16,384 pixels, with brightness histograms](FIG_06)

*Figure 6. Measured with an exact denoiser, same starting noise for both schedules. The data's crescents range from dark to bright; under Stable Diffusion's schedule the samples are correctly shaped and all medium grey. Outside the data's central 90% of brightness lie 9.9% of the data, none of the 4,000 flawed samples, and 5.5% of the rescaled ones.*

The shapes are right and the brightness is wrong, which is exactly the failure Lin and colleagues describe in the real model. <!-- L08 --> Figure 7 separates the cause from everything else.

![Brightness spread kept against pixel count and against sampling steps: the flawed schedule stays near 0.36, the rescaled one nears 1](FIG_07)

*Figure 7. Measured with an exact denoiser. Left: the flawed schedule's loss of brightness spread follows the closed form (dots on the line) and grows with pixel count; starting from the true noisy distribution instead of pure noise removes it. Right: more steps do not help the flawed schedule, which converges on its predicted 0.357; the rescaled schedule's shortfall is sampler error and shrinks with steps.*

Three measurements settle it. Start the same sampler from the true distribution of $`x_T`$, signal and all, and the spread comes back to 99.3%: the start mismatch is the whole cause. Start from pure noise at 16 pixels and the leak is invisible. Add sampling steps and the flawed schedule does not recover: on a separate draw of 1,000 samples it keeps 35.5%, 35.6%, 35.7% and 35.7% at 25, 50, 100 and 200 steps, converging on the 35.65% the closed form predicts. A training-and-sampling mismatch is a fixed point, not a discretisation error.

The rescaled schedule keeps 85.1% at 50 steps; in the step sweep it rises to 96.4% at 200. That residue is the sampler's own error at the start of the trajectory, where the noise level changes fastest; it is the subject of a later part of this series. The sampler's step spacing matters too. Leading spacing, used by the official DDIM and PNDM code, never visits the last training step; with 50 steps the first one is at index 981 of 0–999. <!-- L12 --> <!-- L17 --> There $`\sqrt{\bar\alpha}`$ is 0.0760, and the lab measures 32.2% of the spread instead of 35.4%.

### What it does to a real model

Lin and colleagues fine-tuned Stable Diffusion 2.1-base with all four fixes. Figure 8 is their own comparison, reproduced unchanged.

![Lin et al.'s Figure 3: eight prompt pairs from reference Stable Diffusion and the fixed model, including a solid black background](FIG_08)

*Figure 8. Reproduced unchanged from Lin, Liu, Li & Yang, "Common Diffusion Noise Schedules and Sample Steps are Flawed" (WACV 2024), Figure 3, [arXiv:2305.08891](https://arxiv.org/abs/2305.08891), licensed [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). In each pair the reference model is on the left; "Solid black background" is the clearest case.*

Measured on 10,000 COCO captions with the same 50-step sampler, the fixed model's FID fell from 22.96 to 21.66 and its Inception Score rose from 34.11 to 36.16, against a reference trained on the same data. <!-- L13 --> The same mismatch shows up elsewhere. Video models' initial noise differs from what they were trained on in its low-frequency content, and that content steers the result. <!-- L19 --> One paper turns the leak into a control: adding a modelled leak to the starting noise sets brightness and style without training. <!-- L20 -->

### What the fix costs

Lin and colleagues propose four fixes, and each has a reason. <!-- L09 --> Three of them change training and sampling:

1. **Rescale the schedule** as in the worked example, or, for a cosine schedule, drop the β clip. <!-- L10 -->
2. **Change the target.** At zero SNR the input is pure noise, so predicting ε is trivial and teaches the network nothing; they switch to v, whose target at the last step is $`-x_0`$, the clean image up to sign, so a network with no signal to read learns the data's mean. <!-- L11 --> <!-- L14 -->
3. **Start the sampler at the last step** (trailing spacing).

The fourth, rescaling classifier-free guidance, belongs with guidance later in this series. The first two have a consequence for code: **write the sampler through $`x_0`$.** Code that converts the output to ε first divides by $`\sqrt{\bar\alpha_T} = 0`$. <!-- L16 --> diffusers' Euler and DPM-Solver schedulers patch the rescaled $`\bar\alpha_T`$ to $`2^{-24}`$, close to zero without being zero, so the first σ is finite. <!-- L17 -->

Before the fix, practice reached for **offset noise**: shift each channel's noise by a shared random amount, so the model stops trusting its input's mean. SDXL's final training stage used an offset of 0.05. <!-- L18 --> It does let the model produce very dark and very bright images, but it changes the training distribution, can produce brightness the data never had, and leaves the cause in place. <!-- L15 -->

## Which target should the network predict?

The target looks like a modelling choice, but it is a numerical one. At one noise level, the squared errors in ε, $`x_0`$ and v are constant multiples of each other. The ε-loss, for example, is the $`x_0`$-loss weighted by the SNR, <!-- L31 --> so all three share a minimiser. What differs is how an error in the network's output reaches the quantities the sampler uses. v is defined as $`v = \sqrt{\bar\alpha_t}\,\epsilon - \sqrt{1-\bar\alpha_t}\,x_0`$, and $`x_0 = \sqrt{\bar\alpha_t}\,x_t - \sqrt{1-\bar\alpha_t}\,v`$ recovers the clean image from it. <!-- L31 -->

Suppose the network's output is off by δ. Figure 9 plots what that does to the clean-image estimate and to the noise estimate, as a function of λ.

![Error amplification against log-SNR for ε, x0 and v outputs: ε explodes at high noise, x0 at low noise, and v stays at or below one](FIG_09)

*Figure 9. Computed. An ε-network's error reaches the clean image multiplied by $`e^{-\lambda/2}`$, which is 90 at λ = −9; an $`x_0`$-network's error reaches the noise estimate multiplied by $`e^{\lambda/2}`$. v never multiplies an error by more than one.*

This is the argument behind v. As the SNR goes to zero, recovering $`x_0`$ from a predicted ε divides by $`\sqrt{\bar\alpha_t} \to 0`$, so small output changes are amplified without limit. <!-- L31 --> EDM states the same thing for its noise-scale view: with an ε-style output, any network error is multiplied by σ. EDM picks the output scaling that amplifies errors as little as possible while keeping the network's inputs and targets at unit variance. <!-- L33 --> For data of unit variance that choice is exactly v, as the [math section](#the-math) shows. Imagen Video's authors, in a preprint, report that v also avoided colour-shifting artefacts at high resolution and converged faster than ε. <!-- L35 -->

### Capacity is the other half

Amplification is half the story; the other half is what the network can represent. The lab trains the same small network, a three-layer MLP, with the three targets and one shared objective (Min-SNR-5, introduced in the next section, converted so all three optimise the same loss in expectation). Only the output's meaning changes. At width 256, wider than the 64-pixel data, all three train, and ε pays for amplification: it predicts the noise at λ = −9 to a squared error of 0.0077 per value, and converting that to a clean image multiplies it by $`e^{9}`$, about 8,100, for an excess error of 62. v's samples land closest to the data, at a median distance of 0.072, against 0.153 for ε and 0.443 for $`x_0`$, whose samples degraded in two of three seeds between 10,000 and 20,000 steps while its measured error kept falling. At width 32, narrower than the data, the ranking flips. ε fails outright, with an excess error of 4,275 at λ = −9 and every sampler blown up. v's samples drift to 0.807 and one of its three seeds blew up, and $`x_0`$ is the one target that still works, at 0.091. Figure 10 shows where each one fails.

![Measured excess error over the exact denoiser against log-SNR for ε, x0 and v prediction, at network width 256 and at width 32](FIG_10)

*Figure 10. Measured, three seeds each, same objective. Lines are the excess error over the exact denoiser after 20,000 steps; the numbers below are median sample distances from the σ_rel = 0.10 power average, where two independent draws of the data sit 0.063 apart. Wide, ε pays at the noisy end; narrow, it fails outright and only $`x_0`$ still samples well.*

The reason is that a clean image is simple and noise is not. An ε-network at high noise must reproduce its own 64-dimensional input almost exactly, and a 32-wide last layer cannot: its 64 outputs are combinations of 32 numbers, so at least half the noise is out of reach. At λ = −9 that alone costs an excess error of about $`0.5 \times e^{9} \approx 4{,}050`$, and the lab measured 4,275. v's target, $`\sqrt{\bar\alpha_t}\,\epsilon - \sqrt{1-\bar\alpha_t}\,x_0`$, carries a share of the noise too; counted in clean-image units that share is largest at λ = 0, where v's narrow error has its hump. An $`x_0`$-network only has to land on four crescents and a brightness. A CVPR 2026 study found the same at scale. Pixel-space transformers on ImageNet 256, with 768 values per patch, scored FID 372–395 predicting ε and 97–127 predicting v, against 8.6–10.5 predicting $`x_0`$, whatever space the loss was computed in. At ImageNet 64, with 48 values per patch, all nine combinations landed between 3.46 and 6.20. <!-- L36 --> Its authors' explanation is the manifold one: clean images lie near a low-dimensional surface, noise does not, and loss weighting alone cannot fix a network that has to carry the noise. <!-- L37 --> It is one study, and the effect depends on per-token dimension, not on image size.

So the target is a decision about two things. Where will errors be amplified, and can the network carry what you ask it to output? v is the safe default: it amplifies no error by more than one, and, like $`x_0`$, it survives a zero terminal SNR. $`x_0`$ wins when the data per token outgrows the network. ε is fine with a nonzero terminal SNR and ample capacity, which describes most models trained before 2023.

## Which noise levels should win the loss?

The loss weighting $`w(\lambda)`$ multiplies the squared error at each noise level. Because every common loss can be written as one weighted error over λ, the weighting is the only thing that really distinguishes them, and it matters only because the noise levels share parameters. <!-- L38 --> A weighting is a decision about which levels the network gets right when it cannot get all of them right.

### What Min-SNR changes

Min-SNR-γ, from Hang and colleagues, treats each timestep as a task and reads slow training as tasks fighting over shared weights: fine-tuning on one band of timesteps helped nearby bands and hurt distant ones. <!-- L39 --> Written as a weight on the $`x_0`$ error, the plain ε-loss is $`\mathrm{SNR}`$, a weight that grows without limit as noise vanishes. Min-SNR caps it at $`\min(\mathrm{SNR}, \gamma)`$ with γ = 5. For an ε-network that is $`\min(\gamma/\mathrm{SNR},\ 1)`$, and for v the weight is divided by SNR + 1. <!-- L40 -->

The headline is a 3.4× speed-up to FID 10 on ImageNet 256 latents with a ViT-B. Read the setup before the number: that comparison is among $`x_0`$-prediction weightings, where plain SNR weighting was the worst. <!-- L41 --> On their UNet the picture depends on the target, as the table shows. <!-- L42 -->

| UNet, ImageNet 256 latents | FID at 200K steps | FID at 1M steps |
|---|---:|---:|
| $`x_0`$-prediction, constant weight | 25.93 | 8.33 |
| $`x_0`$-prediction, Min-SNR-5 | 7.99 | 4.28 |
| ε-prediction, standard loss | 8.55 | 4.21 |
| ε-prediction, Min-SNR-5 | 7.32 | 4.14 |

Against the standard ε-loss, Min-SNR's gain is 14% at 200K steps and 2% at 1M. The choice of γ barely matters: across γ = 1, 5, 10 and 20, FID moved by at most 0.57 in any of four settings. <!-- L43 -->

### Where a weighting puts the error

Hang and colleagues explain the speed-up by looking at error per noise level: constant weighting does well at high noise and badly at low noise, SNR weighting the reverse. <!-- L41 --> The lab measures the same thing against the exact denoiser, with four weightings on an $`x_0`$-predicting network: constant, SNR, Min-SNR-5, and Salimans and Ho's truncated SNR, $`\max(\mathrm{SNR}, 1)`$. <!-- L32 --> Each curve is the error a weighting leaves behind at each λ, and Figure 11 shows them.

![Measured excess error by log-SNR for constant, SNR, truncated-SNR and Min-SNR-5 weighting of an x0-predicting network](FIG_11)

*Figure 11. Measured, three seeds each, 40,000 steps; the dashed curve is the exact denoiser's own error, the floor no network can beat. Each weighting buys accuracy at one end of the noise range with error at the other. SNR weighting's error at the noisiest levels exceeds even that floor, and every sampler built on it blew up.*

The trade is visible at both ends. Constant weighting leaves an excess error of 0.0014 at λ = −9, a quarter of a percent of the exact denoiser's own error there, but 0.0105 at λ = 9, about a hundred times the ideal. SNR weighting, the plain ε-loss's weighting applied here to an $`x_0`$-network, does the reverse so thoroughly that at λ = −9 its error, 1.25, is more than twice the exact denoiser's. Its sampler blew up in 80 of 84 evaluations across three seeds, four checkpoints and seven weight averages: a sampler starts at exactly the noise levels this weighting left untrained. Min-SNR-5 is the most accurate of the four from λ = −1 to the clean end, and it too neglects the noisiest levels, because below SNR 5 its weight is the SNR itself. Its samples and constant weighting's landed at about the same distance from the data, a median of 0.098 against 0.105, where two independent draws of the data sit 0.063 apart. This toy reproduces the per-level trade-off and the failure of SNR weighting; it does not reproduce Min-SNR's convergence gap over constant weighting.

Other weightings move the same budget around. P2 weighting divides the standard weight by $`(k+\mathrm{SNR})^\gamma`$, on the argument that nearly clean levels only teach imperceptible detail; at 256×256 it lowered FID from 7.86 to 6.92 on FFHQ and from 9.60 to 6.95 on CUB. <!-- L44 --> On ImageNet 64, Kingma and Gao's monotonic sigmoid weighting lowered FID from 1.85 to 1.68 against the standard cosine ε-loss. <!-- L45 --> In EDM's ablation, the new weighting together with its log-normal noise sampling improved FID in every setting tested, for example from 2.09 to 1.88 on conditional CIFAR-10. <!-- L34 --> EDM2 then found that a weighting set at initialisation drifts as training proceeds, so it tracks the loss at each noise level and divides by it as it goes. <!-- L48 -->

### Reweight, or resample?

A weight and a sampling density are two ways to spend the same budget. Training twice as often at one λ and doubling its weight give the same objective in expectation, but not the same gradient noise. <!-- L21 --> Hang and colleagues' follow-up tested this directly on DiT-B/2 with ImageNet 256 latents and a fixed 500K-iteration budget, sampling log-SNR from distributions concentrated near zero instead of reweighting it. <!-- L46 --> Figure 12 shows the result.

![FID-10K bars for DiT-B/2 on ImageNet 256: cosine, EDM, flow matching, Min-SNR, Soft-Min-SNR, Laplace, Cauchy, scaled and shifted cosine](FIG_12)

*Figure 12. Quoted from Hang et al. (ICCV 2025), Table 3: FID-10K, the best of guidance scales 1.5, 2 and 3 for each method. Reweighting (Min-SNR, Soft-Min-SNR) beat the baseline; moving the samples toward λ = 0 (Laplace, Cauchy, scaled cosine) beat reweighting, while simple diffusion's shifted cosine did not beat the baseline in this setup.*

The cosine baseline scored 10.85, Min-SNR 9.70, Soft-Min-SNR 9.07 and the Laplace schedule 7.96. <!-- L46 --> The Laplace schedule also beat cosine for every target: $`x_0`$ 11.16 to 8.48, v 11.06 to 7.96, ε 10.46 to 9.53. <!-- L47 --> It is one group's measurement on one model, but it reframes the decision. The weighting and the schedule are one knob, and turning the sampling half of it lowers gradient noise as well.

## What does the EMA buy, and how long should it be?

The **EMA** (exponential moving average) is a second copy of the weights, updated after every step as $`\bar\theta \leftarrow \beta\bar\theta + (1-\beta)\,\theta`$, where θ is the trained weights and β the decay. <!-- L49 --> You sample with $`\bar\theta`$, not θ. It exists because a constant-learning-rate optimiser never settles: the raw weights keep jittering around a good region, and the average sits closer to its centre. Averaging reduces the noise of stochastic updates and needs less learning-rate decay than plain SGD. <!-- L56 --> In score-based models it stabilised FID during training and removed colour-shift artefacts. <!-- L53 -->

The decay is easier to reason about as a **half-life**: the number of steps after which a weight's influence has halved, $`\ln 2/\ln(1/\beta) \approx 0.693/(1-\beta)`$. A decay of 0.999 has a half-life of 693 steps; 0.9999 has 6,931. DDPM used 0.9999 and did not sweep it; <!-- L03 --> ADM and DiT used 0.9999 too, and DiT reports every result from the EMA weights. <!-- L54 --> <!-- L55 --> SD3's comparison updated its EMA every 100 batches with decay 0.99, which is a per-step half-life of about 6,900 steps. <!-- L26 -->

The trap is the start. An EMA initialised to the random starting weights still gives them weight $`\beta^t`$ after $t$ steps: with 0.9999 that is 13.5% after 20,000 steps and 1.8% after 40,000. A decay chosen for a long run is wrong for a short one, and the right half-life grows with the run. EDM2 makes that explicit with a power-function average whose update uses $`\beta(t) = (1-1/t)^{\gamma+1}`$. It puts zero weight on the initial parameters and stretches with training time, and its width is given as $`\sigma_\text{rel}`$, a fraction of the run's length. <!-- L49 --> EDM2 also stores two such averages in snapshots during training, so that any EMA length can be reconstructed afterwards by least squares. <!-- L50 --> Its sweeps found that the best EMA length differs considerably between configurations, drifts longer as training proceeds, and depends strongly on guidance strength. It also gets shorter with a higher learning rate, a larger model or simpler data. <!-- L51 -->

Figure 13 shows the profiles and what the lab measured.

![EMA weight over past steps for decays 0.999 and 0.9999 and power averages, beside measured sample distance for raw weights and six EMAs](FIG_13)

*Figure 13. Left, computed: how much each average weights each past step at the end of a 40,000-step run; the 0.9999 average still holds 1.8% of the random initialisation. Right, measured: median sample distance of nine stable runs. The short averages beat the raw weights throughout; the 0.9999 average starts far behind and catches up as its initialisation decays, while the σ_rel = 0.20 average falls behind as the run grows.*

The lab ran that sweep on its nine stable runs. The averages with half-lives of 69 and 693 steps, and the power averages at σ_rel 0.05 and 0.10, kept a median sample distance between 0.092 and 0.105 at every checkpoint, below the raw weights' 0.11 to 0.15. The raw weights and the 69-step average, which follows them closely, each blew up twice in 36 evaluations; no longer average ever did. The 0.9999 average shows the trap: 0.94 at 5,000 steps, when 61% of it was still the random initialisation, improving to 0.25 at 40,000 and still the worst. The power average at σ_rel 0.20 moved the other way, from 0.096 to 0.19, as a fifth of a longer run reached back into weights that were still poor. In this toy short averages were enough; what transfers is the arithmetic, not the winner.

## How does training scale?

A training step costs about three forward passes, because the backward pass costs roughly twice the forward pass. <!-- L57 --> That makes training budgets easy to estimate. DiT-XL/2 costs 118.64 Gflops per forward pass at 256×256, counting a multiply-add once. <!-- L58 --> With a multiply-add counted as two FLOPs, that is 237 GFLOP forward and about 712 GFLOP per image per training step. Its headline run, 7M steps at batch 256 to FID 2.27 with guidance, <!-- L58 --> therefore cost about $1.3 \times 10^{21}$ FLOPs, and its 400K-step comparison runs about $7.3 \times 10^{19}$.

What does more compute buy? SD3 trained models of several depths for 500K steps at 256×256 with batch 4096. Validation loss fell smoothly with both model size and steps, tracked GenEval, human preference and T2I-CompBench, and showed no sign of saturating. <!-- L59 --> Larger models also degrade less when sampled in few steps: the CLIP-score drop at 5 of 50 steps fell from 4.30% at depth 15 to 2.71% at depth 38. <!-- L60 --> Liang and colleagues fitted isoFLOP curves for rectified-flow transformers between $`10^{17}`$ and $`6\times10^{18}`$ FLOPs and found the compute-optimal parameter count grows as $`C^{0.568}`$. Their loss trend tracked FID, and it predicted the loss of a roughly 1B-parameter model at $`1.5\times10^{21}`$ FLOPs. <!-- L61 --> Figure 14 shows EDM2's size ladder and the lab's own capacity sweep.

![EDM2's ImageNet-512 FID falling with parameters from 125M to 1.5B, beside the lab's excess error against width for two weightings](FIG_14)

*Figure 14. Left, quoted from EDM2 (CVPR 2024), Table 2: ImageNet-512, 63 network evaluations per image, deterministic sampling. FID keeps falling from 125M to 1.5B parameters, by less each time. Right, measured: $`x_0`$-networks after 20,000 steps, mean of two seeds, at the noisiest and the cleanest level. Width cuts the clean-end error under both weightings, while SNR weighting's error at λ = −9 grows from 0.10 to 3.0.*

On ImageNet-512, EDM2's FID without guidance fell from 3.53 at 125M parameters to 2.56 at 280M, 2.06 at 777M and 1.91 at 1.5B. <!-- L52 --> The lab's width sweep shows what extra capacity does once the weighting has decided where the gradient goes. With Min-SNR-5, the error at the cleanest level fell fivefold between width 32 and 256. With SNR weighting, the noisiest level, which that weighting barely trains, got worse as the network grew, from 0.10 to 3.0, and the samples followed: usable at width 32, erratic at 64, and blown up for every seed and every average from 128 up. A bigger network spends its capacity where the loss sends gradient; it does not repair a level the weighting ignores. Min-SNR's samples were not immune either: with one learning rate for every width, one of two seeds degraded at width 256 and one blew up at 512.

Two results temper "bigger is better". Under a fixed sampling budget, smaller latent diffusion models frequently beat larger ones, because they can afford more steps. <!-- L62 --> And when backbones were scaled from 0.4B to 4B parameters on up to 600M images, the training set's quality and diversity mattered more than its size. <!-- L63 --> Scale is a decision too, about where the budget goes: model, steps, data, or sampling.

## The math

| Symbol | Meaning |
|---|---|
| $`\bar\alpha_t`$ | share of signal variance left at step $t$; $`x_t = \sqrt{\bar\alpha_t}x_0 + \sqrt{1-\bar\alpha_t}\epsilon`$ |
| $`\lambda_t`$ | log-SNR, $`\ln\big(\bar\alpha_t/(1-\bar\alpha_t)\big)`$ |
| $n$ | number of values in one example (pixels or latent entries) |
| $`s_b`$ | standard deviation of an example's mean brightness across the dataset |
| τ | per-value detail noise in the lab's toy (0.1) |
| δ | an error in the network's output |
| $`w(\lambda)`$ | loss weight on the $`x_0`$ error at log-SNR λ |
| β | EMA decay per step |

**The leak.** Let $e = \mathbf 1/\sqrt n$ be the unit vector along "brightness". In the toy, an example's coordinate along $e$ is $`u_0 \sim \mathcal N(0, V_0)`$ with $`V_0 = n s_b^2 + \tau^2`$, independent of its shape. The forward process makes it $`u_T \sim \mathcal N(0,\ \bar\alpha_T V_0 + 1 - \bar\alpha_T)`$. A deterministic sampler with a perfect denoiser maps that Gaussian onto the data linearly. Fed $`\mathcal N(0, 1)`$ instead, it scales the output spread by

$$
\rho = \frac{1}{\sqrt{1 - \bar\alpha_T + \bar\alpha_T\,(n s_b^2 + \tau^2)}} .
$$

The generated brightness spread is ρ times the data's. With $`\bar\alpha_T = 0.0046601`$, $`s_b = 0.3`$ and τ = 0.1, ρ is 0.9990 at $n$ = 16 and 0.3565 at $n$ = 16,384, the values the worked example quoted.

<details>
<summary>Why the map is linear, and where R² comes from</summary>

Along $e$ the data is a one-dimensional Gaussian, and it is independent of the other directions because every crescent has the same mean. For Gaussian data the probability-flow ODE is linear, so it maps the quantiles of $`\mathcal N(0, V_T)`$ onto those of $`\mathcal N(0, V_0)`$: $`u_0 = \sqrt{V_0/V_T}\,u_T`$ with $`V_T = \bar\alpha_T V_0 + 1 - \bar\alpha_T`$. Starting from $`u_T \sim \mathcal N(0, 1)`$ gives $`\operatorname{Var} u_0 = V_0/V_T`$, a spread ratio of $`1/\sqrt{V_T}`$. The brightness that the last step reveals is the regression of $`u_0`$ on $`u_T`$, whose explained share is $`\bar\alpha_T V_0 / V_T`$; for $`V_0 \approx n s_b^2`$ this is the $R^2$ of the worked example. A 50-step DDIM sampler is not the exact ODE, which is why the lab measures 0.354 rather than 0.357.

</details>

**The rescale.** With $`a_1 = \sqrt{\bar\alpha_1}`$ and $`a_T = \sqrt{\bar\alpha_T}`$, the zero-terminal-SNR schedule is <!-- L09 -->

$$
\sqrt{\bar\alpha'_t} = \frac{a_1}{a_1 - a_T}\left(\sqrt{\bar\alpha_t} - a_T\right).
$$

It keeps the first value, sends the last to zero, and moves each value between in proportion. For Stable Diffusion $`a_1 = 0.999575`$ and the factor is 1.0733.

**Amplification.** From $`x_t = \sqrt{\bar\alpha}\,x_0 + \sqrt{1-\bar\alpha}\,\epsilon`$, an error δ in each output becomes these errors in the two estimates the sampler uses:

| Output | Error in the $`x_0`$ estimate | Error in the ε estimate |
|---|---|---|
| ε | $`\delta\,\sqrt{(1-\bar\alpha)/\bar\alpha} = \delta\,e^{-\lambda/2}`$ | δ |
| $`x_0`$ | δ | $`\delta\,e^{\lambda/2}`$ |
| v | $`\delta\sqrt{1-\bar\alpha} \le \delta`$ | $`\delta\sqrt{\bar\alpha} \le \delta`$ |

ε and $`x_0`$ each blow up at one end of the λ range; v is bounded by one at both.

**Weights in three currencies.** The squared errors are related by $`\lVert\epsilon-\hat\epsilon\rVert^2 = \mathrm{SNR}\,\lVert x_0-\hat x_0\rVert^2`$ and $`\lVert v-\hat v\rVert^2 = (1+\mathrm{SNR})\,\lVert x_0-\hat x_0\rVert^2`$. A weight $`w`$ on the $`x_0`$ error is therefore $`w/\mathrm{SNR}`$ on the ε error and $`w/(1+\mathrm{SNR})`$ on the v error. That is how the lab gives three targets one objective, and how Min-SNR's $`\min(\mathrm{SNR}, 5)`$ becomes $`\min(5/\mathrm{SNR}, 1)`$ for ε. <!-- L40 -->

<details>
<summary>EDM's preconditioning is v when the data has unit variance</summary>

EDM writes the denoiser as $`D(x;\sigma) = c_\text{skip}\,x + c_\text{out}\,F(c_\text{in}\,x)`$ for $`x = x_0 + \sigma n`$, with $`c_\text{skip} = \sigma_d^2/(\sigma^2+\sigma_d^2)`$, $`c_\text{out} = \sigma\sigma_d/\sqrt{\sigma^2+\sigma_d^2}`$ and $`c_\text{in} = 1/\sqrt{\sigma^2+\sigma_d^2}`$, where $`\sigma_d`$ is the data's standard deviation. <!-- L33 --> The network's effective target is $`(x_0 - c_\text{skip}\,x)/c_\text{out}`$. Set $`\sigma_d = 1`$ and substitute $`x = x_0 + \sigma n`$:

$$
\frac{x_0 - \frac{x_0+\sigma n}{\sigma^2+1}}{\sigma/\sqrt{\sigma^2+1}} = \frac{\sigma x_0 - n}{\sqrt{\sigma^2+1}} .
$$

In variance-preserving terms $`\sigma^2 = (1-\bar\alpha)/\bar\alpha`$, so $`\sigma/\sqrt{\sigma^2+1} = \sqrt{1-\bar\alpha}`$ and $`1/\sqrt{\sigma^2+1} = \sqrt{\bar\alpha}`$. The target becomes $`\sqrt{1-\bar\alpha}\,x_0 - \sqrt{\bar\alpha}\,n = -v`$. EDM's choice, derived from unit variance and minimal amplification, is v up to sign.

</details>

**EMA.** After $t$ updates, the exponential average gives step $t - k$ the weight $`(1-\beta)\beta^{k}`$ and the initial weights $`\beta^t`$, so the half-life is $`\ln 2/\ln(1/\beta)`$. EDM2's power-function average gives step τ a weight proportional to $`\tau^\gamma`$, and its relative width is <!-- L49 -->

$$
\sigma_\text{rel} = \frac{\sqrt{\gamma+1}}{(\gamma+2)\sqrt{\gamma+3}} ,
$$

so $`\sigma_\text{rel}`$ = 0.10 is γ ≈ 6.94: the average covers about the last tenth of the run, however long the run is.

## Implementation

The decisions fit in about forty lines of PyTorch. This training step encodes all five at once: Stable Diffusion's schedule with the zero-SNR rescale, a v target, Min-SNR-5 weighting and an EMA. The lab's own step has the same shape on a cosine schedule; the runnable file is under [Lab downloads](#lab-downloads).

```python
import math, torch

T = 1000
betas = torch.linspace(0.00085 ** 0.5, 0.012 ** 0.5, T, dtype=torch.float64) ** 2   # SD's scaled linear
abar = torch.cumprod(1 - betas, 0)

def zero_terminal_snr(abar):                       # Lin et al., Algorithm 1, in sqrt(abar) space
    r = abar.sqrt()
    r0, rT = r[0].clone(), r[-1].clone()
    return ((r - rT) * r0 / (r0 - rT)) ** 2       # first value kept, last exactly 0

abar = zero_terminal_snr(abar).float()

def min_snr_weight(snr, target, gamma=5.0):       # Min-SNR-5, converted to the target's own units
    w_x0 = snr.clamp(max=gamma)                    # weight on ||x0 - x0_hat||^2
    k = {"eps": snr, "x0": torch.ones_like(snr), "v": snr + 1}[target]
    return w_x0 / k

def train_step(net, opt, ema, x0, target="v", ema_decay=0.999):
    t = torch.randint(0, T, (x0.shape[0],))
    a = abar[t].sqrt()[:, None]                    # sqrt(abar_t)
    s = (1 - abar[t]).sqrt()[:, None]              # sqrt(1 - abar_t)
    eps = torch.randn_like(x0)
    xt = a * x0 + s * eps
    snr = abar[t] / (1 - abar[t])                  # exactly 0 at the last step after the rescale
    goal = {"eps": eps, "x0": x0, "v": a * eps - s * x0}[target]
    out = net(xt, t)
    loss = (min_snr_weight(snr, target) * ((out - goal) ** 2).mean(1)).mean()
    opt.zero_grad(set_to_none=True)
    loss.backward()
    opt.step()
    with torch.no_grad():                          # sample with these weights, not the raw ones
        for p_ema, p in zip(ema.parameters(), net.parameters()):
            p_ema.lerp_(p, 1 - ema_decay)
    return loss.item()
```

Three details carry the decisions. The rescale works on $`\sqrt{\bar\alpha}`$, not on β or the SNR. After it, the last step's SNR is zero, and the conversion to ε units, $`\min(\mathrm{SNR}, 5)/\mathrm{SNR}`$, computes 0/0 there, which is one more reason the default target here is v. For v the converted weight, $`\min(\mathrm{SNR}, 5)/(\mathrm{SNR}+1)`$, is exactly zero at that step: below SNR 5, Min-SNR's weight is the SNR itself, so the network learns the zero-SNR step only through its neighbours. The EMA update is one `lerp_` per parameter. Its decay must be chosen against the run length, or initialised from the network after a warm-up rather than from random weights.

Sampling must go through $`x_0`$: convert the output to $`x_0`$ first, then to ε, and never divide by $`\sqrt{\bar\alpha_T}`$ at a zero-SNR step. <!-- L16 --> The lab's `ddim` function is written that way, and so is its exact denoiser. That denoiser is a closed-form posterior mean over the four crescents, and it is what every "excess error" in this post is measured against.

## Limitations and common mistakes

> [!WARNING]
> **Common mistake: comparing loss values across decisions.** A run with Min-SNR weighting and one with the plain ε-loss optimise different functions, so their loss curves are not on the same scale. In the lab, Min-SNR's runs ended at a training loss of 0.029 and constant weighting's at 0.112, yet their samples were within 7% of each other. SD3's authors compared 61 formulations by CLIP score and FID for exactly this reason. <!-- L25 --> Compare samples, or the per-level error against a fixed reference, never the training loss.

- **Pairing ε-prediction with zero terminal SNR.** At the last step the ε target is the input itself and $`x_0 = (x_T - \epsilon)/0`$. <!-- L11 --> <!-- L16 --> The symptom is NaN or exploding samples on the first sampling step, or a library quietly patching $`\bar\alpha_T`$ to $`2^{-24}`$. <!-- L17 --> Use v or $`x_0`$.
- **Fixing the schedule and keeping leading spacing.** A zero-SNR model sampled from index 981 starts from pure noise labelled as a noise level it was never trained on pure noise at. Use trailing spacing. <!-- L12 -->
- **Moving a schedule to a new resolution unchanged.** At four times the side length, the same schedule leaves coarse structure 2.8 log-SNR easier to read. <!-- L28 --> Shift it, or rescale the input. <!-- L27 --> <!-- L29 -->
- **Swapping the autoencoder and keeping its scale factor.** 0.18215 belongs to one VAE. A latent with a different standard deviation moves every noise level. <!-- L06 -->
- **Reading Min-SNR's 3.4× as a promise.** It was measured against other $`x_0`$ weightings; against the standard ε-loss on the same paper's UNet the gain was 14% at 200K steps and 2% at 1M. <!-- L42 -->
- **A long EMA on a short run.** With decay 0.9999, 13.5% of the average is still the random initialisation after 20,000 steps. In the lab, that average's samples were 6.3 times further from the data than the raw weights' after 5,000 steps. Pick the half-life against the run length, or use a power-function average. <!-- L49 -->
- **Trusting the toy's magnitudes.** This post's lab is a 64-pixel MLP world, so its crossings and ratios illustrate mechanisms. The schedule numbers, the leak's closed form and its √n growth carry over directly; the size of each weighting's effect does not.

## Key takeaways

- The schedule's interior is a sampling density over noise levels. Its endpoints, the image's resolution and the data's scale are what decide which noise levels a model ever learns.
- A nonzero terminal SNR leaks the image's mean into training. The leak's strength grows with the number of values averaged: with the lab's brightness spread of 0.3, Stable Diffusion's 0.068 signal coefficient costs a 16,384-value image about two-thirds of that spread, and more sampling steps cannot recover it.
- ε, $`x_0`$ and v share a minimiser but amplify errors at different ends of the noise range. v is bounded everywhere and survives zero terminal SNR; $`x_0`$ wins when the data per token outgrows the network.
- A loss weighting allocates one network's capacity across noise levels. Its published gains are setup-specific, and spending the same budget by resampling noise levels has beaten reweighting them.
- An EMA's decay is a half-life in steps. It must match the run's length, its best value moves during training, and EDM2's post-hoc reconstruction lets you choose it after the fact.

## Try it yourself

These can be answered from the article alone. The full five-rung ladder, with the lab's own run as the answer key, is in the lab's README under [Lab downloads](#lab-downloads).

### E1 — Reproduce: the leak at 4,096 values

Using Stable Diffusion's $`\bar\alpha_T = 0.0046601`$, a brightness spread $`s_b = 0.3`$ and detail noise τ = 0.1, compute the fraction of brightness spread a perfect sampler keeps at $n$ = 4,096.

**Self-check:** within 0.001 of the 60.7% the worked example quoted.

<details><summary>Answer</summary>

$`V_0 = 4{,}096 \times 0.09 + 0.01 = 368.65`$, so $`V_T = 0.0046601 \times 368.65 + 0.99534 = 2.7133`$ and $`\rho = 1/\sqrt{2.7133} = 0.6071`$. The lab measures 0.6036 with its 50-step sampler.

</details>

### E2 — Inspect: where does ε-prediction cost a factor of ten?

From Figure 9, or the amplification table in the math section, find the log-SNR at which an ε-network's output error reaches the clean-image estimate multiplied by 10. Then find it for Stable Diffusion's last step, λ = −5.36.

**Self-check:** $`e^{-\lambda/2}`$ evaluated at your answer is 10.

<details><summary>Answer</summary>

$`e^{-\lambda/2} = 10`$ at $`\lambda = -2\ln 10 = -4.61`$. At Stable Diffusion's last step the factor is $`e^{2.68} = 14.6`$, which is $`\sqrt{1-\bar\alpha_T}/\sqrt{\bar\alpha_T} = 0.9977/0.0683`$.

</details>

### E3 — Predict: does a 0.9999 EMA beat the raw weights after 5,000 steps?

A run uses constant learning rate and an EMA with decay 0.9999, initialised from the random starting weights. Before reading the answer, predict whether sampling from the EMA after 5,000 steps beats sampling from the raw weights, and by roughly how much of the average the initialisation still holds.

**Self-check:** your weight on the initialisation is $`0.9999^{5000}`$ to two digits, and your direction matches the lab.

<details><summary>Answer</summary>

$`0.9999^{5000} = e^{-0.5} = 0.61`$: 61% of the average is still the random initialisation, so the EMA is far worse than the raw weights. In the lab's nine stable runs, the median sample distance after 5,000 steps was 0.94 for the 0.9999 average against 0.15 for the raw weights; by 40,000 steps the initialisation's share had fallen to 1.8% and the gap had narrowed to 0.25 against 0.14.

</details>

## References

### Lab downloads

- [`README.md`](LAB_01) — the lab's grade, what was executed, provenance, run order, and the E1–E5 exercise ladder.
- [`training_decisions.py`](LAB_02) — computes the schedules, measures the terminal-SNR leak with the exact denoiser, and trains the small denoisers for the weighting, target, EMA and width experiments.
- [`requirements.txt`](LAB_03) — the pinned numpy and CPU PyTorch versions.
- [`captures.json`](LAB_04) — the author's run, machine-readable, which every measured figure was drawn from.
- [`expected-output.txt`](LAB_05) — the same run as printed, to compare against your own.
- [Complete lab](https://minio.canery.in/media/lab-training-a-diffusion-model.zip) — every file above in one zip.

### Sources

**Schedules and the endpoint**

1. Ho, Jain & Abbeel. [Denoising Diffusion Probabilistic Models](https://proceedings.neurips.cc/paper/2020/hash/4c5bcfec8584af0d967f1ab10179ca4b-Abstract.html). NeurIPS 2020.
2. Nichol & Dhariwal. [Improved Denoising Diffusion Probabilistic Models](https://proceedings.mlr.press/v139/nichol21a.html). ICML 2021.
3. Rombach, Blattmann, Lorenz, Esser & Ommer. [High-Resolution Image Synthesis with Latent Diffusion Models](https://doi.org/10.1109/CVPR52688.2022.01042). CVPR 2022.
4. Song, Meng & Ermon. [Denoising Diffusion Implicit Models](https://arxiv.org/abs/2010.02502). ICLR 2021.
5. Kingma & Gao. [Understanding Diffusion Objectives as the ELBO with Simple Data Augmentation](https://proceedings.neurips.cc/paper_files/paper/2023/hash/ce79fbf9baef726645bc2337abb0ade2-Abstract-Conference.html). NeurIPS 2023.
6. Karras, Aittala, Aila & Laine. [Elucidating the Design Space of Diffusion-Based Generative Models](https://proceedings.neurips.cc/paper_files/paper/2022/hash/a98846e9d9cc01cfb87eb694d946ce6b-Abstract-Conference.html) (EDM). NeurIPS 2022.
7. Hoogeboom, Heek & Salimans. [simple diffusion: End-to-end diffusion for high resolution images](https://proceedings.mlr.press/v202/hoogeboom23a.html). ICML 2023.
8. Chen. [On the Importance of Noise Scheduling for Diffusion Models](https://arxiv.org/abs/2301.10972). Preprint, arXiv:2301.10972.
9. Esser et al. [Scaling Rectified Flow Transformers for High-Resolution Image Synthesis](https://proceedings.mlr.press/v235/esser24a.html) (SD3). ICML 2024.
10. Lin, Liu, Li & Yang. [Common Diffusion Noise Schedules and Sample Steps are Flawed](https://doi.org/10.1109/WACV57701.2024.00532). WACV 2024.
11. Everaert, Fitsios, Bocchio, Arpa, Süsstrunk & Achanta. [Exploiting the Signal-Leak Bias in Diffusion Models](https://doi.org/10.1109/WACV57701.2024.00398). WACV 2024.
12. Wu, Si, Jiang, Huang & Liu. [FreeInit: Bridging Initialization Gap in Video Diffusion Models](https://doi.org/10.1007/978-3-031-72646-0_22). ECCV 2024.
13. Podell et al. [SDXL: Improving Latent Diffusion Models for High-Resolution Image Synthesis](https://proceedings.iclr.cc/paper_files/paper/2024/hash/081b08068e4733ae3e7ad019fe8d172f-Abstract-Conference.html). ICLR 2024.

**Prediction targets**

14. Salimans & Ho. [Progressive Distillation for Fast Sampling of Diffusion Models](https://arxiv.org/abs/2202.00512). ICLR 2022.
15. Ho et al. [Imagen Video: High Definition Video Generation with Diffusion Models](https://arxiv.org/abs/2210.02303). Preprint, arXiv:2210.02303.
16. Li & He. [Back to Basics: Let Denoising Generative Models Denoise](https://openaccess.thecvf.com/content/CVPR2026/html/Li_Back_to_Basics_Let_Denoising_Generative_Models_Denoise_CVPR_2026_paper.html). CVPR 2026.

**Loss weighting**

17. Hang, Gu, Li, Bao, Chen, Hu, Geng & Guo. [Efficient Diffusion Training via Min-SNR Weighting Strategy](https://doi.org/10.1109/ICCV51070.2023.00684). ICCV 2023.
18. Choi, Lee, Shin, Kim, Kim & Yoon. [Perception Prioritized Training of Diffusion Models](https://doi.org/10.1109/CVPR52688.2022.01118). CVPR 2022.
19. Hang, Gu, Geng & Guo. [Improved Noise Schedule for Diffusion Training](https://doi.org/10.1109/ICCV51701.2025.00456). ICCV 2025.

**Weight averaging**

20. Karras, Aittala, Lehtinen, Hellsten, Aila & Laine. [Analyzing and Improving the Training Dynamics of Diffusion Models](https://doi.org/10.1109/CVPR52733.2024.02282) (EDM2). CVPR 2024.
21. Song & Ermon. [Improved Techniques for Training Score-Based Generative Models](https://proceedings.neurips.cc/paper_files/paper/2020/hash/92c3b916311a5517d9290576e3ea37ad-Abstract.html). NeurIPS 2020.
22. Dhariwal & Nichol. [Diffusion Models Beat GANs on Image Synthesis](https://proceedings.neurips.cc/paper/2021/hash/49ad23d1ec9fa4bd8d77d02681df5cfa-Abstract.html). NeurIPS 2021.
23. Morales-Brotons, Vogels & Hendrikx. [Exponential Moving Average of Weights in Deep Learning: Dynamics and Benefits](https://openreview.net/forum?id=2M9CUnYnBA). TMLR 2024.

**Scaling**

24. Peebles & Xie. [Scalable Diffusion Models with Transformers](https://doi.org/10.1109/ICCV51070.2023.00387) (DiT). ICCV 2023.
25. Hoffmann et al. [Training Compute-Optimal Large Language Models](https://doi.org/10.52202/068431-2176). NeurIPS 2022.
26. Liang, He, Yang & Dai. [Scaling Laws For Diffusion Transformers](https://proceedings.iclr.cc/paper_files/paper/2026/hash/880d8999c07a8efc9bbbeb0c38f50765-Abstract-Conference.html). ICLR 2026.
27. Mei, Tu, Delbracio, Talebi, Patel & Milanfar. [Bigger is not Always Better: Scaling Properties of Latent Diffusion Models](https://openreview.net/forum?id=0u7pWfjri5). TMLR 2024.
28. Li et al. [On the Scalability of Diffusion-based Text-to-Image Generation](https://doi.org/10.1109/CVPR52733.2024.00898). CVPR 2024.

**Survey**

29. Chang, Koulieris, Chang & Shum. [On the design fundamentals of diffusion models: A survey](https://doi.org/10.1016/j.patcog.2025.111934). Pattern Recognition, 2025.

**Configs and code** (accessed 2026-10-03)

30. CompVis. [stable-diffusion v1 inference config](https://github.com/CompVis/stable-diffusion/blob/main/configs/stable-diffusion/v1-inference.yaml).
31. Hugging Face. [diffusers schedulers](https://github.com/huggingface/diffusers/tree/v0.40.0/src/diffusers/schedulers), v0.40.0: `scheduling_ddim.py`, `scheduling_euler_discrete.py` and `scheduling_dpmsolver_multistep.py`.
