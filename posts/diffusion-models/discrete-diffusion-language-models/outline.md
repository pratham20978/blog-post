# Outline — Discrete Diffusion Language Models: Masks, LLaDA, Samplers

Series `diffusion-models`, part 11 of 12 (`series_position: 11`). Private build artifact.

## Brief

- **Answers (plan.md):** can you denoise tokens instead of pixels?
- **Owns:** masked and discrete diffusion, LLaDA-class models, why sampler correctness is contested.
- **Tier:** L3 (plan: 6,500 words, 10 figures). Four things to learn: how to corrupt a category (masking
  beats uniform replacement), why the loss is BERT's averaged over masking rates with weight 1/t, why
  sampling several tokens per step breaks dependencies, and why the samplers behind headline numbers are
  contested (decoders that do not sample, a float32 race that lowered the temperature). The smallest honest
  worked example (Part 1's patch as 16 tokens, its four quarter turns as a world) fits on one screen; the
  mechanisms need a section each. Adjacent option: L4 with a full section on block diffusion and remasking
  samplers and an E5.
- **Difficulty:** advanced. Assumes Part 1 (forward step, ᾱ, the four moving parts), what a transformer and
  cross-entropy are, and Part 3's idea of an ELBO (named, not re-derived). Adjacent option: intermediate,
  which would drop the any-order derivation and the precision closed form.
- **Can assume:** Part 1 (published). **Names in plain text:** Part 3 (the ELBO), Part 6 (DDIM steps and
  NFE), Part 7 (few-step samplers), Part 8 (guidance weight), Part 9 (why one metric hides a trade-off),
  Part 10 (atom types as one-hot vectors; the survey's discrete-data class). **Defers:** memorisation and
  provenance to "later in this series", unnamed.
- **Lab:** G1 · runs anywhere. One numpy file, `tokens.py`, on crescent world as tokens: the series' four
  crescents, faint or strong, at nine brightness levels, each pixel rounded to one of 28 grey levels, so
  exactly 72 images of 64 tokens and an exact denoiser that is a lookup. Stages: `worked` (Part 1's patch),
  `world` (any-order likelihood check), `decode` (12 samplers, 4,096 images each), `precision` (MDLM's
  Gumbel race in float32 and float64). About two minutes on one core. L3 ladder: E1–E4. No access request
  (`../access.md`: G0–G1 planned for part 11).
- **Social:** feed cards only, as for parts 8–10 (owner, 2026-10-19).

## Section budget (target about 6,900 in the validator's count, references included)

| Section | Target | Job |
|---|---|---|
| Insights + who + notice + jump list | 230 | the answer: mask tokens and predict them; BERT's loss weighted 1/t; LLaDA 8B at scale; sampling is where it is contested |
| Why this matters | 170 | SEDD's 6–8× better Gen PPL than GPT-2; Zheng et al.: switch float32 to float64 and Gen PPL goes 31.24 → 126.11, entropy 5.17 → 5.66 |
| The problem | 380 | a token is a category: 0.8 × "cat" + 0.6 ε is not a word; vocabularies 50,257 and 126,464; three questions: how to corrupt, what to predict, how to sample a joint from per-position outputs |
| Worked example | 600 | Part 1's patch as 4 grey levels; masked at ᾱ = 0.64 with Part 1's ε (7 of 16); uniform alternative (0.73 stay); the four-turn world: exact denoiser by counting; corners at once 50% valid; all 16 at once 3.81 × 10⁻⁶; any order costs ln 4 (FIG_01, FIG_02) |
| Intuition | 260 | a crossword filled by several people at once; where the analogy breaks |
| How do you add noise to a token? | 500 | D3PM's matrices; uniform vs absorbing; absorbing wins (D3PM LM1B, SEDD Table 1; FIG_03); continuous embeddings (Diffusion-LM, Plaid's 64×) |
| What does a masked diffusion model learn? | 520 | posterior; SUBS; loss = weighted masked-LM losses, 1/t; BERT's fixed 15%; time-agnostic; any-order AR; the lab's order check; SEDD's ratios = RADD's conditionals; perplexity gap (FIG_04) |
| How does it write, and why does parallel decoding break? | 650 | ancestral sampler; first-hitting; product of marginals; lab: valid share vs calls, ancestral 64 vs 1,024 steps, threshold (FIG_05); survey's Figure 7 (FIG_06); Fast-dLLM theorem; Feng et al. |
| What do LLaDA-class models deliver? | 520 | LLaDA's recipe and Table 1 (FIG_07); reversal poems; 16× compute; no KV cache; throughput; AR initialization (DiffuLLaMA, Dream); block diffusion; Mercury, Gemini Diffusion |
| Why is sampler correctness contested? | 700 | decoders vs samplers: LLaDA Table 9 (FIG_08), lab (FIG_09), Mask-Predict and MaskGIT, Kim et al.; the float32 race (FIG_10, lab + Zheng); Gen PPL needs entropy; what is settled and what is not |
| The math | 420 | symbols; forward marginal; posterior; NELBO with linear schedule; discrete form with 1/n and the any-order identity on the worked example; the race and x/(eˣ − 1) in a details block |
| Implementation | 250 | numpy: forward masking, MDLM's update, first-hitting, LLaDA's low-confidence selection |
| Limitations and common mistakes | 300 | warning: Gen PPL without entropy and sampler settings; four mistakes |
| Key takeaways | 110 | four claims |
| Try it yourself | 220 | E1 and E3 answerable from the article |
| References | ~1,100 | lab downloads + 25 sources |

## Figure plan (route gate run per figure)

| # | Section | One thing it must communicate | Route | Why (the clause that settled it) | Draft caption |
|---|---|---|---|---|---|
| FIG_01 | Worked example | Part 1's patch as 4-level tokens, masked at ᾱ = 0.64 by Part 1's ε (7 of 16), against uniform replacement (each token stays with 0.73) | placed | Q4 — a grid of real tokens and the ε grid that decides the masks, side by side | masking marks what it hid; uniform replacement hides it among real tokens |
| FIG_02 | Worked example | the four-turn world: marginals when all 16 are masked; one token at a time decides the turn in one or two tokens; all at once mixes turns | placed | Q4 — small multiples of real token grids and probabilities | the network's per-position answers are right; drawing them together is not |
| FIG_03 | How do you add noise to a token? | absorbing beats uniform on every zero-shot set (SEDD Table 1), with GPT-2 and Plaid in the same table | chart | Q1 — quoted numbers from one table (L13) | masking beats uniform replacement everywhere; a GPT-2-sized masked model is close to GPT-2 |
| FIG_04 | What does a masked diffusion model learn? | one training step: draw t, mask, a transformer with no causal mask sees all 4,096 positions, cross-entropy on masked positions only, weight 1/t; LLaDA's shapes | placed | Q5 — 6 nodes in one path, a tensor shape or formula on every edge | BERT's loss at every masking rate, with weight 1/t |
| FIG_05 | How does it write? | valid share against network calls: one per step exact; 2/4/8 per step fall; ancestral 64/256/1,024 steps; a certainty threshold exact at ~7 calls | chart | Q1 — lab measurements, 4,096 images per sampler | the joint is the problem, not the marginals |
| FIG_06 | How does it write? | LLaDA's answer correct at 2 tokens per step, wrong at 4, garbled at 16; MMaDA likewise | source | source check — the survey's own Figure 7 is the failure on a real 8B model, CC BY 4.0 (ledger F1) | Reproduced from Li et al. 2025, Figure 7 |
| FIG_07 | What do LLaDA-class models deliver? | LLaDA 8B Base against LLaMA3 8B Base on 15 benchmarks, one protocol | chart | Q1 — quoted numbers from one table (L45) | wins on math and Chinese, losses on reasoning and commonsense; 2.3T vs 15T tokens |
| FIG_08 | Why is sampler correctness contested? | LLaDA 8B Base, random against low-confidence remasking, five tasks | chart | Q1 — quoted numbers from one table (L37) | the decoder, not the model, moves GSM8K from 21.3 to 70.0 |
| FIG_09 | Why is sampler correctness contested? | decoders one token per step: images found (of 72) and brightness spread for random, position-ranked, drawn-ranked, greedy, greedy drawn-ranked, with sample tiles | chart | Q1 — lab measurements, 4,096 images per decoder | ranking by the drawn token's probability, or decoding greedily, stops sampling |
| FIG_10 | Why is sampler correctness contested? | float32's race gives a token a share x/(eˣ − 1) of its fair chance; the line for N-step runs; Zheng et al.'s ablation | chart | Q1 — lab measurements and quoted numbers (L02) | the bug lowered temperature and raised the metric |
| COVER | — | the series' house template cover | placed | template cover, as parts 6–10 | — |

## Term map

| Term | First section | What | Why used here | When it matters |
|---|---|---|---|---|
| token, vocabulary | The problem | a category from a fixed list: a word piece, or a grey level | the data is categorical | any language model |
| absorbing ([MASK]) vs uniform corruption | Worked example | replace a token with a mask symbol, or with a random token | the two forward processes for categories | choosing the forward process |
| transition matrix | How do you add noise | the per-step probability of each token becoming each other token (D3PM) | the general form | designing a discrete process |
| masked language model (MLM), BERT | What does it learn | a network trained to predict hidden tokens from the rest | the loss is an MLM loss at every rate | comparing MDLM/LLaDA with BERT |
| cross-entropy | What does it learn | −log of the probability the network gave the right token | the per-token loss | reading the loss |
| ELBO (Part 3) | What does it learn | a lower bound on log-likelihood; its negative is the training loss | why the 1/t weight | likelihood comparisons |
| time-agnostic network | What does it learn | the best denoiser depends on the visible tokens, not on t | lets samplers cache | MDLM, RADD, LLaDA |
| any-order autoregressive model | What does it learn | a model of every reveal order at once | the loss equals its average | why the bound is tight for an exact model |
| concrete score | What does it learn | ratios of probabilities between neighbouring sequences (SEDD) | the discrete analogue of the score | reading SEDD |
| ancestral sampler | How does it write | step from t to s revealing each masked token with probability (α_s − α_t)/(1 − α_t) | MDLM's default | step counts |
| first-hitting sampler | How does it write | reveal one uniformly chosen masked token at a time | the exact sampler | correctness |
| network call (NFE) | How does it write | one forward pass (Part 6) | the cost unit | speed claims |
| parallel decoding, product of marginals | How does it write | revealing several tokens from their separate distributions | the speed-up and the error | every speed claim |
| sequence error rate | How does it write | the share of whole outputs that are wrong | what parallel decoding hurts | reasoning tasks |
| remasking (low-confidence, random) | Why contested | which predictions to keep each step; the rest are masked again | LLaDA's and MaskGIT's decoder | reading benchmark numbers |
| greedy decoding, temperature | Why contested | taking the most likely token; scaling how sharply probabilities are followed | the decoders behind scores | diversity |
| KV cache | LLaDA-class | stored keys and values of earlier tokens, reused by AR decoding | why bidirectional models lose it | throughput |
| block diffusion | LLaDA-class | AR across blocks, diffusion within | gets the cache back | variable length |
| Gumbel-max trick, exponential race | Why contested | sampling a category as the argmax of perturbed scores | where float32 bites | implementing samplers |
| generative perplexity (Gen PPL), entropy | Why this matters | perplexity of samples under another model; diversity of tokens within a sample | the contested metric pair | evaluating text generators |

## Series handoffs

- Names Part 1 (published) and Parts 3, 6, 7, 8, 9 and 10 (not published) in plain text where used; the
  manifest lists each spot.
- Hands Part 12 nothing new beyond the series' memorisation thread.
