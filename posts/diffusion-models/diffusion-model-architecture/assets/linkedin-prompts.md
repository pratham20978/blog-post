# LinkedIn image prompts — diffusion-model-architecture

## 01 — Noise becomes structure

- Narrative beat: A diffusion system turns a simple noise distribution into structured data through many field-guided corrections.
- File: `linkedin-01-noise-becomes-structure.png`
- Alt text: A chain of tiled fields changes from scattered noise into an ordered structure around one orange correction point.

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 portrait LinkedIn carousel cover introducing diffusion as a repeated transformation from noise into structured data.

SUBJECT
Six tiled fields form a calm vertical-to-diagonal progression. The first is scattered and irregular; each later field becomes more aligned until the final field forms one coherent geometric object. A single correction tile midway through the path is orange.

KEY DETAILS
Use identical cell shapes at every stage so the changing organization is the only variable. Fine arrows connect the states. Keep the last structure abstract rather than depicting a specific photograph, and leave generous negative space around the progression.

CONSTRAINTS
4:5 portrait frame, designed for a LinkedIn carousel. Editorial technical illustration with flat vector-like shapes, fine consistent line work, subtle paper grain, and generous negative space. Palette strictly limited to jet-black #2d3142, blue-slate #4f5d75, silver #bfc0c0, white-smoke #f5f5f5, and atomic-tangerine #eb6c36. White-smoke dominates; atomic-tangerine appears once on the focal element and covers less than five percent of the frame. Maintain the same visual world, scale language, line weight, palette, and recurring objects across every frame in the sequence. One idea per frame. No text, letters, numbers, labels, captions, logos, watermarks, signatures, UI chrome, photorealism, stock-photo people, glossy 3D, lens flare, or drop shadows. Keep meaningful content inside a five percent safe margin and use large shapes that remain legible at mobile-feed size.
```

## 02 — Path, field, and solver

- Narrative beat: The architecture becomes legible when the corruption path, learned field, and numerical solver are treated separately.
- File: `linkedin-02-path-field-solver.png`
- Alt text: Three connected instruments depict a fixed track, a directional compass field, and a stepping numerical mechanism.

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 portrait LinkedIn carousel frame separating the three mechanisms inside a diffusion generator.

SUBJECT
Three large technical instruments share one work surface: a fixed rail connecting ordered and noisy tiles, a compass-like vector field that bends toward structure, and a calibrated stepping mechanism that advances a token along the rail. Only the central field compass has one orange needle.

KEY DETAILS
Make the rail visibly fixed, the vector field visibly learned through directional arrows, and the stepper visibly numerical through repeated equal movements. Reuse the same square noise tokens from the cover so the series feels continuous without requiring words.

CONSTRAINTS
4:5 portrait frame, designed for a LinkedIn carousel. Editorial technical illustration with flat vector-like shapes, fine consistent line work, subtle paper grain, and generous negative space. Palette strictly limited to jet-black #2d3142, blue-slate #4f5d75, silver #bfc0c0, white-smoke #f5f5f5, and atomic-tangerine #eb6c36. White-smoke dominates; atomic-tangerine appears once on the focal element and covers less than five percent of the frame. Maintain the same visual world, scale language, line weight, palette, and recurring objects across every frame in the sequence. One idea per frame. No text, letters, numbers, labels, captions, logos, watermarks, signatures, UI chrome, photorealism, stock-photo people, glossy 3D, lens flare, or drop shadows. Keep meaningful content inside a five percent safe margin and use large shapes that remain legible at mobile-feed size.
```

## 03 — U-Net and transformer backbones

- Narrative beat: U-Nets and diffusion transformers are alternative field estimators, not different definitions of diffusion.
- File: `linkedin-03-unet-and-transformer.png`
- Alt text: A multiscale U-shaped machine and a row of equal token blocks process matching noisy grids toward the same output.

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 portrait LinkedIn carousel comparison of the two main neural backbone families used to estimate a diffusion field.

SUBJECT
One noisy tile grid splits into two parallel machines. On the left, a U-shaped sequence shrinks the grid through multiple scales and restores it with skip bridges. On the right, the grid becomes equal square tokens that pass through a deep stack of uniform attention blocks. Both paths converge on matching output grids.

KEY DETAILS
Keep the inputs and outputs identical so only the internal computation changes. Use one orange bridge on the U-shaped path as the focal accent. Preserve the square-token language and fine blue-slate connectors introduced in earlier frames.

CONSTRAINTS
4:5 portrait frame, designed for a LinkedIn carousel. Editorial technical illustration with flat vector-like shapes, fine consistent line work, subtle paper grain, and generous negative space. Palette strictly limited to jet-black #2d3142, blue-slate #4f5d75, silver #bfc0c0, white-smoke #f5f5f5, and atomic-tangerine #eb6c36. White-smoke dominates; atomic-tangerine appears once on the focal element and covers less than five percent of the frame. Maintain the same visual world, scale language, line weight, palette, and recurring objects across every frame in the sequence. One idea per frame. No text, letters, numbers, labels, captions, logos, watermarks, signatures, UI chrome, photorealism, stock-photo people, glossy 3D, lens flare, or drop shadows. Keep meaningful content inside a five percent safe margin and use large shapes that remain legible at mobile-feed size.
```

## 04 — Conditioning bends the field

- Narrative beat: Text conditioning and classifier-free guidance change the predicted direction before the solver takes a step.
- File: `linkedin-04-conditioning-bends-field.png`
- Alt text: Two vector arrows from one noisy point combine into a stronger orange direction before a single solver step.

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 portrait LinkedIn carousel frame showing how conditional and unconditional predictions combine during classifier-free guidance.

SUBJECT
At one noisy square, a muted arrow points along the unconditional direction and a blue-slate arrow points along the text-conditioned direction. A precise geometric construction subtracts and scales their difference to form one orange guided arrow, which a small stepping mechanism follows once.

KEY DETAILS
Show only one state and one update so this does not imply three separate sampling trajectories. Reuse the compass-field motif and square token from the second frame. The orange guided arrow is the only accent and should remain under five percent of the composition.

CONSTRAINTS
4:5 portrait frame, designed for a LinkedIn carousel. Editorial technical illustration with flat vector-like shapes, fine consistent line work, subtle paper grain, and generous negative space. Palette strictly limited to jet-black #2d3142, blue-slate #4f5d75, silver #bfc0c0, white-smoke #f5f5f5, and atomic-tangerine #eb6c36. White-smoke dominates; atomic-tangerine appears once on the focal element and covers less than five percent of the frame. Maintain the same visual world, scale language, line weight, palette, and recurring objects across every frame in the sequence. One idea per frame. No text, letters, numbers, labels, captions, logos, watermarks, signatures, UI chrome, photorealism, stock-photo people, glossy 3D, lens flare, or drop shadows. Keep meaningful content inside a five percent safe margin and use large shapes that remain legible at mobile-feed size.
```

## 05 — One point, four descriptions

- Narrative beat: Noise, clean data, score, and velocity are four coordinate readings of the same noisy state rather than four rival model families.
- File: `linkedin-05-one-point-four-descriptions.png`
- Alt text: One marked point on a drafting circle carries four measured directions, with the orange one reading the velocity coordinate.

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 portrait LinkedIn carousel frame showing that several diffusion prediction targets describe one noisy state.

SUBJECT
A precise drafting circle with two perpendicular reference rails. A single marked token sits off-centre on the rim, and its position is projected onto both rails by fine dashed construction lines. Four measuring arms radiate from the centre; one of them, orange, is set exactly perpendicular to the arm that reaches the token.

KEY DETAILS
Reuse the square token and compass-arrow motifs from the earlier frames. The perpendicularity between the token arm and the orange arm must be visually exact, because that right angle is the idea. Keep the construction sparse: one circle, two rails, four arms, no clutter.

CONSTRAINTS
4:5 portrait frame, designed for a LinkedIn carousel. Editorial technical illustration with flat vector-like shapes, fine consistent line work, subtle paper grain, and generous negative space. Palette strictly limited to jet-black #2d3142, blue-slate #4f5d75, silver #bfc0c0, white-smoke #f5f5f5, and atomic-tangerine #eb6c36. White-smoke dominates; atomic-tangerine appears once on the focal element and covers less than five percent of the frame. Maintain the same visual world, scale language, line weight, palette, and recurring objects across every frame in the sequence. One idea per frame. No text, letters, numbers, labels, captions, logos, watermarks, signatures, UI chrome, photorealism, stock-photo people, glossy 3D, lens flare, or drop shadows. Keep meaningful content inside a five percent safe margin and use large shapes that remain legible at mobile-feed size.
```

## 06 — Same shape, wrong meaning

- Narrative beat: A checkpoint can satisfy every tensor-shape assertion while its semantics stay ambiguous, which is the usual cause of plausible but wrong output.
- File: `linkedin-06-same-shape-wrong-meaning.png`
- Alt text: Two stacks of identically shaped blocks sit on a balance that reads level, while an orange inspection lens finds their interiors differ.

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 portrait LinkedIn carousel frame about checkpoint metadata that shape checks cannot catch.

SUBJECT
Two columns of identically sized blocks face each other on a level balance beam, implying the shapes match. An orange inspection lens hovers over one pair and reveals that their internal keying is different: one block's notches align with its neighbour, the other's are rotated out of register.

KEY DETAILS
The blocks must look interchangeable at a glance and only differ under the lens, because that is the whole point. Reuse the square token shapes and fine measuring lines from the earlier frames. The balance reading level is essential; do not tip it.

CONSTRAINTS
4:5 portrait frame, designed for a LinkedIn carousel. Editorial technical illustration with flat vector-like shapes, fine consistent line work, subtle paper grain, and generous negative space. Palette strictly limited to jet-black #2d3142, blue-slate #4f5d75, silver #bfc0c0, white-smoke #f5f5f5, and atomic-tangerine #eb6c36. White-smoke dominates; atomic-tangerine appears once on the focal element and covers less than five percent of the frame. Maintain the same visual world, scale language, line weight, palette, and recurring objects across every frame in the sequence. One idea per frame. No text, letters, numbers, labels, captions, logos, watermarks, signatures, UI chrome, photorealism, stock-photo people, glossy 3D, lens flare, or drop shadows. Keep meaningful content inside a five percent safe margin and use large shapes that remain legible at mobile-feed size.
```

## 07 — Design the whole system

- Narrative beat: A production diffusion model must align representation, backbone, objective, conditioning, and sampler interfaces.
- File: `linkedin-07-design-the-whole-system.png`
- Alt text: Five interlocking technical modules form one pipeline, with an orange interface gauge checking their alignment.

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 portrait LinkedIn carousel closing frame that turns diffusion architecture into a whole-system engineering checklist.

SUBJECT
Five substantial modules interlock on one drafting surface: a compressed representation grid, a multiscale or token field engine, a target calibration dial, a conditioning connector, and a numerical stepper. A single orange alignment gauge spans their interfaces while a stream of noise tokens enters and structured tokens leave.

KEY DETAILS
Make every module physically distinct but connected, reusing the square grids, compass arrows, and stepping mechanism from the prior frames. Emphasize interface fit rather than one heroic central network. Keep the lower third open enough to feel like a clear conclusion.

CONSTRAINTS
4:5 portrait frame, designed for a LinkedIn carousel. Editorial technical illustration with flat vector-like shapes, fine consistent line work, subtle paper grain, and generous negative space. Palette strictly limited to jet-black #2d3142, blue-slate #4f5d75, silver #bfc0c0, white-smoke #f5f5f5, and atomic-tangerine #eb6c36. White-smoke dominates; atomic-tangerine appears once on the focal element and covers less than five percent of the frame. Maintain the same visual world, scale language, line weight, palette, and recurring objects across every frame in the sequence. One idea per frame. No text, letters, numbers, labels, captions, logos, watermarks, signatures, UI chrome, photorealism, stock-photo people, glossy 3D, lens flare, or drop shadows. Keep meaningful content inside a five percent safe margin and use large shapes that remain legible at mobile-feed size.
```
