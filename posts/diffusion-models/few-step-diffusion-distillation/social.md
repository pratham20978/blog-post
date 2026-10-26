---
social_schema: 2
canonical_url: "https://canery.in/blogs/few-step-diffusion-distillation"
---

# Social publishing package — few-step-diffusion-distillation

## LinkedIn post

SDXL-Turbo makes an image in one network call. A solver needs 10 to 30, and below about ten its order stops helping. The difference is training: a second network, the student, learns to jump to where the sampling path would end.

Measured against an exact teacher, in a toy whose ideal denoiser and sampling path have closed forms:

→ One DDIM call from pure noise returns the average of every image, a blur. At two calls, a progressively distilled student lands 0.042 from the data; DDIM with the exact denoiser, 0.243.
→ The jump has a cliff. Two noises 0.002 apart end on opposite crescents, and a network fitted to that map strands 1.0% of all noises between them.
→ Errors live at the decisions. The 13% of noises nearest a decision boundary produced 60–76% of every one-call student's wrong decisions; the 53% farthest from one produced one in 17,504.
→ More calls re-decide. Re-noising between calls cut a consistency model's blends from 23% to 0.7%, while its pairing with the starting noise fell to chance.
→ Matching the set can drop a mode. Every distribution-matching run first put all its samples on one crescent; the teacher's noise-image pairs brought all four back within 400 updates, distribution matching alone took 800 to 3,100.

The two failures move different numbers, fidelity and coverage, so FID alone hides one of them.

Part 7 of the Diffusion Models series.

## LinkedIn first comment

Progressive distillation, consistency models, DMD and shortcut models, measured against an exact teacher, with a lab you can run on a laptop CPU.

Read the full article on Canery: https://canery.in/blogs/few-step-diffusion-distillation

## Instagram caption

SDXL-Turbo makes an image in one network call, because a second network learned to jump to where the sampler's path ends.

Swipe through why one solver call returns a blur, the target a distilled student is trained on, the cliff in the map from noise to image, where the errors live, students against solvers, and how matching the set can drop a mode.

Every measured number comes from a lab you can run on a laptop CPU, against an exact teacher; published results are quoted with their setup.

Link in bio.

#diffusionmodels #machinelearning #deeplearning #generativeai #knowledgedistillation #consistencymodels #computervision

## Shared feed order

1. `assets/social/feed-01-twenty-steps-into-one.png` — samples from the exact path, one DDIM call and a one-call student
2. `assets/social/feed-02-told-where-the-path-goes.png` — the worked example's distillation target, by hand
3. `assets/social/feed-03-a-cliff-in-the-map.png` — the exact map's step against a fitted network's ramp
4. `assets/social/feed-04-errors-live-at-decisions.png` — the students' flips against the noises near a boundary
5. `assets/social/feed-05-students-beat-solvers.png` — sample distance at 1, 2 and 4 calls
6. `assets/social/feed-06-matching-the-set-drops-a-mode.png` — crescent coverage during DMD training
7. `assets/social/feed-07-read-the-article.png` — the four method families and the CTA

## Instagram Story

- CTA: How 20 diffusion steps become one, and what breaks, measured in a lab you can run — tap the link.
- Link sticker label: Read the article
- Link sticker URL: https://canery.in/blogs/few-step-diffusion-distillation

### Story order

1. `assets/social/story-01-twenty-steps-into-one.png` — Overlay: One call returns a blur. A student returns an image.
2. `assets/social/story-02-a-cliff-in-the-map.png` — Overlay: Noises 0.002 apart. Opposite images.
3. `assets/social/story-03-errors-live-at-decisions.png` — Overlay: 13% of the noises, most of the mistakes.
4. `assets/social/story-04-read-the-article.png` — Overlay: 20 steps into 1. Link above.

## Asset metadata

### feed-01-twenty-steps-into-one

- File: `assets/social/feed-01-twenty-steps-into-one.png`
- Title: Twenty steps into one
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: One solver call from pure noise can only return the denoiser's first answer, the average of every image; a distilled student returns an image in the same one call
- Technical source: article sections "The problem" and "What does a consistency model learn?", Figure 4, lab captures (samples → exact, methods → ddim_1, pd_1)
- Visual structure: Lockup and counter; serif headline; deck; a three-by-three grid of 8×8 greyscale samples from three starting noises far from any decision boundary, in rows labelled exact path, DDIM with one call (nearly the same ring three times) and the one-call progressive-distillation student; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 07 · Twenty steps · into one. · A sampler walks from noise to image one network call at a time. · A few-step student is trained to jump to where the walk ends. · EXACT PATH · DDIM, 1 CALL · STUDENT, 1 CALL · One DDIM call returns the average of every crescent, a ring. · A distilled student returns a crescent. · FEW-STEP DIFFUSION AND DISTILLATION · CANERY.IN
- Alt text: 8×8 samples from three noises: crescents on the exact path, one grey ring from one DDIM call, the same crescents from a one-call student
- Long description: Three starting noises far from any decision boundary are carried to images three ways in crescent world at 8×8 pixels. The exact probability-flow path, solved to about 10⁻¹⁰, ends on three crescents. One DDIM call with the exact denoiser returns its first answer from σ = 80, the average of all four crescents, a ring, nearly the same for every noise. A progressive-distillation student, trained to jump in one call to where its teacher's path ends, returns the same three crescents as the exact path.
- Keywords: few-step diffusion, distillation, one-step generation, DDIM, progressive distillation, student network, diffusion model
- Canonical URL: https://canery.in/blogs/few-step-diffusion-distillation

### feed-02-told-where-the-path-goes

- File: `assets/social/feed-02-told-where-the-path-goes.png`
- Title: The student is told where the path goes
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Progressive distillation trains one student step to land where two teacher steps land, and inverting the DDIM step turns that landing point into a target about four times further from the blur than the denoiser's answer
- Technical source: article sections "Four steps into two, by hand" and "How does progressive distillation halve the steps?", lab captures (worked → halving, rows)
- Visual structure: Headline and deck; a six-row table of values on the worked example's one coordinate: the true denoiser at x = 40, σ = 80, the teacher's two DDIM steps to σ = 2.515, the student's target in orange, then, below a rule, the endpoints after two calls for DDIM, for a perfectly distilled student and for the exact path; takeaway
- Visible-text transcript: Canery.in · 02 / 07 · The student is told · where the path goes. · Progressive distillation: one student step must land where two · teacher steps land. Inverting that step gives its target. · ONE NUMBER BETWEEN TWO CRESCENTS AT ±5.18 · true denoiser at x = 40, σ = 80 · 0.168 · teacher: two DDIM steps to σ = 2.515 · 1.937 · the student's target for one step · 0.701 · after two calls: DDIM · 4.249 · after two calls: a perfectly distilled student · 5.021 · the exact path · 5.149 · Trained to say 0.701 where the denoiser says 0.168, the student · commits four times sooner. It is not a better denoiser. · FEW-STEP DIFFUSION AND DISTILLATION · CANERY.IN
- Alt text: Denoiser 0.168 at x = 40, σ = 80; the student's target 0.701; after two calls DDIM 4.249, a perfect student 5.021, the exact path 5.149
- Long description: On one number between two crescents at ±5.18, starting from x = 40 at σ = 80, the true denoiser answers 0.168, almost the midpoint. The teacher, DDIM on a four-step grid, takes two steps and reaches 1.937 at σ = 2.515. The student must reach the same point in one step of the same form, which means outputting (1.937 − (2.515/80)·40)/(1 − 2.515/80) = 0.701, about four times further toward the crescent than the denoiser's answer. Two DDIM calls end at 4.249; a student that hits its targets exactly ends at 5.021, where its four-step teacher ends; the exact path ends at 5.149.
- Keywords: progressive distillation, distillation target, DDIM, worked example, denoiser, teacher, student
- Canonical URL: https://canery.in/blogs/few-step-diffusion-distillation

### feed-03-a-cliff-in-the-map

- File: `assets/social/feed-03-a-cliff-in-the-map.png`
- Title: Where each noise ends is a cliff
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: The map from starting noise to endpoint jumps at a decision boundary, and a network fitted to it by least squares can only draw a ramp, stranding the noises on the ramp between the crescents
- Technical source: article section "The cliff", Figure 1, lab captures (worked → map, exact_pm, student_1d)
- Visual structure: Headline and deck; a chart of endpoint against starting noise ε, zoomed to ±0.05: the exact path as a dark step at zero with a dotted riser, a fitted network's orange ramp, dashed lines at the crescents ±5.18 and a tinted band between them; legend; axis note; takeaway
- Visible-text transcript: Canery.in · 03 / 07 · Where each noise ends · is a cliff. · Two noises 0.002 apart end on opposite crescents, ±4.86. · A one-call student must draw that step with a smooth function. · crescent +5.18 · BETWEEN THE CRESCENTS · crescent −5.18 · −0.04 · −0.02 · 0 · +0.02 · +0.04 · exact path · a network fitted to it · STARTING NOISE ε, ZOOMED TO ±0.05 · Fitted by least squares, it ramps from ε −0.010 to +0.015 · and leaves 1.0% of all noises between the crescents. · FEW-STEP DIFFUSION AND DISTILLATION · CANERY.IN
- Alt text: The exact endpoint against starting noise jumps from −4.86 to +4.86 at zero; a fitted network's ramp crosses the band between the crescents
- Long description: In the worked example's one dimension, the exact probability-flow path from noise ε at σ = 80 ends at −4.86 for ε = −0.001 and at +4.86 for ε = +0.001: noises 0.002 apart end on opposite crescents. A small network fitted to that map by least squares is smooth, so it ramps from one crescent to the other, staying within half the crescent distance of the midpoint between ε = −0.010 and +0.015, and the 1.0% of noises it maps there end between the crescents, as blends no exact path produces.
- Keywords: decision boundary, flow map, discontinuity, least squares, blend, one-step student, probability-flow ODE
- Canonical URL: https://canery.in/blogs/few-step-diffusion-distillation

### feed-04-errors-live-at-decisions

- File: `assets/social/feed-04-errors-live-at-decisions.png`
- Title: Errors live at the decisions
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: The one-call students' wrong decisions come mostly from the few noises that lean almost equally toward two crescents, and almost never from the clear ones
- Technical source: article section "What does a consistency model learn?", Figure 5, lab captures (margin_bins, margin_share, students → steps → 1 → flip_by_margin)
- Visual structure: Headline and deck; five labelled horizontal bars: the share of each one-call student's flips from noises with margin below 0.1, in orange (direct regression, progressive distillation, consistency distillation, shortcut model), against the share of all noises there, in grey; takeaway
- Visible-text transcript: Canery.in · 04 / 07 · Errors live at · the decisions. · 4,096 noises through four one-call students. A noise is near a · boundary when it leans almost equally toward two crescents. · SHARE OF EACH STUDENT'S FLIPS FROM NOISES NEAR A BOUNDARY · direct regression · 76% · progressive distillation · 64% · consistency distillation · 69% · shortcut model · 60% · the noises themselves · 13% · For the 53% of noises farthest from a boundary, the four · students, two seeds each, flipped one decision in 17,504. · FEW-STEP DIFFUSION AND DISTILLATION · CANERY.IN
- Alt text: Bars: 76%, 64%, 69% and 60% of four one-call students' flips come from the 13% of noises nearest a decision boundary
- Long description: For each of 4,096 starting noises the lab measures its margin, the gap between its two largest projections onto the four crescent directions, and whether a one-call student draws a different crescent from the exact path, a flip. The 13% of noises with margin below 0.1 produced 76% of direct regression's flips, 64% of progressive distillation's, 69% of consistency distillation's and 60% of the shortcut model's, means of two seeds. For the 53% of noises with margin 0.4 or more, the four students, two seeds each, flipped one decision in 17,504.
- Keywords: decision boundary, margin, flip rate, one-step student, error analysis, consistency distillation, shortcut model
- Canonical URL: https://canery.in/blogs/few-step-diffusion-distillation

### feed-05-students-beat-solvers

- File: `assets/social/feed-05-students-beat-solvers.png`
- Title: Below eight calls, a student wins
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: At the same number of network calls, progressive distillation's networks get closer to the data than two solvers that use the exact denoiser
- Technical source: article section "How does progressive distillation halve the steps?", Figure 3, lab captures (reference → solvers, swd_floor; students → pd)
- Visual structure: Headline and deck; grouped bars of sample distance to the data at 1, 2 and 4 calls for DDIM with the exact denoiser (dark), DPM-Solver++(2M) with the exact denoiser (slate) and the progressive-distillation student (orange), each bar labelled with its value; legend; takeaway
- Visible-text transcript: Canery.in · 05 / 07 · Below eight calls, · a student wins. · Progressive distillation's students against two solvers at the · same number of network calls. The solvers use the exact denoiser. · SAMPLE DISTANCE TO THE DATA · LOWER IS BETTER · 0.707 · 0.707 · 0.046 · 1 call · 0.243 · 0.243 · 0.042 · 2 calls · 0.128 · 0.055 · 0.040 · 4 calls · DDIM, exact denoiser · DPM-Solver++(2M), exact · distilled student · At two calls: 0.042 for the student, 0.243 for DDIM. · Two independent sets of real images differ by 0.034. · FEW-STEP DIFFUSION AND DISTILLATION · CANERY.IN
- Alt text: Sample distance at 1, 2 and 4 calls: DDIM 0.707, 0.243, 0.128; DPM-Solver++(2M) 0.707, 0.243, 0.055; student 0.046, 0.042, 0.040
- Long description: Sliced Wasserstein distance between 4,096 samples and the data, with the students' values the mean of two seeds. With one call, DDIM and DPM-Solver++(2M) both return the blur, 0.707, and the one-step student is at 0.046. At two calls the solvers are at 0.243 and the two-step student at 0.042; at four, DDIM is at 0.128, DPM-Solver++(2M) at 0.055 and the student at 0.040. Two independent sets of real images differ by 0.034, the floor. The solvers use the exact denoiser; the students are trained networks, each round distilled from the last.
- Keywords: progressive distillation, DDIM, DPM-Solver++, network calls, sliced Wasserstein distance, few-step sampling, benchmark
- Canonical URL: https://canery.in/blogs/few-step-diffusion-distillation

### feed-06-matching-the-set-drops-a-mode

- File: `assets/social/feed-06-matching-the-set-drops-a-mode.png`
- Title: Matching the set can drop a mode
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Distribution matching never asks where each noise should end; in the lab every run first collapsed onto one crescent, and the teacher's noise-image pairs brought the others back far sooner
- Technical source: article section "What happens when the student stops following the path?", Figure 7, lab captures (students → dmd_5to1 → 1 → trace)
- Visual structure: Headline and deck; a line chart of the share of samples on each of the four crescents over the first 4,000 generator updates of DMD with five fake-denoiser updates per generator update, seed 1: one line jumps to 100% by update 100 and holds until about update 1,800, the other three drop to 0% and return between updates 1,900 and 3,100; a dashed line at 25%; axis notes; takeaway
- Visible-text transcript: Canery.in · 06 / 07 · Matching the set · can drop a mode. · Distribution matching never asks where each noise should end. · In the lab, every run first put all its samples on one crescent. · 100% · 75% · 50% · 25% · 0% · 0 · 1,000 · 2,000 · 3,000 · 4,000 · GENERATOR UPDATES · SHARE OF SAMPLES ON EACH OF THE FOUR CRESCENTS · DMD WITH FIVE FAKE-DENOISER UPDATES PER GENERATOR UPDATE, SEED 1 · With the teacher's noise-image pairs, every crescent was back above · 15% of the samples within 400 updates; without, after 800 to 3,100. · FEW-STEP DIFFUSION AND DISTILLATION · CANERY.IN
- Alt text: Share of samples per crescent during DMD training: one crescent takes 100% by update 100, the others return between 1,900 and 3,100
- Long description: The lab's DMD generator starts from the teacher's weights, so its first samples are the blur and move together. With five fake-denoiser updates per generator update (seed 1), the samples of all 1,024 fixed noises land on one crescent by update 100, and the other three crescents stay empty until about update 1,800; from update 3,100 every crescent holds at least 15% of the samples again. All six DMD runs collapsed by update 100. With DMD's regression loss on the teacher's noise-image pairs, every crescent was back above 15% within 400 updates; without it, after 800 to 3,100.
- Keywords: distribution matching distillation, DMD, mode collapse, reverse KL, coverage, regression loss, training dynamics
- Canonical URL: https://canery.in/blogs/few-step-diffusion-distillation

### feed-07-read-the-article

- File: `assets/social/feed-07-read-the-article.png`
- Title: Twenty steps into one
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: The method families the article measures, what each costs, and where to read it
- Technical source: article Key takeaways and section "Which metric shows the damage?"
- Visual structure: Headline and deck; a white panel of five headed lines (progressive distillation, consistency models, distribution matching, shortcut models and flow maps, measure both); takeaway; orange CTA footer with the article URL
- Visible-text transcript: Canery.in · 07 / 07 · Twenty steps · into one. · Distillation, consistency models, DMD and flow maps, measured · against an exact teacher in a lab you can run on a laptop. · Progressive distillation · halve the steps round by round; one student per count · Consistency models · jump to the end; extra calls re-decide · Distribution matching · no pairing to keep; watch every mode · Shortcut models, flow maps · one network for any number of steps · Measure both · fidelity and coverage, not one FID · Every few-step method learns the jump, and pays for it: · in fidelity, in coverage, or in both. · READ IT AT CANERY.IN/BLOGS/FEW-STEP-DIFFUSION-DISTILLATION
- Alt text: Four few-step method families and what each costs, a reminder to measure fidelity and coverage, and the article URL
- Long description: The closing card summarises the article. Progressive distillation halves the steps round by round, one student per step count. Consistency models jump to the end, and extra calls re-decide what earlier calls decided. Distribution matching keeps no pairing with the starting noise and has to be watched mode by mode. Shortcut models and flow maps are one network for any number of steps. Measure fidelity and coverage, not one FID. The article and its laptop lab are at canery.in.
- Keywords: few-step diffusion, progressive distillation, consistency models, DMD, flow maps, Canery, article
- Canonical URL: https://canery.in/blogs/few-step-diffusion-distillation

### story-01-twenty-steps-into-one

- File: `assets/social/story-01-twenty-steps-into-one.png`
- Title: Twenty steps into one (Story)
- Platforms: Instagram Story
- Role: cover
- Dimensions: 1080×1920
- Narrative beat: Opening Story frame: one DDIM call returns the blur, and a one-call student returns the image the exact path ends on
- Technical source: article Figure 4, lab captures (samples → exact, methods → ddim_1, pd_1)
- Visual structure: Lockup and counter; serif headline; deck; the feed cover's three-by-three grid of 8×8 samples, larger; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 04 · Twenty steps · into one. · One DDIM call returns a blur. · A distilled student returns an image. · EXACT PATH · DDIM, 1 CALL · STUDENT, 1 CALL · The student learns where the path · from each noise ends. · FEW-STEP DIFFUSION AND DISTILLATION · CANERY.IN
- Alt text: Story frame: 8×8 samples from three noises, crescents on the exact path, a grey ring from one DDIM call, crescents from a one-call student
- Long description: A vertical Story frame. Three starting noises are carried to 8×8 images by the exact probability-flow path, by one DDIM call with the exact denoiser and by a one-call progressive-distillation student. The exact path and the student end on the same three crescents; one DDIM call returns the average of all four crescents, a ring. The student has learned where the path from each noise ends.
- Keywords: Instagram Story, few-step diffusion, one-step generation, DDIM, distillation, crescent, student
- Canonical URL: https://canery.in/blogs/few-step-diffusion-distillation

### story-02-a-cliff-in-the-map

- File: `assets/social/story-02-a-cliff-in-the-map.png`
- Title: Where each noise ends is a cliff (Story)
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: Story version of the cliff: the exact map's step at a decision boundary against a fitted student's ramp
- Technical source: article section "The cliff", Figure 1, lab captures (worked → map, student_1d)
- Visual structure: Headline and deck; the endpoint-against-noise chart with the exact step, the fitted student's orange ramp, dashed crescent lines and the tinted band between them; legend; takeaway
- Visible-text transcript: Canery.in · 02 / 04 · Where each noise ends · is a cliff. · Noises 0.002 apart end on · opposite crescents. · crescent +5.18 · BETWEEN THE CRESCENTS · crescent −5.18 · −0.04 · −0.02 · 0 · +0.02 · +0.04 · exact path · fitted student · A smooth student strands 1.0% · of noises between the crescents. · FEW-STEP DIFFUSION AND DISTILLATION · CANERY.IN
- Alt text: Story frame: the exact endpoint against starting noise jumps between crescents at zero; a fitted student's smooth ramp crosses the gap
- Long description: A vertical Story frame with the worked example's map from starting noise to endpoint, zoomed to ε within ±0.05. The exact path jumps from one crescent to the other at ε = 0, so noises 0.002 apart end on opposite crescents. A network fitted to the map by least squares draws a smooth ramp instead and leaves 1.0% of all noises between the crescents.
- Keywords: Instagram Story, decision boundary, flow map, blend, least squares, one-step student, diffusion
- Canonical URL: https://canery.in/blogs/few-step-diffusion-distillation

### story-03-errors-live-at-decisions

- File: `assets/social/story-03-errors-live-at-decisions.png`
- Title: Errors live at the decisions (Story)
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: Story version of the margin analysis: a small share of noises near decision boundaries carries most of every student's flips
- Technical source: article Figure 5, lab captures (margin_share, students → steps → 1 → flip_by_margin)
- Visual structure: Headline and deck; five large bars, four students' shares of flips from noises near a boundary in orange and the share of noises there in grey; takeaway
- Visible-text transcript: Canery.in · 03 / 04 · Errors live at · the decisions. · Noises near a decision boundary, · against the students' flips. · SHARE OF EACH STUDENT'S FLIPS FROM NOISES NEAR A BOUNDARY · direct regression · 76% · progressive distillation · 64% · consistency distillation · 69% · shortcut model · 60% · the noises themselves · 13% · 13% of the noises carry most · of every student's mistakes. · FEW-STEP DIFFUSION AND DISTILLATION · CANERY.IN
- Alt text: Story frame: 60–76% of four one-call students' flips come from the 13% of noises nearest a decision boundary
- Long description: A vertical Story frame. Of 4,096 starting noises, the 13% that lean almost equally toward two crescents (margin below 0.1) produced 76% of direct regression's flips, 64% of progressive distillation's, 69% of consistency distillation's and 60% of the shortcut model's, means of two seeds.
- Keywords: Instagram Story, decision boundary, margin, flip rate, error analysis, distillation, diffusion
- Canonical URL: https://canery.in/blogs/few-step-diffusion-distillation

### story-04-read-the-article

- File: `assets/social/story-04-read-the-article.png`
- Title: Twenty steps into one (Story)
- Platforms: Instagram Story
- Role: cta
- Dimensions: 1080×1920
- Narrative beat: Closing Story frame: the five questions the article answers, and the link sticker
- Technical source: article Jump-to list and section headings
- Visual structure: Lockup and counter; headline; deck; an orange-tinted panel listing five numbered topics; takeaway; orange CTA footer pointing to the link sticker
- Visible-text transcript: Canery.in · 04 / 04 · Twenty steps · into one. · Few-step diffusion, measured · against an exact teacher. · 1 · why one solver call returns a blur · 2 · how progressive distillation halves steps · 3 · what a consistency model learns · 4 · how distribution matching drops modes · 5 · one network for any step count · The full article is on Canery. · LINK IN THE STICKER ABOVE
- Alt text: Story frame listing five questions about few-step diffusion the article answers, with a call to tap the link sticker above
- Long description: The closing Story frame lists what the article covers: why one solver call returns a blur, how progressive distillation halves the steps, what a consistency model learns, how distribution matching drops modes, and how one network can take any number of steps. Each is measured against an exact teacher in a lab you can run on a laptop. The call to action points to the link sticker above.
- Keywords: Instagram Story, few-step diffusion, distillation, consistency models, DMD, Canery, link
- Canonical URL: https://canery.in/blogs/few-step-diffusion-distillation
