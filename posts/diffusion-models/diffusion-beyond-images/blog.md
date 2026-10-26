---
title: "Diffusion Beyond Images: Video, Audio, 3-D and Molecules"
slug: diffusion-beyond-images
date: 2026-10-21
updated: 2026-10-21
summary: "Diffusion's noise step never sees the data's shape. Off the image grid the denoiser's job changes: frames must agree, symmetries hold, angles wrap, sizes grow."
tags: [machine-learning, diffusion-model, video-generation, audio-generation, 3d-generation, molecule-generation, time-series]
category: machine-learning
series: diffusion-models
series_position: 10
tier: L3
difficulty: intermediate
prerequisites: ["Part 1 of this series", "what a tensor shape is"]
reading_minutes: 31
cover_image: "COVER"
canonical_url: "https://canery.in/blogs/diffusion-beyond-images"
---

![Four frames of a crescent turning a quarter turn each, above four frames sampled one at a time that flicker and jump](COVER)

> [!NOTE]
> **Insights** — Diffusion's forward process never looks at the shape of its data: it adds Gaussian noise to a list of numbers, so video, audio, 3-D shapes, molecules and time series diffuse with the same arithmetic as images. What changes is the denoiser's job. It must see across a new axis (an image model sampled frame by frame flickers or freezes: none of 4,096 clips moved coherently in this post's lab), respect symmetries such as shuffled points and rotated molecules, handle variables that live on circles, and cope with sizes that latent spaces cut by 32× for audio and 48× for video (in Stable Audio and Stable Video Diffusion).

**Level:** intermediate · **You need:** Part 1 of this series (What a Diffusion Model Actually Does), what a tensor shape is · **Time:** ~31 min

**Jump to:** [worked example](#worked-example) · [video](#why-does-a-frame-by-frame-image-model-break-video) · [audio](#what-changes-when-the-signal-is-sound) · [point clouds and molecules](#when-order-and-orientation-dont-matter) · [3-D](#how-do-you-make-3-d-objects-without-3-d-data) · [time series](#why-is-forecasting-inpainting-along-time) · [math](#the-math) · [implementation](#implementation)

> [!IMPORTANT]
> Numbers this post calls **measured** come from its lab: crescent world, the series' 8×8 toy, now also in motion. Its image and clip distributions are known exactly, so every failure belongs to the sampler or the conditioning, never to a badly trained network. Read the toy's sizes as mechanism, not scale. Results **quoted** from papers keep their model, dataset and protocol, and are compared only within their own table.

## Why this matters

Align your Latents turned an image diffusion model into a video model and tested a shortcut: upsample each frame of a driving video separately, with the image upsampler. Frame quality held, FID 19.71 against 19.85 for the video-aware upsampler, while FVD rose from 45.39 to 165.98. <!-- L10 --> FVD, the Fréchet Video Distance, is FID computed on features of a network trained to recognise actions in clips, so it sees motion as well as frames. <!-- L19 --> Part 9 of this series, Evaluating Generative Models: What FID Measures and Hides, explains FID. Every frame was fine and the video was not, and a per-frame metric would have shipped it. That gap, between data that is right piece by piece and data that is right as a whole, is what changes when diffusion leaves the image.

## The problem

Part 1's recipe treats a sample, x₀, as a fixed-length list of real numbers, and trains a network, the denoiser, to undo noise added to it. An image fits perfectly. Other data bends the recipe in five ways:

1. **A new axis must stay consistent:** frames in a video, samples in a waveform, steps in a time series.
2. **Symmetries:** a point cloud is a set, so listing its points in another order changes the array but not the object; a molecule moved or rotated in space is the same molecule.
3. **Variables that do not live on a line:** a bond's torsion angle is periodic, a residue's orientation is a rotation, an atom's type is a category.
4. **Scale:** one sample ranges from a few hundred numbers to tens of millions.
5. **Part of the sample is given:** a forecast extends an observed past; an imputation fills holes.

The ACM survey of diffusion models sorts its applications by task into six categories: computer vision, natural language generation, temporal data modelling, multi-modal learning, robust learning, and interdisciplinary applications. <!-- L01 --> Separately, it sorts methods for data with special structure into three classes: discrete data, data with invariant structure, and data on manifolds, whether known ones such as spheres and tori or learned ones such as an autoencoder's latent space. <!-- L02 --> The two sorts cross. This post's modalities sit in its task categories as follows, re-cut by which of the five changes each one meets:

| Modality | Survey category | x₀ is usually | New axis | Symmetry | Off-line variables | Often given |
|---|---|---|---|---|---|---|
| Video | vision; multi-modal | frames in a latent space | time | — | — | first frames, a prompt |
| Audio | temporal data; multi-modal | waveform, mel spectrogram or latent | time | — | phase, via a vocoder | a spectrogram, a prompt |
| 3-D shapes | vision; multi-modal | points, or a renderable scene | camera views | point order, rotation | — | a partial scan, a prompt |
| Molecules, proteins | interdisciplinary | atom coordinates and types | — | order, rotation, translation | torsions, orientations, types | a protein pocket |
| Time series | temporal data | features × time steps | time | — | — | the past, observed entries |

Scale is the change you meet first. Figure 1 lines up the sizes of one sample in the papers this post quotes.

![Log-scale bars of numbers per sample, from 7.9 torsion angles and a 261-number molecule to 24.8 million for 14 video frames](FIG_01)
*Figure 1. One sample spans more than five orders of magnitude; latent spaces exist because video and audio sit at the top. Computed from each paper's stated configuration.*

Video and audio sit at the top, which is why both now usually diffuse in a **latent space**, the compressed array an autoencoder maps back to data, introduced in Part 2 of this series, Diffusion Model Architecture: The Complete Guide. Stable Audio's autoencoder holds 95.1 s of stereo in 32 times fewer numbers <!-- L24 -->, and Stable Video Diffusion's holds 14 frames in 48 times fewer. <!-- L12 --> <!-- L13 --> Molecules sit at the bottom, where size is no problem and symmetry is.

## Worked example

Take the 16 numbers of Part 1's 4×4 patch, x₀, and the noise ε drawn for it, at the noise level where √ᾱ = 0.8 and √(1−ᾱ) = 0.6. One forward step is sixteen multiply-adds: the top-left value becomes 0.8 × 0.95 + 0.6 × (−0.55) = 0.76 − 0.33 = 0.43, and so on for the other fifteen. Nothing in that arithmetic depends on what the numbers mean. Now read the same 16 numbers four ways, as Figure 2 does.

![One forward step on Part 1's 16 numbers, and the clean values as a 4x4 image, a 16-sample waveform, four 1x4 frames and eight 2-D points](FIG_02)
*Figure 2. The noise step is the same arithmetic in all four readings; what changes is which numbers the denoiser must treat as related, and which rearrangements it must treat as the same.*

1. **An image.** The value 0.45 in row 2, column 2 has four neighbours: 0.60 above, 0.10 below, 0.80 to the left and −0.55 to the right. A convolution reads exactly those, and the same small filter slides over every position, because an image's statistics do not depend on where you look.
2. **A waveform**, the rows end to end. At 16 kHz the 16 samples last 1 ms. The same 0.45 now has two neighbours, 0.80 before it and −0.55 after it, and one second of sound is 16,000 samples, a thousand of these patches in a row. <!-- L20 -->
3. **A clip** of four frames, each a 1×4 strip (one row per frame). In the clean clip, consecutive frames differ by 0.183 per pixel on average; after the forward step they differ by 0.805, 4.4 times as much. A denoiser that sees one frame at a time has no way to know the frames should agree.
4. **Eight points** in a plane, read in pairs along each row: (0.95, 0.60), (−0.30, −0.85) and so on. The same set can be listed in 8! = 40,320 orders, each a different array. And the noise's eight points have their centre at (0.15, −0.0125), so the forward step also moves the whole cloud by 0.6 times that, (0.09, −0.0075), a shift that says nothing about the shape.

Same arithmetic, four jobs. The image denoiser must respect 2-D neighbours. The audio one must reach far along one axis. The video one must look across frames. The point-set one must give the same answer for all 40,320 orderings and ignore where the cloud sits. The rest of this post takes those jobs one modality at a time.

## Intuition

The forward process is a fixed recipe with no idea what it is noising. Every piece of structure, what is next to what, which rearrangements change nothing, which values wrap around, lives in three other choices: the array you feed in (the **representation**), the space the noise lives in, and the denoiser that undoes it. That is why diffusion travels so well. Changing modality changes those three and keeps Part 1's training loss and sampler.

For video, picture a flipbook drawn by an artist who sees one page at a time and draws whatever the scribble on that page suggests. Give every page a fresh scribble and each page is a good drawing of something different: flicker. Give every page the same scribble and the pages are identical: a frozen flipbook. Copy the scribble and turn it a little on each page, and the drawing turns too, but only by the motion you chose. The analogy breaks in one place: an artist could look back at the previous page, and a per-frame diffusion model has no such input. Correlating the scribbles does not give it one; a video model's job is to add it.

## Why does a frame-by-frame image model break video?

### What can correlated noise buy?

Start with a single pixel that is bright (+1) or dark (−1) with equal chance, sampled with a deterministic sampler, DDIM, the one Part 6 of this series, Diffusion Samplers and Solvers: 1,000 Steps Into 20, analyses. By symmetry, DDIM sends a positive starting noise to +1 and a negative one to −1. Two frames sampled from noises with correlation ρ therefore agree when the two noises share a sign, which happens with probability 1/2 + arcsin(ρ)/π: 50% for independent noise, 67% at ρ = 0.5, 86% at ρ = 0.9 and 100% for identical noise. The lab's sampler matched each of those to within 0.002. Correlation buys agreement and nothing else. If real clips switched the pixel every frame, no positive ρ would help, while negated noise (ρ = −1) would switch it every time, because negation is a symmetry of this pixel's distribution.

### Crescent world in motion

The lab's clips are four crescent-world frames. In each clip the crescent turns a quarter turn per frame, always the same way, and keeps one contrast and one brightness throughout. Each frame on its own is an ordinary crescent-world image, so the per-frame model is the series' exact image denoiser; the joint model is the exact denoiser of whole clips. Figure 3 reads 4,096 clips from each scheme.

![Bars for 4,096 clips per noise scheme: independent noise flickers, correlated noise freezes, warped noise and the joint model move](FIG_03)
*Figure 3. Correlating the per-frame model's noise trades flicker for freezing and never yields a coherent clip; warping the noise works because a quarter turn is a symmetry of the image model. Measured, 4,096 clips per scheme.*

With independent noise, 99.7% of frames are valid crescents (real frames: 99.8%), yet 82% of frame changes flicker in brightness, 49% flip contrast, and only half are quarter turns: not one of 4,096 clips is coherent. PYoCo's mixed noise, one shared draw plus one per frame, sets the correlation between frames' noises. <!-- L15 --> At ρ = 0.9 flicker falls to 45% while 74% of frame changes stop turning; at 0.99 the figures are 1.4% and 91%; identical noise freezes every clip. No ρ produced a coherent clip. Warping frame 0's noise a quarter turn per frame gave 99.6% coherent clips, because turning the image model's input turns its output: the lab measures the mismatch at 3 × 10⁻¹⁵. The joint model gave 99.4%, against 99.5% for real clips.

### How do video models let frames see each other?

The real fix is a denoiser whose input is the whole clip. Video Diffusion Models (VDM) built one by factorizing a U-Net over space and time: each 3×3 convolution becomes 1×3×3, staying inside a frame; spatial attention treats the frames as a batch; and after every spatial attention block, a temporal attention block lets each pixel position look across the frames. <!-- L04 --> **Attention** is the layer that lets every token read every other token it is allowed to see; Part 4 of this series, Diffusion Backbones: U-Net to DiT, Block by Block, counts its cost, which grows with the square of the token count. Splitting it into a spatial and a temporal pass is what keeps a clip affordable, and even then VDM trained on 16-frame clips to fit in memory, though real videos run to hundreds or thousands of frames. <!-- L08 --> Figure 4 traces the shapes through one block.

![Video denoiser block: latent clip 14x4x72x128, spatial layers per frame, temporal layers per pixel across frames, shapes on edges](FIG_04)
*Figure 4. The temporal layers are the only place frames meet; remove them and the block is an image model run 14 times. Shapes from Stable Video Diffusion's configuration.*

Align your Latents went further: it froze a pre-trained image latent diffusion model, inserted temporal layers between its spatial ones, and trained only those. <!-- L09 --> Stable Video Diffusion inserted the same kind of temporal layers into Stable Diffusion 2.1, adding 656 million parameters for 1,521 million in all <!-- L12 -->, in a latent with 4 channels at an eighth of each side. <!-- L13 --> Masking the temporal layers turns such a model back into an image model, so it can also train on still images: adding 8 images per 16-frame video took VDM's FVD from 202.28 to 57.84 on its text-to-video task. <!-- L05 -->

Noise priors still matter when the model is joint. PYoCo inverted real video frames to noise one frame at a time with an image model and found the noise maps of one video had average cosine similarity 0.206, against 0.001 across videos. <!-- L14 --> Fine-tuning an image model to video on UCF-101 with correlated rather than independent noise lowered FVD from 566.67 to 337.40. <!-- L16 --> There the correlation is a training prior for a joint model, not a substitute for one. Text2Video-Zero does use an untouched image model: it builds each frame's starting noise by partly denoising the first frame's, shifting it by a chosen camera motion and re-noising it, and lets every frame attend to the first. <!-- L17 --> That is the lab's warped noise with a translation in place of a turn, and it has the same two limits. It produces only the motion you prescribe. And a warp that interpolates between pixels shrinks the noise: shifting by a fraction α of a pixel leaves variance α² + (1−α)², half at half a pixel, while reusing one noise for every frame leaves textures stuck to the screen. <!-- L18 --> The lab's exercise E3 measures what half the variance does.

## What changes when the signal is sound?

Audio is one long axis. A second of speech at 16 kHz is 16,000 samples <!-- L20 -->, and a denoiser must relate samples far apart to keep a voice or a note consistent. DiffWave's denoiser stacks **dilated convolutions**, each skipping a growing gap between the samples it reads; 30 layers with gaps from 1 to 512 see 6,139 samples, 0.38 s at 16 kHz, and running T reverse steps lets information travel up to T times as far. <!-- L21 -->

Most systems shorten the axis first. A **mel spectrogram** records the signal's energy in perceptually spaced frequency bands over short windows; it keeps magnitudes and drops phase, so a **vocoder** must turn it back into a waveform. <!-- L25 --> DiffWave also works as a vocoder, and as one it matched a WaveNet vocoder's listener ratings, 4.44 against 4.43. <!-- L22 --> AudioLDM takes 10 s of 16 kHz audio, 160,000 samples, computes a 64-band mel spectrogram with a hop of 160 samples (64,000 numbers), compresses it with a variational autoencoder to 32,000, diffuses there, and decodes with a HiFi-GAN vocoder. <!-- L23 --> Stable Audio's autoencoder skips the spectrogram: it maps 44.1 kHz stereo to 64 channels at 1/1,024 of the sample rate, 32 times fewer numbers, and generates 95 s of audio in 8 s on one A100. <!-- L24 --> Figure 5 draws one 10-s clip in each form, to scale.

![One 10-second clip drawn to scale as 160,000 waveform samples, 64,000 mel values and 32,000 latent values, with a 0.38 s reach](FIG_05)
*Figure 5. Shortening the axis is most of what changes for sound: an image-style network then runs on a spectrogram or a latent, and the encoder and vocoder carry the rest. Sizes computed from AudioLDM's and DiffWave's configurations.*

So for audio the change is mostly representation, and the cost moves into the encoder and the vocoder. The axis still has to be generated as a whole, exactly as a video's frames do; it is only shorter once compressed.

## When order and orientation don't matter

### Point clouds are sets

A **point cloud** is a set of 3-D points sampled from a surface. Early generators stored one as an N × 3 matrix <!-- L27 -->, which makes the order of the rows part of the data. A function is **invariant** to a transformation if its output does not change, and **equivariant** if its output changes the same way; the ACM survey notes that diffusion models which ignore such invariances can perform worse. <!-- L03 --> Diffusion has met the set in three ways. Luo and Hu model each point as an independent draw given a latent that describes the shape, so the cloud's probability is a product over points and order cannot matter. <!-- L26 --> Point-E feeds its K × 6 array, a position and a colour per point, to a transformer without positional encodings, so the network cannot tell which row is which: it is permutation-equivariant, and shuffling its input only shuffles its output. <!-- L29 --> PVD diffuses 2,048 points per shape directly, and completes a partial scan the way an inpainter fills a hole: the observed points stay fixed in both directions while only the missing ones are denoised. <!-- L28 -->

### Molecules add rotation and translation

A molecule in 3-D has two more symmetries: moved or rotated, it is the same molecule. EDM, the E(3) Equivariant Diffusion Model, handles translation by keeping positions on the subspace where their centre of gravity is zero, since no distribution over all of space can be the same everywhere and still integrate to one; it subtracts the centre from every noise draw, as the worked example's (0.15, −0.0125) would be. <!-- L41 --> It handles rotation with an **E(3)-equivariant graph network** (EGNN), whose predicted noise turns when its input turns. <!-- L40 --> An invariant starting noise plus an equivariant denoiser gives samples whose distribution is the same in every orientation. <!-- L45 --> Atom types ride along as one-hot vectors with Gaussian noise. <!-- L42 --> Figure 6 shows what equivariance bought on QM9, about 130,000 small molecules of up to 29 atoms. <!-- L43 -->

![Bars of QM9 molecule stability: non-equivariant 63.2%, rotation-augmented 71.6%, equivariant EDM 82.0%, training data 95.2%](FIG_06)
*Figure 6. Same network size, same data and sampler; only the handling of rotation changes, and equivariance closes more than half the gap to the data. Quoted from Hoogeboom et al. 2022, Table 1: 10,000 molecules per model, three runs.*

A molecule is **stable** when every atom has the right number of bonds. <!-- L44 --> Without equivariance, 63.2% of generated molecules were; trained on randomly rotated copies, 71.6%; equivariant, 82.0%, against 95.2% for the training data. <!-- L44 --> At larger scale the comparison is contested. AlphaFold 3's structure diffusion runs on raw atom coordinates with no equivariant processing, its authors finding none necessary <!-- L53 -->, as MCF had: a plain transformer of up to 242 million parameters that beat equivariant and torsional models at generating molecular shapes. <!-- L54 --> MCF's own check qualifies its result: rotating each training molecule once at random hurt, which suggests the dataset's molecules share a coordinate frame; rotating them every epoch cost a little, and a larger model recovered most of it. <!-- L55 --> So the evidence splits: at EDM's scale, building rotation into the network won clearly; at the larger scale and on the different tasks of MCF and AlphaFold 3, plain networks did well without it.

### Some variables live on circles and rotations

A **torsion angle**, the rotation about a chemical bond, is periodic: 179° and −179° are 2° apart. Torsional diffusion generates **conformers**, a molecule's possible 3-D arrangements, by diffusing only those angles: a GEOM-DRUGS molecule averages 44 atoms, 132 coordinates, but only 7.9 torsion angles. <!-- L46 --> Gaussian noise on an angle wraps around the circle, giving a **wrapped normal**, and as it grows the density flattens instead of spreading forever, so the noise ends at the uniform distribution rather than at a Gaussian. <!-- L47 --> <!-- L56 --> Figure 7 shows how fast.

![Wrapped normal densities on a circle at three noise levels flattening toward uniform, beside line Gaussians that spread past one turn](FIG_07)
*Figure 7. On a circle, noise ends uniform: at σ = π the wrapped density is within 3% of flat, while the same Gaussian on a line keeps only 68% of its mass inside one turn. Computed.*

At σ = π, torsional diffusion's largest noise <!-- L47 -->, the density's peak is 1.03 times its trough. The payoff of the right coordinates was 20 sampling steps where the Euclidean GeoDiff used 5,000. <!-- L48 --> The same idea covers other compact spaces. RFdiffusion represents each protein residue by a position and an orientation, and noises the orientations by Brownian motion on rotations <!-- L51 -->; DiffDock diffuses a drug's pose in its protein pocket over 3 translations, 3 rotations and its torsion angles. <!-- L49 --> Atom types, being categories, are the remaining misfit; EDM's one-hot trick works, and denoising categories directly comes later in this series.

## How do you make 3-D objects without 3-D data?

No billion-object 3-D dataset exists to train on. DreamFusion's answer was to keep a 2-D text-to-image model frozen and optimize a 3-D object until its renders look likely to it. <!-- L30 --> The object is a **NeRF**, a network mapping a 3-D point and a viewing direction to colour and density, which can be rendered from any camera. Each step renders it from a random camera, adds noise, asks the frozen model to predict that noise, and moves the NeRF's parameters along the predicted noise minus the added noise, skipping the denoiser's own gradient: **score distillation sampling** (SDS). <!-- L31 --> Figure 8 shows the loop.

![Score distillation loop: NeRF parameters, render at a random camera, add noise, frozen 2-D denoiser with guidance, residual back](FIG_08)
*Figure 8. The 2-D model never sees the object, only noisy renders of it; the only thing that travels back is a noise residual. After DreamFusion's Section 3.*

SDS is an optimizer, not a sampler, and it shows. Each object takes 15,000 steps, about 1.5 hours on a 4-chip TPUv4 <!-- L35 -->, and DreamFusion needed guidance weight ω = 100, which is w = 101 in Part 8's convention (Controlling Diffusion Models: Guidance, ControlNet, LoRA), against 5 to 30 for images, because smaller weights oversmoothed; its results were oversaturated and differed little between seeds. <!-- L32 --> <!-- L33 --> ProlificDreamer showed that SDS fits a single point where sampling fits a distribution <!-- L36 -->, and that its failures appear even when the renderer is replaced by the identity, so that the "object" is a plain 2-D image. <!-- L37 --> The lab repeats that identity test on crescent world with the exact denoiser, 256 runs per weight (Figure 9).

![SDS on crescent world: contrast and spread of 256 runs per guidance weight against ancestral samples; SDS collapses and saturates](FIG_09)
*Figure 9. SDS returns modes, not samples: brightness and pixel detail vanish at every weight, every run agrees from w = 2, and guidance pushes contrast past the brightest real crescent. Measured, 256 runs per weight.*

Every SDS run converges. At w = 1 a run ends a median 0.02 from its nearest neighbour, against 0.96 for ancestral samples, and the runs settle on faint (53%) or strong (36%) crescents or stall between the two (11%). Runs below the midpoint average contrast 0.66 and runs above it 0.85, both pulled toward the middle from the real 0.50 and 1.00. Every run has the same brightness (spread 0.012 against the data's 0.31) and no pixel detail left (0.0005 against 0.10): an oversmoothed average. From w = 2 every run returns the same strong crescent. By w = 7.5, 82% of runs exceed the brightest real crescent, and at w = 101 the contrast is 2.35, more than twice a real one. Ancestral sampling at the same weights keeps the brightness spread and the detail. It saturates too, to 1.53 at w = 101, so guidance does part of the damage and SDS the rest.

A 2-D prior also does not know which side of the object it is looking at. Optimized view by view, the prompt's subject gets regenerated on several sides, as in a horse with a face at both ends: the **multi-face Janus problem**, after the two-faced Roman god (Figure 10). <!-- L38 -->

![MVDream's Figure 1: a generated horse with two faces across four views, and fried chicken that turns into waffles across views](FIG_10)
*Figure 10. Left, the multi-face Janus problem; right, content drift between views. Reproduced unchanged from Shi et al., "MVDream: Multi-view Diffusion for 3D Generation" (ICLR 2024), Figure 1, [arXiv:2308.16512](https://arxiv.org/abs/2308.16512), licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).*

DreamFusion's patch appends "front view", "side view" or "back view" to the prompt according to the camera angle. <!-- L34 --> MVDream's fix is video's fix: a multi-view diffusion model, trained on rendered 3-D objects, that stretches the image model's self-attention across views and adds camera embeddings, so all the views are generated together. <!-- L39 --> ProlificDreamer's variational score distillation optimizes a distribution of objects rather than one, and works at ordinary guidance weights. <!-- L37 -->

## Why is forecasting inpainting along time?

A multivariate **time series** is a grid of K features by L time steps, so its diffusion looks like an image's; CSDI's denoiser alternates a transformer across time with one across features, the same factorization video uses. <!-- L58 --> What changes is that part of the grid is given. **Forecasting** generates the future from the past; **imputation** fills missing entries. Both are inpainting along time, and Part 8's lesson applies: pushing the known values into the noisy input, **replacement**, is not the same as conditioning on them. VDM found replacement gave new frames that looked fine alone but did not continue the given ones, because the denoiser only ever sees a noisy copy of the evidence <!-- L06 -->; extending clips by replacement scored FVD 451.45 against 136.22 with the reconstruction guidance it proposed. <!-- L07 --> The lab forecasts crescent clips from their first frames (Figure 11).

![Coherent forecasts from 1, 2 or 3 observed frames: replacement 17%, 63%, 96% against exact conditioning 99% at every count](FIG_11)
*Figure 11. Replacement lets the model's own guesses outvote the evidence when little is observed; conditioning on the frames does not. Measured, 4,096 clips per setting.*

From one observed frame, replacement continued 17% of clips coherently, against 99.3% for exact conditioning, and brightness was the first thing lost: only 37% of forecasts kept it. From two frames replacement reached 63%, from three 96%. The less you observe, the more the noisy guesses for the missing frames outvote the evidence. CSDI trains the conditional model directly, by hiding some observed values and learning to fill them in <!-- L57 -->, and beat imputation with an unconditional model, CRPS 0.238 against 0.360 on a healthcare dataset with 10% of values missing. <!-- L59 --> <!-- L60 --> **CRPS**, the continuous ranked probability score, measures how well a predicted distribution matches the observed value; lower is better. <!-- L61 --> Two other designs avoid the problem differently. TimeGrad generates one time step at a time, each conditioned on a recurrent summary of the past <!-- L62 -->, and TSDiff keeps an unconditional model and adds a guidance term from the observations while sampling, which proved competitive with conditional forecasters. <!-- L63 -->

## The math

| Symbol | Meaning |
|---|---|
| $x_0$, $x_t$, $\epsilon$ | clean array, noisy array, standard Gaussian draw (Part 1) |
| $\rho$ | correlation between two frames' starting noises |
| $D$ | the denoiser; $R$ a rotation of 3-D space |
| $\sigma$ | noise level; on a circle, the spread before wrapping |

The forward step is elementwise, so it is the same for any array shape:

$$
x_t = \sqrt{\bar\alpha}\, x_0 + \sqrt{1-\bar\alpha}\, \epsilon \tag{1}
$$

With √ᾱ = 0.8 it gave the worked example's 0.43 in every reading. For a deterministic sampler and a symmetric two-valued pixel, two frames agree when their noises share a sign:

$$
P(\text{agree}) = \frac{1}{2} + \frac{\arcsin \rho}{\pi} \tag{2}
$$

Agreement rises from 1/2 at ρ = 0 to 1 at ρ = 1 and falls to 0 at ρ = −1. Correlation sets how often frames match, never how they should differ.

<details>
<summary>Deriving equation (2)</summary>

Write the two noises as projections of one standard 2-D Gaussian vector g onto unit vectors u₁ and u₂ at angle θ = arccos ρ, so that their correlation is u₁ · u₂ = ρ. Their signs differ exactly when the line perpendicular to g passes between u₁ and u₂, and since g's direction is uniform, that happens with probability θ/π. They agree with probability 1 − arccos(ρ)/π, and since arccos ρ = π/2 − arcsin ρ, that is 1/2 + arcsin(ρ)/π.

</details>

For molecules, EDM removes the centre of gravity from each draw of noise for N atoms:

$$
\tilde\epsilon_i = \epsilon_i - \frac{1}{N}\sum_{j=1}^{N}\epsilon_j \tag{3}
$$

For the worked example's eight points, every noise point loses (0.15, −0.0125), and the cloud's centre no longer moves. <!-- L41 --> If the starting noise is invariant to a rotation R and the denoiser is equivariant, D(Rx) = R D(x), then every sampling step commutes with R, so the samples' distribution is invariant too. <!-- L45 --> The lab checks the same property for its crescent denoiser and a quarter turn: the two sides differ by 3 × 10⁻¹⁵.

On a circle, Gaussian noise of spread σ around an angle becomes a sum over every whole number of turns:

$$
p_\sigma(\theta) = \sum_{k=-\infty}^{\infty} \mathcal{N}\!\left(\theta + 2\pi k;\, 0,\, \sigma^2\right) \tag{4}
$$

Each term is a copy of the line Gaussian shifted by k turns; at σ = π the sum's peak is 1.0292 times its trough. <!-- L47 -->

Score distillation, in this series' notation, with guided noise prediction $\hat\epsilon_w = \hat\epsilon_u + w(\hat\epsilon_c - \hat\epsilon_u)$:

$$
\nabla_\theta \mathcal{L}_{\text{SDS}} = \mathbb{E}_{t,\epsilon}\!\left[ w(t)\,\big(\hat\epsilon_w(x_t; t) - \epsilon\big)\, \frac{\partial x}{\partial \theta} \right] \tag{5}
$$

Here $w(t)$ weights the noise levels and $x$ is the render. <!-- L31 --> The update stops where noised-and-denoised copies of $x$ average back to $x$, a peak of the smoothed density rather than a draw from it, which is why every run lands on nearly the same image. <!-- L36 -->

## Implementation

The noise schemes and projections above are a few lines of numpy each:

```python
import numpy as np

rng = np.random.default_rng(0)
T, D = 4, 64                                        # frames per clip, pixels per 8x8 frame

def mixed_noise(rho):                               # PYoCo's mixed prior: one shared draw plus one per frame
    return np.sqrt(rho) * rng.normal(size=(1, D)) + np.sqrt(1 - rho) * rng.normal(size=(T, D))

def warped_noise(turn=1):                           # frame f gets frame 0's noise turned f quarter turns
    z0 = rng.normal(size=(8, 8))
    return np.stack([np.rot90(z0, turn * f).ravel() for f in range(T)])

def zero_centre(eps):                               # EDM: noise for N atoms in 3-D, centre of gravity removed
    return eps - eps.mean(axis=0, keepdims=True)

def wrap(theta, sigma):                             # torsional diffusion's forward step on angles
    return np.mod(theta + sigma * rng.normal(size=np.shape(theta)) + np.pi, 2 * np.pi) - np.pi
```

`np.rot90` only moves pixels, so the warped noise keeps exactly the statistics of fresh noise; a sub-pixel warp that interpolates would lower its variance and correlate neighbouring pixels. The lab's `beyond.py` adds the exact frame and clip denoisers, the replacement forecaster and the SDS loop, and runs everything in this post in under a minute on one core; see [Lab downloads](#lab-downloads).

## Limitations and common mistakes

> [!WARNING]
> **Common mistake: judging a video model frame by frame.** Per-frame metrics cannot see flicker or freezing: Align your Latents' frame-by-frame upsampler matched the video-aware one on FID (19.71 against 19.85) and was far worse on FVD (165.98 against 45.39). <!-- L10 --> Score whole clips, and compare FVDs only within one paper's table.

- **Expecting correlated noise to make an image model animate.** It trades flicker for freezing; in the lab no correlation produced a single coherent clip. Warped noise works only for motions you prescribe, and cleanly only when they are symmetries of the model.
- **Calling replacement conditioning.** It lost 83% of the lab's one-frame forecasts and scored FVD 451.45 against 136.22 in VDM's clip extension. <!-- L07 --> Train a conditional model, or add a guidance term from the observations.
- **Diffusing raw coordinates with neither equivariance nor augmentation.** On QM9 that scored 63.2% stable molecules against EDM's 82.0% <!-- L44 -->; plain networks have since done well without equivariance at larger scale and on other tasks, as in AlphaFold 3 and MCF. <!-- L53 --> <!-- L54 -->
- **Treating SDS as sampling.** Different seeds return nearly the same object, and raising guidance to sharpen it oversaturates it. <!-- L33 -->
- **Reading the toy's sizes as typical.** Crescent world has eight kinds of frame and a motion that is an exact symmetry of the image model. Real motion is not, so real per-frame models fail less cleanly, and warped noise works less well.

## Key takeaways

- The forward process is shape-blind; everything that changes off the image grid lives in the representation, the space the noise lives in, and the denoiser.
- Frames, samples and time steps must be generated together: an image model sampled per frame flickers or freezes, correlating its noise only trades one failure for the other, and temporal layers in a latent space are the standard fix.
- Point sets and molecules need a denoiser that respects their symmetries or data that teaches them; angles and rotations need noise that wraps, and their noise ends uniform.
- With no 3-D data, SDS borrows a 2-D model but returns modes, not samples; with partly observed data, condition the model on the evidence instead of pushing the evidence into its input.

## Try it yourself

These can be answered from the article alone. The full exercise ladder, with the lab's own run as the answer key, is in the lab's README under [Lab downloads](#lab-downloads).

### E1 — Reproduce: the worked example's clip

Read the rows of Part 1's x₀ and of x_t as four frames of a 1×4 strip. Compute the mean absolute change between consecutive frames in each.

**Self-check:** 0.1833 clean and 0.8050 noisy, a ratio of 4.39.

<details><summary>Answer</summary>

Clean: the three frame changes sum to 0.60, 0.80 and 0.80, so the mean over 12 pixel changes is 2.20 / 12 = 0.1833. Noisy: x_t's rows are 0.43, 1.32, 0.03, −1.34; 1.15, −0.45, −0.59, −0.30; 1.19, 0.26, −1.13, −0.67; −0.43, 0.38, 0.19, −1.46, whose changes sum to 4.15, 1.66 and 3.85, so 9.66 / 12 = 0.8050. The noise is independent from frame to frame, so it makes consecutive frames disagree.

</details>

### E3 — Predict: anti-correlated noise

Before computing, predict how often the one-pixel video's two frames agree when their noises have correlation ρ = −0.5.

**Self-check:** 1/3, because arcsin(−0.5) = −π/6.

<details><summary>Answer</summary>

1/2 + arcsin(−0.5)/π = 1/2 − 1/6 = 1/3. Negative correlation makes the frames disagree more often than independent noise does; at ρ = −1 they always disagree, the "motion" that negation, this pixel's symmetry, produces.

</details>

## References

### Lab downloads

- [`README.md`](LAB_01) — the lab's grade, what was executed, provenance, run order, and the E1–E4 exercise ladder.
- [`beyond.py`](LAB_02) — crescent world in motion with exact frame and clip denoisers, the noise schemes, forecasting by replacement and by exact conditioning, score distillation, and the size census, in numpy.
- [`requirements.txt`](LAB_03) — the pinned numpy version.
- [`captures.json`](LAB_04) — the author's run, machine-readable, which every measured figure was drawn from.
- [`expected-output.txt`](LAB_05) — the same run as printed, to compare against your own.
- [`notebook.ipynb`](LAB_06) — the README with a runnable cell under each step and exercise.
- [Complete lab](https://minio.canery.in/media/lab-diffusion-beyond-images.zip) — every file above in one zip.

### Sources

**Survey**

1. Yang, Zhang, Song, Hong, Xu, Zhao, Zhang, Cui & Yang. [Diffusion Models: A Comprehensive Survey of Methods and Applications](https://doi.org/10.1145/3626235). ACM Computing Surveys, 2023.

**Video**

2. Ho, Salimans, Gritsenko, Chan, Norouzi & Fleet. [Video Diffusion Models](https://arxiv.org/abs/2204.03458). NeurIPS 2022.
3. Blattmann, Rombach, Ling, Dockhorn, Kim, Fidler & Kreis. [Align your Latents: High-Resolution Video Synthesis with Latent Diffusion Models](https://doi.org/10.1109/CVPR52729.2023.02161). CVPR 2023.
4. Blattmann et al. [Stable Video Diffusion: Scaling Latent Video Diffusion Models to Large Datasets](https://arxiv.org/abs/2311.15127). Preprint, 2023; its inference configuration is [`configs/inference/svd.yaml`](https://github.com/Stability-AI/generative-models/blob/059d8e9cd9c55aea1ef2ece39abf605efb8b7cc9/configs/inference/svd.yaml).
5. Ge, Nah, Liu, Poon, Tao, Catanzaro, Jacobs, Huang, Liu & Balaji. [Preserve Your Own Correlation: A Noise Prior for Video Diffusion Models](https://doi.org/10.1109/ICCV51070.2023.02096). ICCV 2023.
6. Khachatryan, Movsisyan, Tadevosyan, Henschel, Wang, Navasardyan & Shi. [Text2Video-Zero: Text-to-Image Diffusion Models are Zero-Shot Video Generators](https://doi.org/10.1109/ICCV51070.2023.01462). ICCV 2023.
7. Chang, Tang, Gross & Azevedo. [How I Warped Your Noise: a Temporally-Correlated Noise Prior for Diffusion Models](https://arxiv.org/abs/2504.03072). ICLR 2024.
8. Unterthiner, van Steenkiste, Kurach, Marinier, Michalski & Gelly. [Towards Accurate Generative Models of Video: A New Metric & Challenges](https://arxiv.org/abs/1812.01717) (FVD). Preprint, 2018.

**Audio**

9. Kong, Ping, Huang, Zhao & Catanzaro. [DiffWave: A Versatile Diffusion Model for Audio Synthesis](https://arxiv.org/abs/2009.09761). ICLR 2021.
10. Liu, Chen, Yuan, Mei, Liu, Mandic, Wang & Plumbley. [AudioLDM: Text-to-Audio Generation with Latent Diffusion Models](https://proceedings.mlr.press/v202/liu23f.html). ICML 2023.
11. Evans, Carr, Taylor, Hawley & Pons. [Fast Timing-Conditioned Latent Audio Diffusion](https://proceedings.mlr.press/v235/evans24a.html) (Stable Audio). ICML 2024.

**3-D**

12. Luo & Hu. [Diffusion Probabilistic Models for 3D Point Cloud Generation](https://doi.org/10.1109/CVPR46437.2021.00286). CVPR 2021.
13. Zhou, Du & Wu. [3D Shape Generation and Completion through Point-Voxel Diffusion](https://doi.org/10.1109/ICCV48922.2021.00577). ICCV 2021.
14. Nichol, Jun, Dhariwal, Mishkin & Chen. [Point-E: A System for Generating 3D Point Clouds from Complex Prompts](https://arxiv.org/abs/2212.08751). Preprint, 2022.
15. Poole, Jain, Barron & Mildenhall. [DreamFusion: Text-to-3D using 2D Diffusion](https://arxiv.org/abs/2209.14988). ICLR 2023.
16. Wang, Lu, Wang, Bao, Li, Su & Zhu. [ProlificDreamer: High-Fidelity and Diverse Text-to-3D Generation with Variational Score Distillation](https://arxiv.org/abs/2305.16213). NeurIPS 2023.
17. Shi, Wang, Ye, Long, Li & Yang. [MVDream: Multi-view Diffusion for 3D Generation](https://arxiv.org/abs/2308.16512). ICLR 2024.

**Molecules and proteins**

18. Hoogeboom, Satorras, Vignac & Welling. [Equivariant Diffusion for Molecule Generation in 3D](https://proceedings.mlr.press/v162/hoogeboom22a.html). ICML 2022.
19. Xu, Yu, Song, Shi, Ermon & Tang. [GeoDiff: a Geometric Diffusion Model for Molecular Conformation Generation](https://arxiv.org/abs/2203.02923). ICLR 2022.
20. Jing, Corso, Chang, Barzilay & Jaakkola. [Torsional Diffusion for Molecular Conformer Generation](https://arxiv.org/abs/2206.01729). NeurIPS 2022.
21. De Bortoli, Mathieu, Hutchinson, Thornton, Teh & Doucet. [Riemannian Score-Based Generative Modelling](https://arxiv.org/abs/2202.02763). NeurIPS 2022.
22. Corso, Stärk, Jing, Barzilay & Jaakkola. [DiffDock: Diffusion Steps, Twists, and Turns for Molecular Docking](https://arxiv.org/abs/2210.01776). ICLR 2023.
23. Watson et al. [De novo design of protein structure and function with RFdiffusion](https://doi.org/10.1038/s41586-023-06415-8). Nature, 2023.
24. Wang, Elhag, Jaitly, Susskind & Bautista. [Swallowing the Bitter Pill: Simplified Scalable Conformer Generation](https://proceedings.mlr.press/v235/wang24q.html) (MCF). ICML 2024.
25. Abramson et al. [Accurate structure prediction of biomolecular interactions with AlphaFold 3](https://doi.org/10.1038/s41586-024-07487-w). Nature, 2024.

**Time series**

26. Tashiro, Song, Song & Ermon. [CSDI: Conditional Score-based Diffusion Models for Probabilistic Time Series Imputation](https://arxiv.org/abs/2107.03502). NeurIPS 2021.
27. Rasul, Seward, Schuster & Vollgraf. [Autoregressive Denoising Diffusion Models for Multivariate Probabilistic Time Series Forecasting](https://proceedings.mlr.press/v139/rasul21a.html) (TimeGrad). ICML 2021.
28. Kollovieh, Ansari, Bohlke-Schneider, Zschiegner, Wang & Wang. [Predict, Refine, Synthesize: Self-Guiding Diffusion Models for Probabilistic Time Series Forecasting](https://arxiv.org/abs/2307.11494) (TSDiff). NeurIPS 2023.
