---
title: "The Structure Tensor: Harris, Shi–Tomasi, and Optical Flow"
slug: the-structure-tensor
date: 2026-10-12
updated: 2026-10-12
summary: "Corner detectors and Lucas–Kanade optical flow solve with one 2×2 matrix. Worked by hand on a 5×5 patch: eigenvalues, Harris's k, the aperture problem."
tags: [algorithms, image-processing, structure-tensor, corner-detection, optical-flow, lucas-kanade, opencv]
category: algorithms
categories: [algorithms]
tier: L4
difficulty: advanced
series: image-processing
series_position: 9
prerequisites: ["the Sobel gradient and the shared 5×5 patch from part 1 of this series", "eigenvalues of a symmetric 2×2 matrix", "linear least squares"]
reading_minutes: 36
cover_image_url: "COVER"
cover_image_alt: "A 5×5 grid split by a vertical step with one bright pixel, and three ellipses over it: a flat line, a narrow ellipse and a round one"
canonical_url: "https://canery.in/blogs/the-structure-tensor"
---

> [!NOTE]
> **Insights** — The structure tensor is a window's sum of gradient outer products, and to second order it measures how fast the window stops matching itself as it shifts. Its two eigenvalues count the directions the window varies in, so Harris, Shi–Tomasi and Förstner all score those two numbers, its leading eigenvector is the local orientation, and Lucas–Kanade's optical-flow equations have the same matrix on their left side: a window's motion can be solved for only when it scores as a corner. Worked by hand on the series' 5×5 patch, OpenCV's `goodFeaturesToTrack` returns one point, which is neither the patch's bright pixel nor on its edge; the edge's own window cannot measure vertical motion at all; and Harris's k = 0.04 and k = 0.06 disagree about one pixel of the edge.

**Level:** advanced · **You need:** *Image Processing by Hand* (part 1 of this series) for the shared patch and the Sobel gradient, the eigenvalues of a symmetric 2×2 matrix, and linear least squares · **Time:** ~36 min

This is part 9 of *Image Processing by Hand*. Part 1 built this matrix in one section, as the gradient covariance behind Harris's corner response, sketched its eigenvalue plane and promised this post. Part 8, *Canny Edge Detection, Line by Line: Setting the Thresholds*, ended where non-maximum suppression breaks at junctions. Here the matrix is computed on the shared patch and put to its three uses.

**Jump to:** [The problem](#the-problem) · [Worked example](#worked-example) · [Intuition](#intuition) · [Scores](#how-do-harris-shitomasi-and-förstner-score-the-same-two-numbers) · [Orientation](#how-does-the-same-matrix-give-orientation) · [Lucas–Kanade](#why-is-lucaskanade-the-same-matrix) · [Linearisation](#when-does-one-lucaskanade-step-go-wrong) · [Window and scale](#which-window-and-at-what-scale) · [The math](#the-math) · [Tooling map](#implementation-the-tooling-map) · [Limitations](#limitations-and-common-mistakes)

> [!IMPORTANT]
> Nothing in this post was run against an image. Every number is worked by hand on the shared patch and cross-checked with plain Python using only its `math` module; that check is not published. No OpenCV, scikit-image or MATLAB call was executed: library behaviour comes from source read at pinned commits and, for MATLAB, from MathWorks' documentation. There are no timings or measured curves. Figures that draw curves, surfaces or ellipses evaluate closed forms on the worked numbers, and their captions say so.

## Why this matters

Ask OpenCV's `goodFeaturesToTrack` for the best features on the series' 5×5 patch and it names one pixel: column 2, row 2. That is not the patch's single bright pixel, the one structure that looks like a point, and it is not on the patch's edge either. Ask `cornerHarris` instead, and the two values of its constant k that people usually pass, 0.04 and 0.06, disagree about a pixel on the edge: one calls it a corner, the other an edge. Hand that edge to Lucas–Kanade optical flow and it cannot tell whether the edge slid down.

All three answers come from one 2×2 matrix. Knowing what its four numbers mean tells you which points a tracker can follow, why the "corners" it finds are often not corners, and which flow vectors to distrust before you look at them.

## The problem

A gradient at one pixel, $g = (G_x, G_y)$, says how brightness changes across one direction. If the image moves by a small displacement $d = (u, v)$ between two frames and keeps its brightness, the change at that pixel is $I_t \approx -(G_x u + G_y v)$. That is one equation in two unknowns, so one pixel measures only the component of the motion along its own gradient. <!-- L23 --> This is the **aperture problem**: seen through a small aperture, a moving edge shows only its motion across itself. <!-- L09 -->

A single pixel cannot decide whether it is a feature either. The matrix of one gradient, its **outer product** $g g^{\top}$, has rank at most 1: one direction, or none. So both questions, "is this point well defined?" and "where did it go?", need a neighbourhood whose gradients point in more than one direction, and a way to measure that.

Harris and Stephens found the measure by asking how much a **window** of pixels changes when it is shifted by $d$. They expanded Moravec's sum of squared differences to second order and got a quadratic form in the shift: <!-- L02 -->

$$
E(d) = \sum_{\text{window}} w \,\big[I(x + d) - I(x)\big]^2 \approx d^{\top} M d, \qquad M = \sum_{\text{window}} w \begin{bmatrix} G_x^2 & G_x G_y \\ G_x G_y & G_y^2 \end{bmatrix} = \begin{bmatrix} A & B \\ B & C \end{bmatrix}
$$

$E(d)$ is how badly the window matches itself after a shift of $d$, $w$ are the window's weights, and $M$, the sum of the pixels' outer products, is the **structure tensor**, also called the second-moment or autocorrelation matrix. <!-- L34 --> Part 1 introduced $M$, its eigenvalues $\lambda_1 \ge \lambda_2$ and Harris's response; this post starts there. The eigenvalues say how fast $E$ grows along the two principal directions of the window. The question is what those two numbers mean, and why corner detection, orientation and motion all read the same matrix. The constraint is the window: it must be large enough to hold two directions and small enough to hold only one thing moving one way.

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

The computation below is what `cv2.cornerHarris(patch, blockSize=3, ksize=3, k)` and `cv2.cornerMinEigenVal(patch, 3, 3)` do, except for one scale factor treated later: 3×3 Sobel derivatives, their products summed over a 3×3 box, and OpenCV's default reflect-101 border for both steps. <!-- L40 -->

### Step 1: the gradient, one pixel at a time

Part 8 tabulated the patch's Sobel gradient under the replicate border that `cv2.Canny` uses. Under reflect-101 only column c0 changes: the mirror puts a copy of c1 on its left, so its horizontal derivative is 0 everywhere and the impulse leaves only vertical derivatives there.

```text
Gx                          Gy
  0    0  640  640    0       0     0     0    0    0
  0    0  425  640    0     430   430   215    0    0
  0    0  210  640    0       0     0     0    0    0
  0    0  425  640    0    -430  -430  -215    0    0
  0    0  640  640    0       0     0     0    0    0
```

The step reads 640, four times its height of 160, on c2 and c3. The impulse's own pixel has no gradient: its neighbours on opposite sides are equal. So at the pixel level the impulse looks exactly like a flat pixel: both give the zero matrix. A pixel with a gradient gives a rank-1 outer product, one direction. No single pixel can be a corner. Figure 1 draws the gradient and the windows that the next step sums.

![The patch's Sobel gradient as arrows, 640 on both sides of the step and a ring round the impulse, with four 3×3 windows on row r2 outlined](FIG_01)

*Figure 1 — The gradient OpenCV's corner functions sum, under their reflect-101 border. Each outlined 3×3 window on row r2 sums nine outer products. Worked by hand.*

### Step 2: sum over windows along row r2

Now add up the products over each 3×3 window. On row r2 the patch is symmetric top to bottom: $G_x$ is the same above and below, and $G_y$ flips sign, so every off-diagonal sum $B$ cancels. Each tensor on row r2 is diagonal, and its eigenvalues are simply $A$ and $C$.

Take (r2, c2), whose window covers columns c1 to c3. Column c1 has no $G_x$; column c2 gives $425^2 + 210^2 + 425^2 = 405{,}350$; column c3 gives $3 \times 640^2 = 1{,}228{,}800$. So $A = 1{,}634{,}150$. The vertical derivatives sit on rows r1 and r3: $C = 2 \times (430^2 + 215^2) = 462{,}250$. The whole row:

| window centre | A | C | λ1 | λ2 | what the window holds |
|---|---|---|---|---|---|
| (r2, c0) | 0 | 1,109,400 | 1,109,400 | 0 | the ring's vertical derivatives, mirrored |
| (r2, c1) | 405,350 | 832,050 | 832,050 | 405,350 | the impulse and its ring |
| (r2, c2) | 1,634,150 | 462,250 | 1,634,150 | 462,250 | the step and the ring |
| (r2, c3) | 1,634,150 | 92,450 | 1,634,150 | 92,450 | the step and two ring pixels |
| (r2, c4) | 2,457,600 | 0 | 2,457,600 | 0 | the step alone |

At (r2, c4) the window holds only horizontal derivatives, so its second eigenvalue is exactly 0: rank 1, an edge. At (r2, c1) and (r2, c2) both eigenvalues are large. No position on the patch is flat: a 3×3 derivative inside a 3×3 window reads a 5×5 neighbourhood, and every 5×5 neighbourhood of the patch holds the step or the impulse. A flat window would give the zero matrix. Figure 2 draws each tensor as an ellipse.

![Five ellipses for row r2: a vertical line at c0, rounder ellipses at c1 and c2, a flat sliver at c3 and a horizontal line at c4](FIG_02)

*Figure 2 — Row r2's five tensors, each drawn as an ellipse along its eigenvectors with semi-axes proportional to the square roots of its eigenvalues. Summing rank-1 matrices from different directions is what makes rank 2. Worked by hand.*

### Step 3: score them

Harris's response is $R = \lambda_1 \lambda_2 - k(\lambda_1 + \lambda_2)^2$, and Shi and Tomasi's score is $\lambda_2$, the smaller eigenvalue. <!-- L04 --> <!-- L11 --> On row r2, with R in units of $10^9$:

| window centre | R, k = 0.04 | R, k = 0.06 | λ2 (Shi–Tomasi) | λ2 / λ1 |
|---|---|---|---|---|
| (r2, c0) | −49.2 | −73.8 | 0 | 0 |
| (r2, c1) | 276.0 | 245.4 | 405,350 | 0.487 |
| (r2, c2) | 579.6 | 491.7 | 462,250 | 0.283 |
| (r2, c3) | 31.8 | −27.8 | 92,450 | 0.057 |
| (r2, c4) | −241.6 | −362.4 | 0 | 0 |

(r2, c4) is negative for every k: an edge. (r2, c2) is the strongest window on the row by both scores. And (r2, c3), a pixel on the step itself, changes class with k: $+31.8 \times 10^9$ at 0.04, a corner, and $-27.8 \times 10^9$ at 0.06, an edge. Its two ring pixels give it a second eigenvalue 1/18 the size of the first, and the scores section shows that k is exactly a threshold on that ratio.

OpenCV reports smaller numbers because it divides each derivative by $4 \times 3 \times 255 = 3{,}060$ before squaring, for an 8-bit image with a 3×3 aperture and a 3×3 window. <!-- L40 --> So `cornerMinEigenVal` returns 0.04937 at (r2, c2) and `cornerHarris` with k = 0.04 returns 0.006611 there; the ranking is the same.

### Step 4: what `goodFeaturesToTrack` returns

`goodFeaturesToTrack` builds the smaller-eigenvalue map at the default border, finds its maximum over the whole image, zeroes every value at or below `qualityLevel` times that maximum, keeps the pixels that equal the maximum of their 3×3 neighbourhood, and scans for them only from row 1 to the second-last row and from column 1 to the second-last column. <!-- L43 --> <!-- L42 --> Figure 3 shows the map.

![The 5×5 map of smaller eigenvalues: the largest, 616,156, on the excluded top and bottom rows; the one kept local maximum at (r2, c2)](FIG_03)

*Figure 3 — `goodFeaturesToTrack`'s selection on the patch. The map's maximum sits on the border rows, which the function never returns; the only interior 3×3 maximum is (r2, c2), whose tensor is the step's horizontal variation plus the impulse's vertical variation. Worked by hand.*

The map's maximum, 616,155.8, is at (r0, c1) and (r4, c1): reflect-101 mirrors row r1's ring gradients across the top and bottom rows and doubles them. Those pixels are skipped. Inside, the only 3×3 maximum is (r2, c2) at 462,250, so `goodFeaturesToTrack(patch, 10, 0.01, 1)` returns the single point (2, 2) in OpenCV's (x, y) order. With `useHarrisDetector=True` and k = 0.04 it returns the same pixel.

(r2, c2) wins because its window holds two unrelated edges at right angles. Its $A$ comes almost entirely from the step, columns c2 and c3, and its $C$ entirely from the ring above and below the impulse. The impulse's own window, (r2, c1), loses: the ring's negative horizontal derivatives cut the step's 640 at c2 down to 425, 210 and 425, so that window has little horizontal variation left.

### Step 5: the same matrices, read by Lucas–Kanade

Lucas–Kanade finds the shift $d$ that best explains the frame difference $I_t$ over a window. Linearise each pixel's change as $I_t \approx -g \cdot d$, with $g$ in grey levels per pixel, and minimise the squared error over the window. The normal equations are $M d = -\sum g\, I_t$: the same matrix. <!-- L14 --> In Sobel units, which read a one-level-per-pixel ramp as 8, that is $M d = -8 \sum G\, I_t$.

At (r2, c4), $M = \begin{bmatrix} 2{,}457{,}600 & 0 \\ 0 & 0 \end{bmatrix}$. The second equation reads $0 \cdot v = -8 \sum G_y I_t$, and $G_y$ is 0 on all nine pixels, so it reads $0 = 0$ whatever the frames hold. The vertical component of the motion is not in the data: slide the step down by any amount and nothing in this window changes. The aperture problem is the zero eigenvalue.

Now give it a real second frame: the patch moved one pixel right, with the new column c0 filled by 40, the patch's own left value. The frame difference is −160 on every row of c3, which the step has moved past, −215 at (r2, c1), which the impulse left, and +215 at (r2, c2), where it arrived. At (r2, c2), $\sum G_x I_t = 210 \times 215 + 3 \times 640 \times (-160) = -262{,}050$ and $\sum G_y I_t = 0$, so

$$
u = \frac{8 \times 262{,}050}{1{,}634{,}150} = 1.28, \qquad v = 0
$$

The window moved one pixel right, and one Lucas–Kanade step says 1.28 pixels right: the right direction, 28% long. At (r2, c1), the impulse's own window, the same step gives $u = -0.89$, the wrong direction. At (r2, c4) the only non-zero equation gives $u = 2.00$ and $v$ stays undetermined. The rank decides which components can be measured; how well one linear step measures them is a different question, taken up in its own section below.

### The scorecard

| window centre | λ1 | λ2 | Harris 0.04 | Harris 0.06 | Lucas–Kanade, one step, true (1, 0) |
|---|---|---|---|---|---|
| (r2, c4) the step | 2,457,600 | 0 | edge | edge | u = 2.00, v undetermined |
| (r2, c3) the step, two ring pixels | 1,634,150 | 92,450 | corner | edge | (1.28, 0) |
| (r2, c2) step plus ring | 1,634,150 | 462,250 | corner | corner | (1.28, 0) |
| (r2, c1) the impulse | 832,050 | 405,350 | corner | corner | (−0.89, 0) |
| (r2, c0) mirrored ring | 1,109,400 | 0 | edge | edge | v = 0, u undetermined |

The two rank-1 windows are rotated copies of each other: c4 cannot see vertical motion and c0 cannot see horizontal motion.

## Intuition

Picture $E(d)$ as a surface over the plane of possible shifts. At a flat window it is a plane at zero: no shift costs anything. At an edge it is a trough running along the edge: sliding along costs nothing, crossing costs a lot. At a corner, an impulse or a textured window it is a bowl. The structure tensor is that surface's curvature at the bottom, and Figure 4 draws it for four windows of row r2.

![Contour plots of the shift cost over a ±1 pixel square: a vertical trough at c4, a long bowl at c3, rounder bowls at c2 and c1](FIG_04)

*Figure 4 — The quadratic cost $d^{\top} M d$ of shifting each window, in grey levels squared. A trough has a direction that costs nothing; a bowl does not. Evaluated from the worked matrices.*

Every use of the tensor reads this surface. A corner detector asks how steep the shallowest side is. Orientation is the direction of the trough. A tracker finds where the bowl's bottom moves when the next frame arrives, and its precision is how wide that bottom is. Think of a marble in a dish: in a bowl it has one resting place, in a trough it can roll along the trough's length. The picture breaks for large shifts. The dish is only the second-order approximation near zero shift, and for a one-pixel move of a one-pixel impulse the true cost is not this bowl, which is how step 5 got −0.89.

## How do Harris, Shi–Tomasi and Förstner score the same two numbers?

Every score here is a function of $\lambda_1$ and $\lambda_2$ alone. They differ in how they treat a window whose second eigenvalue is small compared with the first.

### Harris's k is a threshold on the eigenvalue ratio

Moravec's detector, which Harris and Stephens started from, shifted a binary rectangular window by one pixel in four directions and kept the smallest change. <!-- L01 --> They replaced the four shifts by the quadratic form, the binary window by a Gaussian, and the minimum by a response that uses both eigenvalues. <!-- L02 --> They also observed that raising the contrast by a factor p multiplies both eigenvalues by p², so whether a window is an edge or a corner must depend on direction in the eigenvalue plane, not distance. <!-- L05 --> Their response does: write $t = \lambda_2/\lambda_1$ and

$$
R = \lambda_1^2 \big[t - k(1 + t)^2\big]
$$

so R is positive exactly when $t/(1+t)^2 > k$. The boundary is a ray: $t = 0.0436$, a ratio of 1 to 23, for k = 0.04, and $t = 0.0685$, 1 to 14.6, for k = 0.06. (r2, c3) has $t = 0.057$, between the two. Above k = 1/4 nothing is a corner, because $t/(1+t)^2$ never exceeds 1/4. Figure 5 draws the plane to scale with the patch's windows on it.

![The eigenvalue plane to scale: Harris rays for k = 0.04 and 0.06, Förstner's roundness rays, and row r2's five windows as points](FIG_05)

*Figure 5 — The plane Part 1 sketched, drawn to scale. Every boundary is a ray from the origin; (r2, c3) sits between the two Harris rays. Computed from the definitions on the worked eigenvalues.*

Harris and Stephens gave no value for k. <!-- L04 --> The conventions came later: 0.04 is typical according to a survey of local feature detectors, <!-- L34 --> an analysis of the detector puts it between 0.04 and 0.06, <!-- L37 --> and one well-known evaluation used 0.06. <!-- L30 --> So the "free parameter" is a choice of how elongated a window may be and still count as a corner. Figure 6 plots each score against the ratio at a fixed trace.

![Scores against the eigenvalue ratio: Harris for k = 0.04 and 0.06 crosses zero at 0.044 and 0.069; Shi–Tomasi and Förstner stay above](FIG_06)

*Figure 6 — Each score as a function of $t = \lambda_2/\lambda_1$, with $\lambda_1 + \lambda_2$ held fixed. Only Harris goes negative, and k sets where. Closed forms.*

R's size has a second problem. It grows as the fourth power of contrast, while the smaller eigenvalue grows as the square, so a fixed threshold on R admits low-contrast corners far less readily than one on $\lambda_2$.

### Shi–Tomasi: ask the tracker

Tomasi and Kanade asked which windows their tracker could follow. Its 2×2 system has to rise above the noise and be well conditioned, which leads to one test: accept a window when its smaller eigenvalue exceeds a threshold. <!-- L06 --> Shi and Tomasi published the criterion in 1994, arguing it is optimal by construction because the right features are the ones that make the tracker work. <!-- L11 --> They said plainly what it accepts: two large eigenvalues can be corners, salt-and-pepper texture, or any other pattern the tracker can follow. <!-- L07 --> The impulse is salt-and-pepper texture with one grain, and Harris and Stephens had already put "a corner or isolated point" in the same class. <!-- L03 -->

Tomasi and Kanade also saw the effect that picks (r2, c2). In their experiments, windows selected at corners sat with the corner at the window's edge, the window filled by the brighter side, because that position maximises the variation inside it. <!-- L08 --> On the patch the winning window holds the impulse in its left column and the step in its right two. Later analysis found that, under certain assumptions, Harris's score, Noble's and Shi–Tomasi's are the same detector up to the choice of a matrix norm, <!-- L36 --> and of five detectors examined against four axioms, only Shi–Tomasi satisfied all of them. <!-- L39 -->

### Förstner: how precisely is the point located?

Förstner and Gülch read the same matrix as the normal equations of a least-squares point location. The same matrix appears whether the point is found by matching, as the intersection of edge elements, or as a gradient-weighted centre of gravity. <!-- L16 --> Its inverse, times the noise variance, is the covariance of the located point, so the matrix defines an error ellipse, and they scored windows by that ellipse's size and shape:

$$
w = \frac{\det M}{\operatorname{tr} M}, \qquad q = \frac{4 \det M}{(\operatorname{tr} M)^2} = 1 - \left(\frac{\lambda_1 - \lambda_2}{\lambda_1 + \lambda_2}\right)^2
$$

$w$ is large when the ellipse is small, and $q$, the **roundness**, is 1 for a circle and 0 on an ideal edge. <!-- L17 --> Windows qualify when $q$ exceeds a limit between 0.5 and 0.75 and $w$ exceeds a threshold, and the best is kept in each neighbourhood. <!-- L19 --> A limit of 0.75 allows eigenvalues in a ratio of up to 3 to 1; 0.5 allows 5.8 to 1.

On row r2, $q$ is 0.881 at the impulse, 0.688 at (r2, c2) and 0.203 at (r2, c3). With a limit of 0.75 the only interior windows that pass are on column c1, and the best of them by $w$ is (r2, c1): the impulse itself. With 0.5, (r2, c2) passes as well and wins on $w$, 360,325 against 272,565. Of the scores here, Förstner's roundness test with a strict limit is the only one that picks the impulse. The **harmonic mean** of the eigenvalues, $2\det M/\operatorname{tr} M$, is $2w$ and needs no parameter at all. <!-- L37 -->

## How does the same matrix give orientation?

The eigenvector of $\lambda_1$ points along the direction of strongest variation, the dominant gradient; an edge or the stripes of a texture run perpendicular to it. Förstner and Gülch read the same angle off the matrix as the direction of the error ellipse: <!-- L18 -->

$$
\theta = \tfrac12 \operatorname{atan2}(2B,\ A - C)
$$

Why build orientation from outer products instead of averaging the gradient vectors? Look at the impulse's window. Its gradients point toward the impulse: down, (0, 430), on the row above, and up, (0, −430), on the row below. Summed as vectors, the vertical parts cancel and the window's total gradient is (1,060, 0). The outer product does not care about sign, because $g g^{\top} = (-g)(-g)^{\top}$, so the same window gives $C = 832{,}050$. In angle terms, the tensor doubles each gradient's angle: a gradient at angle φ contributes the vector $|g|^2 (\cos 2\varphi, \sin 2\varphi)$, and gradients 180° apart, which describe the same edge seen from either side, now add instead of cancelling. The doubled vectors sum to $(A - C,\ 2B)$, Figure 7 shows both sums, and Figure 8 draws every tensor of the patch as an oriented ellipse.

![The impulse window's nine gradients: as vectors the vertical parts cancel; as doubled angles they add to a length of 426,700](FIG_07)

*Figure 7 — Why the tensor squares before it sums. Opposite gradients cancel as vectors and add as doubled angles. Worked by hand on the impulse's window.*

![All 25 tensors as ellipses: vertical lines on c0, horizontal lines on c4, round ellipses near the impulse tilting up to 50 degrees](FIG_08)

*Figure 8 — Orientation and anisotropy across the patch. Each ellipse is a tensor: its long axis lies along the dominant gradient, and its thinness is the coherence. Worked by hand.*

The length of the doubled sum, $\sqrt{(A - C)^2 + 4B^2}$, is exactly $\lambda_1 - \lambda_2$, and the total, $A + C$, is $\lambda_1 + \lambda_2$. Their ratio, the **coherence** $(\lambda_1 - \lambda_2)/(\lambda_1 + \lambda_2)$, is 1 for a single straight edge and 0 when no direction dominates. On row r2 it is 1.00 at c4, 0.89 at c3, 0.56 at c2 and 0.34 at the impulse. Off the middle row the matrices rotate: (r1, c2) points 3.2° off horizontal and (r0, c1) 49.8°, along the ring's diagonal. Förstner's roundness is one minus the coherence squared.

Bigün, Granlund and Wiklund posed orientation as fitting an axis to a neighbourhood's spectrum by least squares, which reduces to an eigenvalue problem computed in the spatial domain, and applied it both to texture and to optical flow. <!-- L29 --> For flow, the gradient gains a third component, the time derivative, and the 3×3 space-time tensor's least eigenvector points along the motion. <!-- L28 --> Exercise E5 builds one.

## Why is Lucas–Kanade the same matrix?

Lucas and Kanade's 1981 paper was about registering images for stereo. It linearised the image for a small displacement, iterated in a Newton–Raphson style, and in two dimensions summed five products over the region, three of them the entries of $M$. <!-- L14 --> Tomasi and Kanade adopted it to track features through image streams. <!-- L55 --> In today's terms it is a Gauss–Newton minimisation of the sum of squared differences, and its approximate Hessian is built from the gradient images. <!-- L22 --> For a pure translation those gradient images are the image gradients themselves, so the Hessian is the structure tensor:

$$
M d = -\sum_{\text{window}} w\, g\, I_t, \qquad \operatorname{Cov}(d) = \sigma^2 M^{-1}
$$

The first equation is the solve. The second is its precision: with noise of standard deviation σ in the frame difference, the estimate's uncertainty is the error ellipse Förstner described, <!-- L17 --> and a Bayesian treatment of the same least squares gives each flow vector such a covariance. <!-- L26 --> Figure 9 draws both.

![The plane of possible motions: at c4 a vertical line of equally good solutions; at c3, c2 and c1 error ellipses, longest vertically at c3](FIG_09)

*Figure 9 — What each window can say about motion. At (r2, c4) every point on the line fits the data equally well; elsewhere the uncertainty is an ellipse whose semi-axes are $\sigma/\sqrt{\lambda_1}$ and $\sigma/\sqrt{\lambda_2}$. Evaluated from the worked matrices.*

At (r2, c3) the vertical component's uncertainty is $\sqrt{1{,}634{,}150 / 92{,}450} = 4.2$ times the horizontal one's; at (r2, c2) it is 1.9 times; at the impulse the long axis is horizontal, 1.4 times the vertical. A rank-1 window turns the ellipse into a line, and only the component across the edge, the **normal flow**, is measured. For a horizontal edge only the vertical component is determined. <!-- L13 -->

Practical trackers act on exactly this. Barron, Fleet and Beauchemin's Lucas–Kanade, which smooths first and weights a 5×5 window, <!-- L24 --> computed a full velocity when both eigenvalues passed a threshold τ, only the normal velocity when just the larger one did, and nothing otherwise, with τ = 1.0, and found the smaller eigenvalue a better reliability test than the sum. <!-- L25 --> MATLAB's `opticalFlowLK` uses the same three-way test. <!-- L54 --> Methods built on this local solve are robust to noise but cannot be dense: the matrix is singular on flat regions and nearly singular along edges. <!-- L27 -->

So the selector and the tracker test the same thing. Bouguet's description of the pyramidal tracker behind OpenCV selects features exactly as `goodFeaturesToTrack` does: the smaller eigenvalue everywhere, a percentage of the maximum as threshold, 3×3 local maxima, a minimum distance. It adds that a 3×3 window is enough for selection but too small for tracking. <!-- L21 --> OpenCV follows it, with `blockSize` 3 for selection and a 21×21 window for `calcOpticalFlowPyrLK`. <!-- L42 --> <!-- L45 --> The matrix that chose a point is not the matrix that tracks it.

## When does one Lucas–Kanade step go wrong?

Step 5 gave 1.28 instead of 1 at (r2, c2), and −0.89 at the impulse. Figure 10 shows why, on row r2.

![Row r2 before and after a one-pixel move: at c2 the gradient predicts the pixel darkens by 26 but it brightens by 215 as the impulse arrives](FIG_10)

*Figure 10 — The linear model against the real frame difference on row r2, for a move of one pixel right. At c2 the step's gradient says "darker", the impulse arriving says "much brighter". Worked by hand.*

The linear model predicts each pixel's change from its gradient: a pixel whose brightness rises to the right gets darker when the pattern moves right. At (r2, c2) the step's gradient wins, 210 in Sobel units or 26 grey levels per pixel, so the model predicts a drop of 26. The impulse arrives there instead and the pixel rises by 215. Inside the impulse's window it is the only pixel with both a gradient and a change, so the solve concludes the pattern moved left.

The approximation is exact only as the displacement shrinks to zero or where intensity is linear, which a one-pixel impulse moving one pixel is not. <!-- L10 --> Lucas and Kanade's remedies are still the ones in use: iterate, re-sampling the second frame at the current estimate, <!-- L14 --> and smooth, which extends the range of motions the linear model covers, at the cost of suppressing details smaller than the smoothing, which may vanish altogether. Smoothing leads to working coarse to fine. <!-- L15 --> Bouguet's pyramid does both: it iterates at each level, uses Scharr derivatives, and with 2 to 4 levels multiplies the reachable displacement by $2^{L+1} - 1$, 15 for three levels above the original image. <!-- L20 --> OpenCV's defaults are 3 levels and up to 30 iterations or a step under 0.01 pixel. <!-- L45 -->

A second requirement is that the window holds one motion. Shi and Tomasi's example is a foreground twig crossing a background twig: the crossing exists only in the image, any selection criterion picks it, and it moves like neither twig. <!-- L12 --> (r2, c2) is such a window. Its "corner" is the step plus the impulse, and its flow is right only if the two move together.

## Which window, and at what scale?

The tensor has two sizes. The derivative's support, OpenCV's `ksize` or a Gaussian derivative's σ_D, decides which details produce a gradient; the window's size, `blockSize` or an integration σ_I, decides how many gradients are pooled. <!-- L32 --> A 3×3 derivative in a 3×3 window reads 5×5 pixels, the whole patch at its centre, which is why no window on the patch is flat.

The window's shape matters too. Harris and Stephens replaced Moravec's binary rectangular window with a Gaussian because the binary one gave a noisy response. <!-- L02 --> OpenCV's `cornerHarris` sums over a box again. An analysis of the detector found OpenCV's version, with Sobel derivatives and a box, faster than a Gaussian implementation but much less repeatable under rotation, and attributed it to aliasing that neither the Sobel kernel nor the box reduces. <!-- L38 --> An earlier evaluation saw a standard Harris repeat worst at 45° and traced it to non-isotropic discrete derivative filters; Gaussian derivatives fixed it. <!-- L31 --> Förstner and Gülch used box windows themselves but noted that a Gaussian gives unique, stable maxima at step edges. <!-- L19 --> Figure 11 shows what the shape does to (r2, c3).

![A 3×3 derivative in a 3×3 window reads 5×5; box against Gaussian weights; (r2, c3)'s ratio is 0.057 under the box, 0.022 under the Gaussian](FIG_11)

*Figure 11 — One window, two weightings. The box counts the ring's corner pixels as fully as the centre; the series' 3×3 Gaussian gives them 0.0571 against the centre's 0.2725, and (r2, c3) drops below both Harris boundaries. Worked by hand.*

With the series' Gaussian as the window, (r2, c3)'s ratio falls from 0.057 to 0.022, below both Harris boundaries, so k = 0.04 and 0.06 agree that it is an edge. The disagreement in step 3 belonged to the box. The other windows keep their order but not their ratios: (r2, c2) falls from 0.283 to 0.211.

When the window changes size across scales, the tensor must be normalised so scales can be compared. Mikolajczyk and Schmid's scale-adapted matrix multiplies it by $\sigma_D^2$ and ties the two scales together, $\sigma_D = 0.7\,\sigma_I$, on levels spaced by a factor of 1.4. <!-- L32 --> <!-- L33 --> The $\sigma_D^2$ is there because a step of height $h$ blurred by a Gaussian of width $\sigma_D$ has a peak slope of $h/(\sqrt{2\pi}\,\sigma_D)$: multiplying the derivative by $\sigma_D$ makes a step read the same at every scale. Harris–Laplace detects the maxima of this Harris response at each level, the half finished here, and keeps those where the Laplacian of Gaussian also peaks over scale. <!-- L33 --> Choosing the scale belongs to the later spoke *Scale Space and SIFT: Why σ Is a Search Dimension*.

## The math

| Symbol | Meaning |
|---|---|
| $G_x$, $G_y$; $g$ | derivatives at a pixel; the gradient vector |
| $w$ | window weights |
| $M = \begin{bmatrix} A & B \\ B & C \end{bmatrix}$ | structure tensor, the window's sum of $w\, g g^{\top}$ |
| $\lambda_1 \ge \lambda_2$, $t$ | eigenvalues; their ratio $\lambda_2/\lambda_1$ |
| $d = (u, v)$, $I_t$ | displacement; frame difference |
| σ | noise standard deviation in $I_t$ |

**Shift cost.** For a small shift $d$,

$$
E(d) \approx d^{\top} M d \tag{1}
$$

so the eigenvalues are the cost's curvatures along the principal directions. At (r2, c2), in grey levels per pixel, a one-pixel shift across the step costs $1{,}634{,}150/64 = 25{,}534$ and along it $462{,}250/64 = 7{,}223$; the 64 is Sobel's gain of 8, squared.

**Eigenvalues.**

$$
\lambda_{1,2} = \frac{A + C}{2} \pm \sqrt{\left(\frac{A - C}{2}\right)^2 + B^2} \tag{2}
$$

This is what `cornerMinEigenVal` computes, with the minus sign. <!-- L41 --> At (r1, c1), $A = 634{,}325$, $B = 91{,}375$ and $C = 416{,}025$ give 667,524 and 382,826.

**Scores.**

$$
R = \lambda_1 \lambda_2 - k(\lambda_1 + \lambda_2)^2 = \lambda_1^2\big[t - k(1+t)^2\big], \qquad R > 0 \iff \frac{t}{(1+t)^2} > k \tag{3}
$$

Harris's sign depends only on the ratio, and at k = 0.04 the boundary is $t = 0.0436$.

$$
\text{Shi–Tomasi: } \lambda_2, \qquad w = \frac{\det M}{\operatorname{tr} M}, \qquad q = \frac{4 \det M}{(\operatorname{tr} M)^2} \tag{4}
$$

All three need only $A$, $B$ and $C$; the smaller eigenvalue costs one square root more.

**Orientation and coherence.**

$$
\theta = \tfrac12 \operatorname{atan2}(2B,\ A - C), \qquad \frac{\lambda_1 - \lambda_2}{\lambda_1 + \lambda_2} = \frac{\sqrt{(A - C)^2 + 4B^2}}{A + C} \tag{5}
$$

At (r1, c1) the angle is 20.0° and the coherence 0.27.

**Lucas–Kanade.** Minimising $\sum w\,(I_t + g \cdot d)^2$ gives

$$
M d = -\sum w\, g\, I_t, \qquad \operatorname{Cov}(d) = \sigma^2 M^{-1} \tag{6}
$$

which has a unique solution only when $\lambda_2 > 0$, and whose error ellipse has semi-axes $\sigma/\sqrt{\lambda_1}$ and $\sigma/\sqrt{\lambda_2}$.

**Scale.** The scale-adapted tensor is <!-- L32 -->

$$
\mu(x; \sigma_I, \sigma_D) = \sigma_D^2\, g_{\sigma_I} * \big(\nabla L\, \nabla L^{\top}\big), \qquad L = g_{\sigma_D} * I \tag{7}
$$

where $g_\sigma$ is a Gaussian of standard deviation σ and $\nabla L$ the gradient of the image smoothed at $\sigma_D$; the factor $\sigma_D^2$ keeps a step's response the same at every scale.

## Implementation: the tooling map

Every entry below maps to the arithmetic above. **None of it was executed for this post**; it comes from source at pinned commits and MathWorks' documentation. Figure 12 is the same map in one picture.

![Grid comparing OpenCV, scikit-image and MATLAB on derivative, window, border, response, units, selection and Lucas–Kanade defaults](FIG_12)

*Figure 12 — One matrix, three libraries: different derivatives, windows, borders and units. Check the row before carrying a threshold from one library to another.*

### OpenCV

| Want | Call | Note |
|---|---|---|
| Harris response | `cv2.cornerHarris(img, blockSize, ksize, k)` | k has no default; box window; reflect-101 <!-- L40 --> <!-- L42 --> |
| smaller eigenvalue | `cv2.cornerMinEigenVal(img, blockSize, ksize=3)` | the Shi–Tomasi map <!-- L41 --> |
| both eigenvalues and vectors | `cv2.cornerEigenValsAndVecs(img, blockSize, ksize)` | six numbers per pixel; documented as unsorted, the code writes the larger first <!-- L56 --> |
| features | `cv2.goodFeaturesToTrack(img, maxCorners, qualityLevel, minDistance, blockSize=3, useHarrisDetector=False, k=0.04)` | never returns the 1-pixel border; qualityLevel is relative <!-- L43 --> |
| sparse flow | `cv2.calcOpticalFlowPyrLK(prev, next, pts, None, winSize=(21, 21), maxLevel=3)` | Scharr derivatives; minEigThreshold 1e-4 <!-- L45 --> <!-- L46 --> |

The units are OpenCV's own. For 8-bit input each derivative is divided by $2^{\text{ksize}-1} \times \text{blockSize} \times 255$, so with the defaults the tensor is the window's mean of $(\text{Sobel}/1{,}020)^2$, and Harris's R scales as the fourth power of that. <!-- L40 --> `calcOpticalFlowPyrLK` keeps the image ×32 and its Scharr derivatives at their raw gain of 32, scales the matrix by $2^{-20}$ and divides its smaller eigenvalue by the window's pixel count. <!-- L46 --> The default threshold of $10^{-4}$ therefore asks the window's mean squared gradient along its weakest direction to reach 0.1024, an RMS of 0.32 grey levels per pixel; below that, the point's status is 0.

Which code runs is itself a setting. `cornerHarris` hands the call to Intel IPP only for apertures 3 and 5 with a constant or replicate border, so the default reflect-101 runs the code described here; `cornerMinEigenVal`'s IPP call is commented out; UMat inputs go to OpenCL. <!-- L44 --> The Lucas–Kanade level solver has a platform replacement only in 32-bit ARMv7 builds. <!-- L47 --> Release 4.10.0 has the same rules and constants. <!-- L48 -->

### scikit-image and MATLAB

| Want | Call | Note |
|---|---|---|
| the tensor | `skimage.feature.structure_tensor(img, sigma=1)` | 0–1 image, SciPy Sobel, Gaussian window, zero padding <!-- L49 --> |
| scores | `corner_harris(img, k=0.05)`, `corner_shi_tomasi(img)`, `corner_foerstner(img)` | k defaults to 0.05; Förstner returns (w, q) <!-- L50 --> |
| peaks | `corner_peaks(response, min_distance=1)` | excludes a 1-pixel border <!-- L50 --> |
| dense flow | `skimage.registration.optical_flow_ilk(ref, moving, radius=7)` | 15×15 window, 10 warps, coarse to fine; singular windows get zero flow <!-- L51 --> |
| MATLAB | `detectHarrisFeatures(I)`, `detectMinEigenFeatures(I)`, `opticalFlowLK` | 5×5 Gaussian window, MinQuality 0.01, k not documented; NoiseThreshold 0.0039 <!-- L52 --> <!-- L53 --> <!-- L54 --> |

scikit-image's tensor is a Gaussian-weighted mean of $(\text{Sobel}/255)^2$, sixteen times OpenCV's for the same window, and its default zero padding turns an image's border into a step: on the patch the right edge would read as a drop from 200 to 0. <!-- L49 -->

### The worked example, in OpenCV

```python
import numpy as np
import cv2

patch = np.full((5, 5), 40, np.uint8)
patch[:, 3:] = 200
patch[2, 1] = 255

lam2 = cv2.cornerMinEigenVal(patch, 3, 3)          # (r2, c2): 0.04937
r04 = cv2.cornerHarris(patch, 3, 3, 0.04)          # (r2, c3): +0.000363, a corner
r06 = cv2.cornerHarris(patch, 3, 3, 0.06)          # (r2, c3): -0.000317, an edge
pts = cv2.goodFeaturesToTrack(patch, 10, 0.01, 1)  # [[[2., 2.]]]: one point, x = 2, y = 2
none = cv2.goodFeaturesToTrack(patch, 10, 0.8, 1)  # None: the bar is set by a border pixel
```

This was not run for this post. The comments state what the worked example predicts.

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** reading the output of a corner detector as corners. Harris, Shi–Tomasi and Förstner find windows whose gradients span two directions: impulses, texture, accidental crossings of unrelated edges, and real corners. Detected points need not be 3-D corners at all. <!-- L35 --> On the patch the winner is a window holding an edge and the side of a bright pixel.

- **Tuning k as a sensitivity knob.** It is an eigenvalue-ratio threshold: 1 to 23 at 0.04, 1 to 14.6 at 0.06. Decide how elongated a window may be, then set k.
- **One threshold on R across images.** R grows as contrast to the fourth power; a threshold tuned on one image means something else on a darker one. Use `qualityLevel`-style relative thresholds, or the smaller eigenvalue.
- **Selecting with one window and tracking with another.** `goodFeaturesToTrack` scores 3×3 windows; `calcOpticalFlowPyrLK` solves 21×21 ones. <!-- L21 --> <!-- L45 --> A point that was well conditioned at selection may not be when tracked.
- **Trusting points near the border.** `goodFeaturesToTrack` drops the outermost ring of pixels, reflect-101 mirrors structures across the border and can double them, and scikit-image's zero padding manufactures an edge there. <!-- L43 --> <!-- L49 -->
- **Expecting normal flow from OpenCV.** Below `minEigThreshold`, `calcOpticalFlowPyrLK` drops the point; Barron et al.'s rule returns the normal component, MATLAB a normalised gradient flow, and scikit-image's dense solver zero for singular windows. <!-- L46 --> <!-- L25 --> <!-- L51 -->
- **Tracking structures smaller than the motion.** One linear step at the impulse got the direction wrong. Smooth, iterate, or start coarse. <!-- L15 -->
- **Assuming the box window is harmless.** It changed (r2, c3) from edge to corner at k = 0.04, and it costs repeatability under rotation. <!-- L38 -->

## Key takeaways

- **The structure tensor is the curvature of a window's self-matching cost.** Its eigenvalues count the directions the window varies in: zero, one or two.
- **Every corner score is a function of the two eigenvalues.** Harris's k is a threshold on their ratio, Shi–Tomasi takes the smaller one, Förstner adds roundness; on the patch only Förstner's strict roundness test picks the impulse.
- **Lucas–Kanade's matrix is the same tensor,** so a rank-1 window cannot measure motion along its edge, and a point is trackable only when it scores as a corner.
- **A high score is necessary, not sufficient, for tracking:** one linear step on a one-pixel impulse moving one pixel got the direction wrong, and a window holding two structures has one flow only if they move together.
- **The window's size, shape and border are part of the answer:** the box made (r2, c3) a corner at k = 0.04, and the Gaussian made it an edge.

## Try it yourself

The exercises are pen and paper, matching the post; each names its rung.

### E1 — Reproduce: one tensor off the middle row

Compute $A$, $B$ and $C$ at (r1, c2) under reflect-101 with a 3×3 box, then its eigenvalues and Harris's R at k = 0.04.

**Self-check:** three sums, two eigenvalues, and R in units of $10^9$.

<details><summary>Answer</summary>

The window covers rows r0 to r2 and columns c1 to c3. $A = (640^2 + 425^2 + 210^2) + 3 \times 640^2 = 1{,}863{,}125$ from columns c2 and c3. $B$ comes from (r1, c2) alone, $425 \times 215 = 91{,}375$. $C = 430^2 + 215^2 = 231{,}125$ from (r1, c1) and (r1, c2). Equation (2) gives $\lambda_1 = 1{,}868{,}225$ and $\lambda_2 = 226{,}025$, and $R = 246.8 \times 10^9$. The non-zero $B$ tilts the tensor 3.2° off horizontal.

</details>

### E2 — Inspect: when does (r2, c2) stop being a corner?

Using Figure 6 or equation (3), find the value of k above which Harris calls (r2, c2) an edge.

**Self-check:** a value of k and the ratio it comes from.

<details><summary>Answer</summary>

$t = 462{,}250 / 1{,}634{,}150 = 0.283$, and $t/(1+t)^2 = 0.172$. Any k above 0.172 makes R negative there. The impulse's window, $t = 0.487$, survives up to 0.220; (r2, c3) flips at 0.0507.

</details>

### E3 — Predict: a fainter impulse

Replace the 255 by 120. Before computing, predict which point `goodFeaturesToTrack(patch, 10, 0.01, 1)` returns. Then compute the smaller eigenvalue at (r2, c1) and (r2, c2).

**Self-check:** both eigenvalues and the returned point. A right answer for the wrong reason does not count.

<details><summary>Answer</summary>

It returns (1, 2) in (x, y) order: the impulse itself. With 120 the ring's derivatives fall to 160 and 80, so they cut the step's 640 at c2 only to 560, 480 and 560, and the impulse's window keeps its horizontal variation: $A = 857{,}600$ and $C = 2 \times (160^2 + 160^2 + 80^2) = 115{,}200$ at (r2, c1). At (r2, c2) the vertical part is only $C = 2 \times (160^2 + 80^2) = 64{,}000$. The bright impulse had been weakening its own window; the faint one does not.

</details>

### E4 — Diagnose: no features at all

A colleague calls `goodFeaturesToTrack(patch, 10, 0.8, 1)` and gets `None`, though (r2, c2) is a clear local maximum. Find the cause and the largest `qualityLevel` that still returns a point.

**Self-check:** the two numbers the threshold compares, and a limit.

<details><summary>Answer</summary>

The threshold is 0.8 times the map's maximum, and that maximum is 616,155.8 on a border row that the function never returns. 0.8 × 616,155.8 = 492,925, above (r2, c2)'s 462,250, so every interior value is zeroed. Any `qualityLevel` up to 462,250 / 616,155.8 = 0.750 still returns (2, 2). The border sets a bar the interior has to clear.

</details>

### E5 — Extend: flow as orientation in space-time

Add time as a third axis. At (r2, c4), for the patch moved one pixel right, build the 3×3 tensor of $(G_x/8,\ G_y/8,\ I_t)$ summed over the window, find its null space, and read the motion from it.

**Self-check:** the matrix, a basis of its null space, and $(u, v)$.

<details><summary>Answer</summary>

$G_x/8 = 80$ and $I_t = -160$ on column c3 and its mirror, six pixels; everything else is 0. The tensor is $\begin{bmatrix} 38{,}400 & 0 & -76{,}800 \\ 0 & 0 & 0 \\ -76{,}800 & 0 & 153{,}600 \end{bmatrix}$. Its null space is spanned by $(0, 1, 0)$ and $(2, 0, 1)$. Brightness constancy says $(u, v, 1)$ is orthogonal to every space-time gradient, so the motion is $u = 2$ with $v$ free: the same answer as the 2×2 solve, and the same aperture problem, now as a two-dimensional null space.

</details>

## References

1. Harris, C., and Stephens, M. "A Combined Corner and Edge Detector." *Proceedings of the Alvey Vision Conference 1988*, 147–151. doi:10.5244/C.2.23. [PDF](https://www.bmva-archive.org.uk/bmvc/1988/avc-88-023.pdf)
2. Shi, J., and Tomasi, C. "Good Features to Track." *Proceedings of CVPR 1994*, 593–600. doi:10.1109/CVPR.1994.323794. [PDF](https://users.cs.duke.edu/~tomasi/papers/shi/shiCvpr94.pdf)
3. Lucas, B. D., and Kanade, T. "An Iterative Image Registration Technique with an Application to Stereo Vision." *Proceedings of IJCAI 1981*, vol. 2, 674–679. [PDF](https://www.ijcai.org/Proceedings/81-2/Papers/017.pdf)
4. Tomasi, C., and Kanade, T. *Detection and Tracking of Point Features.* Technical report CMU-CS-91-132, Carnegie Mellon University, 1991. [PDF](http://cecas.clemson.edu/~stb/klt/tomasi-kanade-techreport-1991.pdf)
5. Förstner, W., and Gülch, E. "A Fast Operator for Detection and Precise Location of Distinct Points, Corners and Centres of Circular Features." *ISPRS Intercommission Conference on Fast Processing of Photogrammetric Data*, Interlaken, 1987, 281–305. [PDF](https://www.ipb.uni-bonn.de/pdfs/Forstner1987Fast.pdf)
6. Bouguet, J.-Y. "Pyramidal Implementation of the Lucas Kanade Feature Tracker: Description of the Algorithm." Intel Corporation, Microprocessor Research Labs (undated; OpenCV cites it as 2001). [PDF](http://robots.stanford.edu/cs223b04/algo_tracking.pdf)
7. Baker, S., and Matthews, I. "Lucas-Kanade 20 Years On: A Unifying Framework." *International Journal of Computer Vision* 56(3):221–255, 2004. [doi:10.1023/B:VISI.0000011205.11775.fd](https://doi.org/10.1023/B:VISI.0000011205.11775.fd)
8. Barron, J. L., Fleet, D. J., and Beauchemin, S. S. "Performance of Optical Flow Techniques." *International Journal of Computer Vision* 12(1):43–77, 1994. [doi:10.1007/BF01420984](https://doi.org/10.1007/BF01420984)
9. Simoncelli, E. P., Adelson, E. H., and Heeger, D. J. "Probability Distributions of Optical Flow." *Proceedings of CVPR 1991*, 310–315. [doi:10.1109/CVPR.1991.139707](https://doi.org/10.1109/CVPR.1991.139707)
10. Bruhn, A., Weickert, J., and Schnörr, C. "Lucas/Kanade Meets Horn/Schunck: Combining Local and Global Optic Flow Methods." *International Journal of Computer Vision* 61(3):211–231, 2005. [doi:10.1023/B:VISI.0000045324.43199.43](https://doi.org/10.1023/B:VISI.0000045324.43199.43)
11. Bigün, J., Granlund, G. H., and Wiklund, J. "Multidimensional Orientation Estimation with Applications to Texture Analysis and Optical Flow." *IEEE Transactions on Pattern Analysis and Machine Intelligence* 13(8):775–790, 1991. [doi:10.1109/34.85668](https://doi.org/10.1109/34.85668)
12. Schmid, C., Mohr, R., and Bauckhage, C. "Evaluation of Interest Point Detectors." *International Journal of Computer Vision* 37(2):151–172, 2000. [doi:10.1023/A:1008199403446](https://doi.org/10.1023/A:1008199403446)
13. Mikolajczyk, K., and Schmid, C. "Scale & Affine Invariant Interest Point Detectors." *International Journal of Computer Vision* 60(1):63–86, 2004. [doi:10.1023/B:VISI.0000027790.02288.f2](https://doi.org/10.1023/B:VISI.0000027790.02288.f2)
14. Tuytelaars, T., and Mikolajczyk, K. "Local Invariant Feature Detectors: A Survey." *Foundations and Trends in Computer Graphics and Vision* 3(3):177–280, 2008. [doi:10.1561/0600000017](https://doi.org/10.1561/0600000017)
15. Sánchez, J., Monzón, N., and Salgado, A. "An Analysis and Implementation of the Harris Corner Detector." *Image Processing On Line* 8:305–328, 2018. [doi:10.5201/ipol.2018.229](https://doi.org/10.5201/ipol.2018.229)
16. Kenney, C. S., Zuliani, M., and Manjunath, B. S. "An Axiomatic Approach to Corner Detection." *Proceedings of CVPR 2005*, vol. 1, 191–197. [doi:10.1109/CVPR.2005.68](https://doi.org/10.1109/CVPR.2005.68)
17. Zuliani, M., Kenney, C. S., and Manjunath, B. S. "A Mathematical Comparison of Point Detectors." *Proceedings of CVPR Workshops 2004*, 172. [doi:10.1109/CVPR.2004.282](https://doi.org/10.1109/CVPR.2004.282)
18. OpenCV source, commit 802cf95: `corner.cpp`, `featureselect.cpp`, `spatialgradient.cpp`, `imgproc.hpp`, `lkpyramid.cpp`, `lkpyramid.simd.hpp`, `tracking.hpp`, and the Carotene and RISC-V HAL headers. <https://github.com/opencv/opencv/tree/802cf95aa3d42816995695bf68a86b3532f12760> (accessed 2026-10-12)
19. OpenCV source, tag 4.10.0: `corner.cpp`, `featureselect.cpp`, `lkpyramid.cpp`. <https://github.com/opencv/opencv/tree/4.10.0/modules> (accessed 2026-10-12)
20. scikit-image source, commit b700edc: `feature/corner.py`, `feature/util.py`, `filters/_gaussian.py`, `registration/_optical_flow.py`. <https://github.com/scikit-image/scikit-image/tree/b700edc8005e4ee9e74fc83259f09e8df3213f15/src/_skimage2> (accessed 2026-10-12)
21. MathWorks. "detectHarrisFeatures", "detectMinEigenFeatures" and "opticalFlowLK." Computer Vision Toolbox documentation, release R2026b. <https://www.mathworks.com/help/vision/ref/detectharrisfeatures.html>, <https://www.mathworks.com/help/vision/ref/detectmineigenfeatures.html>, <https://www.mathworks.com/help/vision/ref/opticalflowlk.html> (accessed 2026-10-12)
