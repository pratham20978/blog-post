---
title: "Mathematical Morphology as Lattice Algebra"
slug: mathematical-morphology
date: 2026-10-14
updated: 2026-10-14
summary: "Erosion and dilation are an adjoint pair, and every law of opening, closing, top-hat and granulometry follows from it. Worked by hand on a tiny 5×5 patch."
tags: [algorithms, image-processing, mathematical-morphology, structuring-element, top-hat-transform, opencv]
category: algorithms
categories: [algorithms]
tier: L3
difficulty: advanced
series: image-processing
series_position: 12
prerequisites: ["the shared 5×5 patch and the non-linear operators from part 1 of this series", "sets, unions and intersections", "reading Python signatures"]
reading_minutes: 30
cover_image_url: "COVER"
cover_image_alt: "A 5×5 mask with a bright bar and a tangerine speck, opened by a blue cross into the bar alone, beside the adjunction law"
canonical_url: "https://canery.in/blogs/mathematical-morphology"
---

> [!NOTE]
> **Insights** — Erosion and dilation are an adjoint pair: dilating a set A stays inside a set Y exactly when A stays inside the erosion of Y. Every law of mathematical morphology follows from that one equivalence: opening never adds a pixel, closing never removes one, both are idempotent, and openings by growing structuring elements whose sizes add sieve objects by size. Grey levels inherit the laws because flat operators commute with thresholds. The laws hold only while an implementation keeps the pair adjoint: on the series' 5×5 patch, OpenCV's closing with a 2×2 kernel deletes five pixels, and SciPy's default binary closing deletes seven.

**Level:** advanced · **You need:** *Image Processing by Hand* (part 1 of this series) for the shared patch and its non-linear operators, sets with union and intersection, and enough Python to read a signature · **Time:** ~30 min

This is part 12 of *Image Processing by Hand*. Part 1 defined erosion and dilation as a local minimum and maximum over a structuring element, drew morphology inside the rank operators in its Figure 10, and named this post for the algebra behind them. <!-- L54 --> Part 11, *Thresholding and Segmentation: Otsu, Sauvola, Watershed*, binarised the same patch and left the operators its watershed markers come from to this post, which builds them and hands their use in segmentation back.

**Jump to:** [The problem](#the-problem) · [Worked example](#worked-example) · [Intuition](#intuition) · [Dilations](#what-makes-an-operator-a-dilation) · [Idempotence](#why-are-opening-and-closing-idempotent) · [Grey levels](#how-do-grey-levels-inherit-the-laws) · [What the laws build](#what-do-the-laws-let-you-build) · [Libraries](#where-do-libraries-break-the-laws) · [The math](#the-math) · [Tooling map](#implementation-the-tooling-map) · [Limitations](#limitations-and-common-mistakes)

> [!IMPORTANT]
> Nothing in this post was run against an image. Every number is worked by hand on the shared patch, or on the patch tiled beside a copy of itself, and cross-checked with plain Python using only its built-in sets and lists; that check is not published. No OpenCV, scikit-image, SciPy or MATLAB call was executed: library behaviour comes from source read at pinned commits and release tags, replayed in that plain Python, and from MathWorks' documentation. There are no timings or measured curves.

## Why this matters

`cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)` reads like "open the mask twice, to clean it harder". It cannot mean that, because an opening applied a second time changes nothing. OpenCV erodes twice and then dilates twice, which is an opening by an element twice the size. <!-- L37 --> On the series' 5×5 patch with a 3×3 kernel, opening twice leaves 10 pixels of the mask; `iterations=2` leaves none.

Swap the kernel for `np.ones((2, 2))` and OpenCV's closing, an operation that by definition only adds pixels, deletes five of the mask's eleven. Neither result is a bug in your code. Both follow from laws that hold or fail for reasons you can check on paper, and this post derives those laws from one equivalence so you can predict a morphology call before you run it.

## The problem

Morphology treats a binary image as a **set**: the set of its foreground pixels, which this series calls a **mask**. A grey image is a function from pixels to grey levels. Both are probed with a **structuring element**, a small set of offsets around an origin, such as the 3×3 **cross**: the centre and its four neighbours. Moving the element so that its origin sits on pixel x gives its **translate**, $B_x$.

Part 1 gave the two primitives as a local minimum and maximum over the element. <!-- L54 --> On a mask, **erosion** keeps the pixels where the whole element fits inside the mask, and **dilation** stamps a copy of the element on every mask pixel and keeps the union, which is the **Minkowski sum** $X \oplus B$. Everything else is built by composing the two, and that is where the questions start. To trust a composite you need to know:

- whether it only removes pixels, only adds them, or both;
- whether applying it again changes anything;
- whether its grey version does, level by level, what its binary version does;
- whether two libraries that print the same function name compute the same set.

Linear filtering answers questions like these with a transfer function. Morphology has none, because the minimum of a sum is not the sum of the minima; Part 1 placed it in the stage where linearity stops. What replaces linearity is order: one mask lies inside another, one grey image is darker than another at every pixel. The problem is to find the laws that order gives, and the conditions, the image border and the direction of the element, under which a real implementation keeps them.

## Worked example

The patch is the series' 5×5 8-bit patch: every row is `40 40 40 200 200` except r2, which has an impulse of 255 at (r2, c1).

```text
      c0   c1   c2   c3   c4
r0    40   40   40  200  200
r1    40   40   40  200  200
r2    40  255   40  200  200
r3    40   40   40  200  200
r4    40   40   40  200  200
```

### Step 1: binarise

Keep the pixels brighter than 40, the cut Otsu's method returns on this patch in Part 11. The mask X has 11 pixels: a **bar** in columns c3 and c4, and the impulse alone at (r2, c1), a **speck**.

```text
      c0  c1  c2  c3  c4
r0     .   .   .   1   1
r1     .   .   .   1   1
r2     .   1   .   1   1
r3     .   .   .   1   1
r4     .   .   .   1   1
```

### Step 2: erode and dilate by the cross

Dilation stamps the cross on all 11 pixels. The bar's stamps cover columns c2 to c4, and the speck's stamp adds (r1, c1), (r2, c0), (r2, c1) and (r3, c1): 19 pixels.

Erosion keeps the pixels whose whole cross lies inside X. No pixel of c3 qualifies, because its left arm lands on c2, and the speck fails at once. Column c4 passes only because of a **border rule**, a decision about pixels outside the image: its right arm points outside. OpenCV pads an 8-bit erosion with 255 and a dilation with 0, and MATLAB assumes +∞ and −∞, so the outside never wins a minimum or a maximum and an arm that points outside is ignored. <!-- L35 --> <!-- L50 --> <!-- L51 --> The erosion is column c4, 5 pixels. Figure 1 shows both.

![The 11-pixel mask, the 3×3 cross, the 19-pixel dilation and the 5-pixel erosion, which is column c4 only](FIG_01)

*Figure 1 — The cross probes the mask. Dilation stamps it on every pixel (19 pixels); erosion keeps the 5 pixels where it fits, all on the right edge, because the outside is ignored. Worked by hand.*

### Step 3: open and close

The **opening** erodes then dilates. Stamping the cross on column c4 restores c3, so the opening is the bar, 10 pixels, with the speck gone. The **closing** dilates then erodes. Eroding the 19-pixel dilation keeps the bar, the speck, and c2 in rows r1 to r3, where every arm of the cross now lands on a dilated pixel: 14 pixels, with the one-pixel gap between speck and bar bridged. Figure 2 shows each applied once and twice.

![Opening keeps the 10-pixel bar and drops the speck; closing fills c2 in rows r1 to r3; each applied twice is unchanged](FIG_02)

*Figure 2 — Opening removes the bright detail the cross cannot fit; closing fills the dark detail it cannot fit. Applying either a second time changes nothing. Worked by hand.*

### Step 4: check the adjunction

The **adjunction** says that for any two masks A and Y, $\delta_B(A) \subseteq Y$ exactly when $A \subseteq \varepsilon_B(Y)$, where $\delta_B$ and $\varepsilon_B$ are dilation and erosion by B. <!-- L04 --> Check it on the sets already computed:

| A | Y | is δ(A) inside Y? | is A inside ε(Y)? |
|---|---|---|---|
| the speck | X | no: its cross reaches (r1, c1) | no: ε(X) is column c4 |
| ε(X), column c4 | X | yes: δ(c4) is the bar | yes, trivially |
| X | δ(X) | yes, trivially | yes: ε(δ(X)), the closing, contains X |
| X | X | no: δ(X) has 19 pixels | no: ε(X) has 5 |

The second row is the opening seen through the law: δ(ε(X)) lies inside X, so an opening never adds a pixel. The third row is the closing: X lies inside ε(δ(X)), so a closing never removes one. Across all 64 pairs drawn from the eight sets met so far (empty, speck, ε(X), opening, X, closing, δ(X) and the whole grid), the two sides agree every time. Figure 3 draws the four rows.

![Four rows of paired grids: δ(A) beside Y and A beside ε(Y), with the same yes or no on both sides of every row](FIG_03)

*Figure 3 — The adjunction on the patch: each row asks one question two ways and gets one answer. Rows 2 and 3 are the opening's and the closing's laws. Worked by hand.*

### Step 5: apply each twice

Open the opening: its erosion is column c4 again, the same as ε(X), so dilating gives back the same 10 pixels. Close the closing: its dilation is the same 19 pixels as δ(X), so eroding gives back the same 14. Both operators are **idempotent**: a second application changes nothing. The two identities just used, ε of the opening equals ε(X) and δ of the closing equals δ(X), follow from step 4's law, as the math section shows.

### Step 6: sieve by four sizes

Now open with growing elements: nB, the Minkowski sum of n crosses, for n = 0 to 3, which is a single pixel, the cross, and diamonds of 13 and 25 pixels. Each opening keeps what its element fits. The grey column applies the same openings to the patch itself, which the section on grey levels justifies, and sums its 25 values.

| n | element | mask area | grey volume |
|---|---|---|---|
| 0 | 1 pixel | 11 | 2,815 |
| 1 | cross, 5 pixels | 10 | 2,600 |
| 2 | diamond, 13 pixels | 0 | 1,000 |
| 3 | diamond, 25 pixels | 0 | 1,000 |

A family of openings by growing elements is a **granulometry**, a sieve, and its drops are the **pattern spectrum**: a size distribution of what the image contains. <!-- L23 --> <!-- L25 --> Here it reads one pixel of size 0, the speck, gone at n = 1, and ten of size 1, the bar, gone at n = 2; in grey, 215 and 1,600 above the floor of 40. Figure 4 plots both curves.

![Mask area 11, 10, 0, 0 and grey volume 2,815, 2,600, 1,000, 1,000 over sizes 0 to 3, with the pattern spectrum's two bars](FIG_04)

*Figure 4 — A sieve with four meshes. The speck falls through the first, the bar through the second, and nothing is left for the third. Computed from the definitions.*

Read the bar's size with care. It is two pixels wide, yet it survives the cross, which is three wide, because it touches the image's right edge and the outside is ignored. The section on libraries tiles the patch to show that a sieve measures an object touching the border as bigger than it is.

## Intuition

Dilation is stamping and erosion is fitting. Stamp the element on every pixel of A, and the stamps stay inside Y exactly when every pixel of A is a place where the element fits inside Y: the adjunction is one question asked from its two ends. The opening is then the union of every placement of the element that fits inside X. <!-- L08 --> It cannot add a pixel, since each placement lies inside X, and running it again finds the same placements.

Haralick, Sternberg and Zhuang compared opening and closing to ideal band-pass filters: once filtered, filtering again changes nothing. <!-- L31 --> The analogy holds for idempotence and breaks at addition. A linear filter splits an image into parts that sum back to it; the opening of a sum is not the sum of the openings, and what an opening removes is not a band you could filter out separately. It breaks at symmetry too. A band-pass treats bright and dark detail alike, while an opening removes only bright detail the element cannot fit and a closing only dark detail: on the patch the opening deletes the bright speck and leaves the dark gap, and the closing fills the gap and keeps the speck.

## What makes an operator a dilation?

### Order and the lattice

A **partial order** says when one image lies below another: mask A inside mask Y, or grey image f no brighter than g at any pixel. Two masks may be incomparable, neither inside the other, but any family of them has a smallest mask containing them all, the **supremum** (their union), and a largest mask inside them all, the **infimum** (their intersection). An order in which every family, the empty one included, has both is a **complete lattice**. <!-- L01 --> Grey images form one too, with the pixelwise maximum and minimum. Matheron and Serra, who started the field at the Paris School of Mines in 1964, were the first to observe that a general theory of morphology should assume this structure. <!-- L32 --> <!-- L33 -->

Linear filtering builds on operators that commute with sums, and the translation-invariant ones are convolutions. Morphology makes the same move with the lattice: a **dilation** is any operator that commutes with suprema, $\delta(\bigcup_i X_i) = \bigcup_i \delta(X_i)$, and an **erosion** is any operator that commutes with infima. <!-- L02 -->

### One pixel fixes a dilation

On the patch, the dilation of bar and speck together is the union of their dilations: 15 pixels and 5, overlapping at (r2, c2), make step 2's 19. Erosion distributes over intersections instead; over a union it gives only containment. <!-- L03 -->

That law has a strong consequence. Every mask is the union of its single pixels, so a dilation is fixed by what it does to one pixel. If it also commutes with translation, it does the same thing everywhere: it stamps one shape, the dilation of the pixel at the origin, which is the element. On a grid, then, the translation-invariant dilations and erosions are exactly the Minkowski sums and their adjoints. <!-- L07 --> The element plays the part a linear filter's impulse response plays.

Elements compose the same way: dilating by A and then by B is dilating by A ⊕ B, and two erosions are one erosion by the sum. <!-- L16 --> Two crosses make step 6's 13-pixel diamond. OpenCV uses this law: given a full rectangular kernel and several iterations, it substitutes one larger rectangle. <!-- L38 -->

### The median is morphology too

Part 1's Figure 10 drew morphology inside the rank filters, because erosion and dilation are the lowest and highest ranks. Matheron proved the reverse inclusion: every increasing, translation-invariant set operator is a union of erosions. <!-- L11 --> For rank filters the erosions are explicit. Rank k over a window of p pixels is the largest of the erosions by all of the window's k-pixel subsets, and k = (p + 1)/2 is the median. <!-- L12 --> <!-- L13 --> On the cross p = 5, so the median is the maximum of ten erosions by three-pixel subsets. On the patch it returns 40 at the impulse, as Part 1's median did, and so removes the impulse exactly, as the opening does. Figure 5 collects the four laws.

![Four panels: a pixel dilates to the cross; two dilations union to 19 pixels; two crosses make a diamond; the cross's ten 3-pixel subsets](FIG_05)

*Figure 5 — Four laws of dilation on the patch: a pixel dilates to the element, dilation distributes over union, elements compose by Minkowski sum, and the median is a maximum of erosions. Worked by hand.*

## Why are opening and closing idempotent?

The adjunction $\delta_B(A) \subseteq Y \iff A \subseteq \varepsilon_B(Y)$ is not a property of the cross. It holds for any element, provided the erosion is the set of places where B itself fits, and in any complete lattice every dilation has exactly one erosion paired with it this way. <!-- L04 --> <!-- L05 --> Lattice theory calls such a pair a **Galois connection**, and Serra called it morphological duality. <!-- L05 -->

Two substitutions give the laws. Put Y = δ(A): the left side holds, so A lies inside ε(δ(A)) and the closing is **extensive**, never removing a pixel. Put A = ε(Y): the right side holds, so δ(ε(Y)) lies inside Y and the opening is **anti-extensive**, never adding one. One more line gives δεδ = δ and εδε = ε, so opening twice is opening once and closing twice is closing once. <!-- L06 --> Step 5's two identities are these equations evaluated on the patch.

They are what morphology means by a **filter**: an operator that is **increasing**, preserving order, and idempotent. An **algebraic opening** is a filter that is also anti-extensive, an **algebraic closing** one that is also extensive. <!-- L09 --> Serra set out this axiomatics in 1982. <!-- L10 --> A union of openings is again an opening, so openings can be built from many elements, or from criteria that are not elements at all. <!-- L09 -->

### The other duality needs a reflection

Erosion has a second partner. The complement of the erosion of X is the dilation of the background, but by the **reflected** element $\check B$, the element turned through 180 degrees: eroding the foreground is dilating the background with the element flipped. <!-- L14 -->

So erosion by B has two dilations attached: the adjoint, by B, and the complement dual, by $\check B$. For the cross, and any element symmetric about its origin, they are the same set. For an asymmetric element they differ, and only the adjoint gives an opening that never adds and a closing that never removes. Authors disagree on which operator carries the reflection: Matheron and Serra write Minkowski subtraction with it, Hadwiger and Sternberg without, so textbooks print different formulas for the same opening. <!-- L15 --> Libraries disagree as well, as the section on libraries shows in numbers.

## How do grey levels inherit the laws?

### Threshold sets

Cut a grey image at level t and keep the pixels at t or above: that is its **threshold set** at t. The patch has only three distinct ones. Every t from 41 to 200 gives the mask X of step 1, every t from 201 to 255 gives the impulse alone, and every t up to 40 gives the whole grid.

A **flat** grey erosion takes the minimum over the element and a flat dilation the maximum. <!-- L17 --> Flat operators commute with thresholds: the threshold set of the eroded image is the erosion of the threshold set. <!-- L18 --> So the grey erosion of the patch is the binary erosion done at each level and stacked: column c4 at the mask's levels, nothing at the impulse's, the whole grid up to 40. Stacked, that is 200 on c4 and 40 everywhere else, the impulse gone and the step moved one column right, as Figure 6 shows.

![The patch's threshold sets at 41 and 201, each eroded by the cross, stacked back into the grey erosion with 200 on c4 and 40 elsewhere](FIG_06)

*Figure 6 — Grey erosion is binary erosion at every level. The threshold set at 41 is the worked example's mask; eroding each set and stacking them gives the grey result. Worked by hand.*

That is why the laws carry over without new proofs: every grey identity is the binary identity at each level. Meyer and Sternberg were among the first to extend morphology to grey images. <!-- L19 --> On the patch the grey opening is the patch without its impulse, with a sum of 2,600, the median's answer again; the grey closing raises the dark gap in c2 to 200 in rows r1 to r3.

### Gradients and top-hats

When the element contains its own origin, erosion is never brighter than the image and dilation never darker; the opening is never brighter and the closing never darker for any element. So four differences are never negative, and each picks out something:

- The **morphological gradient**, dilation minus erosion, is 160 on both sides of the step, the step's height, and 215 on the impulse and its four neighbours, (r2, c2) included. <!-- L21 --> The Sobel magnitude that Part 8, *Canny Edge Detection, Line by Line: Setting the Thresholds*, worked out for the patch reads 640 along c3, four times the step's height, and 0 on the impulse itself, where the derivative's two halves cancel. The morphological gradient is a range, maximum minus minimum, so it reads heights in grey levels and never cancels. Heijmans halves it, which makes it tend to the gradient's magnitude on a smooth image. <!-- L22 -->
- The **half-gradients** split it: the image minus its erosion is 160 on the bright side of the step (c3), the dilation minus the image 160 on the dark side (c2). <!-- L21 -->
- The **white top-hat**, the image minus its opening, is 215 at the impulse and 0 everywhere else: the impulse's height above its surroundings, extracted exactly. The top-hat exists to pull out narrow peaks. <!-- L20 -->
- The **black top-hat**, the closing minus the image, is 160 at c2 in rows r1 to r3: the dark gap the closing filled.

Figure 7 sets them beside the Sobel table.

![The morphological gradient (160 at the step, 215 round the impulse), Part 8's Sobel (640 and 0), and the white and black top-hats](FIG_07)

*Figure 7 — The morphological gradient reads the step's height, 160, on both sides of it and marks the impulse with 215, where Sobel reads 640 and 0. The top-hats isolate the bright peak and the dark gap. Worked by hand.*

## What do the laws let you build?

### Sieves

A granulometry needs one law: sieving twice keeps what the coarser sieve keeps, $\gamma_m \gamma_n = \gamma_{\max(m,n)}$. <!-- L23 --> Openings by a family of elements obey it when the sizes add, B(r) ⊕ B(s) = B(r + s), which for a compact element requires convexity. <!-- L24 --> The cross family does: nB is n crosses summed, and step 6's openings satisfy the law for every pair of sizes from 0 to 3.

Exact digital disks do not. The disk of radius 3, the 29 pixels with x² + y² ≤ 9, opened by the disk of radius 2 loses its four corner pixels at (±2, ±2), so a coarser sieve can keep pixels a finer one removed. MATLAB's `strel("disk", r)` approximates disks with periodic lines by default, and its documentation says exact disks are not suitable for granulometries. <!-- L52 -->

### Reconstruction

Grow a **marker** inside a mask one step at a time, dilating and then intersecting with the mask, until nothing changes. The result keeps, whole, every connected part of the mask that the marker touches: that is **reconstruction**. <!-- L26 --> Erode first and reconstruct under the original, and you get **opening by reconstruction**: parts the element cannot fit in vanish, and the rest come back exactly instead of smoothed. <!-- L27 --> On the patch it equals the opening, because the opening already restored the bar; it differs when a surviving object has detail the element cannot regrow.

In grey, subtract a height h and reconstruct under the image. A **regional maximum**, a plateau whose neighbours are all lower, survives only while h is below its **dynamic**: how far it must descend before reaching anything higher, or, for the highest maximum, its height above the image's minimum. <!-- L28 --> The bar's dynamic is 160 and the impulse's 215. With h = 100 both survive, at 100 and 155; with h = 180 only the impulse does, at 75; at h = 215 both are flat, as Figure 8 shows. The regional maxima themselves, the image minus its reconstruction from the image less 1, are the bar and the impulse: the mask X again. <!-- L28 -->

![Three grids of the patch reconstructed from itself minus h, for h = 100, 180 and 215, with the bar and impulse heights shrinking to 40](FIG_08)

*Figure 8 — Reconstruction from the patch minus h. Each maximum survives until h reaches its dynamic: 160 for the bar, 215 for the impulse. Worked by hand.*

This is the maxima version of the h-minima filter that Part 11 used to choose watershed markers, where the same reconstruction, run on the gradient, kept two of four minima.

### Distance

Erode the mask repeatedly by the cross and count how many erosions each pixel survives. Each erosion peels off one step of **city-block distance**, so the count is each pixel's distance to the background; in general the level sets of a **distance transform** are dilations and erosions by the metric's balls. <!-- L29 --> On the patch it is 1 on c3 and on the speck and 2 on c4. Part 11 floods the negated distance transform to split touching blobs, and the cleaned masks, the h-minima and this distance are the markers its watershed needs.

## Where do libraries break the laws?

### The border rule

A finite image needs a rule for its outside. OpenCV pads erosion with the type's maximum and dilation with its minimum, which is 0 for 8-bit images and −DBL_MAX only for 64-bit floats; <!-- L35 --> MATLAB assumes +∞ outside for erosion and −∞ for dilation; <!-- L50 --> <!-- L51 --> scikit-image's binary functions treat the outside as foreground when eroding. <!-- L46 --> All three say the outside never wins, and that keeps erosion and dilation adjoint on the bounded image: step 4's table holds exactly, and so do 20,000 random pairs of masks on the 5×5 grid.

SciPy's binary functions default to a border value of 0, the value assumed outside the input. <!-- L48 --> With it the cross erodes the mask to nothing, since every pixel's cross touches c2 or the outside, and the closing returns 7 pixels: it loses all of c4 and both ends of c3, and gains c2 in rows r1 to r3. A closing that removes pixels is not a closing. The adjunction fails on 616 of the same 20,000 pairs, and the smallest failure is one corner pixel, which is not inside the erosion of its own dilation.

The border also biases sizes. Tile the patch beside a copy of itself and the two bars are identical, but the inner one vanishes at n = 1 with the specks while the one on the edge survives to n = 2. Figure 9 shows both rules and the tiling.

![Erosion and closing of the mask with the outside ignored (5 and 14 px) and set to 0 (0 and 7), and the tiled patch keeping its edge bar](FIG_09)

*Figure 9 — The border rule is part of the operator. With the outside ignored the laws hold; with it set to 0, erosion empties the mask and closing removes seven pixels. Tiled, the edge bar outlasts its twin. Worked by hand.*

### The reflection

OpenCV's `dilate` takes the maximum of src(x + x′, y + y′) over the kernel's offsets, the same offsets `erode` uses for the minimum. <!-- L34 --> So OpenCV's dilate is the complement dual of its erode, not its adjoint. For a symmetric kernel nothing changes. For an asymmetric one `MORPH_OPEN` and `MORPH_CLOSE` compute the wrong composite, and every even-sized kernel is asymmetric: its **anchor**, OpenCV's name for the origin, sits at half the size, (1, 1) in a 2×2 kernel, off the centre. On the mask with `np.ones((2, 2))`, OpenCV's opening keeps only column c4, though the bar is a union of 2×2 squares and the true opening keeps all 10 pixels; its closing returns 7 pixels and loses 5 of the mask's 11. Issue #23605 has reported this since May 2023, noting that MATLAB and Octave give the expected result; it is still open. <!-- L42 --> Figure 10 shows both results and the fix: give the dilation the reflected anchor, `anchor=(0, 0)` for a 2×2 kernel.

![OpenCV's 2×2 opening (5 pixels) and closing (7 pixels, missing mask pixels) beside the true opening (10) and closing (13) and the anchor fix](FIG_10)

*Figure 10 — OpenCV's 2×2 opening and closing against the true ones. Without the reflection the closing removes pixels; dilating with the anchor at (0, 0) restores both laws. Replayed from OpenCV's source.*

scikit-image had the same defect and fixed it in 2023 by mirroring the footprint inside `opening` and `closing`. <!-- L43 --> Its grey `dilation` still does not mirror while `binary_dilation` does, which its docstring states. <!-- L44 --> At the pinned commit its next namespace, `skimage2`, drops the mirroring to follow SciPy, whose dilations reflect, and changes the grey border default from 'reflect' to 'ignore'. <!-- L45 --> <!-- L49 --> MATLAB reflects inside `imdilate`. <!-- L50 -->

### Iterations and names

OpenCV's `iterations=n` erodes n times and then dilates n times, as its documentation notes: <!-- L37 --> an opening by nB, which on the patch empties the mask. Element names do not travel either. OpenCV's default kernel is the 3×3 square <!-- L36 --> and scikit-image's the cross; <!-- L46 --> OpenCV's 3×3 "ellipse" is the cross, and its 5×5 ellipse has 17 pixels where scikit-image's `disk(2)` has 13. <!-- L40 --> <!-- L47 -->

## The math

| Symbol | Meaning |
|---|---|
| $X, Y, A$ | masks: sets of pixels |
| $B$, $B_x$, $\check B$ | structuring element; its translate to x; its reflection |
| $\oplus$ | Minkowski sum |
| $\varepsilon_B$, $\delta_B$ | erosion and dilation by $B$ |
| $\gamma_B = \delta_B\varepsilon_B$, $\varphi_B = \varepsilon_B\delta_B$ | opening and closing |
| $f$, $X_t(f)$ | grey image; its threshold set at level t |
| $D$ | the image's grid of pixels |

**Erosion and dilation.**

$$
\varepsilon_B(X) = \{x : B_x \subseteq X\}, \qquad \delta_B(X) = X \oplus B = \bigcup_{b \in B} X_b \tag{1}
$$

Erosion keeps the places where the element fits, and dilation is the union of copies of X shifted by each offset of B: 5 and 19 pixels on the patch.

**The adjunction.**

$$
\delta_B(A) \subseteq Y \iff A \subseteq \varepsilon_B(Y) \tag{2}
$$

Both sides say that every stamp of B centred on a pixel of A lies inside Y. <!-- L04 -->

<details>
<summary>Deriving the laws from (2)</summary>

Put $Y = \delta(A)$ in (2): the left side holds, so $A \subseteq \varepsilon\delta(A)$, and the closing is extensive. Put $A = \varepsilon(Y)$: the right side holds, so $\delta\varepsilon(Y) \subseteq Y$, and the opening is anti-extensive. Dilation is increasing, so applying it to $A \subseteq \varepsilon\delta(A)$ gives $\delta(A) \subseteq \delta\varepsilon\delta(A)$, while anti-extensivity at $Y = \delta(A)$ gives $\delta\varepsilon\delta(A) \subseteq \delta(A)$. So $\delta\varepsilon\delta = \delta$, and in the same way $\varepsilon\delta\varepsilon = \varepsilon$. Then $\gamma\gamma = \delta(\varepsilon\delta\varepsilon) = \delta\varepsilon = \gamma$ and $\varphi\varphi = \varepsilon(\delta\varepsilon\delta) = \varepsilon\delta = \varphi$. <!-- L06 -->

</details>

**On a bounded grid.** With the outside ignored,

$$
\delta(A) = (A \oplus B) \cap D, \qquad \varepsilon(Y) = \{x \in D : B_x \cap D \subseteq Y\} \tag{3}
$$

and both sides of (2) say the same thing, that every pixel of the grid within reach of A lies in Y, so the pair stays adjoint. A zero border replaces the second set with $\{x : B_x \subseteq Y\}$, which no pixel next to the edge can satisfy; that breaks (2) at the edge, and the closing's extensivity with it.

**Complement duality.**

$$
\left(\varepsilon_B X\right)^c = \delta_{\check B}\left(X^c\right) \tag{4}
$$

The dual of erosion by B is dilation by the reflected element, while the adjoint in (2) is dilation by B itself: two different dilations unless B is symmetric. <!-- L14 -->

**Grey levels.** For a flat element,

$$
(\varepsilon_B f)(x) = \min_{b \in B} f(x + b), \qquad (\delta_B f)(x) = \max_{b \in B} f(x - b), \qquad X_t(\varepsilon_B f) = \varepsilon_B\left(X_t f\right) \tag{5}
$$

The minus sign in the dilation is the reflection, and the last identity is the threshold law that lets every binary result hold level by level. <!-- L17 --> <!-- L18 -->

**Sieves.** For elements whose sizes add, $B(r) \oplus B(s) = B(r + s)$,

$$
\gamma_{B(m)}\,\gamma_{B(n)} = \gamma_{B(\max(m,n))}, \qquad \mathrm{PS}(n) = \operatorname{area}\left(\gamma_{nB}X\right) - \operatorname{area}\left(\gamma_{(n+1)B}X\right) \tag{6}
$$

The pattern spectrum is the area each size removes: 1 and 10 on the patch. <!-- L24 -->

## Implementation: the tooling map

Every entry below maps to the algebra above. **None of it was executed for this post**; it comes from source at pinned commits and tags and from MathWorks' documentation. Figure 11 is the same map in one picture.

![Grid comparing OpenCV, scikit-image, SciPy and MATLAB on default element, border rule, reflection in dilation, iterations and disk shapes](FIG_11)

*Figure 11 — Four libraries, four sets of conventions. Only the reflection and the border rule decide whether opening and closing keep their laws.*

### OpenCV

| Want | Call | Note |
|---|---|---|
| erosion, dilation | `cv2.erode(src, k)`, `cv2.dilate(src, k)` | default kernel the 3×3 square; the outside never wins; dilate does not reflect <!-- L34 --> <!-- L35 --> <!-- L36 --> |
| opening, closing | `cv2.morphologyEx(src, cv2.MORPH_OPEN, k)` | erode then dilate with the same anchor; `iterations=n` means n of each <!-- L37 --> |
| gradient, top-hats | `cv2.MORPH_GRADIENT`, `cv2.MORPH_TOPHAT`, `cv2.MORPH_BLACKHAT` | dilate minus erode; the image minus its opening; the closing minus the image <!-- L39 --> |
| element | `cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))` | the 3×3 ellipse is the cross; `MORPH_DIAMOND` from 4.12.0 <!-- L40 --> |
| reconstruction | none in `imgproc` | loop `marker = cv2.min(cv2.dilate(marker, k), mask)` until it stops changing <!-- L57 --> <!-- L26 --> |

Builds with Intel IPP do not change any of this: IPP's morphology path is compiled out at the pinned commit and in releases 4.10.0 to 4.12.0, and the only layers that replace OpenCV's own loops are the ARM (Carotene), OpenVX and RISC-V ones. <!-- L41 --> The behaviour described here is OpenCV's own code.

### scikit-image, SciPy and MATLAB

| Want | Call | Note |
|---|---|---|
| scikit-image grey | `erosion(img)`, `opening(img)`, `white_tophat(img)` | default footprint the cross; border mode 'reflect' <!-- L46 --> |
| scikit-image binary | `binary_erosion(mask)`, `binary_closing(mask)` | the outside never wins (mode 'ignore') <!-- L46 --> |
| reconstruction | `reconstruction(seed, mask)`, `h_maxima(img, h)` | 3×3 square by default <!-- L47 --> |
| SciPy binary | `ndimage.binary_dilation(m, border_value=0)` then `ndimage.binary_erosion(..., border_value=1)` | one `binary_closing` call uses one border value for both steps; its default 0 removes edge pixels <!-- L48 --> |
| SciPy reconstruction | `ndimage.binary_propagation(marker, mask=m)` | binary only; `iterations=n` in `binary_opening` means n of each, as in OpenCV <!-- L58 --> |
| MATLAB | `imerode`, `imdilate`, `imopen`, `imtophat`, `imreconstruct`, `imhmax` | `imdilate` reflects; ±∞ outside; `strel("disk", r)` approximates by default <!-- L50 --> <!-- L52 --> <!-- L53 --> |

### The worked example, in OpenCV and scikit-image

```python
import numpy as np
import cv2
from skimage.morphology import opening

patch = np.full((5, 5), 40, np.uint8)
patch[:, 3:] = 200
patch[2, 1] = 255
mask = (patch > 40).astype(np.uint8)                                  # 11 pixels
cross = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))

eroded = cv2.erode(mask, cross)                                       # column c4, 5 pixels
opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, cross)                # the bar, 10 pixels
closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cross)               # 14 pixels
emptied = cv2.morphologyEx(mask, cv2.MORPH_OPEN, cross, iterations=2) # 0 pixels, not "opened twice"
tophat = cv2.morphologyEx(patch, cv2.MORPH_TOPHAT, cross)             # 215 at (2, 1), 0 elsewhere

k2 = np.ones((2, 2), np.uint8)
bad = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k2)                     # 7 pixels, 5 of the mask's lost
good = cv2.erode(cv2.dilate(mask, k2, anchor=(0, 0)), k2)             # 13 pixels, contains the mask

same = (opening(patch) == cv2.morphologyEx(patch, cv2.MORPH_OPEN, cross)).all()  # True
```

This was not run for this post. The comments state what the worked example predicts.

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** giving `cv2.morphologyEx` an even-sized kernel such as `np.ones((2, 2))`. OpenCV's dilate does not reflect the kernel, so `MORPH_CLOSE` can remove pixels and `MORPH_OPEN` can shrink an object the kernel fits exactly; on the patch the closing loses five of the mask's pixels. Use odd, symmetric kernels, or dilate with the reflected anchor.

- **Reading `iterations` as repetition.** `iterations=2` is an opening by a larger element; to open twice, which changes nothing, call it once. <!-- L37 -->
- **SciPy's border default.** `binary_erosion` and `binary_closing` assume 0 outside, so objects touching the edge shrink and closings stop being closings. <!-- L48 -->
- **Sizing objects that touch the border.** With the outside ignored they survive larger elements than their width allows; drop them or pad before a granulometry.
- **Granulometries with exact disks.** They break the sieve law; use a family whose sizes add, such as diamonds, squares or periodic-line disks. <!-- L52 -->
- **Expecting an opening to respect length.** It removes every part the element cannot fit, so a one-pixel-wide line goes however long it is, and narrow isthmuses break. <!-- L30 -->
- **Treating bright and dark alike.** An opening removes bright detail only and a closing dark detail only; open-closing and clos-opening differ, which lets them tell positive impulses from negative ones. <!-- L55 -->
- **Non-flat elements on 8-bit data.** Adding heights to a finite grey range and truncating gives wrong results. <!-- L56 -->

## Key takeaways

- **Erosion and dilation are adjoint:** δ(A) lies inside Y exactly when A lies inside ε(Y), and that is why an opening never adds pixels, a closing never removes them, and both are idempotent.
- **On a grid, every translation-invariant dilation is a Minkowski sum** with one element, the dilation of a single pixel; elements compose by Minkowski sum, so iterating an operator enlarges its element.
- **Grey morphology is binary morphology at every threshold:** the gradient reads heights, 160 at the patch's step, and the top-hats isolate peaks and valleys smaller than the element.
- **The laws belong to the implementation as much as to the theory:** the border rule and the reflection decide them, and OpenCV's unreflected dilate breaks opening and closing for every asymmetric kernel.
- **A sieve needs elements whose sizes add,** and it measures objects that touch the border as larger than they are.

## Try it yourself

The exercises are pen and paper, matching the post; each names its rung.

### E1 — Reproduce: two pixels of the closing

Using the mask X and the cross, decide whether (r1, c2) and (r0, c2) belong to the closing. Compute the dilation at each pixel of their crosses first.

**Self-check:** a yes or no for each, with the arm of the cross that decides it.

<details><summary>Answer</summary>

The dilation contains all of c2 (from the bar) and (r1, c1), (r2, c1), (r3, c1), (r2, c0) (from the speck). The cross at (r1, c2) covers (r0, c2), (r2, c2), (r1, c1), (r1, c3) and itself, all dilated, so (r1, c2) is in the closing. The cross at (r0, c2) covers (r0, c1), which is not dilated, so (r0, c2) is not. The arm that decides it is the left one.

</details>

### E2 — Inspect: what each drop measures

In Figure 4, read off the grey volume each opening removes and say which structure of the patch it belongs to.

**Self-check:** two numbers that add up to the volume above the floor of 40.

<details><summary>Answer</summary>

From n = 0 to 1 the volume falls by 215, the impulse's height above 40 on one pixel. From n = 1 to 2 it falls by 1,600, the bar's ten pixels at 160 above 40. Together they make 1,815, the patch's volume above the floor (2,815 − 1,000).

</details>

### E3 — Predict: the gradient with the 3×3 square

Replace the cross by the 3×3 square and predict the morphological gradient of the grey patch: where it is 215, where it is 160, and how many pixels of each.

**Self-check:** the two sets of positions and their counts.

<details><summary>Answer</summary>

The square reaches the diagonals, so the impulse is inside the window of every pixel in rows r1 to r3 and columns c0 to c2, where the maximum is 255 and the minimum 40: 215 on those 9 pixels. The step gives 160 wherever the window holds both 40 and 200 without the impulse: all of c3, and c2 in rows r0 and r4, 7 pixels. Everything else is 0.

</details>

### E4 — Diagnose: a closing that loses pixels

A colleague closes the mask with `cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((2, 2), np.uint8))` and finds pixels of the bar missing from the result. Find the cause and give a fix that provably keeps every mask pixel.

**Self-check:** the law that was broken, the step that broke it, and a corrected call with its pixel count.

<details><summary>Answer</summary>

A closing must be extensive, and that follows only from the adjunction. OpenCV's dilate takes the maximum over the same offsets as erode, here (−1, −1), (−1, 0), (0, −1) and (0, 0) from the anchor at (1, 1), without reflecting them, so the dilation is the complement dual of the erosion and not its adjoint. The closing returns column c4 plus (r3, c2) and (r3, c3): 7 pixels, missing (r0, c3), (r1, c3), (r2, c3), (r4, c3) and the speck. Dilating with the reflected anchor, `cv2.erode(cv2.dilate(mask, k, anchor=(0, 0)), k)`, uses the offsets (0, 0) to (1, 1) for the dilation, makes the pair adjoint, and returns 13 pixels: the mask plus (r2, c0) and (r2, c2).

</details>

## References

1. Heijmans, H. J. A. M., and Ronse, C. "The Algebraic Basis of Mathematical Morphology I. Dilations and Erosions." *Computer Vision, Graphics, and Image Processing* 50(3):245–295, 1990. doi:10.1016/0734-189X(90)90148-O. [CWI report version](https://ir.cwi.nl/pub/5977/5977D.pdf)
2. Heijmans, H. J. A. M. "Mathematical Morphology: A Modern Approach in Image Processing Based on Algebra and Geometry." *SIAM Review* 37(1):1–36, 1995. doi:10.1137/1037001. [PDF](https://ir.cwi.nl/pub/2230/2230D.pdf)
3. Serra, J., and Vincent, L. "An Overview of Morphological Filtering." *Circuits, Systems and Signal Processing* 11(1):47–108, 1992. [doi:10.1007/BF01189221](https://doi.org/10.1007/BF01189221)
4. Vincent, L. "Morphological Grayscale Reconstruction in Image Analysis: Applications and Efficient Algorithms." *IEEE Transactions on Image Processing* 2(2):176–201, 1993. [doi:10.1109/83.217222](https://doi.org/10.1109/83.217222)
5. Haralick, R. M., Sternberg, S. R., and Zhuang, X. "Image Analysis Using Mathematical Morphology." *IEEE Transactions on Pattern Analysis and Machine Intelligence* 9(4):532–550, 1987. doi:10.1109/TPAMI.1987.4767941. [PDF](http://haralick.org/journals/04767941.pdf)
6. Maragos, P., and Schafer, R. W. "Morphological Filters — Part II: Their Relations to Median, Order-Statistic, and Stack Filters." *IEEE Transactions on Acoustics, Speech, and Signal Processing* 35(8):1170–1184, 1987. [doi:10.1109/TASSP.1987.1165254](https://doi.org/10.1109/TASSP.1987.1165254)
7. Maragos, P. "Pattern Spectrum and Multiscale Shape Representation." *IEEE Transactions on Pattern Analysis and Machine Intelligence* 11(7):701–716, 1989. [doi:10.1109/34.192465](https://doi.org/10.1109/34.192465)
8. Rivest, J.-F., Soille, P., and Beucher, S. "Morphological Gradients." *Journal of Electronic Imaging* 2(4):326–336, 1993. [doi:10.1117/12.159642](https://doi.org/10.1117/12.159642)
9. Heijmans, H. J. A. M. "Theoretical Aspects of Gray-Level Morphology." *IEEE Transactions on Pattern Analysis and Machine Intelligence* 13(6):568–582, 1991. [doi:10.1109/34.87343](https://doi.org/10.1109/34.87343)
10. OpenCV source, commit 802cf95: `morph.dispatch.cpp`, `morph.simd.hpp` and `imgproc.hpp`. <https://github.com/opencv/opencv/blob/802cf95aa3d42816995695bf68a86b3532f12760/modules/imgproc/src/morph.dispatch.cpp> (accessed 2026-10-14)
11. OpenCV source, tags 4.10.0 and 4.12.0. <https://github.com/opencv/opencv/blob/4.12.0/modules/imgproc/src/morph.dispatch.cpp> (accessed 2026-10-14)
12. OpenCV issue #23605, "Morphological openings are not anti extensive." <https://github.com/opencv/opencv/issues/23605> (accessed 2026-10-14)
13. scikit-image source, commit b700edc and release v0.26.0: `morphology/gray.py`, `binary.py`, `footprints.py`, `grayreconstruct.py`. <https://github.com/scikit-image/scikit-image/blob/v0.26.0/src/skimage/morphology/gray.py> (accessed 2026-10-14)
14. scikit-image issue #6676, "Morphological closing and opening are incorrect." <https://github.com/scikit-image/scikit-image/issues/6676> (accessed 2026-10-14)
15. SciPy source, release v1.18.1: `scipy/ndimage/_morphology.py`. <https://github.com/scipy/scipy/blob/v1.18.1/scipy/ndimage/_morphology.py> (accessed 2026-10-14)
16. MathWorks. "imdilate", "imerode", "imopen", "strel" and "imreconstruct." Image Processing Toolbox documentation, release R2026b. <https://www.mathworks.com/help/images/ref/imdilate.html> (accessed 2026-10-14)
17. OpenCV Python tutorials, commit 802cf95: "Morphological Transformations." <https://github.com/opencv/opencv/blob/802cf95aa3d42816995695bf68a86b3532f12760/doc/py_tutorials/py_imgproc/py_morphological_ops/py_morphological_ops.markdown> (accessed 2026-10-14)
