# Source ledger — laya-decision-model-explained

Series: frontier-models, Part 1 (Laya, Part 1). Researched 2026-09-26. Every Laya number in the
article is either *vendor-reported* (S1–S4, Convai), *third-party* (labelled), or *our local run*
(`lab/trace.json`, laya 0.3.20, torch 2.14.0+cpu, checkpoint commit 55cf4c4e, CPU, FP32). Our-run
numbers are computed in the article and carry no ledger key; the lab is their source.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S1 | T2 | Convai Innovations, Laya model card (`convaiinnovations/laya`, README at commit 55cf4c4e) | Hugging Face | 2026 | — | official-docs | https://huggingface.co/convaiinnovations/laya | 2026-09-26 |
| S2 | T2 | Convai Innovations, laya-multilingual model card | Hugging Face | 2026 | — | official-docs | https://huggingface.co/convaiinnovations/laya-multilingual | 2026-09-26 |
| S3 | T2 | Convai Innovations, laya-typed-decisions model card | Hugging Face | 2026 | — | official-docs | https://huggingface.co/convaiinnovations/laya-typed-decisions | 2026-09-26 |
| S4 | T3 | Laya checkpoint files at commit 55cf4c4e: `rl_agent_config.json`, `encoder/config.json` for all three checkpoints, `rl_common.py`, `rl_agent_api.py`; Hub API metadata (createdAt, lastModified) | Hugging Face | 2026 | commit 55cf4c4ebb4ebe31b2550e8bdf3bd21b99753851 | source | https://huggingface.co/convaiinnovations/laya/tree/55cf4c4ebb4ebe31b2550e8bdf3bd21b99753851 | 2026-09-26 |
| S5 | T3 | `laya` Python package 0.3.20 (`laya/common.py`, `laya/agent.py`), released 2026-09-24 | PyPI | 2026 | laya==0.3.20 | source | https://pypi.org/project/laya/0.3.20/ | 2026-09-26 |
| S6 | T3 | NandhaKishorM/laya GitHub repository at commit 4066d5d (tree, README, BENCHMARKS.md, fine-tuning notebook) | GitHub | 2026 | commit 4066d5d5fbf08b66c6757ddeedbd797bd7655bc0 | source | https://github.com/NandhaKishorM/laya/tree/4066d5d5fbf08b66c6757ddeedbd797bd7655bc0 | 2026-09-26 |
| S7 | T3 | Laya issue #185, "The decision head's output is unnormalized … act_probability is always 1.0" (open) | GitHub | 2026 | issue #185 | source | https://github.com/NandhaKishorM/laya/issues/185 | 2026-09-26 |
| S8 | T3 | Laya issue #156, "`noul` returns the negative label regardless of state" (closed 2026-09-23) | GitHub | 2026 | issue #156 | source | https://github.com/NandhaKishorM/laya/issues/156 | 2026-09-26 |
| S9 | T4 | Nandakishor M, "I built non-autoregressive decision models a year ago…", the write-up linked from the card | DEV Community | 2026 | — | practitioner | https://dev.to/nandakishor_m_6cc0adfde9f/i-built-non-autoregressive-decision-models-a-year-ago-then-a-frontier-lab-called-it-a-18me | 2026-09-26 |
| S10 | T1 | Nandakishor M, "SalesRLAgent: A Reinforcement Learning Approach for Real-Time Sales Conversion Prediction and Optimization" | arXiv | 2025 | arXiv:2503.23303v1 | preprint | https://arxiv.org/abs/2503.23303 | 2026-09-26 |
| S11 | T2 | TypeSafe AI, "Introducing System One Models & Jev" (dated 2026-09-15) | TypeSafe blog | 2026 | — | official-docs | https://typesafe.ai/blog/introducing-system-one-models-and-jev | 2026-09-26 |
| S12 | T2 | TypeSafe AI documentation: System One, Primitives (Choice, Score, Noul), Quick start | docs.typesafe.ai | 2026 | — | official-docs | https://docs.typesafe.ai/concepts/system-one | 2026-09-26 |
| S13 | T1 | Devlin, Chang, Lee, Toutanova, "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding" | NAACL-HLT | 2019 | 10.18653/v1/N19-1423 | peer-reviewed | https://aclanthology.org/N19-1423/ | 2026-09-26 |
| S14 | T1 | Vaswani et al., "Attention Is All You Need" | NeurIPS | 2017 | arXiv:1706.03762 | peer-reviewed | https://arxiv.org/abs/1706.03762 | 2026-09-26 |
| S15 | T1 | Warner et al., "Smarter, Better, Faster, Longer: A Modern Bidirectional Encoder for Fast, Memory Efficient, and Long Context Finetuning and Inference" (ModernBERT) | ACL | 2025 | 10.18653/v1/2025.acl-long.127 | peer-reviewed | https://aclanthology.org/2025.acl-long.127/ | 2026-09-26 |
| S16 | T1 | Marone et al., "mmBERT: A Modern Multilingual Encoder with Annealed Language Learning" | arXiv | 2025 | arXiv:2509.06888v1 | preprint | https://arxiv.org/abs/2509.06888 | 2026-09-26 |
| S17 | T1 | Su et al., "RoFormer: Enhanced Transformer with Rotary Position Embedding" | Neurocomputing | 2024 | 10.1016/j.neucom.2023.127063 | peer-reviewed | https://doi.org/10.1016/j.neucom.2023.127063 | 2026-09-26 |
| S18 | T1 | Shazeer, "GLU Variants Improve Transformer" | arXiv | 2020 | arXiv:2002.05202 | preprint | https://arxiv.org/abs/2002.05202 | 2026-09-26 |
| S19 | T1 | Beltagy, Peters, Cohan, "Longformer: The Long-Document Transformer" | arXiv | 2020 | arXiv:2004.05150 | preprint | https://arxiv.org/abs/2004.05150 | 2026-09-26 |
| S20 | T1 | Xiong et al., "On Layer Normalization in the Transformer Architecture" | ICML (PMLR 119) | 2020 | arXiv:2002.04745 | peer-reviewed | https://proceedings.mlr.press/v119/xiong20b.html | 2026-09-26 |
| S21 | T1 | Yin, Hay, Roth, "Benchmarking Zero-shot Text Classification: Datasets, Evaluation and Entailment Approach" | EMNLP-IJCNLP | 2019 | 10.18653/v1/D19-1404 | peer-reviewed | https://aclanthology.org/D19-1404/ | 2026-09-26 |
| S22 | T1 | Schick, Schütze, "Exploiting Cloze-Questions for Few-Shot Text Classification and Natural Language Inference" (PET) | EACL | 2021 | 10.18653/v1/2021.eacl-main.20 | peer-reviewed | https://aclanthology.org/2021.eacl-main.20/ | 2026-09-26 |
| S23 | T1 | Yang et al., "Zero-Shot Learners for Natural Language Understanding via a Unified Multiple Choice Perspective" (UniMC) | EMNLP | 2022 | 10.18653/v1/2022.emnlp-main.474 | peer-reviewed | https://aclanthology.org/2022.emnlp-main.474/ | 2026-09-26 |
| S24 | T1 | Zaratiana, Tomeh, Holat, Charnois, "GLiNER: Generalist Model for Named Entity Recognition using Bidirectional Transformer" | NAACL | 2024 | 10.18653/v1/2024.naacl-long.300 | peer-reviewed | https://aclanthology.org/2024.naacl-long.300/ | 2026-09-26 |
| S25 | T1 | Stepanov et al., "GLiClass: Generalist Lightweight Model for Sequence Classification Tasks" | arXiv | 2025 | arXiv:2508.07662v1 | preprint | https://arxiv.org/abs/2508.07662 | 2026-09-26 |
| S26 | T1 | Liu et al., "Pre-train, Prompt, and Predict: A Systematic Survey of Prompting Methods in Natural Language Processing" | ACM Computing Surveys | 2023 | 10.1145/3560815 | peer-reviewed | https://doi.org/10.1145/3560815 | 2026-09-26 |
| S27 | T1 | Tam et al., "Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of Large Language Models" | EMNLP Industry | 2024 | 10.18653/v1/2024.emnlp-industry.91 | peer-reviewed | https://aclanthology.org/2024.emnlp-industry.91/ | 2026-09-26 |
| S28 | T1 | Willard, Louf, "Efficient Guided Generation for Large Language Models" | arXiv | 2023 | arXiv:2307.09702v4 | preprint | https://arxiv.org/abs/2307.09702 | 2026-09-26 |
| S29 | T1 | OpenAI, "GPT-4 Technical Report" | arXiv | 2023 | arXiv:2303.08774v6 | preprint | https://arxiv.org/abs/2303.08774 | 2026-09-26 |
| S30 | T1 | Geng, Josifoski, Peyrard, West, "Grammar-Constrained Decoding for Structured NLP Tasks without Finetuning" | EMNLP | 2023 | 10.18653/v1/2023.emnlp-main.674 | peer-reviewed | https://aclanthology.org/2023.emnlp-main.674/ | 2026-09-26 |
| S31 | T3 | Hugging Face transformers 5.17.0: `models/modernbert/modeling_modernbert.py`, `configuration_modernbert.py`, `masking_utils.py` | PyPI | 2026 | transformers==5.17.0 | source | https://pypi.org/project/transformers/5.17.0/ | 2026-09-26 |
| S32 | T1 | Zaratiana et al., "GLiGuard: Schema-Conditioned Classification for LLM Safeguard" | arXiv | 2026 | arXiv:2605.07982 | preprint | https://arxiv.org/abs/2605.07982 | 2026-09-26 |
| S33 | T1 | Sun, Xu, Shi, Yang, "Type-Safe Is Not Error-Free: A Constrained Decision Head Follows the Option Name, Not the Rubric Bound to It" (abstract read) | arXiv | 2026 | arXiv:2609.26758 | preprint | https://arxiv.org/abs/2609.26758 | 2026-09-26 |

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | Hugging Face Hub API | models?author=convaiinnovations | three Laya repos created 2026-09-18/19; no newer Laya checkpoint (currency check) |
| 2 | 1 | GitHub API | repos/NandhaKishorM/laya tree at main | inference package, benchmarks, a fine-tuning notebook; no RLCD pre-training code and no paper (currency check) |
| 3 | 1 | PyPI JSON API | laya | 0.1.0 on 2026-09-18 to 0.3.20 on 2026-09-24; pinned 0.3.20 for the lab |
| 4 | 1 | arXiv API | id_list 2503.23303, 2510.01237 (named in the author's write-up) | two single-author preprints by the same author, neither describing Laya's architecture |
| 5 | 1 | arXiv API | id_list 2412.13663, 2509.06888 | ModernBERT and mmBERT full metadata; both PDFs read for architecture tables |
| 6 | 1 | DBLP | ModernBERT Smarter Better Faster Longer | blocked by an Anubis bot challenge; not solved, venue taken from OpenAlex + ACL Anthology instead |
| 7 | 1 | OpenAlex | Smarter Better Faster Longer bidirectional encoder | ModernBERT published at ACL 2025, DOI 10.18653/v1/2025.acl-long.127 |
| 8 | 1 | OpenAlex | mmBERT modern multilingual encoder annealed language learning | arXiv record only; no venue found, so it stays a preprint |
| 9 | 1 | Google Scholar | zero-shot text classification survey | Yin et al. 2019 (EMNLP, 1,087 cites) as the entailment baseline; a 2026 ICLR zero-shot benchmark; LLM-classification reviews |
| 10 | 1 | Google Scholar | structured output generation large language models survey | no dedicated survey of JSON mode; user-constraint and controllable-generation surveys only |
| 11 | 1 | Google Scholar | UniMC unified multiple choice zero-shot learners option mask | UniMC (EMNLP 2022; IEEE Access 2023 version): an [O-MASK] per option in one sequence |
| 12 | 1 | Google Scholar | GLiNER generalist named entity recognition bidirectional transformer | GLiNER (NAACL 2024, 396 cites): [ENT] marker per entity type in one sequence |
| 13 | 1 | Google Scholar | GLiClass generalist lightweight sequence classification | GLiClass (arXiv 2025): a «LABEL» marker per label, one pass, PPO variant |
| 14 | 1 | Google Scholar | exploiting cloze questions few shot text classification pattern | empty page (rate-limited); PET located through OpenAlex instead |
| 15 | 1 | OpenAlex | UniMC / GLiNER / GLiClass / PET / Yin / BERT / Transformer titles | DOIs and venues for S13, S21–S25; Liu et al. 2023 survey surfaced as the prompting-methods map |
| 16 | 1 | Semantic Scholar | citations of 10.18653/v1/2022.emnlp-main.474 and 2024.naacl-long.300 (DOI form) | 404 for the DOI form; retried by arXiv id |
| 17 | 1 | Semantic Scholar | cited-by arXiv:2311.08526 (GLiNER), filtered for classification | 189 citers; GLiClass, and a 2026 preprint using Jev models for edge orchestration |
| 18 | 1 | Semantic Scholar | cited-by arXiv:2412.13663 (ModernBERT), filtered | GLiGuard (May 2026, schema-conditioned single-pass encoder) and Sun et al. 2026 (option names override rubrics in Jev-like models) — the forward-chase finds |
| 19 | 2 | Hugging Face | convaiinnovations/laya raw files: rl_common.py, rl_agent_api.py, configs | exact sequence format, head modules, temperatures; one sequence per question |
| 20 | 2 | PyPI / GitHub | laya 0.3.20 laya/common.py, laya/agent.py | same mechanism as the Hub files; state tokenized once and copied into each question's row; temperature clamp to [0.5, 5] |
| 21 | 2 | ACL Anthology | UniMC, GLiNER, PET, BERT, Yin PDFs | input formats read from each paper's method section; BERT SWAG uses four sequences |
| 22 | 2 | local source | transformers 5.17.0 ModernBERT and masking_utils | local window is abs(i − j) ≤ 64; no unpadding on the SDPA path |
| 23 | 3 | Hugging Face | Laya card benchmark and limits tables | T4 latency (vendor-reported), typed-decisions accuracy 0.362 base vs 0.766 fine-tuned, act AUROC 0.30 |
| 24 | 4 | GitHub issues | NandhaKishorM/laya #156, #185 | label-word trap for noul; unnormalized head output saturating the act head |
| 25 | 4 | arXiv (via Semantic Scholar) | Type-Safe Is Not Error-Free | preprint: renaming options 0/1 to no/yes changed 70.4 answers per 100 in Jev and two open Jev-like models |
| 26 | 4 | ACL Anthology / arXiv | Tam et al. 2024; GPT-4 Technical Report | JSON mode hurts reasoning but is competitive on classification; post-training reduced GPT-4's calibration |
| 27 | 5 | TypeSafe docs (llms.txt, primitives, quickstart) | system-one, choice, score, noul | three primitives, POST /v1/systemone, 255-option cap, calibration is a group property |
| 28 | 5 | TypeSafe blog | Introducing System One Models & Jev | datePublished 2026-09-15; "can't hallucinate" tied to type safety; RLCD named, undisclosed |
| 29 | 6 | Web search | laya decision model convai explained | at least eight release-week explainers; one checked in full shows no token sequence, shapes, logits or lineage (saturation check) |
| 30 | 6 | Web search | what is a decision model AI system one vs LLM JSON mode classifier | glossary and news explainers built on TypeSafe's launch post; none traces a model |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | Laya is Convai Innovations' model, released under Apache-2.0; the English repo was created on 2026-09-18 | S1, S4 | Hub createdAt 2026-09-18T05:05Z |
| L02 | Laya takes a state and typed questions and returns typed answers with probabilities from a single forward pass without generating text | S1 | vendor description |
| L03 | Card architecture: a fully fine-tuned ModernBERT-large backbone (395M) plus a decision head trained from scratch — 2 transformer layers, an option-marker scorer and an act/escalate head — 421M in total | S1 | vendor-reported |
| L04 | Each option is scored at its own `[MASK]` and softmaxed over that question's options; the answer space is set at request time, so a new schema needs no retraining | S1 | — |
| L05 | English checkpoint: 512 tokens per question with a 192-token budget for question plus options; multilingual and typed-decisions: 1,024 with 256 | S1, S4 | config values at commit 55cf4c4e |
| L06 | Three checkpoints: `laya` (ModernBERT-large, 421M, 512), `laya-multilingual` (mmBERT-base, 322M, 1,024, up to 8,192 when asked), `laya-typed-decisions` (ModernBERT-large, 421M, 1,024, fine-tuned for four workflows) | S1, S2, S3 | vendor-reported |
| L07 | The card says `act_probability` carries no usable signal yet: it reads 1.0 for almost every input, its raw logits score an AUROC of 0.30 on 396 labelled decisions, against 0.77 for `confidence` | S1 | vendor-measured, one labelled set |
| L08 | Issue #185: the head layers are pre-norm and nothing normalizes their output, so the `[CLS]` vector reaching the unnormalized act head is about 300× the encoder's scale and saturates it; the scorer starts with its own LayerNorm and is unaffected | S7 | measured by the issue author on laya 0.3.5, open |
| L09 | A `noul` question renders its two options as `false:` and `true:`, and on the English checkpoint that label pair can decide the answer instead of the state | S1, S8 | #156 closed 2026-09-23; card still warns |
| L10 | On the typed-decisions benchmark the base English checkpoint scores 0.362 accuracy, below the 0.461 majority-class baseline, while the checkpoint fine-tuned on that benchmark scores 0.766 | S1 | vendor-measured, 2,000 decisions |
| L11 | Options share the question budget; at 77 options each label keeps only about 3–4 tokens, and Laya scores 0.425 on Banking77 against a third-party-published 0.870 for Jev | S1 | Laya at the 256-token head budget on 77 labels; Jev's 0.870 is third-party, on 72 labels, not measured by Convai |
| L12 | The English checkpoint fails on non-Latin scripts while staying confident (Khmer: 0.000 accuracy at 0.952 confidence), which is why the Router sends such text to the multilingual checkpoint | S1 | vendor-measured |
| L13 | `laya-serve` exposes the same `POST /v1/systemone` request and response shape as TypeSafe Jev, so a TypeSafe client can switch by base URL | S1 | — |
| L14 | TypeSafe AI introduced Jev on 2026-09-15 as the first of a class it calls System One models, a name taken from Kahneman's fast System 1 | S11, S12 | — |
| L15 | TypeSafe defines three primitives: Choice (option, per-option probabilities, confidence), Score (score, per-level probabilities, confidence) and Noul (probability that the answer is yes) | S12 | — |
| L16 | TypeSafe's endpoint is `POST https://api.typesafe.ai/v1/systemone` | S12 | — |
| L17 | TypeSafe says Jev cannot hallucinate and ties this to type safety; a Choice accepts up to 255 options | S11, S12 | vendor claim |
| L18 | TypeSafe's docs say calibration is measured over groups of predictions and does not make any single answer correct | S12 | — |
| L19 | Laya's sequence is `[CLS] <type> question: <instructions> [SEP] [MASK] opt0 [MASK] opt1 … [SEP] <state> [SEP]`; each option text is capped at 48 tokens; if options overflow the budget each is cut to max(4, (budget − 16) // k) tokens; the question keeps at least 8 tokens; the state gets what remains of `max_len` | S4, S5 | laya 0.3.20 `build_sequence` |
| L20 | `predict()` builds one sequence per question, tokenizes the state once and copies it into every question's row, collates the rows into one batch for one forward pass, and reports `input_tokens` as the sum of all rows with `output_tokens` 0; a long state is cut from the end, a list of conversation turns from the start | S5 | laya 0.3.20 `_encode_state`, `predict_batch`, `build_sequence` |
| L21 | Options render as `key: description` (choice), `level i: description` (score) and `false: …` / `true: …` (noul); a noul's answer is the probability of the second, `true`, option | S5 | — |
| L22 | The head adds a learned question-type embedding to every position, runs two pre-norm `nn.TransformerEncoderLayer`s (16 heads, feed-forward 4d), gathers the marker positions, and scores them with LayerNorm → Linear → GELU → Linear(d, 1); unused marker slots are masked to −10,000; the act head reads `[CLS]` plus four summary features of the option distribution; the only attention mask is the padding mask, so options attend to each other | S4, S5 | — |
| L23 | Returned probabilities divide the logits by a fitted temperature chosen by question type and option count (clamped to 0.5–5); `confidence` is 1 − H(p)/ln k for choice and score and max(p) for noul; `answer_confidence` is max(p); `score` is the expected level Σ i·pᵢ | S5 | laya 0.3.20 |
| L24 | The English config ships temperatures 1.7602 (choice, 3–5 options), 1.2514 (score, 3–5 levels) and 1.9834 (noul); the typed-decisions config ships fitted values too; the multilingual config ships 1.0 for every type and no per-count values | S4 | commit 55cf4c4e |
| L25 | ModernBERT-large: 28 layers, hidden 1,024, 16 heads, GeGLU with intermediate size 2,624, pre-norm, no linear biases, vocabulary 50,368, 395M parameters; every third layer is global with RoPE θ 160,000, the rest use a 128-token local window with θ 10,000; trained on 2 trillion tokens with a native 8,192 context | S15 | paper Table 4 and §2 |
| L26 | ModernBERT removes padding tokens before the embedding layer (unpadding) and runs attention on the jagged batch with FlashAttention's variable-length kernels | S15 | the paper's GPU path |
| L27 | Rotary position embedding encodes position by rotating query and key pairs, so attention scores depend on relative offset | S17 | — |
| L28 | GeGLU is a gated linear unit whose gate uses GELU | S18 | — |
| L29 | Sliding-window local attention restricts each token to a fixed neighbourhood | S19 | — |
| L30 | In transformers 5.17, a local ModernBERT layer lets position i attend to j only when abs(i − j) ≤ 64 (half of the 128 window), and the model runs on the padded batch with masks rather than unpadding | S31 | this library version, SDPA path |
| L31 | mmBERT uses ModernBERT's architecture with the Gemma 2 tokenizer, trained on 3T tokens in over 1,800 languages; its base model has 22 layers, 110M non-embedding and 307M total parameters, and extends context to 8,192 | S16 | preprint |
| L32 | BERT pre-trains by predicting 15% of tokens, replacing 80% of them with `[MASK]`; its `[CLS]` vector feeds classification; BERT-large has 340M parameters | S13 | — |
| L33 | BERT handles SWAG's four-way choice by building four sequences, one per candidate, and softmaxing a learned dot product with each `[CLS]` vector | S13 §4.4 | — |
| L34 | Yin et al. treat each label as an entailment hypothesis, so zero-shot classification over k labels needs k premise–hypothesis passes | S21 | — |
| L35 | PET turns classification into a cloze question and reads the answer from BERT's masked-token prediction through a verbalizer that maps labels to words | S22 | — |
| L36 | UniMC puts every option into one sequence behind its own `[O-MASK]` token, predicts yes/no at each, and trains a softmax across options; an attention mask stops options attending to each other | S23 §3 | — |
| L37 | GLiNER prefixes each entity type with an `[ENT]` token and encodes the types and the text together in one bidirectional pass | S24 §2 | — |
| L38 | GLiClass prefixes each label with a `«LABEL»` token, encodes labels and text jointly in one forward pass, and adapts PPO for classification | S25 §2 | preprint |
| L39 | GLiGuard (May 2026) encodes task definitions and label semantics as token schemas and evaluates many safety tasks in one non-autoregressive pass of a 0.3B encoder | S32 | preprint |
| L40 | Cloze-style prompting of masked language models is one branch of a surveyed family of prompt-based methods | S26 | survey |
| L41 | Format restrictions such as JSON mode lowered LLM reasoning scores but were competitive or better on classification tasks | S27 | the paper's tasks and models |
| L42 | Constrained decoding enforces a schema by masking disallowed tokens at every generation step | S28, S30 | — |
| L43 | GPT-4's pre-trained model was well calibrated on an MMLU subset, and post-training reduced that calibration | S29 Fig. 8 | one model, one subset |
| L44 | A preprint found that renaming two options from 0/1 to no/yes changed 70.4 answers per hundred across Jev and two open Jev-like models, with the rubric text unchanged | S33 | preprint, abstract only |
| L45 | The card describes RLCD as rewarding a strictly proper scoring rule so that honest probabilities maximise expected reward | S1 | vendor description; no training code released |
| L46 | Laya's repository ships inference code and a fine-tuning notebook, but no RLCD pre-training code and no paper | S6 | repository state at commit 4066d5d |
| L47 | The author's earlier SalesRLAgent (March 2025) scored sales conversations from 3,072-dimensional Azure OpenAI embeddings; the author's write-up says that design used frozen embeddings and could not take new questions at run time | S9, S10 | author's account |
| L48 | Convai reports 39.5 ms for one question on a Tesla T4 for the English checkpoint | S1 | vendor-reported, T4, local inference |
| L49 | TypeSafe's docs say the questions in one request are evaluated independently, in parallel, against the same state | S12 | — |
| L50 | The multilingual checkpoint ships with a 1,024-token limit that cuts long documents, and reads up to 8,192 when called with `max_len=8192` | S1, S2 | — |
| L51 | The Router detects the script and language and sends non-English text to the multilingual checkpoint | S1 | — |
| L52 | The Transformer encoder stacks blocks of multi-head self-attention and a position-wise feed-forward network, each wrapped in a residual connection with layer normalization | S14 §3.1 | — |
| L53 | Pre-norm (Pre-LN) places layer normalization inside each residual branch, before the sublayer, so the residual stream itself is not normalized between blocks and a final normalization is added at the end | S20 | — |
| L54 | The card says the checkpoints ship over-confident and should have their temperatures refitted on the user's own data | S1 | vendor statement |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S23 | Figure 3 (UniMC input and O-MLM) | lineage / L36 | shows the one-sequence option-mask format | ACL Anthology papers are CC BY 4.0, but our lineage figure compares seven formats on our own ticket, which the source figure cannot do | https://aclanthology.org/2022.emnlp-main.474.pdf | do not reuse — our comparative figure carries the analysis |
| F2 | S1 | `assets/laya_vs_jev_full.png` | none | vendor comparison chart; Part 4's material | Apache-2.0 repo asset, but vendor marketing | https://huggingface.co/convaiinnovations/laya | do not reuse |

## Open questions

- The card gives two different typed-decisions accuracies for the multilingual base checkpoint (0.342 in its table, 0.352 in *Honest Limits*). The article uses neither.
- The English and typed-decisions configs carry identical `temperature_by_options` and `training` blocks. Whether the root config was copied from the fine-tuned one is not stated. The article reports only which temperature was applied.
- Whether Sun et al. 2026's "two open Jev-like models" include Laya is not stated in the abstract. The article does not say it does.
