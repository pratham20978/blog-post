# Outline — diffusion-backbones-unet-to-dit

Series: `diffusion-models`, part 4 of 12. Read `../plan.md` and `../context.md` before editing.

## Brief

- **Subject:** machine learning / generative modelling — the denoiser network.
- **Tier:** L4 · **Difficulty:** advanced. Set by the series plan, not re-proposed. L4 because the
  reader must learn four linked things — a real U-Net's shapes and where its cost lives, DiT's
  token arithmetic at two patch sizes, MM-DiT's two-stream block, and the attention-cost and
  memory arithmetic that decides between them — and the smallest honest example (one real model
  traced block by block) needs a page. Advanced because it assumes convolution, attention and
  tensor shapes, and part 1's account of what the denoiser is for.
- **Audience:** an engineer who has loaded a Stable Diffusion or SD3 checkpoint, seen "860M" or
  "2B" on a model card, and wants to know what those numbers do and do not predict about speed,
  memory and quality.
- **The one question this part owns:** what is the denoiser, block by block, and when do you swap it?
- **What falls out of it, and the post also owns:**
  1. Where does a U-Net keep its parameters, and where does it spend its compute? (opposite ends)
  2. What does DiT's patch size buy? (4× tokens, ~4× compute, same parameters, much lower FID)
  3. What do MM-DiT's two streams cost? (≈2× parameters per block, 2.4% of compute)
  4. When does attention dominate? (share = N/(N+6D); half at N = 6D)
  5. How much memory does a backbone need? (weights, 16 B/param training state, activations, encoders)
- **Deliberately deferred:** prediction targets and loss weighting → part 5; samplers and step
  counts → part 6; ControlNet and adapters → part 8; video/3-D backbones → part 10.
- **Series links:** part 1 is published and may be named in plain text. Parts 2 and 3 are not
  live, so they are not named; the post re-establishes the one fact it needs from part 2 (the
  denoiser's interface) in two sentences rather than pointing at an unpublished page.
- **Must not repeat from part 2:** part 2 draws an *illustrative* three-level U-Net, introduces
  adaLN, U-ViT and MM-DiT in a paragraph each, and gives N = HW/P². This post measures the real
  SD 1.5 U-Net, DiT-XL and SD3-2B, and adds what part 2 does not have: per-level parameter/FLOP
  split, patch-size compute, per-stream cost, the N/(N+6D) law, measured attention memory, and
  the memory bill.
- **Lab:** **G1** — CPU PyTorch 2.14 and diffusers 0.40 in a pinned environment; all models built
  on the `meta` device (exact shapes, parameters, FLOPs, no weights), plus one real CPU attention
  sweep and an optional real U-Net forward pass. No access request: a GPU would change timings,
  not any claim the post makes, and the post labels CPU timings as CPU timings.
- **Target:** 8,000 words, 13 figures, one lab (README, `census.py`, requirements, two captures).

## Section budget

| Section | Budget | Reader can now… |
|---|---:|---|
| Insights + who this is for + jump list | 200 | say where a U-Net's and a DiT's compute goes, in two sentences |
| Why this matters | 220 | see why "2B parameters" does not answer "will it fit, how fast" |
| The problem | 450 | state the denoiser contract and the token-count tension with sizes |
| Worked example | 850 | shrink part 1's 4×4 patch two ways, count tokens and pairs, scale to a real latent |
| Intuition | 400 | describe a backbone as a budget over positions and width, and where the analogy breaks |
| What does a real U-Net do to a tensor? | 1,300 | trace SD 1.5 block by block, read the skip stack, explain the params-vs-FLOPs inversion |
| What does DiT's patch size buy? | 1,100 | compute DiT's tokens and compute at two patch sizes, read the adaLN-Zero block |
| How does MM-DiT run two streams through one attention? | 900 | explain the dual-stream block with SD3-2B's shapes and its cost split |
| When does attention dominate the bill? | 800 | derive N/(N+6D), place any model on it, read naive vs fused memory |
| How much memory does a backbone need? | 650 | compute weights, training state, activations and encoder memory |
| When should you swap the backbone? | 550 | choose by token count, conditioning and evidence, with the open question stated |
| The math | 500 | count conv, linear and attention FLOPs and reproduce 118.6 GMAC |
| Implementation | 400 | patchify, an adaLN-Zero block, and a meta-device FLOP count |
| Limitations and common mistakes | 450 | avoid six concrete misreadings |
| Key takeaways + Try it yourself + References | 450 | — |

## Term map

| Term | First section | What | Why | When |
|---|---|---|---|---|
| denoiser / backbone | The problem | the trained network; its architecture family | the only learned part, and the bulk of compute | choosing or swapping a model |
| latent, downsampling factor f | The problem | the autoencoder's compressed grid; f = 8 here | sets the grid the backbone sees | reading any resolution claim |
| token, sequence length N | Worked example | one vector per position or patch | attention cost grows with N² | any transformer cost |
| patchify, patch size p | Worked example | cutting the latent into p×p squares, one token each | sets N = (h/p)(w/p) | DiT configs, "/2" in names |
| U-Net level, skip connection | Worked example / U-Net | one resolution of the pyramid; tensor saved on the way down and concatenated on the way up | returns detail the bottleneck lost | U-Net memory and shapes |
| ResNet block, GroupNorm | U-Net | conv–norm–activation with an identity path; per-example channel-group normalisation | the U-Net's local workhorse | U-Net internals |
| self-attention / cross-attention | U-Net | tokens attend to tokens / to text tokens | global context; prompt injection | where text enters |
| head, head width | U-Net | parallel attention sub-spaces | config trap in diffusers | reading configs |
| FLOP, multiply-add (MAC), GFLOP vs Gflops | U-Net / DiT | one multiply-add = 2 FLOPs | DiT's "Gflops" are MACs | comparing compute numbers |
| adaLN, adaLN-Zero, FiLM, AdaGN | DiT | condition-predicted scale/shift (and gate) on a normalisation | how t and class enter a DiT | conditioning design |
| MM-DiT, stream, joint attention | MM-DiT | separate weights per modality, one attention over both sequences | bidirectional text–image exchange | SD3/FLUX |
| fused attention, FlashAttention | Attention | exact attention without storing the N×N matrix | memory linear in N | any N above a few thousand |
| mixed-precision Adam state | Memory | 16 bytes per parameter | training memory floor | fine-tuning budgets |
| activation memory | Memory | tensors kept for backward | dominates at high resolution | training at 1024px |

## Figure plan

Route gate run per figure; the `source` check was run first for every paper-backed figure — the
candidate paper figures (DiT Fig. 3, SD3 Fig. 2, DiT Fig. 2, U-Net Fig. 1) have no reuse licence,
so none is reused, and every figure below adds measured shapes or numbers the papers' figures do
not carry.

| # | Section | Communicates | Route | Why | Draft caption |
|---|---|---|---|---|---|
| 1 | The problem | three backbones honour one contract: same-shape in, same-shape out, but differ in how many positions each layer sees | placed | Q4 — three small multiples, each drawn with its real grid or token strip | Every backbone maps a 4×64×64 latent to a 4×64×64 prediction; they differ in what happens to the 4,096 positions in between |
| 2 | Worked example | part 1's patch shrunk two ways: pooled to 2×2 (lossy), patchified to 4 tokens (lossless), with pair counts | placed | Q4 — a grid of real values and token strips; values are the figure | Pooling throws values away and needs a skip to recover them; patchifying keeps all 16 and moves them into token width |
| 3 | U-Net | SD 1.5's real trace: every block's shape, all 12 skips, attention token counts | plot | Q1 — every shape and parameter count is the lab's hook capture, drawn to scale | The U-Net trades positions for channels on the way down and gets detail back through 12 skips |
| 4 | U-Net | inside one 64×64 stage: ResNet block then transformer block, with shapes on every edge | mermaid | Q3 — 14 nodes, two side inputs (time, text) cross the main path | Time enters as a channel bias; text enters only through cross-attention's keys and values |
| 5 | U-Net | where parameters live vs where FLOPs go, per level | chart | Q1 — measured parameter and FLOP counts per level | 3.4% of the parameters, 38.2% of the compute: the finest level is cheap to store and expensive to run |
| 6 | DiT | XL/4 vs XL/2 on the same latent: token lattices, params, compute, FID | placed | Q4 — two lattices drawn to scale side by side with ledger and lab numbers | Same 675M parameters, four times the tokens, 4.08× the compute, less than half the FID |
| 7 | DiT | the adaLN-Zero block with shapes; six modulation vectors | mermaid | Q3 — 12 nodes; the condition path feeds four points on the main path | The condition never becomes a token: it scales, shifts and gates every sublayer |
| 8 | MM-DiT | one SD3-2B block: two streams, separate weights, one joint attention over 4,250 tokens | mermaid | Q3 — two parallel paths that merge and split, 13 nodes | Two transformers that meet only inside attention |
| 9 | MM-DiT | parameters vs FLOPs by stream at 1024px | chart | Q1 — measured per-stream counts | The text stream holds half the weights and does 2.4% of the arithmetic |
| 10 | Attention | the share law N/(N+6D) with real models on it | plot | Q1/Q4 — a closed-form curve with measured points from the lab | Attention passes a third of a block's FLOPs near N = 3D and half at N = 6D |
| 11 | Attention | naive vs fused attention on this CPU: time and largest allocation vs N | chart | Q1 — measured on the build machine | Same FLOPs, 58× less memory at 4,096 tokens: the score matrix is what the fused kernel never stores |
| 12 | Memory | the memory bill per model: weights, training state, activations, encoders | chart | Q1 — arithmetic on measured parameter counts and ledger formulas, labelled as computed | Weights are the small part; activations and a T5 encoder dominate at 1024px |
| 13 | Swap | decision map: token count vs conditioning, with real models placed | placed | Q5 — a two-axis trade-off with 7 placed models, no crossings | Swap when the token count or the conditioning changes, not when the parameter count does |
