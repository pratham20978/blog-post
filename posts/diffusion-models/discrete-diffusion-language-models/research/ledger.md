# Source ledger — discrete-diffusion-language-models

Series `diffusion-models`, part 11. Sweep run 2026-10-22. Tier L3, so the floor is 7 peer-reviewed or
standard sources carrying an identifier, across 4 scholarly databases (Google Scholar, OpenAlex, arXiv,
Crossref; the NeurIPS, ICLR and ICML proceedings sites confirmed venues; DBLP served its Anubis bot wall
and Semantic Scholar answered 429, both logged below).

Every arXiv source was read in full text in the session scratchpad from arXiv's own HTML rendering
(arxiv.org/html/<id>, math kept as LaTeX `alttext`, with `<` and `>` preserved). The survey's Figure 7,
which the HTML does not render, was read from the v3 PDF (page 20). Every claim row was checked against
the paper's own text, table or equation, not an abstract or a search snippet. The three code rows were
read at the commits named, through raw.githubusercontent.com. LLaDA was read in its v3 (18 Oct 2025),
the NeurIPS 2025 camera-ready; its numbers below are v3's.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S1 | T1 | Yang, Zhang, Song, Hong, Xu, Zhao, Zhang, Cui & Yang, "Diffusion Models: A Comprehensive Survey of Methods and Applications" (survey) | ACM Computing Surveys 56(4) | 2023 | 10.1145/3626235 | peer-reviewed | https://arxiv.org/abs/2209.00796 | 2026-10-22 |
| S2 | T1 | Li, Chen, Guo & Shen, "A Survey on Diffusion Language Models" (survey, v3) | arXiv | 2025 | arXiv:2508.10875 | preprint | https://arxiv.org/abs/2508.10875 | 2026-10-22 |
| S3 | T1 | Austin, Johnson, Ho, Tarlow & van den Berg, "Structured Denoising Diffusion Models in Discrete State-Spaces" (D3PM) | NeurIPS 2021 | 2021 | arXiv:2107.03006 | peer-reviewed | https://arxiv.org/abs/2107.03006 | 2026-10-22 |
| S4 | T1 | Hoogeboom, Nielsen, Jaini, Forré & Welling, "Argmax Flows and Multinomial Diffusion: Learning Categorical Distributions" | NeurIPS 2021 | 2021 | arXiv:2102.05379 | peer-reviewed | https://arxiv.org/abs/2102.05379 | 2026-10-22 |
| S5 | T1 | Lou, Meng & Ermon, "Discrete Diffusion Modeling by Estimating the Ratios of the Data Distribution" (SEDD) | ICML 2024 | 2024 | arXiv:2310.16834 | peer-reviewed | https://arxiv.org/abs/2310.16834 | 2026-10-22 |
| S6 | T1 | Sahoo, Arriola, Schiff, Gokaslan, Marroquin, Chiu, Rush & Kuleshov, "Simple and Effective Masked Diffusion Language Models" (MDLM) | NeurIPS 2024 | 2024 | 10.52202/079017-4135 | peer-reviewed | https://arxiv.org/abs/2406.07524 | 2026-10-22 |
| S7 | T1 | Shi, Han, Wang, Doucet & Titsias, "Simplified and Generalized Masked Diffusion for Discrete Data" (MD4) | NeurIPS 2024 | 2024 | arXiv:2406.04329 | peer-reviewed | https://arxiv.org/abs/2406.04329 | 2026-10-22 |
| S8 | T1 | Ou, Nie, Xue, Zhu, Sun, Li & Li, "Your Absorbing Discrete Diffusion Secretly Models the Conditional Distributions of Clean Data" (RADD) | ICLR 2025 | 2025 | arXiv:2406.03736 | peer-reviewed | https://arxiv.org/abs/2406.03736 | 2026-10-22 |
| S9 | T1 | Zheng, Chen, Mao, Liu, Zhu & Zhang, "Masked Diffusion Models are Secretly Time-Agnostic Masked Models and Exploit Inaccurate Categorical Sampling" | ICLR 2025 | 2025 | arXiv:2409.02908 | peer-reviewed | https://arxiv.org/abs/2409.02908 | 2026-10-22 |
| S10 | T1 | Nie, Zhu, You, Zhang, Ou, Hu, Zhou, Lin, Wen & Li, "Large Language Diffusion Models" (LLaDA, v3) | NeurIPS 2025 | 2025 | arXiv:2502.09992 | peer-reviewed | https://arxiv.org/abs/2502.09992 | 2026-10-22 |
| S11 | T1 | Nie, Zhu, Du, Pang, Liu, Zeng, Lin & Li, "Scaling up Masked Diffusion Models on Text" | ICLR 2025 | 2025 | arXiv:2410.18514 | peer-reviewed | https://arxiv.org/abs/2410.18514 | 2026-10-22 |
| S12 | T1 | Devlin, Chang, Lee & Toutanova, "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding" | NAACL 2019 | 2019 | 10.18653/v1/N19-1423 | peer-reviewed | https://arxiv.org/abs/1810.04805 | 2026-10-22 |
| S13 | T1 | Ghazvininejad, Levy, Liu & Zettlemoyer, "Mask-Predict: Parallel Decoding of Conditional Masked Language Models" | EMNLP 2019 | 2019 | 10.18653/v1/D19-1633 | peer-reviewed | https://arxiv.org/abs/1904.09324 | 2026-10-22 |
| S14 | T1 | Chang, Zhang, Jiang, Liu & Freeman, "MaskGIT: Masked Generative Image Transformer" | CVPR 2022 | 2022 | 10.1109/CVPR52688.2022.01103 | peer-reviewed | https://arxiv.org/abs/2202.04200 | 2026-10-22 |
| S15 | T1 | Li, Thickstun, Gulrajani, Liang & Hashimoto, "Diffusion-LM Improves Controllable Text Generation" | NeurIPS 2022 | 2022 | arXiv:2205.14217 | peer-reviewed | https://arxiv.org/abs/2205.14217 | 2026-10-22 |
| S16 | T1 | Gulrajani & Hashimoto, "Likelihood-Based Diffusion Language Models" (Plaid) | NeurIPS 2023 | 2023 | arXiv:2305.18619 | peer-reviewed | https://arxiv.org/abs/2305.18619 | 2026-10-22 |
| S17 | T1 | Wu, Zhang, Xue, Liu, Diao, Zhu, Luo, Han & Xie, "Fast-dLLM: Training-free Acceleration of Diffusion LLM by Enabling KV Cache and Parallel Decoding" | ICLR 2026 | 2026 | arXiv:2505.22618 | peer-reviewed | https://arxiv.org/abs/2505.22618 | 2026-10-22 |
| S18 | T1 | Kim, Shah, Kontonis, Kakade & Chen, "Train for the Worst, Plan for the Best: Understanding Token Ordering in Masked Diffusions" | ICML 2025 | 2025 | arXiv:2502.06768 | peer-reviewed | https://arxiv.org/abs/2502.06768 | 2026-10-22 |
| S19 | T1 | Feng, Geng, Guan, Wu, Wang & He, "Theoretical Benefit and Limitation of Diffusion Language Model" | NeurIPS 2025 | 2025 | 10.52202/085713-0825 | peer-reviewed | https://arxiv.org/abs/2502.09622 | 2026-10-22 |
| S20 | T1 | Wang, Schiff, Sahoo & Kuleshov, "Remasking Discrete Diffusion Models with Inference-Time Scaling" (ReMDM) | NeurIPS 2025 | 2025 | arXiv:2503.00307 | peer-reviewed | https://arxiv.org/abs/2503.00307 | 2026-10-22 |
| S21 | T1 | Arriola, Gokaslan, Chiu, Yang, Qi, Han, Sahoo & Kuleshov, "Block Diffusion: Interpolating Between Autoregressive and Diffusion Language Models" (BD3-LM) | ICLR 2025 | 2025 | arXiv:2503.09573 | peer-reviewed | https://arxiv.org/abs/2503.09573 | 2026-10-22 |
| S22 | T1 | Gong, Agarwal, Zhang, Ye, Zheng, Li, An, Zhao, Bi, Han, Peng & Kong, "Scaling Diffusion Language Models via Adaptation from Autoregressive Models" (DiffuGPT, DiffuLLaMA) | ICLR 2025 | 2025 | arXiv:2410.17891 | peer-reviewed | https://arxiv.org/abs/2410.17891 | 2026-10-22 |
| S23 | T1 | Ye, Xie, Zheng, Gao, Wu, Jiang, Li & Kong, "Dream 7B: Diffusion Large Language Models" | arXiv | 2025 | arXiv:2508.15487 | preprint | https://arxiv.org/abs/2508.15487 | 2026-10-22 |
| S24 | T1 | Inception Labs (Khanna, Kharbanda, Li, Varma, Wang, Birnbaum, Luo, Miraoui, Palrecha, Ermon, Grover & Kuleshov), "Mercury: Ultra-Fast Language Models Based on Diffusion" | arXiv | 2025 | arXiv:2506.17298 | preprint | https://arxiv.org/abs/2506.17298 | 2026-10-22 |
| S25 | T2 | Google DeepMind, Gemini Diffusion model page | — | 2025 | — | official-docs | https://deepmind.google/models/gemini-diffusion/ | 2026-10-22 |
| S26 | T3 | kuleshov-group/mdlm, `diffusion.py` at commit b886f9f (MDLM's released sampler) | — | 2024 | b886f9f1d523faa62d484aa6985730c17163bc18 | source | https://github.com/kuleshov-group/mdlm/blob/b886f9f1d523faa62d484aa6985730c17163bc18/diffusion.py | 2026-10-22 |
| S27 | T3 | louaaron/Score-Entropy-Discrete-Diffusion, `catsample.py` at commit 0605786 (SEDD's released categorical sampler) | — | 2024 | 0605786da5ccb5747545e26d66fdf477187598b6 | source | https://github.com/louaaron/Score-Entropy-Discrete-Diffusion/blob/0605786da5ccb5747545e26d66fdf477187598b6/catsample.py | 2026-10-22 |
| S28 | T3 | ML-GSAI/LLaDA, `generate.py` at commit f2683fd (LLaDA's released sampler) | — | 2026 | f2683fd9cd10721f2853bafa52f8572ae8155d0c | source | https://github.com/ML-GSAI/LLaDA/blob/f2683fd9cd10721f2853bafa52f8572ae8155d0c/generate.py | 2026-10-22 |

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | OpenAlex | title.search "diffusion language models survey", sort cited_by_count | Zou et al. 2023 NLP survey (8 citations), Yu et al. 2025 and very recent low-citation surveys; OpenAlex undercounts arXiv-only work |
| 2 | 1 | OpenAlex | title.search "discrete diffusion survey"; "diffusion models natural language processing survey" | mostly statistics surveys of diffusion processes; Yu et al. 2025 and Zou et al. 2023 again |
| 3 | 1 | Google Scholar | survey diffusion language models | Li, Chen, Guo & Shen 2025 (111 citations), the ACM survey (3,883), Yu et al. 2025 (72), Zou et al. 2023 (44); Li et al. chosen as the map (S2) |
| 4 | 1 | arXiv | API: ti:survey AND ti:diffusion AND ti:language | 2508.10875, 2305.14671, 2506.13759, 2508.08712 and a 2026 inference-acceleration survey |
| 5 | 1 | arXiv | 2508.10875v3 full text (HTML) and PDF page 20 | taxonomy (continuous, discrete, hybrid), inference strategies, the parallel decoding curse, Figure 7 (LLaDA and MMaDA at different step counts); CC BY 4.0 (S2, F1, L35) |
| 6 | 1 | arXiv | 2209.00796 (ACM survey, v15) Section 5.1 | why Gaussian perturbation does not fit discrete data; D3PM and Campbell et al. as the discrete line (S1, L08) |
| 7 | 2 | arXiv | full text of 2107.03006, 2102.05379, 2310.16834, 2406.07524, 2406.04329, 2406.03736 | transition matrices, multinomial noise, score entropy, the masked-diffusion objective as weighted masked-LM losses, the time-free network (L06, L10–L15, L19–L21, L25–L28) |
| 8 | 4 | arXiv | full text of 2409.02908 | time-agnostic training and sampling, the first-hitting sampler, the float32 Gumbel truncation with its ablation table (L01–L04, L09, L24, L29) |
| 9 | 2 | arXiv | full text of 2502.09992 (v3) and 2410.18514 | LLaDA's recipe, benchmark tables, remasking ablation, evaluation protocol; the 16x compute gap (L09, L18, L22, L36–L37, L43–L48, L54) |
| 10 | 5 | GitHub | raw `diffusion.py` of kuleshov-group/mdlm and its commits atom feed | `_sample_categorical` is the exponential race in the probabilities' dtype; last change 2024-06-28, before Zheng et al. (S26, L07) |
| 11 | 5 | GitHub | raw `catsample.py` of louaaron/Score-Entropy-Discrete-Diffusion and its atom feed | the same race form, committed 2024-02-29 (S27, L07) |
| 12 | 5 | GitHub | raw `generate.py` of ML-GSAI/LLaDA and its atom feed | float64 Gumbel noise with a docstring citing 2409.02908; temperature 0 and low_confidence remasking as defaults (S28, L55) |
| 13 | 1 | NeurIPS proceedings | web search for LLaDA's venue | NeurIPS 2025 main track, oral (proceedings.neurips.cc hash 48b383b2…) |
| 14 | 4 | arXiv | full text of 2505.22618, 2502.06768, 2502.09622, 2503.00307 | the parallel decoding curse and its high-confidence theorem, adaptive ordering on Sudoku, step-count bounds for token versus sequence error, remasking and Gen PPL gaming (L31–L34, L40–L42) |
| 15 | 2 | arXiv | full text of 2503.09573, 2410.17891, 2508.15487, 2506.17298 | block diffusion with KV caching; adapting AR checkpoints into diffusion models; Dream 7B from Qwen2.5; Mercury's throughputs (L49–L52) |
| 16 | 6 | arXiv | full text of 1810.04805, 1904.09324, 2202.04200, 2205.14217, 2305.18619 | BERT's fixed 15% masking; Mask-Predict and MaskGIT's confidence remasking; Diffusion-LM's rounding; Plaid's 64x compute factor (L16–L17, L23, L38–L39) |
| 17 | 5 | Google DeepMind site | Gemini Diffusion model page (WebFetch) | experimental model, 1,479 tokens/s excluding 0.84 s overhead, benchmark table against Gemini 2.0 Flash-Lite (S25, L53) |
| 18 | 1 | OpenAlex | batch title.search of 16 sources | NeurIPS DOIs for MDLM, Feng et al., Plaid, Diffusion-LM; CVPR for MaskGIT; EMNLP for Mask-Predict; RADD, the scaling paper, Fast-dLLM and Kim et al. listed only as arXiv, so confirmed below; one 429 |
| 19 | 1 | ICML proceedings | web search for Kim et al.'s venue | ICML 2025 oral (icml.cc virtual site, mlanthology) |
| 20 | 1 | ICLR proceedings | web search for RADD, the scaling paper and Fast-dLLM | RADD and Nie et al. in the ICLR 2025 proceedings (with the scaling paper's full author list); Fast-dLLM in the ICLR 2026 proceedings |
| 21 | 1 | Crossref | works API for six DOIs | NAACL 2019 (BERT), EMNLP 2019 (Mask-Predict), CVPR 2022 (MaskGIT), ACM CSUR 56(4) (S1), NeurIPS 37 (MDLM), NeurIPS 38 (Feng et al.) |
| 22 | 1 | DBLP | search API, "Simple and Effective Masked Diffusion Language Models" | Anubis bot wall ("Making sure you're not a bot"); nothing returned; not retried |
| 23 | 1 | Semantic Scholar | paper API and citations for arXiv:2409.02908 | HTTP 429 for both calls |
| 24 | 4 | OpenAlex | forward chase: works citing 2409.02908 and 2502.09992 with sampling, precision, decoding, remasking, order in the title | a near-empty graph (0 citations listed for Zheng et al.); unusable for this chase |
| 25 | 4 | Google Scholar | Zheng et al.'s record and its "Cited by" list | only a citation-only record (3 citations); unusable for this chase |
| 26 | 4 | arXiv | forward chase through the later papers' full texts (BD3-LM, ReMDM, Fast-dLLM, Kim et al., Feng et al.) and LLaDA's code | BD3-LM and ReMDM, from MDLM's own group, sample with 64-bit Gumbel noise because of Zheng et al.; LLaDA's sampler does the same; nobody reports the truncation result overturned (L05) |
| 27 | 3 | arXiv | BD3-LM Table 7 and Supplement C.5 | Gen PPL there uses nucleus sampling (p = 0.9 for AR, MDLM and BD3-LM, 0.99 for SEDD), so it is not comparable with Zheng et al.'s unannealed numbers; not quoted |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | In float32 the largest uniform draw is 1 − 2^-24, so the largest Gumbel value is about 16.6355; in float64 it is about 36.7368 | S9 §5.2, Table 1 | the Gumbel-max transform g = −log(−log u) |
| L02 | Changing only the categorical-sampling code: 32-bit gave Gen PPL 31.24 and entropy 5.17, 64-bit gave 126.11 and 5.66, and 64-bit truncated like 32-bit gave 28.64 and 5.12 | S9 Table 2 | 8 samples of 2,048 steps; Gen PPL under GPT-2 Large; entropy is the unigram entropy within each sequence |
| L03 | With the original 32-bit samplers, MDMs' Gen PPL beat the AR model's at around 2,000 steps while their entropy stayed lower and kept falling; near 50,000 steps Gen PPL fell below 15 | S9 §5.1, Figure 7 | SEDD Absorb and MDLM against an AR model of the same architecture, all trained on OpenWebText by MDLM's authors; 64 samples per point |
| L04 | After fixing the precision, entropy returned to 5.60–5.70 for every model and MDMs' Gen PPL was about 100, against below 40 for the AR models | S9 §6.1 | same models; about 170M parameters, GPT-2 tokenizer, sequences of 1,024 tokens |
| L05 | Later work from MDLM's own group samples with 64-bit Gumbel noise because 32-bit truncation lowers the temperature and the entropy; LLaDA's released sampler uses float64 citing the same paper | S20 §5.1.1 (64-bit for all text sampling); S21 Suppl. C.5 (corrected Gumbel sampling); S28 `add_gumbel_noise` | forward chase from S9 |
| L06 | SEDD reported 6–8x better Gen PPL than unannealed GPT-2 with its full step count and matched GPT-2 with 32x fewer network evaluations, comparing unannealed samples because annealing can hack Gen PPL | S5 abstract, §5.3.1, Figure 1 | sequences of 1,024 tokens, 32 to 2,048 steps, GPT-2 Large evaluator |
| L07 | MDLM's and SEDD's released samplers draw each categorical as argmax(q / (1e-10 − log(u + 1e-10))) with u from torch.rand_like, in the probabilities' own dtype; MDLM's update gives the mask weight s and each token p(t − s) | S26 `_sample_categorical`, `_ddpm_caching_update`; S27 `sample_categorical` | code at the commits named |
| L08 | Gaussian perturbation is not a natural fit for discrete data, and score functions are defined only on continuous domains | S1 §5.1 | — |
| L09 | GPT-2's tokenizer has 50,257 tokens; LLaDA 8B's vocabulary has 126,464 | S9 App. H.2; S10 Table 5 | — |
| L10 | D3PM defines discrete forward processes by transition matrices with closed-form marginals and offers four: uniform, absorbing ([MASK]), discretized Gaussian for ordinal data, and nearest neighbours in an embedding space | S3 §3, §3.1 | — |
| L11 | Multinomial diffusion corrupts categories with uniform transitions, the matrix D3PM calls uniform | S4 abstract; S3 §3.1 | — |
| L12 | On LM1B, D3PM absorbing reached perplexity 76.9 at 1,000 steps against 137.9 for uniform and 149.5 for nearest neighbours, while a same-size transformer reached 43.6 | S3 Table 2 | 8,192-token sentencepiece vocabulary, length 128, 12 layers; diffusion values are bounds |
| L13 | Zero-shot perplexity of small models (GPT-2 / SEDD absorb / SEDD uniform / D3PM / Plaid): LAMBADA 45.04 / 50.92 / 65.40 / 93.47 / 57.28; WikiText2 42.43 / 41.84 / 50.27 / 77.28 / 51.80; PTB 138.43 / 114.24 / 140.12 / 200.82 / 142.60; WikiText103 41.60 / 40.62 / 49.60 / 75.16 / 50.86; 1BW 75.20 / 79.29 / 101.37 / 138.92 / 91.12 | S5 Table 1 | diffusion values are upper bounds; GPT-2 recomputed without a sliding window |
| L14 | Absorbing (masking) diffusion consistently performs best among discrete forward processes | S6 §3 citing S3 and S5 | language modelling |
| L15 | BERT's objective is a one-step discrete diffusion; an absorbing D3PM trained on the ELBO reduces to a reweighted masked-LM objective; autoregressive models are diffusion with tokens masked one by one in order | S3 §4 | — |
| L16 | Diffusion-LM diffuses continuous word embeddings and needs a rounding step to map vectors back to words | S15 §4.1–4.2 | — |
| L17 | Plaid 1B beats GPT-2 124M in zero-shot likelihood but needs about 64x the compute of an equivalent AR model | S16 abstract, §5, Figure 2 | continuous embedding diffusion |
| L18 | Masked diffusion needs about 16x the compute of AR for the same validation loss, with a similar scaling rate | S11 §1, §3, Figure 2 | IsoFLOP study from 6e18 to 1e20 FLOPs, models up to 1.1B parameters |
| L19 | The masking posterior: a masked token stays masked from t to s with probability (1 − α_s)/(1 − α_t) and otherwise becomes its clean value; an unmasked token stays | S6 eq. 8; S9 eq. 2 | absorbing process with α_t the probability a token is still clean |
| L20 | MDLM builds two facts into the network: it never predicts [MASK], and an unmasked token is copied unchanged | S6 §3.2.3 | — |
| L21 | The continuous-time ELBO of masked diffusion is a weighted integral of masked-token cross-entropies, a weighted average of masked-LM losses, and does not depend on the schedule's shape | S6 eq. 12–13; S7 abstract | — |
| L22 | LLaDA's loss: draw t uniformly from 0 to 1, mask each token with probability t, and weight the masked tokens' cross-entropy by 1/t; it bounds the negative log-likelihood | S10 eq. 3–4 | — |
| L23 | BERT chooses 15% of positions to predict and replaces 80% of them with [MASK], 10% with a random token and leaves 10% unchanged | S12 §3.1, App. C.2 | — |
| L24 | The optimal masked-diffusion network does not depend on time, and the ELBO can be written over the number of masked tokens with weight 1/n | S9 Prop. 3.1–3.2 | — |
| L25 | For absorbing diffusion the concrete score is the clean data's conditional probability times an analytic time factor, so a time-free network suffices and its output can be cached while the sample is unchanged; the bound equals the any-order autoregressive objective | S8 abstract; S10 App. A.2 | — |
| L26 | SEDD learns ratios between the probabilities of neighbouring sequences, the concrete score, with a score-entropy loss that extends score matching to discrete spaces | S5 abstract, §3 | — |
| L27 | On OpenWebText after 262B training tokens: AR 17.54, SEDD at most 24.10, MDLM at most 23.21 perplexity | S6 Table 2 | GPT-2 tokenizer, context 1,024, AR retrained with the same architecture |
| L28 | MDLM's ancestral sampler draws every masked position independently each step, reuses the network output when nothing changed, and never changes an unmasked token | S6 §4.1 | — |
| L29 | The first-hitting sampler unmasks one uniformly chosen masked token at a time, is equivalent to the continuous-time reverse process, and was up to 20x faster in wall-clock time | S9 §4.2, §6.1 | — |
| L31 | Unmasking two positions in one step samples them from the product of their marginals; the true joint needs one conditioned on the other | S17 §2 ("Curse of Parallel Decoding") | — |
| L32 | If each of n tokens has marginal confidence above 1 − ε and (n + 1)ε is at most 1, greedy decoding from the product of marginals equals greedy decoding from the joint, and their total variation distance is below (3n − 1)ε/2 | S17 Theorem 1 | — |
| L33 | Confidence-threshold parallel decoding with an approximate KV cache gave up to 27.6x throughput on LLaDA and Dream with little accuracy loss | S17 abstract | LLaDA and Dream benchmarks |
| L34 | Near-optimal token error rate needs a number of steps independent of length, but for some HMM over 16 tokens any schedule with N = CL steps leaves sequence error above 1/2, so low sequence error needs steps that grow with length | S19 Theorems 4.2, 4.4 | worst case, under the paper's learning assumption |
| L35 | In the survey's test LLaDA's 128-token answer was correct only at 64 steps (2 tokens per step) and MMaDA's 256-token answer only at 256 steps; with fewer steps the answers were wrong or garbled | S2 §VIII-A, Figure 7 | one math prompt |
| L36 | LLaDA notes that in principle remasking should be random, then uses low-confidence remasking, keeping the most confident predictions as MaskGIT does; its algorithm predicts tokens greedily | S10 §2.4, App. A.3 | — |
| L37 | LLaDA 8B Base with random against low-confidence remasking: BBH 32.1 against 45.0, GSM8K 21.3 against 70.0, Math 9.2 against 30.3, HumanEval 11.6 against 32.9, MBPP 21.0 against 40.2; the authors suggest low confidence works like annealed sampling by reducing diversity | S10 App. B.4, Table 9 | generation length and steps both 256, one token per step |
| L38 | Mask-Predict predicts every target word, then repeatedly re-masks and re-predicts the words it is least confident about | S13 abstract | machine translation |
| L39 | MaskGIT predicts every token, keeps the most confident and re-masks the rest on a cosine schedule, and decodes up to 64x faster than autoregressive decoding | S14 §3.2, abstract | ImageNet, against VQGAN |
| L40 | MDMs train on infilling subproblems, some computationally intractable, that AR models never face; adaptive choice of which position to decode next (top probability margin) sidesteps the hard ones and raised Sudoku accuracy of a pretrained MDM from below 7% to about 90%; the rules choose positions, not values | S18 abstract, §4.1 | small MDMs on Sudoku; also LLaDA 8B on code and math |
| L41 | Masked diffusion cannot revise a token once written; ReMDM adds a remasking backward process that can | S20 abstract | — |
| L42 | A corrector schedule can push Gen PPL to 1.5 by repeating one word, so ReMDM reports MAUVE instead | S20 §5.1.1, App. F.1 | OpenWebText samples |
| L43 | LLaDA's benchmarks: MMLU, ARC-C, HellaSwag and similar are scored by Monte Carlo likelihood (128 samples), the rest by generation with low-confidence remasking, with length and steps both 1,024 for the base model | S10 App. B.6 | — |
| L44 | LLaDA 8B was trained from scratch on 2.3T tokens with 0.13M H800 GPU hours, sequence length 4,096, then fine-tuned on 4.5M pairs; it uses no causal mask and plain multi-head attention because it cannot use a KV cache | S10 §1, §2.2–2.3 | — |
| L45 | LLaDA 8B Base against LLaMA3 8B Base under one protocol: MMLU 65.9/65.4, BBH 49.7/62.1, ARC-C 45.9/53.1, HellaSwag 70.5/79.1, TruthfulQA 46.1/44.0, WinoGrande 74.8/77.3, PIQA 73.6/80.6, GSM8K 70.3/48.7, Math 31.4/16.0, GPQA 25.2/25.9, HumanEval 35.4/34.8, HumanEval-FIM 73.8/73.3, MBPP 40.0/48.8, CMMLU 69.9/50.7, C-Eval 70.5/51.7; trained on 2.3T against 15T tokens | S10 Table 1 | shots as in the table; the authors attribute part of the gaps to data |
| L46 | Chinese poem completion, forward/reversal: GPT-4o 82.7/34.3, Qwen2.5 7B Instruct 75.9/38.0, LLaDA 8B Instruct 51.8/45.6 | S10 Table 4 | 496 poem sentence pairs, zero-shot |
| L47 | LLaDA's authors answer the 16x compute gap by noting that likelihood is an indirect metric, and extend the scaling range to 1e23 FLOPs | S10 §3.1 | — |
| L48 | On GSM8K and Math, LLaDA 8B Base matched LLaMA3 8B Base with 1.5x and 1.8x the throughput, LLaMA3 using a KV cache and LLaDA none | S10 App. B.7 | one A100-80GB, batch size 1, 256 output tokens |
| L49 | AR models from 127M to 7B parameters were converted into diffusion models (DiffuGPT, DiffuLLaMA) with under 200B tokens of training | S22 abstract | — |
| L50 | Dream 7B is initialized from Qwen2.5 7B and trained on 580B tokens | S23 §4.1–4.2 | — |
| L51 | Block diffusion generates blocks left to right and runs diffusion inside each block, which allows KV caching and arbitrary-length generation | S21 abstract | — |
| L52 | Mercury Coder Mini and Small reached 1,109 and 737 tokens/s on H100 GPUs in independent measurements, up to 10x faster than speed-optimized frontier models | S24 abstract | vendor technical report, coding models; measured by Artificial Analysis |
| L53 | Gemini Diffusion is an experimental model; its page reports 1,479 tokens/s excluding 0.84 s of overhead, averaged over its evals, with scores above and below Gemini 2.0 Flash-Lite (for example LiveCodeBench 30.9 against 28.5, GPQA Diamond 40.4 against 56.5) | S25 | architecture undisclosed; page accessed 2026-10-22 |
| L54 | For LLaDA the generation length is a hyperparameter fixed before sampling | S10 §2.4, App. B.5 | — |
| L55 | LLaDA's released sampler defaults to temperature 0 and low_confidence remasking, and ranks masked positions by the softmax probability of the token it drew there; at temperature 0 that token is the argmax | S28 `generate`, `add_gumbel_noise` | code at the commit named |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S2 | Figure 7 | Why does parallel decoding break? / L35 | a real 8B model's answer at 2, 4 and 16 tokens per step: the curse on text, which the lab can only show on images | CC BY 4.0 (arXiv record of 2508.10875) | https://arxiv.org/abs/2508.10875 | reuse unchanged, cropped from the v3 PDF |
| F2 | S6 | Figure 1 | What does the model learn? / L21 | the masked-LM view of the loss | CC BY 4.0 | https://arxiv.org/abs/2406.07524 | do not reuse: a graphical abstract whose right half is a word cloud and whose transparent background loses its text on dark pages; our figure adds LLaDA's shapes and the 1/t weight |
| F3 | S5 | Figure 1 | Why this matters / L06 | SEDD's Gen PPL against steps | CC BY 4.0 | https://arxiv.org/abs/2310.16834 | do not reuse: it shows the curve S9 attributes to the precision fault; the post charts S9's own ablation instead |
| F4 | S3, S10, S9 | D3PM Figure 1; LLaDA Figure 2; Zheng et al. Figures 7, 9 | forward process, LLaDA overview, precision | — | CC BY-NC-SA 4.0 (D3PM); arXiv non-exclusive licence (LLaDA, Zheng et al.) | — | do not reuse; the post draws its own from the lab and from the papers' tables |

## Open questions

- LLaDA's Table 9 does not state the temperature of its random-remasking run. Its algorithm predicts
  greedily, so both rows are probably greedy; the post says only "random positions" against "most
  confident positions" and does not call either row the principled sampler.
- Which model Zheng et al.'s Table 2 used is not stated beside the table (the section uses MDLM's
  codebase and models). The post says "their ablation", not a model name.
- Gemini Diffusion's architecture and training are undisclosed; the post quotes only its page's speed and
  states that.
