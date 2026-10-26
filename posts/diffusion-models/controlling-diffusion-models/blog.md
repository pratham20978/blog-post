---
title: "Controlling Diffusion Models: Guidance, ControlNet, LoRA"
slug: controlling-diffusion-models
date: 2026-10-18
updated: 2026-10-19
summary: "Guidance, ControlNet, LoRA, inpainting and editing steer a diffusion model from the sampler, new inputs or its weights. What each changes, and what it costs."
tags: [machine-learning, diffusion-model, generative-model, classifier-free-guidance, controlnet, lora, image-editing]
category: machine-learning
series: diffusion-models
series_position: 8
tier: L4
difficulty: advanced
prerequisites: ["Part 6 of this series", "the denoiser as an estimate of the clean image", "DDIM's update and the probability-flow ODE"]
reading_minutes: 40
cover_image: "COVER"
canonical_url: "https://canery.in/blogs/controlling-diffusion-models"
---

![Guided paths overshooting the strongest crescent beside one crescent sample that turns from faint to strong as the guidance weight grows](COVER)

> [!NOTE]
> **Insights** — A diffusion model can be made to obey something other than its prompt in three places: in the sampler's arithmetic (classifier-free guidance, inpainting by replacement, SDEdit and DDIM inversion), through new inputs wired into the frozen network by paths that start at zero (ControlNet, T2I-Adapter, IP-Adapter, inpainting and editing channels), or in the weights (LoRA, DreamBooth, textual inversion's new token). Each place has a price you can measure. Guidance cleans up samples by deleting the less typical look of a class and pushing the rest past anything real, and it over-saturates in proportion to the network's own error; a zero-initialised branch starts out changing nothing at all; fine-tuning on five photos learns the photos and rewrites the class it was taught under.

**Level:** advanced · **You need:** Part 6 of this series (Diffusion Samplers and Solvers: 1,000 Steps Into 20), the denoiser as an estimate of the clean image, what fine-tuning a network means · **Time:** ~40 min

**Jump to:** [worked example](#worked-example) · [guidance](#what-does-classifier-free-guidance-do-to-the-distribution) · [fixes](#which-fixes-keep-guidances-benefit) · [ControlNet](#how-does-controlnet-add-a-condition-without-breaking-the-model) · [LoRA](#what-do-lora-and-personalisation-change-and-what-do-they-forget) · [inpainting](#how-do-you-fill-in-part-of-an-image) · [editing](#how-do-you-edit-an-image-you-already-have) · [math](#the-math) · [implementation](#implementation)

> [!IMPORTANT]
> Numbers this post calls **measured** come from its lab: crescent world, a toy whose ideal denoisers have closed forms, at 8×8 pixels, with every network trained on one laptop CPU. A toy with few relevant directions exaggerates guidance's overshoot and shrinkage, which theory shows grow as dimension falls, so read its sizes as mechanism, not scale. <!-- L27 --> Results **quoted** from papers carry their model and dataset, and scores are compared only within one paper's table.

## Why this matters

Stable Diffusion samples at a guidance weight of 7.5 by default. <!-- L62 --> Raise it and the prompt is obeyed more closely while colours saturate; lower it and the prompt starts to matter less. <!-- L10 --> <!-- L13 --> A ControlNet trained for five days on one consumer GPU with 200,000 images makes the same model follow a depth map, and users could barely tell it from a depth model trained on an A100 cluster with more than 12 million images. <!-- L36 --> Five minutes of DreamBooth on five photos of one dog teaches the model that dog, and, unless you stop it, teaches it that every dog is that dog. <!-- L46 --> <!-- L47 --> Every control knob changes a different thing and breaks a different thing, and choosing a knob is choosing what to lose.

## The problem

Part 6 framed sampling as integrating one differential equation from noise to an image. With a noisy sample written $x = x_0 + \sigma\epsilon$, the denoiser $D(x;\sigma)$ returns the network's estimate of the clean image, $E[x_0 \mid x]$, and DDIM moves $x$ toward that estimate one noise level at a time. A text-to-image model has a denoiser $D(x;\sigma,c)$ for every prompt $c$. The question is how to make the sample also respect something else, $y$: an edge map, a particular person's face, the pixels that are already there, or an instruction such as "make it winter".

Bayes' rule says what that takes. The score of the noisy conditional splits into the score of the noisy images and the score of the condition given a noisy image:

$$
\nabla_x \log p_\sigma(x \mid y) = \nabla_x \log p_\sigma(x) + \nabla_x \log p_\sigma(y \mid x).
$$

The first term is what the model already knows. The second is new, and in denoiser form, through Tweedie's formula, it is a correction added to the denoised image: $D(x;\sigma,y) = D(x;\sigma) + \sigma^2\,\nabla_x \log p_\sigma(y \mid x)$. Every control method in this post is a way to get that correction.

It is hard to get for three reasons. At high noise, $p_\sigma(y \mid x)$ asks how likely a sketch is given an image that is almost pure noise, which no closed form answers. Training a model that takes $y$ as an input from scratch costs what training the original did. And a handful of examples, five photos of a dog, is not a distribution. The methods sort by where they put the estimate: computed at sampling time from what is at hand, learned by a new input path attached to a frozen network, or absorbed into the weights. A survey of controllable generation splits them the same way, into condition-guided score estimation and conditional score prediction that is training-free, adapter-based or tuning-based; a survey of editing sorts its 100-odd methods into training-based, test-time fine-tuning, and training- and fine-tuning-free. <!-- L01 --> <!-- L02 -->

**A convention, because papers disagree.** This post writes guidance as $D_w = D_u + w\,(D_c - D_u)$, with $D_c$ the conditional denoiser and $D_u$ the unconditional one, so $w = 1$ is plain conditional sampling. That is the convention of the guidance-interval and autoguidance papers and the scale Stable Diffusion's 7.5 refers to; the original classifier-free guidance paper writes $(1+w)$ and $-w$, so its $w$ is this post's minus one. <!-- L06 -->

The lab is crescent world from Parts 5 to 7 (Part 5 is Training a Diffusion Model: The Decisions Before Step One), with a contrast dial. Every 8×8 image shows one of four crescents, which are the classes, and each crescent comes **faint** (contrast 0.5) or **strong** (contrast 1.0), half and half, plus a random brightness and fine detail. Its unconditional and class-conditional denoisers have closed forms, so every method runs first against an exact model. Networks are then trained the way real ones are, on data, with EDM's preconditioning and noise levels and the class dropped 10% of the time, as Stable Diffusion's training dropped its text. <!-- L67 --> <!-- L70 --> Four numbers judge a set of samples of one class:

- **Faint share**, the share of samples that are faint. The data has 50%. It is the coverage of the class's less typical look.
- **Blends**, samples with a contrast between 0.685 and 0.815, which no real crescent has. They are the network's own errors.
- **Over-saturated**, samples with a contrast above 1.185, three spreads past the strong look. The data has 0.02% of them.
- **Sample distance**, Part 5's sliced Wasserstein distance between the samples and real images of the class. Two real sets of 4,096 sit 0.014 apart.

## Worked example

### Guidance on one number

Follow one number: how much of the requested crescent an image shows, along that crescent's own direction, in the same units as σ. In this one-number world the requested class sits at 3.6 (faint) and 7.2 (strong), and the other class, a crescent pointing the opposite way, at −3.6 and −7.2. Each look has a spread of 0.443. The exact denoiser is a weighted average of four Gaussians' answers,

$$
D(x;\sigma) = \sum_i \pi_i(x)\Big(m_i + \frac{s^2}{s^2+\sigma^2}(x - m_i)\Big), \qquad \pi_i(x) \propto e^{-(x-m_i)^2/2(s^2+\sigma^2)},
$$

where $m_i$ are the four looks, $s = 0.443$ their spread, and the conditional denoiser keeps only the requested class's two terms.

Start at σ = 80 with noise ε = 0.5, so $x = 40$. At that noise every look is almost equally likely, so the unconditional denoiser returns roughly the average of all four looks, 0.203, and the conditional one roughly the average of 3.6 and 7.2, 5.419. Guidance at $w = 3$ asks for

$$
D_3 = 0.203 + 3 \times (5.419 - 0.203) = 15.85 ,
$$

a crescent more than twice as strong as the strongest real one. One DDIM step to σ = 17.53, $x' = D + (17.53/80)(40 - D)$, takes the sample to 8.92 unconditionally, 13.00 conditionally and 21.14 guided.

The overshoot does not survive: once the noise is low enough for the path to decide between faint and strong, both denoisers agree on the answer and guidance has nothing left to push. What survives is the decision. Solving the exact paths for every starting noise gives the share that ends faint:

| guidance weight $w$ | 1 | 1.5 | 2 | 3 | 5 | 7.5 |
|---|---:|---:|---:|---:|---:|---:|
| faint share | 52.7% | 38.1% | 23.1% | 3.2% | 0.000002% | 0 |
| mean strong contrast at the end | 7.18 | 7.19 | 7.21 | 7.34 | 7.65 | 7.91 |

Without guidance the share is 52.7%, not 50%, and the reason is exact: the faint and strong basins meet at a starting noise of ε = 0.0675 = 5.4/80, because the sampler starts from noise centred on zero rather than on the class's mean, 5.4. With guidance the meeting point moves to ε = −0.30 at $w = 1.5$, −0.74 at 2 and −1.86 at 3, and by $w = 5$ only starting noises more than five standard deviations out still end faint. Figure 1 draws the paths.

![Fifteen paths of the requested crescent's contrast: unguided they split between faint and strong; at w = 3 all but one end strong](FIG_01)

*Figure 1. Computed, one-number world. Without guidance (left) the paths divide between the faint look at 3.6 and the strong one at 7.2. At $w = 3$ (right) every path is first pulled toward the guided target of about 15, and by the time the choice is made only the lowest of these fifteen starting noises still ends faint.*

## Intuition

Guidance is a caricature. It takes the difference between "a crescent of this class" and "an image of anything" and exaggerates it. A faint crescent looks less like its class than a strong one does, because faint crescents of every class sit closer to each other, so exaggerating class-ness turns faint ones into strong ones, and strong ones into crescents stronger than any real one. The analogy breaks in one place: a caricaturist exaggerates a face that is already chosen, while guidance acts before the choice and changes which face gets drawn. It moves samples between modes, not only within them.

The other two places work differently. A new input path computes the correction from data it was trained on, and starts out contributing nothing. A weight change moves the model's distribution itself. Figure 2 puts every method in this post in its place.

![Map of control methods in three places: the sampler's arithmetic, new inputs to a frozen network, and changed weights, each with its cost](FIG_02)

*Figure 2. Three places to add a condition. The sampler needs no training but only approximates the correction; a new input learns it while the original weights stay frozen; a weight change is cheapest at sampling time and the only one that can forget.*

## What does classifier-free guidance do to the distribution?

Guidance began with a classifier. Dhariwal & Nichol trained a classifier on noisy images and added its gradient, scaled by a factor $s$, to the diffusion model's score, which samples in proportion to $p(y \mid x)^s$, a sharper distribution than $p(y \mid x)$. <!-- L03 --> They needed $s$ above 1: at scale 1 an unconditional ImageNet model's samples were assigned about 50% probability for the intended class and still did not look like it, and raising the scale traded recall for precision. <!-- L04 --> <!-- L05 -->

**Classifier-free guidance** (CFG) removes the classifier. One network is trained for both jobs by replacing the condition with a **null token**, an empty prompt, for a fraction $p_\text{uncond}$ of training examples, a step called **label dropout**; 0.1 and 0.2 performed about equally and 0.5 worse, and 10–20% is what later models use. <!-- L06 --> <!-- L07 --> <!-- L18 --> With exact scores, the difference between the two predictions is the gradient of the implicit classifier $p(c \mid x) \propto p(x \mid c)/p(x)$, so CFG is classifier guidance without a classifier, at the price of two network calls per step. <!-- L11 --> GLIDE compared it with guidance by a CLIP model, and human raters preferred CFG for both photorealism and caption match. <!-- L12 -->

The exact model shows what guidance does when the network has nothing to fix. Figure 3 lines up ten samples from the same ten starting noises at four weights.

![Ten 8x8 crescent samples at guidance weights 1, 2, 3 and 5: faint crescents turn strong and the strong ones brighten past the data](FIG_03)

*Figure 3. Measured, exact model, the same ten starting noises in every row. Faint samples (outlined) disappear as $w$ grows, and the strong ones gain contrast; brightness, which the classes do not disagree about, does not change.*

Over 4,096 samples the faint share falls from 52.9% unguided to 24.1% at $w = 2$, 9.5% at 3 and 1.3% at 5, and the average strong crescent's contrast rises from 0.994 to 1.035 at 3 and 1.116 at 7.5, where 7.2% of samples are over-saturated. The brightness spread stays at 0.293 at every weight, because the conditional and unconditional denoisers agree exactly about brightness, and guidance only extrapolates what they disagree about. Sample distance grows from 0.024 to 0.225 at $w = 3$: with an ideal denoiser, guidance is strictly harmful. <!-- L16 -->

Networks are not ideal, and that is the only reason guidance helps. The lab's model, trained for 20,000 steps, draws 7.2–9.8% blends unguided, half-faint crescents that no real image has. Figure 4 compares it with the exact model and with a weaker copy trained a quarter as long.

![Faint share, blends and over-saturated share against guidance weight for the exact model, a trained network and a weaker network](FIG_04)

*Figure 4. Measured, mean of two seeds for the networks. Guidance removes the network's blends, the one thing it is for, and deletes faint crescents on all three models. Over-saturation grows with the network's error: the weaker copy reaches 43% at $w = 5$, the exact model 1.8%.*

At $w = 3$ guidance cuts the model's blends to 4.0–4.2% and its faint share to 13–17%, and its sample distance worsens from 0.027–0.030 to 0.19–0.21; in this toy the trade never paid off on sample distance. The weaker network shows where over-saturation comes from. Its two predictions disagree about more than the class, and guidance multiplies every disagreement: at $w = 3$ 16–20% of its samples are over-saturated against 0.4–0.5% for the model and 0.37% for the exact denoiser, and at $w = 5$ its brightness spread has grown from 0.29 to 0.34–0.39.

Theory now explains each of these. Guidance does not sample the tilted distribution $p(x)\,p(c \mid x)^w$ it is often described as: it samples increasingly from the edge of the conditional's support away from the other classes, and with any error in the score, from outside it. <!-- L23 --> For Gaussian mixtures it raises classification confidence and lowers the samples' differential entropy. <!-- L24 --> With several modes per condition it works in three stages: early guidance pulls toward the weighted mean and leaves a bias, that bias then suppresses the weaker modes, and late guidance tightens each mode. <!-- L26 --> A preprint shows that DDPM and DDIM respond differently to the same CFG, and that in the stochastic limit CFG behaves like a predictor-corrector. <!-- L25 -->

Real models have the same shape at a different size. Figure 5 charts Ho & Salimans' own tables.

![Quoted FID and Inception Score against guidance strength on ImageNet 64 and 128: FID is lowest at a little guidance, IS keeps rising](FIG_05)

*Figure 5. Quoted from Ho & Salimans, Tables 1–2, re-labelled to this post's convention (their $w$ plus one). FID falls with a little guidance and rises after it, while the Inception Score keeps climbing: a trade between fidelity and variety, not an optimum.*

On ImageNet 64 FID goes from 1.8 unguided to 1.55 at this post's $w = 1.1$, then 3.03 at 1.3 and 26.22 at 5, while the Inception Score rises from 53.71 to 260.2; on ImageNet 128 the best FID, 2.43 against 7.27 unguided, is at $w = 1.3$. <!-- L08 --> <!-- L09 --> The authors note the saturated colours of strongly guided samples, and Imagen traced them to predicted clean images that leave the range the model was trained on. <!-- L10 --> <!-- L13 -->

## Which fixes keep guidance's benefit?

The fixes split by what they remove. Imagen's **dynamic thresholding** rescales the predicted clean image whenever a chosen percentile of its pixels exceeds the valid range. <!-- L13 --> **CFG-rescale** (Lin et al.) rescales the guided prediction's standard deviation back toward the conditional prediction's, mixed in at a weight φ, with $w = 7.5$ and φ = 0.7 as its setting. <!-- L14 --> **Adaptive projected guidance** (APG) splits the update $D_c - D_u$ into a part along $D_c$, which acts as a gain and saturates, and a part orthogonal to it, and down-weights the first. <!-- L21 --> All three target saturation.

The **guidance interval** targets the mode loss. Kynkäänniemi et al. found guidance harmful at high noise, largely unnecessary at low noise and useful in between, and limiting it to an interval moved the ImageNet-512 FID record from 1.81 to 1.40 on EDM2-XXL (and 2.23 to 1.68 on EDM2-S, 3.04 to 2.40 on DiT-XL/2). <!-- L15 --> <!-- L17 --> Figure 6 asks the exact model where guidance does its damage, by switching $w = 3$ on only above, or only below, a noise level.

![Faint share with guidance only above, or only below, a noise level: the faint/strong decision happens between sigma 2 and 20](FIG_06)

*Figure 6. Measured, exact model, $w = 3$. Guidance only below σ = 2 leaves the faint share at 50–53%, as if there were none; guidance only above σ = 10 already takes it to 32.5%. The decision this toy's guidance distorts is made between σ ≈ 2 and 20.*

On the trained model none of these three helps much, and the reason is the toy's geometry. Guidance at $w = 3$ restricted to σ ≤ 2 keeps the faint share at 52–54% but leaves the blends at 7.5–8.2%, because the blends form at the same noise levels as the faint/strong decision. CFG-rescale at $w = 3$ keeps 40–43% faint and 7.6–8.3% blends, and narrows the brightness spread to 0.27–0.28. APG keeps 52–54% faint, removes almost none of the blends (6.6–8.4%) and narrows the brightness spread to 0.25–0.26: in crescent world the contrast that separates faint from strong lies along the conditional prediction itself, so removing the parallel part removes the guidance.

**Autoguidance** changes the other prediction. Karras et al. guide a model with a smaller, less-trained version of itself instead of with its unconditional mode, so the extrapolation points away from the weak model's mistakes rather than away from other classes. On ImageNet-512 it took EDM2-S from FID 2.56 unguided to 1.34, and EDM2-XXL to 1.25; the guide has to suffer the same kinds of errors as the main model, and a guide that was only trained for less time gave 1.51. <!-- L19 --> <!-- L20 --> Figure 7 places every fix in one plane.

![Blends against faint share for CFG, autoguidance, guidance intervals, CFG-rescale and APG on the trained network](FIG_07)

*Figure 7. Measured, trained model, two seeds. The ideal is the lower right: few blends, half faint. CFG moves left as it cleans up; the interval, rescale and APG stay near the start; only autoguidance moves down without moving left.*

Guided at $w = 2$ by the copy trained a quarter as long, the model's blends fell from 7.2–9.8% to 4.0–5.4% with 50–51% still faint, and its sample distance improved from 0.027–0.030 to 0.019–0.024. It was the only setting in the lab that improved the model's sample distance. Two other ideas attack different costs. CADS keeps guidance but adds decreasing noise to the condition during sampling, to restore diversity. <!-- L22 --> Guidance distillation removes guidance's doubled cost: the first of Meng et al.'s two stages trains one student, given $w$ as an input, to match the guided combination in a single call, and the second stage is the progressive distillation of Part 7 of this series, Few-Step Diffusion and Distillation: 20 Steps Into 1. <!-- L28 -->

## How does ControlNet add a condition without breaking the model?

Guidance only strengthens a condition the model was trained on. An edge map, a depth map or a pose is a new input, and the naive way to add one is to retrain: Stable Diffusion's own depth model was trained on an A100 cluster with more than 12 million images. <!-- L36 --> **ControlNet** (Zhang, Rao & Agrawala) adds it to a frozen model instead. It locks the pretrained network, makes a **trainable copy** of its encoder, feeds the condition to the copy, and joins the copy back through **zero convolutions**, 1×1 convolutions whose weight and bias both start at zero: $y_c = F(x;\Theta) + Z\big(F(x + Z(c;\Theta_{z1});\Theta_c);\Theta_{z2}\big)$. <!-- L29 --> For Stable Diffusion 1.5 the copy is the 12 encoder blocks and the middle block, whose 13 outputs are added to the U-Net's skip connections and middle block, and the 512×512 condition image is shrunk to the latent's 64×64 by four small convolutions. <!-- L31 --> Figure 8 draws the wiring, with the U-Net's skips from Part 4 of this series, Diffusion Backbones: U-Net to DiT, Block by Block.

![Stable Diffusion 1.5 with a ControlNet: frozen U-Net, a trainable copy of its encoder, and 13 zero convolutions feeding its skip connections](FIG_08)

*Figure 8. SD 1.5's U-Net (859.5M parameters, frozen) with a ControlNet (361.3M, trained). Every output of the copy enters the frozen network through a zero convolution, so at the first step the sum is the original model's.*

Counted from SD 1.5's published configuration, the ControlNet trains 361,279,120 parameters, 42.0% of the U-Net's 859,520,964; the zero convolutions are 11.5M of them and the condition encoder 1.1M. <!-- L68 --> <!-- L69 --> Because the locked half needs no gradients, a training step costs about 23% more memory and 34% more time than a step of Stable Diffusion alone, and half of the training prompts are replaced with empty strings so the copy learns to read the condition by itself. <!-- L32 --> <!-- L33 -->

The zeros are the design. At the first step both zero-convolution terms vanish, so the ControlNet's output is the locked model's exactly, and no random noise reaches the pretrained features while the copy learns. <!-- L30 --> The gradient still flows, because a zero weight's gradient is the product of the incoming features and the outgoing error, and neither is zero. The paper reports that control then arrives abruptly, usually within 10,000 steps, which it calls sudden convergence, and that Gaussian-initialised connectors left the result about as poor as its lightweight variant. <!-- L34 --> <!-- L35 -->

The lab wires the same branch onto its trained model: a copy of the first two hidden layers reads the image plus a 4×4 average-pooled layout of the target image, and enters the frozen network through zero-initialised layers. Figure 9 follows two seeds of it, and two with Gaussian connectors, through training.

![ControlNet training: zero-initialised connectors start as the frozen model and learn the layout; Gaussian ones start damaged](FIG_09)

*Figure 9. Measured, two seeds each. Zero connectors start exactly at the frozen model (top left) and learn the layout abruptly between steps 100 and 400; Gaussian connectors start with images four to five times further from the data and need about twice the steps to reach each control error.*

At step 0 the zero-initialised branch changed no output at all, to the last bit, and its control error stayed at the frozen model's 0.47 for the first 100 steps before falling to 0.10–0.12 by step 400. The Gaussian branch began with a sample distance of 0.20–0.26 against the frozen model's 0.05 and a control error of 0.54–0.58, worse than ignoring the layout, and reached 0.11–0.12 only at step 800. By step 3,200 both reached 0.066, so the toy reproduces the damaged start and the slower climb, not the lasting loss the paper reports at Stable Diffusion's scale.

Control is still not obedience. Measured by extracting the condition back out of the generated image, ControlNet's outputs often miss their conditions, and fine-tuning on that cycle consistency improved it by 11.1% mIoU on segmentation, 13.4% SSIM on line art and 7.6% RMSE on depth. <!-- L38 --> ControlNet-XS reports a 1.7M-parameter control network that matched ControlNet's 361M on its depth benchmark. <!-- L39 --> And a ControlNet added only to the conditional branch makes guidance too strong when there is no prompt, which ControlNet fixes by weighting each connection by its resolution. <!-- L37 -->

Lighter **adapters** use the same rule, a side path that starts at zero or near it, in smaller places. T2I-Adapter trains about 77M parameters whose features enter Stable Diffusion's encoder at its four scales, once per generation. <!-- L40 --> IP-Adapter, a preprint, gives each of the 16 cross-attention layers a second attention over image features, initialised from the text layer's key and value weights and added with a weight λ, where λ = 0 is the original model; about 22M parameters. <!-- L41 --> GLIGEN inserts a gated self-attention for grounding boxes, $v \leftarrow v + \beta\tanh(\gamma)\,\text{SelfAttn}(\dots)$, with γ starting at 0. <!-- L42 --> Figure 10 sets each method's trained parameters against the U-Net it steers.

![Trainable parameters per control method on SD 1.5, log scale, from 859.5 million for the full U-Net down to 768 for textual inversion](FIG_10)

*Figure 10. Computed from SD 1.5's configuration, except T2I-Adapter and IP-Adapter, which are quoted. Six orders of magnitude separate a full fine-tune from a new word, and each step down trains a narrower part of the model.*

## What do LoRA and personalisation change, and what do they forget?

The third place is the weights. **LoRA** (Hu et al.) leaves each weight matrix $W_0$ frozen and learns its change as a product of two thin matrices, $W_0 + (\alpha/r)BA$, of rank $r$; $A$ starts Gaussian and $B$ at zero, so the update starts at nothing, and the product can be merged into $W_0$ afterwards at no inference cost. <!-- L43 --> On GPT-3 it cut trainable parameters 10,000 times. <!-- L44 --> On Stable Diffusion 1.5, rank 4 on all 128 attention projections is 797,184 parameters, 0.09% of the U-Net.

Personalisation teaches a model one subject from a few images, and three recipes differ in what they let move. **Textual inversion** freezes the model and learns one new word embedding, starting from a coarse word such as "cat", over 5,000 steps. <!-- L45 --> **DreamBooth** fine-tunes the diffusion model on 3–5 photos captioned "a [V] dog", where [V] is a rare token with little prior meaning, for about 1,000 steps, five minutes on an A100. <!-- L46 --> Its authors name two failures: **language drift**, where the class noun stops meaning the class, and lost diversity. Their fix, the **prior-preservation loss**, mixes in about 1,000 of the model's own images of "a dog". <!-- L47 --> On Imagen it cut how much random dogs resembled the subject from 0.664 to 0.493, at a small cost in subject fidelity (DINO 0.712 to 0.684). <!-- L48 --> **Custom Diffusion** sits between: it fine-tunes only the cross-attention key and value projections, the weights that move most under full fine-tuning though they are about 5% of the model, in six minutes on two A100s. <!-- L50 --> On SD 1.5 those are 19,169,280 parameters, 77 MB in 32-bit floats.

The lab teaches its model one subject, a thinner version of crescent 0, from five photos, with each recipe trained for 2,000 steps on two seeds. Figure 11 shows what each one learned and what it cost.

![Subject share, drift of the plain class, other classes' sample distance and the subject's brightness spread for each personalisation method](FIG_11)

*Figure 11. Measured, after 2,000 steps, two seeds. Textual inversion learns nothing it cannot already draw; fine-tuning learns the subject and, without prior preservation, turns every plain crescent 0 into it; nothing protects the classes that were never mentioned.*

Textual inversion, 32 trainable numbers here, produced the thin crescent in 0.9–1.3% of samples: a frozen model can only be steered toward what it can already draw, which is DreamBooth's objection to it. <!-- L49 --> LoRA (6,912 parameters) and full fine-tuning (181,056) drew the subject 100% of the time and, without prior preservation, drew it for the plain prompt "crescent 0" 100% of the time too. Prior preservation took that drift to 0–0.2% for both. It did not protect the other three classes, whose sample distance rose from 0.03 for the base model to 0.09–0.37 after 2,000 steps, with or without it. In language-model fine-tuning, LoRA learned less and forgot less than full fine-tuning; here, at the same subject fidelity, it forgot no less: the other classes' sample distance ended at 0.27–0.37 under LoRA and 0.09–0.27 under full fine-tuning. <!-- L51 -->

The subject itself was learned too well. A real thin crescent varies in brightness with a spread of 0.30; the five photos of seed 1 happened to spread 0.119 and those of seed 2 0.194, and every fine-tuned model reproduced its own photos' spread (0.11–0.14 and 0.18–0.20), not the subject's. With five examples the model learns the photos. A study of LoRA-style fine-tuning on Stable Diffusion found the same direction at scale: more training raises concept fidelity while lowering diversity and the preservation of the base model. <!-- L52 -->

## How do you fill in part of an image?

**Inpainting** fills a masked region so that it agrees with the pixels that are already there. The sampler-side method needs no training: at every step, replace the known region with the known pixels noised to the current level, and let an unconditional model fill in the rest. <!-- L53 --> RePaint showed that this gives matching textures and wrong content, and added **resampling**: after each step, add noise back and redo the step, so that the two halves can negotiate; the benefit saturated at about 10 resamplings, at a large cost in time. <!-- L54 --> <!-- L55 --> DPS replaces the intractable likelihood of the known pixels given a noisy image by their likelihood given the denoiser's clean estimate, and steps along its gradient. <!-- L56 --> The twisted diffusion sampler is exact in the limit of many particles. <!-- L57 --> The trained route gives the network the mask and the masked image as extra inputs: Stable Diffusion's inpainting model adds five input channels whose weights start at zero, then trains 440,000 steps with synthetic masks. <!-- L58 -->

The lab hides the right half of 2,048 real images and fills it in. Because crescent world is Gaussian within each look, the exact posterior is known, and a completion is coherent when its right half sits within three detail spreads (RMS) of the posterior mean, that is, the same crescent at the same contrast. Figure 12 shows four completions per method and the coherence of each.

![Right-half completions of four crescents by replacement, resampling, a network with mask inputs and the exact posterior, with coherence](FIG_12)

*Figure 12. Measured, 2,048 images, left half known. Replacement completes a third of them with the wrong crescent or the wrong contrast although its denoiser is exact; resampling repairs this at ten times the calls; a network fine-tuned with zero-initialised mask inputs does it at the original cost.*

Replacement completed 64.6% of the images coherently, with the exact unconditional denoiser, so the fault is the sampler's approximation, not the model. The known half is re-noised from fresh noise at every step, so at high noise it says nothing, and the hidden half commits to a crescent before the known half can contradict it. Resampling raised coherence to 81.6% at 128 denoiser calls, 91.6% at 320 and 98.5% at 640. Fine-tuning the trained model for 4,000 steps with the mask and masked image as zero-initialised inputs gave 98.9–99.1% at 64 calls. A sampler-side method pays at every image; a trained one pays once.

## How do you edit an image you already have?

The cheapest edit is **SDEdit**: add noise to the image up to a level σ₀, then denoise under the new condition. More noise gives a result that is more realistic and less faithful to the input; its authors found $t_0$ between 0.3 and 0.6 of the way to noise worked, and human raters preferred it to GAN-based editors by up to 98.09% on realism. <!-- L59 --> <!-- L60 --> In crescent world the trade has a closed form. The new class's denoiser treats everything it cannot explain, the old crescent and the image's fine detail alike, as detail, and the path from σ₀ to the image keeps a fraction $\tau/\sqrt{\tau^2 + \sigma_0^2}$ of it, with τ = 0.1 the detail's spread: 0.196 at σ₀ = 0.5, 0.0995 at 1. Figure 13 measures that one dial.

![SDEdit's ghost of the old crescent and its kept detail fall together with starting noise; DDIM inversion keeps the detail, no ghost](FIG_13)

*Figure 13. Measured, 1,024 class-0 images edited into class 1. SDEdit's ghost of the old crescent and its kept detail fall together along the closed form; brightness drifts as σ₀ grows. DDIM inversion sits in the corner SDEdit cannot reach: no ghost, all the detail.*

At σ₀ = 0.5, 19% of the old crescent remained and the fine detail correlated 0.20 with the source; at σ₀ = 2, 4.9% remained, the detail was gone (0.06) and the brightness had drifted by 0.16. No setting of σ₀ keeps the detail without keeping the ghost, because both are the same off-class component, scaled by the same factor.

**DDIM inversion** escapes the dial. DDIM's deterministic sampler is an ODE, so it can be run backwards to find the noise that generates an image, and forwards again from that noise under a new condition. <!-- L61 --> Inverting each image with the class-0 path and regenerating with class 1 left 0.1% of the old crescent, kept the brightness within 0.002 and the fine detail at a correlation of 1.00; regenerating with class 0 reproduced the source to 0.003 RMS. The noise carries everything the condition does not. It carries it only along the unguided path, though: regenerated from the same noise with guidance at $w = 1.5$, 2 and 3, the reconstruction missed by 0.13, 0.20 and 0.28. Null-text inversion exists for exactly this: Stable Diffusion edits need guidance, so it inverts at $w = 1$ and then optimises the empty prompt's embedding at every step until the guided path reconstructs the image. <!-- L62 --> Prompt-to-Prompt keeps the layout of a generated image under a changed prompt by reusing the original's cross-attention maps for some of the steps. <!-- L63 -->

**InstructPix2Pix** trains the edit in. GPT-3, fine-tuned on 700 human-written examples, wrote 454,445 instructions with before and after captions, and Stable Diffusion with Prompt-to-Prompt turned each caption pair into image pairs, filtered for consistency; Figure 14 is the paper's own diagram of that pipeline. <!-- L64 -->

![InstructPix2Pix's pipeline: GPT-3 writes edits, Stable Diffusion with Prompt-to-Prompt renders image pairs, a diffusion model learns to edit](FIG_14)

*Figure 14. Reproduced unchanged from Brooks, Holynski & Efros, InstructPix2Pix: Learning to Follow Image Editing Instructions, CVPR 2023, Figure 2 ([arXiv:2211.09800](https://arxiv.org/abs/2211.09800)), licensed CC BY 4.0. The training data is manufactured by two models before the editor is trained.*

The editor starts from Stable Diffusion with extra input channels for the input image, their weights at zero, and trained for 10,000 steps on eight A100s in 25.5 hours. <!-- L65 --> It drops the image, the instruction or both 5% of the time each, so it can sample with two guidance weights: $s_I$ for staying close to the input image and $s_T$ for following the instruction; with $s_T = 7.5$, raising $s_I$ from 1.0 to 2.2 trades the edit's strength for consistency with the input. <!-- L66 -->

## The math

| Symbol | Meaning |
|---|---|
| $x$, σ | a noisy sample and its noise level, $x = x_0 + \sigma\epsilon$ |
| $D(x;\sigma)$, $D(x;\sigma,c)$ | the unconditional and conditional denoisers, $E[x_0 \mid x]$ and $E[x_0 \mid x, c]$ |
| $D_w$ | the guided denoised image at weight $w$ |
| $y$ | a new condition: a layout, known pixels, a subject |
| $W_0$, $A$, $B$, $r$ | a frozen weight, LoRA's two factors and its rank |
| τ, σ₀ | the detail's spread; SDEdit's starting noise level |

**Every condition is one extra term.** Tweedie's formula ties the denoiser to the score, $\nabla_x \log p_\sigma(x) = (D(x;\sigma) - x)/\sigma^2$, so Bayes' rule for the conditional reads, in denoiser form,

$$
D(x;\sigma,y) = D(x;\sigma) + \sigma^2\,\nabla_x \log p_\sigma(y \mid x).
$$

The correction is the condition's noisy likelihood, scaled by σ². At large σ the image says little about $y$, so the gradient is small but multiplied by a large σ², which is why errors made early decide so much.

**Guidance as a tilt, and why the tilt is not sampled.** With exact denoisers, $D_c - D_u = \sigma^2 \nabla_x \log p_\sigma(c \mid x)$, so

$$
D_w = D_u + w\,(D_c - D_u) = D(x;\sigma) + w\,\sigma^2\,\nabla_x \log p_\sigma(c \mid x),
$$

which is the denoiser of the tilted density $p_\sigma(x)\,p_\sigma(c \mid x)^w$ at each noise level. The tilted densities at different σ are not noisy versions of one distribution, so the sampler that follows them does not end at $p(x)\,p(c \mid x)^w$. <!-- L23 --> <!-- L25 --> The tilt still predicts the direction of every effect in the lab: a faint crescent has a lower $p(c \mid x)$ than a strong one, because faint crescents of all classes sit close together, so raising it to a power $w$ shrinks faint mass and moves strong mass outward.

**Why a zero weight still learns.** For a zero-initialised layer $z = W h + b$ added to a frozen network's activations, $\partial \mathcal{L}/\partial W = (\partial \mathcal{L}/\partial z)\,h^{\top}$. At the first step $W = 0$ makes $z = 0$, so the network's output is unchanged, but $h$, the copy's features, and $\partial \mathcal{L}/\partial z$, the loss gradient at the frozen network's activations, are both non-zero, so the first update already moves $W$. LoRA's $B = 0$ is the same trick with a factored matrix.

**LoRA's count.** A $d \times k$ weight has $dk$ parameters; its rank-$r$ update has $r(d + k)$. For a 320 × 320 attention projection in SD 1.5's first stage that is 102,400 against 2,560 at $r = 4$, and summed over the U-Net's 128 attention projections, 797,184.

<details>
<summary>SDEdit's dial, derived</summary>

Take any direction the target class's denoiser cannot explain: the old crescent's part that the new crescent lacks, or a direction of fine detail. Along it the target class's data is Gaussian with spread τ, and its exact denoiser is the linear shrink $D = \tau^2 x/(\tau^2 + \sigma^2)$. The probability-flow ODE $dx/d\sigma = (x - D)/\sigma$ then has the solution $x(\sigma) = x(\sigma_0)\sqrt{\tau^2+\sigma^2}/\sqrt{\tau^2+\sigma_0^2}$, so the path from σ₀ to the image multiplies that coordinate by

$$
\frac{\tau}{\sqrt{\tau^2 + \sigma_0^2}} .
$$

SDEdit starts from $x(\sigma_0) = u + \sigma_0\epsilon$, where $u$ is the source's value. The ghost of the old crescent is therefore its old amplitude times this factor, and the kept detail correlates with the source's at exactly this factor, because $\operatorname{corr}(u, u + \sigma_0\epsilon) = \tau/\sqrt{\tau^2+\sigma_0^2}$ for detail of spread τ. At σ₀ = 0.5 both are 0.196; the lab measured 0.194 for the ghost and 0.202 for the detail.

</details>

## Implementation

The guidance variants differ only in the line that forms the denoised image. Over any denoiser `D(x, s, c)` with an empty prompt `NULL` and a weaker copy `D_weak`, one DDIM step is:

```python
import torch

def guided(D, x, s, c, w, mode="cfg", D_weak=None, lo=0.0, hi=float("inf"), phi=0.7):
    """The denoised image one guided DDIM step moves toward (this post's convention: w = 1 is unguided)."""
    dc = D(x, s, c)
    if w == 1 or not (lo < s <= hi):          # the guidance interval: outside it, plain conditional
        return dc
    du = D_weak(x, s, c) if mode == "auto" else D(x, s, NULL)   # autoguidance swaps the unconditional
    if mode == "apg":                          # keep only the part of the update orthogonal to dc
        diff = dc - du
        par = (diff * dc).sum(1, keepdim=True) / (dc * dc).sum(1, keepdim=True) * dc
        return dc + (w - 1) * (diff - par)
    d = du + w * (dc - du)
    if mode == "rescale":                      # Lin et al.: pull the spread back toward the conditional's
        d = phi * d * dc.std(1, keepdim=True) / d.std(1, keepdim=True) + (1 - phi) * d
    return d

def ddim_step(x, s, s_next, d):
    return d + (s_next / s) * (x - d)
```

A new input path and a LoRA layer are both additions that start at zero:

```python
import torch.nn as nn

class ZeroLinear(nn.Linear):
    """ControlNet's zero convolution, as a linear layer: the branch adds nothing until it has learned."""
    def __init__(self, n_in, n_out):
        super().__init__(n_in, n_out)
        nn.init.zeros_(self.weight); nn.init.zeros_(self.bias)

class LoRA(nn.Module):
    """W0 x + (alpha / r) B A x, with B = 0 so the layer starts as W0."""
    def __init__(self, lin, r=4, alpha=4.0):
        super().__init__()
        self.lin, self.scale = lin, alpha / r
        self.A = nn.Parameter(torch.randn(r, lin.in_features) / lin.in_features ** 0.5)
        self.B = nn.Parameter(torch.zeros(lin.out_features, r))
    def forward(self, x):
        return self.lin(x) + self.scale * (x @ self.A.T) @ self.B.T
```

Inpainting by replacement is one line inside the sampling loop, `x[:, known] = y + s * torch.randn_like(y)`, run before every denoiser call; RePaint's resampling repeats a step after adding back noise of variance $\sigma^2 - \sigma'^2$. The lab's `control.py` implements all of it against crescent world's exact denoisers and its trained networks, with every number and figure in this post; it is under [Lab downloads](#lab-downloads).

## Limitations and common mistakes

> [!WARNING]
> **Common mistake: turning up guidance to fix a model that is not good enough.** Guidance multiplies whatever the conditional and unconditional predictions disagree about, so an under-trained or badly fine-tuned model over-saturates first: in the lab, a network trained a quarter as long over-saturated 16–20% of its samples at $w = 3$, against 0.4–0.5% for the better one. If high guidance burns colours, check the model before the scale, and try a guide with the model's own errors (autoguidance) before more of the unconditional one.

- **Reading guidance weights across codebases.** The original CFG paper's $w$ is this post's and diffusers' minus one; a "w = 0.3" there is 1.3 here. <!-- L06 --> Compare scales only within one convention.
- **Assuming the guidance interval or APG will fix diversity everywhere.** They remove guidance where it harms; in a world where the blends a model makes and the mode it drops are decided at the same noise levels, as in this toy, they remove the benefit with the harm. Measure coverage and fidelity separately before choosing.
- **Trusting prior preservation to protect the whole model.** It protects the class it names. In the lab the three unnamed classes degraded with or without it; regularise with images of what you need to keep, as Custom Diffusion does with real images. <!-- L50 -->
- **Inpainting by replacement with a good model and expecting coherent results.** With an exact denoiser it still completed a third of the images with the wrong crescent or contrast; budget for resampling or train mask inputs.
- **Editing real images with guidance from a plain DDIM inversion.** The inverted noise reconstructs the image only along the unguided path; under guidance it drifts, which is what null-text inversion corrects. <!-- L62 -->
- **Reading the toy as typical.** Crescent world has four isolated classes, two looks per class and a few relevant directions, and its networks are tiny; real models drop modes partially, and in high enough dimension guidance's overshoot and shrinkage fade. <!-- L27 --> The toy's sizes are mechanism; the papers' numbers are scale.

## Key takeaways

- Every control method estimates one term, the condition's noisy likelihood, in one of three places: the sampler, a new input path or the weights; the place decides the price.
- Classifier-free guidance cleans a network's errors by extrapolating away from its unconditional prediction, which also deletes a class's less typical look and over-saturates in proportion to the network's own error; with an ideal model it is pure cost.
- Autoguidance, guiding with a weaker copy of the same model, kept coverage and cut errors where guidance intervals, CFG-rescale and APG mostly removed guidance itself.
- New inputs attach safely when their path starts at zero: ControlNet, adapters, and the inpainting and editing channels all leave the pretrained model's outputs untouched at step zero.
- Fine-tuning on a few images learns those images and rewrites the class it was taught under; prior preservation protects only that class, and nothing protects the rest without data that covers it.

## Try it yourself

These can be answered from the article alone. The full exercise ladder, with the lab's own run as the answer key, is in the lab's README under [Lab downloads](#lab-downloads).

### E1 — Reproduce: the guided denoiser at x = 40

In the one-number world (looks at ±3.6 and ±7.2, spread 0.443), compute the unconditional and the conditional denoiser at $x = 40$, σ = 80, approximately, by treating every look as equally likely; then the guided value at $w = 3$ and one DDIM step to σ = 17.53.

**Self-check:** your guided value is within 0.5 of the lab's 15.85 and your guided step within 0.5 of its 21.14; equal weights put you about 0.35 high.

<details><summary>Answer</summary>

With equal weights the unconditional answer is the average of the four looks, 0, and the conditional one the average of 3.6 and 7.2, 5.4 (the shrink toward $x$ adds 0.001 at this noise). So $D_3 \approx 0 + 3 \times 5.4 = 16.2$, and the step is $16.2 + (17.53/80)(40 - 16.2) = 21.4$. The exact weights tilt slightly toward the looks nearer $x = 40$, which is why the lab prints 0.203 and 5.419, a guided value of 15.849 and a step to 21.140.

</details>

### E3 — Predict: SDEdit at σ₀ = 1

Before looking at Figure 13, predict how much of the old crescent survives SDEdit from σ₀ = 1, and the correlation of the kept detail with the source's, using the detail spread τ = 0.1.

**Self-check:** both predictions within 0.01 of the lab's, for the reason that both are the same off-class coordinate scaled by one factor.

<details><summary>Answer</summary>

Both are $\tau/\sqrt{\tau^2 + \sigma_0^2} = 0.1/\sqrt{1.01} = 0.0995$. The lab measured a ghost of 0.098 and a detail correlation of 0.106: the target class's denoiser shrinks everything it cannot explain at the same rate, so a smaller σ₀ keeps more detail only by keeping more of the old crescent.

</details>

## References

### Lab downloads

- [`README.md`](LAB_01) — the lab's grade, what was executed, provenance, run order, and the E1–E5 exercise ladder.
- [`control.py`](LAB_02) — crescent world's exact denoisers, the trained networks, every control method and every experiment in this post.
- [`requirements.txt`](LAB_03) — the pinned numpy and CPU PyTorch versions, and the optional diffusers for the census.
- [`captures.json`](LAB_04) — the author's run, machine-readable, which every measured figure was drawn from.
- [`expected-output.txt`](LAB_05) — the same run as printed, to compare against your own.
- [`notebook.ipynb`](LAB_06) — the README with a runnable cell under each step and exercise.
- [Complete lab](https://minio.canery.in/media/lab-controlling-diffusion-models.zip) — every file above in one zip.

### Sources

**Surveys**

1. Cao, Zhou, Song & Yang. [Controllable Generation with Text-to-Image Diffusion Models: A Survey](https://doi.org/10.1109/TPAMI.2025.3646548). IEEE TPAMI, 2025.
2. Huang et al. [Diffusion Model-Based Image Editing: A Survey](https://doi.org/10.1109/TPAMI.2025.3541625). IEEE TPAMI, 2025.

**Guidance**

3. Dhariwal & Nichol. [Diffusion Models Beat GANs on Image Synthesis](https://arxiv.org/abs/2105.05233). NeurIPS 2021.
4. Ho & Salimans. [Classifier-Free Diffusion Guidance](https://arxiv.org/abs/2207.12598). arXiv preprint, 2022; a short version appeared at a NeurIPS 2021 workshop.
5. Nichol et al. [GLIDE: Towards Photorealistic Image Generation and Editing with Text-Guided Diffusion Models](https://proceedings.mlr.press/v162/nichol22a.html). ICML 2022.
6. Saharia et al. [Photorealistic Text-to-Image Diffusion Models with Deep Language Understanding](https://doi.org/10.52202/068431-2643) (Imagen). NeurIPS 2022.
7. Lin, Liu, Li & Yang. [Common Diffusion Noise Schedules and Sample Steps are Flawed](https://doi.org/10.1109/WACV57701.2024.00532). WACV 2024.
8. Kynkäänniemi, Aittala, Karras, Laine, Aila & Lehtinen. [Applying Guidance in a Limited Interval Improves Sample and Distribution Quality in Diffusion Models](https://doi.org/10.52202/079017-3892). NeurIPS 2024.
9. Karras, Aittala, Kynkäänniemi, Lehtinen, Aila & Laine. [Guiding a Diffusion Model with a Bad Version of Itself](https://doi.org/10.52202/079017-1679). NeurIPS 2024.
10. Sadat, Hilliges & Weber. [Eliminating Oversaturation and Artifacts of High Guidance Scales in Diffusion Models](https://proceedings.iclr.cc/paper_files/paper/2025/hash/d1450d6c10c6b6cf1b80964357f5fa08-Abstract-Conference.html) (APG). ICLR 2025.
11. Sadat, Buhmann, Bradley, Hilliges & Weber. [CADS: Unleashing the Diversity of Diffusion Models through Condition-Annealed Sampling](https://proceedings.iclr.cc/paper_files/paper/2024/hash/6769bfdeb7313ded45714aabf759adfe-Abstract-Conference.html). ICLR 2024.
12. Chidambaram, Gatmiry, Chen, Lee & Lu. [What does guidance do? A fine-grained analysis in a simple setting](https://arxiv.org/abs/2409.13074). NeurIPS 2024.
13. Wu, Chen, Li, Wang & Wei. [Theoretical Insights for Diffusion Guidance: A Case Study for Gaussian Mixture Models](https://arxiv.org/abs/2403.01639). ICML 2024.
14. Bradley & Nakkiran. [Classifier-Free Guidance is a Predictor-Corrector](https://arxiv.org/abs/2408.09000). arXiv preprint, 2024.
15. Jin, Shi & Gu. [Stage-wise Dynamics of Classifier-Free Guidance in Diffusion Models](https://proceedings.iclr.cc/paper_files/paper/2026/hash/f9e2800a251fa9107a008104f47c45d1-Abstract-Conference.html). ICLR 2026.
16. Lehman Pavasovic, Verbeek, Biroli & Mezard. [Overshoot and Shrinkage in Classifier-Free Guidance: From Theory to Practice](https://proceedings.iclr.cc/paper_files/paper/2026/hash/d7168ad82b4780797ffa8202c531ef6a-Abstract-Conference.html). ICLR 2026.
17. Meng, Rombach, Gao, Kingma, Ermon, Ho & Salimans. [On Distillation of Guided Diffusion Models](https://doi.org/10.1109/CVPR52729.2023.01374). CVPR 2023.

**New inputs**

18. Zhang, Rao & Agrawala. [Adding Conditional Control to Text-to-Image Diffusion Models](https://doi.org/10.1109/ICCV51070.2023.00355) (ControlNet). ICCV 2023.
19. Li, Yang, Kuang, Wu, Wang, Xiao & Chen. [ControlNet++: Improving Conditional Controls with Efficient Consistency Feedback](https://doi.org/10.1007/978-3-031-72667-5_8). ECCV 2024.
20. Zavadski, Feiden & Rother. [ControlNet-XS: Rethinking the Control of Text-to-Image Diffusion Models as Feedback-Control Systems](https://doi.org/10.1007/978-3-031-73223-2_20). ECCV 2024.
21. Mou et al. [T2I-Adapter: Learning Adapters to Dig Out More Controllable Ability for Text-to-Image Diffusion Models](https://doi.org/10.1609/aaai.v38i5.28226). AAAI 2024.
22. Ye, Zhang, Liu, Han & Yang. [IP-Adapter: Text Compatible Image Prompt Adapter for Text-to-Image Diffusion Models](https://arxiv.org/abs/2308.06721). arXiv preprint, 2023.
23. Li et al. [GLIGEN: Open-Set Grounded Text-to-Image Generation](https://doi.org/10.1109/CVPR52729.2023.02156). CVPR 2023.

**New weights**

24. Hu et al. [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685). ICLR 2022.
25. Gal et al. [An Image is Worth One Word: Personalizing Text-to-Image Generation using Textual Inversion](https://arxiv.org/abs/2208.01618). ICLR 2023.
26. Ruiz, Li, Jampani, Pritch, Rubinstein & Aberman. [DreamBooth: Fine Tuning Text-to-Image Diffusion Models for Subject-Driven Generation](https://doi.org/10.1109/CVPR52729.2023.02155). CVPR 2023.
27. Kumari, Zhang, Zhang, Shechtman & Zhu. [Multi-Concept Customization of Text-to-Image Diffusion](https://doi.org/10.1109/CVPR52729.2023.00192) (Custom Diffusion). CVPR 2023.
28. Biderman et al. [LoRA Learns Less and Forgets Less](https://arxiv.org/abs/2405.09673). TMLR 2024.
29. Yeh et al. [Navigating Text-To-Image Customization: From LyCORIS Fine-Tuning to Model Evaluation](https://proceedings.iclr.cc/paper_files/paper/2024/hash/727658ad24ba28e02dffd379bdc69448-Abstract-Conference.html). ICLR 2024.

**Inpainting and editing**

30. Song, Sohl-Dickstein, Kingma, Kumar, Ermon & Poole. [Score-Based Generative Modeling through Stochastic Differential Equations](https://arxiv.org/abs/2011.13456). ICLR 2021.
31. Lugmayr, Danelljan, Romero, Yu, Timofte & Van Gool. [RePaint: Inpainting using Denoising Diffusion Probabilistic Models](https://doi.org/10.1109/CVPR52688.2022.01117). CVPR 2022.
32. Chung, Kim, McCann, Klasky & Ye. [Diffusion Posterior Sampling for General Noisy Inverse Problems](https://arxiv.org/abs/2209.14687). ICLR 2023.
33. Wu, Trippe, Naesseth, Blei & Cunningham. [Practical and Asymptotically Exact Conditional Sampling in Diffusion Models](https://doi.org/10.52202/075280-1363). NeurIPS 2023.
34. Meng et al. [SDEdit: Guided Image Synthesis and Editing with Stochastic Differential Equations](https://arxiv.org/abs/2108.01073). ICLR 2022.
35. Song, Meng & Ermon. [Denoising Diffusion Implicit Models](https://arxiv.org/abs/2010.02502). ICLR 2021.
36. Hertz et al. [Prompt-to-Prompt Image Editing with Cross Attention Control](https://arxiv.org/abs/2208.01626). ICLR 2023.
37. Mokady, Hertz, Aberman, Pritch & Cohen-Or. [Null-text Inversion for Editing Real Images using Guided Diffusion Models](https://doi.org/10.1109/CVPR52729.2023.00585). CVPR 2023.
38. Brooks, Holynski & Efros. [InstructPix2Pix: Learning to Follow Image Editing Instructions](https://doi.org/10.1109/CVPR52729.2023.01764). CVPR 2023.

**Models, code and method** (pages accessed 2026-10-18)

39. Karras, Aittala, Aila & Laine. [Elucidating the Design Space of Diffusion-Based Generative Models](https://proceedings.neurips.cc/paper_files/paper/2022/hash/a98846e9d9cc01cfb87eb694d946ce6b-Abstract-Conference.html) (EDM). NeurIPS 2022.
40. [Stable Diffusion v1.5 inpainting model card](https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-inpainting), Hugging Face.
41. [Stable Diffusion v1.5 U-Net configuration](https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/blob/main/unet/config.json), Hugging Face.
42. [diffusers v0.40.0, ControlNet models](https://github.com/huggingface/diffusers/tree/v0.40.0/src/diffusers/models/controlnets), GitHub.
