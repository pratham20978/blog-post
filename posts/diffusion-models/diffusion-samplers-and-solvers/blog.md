---
title: "Diffusion Samplers and Solvers: 1,000 Steps Into 20"
slug: diffusion-samplers-and-solvers
date: 2026-10-09
updated: 2026-10-09
summary: "A diffusion sampler is an ODE solver. DDIM, Heun and DPM-Solver measured against the exact path at matched network calls: order and step placement set the cost."
tags: [machine-learning, diffusion-model, generative-model, ode-solver, numerical-methods, deep-learning]
category: machine-learning
series: diffusion-models
series_position: 6
tier: L4
difficulty: advanced
prerequisites: ["Part 1 of this series", "the denoiser as an estimate of the clean image", "what an ODE and Euler's method are"]
reading_minutes: 35
cover_image: "COVER"
canonical_url: "https://canery.in/blogs/diffusion-samplers-and-solvers"
---

![Error against network calls for DDIM and a third-order solver, beside exact sampling paths that bend once and end on crescents](COVER)

> [!NOTE]
> **Insights** — A diffusion sampler is a numerical solver for a differential equation the trained network already defines, so the step count is an accuracy dial, not a property of the model. DDIM, Heun and DPM-Solver differ only in how they guess the way the network's answer drifts between calls, and every one of them makes its error where the sampling path bends, which is where the image is being decided. Measured against the exact path in this post's lab, first-order DDIM needs 100 network calls to land within one 8-bit grey level of it and a third-order solver needs 16; on one CIFAR-10 model the same kind of choice moves FID at 10 calls from 16.44 to 2.98. Adding noise during sampling costs accuracy per step but forgets earlier errors, which is why stochastic samplers win only when calls are plentiful.

**Level:** advanced · **You need:** Part 1 of this series (What a Diffusion Model Actually Does), the denoiser as an estimate of the clean image, what an ODE and Euler's method are · **Time:** ~35 min

**Jump to:** [worked example](#worked-example) · [no retraining](#why-can-the-step-count-change-without-retraining) · [DDIM](#what-does-ddim-actually-compute) · [higher order](#how-do-higher-order-solvers-buy-accuracy) · [step placement](#where-should-the-steps-go) · [noise](#should-the-sampler-add-noise) · [choosing](#how-should-you-choose-a-sampler-and-a-step-count) · [math](#the-math) · [implementation](#implementation)

> [!IMPORTANT]
> Numbers this post calls **measured** come from its lab, run on one laptop CPU against a toy whose ideal denoiser has a closed form, so the exact sampling path is known and every error is the sampler's own. Numbers it calls **computed** come from closed forms the lab evaluates. Their magnitudes are a toy's; the orders, crossovers and failure modes are the mechanism. Results **quoted** from papers carry their model and dataset, and FIDs are compared only within one paper.

## Why this matters

Every diffusion pipeline exposes two knobs nobody trains: a sampler and a step count. Each step costs at least one full pass through the network, so the step count sets latency almost one for one; DDIM's authors measured sampling time growing linearly with the number of steps. <!-- L03 --> The sampler is not cosmetic either. On EDM's CIFAR-10 model at 10 network calls, DDIM with evenly spaced log-SNR steps scores FID 16.44 and DPM-Solver++(2M) with optimised steps 2.98; at 50 calls they meet at 2.82 and 2.01. <!-- L38 --> Choosing by folklore leaves either image quality or a factor of five in compute on the table. Choosing by measurement takes an afternoon, and this post shows how.

## The problem

Part 1 of this series, What a Diffusion Model Actually Does, explained why a diffusion model samples in many small steps and ended on a promise: the same network can sample in far fewer steps without being retrained. This post is about how far, and why.

Start with what training leaves behind. The network is a **denoiser**: given a noisy image and its noise level, it returns its best estimate of the clean image, the conditional mean of the clean image given the noisy one. This post writes it $D(x;\sigma)$. Part 3 of this series, Where the Diffusion MSE Loss Comes From, showed that dividing a noisy sample $`x_t`$ by $`\sqrt{\bar\alpha_t}`$ turns it into the clean image plus Gaussian noise of standard deviation $`\sigma = \sqrt{(1-\bar\alpha_t)/\bar\alpha_t}`$. This post works in those coordinates throughout, as DDIM and EDM do, and writes $x$ for the rescaled sample. <!-- L05 --> <!-- L23 -->

In them, sampling is one ordinary differential equation:

$$
\frac{dx}{d\sigma} = \frac{x - D(x;\sigma)}{\sigma} .
$$

This is the **probability-flow ODE**, the deterministic twin of the reverse diffusion process: its solutions carry the noise distribution at every level onto the next with the same marginals the stochastic process has, so solving it exactly from pure noise at large σ down to σ = 0 lands on a sample from the model. <!-- L10 --> Every starting noise has exactly one image it flows to.

A **sampler**, or solver, is a numerical method for that equation. It picks a decreasing list of noise levels $`\sigma_0 > \sigma_1 > \dots > 0`$ and a rule for moving from one to the next using denoiser calls. Its cost is counted in **NFE**, the number of function evaluations, meaning network calls per sample, because the network dominates the cost of sampling. <!-- L30 --> Steps are the wrong unit: a Heun step makes two calls, so 25 Heun steps cost 49 NFE, and comparing it with 25 DDIM steps compares unequal budgets. <!-- L21 --> The sampler's error is the distance between where it lands and where the exact ODE would have landed from the same noise.

Where does 1,000 come from? DDPM set its number of steps to 1,000 so that its sampler made as many network calls as earlier models did, and kept each step small so that its learned reverse step could be modelled as a Gaussian. <!-- L02 --> Its ancestral sampler used all 1,000. Stable Diffusion's original reference script, from 2022, defaults to 50 deterministic DDIM steps. <!-- L46 --> This post asks what makes that drop legitimate and what decides how far it can go: the solver's order, where its steps are placed, and whether it adds noise. A review of the field files all of these under learning-free sampling, as distinct from methods that train something new, such as distillation, which comes later in this series. <!-- L01 -->

The obstacle to measuring any of it is that the exact ODE solution is unknown for a real network. So the lab uses the toy from Part 5 of this series, Training a Diffusion Model: The Decisions Before Step One: "crescent world", images of one of four bright crescents with a random overall brightness and fine per-pixel detail. It is a mixture of Gaussians, so its ideal denoiser has a closed form, and the exact ODE can be solved by brute force to twelve decimal places. Every error below is the sampler's alone.

## Worked example

Part 5 left one number open. A 50-step DDIM sampler, run with that exact denoiser on 16,384-value crescent images and a correctly ending schedule, kept only 85.1% of the data's spread in brightness, and part 5 attributed the gap to the sampler. Here is the gap, computed by hand.

### One Gaussian number

Brightness is one number per image: its projection on the all-ones direction. In crescent world that number is an exact Gaussian, independent of which crescent is drawn, with variance $`V_0 = 16{,}384 \times 0.3^2 + 0.1^2 = 1{,}474.57`$. Along it the denoiser is a fixed shrinkage, $`D(x;\sigma) = \frac{V_0}{V_0+\sigma^2}\,x`$, and the ODE has a closed-form solution, $`x(\sigma) = \epsilon\sqrt{V_0+\sigma^2}`$, where ε is the starting noise value. Far above $`\sqrt{V_0} = 38.4`$ the exact path is the straight line $x \approx \epsilon\sigma$; far below it, the path is flat at $38.4\,\epsilon$. It bends where σ is near 38.4.

DDIM's update, in these coordinates, is $`x' = D + \frac{\sigma'}{\sigma}(x - D)`$: jump to the denoiser's guess, then keep the fraction σ′/σ of what is left. With the shrinkage substituted, one step from σ to σ′ multiplies $x$ by $`(V_0+\sigma\sigma')/(V_0+\sigma^2)`$, while the exact path multiplies it by $`\sqrt{(V_0+\sigma'^2)/(V_0+\sigma^2)}`$.

### The first six steps

Part 5's sampler starts at pure noise, σ = ∞, where the denoiser can only return the dataset's mean brightness, 0, so its first step lands at $x = 107.96\,\epsilon$, the next level on its grid. The exact path is at $`\sqrt{1{,}474.57 + 107.96^2}\,\epsilon = 114.59\,\epsilon`$, so the first step keeps $107.96/114.59 = 0.942$ of the spread. The next five steps compound:

| Step | σ → σ′ | DDIM multiplies by | Exact multiplies by | Spread kept so far |
|---:|---|---:|---:|---:|
| 1 | ∞ → 107.96 | — | — | 0.942 |
| 2 | 107.96 → 51.62 | 0.5367 | 0.5615 | 0.901 |
| 3 | 51.62 → 32.93 | 0.7669 | 0.7863 | 0.879 |
| 4 | 32.93 → 23.65 | 0.8806 | 0.8915 | 0.868 |
| 5 | 23.65 → 18.13 | 0.9358 | 0.9416 | 0.862 |
| 6 | 18.13 → 14.49 | 0.9634 | 0.9665 | 0.860 |

After six steps the sampler has kept 0.860 of the spread. The remaining 44 steps, all below σ = 14.5, lose only half a percent more and end at 0.855, part 5's number from first principles; the lab measures 0.854, with a standard error of 0.014, on 2,000 full images. Figure 1 shows where the loss happens.

![DDIM's share of the exact path after each of 50 steps, falling to 0.860 by σ = 14.5; log-SNR steps end at 0.941, DPM-Solver++ at 1.004](FIG_01)

*Figure 1. Computed exactly. The whole loss happens in the six steps around σ ≈ √V₀, where the path bends; above and below it, DDIM is close to exact. Spreading the same 50 steps evenly in log-SNR keeps 0.941; DPM-Solver++(2M) on that grid keeps 1.004.*

The pattern is the one the update rule predicts. Where σ is far above or far below 38.4 the denoiser's answer barely changes between levels, and DDIM's assumption that it does not change at all costs nothing. In the bend, each step's guess is stale by the time the step ends.

### The same 50 calls, two fixes

Two things decide the error: where the steps are, and what each step assumes about the denoiser. Spread 50 steps evenly in log-SNR instead, starting at σ = 4,096 (the finite stand-in for infinity that diffusers uses), and DDIM keeps 0.941. <!-- L44 --> Replace DDIM by DPM-Solver++(2M), a second-order method that still makes one call per step, and it keeps 1.0035. The error falls from 14.5% to 0.35%, 41 times smaller, at the same cost.

Figure 2 shows how each choice converges as calls are added.

![Error in brightness spread against network calls on two grids: DDIM reaches 1% at 778 calls, DPM-Solver++(2M) on log-SNR steps at 30](FIG_02)

*Figure 2. Computed exactly. DDIM's error halves each time its calls double; DPM-Solver++(2M)'s falls about four times. Heun, started at σ = 4,096 on part 5's grid, overshoots by a factor of 12 at 49 calls and needs 621 to come within 1%.*

Double DDIM's steps and its error halves: 27.5% at 25 steps, 14.5% at 50, 7.5% at 100, 3.8% at 200. That is a **first-order** method, whose error is proportional to its step size, and at that rate getting within 1% takes about 780 steps. DPM-Solver++(2M) on log-SNR steps gets there at 30 calls, because its error falls with the square of the step: between 20 and 50 calls, 2.5 times the calls cut its error sixfold. That factor of about 26 in cost is the whole post in one number. 1,000 steps become 20 or 30 by choosing a higher-order method and putting its steps where the path bends.

Heun, EDM's second-order method, is the warning. On part 5's spacing with 25 steps, 49 calls, its first step spans σ = 4,096 down to 52, and it returns 12 times the right spread. The trapezoid rule it uses averages the slope at the two ends of a step, and here the slope is nearly constant for most of the step and then drops in a narrow band at its end. A method's order is a promise about small steps.

## Intuition

A deterministic sampler navigates by compass readings that are expensive to take. Each denoiser call says which way the sample is heading: in these coordinates the path's tangent points straight at D, the network's current guess of the clean image. <!-- L23 --> DDIM takes one reading per step and holds the heading until the next. That is exact while the guess holds still: early, when the guess is the dataset's average, and late, when it is already the final image. It goes wrong in between, where each reading changes the guess. Higher-order solvers spend extra readings inside a step (Heun, DPM-Solver-2 and -3), or reuse the previous one (multistep methods), to estimate how the heading turns. A step schedule decides where the readings are taken. A stochastic sampler drifts off course on purpose with fresh noise every step, which costs accuracy and also erases part of every earlier wrong turn.

The analogy breaks in two places. A compass does not care how you steered, but here the reading depends on the sampler's own mistakes: the network reads the image the sampler made, so a wrong turn changes the next reading. And deliberate drift helps no navigator, because a ship has one port. A sampler's destination is a whole distribution, so noise that knocks it off one path puts it on another valid one.

## Why can the step count change without retraining?

Because the network learned a field, not a chain. It was trained to denoise at a continuum of noise levels, or at a dense grid of them, and a sampler can ask it about any level it likes. Discrete-time models trained on 1,000 levels still give good answers at levels in between, which is how DPM-Solver runs on them. <!-- L19 --> DDIM's authors made the deeper point: the training objective depends only on the marginal distribution at each noise level, not on the chain that connects them, so the same network supports shorter generative processes with no retraining at all. <!-- L04 -->

What cannot shrink freely is the ancestral sampler DDPM shipped with. Its reverse step is a Gaussian, and a Gaussian is the right shape only when the step is small. <!-- L02 --> Cut it to 10 steps on a CIFAR-10 model trained with 1,000, and its FID is 41.07, against 13.36 for deterministic DDIM on the same network. <!-- L06 --> The probability-flow ODE has no such limit: it is a deterministic equation, and any solver accurate enough lands at the same image. DDIM's authors saw the consequence directly. From the same starting noise, samples generated with different step counts share their high-level features, which ancestral samples do not. <!-- L07 --> In the lab, every deterministic solver converges on the same endpoint as its calls grow.

What makes few steps enough is the path's shape. In DDIM's coordinates the tangent always points at the denoiser's current answer, and that answer changes slowly with the noise level, so paths are close to straight lines with their curvature confined to a narrow range of σ. <!-- L23 --> Figure 3 draws the toy's exact paths.

![Exact ODE paths of six crescent samples, straight above σ = 20 and below σ = 5, with DDIM's six-step chords cutting across the bend](FIG_03)

*Figure 3. Measured with the exact denoiser. Above σ ≈ 20 the paths are straight lines aimed at the dataset's average; below σ ≈ 5 they are straight lines aimed at a finished crescent. Between, the sampler is deciding which crescent: its uncertainty falls from 1.35 bits at σ = 20 to 0.01 at σ = 5.*

DDIM with six steps cuts across the bend with straight chords, and lands close anyway, because only one of its six steps, from σ = 24.4 to 5.8, spans it. Real models behave the same way, which is what makes few-step solvers possible at all. One study finds that each sampling path lies almost in a two-dimensional plane; another, that the paths share a regular shape whatever image they produce, and fits the step schedule to that shape. <!-- L41 --> <!-- L40 -->

## What does DDIM actually compute?

DDIM's rule, $`x' = D + \frac{\sigma'}{\sigma}(x - D)`$, goes by several names. It is Euler's method on the ODE above, taking its steps in σ, which is how DDIM's paper derives it. <!-- L05 --> It is EDM's Euler step with the noise schedule σ(t) = t, the same choice. <!-- L23 --> And it is DPM-Solver-1, the first-order member of the DPM-Solver family. <!-- L15 --> diffusers' DDIM scheduler with η = 0 and k-diffusion's `sample_euler` both compute it. <!-- L44 --> <!-- L45 -->

Why does this simple rule work so well? The ODE is **semi-linear**: its right-hand side is a linear term in x plus the denoiser's output, a nonlinear term. For such equations the linear part can be integrated exactly, by the variation-of-constants formula, leaving only an integral of the nonlinear term to approximate. <!-- L13 --> Freezing the nonlinear term at its value at the start of the step gives the **exponential Euler** method, the simplest member of the family numerical analysts call exponential integrators. <!-- L43 --> DDIM is exactly that, with D frozen. It is exact whenever the denoiser's answer does not change across the step, which is what the worked example's factors show at both ends of the path.

The coordinates matter, because the same order of accuracy applied to a different form of the same equation can be far worse. DPM-Solver's authors compared second- and third-order Runge–Kutta methods, applied to the ODE in its original time variable or in log-SNR, with their own solvers of the same order, on one CIFAR-10 model. At 12 calls, second-order Runge–Kutta in time scored FID 16.40, in log-SNR 107.81, and DPM-Solver-2 5.28. <!-- L16 --> Generic Runge–Kutta approximates the linear term too, and because that term's exact solution is an exponential, large steps make its error grow and the method go unstable. <!-- L16 --> EDM's three sampling changes together (Heun's method, its step schedule, and σ(t) = t) cut the calls needed for high-quality samples by 7.3 times for a variance-preserving model and 300 times for a variance-exploding one. <!-- L24 -->

One caution from the toy. Its pixels have nearly unit variance, and for unit-variance Gaussian data the path in the variance-preserving coordinates does not move at all (the [math section](#the-math) shows why). So in this toy, plain Euler steps in the variance-preserving time variable are about as accurate as DDIM on the same grid: the lab measures 160 calls against 200 to reach one grey level. The best coordinates are the ones in which the path is straightest, and that depends on the data's scale.

Figure 4 puts the names in one family.

![Sampler family tree: DDPM ancestral is DDIM at η = 1; DDIM at η = 0 is Euler and DPM-Solver-1; higher-order solvers build on it](FIG_04)

*Figure 4. Six names, two algorithms, and every faster solver built on the first. Each edge says what was added. "Euler a" is DDPM's ancestral chain; "Euler" is DDIM.*

The stochastic side has the same structure. DDIM's paper introduced a parameter η that interpolates between its deterministic sampler, η = 0, and DDPM's ancestral sampler, η = 1, on any subsequence of steps. <!-- L08 --> k-diffusion's "Euler ancestral" computes η = 1: it steps down past the target noise level, to $`\sigma_\text{down} = \sigma'^2/\sigma`$, then adds fresh noise back up to σ′. <!-- L45 --> PNDM's pseudo linear multistep method, PLMS, contains DDIM as its simplest case. <!-- L12 -->

## How do higher-order solvers buy accuracy?

A solver's **order** p says how its error scales with step size h. One step of an order-p method makes a **local** error proportional to $`h^{p+1}`$, and N steps of size h accumulate a **global** error proportional to $`h^p`$. Euler's method, and so DDIM, has local error $`O(h^2)`$ and is first order; Heun's method adds a correction step for local error $`O(h^3)`$, second order, at the cost of one more denoiser call per step. <!-- L21 --> DPM-Solver-k is proved to be of order k. <!-- L14 --> In NFE terms, doubling a p-th-order method's calls divides its error by $`2^p`$, once the steps are small.

Each method buys its order with information about how the denoiser's answer drifts across a step. Figure 5 shows where each one asks.

![One step on a log-SNR axis with a dot per denoiser call: one for DDIM, two for Heun, three for DPM-Solver-3, one reused for 2M](FIG_05)

*Figure 5. One step from σ to σ′. Heun calls the denoiser again at σ′ and averages the two slopes; DPM-Solver-2 calls it at the log-SNR midpoint; DPM-Solver-3 at two inner points. DPM-Solver++(2M) gets the same second-order information for free by reusing the previous step's call.*

The last row is the practical breakthrough. A **singlestep** method like Heun or DPM-Solver-2 spends its extra calls inside each step. A **multistep** method reuses the calls it already made: DPM-Solver++(2M) extrapolates the denoiser's answer from its last two calls, so it is second order at one call per step. For a fixed budget of N calls a multistep method takes N steps where a k-th-order singlestep method takes N/k, so its steps are about k times shorter. <!-- L32 --> DPM-Solver++ also writes the solver in terms of the denoiser's clean-image prediction rather than its noise prediction, which its authors found more stable. <!-- L31 --> UniPC adds a corrector that reuses the next step's call, raising the order by one at no extra cost. <!-- L33 -->

Figure 6 measures all of them against the exact endpoint.

![Log-log error against network calls for five solvers, slopes near 1, 2 and 3; one grey level at 100, 49, 41, 25 and 16 calls](FIG_06)

*Figure 6. Measured: RMS distance from the exact endpoint over 256 shared starting noises, on EDM's ρ = 7 grid. The order appears as the slope once the steps are small: between 200 and 500 calls it is −1.00 for DDIM, −2.02 for Heun, DPM-Solver-2 and DPM-Solver++(2M), and −2.75 for DPM-Solver-3, still steepening.*

The yardstick is one 8-bit grey level, 2/256 of the range of an image scaled to −1 to 1, the same tolerance DPM-Solver's adaptive solver uses for image data. <!-- L20 --> DDIM stays under it from 100 calls, Heun from 49, DPM-Solver-2 from 41, DPM-Solver++(2M) from 25 and DPM-Solver-3 from 16. Between DDIM and the third-order solver that is a factor of six, at an accuracy no one could see.

The published results agree in shape and differ in magnitude, as they should. Figure 7 charts two of DPM-Solver's tables.

![Quoted DPM-Solver FIDs on CIFAR-10: Runge–Kutta in t or λ against DPM-Solver, and five samplers on DDPM's model, 10 to 1,000 calls](FIG_07)

*Figure 7. Quoted from Lu et al., NeurIPS 2022, Tables 1 and 4: FID on CIFAR-10, 50,000 samples. Left, one continuous-time model; right, DDPM's own discrete-time model sampled five ways.*

On DDPM's own CIFAR-10 model, at 10 calls, the ancestral sampler scores FID 278.67, Analytic-DDPM's optimised variance brings that to 35.03, DDIM gets 13.58 and DPM-Solver 6.37; at 1,000 calls the ancestral sampler is best, at 3.16 against DDIM's 3.95. <!-- L18 --> <!-- L11 --> On a continuous-time model, DPM-Solver reaches FID 4.70 at 10 calls and 2.87 at 20. <!-- L17 --> Later solvers, each on its own setup, report UniPC at 3.87 with 10 calls, DPM-Solver-v3 at 2.51 with 10 and 12.21 with 5, and AMED-Solver at 6.61 with 5. <!-- L33 --> <!-- L34 --> <!-- L41 --> None of these is comparable across papers; each is a claim about one model.

Figure 6's left edge is the trap. Below about 10 calls the steps are too large for order to show, and the singlestep methods are worse than DDIM, not better. At 5 calls DDIM's error is 0.18, Heun's 4.2 and DPM-Solver-2's 1.9, and DPM-Solver-3 is still at 0.49 with 10: a step that spans most of the noise range gets its extra slope evaluations from points that have little to do with the path. The multistep DPM-Solver++(2M) matches DDIM at 5 calls and is three times better at 10. Figure 8 shows what the errors look like.

![Crescent samples from four samplers at about 5, 10 and 20 network calls beside the exact endpoints of the same three noises](FIG_08)

*Figure 8. Measured, same three starting noises. At 5 calls Heun leaves noise in the image and DPM-Solver++(2M) a ghost of a second crescent, while DDIM's images are smoother than the exact ones. By 20 calls the deterministic samplers match the exact endpoints.*

## Where should the steps go?

A solver's global error is bounded by its largest local error times a factor that depends on the whole run, so the schedule's job is to keep every step's error small, which means short steps where the path bends and long ones where it is straight. <!-- L25 --> EDM measured the error of single steps at each noise level on a real CIFAR-10 model and found that evenly spaced σ makes very large errors at low noise (a root-mean-square error near 0.56 below σ = 0.5). <!-- L25 --> Its fix is a polynomial spacing,

$$
\sigma_i = \Big(\sigma_\text{max}^{1/\rho} + \tfrac{i}{N-1}\big(\sigma_\text{min}^{1/\rho} - \sigma_\text{max}^{1/\rho}\big)\Big)^{\rho},
$$

where a larger exponent ρ crowds the steps toward the clean end. <!-- L22 --> With ρ = 3 Heun's error per step was almost constant, between 0.0030 and 0.0045; ρ between 5 and 10 gave better images, which says the errors near the clean end matter most for perception. ρ = 7 became the default. <!-- L22 --> <!-- L25 --> diffusers and k-diffusion both hard-code it for what they call Karras sigmas. <!-- L44 --> <!-- L45 -->

Figure 9 repeats EDM's measurement on the toy, with 32 steps per schedule.

![One-step error against noise level for DDIM and Heun under four 32-step schedules, peaking where structure and detail are decided](FIG_09)

*Figure 9. Measured: each point is one step started on the exact path. DDIM's error peaks where the toy decides its crescent and brightness (σ ≈ 10) and again at the scale of its fine detail (σ ≈ 0.1). Evenly spaced σ puts one huge step at the end.*

The toy has structure at two scales, and the peaks sit on them. With ρ = 7 and with log-SNR spacing, DDIM's worst step is near σ = 10, inside the bend of Figure 3; with ρ = 3, which leaves fewer steps at the clean end, its worst step moves to σ ≈ 0.06, where the detail lives. Evenly spaced σ takes 30 of its 32 steps above σ = 2.6 and then jumps to 0.002 in one step, whose error is 0.09 for DDIM and 1.2 for Heun. A schedule cannot remove the bends; it can only decide how many steps each one gets.

Figure 10 turns that into the number that matters, the calls needed to reach one grey level, for every pairing in the lab.

![Network calls each solver needs under five step schedules, beside quoted CIFAR-10 FIDs for log-SNR and optimised steps](FIG_10)

*Figure 10. Left, measured on the toy. The same solver can need five times the calls on a poorly matched schedule, and the multistep DPM-Solver++(2M) sixteen times; on evenly spaced σ only DPM-Solver-3 gets there at all. Right, quoted from Align Your Steps (ICML 2024), Table 5: FID on EDM's CIFAR-10 model.*

Two results stand out. The schedule moves the cost as much as the order does: DPM-Solver-2 needs 41 calls on ρ = 7 and 201 on time-uniform steps. And a schedule with an abrupt change in step size breaks multistep extrapolation, which assumes the last step resembles the next. The time-uniform grid's final step is five to seven times longer in log-SNR than the one before it, and DPM-Solver++(2M) needs 320 calls there against 20 on log-SNR steps.

Hand-made schedules are where recent work found its easiest gains. Align Your Steps optimises the schedule for a given solver, model and dataset: at 10 calls on EDM's CIFAR-10 model it cut DDIM's FID from 16.44 to 10.73 and DPM-Solver++(2M)'s from 5.07 to 2.98. <!-- L38 --> Another method chooses the steps that minimise the distance to the exact ODE solution, the quantity this post measures, and solves for them in under 15 seconds. <!-- L39 --> In the worked example, moving part 5's 50 steps onto a log-SNR grid did the same job by hand, from 0.855 to 0.941.

## Should the sampler add noise?

A stochastic sampler adds fresh noise at every step. DDPM's ancestral sampler is one: score-based modelling showed it is a particular discretisation of the reverse-time SDE. <!-- L09 --> EDM gave the clearest account of what the noise does. Its stochastic equation is the probability-flow ODE plus a Langevin term that removes some noise and adds the same amount back; the Langevin part pulls the sample toward the right distribution at its current noise level, actively correcting errors made in earlier steps, while discretising it adds error of its own, so the right amount of noise is found empirically. <!-- L26 --> Its sampler raises the noise by a factor γ, then takes one Heun step down, with settings tuned per model by grid search. <!-- L27 -->

The cost is order. For the same step size, Euler's method on the ODE makes a local error of order $`h^2`$ while its stochastic counterpart, Euler–Maruyama, makes one of order $`h^{3/2}`$, so deterministic samplers win when steps are large. <!-- L35 --> The benefit is contraction: fresh noise makes the sampler forget part of every earlier error, including the network's own mistakes, which dominate once the steps are small. <!-- L35 --> Theory agrees from the other side. The first polynomial-time guarantees for the probability-flow ODE needed an added stochastic corrector step, because deterministic dynamics lack the contraction the analyses of stochastic samplers rely on. <!-- L37 -->

The toy can show both halves, because its denoiser is exact. Figure 11 starts with a good start and then a bad one.

![Sample detail against calls for deterministic and stochastic samplers; spread on part 5's flawed schedule: 0.357 by ODE, 0.487 by SDE](FIG_11)

*Figure 11. Measured with the exact denoiser. Left: how much fine detail samples carry, divided by the data's; deterministic samplers reach the data's level with fewer calls. Right: part 5's flawed schedule starts sampling from the wrong distribution, and only fresh noise moves the answer toward the right one.*

With a good start, at about 100 calls, DPM-Solver++(2M)'s samples carry 1.005 times the data's fine detail, Heun's 1.019 and DDIM's 0.930, while ancestral sampling's carry 0.861 and EDM's stochastic sampler's 1.092. Each stochastic sampler lands farther from the data than its deterministic counterpart at the same number of calls. With an exact network there are no network errors to forget, so noise has nothing to buy.

Part 5's flawed schedule provides an error to forget. Its last training step is not pure noise, so a sampler that starts from pure noise begins from the wrong distribution. Every deterministic sampler carries that error to the end: the exact ODE keeps 0.357 of the brightness spread, and DDIM and DPM-Solver++(2M) converge on it from 25 steps to 1,000. The exact reverse SDE keeps 0.487, and ancestral sampling climbs toward it: 0.443 at 25 steps, 0.481 at 200, 0.486 at 1,000. The lab measures 0.489, with a standard error of 0.008, on 2,000 full images at 200 steps. Noise recovers a fifth of what the start lost. It cannot recover all of it, because the brightness was decided at noise levels the sampler never visits.

Real models have errors to forget everywhere, and the crossover appears. Figure 12 charts it from two papers.

![Quoted FIDs: Heun, EDM's stochastic sampler, Euler–Maruyama and Restart on ImageNet-64; DDIM at three η values on CIFAR-10](FIG_12)

*Figure 12. Quoted. Left: Xu et al. (NeurIPS 2023), EDM's ImageNet-64 model. Right: DDIM's Table 1, CIFAR-10. In both, the deterministic sampler wins with few calls and a stochastic one wins with many.*

On EDM's ImageNet 64×64 model, Heun's FID is 2.46 at 35 calls and flattens at 2.24 from 255 on. EDM's stochastic sampler is worse at 35 calls, 2.97, already ahead at 63, 2.24 against 2.30, and reaches 1.40 at 1,023; plain Euler–Maruyama is at 59.71 even with 128 calls. <!-- L36 --> Sampler changes alone had already taken that model from FID 2.07 to 1.55. <!-- L29 --> On DDIM's CIFAR-10 model, deterministic DDIM is best at every step count from 10 to 100, but at 1,000 steps DDPM with its larger noise variance scores 3.17 against DDIM's 4.04. <!-- L06 --> Restart sampling builds on exactly this split: it runs the ODE, and in a few chosen intervals repeatedly adds a large amount of noise and runs the ODE back down, keeping the ODE's small errors and the SDE's forgetting; on the ImageNet model it reaches 1.36 at 623 calls. <!-- L35 --> <!-- L36 -->

So noise is worth adding when calls are plentiful and the network is the main source of error, and it must be tuned: EDM found that too much of it slowly erases detail with trained networks, a degradation its experiments with analytic denoisers did not show. <!-- L28 -->

## How should you choose a sampler and a step count?

Measure it. The procedure takes one script:

1. **Count NFE, not steps.** A Heun or DPM-Solver-2 step costs two calls, DPM-Solver-3 three.
2. **Start from a second-order multistep solver** in data-prediction form, DPM-Solver++(2M) or UniPC, on a log-SNR or ρ = 7 schedule. diffusers' multistep DPM-Solver scheduler defaults to DPM-Solver++ at order 2, and falls back to first order on its final steps below 15 steps for stability. <!-- L44 -->
3. **Build a reference.** Fix a few dozen starting noises and run the same sampler at 4 to 10 times your budget. Its output is the target your candidates should land on.
4. **Measure the distance** from each candidate's output to the reference for the same noise, in pixel units, and take the smallest NFE under one grey level, or under whatever tolerance your application can see.
5. **Add noise only for large budgets**, and tune its amount on your model, as EDM did. <!-- L27 -->

If your tool lists samplers by k-diffusion's or diffusers' names, this is what each computes:

| Name | Algorithm | Calls per step | Order | Noise |
|---|---|---:|---:|---|
| DDIM (η = 0), Euler | DDIM = DPM-Solver-1 | 1 | 1 | no |
| Euler ancestral ("Euler a"), DDIM with η = 1 | DDPM's ancestral chain | 1 | — | yes |
| Heun | EDM's second-order method | 2 | 2 | no, unless churn is set |
| DPM2 | DPM-Solver-2 | 2 | 2 | no |
| DPM++ 2M | DPM-Solver++(2M) | 1 | 2 | no |
| UniPC | DPM-Solver++-style predictor plus corrector | 1 | 2–3 | no |
| PLMS | PNDM's pseudo linear multistep | 1 | — | no |
| "Karras" suffix | EDM's ρ = 7 schedule | — | — | — |

<!-- L45 --> <!-- L44 --> <!-- L12 --> <!-- L33 -->

## The math

| Symbol | Meaning |
|---|---|
| $x$ | the sample in DDIM's coordinates, $`x_t/\sqrt{\bar\alpha_t}`$ |
| σ | noise level, $`\sqrt{(1-\bar\alpha_t)/\bar\alpha_t}`$ |
| $D(x;\sigma)$ | the denoiser's estimate of the clean image |
| λ | log-SNR, $`\ln\big(\bar\alpha/(1-\bar\alpha)\big) = -2\ln\sigma`$ |
| $h$ | a step's length in half-log-SNR, $`\ln(\sigma/\sigma')`$ |
| $`V_0`$ | data variance along one Gaussian direction |

DPM-Solver's papers write λ for half the log-SNR, $`\ln(\alpha/\sigma)`$ in their notation; here λ keeps the series' meaning, and h is defined in half-log-SNR units to match their step formulas.

**The exact step.** Write the ODE in $u = \ln\sigma$: $`dx/du = x - D`$. Its linear part integrates exactly, which gives

$$
x(\sigma') = \frac{\sigma'}{\sigma}\,x(\sigma) + \sigma'\int_{\sigma'}^{\sigma} \frac{D\big(x(s);s\big)}{s^2}\,ds .
$$

Every deterministic sampler is a way of approximating that one integral of the denoiser's output. Freeze D at its value at the start and the integral is $`D\,(1 - \sigma'/\sigma)`$, which gives DDIM's $`x' = D + \frac{\sigma'}{\sigma}(x - D)`$ exactly. <!-- L13 -->

<details>
<summary>Second order: where DPM-Solver++(2M)'s coefficients come from</summary>

Let D vary linearly in $`\ell = -\ln s`$ across the step, $`D(\ell) \approx D_i + (\ell - \ell_i)\,D'`$. Substituting into the integral and integrating by parts gives the second-order update $`x' = \frac{\sigma'}{\sigma}x + (1-\frac{\sigma'}{\sigma})\big(D_i + \tfrac{h}{2}D'\big)`$ up to $`O(h^3)`$. A singlestep method estimates $`D'`$ from an extra call inside the step. A multistep method estimates it from the previous call, $`D' \approx (D_i - D_{i-1})/h_{i-1}`$, which turns the bracket into

$$
D_i + \frac{1}{2r}\,(D_i - D_{i-1}), \qquad r = \frac{h_{i-1}}{h_i},
$$

DPM-Solver++(2M)'s $`(1 + \frac{1}{2r})D_i - \frac{1}{2r}D_{i-1}`$. <!-- L32 --> When the previous step was much shorter than this one, r is small and the extrapolation coefficient $`1/(2r)`$ is large: the instability on the time-uniform grid in Figure 10.

</details>

**The Gaussian direction.** For data of variance $`V_0`$ along a direction, $`D = \frac{V_0}{V_0+\sigma^2}x`$, and the ODE becomes $`dx/d\sigma = x\sigma/(V_0+\sigma^2)`$, solved by $`x(\sigma) = c\sqrt{V_0+\sigma^2}`$. One DDIM step multiplies x by

$$
\frac{V_0 + \sigma\sigma'}{V_0 + \sigma^2} \quad\text{where the exact path multiplies it by}\quad \sqrt{\frac{V_0+\sigma'^2}{V_0+\sigma^2}} .
$$

When both σ and σ′ are far below $`\sqrt{V_0}`$, both factors are close to 1; when both are far above it, both are close to σ′/σ. The two disagree only for steps near $`\sqrt{V_0}`$, which is the worked example's table. The same calculation in the variance-preserving coordinates shows why the toy flatters them: there the noisy sample is $`\sqrt{\bar\alpha}\,x_0 + \sqrt{1-\bar\alpha}\,\epsilon`$, which for unit-variance Gaussian data has unit variance at every noise level, so the probability-flow path does not move and Euler's method in that time variable is exact along such a direction.

**Heun's step** averages the slope at the start with the slope at the Euler prediction, $`x' = x + (\sigma'-\sigma)\tfrac12\big(d(x,\sigma) + d(\tilde x,\sigma')\big)`$ with $`d = (x - D)/\sigma`$ and $`\tilde x`$ the Euler prediction. That is the trapezoid rule, accurate to $`O(h^3)`$ per step when the slope is smooth across the step, and badly wrong when the step spans a region where it is not. <!-- L21 -->

**The ancestral step** goes from σ to σ′ in two moves: a DDIM step to $`\sigma_\text{down} = \sigma'^2/\sigma`$, then fresh Gaussian noise of standard deviation $`\sigma_\text{up} = \sigma'\sqrt{1 - \sigma'^2/\sigma^2}`$, which restores the variance of a sample at σ′ because $`\sigma_\text{down}^2 + \sigma_\text{up}^2 = \sigma'^2`$. Converting DDIM's η = 1 noise to these coordinates gives the same two numbers, so the two are one algorithm. <!-- L08 --> <!-- L45 -->

**Calls against tolerance.** If a p-th-order method's error is $`C\cdot\mathrm{NFE}^{-p}`$, the calls needed for tolerance ε are $`(C/\varepsilon)^{1/p}`$. Tightening the tolerance tenfold multiplies a first-order method's calls by 10 and a second-order method's by 3.2, which is why the gap between them widens as the accuracy target rises.

## Implementation

The three deterministic samplers fit in thirty lines over any denoiser `denoise(x, sigma)`. For an ε-prediction network trained on a variance-preserving schedule, that wrapper is `x - sigma * eps_net(x / sqrt(1 + sigma**2), t(sigma))`, where `t(sigma)` is the training timestep whose $`\bar\alpha`$ equals $`1/(1+\sigma^2)`$.

```python
import math
import numpy as np

def karras_sigmas(n, sigma_min=0.002, sigma_max=80.0, rho=7.0):
    ramp = np.linspace(0.0, 1.0, n)
    s = (sigma_max ** (1 / rho) + ramp * (sigma_min ** (1 / rho) - sigma_max ** (1 / rho))) ** rho
    return np.append(s, 0.0)                      # n noise levels, then 0: n steps

def ddim(denoise, x, sigmas):                     # Euler in sigma = DPM-Solver-1; 1 call per step
    for s, s_next in zip(sigmas[:-1], sigmas[1:]):
        d = denoise(x, s)
        x = d + (s_next / s) * (x - d)            # exact if d would not change across the step
    return x

def heun(denoise, x, sigmas):                     # EDM Algorithm 1; 2 calls per step, 1 on the last
    for s, s_next in zip(sigmas[:-1], sigmas[1:]):
        slope = (x - denoise(x, s)) / s
        x_euler = x + (s_next - s) * slope
        if s_next == 0:                           # the corrector would divide by zero
            x = x_euler
        else:
            slope_next = (x_euler - denoise(x_euler, s_next)) / s_next
            x = x + (s_next - s) * 0.5 * (slope + slope_next)
    return x

def dpmpp_2m(denoise, x, sigmas):                 # DPM-Solver++(2M); 1 call per step, second order
    d_prev = h_prev = None
    for s, s_next in zip(sigmas[:-1], sigmas[1:]):
        d = denoise(x, s)
        if s_next == 0:
            return d
        h = math.log(s / s_next)                  # step length in half-log-SNR
        d_use = d if d_prev is None else d + (d - d_prev) * h / (2 * h_prev)
        x = (s_next / s) * x + (1 - s_next / s) * d_use
        d_prev, h_prev = d, h
    return x
```

Measuring a choice is a loop over budgets against one reference:

```python
def error_at_matched_nfe(denoise, shape, budgets=(5, 10, 20, 50), seed=0):
    x_start = 80.0 * np.random.default_rng(seed).standard_normal(shape)   # sigma_max times unit noise
    ref = dpmpp_2m(denoise, x_start, karras_sigmas(500))                   # far beyond any budget below
    for nfe in budgets:
        for name, run, steps in (("DDIM", ddim, nfe), ("Heun", heun, (nfe + 1) // 2),
                                 ("DPM-Solver++(2M)", dpmpp_2m, nfe)):
            out = run(denoise, x_start, karras_sigmas(steps))
            print(f"{nfe:4d} NFE  {name:17s} rms error {np.sqrt(np.mean((out - ref) ** 2)):.2e}")
```

Heun's budget is converted to steps because its N steps cost 2N − 1 calls. The lab's `samplers.py` adds DPM-Solver-2 and -3, the ancestral and EDM stochastic samplers, five schedules, and the exact crescent-world denoiser, and writes every number in this post to `captures.json`; it is under [Lab downloads](#lab-downloads).

## Limitations and common mistakes

> [!WARNING]
> **Common mistake: comparing samplers at equal steps.** Twenty Heun steps make 39 network calls and twenty DDIM steps make 20, so "Heun is better at 20 steps" compares unequal budgets. Plot error or FID against NFE, as every result in this post does.

- **Trusting a method's order at very few calls.** Order describes small steps. In the lab, Heun at 5 calls leaves visible noise in its images, and on part 5's spacing with 25 steps, whose first step spans σ = 4,096 to 52, it returns 12 times the right brightness spread at 49 calls. Below about 10 calls, judge solvers by measurement, not by their order.
- **Running a multistep solver across an abrupt change in step size.** DPM-Solver++(2M) extrapolates from its previous step. On the time-uniform grid, whose last step is five to seven times longer in log-SNR than the one before, its error in the lab is 0.011 at 12 calls and 0.038 at 30, worse with more calls. diffusers drops to first order on its final steps below 15 steps for this reason. <!-- L44 -->
- **Expecting an ancestral sampler to refine its image as steps grow.** Its path is random, so a different step count gives a different image. To compare settings on fixed seeds, use a deterministic sampler, whose images keep their features across step counts. <!-- L07 -->
- **High-order solvers under strong guidance.** DPM-Solver++'s authors found that with large classifier guidance, earlier high-order solvers became unstable and worse than DDIM; data prediction and the multistep form were their fix. <!-- L31 --> Guidance itself is the subject of a later part of this series.
- **Reading the toy's exactness as typical.** A real network is evaluated on the sampler's own imperfect images, not on the noisy data it was trained on, and its prediction errors compound from step to step; this **exposure bias** is invisible in a toy whose denoiser is exact. <!-- L42 --> So are the denoiser flaws EDM blames for its churn's loss of detail. The lab measures the sampler's error alone.
- **Comparing FIDs across papers.** Every quoted number here is one model, one dataset and one sample count. A solver's ranking can change on another model, which is why the procedure above measures your own.

## Key takeaways

- A sampler is a numerical solver for the probability-flow ODE that the trained denoiser defines, so reducing 1,000 steps needs no retraining; DDPM's 1,000 was a property of its Gaussian ancestral step.
- DDIM is Euler's method in the coordinates where paths are straightest, an exponential integrator that is exact whenever the denoiser's answer holds still. Its error is made where the path bends.
- Higher order buys accuracy by learning how the denoiser's answer drifts across a step. Multistep methods such as DPM-Solver++(2M) get second order at one call per step; order pays only once steps are small.
- The step schedule matters as much as the solver: in the lab the same method needed five to sixteen times the calls on a poorly placed grid, and optimised schedules gave the largest recent gains at 10 calls.
- Noise costs accuracy per step and buys forgetting of earlier errors. Deterministic samplers win with few calls; stochastic ones win with many, when the network's own errors dominate.

## Try it yourself

These can be answered from the article alone. The full five-rung ladder, with the lab's own run as the answer key, is in the lab's README under [Lab downloads](#lab-downloads).

### E1 — Reproduce: DDIM's first step from pure noise

Part 5's grid takes its first DDIM step from σ = ∞ to σ = 107.96 on the brightness direction with $`V_0 = 1{,}474.57`$. Compute the fraction of the spread it keeps.

**Self-check:** within 0.001 of the 0.942 in the worked example's table.

<details><summary>Answer</summary>

At σ = ∞ the denoiser returns the mean, 0, so DDIM lands at $107.96\,\epsilon$. The exact path is at $`\sqrt{1{,}474.57 + 107.96^2}\,\epsilon = \sqrt{13{,}130.2}\,\epsilon = 114.59\,\epsilon`$. The fraction kept is $107.96/114.59 = 0.9422$.

</details>

### E2 — Inspect: read an order off Figure 6

From Figure 6, read DPM-Solver++(2M)'s error at about 80 calls and at about 200 calls, and compute the slope of the line between them on log-log axes.

**Self-check:** your slope is between −1.8 and −2.2, the signature of a second-order method.

<details><summary>Answer</summary>

The lab's run gives $`4.8 \times 10^{-4}`$ at 80 calls and $`7.4 \times 10^{-5}`$ at 200. The slope is $`\ln(7.4\times10^{-5}/4.8\times10^{-4})/\ln(200/80) = -1.87/0.916 = -2.04`$.

</details>

### E3 — Predict: DDIM steps for 2% error

DDIM on part 5's grid misses the brightness spread by 14.5% at 50 steps and 7.5% at 100. Before reading the answer, predict how many steps bring the error to 2%.

**Self-check:** within 15% of the lab's step count, with the reason that a first-order method's error falls in proportion to its steps.

<details><summary>Answer</summary>

Error times steps is roughly constant for a first-order method: $0.145 \times 50 = 7.2$ and $0.075 \times 100 = 7.5$, so 2% needs about $7.5/0.02 = 375$ steps. The lab computes 1.99% at 400 steps.

</details>

## References

### Lab downloads

- [`README.md`](LAB_01) — the lab's grade, what was executed, provenance, run order, and the E1–E5 exercise ladder.
- [`samplers.py`](LAB_02) — the exact crescent-world denoiser, eight samplers, five schedules, and every experiment in this post.
- [`requirements.txt`](LAB_03) — the pinned numpy version; nothing else is needed.
- [`captures.json`](LAB_04) — the author's run, machine-readable, which every measured and computed figure was drawn from.
- [`expected-output.txt`](LAB_05) — the same run as printed, to compare against your own.
- [Complete lab](https://minio.canery.in/media/lab-diffusion-samplers-and-solvers.zip) — every file above in one zip.

### Sources

**Surveys and foundations**

1. Yang, Zhang, Song, Hong, Xu, Zhao, Zhang, Cui & Yang. [Diffusion Models: A Comprehensive Survey of Methods and Applications](https://doi.org/10.1145/3626235). ACM Computing Surveys, 2023.
2. Ho, Jain & Abbeel. [Denoising Diffusion Probabilistic Models](https://proceedings.neurips.cc/paper/2020/hash/4c5bcfec8584af0d967f1ab10179ca4b-Abstract.html). NeurIPS 2020.
3. Song, Meng & Ermon. [Denoising Diffusion Implicit Models](https://arxiv.org/abs/2010.02502). ICLR 2021.
4. Song, Sohl-Dickstein, Kingma, Kumar, Ermon & Poole. [Score-Based Generative Modeling through Stochastic Differential Equations](https://arxiv.org/abs/2011.13456). ICLR 2021.
5. Hochbruck & Ostermann. [Exponential integrators](https://doi.org/10.1017/S0962492910000048). Acta Numerica 19, 2010.

**Deterministic solvers**

6. Lu, Zhou, Bao, Chen, Li & Zhu. [DPM-Solver: A Fast ODE Solver for Diffusion Probabilistic Model Sampling in Around 10 Steps](https://doi.org/10.52202/068431-0418). NeurIPS 2022.
7. Lu, Zhou, Bao, Chen, Li & Zhu. [DPM-Solver++: Fast Solver for Guided Sampling of Diffusion Probabilistic Models](https://doi.org/10.1007/s11633-025-1562-4). Machine Intelligence Research, 2025.
8. Karras, Aittala, Aila & Laine. [Elucidating the Design Space of Diffusion-Based Generative Models](https://proceedings.neurips.cc/paper_files/paper/2022/hash/a98846e9d9cc01cfb87eb694d946ce6b-Abstract-Conference.html) (EDM). NeurIPS 2022.
9. Liu, Ren, Lin & Zhao. [Pseudo Numerical Methods for Diffusion Models on Manifolds](https://arxiv.org/abs/2202.09778). ICLR 2022.
10. Zhao, Bai, Rao, Zhou & Lu. [UniPC: A Unified Predictor-Corrector Framework for Fast Sampling of Diffusion Models](https://doi.org/10.52202/075280-2170). NeurIPS 2023.
11. Zheng, Lu, Chen & Zhu. [DPM-Solver-v3: Improved Diffusion ODE Solver with Empirical Model Statistics](https://doi.org/10.52202/075280-2423). NeurIPS 2023.
12. Zhou, Chen, Wang & Chen. [Fast ODE-based Sampling for Diffusion Models in Around 5 Steps](https://doi.org/10.1109/CVPR52733.2024.00743). CVPR 2024.
13. Chen, Zhou, Wang, Shen & Lyu. [On the Trajectory Regularity of ODE-based Diffusion Sampling](https://proceedings.mlr.press/v235/chen24bm.html). ICML 2024.

**Step schedules**

14. Sabour, Fidler & Kreis. [Align Your Steps: Optimizing Sampling Schedules in Diffusion Models](https://proceedings.mlr.press/v235/sabour24a.html). ICML 2024.
15. Xue, Liu, Chen, Zhang, Hu, Xie & Li. [Accelerating Diffusion Sampling with Optimized Time Steps](https://doi.org/10.1109/CVPR52733.2024.00792). CVPR 2024.

**Stochastic samplers**

16. Bao, Li, Zhu & Zhang. [Analytic-DPM: an Analytic Estimate of the Optimal Reverse Variance in Diffusion Probabilistic Models](https://arxiv.org/abs/2201.06503). ICLR 2022.
17. Xu, Deng, Cheng, Tian, Liu & Jaakkola. [Restart Sampling for Improving Generative Processes](https://doi.org/10.52202/075280-3356). NeurIPS 2023.
18. Chen, Chewi, Lee, Li, Lu & Salim. [The probability flow ODE is provably fast](https://doi.org/10.52202/075280-2998). NeurIPS 2023.
19. Ning, Li, Su, Salah & Ertugrul. [Elucidating the Exposure Bias in Diffusion Models](https://proceedings.iclr.cc/paper_files/paper/2024/hash/4267d84ca2f6fbb4aa5172b76b433aca-Abstract-Conference.html). ICLR 2024.

**Implementations** (accessed 2026-10-09)

20. Hugging Face. [diffusers schedulers](https://github.com/huggingface/diffusers/tree/v0.40.0/src/diffusers/schedulers), v0.40.0: `scheduling_dpmsolver_multistep.py`, `scheduling_ddim.py` and `scheduling_heun_discrete.py`.
21. Crowson. [k-diffusion `sampling.py`](https://github.com/crowsonkb/k-diffusion/blob/v0.1.1.post1/k_diffusion/sampling.py), v0.1.1.post1.
22. CompVis. [stable-diffusion `scripts/txt2img.py`](https://github.com/CompVis/stable-diffusion/blob/21f890f9da3cfbeaba8e2ac3c425ee9e998d5229/scripts/txt2img.py), commit 21f890f.
