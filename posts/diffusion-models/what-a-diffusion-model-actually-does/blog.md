---
title: "What a Diffusion Model Actually Does"
slug: what-a-diffusion-model-actually-does
date: 2026-09-22
updated: 2026-09-22
summary: "A diffusion model never learns to draw. It learns to guess the noise in a picture you deliberately spoiled — and that turns out to be enough to make a new one."
tags: [machine-learning, diffusion-model, generative-model, deep-learning, computer-vision]
category: machine-learning
series: diffusion-models
series_position: 1
tier: L2
difficulty: beginner
prerequisites: ["what a neural network is", "a Gaussian is a bell curve with a mean and a spread"]
reading_minutes: 16
cover_image: "https://minio.canery.in/media/cover-what-a-diffusion-model-actually-does.png"
canonical_url: "https://canery.in/blogs/what-a-diffusion-model-actually-does"
---
![A twelve-by-twelve patch of pure noise resolving through six stages into a bright crescent, under the line 'Trained only to undo noise'](https://minio.canery.in/media/cover-what-a-diffusion-model-actually-does.png)

> [!NOTE]
> **Insights** — A diffusion model is never shown a picture and asked to draw one. It is shown a picture you deliberately spoiled with a known amount of random noise, and asked which noise you added. That question has a free answer — you drew the noise, so you already know it — which is why the training needs no labels at all. The new image comes from the random tensor you start sampling from, not from anything the network remembers.

**Level:** beginner · **You need:** what a neural network is; a Gaussian is a bell curve with a mean and a spread · **Time:** ~16 min

## Why this matters

Two failures look identical from the outside and have nothing to do with each other. A model that produces smooth, plausible mush at any setting has a denoiser problem. A model that produces sharp images with mangled geometry at 8 steps and clean ones at 50 has a sampler problem, and its denoiser is fine. Telling them apart takes about thirty seconds once you know that a diffusion model is two separate things — a network and a procedure that calls it — and is impossible while "the model" means both at once.

## The problem

You have a folder of images and you want a new one that belongs in that folder. You cannot write down what "belongs in that folder" means; that is the entire difficulty. The set of tensors that look like photographs is a vanishingly thin sliver of the set of all tensors, and nobody can describe its boundary.

Diffusion sidesteps the description. Instead of characterising the good images, it builds a road from them to something trivially easy to sample — pure Gaussian noise — and then learns to walk the road backwards.

The **forward process** is that road. It is a fixed recipe, chosen by you before training, that adds a little Gaussian noise at a time until nothing of the original survives. **Gaussian noise** here means each pixel gets an independent draw from a bell curve centred on zero. "Forward" means data → noise; it is the destructive direction, and it is never the direction you generate in.

The forward process has a property that decides everything downstream. You do not have to simulate it step by step: there is a closed form that jumps straight from the clean image to any noise level in one operation.

$$
x_t = \sqrt{\bar\alpha_t}\, x_0 + \sqrt{1-\bar\alpha_t}\, \epsilon
$$

Here $x_0$ is the clean image, $\epsilon$ is one draw of Gaussian noise the same shape as the image, and $`\bar\alpha_t`$ is a number between 0 and 1 that says how much signal is left at step $t$. At $`\bar\alpha_t = 1`$ you have the original; at $`\bar\alpha_t = 0`$ you have pure noise. Everything in this post is an argument about that one line.

Now the asymmetry. Going right along that road is arithmetic — two multiplications and an addition, with no parameters to learn. Going left is not arithmetic, because many different clean images could have produced the same noisy one, and the formula does not tell you which. *That* is the thing a neural network is for, and it is the only thing it is for.

![A crescent-shaped patch shown at five rising noise levels; the left-to-right arrow carries a closed-form equation with no parameters, the right-to-left arrow carries the learned network](https://minio.canery.in/media/fig-01-forward-is-a-formula-what-a-diffusion-model-actually-does.png)

*Figure 1. The crescent is still visible at ᾱ = 0.64 and gone by ᾱ = 0.02. The top arrow is a formula; the bottom arrow is every parameter anyone trains.*

## Worked example

Take a 4×4 greyscale patch. Pixel values are scaled to roughly $[-1, 1]$, which is what diffusion implementations do, so −1 is black and +1 is white.

$$
x_0 = \begin{bmatrix}
0.95 & 0.60 & -0.30 & -0.85\\
0.80 & 0.45 & -0.55 & -0.90\\
0.55 & 0.10 & -0.70 & -0.95\\
0.25 & -0.20 & -0.85 & -1.00
\end{bmatrix}
\qquad
\epsilon = \begin{bmatrix}
-0.55 & 1.40 & 0.45 & -1.10\\
0.85 & -1.35 & -0.25 & 0.70\\
1.25 & 0.30 & -0.95 & 0.15\\
-1.05 & 0.90 & 1.45 & -1.10
\end{bmatrix}
$$

$x_0$ is a bright-to-dark diagonal ramp. $\epsilon$ is one draw of sixteen standard Gaussian numbers — this particular draw has mean 0.07 and standard deviation 0.98, which is what a draw of sixteen should look like. In training it is random every time; fixed here so you can check the arithmetic.

Pick a noise level where $`\bar\alpha_t = 0.64`$. Then $`\sqrt{\bar\alpha_t} = 0.8`$ and $`\sqrt{1-\bar\alpha_t} = 0.6`$ exactly, which is the only reason this value was chosen. Scale the two tensors separately:

$$
0.8\,x_0 = \begin{bmatrix}
0.76 & 0.48 & -0.24 & -0.68\\
0.64 & 0.36 & -0.44 & -0.72\\
0.44 & 0.08 & -0.56 & -0.76\\
0.20 & -0.16 & -0.68 & -0.80
\end{bmatrix}
\qquad
0.6\,\epsilon = \begin{bmatrix}
-0.33 & 0.84 & 0.27 & -0.66\\
0.51 & -0.81 & -0.15 & 0.42\\
0.75 & 0.18 & -0.57 & 0.09\\
-0.63 & 0.54 & 0.87 & -0.66
\end{bmatrix}
$$

Add them and you have $x_t$, the thing the network will actually be shown:

$$
x_t = \begin{bmatrix}
0.43 & 1.32 & 0.03 & -1.34\\
1.15 & -0.45 & -0.59 & -0.30\\
1.19 & 0.26 & -1.13 & -0.67\\
-0.43 & 0.38 & 0.19 & -1.46
\end{bmatrix}
$$

![Three four-by-four grids of printed values, shaded by brightness: the scaled clean patch, the scaled noise, and their sum, with two cells traced through the addition](https://minio.canery.in/media/fig-02-one-forward-step-what-a-diffusion-model-actually-does.png)

*Figure 2. Follow the top-right pair: 0.48 + 0.84 = 1.32, brighter than 0.95, the brightest pixel the original had. Noise does not merely dim an image; it moves values outside the range the data ever occupied.*

Two cells are worth stopping on. The pixel at row 1, column 2 was a mid-grey 0.60 and arrives at 1.32 — brighter than anything in the original. The pixel at row 4, column 3 was a near-black −0.85 and arrives at 0.19, essentially neutral grey. Individual pixels have stopped being trustworthy. What survives at this level is the overall arrangement: the left side is still brighter than the right.

### The answer key is free

Here is the move that makes the whole field work. We hand the network $x_t$ and the number $t$, and ask it to output $\epsilon$ — the noise we added.

We know $\epsilon$. We drew it. Nobody labelled anything, nobody paid an annotator, and we can manufacture a fresh training pair from any image in the dataset at any noise level, forever, in one operation. The loss is just the squared difference between the network's guess $\hat\epsilon$ and the $\epsilon$ we used.

And predicting the noise is equivalent to predicting the image, because the forward equation rearranges:

$$
\hat{x}_0 = \frac{x_t - \sqrt{1-\bar\alpha_t}\,\hat\epsilon}{\sqrt{\bar\alpha_t}}
= \frac{x_t - 0.6\,\hat\epsilon}{0.8}
$$

Put the true $\epsilon$ into that and you get $x_0$ back exactly, to the last decimal. A preprint by Luo works through why predicting the noise, predicting the clean image, and predicting the score are three interchangeable targets for the same objective.  Hold onto this equation; it is about to explain the single most confusing thing about diffusion models.

## Intuition

Stop thinking of the network as a painter and start thinking of it as a compass.

Picture every possible tensor of the right shape as a point in an enormous space. Real images occupy a thin, complicated region of it. Adding noise pushes a point off that region; the more noise, the further off. What the network learns is, for every point in that space and every noise level, which direction points back toward the region. It never sees the region as a whole, and it could not draw you a map of it. It only answers one question — "from here, which way?" — and it answers it locally.

That is why the same network can be described two ways that sound unrelated. Predicting the noise that was added and predicting the **score** — the gradient of the log density, a vector field pointing toward where data is denser  — are the same output up to a known scale factor. One is phrased as an error to subtract, the other as a direction to follow.

Sampling, then, is walking. You are dropped at a random point in fog, you read the compass, you take a small step, and you read it again from the new position. After enough steps you are standing somewhere in the region of real images.

The analogy breaks in one specific place, and the break is the interesting part. Walking downhill in fog gets you to *the* bottom of the valley — one destination, the same one every time. Here there is no single bottom. There is an entire landscape of valid destinations, and which one you arrive at is fixed by where you were dropped and by the small random nudge the sampler adds at each step. The compass is identical for every user of the model. The walk is not.

## Where does 0.64 come from?

From the **noise schedule**: the fixed list of per-step variances $`\beta_1 \ldots \beta_T`$ you choose before training. Each $`\beta_t`$ is how much variance one step adds, $`\alpha_t = 1 - \beta_t`$, and $`\bar\alpha_t`$ is all the $\alpha$ up to $t$ multiplied together — the fraction of the original signal *power* still present. The schedule is configuration. It is not a layer, it has no parameters, and gradient descent never touches it.

Why a whole ladder of levels rather than one? Because a single level fails in two ways at once. Off the region of real images the direction the network needs is undefined; and in the sparse stretches there is too little data to estimate it, while a sampler crossing those stretches mixes too slowly to recover the right balance between distant modes. Large noise fixes both and destroys the image; small noise preserves the image and reinstates both. The ladder is the compromise.

The original DDPM(Denoising Diffusion Probabilistic Model) paper ran 1,000 steps with $`\beta_t`$ rising linearly from 0.0001 to 0.02.  Multiply that out and $`\sqrt{\bar\alpha_T} = 0.0064`$ — less than one part in 150 of the original amplitude survives.

![Two curves of the signal coefficient against normalised timestep: the linear schedule loses half its signal far earlier than the cosine one and flattens near zero for the last third, with the worked example's value of 0.80 marked](https://minio.canery.in/media/fig-03-noise-schedule-what-a-diffusion-model-actually-does.png)

*Figure 3. Both curves are computed from the published schedule definitions, not measured. The linear schedule is down to √ᾱ = 0.058 at three-quarters of the way through — it spends its last quarter shuffling noise.*

That flatness is a real defect, not an aesthetic one. Nichol and Dhariwal introduced the cosine schedule precisely because the linear one destroys information faster than it needs to,  and reported that a linear-schedule model barely loses FID when up to 20% of the reverse process is skipped — those steps were doing almost nothing.  Their replacement defines $`\bar\alpha_t`$ directly as a cosine curve with a small offset of 0.008, chosen so the first step's noise sits just under one 8-bit pixel level.

Choosing the schedule is choosing which noise levels the network ever gets to practise on, and a level it never practises is a level it will be bad at.

Schedules also tend not to end where they claim to. The one Stable Diffusion ships leaves $`\sqrt{\bar\alpha_T} = 0.068`$ at the final step, so its last training input still holds about 7% of the original signal while sampling begins from pure noise.  That mismatch is small, real, and the subject of its own paper.

## Why does one call blur and many calls draw?

Ask what the ideal network *should* output when the noise is heavy. At $`\bar\alpha = 0.09`$, a huge number of different clean patches are consistent with the same $x_t$ — a vertical edge, a horizontal edge, a diagonal, a blob — each needing only an ordinary-looking noise draw to explain the observation. The network has no way to tell them apart, because the information that would distinguish them was destroyed.

So it hedges, and squared-error training tells it exactly how. The function that minimises mean squared error is the conditional mean: the average of every clean image consistent with this input, weighted by how plausible each one is.  That identity is old — it is Tweedie's formula, which gives the posterior mean of something observed through Gaussian noise as the observation plus the noise variance times the score of its marginal.

![A noisy patch on the left fans out to four different clean patches, each needing an equally ordinary noise draw, and those four average on the right into a smeared grey patch](https://minio.canery.in/media/fig-04-the-average-is-the-blur-what-a-diffusion-model-actually-does.png)

*Figure 4. Averaging four sharp patches gives a smeared one. A single denoiser call at high noise is doing this over the entire dataset, which is why its output is a blur — and why the blur is the correct answer, not a failure.*

This is the central point of the post. **A single denoiser call at high noise returns a blur because a blur is the right answer.** It is not the network being weak; a perfect network would return the same blur.

Now the arithmetic. Rearranged, a prediction error $\delta$ in $\hat\epsilon$ shows up in the reconstructed image multiplied by $`\sqrt{1-\bar\alpha}/\sqrt{\bar\alpha}`$:

| $`\bar\alpha`$ | multiplier |
| ---------------- | ---------- |
| 0.96             | ×0.20     |
| 0.64             | ×0.75     |
| 0.25             | ×1.73     |
| 0.02             | ×7.00     |

![Top lane: one arrow from pure noise to a blurred patch, beside a table of error multipliers. Bottom lane: the same noise through eight small steps to a sharp crescent](https://minio.canery.in/media/fig-05-one-jump-versus-eight-steps-what-a-diffusion-model-actually-does.png)

*Figure 5. Same starting noise, both lanes. Eight steps do not do more work than one — they commit to less of it at a time, while the multiplier is still small.*

At $`\bar\alpha = 0.02`$ the multiplier is 7.00, so a modest 0.20 error in the predicted noise lands as a 1.40 error in the image — wider than the whole pixel range. Jumping in one step amplifies your least reliable prediction by the largest factor available.

Taking many small steps avoids this twice over. Each step only has to move a short distance, so the multiplier stays near 1; and each step re-reads the *partially* cleaned image, so the next prediction is made from better evidence than the last. There is also a theoretical reason the steps must be small: the reverse of a Gaussian diffusion is itself Gaussian only in the small-step limit,  and DDPM cites exactly that result to justify modelling its reverse transitions as Gaussians at all.

None of which means 1,000 steps is a law. Consistency models reach FID 3.55 on CIFAR-10 in a single step — but by training a different function with a different procedure, distilled from an already-trained diffusion model.  You can have one step. You cannot have it for free from a network trained this way. Part 6 of this series is about how 1,000 becomes 20, and part 7 about how 20 becomes 1.

## Where does the new image come from?

If the network only ever saw corrupted copies of training images, why is the output not a training image?

Because you never feed it one. Sampling starts at $`x_T \sim \mathcal{N}(0, I)`$ — a tensor of fresh random numbers, generated right then.  That seed is the only genuinely new thing in the system, and every subsequent step is a short move guided by it. The network supplies a direction; the seed supplies a destination.

The strongest evidence that this is more than a story comes from training two separate networks on *non-overlapping* halves of a dataset. Once the training set is large enough, they converge on nearly the same denoising function and, given the same seed, produce nearly the same image — one that resembles nothing in either network's training set.  Two models that never saw a single image in common agree on what should come out. That is not recall; there is nothing shared to recall from.

But the same experiment shows the other side. At small training-set sizes — a thousand images or fewer — the two networks memorise their own data and return training images instead. The transition is a function of how much data the model saw.

And memorisation happens in production systems too. Carlini and colleagues extracted 94 training images from Stable Diffusion, plus 13 further near-copies found by hand.  The setup matters as much as the number: they used the captions of the 350,000 *most-duplicated* training examples and generated 500 images for each, 175 million in total, then filtered.  That is an adversarial search, not ordinary use.

A second study found about 1.88% of 9,000 generations from random captions matched a training image closely enough to count as replication — though against an index covering under 0.6% of the training data, so it is a partial search.  What predicted replication was duplication: the matched images had appeared in the training set 34.1 times on average.  And their own models trained on 300 or 3,000 images produced blatant copies, while a full-ImageNet model produced none they could detect.

So the honest answer is conditional. A well-trained model on a large, deduplicated dataset generates genuinely new images, and the seed is where the newness lives. A model trained on a small dataset, or on one image repeated a thousand times, will hand that image back. Part 12 takes this apart properly.

## What are the four moving parts?

![An end-to-end graph placing the training loop and the sampling loop around one shared denoiser, with the fixed schedule feeding both](https://minio.canery.in/media/fig-06-the-four-moving-parts-what-a-diffusion-model-actually-does.png)

*Figure 6. Only box ③ was trained. The schedule is constants, the sampler is arithmetic, and the seed is a random draw — swap any of the three and the same checkpoint still works.*

**① The schedule** — the fixed $`\beta_1 \ldots \beta_T`$. Configuration.

**② The training loop** — pick an image, pick a random $t$, draw $\epsilon$, corrupt in one operation, ask the network for $\epsilon$, take a gradient step. It runs once, offline.

**③ The denoiser** — the only trained component. It takes $x_t$ and $t$ and returns $\hat\epsilon$. Everything about how it is built — convolutions, attention, transformers, where a text prompt enters — lives inside this box and is what part 2 of this series opens up.

**④ The sampler** — the numerical procedure that repeatedly calls ③ and walks from noise to an image. It is arithmetic with no parameters, which is why you can replace a 1,000-step sampler with a 20-step one on a checkpoint you did not train.

One thing the diagram deliberately leaves out: in most systems you actually use, ③ does not run on pixels at all. Latent diffusion first compresses the image with a pretrained autoencoder — eight times smaller per side in the paper's text-to-image model — and denoises that compressed code instead.  It changes what the tensors are, not what any of the four parts do.

That separation is the whole payoff of the post. "Diffusion" names the system, not the network. When you read that some new model is faster, the first question is which box changed — a sampler improvement and a denoiser improvement are not comparable claims. Treating schedule, weighting, backbone and solver as independent choices rather than one fixed recipe is exactly how the EDM paper reorganised this field.

If you want a map of what has been tried in each box, the standard survey sorts the whole methods literature along three axes: efficient sampling, better likelihoods, and data that is not a grid.  It becomes a usable reading list the moment you can tell which box a paper is touching.

## The math

There are three symbols and one equation to carry forward.

| Symbol                                           | Meaning                                                            | Range        |
| ------------------------------------------------ | ------------------------------------------------------------------ | ------------ |
| $`\beta_t`$      | variance added by step$t$ | small, e.g. 0.0001 → 0.02                                         |              |
| $`\alpha_t`$                                   | $`1-\beta_t`$, the fraction of variance that survives one step   | just under 1 |
| $`\bar\alpha_t`$                               | $`\prod_{s\le t}\alpha_s`$, signal power surviving to step $t$ | 1 down to ~0 |

Training minimises one expectation, over random images, random timesteps and random noise:

$$
L = \mathbb{E}_{x_0,\,t,\,\epsilon}\left[\left\|\epsilon - \epsilon_\theta\!\left(\sqrt{\bar\alpha_t}x_0 + \sqrt{1-\bar\alpha_t}\epsilon,\; t\right)\right\|^2\right]
$$

In words: corrupt a real image to a random noise level, ask the network which noise you used, and penalise the squared error. That is the entire training objective — it is a regression loss, and there is nothing adversarial or probabilistic-looking about it. Where it comes from, and why minimising it fits a probability distribution at all, is part 3.

Sampling walks back down with the update DDPM calls Algorithm 2:

$$
x_{t-1} = \frac{1}{\sqrt{\alpha_t}}\left(x_t - \frac{\beta_t}{\sqrt{1-\bar\alpha_t}}\,\epsilon_\theta(x_t, t)\right) + \sigma_t z
$$

Read it in two halves. The bracket is "remove the amount of noise the network says is there, then undo the shrinking." The $`\sigma_t z`$ on the end adds a small amount of *fresh* noise back, with $z \sim \mathcal{N}(0,I)$ for every step except the last. DDPM does not learn $`\sigma_t`$; it sets it to $`\beta_t`$ or a close relative and reports similar results either way.

That re-noising looks perverse and is not. The network's output is an average, and stepping straight onto an average walks you off the set of real images. Injecting a little noise keeps the trajectory stochastic, so the sample commits to one of the plausible images instead of landing between several. The same learned function can also be run as a fully deterministic ordinary differential equation, which is the basis of the fast samplers.

## Implementation

The forward process and the loss, with no framework. This is the whole training step.

```python
import numpy as np

T = 1000
betas = np.linspace(1e-4, 0.02, T)          # the schedule: fixed, never learned
alphas = 1.0 - betas
abar = np.cumprod(alphas)                    # signal power surviving to each step

def training_pair(x0, rng):
    """One (input, target) pair. No labels, no annotation — we draw the target."""
    t = rng.integers(0, T)                   # a random noise level for this example
    eps = rng.standard_normal(x0.shape)      # the target, drawn before it is needed
    xt = np.sqrt(abar[t]) * x0 + np.sqrt(1 - abar[t]) * eps
    return xt, t, eps                        # the network sees xt and t; eps is the answer

def loss(eps_hat, eps):
    return float(np.mean((eps_hat - eps) ** 2))
```

`abar[t]` is the $`\bar\alpha_t`$ from the worked example — `abar[207]` is 0.6405, which is where the 0.64 came from. The only thing missing is `eps_hat = network(xt, t)`, and the network is a plain regressor: tensor in, same-shaped tensor out.

```python
def reconstruct(xt, t, eps_hat):
    """The network predicted noise; recover its implied clean image."""
    return (xt - np.sqrt(1 - abar[t]) * eps_hat) / np.sqrt(abar[t])
```

Feed `reconstruct` the true `eps` and it returns `x0` exactly. Feed it a prediction off by δ and the error arrives scaled by `sqrt(1 - abar[t]) / sqrt(abar[t])` — the multiplier from Figure 5, in one line of code.

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** treating the denoiser as an image-restoration tool. It was trained on *synthetic* noise, at a noise level it is told, with a known statistical shape. Hand it a real photograph with sensor noise, JPEG artefacts or motion blur and you are outside its training distribution in three directions at once.

- **"More steps is always better."** Steps stop helping once discretisation error is no longer what limits the sample, and where that happens is a property of the sampler, not the network. A linear-schedule DDPM loses little FID when a fifth of the reverse process is dropped.
- **"It is just memorising."** Mostly wrong, occasionally right, and the condition that separates the two is duplication in the training set, not model size. Carry the numbers — 94 images out of 175 million adversarially chosen generations   — rather than a reassurance.
- **"Diffusion means DDPM."** The 2020 objective is one member of a family. The standard vision survey treats the field as three formulations at once — denoising diffusion probabilistic models, noise-conditioned score networks, and stochastic differential equations  — and modern text-to-image transformers frequently train with none of them.
- **Benchmark numbers without their setup.** DDPM's CIFAR-10 FID of 3.17 is the best *unconditional* result in its own table, not the best result in it, and it is measured against the training set; against the test set the same model scores 5.24.  Guided diffusion's 4.59 on ImageNet 256×256 beats BigGAN-deep's 6.95 — but the *unguided* model scores 10.94 and loses.  An FID with no setup attached is not a fact.

## Key takeaways

- The forward corruption is a closed-form formula with zero parameters; the network exists only because that formula cannot be run backwards.
- The training target is free, because you draw the noise yourself before adding it — which is why diffusion training needs no labelled data.
- A single denoiser call at high noise returns the average of every clean image consistent with its input. The blur is the correct output, and it is why sampling iterates.
- An error in the predicted noise is amplified by $`\sqrt{1-\bar\alpha}/\sqrt{\bar\alpha}`$ when converted back to an image — ×0.75 at ᾱ = 0.64 and ×7.00 at ᾱ = 0.02. Small steps keep that multiplier small.
- Novelty comes from the random seed, and it is conditional: duplicated training images are the measured route back to memorisation.
- Schedule, denoiser and sampler are three independent choices. Only the denoiser is trained.

## Try it yourself

1. Using the worked example's numbers, suppose the network returns $\hat\epsilon$ equal to the true $\epsilon$ everywhere except the top-left cell, where it returns −0.35 instead of −0.55. What is the reconstructed value at that cell, and how far is it from the true 0.95?

<details><summary>Answer</summary>

The error is $\delta = -0.35 - (-0.55) = +0.20$. The multiplier at $`\bar\alpha = 0.64`$ is $0.6/0.8 = 0.75$, and it enters with a minus sign, so the reconstruction is off by $-0.75 \times 0.20 = -0.15$, giving 0.80 instead of 0.95.

Directly: $`(0.43 - 0.6 \times (-0.35)) / 0.8 = (0.43 + 0.21)/0.8 = 0.80`$. ✓

</details>

2. At which $`\bar\alpha`$ does an error in the predicted noise arrive in the image at exactly the same size — multiplier 1.00?

<details><summary>Answer</summary>

$`\sqrt{1-\bar\alpha}/\sqrt{\bar\alpha} = 1`$ when $`1-\bar\alpha = \bar\alpha`$, so $`\bar\alpha = 0.5`$. Above 0.5 the network's errors are damped; below it they are amplified, and the amplification runs away as $`\bar\alpha \to 0`$.

</details>

3. Why does the last sampling step set $z = 0$ instead of adding noise like every other step?

<details><summary>Answer</summary>

Because its output is the image you keep. Every earlier step adds noise so the trajectory can still commit to one of several plausible images; after the final step there is nothing left to commit to, and added noise would just be visible grain in the result.

</details>

## References

1. Sohl-Dickstein, J., Weiss, E., Maheswaranathan, N. & Ganguli, S. *Deep Unsupervised Learning using Nonequilibrium Thermodynamics*. ICML (PMLR v37), 2015. [https://proceedings.mlr.press/v37/sohl-dickstein15.html](https://proceedings.mlr.press/v37/sohl-dickstein15.html) (accessed 2026-09-22)
2. Ho, J., Jain, A. & Abbeel, P. *Denoising Diffusion Probabilistic Models*. NeurIPS 33, 2020. [https://proceedings.neurips.cc/paper/2020/hash/4c5bcfec8584af0d967f1ab10179ca4b-Abstract.html](https://proceedings.neurips.cc/paper/2020/hash/4c5bcfec8584af0d967f1ab10179ca4b-Abstract.html) (accessed 2026-09-22)
3. Song, Y. & Ermon, S. *Generative Modeling by Estimating Gradients of the Data Distribution*. NeurIPS 32, 2019. [https://proceedings.neurips.cc/paper/2019/hash/3001ef257407d5a371a96dcd947c7d93-Abstract.html](https://proceedings.neurips.cc/paper/2019/hash/3001ef257407d5a371a96dcd947c7d93-Abstract.html) (accessed 2026-09-22)
4. Song, Y., Sohl-Dickstein, J., Kingma, D. P., Kumar, A., Ermon, S. & Poole, B. *Score-Based Generative Modeling through Stochastic Differential Equations*. ICLR, 2021. arXiv:2011.13456. [https://arxiv.org/abs/2011.13456](https://arxiv.org/abs/2011.13456) (accessed 2026-09-22)
5. Nichol, A. & Dhariwal, P. *Improved Denoising Diffusion Probabilistic Models*. ICML (PMLR v139), 2021, pp. 8162–8171. [https://proceedings.mlr.press/v139/nichol21a.html](https://proceedings.mlr.press/v139/nichol21a.html) (accessed 2026-09-22)
6. Dhariwal, P. & Nichol, A. *Diffusion Models Beat GANs on Image Synthesis*. NeurIPS 34, 2021. [https://proceedings.neurips.cc/paper/2021/hash/49ad23d1ec9fa4bd8d77d02681df5cfa-Abstract.html](https://proceedings.neurips.cc/paper/2021/hash/49ad23d1ec9fa4bd8d77d02681df5cfa-Abstract.html) (accessed 2026-09-22)
7. Rombach, R., Blattmann, A., Lorenz, D., Esser, P. & Ommer, B. *High-Resolution Image Synthesis with Latent Diffusion Models*. CVPR, 2022. [https://openaccess.thecvf.com/content/CVPR2022/html/Rombach_High-Resolution_Image_Synthesis_With_Latent_Diffusion_Models_CVPR_2022_paper.html](https://openaccess.thecvf.com/content/CVPR2022/html/Rombach_High-Resolution_Image_Synthesis_With_Latent_Diffusion_Models_CVPR_2022_paper.html) (accessed 2026-09-22)
8. Song, Y., Dhariwal, P., Chen, M. & Sutskever, I. *Consistency Models*. ICML (PMLR v202), 2023, pp. 32211–32252. [https://proceedings.mlr.press/v202/song23a.html](https://proceedings.mlr.press/v202/song23a.html) (accessed 2026-09-22)
9. Kadkhodaie, Z., Guth, F., Simoncelli, E. P. & Mallat, S. *Generalization in diffusion models arises from geometry-adaptive harmonic representations*. ICLR, 2024. arXiv:2310.02557. [https://arxiv.org/abs/2310.02557](https://arxiv.org/abs/2310.02557) (accessed 2026-09-22)
10. Carlini, N., Hayes, J., Nasr, M., Jagielski, M., Sehwag, V., Tramèr, F., Balle, B., Ippolito, D. & Wallace, E. *Extracting Training Data from Diffusion Models*. USENIX Security 23, 2023, pp. 5253–5270. [https://www.usenix.org/conference/usenixsecurity23/presentation/carlini](https://www.usenix.org/conference/usenixsecurity23/presentation/carlini) (accessed 2026-09-22)
11. Somepalli, G., Singla, V., Goldblum, M., Geiping, J. & Goldstein, T. *Diffusion Art or Digital Forgery? Investigating Data Replication in Diffusion Models*. CVPR, 2023, pp. 6048–6058. [https://openaccess.thecvf.com/content/CVPR2023/html/Somepalli_Diffusion_Art_or_Digital_Forgery_Investigating_Data_Replication_in_Diffusion_CVPR_2023_paper.html](https://openaccess.thecvf.com/content/CVPR2023/html/Somepalli_Diffusion_Art_or_Digital_Forgery_Investigating_Data_Replication_in_Diffusion_CVPR_2023_paper.html) (accessed 2026-09-22)
12. Efron, B. *Tweedie's Formula and Selection Bias*. Journal of the American Statistical Association 106(496), 2011, pp. 1602–1614. DOI 10.1198/jasa.2011.tm11181. [https://www.tandfonline.com/doi/abs/10.1198/jasa.2011.tm11181](https://www.tandfonline.com/doi/abs/10.1198/jasa.2011.tm11181) (accessed 2026-09-22)
13. Yang, L., Zhang, Z., Song, Y., Hong, S., Xu, R., Zhao, Y., Zhang, W., Cui, B. & Yang, M.-H. *Diffusion Models: A Comprehensive Survey of Methods and Applications*. ACM Computing Surveys 56(4), 2023. DOI 10.1145/3626235. [https://doi.org/10.1145/3626235](https://doi.org/10.1145/3626235) (accessed 2026-09-22)
14. Croitoru, F.-A., Hondru, V., Ionescu, R. T. & Shah, M. *Diffusion Models in Vision: A Survey*. IEEE TPAMI 45(9), 2023, pp. 10850–10869. DOI 10.1109/TPAMI.2023.3261988. [https://doi.org/10.1109/TPAMI.2023.3261988](https://doi.org/10.1109/TPAMI.2023.3261988) (accessed 2026-09-22)
15. Luo, C. *Understanding Diffusion Models: A Unified Perspective*. Preprint, arXiv:2208.11970, 2022. [https://arxiv.org/abs/2208.11970](https://arxiv.org/abs/2208.11970) (accessed 2026-09-22)
16. Lin, S., Flores, B., Li, X., Yuan, L. & Xiao, X. *Common Diffusion Noise Schedules and Sample Steps are Flawed*. WACV, 2024. arXiv:2305.08891. [https://arxiv.org/abs/2305.08891](https://arxiv.org/abs/2305.08891) (accessed 2026-09-22)
17. Karras, T., Aittala, M., Aila, T. & Laine, S. *Elucidating the Design Space of Diffusion-Based Generative Models*. NeurIPS 35, 2022. arXiv:2206.00364. [https://arxiv.org/abs/2206.00364](https://arxiv.org/abs/2206.00364) (accessed 2026-09-22)
18. Song, J., Meng, C. & Ermon, S. *Denoising Diffusion Implicit Models*. ICLR, 2021. arXiv:2010.02502. [https://arxiv.org/abs/2010.02502](https://arxiv.org/abs/2010.02502) (accessed 2026-09-22)
