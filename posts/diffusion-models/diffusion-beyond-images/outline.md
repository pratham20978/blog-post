# Outline — Diffusion Beyond Images: Video, Audio, 3-D and Molecules

Series `diffusion-models`, part 10 of 12 (`series_position: 10`). Private build artifact.

## Brief

- **Answers (plan.md):** what changes when the data isn't a 2-D grid?
- **Owns:** video, audio, 3-D, molecules, time series; the ACM survey's application taxonomy (Yang et
  al. 2023, Table 3) lands here, re-cut by what changes for the denoiser.
- **Tier:** L3 (plan: 6,500 words, 11 figures). Four distinct things to learn (a new axis to keep
  coherent, symmetries the model must respect, variables that do not live on a line, conditioning on an
  observed part), each shown on a modality; the smallest honest worked example (Part 1's 16 numbers read
  four ways) fits on one screen, but the mechanisms need a page each. Adjacent option: L4 with a section per
  modality and audio and time series given their own labs.
- **Difficulty:** intermediate. Assumes Part 1 (the forward step and the four moving parts) and what a
  tensor shape is. Attention, latent space, equivariance, NeRF, mel spectrogram, torsion angle and CRPS are
  introduced where first used. Adjacent option: advanced, which would add the reverse SDE on a manifold and
  the VSD derivation.
- **Can assume:** Part 1 (published). **Names in plain text:** Part 2 (latent space, the five axes), Part 4
  (backbones, attention cost), Part 6 (DDIM as the sampler the lab uses), Part 8 (guidance weight w; the
  replacement-inpainting result), Part 9 (FID, and the rule that quoted scores keep their setup).
  **Defers:** discrete tokens (atom types beyond one-hot) to "later in this series", unnamed.
- **Lab:** G1 · runs anywhere. One numpy file, `beyond.py`, on crescent world (parts 5–9's toy, unchanged
  per frame): crescent world in motion (a crescent turning a quarter-turn per frame) with exact per-frame
  and joint denoisers; noise schemes (independent, mixed, shared, warped); forecasting by replacement
  against exact conditioning; score distillation on crescent world with an identity renderer; and the
  size census and wrapped-normal arithmetic. Expected under 2 min on one core. L3 ladder: E1–E4. No access
  request (see `../access.md`: G0–G1 planned for part 10).
- **Social:** feed cards only, as for parts 8–9 (owner, 2026-10-19).

## Section budget (target about 6,900 in the validator's count, references included)

| Section | Target | Job |
|---|---|---|
| Insights + who + notice + jump list | 190 | the answer: the forward step is shape-blind; what changes is coupling, symmetry, space, scale, conditioning |
| Why this matters | 120 | Align your Latents: per-frame upsampling kept FID (19.71 vs 19.85) and tripled FVD (45.39 to 165.98) |
| The problem | 430 | five things change; the survey's six task categories vs its three special structures; a table mapping modalities; size census (FIG_01) |
| Worked example | 520 | Part 1's 16 numbers: one forward step, four readings (image, audio, video, points) and what each denoiser must know (FIG_02) |
| Intuition | 280 | the denoiser carries all the structure; the flipbook analogy and where it breaks |
| Why does a frame-by-frame image model break video? | 850 | one-pixel agreement 1/2 + arcsin(ρ)/π; crescent world in motion (FIG_03); joint models, temporal layers, latents (FIG_04); PYoCo, Text2Video-Zero, warped noise; FVD |
| What changes when the signal is sound? | 380 | waveform length and receptive field; spectrogram and vocoder; latents (FIG_05) |
| When order and orientation don't matter | 850 | point sets (Point-E, Luo & Hu, PVD); E(3): zero centre, equivariance, EDM's ablation (FIG_06); AF3 and MCF; variables on circles and rotations (FIG_07) |
| How do you make 3-D objects without 3-D data? | 600 | SDS loop (FIG_08); SDS on crescent world (FIG_09); Janus (FIG_10); fixes |
| Why is forecasting inpainting along time? | 420 | conditional vs replacement (FIG_11); CSDI CRPS; TimeGrad; TSDiff; CRPS |
| The math | 380 | shape-blind forward step; agreement probability; invariance with the zero-centre projection on the worked example; wrapped normal; SDS in this series' notation |
| Implementation | 230 | numpy: noise schemes, zero-centre noise, wrapped noise |
| Limitations and common mistakes | 280 | warning plus four mistakes |
| Key takeaways | 110 | four claims |
| Try it yourself | 220 | E1 and E3 answerable from the article |
| References | ~1,000 | lab downloads + 28 sources |

## Figure plan (route gate run per figure)

| # | Section | One thing it must communicate | Route | Why (the clause that settled it) | Draft caption |
|---|---|---|---|---|---|
| FIG_01 | The problem | one sample ranges from 261 numbers (a molecule) to 24.8 million (14 video frames), and latents cut audio and video by 32–48x | chart | Q1 — counts computed from published configs (lab `census`, ledger L13, L21, L23, L24, L28, L29, L43, L46) | a sample's size spans five orders of magnitude; latent spaces exist because video and audio sit at the top |
| FIG_02 | Worked example | the same 16-number forward step read as an image, a waveform, a 4-frame strip and 8 points, with what each denoiser must treat as related or as the same | placed | Q4 — a grid of real values in four layouts, side by side | the noise step is identical; the neighbours and the symmetries differ |
| FIG_03 | Video | per-frame model: independent noise flickers, shared noise freezes, mixed noise trades one for the other, warped noise moves only by a symmetry; the joint model moves | chart | Q1 — lab measurements, 4,096 clips per scheme | no amount of noise correlation makes an image model animate; warping does, for one prescribed motion |
| FIG_04 | Video | how a joint video denoiser is built from an image one: frames as a batch for spatial layers, pixels as a batch for temporal layers, in an 8x latent; shapes on every edge | placed | Q5 — 7 nodes, one path, a tensor shape on every edge | temporal layers are the only place frames meet |
| FIG_05 | Audio | one 10-s clip as waveform (160,000), mel spectrogram (64,000), latent (32,000), with a 0.38-s receptive field to scale | placed | Q4 — lengths must be drawn to scale | representation choice sets what the denoiser must reach |
| FIG_06 | Molecules | three ways to handle rotation on one network: none 63.2%, augmentation 71.6%, equivariance 82.0% stable molecules (data 95.2%) | chart | Q1 — ledger numbers (L44), one table | same network, same data; only how rotations are handled changes |
| FIG_07 | Molecules (circles) | Gaussian noise on an angle wraps; by σ = π the density is within 3% of flat, so the prior is uniform | plot | Q4 — densities computed on the circle (lab `census`) | on a circle the noise ends uniform, not Gaussian |
| FIG_08 | 3-D | the SDS loop: parameters → render → noise → frozen 2-D denoiser with guidance → residual → back to parameters | placed | Q5 — 6 nodes, one loop; a quantity on every edge | the 2-D model never sees the object, only its renders |
| FIG_09 | 3-D | SDS on crescent world: every run lands on one of two images per class; brightness, jitter and pixel detail vanish; guidance pushes contrast past the real range | chart | Q1 — lab measurements, 256 runs per weight | SDS returns modes, not samples |
| FIG_10 | 3-D | the Janus problem and content drift | source | source check — MVDream's Figure 1 is the failure itself, CC BY 4.0 (ledger F1) | Reproduced from Shi et al. 2024, Figure 1 |
| FIG_11 | Time series | forecasting by replacement leaves predictions inconsistent with the observed frames; exact conditioning does not | chart | Q1 — lab measurements, 4,096 clips per setting | conditioning must reach the model, not just the noisy input |
| COVER | — | the series' house template cover | placed | template cover, as parts 6–9 | — |

## Term map

| Term | First section | What | Why used here | When it matters |
|---|---|---|---|---|
| modality | Insights / The problem | a kind of data: image, video, audio, 3-D shape, molecule, time series | the post's unit of comparison | choosing the representation |
| frame, clip | Why this matters | one image in a video; a short video | video's new axis | anything with time |
| FVD | Why this matters | FID's video counterpart on I3D action-recognition features over whole clips | scores temporal defects | judging video; compare only within one table |
| representation | The problem | the array x₀ actually is: pixels, latents, waveform, mel, coordinates, angles | decides what the denoiser must learn | first design decision |
| latent space / autoencoder | The problem | a learned compressed array a decoder maps back to data (Part 2) | how video and audio fit | when the raw array is too large |
| neighbour / coupling axis | Worked example | which values the denoiser treats as related | what a per-frame model lacks | video, audio, time series |
| permutation, invariance, equivariance | Worked example / molecules | invariant: output unchanged by a transformation; equivariant: output transforms the same way | point sets and molecules have no order or orientation | sets, molecules, rotations |
| centre of gravity (zero-CoM) | Worked example / molecules | the mean position of the points; diffusion on the subspace where it is zero | translation invariance without an improper prior | 3-D coordinates |
| temporal layer / factorized attention | Video | layers that mix frames at each spatial position; spatial layers keep frames independent | the cheap way to make an image model joint | video, multi-view, CSDI's features × time |
| attention | Video | a layer that lets every token read every other token it is allowed to see | what gets factorized | cost grows with token count (Part 4) |
| noise prior (mixed, warped) | Video | how starting noise is correlated across frames | the training-free fix and PYoCo's training fix | per-frame models; fine-tuning |
| replacement vs reconstruction guidance | Video / time series | imposing observed values on the noisy input vs adding the missing gradient | why conditional sampling fails or works | prediction, imputation |
| receptive field | Audio | how many input samples one output can see | waveform length vs network reach | raw audio |
| mel spectrogram, vocoder | Audio | time-frequency magnitudes on a perceptual scale; a model that turns them back into a waveform | the standard audio representation | when phase matters |
| point cloud | Point clouds | an unordered set of 3-D points | a set, not a grid | 3-D shapes |
| E(3), equivariant network (EGNN) | Molecules | translations, rotations and reflections of 3-D space; a network whose output moves with its input | molecules' symmetry | 3-D molecules |
| torsion angle, conformer | Molecules | rotation about a bond; a 3-D arrangement of a molecule | variables on a circle | conformer generation, docking |
| wrapped normal | Molecules | a Gaussian taken mod 2π | Gaussian noise on a circle | angles |
| frame (protein), rotation group | Molecules | a residue's position plus orientation; the space of 3-D orientations | noise on rotations | proteins |
| NeRF | 3-D | a network mapping 3-D points and directions to colour and density, renderable from any camera | the "object" SDS optimizes | text-to-3-D |
| score distillation sampling (SDS) | 3-D | gradient from a frozen 2-D model's noise residual on renders | 3-D without 3-D data | text-to-3-D |
| mode-seeking | 3-D | converging to the most likely point instead of sampling | SDS's failure | judging any distillation-by-optimization |
| Janus problem | 3-D | a 2-D prior puts the front view on every side | view-independent prior | text-to-3-D |
| imputation, forecasting | Time series | filling missing values; generating future values | conditional generation along time | time series |
| CRPS | Time series | a score for a predicted distribution against the observed value | probabilistic forecasts | comparing forecasters within one table |

## Series handoffs

- Names Part 1 (published), and Parts 2, 4, 6, 8 and 9 (not published) in plain text where used; the
  manifest lists each spot.
- Defers truly discrete data (tokens, atom types as categories) to "later in this series".
- Hands Part 11 the survey's discrete-data class (Section 5.1) and the observation that one-hot plus
  Gaussian noise is the continuous workaround EDM uses.
