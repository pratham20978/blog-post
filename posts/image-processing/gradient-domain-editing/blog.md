---
title: "Gradient-Domain Editing: Poisson Cloning, HDR and Tiling"
slug: gradient-domain-editing
date: 2026-10-15
updated: 2026-10-15
summary: "Keep an image's gradients and its border, and a Poisson equation gives back every pixel. Cloning, HDR and seamless tiling, solved by hand on nine pixels."
tags: [algorithms, image-processing, poisson-image-editing, image-gradient, high-dynamic-range, multigrid, opencv]
category: algorithms
categories: [algorithms]
tier: L3
difficulty: advanced
series: image-processing
series_position: 14
prerequisites: ["the five-point Laplacian from part 2 of this series", "partial derivatives and the divergence of a vector field", "solving a small linear system"]
reading_minutes: 32
cover_image_url: "COVER"
cover_image_alt: "Twelve known frame pixels around nine question marks, an arrow labelled solve, and the frame with the nine pixels back, 255 at the impulse"
canonical_url: "https://canery.in/blogs/gradient-domain-editing"
---

> [!NOTE]
> **Insights** — Keep an image's gradients, throw its pixels away, and you can get the pixels back: the gradients inside a region and the values on its border fix every pixel inside, as the one solution of a Poisson equation. Gradient-domain editing changes one of the two and solves again. Poisson cloning (OpenCV's `seamlessClone`) takes the border from another image and spreads the mismatch inward as a smooth membrane; HDR compression shrinks the large gradients and solves for the nearest image; seamless tiling makes opposite borders agree. On the series' 5×5 patch the 3×3 interior is nine equations: three Gauss–Seidel sweeps from zero leave a 31-level error, one multigrid V-cycle leaves 15, and a sine transform, which is what OpenCV uses, leaves none.

**Level:** advanced · **You need:** *The Laplacian by Hand* (part 2 of this series) for the five-point stencil and its values on the patch, partial derivatives and the divergence of a vector field, and solving a small linear system · **Time:** ~32 min

This is part 14 of *Image Processing by Hand*, and the last of its spokes. Its one prerequisite is Part 2, *The Laplacian by Hand: Edges, Blobs, Pyramids, Sharpening*, which computed the five-point Laplacian on the patch and closed its section "Keeping the Laplacian instead of the pixels" by naming this post. <!-- L54 --> That section kept the Laplacian; this post solves for the pixels, edits them three ways, and maps the result onto what the libraries compute.

**Jump to:** [The problem](#the-problem) · [Worked example](#worked-example) · [Intuition](#intuition) · [Cloning](#what-does-a-clone-keep-and-what-does-it-give-up) · [Solvers](#why-is-the-solve-slow-and-what-makes-it-fast) · [HDR](#hdr-compression-which-gradients-shrink) · [Tiling](#seamless-tiling-making-opposite-edges-agree) · [The math](#the-math) · [Tooling map](#implementation-the-tooling-map) · [Limitations](#limitations-and-common-mistakes)

> [!IMPORTANT]
> Nothing in this post was run against an image. Every number is worked by hand on the series' 5×5 patch and cross-checked with plain Python using only `math` and `fractions`: exact Gauss–Seidel sweeps, elimination, the V-cycle, the sine-transform solve, and a line-by-line replay of OpenCV's `seamlessClone`. That check is not published. No OpenCV, MATLAB, SciPy or Luminance HDR call was executed: library behaviour comes from source read at pinned commits and releases and from vendor documentation. Figures 6 and 7 are plotted from closed forms. There are no timings or measured curves of our own; the few quoted are the authors', on their hardware.

## Why this matters

Paste a photographed object into another photograph and the cut shows, however carefully it was drawn. The two pictures were lit differently, so the values on either side of the cut disagree, and feathering only blurs the disagreement. Gradient-domain editing removes it by pasting differences instead of values, then solving for the values that fit the new surroundings. `cv2.seamlessClone` does it in one call. The same machinery squeezes a scene spanning 25,000:1 in light into a monitor spanning less than 100:1, <!-- L17 --> and makes a photographed texture repeat without a seam.

Each of these is a linear system with one unknown per pixel, and how it is set up and solved decides what you get. Clone a full-light object into a shadow and part of it goes below black. Stop a solver early and a soft bowl of error sits over the paste. Hand OpenCV a mask narrower than seven pixels and nothing is cloned at all. This post works out why, on nine pixels.

## The problem

An image's **gradient field** gives every pixel two numbers: the difference to its right-hand neighbour and the difference to the one below. On the patch, row r2 reads `40 255 40 200 200`, so its differences to the right are +215, −215, +160 and 0. **Gradient-domain editing** changes these differences rather than the pixels, then turns the edited field back into an image.

In one dimension that last step is a running sum. In two it is not, because a field of differences describes an image only if the differences along any two paths between the same two pixels add up to the same total. A field with that property is **integrable**, and an edited field almost never is. So the question becomes: which image has differences *closest* to the field, in the least-squares sense?

Two more pieces fix the answer. The **region** Ω is the set of pixels being solved for. Its **boundary** ∂Ω is the set of outside pixels that touch it, and their values are held fixed, which is called a **Dirichlet condition**. The field that the region's differences should match is the **guidance field** v. Minimising the squared mismatch gives one linear equation per pixel of Ω: four times the pixel minus its four neighbours must equal the guidance's version of the same quantity, its four guidance differences, pixel minus neighbour, added up. Any neighbour on the boundary moves to the right-hand side at its fixed value. <!-- L03 --> That is Part 2's five-point stencil used as a constraint instead of a filter. Its continuous form is the **Poisson equation** ∇²f = div v, where the **divergence** div v is the field's net outflow at a point. <!-- L01 --> With no guidance, v = 0, it becomes the **Laplace equation**, whose solution is the smoothest possible fill of the region, called the **membrane**.

Two things make it hard. There is one unknown per pixel, so a million-pixel region is a million coupled equations. And the simplest solvers remove quickly varying error fast and slowly varying error slowly, which is the wrong way round for a seamless edit, whose whole correction varies slowly.

## Worked example

Five steps: decide what is kept, write the nine equations, solve them by Gauss–Seidel, then by one multigrid V-cycle, and finally without iterating at all.

### Step 1: what is kept

Take Ω to be the nine pixels inside the patch's frame, rows r1 to r3 by columns c1 to c3. The frame's twelve pixels that touch Ω are the boundary: 40, 40 and 200 along the top and along the bottom, 40 down the left side, 200 down the right. The four corners touch nothing in Ω and play no part. For guidance, keep the patch's own differences. Along an edge from p to q the guidance is g_p − g_q, so each equation sees its pixel's four such differences summed, which is minus the Laplacian. On Ω that is Part 2's table: 215, 160 and −160 on r1; −860, 375 and −160 on r2; 215, 160 and −160 on r3. <!-- L54 --> Figure 1 shows what stays and what goes.

![The 5×5 patch with its 3×3 interior erased, the kept Laplacian printed in each erased cell, and the twelve frame pixels that touch it kept](FIG_01)

*Figure 1 — What gradient-domain editing keeps: twelve boundary values and nine Laplacians. The nine pixel values are thrown away. Worked by hand.*

### Step 2: nine equations

Number the unknowns row by row. At (r1, c1) the unknown neighbours are (r1, c2) and (r2, c1), and the known ones are the 40 above and the 40 to the left:

$$
4f_{11} - f_{12} - f_{21} = 80 - 215 = -135 .
$$

At the impulse, (r2, c1), only the 40 to its left is known, and its Laplacian is −860, so the right-hand side is 40 + 860 = 900. All nine equations form one system, Ax = b, in Figure 2. A has 4 on its diagonal and −1 wherever two unknowns are neighbours. The vector b is each pixel's sum of known neighbours, 80, 40, 400, 40, 0, 200, 80, 40 and 400 in row order, minus its Laplacian: −135, −120, 560, 900, −375, 360, −135, −120 and 560.

![The nine equations as a 9×9 matrix with 4 on the diagonal and −1 between neighbours, times the patch's nine pixels, equal to b](FIG_02)

*Figure 2 — The nine equations as one system. Each row of A is the five-point stencil with its known neighbours moved into b. Worked by hand.*

The patch satisfies every row: at the impulse, 4 × 255 − 40 − 40 − 40 = 900. A is symmetric and positive definite, so the system has exactly one solution, <!-- L03 --> and the nine pixels thrown away come back. The round trip is exact only because the guidance is made of the stencil's own differences; take the gradient by central differences instead and the recovered image comes out close to the original but not equal. <!-- L21 -->

### Step 3: three Gauss–Seidel sweeps

**Gauss–Seidel** is the simplest way to solve such a system: visit the unknowns in order and set each one to its b plus the current values of its unknown neighbours, divided by 4. One pass over all nine is a **sweep**. Throw the pixels away literally and start from zero. The first update is f₁₁ = −135/4 = −33.75. The second uses it at once: f₁₂ = (−120 − 33.75)/4 = −38.44. The rest of the first sweep gives 130.39, 216.56, −49.22, 110.29, 20.39, −37.21 and 158.27. Values below zero are no cause for alarm: until the solve converges the numbers are not an image.

Figure 3 tracks the error, the iterate minus the patch. Its largest entry falls from 255 to 89.7, then 62.1, then 31.1 after three sweeps. The error also changes shape. At the start it jumps by up to 215 between neighbours, and only 56% of its energy lies in the smoothest pattern it could have, one broad bowl over all nine pixels. After the first sweep that share is 92%, after the second 97%: the sweeps strip out the part that jumps from pixel to pixel and leave a bowl, deepest at the centre (−62.1 after the second sweep) and shallowest in a corner (−16.9). From the third sweep on, the bowl halves each time, to 15.5, 7.8, 3.9, 1.9 and 0.97, and only after nine sweeps does rounding give the right 8-bit answer everywhere.

![Four 3×3 iterates and their errors, zero and three Gauss–Seidel sweeps; the largest error falls 255, 89.7, 62.1, 31.1 into a bowl](FIG_03)

*Figure 3 — Three sweeps from zero. The first two strip the error that jumps between neighbours and leave a bowl; from then on the bowl halves per sweep. Worked by hand.*

### Step 4: one V-cycle

**Multigrid** removes the smooth error where it is no longer smooth: on a coarser grid. Here the coarser grid has a single point, the centre, because a 5×5 grid with its frame halves to a 3×3 one. One **V-cycle** goes down and back up: <!-- L29 -->

1. *Pre-smooth.* One Gauss–Seidel sweep: the first sweep above.
2. *Residual.* What the equations still lack, r = b − Ax: 178.1, 81.2 and 110.3; −28.8, 73.1 and 158.3; −37.2, 158.3 and 0.
3. *Restrict.* Average the residual onto the centre by **full weighting**: weight 4 at the centre, 2 on the edges and 1 at the corners, over 16. That gives 80.1. <!-- L30 -->
4. *Coarse solve.* The coarse grid's equation is the fine one seen through the trip down and back up: restriction times A times interpolation. On one point that is 3/4, not the 1 that writing the stencil afresh on the coarse grid would give; in two dimensions the two choices differ. <!-- L30 --> So the coarse correction is 80.1/0.75 = 106.8.
5. *Prolong.* Interpolate the correction back bilinearly, which is four times the transpose of full weighting: 106.8 at the centre, 53.4 on the edges, 26.7 at the corners. <!-- L30 --> Add it.
6. *Post-smooth.* One more sweep.

The largest error is now 15.4, against 31.1 after three plain sweeps: about the same work, two sweeps and a one-number solve, for half the error. A second cycle leaves 0.82. Figure 4 lays the cycle out.

![One V-cycle: a sweep, the residual, its average 80.1 on one coarse point, the solve 106.8, interpolation back, a sweep; error 15.4](FIG_04)

*Figure 4 — One V-cycle on nine unknowns. The coarse point removes the bowl that the sweeps could only shave. Worked by hand.*

### Step 5: no iteration at all

On a rectangle the system can be solved outright. The **discrete sine transform** (DST) rewrites any 3×3 array as a sum of the patterns sin(πkr/4) sin(πlc/4), for k and l from 1 to 3, and in that basis A is diagonal. Its nine entries are 4 − 2cos(kπ/4) − 2cos(lπ/4): 1.172 for the smoothest pattern, k = l = 1, up to 6.828 for the roughest. <!-- L25 --> Transform b, divide each of its nine coefficients by its entry, transform back, and out comes the patch, exactly. The three coefficients with k = 2 are zero: that pattern is odd about the middle row, and rows r1 and r3 of b are equal. This is how OpenCV solves it, as the tooling map shows.

The smallest entry explains step 3. A Jacobi sweep, which updates every unknown from the previous sweep's values, multiplies the smoothest pattern's error by 1 − 1.172/4 = 0.707. <!-- L26 --> Gauss–Seidel squares that factor to 0.5, <!-- L27 --> the halving seen from the third sweep on.

## Intuition

Picture the boundary as a wire frame and the solution with no guidance as a soap film stretched across it: every point of the film sits at the average of its neighbours, which is what ∇²f = 0 says on the grid. Guidance adds wrinkles that the film must carry; with the patch's own differences, the wrinkles are the step and the spike. Cloning keeps the wrinkles and stretches the film over a different frame. The film takes up the difference between the two frames smoothly, and the wrinkles ride on top. That is why the seam disappears: across it nothing changes but a slow gradient, which the eye barely notices. <!-- L10 -->

The picture breaks in two places. A soap film never leaves the range of its frame, but a wrinkled one can: the spike rides on the film and can be pushed past 255 or below 0. And a film knows nothing about the picture under it, so a frame drawn across an edge of the destination smears that edge inward.

The same picture explains the slow sweeps. A sweep moves information one pixel at a time. Rough error is local, so a sweep or two of neighbours cancel it. A smooth bowl needs the same correction everywhere at once, and each sweep shaves only a little off it, less the wider the region. On a grid with half the points per side the bowl looks twice as rough, and a sweep there cuts it the way the rough error was cut above.

## What does a clone keep, and what does it give up?

### The correction is a membrane

**Seamless cloning**, in Pérez, Gangnet and Blake's formulation, takes the guidance from a source image g, v = ∇g, and the boundary values f* from the destination. They write the result as the source plus a correction, f = g + h. The correction h has no guidance of its own, so it is the membrane spanning the *mismatch* f* − g around the frame. <!-- L02 --> If the destination's frame is the patch's own frame darkened by 60 levels, the mismatch is −60 everywhere, the membrane is flat at −60, and the clone is the patch moved down by 60: −20, −20 and 140 on the outer rows, 195, −20 and 140 in the middle. Its shape is unchanged and nothing marks the seam. The −20s are already a warning.

### A change of light is not a difference

Now clone into the shadowed copy that Part 11, *Thresholding and Segmentation: Otsu, Sauvola, Watershed*, set beside the patch: the same scene at a fifth of the light, which reads 8 where the patch reads 40, 40 where it reads 200, and 51 for the impulse. <!-- L55 --> The mismatch is −32 on the dark side of the frame and −160 on the bright side. The membrane interpolates between them: −46.9, −72 and −129.1 across the outer rows, −51.4, −80 and −124.6 across the middle. Added to the patch, it gives −6.9, −32 and 70.9 on the outer rows and 203.6, −40 and 75.4 in the middle. The step still rises 102.9 between c2 and c3 and the spike stands 243.6 above its neighbour, where a fifth of the light would give 32 and 43. The clone kept most of its full-light differences, and its dark side went below black to make room for them. Clamped to 0–255 and truncated, as OpenCV stores it, it reads 0, 0 and 70 above 203, 0 and 75.

The fix is to clone the logarithm. In log, a fifth of the light is a constant, −ln 5, so the mismatch is −ln 5 all round the frame, the membrane is flat, and the clone, exponentiated, is exactly 8, 8 and 40 above 51, 8 and 40: the shadowed patch. Poisson cloning keeps differences, a change of light is a ratio, and the logarithm turns ratios into differences. Fattal's tone mapping works in log for that reason, <!-- L11 --> and Pérez's illumination tool works there too. <!-- L08 --> Figure 5 sets these fills beside the membrane alone, which loses the spike and spreads the step across the hole as 58.6, 90 and 161.4.

![Four fills of the patch's interior: the membrane, guided by the patch, cloned into the shadowed copy in codes with negatives, and in log](FIG_05)

*Figure 5 — Four fills of one hole. The guided fill keeps the patch's differences; in codes those differences overshoot a darker frame, in log they fit it. Worked by hand.*

### Mixing gradients, and where the frame goes

The membrane carries any disagreement along the frame into the clone. Jia and colleagues observed that Poisson editing works well only when the salient structures of source and destination do not conflict along the boundary, and moved the boundary to where they agree, along a shortest closed path. <!-- L34 --> Pérez and colleagues offered **mixed gradients** instead: on each edge between two pixels, keep the destination's difference where its magnitude exceeds the source's, and the source's otherwise. That stops a destination object touching the region from bleeding into it, and lets a transparent or holed object keep the texture behind it. <!-- L05 --> A third mode, **monochrome transfer**, turns the source grey first, so that only its pattern of light comes across. <!-- L06 -->

## Why is the solve slow, and what makes it fast?

### Gauss–Seidel's rate

On an N × N region with a fixed frame, the smoothest error pattern shrinks by cos²(π/(N + 1)) per Gauss–Seidel sweep, the square of a Jacobi sweep's factor. <!-- L25 --> <!-- L27 --> At N = 3 that is the 0.5 of step 3. At N = 1,023 it is 0.9999906, and one decimal digit of accuracy takes 244,633 sweeps. The count grows as the square of the width, about 0.233 (N + 1)². Brandt put it the same way in 1977: plain relaxation converges at 1 − O(h²) per sweep, so it needs O(h⁻²) sweeps per digit, h being the grid spacing. <!-- L33 --> Figure 6 plots the closed forms.

![Log–log curves of sweeps per digit against region width: Gauss–Seidel from 3.3 at width 3 to 244,633 at 1,023; optimal SOR 375](FIG_06)

*Figure 6 — Sweeps per decimal digit of accuracy. Plain sweeps grow with the square of the width, over-relaxed ones with the width. Plotted from the closed forms; the error is the smoothest pattern's.*

**Successive over-relaxation** (SOR), which Pérez and colleagues used, moves each unknown ω times as far as Gauss–Seidel would. With the best ω, 2/(1 + sin(π/(N + 1))), <!-- L28 --> the square becomes a first power: 375 sweeps per digit at N = 1,023. Their reported cost was 0.4 s for a 60,000-pixel disc on a Pentium 4, with SOR or with V-cycle multigrid. <!-- L04 -->

### Multigrid, transforms and fewer unknowns

Multigrid gives each grid the error it handles well. A Gauss–Seidel sweep shrinks every rough pattern by at least half, so three sweeps cut the rough error almost tenfold; <!-- L33 --> the coarser grids take the rest. Each coarser grid has a quarter of the points, so a V-cycle costs the fine grid's sweeps plus a quarter, a sixteenth and so on of them, 4/3 in all. <!-- L31 --> Brandt's method solved n equations in O(n) operations, about 40n additions and shifts for a Poisson problem. <!-- L32 --> A GPU multigrid integrates megapixel gradient fields at over 20 frames a second, and a streaming one tone-maps gigapixel images in about an hour on a notebook. <!-- L36 -->

On a rectangle, fast transforms solve the system directly, <!-- L38 --> in O(n log n): step 5 at scale. Fattal and colleagues name this as the alternative to their multigrid. <!-- L16 --> Compositing needs even less. Agarwala noticed that the correction to a plain colour copy is smooth away from the seams, so it needs few unknowns there. A **quadtree**, a grid of squares split finer only near the seams, cut them to 0.38–0.94% of the pixels, with colours at most two levels from the full solution after rounding. <!-- L19 --> <!-- L20 --> Farbman and colleagues went further and computed the membrane at each pixel as a weighted sum of the frame's values, using mean-value coordinates, with no system at all. <!-- L35 -->

## HDR compression: which gradients shrink?

### Ratios, in log

A **high-dynamic-range** (HDR) image stores light over a range far wider than a display's. Fattal, Lischinski and Werman's lobby spanned about 25,000:1 and a streetlight at night over 100,000:1, against a monitor's range, typically below 100:1. <!-- L17 --> **Tone mapping** squeezes such a range into the display's. Their idea was to squeeze the gradients rather than the values: work on H, the logarithm of luminance, where a difference is a ratio of light; <!-- L11 --> shrink the large differences more than the small ones; and solve for the image. <!-- L13 -->

The shrink is an **attenuation factor** φ per pixel, set by the gradient's magnitude there:

$$
\varphi = \left(\frac{\lVert\nabla H\rVert}{\alpha}\right)^{\beta - 1},
$$

where α is 0.1 times the image's average gradient magnitude and β lies between 0.8 and 0.9. Gradients larger than α shrink and smaller ones grow slightly. <!-- L14 --> The paper builds φ on every level of a Gaussian pyramid whose coarsest level is at least 32 pixels wide; the patch is smaller than that, so here φ has one level.

### The step row

On the step row, H rises by ln 5 = 1.609 between c2 and c3 and is flat elsewhere. Central differences put half of that, 0.805, on c2 and c3 and nothing on the other three pixels, so the average magnitude is 0.322 and α is 0.0322: the step sits at exactly 25α. At β = 0.85, φ = 25^−0.15 = 0.617. The step's log rise becomes 0.993, and a 5:1 step becomes 2.70:1, while the flat runs stay flat. In one dimension the shrunken differences add up directly. <!-- L12 --> Figure 7 draws φ for the three values of β.

![Fattal's factor against gradient size in units of alpha for beta 0.8, 0.85, 0.9; the step at 25 alpha keeps 0.617 at 0.85](FIG_07)

*Figure 7 — Gradients above α shrink, those below it grow slightly. The step row's step, at 25α, keeps 0.617 of its log size at β = 0.85: 5:1 becomes 2.70:1. Plotted from the closed form.*

### A square that does not close

In two dimensions the differences do not add up. The impulse sits two columns from the step, and at (r2, c2) the central difference spans from 255 to 200 instead of from 40 to 200: 0.12 instead of 0.805. The patch's average magnitude is now 0.406 and α is 0.0406, so φ at (r2, c2) is 0.848 against 0.639 at (r1, c2). Row r2's step is squeezed less than row r1's: its log rise becomes 1.365, a 3.92:1 step, against 1.028 and 2.80:1 above it. Down columns c2 and c3, from r1 to r2, the vertical differences are zero. Go round that square, right along r1, down c3, left along r2 and up c2, and the differences sum to −0.337 instead of zero (Figure 8). No image has these differences.

![One square of the patch after attenuation: 1.028 along row r1, 1.365 along row r2, 0 up both columns; the loop sums to −0.337](FIG_08)

*Figure 8 — The attenuated field is no image's gradient. Around one square of the patch its differences sum to −0.337, so least squares must split the disagreement. Worked by hand.*

So the method asks for the image whose gradient is nearest in least squares, which satisfies ∇²I = div G for the attenuated field G. <!-- L13 --> At the image's edge it uses a **Neumann condition**, zero derivative across the edge, which fixes the answer only up to a constant; the result is shifted and scaled to the display. <!-- L15 --> The gradient is taken by forward differences and the divergence by backward ones, matching the five-point stencil, and the solve is a full multigrid with Gauss–Seidel smoothing. <!-- L16 -->

The impulse itself shows the formula's blind spot. Central differences skip the centre pixel, so at a lone spike they read zero, and φ, a negative power of the magnitude, is unbounded. Luminance HDR's open implementation floors the magnitude at 10⁻⁴ and adds a noise term. <!-- L37 --> With the floor alone, φ at the spike is 2.46 on the patch, so the steepest differences in the patch, the spike's two log differences of −1.852 to its right and below, become −4.56: magnified instead of compressed.

## Seamless tiling: making opposite edges agree

Repeat the step row and every seam jumps from 200 back down to 40: a 160-level edge every five pixels. Pérez and colleagues made a rectangle **tileable** by giving opposite sides identical boundary values, the average of the two, and solving inside with the original differences as guidance. <!-- L09 --> On the step row both ends become 120. In one dimension the membrane is a straight line, here from +80 at c0 to −80 at c4, and the row becomes 120, 80, 40, 160 and 120. Tiled, the seam reads 120 against 120 (Figure 9).

![The step row tiled three times, before with a 160 jump at each seam, after Pérez's rule as 120 80 40 160 120 with no jump](FIG_09)

*Figure 9 — The averaging rule moves the seam's 160 into a slope across the tile. Over five pixels the slope is 40 a pixel and the step shrinks to 120. Worked by hand.*

The price shows in the numbers: the step shrinks from 160 to 120, and the flat runs now fall by 40 a pixel. Over a large texture the same 160 would spread across hundreds of pixels and the slope would be invisible; over five it is not. On the patch's 3×3 interior, with its top and bottom rows unchanged, the same rule lifts the spike to 289.3, which an 8-bit image cannot hold.

## The math

| Symbol | Meaning |
|---|---|
| $\Omega$, $\partial\Omega$ | the pixels solved for; the outside pixels that touch them |
| $f$, $f^*$, $g$ | the result; the destination, fixed on $\partial\Omega$; the source |
| $\mathbf v$, $v_{pq}$ | the guidance field; its value along the edge from $p$ to $q$ |
| $N_p$ | the four neighbours of $p$ |
| $h$ | the correction $f - g$ |
| $\rho$ | an iteration's per-sweep factor on the slowest error |
| $R$, $P$, $A_c$ | restriction, prolongation, the coarse operator |
| $H$, $\varphi$, $\alpha$, $\beta$ | log luminance; Fattal's factor and its two parameters |

**Least squares and the Poisson equation.** <!-- L01 -->

$$
\min_f \iint_\Omega \lVert \nabla f - \mathbf v\rVert^2 \ \text{ with } f = f^* \text{ on } \partial\Omega
\quad\Longleftrightarrow\quad
\nabla^2 f = \operatorname{div}\mathbf v \ \text{ in } \Omega \tag{1}
$$

The minimiser satisfies the Euler–Lagrange equation of the left side, which is the Poisson equation on the right; with v = 0 it is the membrane.

**The discrete equations.** <!-- L03 -->

$$
\lvert N_p\rvert\, f_p - \sum_{q \in N_p \cap \Omega} f_q = \sum_{q \in N_p \cap \partial\Omega} f^*_q + \sum_{q \in N_p} v_{pq} \tag{2}
$$

One equation per pixel of Ω, with four neighbours away from the image's edge. With imported gradients, $v_{pq} = g_p - g_q$, the last sum is minus the Laplacian of g, which is why b in step 2 is the boundary sums minus the Laplacian.

**The correction.** <!-- L02 -->

$$
f = g + h, \qquad \nabla^2 h = 0 \ \text{ in } \Omega, \qquad h = f^* - g \ \text{ on } \partial\Omega \tag{3}
$$

For the shadowed copy, h runs from −46.9 to −129.1 across the hole, and g + h is the clone in codes worked above.

**Gauss–Seidel and its rate.** Each update is $f_p \leftarrow \big(b_p + \sum_{q \in N_p \cap \Omega} f_q\big)/4$, newest values first. On an N × N region the error patterns $\sin(\pi k r/(N+1))\sin(\pi l c/(N+1))$ have eigenvalues <!-- L25 -->

$$
\lambda_{kl} = 4 - 2\cos\frac{k\pi}{N+1} - 2\cos\frac{l\pi}{N+1}, \qquad \rho_{\mathrm{GS}} = \cos^2\frac{\pi}{N+1} \tag{4}
$$

and a Jacobi sweep multiplies each by $1 - \lambda_{kl}/4$, whose largest value, $\cos(\pi/(N+1))$, Gauss–Seidel squares. <!-- L27 --> Sweeps per digit are $\ln 10 / (-\ln\rho) \approx (\ln 10/\pi^2)(N+1)^2 = 0.233\,(N+1)^2$: 3.3 for the patch's N = 3.

**The coarse equation.** With bilinear interpolation P and full weighting $R = P^{\mathsf T}/4$, the coarse operator is $A_c = RAP$. <!-- L30 -->

<details>
<summary>Why it is 3/4 on the patch</summary>

P carries one coarse value to the nine fine points with weights 1/4 at the corners, 1/2 on the edges and 1 at the centre. Applying A to that pattern gives 0 at the corners, 4 × 1/2 − 1/4 − 1/4 − 1 = 1/2 on each edge, and 4 − 4 × 1/2 = 2 at the centre. R averages it back with weights 1/16, 1/8 and 1/4: 4 × 1/8 × 1/2 + 1/4 × 2 = 3/4. Writing the stencil afresh with spacing 2 instead gives 4/2² = 1, and the V-cycle with it leaves an error of 27.1 rather than 15.4.

</details>

**Fattal's attenuation.** <!-- L14 --> <!-- L13 -->

$$
\varphi = \left(\frac{\lVert\nabla H\rVert}{\alpha}\right)^{\beta - 1}, \qquad G = \varphi\, \nabla H, \qquad \nabla^2 I = \operatorname{div} G \tag{5}
$$

On the step row, $\lVert\nabla H\rVert = 25\alpha$, so $\varphi = 25^{\beta-1}$: 0.525, 0.617 and 0.725 for β of 0.8, 0.85 and 0.9.

## Implementation: the tooling map

Every entry below maps to a section above. **None of it was executed for this post**; it comes from source at pinned commits and releases and from vendor documentation. Figure 10 is the same map in one picture.

![Tooling map: OpenCV seamlessClone, illuminationChange, textureFlattening, TonemapMantiuk; MATLAB regionfill; SciPy solvers](FIG_10)

*Figure 10 — Where each piece lives. OpenCV solves rectangles directly and departs from the paper in four places, marked; SciPy leaves the assembly to you.*

### OpenCV's photo module

| Want | Call | What it computes |
|---|---|---|
| Poisson cloning | `cv2.seamlessClone(src, dst, mask, p, cv2.NORMAL_CLONE)` | region: the mask's bounding rectangle; boundary: that rectangle's frame in `dst`; guidance: forward differences of `src` inside the mask and of `dst` outside it; solved by a sine transform <!-- L40 --> <!-- L41 --> <!-- L43 --> |
| mixed gradients | `cv2.MIXED_CLONE` | keeps the source's pair of differences where abs(gx − gy) is larger, not where each edge's magnitude is <!-- L45 --> |
| monochrome transfer | `cv2.MONOCHROME_TRANSFER` | the source turned grey before its differences are taken <!-- L46 --> |
| illumination change | `cv2.illuminationChange(src, mask, alpha=0.2, beta=0.4)` | Pérez's attenuation applied to the codes, not in log, with α a fixed number rather than a fraction of the mean gradient <!-- L49 --> |
| texture flattening | `cv2.textureFlattening(src, mask, 30, 45, 3)` | Pérez's texture flattening: keeps differences only where Canny marks an edge <!-- L07 --> <!-- L50 --> |
| HDR tone mapping | `cv2.createTonemapMantiuk()` | Mantiuk and colleagues' contrast framework, reconstructed by at most 100 iterations of conjugate gradients, an iterative solver for symmetric systems; OpenCV has no Fattal operator <!-- L51 --> <!-- L39 --> |

`seamlessClone` departs from the paper in four places. First, the region is the mask's whole bounding rectangle, so pixels outside the mask but inside the rectangle are solved too and take part of the membrane; the paper's form leaves everything outside Ω untouched. <!-- L22 --> Second, once the mask image's outer frame has been cleared, the mask is eroded three times by a 3×3 square, one 7×7 erosion in effect, before any source difference is used. <!-- L42 --> <!-- L40 --> A mask must therefore be seven pixels across before a single source difference counts. The 5×5 patch with a full mask clones nothing: cleared to 3×3, then eroded away, it leaves the destination unchanged, give or take the truncation below. The erosion is issue #17450, open since 2020. Third, `MIXED_CLONE` compares abs(gx − gy): at the impulse both forward differences are 40 − 255 = −215, so the comparison sees 0 and the spike's own differences never win. Fourth, results are clamped to 0–255 and truncated, not rounded, so a value that should be 40 can be stored as 39. <!-- L44 -->

Two more details matter in practice. Without a `_WIDE` flag, `p` is the centre of the mask's bounding rectangle in `dst`, while the documentation describes it as the centre of the source image; the `_WIDE` flags, added in 4.11.0, make the code match that description. <!-- L47 --> And from 4.11.0 a single-channel mask is no longer copied: the call clears its frame, erodes it and inverts it in place, in the caller's own array. The 2018 fix for the same complaint, issue #12053, was undone by the pull request that added the `_WIDE` flags, and `colorChange`, `illuminationChange` and `textureFlattening`, which share the code, erode and invert their masks the same way. <!-- L48 --> <!-- L56 --> Everything else above is the same in 4.10.0, 4.14.0 and 5.0.0.

### MATLAB and SciPy

| Want | Call | Note |
|---|---|---|
| membrane fill | `regionfill(I, mask)` | the Laplace equation with Dirichlet values from the region's outer boundary; MATLAB since R2015a <!-- L52 --> |
| any Poisson system | `scipy.sparse` and `scipy.sparse.linalg.spsolve` | assemble equation (2) yourself, one row per pixel of Ω |
| a rectangle, directly | `scipy.fft.dstn(b, type=1)` and `idstn` | step 5 at any size <!-- L53 --> |

### The worked example in SciPy

```python
import numpy as np
from scipy.fft import dstn, idstn

b = np.array([[-135, -120, 560],
              [ 900, -375, 360],
              [-135, -120, 560]], float)    # boundary sums minus the Laplacian (Figure 2)
c = np.cos(np.arange(1, 4) * np.pi / 4)
lam = 4 - 2 * c[:, None] - 2 * c[None, :]    # A's nine eigenvalues, 1.172 to 6.828
x = idstn(dstn(b, type=1) / lam, type=1)    # [[40, 40, 200], [255, 40, 200], [40, 40, 200]]
```

This was not run for this post. The comments state what the worked example predicts.

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** cloning across a change of light in pixel values. Poisson cloning keeps differences, so a full-light object pasted into shadow keeps its full-light contrast and is pushed below black to fit: the patch cloned into its fifth-light copy reads −40 at (r2, c2). Clone the logarithm, or bring the source to the destination's level first.

- **Results outside 0–255.** The solve keeps differences, not range: the shadow clone reaches −40 and the tiled spike 289.3. OpenCV clamps and truncates; IPOL's implementation, for its contrast edits, renormalises the whole result instead, which keeps the detail but moves every level. <!-- L24 -->
- **Stopping the solver early.** Three sweeps leave a 31-level error, and it is a smooth bowl: exactly the slow gradient a seamless edit hides, so it reads as a lighting change rather than as an error. Iterate to a tolerance, or use multigrid or a transform.
- **Thin masks in OpenCV.** A stroke narrower than seven pixels clones nothing, because of the erosion. <!-- L42 --> Since 4.11.0 the mask is also changed in place, so pass a copy if you reuse it. <!-- L48 -->
- **Where `p` lands.** Without a `_WIDE` flag it is the centre of the mask's bounding rectangle, not of the source image. <!-- L47 -->
- **`MIXED_CLONE` on spikes and diagonals.** Its abs(gx − gy) test discards every source gradient whose two components are equal: a one-pixel spike's own, or a 45° edge's. <!-- L45 -->
- **A frame across an edge.** The membrane smears a destination edge that crosses the boundary into the clone. Move the boundary, <!-- L34 --> or mix gradients. <!-- L05 -->
- **Fattal's factor at spikes.** Central differences read zero at a lone hot pixel, so floor the magnitude or remove such pixels first; otherwise the spike is magnified. <!-- L37 -->

## Key takeaways

- **Gradients plus a border are the image.** The patch's nine interior pixels come back, uniquely, from their Laplacian and the twelve values around them: the system is symmetric and positive definite.
- **A clone is the source plus a membrane.** The correction is the smoothest fill of the mismatch around the frame. It hides a seam when the mismatch is smooth, and it keeps differences, so clone across a change of light in log.
- **Edited fields need least squares.** Fattal's attenuation leaves a field whose loops do not close, −0.337 around one square of the patch, so the solve finds the nearest image through ∇²I = div G.
- **Gauss–Seidel kills rough error and keeps smooth error.** Its slowest factor is cos²(π/(N + 1)): 3.3 sweeps per digit on nine pixels, 244,633 on a 1,023-wide square. Multigrid, transforms or fewer unknowns fix it.
- **`seamlessClone` is not the paper.** A sine-transform solve over the bounding rectangle, a mask eroded by three pixels, an abs(gx − gy) mixing test, truncation, and from 4.11.0 a mask edited in place.

## Try it yourself

The exercises are pen and paper, matching the post; each names its rung.

### E1 — Reproduce: one equation, one update

Write the equation at (r2, c3) and check that the patch satisfies it. Then do the third update of the first Gauss–Seidel sweep, at (r1, c3).

**Self-check:** a right-hand side of 360, and an update of 130.39.

<details><summary>Answer</summary>

The unknown neighbours of (r2, c3) are (r1, c3), (r3, c3) and (r2, c2); the 200 to its right is known. Its Laplacian is −160, so b = 200 + 160 = 360, and with the patch, 4 × 200 − 200 − 200 − 40 = 360. The third update uses the second one at once: f₁₃ = (560 + f₁₂ + f₂₃)/4 = (560 − 38.44 + 0)/4 = 130.39.

</details>

### E2 — Inspect: is the error smooth?

From Figure 3, read the errors after the second sweep, say what shape they make and how it differs from the starting error, and predict roughly what the fourth sweep leaves.

**Self-check:** a shape, and a number within a factor of two of the worked value.

<details><summary>Answer</summary>

A bowl: −62.1 at the centre, −32.9 to −47.0 on the edges, −16.9 to −34.2 at the corners, with neighbours a few tens apart. The starting error, minus the patch, jumped by 215 between (r2, c1) and its neighbours. From the third sweep on, the largest error halves per sweep, ρ = cos²(π/4) = 0.5, so the fourth sweep leaves about half of 31.1. The worked value is 15.5.

</details>

### E3 — Predict: a gentler exponent

Predict the step row's tone-mapped ratio at β = 0.9 instead of 0.85, with α unchanged, and say which way it moves and why.

**Self-check:** a ratio between 2.70:1 and 5:1, with the reason.

<details><summary>Answer</summary>

φ = 25^(0.9 − 1) = 25^−0.1 = 0.725, so the log rise becomes 1.609 × 0.725 = 1.166, and e^1.166 = 3.21: a 3.21:1 step. A β closer to 1 brings φ closer to 1 for every gradient, and β = 1 would leave the image unchanged.

</details>

### E4 — Diagnose: the dimmed spike

A colleague takes the patch's left three columns, a lone 255 on 40, pads them with their edge value to 15 × 15 so that the spike sits in the middle, and clones them into a flat field of 40 with `cv2.seamlessClone` and a full mask. `NORMAL_CLONE` brings the 255 back. `MIXED_CLONE` returns about 147 at the spike, about 1 just left of it and just above it, and about 78 just right of it and just below. Find the cause, the observation that proves it, and a fix.

**Self-check:** the cause in the code, the spike's two differences, and a fix that keeps mixing.

<details><summary>Answer</summary>

`MIXED_CLONE` keeps the source's differences at a pixel only where abs(gx − gy) is larger than the destination's. At the spike both forward differences are 40 − 255 = −215, so abs(gx − gy) is 0, which never beats the flat field's 0: the spike's own two differences are replaced by zeros. Its neighbours to the left and above keep their +215. The field now climbs into the spike and never comes down, its loops no longer close, and the least-squares solve spreads the mismatch: the spike drops, its right and lower neighbours rise, and its left and upper ones fall. Fix: `NORMAL_CLONE` here, or Pérez's rule, which compares each edge's magnitudes, 215 against 0, and keeps the spike.

</details>

## References

1. Pérez, P., Gangnet, M., and Blake, A. "Poisson Image Editing." *ACM Transactions on Graphics* 22(3):313–318, 2003. doi:10.1145/882262.882269. [Author copy](http://www.irisa.fr/vista/Papers/2003_siggraph_perez.pdf)
2. Fattal, R., Lischinski, D., and Werman, M. "Gradient Domain High Dynamic Range Compression." *ACM Transactions on Graphics* 21(3):249–256, 2002. doi:10.1145/566654.566573. [Authors' copy](https://www.cs.huji.ac.il/~danix/hdr/hdrc.pdf)
3. Agarwala, A. "Efficient Gradient-Domain Compositing Using Quadtrees." *ACM Transactions on Graphics* 26(3), article 94, 2007. doi:10.1145/1276377.1276495. [Author's preprint](https://agarwala.org/efficient_gdc/preprint.pdf)
4. Di Martino, J. M., Facciolo, G., and Meinhardt-Llopis, E. "Poisson Image Editing." *Image Processing On Line* 6:300–325, 2016. [doi:10.5201/ipol.2016.163](https://doi.org/10.5201/ipol.2016.163)
5. Saad, Y. *Iterative Methods for Sparse Linear Systems*, 2nd edition, SIAM, 2003, §4.2 and chapter 13. doi:10.1137/1.9780898718003. [Author's copy](https://www-users.cse.umn.edu/~saad/IterMethBook_2ndEd.pdf)
6. Brandt, A. "Multi-Level Adaptive Solutions to Boundary-Value Problems." *Mathematics of Computation* 31(138):333–390, 1977. [doi:10.1090/S0025-5718-1977-0431719-X](https://doi.org/10.1090/S0025-5718-1977-0431719-X)
7. Jia, J., Sun, J., Tang, C.-K., and Shum, H.-Y. "Drag-and-Drop Pasting." *ACM Transactions on Graphics* 25(3):631–637, 2006. [doi:10.1145/1141911.1141934](https://doi.org/10.1145/1141911.1141934)
8. Farbman, Z., Hoffer, G., Lipman, Y., Cohen-Or, D., and Lischinski, D. "Coordinates for Instant Image Cloning." *ACM Transactions on Graphics* 28(3), article 67, 2009. [doi:10.1145/1531326.1531373](https://doi.org/10.1145/1531326.1531373)
9. McCann, J., and Pollard, N. S. "Real-Time Gradient-Domain Painting." *ACM Transactions on Graphics* 27(3), article 93, 2008. [doi:10.1145/1360612.1360692](https://doi.org/10.1145/1360612.1360692)
10. Kazhdan, M., and Hoppe, H. "Streaming Multigrid for Gradient-Domain Operations on Large Images." *ACM Transactions on Graphics* 27(3), article 21, 2008. [doi:10.1145/1360612.1360620](https://doi.org/10.1145/1360612.1360620)
11. Simchony, T., Chellappa, R., and Shao, M. "Direct Analytical Methods for Solving Poisson Equations in Computer Vision Problems." *IEEE Transactions on Pattern Analysis and Machine Intelligence* 12(5):435–446, 1990. [doi:10.1109/34.55103](https://doi.org/10.1109/34.55103)
12. Mantiuk, R., Myszkowski, K., and Seidel, H.-P. "A Perceptual Framework for Contrast Processing of High Dynamic Range Images." *ACM Transactions on Applied Perception* 3(3):286–308, 2006. [doi:10.1145/1166087.1166095](https://doi.org/10.1145/1166087.1166095)
13. OpenCV source, commit 802cf95: `photo/src/seamless_cloning.cpp`, `seamless_cloning_impl.cpp`, `tonemap.cpp`, `photo.hpp` and `imgproc/src/morph.dispatch.cpp`. <https://github.com/opencv/opencv/blob/802cf95aa3d42816995695bf68a86b3532f12760/modules/photo/src/seamless_cloning_impl.cpp> (accessed 2026-10-15)
14. OpenCV source, tags 4.10.0 to 4.14.0 and 5.0.0. <https://github.com/opencv/opencv/blob/4.14.0/modules/photo/src/seamless_cloning.cpp> (accessed 2026-10-15)
15. OpenCV issues #17450, #12053 and #21902, and pull request #26511. <https://github.com/opencv/opencv/issues/17450> (accessed 2026-10-15)
16. MathWorks. "regionfill." Image Processing Toolbox documentation, release R2026b. <https://www.mathworks.com/help/images/ref/regionfill.html> (accessed 2026-10-15)
17. Luminance HDR source, commit 764fb83: `tmo_fattal02.cpp`. <https://github.com/LuminanceHDR/LuminanceHDR/blob/764fb83683c03385b1986a8b6da3122a24798d68/src/TonemappingOperators/fattal02/tmo_fattal02.cpp> (accessed 2026-10-15)
18. SciPy 1.18.0 documentation, `scipy.fft.dstn`. <https://docs.scipy.org/doc/scipy/reference/generated/scipy.fft.dstn.html> (accessed 2026-10-15)
