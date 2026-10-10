# LinkedIn post

Most people who freeze at image processing don't freeze at the symbols. They freeze
because nobody ever showed them what the symbols are actually evaluating.

So here is the whole field on one 5×5 patch of integers, worked by hand.

Background 40. Foreground 200. One bad pixel at 255.

Apply three "noise removal" operators to the identical nine numbers around that bad
pixel and you get three different answers: the box mean says 64, the Gaussian says
99, the median says 40. Only one of them actually removed anything. The Gaussian did
worse than the box because it puts 27% of its weight on the one pixel that's wrong.

That gap is the whole subject. Two of those three operators are the same operation
with different weights — lay a small grid over a neighbourhood, multiply, add. The
third one sorts instead, and that single distinction separates half the field from
the other half.

Swipe through for the four stages the whole thing decomposes into, and the place
where a single bad pixel moves a Sobel gradient by 67%.

---

## Carousel order

1. `linkedin-01-grid-takes-it.png` — a continuous surface becomes discrete samples, and everything between them is gone
2. `linkedin-02-the-window.png` — almost every classical operation is a small square of weights sliding across the image
3. `linkedin-03-three-answers.png` — three operators on one identical neighbourhood return three different values
4. `linkedin-04-one-bad-pixel.png` — a single corrupted sample throws a derivative measured three positions away
5. `linkedin-05-l1-overstates.png` — measuring the same diagonal along the legs instead of straight across overstates it
6. `linkedin-06-library-vs-math.png` — the documented behaviour and the operation the name implies are not the same thing

---

## Accessibility checklist

- [ ] Upload frames in the numbered order.
- [ ] Apply each frame's supplied alt text from `assets/linkedin-prompts.md`.
- [ ] Check every frame is legible at mobile-feed size before posting.
- [ ] Confirm no frame rendered text, since the prompts forbid it and models sometimes ignore that.

---

## First comment

Every "optimal" operator in this field is optimal under conditions its name does not
carry — Canny assumes a one-dimensional step edge in white Gaussian noise, and the
detector you actually call defaults to a gradient magnitude that overstates diagonal
edges by 41%.

Read the full article on Canery: https://canery.in/blogs/image-processing-by-hand
