# LinkedIn visual handoff

Create this handoff after the article and its canonical URL are final. It is a
social adaptation of the article, not a second set of explanatory blog figures.

## Choose the sequence

Select 4–10 beats that form one teaching arc: problem, model, mechanism,
consequence, and practical takeaway. Use only the beats the article needs; do
not inflate the count to fill a carousel. Each frame must advance the argument.

Write `assets/linkedin-prompts.md` in this shape:

````markdown
# LinkedIn image prompts — <slug>

## 01 — <short frame name>

- Narrative beat: <what this frame teaches>
- File: linkedin-01-<slug>.png
- Alt text: <80–140 character description>

### Prompt

```text
SCENE AND INTENDED USE
<a 4:5 LinkedIn carousel frame and the moment it depicts>

SUBJECT
<physical, drawable subject and action>

KEY DETAILS
<composition, continuity objects, technique, and single focal point>

CONSTRAINTS
<the complete locked style block below>
```
````

Number frames contiguously from `01`. Every prompt is self-contained: someone
must be able to paste frame 06 into ChatGPT without carrying context from frame
05. Repeat the full constraints in every prompt.

The prompt order follows the official OpenAI image guidance: intended use and
scene, subject, key details, then constraints. Clear visual beats make a
multi-image story coherent:
https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide

## Locked sequence style

Copy this into every prompt:

```text
4:5 portrait frame, designed for a LinkedIn carousel. Editorial technical
illustration with flat vector-like shapes, fine consistent line work, subtle
paper grain, and generous negative space. Palette strictly limited to
jet-black #2d3142, blue-slate #4f5d75, silver #bfc0c0, white-smoke #f5f5f5,
and atomic-tangerine #eb6c36. White-smoke dominates; atomic-tangerine appears
once on the focal element and covers less than five percent of the frame.
Maintain the same visual world, scale language, line weight, palette, and
recurring objects across every frame in the sequence. One idea per frame.
No text, letters, numbers, labels, captions, logos, watermarks, signatures, UI
chrome, photorealism, stock-photo people, glossy 3D, lens flare, or drop
shadows. Keep meaningful content inside a five percent safe margin and use
large shapes that remain legible at mobile-feed size.
```

## LinkedIn copy

Write `linkedin.md` beside `blog.md`:

```markdown
# LinkedIn post

<specific hook, short teaching arc, and invitation to move through the images>

## Carousel order

1. `linkedin-01-<slug>.png` — <beat>
...

## Accessibility checklist

- [ ] Upload frames in the numbered order.
- [ ] Apply each frame's supplied alt text.

## First comment

<one-line takeaway or short pull quote>

Read the full article on Canery: <canonical_url>
```

Keep the article URL out of the main post. The first comment owns the link and
must contain the resolved `canonical_url` from frontmatter, not a placeholder.
Do not invent performance claims or quotations while shortening the article.
