---
social_schema: 2
canonical_url: "https://canery.in/blogs/diffusion-beyond-images"
---

# Social publishing package — diffusion-beyond-images

## LinkedIn post

Run an image diffusion model frame by frame and every frame can be a perfect image while the video is broken. Align your Latents measured it on driving video: upsampling each frame on its own left frame FID unchanged (19.71 against 19.85) and more than tripled FVD (45.39 to 165.98).

The noise step of a diffusion model never sees the shape of its data. What changes off the image grid is the denoiser's job. Measured in a toy whose true distribution is known exactly, and quoted from papers with their setup:

→ Every frame right, the video wrong. Sampled one frame at a time, 99.7% of frames were valid and not one clip in 4,096 moved coherently.
→ Correlated noise freezes, not moves. Sharing noise between frames trades flicker for frozen clips; turning the noise a quarter turn per frame makes it turn, and a joint model gets 99.4%.
→ Sound is one long axis. A second of speech is 16,000 samples; AudioLDM diffuses 10 s in 32,000 numbers.
→ Rotate a molecule: same molecule. On QM9, an equivariant network made 82.0% stable molecules, against 63.2% without equivariance (Hoogeboom et al., ICML 2022).
→ SDS returns modes, not samples. Score distillation, which builds 3-D from 2-D models, returned nearly the same image from every run.
→ Forecasting is inpainting in time. Forcing the known frames into the noisy input continued 17% of clips; conditioning on them, 99.3%.

The toy's sizes are mechanism, not scale; published results keep their model, dataset and protocol.

Part 10 of the Diffusion Models series.

## LinkedIn first comment

What changes when diffusion leaves the image grid, modality by modality, with a numpy lab that runs in about a minute.

Read the full article on Canery: https://canery.in/blogs/diffusion-beyond-images

## Instagram caption

A diffusion model's noise step never sees the shape of its data. Video, audio, 3-D shapes, molecules and time series all diffuse with the same arithmetic as images; what changes is what the denoiser has to see and respect.

Swipe through an image model that animates nothing, the one forward step read four ways, noise that freezes instead of moves, sound as one long axis, molecules that must look the same in every orientation, score distillation returning one image per prompt, and forecasting as inpainting in time.

Every measured number comes from a lab you can run on a laptop in about a minute; published results are quoted with their setup.

Link in bio.

#generativeai #machinelearning #deeplearning #diffusionmodels #videogeneration #audiogeneration #3dgeneration

## Shared feed order

1. `assets/social/feed-01-every-frame-right-video-wrong.png` — an image model sampled frame by frame makes valid frames and no coherent clip; a joint model makes coherent clips
2. `assets/social/feed-02-the-noise-step-is-shape-blind.png` — the worked example: one forward step on part 1's numbers, read as an image, a waveform, a clip and a point set
3. `assets/social/feed-03-correlated-noise-freezes.png` — correlating the per-frame noise trades flicker for freezing; warped noise and the joint model move
4. `assets/social/feed-04-sound-is-one-long-axis.png` — one 10-second clip as waveform, mel spectrogram and latent, to scale, with DiffWave's reach
5. `assets/social/feed-05-rotate-a-molecule.png` — EDM's QM9 comparison of no equivariance, rotation augmentation and an equivariant network
6. `assets/social/feed-06-sds-returns-modes.png` — score distillation on crescent world returns the same image from every run, and saturates at high guidance
7. `assets/social/feed-07-forecasting-is-inpainting.png` — forecasting clips by replacement against exact conditioning, from 1, 2 and 3 observed frames
8. `assets/social/feed-08-read-the-article.png` — the five things that change off the grid, and the call to read the article

## Instagram Story

Not produced: this part ships feed cards only, as Parts 8 and 9 did at the owner's request (2026-10-19), so there are no Story frames, Story CTA or link sticker to post.

### Story order

None.

## Asset metadata

### feed-01-every-frame-right-video-wrong

- File: `assets/social/feed-01-every-frame-right-video-wrong.png`
- Title: Every frame right, the video wrong
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: an image model sampled one frame at a time makes valid frames and no coherent clip, while a joint model makes coherent clips
- Technical source: Why does a frame-by-frame image model break video? (Crescent world in motion); Figure 3; lab video stage
- Visual structure: lockup and counter; serif title; deck; two rows of four 8×8 frame tiles, the top row from the joint model turning a quarter turn per frame, the bottom row sampled frame by frame and jumping; each row's coherent-clip share in large type at right; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 08 · Every frame right, the video wrong. · Sampled frame by frame, an image diffusion model draws valid crescents in 99.7% of frames, and not one coherent clip in 4,096. · ONE DENOISER FOR THE WHOLE CLIP · COHERENT CLIPS · 99.4% · ONE FRAME AT A TIME, FRESH NOISE · COHERENT CLIPS · 0.0% · The noise step never sees the data's shape. What changes off the image grid is what the denoiser must see across. · DIFFUSION BEYOND IMAGES · CANERY.IN
- Alt text: Two rows of four crescent frames: a joint model's clip turning smoothly, 99.4% coherent, and a frame-by-frame clip, 0.0%
- Long description: Cover card. Crescent world in motion: each 8×8 frame shows one of four crescents, and real four-frame clips turn a quarter turn per frame with one contrast and one brightness. The top row is a clip from the exact joint (video) denoiser, which turns smoothly; 99.4% of its 4,096 clips are coherent. The bottom row is a clip from the exact per-frame (image) denoiser with fresh noise per frame, whose frames jump between orientations and brightnesses; 99.7% of its frames are valid crescents, yet 0.0% of its clips are coherent. The takeaway: the noise step never sees the data's shape, and what changes off the image grid is what the denoiser must see across.
- Keywords: video diffusion, temporal coherence, flicker, image diffusion model, joint denoiser, crescent world
- Canonical URL: https://canery.in/blogs/diffusion-beyond-images

### feed-02-the-noise-step-is-shape-blind

- File: `assets/social/feed-02-the-noise-step-is-shape-blind.png`
- Title: The noise step is shape-blind
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: one forward step on part 1's sixteen numbers is the same arithmetic whatever they mean; the denoiser's job differs by reading
- Technical source: Worked example; Figure 2; lab worked stage
- Visual structure: lockup and counter; serif title; deck; a white box with the top-left forward step in large mono; four rows, each a reading in serif and what its denoiser must do in mono; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 08 · The noise step is shape-blind. · Part 1's 16 numbers, noised once. The same arithmetic, whether they are an image, a waveform, a clip or a set of points. · ONE FORWARD STEP, THE TOP-LEFT VALUE · 0.8 × 0.95 + 0.6 × (−0.55) = 0.43 · an image · respect its 2-D neighbours · a waveform · reach far: 1 s is 16,000 samples · a clip · frames differ 0.183 clean, 0.805 noised · 8 points · ignore order (40,320 listings) and position · Same sixteen multiply-adds, four different jobs for the denoiser. · DIFFUSION BEYOND IMAGES · CANERY.IN
- Alt text: The forward step 0.8 × 0.95 + 0.6 × (−0.55) = 0.43, above four readings of the same numbers and what each denoiser must do
- Long description: The worked example. Part 1's 4×4 patch is noised once at signal scale 0.8 and noise scale 0.6; its top-left value becomes 0.8 × 0.95 + 0.6 × (−0.55) = 0.43, and the same sixteen multiply-adds apply whatever the numbers mean. Read as an image, the denoiser must respect 2-D neighbours; as a waveform, reach far along one axis (one second at 16 kHz is 16,000 samples); as a clip of four 1×4 frames, see across frames, which differ by 0.183 per pixel clean and 0.805 after noising; as eight points, ignore their order (40,320 listings of one set) and their position.
- Keywords: forward process, diffusion noise step, worked example, waveform, video frames, point cloud, permutation
- Canonical URL: https://canery.in/blogs/diffusion-beyond-images

### feed-03-correlated-noise-freezes

- File: `assets/social/feed-03-correlated-noise-freezes.png`
- Title: Correlated noise freezes, not moves
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: correlating a per-frame model's noise trades brightness flicker for frames that stop turning; warped noise and a joint model move
- Technical source: Why does a frame-by-frame image model break video?; Figure 3; lab video stage
- Visual structure: lockup and counter; serif title; deck; legend; five rows of paired horizontal bars (brightness flicker in orange, no turn in dark) for independent, mixed and shared noise; a rule; two rows giving coherent-clip shares for warped noise and the joint model; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 08 · Correlated noise freezes, not moves. · Share noise between frames and the flicker stops, but so does the motion. Turning the noise a quarter turn per frame makes it turn. · SHARE OF FRAME CHANGES · brightness flicker · no turn · independent noise · 81.6% · 24.7% · mixed noise, ρ = 0.5 · 73.4% · 44.5% · mixed noise, ρ = 0.9 · 44.9% · 74.1% · mixed noise, ρ = 0.99 · 1.4% · 91.3% · shared noise · 0.0% · 100.0% · warped noise · coherent clips 99.6% · joint model · coherent clips 99.4% · No correlation gave a coherent clip; warped noise gave 99.6%, the joint model 99.4%. A video model has to see the other frames. · DIFFUSION BEYOND IMAGES · CANERY.IN
- Alt text: Paired bars: as noise correlation rises, brightness flicker falls from 81.6% to 0% while frames that stop turning rise to 100%
- Long description: Measured on crescent world in motion with 4,096 clips per scheme. With an exact per-frame image denoiser, independent noise makes 81.6% of frame changes flicker in brightness and 24.7% show no turn; PYoCo-style mixed noise at correlation 0.5, 0.9 and 0.99 gives flicker 73.4%, 44.9% and 1.4% and no-turn shares 44.5%, 74.1% and 91.3%; shared noise gives 0.0% flicker and 100.0% no turn. No correlation produced a coherent clip. Warping frame 0's noise a quarter turn per frame gives 99.6% coherent clips, because a quarter turn is a symmetry of the image model, and the exact joint video denoiser gives 99.4%.
- Keywords: noise prior, PYoCo, correlated noise, warped noise, Text2Video-Zero, video diffusion, flicker
- Canonical URL: https://canery.in/blogs/diffusion-beyond-images

### feed-04-sound-is-one-long-axis

- File: `assets/social/feed-04-sound-is-one-long-axis.png`
- Title: Sound is one long axis
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: audio is one long axis, and most audio diffusion models shorten it before diffusing
- Technical source: What changes when the signal is sound?; Figure 5; lab census stage (DiffWave, AudioLDM and Stable Audio configurations)
- Visual structure: lockup and counter; serif title; deck; three horizontal bars to scale for one 10-second clip (waveform, mel spectrogram, AudioLDM latent) with DiffWave's reach marked under the waveform; a note on phase; takeaway; footer
- Visible-text transcript: Canery.in · 04 / 08 · Sound is one long axis. · One second of speech at 16 kHz is 16,000 samples. Most audio models shorten the axis before they diffuse. · ONE 10-SECOND CLIP AT 16 KHZ, LENGTHS TO SCALE · waveform · 160,000 · mel spectrogram · 64,000 · AudioLDM latent · 32,000 · DiffWave's reach: 6,139 samples, 0.38 s · the spectrogram drops phase; a vocoder puts a waveform back · AudioLDM diffuses 10 s in 32,000 numbers; Stable Audio's latent holds 95.1 s of stereo in 32 times fewer numbers than the audio. · DIFFUSION BEYOND IMAGES · CANERY.IN
- Alt text: Bars to scale for one 10-second clip: waveform 160,000, mel spectrogram 64,000, AudioLDM latent 32,000, with a 0.38 s reach
- Long description: One 10-second clip at 16 kHz in AudioLDM's pipeline, lengths to scale: 160,000 waveform samples, 64,000 mel-spectrogram values (1,000 frames × 64 bands at a hop of 160) and 32,000 latent values (compression 4 in time and frequency, 8 channels). DiffWave's 30 dilated layers reach 6,139 samples, 0.38 s, marked under the waveform. A mel spectrogram keeps magnitudes and drops phase, so a vocoder must turn it back into a waveform. Stable Audio's autoencoder holds 95.1 s of 44.1 kHz stereo in 32 times fewer numbers than the audio.
- Keywords: audio diffusion, DiffWave, AudioLDM, Stable Audio, mel spectrogram, vocoder, latent diffusion
- Canonical URL: https://canery.in/blogs/diffusion-beyond-images

### feed-05-rotate-a-molecule

- File: `assets/social/feed-05-rotate-a-molecule.png`
- Title: Rotate a molecule: same molecule
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: a molecule denoiser has to treat every orientation alike; building that in beat learning it from rotated copies on QM9
- Technical source: When order and orientation don't matter (Molecules add rotation and translation); Figure 6; ledger L44, L53, L54
- Visual structure: lockup and counter; serif title; deck; four labelled horizontal bars of quoted molecule stability; source line; takeaway; footer
- Visible-text transcript: Canery.in · 05 / 08 · Rotate a molecule: same molecule. · A denoiser for 3-D molecules has to treat every orientation alike. EDM tested three ways on QM9, with the same network and data. · QM9 · STABLE MOLECULES, SAME NETWORK AND DATA · QUOTED · no equivariance · 63.2% · random rotations in training · 71.6% · equivariant network · 82.0% · training data · 95.2% · Hoogeboom et al., ICML 2022, Table 1: 10,000 molecules per model · Equivariance closed 59% of the gap to the data. At larger scale and on other tasks, AlphaFold 3 and MCF did well without it. · DIFFUSION BEYOND IMAGES · CANERY.IN
- Alt text: Bars of QM9 stable molecules: no equivariance 63.2%, rotation augmentation 71.6%, equivariant network 82.0%, data 95.2%
- Long description: Quoted from Hoogeboom et al., Equivariant Diffusion for Molecule Generation in 3D (ICML 2022), Table 1: on QM9, with the same 9-layer, 256-feature network, 10,000 generated molecules per model and three runs, the share of stable molecules (every atom with the right number of bonds) was 63.2% without equivariance, 71.6% with random rotations in training, 82.0% with an equivariant network, against 95.2% for the training data. Equivariance closed 59% of the gap between no equivariance and the data. At larger scale and on other tasks, AlphaFold 3 and MCF did well with networks that have no equivariance built in.
- Keywords: equivariant diffusion, EDM, EGNN, QM9, molecule generation, rotation invariance, AlphaFold 3
- Canonical URL: https://canery.in/blogs/diffusion-beyond-images

### feed-06-sds-returns-modes

- File: `assets/social/feed-06-sds-returns-modes.png`
- Title: SDS returns modes, not samples
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: score distillation optimizes one object, so every run lands on the same image, losing variety, and guidance saturates it
- Technical source: How do you make 3-D objects without 3-D data?; Figure 9; lab sds stage
- Visual structure: lockup and counter; serif title; deck; two rows of four 8×8 tiles, four SDS runs at w = 1 (nearly identical) and four ancestral samples at w = 1 (varied), each with its brightness spread at right; a line on contrast at w = 101; takeaway; footer
- Visible-text transcript: Canery.in · 06 / 08 · SDS returns modes, not samples. · Score distillation builds 3-D objects by optimizing their renders against a 2-D model. On crescent world every run lands alike. · four SDS runs, w = 1 · BRIGHTNESS SPREAD · 0.012 · four ancestral samples, w = 1 · BRIGHTNESS SPREAD · 0.30 · at w = 101: contrast 2.35; real strong crescents 1.00 · Brightness spread 0.012 against 0.30 for ancestral samples; at DreamFusion's w = 101, a contrast of 2.35, more than twice a real one. · DIFFUSION BEYOND IMAGES · CANERY.IN
- Alt text: Four near-identical SDS crescents, brightness spread 0.012, above four varied ancestral samples with spread 0.30
- Long description: Measured on crescent world with the exact denoiser and an identity renderer, 256 score-distillation runs per guidance weight, 3,000 steps each. At w = 1, four SDS runs come out nearly identical, with a brightness spread of 0.012 across runs, while four ancestral (DDIM) samples at the same weight vary, with a spread of 0.30. At DreamFusion's guidance (ω = 100, w = 101 in the series' convention) the SDS contrast is 2.35, more than twice a real strong crescent's 1.00.
- Keywords: score distillation sampling, SDS, DreamFusion, text-to-3D, mode seeking, classifier-free guidance, oversaturation
- Canonical URL: https://canery.in/blogs/diffusion-beyond-images

### feed-07-forecasting-is-inpainting

- File: `assets/social/feed-07-forecasting-is-inpainting.png`
- Title: Forecasting is inpainting in time
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: forcing known frames into the noisy input is not conditioning on them; replacement fails most when little is observed
- Technical source: Why is forecasting inpainting along time?; Figure 11; lab forecast stage
- Visual structure: lockup and counter; serif title; deck; grouped bar chart of coherent forecasts from 1, 2 and 3 observed frames, replacement in orange and exact conditioning in dark; legend; takeaway; footer
- Visible-text transcript: Canery.in · 07 / 08 · Forecasting is inpainting in time. · Predict the rest of a clip from its first frames. Forcing the known frames into the noisy input is not the same as conditioning on them. · 0% · 50% · 100% · 17% · 99% · 1 observed · 63% · 99% · 2 observed · 96% · 99% · 3 observed · replacement · exact conditioning · From one frame, replacement continued 17% of clips coherently; exact conditioning 99.3%. Brightness went first: kept in only 37%. · DIFFUSION BEYOND IMAGES · CANERY.IN
- Alt text: Grouped bars of coherent forecasts from 1, 2, 3 observed frames: replacement 17%, 63%, 96%; exact conditioning 99% each
- Long description: Measured on crescent world in motion, 4,096 real clips per setting: predicting the rest of a four-frame clip from its first frames with the exact joint model. Replacement, which re-noises the true frames and forces them into the noisy input at every step, continued 17% of clips coherently from one observed frame, 63% from two and 96% from three; exact conditioning continued 99% in every case (99.3% from one frame). With one observed frame, brightness was lost first: only 37% of replacement forecasts kept it.
- Keywords: time series forecasting, imputation, replacement sampling, conditional diffusion, CSDI, video prediction, inpainting
- Canonical URL: https://canery.in/blogs/diffusion-beyond-images

### feed-08-read-the-article

- File: `assets/social/feed-08-read-the-article.png`
- Title: What changes off the grid
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: the five things that change when diffusion leaves the image grid, and the call to read the article
- Technical source: Insights; The problem; Key takeaways
- Visual structure: lockup and counter; serif title; deck; a white panel listing five headings in serif, each with a one-line mono explanation; takeaway; call to action in orange in place of the footer
- Visible-text transcript: Canery.in · 08 / 08 · What changes off the grid. · Video, audio, 3-D, molecules and time series, through one recipe whose noise step never changes. · A new axis · frames, samples and steps generated together · Symmetry · point order, rotation and translation · Circles · angles and rotations: noise that wraps ends uniform · Scale · latents shrink audio 32× and video 48× (Stable Audio, SVD) · What is given · condition on it; don't force it into the noisy input · Pick the representation and the symmetries before the network. · READ IT AT CANERY.IN/BLOGS/DIFFUSION-BEYOND-IMAGES
- Alt text: Five things that change off the image grid: a new axis, symmetry, circles, scale and what is given, with the article link
- Long description: Call-to-action card. Five headings summarise what changes when diffusion leaves the 2-D image grid: a new axis (frames, samples and time steps generated together), symmetry (point order, rotation and translation), circles (angles and rotations, where noise wraps and ends uniform), scale (latents shrink audio 32 times in Stable Audio and video 48 times in Stable Video Diffusion) and what is given (condition on it rather than forcing it into the noisy input). Takeaway: pick the representation and the symmetries before the network. Link: canery.in/blogs/diffusion-beyond-images.
- Keywords: diffusion models, video, audio, 3-D, molecules, time series, equivariance
- Canonical URL: https://canery.in/blogs/diffusion-beyond-images
