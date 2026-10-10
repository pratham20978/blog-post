# LinkedIn post

You change one argument — `ksize=1` to `ksize=3` — in `cv2.Laplacian`, and every value
in the output quadruples. The threshold you tuned yesterday now passes everything.

That is not a bug. It is a different operator with the same name.

"The Laplacian" is a family of 3×3 stencils. On smooth data they agree up to a scale
factor: ×1, ×2, ×3, ×4. On the pixels you actually care about — edges, hot pixels,
corners — they disagree, and OpenCV's `ksize=3` is the diagonal-only member at four
times the scale. The docs say "Sobel second derivatives"; the source says
`[2 0 2; 0 −8 0; 2 0 2]`. Both are true.

Underneath all of it is one identity: the Laplacian is what Gaussian blur removes, per
unit of scale. Sharpening adds it back. Zero-crossing edge detection finds where it is
zero. Blob detection multiplies it by σ² and searches for the σ that makes it
extremal. The Laplacian pyramid stores it once per octave. Poisson editing keeps it
and throws the pixels away.

Worked by hand on one 5×5 patch of integers: +160 and −160 either side of a step, −860
at a single bad pixel, a 134% error from one pixel that isn't even next to the edge.

Swipe through for the five jobs, the one bad pixel, and the factor each library call
silently applies.

---

## Carousel order

1. `linkedin-01-one-operator.png` — one identity, five jobs
2. `linkedin-02-mean-minus-centre.png` — the operator is four times the gap between a pixel and its neighbours' mean
3. `linkedin-03-one-bad-pixel.png` — one defective sample produces the largest response in the field and a 134% error next to it
4. `linkedin-04-ksize-three.png` — OpenCV's ksize=3 is a different stencil at four times the scale
5. `linkedin-05-sigma-is-a-ruler.png` — multiply by σ² and the σ at the peak is the size of the structure
6. `linkedin-06-the-factor.png` — each library call applies a scale factor the docs mention on a different page

---

## Accessibility checklist

- [ ] Upload frames in the numbered order.
- [ ] Apply each frame's supplied alt text from `assets/linkedin-prompts.md`.
- [ ] Check every frame is legible at mobile-feed size before posting.
- [ ] Confirm no frame rendered text, if the prompt route was used instead of the built frames.

---

## First comment

Every discrete Laplacian without a σ is a defect detector first and an edge detector
second: on the patch, a single hot pixel scores −860 and the genuine edge scores 160.

Read the full article on Canery: https://canery.in/blogs/laplacian-by-hand
