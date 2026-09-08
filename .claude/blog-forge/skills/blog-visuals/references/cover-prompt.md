# Cover image prompt

The cover is generated outside this pipeline. This skill writes `assets/cover-prompt.md`, which the user pastes into an image tool.

The goal is not one good image. It is 365 covers that look like they came from the same publication. That comes from the house-style block, which never changes, and from the discipline of only varying blocks 1 to 3.

---

## Structure

Eight blocks, always in this order.

| # | Block | Varies per post |
|---|---|---|
| 1 | Concept | yes |
| 2 | Composition | yes |
| 3 | Technique | slightly |
| 4 | Palette | no — locked |
| 5 | Light and mood | no — locked |
| 6 | Frame | no — locked |
| 7 | Negative | no — locked |
| 8 | House style | no — identical every time |

Blocks 4 to 8 are copied verbatim from this file. Only 1 to 3 are written fresh.

---

### 1 — Concept

The idea, and the visual metaphor for it. Two to four sentences.

The metaphor must be **physical and drawable**. Image models cannot render abstraction directly. "Congestion control" produces nothing; "a narrow channel where flow backs up behind a constriction" produces something.

Sources for a metaphor: the physical thing the concept is named after, the shape of the data, the failure mode, the geometry of the problem.

Do not ask for the diagram. The cover is an image that sets a mood and signals the subject. The explaining is what the figures inside the post are for.

### 2 — Composition

Where things sit. Be explicit, because unspecified composition is where covers drift apart from each other.

Name: the focal element and its position, what sits behind it, what sits in the foreground, and where the negative space is. Keep the right third or the lower third relatively empty so a title overlay has somewhere to go.

Example: "The constriction sits slightly left of centre, at about one third across. Flowing forms enter from the left edge and compress into it. Behind, a faint regular grid recedes. The right third is near-empty, holding only a soft gradient."

### 3 — Technique

How it is rendered. Keep close to the house style; this block is for small variations only.

Options that hold together across a series: technical illustration, isometric line work, editorial print illustration, risograph texture, blueprint drafting, engraved cross-hatch, soft geometric abstraction.

Name line weight and texture. "Fine consistent line weight, subtle paper grain, flat fills with no gradients inside shapes."

### 4 — Palette (locked)

```
Palette, strictly limited to these five colours and their tints:
jet-black #2d3142, blue-slate #4f5d75, silver #bfc0c0,
white-smoke #f5f5f5, atomic-tangerine #eb6c36.
White-smoke dominates as the background. Jet-black and blue-slate carry
structure. Atomic-tangerine is used once, on the single focal element, and
covers less than five percent of the frame. No other hues anywhere.
```

The single-accent rule is what makes a cover read as ours and matches the diagram style inside the post. Tangerine everywhere is the fastest way to lose it.

### 5 — Light and mood (locked)

```
Even, diffuse light with no dramatic shadows. Calm, precise, and technical
rather than energetic. The mood of a well-made reference book, not a
conference keynote slide.
```

### 6 — Frame (locked)

```
16:9 aspect ratio, 1200 by 630 pixels. Keep all meaningful content within a
5 percent margin from every edge. The composition must survive being cropped
to a square and to a 4:1 banner.
```

The crop requirement matters because the same image is used as a social card, a list thumbnail, and a page header.

### 7 — Negative (locked)

```
Do not include: any text, letters, numbers, words, labels, or captions.
No logos, watermarks, signatures, or UI chrome. No photorealism, no stock-photo
people, no 3D chrome or glossy renders, no lens flare, no drop shadows.
No colours outside the stated palette. No busy detail — large readable shapes
only, since this is viewed at thumbnail size.
```

Text is the important one. Image models mangle typography, and the title is overlaid by the site anyway.

### 8 — House style (locked, identical every time)

```
House style: an editorial technical illustration for a computer-science
publication. Flat vector-like shapes with fine line work, generous negative
space, and a single point of emphasis. Restrained and geometric. It should
look hand-designed for this specific article rather than generic tech art,
and it should sit comfortably beside clean black-and-white technical diagrams
without competing with them. Composed to stay legible at 300 pixels wide.
```

---

## Worked example

For a post on TCP treating wireless loss as congestion:

```
1. CONCEPT
A wide stream of uniform flowing forms moving left to right, meeting a
narrow constriction. Some forms scatter and dissipate before reaching the
constriction rather than queuing at it — the loss happened for a reason
unrelated to the narrowing. The constriction is the focal element.

2. COMPOSITION
The constriction sits one third from the left, vertically centred. The
flowing forms enter from the left edge, dense and regular. Past the
constriction they thin out and drift toward the lower right. A faint
regular grid recedes behind everything. The upper right third is near-empty.

3. TECHNIQUE
Flat editorial technical illustration. Fine consistent line weight, flat
fills with no internal gradients, subtle paper grain over the whole frame.
No outlines on the background grid.

4. PALETTE
[locked block, verbatim]

5. LIGHT AND MOOD
[locked block, verbatim]

6. FRAME
[locked block, verbatim]

7. NEGATIVE
[locked block, verbatim]

8. HOUSE STYLE
[locked block, verbatim]
```

---

## Template cover fallback

When an external tool is not wanted, build the cover in diagram-design and export to PNG.

The template: title in Instrument Serif at the optical centre, category label in Geist Mono small caps above it, a single simplified diagram motif drawn from the post's most important figure, on white-smoke paper with one tangerine element.

This is deterministic, on-brand, carries real typography, and takes seconds. It is the right choice for a day when the post matters more than the cover.

---

## Alt text for the cover

The cover still needs alt text, even though it is decorative. Describe what it depicts, not what it means:

> Flowing forms narrowing into a constriction, with some scattering away before reaching it
