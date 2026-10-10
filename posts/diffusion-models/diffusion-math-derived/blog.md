---
title: "Where the Diffusion MSE Loss Comes From"
slug: diffusion-math-derived
date: 2026-09-25
updated: 2026-09-25
summary: "Diffusion's MSE loss is a reweighted ELBO: each reverse step's KL between Gaussians is a squared error, and DDPM, NCSN and score SDEs differ only in the weights."
tags: [machine-learning, diffusion-model, generative-model, variational-inference, score-matching, deep-learning]
category: machine-learning
series: diffusion-models
series_position: 3
tier: L4
difficulty: advanced
prerequisites: ["Part 2's map of a diffusion system", "calculus", "expectations", "KL divergence"]
reading_minutes: 44
cover_image: "COVER"
canonical_url: "https://canery.in/blogs/diffusion-math-derived"
---

![Two overlapping bell curves, the teacher's solid and the network's dashed, with the gap between their centres marked, beside the crescent patch clean and noised](COVER)

> [!NOTE]
> **Insights** — The MSE loss that trains a diffusion model is a reweighted variational bound on its log-likelihood. The bound splits into one KL divergence per denoising step. Both sides of every KL are Gaussians with the same variance, so each KL is a squared distance between two means; writing those means in terms of the noise turns it into $`\lVert\epsilon-\hat\epsilon\rVert^2`$ times a weight. DDPM throws the weight away. Denoising score matching, NCSN and the score SDE arrive at the same squared error with different weights, which is why the three are one object.

**Level:** advanced · **You need:** [Part 2's map of the system](https://canery.in/blogs/diffusion-model-architecture#the-math), calculus, expectations, KL divergence · **Time:** ~44 min

**Jump to:** [worked example](#worked-example) · [the ELBO](#what-is-the-elbo-and-why-is-diffusion-a-vae) · [one squared error per step](#how-does-the-bound-become-one-squared-error-per-step) · [the dropped weights](#why-does-ddpm-throw-the-weights-away) · [one loss, many weights](#is-every-diffusion-loss-the-same-loss) · [the score](#where-does-the-score-come-from) · [one object](#how-are-ddpm-ncsn-and-the-sde-one-object) · [math](#the-math) · [implementation](#implementation)

## Why this matters

You train a diffusion model, the loss curve settles at 0.03, and someone asks for its log-likelihood in bits per dimension. The loss value is not that number. DDPM's own best-looking CIFAR-10 model, trained on the simple loss, has a *worse* likelihood bound than the model trained on the bound itself: 3.75 bits per dimension against 3.70. <!-- L10 -->

Or you switch the network's target from noise to "velocity" because a paper said it trains more stably, and the model behaves differently. At any single noise level the two targets have the same optimum. What you changed is how the loss trades one noise level against another. Both situations are unreadable until you know which exact steps turn a likelihood into a regression, and which single step does not.

## The problem

A diffusion model is a **latent-variable model**: a model with unobserved random variables that it averages over. Here the unobserved variables are the noisy states $`x_1,\dots,x_T`$, each the same size as the image $`x_0`$. The model defines a joint distribution over the whole chain — start from Gaussian noise $`x_T`$, then take learned Gaussian steps down to $`x_0`$ — and the probability it gives a real image is that joint with every latent integrated out: <!-- L01 -->

$$
p_\theta(x_0)=\int p(x_T)\prod_{t=1}^{T}p_\theta(x_{t-1}\mid x_t)\,dx_{1:T}.
$$

The log of this number, $`\log p_\theta(x_0)`$, is the **evidence**, or log-likelihood. Maximum-likelihood training would push it up for every training image. It cannot, because the integral runs over every trajectory the chain could take.

Put sizes on that. For part 1's 4×4 patch and DDPM's $`T = 1000`$ steps, the integral is over 16,000 dimensions. For one 256×256 RGB image it is over 196,608 × 1,000, about 197 million. Each factor inside it is a neural network call, so there is no closed form. Sampling trajectories from the model and averaging does not help either: almost none of them end anywhere near the particular $`x_0`$ you are scoring.

Meanwhile, [part 1](https://canery.in/blogs/what-a-diffusion-model-actually-does#the-answer-key-is-free) trained the same model with a loss that looks nothing like a probability:

$$
L_{\text{simple}}=\mathbb{E}_{t,\,x_0,\,\epsilon}\Big[\big\lVert \epsilon-\epsilon_\theta\big(\sqrt{\bar\alpha_t}\,x_0+\sqrt{1-\bar\alpha_t}\,\epsilon,\;t\big)\big\rVert^2\Big].
$$

Corrupt an image, ask the denoiser for the noise, penalise the squared error. The problem this post solves is the gap between those two equations. The path between them has five steps: one inequality, one application of Bayes' rule, one identity about Gaussians, one change of variables, and one deliberate choice. Only the last one is not exact.

## Worked example

Take the top-left pixel of part 1's patch: $`x_0 = 0.95`$, with noise draw $`\epsilon = -0.55`$. At $`\bar\alpha_t = 0.64`$ the forward process gives

$$
x_t = 0.8 \times 0.95 + 0.6 \times (-0.55) = 0.76 - 0.33 = 0.43 .
$$

The network sees $`x_t = 0.43`$ and predicts the noise. Suppose it answers $`\hat\epsilon = -0.35`$, off by $+0.20$ — the same error part 1's first exercise used.

To keep every number checkable by hand, use a **coarse chain**: the step before $`x_t`$ sits at $`\bar\alpha_{t-1} = 0.80`$, so this one step has $`\alpha_t = 0.64/0.80 = 0.80`$ and $`\beta_t = 0.20`$. DDPM's real linear schedule takes 62 small steps to cross the same range, from step 146 to step 208. Every identity below holds for any step size; the coarse one only makes the arithmetic short.

### The teacher: where the previous step really was

Ask a question the network cannot answer but we can: given the noisy pixel *and* the clean one, where was the pixel one step earlier? Two independent Gaussian pieces of evidence bear on $`x_{t-1}`$.

- **From the clean pixel.** Running the forward process to step $t-1$ gives $`x_{t-1} \sim \mathcal N(\sqrt{0.80}\times 0.95,\ 0.20) = \mathcal N(0.8497,\ 0.20)`$.
- **From the noisy pixel.** One forward step turned $`x_{t-1}`$ into $`x_t = \sqrt{\alpha_t}\,x_{t-1} + \sqrt{\beta_t}\,\epsilon'`$. Read as a function of $`x_{t-1}`$, that step's likelihood is a Gaussian centred at $`0.43/\sqrt{0.80} = 0.4808`$ with variance $`0.20/0.80 = 0.25`$.

Two Gaussian beliefs about one quantity combine by adding their **precisions** — precision is 1/variance — and averaging their means weighted by precision. The precisions are 5 and 4, so the combined precision is 9 and the variance is 1/9:

$$
\text{mean} = \frac{5 \times 0.8497 + 4 \times 0.4808}{9} = 0.6857,
\qquad \text{variance} = \tfrac19 = 0.1111 .
$$

This Gaussian, $`\mathcal N(0.6857,\ 0.1111)`$, is the **forward posterior** $`q(x_{t-1}\mid x_t, x_0)`$: the exact distribution of the previous state given both endpoints. Call it the teacher. It knows $`x_0`$.

### The student: the network's step

The network does not know $`x_0`$. It has $`\hat\epsilon = -0.35`$, which implies a clean pixel of

$$
\hat x_0 = \frac{0.43 - 0.6\times(-0.35)}{0.8} = \frac{0.64}{0.8} = 0.80 .
$$

The student takes the teacher's recipe and plugs in its own guess: the same precisions 5 and 4, with $`\sqrt{0.80}\times 0.80 = 0.7155`$ in place of 0.8497. Its step is $`\mathcal N(0.6112,\ 0.1111)`$ — the teacher's bell curve, shifted left by 0.0745.

### The price

The **Kullback–Leibler (KL) divergence** $`D_{\mathrm{KL}}(q\,\Vert\,p)`$ is the expected log-ratio of two distributions: zero when they match, positive otherwise. For two Gaussians with the *same* variance $v$ it reduces to the squared gap between their means over $2v$:

$$
D_{\mathrm{KL}} = \frac{(0.6857 - 0.6112)^2}{2 \times 0.1111} = \frac{0.005556}{0.2222} = 0.0250 \text{ nats}.
$$

Figure 1 draws all four curves on one axis.

![Four bell curves over the previous pixel value: evidence from the clean pixel centred at 0.85, evidence from the noisy pixel at 0.48, their product the teacher at 0.69, and the student at 0.61](FIG_01)

*Figure 1. The teacher is narrower than either piece of evidence because precisions add, 5 + 4 = 9. The student has exactly the teacher's width, so the only thing the KL can measure is the 0.0745 gap between centres.*

The student's curve is not wrong in shape, only in position, and the position error is inherited entirely from the 0.20 error in $`\hat\epsilon`$. That is the whole mechanism of this post in one pixel.

### One error, five prices

The 0.20 error can be expressed in any of the quantities a diffusion network is trained to predict. Each gives a different squared error, and each converts back to the noise error by a constant fixed by the noise level:

| Network predicts | True | Predicted | Squared error | × constant | In noise units |
|---|---:|---:|---:|---|---:|
| noise $\epsilon$ | −0.5500 | −0.3500 | 0.0400 | × 1 | 0.0400 |
| clean pixel $x_0$ | 0.9500 | 0.8000 | 0.0225 | × SNR 1.7778 | 0.0400 |
| score $-\epsilon/0.6$ | 0.9167 | 0.5833 | 0.1111 | × $`1-\bar\alpha_t`$ 0.36 | 0.0400 |
| velocity $0.8\epsilon - 0.6x_0$ | −1.0100 | −0.7600 | 0.0625 | × $`\bar\alpha_t`$ 0.64 | 0.0400 |
| this step's KL | | | 0.0250 | = 0.625 × 0.0400 | |

SNR is the signal-to-noise ratio $`\bar\alpha_t/(1-\bar\alpha_t) = 0.64/0.36`$. Figure 2 lays the five rows side by side.

![Five rows pricing one prediction error: noise, clean pixel, score, velocity and the ELBO step, each with its squared error as a bar and the constant that converts it back to 0.04](FIG_02)

*Figure 2. Four of the five rows are the same number, 0.04, wearing a different constant. The fifth — the price the likelihood bound charges — is that number times 0.625, and the rest of this post derives where 0.625 comes from.*

At one noise level every one of these losses is proportional to every other, so all of them are minimised by the same prediction. The argument between "predict the noise" and "predict the velocity" is entirely about the constants: how much an error at this noise level should count against an error at another.

## Intuition

Think of each reverse step as a student copying a teacher who holds the answer key. The teacher, $`q(x_{t-1}\mid x_t,x_0)`$, has seen the clean image and says exactly where the previous state should be, with a known spread. The student, $`p_\theta(x_{t-1}\mid x_t)`$, has seen only the noisy state. Training scores the student by its KL divergence from the teacher, one step at a time, summed along the chain.

Because both are Gaussians of the same width, the KL cannot reward the student for getting the width right or penalise it for a wrong shape; there is nothing left to compare except where the centres sit. A squared distance between centres is a regression loss. That is why a likelihood-motivated objective looks like mean squared error: not by approximation, but because the two distributions it compares were chosen to differ only in their means.

The analogy breaks in one place, and the break matters. A real student could memorise the answer key. This one never sees it. Many clean images are consistent with the same $`x_t`$, the teacher moves with each of them, and the student must give one answer for all of them. The best it can do is the teacher's *average* over every $`x_0`$ that could have produced $`x_t`$ — which is [the conditional-mean argument from part 1](https://canery.in/blogs/what-a-diffusion-model-actually-does#why-does-one-call-blur-and-many-calls-draw), now seen from the loss side. The same average will turn out to be a score estimate, which is how the three formulations meet.

What makes the whole thing a bound rather than an identity is also visible here. We cannot compute how likely the image is. We can compute how far the student's steps are from the teacher's, and the log-likelihood is at least minus the total of those distances, plus two edge terms.

## What is the ELBO, and why is diffusion a VAE?

Start with one latent variable $z$ and any distribution $`q(z\mid x)`$ over it. Multiply and divide inside the integral, then move the log inside the average:

$$
\log p(x) = \log \mathbb{E}_{q(z\mid x)}\!\left[\frac{p(x,z)}{q(z\mid x)}\right] \;\ge\; \mathbb{E}_{q(z\mid x)}\!\left[\log\frac{p(x,z)}{q(z\mid x)}\right].
$$

The inequality is Jensen's: the log of an average is at least the average of the logs, because log is concave. The right-hand side is the **evidence lower bound (ELBO)**, the tractable quantity that stands in for the likelihood when the likelihood cannot be computed. It is not only a bound; the gap is known exactly: <!-- L18 -->

$$
\log p(x) = \mathrm{ELBO} + D_{\mathrm{KL}}\big(q(z\mid x)\,\Vert\,p(z\mid x)\big).
$$

The bound is tight precisely when $`q(z\mid x)`$ equals the model's true posterior. You care about this gap whenever someone reads a training loss as a likelihood: the negative ELBO is the negative log-likelihood plus a nonnegative gap that nobody measured.

A **variational autoencoder (VAE)** learns both halves: an encoder $`q_\phi(z\mid x)`$ and a decoder $`p_\theta(x\mid z)`$, trained jointly on this bound. A **hierarchical VAE** replaces the single latent with a chain, $`x \to z_1 \to z_2 \to \cdots`$, each encoded from the one before. A preprint by Luo describes a diffusion model as exactly this kind of chain with three restrictions: every latent is the same size as the data, each encoder step is fixed rather than learned — a Gaussian centred on a scaled copy of the previous state — and the encoder's variances are set so that the last latent is a standard Gaussian. <!-- L14 --> Set $`T = 1`$ and the diffusion bound collapses to the ordinary VAE bound. <!-- L16 --> The peer-reviewed Variational Diffusion Models paper takes the same reading, treating a diffusion model with a fixed number of steps as a hierarchical latent-variable model and building a lossless compressor on it. <!-- L55 -->

![Three small graphical models side by side: a VAE with a learned encoder, a hierarchical VAE with a chain of learned encoders, and a diffusion model whose encoder chain is fixed and whose latents have the image's size](FIG_03)

*Figure 3. The only arrows diffusion trains are the reverse ones. Freezing the encoder is what makes every later step of the derivation tractable — and what leaves the whole bound's gap for the decoder to close.*

Written for the chain, the bound is the one DDPM trains on: <!-- L02 -->

$$
-\log p_\theta(x_0) \;\le\; \mathbb{E}_{q(x_{1:T}\mid x_0)}\!\left[-\log\frac{p_\theta(x_{0:T})}{q(x_{1:T}\mid x_0)}\right] =: L .
$$

Sohl-Dickstein and colleagues derived this bound for diffusion in 2015, from the same Jensen step. <!-- L13 --> Here $`q(x_{1:T}\mid x_0)`$ is the forward process run from the image, and $`p_\theta(x_{0:T})`$ is the reverse chain.

Figure 3's frozen encoder has one consequence that is easy to miss. In a VAE, the gap $`D_{\mathrm{KL}}(q\,\Vert\,p)`$ can shrink from either side, by improving the encoder or the decoder. In diffusion the encoder cannot move, so only the reverse model can close it — and it can only do so if a chain of Gaussian reverse steps can imitate the forward chain's true reversal, which is why those steps have to be small. Part 1 made that argument; the bound is where it becomes a number.

## How does the bound become one squared error per step?

The bound above is correct and useless: its log-ratio mixes every step with every other. Four exact moves turn it into a sum of per-step squared errors.

### Step 1: compare each reverse step with the teacher, not the forward step

Expand both chains into their factors. The log-ratio becomes a sum of terms $`\log p_\theta(x_{t-1}\mid x_t)/q(x_t\mid x_{t-1})`$, each comparing a reverse step with a forward step that points the other way. Each depends on two random states at once, so its Monte Carlo estimate is noisy, and there are $T - 1$ of them. <!-- L15 -->

The fix is Bayes' rule on the forward step. Because the forward chain is Markov, conditioning $`q(x_t\mid x_{t-1})`$ on $`x_0`$ as well changes nothing, and Bayes turns it around:

$$
q(x_t\mid x_{t-1}) = q(x_t\mid x_{t-1},x_0) = \frac{q(x_{t-1}\mid x_t,x_0)\;q(x_t\mid x_0)}{q(x_{t-1}\mid x_0)} .
$$

The ratios $`q(x_t\mid x_0)/q(x_{t-1}\mid x_0)`$ telescope along the chain and cancel, and what remains groups into three kinds of term: <!-- L03 -->

$$
L = \underbrace{D_{\mathrm{KL}}\big(q(x_T\mid x_0)\,\Vert\,p(x_T)\big)}_{L_T\ \text{prior matching}}
+ \sum_{t=2}^{T}\underbrace{D_{\mathrm{KL}}\big(q(x_{t-1}\mid x_t,x_0)\,\Vert\,p_\theta(x_{t-1}\mid x_t)\big)}_{L_{t-1}\ \text{denoising matching}}
\;\underbrace{-\,\log p_\theta(x_0\mid x_1)}_{L_0\ \text{reconstruction}}
$$

with every term averaged over the forward process. Each denoising-matching term is the teacher-versus-student KL from the worked example. The prior term asks whether the last forward state looks like the Gaussian that sampling starts from; it has no parameters, and under DDPM's schedule it is about $`10^{-5}`$ bits per dimension. <!-- L12 --> The reconstruction term is a decoder from $`x_1`$ to discrete pixel values. Figure 4 places the three on the chain.

![The chain from x-zero to x-T with three brackets: the prior term at the noise end, one denoising-matching term per intermediate step, and the reconstruction term at the image end, each marked with whether it touches the network](FIG_04)

*Figure 4. Only the middle bracket repeats, and only it trains the denoiser at every noise level. The prior term is a constant under a fixed schedule; the reconstruction term is one step out of a thousand.*

### Step 2: the teacher is a Gaussian with a formula

Each forward step multiplies by a constant and adds Gaussian noise, so every distribution involved is Gaussian, and so is the posterior. DDPM gives it in closed form: <!-- L04 -->

$$
q(x_{t-1}\mid x_t,x_0)=\mathcal N\!\big(\tilde\mu_t,\ \tilde\beta_t I\big),\qquad
\tilde\mu_t=\frac{\sqrt{\bar\alpha_{t-1}}\,\beta_t}{1-\bar\alpha_t}\,x_0+\frac{\sqrt{\alpha_t}\,(1-\bar\alpha_{t-1})}{1-\bar\alpha_t}\,x_t,\qquad
\tilde\beta_t=\frac{1-\bar\alpha_{t-1}}{1-\bar\alpha_t}\,\beta_t .
$$

The teacher's mean is a fixed blend of the clean image and the current noisy state, and its variance comes from the schedule alone. On the worked example both blend coefficients equal $`\sqrt{0.8}\times 0.2/0.36 = 0.4969`$, giving $`0.4969\times(0.95+0.43) = 0.6857`$ and $`\tilde\beta_t = 0.2/0.36\times 0.2 = 0.1111`$ — the same numbers the precision sum produced. On DDPM's real schedule at the same noise level, step 207, the coefficients are 0.0094 on $`x_0`$ and 0.9904 on $`x_t`$: a single fine step leans almost entirely on where the pixel already is. The derivation is in [the math section](#the-math).

### Step 3: equal variances turn the KL into a squared error

DDPM fixes the student's variance to a constant $`\sigma_t^2`$ and learns only its mean, $`p_\theta(x_{t-1}\mid x_t) = \mathcal N(\mu_\theta(x_t,t),\ \sigma_t^2 I)`$. The KL between the teacher and the student is then <!-- L05 -->

$$
L_{t-1} = \mathbb{E}_q\!\left[\frac{1}{2\sigma_t^2}\,\big\lVert\tilde\mu_t(x_t,x_0)-\mu_\theta(x_t,t)\big\rVert^2\right] + C ,
$$

where $C$ does not depend on the network. The step's loss is a squared error between two means, scaled by the student's variance. DDPM tried $`\sigma_t^2 = \beta_t`$ and $`\sigma_t^2 = \tilde\beta_t`$ and found similar results; the first is optimal if the data were standard Gaussian, the second if the data were a single fixed point. <!-- L06 --> With $`\sigma_t^2 = \tilde\beta_t`$ the worked example's $C$ is zero and the KL is 0.0250. With $`\sigma_t^2 = \beta_t = 0.20`$ the network-dependent part becomes 0.0139, and a constant of 0.0717 appears that no amount of training can remove.

### Step 4: write the mean through the noise

Rearrange the forward equation to $`x_0 = (x_t - \sqrt{1-\bar\alpha_t}\,\epsilon)/\sqrt{\bar\alpha_t}`$ and substitute it into $`\tilde\mu_t`$. The teacher's mean becomes a function of $`x_t`$ and the noise:

$$
\tilde\mu_t = \frac{1}{\sqrt{\alpha_t}}\left(x_t - \frac{\beta_t}{\sqrt{1-\bar\alpha_t}}\,\epsilon\right).
$$

The student has $`x_t`$ too, so give it the same form with a predicted noise $`\epsilon_\theta(x_t,t)`$ in place of $`\epsilon`$. Now the two means differ only through the noise estimate, and the step's loss becomes <!-- L07 -->

$$
L_{t-1} - C = \mathbb{E}_{x_0,\epsilon}\!\left[\frac{\beta_t^2}{2\sigma_t^2\,\alpha_t\,(1-\bar\alpha_t)}\,\big\lVert\epsilon-\epsilon_\theta\big(\sqrt{\bar\alpha_t}x_0+\sqrt{1-\bar\alpha_t}\epsilon,\ t\big)\big\rVert^2\right].
$$

That is the MSE, with a weight in front. On the worked example the weight is $`0.2^2/(2\times 0.1111\times 0.8\times 0.36) = 0.625`$, and $`0.625\times 0.20^2 = 0.0250`$: the fifth row of Figure 2. The DDPM authors noted that this form resembles denoising score matching over many noise scales, which is the thread the score section picks up. <!-- L07 -->

Nothing forced the noise. Writing the student's mean through a predicted clean image, or through a predicted score, gives the other rows of Figure 2 with their own constants; Luo's preprint works all three through and shows they are interchangeable parameterisations of one objective. <!-- L17 --> DDPM reported that predicting $`x_0`$ directly gave worse samples in its early experiments, a statement about optimisation with its architecture rather than about the objective. <!-- L08 -->

### Step 5: the weight is a difference of SNRs

Keep $`\sigma_t^2 = \tilde\beta_t`$ and write the error on the clean image instead of the noise. The weight collapses to something with a meaning: <!-- L19 -->

$$
L_{t-1} = \tfrac12\big(\mathrm{SNR}(t-1)-\mathrm{SNR}(t)\big)\,\mathbb{E}\big\lVert x_0-\hat x_0(x_t,t)\big\rVert^2,
\qquad \mathrm{SNR}(t)=\frac{\bar\alpha_t}{1-\bar\alpha_t}.
$$

A step's price is how much signal-to-noise ratio that step destroys, times how wrong the clean-image guess is. The worked example: $`\tfrac12(4 - 1.7778)\times 0.0225 = 0.0250`$. The **log-SNR**, $`\lambda = \log\mathrm{SNR}`$, is the natural clock for the rest of this post, because it is the only property of a noise level that the bound can see.

## Why does DDPM throw the weights away?

Setting every weight in step 4 to 1 and drawing $t$ uniformly gives $`L_{\text{simple}}`$, the loss from [the problem](#the-problem). The $`t = 1`$ term stands in for the decoder, and the prior term drops out because nothing in it is trained. <!-- L09 --> Figure 5 shows what was discarded, on DDPM's real schedule: $T = 1000$, $`\beta_t`$ rising linearly from $`10^{-4}`$ to 0.02, $`\sigma_t^2 = \beta_t`$. <!-- L12 -->

![Log-scale curve of the per-step ELBO weight across 1,000 DDPM steps: 0.27 at the second step, falling to a minimum of 0.005 near step 349, rising to 0.010 at the last step, beside a flat line at 1 for the simple loss](FIG_05)

*Figure 5. Computed from the published schedule, not measured. Inside the bound the second step is worth 55 times the cheapest one; the simple loss makes them equal, which in relative terms turns down the lowest-noise steps.*

The bound puts its largest per-step weights on the first few steps, where the image is almost clean; the first 100 of the 1,000 steps carry a third of its total weight. Improved DDPM found the same thing from the other side: the first few steps contribute the most to the bound's value. <!-- L41 --> DDPM's stated reason for dropping the weights is exactly this. Those steps teach the network to remove imperceptible noise, and down-weighting them lets it spend capacity on the harder, noisier steps. <!-- L09 -->

Why is it allowed to change the weights at all? The DDIM paper made the argument precise. The loss is a sum of one term per noise level, and if each noise level had its own separate network, the optimum of each term would not depend on its weight, so every weighting would train the same model. <!-- L48 --> Weights matter only because one network with finite capacity is shared across all levels. They decide which levels win when the network cannot be perfect everywhere — that is the whole content of a "loss weighting", and it is why choosing one is a training decision that part 5 of this series takes up.

So the price of dropping them is paid in likelihood, and it has been measured. Figure 6 puts two papers' CIFAR-10 numbers side by side.

![Two bar panels of CIFAR-10 results: negative log-likelihood in bits per dimension and FID for the true bound, the hybrid loss and the simple loss, from the DDPM and Improved DDPM papers with their setups labelled](FIG_06)

*Figure 6. Measured, from two papers with different setups — do not compare across the groups. Within each group the ordering is the same: the bound wins on likelihood and loses on FID.*

In DDPM, the bound with fixed variances reached 3.70 bits per dimension and FID 13.51; the simple loss reached 3.75 and FID 3.17 — unconditional CIFAR-10, FID measured against the training set. <!-- L10 --> Its ablation adds the mechanism: predicting the teacher's mean directly only worked when trained on the true bound, while predicting the noise beat it by a wide margin only under the simple loss. <!-- L11 --> Improved DDPM, at 500K iterations with 4,000 steps and a cosine schedule, measured 2.94 bits and FID 11.47 for the bound, 3.26 and 3.05 for the simple loss. <!-- L42 -->

It also found why the bound is hard to train on directly: its terms differ greatly in size, so sampling $t$ uniformly gives very noisy gradients. Importance-sampling $t$ in proportion to the root-mean-square size of each term made the bound trainable. <!-- L40 --> Its compromise, the hybrid loss, adds the bound back at a weight of 0.001 so that it can steer learned variances while the simple loss drives the mean. <!-- L39 --> That hybrid sits between the other two in Figure 6, which is what a compromise should do.

## Is every diffusion loss the same loss?

Step 5 already points at the answer. Take the SNR form into continuous time, where the noise level is the log-SNR $\lambda$ and the steps become infinitely fine. Two facts make the change of variable short: the clean-image error and the noise error are related by $`\lVert x_0-\hat x_0\rVert^2 = \lVert\epsilon-\hat\epsilon\rVert^2/\mathrm{SNR}`$, and $`d\,\mathrm{SNR} = \mathrm{SNR}\,d\lambda`$. Substituting both,

$$
\tfrac12\int \mathbb{E}\lVert x_0-\hat x_0\rVert^2\,d\,\mathrm{SNR}
\;=\; \tfrac12\int \mathbb{E}\lVert \epsilon-\hat\epsilon\rVert^2\,d\lambda .
$$

In log-SNR coordinates, the continuous-time ELBO weights the noise error *uniformly*. Every other loss in the literature can be written the same way with a weighting function $`w(\lambda)`$ in the integrand; Kingma and Gao tabulate them. <!-- L24 --> The **weighting function** is how much a loss cares about the noise error at each log-SNR, and it is the one thing that distinguishes them:

| Loss | $`w(\lambda)`$ | Monotonic? |
|---|---|---|
| ELBO | 1 | yes |
| ε-prediction, cosine schedule | $`\operatorname{sech}(\lambda/2)`$ | no |
| v-prediction, cosine schedule | $`e^{-\lambda/2}`$ | yes |
| EDM | $`\mathcal N(\lambda;\,2.4,\,2.4^2)\,(e^{-\lambda}+0.25)`$ | no |
| Flow matching, optimal-transport path | $`e^{-\lambda/2}`$ | yes |
| Min-SNR-γ | $`\operatorname{sech}(\lambda/2)\,\min(1,\ \gamma e^{-\lambda})`$ | no |

<!-- L24 --> <!-- L28 -->

Two entries need unpacking. Plain ε-prediction with $t$ drawn uniformly has $`w(\lambda) = p(\lambda)`$, the density of noise levels the schedule visits; the cosine schedule's density is the sech. <!-- L25 --> **v-prediction** trains on $`v = \sqrt{\bar\alpha_t}\,\epsilon - \sqrt{1-\bar\alpha_t}\,x_0`$, and its squared error is $`(1+\mathrm{SNR})\lVert x_0-\hat x_0\rVert^2`$, so it multiplies the ε-loss by $`1/\bar\alpha_t`$ — the 0.64 in Figure 2. <!-- L47 --> Min-SNR uses $`\gamma = 5`$ by default. <!-- L51 --> Figure 7 plots the table.

![Weighting curves over log signal-to-noise ratio for the ELBO, epsilon and velocity prediction with the cosine schedule, EDM and Min-SNR, with the worked example's noise level and DDPM's range marked](FIG_07)

*Figure 7. Curves evaluated from the published weighting formulas, each scaled to 1 at SNR = 1 on a log axis; not measured. The ELBO is flat. v-prediction keeps climbing toward pure noise, the cosine ε-loss falls away on both sides, and Min-SNR cuts off the clean end hardest.*

Scaled to 1 at SNR = 1, the cosine ε-loss weighs the worked example's noise level, $`\lambda = \log 1.7778 = 0.575`$, at 0.96, and the v-loss at $`e^{-0.2877} = 0.75`$ — the same 0.75 that [part 1's error multiplier](https://canery.in/blogs/what-a-diffusion-model-actually-does#why-does-one-call-blur-and-many-calls-draw) printed at this level, since both are $`1/\sqrt{\mathrm{SNR}}`$.

This framing settles three questions that otherwise get argued by folklore.

**What does the schedule do?** Once the weighting $`w(\lambda)`$ is fixed, nothing to the objective between its endpoints. The integral over $\lambda$ does not care how fast the schedule moves through the noise levels, only which levels it covers and how the loss weights them. <!-- L26 --> Plain ε-prediction is the one place this bites, because there the weight *is* the schedule's density — switching from the linear to the cosine schedule changes the weighting along with it. What the schedule does change is the *variance* of the training estimate, because it decides how often each level is sampled: it acts as an importance-sampling distribution. The VDM paper measured this directly. Rescaled to identical endpoints, the linear, cosine and learned schedules all gave the same bound, 2.66 bits per dimension, but the estimate's variance was 31.6 for linear, 31.1 for cosine and 0.53 for their learned schedule. <!-- L23 -->

**Which losses are still likelihoods?** If the weight grows monotonically as noise increases, the weighted loss equals the ELBO of the data *after* augmenting it with Gaussian noise — a likelihood bound on a slightly blurred copy of the dataset. <!-- L27 --> In the table, the ELBO, v-prediction with the cosine schedule and optimal-transport flow matching have that property; the popular cosine ε-loss, EDM and Min-SNR do not. <!-- L28 -->

**Does the target matter?** Not to what the loss is minimised by, as the worked example showed. It matters through the implied weight, and through numerical conditioning: a network asked for ε near zero noise must output a signal it can barely see, and one asked for $`x_0`$ near pure noise must output an image it cannot see at all. That is an optimisation property, not a different objective.

## Where does the score come from?

The **score** of a distribution is the gradient of its log-density, $`\nabla_x \log p(x)`$ — a vector field pointing toward where data is denser. Two different scores sit inside a diffusion model, and keeping them apart is most of this section:

- the **conditional score** $`\nabla_{x_t}\log q(x_t\mid x_0) = -\epsilon/\sqrt{1-\bar\alpha_t}`$, which we know exactly for each training example because we drew $\epsilon$; and
- the **marginal score** $`\nabla_{x_t}\log q(x_t)`$ of the noised data distribution, which nobody knows and which a sampler needs.

### Tweedie: the ideal denoiser and the marginal score are one function

Differentiate $`q(x_t) = \int q(x_t\mid x_0)\,q(x_0)\,dx_0`$ under the integral. The derivative of the Gaussian kernel pulls down $`(\sqrt{\bar\alpha_t}x_0 - x_t)/(1-\bar\alpha_t)`$, and dividing by $`q(x_t)`$ turns the integral over $`x_0`$ into a posterior average:

$$
\sqrt{\bar\alpha_t}\;\mathbb{E}[x_0\mid x_t] \;=\; x_t + (1-\bar\alpha_t)\,\nabla_{x_t}\log q(x_t).
$$

This is **Tweedie's formula**: the posterior mean of something observed through Gaussian noise is the observation plus the noise variance times the score of what was observed. <!-- L46 --> The EDM paper writes the same statement as $`\nabla\log p(x;\sigma) = (D(x;\sigma) - x)/\sigma^2`$, with $D$ the ideal denoiser. <!-- L43 --> In noise units it says the best possible noise prediction is $`\mathbb{E}[\epsilon\mid x_t] = -\sqrt{1-\bar\alpha_t}\,\nabla\log q(x_t)`$. A perfectly trained ε-network is a score network, rescaled.

For a finite training set the ideal denoiser has a closed form: a softmax-weighted average of the training points, weighted by how likely each was to produce $`x_t`$. <!-- L45 --> Figure 8 draws it for a three-value "dataset" — the three grey levels of the crescent motif, −0.85, 0.10 and 0.95 — at the worked noise level.

![Three data values with bars for their posterior weights and the weighted average between them; below, the noisy value 0.43 with an arrow to the scaled average, and the score curve marked at that value](FIG_08)

*Figure 8. At x_t = 0.43 the weights are 0.10, 0.45 and 0.46, so the ideal denoiser answers 0.40 — not any of the three levels. The score is the arrow from x_t to 0.8 × 0.40, divided by the noise variance: −0.313.*

The ideal answer, 0.40, is not the pixel's true value and does not need to be. It is right on average over every clean value that could have produced 0.43, which is all a squared-error loss can ask of it.

### Denoising score matching: noisy targets, exact answer

Suppose you want a network $`s_\theta`$ to approximate the marginal score directly. The obvious loss, $`\mathbb{E}\lVert s_\theta(x_t) - \nabla\log q(x_t)\rVert^2`$, needs the target it is trying to learn. Hyvärinen's **score matching** removed the target by integration by parts, leaving an objective with no normalising constant and no true score in it, at the price of a Jacobian trace. <!-- L33 --> Vincent then showed a cheaper route: regress onto the *conditional* score of the corruption kernel instead. This **denoising score matching (DSM)** objective equals explicit score matching against the noised density up to a constant, for any differentiable corruption kernel. <!-- L32 -->

The reason is one line. The conditional score, averaged over the clean images that could have produced $`x_t`$, *is* the marginal score — the same differentiation as Tweedie's formula. A squared-error regression converges to the conditional mean of its target, so a network regressed onto the noisy per-example target converges to the marginal score. The proof is in [the math section](#the-math). Figure 9 shows it happening.

![Scatter of six hundred per-sample targets falling on three straight lines, one per clean value, with binned averages of those targets lying on the exact score curve between them](FIG_09)

*Figure 9. Simulated from the lab script, not measured on a real model. Each clean level produces its own straight line of targets, so no dot sits on the score; their average in each bin does, within 0.12 at 6,000 samples and 0.07 at 60,000.*

Now put in the Gaussian kernel. With conditional score $`-\epsilon/\sqrt{1-\bar\alpha_t}`$ and a weight of $`1-\bar\alpha_t`$ on each noise level,

$$
(1-\bar\alpha_t)\,\Big\lVert s_\theta(x_t,t)+\frac{\epsilon}{\sqrt{1-\bar\alpha_t}}\Big\rVert^2
= \big\lVert \epsilon - \epsilon_\theta(x_t,t)\big\rVert^2,
\qquad \epsilon_\theta = -\sqrt{1-\bar\alpha_t}\;s_\theta .
$$

Weighted denoising score matching *is* the noise-prediction loss. <!-- L25 --> This is the third row of Figure 2: the score error of 0.3333, squared and multiplied by 0.36, is the 0.04.

That weight has a history. The **noise-conditional score network (NCSN)** of Song and Ermon trained one network on denoising score matching at every noise level, and weighted level $\sigma$ by $`\lambda(\sigma) = \sigma^2`$ because trained score norms scale like $`1/\sigma`$ and the weight evens out the terms. <!-- L29 --> DDPM arrived at the same unweighted ε-loss by deleting the bound's weights, and its authors say so. <!-- L09 --> One group reached $`L_{\text{simple}}`$ by balancing magnitudes, the other by simplifying a likelihood bound.

One precision point that the tutorial literature sometimes blurs. The network learns the score of the *noised* data at each level, which approaches the data's own score only as the noise goes to zero. <!-- L31 --> Luo's preprint writes the marginal score in steps where only the conditional score holds exactly; the two agree in expectation, which is the DSM argument above, but not example by example.

## How are DDPM, NCSN and the SDE one object?

The standard surveys present diffusion as three formulations: denoising diffusion probabilistic models, noise-conditional score networks, and stochastic differential equations. <!-- L54 --> Figure 10 draws them as one object seen from different sides, with the conversion written on every edge.

![A graph of the discrete DDPM and NCSN chains and the continuous VP and VE SDEs, joined by rescaling and limit edges, all feeding one shared network whose loss splits into ELBO, simple-loss and DSM weightings](FIG_10)

*Figure 10. Every edge is a rescaling of x, a limit of infinitely many steps, a fixed conversion between outputs, or a choice of weight. None of them changes what the network is asked to learn at a given signal-to-noise ratio.*

### One corruption family, two coordinate systems

DDPM corrupts with $`x_t = \sqrt{\bar\alpha_t}\,x_0 + \sqrt{1-\bar\alpha_t}\,\epsilon`$. The signal shrinks while noise grows, and the total variance stays near 1 for unit-variance data: a **variance-preserving (VP)** process. NCSN corrupts with $`\tilde x = x_0 + \sigma\epsilon`$. The signal stays put while noise grows without bound: a **variance-exploding (VE)** process.

Divide the VP sample by $`\sqrt{\bar\alpha_t}`$:

$$
\frac{x_t}{\sqrt{\bar\alpha_t}} = x_0 + \sqrt{\frac{1-\bar\alpha_t}{\bar\alpha_t}}\;\epsilon = x_0 + \frac{1}{\sqrt{\mathrm{SNR}}}\;\epsilon .
$$

That is a VE sample at $`\sigma = 1/\sqrt{\mathrm{SNR}}`$. The two processes contain the same information at every noise level; they differ by a known scale. On the worked pixel at $`\bar\alpha_t = 0.64`$, the VE noise level is $\sigma = 0.75$ and the VE value is $0.43/0.8 = 0.5375$. The VDM paper proves the general version: in continuous time, VP and VE diffusions with the same SNR endpoints define the same model, up to this rescaling of the latents. <!-- L21 --> The EDM paper builds its whole design space on the same observation, with every VP, VE and iDDPM model trained with a $`1/\sigma^2`$ weight on its denoiser loss. <!-- L44 --> Figure 11 follows one pixel through both.

(Recent papers write the signal and noise coefficients as $`\alpha_t`$ and $`\sigma_t`$. In this series $`\alpha_t`$ is already the per-step factor $`1-\beta_t`$, so the coefficients stay $`\sqrt{\bar\alpha_t}`$ and $`\sqrt{1-\bar\alpha_t}`$ throughout.)

![Two trajectories of the top-left pixel against log signal-to-noise ratio: the VE value explodes past minus three as noise grows while the VP value stays within one, and the rescaled VE curve lies exactly on the VP curve](FIG_11)

*Figure 11. Same pixel, same noise draw, computed. Multiplying the VE path by the signal coefficient lands it exactly on the VP path at every level; at the marked worked level the two read 0.5375 and 0.43.*

The scale difference is not free in practice. A network fed VE inputs sees values up to $\sigma_{\max}$ in size, which is why EDM scales inputs by $`1/\sqrt{\sigma^2+\sigma_{\text{data}}^2}`$ before the network. <!-- L44 --> That is a conditioning decision for part 5, not a different objective.

### The continuous-time limit

Let the number of noise levels go to infinity. NCSN's chain, which adds fresh noise of variance $`\sigma_i^2 - \sigma_{i-1}^2`$ at each level, becomes the VE stochastic differential equation $`dx = \sqrt{d[\sigma^2(t)]/dt}\;dw`$. DDPM's chain becomes the VP one, $`dx = -\tfrac12\beta(t)\,x\,dt + \sqrt{\beta(t)}\,dw`$, where $w$ is Brownian motion. <!-- L36 --> A **stochastic differential equation (SDE)** here is the continuous-time description of a noising process: a deterministic drift plus infinitesimal Gaussian kicks. The survey literature states the same thing plainly: both discrete forward processes are discretisations of one SDE. <!-- L53 -->

Reversing an SDE needs exactly one learned quantity. The reverse of a diffusion process is again a diffusion, whose drift is corrected by the squared noise strength $`g(t)^2`$ times the marginal score — a 1982 result by Anderson that the score-SDE paper builds on. <!-- L34 --> Its training objective is denoising score matching integrated over time with a positive weight $`\lambda(t)`$. <!-- L35 --> Integrating that reverse equation, or its deterministic probability-flow twin, is numerical analysis, and it belongs to part 6.

The likelihood story survives the limit. With the weight $`\lambda(t) = g(t)^2`$, the score-matching loss becomes an upper bound on the negative log-likelihood; for the VE SDE this happens to coincide with the weight the score-SDE paper already used, for VP it does not. <!-- L37 --> A companion analysis showed that minimising the score-matching loss maximises a lower bound on the likelihood of the plug-in reverse SDE, which can be read as an infinitely deep VAE. <!-- L38 --> VDM gives the cleanest statement: as the step count grows, the diffusion part of the bound becomes $`\tfrac12\int\mathbb{E}\lVert x_0-\hat x_0\rVert^2\,d\,\mathrm{SNR}`$, which depends on the schedule only through its two endpoint SNRs. <!-- L21 -->

It also says which direction the limit goes. The discrete loss is an upper Riemann sum of that integral, and the integrand decreases as SNR rises, so adding steps can only lower the bound when the denoiser is good enough. <!-- L20 --> Figure 12 shows the measured version.

![Bits per dimension on the CIFAR-10 test set falling as the number of diffusion steps grows from 10 to 10,000, levelling toward the continuous-time value of 2.65](FIG_12)

*Figure 12. Measured by the VDM paper on CIFAR-10, training and evaluating with the same step count. Ten steps cost 4.31 bits per dimension; a thousand cost 2.67; continuous time costs 2.65.*

<!-- L22 --> The curve is steep and then flat: most of the bound's looseness is gone by a few hundred steps. With the ideal denoiser in place of a trained one, the integrand is exactly the minimum mean-square error at each SNR, and the integral stops being a bound. The derivative of mutual information with respect to SNR in a Gaussian channel is half the minimum mean-square error — a 2005 information-theory identity <!-- L49 --> — and Kong and colleagues used it to show that, with the optimal denoiser, half the integral of the pointwise error equals the negative log-likelihood plus constants, exactly. <!-- L50 -->

Put the pieces together and the three formulations reduce to a short list of choices:

| Formulation | Corruption | Network output | Weight on the ε-error | Sampler |
|---|---|---|---|---|
| DDPM | VP, 1,000 discrete steps | noise ε | 1 per step, uniform t | ancestral |
| NCSN | VE, 10 discrete levels | score | $`\sigma^2`$ on the score error, which is 1 on ε | annealed Langevin |
| Score SDE | VP or VE, continuous | score | $`\lambda(t)`$; $`g(t)^2`$ for a likelihood bound | reverse SDE or ODE |
| VDM | VP, continuous, learned schedule | noise (via $`\hat x_0`$) | uniform in $\lambda$ — the ELBO | ancestral |
| EDM | VE with input scaling | clean image $D$ | its $`\lambda(\sigma)`$ | Heun ODE/SDE |

NCSN's CIFAR-10 ladder, for the record, is 10 levels in geometric progression from $`\sigma = 1`$ to 0.01 on pixels in [0, 1], <!-- L30 --> and VDM samples ancestrally from its learned reverse step. <!-- L56 --> Every row learns the same function of the same noisy input, up to a known rescaling of its output. The rows differ in which noise levels they practise on and how they sample, which is why they are one object and not three.

## The math

The body derived every step; this section keeps the three derivations it skipped and the conversions between targets. Symbols not defined here are the series' standard ones: $`x_0`$, $`x_t`$, $\epsilon$, $`\beta_t`$, $`\alpha_t = 1-\beta_t`$, $`\bar\alpha_t = \prod_{s\le t}\alpha_s`$.

| Symbol | Meaning | Range |
|---|---|---|
| $`\tilde\mu_t,\ \tilde\beta_t`$ | mean and variance of the forward posterior $`q(x_{t-1}\mid x_t,x_0)`$ | data shape; $(0,\beta_t]$ |
| $`\sigma_t^2`$ | fixed variance of the learned reverse step | $`\tilde\beta_t`$ or $`\beta_t`$ |
| $`\mathrm{SNR}(t)`$ | $`\bar\alpha_t/(1-\bar\alpha_t)`$ | $(0,\infty)$, decreasing in $t$ |
| $\lambda$ | $`\log\mathrm{SNR}`$ | $`(-\infty,\infty)`$ |
| $`w(\lambda)`$ | weight a loss puts on the noise error at log-SNR $\lambda$ | $\ge 0$ |
| $`s_\theta`$ | score network output | data shape |
| $v$ | velocity target $`\sqrt{\bar\alpha_t}\,\epsilon-\sqrt{1-\bar\alpha_t}\,x_0`$ | data shape |

Once $`x_t`$ and the schedule are known, any one prediction fixes the others:

| From | $`\hat x_0`$ | $`\hat\epsilon`$ | $`\hat s`$ |
|---|---|---|---|
| $`\hat\epsilon`$ | $`(x_t-\sqrt{1-\bar\alpha_t}\,\hat\epsilon)/\sqrt{\bar\alpha_t}`$ | — | $`-\hat\epsilon/\sqrt{1-\bar\alpha_t}`$ |
| $`\hat v`$ | $`\sqrt{\bar\alpha_t}\,x_t-\sqrt{1-\bar\alpha_t}\,\hat v`$ | $`\sqrt{1-\bar\alpha_t}\,x_t+\sqrt{\bar\alpha_t}\,\hat v`$ | via $`\hat\epsilon`$ |

<details>
<summary>The forward posterior, by completing the square</summary>

By Bayes, $`q(x_{t-1}\mid x_t,x_0)\propto q(x_t\mid x_{t-1})\,q(x_{t-1}\mid x_0)`$. Both factors are Gaussian in $`x_{t-1}`$:

$$
q(x_t\mid x_{t-1}) \propto \exp\!\Big(-\frac{(x_t-\sqrt{\alpha_t}x_{t-1})^2}{2\beta_t}\Big),\qquad
q(x_{t-1}\mid x_0) \propto \exp\!\Big(-\frac{(x_{t-1}-\sqrt{\bar\alpha_{t-1}}x_0)^2}{2(1-\bar\alpha_{t-1})}\Big).
$$

The first, read as a function of $`x_{t-1}`$, has precision $`\alpha_t/\beta_t`$ and mean $`x_t/\sqrt{\alpha_t}`$; the second has precision $`1/(1-\bar\alpha_{t-1})`$. Precisions add:

$$
\frac{1}{\tilde\beta_t}=\frac{\alpha_t}{\beta_t}+\frac{1}{1-\bar\alpha_{t-1}}=\frac{\alpha_t(1-\bar\alpha_{t-1})+\beta_t}{\beta_t(1-\bar\alpha_{t-1})}=\frac{1-\bar\alpha_t}{\beta_t(1-\bar\alpha_{t-1})},
$$

using $`\alpha_t-\alpha_t\bar\alpha_{t-1}+1-\alpha_t = 1-\bar\alpha_t`$. The mean is the precision-weighted average, $`\tilde\mu_t = \tilde\beta_t\big(\sqrt{\alpha_t}\,x_t/\beta_t+\sqrt{\bar\alpha_{t-1}}\,x_0/(1-\bar\alpha_{t-1})\big)`$, which expands to the two coefficients in step 2. On the coarse chain the precisions are $0.8/0.2 = 4$ and $1/0.2 = 5$ — the worked example's 4 and 5.

</details>

<details>
<summary>The KL between two Gaussians, and where the constant comes from</summary>

For $d$-dimensional Gaussians with isotropic covariances,

$$
D_{\mathrm{KL}}\big(\mathcal N(\mu_1,v_1I)\,\Vert\,\mathcal N(\mu_2,v_2I)\big)=\frac d2\Big(\log\frac{v_2}{v_1}+\frac{v_1}{v_2}-1\Big)+\frac{\lVert\mu_1-\mu_2\rVert^2}{2v_2}.
$$

Only the last term involves the means. With $`v_1=\tilde\beta_t`$ fixed by the schedule and $`v_2=\sigma_t^2`$ fixed by choice, the bracket is the constant $C$, and it vanishes exactly when $`\sigma_t^2=\tilde\beta_t`$. For the worked pixel with $`\sigma_t^2=0.2`$: $`\tfrac12(\log 1.8+0.5556-1)=0.0717`$, and the mean term is $`0.005556/0.4=0.0139`$.

</details>

<details>
<summary>Why denoising score matching equals explicit score matching</summary>

Expand the explicit objective and drop the term that does not involve $\theta$:

$$
\mathbb{E}_{q(\tilde x)}\lVert s_\theta(\tilde x)-\nabla\log q(\tilde x)\rVert^2 = \mathbb{E}\lVert s_\theta\rVert^2-2\,\mathbb{E}_{q(\tilde x)}\big[s_\theta(\tilde x)^\top\nabla\log q(\tilde x)\big]+C_1 .
$$

The cross term is the only one that needs the unknown score. Write $`q(\tilde x)\nabla\log q(\tilde x)=\nabla q(\tilde x)=\int q(x)\,\nabla_{\tilde x}q(\tilde x\mid x)\,dx`$, so

$$
\mathbb{E}_{q(\tilde x)}\big[s_\theta^\top\nabla\log q(\tilde x)\big]=\mathbb{E}_{q(x,\tilde x)}\big[s_\theta(\tilde x)^\top\nabla_{\tilde x}\log q(\tilde x\mid x)\big].
$$

Substituting back gives $`\mathbb{E}_{q(x,\tilde x)}\lVert s_\theta(\tilde x)-\nabla_{\tilde x}\log q(\tilde x\mid x)\rVert^2`$ plus a different constant. Nothing in the argument used the kernel's form beyond differentiability, which is Vincent's condition.

</details>

The ε-weight in step 4 turns into the SNR form of step 5 with two substitutions. With $`\sigma_t^2=\tilde\beta_t`$, the weight on the noise error is $`\beta_t/(2\alpha_t(1-\bar\alpha_{t-1}))`$, and the squared noise error is $`\mathrm{SNR}(t)`$ times the squared clean-image error. So the weight on the clean-image error is their product, which simplifies to $`\tfrac12\big(\mathrm{SNR}(t-1)-\mathrm{SNR}(t)\big)`$ using $`\bar\alpha_{t-1}=\bar\alpha_t/\alpha_t`$. On the coarse chain that is $`\tfrac12(4-1.7778)=1.1111`$ on the clean-image error, or $`1.1111/1.7778=0.625`$ on the noise error.

## Implementation

The core of the lab script, standard-library Python, reproduces the worked example's KL three ways and the weight curve of Figure 5. It runs in under a second and asserts every identity it prints.

```python
import math

def gauss_kl(m1, v1, m2, v2):
    """KL( N(m1, v1) || N(m2, v2) ) for scalars, in nats."""
    return 0.5 * (math.log(v2 / v1) + (v1 + (m1 - m2) ** 2) / v2 - 1.0)

def snr(abar):
    return abar / (1.0 - abar)

abar_s, abar_t = 0.80, 0.64                              # one step of the coarse chain
alpha = abar_t / abar_s; beta = 1 - alpha                 # 0.80, 0.20
x0, eps, eps_hat = 0.95, -0.55, -0.35
xt = math.sqrt(abar_t) * x0 + math.sqrt(1 - abar_t) * eps  # 0.43

c_x0 = math.sqrt(abar_s) * beta / (1 - abar_t)             # DDPM eq. 7
c_xt = math.sqrt(alpha) * (1 - abar_s) / (1 - abar_t)
var = (1 - abar_s) / (1 - abar_t) * beta                   # beta_tilde = 1/9

x0_hat = (xt - math.sqrt(1 - abar_t) * eps_hat) / math.sqrt(abar_t)   # 0.80
teacher = c_x0 * x0 + c_xt * xt                            # 0.6857
student = c_x0 * x0_hat + c_xt * xt                        # 0.6112

kl = gauss_kl(teacher, var, student, var)                          # Gaussian KL
kl_eps = beta**2 / (2 * var * alpha * (1 - abar_t)) * (eps_hat - eps) ** 2   # eps form
kl_snr = 0.5 * (snr(abar_s) - snr(abar_t)) * (x0_hat - x0) ** 2            # SNR form
print(f"{kl:.4f} {kl_eps:.4f} {kl_snr:.4f}")               # 0.0250 0.0250 0.0250
```

The three numbers agree because they are the same quantity: the Gaussian KL, the ε-weighted MSE, and the SNR-weighted clean-image error. The weight curve is one loop over DDPM's schedule:

```python
def elbo_weights(T=1000):
    """Per-step weight on ||eps - eps_hat||^2 inside the bound, sigma_t^2 = beta_t."""
    betas = [1e-4 + (0.02 - 1e-4) * i / (T - 1) for i in range(T)]
    abar, p = [], 1.0
    for b in betas:
        p *= 1 - b
        abar.append(p)
    return {t: betas[t-1] / (2 * (1 - betas[t-1]) * (1 - abar[t-1]))
            for t in range(2, T + 1)}

w = elbo_weights()
print(round(w[2], 4), round(min(w.values()), 5), round(w[1000], 4))   # 0.2727 0.00497 0.0102
```

With $`\sigma_t^2=\beta_t`$ the step-4 weight simplifies to $`\beta_t/(2\alpha_t(1-\bar\alpha_t))`$, which is what the dictionary holds. The full script adds the Tweedie and denoising-score-matching checks behind Figures 8 and 9, the VP/VE rescaling behind Figure 11, and a Gaussian-data version of the step-count argument behind Figure 12. It is in [Lab downloads](#lab-downloads).

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** reporting $`L_{\text{simple}}`$ as a log-likelihood. It is the bound with its per-step weights replaced by 1, so its value is neither a bound nor bits per dimension. To report likelihood you evaluate the true bound — per-step weights, prior term, discrete decoder — on held-out data. DDPM's simple-loss model scores worse on that bound than its bound-trained model, 3.75 against 3.70 bits per dimension on CIFAR-10. <!-- L10 -->

- **"ε-, x₀-, v- and score-prediction are different objectives."** At a fixed noise level they share one minimiser; Figure 2 is the proof on numbers. They differ in the implied weight over noise levels and in how well-conditioned the regression is near each end of the schedule. If you switch targets, you have changed the weighting whether you meant to or not.
- **"Training on the true bound gives the best samples."** Measured, it gives the best likelihood and worse samples: 2.94 bits and FID 11.47 against 3.26 bits and FID 3.05 for the simple loss in one CIFAR-10 setup. <!-- L42 --> Its heaviest per-step weights sit on imperceptible detail.
- **"The prior term is zero."** It is small, not zero. DDPM's schedule leaves it near $`10^{-5}`$ bits per dimension, <!-- L12 --> and common schedules leave a nonzero terminal signal-to-noise ratio, so the last training input still carries signal that the Gaussian a sampler starts from does not. <!-- L52 --> Fixing that is a schedule decision for part 5.
- **"The network learns the data's score."** It learns the score of the data *noised to each level*. The two agree only as noise goes to zero, <!-- L31 --> and exactly there the DSM target $`-\epsilon/\sqrt{1-\bar\alpha_t}`$ has variance $`1/(1-\bar\alpha_t)`$ per dimension, which diverges. That is why score losses multiply the score error by the noise variance: it turns the diverging target back into the unit-variance noise target.
- **"The bound is tight if the network is good."** The gap is $`D_{\mathrm{KL}}\big(q(x_{1:T}\mid x_0)\,\Vert\,p_\theta(x_{1:T}\mid x_0)\big)`$. With the encoder frozen, only the reverse chain can close it, and a chain of Gaussian steps can match the true reversal only when the steps are small — the reason Figure 12 is still falling at a few hundred steps.

## Key takeaways

- The MSE loss is the diffusion ELBO with its per-step weights set to 1. Every step before that choice — Jensen's inequality, Bayes on the forward step, the Gaussian KL, writing the mean through the noise — is exact.
- Each term of the bound is a KL between the forward posterior and the learned step. Both are Gaussians of the same variance, so the KL is a squared distance between means, weighted by $`\tfrac12\Delta\mathrm{SNR}`$ on the clean-image error.
- At a single noise level, ε-, x₀-, v- and score-prediction are proportional losses with the same minimiser. Every published diffusion loss is one integral over log-SNR; only the weighting function differs, and once that weighting is fixed the schedule changes the estimator's variance, not the objective.
- Dropping the weights trades likelihood for sample quality, measurably: better FID, worse bits per dimension, in both DDPM and Improved DDPM.
- By Tweedie's formula the ideal denoiser is a score estimator, and denoising score matching with weight $`1-\bar\alpha_t`$ is exactly the noise-prediction loss. DDPM is the VP discretisation, NCSN the VE one, and the score SDE is their shared continuous limit.

## Try it yourself

1. Redo the worked example's KL with the student's variance set to $`\sigma_t^2 = \beta_t = 0.20`$ instead of $`\tilde\beta_t`$. How much of the answer can training reduce?

<details><summary>Answer</summary>

The full KL is $`\tfrac12\big(\log(0.2/0.1111)+0.1111/0.2-1\big)+0.0745^2/(2\times0.2) = 0.0717+0.0139 = 0.0856`$ nats. Only the 0.0139 depends on the network's mean; the 0.0717 is fixed by the variance mismatch. That is DDPM's constant $C$, made concrete.

</details>

2. At what noise level do the ε-loss and the x₀-loss put the same weight on an error, and what is $`\bar\alpha_t`$ there?

<details><summary>Answer</summary>

The x₀-error is the ε-error divided by SNR, so the two weights agree where $`\mathrm{SNR}=1`$: $`\lambda = 0`$, $`\bar\alpha_t = 0.5`$. Noisier than that, an x₀-loss counts the same prediction error as larger than the ε-loss does; cleaner than that, smaller.

</details>

3. For Figure 8's three-level dataset at $`\bar\alpha_t = 0.64`$ and $`x_t = 1.00`$, the posterior weights are 0.016, 0.247 and 0.738. What noise does the ideal ε-network predict, and what is the score?

<details><summary>Answer</summary>

$`\mathbb{E}[x_0\mid x_t] = 0.016(-0.85)+0.247(0.10)+0.738(0.95) = 0.712`$. The ideal noise estimate is $`(1.00-0.8\times0.712)/0.6 = 0.717`$, and the score is $`-0.717/0.6 = -1.196`$ — which is also $`(0.8\times0.712-1.00)/0.36`$ by Tweedie's formula.

</details>

## References

### Lab downloads

- [`loss_identities.py`](LAB_01) — standard-library Python that recomputes every identity in this post on its own numbers and asserts each one: the worked KL three ways, the five prices, DDPM's per-step weights, Tweedie and denoising score matching on the three-level dataset, the VP/VE rescaling, and the step-count argument on Gaussian data.

### Sources

1. Ho, J., Jain, A. & Abbeel, P. *Denoising Diffusion Probabilistic Models*. NeurIPS 33, 2020. arXiv:2006.11239. [https://proceedings.neurips.cc/paper/2020/hash/4c5bcfec8584af0d967f1ab10179ca4b-Abstract.html](https://proceedings.neurips.cc/paper/2020/hash/4c5bcfec8584af0d967f1ab10179ca4b-Abstract.html) (accessed 2026-09-25)
2. Sohl-Dickstein, J., Weiss, E., Maheswaranathan, N. & Ganguli, S. *Deep Unsupervised Learning using Nonequilibrium Thermodynamics*. ICML (PMLR v37), 2015. [https://proceedings.mlr.press/v37/sohl-dickstein15.html](https://proceedings.mlr.press/v37/sohl-dickstein15.html) (accessed 2026-09-25)
3. Luo, C. *Understanding Diffusion Models: A Unified Perspective*. Preprint, arXiv:2208.11970, 2022. [https://arxiv.org/abs/2208.11970](https://arxiv.org/abs/2208.11970) (accessed 2026-09-25)
4. Kingma, D. P., Salimans, T., Poole, B. & Ho, J. *Variational Diffusion Models*. NeurIPS 34, 2021. arXiv:2107.00630. [https://proceedings.neurips.cc/paper_files/paper/2021/hash/b578f2a52a0229873fefc2a4b06377fa-Abstract.html](https://proceedings.neurips.cc/paper_files/paper/2021/hash/b578f2a52a0229873fefc2a4b06377fa-Abstract.html) (accessed 2026-09-25)
5. Kingma, D. P. & Gao, R. *Understanding Diffusion Objectives as the ELBO with Simple Data Augmentation*. NeurIPS 36, 2023, pp. 65484–65516. DOI 10.52202/075280-2858. [https://proceedings.neurips.cc/paper_files/paper/2023/hash/ce79fbf9baef726645bc2337abb0ade2-Abstract-Conference.html](https://proceedings.neurips.cc/paper_files/paper/2023/hash/ce79fbf9baef726645bc2337abb0ade2-Abstract-Conference.html) (accessed 2026-09-25)
6. Song, Y. & Ermon, S. *Generative Modeling by Estimating Gradients of the Data Distribution*. NeurIPS 32, 2019. arXiv:1907.05600. [https://proceedings.neurips.cc/paper/2019/hash/3001ef257407d5a371a96dcd947c7d93-Abstract.html](https://proceedings.neurips.cc/paper/2019/hash/3001ef257407d5a371a96dcd947c7d93-Abstract.html) (accessed 2026-09-25)
7. Song, Y., Sohl-Dickstein, J., Kingma, D. P., Kumar, A., Ermon, S. & Poole, B. *Score-Based Generative Modeling through Stochastic Differential Equations*. ICLR, 2021. arXiv:2011.13456. [https://arxiv.org/abs/2011.13456](https://arxiv.org/abs/2011.13456) (accessed 2026-09-25)
8. Song, Y., Durkan, C., Murray, I. & Ermon, S. *Maximum Likelihood Training of Score-Based Diffusion Models*. NeurIPS 34, 2021. arXiv:2101.09258. [https://proceedings.neurips.cc/paper_files/paper/2021/hash/0a9fdbb17feb6ccb7ec405cfb85222c4-Abstract.html](https://proceedings.neurips.cc/paper_files/paper/2021/hash/0a9fdbb17feb6ccb7ec405cfb85222c4-Abstract.html) (accessed 2026-09-25)
9. Huang, C.-W., Lim, J. H. & Courville, A. *A Variational Perspective on Diffusion-Based Generative Models and Score Matching*. NeurIPS 34, 2021. arXiv:2106.02808. [https://proceedings.neurips.cc/paper_files/paper/2021/hash/c11abfd29e4d9b4d4b566b01114d8486-Abstract.html](https://proceedings.neurips.cc/paper_files/paper/2021/hash/c11abfd29e4d9b4d4b566b01114d8486-Abstract.html) (accessed 2026-09-25)
10. Nichol, A. & Dhariwal, P. *Improved Denoising Diffusion Probabilistic Models*. ICML (PMLR v139), 2021, pp. 8162–8171. [https://proceedings.mlr.press/v139/nichol21a.html](https://proceedings.mlr.press/v139/nichol21a.html) (accessed 2026-09-25)
11. Karras, T., Aittala, M., Aila, T. & Laine, S. *Elucidating the Design Space of Diffusion-Based Generative Models*. NeurIPS 35, 2022. arXiv:2206.00364. [https://arxiv.org/abs/2206.00364](https://arxiv.org/abs/2206.00364) (accessed 2026-09-25)
12. Vincent, P. *A Connection Between Score Matching and Denoising Autoencoders*. Neural Computation 23(7), 2011, pp. 1661–1674. DOI 10.1162/NECO_a_00142. [https://doi.org/10.1162/NECO_a_00142](https://doi.org/10.1162/NECO_a_00142) (accessed 2026-09-25)
13. Hyvärinen, A. *Estimation of Non-Normalized Statistical Models by Score Matching*. Journal of Machine Learning Research 6, 2005, pp. 695–709. [https://jmlr.org/papers/v6/hyvarinen05a.html](https://jmlr.org/papers/v6/hyvarinen05a.html) (accessed 2026-09-25)
14. Efron, B. *Tweedie's Formula and Selection Bias*. Journal of the American Statistical Association 106(496), 2011, pp. 1602–1614. DOI 10.1198/jasa.2011.tm11181. [https://www.tandfonline.com/doi/abs/10.1198/jasa.2011.tm11181](https://www.tandfonline.com/doi/abs/10.1198/jasa.2011.tm11181) (accessed 2026-09-22)
15. Salimans, T. & Ho, J. *Progressive Distillation for Fast Sampling of Diffusion Models*. ICLR, 2022. arXiv:2202.00512. [https://arxiv.org/abs/2202.00512](https://arxiv.org/abs/2202.00512) (accessed 2026-09-25)
16. Song, J., Meng, C. & Ermon, S. *Denoising Diffusion Implicit Models*. ICLR, 2021. arXiv:2010.02502. [https://arxiv.org/abs/2010.02502](https://arxiv.org/abs/2010.02502) (accessed 2026-09-25)
17. Blei, D. M., Kucukelbir, A. & McAuliffe, J. D. *Variational Inference: A Review for Statisticians*. Journal of the American Statistical Association 112(518), 2017, pp. 859–877. DOI 10.1080/01621459.2017.1285773. [https://doi.org/10.1080/01621459.2017.1285773](https://doi.org/10.1080/01621459.2017.1285773) (accessed 2026-09-25)
18. Guo, D., Shamai, S. & Verdú, S. *Mutual Information and Minimum Mean-Square Error in Gaussian Channels*. IEEE Transactions on Information Theory 51(4), 2005, pp. 1261–1282. DOI 10.1109/TIT.2005.844072. [https://doi.org/10.1109/TIT.2005.844072](https://doi.org/10.1109/TIT.2005.844072) (accessed 2026-09-25)
19. Kong, X., Brekelmans, R. & Ver Steeg, G. *Information-Theoretic Diffusion*. ICLR, 2023. arXiv:2302.03792. [https://arxiv.org/abs/2302.03792](https://arxiv.org/abs/2302.03792) (accessed 2026-09-25)
20. Hang, T., Gu, S., Li, C., Bao, J., Chen, D., Hu, H., Geng, X. & Guo, B. *Efficient Diffusion Training via Min-SNR Weighting Strategy*. ICCV, 2023, pp. 7407–7417. DOI 10.1109/ICCV51070.2023.00684. [https://doi.org/10.1109/ICCV51070.2023.00684](https://doi.org/10.1109/ICCV51070.2023.00684) (accessed 2026-09-25)
21. Lin, S., Liu, B., Li, J. & Yang, X. *Common Diffusion Noise Schedules and Sample Steps are Flawed*. WACV, 2024. arXiv:2305.08891. [https://arxiv.org/abs/2305.08891](https://arxiv.org/abs/2305.08891) (accessed 2026-09-25)
22. Yang, L., Zhang, Z., Song, Y., Hong, S., Xu, R., Zhao, Y., Zhang, W., Cui, B. & Yang, M.-H. *Diffusion Models: A Comprehensive Survey of Methods and Applications*. ACM Computing Surveys 56(4), 2023. DOI 10.1145/3626235. [https://doi.org/10.1145/3626235](https://doi.org/10.1145/3626235) (accessed 2026-09-25)
23. Croitoru, F.-A., Hondru, V., Ionescu, R. T. & Shah, M. *Diffusion Models in Vision: A Survey*. IEEE TPAMI 45(9), 2023, pp. 10850–10869. DOI 10.1109/TPAMI.2023.3261988. [https://doi.org/10.1109/TPAMI.2023.3261988](https://doi.org/10.1109/TPAMI.2023.3261988) (accessed 2026-09-25)
