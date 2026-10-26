---
social_schema: 2
canonical_url: "https://canery.in/blogs/discrete-diffusion-language-models"
---

# Social publishing package — discrete-diffusion-language-models

## LinkedIn post

For about a year, the headline evidence that diffusion could write better text than GPT-2 came from a sampler, not a model. Changing only the precision of the sampler's random numbers, from 32-bit to 64-bit, moved one masked diffusion model's generative perplexity from 31.24 to 126.11 (Zheng et al., ICLR 2025).

Discrete diffusion language models replace Gaussian noise with a [MASK] symbol and learn to fill the masks back in. The training half is settled; the sampling half is not. Measured in a toy whose true distribution and denoiser are known exactly, and quoted from papers with their setup:

→ Right predictions, wrong samples. With an exact denoiser, writing two tokens per network call left 17.9% of samples valid.
→ Noise a token by hiding it. Masking beat uniform replacement on every dataset in SEDD's zero-shot table.
→ BERT's loss, at every rate. The loss is masked-token cross-entropy weighted by 1/t, and LLaDA 8B was trained this way on 2.3T tokens.
→ Two at once can clash. MDLM's own sampler with 64 steps for 64 tokens produced 51.9% valid samples.
→ Same model, different decoder. LLaDA's GSM8K moved from 21.3 to 70.0 when its decoder kept the most confident predictions instead of random ones.
→ Most confident first stops sampling. Ranking positions by the token just drawn found 8 of the toy's 72 images.
→ Float32 lowered the temperature. Unlikely tokens almost never win the sampler's race in 32-bit floats.

The toy's sizes are mechanism, not scale; published results keep their model, dataset and protocol.

Part 11 of the Diffusion Models series.

## LinkedIn first comment

How masked diffusion turns BERT's loss into a text generator, and why its samplers decide what its numbers mean, with a numpy lab that runs in about two minutes.

Read the full article on Canery: https://canery.in/blogs/discrete-diffusion-language-models

## Instagram caption

Can you denoise tokens instead of pixels? Yes: replace tokens with a [MASK] symbol and train a network to fill them back in. The loss is BERT's, at every masking rate, and LLaDA scaled it to 8B parameters.

Swipe through a denoiser whose predictions are exact and whose samples still break, a token noised by hiding it, the training loss, two tokens that clash when drawn together, one model scored with two decoders, a confidence rule that stops sampling, and a float32 rounding that lowered the temperature.

Every measured number comes from a lab you can run on a laptop in about two minutes; published results are quoted with their setup.

Link in bio.

#generativeai #machinelearning #deeplearning #diffusionmodels #languagemodels #llm #nlp

## Shared feed order

1. `assets/social/feed-01-right-predictions-wrong-samples.png` — with an exact denoiser, one token per call gives valid samples and two per call breaks most of them
2. `assets/social/feed-02-noise-a-token-by-hiding-it.png` — the worked example: Part 1's patch as 16 tokens, masked at ᾱ = 0.64 by Part 1's own noise draw
3. `assets/social/feed-03-berts-loss-at-every-rate.png` — the training loss: masked cross-entropy weighted by 1/t, against BERT's fixed rate
4. `assets/social/feed-04-two-at-once-can-clash.png` — two corners drawn at once form a pair no turn has; valid samples fall with tokens per call
5. `assets/social/feed-05-same-model-different-decoder.png` — LLaDA's ablation: random against low-confidence remasking on five tasks
6. `assets/social/feed-06-most-confident-first-stops-sampling.png` — one-token-per-call decoders: ranking by position certainty stays exact, by the drawn token collapses
7. `assets/social/feed-07-float32-lowered-the-temperature.png` — Zheng et al.'s precision ablation and the lab's race between [MASK] and one token
8. `assets/social/feed-08-read-the-article.png` — five things to check in a diffusion language model claim, and the call to read the article

## Instagram Story

Not produced: this part ships feed cards only, as Parts 8, 9 and 10 did at the owner's request (2026-10-19), so there are no Story frames, Story CTA or link sticker to post.

### Story order

None.

## Asset metadata

### feed-01-right-predictions-wrong-samples

- File: `assets/social/feed-01-right-predictions-wrong-samples.png`
- Title: Right predictions, wrong samples
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: an exact denoiser's samples are valid when it writes one token per call and mostly broken when it writes two
- Technical source: How does it write, and why does parallel decoding break?; Figure 5; lab decode stage
- Visual structure: lockup and counter; serif title; deck; two rows of four 8×8 token images, the top written one token per call and each marked "one of the 72", the bottom written two per call with three marked "not an image"; each row's valid share in large type at right; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 08 · Right predictions, wrong samples. · A masked diffusion model whose every prediction is exact still writes broken images when it fills in two tokens per network call. · ONE TOKEN PER CALL · one of the 72 (four times) · VALID SAMPLES · 100% · TWO TOKENS PER CALL · not an image · not an image · not an image · one of the 72 · VALID SAMPLES · 17.9% · The joint is what parallel decoding breaks, not the predictions. Crescent world as tokens, 4,096 images per sampler. · DISCRETE DIFFUSION LANGUAGE MODELS · CANERY.IN
- Alt text: Two rows of four token images of crescents: one token per call, all valid, 100%; two per call, three broken, 17.9% valid
- Long description: Cover card. Crescent world as tokens: 72 images of 64 tokens over 28 grey levels, with an exact denoiser, so every prediction is the true conditional probability. The top row shows four samples written one token per network call, all of them real images; 100% of 4,096 samples are valid. The bottom row shows four samples written two tokens per call; three are not any of the 72 images and one is, and 17.9% of 4,096 samples are valid. The takeaway: the joint is what parallel decoding breaks, not the predictions.
- Keywords: masked diffusion, parallel decoding, discrete diffusion, language model sampling, crescent world
- Canonical URL: https://canery.in/blogs/discrete-diffusion-language-models

### feed-02-noise-a-token-by-hiding-it

- File: `assets/social/feed-02-noise-a-token-by-hiding-it.png`
- Title: Noise a token by hiding it
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Gaussian noise means nothing for a category, so discrete diffusion masks tokens; the worked example's 16 tokens masked by Part 1's own noise draw
- Technical source: Worked example; Figure 1; lab worked stage
- Visual structure: lockup and counter; serif title; deck; a 4×4 grid of grey-level tokens, an arrow, and the same grid with seven cells hatched and marked M; three explanatory lines; a boxed rule saying which tokens to hide; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 08 · Noise a token by hiding it. · Text is categories, so diffusion swaps Gaussian noise for a [MASK] symbol. Part 1's patch, rounded to four grey levels, shows how. · PART 1'S PATCH AS 16 TOKENS · 3 3 1 0 / 3 2 0 0 / 3 2 0 0 / 2 1 0 0 · MASKED AT ᾱ = 0.64: 7 OF 16 HIDDEN · 3 M M 0 / M 2 0 M / M 2 0 0 / 2 M M 0 · Gaussian noise on a token is meaningless: level 3 plus noise is no token. Masking hides a token and says which one it hid; uniform replacement keeps it with 0.73 and hides its changes. · WHICH TOKENS TO HIDE · part 1's own noise draw: hidden where ε > 0.3585, Φ(ε) > 0.64 · Masking beat uniform replacement on every dataset in SEDD's zero-shot table, and later work built on masking. · DISCRETE DIFFUSION LANGUAGE MODELS · CANERY.IN
- Alt text: A 4 by 4 grid of grey-level tokens and the same grid with 7 cells masked, chosen by Part 1's noise draw at abar 0.64
- Long description: Part 1's 4×4 patch rounded to four grey levels gives 16 tokens: 3 3 1 0, 3 2 0 0, 3 2 0 0, 2 1 0 0. At ᾱ = 0.64 each token survives with probability 0.64; Part 1's own noise draw decides which, masking a token where ε exceeds 0.3585, so that Φ(ε) exceeds 0.64. Seven tokens are hidden. Uniform replacement would instead keep each token with probability 0.73 and hide its changes among real tokens. In SEDD's zero-shot table, masking beat uniform replacement on every dataset.
- Keywords: masked diffusion, absorbing state, discrete diffusion, forward process, tokens
- Canonical URL: https://canery.in/blogs/discrete-diffusion-language-models

### feed-03-berts-loss-at-every-rate

- File: `assets/social/feed-03-berts-loss-at-every-rate.png`
- Title: BERT's loss, at every rate
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the masked diffusion loss is masked-token cross-entropy weighted by 1/t, averaged over every masking rate; for an exact denoiser it is the true likelihood
- Technical source: What does a masked diffusion model learn?; Figure 4; equation (3); lab world stage
- Visual structure: lockup and counter; serif title; deck; a boxed formula; three rows comparing BERT, LLaDA and the weight; an accent line on the lab's order check; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 08 · BERT's loss, at every rate. · Mask each token with probability t, predict the hidden ones, and weight their cross-entropy by 1/t: a bound on the likelihood. · THE TRAINING LOSS · (1/t) × Σ hidden −log p(true token) · BERT · one fixed rate: 15% of positions · LLaDA · every rate t from 0 to 1, weight 1/t · the weight · about tL tokens hidden: every rate weighs L · exact denoiser: every reveal order of 72 images costs −log p(image) to 8.9 × 10⁻¹⁶ nats · Training every rate turns a fill-in-the-blank model into a generator. LLaDA 8B was trained this way on 2.3T tokens. · DISCRETE DIFFUSION LANGUAGE MODELS · CANERY.IN
- Alt text: The masked diffusion loss, (1/t) times the summed cross-entropy of hidden tokens, compared with BERT's fixed 15% rate
- Long description: The training loss of a masked diffusion language model: draw t between 0 and 1, mask each token with probability t, and weight the cross-entropy of the hidden tokens by 1/t. About tL tokens are hidden at rate t, so every rate carries the same expected weight, L token losses. BERT trains one fixed rate, 15% of positions; LLaDA trains every rate. The loss bounds the negative log-likelihood, and for an exact denoiser it equals it: in the lab every reveal order of each of 72 images costs −log p(image) to within 8.9 × 10⁻¹⁶ nats. LLaDA 8B was trained this way on 2.3T tokens.
- Keywords: masked language modeling, BERT, ELBO, LLaDA, cross-entropy, masked diffusion loss
- Canonical URL: https://canery.in/blogs/discrete-diffusion-language-models

### feed-04-two-at-once-can-clash

- File: `assets/social/feed-04-two-at-once-can-clash.png`
- Title: Two at once can clash
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: tokens drawn in the same step come from their separate predictions, so dependent tokens can disagree; valid samples fall as tokens per call rise
- Technical source: Worked example (the corners); How does it write, and why does parallel decoding break?; Figure 5; lab worked and decode stages
- Visual structure: lockup and counter; serif title; deck; a box with the corners example; four bars of valid share for one, two, four and eight tokens per call; takeaway; footer
- Visible-text transcript: Canery.in · 04 / 08 · Two at once can clash. · Each hidden token is drawn from its own prediction. Drawn together, two tokens that depend on each other can come from different answers. · TWO OPPOSITE CORNERS OF THE FOUR-TURN WORLD, DRAWN AT ONCE · each corner alone: 0 with 1/2, 2 with 1/4, 3 with 1/4 · a real pair 0.50 of the time; both 0 (0.25) is a pair no turn has · CRESCENT WORLD AS TOKENS: VALID SAMPLES · one per call 100% · two per call 17.9% · four per call 0.34% · eight per call 0% · MDLM's own sampler at 64 steps for 64 tokens revealed 63% of tokens alongside another: 51.9% of its samples were valid. · DISCRETE DIFFUSION LANGUAGE MODELS · CANERY.IN
- Alt text: Corners drawn together form a real pair half the time; valid samples fall from 100% at one token per call to 0% at eight
- Long description: In the four-turn world each opposite corner, alone, is 0 with probability 1/2 and 2 or 3 with 1/4 each. Drawn at once from their separate predictions, they form a pair that some turn has half the time, and a quarter of the time both are 0, which no turn has. In crescent world as tokens, the share of valid samples is 100% at one token per call, 17.9% at two, 0.34% at four and 0% at eight. MDLM's ancestral sampler with 64 steps for 64 tokens revealed 63% of tokens alongside another, and 51.9% of its samples were valid.
- Keywords: parallel decoding, product of marginals, masked diffusion sampling, MDLM, sequence error
- Canonical URL: https://canery.in/blogs/discrete-diffusion-language-models

### feed-05-same-model-different-decoder

- File: `assets/social/feed-05-same-model-different-decoder.png`
- Title: Same model, different decoder
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: LLaDA's own ablation shows its decoder, not its model, moving scores by tens of points
- Technical source: Why is sampler correctness contested? (Decoders that do not sample); Figure 8; ledger L37
- Visual structure: lockup and counter; serif title; deck; paired bars for BBH, GSM8K, Math, HumanEval and MBPP, random in slate and low-confidence in tangerine; legend; takeaway; footer
- Visible-text transcript: Canery.in · 05 / 08 · Same model, different decoder. · LLaDA's ablation kept either random predictions or the most confident ones each step. The model did not change; the scores did. · LLADA 8B BASE · ONE TOKEN PER STEP, 256 TOKENS · QUOTED · BBH 32.1 45.0 · GSM8K 21.3 70.0 · Math 9.2 30.3 · HumanEval 11.6 32.9 · MBPP 21.0 40.2 · random positions · most confident positions · GSM8K went from 21.3 to 70.0. Headline scores describe the decoder, which the authors liken to annealed sampling: accurate, less diverse. · DISCRETE DIFFUSION LANGUAGE MODELS · CANERY.IN
- Alt text: Paired bars for LLaDA 8B Base on five tasks: random remasking against low-confidence remasking, GSM8K 21.3 against 70.0
- Long description: Quoted from Nie et al., Large Language Diffusion Models (NeurIPS 2025), Table 9: LLaDA 8B Base generating 256 tokens in 256 steps, one token per step. Keeping random predictions each step against keeping the most confident ones: BBH 32.1 against 45.0, GSM8K 21.3 against 70.0, Math 9.2 against 30.3, HumanEval 11.6 against 32.9, MBPP 21.0 against 40.2. The model is the same in both; the authors liken the low-confidence decoder to the annealed sampling autoregressive models use, gaining accuracy by losing diversity.
- Keywords: LLaDA, remasking, low-confidence remasking, decoding strategy, GSM8K, diffusion language model
- Canonical URL: https://canery.in/blogs/discrete-diffusion-language-models

### feed-06-most-confident-first-stops-sampling

- File: `assets/social/feed-06-most-confident-first-stops-sampling.png`
- Title: Most confident first stops sampling
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: with exact predictions the order of decoding is harmless; ranking by the drawn token's probability, or decoding greedily, collapses the samples onto a few images
- Technical source: Why is sampler correctness contested? (Decoders that do not sample); Figure 9; lab decode stage
- Visual structure: lockup and counter; serif title; deck; four rows, each a decoder's name, images found and brightness spread, with four sample tiles at right; the world's own spread; takeaway; footer
- Visible-text transcript: Canery.in · 06 / 08 · Most confident first stops sampling. · With exact predictions the order is harmless. Ranking by the token just drawn keeps lucky draws, and brightness collapses. · ONE TOKEN PER CALL · IMAGES FOUND OF 72 · BRIGHTNESS SPREAD · random order, sampled · 72 images · spread 0.276 · surest position first · 72 images · spread 0.281 · likeliest draw first · 8 images · spread 0.000 · surest first, greedy · 4 images · spread 0.000 · the world's own spread: 0.278 · LLaDA's default decoder, greedy and most confident first, returned 4 of the toy's 72 images, all faint and at one brightness. · DISCRETE DIFFUSION LANGUAGE MODELS · CANERY.IN
- Alt text: Four decoders at one token per call: 72, 72, 8 and 4 of 72 images found, with sample crescent tiles for each
- Long description: Crescent world as tokens, 4,096 images per decoder, one token per network call, exact denoiser. Random order with sampled tokens finds all 72 images with brightness spread 0.276; ranking positions by how sure the denoiser is finds all 72 with spread 0.281, against the world's own 0.278. Ranking by the probability of the token just drawn finds 8 images, all at one brightness; greedy decoding with that ranking, LLaDA's default, finds 4, all faint and at one brightness.
- Keywords: decoding order, confidence ranking, greedy decoding, mode collapse, masked diffusion, LLaDA
- Canonical URL: https://canery.in/blogs/discrete-diffusion-language-models

### feed-07-float32-lowered-the-temperature

- File: `assets/social/feed-07-float32-lowered-the-temperature.png`
- Title: Float32 lowered the temperature
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: MDLM's and SEDD's samplers race [MASK] against every token, and in float32 unlikely tokens almost never win, which lowered the temperature and the measured perplexity
- Technical source: Why is sampler correctness contested? (A temperature hidden in float32); Figure 10; ledger L02; lab precision stage
- Visual structure: lockup and counter; serif title; deck; a box with Zheng et al.'s 32-bit and 64-bit results; four lines on the lab's race; takeaway; footer
- Visible-text transcript: Canery.in · 07 / 08 · Float32 lowered the temperature. · MDLM's and SEDD's samplers race [MASK] against every token each step. In float32 unlikely tokens almost never win, so diversity quietly falls. · ZHENG ET AL. · ONLY THE SAMPLING CODE CHANGED · QUOTED · 32-bit · Gen PPL 31.24 · entropy 5.17 · 64-bit · Gen PPL 126.11 · entropy 5.66 · lower perplexity, lower entropy: a lower temperature · THE LAB'S RACE: [MASK] AGAINST ONE TOKEN · weight 1e-8 of the mask's: float32 wins 1.5% of its fair chance · float32 halves a token's chance below c = 4.74 × 10⁻⁸ · at step 1 of 1,000 that is a token probability of 4.74e-05; an even share of GPT-2's 50,257 tokens, 1.99e-05, is below it · Masked diffusion looked better than GPT-2 on generative perplexity until the sampler ran in float64. Later codebases sample in float64. · DISCRETE DIFFUSION LANGUAGE MODELS · CANERY.IN
- Alt text: 32-bit sampling gave Gen PPL 31.24 and entropy 5.17, 64-bit 126.11 and 5.66; in float32 a rare token wins 1.5% of its fair chance
- Long description: Quoted from Zheng et al. (ICLR 2025), Table 2: changing only the categorical sampling code, 8 samples of 2,048 steps scored generative perplexity 31.24 at entropy 5.17 in 32-bit and 126.11 at entropy 5.66 in 64-bit; lower perplexity with lower entropy is a lower temperature. The lab runs the race between [MASK] and one token: at a weight of 10⁻⁸ of the mask's, a float32 race gives the token 1.5% of its fair chance, and float32 halves a token's chance below 4.74 × 10⁻⁸. At the first step of a 1,000-step run that is a token probability of 4.74 × 10⁻⁵, and an even share of GPT-2's 50,257 tokens, 1.99 × 10⁻⁵, is below it.
- Keywords: float32, Gumbel-max, numerical precision, generative perplexity, temperature, MDLM, SEDD
- Canonical URL: https://canery.in/blogs/discrete-diffusion-language-models

### feed-08-read-the-article

- File: `assets/social/feed-08-read-the-article.png`
- Title: What to check in a diffusion LM claim
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: five things to check before comparing a diffusion language model's numbers, and the call to read the article
- Technical source: Limitations and common mistakes; Key takeaways
- Visual structure: lockup and counter; serif title; deck; a box listing precision, tokens per step, decoder, metric and protocol, each with one line; takeaway; call to action in place of the footer
- Visible-text transcript: Canery.in · 08 / 08 · What to check in a diffusion LM claim. · Masked diffusion writes text by unmasking tokens. The model is half the story; the sampler is the other half. · Precision · float32 races [MASK] against tiny weights; use float64 · Tokens per step · two at once can clash; threshold on certainty · Decoder · greedy, most confident first is not sampling the model · Metric · report entropy beside generative perplexity · Protocol · likelihood-scored or generated, and at how many steps · Ask how it was sampled before you compare it. · READ IT AT CANERY.IN/BLOGS/DISCRETE-DIFFUSION-LANGUAGE-MODELS
- Alt text: A checklist for diffusion language model claims: precision, tokens per step, decoder, metric and protocol
- Long description: Closing card. Five things to check in a diffusion language model claim: precision, because a float32 sampler races [MASK] against tiny token weights and should be float64; tokens per step, because two tokens drawn at once can clash, so threshold on certainty; the decoder, because greedy, most-confident-first decoding is not sampling the model; the metric, because generative perplexity needs entropy beside it; and the protocol, whether a score was likelihood-scored or generated, and at how many steps. The takeaway: ask how it was sampled before you compare it.
- Keywords: diffusion language models, evaluation, sampling, generative perplexity, LLaDA, masked diffusion
- Canonical URL: https://canery.in/blogs/discrete-diffusion-language-models
