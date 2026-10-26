---
social_schema: 2
canonical_url: "https://canery.in/blogs/controlling-diffusion-models"
---

# Social publishing package — controlling-diffusion-models

## LinkedIn post

Stable Diffusion samples at a guidance weight of 7.5 by default. Raise it and the prompt is obeyed more closely while colours saturate. Every way of making a diffusion model obey something other than its prompt, in the sampler, through new inputs or in the weights, pays for it in something you can measure.

Measured in a toy whose ideal denoisers have closed forms, at 8×8 pixels, with every network trained on a laptop CPU:

→ Guidance asks for more than exists. At σ = 80, the guided target at w = 3 is 15.85, more than twice the strongest real crescent, 7.2.
→ Guidance deletes the less typical look. With exact denoisers, w = 3 left 9.5% of samples faint where the data has 50%, and sample distance grew from 0.024 to 0.225.
→ A weaker model is a better guide. Autoguidance at w = 2 cut a trained model's blends from 7.2–9.8% to 4.0–5.4% and kept 50–51% faint; CFG at w = 3 kept 13–17%.
→ ControlNet starts by changing nothing. With zero-initialised connectors the first output was the frozen model's, to the last bit; Gaussian connectors started 0.20–0.26 from real images, against 0.05.
→ Five photos teach the photos. LoRA and full fine-tuning learned the subject, turned every plain "crescent 0" into it unless prior preservation was on, and copied the five photos' narrow brightness spread.
→ Editing trades a ghost for detail. SDEdit keeps τ/√(τ² + σ₀²) of both the old crescent and the fine detail; DDIM inversion kept all the detail with 0.1% of the old crescent left.

A toy with few relevant directions exaggerates guidance's overshoot, so read its sizes as mechanism, not scale; published results are quoted with their model and dataset.

Part 8 of the Diffusion Models series.

## LinkedIn first comment

Classifier-free guidance and its fixes, ControlNet, LoRA and DreamBooth, inpainting and editing, each measured in a toy world with exact denoisers, with a lab you can run on a laptop CPU.

Read the full article on Canery: https://canery.in/blogs/controlling-diffusion-models

## Instagram caption

Every way of making a diffusion model obey something other than its prompt has a price you can measure.

Swipe through what guidance asks for, the look it deletes, the weaker model that guides better, why ControlNet starts at zero, what five photos teach a fine-tuned model, and the trade SDEdit cannot escape.

Every measured number comes from a lab you can run on a laptop CPU, in a toy world whose ideal denoisers have closed forms; published results are quoted with their setup.

Link in bio.

#diffusionmodels #machinelearning #deeplearning #generativeai #stablediffusion #controlnet #lora #computervision

## Shared feed order

1. `assets/social/feed-01-every-control-has-a-price.png` — four starting noises that end faint unguided, sampled at w = 1, 2, 3 and 5
2. `assets/social/feed-02-guidance-asks-for-more.png` — the worked example's guided target, 15.85 against a strongest real crescent of 7.2
3. `assets/social/feed-03-guidance-deletes-the-faint-look.png` — faint and over-saturated shares at seven guidance weights, exact model
4. `assets/social/feed-04-a-weaker-model-is-a-better-guide.png` — no guidance, CFG at w = 3 and autoguidance at w = 2 on the lab's trained model
5. `assets/social/feed-05-controlnet-starts-at-zero.png` — sample distance while training a ControlNet branch, zero against Gaussian connectors
6. `assets/social/feed-06-five-photos-teach-the-photos.png` — five personalisation recipes: subject share, drift and the subject's brightness spread
7. `assets/social/feed-07-editing-trades-a-ghost-for-detail.png` — SDEdit's ghost and kept detail against the closed form, and DDIM inversion
8. `assets/social/feed-08-read-the-article.png` — the five control families, what each costs, and the CTA

## Instagram Story

Not produced: the owner asked for feed cards only for this part (2026-10-19), so there are no Story frames, Story CTA or link sticker to post.

### Story order

None.

## Asset metadata

### feed-01-every-control-has-a-price

- File: `assets/social/feed-01-every-control-has-a-price.png`
- Title: Every control has a price
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: Guidance turns faint crescents strong: four starting noises that end faint without guidance end strong as the weight grows
- Technical source: article section "What does classifier-free guidance do to the distribution?", Figure 3, lab captures (samples → 1.0, 2.0, 3.0, 5.0; exact → weights → 3.0 → faint; exact → data → faint)
- Visual structure: Lockup and counter; serif headline; deck; a four-by-four grid of 8×8 greyscale samples, rows labelled w = 1, 2, 3 and 5, columns the same four starting noises, each tile's crescent contrast under it and faint tiles outlined in blue; a legend for the outline; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 08 · Every control · has a price. · Guidance, ControlNet, LoRA, inpainting and editing each steer a · diffusion model, and each pays in something you can measure. · FOUR NOISES THAT END FAINT UNGUIDED · EXACT MODEL · w = 1 · 0.53 · 0.56 · 0.39 · 0.49 · w = 2 · 0.92 · 0.99 · 0.50 · 0.95 · w = 3 · 0.98 · 1.03 · 0.61 · 1.01 · w = 5 · 1.04 · 1.08 · 1.01 · 1.07 · faint: contrast below 0.75 · With exact denoisers, guidance at w = 3 left 9.5% of samples faint, · where the data has 50%. It deletes the less typical look. · CONTROLLING DIFFUSION MODELS · CANERY.IN
- Alt text: Four crescent samples at guidance weights 1, 2, 3 and 5: all faint unguided, one still faint at w = 3, all strong at w = 5
- Long description: Four starting noises that end on a faint crescent (contrast about 0.5) without guidance are sampled again with crescent world's exact class-conditional and unconditional denoisers at guidance weights 2, 3 and 5. Their contrasts move from 0.53, 0.56, 0.39 and 0.49 at w = 1 to 0.92, 0.99, 0.50 and 0.95 at w = 2, 0.98, 1.03, 0.61 and 1.01 at w = 3, and 1.04, 1.08, 1.01 and 1.07 at w = 5. Over 4,096 samples, guidance at w = 3 leaves 9.5% of samples faint where the data has 50%: it deletes the class's less typical look rather than refining it.
- Keywords: classifier-free guidance, guidance weight, mode coverage, sample diversity, exact denoiser, diffusion model
- Canonical URL: https://canery.in/blogs/controlling-diffusion-models

### feed-02-guidance-asks-for-more

- File: `assets/social/feed-02-guidance-asks-for-more.png`
- Title: Guidance asks for more than exists
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: At high noise the guided denoiser asks for a crescent more than twice as strong as any real one; the overshoot fades, the decision it moved stays
- Technical source: article section "Worked example" (Guidance on one number), lab captures (worked → D_uncond, D_cond, D_guided, step_uncond, step_cond, step_guided)
- Visual structure: Lockup and counter; serif headline; deck; a ledger of five rows: the unconditional denoiser 0.203, the conditional 5.419 and the guided target at w = 3, 15.849, in orange; below a rule, the strongest real crescent, 7.2, and one DDIM step's three results; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 08 · Guidance asks for · more than exists. · One number: how much of the requested crescent an image shows. Its · real crescents sit at 3.6 (faint) and 7.2 (strong). · ONE NUMBER AT σ = 80, X = 40 · EXACT DENOISERS · unconditional denoiser D_u · 0.203 · conditional denoiser D_c · 5.419 · guided, w = 3: D_u + 3 (D_c − D_u) · 15.849 · the strongest real crescent · 7.2 · one DDIM step to σ = 17.53: unguided · conditional · guided · 8.92 · 13.00 · 21.14 · The guided target is more than twice the strongest real crescent. · The overshoot fades; the decision it moved stays. · CONTROLLING DIFFUSION MODELS · CANERY.IN
- Alt text: Worked numbers at σ = 80, x = 40: unconditional denoiser 0.203, conditional 5.419, guided at w = 3 15.849, against a real maximum of 7.2
- Long description: In a one-number version of crescent world, the requested class's real crescents sit at 3.6 (faint) and 7.2 (strong) and the other class's at −3.6 and −7.2, each with a spread of 0.443. At σ = 80 and x = 40 the exact unconditional denoiser returns 0.203 and the conditional one 5.419, and guidance at w = 3, D_u + 3(D_c − D_u), asks for 15.849, more than twice the strongest real crescent. One DDIM step to σ = 17.53 takes the sample to 8.92 unconditionally, 13.00 conditionally and 21.14 guided. The overshoot does not survive to the end of sampling; the faint-or-strong decision that guidance moved does.
- Keywords: classifier-free guidance, denoiser, DDIM, worked example, guidance weight, overshoot
- Canonical URL: https://canery.in/blogs/controlling-diffusion-models

### feed-03-guidance-deletes-the-faint-look

- File: `assets/social/feed-03-guidance-deletes-the-faint-look.png`
- Title: Guidance deletes the faint look
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: With exact denoisers, raising the guidance weight drains the faint half of a class and pushes a growing share past the strongest real look
- Technical source: article section "What does classifier-free guidance do to the distribution?", Figure 4, lab captures (exact → weights, exact → data)
- Visual structure: Lockup and counter; serif headline; deck; horizontal bars of the faint share for w = 1, 1.5, 2, 3, 4, 5 and 7.5 with a dashed line at the data's 50%, and a right-hand column of over-saturated shares in orange; a note on the sample size and the over-saturation threshold; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 08 · Guidance deletes · the faint look. · Samples of one class from the exact model, whose denoisers have · closed forms, where half of all real crescents are faint. · FAINT SHARE · OVER-SATURATED · w = 1 · 52.9% · 0.00% · w = 1.5 · 36.4% · 0.05% · w = 2 · 24.1% · 0.07% · w = 3 · 9.5% · 0.37% · w = 4 · 3.4% · 0.85% · w = 5 · 1.3% · 1.76% · w = 7.5 · 0.1% · 7.20% · THE DATA: 50% · 4,096 SAMPLES PER WEIGHT · OVER-SATURATED: CONTRAST ABOVE 1.185 · Sample distance grew from 0.024 unguided to 0.225 at w = 3: · with an ideal denoiser, guidance is strictly harmful. · CONTROLLING DIFFUSION MODELS · CANERY.IN
- Alt text: Faint share falling from 52.9% unguided to 0.1% at w = 7.5 while over-saturated samples rise from 0% to 7.2%, exact model
- Long description: 4,096 samples of one class from crescent world's exact denoisers at each of seven guidance weights. The share of faint crescents, half of the real data, is 52.9% unguided, 36.4% at w = 1.5, 24.1% at 2, 9.5% at 3, 3.4% at 4, 1.3% at 5 and 0.1% at 7.5. The share over-saturated, with a contrast above 1.185, rises from 0.00% unguided to 0.37% at w = 3, 1.76% at 5 and 7.20% at 7.5. Sample distance to real images grows from 0.024 to 0.225 at w = 3: with an ideal denoiser, guidance only costs; a network's errors are what give it something to fix.
- Keywords: classifier-free guidance, mode coverage, over-saturation, faint share, exact denoiser, sample diversity
- Canonical URL: https://canery.in/blogs/controlling-diffusion-models

### feed-04-a-weaker-model-is-a-better-guide

- File: `assets/social/feed-04-a-weaker-model-is-a-better-guide.png`
- Title: A weaker model is a better guide
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Autoguidance removes a trained model's blends without deleting the faint look; classifier-free guidance pays for the same cleanup in coverage
- Technical source: article section "Which fixes keep guidance's benefit?", Figure 7, lab captures (networks → seeds → model → cfg w=1, cfg w=3, auto w=2; exact → data)
- Visual structure: Lockup and counter; serif headline; deck; a table with columns faint, blends and distance and rows no guidance, CFG at w = 3, autoguidance at w = 2 in orange and, below a rule, the data; notes on the model, seeds and metrics; takeaway; footer
- Visible-text transcript: Canery.in · 04 / 08 · A weaker model · is a better guide. · Autoguidance extrapolates away from a copy of the model trained a · quarter as long, not away from its unconditional mode. · FAINT · BLENDS · DISTANCE · no guidance · 52% · 7.2–9.8% · 0.027–0.030 · CFG, w = 3 · 13–17% · 4.0–4.2% · 0.192–0.206 · autoguidance, w = 2 · 50–51% · 4.0–5.4% · 0.019–0.024 · the data · 50% · 0.12% · 0.014 · THE LAB'S TRAINED MODEL · TWO SEEDS · 4,096 SAMPLES EACH · BLENDS: HALF-FAINT CRESCENTS NO REAL IMAGE HAS · DISTANCE: SLICED WASSERSTEIN TO REAL IMAGES; THE DATA ROW: TWO REAL SETS · Autoguidance was the only setting in the lab that improved the · model's sample distance. CFG paid for its cleanup in coverage. · CONTROLLING DIFFUSION MODELS · CANERY.IN
- Alt text: Table for the lab's model: autoguidance at w = 2 keeps 50–51% faint and cuts the blends; CFG at w = 3 keeps 13–17% faint
- Long description: The lab's class-conditional network, trained for 20,000 steps with 10% label dropout, sampled 4,096 times per setting on two seeds. Unguided it keeps 52% of crescents faint but draws 7.2–9.8% blends, half-faint crescents no real image has, at a sample distance of 0.027–0.030 from real images. Classifier-free guidance at w = 3 cuts the blends to 4.0–4.2% but keeps only 13–17% faint and worsens the distance to 0.192–0.206. Autoguidance at w = 2, guided by a copy trained a quarter as long, cuts the blends to 4.0–5.4%, keeps 50–51% faint and improves the distance to 0.019–0.024, the only setting in the lab that improved it. The data has 50% faint and 0.12% blends, and two real sets sit 0.014 apart.
- Keywords: autoguidance, classifier-free guidance, guidance, sample quality, mode coverage, diffusion model
- Canonical URL: https://canery.in/blogs/controlling-diffusion-models

### feed-05-controlnet-starts-at-zero

- File: `assets/social/feed-05-controlnet-starts-at-zero.png`
- Title: ControlNet starts by changing nothing
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Zero-initialised connectors leave the frozen model's output untouched at the first step; Gaussian connectors damage the images before the branch has learned anything
- Technical source: article section "How does ControlNet add a condition without breaking the model?", Figure 9, lab captures (controlnet → zero, gaussian → swd, max_change)
- Visual structure: Lockup and counter; serif headline; deck; a line chart of sample distance against training steps 0 to 3,200 on a stepped axis, Gaussian connectors dashed from 0.23 and zero connectors in orange from the frozen model's 0.05, each the mean of two seeds; a note on the largest output change at step 0; takeaway; footer
- Visible-text transcript: Canery.in · 05 / 08 · ControlNet starts · by changing nothing. · A trainable copy joins the frozen model through layers whose · weights start at zero, so its first output is the frozen model's. · SAMPLE DISTANCE TO REAL IMAGES · MEAN OF TWO SEEDS · 0 · 0.1 · 0.2 · 0.3 · 0 · 25 · 50 · 100 · 200 · 400 · 800 · 1,600 · 3,200 · Gaussian connectors: 0.23 · zero: 0.05, the frozen model's · TRAINING STEP · LARGEST OUTPUT CHANGE AT STEP 0: ZERO 0 · GAUSSIAN UP TO 5.3 · Gaussian connectors began 0.20–0.26 from real images, against the · frozen model's 0.05. With zeros, no noise reaches the frozen features. · CONTROLLING DIFFUSION MODELS · CANERY.IN
- Alt text: Line chart of sample distance while a ControlNet branch trains: zero connectors flat from the frozen model's 0.05, Gaussian from 0.23
- Long description: A ControlNet-style branch on the lab's trained network: a trainable copy of its first two hidden layers reads the image plus a 4×4 pooled layout of the target and joins the frozen network through connectors initialised at zero, as in ControlNet, or from a Gaussian, measured on two seeds each over 3,200 training steps. At step 0 the zero branch changes no output at all (largest change 0) and its samples sit 0.05 from real images, the frozen model's distance; the Gaussian branch changes outputs by up to 5.3 and starts 0.20–0.26 from real images, then recovers as it trains. With zeros, no random noise reaches the frozen features while the copy learns.
- Keywords: ControlNet, zero convolution, initialisation, conditional generation, adapters, diffusion model
- Canonical URL: https://canery.in/blogs/controlling-diffusion-models

### feed-06-five-photos-teach-the-photos

- File: `assets/social/feed-06-five-photos-teach-the-photos.png`
- Title: Five photos teach the photos
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Fine-tuning on five photos learns the subject, rewrites the plain class without prior preservation and copies the photos' own narrow brightness spread
- Technical source: article section "What do LoRA and personalisation change, and what do they forget?", Figure 11, lab captures (personal → methods at 2,000 steps; world → brightness_sd)
- Visual structure: Lockup and counter; serif headline; deck; a table of subject share and drift for textual inversion, LoRA, LoRA with prior preservation, full fine-tuning and full fine-tuning with prior preservation, drifts of 100% in orange; below a rule, the brightness spread of a real thin crescent and of each seed's five photos and four fine-tunes; takeaway; footer
- Visible-text transcript: Canery.in · 06 / 08 · Five photos teach · the photos. · The lab fine-tuned its model on five photos of a thinner crescent 0, · five ways, 2,000 steps each, two seeds. · DRAWS THE SUBJECT · PLAIN 'CRESCENT 0' DRIFTS · textual inversion · 0.9–1.3% · 0% · LoRA · 100% · 100% · LoRA + prior preservation · 100% · 0% · full fine-tune · 100% · 100% · full fine-tune + prior · 100% · 0–0.2% · BRIGHTNESS SPREAD OF THE SUBJECT'S SAMPLES · a real thin crescent · 0.30 · seed 1: its five photos · the four fine-tunes · 0.119 · 0.11–0.14 · seed 2: its five photos · the four fine-tunes · 0.194 · 0.18–0.20 · Without prior preservation, every plain 'crescent 0' became the · subject. Every fine-tune copied its photos' brightness spread. · CONTROLLING DIFFUSION MODELS · CANERY.IN
- Alt text: Table of subject share and drift for five personalisation recipes, and the brightness spread fine-tuned models copied from five photos
- Long description: The lab's network is taught one subject, a thinner crescent 0, from five photos by five recipes, each for 2,000 steps on two seeds. Textual inversion produced the subject in 0.9–1.3% of samples and never drifted. LoRA and full fine-tuning produced it 100% of the time and, without prior preservation, also produced it for the plain prompt 'crescent 0' 100% of the time; with prior preservation that drift was 0% and 0–0.2%. A real thin crescent's brightness varies with a spread of 0.30, but seed 1's five photos spread 0.119 and seed 2's 0.194, and the four fine-tuned models reproduced 0.11–0.14 and 0.18–0.20: with five examples, the model learns the photos.
- Keywords: LoRA, DreamBooth, textual inversion, prior preservation, language drift, personalisation
- Canonical URL: https://canery.in/blogs/controlling-diffusion-models

### feed-07-editing-trades-a-ghost-for-detail

- File: `assets/social/feed-07-editing-trades-a-ghost-for-detail.png`
- Title: Editing trades a ghost for detail
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: SDEdit's one dial keeps the old image's ghost and its fine detail in the same closed-form proportion; DDIM inversion escapes the trade
- Technical source: article sections "How do you edit an image you already have?" and "The math", Figure 13, lab captures (edit → sdedit, edit → inversion)
- Visual structure: Lockup and counter; serif headline; deck; the closed form kept = τ/√(τ² + σ₀²) with τ = 0.1; a table of ghost left, detail kept and the closed form at σ₀ = 0.5, 1, 2 and 4; below a rule, DDIM inversion's ghost and detail; notes on the data and metrics; takeaway; footer
- Visible-text transcript: Canery.in · 07 / 08 · Editing trades · a ghost for detail. · SDEdit noises an image to σ₀ and denoises it as the new class; in · crescent world, what it keeps of the old image has a closed form. · kept = τ / √(τ² + σ₀²) · τ = 0.1 · σ₀ · GHOST LEFT · DETAIL KEPT · CLOSED FORM · 0.5 · 0.194 · 0.202 · 0.196 · 1 · 0.098 · 0.106 · 0.100 · 2 · 0.049 · 0.056 · 0.050 · 4 · 0.025 · 0.032 · 0.025 · DDIM inversion · 0.001 · 1.000 · 1,024 IMAGES OF CRESCENT 0 EDITED INTO CRESCENT 1 · EXACT DENOISERS · GHOST: SHARE OF THE OLD CRESCENT LEFT · DETAIL: CORRELATION WITH THE SOURCE'S · No σ₀ keeps the detail without keeping the ghost. DDIM inversion · escapes the dial: 0.1% of the old crescent left, all of the detail. · CONTROLLING DIFFUSION MODELS · CANERY.IN
- Alt text: SDEdit's ghost and kept detail at σ₀ = 0.5 to 4 beside the closed form τ/√(τ² + σ₀²); DDIM inversion keeps the detail without a ghost
- Long description: 1,024 images of crescent 0 are edited into crescent 1 with crescent world's exact denoisers. SDEdit noises each image to σ₀ and denoises it under the new class, and keeps a fraction τ/√(τ² + σ₀²) of everything the new class's denoiser cannot explain, with τ = 0.1 the detail's spread. Measured, the ghost of the old crescent and the detail's correlation with the source are 0.194 and 0.202 at σ₀ = 0.5 (closed form 0.196), 0.098 and 0.106 at 1 (0.100), 0.049 and 0.056 at 2 (0.050), and 0.025 and 0.032 at 4 (0.025). No σ₀ keeps the detail without keeping the ghost. DDIM inversion runs crescent 0's path back to noise and crescent 1's forward again: 0.1% of the old crescent left, detail correlation 1.000.
- Keywords: SDEdit, DDIM inversion, image editing, closed form, image-to-image, diffusion model
- Canonical URL: https://canery.in/blogs/controlling-diffusion-models

### feed-08-read-the-article

- File: `assets/social/feed-08-read-the-article.png`
- Title: Every control has a price: read the article
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: The five control families and the price of each, with the call to read the full article
- Technical source: article sections "Intuition" (Figure 2) and "Key takeaways", Figure 10
- Visual structure: Lockup and counter; serif headline; deck; a white panel listing five methods in serif, each with its price in mono; takeaway; the orange call to action with the article address
- Visible-text transcript: Canery.in · 08 / 08 · Every control · has a price. · Guidance and its fixes, ControlNet, LoRA, DreamBooth, inpainting and · editing, measured on a laptop in a toy world with exact denoisers. · Classifier-free guidance · pays in coverage: the less typical look goes · ControlNet · 361M trained parameters whose output starts at zero · LoRA and DreamBooth · learn the subject; without prior preservation, the class too · Inpainting · coherence, or ten times the calls · SDEdit and DDIM inversion · a ghost, or the inverse path · Choosing a knob is choosing what to lose. · READ IT AT CANERY.IN/BLOGS/CONTROLLING-DIFFUSION-MODELS
- Alt text: Closing card: classifier-free guidance, ControlNet, LoRA and DreamBooth, inpainting and editing, each with its price, and the article link
- Long description: The closing card lists five ways to control a diffusion model and what each costs, as the article measures them: classifier-free guidance pays in coverage, deleting a class's less typical look; ControlNet trains 361M parameters on Stable Diffusion 1.5 whose output starts at zero; LoRA and DreamBooth learn the subject and, without prior preservation, the class too; inpainting by replacement costs coherence, or ten times the denoiser calls with resampling; SDEdit leaves a ghost of the old image, and DDIM inversion needs the inverse path. Choosing a knob is choosing what to lose. The full article is at canery.in/blogs/controlling-diffusion-models.
- Keywords: diffusion models, classifier-free guidance, ControlNet, LoRA, DreamBooth, inpainting, image editing
- Canonical URL: https://canery.in/blogs/controlling-diffusion-models
