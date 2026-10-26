---
title: "Few-Step Diffusion and Distillation: 20 Steps Into 1"
slug: few-step-diffusion-distillation
date: 2026-10-16
updated: 2026-10-16
summary: "Few-step diffusion trains a student to jump along the sampling path. Progressive distillation, consistency models, DMD and flow maps: what one step costs."
tags: [machine-learning, diffusion-model, generative-model, knowledge-distillation, consistency-model, deep-learning]
category: machine-learning
series: diffusion-models
series_position: 7
tier: L3
difficulty: advanced
prerequisites: ["Part 6 of this series", "the denoiser as an estimate of the clean image", "the probability-flow ODE and DDIM's update"]
reading_minutes: 30
cover_image: "COVER"
canonical_url: "https://canery.in/blogs/few-step-diffusion-distillation"
---

![The exact endpoint of the path as a step against a student's ramp, beside crescent samples from the exact path, DDIM and a student](COVER)

> [!NOTE]
> **Insights** — Few-step diffusion trains a second network, the student, to jump along the path a diffusion sampler would walk, so one network call can do the work of twenty. Progressive distillation, consistency models, shortcut models and flow maps all learn pieces of that jump, and they break in the same place: where starting noises a hair apart end on different images, a smooth student lands between them. Distribution matching (DMD, DMD2, ADD) stops following the path and matches only the set of images, which lifts that limit and brings another, dropped modes. The two failures move different numbers, fidelity and coverage, so judging a few-step model by FID alone hides one of them.

**Level:** advanced · **You need:** Part 6 of this series (Diffusion Samplers and Solvers: 1,000 Steps Into 20), the denoiser as an estimate of the clean image, what training a network against a target means · **Time:** ~30 min

**Jump to:** [worked example](#worked-example) · [progressive distillation](#how-does-progressive-distillation-halve-the-steps) · [consistency models](#what-does-a-consistency-model-learn) · [distribution matching](#what-happens-when-the-student-stops-following-the-path) · [any step count](#can-one-network-take-any-number-of-steps) · [which metric](#which-metric-shows-the-damage) · [math](#the-math) · [implementation](#implementation)

> [!IMPORTANT]
> Numbers this post calls **measured** come from its lab: crescent world, a toy whose ideal denoiser and exact sampling path have closed forms, at 8×8 pixels, with every student network trained on one laptop CPU. Their sizes are a toy's; which method fails where, and in which metric, is the mechanism. Results **quoted** from papers carry their model and dataset, and scores are compared only within one paper's table.

## Why this matters

SDXL-Turbo makes a 512×512 image in a single network call, and FLUX.1-schnell, a 12-billion-parameter model, in one to four. <!-- L52 --> <!-- L53 --> Neither got there with a better sampler. Part 6 of this series, Diffusion Samplers and Solvers: 1,000 Steps Into 20, took a trained model from 1,000 calls to 10–30 without retraining, and found that below about ten calls a solver's order stops helping. Both models were made by training a second network on the first, and SDXL-Turbo's own model card lists what that cost: imperfect photorealism, no legible text, unreliable faces. <!-- L52 --> Once a product needs interactive generation, the step count is a training decision, and the training decides what you lose.

## The problem

Part 6 framed sampling as solving one differential equation. With a noisy sample written $x = x_0 + \sigma\epsilon$ and the denoiser $D(x;\sigma)$ returning the network's estimate of the clean image, the probability-flow ODE is $dx/d\sigma = (x - D(x;\sigma))/\sigma$. A sampler integrates it from large σ down to 0; DDIM spends one denoiser call per step, and cost is counted in network calls.

Why can't a sampler take one step? Because a single step can use only what the denoiser says at the start, and at σ = 80 it says almost nothing about the image. The denoiser returns the average of every clean image consistent with its input, which Part 1 of this series, What a Diffusion Model Actually Does, called the averaging argument; from pure noise that average is the dataset's mean, a blur of everything. One DDIM step from σ = 80 to 0 returns exactly that blur. In this post's lab, all of 4,096 one-call DDIM samples are blends of crescents rather than crescents, with the exact denoiser; at two calls, 76% still are.

A few-step method must therefore learn something the diffusion model never stored: where each path ends. Write $\Phi(x;\sigma\to\sigma')$ for the point that the exact path through $x$ at noise level σ reaches at level σ′. This solution operator of the ODE is the **flow map**. <!-- L44 --> The denoiser fixes its slope where σ′ meets σ; a sampler rebuilds the jump from that slope at run time, a few calls per jump; a few-step method trains a network to output the jump itself. Training one network to reproduce what a slower procedure produces is **knowledge distillation**: the slow procedure is the **teacher**, the new network the **student**. A survey of the field files distillation among the learning-based ways to sample faster, beside the learning-free solvers of Part 6. <!-- L01 -->

A student can be judged two ways, and this post keeps them apart because they disagree:

- **Pairing.** Give the student the teacher's starting noise and compare where the two land. The lab reports the **flip rate**, the share of noises for which the student draws a different crescent than the exact path does, and the distance between the two images.
- **The set.** Ignore pairing and ask whether the samples, as a collection, look like the data. The lab uses the sliced Wasserstein distance of Part 5 of this series, Training a Diffusion Model: The Decisions Before Step One, called **sample distance** here; two independent sets of 4,096 real samples sit 0.034 apart, the floor. It also counts **blends**, samples whose shape lies more than a tenth of the way from one crescent toward another, which no real sample does.

The lab is crescent world from Parts 5 and 6, at 8×8 pixels: images of one of four bright crescents, with a random overall brightness and fine per-pixel detail. Its ideal denoiser has a closed form, so the exact path from any noise is solved to ten decimal places, and every error is the student's. Each student is a small network trained on the CPU, warm-started from a network trained to imitate the exact denoiser, the way real distillation starts from a pretrained diffusion model. That copy is close but not exact: its own 128-call sampler draws a different crescent than the exact path for 1.8% of noises.

## Worked example

### One number between two crescents

Keep two of crescent world's four crescents, the two that point in opposite directions, and follow one number: the position along the line from one to the other, measured from their midpoint. On that line the clean data sits in two tight clusters, at −5.18 and +5.18, each with spread 0.1 from the fine detail. The exact denoiser along the line is a closed form:

$$
D(x;\sigma) = \frac{0.01\,x + 5.18\,\sigma^2 \tanh\!\big(5.18\,x/(0.01+\sigma^2)\big)}{0.01+\sigma^2}
$$

It averages the two clusters, weighted by how likely each is to have produced $x$, and shrinks toward $x$ by the detail noise. Start at σ = 80 with noise ε = 0.5, so $x = 40$. The tanh's argument is 5.18 × 40 / 6,400 = 0.0324, so $D(40; 80) = 5.18 × 0.0324 = 0.168$. One DDIM step to σ = 0 returns exactly that: a point 3% of the way from the midpoint to a crescent.

The table follows two starting noises through DDIM with more calls, on EDM's ρ = 7 spacing of noise levels between 80 and 0.002, which the lab uses everywhere (80, 17.53, 2.515 and 0.170 for four steps): <!-- L55 -->

| starting noise ε | $x$ at σ = 80 | DDIM, 1 call | 2 calls | 4 calls | exact path |
|---:|---:|---:|---:|---:|---:|
| 0.5 | 40 | 0.168 | 4.249 | 5.021 | 5.149 |
| 0.02 | 1.6 | 0.0067 | 0.240 | 3.925 | 4.964 |

From ε = 0.5 two calls land near the crescent at +5.18. From ε = 0.02 they land at 0.240, almost on the midpoint: a blend. The exact path takes both noises all the way to the crescent.

### Four steps into two, by hand

Progressive distillation, the first method below, trains a student whose one step does the work of two teacher steps. Let the teacher be DDIM on four steps (80 → 17.53 → 2.515 → 0.170 → 0) and the student take two (80 → 2.515 → 0). From $x = 40$ the teacher's two steps are:

1. $D(40; 80) = 0.168$, so $x' = 0.168 + (17.53/80)(40 - 0.168) = 8.895$.
2. $D(8.895; 17.53) = 0.771$, so $x'' = 0.771 + (2.515/17.53)(8.895 - 0.771) = 1.937$.

The student's single DDIM step from 40 lands at $\tilde D + (2.515/80)(40 - \tilde D)$, and it must land at 1.937, so the student has to output $\tilde D = (1.937 - 0.03144 \times 40)/(1 - 0.03144) = 0.701$. Where the true denoiser says 0.168, the student is trained to say 0.701, four times further toward the crescent. A distilled student is not a better denoiser. It is told where the path goes next, so it commits sooner. Repeated at the second step, the two-step student lands where four teacher steps land, 5.021, against 4.249 for DDIM's own two calls.

### The cliff

Now let ε approach zero. ε = +0.001 ends at +4.863 and ε = −0.001 at −4.863: starting noises 0.002 apart end on opposite crescents. The exact map from noise to image is a step at ε = 0, which Figure 1 draws. A one-call student must reproduce that step with a smooth function. Fitted by least squares to 200,000 exact pairs, a network with two hidden layers of 64 units ramps across ε from −0.010 to +0.015, and 1.0% of all starting noises land closer to the midpoint than to either crescent.

![Endpoint against starting noise between two crescents: the exact map jumps at zero, DDIM and a fitted network make ramps across it](FIG_01)

*Figure 1. Computed along the line between two opposite crescents. The exact endpoint jumps from −4.863 to +4.863 at ε = 0; one DDIM call returns the near-flat blur, two calls a wide ramp, and even a network fitted to the exact endpoints keeps a ramp 0.025 wide.*

The ramp is the whole difficulty of one-step generation, compressed into one number. In 64 dimensions the step becomes a boundary surface between the regions of noise that end on each crescent, and every method below either learns to approximate it, or, in the case of distribution matching, stops asking where any particular noise should end.

## Intuition

Part 6 pictured a sampler navigating by compass: each denoiser call says which way the image is heading, and the sampler walks. A distilled student replaces the compass with an atlas: look up the start, read off the destination. The atlas is easy to draw where neighbouring starts end at neighbouring images, and impossible to draw exactly on a watershed, where two starts a hair apart drain into different valleys; a smooth atlas strands some travellers on the ridge. The analogy breaks for distribution matching, which throws the atlas away and promises only that each valley gets its share of travellers, not which traveller goes where. Nothing in that promise says every valley gets anyone.

Figure 2 sorts the methods in this post by where each one's training target comes from.

![Method family tree: path-followers take targets from teacher steps or their own jumps; distribution matchers from scores and real images](FIG_02)

*Figure 2. Every method that follows the path gets its targets from the teacher's ODE or from its own earlier jumps; distribution matching takes only scores and real images, and no target says where a particular noise should end.*

## How does progressive distillation halve the steps?

Progressive distillation (Salimans & Ho, ICLR 2022) is the worked example's halving, repeated. The student starts as a copy of the teacher; its target makes one student DDIM step land where two teacher DDIM steps land; once trained, the student becomes the next round's teacher and the step count halves again. <!-- L07 --> Training inputs are noised training images, not points on the teacher's paths, so each update costs about what an ordinary diffusion update costs. <!-- L09 --> The paper started CIFAR-10 at 8,192 steps and its larger datasets at 1,024, trained 50,000 updates per round (100,000 for the last two), and reached four steps for no more compute than training the original model. <!-- L11 -->

Why give the student its own target rather than the denoiser's? The paper's answer is the worked example's: the distillation target is fully determined by the noisy input and the teacher, so the student can be sharp, while the denoising target averages over every clean image the input could have come from. <!-- L08 --> The method also forced a change of parameterization. A network that predicts the noise recovers the image by subtracting σ times its prediction, which multiplies any error by σ, and a one-step student works at the largest σ there is, where the input carries no signal at all. Part 5 met the same problem as ε-prediction failing at zero signal-to-noise ratio. Predicting the image, the velocity v, or both stayed stable; predicting ε with truncated-SNR weighting diverged. <!-- L10 -->

The lab runs progressive distillation from DDIM with the exact denoiser on 64 steps, halving six times, 4,000 updates a round and 8,000 for the last two, two seeds. Figure 3 compares every round's student with DDIM and DPM-Solver++(2M) at the same number of calls, both with the exact denoiser.

![Sample distance and blends against calls: progressive distillation's students beat DDIM and DPM-Solver++ with the exact denoiser](FIG_03)

*Figure 3. Measured, mean of two seeds. The solvers use the exact denoiser; the students are trained networks, starting from 64 DDIM steps and halving six times. Below eight calls every student is far closer to the data than either solver with the same calls.*

Below eight calls every student beats both solvers, though the solvers use the exact denoiser and the students are networks. At two calls the student's samples sit 0.042 from the data and DDIM's 0.243, with 9% blends against 76%; at four, 0.040 against DDIM's 0.128 and DPM-Solver++(2M)'s 0.055. The student's own errors grow round by round. After the first halving it draws a different crescent from the exact path for 1.9% of noises, about the network teacher's own 1.8%; at one step, 3.7%, with 16% of samples blended and a sample distance of 0.046.

Direct regression, the older recipe of Luhman & Luhman (an arXiv preprint), maps each noise straight to its teacher's endpoint in one call, and it does as well here: 3.0% flips, 12% blends, 0.044. <!-- L04 --> Its price is the training set. Every pair costs a full solve of the ODE, 4,000 exact-denoiser calls apiece in the lab, and the original paper built 1.024 million pairs per dataset; progressive distillation was designed to avoid exactly that cost. <!-- L05 --> <!-- L06 -->

The published numbers have the same shape. On CIFAR-10, progressive distillation scored FID 9.12, 4.51, 3.00 and 2.57 at one, two, four and eight steps: near its teacher down to four or eight, degrading faster below. <!-- L12 --> Its students also lose something a solver never does. Each works at its own step count only, and a one-step student cannot be sampled with more steps to recover detail; trained in one codebase beside five alternatives, a progressively distilled model was the best of six at one step on CelebA-HQ (FID 14.8) and unusable at 128 steps (302.9). <!-- L42 -->

## What does a consistency model learn?

A **consistency model** learns the flow map's endpoint from every noise level at once: $f(x,\sigma)$ is where the exact path through $x$ at level σ ends, so its outputs agree for every point on one path, the property its authors call self-consistency. <!-- L13 --> The end condition is built into the network as $f = c_\text{skip}(\sigma)\,x + c_\text{out}(\sigma)\,F_\theta$ with $c_\text{skip}(\sigma_\text{min}) = 1$ and $c_\text{out}(\sigma_\text{min}) = 0$, so at the clean end $f$ returns its input, which rules out the trivial solution $f \equiv 0$, whose outputs agree on every path too. <!-- L14 -->

**Consistency distillation** trains it from a teacher. Take a training image noised to level $t_{n+1}$, take one Heun step of the teacher's ODE down to $t_n$, and train $f$ at $t_{n+1}$ to match a slowly updated copy of itself, the **target network**, at $t_n$. <!-- L16 --> On CIFAR-10 the best settings were 18 levels, Heun's solver and the LPIPS distance; the target's moving-average rate was 0 there and 0.95 on ImageNet. <!-- L17 --> To spend more calls, the sampler alternates: jump to the end, add fresh noise back to a lower level, jump again. <!-- L15 --> **Consistency training** drops the teacher: the two points come from one training image noised to adjacent levels with the same noise. <!-- L18 -->

The line of work moved fast. With both distilling the same EDM teacher, the original paper put consistency distillation ahead of progressive distillation at one step, FID 3.55 against 8.34 on CIFAR-10 and 6.20 against 15.39 on ImageNet 64. <!-- L19 --> <!-- L20 --> Improved consistency training (iCT) needed no teacher and reached 2.51 and 3.25 in one step; sCM's continuous-time version reached 2.06 on CIFAR-10 and 1.48 on ImageNet 64 with two steps, and 1.88 on ImageNet 512 at 1.5 billion parameters. <!-- L21 --> <!-- L23 --> Latent consistency models brought the recipe to Stable Diffusion: a 768×768 model sampling in two to four steps trained in about 32 A100 GPU hours, as an arXiv preprint reports. <!-- L49 -->

The lab's consistency student follows the original recipe with the exact denoiser as teacher: 18 levels, one Heun step per target, squared error, a target-network rate of 0.95. With one call it draws a different crescent from the exact path for 3.2% of noises, as often as the progressive and regression students, but 23% of its samples are blends against their 12–16%, and its sample distance is 0.049. Figure 4 lines up six of its samples with the other one-call students', three from noises within 0.002 of a decision boundary and three far from one.

![Eight-by-eight samples from six noises: exact endpoints, DDIM and one-call students; near a decision boundary some blend or switch crescent](FIG_04)

*Figure 4. Measured, seed 1. Far from a boundary every student draws the exact path's crescent. Near one, DDIM's single call returns the blur and the students either blend two crescents or commit to the other one (outlined).*

Figure 5 shows where the misses happen. For each starting noise the lab measures how close it sits to a decision boundary: the gap between its two largest projections onto the four crescent directions, which picks the exact path's crescent for 97% of noises.

![Flip and blend shares of one-call students by distance from a decision boundary: errors concentrate in the 13% of noises nearest one](FIG_05)

*Figure 5. Measured, mean of two seeds. The grey bars show how many of the 4,096 noises fall in each bin. Above a margin of 0.4 the four students flipped one noise between them, and the nearest bins hold most of the flips.*

Noises within 0.1 of a boundary are 13% of all starting noises and produce 58–78% of every one-call student's flips. In the nearest bin, the 3% of noises with a margin below 0.025, a fifth to a quarter of each student's samples flip and 68–99% are blends. Past a margin of 0.4, more than half of all noises, none of the four students flipped a single noise, apart from one noise in one seed of the shortcut model. This is the worked example's cliff in 64 dimensions: where the exact map changes crescent abruptly, a smooth student is wrong; everywhere else it is close.

More calls help a consistency model less than they help a solver. Re-noising between calls cut the consistency student's blends from 23% at one call to 9.8% at two and 0.7% at eight, but its sample distance did not fall steadily (0.049, 0.045, 0.063, 0.056 and 0.041 at one, two, three, four and eight calls), its samples kept 41–77% more fine-scale noise than the data, and its pairing with the starting noise went: by three calls 58% of samples showed a different crescent from the exact path, by eight 75%, the share a random pick would give. Each extra call adds fresh noise and lets the model decide again what the previous call decided, and Align Your Flow's authors prove that this multistep sampling accumulates error, with quality degrading from about four steps on. <!-- L47 -->

## What happens when the student stops following the path?

Distribution matching distillation (DMD, CVPR 2024) trains a one-step generator $G$ without asking where any particular noise should end. It minimises an approximate reverse Kullback–Leibler divergence between the generator's output distribution and the data's, and the gradient of that divergence with respect to a sample is the difference between two **scores**, the directions in which each distribution's density rises. <!-- L30 --> Both are read off denoisers after noise is added to the sample: the frozen teacher gives the real one, and a second denoiser, trained online on the generator's own samples, gives the fake one. <!-- L30 --> <!-- L31 --> Figure 6 draws one update.

![DMD's update: a generated sample is noised and read by the frozen teacher and a fake denoiser; their difference moves the generator](FIG_06)

*Figure 6. The difference between the two denoisers pushes each generated sample toward the data and away from where the generator already puts its samples. The fake denoiser has to keep up with a generator that keeps moving.*

Reverse KL is mode-seeking: it penalises samples where the data has none, not data where the samples have none. DMD's own two-mode toy shows the consequence, its generator recovering only the nearer mode, and DMD adds a regression loss on noise–image pairs from the teacher's sampler to pin the modes down. <!-- L56 --> <!-- L32 --> On ImageNet 64 that gave FID 2.62 in one step against its EDM teacher's 2.32 at 512 calls; dropping the regression loss cost 2.62 → 5.61. <!-- L33 --> DMD2 removed the pairs, which for SDXL would take about 700 A100-days to generate, and found that without them training oscillates unless the fake denoiser gets five updates for every generator update; with that ratio and a GAN loss on real images it reached FID 1.28, below the teacher's ODE sampler (2.32) and its stochastic sampler (1.36). <!-- L35 --> <!-- L36 -->

The lab's distribution matcher uses the exact denoiser as the real one and, for the fake one, a copy of the network teacher that first trains for 2,000 updates on the generator's initial samples. Every run, with one or five fake updates per generator update and with or without the regression loss, put all of its samples on a single crescent within the first 100 generator updates (Figure 7). The generator starts as the teacher's answer at σ = 80, which is the blur of the problem section, so every sample moves the same way at first.

![Crescent coverage during DMD training: every run collapses onto one crescent by update 100, then recovers; brightness drifts less at 5:1](FIG_07)

*Figure 7. Measured. Top, seed 1 (seed 2 alike): the share of 1,024 fixed noises' samples on each crescent. Every run collapses by update 100; the regression loss puts every crescent back above 15% of the samples within 400 updates, distribution matching alone after 800 to 3,100. Bottom, both seeds: mean brightness of the same samples, which the 5:1 ratio keeps closer to the data's 0.*

With the regression loss, every crescent was back above 15% of the samples within 400 updates; without it, only after 800 to 3,100. By 8,000 updates every run covered all four, the smallest share 20%, but the samples were still soft: 27–38% blends, and a sample distance of 0.072–0.090 without the regression loss and 0.055 with it, where the one-call regression, progressive and consistency students reached 0.044–0.049. The lab leaves out the GAN loss on real images that DMD2 adds. Five fake updates per generator update did one of the two things DMD2 reports: the mean brightness of the same 1,024 samples drifted between −0.060 and +0.075 over training with one update, and between −0.016 and +0.038 with five. They did not speed the recovery, and the one-update runs ended more evenly spread. One thing nobody asked for also happened: 84–85% of each generator's samples landed on the same crescent as the exact path from the same noise.

Adversarial diffusion distillation (ADD), the method behind SDXL-Turbo, mixes the same kind of score distillation with a discriminator trained on real images, and samples in one to four steps; its paper notes that the realism comes with lower sample diversity than its SDXL teacher. <!-- L39 --> <!-- L52 --> sCM's authors measured the trade directly: score distillation behaves like strong guidance, raising precision and lowering recall until modes collapse, while their two-step consistency model kept the teacher's precision and recall. <!-- L25 -->

## Can one network take any number of steps?

Every student so far is tied to its training: a progressive student to its step count, a consistency model to the end of the path, a distribution matcher to one call or a fixed few. **Shortcut models** (ICLR 2025) condition one network on the size of the jump as well as the noise level. A jump of size zero is ordinary **flow matching**, which regresses the velocity of a straight path from noise to a training image and needs no teacher; a jump of size $2d$ is trained to equal two jumps of size $d$ made by the network itself. <!-- L40 --> With 128 as the smallest step, a quarter of each batch spent on these self-made targets and weight decay for stability, training costs about 16% more than a plain diffusion model, in one run. <!-- L41 -->

The lab's shortcut model writes each jump as a DDIM step with a learned target, trained from data alone, 40,000 updates, so it starts with no teacher at all. Figure 8 compares it with the students that serve a single step count.

![Sample distance and flip share against calls: a shortcut model improves and stays paired; a consistency model's flips rise to 75%](FIG_08)

*Figure 8. Measured, mean of two seeds. One shortcut network serves every count and keeps its pairing; the consistency model gains from a second call and then re-decides at random; progressive distillation needs a separate student for each count.*

At one call the shortcut model is the weakest path-follower: 40% of its samples are blends and its sample distance is 0.076, against progressive distillation's 16% and 0.046, the same order the published comparison below finds. It differs in what more calls do. Its blends fall to 19% at two calls, 7.9% at eight and 0.4% at 128, with a sample distance between 0.040 and 0.046 from eight calls on, and its flips stay between 2.9% and 4.7% at every count, because each call is a deterministic jump along one path. The consistency model, re-noising between calls, had lost its pairing by three. The shortcut model's floor is its own: trained from noisy single-image targets with no teacher, its 128-call samples flip 3.0% of decisions where the network teacher's flip 1.8%.

The published comparison agrees. Figure 9 charts one paper's table, in which every objective was trained in one codebase on the same transformer. Its reflow row is rectified flow's way to fewer steps: retrain on the model's own noise–image pairs so that its paths straighten, until even one Euler step lands close. <!-- L29 -->

![Quoted FIDs at 128, 4 and 1 steps for six training objectives on CelebA-HQ and ImageNet 256: the shortcut model stays low at every budget](FIG_09)

*Figure 9. Quoted from Frans, Hafner, Levine & Abbeel, ICLR 2025, Table 1: FID-50k on CelebA-HQ and ImageNet at 256×256, DiT-B. Progressive distillation is best at one step and has no use at 128; the shortcut model is close to the best at every budget.*

All of these are pieces of one object. The flow map can be written $X_{s,t}(x) = x + (t-s)\,v_{s,t}(x)$, where $v_{s,t}$ is the slope of the straight line between two points on a path; on the diagonal it is the ODE's velocity, and consistency models, consistency trajectory models, shortcut models and MeanFlow are each a way of learning it off the diagonal. <!-- L44 --> The consistency trajectory model (CTM) learns jumps from any level to any lower one, in exactly the DDIM form the worked example used, and reports FID 1.92 on ImageNet 64 in one step with added denoising and GAN losses. <!-- L27 --> <!-- L28 --> MeanFlow learns the average velocity over an interval through an identity that ties it to the instantaneous one, and reaches FID 3.43 in one call on ImageNet 256 trained from scratch. <!-- L46 --> The same paper that wrote down the flow map's characterisations found its "Lagrangian" training family the most stable. <!-- L45 -->

## Which metric shows the damage?

Two numbers can rank the same students in opposite orders. A workshop paper made the point sharply: a consistency model trained to match an ODE solver directly solved the ODE more accurately than a standard one, error 0.25 against 0.29, and produced worse images, FID 158.6 against 103.9. <!-- L50 --> So a student's damage has to be read in the metric that matches its failure. **Precision** is the chance that a generated image falls within the support of real images, and **recall** the chance that a real image falls within the support of generated ones; together they separate fidelity from coverage. <!-- L58 --> Figure 10 plots both for one benchmark from one paper's table.

![Quoted precision against recall on ImageNet 64: one-step PD loses precision, consistency training and a GAN lose recall](FIG_10)

*Figure 10. Quoted from Song & Dhariwal, iCT, ICLR 2024, Table 3: class-conditional ImageNet 64×64, precision against recall. One-step progressive distillation loses precision; consistency training and a GAN lose recall; iCT-deep sits next to the teacher.*

<!-- L57 -->

The lab's one-call students, side by side (mean of two seeds):

| Method | Keeps the teacher's pairing | One call: flips · blends · sample distance | What breaks | Where it shows |
|---|---|---|---|---|
| Direct regression | yes | 3.0% · 12% · 0.044 | blends at decisions; a full ODE solve per training pair | fidelity |
| Progressive distillation | yes | 3.7% · 16% · 0.046 | errors compound per round; one student per step count | fidelity: one-step precision 0.59 against the teacher's 0.71 on ImageNet 64 |
| Consistency distillation | at one call | 3.2% · 23% · 0.049 | more calls re-decide and leave grain | fidelity; pairing at more calls |
| Shortcut model | yes | 4.7% · 40% · 0.076 | weakest at one call | fidelity at one call |
| DMD, no pairs | mostly, unasked (84–85%) | 15–16% · 32–37% · 0.075–0.084 | collapse onto one mode, slow recovery, soft samples | coverage during training; recall in published models |
| DMD with regression | mostly (90%) | 9.8% · 31% · 0.055 | soft samples: 70% of the data's fine detail | fidelity |

<!-- L57 --> <!-- L25 -->

rCM, distilling video models at scale, reports both failures at once: consistency distillation alone loses fine detail, DMD2-style distillation loses diversity, and the two losses combined keep both. <!-- L51 --> The surveys file these methods differently: one TPAMI survey puts progressive distillation among "distribution-based" methods, another among "fidelity distillation". <!-- L02 --> <!-- L03 --> The split that predicts the failure is the one this post measures: whether the student keeps the teacher's pairing of noise to image.

## The math

| Symbol | Meaning |
|---|---|
| $x$, σ | a noisy sample and its noise level, $x = x_0 + \sigma\epsilon$ |
| $D(x;\sigma)$ | the denoiser: the estimate of the clean image |
| $\Phi(x;\sigma\to\sigma')$ | the flow map: where the exact path through $x$ at σ is at σ′ |
| $\bar D(x;\sigma,\sigma')$ | the target that makes one DDIM step from σ to σ′ exact |
| $f(x,\sigma)$ | a consistency model, $\Phi(x;\sigma\to\sigma_\text{min})$ |
| $G(z)$ | a one-step generator |

**Every path-following student learns one DDIM step with a better target.** Part 6 wrote the exact solution of the ODE from σ to σ′ as $x(\sigma') = \frac{\sigma'}{\sigma}x(\sigma) + \sigma'\int_{\sigma'}^{\sigma} D(x(s);s)\,s^{-2}\,ds$. Since $\sigma'\int_{\sigma'}^{\sigma} s^{-2}\,ds = 1 - \sigma'/\sigma$, the same equation reads

$$
\Phi(x;\sigma\to\sigma') = \frac{\sigma'}{\sigma}\,x + \Big(1 - \frac{\sigma'}{\sigma}\Big)\,\bar D(x;\sigma,\sigma'), \qquad
\bar D = \frac{\int_{\sigma'}^{\sigma} D(x(s);s)\,s^{-2}\,ds}{\int_{\sigma'}^{\sigma} s^{-2}\,ds} .
$$

A jump is a DDIM step whose "denoised image" is the average of the denoiser's answers along the exact path, weighted by $1/s^2$, which leans toward the clean end. DDIM freezes that average at its first term, $D(x;\sigma)$, and is exact only where $D$ does not change; the worked example's 0.168 against 0.701 is this gap. In the lab the jump from 80 to 2.515 at $x = 40$ gives $\bar D = 3.270$ by solving the path and 3.270 by averaging $D$ along it. As σ′ → σ, $\bar D \to D$, the diffusion model; as σ′ → 0, $\bar D \to \Phi(x;\sigma\to 0)$, the consistency function. CTM's jump $G(x_t,t,s) = \frac{s}{t}x_t + (1-\frac{s}{t})\,g_\theta(x_t,t,s)$ is this form with a network for $\bar D$. <!-- L27 -->

**Progressive distillation** gets $\bar D$ for a grid step from two teacher steps, $x \to x' \to x''$, by inverting one DDIM step:

$$
\tilde D = \frac{x'' - (\sigma''/\sigma)\,x}{1 - \sigma''/\sigma} .
$$

**Consistency distillation** minimises $\lVert f_\theta(x_{t_{n+1}}, t_{n+1}) - f_{\theta^-}(\hat x_{t_n}, t_n)\rVert^2$, with $\hat x_{t_n}$ one teacher step from $x_{t_{n+1}}$ and $\theta^-$ the target network. **The shortcut model** trains a jump of size $2d$ to match two of its own jumps of size $d$, which is the same inversion as progressive distillation with the network as its own teacher.

**Distribution matching.** DMD's update moves each generated sample $x = G(z)$, noised to $x_\sigma = x + \sigma\epsilon$, along

$$
g = \frac{D_\text{fake}(x_\sigma;\sigma) - D_\text{real}(x_\sigma;\sigma)}{\operatorname{mean}\,\lvert D_\text{real}(x_\sigma;\sigma) - x\rvert}, \qquad x \leftarrow x - \eta\,g ,
$$

the difference of the two scores rewritten through the denoisers, normalised per sample. <!-- L31 --> Nothing in $g$ refers to $\Phi$: two generators that send each noise to different images are equally good if their sets of images match.

<details>
<summary>Why the score difference is the reverse-KL gradient</summary>

For $p_\text{fake}$ the distribution of $G_\theta(z)$, $\nabla_\theta D_\text{KL}(p_\text{fake}\,\Vert\,p_\text{real}) = \mathbb{E}_z\big[(s_\text{fake}(x) - s_\text{real}(x))\,\partial G_\theta(z)/\partial\theta\big]$ with $s = \nabla_x \log p$: the term from differentiating $p_\text{fake}$ itself has zero expectation. Neither score exists where the two distributions do not overlap, so DMD evaluates both after adding noise, where Tweedie's formula turns each denoiser into a score, $s(x_\sigma) = (D(x_\sigma;\sigma) - x_\sigma)/\sigma^2$. <!-- L30 --> Then $s_\text{fake} - s_\text{real} = (D_\text{fake} - D_\text{real})/\sigma^2$, and DMD's per-sample weight $\sigma^2/\operatorname{mean}\lvert D_\text{real} - x\rvert$ gives $g$ above. <!-- L31 -->

</details>

## Implementation

The three targets fit in a few lines over any denoiser `D(x, s)` that takes a batch and a column of noise levels; each loss trains a network `net(x, s)` that outputs a denoised image.

```python
import torch

def pd_loss(student, teacher, x0, s, s_mid, s_next):
    """Progressive distillation: one student DDIM step must match two teacher steps."""
    z = x0 + s * torch.randn_like(x0)                    # noised training data
    with torch.no_grad():
        d1 = teacher(z, s);   zm = d1 + (s_mid / s) * (z - d1)
        d2 = teacher(zm, s_mid); z2 = d2 + (s_next / s_mid) * (zm - d2)
        r = s_next / s
        target = (z2 - r * z) / (1 - r)                  # invert one DDIM step
    return ((student(z, s) - target) ** 2).mean()

def cd_loss(f, f_target, D_teacher, x0, t_n, t_n1):
    """Consistency distillation: f at t_{n+1} matches the EMA target at t_n after one Heun step."""
    x1 = x0 + t_n1 * torch.randn_like(x0)
    with torch.no_grad():
        d = (x1 - D_teacher(x1, t_n1)) / t_n1
        xe = x1 + (t_n - t_n1) * d
        x_hat = x1 + (t_n - t_n1) * 0.5 * (d + (xe - D_teacher(xe, t_n)) / t_n)
        goal = f_target(x_hat, t_n)
    return ((f(x1, t_n1) - goal) ** 2).mean()

def dmd_loss(G, D_fake, D_real, z, s):
    """Distribution matching: the gradient of this loss with respect to x is exactly g."""
    x = G(z)
    with torch.no_grad():
        x_s = x + s * torch.randn_like(x)
        dr, df = D_real(x_s, s), D_fake(x_s, s)
        g = (df - dr) / (dr - x).abs().mean(1, keepdim=True)
    return 0.5 * ((x - (x - g).detach()) ** 2).sum(1).mean()   # detach: the target is x - g, held fixed
```

Every network in the lab uses EDM's preconditioning, which scales the input and output by the noise level so one network serves every σ. <!-- L54 --> `cd_loss` needs a network whose output is pinned at the clean end, `f = c_skip * x + c_out * F` with $c_\text{out}(\sigma_\text{min}) = 0$, and `dmd_loss` needs `D_fake` trained on detached samples of `G` between generator steps, five times per step in DMD2. The lab's `distill.py` adds direct regression and the shortcut model, the exact crescent-world teacher, and every number and figure in this post; it is under [Lab downloads](#lab-downloads).

## Limitations and common mistakes

> [!WARNING]
> **Common mistake: judging a distilled model by one metric.** A path-following student can match its teacher on FID and still blend images at decision boundaries; a distribution-matching student can score a better FID than its teacher and have dropped a mode. Report a fidelity measure and a coverage measure, precision and recall or their equivalents, and check pairing against the teacher when the application needs it, such as editing an image by editing its noise.

- **Distilling an ε-prediction network as it stands.** A one-step student runs where the input holds no signal, and an ε-prediction head multiplies its error by σ there. Convert to x-, v- or mixed prediction first, as progressive distillation did. <!-- L10 -->
- **Expecting more calls to fix a few-step model.** A progressive student works at its own step count only, and a consistency model's multistep sampling stops improving after a few calls; in the lab a consistency model's sample distance went 0.049, 0.045, 0.063, 0.056 and 0.041 from one call to eight while its decisions became random. If you need a step-count dial, train a shortcut model or a flow map. <!-- L47 --> <!-- L42 -->
- **Starting distribution matching from the teacher's weights and walking away.** The generator's first answer is the blur, every sample moves together, and in the lab every run first put all its samples on one crescent; the pairs of DMD's regression loss brought all four back within 400 updates, distribution matching alone took up to 3,100. Watch per-mode coverage and simple statistics such as mean brightness during training, as DMD2 recommends, not only the loss. <!-- L35 -->
- **Reading the toy as typical.** Crescent world has four isolated modes, the worst case for mode-seeking objectives and the clearest case for decision boundaries, and its networks are tiny. Real images have no clean modes, so the same failures show up as partial loss of recall and softer detail rather than whole missing crescents, and the lab has no guidance, which every shipped text-to-image student distils as well. Meng et al. showed how, in two stages: one student first matches the guided combination of the conditional and unconditional models, then progressive distillation cuts its steps. <!-- L48 --> Guidance itself is the subject of a later part of this series.

## Key takeaways

- A diffusion model learns the slope of the sampling path; few-step methods learn the jump, the flow map, which no solver can recover in one call because one call only ever sees the blur at the start.
- Progressive distillation, consistency models, shortcut models, CTM and MeanFlow all learn the flow map at different pairs of noise levels; each jump is a DDIM step whose target is a path-average of the denoiser.
- Path-following students fail at decisions: where starting noises a hair apart end on different images, a smooth student blends them, and blends cost fidelity.
- Distribution matching drops the pairing and with it that limit, but its mode-seeking objective can lose whole modes, which costs coverage; in the lab a regression loss on the teacher's pairs restored them within 400 updates, and a faster-updated critic did not speed that up.
- Read precision and recall, not one FID, and keep a step-count dial if you need one: only flow-map students keep improving with more calls.

## Try it yourself

These can be answered from the article alone. The full exercise ladder, with the lab's own run as the answer key, is in the lab's README under [Lab downloads](#lab-downloads).

### E1 — Reproduce: the distillation target at x = 40

With the closed-form denoiser of the worked example and the levels 80 → 17.53 → 2.515, take the teacher's two DDIM steps from $x = 40$ and invert one student step from 80 to 2.515.

**Self-check:** your target is within 0.005 of 0.701.

<details><summary>Answer</summary>

Step 1: $D(40; 80) = 0.168$ and $x' = 0.168 + 0.2191 \times 39.832 = 8.895$. Step 2: $D(8.895; 17.53) = 0.771$ and $x'' = 0.771 + 0.1435 \times 8.124 = 1.937$. The student must reach 1.937 from 40 in one step from 80 to 2.515, so $\tilde D = (1.937 - 0.03144 \times 40)/(1 - 0.03144) = 0.6791/0.9686 = 0.701$. The lab prints 0.7012.

</details>

### E3 — Predict: the same halving at x = 1.6

Repeat the halving from ε = 0.02, $x = 1.6$, where $D(1.6;80) = 0.0067$. Before computing, predict the ratio of the student's target to $D$.

**Self-check:** your predicted ratio is within 10% of the computed one, for the reason that near the midpoint every step is linear in $x$.

<details><summary>Answer</summary>

About 4.2 again: the lab prints a target of 0.0283 against $D = 0.0067$. Near the midpoint the tanh in the denoiser is almost linear, so each teacher step multiplies $x$ by a fixed factor and the target is a fixed multiple of the denoiser's answer. At $x = 40$ the ratio was 0.701/0.168 = 4.18; at $x = 1.6$ it is 4.22. It changes only where a step's tanh leaves its linear range, closer to a crescent.

</details>

## References

### Lab downloads

- [`README.md`](LAB_01) — the lab's grade, what was executed, provenance, run order, and the E1–E4 exercise ladder.
- [`distill.py`](LAB_02) — the exact crescent-world teacher, five families of students, and every experiment in this post.
- [`requirements.txt`](LAB_03) — the pinned numpy and CPU PyTorch versions.
- [`captures.json`](LAB_04) — the author's run, machine-readable, which every measured figure was drawn from.
- [`expected-output.txt`](LAB_05) — the same run as printed, to compare against your own.
- [`notebook.ipynb`](LAB_06) — the README with a runnable cell under each step and exercise.
- [Complete lab](https://minio.canery.in/media/lab-few-step-diffusion-distillation.zip) — every file above in one zip.

### Sources

**Surveys**

1. Yang, Zhang, Song, Hong, Xu, Zhao, Zhang, Cui & Yang. [Diffusion Models: A Comprehensive Survey of Methods and Applications](https://doi.org/10.1145/3626235). ACM Computing Surveys, 2023.
2. Ma, Zhang, Jia, Zhao, Ma, Ma, Liu, Zhang, Li & Zhou. [Efficient Diffusion Models: A Comprehensive Survey From Principles to Practices](https://doi.org/10.1109/TPAMI.2025.3569700). IEEE TPAMI 47(9), 2025.
3. Fan, Wu & Wu. [A Survey on Pre-Trained Diffusion Model Distillations](https://arxiv.org/abs/2502.08364). arXiv preprint, 2025.

**Following the path**

4. Luhman & Luhman. [Knowledge Distillation in Iterative Generative Models for Improved Sampling Speed](https://arxiv.org/abs/2101.02388). arXiv preprint, 2021.
5. Salimans & Ho. [Progressive Distillation for Fast Sampling of Diffusion Models](https://arxiv.org/abs/2202.00512). ICLR 2022.
6. Meng, Rombach, Gao, Kingma, Ermon, Ho & Salimans. [On Distillation of Guided Diffusion Models](https://doi.org/10.1109/CVPR52729.2023.01374). CVPR 2023.
7. Song, Dhariwal, Chen & Sutskever. [Consistency Models](https://proceedings.mlr.press/v202/song23a.html). ICML 2023.
8. Song & Dhariwal. [Improved Techniques for Training Consistency Models](https://proceedings.iclr.cc/paper_files/paper/2024/hash/41bd71e7bf7f9fe68f1c936940fd06bd-Abstract-Conference.html). ICLR 2024.
9. Lu & Song. [Simplifying, Stabilizing and Scaling Continuous-time Consistency Models](https://proceedings.iclr.cc/paper_files/paper/2025/hash/7e9c2053258b1bdd32ff2654802cd594-Abstract-Conference.html). ICLR 2025.
10. Luo, Tan, Huang, Li & Zhao. [Latent Consistency Models: Synthesizing High-Resolution Images with Few-Step Inference](https://arxiv.org/abs/2310.04378). arXiv preprint, 2023.
11. Vouitsis, Hosseinzadeh, Ross, Villecroze, Gorti, Cresswell & Loaiza-Ganem. [Inconsistencies In Consistency Models: Better ODE Solving Does Not Imply Better Samples](https://arxiv.org/abs/2411.08954). NeurIPS 2024 ATTRIB workshop; arXiv preprint.

**Matching the set**

12. Yin, Gharbi, Zhang, Shechtman, Durand, Freeman & Park. [One-step Diffusion with Distribution Matching Distillation](https://doi.org/10.1109/CVPR52733.2024.00632). CVPR 2024.
13. Yin, Gharbi, Park, Zhang, Shechtman, Durand & Freeman. [Improved Distribution Matching Distillation for Fast Image Synthesis](https://doi.org/10.52202/079017-1505). NeurIPS 2024.
14. Sauer, Lorenz, Blattmann & Rombach. [Adversarial Diffusion Distillation](https://doi.org/10.1007/978-3-031-73016-0_6). ECCV 2024.
15. Zheng, Wang, Ma, Chen, Zhang, Balaji, Chen, Liu, Zhu & Zhang. [Large Scale Diffusion Distillation via Score-Regularized Continuous-Time Consistency](https://arxiv.org/abs/2510.08431). ICLR 2026.

**Flow maps**

16. Kim, Lai, Liao, Murata, Takida, Uesaka, He, Mitsufuji & Ermon. [Consistency Trajectory Models: Learning Probability Flow ODE Trajectory of Diffusion](https://proceedings.iclr.cc/paper_files/paper/2024/hash/c204d12afa0175285e5aac65188808b4-Abstract-Conference.html). ICLR 2024.
17. Frans, Hafner, Levine & Abbeel. [One Step Diffusion via Shortcut Models](https://proceedings.iclr.cc/paper_files/paper/2025/hash/559a0998fab1d19b80e7e43a5852401c-Abstract-Conference.html). ICLR 2025.
18. Boffi, Albergo & Vanden-Eijnden. [How to build a consistency model: Learning flow maps via self-distillation](https://doi.org/10.52202/085713-1121). NeurIPS 2025.
19. Geng, Deng, Bai, Kolter & He. [Mean Flows for One-step Generative Modeling](https://doi.org/10.52202/085713-2534). NeurIPS 2025.
20. Sabour, Fidler & Kreis. [Align Your Flow: Scaling Continuous-Time Flow Map Distillation](https://doi.org/10.52202/085713-4900). NeurIPS 2025.
21. Liu, Gong & Liu. [Flow Straight and Fast: Learning to Generate and Transfer Data with Rectified Flow](https://arxiv.org/abs/2209.03003). ICLR 2023.

**Evaluation and models in use** (model cards accessed 2026-10-16)

22. Kynkäänniemi, Karras, Laine, Lehtinen & Aila. [Improved Precision and Recall Metric for Assessing Generative Models](https://arxiv.org/abs/1904.06991). NeurIPS 2019.
23. Karras, Aittala, Aila & Laine. [Elucidating the Design Space of Diffusion-Based Generative Models](https://proceedings.neurips.cc/paper_files/paper/2022/hash/a98846e9d9cc01cfb87eb694d946ce6b-Abstract-Conference.html) (EDM). NeurIPS 2022.
24. Stability AI. [SDXL-Turbo model card](https://huggingface.co/stabilityai/sdxl-turbo).
25. Black Forest Labs. [FLUX.1-schnell model card](https://huggingface.co/black-forest-labs/FLUX.1-schnell).
