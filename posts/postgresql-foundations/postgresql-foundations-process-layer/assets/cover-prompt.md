# Cover prompt — postgresql-foundations-process-layer

Paste blocks 1–8 into an image tool. Blocks 4–8 are the locked house style and are
copied verbatim from `blog-visuals/references/cover-prompt.md` — do not edit them.
They are identical to part 1's, which is the point: the three covers of the series
should read as one set.

A deterministic fallback already exists at `assets/cover.png`, built in the
diagram-design skin (title in Instrument Serif, the supervisor-and-workers motif, one
tangerine worker). Use it on any day when the post matters more than the cover.

**Alt text for the cover:** One small square set above a row of identical squares, each
joined to it by a thin line, with one square in the row highlighted and carrying a
short trail of dots behind it

---

```
1. CONCEPT
A single small square sits alone near the top of the frame. Below it, a row of
identical squares stands side by side, each joined to the lone square above by
a single thin line, so the lines fan outward from one point. The squares in the
row are plain and evenly spaced except one, which is the only coloured element
and trails a short row of small dots behind it, as if it has been sweeping
along the row picking things up. One position in the row is empty — a gap where
a square used to be, with its fan line ending in nothing. The coloured square
is the focal element.

2. COMPOSITION
The lone square sits at about one quarter down the frame and one third across.
The row of squares runs along the lower third, extending from one fifth across
to about four fifths, leaving the right edge open. The fan lines are fine and
evenly spaced, never crossing. The coloured square sits right of centre in the
row, with the empty gap two positions to its left. Behind everything a faint
regular grid recedes. Generous empty ground above and to the right.

3. TECHNIQUE
Flat editorial technical illustration. Fine consistent line weight, flat
fills with no internal gradients, subtle paper grain over the whole frame.
Squares drawn as rounded squares with a single hairline outline; the row
implied by alignment rather than drawn as a container.

4. PALETTE
Palette, strictly limited to these five colours and their tints:
jet-black #2d3142, blue-slate #4f5d75, silver #bfc0c0,
white-smoke #f5f5f5, atomic-tangerine #eb6c36.
White-smoke dominates as the background. Jet-black and blue-slate carry
structure. Atomic-tangerine is used once, on the single focal element, and
covers less than five percent of the frame. No other hues anywhere.

5. LIGHT AND MOOD
Even, diffuse light with no dramatic shadows. Calm, precise, and technical
rather than energetic. The mood of a well-made reference book, not a
conference keynote slide.

6. FRAME
16:9 aspect ratio, 1200 by 630 pixels. Keep all meaningful content within a
5 percent margin from every edge. The composition must survive being cropped
to a square and to a 4:1 banner.

7. NEGATIVE
Do not include: any text, letters, numbers, words, labels, or captions.
No logos, watermarks, signatures, or UI chrome. No photorealism, no stock-photo
people, no 3D chrome or glossy renders, no lens flare, no drop shadows.
No colours outside the stated palette. No busy detail — large readable shapes
only, since this is viewed at thumbnail size.

8. HOUSE STYLE
House style: an editorial technical illustration for a computer-science
publication. Flat vector-like shapes with fine line work, generous negative
space, and a single point of emphasis. Restrained and geometric. It should
look hand-designed for this specific article rather than generic tech art,
and it should sit comfortably beside clean black-and-white technical diagrams
without competing with them. Composed to stay legible at 300 pixels wide.
```

---

## Why this motif

The lone square is the postmaster; the fan lines are the fork relationships that make
every other process its child; the coloured square with a trail is an autovacuum worker
moving through the table; the gap is the backend that was killed. Part 1's cover was
three stacked shelves (the three memory pools). Part 3's should be a single wide band of
tiles (the file on disk), so the three read as one set without repeating a shape.
