---
title: "Discrete Diffusion Language Models: Masks, LLaDA, Samplers"
slug: discrete-diffusion-language-models
date: 2026-10-22
updated: 2026-10-22
summary: "Discrete diffusion writes text by unmasking tokens. Its loss is BERT's, weighted 1/t, and it scales to LLaDA 8B, but how you sample it decides what you measure."
tags: [machine-learning, diffusion-model, language-model, discrete-diffusion, masked-diffusion, generative-model]
category: machine-learning
series: diffusion-models
series_position: 11
tier: L3
difficulty: advanced
prerequisites: ["Part 1 of this series", "what a transformer and cross-entropy are"]
reading_minutes: 27
cover_image: "COVER"
canonical_url: "https://canery.in/blogs/discrete-diffusion-language-models"
---

![Four 8 by 8 token grids unmasking a crescent in random order: 16, 32, 48 and all 64 tokens written, masked cells hatched](COVER)

> [!NOTE]
> **Insights** — Yes, you can denoise tokens: a discrete diffusion language model corrupts text by replacing tokens with a [MASK] symbol instead of adding Gaussian noise, and learns to fill the masks back in. Its loss is BERT's masked-token cross-entropy averaged over every masking rate and weighted by 1/t, and it scales: LLaDA 8B, trained from scratch, scores 65.9 on MMLU against LLaMA 3 8B's 65.4. <!-- L45 --> Sampling is the contested half. Writing several tokens per step draws each from its own prediction and breaks the dependencies between them, the decoders behind headline scores keep the most confident guesses rather than sampling the model, and a float32 rounding once made masked diffusion look better than GPT-2 by quietly lowering its temperature.

**Level:** advanced · **You need:** Part 1 of this series (What a Diffusion Model Actually Does), what a transformer and cross-entropy are · **Time:** ~27 min

**Jump to:** [worked example](#worked-example) · [noising a token](#how-do-you-add-noise-to-a-token) · [training](#what-does-a-masked-diffusion-model-learn) · [sampling](#how-does-it-write-and-why-does-parallel-decoding-break) · [LLaDA](#what-do-llada-class-models-deliver) · [the dispute](#why-is-sampler-correctness-contested) · [math](#the-math) · [implementation](#implementation)

> [!IMPORTANT]
> Numbers this post calls **measured** come from its lab: crescent world as tokens, 72 images of 64 tokens over 28 grey levels. Its distribution is known exactly and its denoiser is exact, so every failure belongs to the sampler, never to a badly trained network. Read the toy's sizes as mechanism, not scale. Results **quoted** from papers keep their model, data and protocol, and are compared only within their own table.

## Why this matters

SEDD, a masked diffusion model presented at ICML 2024, reported text whose **generative perplexity** was 6 to 8 times better than unannealed GPT-2's. <!-- L06 --> Generative perplexity (Gen PPL) is the perplexity a separate evaluator, here GPT-2 Large, assigns to a model's samples; lower reads as more fluent, but repetitive text also scores well, so it is reported beside the **entropy** of the tokens within each sample. Zheng et al. then changed only the numerical precision of the sampler's random draws. In 32-bit floating point a run of 2,048 steps scored Gen PPL 31.24 at entropy 5.17; in 64-bit the same model scored 126.11 at entropy 5.66. <!-- L02 --> After the fix the masked models sat near 100 against below 40 for autoregressive models of the same size. <!-- L04 --> The headline evidence that diffusion writes better than GPT-2 came from the sampler, not the model. If you evaluate, compare or deploy a diffusion language model, the sampler's precision, order and tokens per step can move the numbers more than the model does.

## The problem

Part 1's forward step mixes a sample with Gaussian noise: x_t = √ᾱ·x₀ + √(1−ᾱ)·ε. Text has no such sample. A token is an entry in a fixed vocabulary, 50,257 entries for GPT-2's tokenizer and 126,464 for LLaDA's <!-- L09 -->, and its number is a label: 0.8 times one token's number plus noise names some other token that shares nothing with it but a nearby number. The ACM survey of diffusion models puts it plainly: Gaussian perturbation is not a natural fit for discrete data, and the score that continuous samplers follow is defined only on continuous domains. <!-- L08 --> Part 10 of this series, Diffusion Beyond Images: Video, Audio, 3-D and Molecules, met the same wall with atom types and stepped around it by noising one-hot vectors as if they were continuous.

A diffusion model of text has to answer three questions afresh:

1. **Forward process.** What corruption replaces Gaussian noise, so that a fully corrupted sequence carries no information and every intermediate state has a closed form?
2. **Training target.** What does the network predict from a corrupted sequence, and which loss makes the result a model of the data's probability?
3. **Sampling.** The network returns one distribution per position. Text is a joint object, where "New" makes "York" likely, so how do you draw a whole sequence from per-position answers, and how many positions can you draw at once?

The first two have settled answers. The third is where the field disagrees.

## Worked example

Take Part 1's 4×4 patch and round each value to one of four grey levels: below −0.5 is level 0, −0.5 to 0 is level 1, 0 to 0.5 is level 2, and 0.5 or more is level 3. The patch becomes 16 tokens over a four-token vocabulary:

| | col 1 | col 2 | col 3 | col 4 |
|---|---|---|---|---|
| row 1 | 3 | 3 | 1 | 0 |
| row 2 | 3 | 2 | 0 | 0 |
| row 3 | 3 | 2 | 0 | 0 |
| row 4 | 2 | 1 | 0 | 0 |

**Forward step, by masking.** At Part 1's noise level, ᾱ = 0.64, each token survives with probability 0.64 and otherwise becomes [MASK]. Part 1's own noise draw ε decides which: ε is standard normal, so Φ(ε), its normal cumulative probability, is uniform, and "masked when Φ(ε) exceeds 0.64" is the same as "masked when ε exceeds 0.3585". Seven of the 16 values do (1.40, 0.45, 0.85, 0.70, 1.25, 0.90 and 1.45), so seven tokens are hidden; 16 × 0.36 = 5.76 is the expectation. **By uniform replacement** instead, each token is redrawn uniformly with probability 0.36, so it stays itself with probability 0.64 + 0.36/4 = 0.73 and becomes each other level with probability 0.09. Figure 1 shows both. A mask announces what it hid; a replaced token looks like any other.

![Part 1's patch as 16 grey-level tokens, Part 1's noise draw marking 7 of them masked at abar 0.64, and uniform replacement's odds](FIG_01)
*Figure 1. The same forward step on categories: masking hides 7 tokens and says which, while uniform replacement keeps each token with probability 0.73 and hides its changes among real tokens. Computed.*

**A world to denoise against.** Let the data be this patch in its four quarter turns, each with probability 1/4, a miniature of crescent world's four orientations. The exact denoiser simply counts: of the turns that agree with every visible token, how many put each value at each hidden position? With the nine tokens Figure 1 leaves visible, only the upright turn agrees, because no other turn has a 3 in the top-left corner. The seven hidden tokens are certain, and the loss on them is zero; training earns its loss in states where little is visible.

**Decoding from all 16 masked** (Figure 2). The four turns hold 3, 0, 0 and 2 in the top-left corner, so the denoiser predicts level 0 with probability 1/2 and levels 2 and 3 with 1/4 each. Drawn one token at a time, the first draw narrows four turns to one or two: a top-left 0 leaves two turns, and the top-right corner then decides between them with probability 1/2. That path costs ln 2 + ln 2 nats, a 3 in the top-left costs ln 4 at once, and in every order the costs add to ln 4 = 1.386 nats, the information in "which of four turns".

![Four quarter turns of the patch, per-position probabilities with all 16 masked, decoding one token at a time, and one all-at-once draw](FIG_02)
*Figure 2. Each position's prediction is exactly right, and drawing the positions one at a time is exact; drawing them all at once mixes turns and almost never yields one. Computed.*

Drawn all at once, each position from its own prediction, the 16 tokens form a real turn with probability 3.81 × 10⁻⁶. Two at once already fail. The top-left and bottom-right corners both have prediction {0: 1/2, 2: 1/4, 3: 1/4}, but only four pairs occur in the world: (3, 0), (0, 2), (0, 3) and (2, 0). Drawn independently, the corners form one of those pairs half the time; a quarter of the time both come out 0, a dark-dark pair that no turn has.

## Intuition

A masked diffusion model solves a crossword. Every blank gets a best guess from the letters already in, you ink some guesses, and you guess again. Fill one blank at a time and every guess sees the ones before it. Fill a whole region at once and two guesses that each fit their own clue can clash where they cross, which is the corners' dark-dark pair. The analogy breaks in one place: a crossword has one right answer, while a language model must draw one of many good answers in proportion to its probability. So "ink the surest blank first" is not neutral. It changes which answer comes out, and that is the dispute this post ends on.

## How do you add noise to a token?

D3PM, the framework most discrete diffusion builds on, writes a forward step on categories as a **transition matrix**: entry (i, j) is the probability that token i becomes token j in one step, and the marginal after many steps is a product of these matrices, available in closed form for the simple choices. <!-- L10 --> D3PM tried four. Uniform transitions, from multinomial diffusion <!-- L11 -->, replace a token with a random one. Absorbing transitions send it to [MASK] and keep it there. A discretized Gaussian moves ordinal tokens such as grey levels to nearby levels, and a nearest-neighbour matrix moves words toward words with similar embeddings. <!-- L10 -->

Masking won, and by a wide margin. On LM1B, D3PM's absorbing model reached a perplexity bound of 76.9 against 137.9 for uniform and 149.5 for nearest neighbours; a transformer of the same size reached 43.6. <!-- L12 --> SEDD's zero-shot table, Figure 3, repeats the ranking on five datasets at GPT-2 small's size. <!-- L13 --> One reason is visible in Figure 1: a mask tells the network exactly which positions are unknown, while under uniform replacement the network must also decide which visible tokens to trust.

![Zero-shot perplexity of GPT-2 small, SEDD absorbing, SEDD uniform, D3PM and Plaid on five datasets; absorbing beats uniform on all five](FIG_03)
*Figure 3. Masking beats uniform replacement on every dataset, and a GPT-2-sized masked model beats GPT-2 on three of five. Diffusion values are upper bounds. Quoted from Lou et al. 2024, Table 1.*

MDLM builds on masking because, among discrete forward processes, it had consistently performed best. <!-- L14 --> The other road, diffusing continuous embeddings of tokens as Diffusion-LM does, needs a rounding step to map vectors back to words <!-- L16 --> and paid in compute: Plaid 1B beat GPT-2 124M on likelihood, but needed about 64 times the compute of an equivalent autoregressive model. <!-- L17 --> Masked diffusion's gap, in a similar scaling study, is about 16 times. <!-- L18 -->

## What does a masked diffusion model learn?

Reverse a masking step and only one thing is unknown. Going from noise level t back to s, a hidden token stays hidden with probability (1 − ᾱ_s)/(1 − ᾱ_t) and otherwise becomes its clean value; a visible token stays as it is. <!-- L19 --> From the worked example's ᾱ = 0.64 to ᾱ = 0.8, each hidden token is revealed with probability (0.8 − 0.64)/(1 − 0.64) = 0.444. The network supplies a distribution for "its clean value", and MDLM, a 2024 simplification, builds in two facts: it never predicts [MASK], and it copies visible tokens unchanged. <!-- L20 -->

With those two facts the training objective collapses. The ELBO, the variational bound that Part 3 of this series, Where the Diffusion MSE Loss Comes From, derives for Gaussian diffusion, becomes a weighted average of **masked language modelling** losses: cross-entropy on the hidden tokens only, the task BERT is pre-trained on, and its value does not depend on the schedule's shape. <!-- L21 --> LLaDA's version is the plainest. Draw t uniformly between 0 and 1, mask each token with probability t, and weight the hidden tokens' cross-entropy by 1/t; the result bounds the negative log-likelihood. <!-- L22 --> Figure 4 traces one step at LLaDA's sizes.

![One LLaDA training step: draw t, mask 4,096 tokens, a transformer without a causal mask, cross-entropy on masked tokens times 1/t](FIG_04)
*Figure 4. BERT's loss at every masking rate, weighted by 1/t: about tL tokens are hidden at rate t, so every rate carries the same expected weight, L token losses. Shapes from LLaDA's configuration.*

BERT masks a fixed 15% of positions (80% of them become [MASK], 10% a random token, 10% stay) <!-- L23 -->, so BERT trains one point of this curve, and D3PM noted that its objective is a one-step discrete diffusion. <!-- L15 --> Training every rate is what turns a fill-in-the-blank model into a generator.

The best possible network does not need t at all: the right prediction depends only on which tokens are visible, and the bound can be written over the number of hidden tokens n with weight 1/n. <!-- L24 --> In that form it is the average, over all reveal orders, of an autoregressive loss, which makes a masked diffusion model an **any-order autoregressive model**: one network for every left-to-right, right-to-left or scattered order at once. <!-- L25 --> SEDD reached the same place from another side. It learns ratios between the probabilities of neighbouring sequences, the discrete analogue of the score <!-- L26 -->, and for masking those ratios are the clean-token predictions times a factor that depends only on time. <!-- L25 -->

For an exact denoiser the bound is the true likelihood, which the lab checks: for each of its 72 images and 64 random orders, the per-token costs add to −log p(image) within 8.9 × 10⁻¹⁶ nats, as they added to ln 4 in the worked example. A trained network has no such guarantee, and the bound is loose. On OpenWebText after 262B training tokens, MDLM's bound was perplexity 23.21 against 17.54 for a retrained autoregressive model and 24.10 for SEDD. <!-- L27 -->

## How does it write, and why does parallel decoding break?

MDLM samples ancestrally. From t to s, each hidden token is revealed with probability (t − s)/t under the linear schedule ᾱ_t = 1 − t, drawn from the network's prediction for its position; revealed tokens never change, and the network is called again only when something changed. <!-- L28 --> A **network call**, one forward pass, is the cost unit, the NFE of Part 6 of this series, Diffusion Samplers and Solvers: 1,000 Steps Into 20.

Every token revealed in the same step is drawn from its own prediction, so the step samples from the product of the positions' marginals instead of their joint, which would need each draw conditioned on the others. <!-- L31 --> Revealing one token per call avoids this. Zheng et al.'s **first-hitting sampler** reveals one uniformly chosen hidden token per call and is exactly the continuous-time reverse process <!-- L29 -->, but then a sequence of L tokens costs L calls, with no speed-up over writing left to right.

The lab measures what the product of marginals costs (Figure 5). Crescent world as tokens has 72 images: four crescents, faint or strong, at nine brightness levels, each pixel rounded to one of 28 grey levels. Revealing one token per call in random order, every sample is one of the 72 images in the world's own proportions: all 72 appear, and the brightness spread is 0.276 against the world's 0.278. Two tokens per call leave 17.9% of samples valid, four leave 0.34%, and eight or more leave none. MDLM's ancestral sampler with 64 steps for 64 tokens is itself a parallel decoder: 63.1% of its tokens are revealed in a step that reveals another, and 51.9% of its samples are valid. With 1,024 steps the share falls to 6.0% and validity rises to 95.8%, at 63.0 calls thanks to caching.

![Share of valid images against network calls: one token per call is exact; 2, 4 and 8 per call fail; ancestral steps; a threshold](FIG_05)
*Figure 5. Each prediction is exact, yet writing several tokens per call breaks the samples; a certainty threshold recovers exact samples in about 7 calls in this toy. Measured, 4,096 images per sampler.*

The reason is how late the image is decided. In a random order the image is fixed only after a median of 4 tokens, and 8 at the 90th percentile; until then the hidden tokens depend on each other through the crescent's orientation, contrast and brightness. A **certainty threshold** uses this: reveal every position the denoiser is certain about at once, and otherwise only the single surest one. In the toy it produced valid samples in the world's proportions in 7.2 calls, because once the image is decided every remaining token is certain. Text is never that certain, and the toy is also a worst case the other way: every one of its tokens shares the image's brightness.

A real model degrades the same way. In the survey's test, Figure 6, LLaDA's 128-token answer to a math problem was right with 2 tokens per step, wrong with 4, and incoherent with 16. <!-- L35 -->

![LLaDA and MMaDA answers to one prompt at several step counts: correct with 1 or 2 tokens per step, wrong or garbled with more](FIG_06)
*Figure 6. LLaDA's answer is right at 2 tokens per step and wrong at 4; MMaDA's is right only at 1. Reproduced unchanged from Li, Chen, Guo & Shen, "A Survey on Diffusion Language Models" (arXiv:2508.10875, v3), Figure 7, [arXiv:2508.10875](https://arxiv.org/abs/2508.10875), licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).*

Theory says when parallel decoding is safe and when it cannot be. Fast-dLLM proved that if each of n tokens has a prediction above 1 − ε with (n + 1)ε at most 1, greedy decoding of the n tokens together picks the same tokens as greedy decoding of their joint <!-- L32 -->, and built a decoder on that threshold that, with an approximate key-value cache, ran up to 27.6 times faster on LLaDA and Dream. <!-- L33 --> Feng et al. separated two targets. Near-optimal per-token error, the kind perplexity tracks, needs a number of steps independent of length, but a low **sequence error rate**, the share of whole outputs that are wrong, can need steps that grow with length. <!-- L34 --> The lab's valid share is one minus its sequence error rate.

## What do LLaDA-class models deliver?

LLaDA 8B is the reference point. It was trained from scratch on 2.3T tokens with 0.13M H800 GPU hours at sequence length 4,096, then fine-tuned on 4.5M prompt-response pairs. It has no causal mask and uses plain multi-head attention, because it cannot use a **KV cache**: an autoregressive model stores the keys and values of tokens it has written and reuses them, but in a bidirectional model every written token's representation changes as masks are filled. <!-- L44 --> Figure 7 sets it against LLaMA 3 8B under one protocol.

![LLaDA 8B Base against LLaMA 3 8B Base on 15 benchmarks: ahead on math and Chinese, behind on BBH, HellaSwag, PIQA and MBPP](FIG_07)
*Figure 7. LLaDA leads on MMLU, math and Chinese and trails on reasoning, commonsense and MBPP, after 2.3T training tokens against LLaMA 3's 15T. Quoted from Nie et al. 2025, Table 1.*

It leads on MMLU (65.9 against 65.4), GSM8K (70.3 against 48.7), Math (31.4 against 16.0) and the Chinese CMMLU (69.9 against 50.7), and trails on BBH (49.7 against 62.1), HellaSwag (70.5 against 79.1), PIQA (73.6 against 80.6) and MBPP (40.0 against 48.8); its authors attribute part of both gaps to training data. <!-- L45 --> How the numbers were made matters. MMLU-style tasks score each candidate answer by Monte Carlo likelihood, and generation tasks decode with low-confidence remasking, one token per step, 1,024 steps for 1,024 tokens. <!-- L43 --> Bidirectional training shows in one place: completing the line before a given line of a Chinese poem, LLaDA scored 45.6 against GPT-4o's 34.3, though GPT-4o led forward, 82.7 against 51.8. <!-- L46 -->

The costs are real. Masked diffusion needed about 16 times an autoregressive model's compute for the same validation loss up to 10²⁰ FLOPs <!-- L18 -->; LLaDA's authors answer that likelihood is an indirect target and extend scaling to 10²³ FLOPs. <!-- L47 --> Without a cache, LLaDA still matched LLaMA 3 on GSM8K and Math at 1.5 and 1.8 times its throughput, with LLaMA 3 using a cache. <!-- L48 --> The output length is fixed before sampling. <!-- L54 -->

The field has since moved toward hybrids. Autoregressive checkpoints convert: DiffuLLaMA adapted models up to 7B with under 200B tokens <!-- L49 -->, and Dream 7B starts from Qwen2.5 7B and trains on 580B. <!-- L50 --> **Block diffusion** writes blocks left to right and runs diffusion inside each block, which restores the KV cache and lifts the fixed length. <!-- L51 --> Commercial systems lead with speed: Inception's Mercury Coder models reached 1,109 and 737 tokens/s on H100 GPUs in independent measurements <!-- L52 -->, and Google DeepMind's experimental Gemini Diffusion reports 1,479 tokens/s excluding 0.84 s of overhead, its architecture undisclosed and its scores on both sides of Gemini 2.0 Flash-Lite's. <!-- L53 -->

## Why is sampler correctness contested?

### Decoders that do not sample

LLaDA's paper notes that remasking should in principle be random, then keeps the most confident predictions and re-masks the rest, as MaskGIT did for images, and predicts each token greedily. <!-- L36 --> <!-- L39 --> Mask-Predict did the same for translation in 2019. <!-- L38 --> With one token per step, its own ablation (Figure 8) moved GSM8K from 21.3 with random positions to 70.0 with the most confident ones; the authors liken the effect to annealed sampling in autoregressive models, which gains accuracy by losing diversity. <!-- L37 -->

![LLaDA 8B Base with random against low-confidence remasking: BBH, GSM8K, Math, HumanEval and MBPP all rise with low confidence](FIG_08)
*Figure 8. Keeping the most confident predictions instead of random ones raised all five tasks, GSM8K by 48.7 points; the model is the same in both rows. One token per step, 256 tokens. Quoted from Nie et al. 2025, Table 9.*

The lab separates two things this mixes (Figure 9). With exact predictions, the order is not the problem: ranking positions by how sure the denoiser is of each, one token per step, still gives exact samples, 72 images with brightness spread 0.281. What breaks sampling is ranking by the probability of the token just drawn, which is what LLaDA's released code does when its temperature is above zero <!-- L55 -->: it keeps draws that happened to land on likely values. In the toy, brightness collapsed to its commonest level and only 8 of 72 images ever appeared. Greedy decoding in random order produced 23 images; greedy with confidence ranking, LLaDA's default <!-- L55 -->, produced 4, every one faint and at middle brightness.

![Images found of 72 and brightness spread for five one-token-per-step decoders with sample tiles; ranking by the drawn token collapses](FIG_09)
*Figure 9. Ranking positions by certainty keeps the samples exact; ranking by the drawn token's probability, or decoding greedily, loses most of the 72 images. Measured, 4,096 images per decoder.*

For a benchmark with one right answer, returning a mode is defensible, but it means the numbers describe a decoder, not the model's distribution, and the likelihood bound the model was trained on says nothing about that decoder. The order also interacts with what a trained network learned: choosing the next position by the margin between its two likeliest values raised a masked model's Sudoku accuracy from below 7% to about 90%, because a masked model trains on every fill-in subproblem, some of them computationally intractable, and a good order sidesteps the hard ones. <!-- L40 -->

### A temperature hidden in float32

The **Gumbel-max trick** samples a category by perturbing each log-probability with Gumbel noise and taking the largest; MDLM and SEDD use an equivalent race, the largest q/E with E = −log u for a uniform u. <!-- L07 --> In float32, u can be at most 1 − 2⁻²⁴, so E is never smaller than about 6 × 10⁻⁸ and the largest Gumbel value is 16.6355. <!-- L01 --> MDLM's step pits [MASK], with weight s, against each token, with weight p(t − s). With many steps a token's weight is tiny next to the mask's, which is exactly where float32 cannot resolve the race.

The lab runs the race in both precisions (Figure 10). In float64 a token with weight c against the mask's 1 wins its fair share, c, at every c. In float32 it wins a share x/(eˣ − 1) of it, with x = 2⁻²⁴/c: 73.2% at c = 10⁻⁷, 1.5% at 10⁻⁸, and less than half below c = 4.74 × 10⁻⁸. At the first step of a 1,000-step run that line sits at a token probability of 4.74 × 10⁻⁵, and with GPT-2's 50,257 tokens an even share is 1.99 × 10⁻⁵, below it. The sampler draws early tokens from the head of each distribution, which lowers the temperature.

![Share of its fair chance a token wins MDLM's race against the mask, float32 against float64, with the closed form and Zheng's ablation](FIG_10)
*Figure 10. Float32 starves tokens whose weight falls below a fixed line, and more of them the more steps a run takes; Zheng et al.'s ablation shows the same fault in a real sampler. Measured, plus quoted from Zheng et al. 2025, Table 2.*

With the original samplers, masked models' Gen PPL crossed below the autoregressive model's at about 2,000 steps while their entropy kept falling, reaching Gen PPL below 15 near 50,000 steps. <!-- L03 --> This part is settled: later work from MDLM's own group and LLaDA's released sampler draw in float64, citing Zheng et al. <!-- L05 -->

### What a metric can certify

Gen PPL alone cannot separate fluency from repetition. ReMDM's authors, whose sampler lets decoded tokens be masked again and revised <!-- L41 -->, found that a corrector schedule could push Gen PPL to 1.5 by repeating one word, and reported MAUVE instead. <!-- L42 --> Part 9 of this series, Evaluating Generative Models: What FID Measures and Hides, makes the same point about images: one number hides a trade-off. What remains contested is not the bug but the rest: whether gains measured with greedy, most-confident-first decoders belong to the model, and how many tokens per step text can bear.

## The math

| Symbol | Meaning |
|---|---|
| $x_0$, $x_t$ | clean sequence of $L$ tokens; the same sequence with some tokens masked |
| $\mathrm{m}$ | the mask token |
| $\bar\alpha_t$ | probability that a token is still visible at time $t$; here $\bar\alpha_t = 1 - t$ |
| $p_\theta(\cdot \mid x_t)$ | the network's prediction of a hidden token's clean value |
| $n$ | number of masked tokens |

Each token is masked independently:

$$
q(x_t^i = x_0^i) = \bar\alpha_t, \qquad q(x_t^i = \mathrm{m}) = 1 - \bar\alpha_t \tag{1}
$$

The worked example used $\bar\alpha = 0.64$: seven of sixteen tokens masked. Going back from $t$ to $s$, a masked token is revealed with probability

$$
\frac{\bar\alpha_s - \bar\alpha_t}{1 - \bar\alpha_t} \tag{2}
$$

and keeps its mask otherwise; with the linear schedule this is $(t - s)/t$, and from 0.64 to 0.8 it is 0.444. The training loss, with $t$ drawn uniformly from 0 to 1:

$$
\mathcal{L} = \mathbb{E}_{t,\,x_0,\,x_t}\!\left[\frac{1}{t}\sum_{i:\,x_t^i = \mathrm{m}} -\log p_\theta(x_0^i \mid x_t)\right] \tag{3}
$$

The cross-entropy counts only hidden tokens, and the weight $1/t$ makes a lightly masked sequence, with few hidden tokens, weigh as much in total as a heavily masked one. Written over the number of hidden tokens instead of time,

$$
\mathcal{L} = \sum_{n=1}^{L} \mathbb{E}_{x_n}\!\left[\frac{1}{n}\sum_{i:\,x_n^i = \mathrm{m}} -\log p_\theta(x_0^i \mid x_n)\right] \tag{4}
$$

the inner average is the expected cost of the next token in a uniformly random reveal order, so equation (4) is the average over orders of an autoregressive loss. For the exact denoiser every order costs $-\log p(x_0)$, ln 4 for each of the worked example's turns, so the bound is tight.

Two tokens revealed in one step are drawn from $p(x^i \mid x_t)\,p(x^j \mid x_t)$, while the data needs

$$
p(x^i, x^j \mid x_t) = p(x^i \mid x_t)\, p(x^j \mid x_t, x^i) \tag{5}
$$

For the worked example's two corners the product puts probability 1/4 on a dark-dark pair that the joint gives 0.

<details>
<summary>Why float32 gives a token a share x/(eˣ − 1) of its chance</summary>

Give [MASK] weight 1 and a token weight $c$; the token wins when $c/E_{\text{tok}} > 1/E_{\text{mask}}$, so with probability $c$ when $c$ is small. In float32 the uniform below 1 takes the values $1 - j\,2^{-24}$, so $E_{\text{tok}} = -\log u$ takes the values $j\,2^{-24}$ near zero, each with probability $2^{-24}$. The token wins when $j\,2^{-24} \lt c\,E_{\text{mask}}$, with $E_{\text{mask}}$ exponential, so its chance is $2^{-24}\,\mathbb{E}\lfloor c\,E_{\text{mask}}\,2^{24}\rfloor = 2^{-24}/(e^{x} - 1)$ with $x = 2^{-24}/c$. Divided by $c$ that is $x/(e^{x}-1)$: near 1 for large $c$, one half at $x = 1.2564$, and exponentially small as $c$ falls further. The lab's race matches it to within 0.007 at every $c$ it tried.

</details>

## Implementation

The forward step and three decoders, for one sequence and a denoiser output `p` of shape (L, V):

```python
import numpy as np

rng = np.random.default_rng(0)

def mask_forward(x0, abar, mask_id):                 # equation (1)
    return np.where(rng.random(x0.shape) < abar, x0, mask_id)

def draw(p):                                         # one token per row, by inverse CDF
    return (p.cumsum(1) < rng.random((len(p), 1))).sum(1)

def ancestral_step(x, p, t, s, mask_id):             # MDLM, linear schedule: equation (2)
    reveal = (x == mask_id) & (rng.random(len(x)) < (t - s) / t)
    return np.where(reveal, draw(p), x)

def first_hitting_step(x, p, mask_id):               # one uniformly chosen masked token per call
    i = rng.choice(np.flatnonzero(x == mask_id))
    x = x.copy(); x[i] = draw(p[i:i + 1])[0]
    return x

def low_confidence_step(x, p, k, mask_id):           # LLaDA's default: greedy tokens, keep the k surest
    x0, sure = p.argmax(1), p.max(1)
    sure[x != mask_id] = -np.inf
    keep = np.argsort(-sure)[:k]
    x = x.copy(); x[keep] = x0[keep]
    return x
```

`ancestral_step` decides reveals with float64 uniforms and draws each token from `p` itself, so no token races the mask at weight p(t − s): it has none of the float32 fault. The lab's `tokens.py` adds the 72-image world and its exact denoiser, every sampler in this post, and the race in both precisions, and runs in two minutes on one core; see [Lab downloads](#lab-downloads).

## Limitations and common mistakes

> [!WARNING]
> **Common mistake: reporting Gen PPL without entropy and the sampler's settings.** Repetition scores well: in ReMDM's tests a corrector schedule reached Gen PPL 1.5 by repeating one word <!-- L42 -->, and a float32 sampler scored 31.24 where the same model in float64 scored 126.11. <!-- L02 --> State the precision, steps, temperature, order and tokens per step, and report entropy beside Gen PPL.

- **Reading benchmark scores as samples from the model.** LLaDA's generation scores come from greedy, most-confident-first decoding at one token per step, and its multiple-choice scores from likelihood estimates. <!-- L43 --> <!-- L36 --> Random positions gave GSM8K 21.3 against 70.0. <!-- L37 -->
- **Assuming parallel decoding is free.** In the toy two tokens per call left 17.9% of samples valid, and LLaDA's answer in Figure 6 failed at four per step. Threshold on certainty instead of fixing a count.
- **Comparing perplexities across processes and papers.** Diffusion perplexities are bounds, and Gen PPL changes with the evaluator, the sampling settings and the precision.
- **Reading the toy as typical.** Crescent world as tokens has 72 images and one brightness shared by all 64 tokens: a worst case for parallel decoding and a best case for certainty thresholds, since its tokens become certain once the image is decided. Text is neither, and an exact denoiser hides every training error.

## Key takeaways

- A discrete diffusion language model replaces Gaussian noise with masking; its loss is BERT's masked-token cross-entropy averaged over masking rates with weight 1/t, a likelihood bound that is tight for an exact denoiser.
- Exact per-position predictions do not make a sampler exact: drawing several hidden tokens at once ignores their dependence, and a certainty threshold, not a fixed count, decides how many are safe.
- LLaDA-class models are competitive with autoregressive models of their size on many benchmarks, but LLaDA's generation scores come from a greedy decoder that returns modes, not from sampling the model.
- Check samplers against something known: a float32 rounding lowered masked diffusion's temperature and made it look better than GPT-2.

## Try it yourself

These can be answered from the article alone. The full exercise ladder, with the lab's own run as the answer key, is in the lab's README under [Lab downloads](#lab-downloads).

### E1 — Reproduce: the corners

All 16 tokens of the four-turn world are masked. Draw the top-left and bottom-right corners at once, each from its own prediction. Compute the probability that the pair occurs in some turn, and the probability that both come out 0.

**Self-check:** 1/2 and 1/4.

<details><summary>Answer</summary>

Both corners have prediction {0: 1/2, 2: 1/4, 3: 1/4}. The pairs that occur are (3, 0), (0, 2), (0, 3) and (2, 0), with product probabilities 1/8 each, so 4 × 1/8 = 1/2. Both 0 has probability 1/2 × 1/2 = 1/4 under the product and 0 in the world, because no turn is dark in both corners.

</details>

### E3 — Predict: adjacent corners

Before computing, predict whether drawing the top-left and top-right corners at once does better or worse than the opposite corners. Then compute it.

**Self-check:** better, 9/16 = 0.5625, because the product's likeliest pair is now a real one.

<details><summary>Answer</summary>

The top-right corner holds 0, 0, 2 and 3 across the turns, so its prediction is also {0: 1/2, 2: 1/4, 3: 1/4}. The pairs that occur are (3, 0), (0, 0), (0, 2) and (2, 3), with product probabilities 1/8, 1/4, 1/8 and 1/16, which add to 9/16. The dark-dark pair, the product's likeliest at 1/4, now occurs in the world, because one turn is dark in both corners, so less of the product falls outside it.

</details>

## References

### Lab downloads

- [`README.md`](LAB_01) — the lab's grade, what was executed, provenance, run order, and the E1–E4 exercise ladder.
- [`tokens.py`](LAB_02) — crescent world as tokens with its exact denoiser, the worked example, every sampler in this post, and the float32 race, in numpy.
- [`requirements.txt`](LAB_03) — the pinned numpy version.
- [`captures.json`](LAB_04) — the author's run, machine-readable, which every measured figure was drawn from.
- [`expected-output.txt`](LAB_05) — the same run as printed, to compare against your own.
- [`notebook.ipynb`](LAB_06) — the README with a runnable cell under each step and exercise.
- [Complete lab](https://minio.canery.in/media/lab-discrete-diffusion-language-models.zip) — every file above in one zip.

### Sources

**Surveys**

1. Yang, Zhang, Song, Hong, Xu, Zhao, Zhang, Cui & Yang. [Diffusion Models: A Comprehensive Survey of Methods and Applications](https://doi.org/10.1145/3626235). ACM Computing Surveys, 2023.
2. Li, Chen, Guo & Shen. [A Survey on Diffusion Language Models](https://arxiv.org/abs/2508.10875). Preprint, 2025.

**Discrete diffusion**

3. Austin, Johnson, Ho, Tarlow & van den Berg. [Structured Denoising Diffusion Models in Discrete State-Spaces](https://arxiv.org/abs/2107.03006) (D3PM). NeurIPS 2021.
4. Hoogeboom, Nielsen, Jaini, Forré & Welling. [Argmax Flows and Multinomial Diffusion: Learning Categorical Distributions](https://arxiv.org/abs/2102.05379). NeurIPS 2021.
5. Lou, Meng & Ermon. [Discrete Diffusion Modeling by Estimating the Ratios of the Data Distribution](https://arxiv.org/abs/2310.16834) (SEDD). ICML 2024.
6. Sahoo, Arriola, Schiff, Gokaslan, Marroquin, Chiu, Rush & Kuleshov. [Simple and Effective Masked Diffusion Language Models](https://arxiv.org/abs/2406.07524) (MDLM). NeurIPS 2024.
7. Shi, Han, Wang, Doucet & Titsias. [Simplified and Generalized Masked Diffusion for Discrete Data](https://arxiv.org/abs/2406.04329) (MD4). NeurIPS 2024.
8. Ou, Nie, Xue, Zhu, Sun, Li & Li. [Your Absorbing Discrete Diffusion Secretly Models the Conditional Distributions of Clean Data](https://arxiv.org/abs/2406.03736) (RADD). ICLR 2025.
9. Zheng, Chen, Mao, Liu, Zhu & Zhang. [Masked Diffusion Models are Secretly Time-Agnostic Masked Models and Exploit Inaccurate Categorical Sampling](https://arxiv.org/abs/2409.02908). ICLR 2025.

**Masked language models and their decoders**

10. Devlin, Chang, Lee & Toutanova. [BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding](https://doi.org/10.18653/v1/N19-1423). NAACL 2019.
11. Ghazvininejad, Levy, Liu & Zettlemoyer. [Mask-Predict: Parallel Decoding of Conditional Masked Language Models](https://doi.org/10.18653/v1/D19-1633). EMNLP 2019.
12. Chang, Zhang, Jiang, Liu & Freeman. [MaskGIT: Masked Generative Image Transformer](https://doi.org/10.1109/CVPR52688.2022.01103). CVPR 2022.

**Continuous embeddings**

13. Li, Thickstun, Gulrajani, Liang & Hashimoto. [Diffusion-LM Improves Controllable Text Generation](https://arxiv.org/abs/2205.14217). NeurIPS 2022.
14. Gulrajani & Hashimoto. [Likelihood-Based Diffusion Language Models](https://arxiv.org/abs/2305.18619) (Plaid). NeurIPS 2023.

**Large models**

15. Nie, Zhu, You, Zhang, Ou, Hu, Zhou, Lin, Wen & Li. [Large Language Diffusion Models](https://arxiv.org/abs/2502.09992) (LLaDA). NeurIPS 2025.
16. Nie, Zhu, Du, Pang, Liu, Zeng, Lin & Li. [Scaling up Masked Diffusion Models on Text](https://arxiv.org/abs/2410.18514). ICLR 2025.
17. Gong, Agarwal, Zhang, Ye, Zheng, Li, An, Zhao, Bi, Han, Peng & Kong. [Scaling Diffusion Language Models via Adaptation from Autoregressive Models](https://arxiv.org/abs/2410.17891) (DiffuLLaMA). ICLR 2025.
18. Ye, Xie, Zheng, Gao, Wu, Jiang, Li & Kong. [Dream 7B: Diffusion Large Language Models](https://arxiv.org/abs/2508.15487). Preprint, 2025.
19. Arriola, Gokaslan, Chiu, Yang, Qi, Han, Sahoo & Kuleshov. [Block Diffusion: Interpolating Between Autoregressive and Diffusion Language Models](https://arxiv.org/abs/2503.09573). ICLR 2025.
20. Inception Labs. [Mercury: Ultra-Fast Language Models Based on Diffusion](https://arxiv.org/abs/2506.17298). Preprint, 2025.
21. Google DeepMind. [Gemini Diffusion](https://deepmind.google/models/gemini-diffusion/). Model page, accessed 2026-10-22.

**Sampling**

22. Wu, Zhang, Xue, Liu, Diao, Zhu, Luo, Han & Xie. [Fast-dLLM: Training-free Acceleration of Diffusion LLM by Enabling KV Cache and Parallel Decoding](https://arxiv.org/abs/2505.22618). ICLR 2026.
23. Kim, Shah, Kontonis, Kakade & Chen. [Train for the Worst, Plan for the Best: Understanding Token Ordering in Masked Diffusions](https://arxiv.org/abs/2502.06768). ICML 2025.
24. Feng, Geng, Guan, Wu, Wang & He. [Theoretical Benefit and Limitation of Diffusion Language Model](https://arxiv.org/abs/2502.09622). NeurIPS 2025.
25. Wang, Schiff, Sahoo & Kuleshov. [Remasking Discrete Diffusion Models with Inference-Time Scaling](https://arxiv.org/abs/2503.00307) (ReMDM). NeurIPS 2025.

**Code**

26. MDLM's sampler: [`diffusion.py`](https://github.com/kuleshov-group/mdlm/blob/b886f9f1d523faa62d484aa6985730c17163bc18/diffusion.py) at commit b886f9f.
27. SEDD's categorical sampler: [`catsample.py`](https://github.com/louaaron/Score-Entropy-Discrete-Diffusion/blob/0605786da5ccb5747545e26d66fdf477187598b6/catsample.py) at commit 0605786.
28. LLaDA's sampler: [`generate.py`](https://github.com/ML-GSAI/LLaDA/blob/f2683fd9cd10721f2853bafa52f8572ae8155d0c/generate.py) at commit f2683fd.
