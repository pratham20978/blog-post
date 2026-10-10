# Series plan — Foundational Architectures

**Slug:** foundational-architectures · **Shape:** hybrid (a toolkit root, two tracks that converge,
four two-part models) · **Parts:** 18 (14 committed, 4 optional) · **Category:** `machine-learning`
for every part

## Why this is a series and not one post

Each model here exists because the model before it hit a wall the reader can state in one
sentence. AlexNet asked whether a CNN could learn ImageNet at all. VGG asked whether depth could
replace large kernels, Inception whether that depth could be afforded, and BatchNorm whether it
could be trained quickly. ResNet asked why deeper networks trained *worse*, and MobileNet whether
any of it would run on a phone. On the sequence side, the LSTM asked why RNNs forget, attention
asked why one vector could not hold a sentence, and the Transformer asked whether recurrence could
go. ViT asked whether convolution could go. Each wall is a prerequisite seam: the fix means
nothing until the reader has felt the wall, and feeling it takes a worked example of its own. That
puts one seam at every model.

Four models carry more than one post of material. For LeNet-5, Inception, ResNet and the
Transformer, the mechanism (every shape, one worked forward pass) and the depth (the derivations,
and why it works) together run past 10,000 words or 18 figures. So each of those four is a
two-rung ladder inside the series. Budgeted as one article, the fourteen committed parts come to
about 104,000 words and 167 figures.

**Shape.** Part 1 is the counting toolkit that every later part prints its numbers in. Two tracks
leave it: a vision track (Parts 2–9) and a sequence track (Parts 10–13). They converge at ViT
(Part 14), where a Transformer reads an image. Inside a two-part model, Part 2 of that model assumes
its Part 1. Elsewhere each part names at most one prerequisite and restates it in two or three
sentences, so a reader can land on any model first.

## Why two series, and why this one is not called "Foundation Models"

This plan is the first of two. The second, `posts/frontier-models/`, covers the families that are
still changing: GPT, Llama, DeepSeek, Mamba and DeltaNet, JEPA and CLIP. They are split because
the seam between them is **stability**, not topic. Every part of this series can be finished and
stay true — ResNet-50 will have 25,557,032 parameters forever. The frontier series goes stale in
months. In 2026 alone Meta retired open Llama in favour of Muse, DeepSeek shipped V4, and the JEPA
line added LeJEPA and VL-JEPA. Mixing the two would make the stable half inherit the churn of the
live half. The frontier series assumes this one's LSTM (Part 10), Transformer (Part 12) and ViT
(Part 14). Nothing here depends on it.

In ML writing, "foundation model" is a term of art. Bommasani et al. (2021) coined it for large
models pretrained at scale and adapted to many tasks — GPT-3, CLIP, BERT. That describes the
*second* series. A "Foundation Models" title on a ResNet post would mislead exactly the readers who
search for that phrase. So this series is **Foundational Architectures**. The name is one word to
overrule.

## The angle

Introductory explanations of these models are the most saturated ground in machine learning. d2l.ai,
the CS231n notes, *The Illustrated Transformer*, *The Annotated Transformer* and thousands of posts
already own the block diagram, the headline equation and the PyTorch snippet. Restating them is
worthless. What they mostly do not do is below — each part's literature sweep must confirm this for
its own model, not assume it:

1. **Reconcile.** Recompute the paper's reported totals from its own layer table. Name the
   convention that makes popular sources disagree: MACs vs FLOPs, ResNet v1 vs v1.5, AlexNet's 224
   vs 227, single-crop vs 10-crop.
2. **Derive the "why" on numbers the reader can check.** Take the gradient through a shortcut or
   the variance behind √d_k on real values, instead of asserting the result.
3. **Measure.** Show gradient norms, loss-landscape slices and attention maps from runs a reader can
   repeat on a laptop CPU, each labelled as toy scale, beside the paper's reported numbers.
4. **Draw to scale.** A tensor's size on the page is proportional to its size in memory, and the
   scale is printed.

Every part is built on all four. A part that cannot do one of them says which, and why.

## Naming: "Part 1" belongs to the model, not the series

- `series_position` is the reading order of the whole series (1–18). It never appears in a title.
- "Part 1" and "Part 2" appear in a title only when one model needs more than one post, and they
  count within that model: *ResNet, Part 1: …* and *ResNet, Part 2: …*.
- A model's Part 1 is the **mechanism** (intermediate or beginner): what it is, every shape, the
  worked forward pass. Its Part 2 is the **depth** (advanced): the derivations and why it works.
  Difficulty rises from Part 1 to Part 2 and never falls.
- **Slugs never carry the part number.** If ResNet later needs a Part 3, no published URL changes.
- A model earns a second post only when its combined material passes the skill's own series
  threshold of 10,000 words or 18 figures. Here that is LeNet-5, Inception, ResNet and the
  Transformer.

## Reader objectives

| # | After this the reader can ... | Part |
|---|---|---|
| 1 | compute any conv layer's output shape, parameters and multiply–accumulates from its hyperparameters | 1 |
| 2 | compute a stack's theoretical receptive field and say why the effective one is smaller | 1 |
| 3 | check a paper's reported totals against its own layer table and name the convention behind any gap | 1 |
| 4 | derive the gradients of convolution, pooling and softmax–cross-entropy and verify them numerically | 2 |
| 5 | say why a convolution's input gradient is a full convolution with the kernel rotated 180° | 2 |
| 6 | say which of AlexNet's five changes survived and why ReLU trains faster than tanh | 3 |
| 7 | explain dropout's inverted scaling as an expectation match | 3 |
| 8 | prove that two stacked 3×3 convolutions see a 5×5 region with 28% fewer weights | 4 |
| 9 | locate where a network's parameters live versus where its compute lives | 4 |
| 10 | compute what a 1×1 bottleneck saves in an Inception module | 5 |
| 11 | derive BatchNorm's backward pass and explain the train/eval discrepancy on real numbers | 6 |
| 12 | say what the internal-covariate-shift story claimed and what replaced it | 6 |
| 13 | explain the degradation problem and why it is not overfitting | 7 |
| 14 | trace ResNet-50 block by block and reconcile its 25.6M parameters | 7 |
| 15 | derive why the identity shortcut keeps a gradient alive at depth | 8 |
| 16 | derive He initialisation from ReLU's effect on the second moment | 8 |
| 17 | read a filter-normalised loss-landscape slice and say what it cannot show | 8 |
| 18 | compute a depthwise-separable saving and say why it does not show up as latency | 9 |
| 19 | explain why MobileNetV2 removes the ReLU from its bottleneck | 9 |
| 20 | derive the vanishing-gradient bound for a plain RNN | 10 |
| 21 | trace a gradient along an LSTM's cell state and say what the forget gate does to it | 10 |
| 22 | compute an additive-attention alignment by hand | 11 |
| 23 | say why a fixed context vector fails on long sentences | 11 |
| 24 | give the shape of every tensor in the original Transformer and count its ~65M parameters | 12 |
| 25 | apply causal and padding masks correctly | 12 |
| 26 | derive why attention scores are divided by √d_k | 13 |
| 27 | show that sinusoidal position encodings make a shift a rotation | 13 |
| 28 | say why Pre-LN trains without warmup and Post-LN often does not | 13 |
| 29 | turn an image into ViT tokens and count ViT-B/16's parameters | 14 |
| 30 | say what inductive bias a CNN gets for free and what ViT pays in data to learn it | 14 |
| 31 | compare ResNeXt, DenseNet and SE blocks at one input shape | 15 |
| 32 | derive EfficientNet's compound-scaling constraint | 16 |
| 33 | attribute ConvNeXt's gains change by change | 17 |
| 34 | explain masked-language-model pretraining and why scaling went decoder-only | 18 |

## Parts

Every "Hook" number below is from memory of the primary source and **must be verified at research
time**. A hook whose number fails verification is rewritten; the number is never bent to fit.

### 1 · LeNet-5, Part 1 — How to Read a CNN: Every Shape, Parameter and FLOP by Hand

- **Slug:** lenet-5-every-number-by-hand
- **Tier:** L3 · **Difficulty:** beginner · **Est. words:** 6,500 · **Figures:** 10
- **Hook:** LeNet-5's C3 layer has 1,516 trainable parameters. Counted the way most tutorials count
  a conv layer, it would have 2,416. The gap is a connection table almost nobody draws.
- **Answers:** given any CNN's layer table, how do you compute every output shape, parameter count,
  multiply–accumulate count and receptive field yourself, and check them against the paper?
- **Assumes:** matrix multiplication, what a layer is, Python. Links image-processing Part 1 for
  convolution as filtering and does not re-teach it.
- **Owns (math):** output size ⌊(n + 2p − k)/s⌋ + 1; parameters (k²·C_in + 1)·C_out; MACs
  H_out·W_out·k²·C_in·C_out; the series' MACs-vs-FLOPs convention; the receptive-field recurrence;
  activation memory.
- **Hands off:** every gradient to Part 2. Fixed (non-learned) kernels stay with the image-processing
  series.
- **Worked example:** LeNet-5 traced from a 32×32 input to 10 outputs. Every layer's shape,
  parameters, connections and MACs go in one table whose columns sum to the paper's totals, with
  C3's connection table drawn and counted.
- **Signature figures:** V1 shape strip of LeNet-5 to scale; V4 receptive-field growth C1 → C5;
  V2 where parameters live (C5, F6) against where MACs live (C1, C3).
- **Traps:** S2/S4 are trainable subsampling layers with a coefficient and bias, not max-pools. The
  output layer is RBF, not softmax. "Seven layers" excludes the input.
- **Key sources:** LeCun, Bottou, Bengio & Haffner 1998 (Proc. IEEE); Dumoulin & Visin 2016
  (convolution arithmetic); Luo et al. 2016 (NeurIPS, effective receptive field).
- **Search intent:** "cnn output size formula", "how to calculate parameters in cnn", "receptive
  field calculation", "lenet-5 architecture"

### 2 · LeNet-5, Part 2 — Backpropagation Through a CNN, by Hand

- **Slug:** backpropagation-through-a-cnn-by-hand
- **Tier:** L4 · **Difficulty:** intermediate · **Est. words:** 8,000 · **Figures:** 13
- **Hook:** the gradient of a convolution is two more convolutions, one of them with the kernel
  turned upside down. It happens on nine numbers you can check.
- **Answers:** what exactly flows backward through convolution, pooling, activation and a
  softmax–cross-entropy head, and how do you prove your gradients right?
- **Assumes:** Part 1's counting rules (`#the-counting-rules`) and the chain rule.
- **Owns (math):** softmax–cross-entropy gradient p − y; ∂L/∂W as a correlation of the input with the
  output gradient; ∂L/∂x as a full convolution with the kernel rotated 180°; max-pool vs
  average-pool routing; stride and padding in the backward pass; gradient checking by central
  differences, and the float64 step size.
- **Hands off:** vanishing gradients across depth to Part 8 and across time to Part 10; normalisation
  gradients to Part 6.
- **Worked example:** the image-processing series' shared 5×5 patch (rows `40 40 40 200 200`, r2
  `40 255 40 200 200`), scaled to [0, 1], through one learned 3×3 conv, ReLU, a pool and a two-class
  softmax. Forward and backward, every value printed, and every gradient confirmed by finite
  differences. The exact geometry is fixed at outline so each step fits one screen.
- **Signature figures:** V3 forward and backward number grids drawn with mirrored geometry; V3 the
  rotated-kernel full convolution as small multiples; a gradient-check table captured from the lab.
- **Traps:** framework "convolution" is cross-correlation, so the flip appears in the backward pass,
  not the forward. The average-pool gradient divides by the window size. Max-pool ties need a rule.
- **Key sources:** Rumelhart, Hinton & Williams 1986 (Nature); LeCun et al. 1989 (Neural
  Computation); LeCun et al. 1998; Goodfellow, Bengio & Courville 2016, ch. 6 and 9.
- **Search intent:** "backpropagation in cnn by hand", "gradient of convolution layer", "backprop
  through max pooling", "softmax cross entropy gradient derivation"

### 3 · AlexNet — ReLU, Dropout, Two GPUs, and Why the Input Is 227 Pixels

- **Slug:** alexnet-by-the-numbers
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,500 · **Figures:** 10
- **Hook:** the paper says the input is 224×224. An 11×11 kernel at stride 4 on 224 pixels gives a
  first layer 54.25 pixels wide. Only 227 makes the arithmetic work.
- **Answers:** what did AlexNet change that let a CNN win ImageNet 2012 by a wide margin, and which
  of those changes survived?
- **Assumes:** Part 1's counting rules (`#the-counting-rules`). Links Part 2 for the ReLU and
  dropout gradients.
- **Owns (math):** ReLU's non-saturating derivative against tanh and sigmoid; dropout's inverted
  scaling as an expectation match, and its ensemble reading; grouped convolution as an accident of
  the two-GPU split; overlapping pooling; local response normalisation, and why it vanished;
  augmentation arithmetic; the ~60M parameter count reconciled.
- **Hands off:** depth to Part 4; normalisation to Part 6; multi-GPU parallelism as engineering to
  nvidia-stack Part 15.
- **Worked example:** the full layer table with the two-GPU towers drawn as groups, reconciled to
  the paper's "60 million parameters" and to torchvision's single-tower variant. Research establishes
  how far the two differ.
- **Signature figures:** V1 shape strip with both towers; V2 parameters vs MACs (the FC layers hold
  most of the parameters); V7 exact derivative curves for sigmoid, tanh and ReLU; V5 a measured toy
  run of ReLU vs tanh convergence beside the paper's reported CIFAR-10 speed-up.
- **Traps:** 224 vs 227. torchvision's AlexNet follows Krizhevsky's 2014 "one weird trick" variant,
  not the 2012 paper. One-CNN and ensemble results are different numbers.
- **Key sources:** Krizhevsky, Sutskever & Hinton 2012 (NeurIPS); Srivastava et al. 2014 (JMLR);
  Nair & Hinton 2010 (ICML); Krizhevsky 2014 (arXiv, one weird trick).
- **Search intent:** "alexnet architecture explained", "why relu instead of sigmoid", "how does
  dropout work", "alexnet 224 or 227"

### 4 · VGG — Why Stacked 3×3 Convolutions Won, and Where 138 Million Parameters Went

- **Slug:** vgg-3x3-convolutions-138-million-parameters
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 5,500 · **Figures:** 9
- **Hook:** VGG-16 has 138,357,544 parameters. 102,764,544 of them, about three in four, sit in
  one fully connected layer.
- **Answers:** why do two stacked 3×3 convolutions beat one 5×5, and what does depth cost in
  parameters, compute and memory?
- **Assumes:** Part 1's receptive-field recurrence (`#receptive-field`).
- **Owns (math):** receptive-field equivalence (two 3×3 = 5×5, three = 7×7) with the weight counts
  18C² vs 25C² and 27C² vs 49C²; the extra non-linearities; activation memory per image; the
  parameter wall in the classifier; why VGG trained shallow configurations first, the initialisation
  problem Part 8 solves.
- **Hands off:** the initialisation derivation to Part 8; the 1×1 answer to the parameter wall to
  Part 5.
- **Worked example:** VGG-16 (configuration D) traced stage by stage. Parameters and MACs are summed
  and reconciled, and activation memory is computed for one 224×224 float32 image.
- **Signature figures:** V2 parameters live in FC while MACs live in conv, the series' most striking
  asymmetry; V1 shape strip to scale; V4 5×5 vs two 3×3 receptive fields overlaid with the weight
  counts on the figure.
- **Traps:** VGG-16 is configuration "D" and VGG-19 is "E". Reported errors mix dense and multi-crop
  evaluation, so carry the protocol.
- **Key sources:** Simonyan & Zisserman 2015 (ICLR); Glorot & Bengio 2010 (AISTATS); Zeiler & Fergus
  2014 (ECCV).
- **Search intent:** "vgg16 architecture", "why 3x3 convolution", "vgg16 number of parameters",
  "two 3x3 vs one 5x5"

### 5 · GoogLeNet (Inception), Part 1 — 1×1 Convolutions and the Inception Module

- **Slug:** googlenet-inception-module-1x1-convolutions
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,500 · **Figures:** 10
- **Hook:** 22 layers deep, with about 12× fewer parameters than AlexNet. The trick is a convolution
  that looks at one pixel.
- **Answers:** what does a 1×1 convolution actually compute, and how does an Inception module spend
  a fixed compute budget across four branches?
- **Assumes:** Part 1's counting rules. Contrasts with VGG's parameter wall by link (Part 4) and does
  not depend on it.
- **Owns (math):** the 1×1 convolution as a per-pixel linear map across channels (Network in
  Network); the bottleneck saving for one module; branch concatenation shapes; auxiliary classifiers
  and their 0.3 loss weight; global average pooling in place of FC.
- **Hands off:** BatchNorm and factorised convolutions to Part 6; the bottleneck inside a residual
  block to Part 7.
- **Worked example:** module 3a (28×28×192 in, 28×28×256 out) counted with and without its 1×1
  reductions — MACs and parameters for every branch.
- **Signature figures:** V10 anatomy of module 3a with a shape on every edge and MACs on every node;
  V2 with vs without reductions; V9 the whole network (nine modules, stem and auxiliary heads — far
  past nine nodes, so Mermaid).
- **Traps:** "22 layers" counts parameterised layers only (27 with pooling). ~6.8M against "about
  7M". The ILSVRC 2014 result is a 7-model, 144-crop ensemble.
- **Key sources:** Szegedy et al. 2015 (CVPR); Lin, Chen & Yan 2014 (ICLR, Network in Network).
- **Search intent:** "1x1 convolution explained", "inception module explained", "googlenet
  architecture"

### 6 · Inception, Part 2 — Batch Normalization, Derived, and What Inception v3 Changed

- **Slug:** batch-normalization-derived-inception-v3
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 8,500 · **Figures:** 13
- **Hook:** batch normalisation made networks train far faster. The reason its paper gave, internal
  covariate shift, did not survive testing. What it actually does fits on one page of math.
- **Answers:** what does BatchNorm compute in training and at inference, what is its exact backward
  pass, and why does it help?
- **Assumes:** Part 2's backward-pass conventions (`#the-backward-pass`). Restates Part 5's module in
  two sentences.
- **Owns (math):** the BN forward pass (batch mean and variance, ε, γ, β); the full backward
  derivation; train vs eval running statistics and momentum; batch-size dependence; the
  loss-smoothing account (Santurkar et al. 2018) against internal covariate shift; label smoothing as
  cross-entropy with a mixed target; factorised n×1 · 1×n convolutions and their cost.
- **Hands off:** LayerNorm and its backward to Part 13; BN inside residual blocks to Part 7;
  zero-initialised γ to Part 8. Separability of fixed kernels stays with image-processing Part 4
  (link only).
- **Worked example:** a batch of four activations over two channels, normalised by hand forward and
  backward. The same numbers then go through eval mode with running statistics, showing the
  train/eval gap on real values.
- **Signature figures:** V3 BN forward and backward number grids; V5 a measured toy run with and
  without BN (loss and gradient norm); V7 label-smoothed targets and loss against logit margin.
- **Traps:** momentum conventions differ (PyTorch's 0.1 means new = 0.9·old + 0.1·batch; Keras
  uses 0.99). Biased vs unbiased variance. "Inception-v2" names two different networks across the BN
  and Rethinking papers.
- **Key sources:** Ioffe & Szegedy 2015 (ICML); Szegedy et al. 2016 (CVPR, Rethinking); Santurkar
  et al. 2018 (NeurIPS); Müller, Kornblith & Hinton 2019 (NeurIPS, label smoothing).
- **Search intent:** "batch normalization backward pass derivation", "batchnorm train vs eval",
  "label smoothing explained", "inception v3 factorized convolution"

### 7 · ResNet, Part 1 — The Degradation Problem and the Residual Block, Shape by Shape

- **Slug:** resnet-residual-block-shape-by-shape
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 7,000 · **Figures:** 11
- **Hook:** a 56-layer network has higher *training* error than a 20-layer one. It is not
  overfitting: the deeper network is worse on the very data it trains on.
- **Answers:** what problem did residual learning solve, and what exactly is inside ResNet-50, stage
  by stage?
- **Assumes:** Part 1's counting rules. Treats BatchNorm as a known layer, linking Part 6 and
  restating it in two sentences.
- **Owns (math):** the degradation problem; y = F(x) + x; identity vs projection shortcuts (options
  A, B and C); basic vs bottleneck block arithmetic; the stage layout of ResNet-18/34/50/101/152;
  ResNet-50's 25,557,032 parameters reconciled.
- **Hands off:** every "why it trains" argument to Part 8; ResNeXt, DenseNet and SE to Part 15; the
  mobile inversion to Part 9.
- **Worked example:** one 224×224×3 image through ResNet-50. The shape after the stem and after each
  of the 16 bottleneck blocks, with every projection shortcut marked, and parameters and MACs summed
  to torchvision's totals.
- **Signature figures:** V5 degradation replicated at toy scale — plain vs residual at equal depth,
  CPU, seed printed — beside the paper's reported curves; V10 bottleneck anatomy with a shape on
  every edge; V1 ResNet-50 shape strip; V9 the whole network in Mermaid.
- **Traps:** v1 vs v1.5 (torchvision puts the stride on the 3×3 conv, the paper on the first 1×1).
  The paper's "3.8 billion FLOPs" are multiply-adds. Shortcut options A, B and C change the count.
- **Key sources:** He, Zhang, Ren & Sun 2016 (CVPR); torchvision's `resnet.py` as the
  implementation reference; Goyal et al. 2017 (arXiv).
- **Search intent:** "resnet explained", "resnet50 architecture", "bottleneck block resnet",
  "degradation problem deep learning"

### 8 · ResNet, Part 2 — Why Residual Networks Train: Gradients, Paths, Landscapes and Initialisation

- **Slug:** why-residual-networks-train
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,500 · **Figures:** 16
- **Hook:** delete one block from a trained ResNet and accuracy barely moves. Do the same to VGG and
  it collapses. That one experiment says what a ResNet really is.
- **Answers:** why can a residual network train at hundreds of layers when a plain one cannot? The
  answer is given three ways: in gradients, in paths, and in the shape of the loss surface.
- **Assumes:** Part 7's residual block (`#the-residual-block`). Calculus and the variance of a sum.
- **Owns (math):** the identity-mapping gradient ∂L/∂x_l = ∂L/∂x_L · (1 + ∂/∂x_l Σ F), and why
  pre-activation keeps it clean; He initialisation Var[w] = 2/n_in, derived from ReLU halving the
  second moment; the ensemble-of-paths view, where path lengths are Binomial(n, ½); lesion
  experiments; filter-normalised loss-landscape slices; zero-initialised γ; the residual as an
  Euler step (one paragraph, linked).
- **Hands off:** hyper-connections, the 2025–26 generalisation of the residual stream, to Frontier
  Models (optional DeepSeek Part 4); vanishing gradients through time to Part 10.
- **Worked example:** a three-block residual stack with scalar weights, with the gradient reaching
  block 1 computed by hand with and without shortcuts. Then the exact path-length distribution for
  the 54-block network the ensemble paper studies.
- **Signature figures:** V6 loss-landscape slices of plain vs residual (toy, measured, identical
  contour levels); V5 per-layer gradient norm at initialisation for plain, residual and
  pre-activation; V7 exact binomial path-length distribution with the effective-path band; V7
  variance against depth under Xavier and He initialisation (exact); the lesion curve as reported.
- **Traps:** the ensemble view is not a literal ensemble, because paths share weights. A landscape
  plot is a 2-D slice of a million-dimensional surface, and the figure says so. He initialisation's
  fan-in vs fan-out modes.
- **Key sources:** He et al. 2016 (ECCV, identity mappings); He et al. 2015 (ICCV, rectifiers and
  initialisation); Veit, Wilber & Belongie 2016 (NeurIPS); Li et al. 2018 (NeurIPS, loss landscape);
  Balduzzi et al. 2017 (ICML, shattered gradients).
- **Search intent:** "why does resnet work", "resnet vanishing gradient", "kaiming initialization
  derivation", "loss landscape visualization", "pre-activation resnet"

### 9 · MobileNet — Depthwise Separable Convolutions and Inverted Residuals, Counted

- **Slug:** mobilenet-depthwise-separable-inverted-residuals
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,500 · **Figures:** 10
- **Hook:** splitting a 3×3 convolution into two cheaper ones cuts multiply-adds by 8–9×. It does
  not cut latency by 8–9×. Both facts are arithmetic.
- **Answers:** how do depthwise separable convolutions and inverted residuals shrink a CNN, and where
  does the saving stop showing up on real hardware?
- **Assumes:** Part 7's bottleneck block (`#the-bottleneck-block`), which MobileNetV2 inverts.
- **Owns (math):** the cost ratio 1/N + 1/k²; the width and resolution multipliers and their
  quadratic effect; inverted residuals with linear bottlenecks; the ReLU-in-low-dimensions argument;
  where the MACs move (to the 1×1 convolutions).
- **Hands off:** FLOPs vs latency on a GPU to nvidia-stack Part 5 (roofline); compound scaling to
  Part 16. Separable fixed filters stay with image-processing Part 4 (link).
- **Worked example:** one 3×3 layer at 14×14×512 → 512 counted standard vs separable, then one
  MobileNetV2 block (expansion 6) traced with shapes.
- **Signature figures:** V2 MAC share by layer type; V10 the inverted residual beside ResNet's
  bottleneck, where the "inversion" is visible as widths; V7 the low-dimensional ReLU experiment,
  recomputed as our own run.
- **Traps:** v1 vs v2 vs v3. Depthwise convolution's low arithmetic intensity. The naming of width
  multipliers.
- **Key sources:** Howard et al. 2017 (arXiv 1704.04861); Sandler et al. 2018 (CVPR); Chollet 2017
  (CVPR, Xception).
- **Search intent:** "depthwise separable convolution explained", "mobilenetv2 inverted residual",
  "why depthwise convolution is slow on gpu"

### 10 · LSTM — Vanishing Gradients and the Cell State That Carries Them

- **Slug:** lstm-vanishing-gradients-cell-state
- **Tier:** L4 · **Difficulty:** intermediate · **Est. words:** 9,000 · **Figures:** 14
- **Hook:** the 1997 LSTM had no forget gate. The gate everyone draws first was added three years
  later.
- **Answers:** why does a plain RNN forget, and which path through an LSTM lets a gradient survive
  a hundred steps?
- **Assumes:** Part 2's backward pass (`#the-backward-pass`); backpropagation through time is that
  pass, unrolled.
- **Owns (math):** BPTT; the product-of-Jacobians bound and the spectral-radius condition for
  vanishing and exploding gradients (the bound goes in a `<details>` block); gradient clipping; the
  gate and cell equations; the additive cell-state gradient path, linked to Part 8's identity path;
  the forget gate and its bias initialisation; GRU in one section.
- **Hands off:** encoder–decoders and attention to Part 11; selective state-space models to Frontier
  Models (Mamba), which assumes this part.
- **Worked example:** one LSTM cell with a two-dimensional hidden state, stepped three times on real
  numbers forward and backward, beside a plain RNN on the same inputs, with the gradient norm printed
  at every step.
- **Signature figures:** V5 measured gradient norm against time-step distance, RNN vs LSTM (toy,
  CPU); V10 the LSTM cell with shapes and the gradient highway highlighted; V3 number grids of the
  three-step trace; V7 exact |λ|ᵗ decay at spectral radii 0.9, 1.0 and 1.1.
- **Traps:** the 1997 and 2000 LSTMs differ. Peepholes. PyTorch keeps two bias vectors per gate.
  Gate order differs across frameworks.
- **Key sources:** Hochreiter & Schmidhuber 1997 (Neural Computation); Gers, Schmidhuber & Cummins
  2000 (Neural Computation); Bengio, Simard & Frasconi 1994 (IEEE TNN); Pascanu, Mikolov & Bengio
  2013 (ICML); Greff et al. 2017 (IEEE TNNLS); Cho et al. 2014 (EMNLP, GRU).
- **Search intent:** "lstm explained", "vanishing gradient problem rnn", "why lstm solves vanishing
  gradient", "lstm vs gru"

### 11 · Seq2seq and Bahdanau Attention — Where Attention Came From

- **Slug:** seq2seq-bahdanau-attention
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,000 · **Figures:** 10
- **Hook:** squeeze a 50-word sentence into one fixed vector and translation quality falls off a
  cliff as sentences get longer. Attention was the fix: let the decoder look back.
- **Answers:** what problem did attention solve in encoder–decoder models, and how is an alignment
  computed?
- **Assumes:** Part 10's LSTM (`#the-lstm-cell`).
- **Owns (math):** the encoder–decoder with a fixed context vector; the length bottleneck; additive
  (Bahdanau) and multiplicative (Luong) scoring; the alignment softmax and context vector; teacher
  forcing; greedy vs beam decoding.
- **Hands off:** queries, keys, values and self-attention to Part 12. Beam search as a search
  algorithm goes to search-algorithms (optional Part 18), linked only once that is live.
- **Worked example:** a four-word source and four-word target, with additive scores, the softmax and
  the context vector computed by hand at every decoder step.
- **Signature figures:** V8 an alignment heatmap, hand-worked first and then from a small trained toy
  model (measured); V3 the score computations; the encoder–decoder map, routed at outline.
- **Traps:** Bahdanau scores with the previous decoder state and Luong with the current one. A
  bidirectional encoder doubles the annotation width.
- **Key sources:** Sutskever, Vinyals & Le 2014 (NeurIPS); Cho et al. 2014 (EMNLP); Bahdanau, Cho &
  Bengio 2015 (ICLR); Luong, Pham & Manning 2015 (EMNLP).
- **Search intent:** "attention mechanism explained", "bahdanau attention", "seq2seq model
  explained", "bahdanau vs luong attention"

### 12 · Transformer, Part 1 — Attention Is All You Need, Shape by Shape

- **Slug:** transformer-shape-by-shape
- **Tier:** L4 · **Difficulty:** intermediate · **Est. words:** 8,000 · **Figures:** 14
- **Hook:** the base Transformer has about 65 million parameters. By the end of this post the reader
  will have counted every one.
- **Answers:** what is every tensor in the original Transformer, from token id to output
  probability, and what does each block do to it?
- **Assumes:** Part 11's alignment (`#the-alignment-softmax`), restated as query–key–value in three
  sentences.
- **Owns (math):** embeddings scaled by √d_model; the sinusoidal encoding (definition only);
  scaled dot-product attention shapes; the multi-head split and merge; causal and padding masks; the
  position-wise FFN; residual + Post-LN placement; encoder–decoder cross-attention; shared
  embeddings; the base model's parameter count.
- **Hands off:** √d_k, the encoding's properties, LayerNorm placement and complexity to Part 13;
  decoder-only models to Frontier Models GPT Part 1; images to Part 14.
- **Worked example:** a four-token sentence at d_model = 8 with two heads of d_k = 4, printing every
  Q, K, V, score, mask, softmax and output. Then the same computation at base size (d_model 512,
  8 heads), shapes only. **These toy numbers are the series' shared attention example** — Part 13 and
  Frontier Models reuse them.
- **Signature figures:** V9 the whole model with a shape on every edge (Mermaid); V8 hand-worked
  attention heatmaps per head; V1 the token-strip variant (T × d) through one layer; V2 where the 65M
  parameters live.
- **Traps:** the original is Post-LN; d_ff is 2048 at base size; the source and target share a BPE
  vocabulary and embeddings; the row-vector convention (XW) is fixed series-wide.
- **Key sources:** Vaswani et al. 2017 (NeurIPS); Phuong & Hutter 2022 (Formal Algorithms for
  Transformers); Rush 2018 (The Annotated Transformer) as an implementation cross-check.
- **Search intent:** "transformer architecture explained", "attention is all you need explained",
  "multi head attention shapes", "transformer parameter count"

### 13 · Transformer, Part 2 — The Math: √d_k, Positional Encodings and Where LayerNorm Goes

- **Slug:** transformer-math-derived
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,500 · **Figures:** 15
- **Hook:** divide by √d_k — not by d_k, and not by nothing. The reason is one line of variance
  arithmetic, and skipping it saturates the softmax.
- **Answers:** why is each of the Transformer's design constants what it is, and what breaks when you
  change it?
- **Assumes:** Part 12's shapes (`#scaled-dot-product-attention`). Expectation, variance, the
  softmax Jacobian.
- **Owns (math):** Var(q·k) = d_k and softmax saturation; the softmax Jacobian; attention as kernel
  smoothing; the permutation-equivariance proof and why position must be injected; the sinusoidal
  shift property (PE at p + k is a rotation of PE at p — the seed of RoPE); O(T²d) vs O(Td²) and
  their crossover; the LayerNorm forward and backward; the Post-LN vs Pre-LN gradient analysis; the
  warmup schedule formula.
- **Hands off:** RoPE and context extension to Frontier Models Llama Part 2; the KV cache to
  nvidia-stack Part 11; linear-time alternatives to Frontier Models Mamba and Gated DeltaNet.
- **Worked example:** Part 12's four-token toy reused, with attention recomputed at scales 1, √d_k
  and d_k to show saturation, and the rotation property checked numerically for one position shift.
- **Signature figures:** V7 exact distributions of q·k at d_k = 4, 64 and 512, with and without
  scaling; the encoding as rotating 2-D pairs across wavelengths; V5 measured toy Post-LN vs Pre-LN
  gradient norms per layer, with and without warmup; V7 the exact T²d vs Td² crossover.
- **Traps:** the paper's schedule is d_model^−0.5 · min(step^−0.5, step · warmup^−1.5) with 4,000
  warmup steps. Libraries disagree on Pre-/Post-LN placement and LayerNorm's ε.
- **Key sources:** Vaswani et al. 2017; Ba, Kiros & Hinton 2016 (LayerNorm); Xiong et al. 2020
  (ICML); Liu et al. 2020 (EMNLP, difficulty of training Transformers); Tsai et al. 2019 (EMNLP,
  attention as a kernel).
- **Search intent:** "why scale by sqrt dk", "positional encoding explained", "pre-ln vs post-ln
  transformer", "transformer time complexity"

### 14 · ViT — An Image Is 196 Tokens

- **Slug:** vision-transformer-vit
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 7,000 · **Figures:** 12
- **Hook:** cut a 224×224 image into 16×16 patches and you have 196 tokens. Trained on ImageNet
  alone, that model loses to a ResNet. Trained on 300 million images, it wins.
- **Answers:** how does a Transformer read an image, and why does it need so much more data than a
  CNN to match one?
- **Assumes:** Part 12's encoder (`#the-encoder-block`). Contrasts with ResNet (Part 7) by link.
- **Owns (math):** patch embedding as a 16×16, stride-16 convolution; the class token; learned
  position embeddings and 2-D interpolation for a new resolution; ViT-B/16's ~86M parameters
  reconciled; inductive bias (locality, translation equivariance) as what a CNN gets for free; the
  data regime (ImageNet-1k vs 21k vs JFT-300M); DeiT's recipe in one section; mean attention
  distance by layer.
- **Hands off:** JEPA, CLIP and every ViT-based model to Frontier Models; diffusion transformers to
  diffusion-models Part 4; ConvNeXt's reply to Part 17.
- **Worked example:** the series' shared image (chosen at Part 1's research) patchified into 196
  vectors of 768 values and embedded, then one real CPU forward pass of pretrained ViT-B/16, with the
  last layer's class-token attention.
- **Signature figures:** V1 token strip (patches → tokens → 197×768); V8 real class-token attention
  per head (measured); V4 mean attention distance per layer and head (measured), set against Part 1's
  receptive-field growth; V12 the lineage map where the two tracks meet (Mermaid).
- **Traps:** 224 vs 384 input (577 tokens). JFT is private. Reported accuracy depends on the
  pretraining set and resolution, so carry the protocol.
- **Key sources:** Dosovitskiy et al. 2021 (ICLR); Touvron et al. 2021 (ICML, DeiT); Raghu et al.
  2021 (NeurIPS).
- **Search intent:** "vision transformer explained", "vit patch embedding", "vit vs cnn", "why vit
  needs more data"

### 15 (optional) · After ResNet — ResNeXt, DenseNet and Squeeze-and-Excitation

- **Slug:** resnext-densenet-senet
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,500 · **Figures:** 10
- **Answers:** what are the three ways the residual block was generalised — width by groups,
  connection by concatenation, channels by gating — and what does each cost?
- **Assumes:** Part 7 (`#the-bottleneck-block`).
- **Owns (math):** cardinality and grouped-convolution arithmetic; DenseNet's growth rate and
  concatenation memory; the SE block's squeeze (global pooling) and excitation (FC–ReLU–FC–sigmoid,
  r = 16), the first channel attention.
- **Worked example:** one block of each at one input shape, with parameters and MACs compared.
- **Key sources:** Xie et al. 2017 (CVPR); Huang et al. 2017 (CVPR); Hu, Shen & Sun 2018 (CVPR).
- **Search intent:** "resnext vs resnet", "densenet explained", "squeeze and excitation block"

### 16 (optional) · EfficientNet — Compound Scaling, Derived

- **Slug:** efficientnet-compound-scaling
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 5,500 · **Figures:** 9
- **Answers:** given twice the compute, how should depth, width and resolution each grow?
- **Assumes:** Part 9's MBConv block (`#inverted-residuals`).
- **Owns (math):** FLOPs ∝ d·w²·r²; the constraint α·β²·γ² ≈ 2; the grid search at φ = 1; B0 → B7.
- **Key sources:** Tan & Le 2019 (ICML); Tan & Le 2021 (ICML, EfficientNetV2).
- **Search intent:** "efficientnet explained", "compound scaling"

### 17 (optional) · ConvNeXt — A ResNet Modernised, One Change at a Time

- **Slug:** convnext-resnet-modernised
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,000 · **Figures:** 10
- **Answers:** how much of ViT's advantage was the Transformer, and how much was a training recipe and
  a handful of design choices a CNN can copy?
- **Assumes:** Part 7; links Part 14.
- **Owns (math):** the modernisation roadmap as a ledger of reported accuracy deltas; 7×7 depthwise
  convolution, the inverted bottleneck, LayerNorm, GELU, fewer norms and activations.
- **Key sources:** Liu et al. 2022 (CVPR); Woo et al. 2023 (CVPR, ConvNeXt V2).
- **Search intent:** "convnext explained", "convnext vs vit"

### 18 (optional) · BERT — The Encoder-Only Branch

- **Slug:** bert-encoder-only-transformer
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,500 · **Figures:** 10
- **Answers:** what does an encoder-only Transformer learn from masked-token prediction, and why did
  scaling go decoder-only instead?
- **Assumes:** Part 12 (`#the-encoder-block`).
- **Owns (math):** MLM at 15% with the 80/10/10 rule; next-sentence prediction and RoBERTa's removal
  of it; [CLS] and segment embeddings; BERT-base's ~110M reconciled; fine-tuning heads.
- **Hands off:** decoder-only models to Frontier Models GPT Part 1; masked image modelling to
  Frontier Models JEPA Part 1 (the MAE contrast).
- **Key sources:** Devlin et al. 2019 (NAACL); Liu et al. 2019 (arXiv, RoBERTa).
- **Search intent:** "bert explained", "masked language model", "bert vs gpt"

## Visual system

This is the part of the plan that makes the series precise, not pretty. Plain boxes and arrows are
the weakest figure an ML post can carry. Here a block diagram is allowed only when every edge
carries a tensor shape and every node carries its operation and parameter count, and most figures
are not block diagrams at all. The families below are drawn by **shared generators** copied into
each part's `assets/` (house rule: copy, don't import across posts). Readers learn to read a V1
strip once and can then read it in every part.

| Code | Family | What it must show | Route | Precision rule |
|---|---|---|---|---|
| V1 | Shape strip | every activation as a block, H and W linear, C on a printed log₂ scale, exact shape under each, stride and padding on each edge; the token variant draws T × d | `placed` (Q4) | generated from the lab's layer table, so drawing and count cannot disagree |
| V2 | Where parameters vs compute live | paired stacked bars of parameters and MACs by layer group, zero baseline, paper total and our total with the delta printed | `chart` | computed numbers only; convention (MACs vs FLOPs) in the axis title |
| V3 | Number grid | the hand-worked tensors with every cell printed, the active window highlighted and linked to the cell it produces; backward drawn in the same geometry as forward | `placed` | small multiples, never animation — the renderer shows static images |
| V4 | Receptive field | theoretical receptive field as nested squares per layer, beside the measured effective receptive field (input-gradient heatmap) | `plot` | theoretical and measured never share a mark without a legend |
| V5 | Training dynamics | per-layer gradient norms (log y), training-error curves, from our CPU runs | `plot` | caption carries the setup line: model, width, depth, seed, steps, framework version; never presented as the paper's experiment |
| V6 | Landscape slice | filter-normalised 2-D loss contours, plain vs residual, same axes and levels | `plot` | the figure says it is a 2-D slice |
| V7 | Exact curves and distributions | anything computed exactly — binomial paths, variance vs depth, q·k spread, derivative curves | `plot` | caption says "exact computation" vs "sampled, n = …" |
| V8 | Attention / alignment heatmap | queries × keys, one sequential colour map 0–1 with a colour bar, masked cells hatched, per-head small multiples | `plot` | row sums of 1 stated; source (hand-worked, toy-trained or pretrained) in the caption |
| V9 | Whole-model map | the one end-to-end view per part, shape on every edge, parameters on every node | `mermaid` (Q3) | at most one per part; never split in two to fit |
| V10 | Block anatomy | one block (≤ 9 nodes) with shapes, operations, parameter counts and a printed "why" verdict | `placed` | the verdict names what breaks without the component |
| V12 | Lineage map | which component each model introduced and who inherited it | `mermaid` | drawn once, in Part 14, where the tracks meet |

(V11 is reserved and V13–V24 belong to the frontier series. The codes are unique across both
series so the shared context files never collide.)

Rules that apply to every figure in the series:

1. **Every number has one of three provenances, and the caption says which.** *Computed* means a
   deterministic lab script working from the published configuration. *Measured* means our own run,
   with its setup line. *Reported* means a ledger row from the paper, with its protocol. A single mark
   never mixes provenances without a legend.
2. **To scale means the scale is printed.** A strip without its scale bar fails review.
3. **One sequential colour map** for probabilities and attention, and **one diverging map centred
   on zero** for signed values (gradients, weights). Both are fixed at Part 1 and never changed. The
   accent colour marks the one thing the figure is about.
4. **Equations stay in KaTeX, never in images.** A figure may print the substituted numbers of a
   worked instance; the symbolic form lives in the prose.
5. **Figure scripts import the lab's numbers** — the pattern nvidia-stack Part 3 set — so prose,
   figure and lab cannot disagree.
6. **Paper figures take the `source` route only with a verified licence.** Most of these papers sit
   under arXiv's default licence, which grants no reuse. No lookalike redraws of a paper's famous
   diagram: our figure must carry our own analysis (shapes, counts, measurements).
7. **Every rendered PNG is opened and read before the gate**, checking arithmetic, arrow ownership,
   label collisions and legend-to-mark agreement. The validator cannot see any of it.

## Math ownership

Each derivation lives in exactly one part. Everyone else links to it by anchor and restates the
result in one line at most.

| Derivation | Owner | Linked from |
|---|---|---|
| output size, parameters, MACs, receptive field, the FLOP convention | 1 | every part |
| convolution / pooling / softmax–cross-entropy gradients, gradient checking | 2 | 6, 10 |
| dropout expectation, ReLU vs saturating derivatives, grouped conv | 3 | 15 |
| stacked-3×3 equivalence, activation memory | 4 | 5 |
| 1×1 bottleneck saving | 5 | 7, 9 |
| BatchNorm forward/backward, label smoothing, factorised conv | 6 | 7, 8, 13 |
| residual formulation, bottleneck arithmetic, projection shortcuts | 7 | 8, 9, 15, 17 |
| identity-gradient decomposition, He init, path ensemble, landscapes | 8 | 10, frontier |
| depthwise-separable ratio, linear bottleneck | 9 | 16, 17 |
| BPTT, Jacobian-product bound, LSTM cell gradient | 10 | 11, frontier (Mamba) |
| additive / multiplicative alignment | 11 | 12 |
| attention shapes, heads, masks, parameter count | 12 | 13, 14, 18, frontier |
| √d_k, softmax Jacobian, PE shift, equivariance, complexity, LayerNorm, Pre/Post-LN | 13 | 14, frontier |
| patch embedding, position-embedding interpolation, inductive bias | 14 | 17, frontier |

## Conventions printed beside every number

These are the places where honest sources disagree, and the series names the convention every
time instead of picking one silently.

- **MACs vs FLOPs.** We count multiply–accumulates (MACs) and write FLOPs = 2 × MACs. Many papers
  write "FLOPs" and mean multiply-adds (ResNet's 3.8 billion is one of them). State which, every time.
- **Parameter totals** say whether biases, BN parameters and running statistics are included.
  Running statistics are buffers, not parameters.
- **Layout** is N × C × H × W for images and B × T × d for sequences, with the row-vector
  convention y = xW.
- **Accuracy** always carries top-1/top-5, crop protocol, resolution and dataset split.
- **Architecture versions** always carry their variant: ResNet v1/v1.5, AlexNet 2012/2014,
  VGG configuration letter, LSTM 1997/2000.

## Publication order and cadence

Reading order is the numbering. Build order is in waves.

- **Wave 1 — the conventions and the named models:** 1 (LeNet-5 Part 1), then 7 and 8 (ResNet),
  12 and 13 (Transformer), 14 (ViT). Part 1 goes first because it fixes the counting convention and
  builds the V1/V2 generators and the Tier A counting lab that every later part copies.
- **Wave 2 — the rest of the vision track:** 2, 3, 4, 5, 6.
- **Wave 3:** 9, 10, 11, then the optional parts as the user chooses.

Publish in dependency order even when building out of order: a part never links forward to an
unpublished post. The frontier series' GPT Part 1 links to Part 12, so Part 12 should be live before
it. One part a week; once the frontier series opens, alternate between the two.

## Cross-links

- **Within the series:** each part links back to at most one prerequisite anchor, plus the parts in
  the Math ownership table it uses. The Part 2 of a two-part model links to its Part 1. No forward
  links to unpublished posts.
- **image-processing:** Parts 1 and 2 link image-processing Part 1 (convolution by hand), and Part 2
  reuses its shared 5×5 patch on purpose, so readers of both see the same numbers go through a fixed
  kernel and then a learned one. Parts 6 and 9 link image-processing Part 4 for separability of fixed
  kernels.
- **nvidia-stack:** Part 9 links Part 5 (roofline) for FLOPs vs latency. Part 3 links Part 15
  (parallelism) for the two-GPU split.
- **diffusion-models:** Part 7 and Part 14 link diffusion Part 4 (backbones: U-Net, DiT). This
  series never covers U-Net or DiT.
- **search-algorithms:** Part 11 links optional Part 18 (beam search) only if it is live.
- **frontier-models:** that series assumes Parts 10, 12 and 14, and its optional DeepSeek Part 4
  continues Part 8's residual-stream story. Links go from there to here, not the other way, until
  those parts are live.

All links use the canonical `https://canery.in/blogs/<slug>#<anchor>` form, never a local path.

## The lab policy

The authoring machine has 16 CPU cores, 14 GB RAM and no NVIDIA GPU. Nothing numeric is installed
in the system Python or the repo's `.venv`, and `uv` is available. So labs come in two tiers, and
every lab README states its tier:

- **Tier A — standard library only**, like every existing series. It covers layer counting,
  hand-worked numbers and exact distributions, runs anywhere and feeds figures directly.
- **Tier B — CPU PyTorch in a per-series `uv` environment with pinned versions.** It covers toy-scale
  training runs (degradation, gradient flow, landscapes, BN, Pre/Post-LN) and forward passes with
  public pretrained weights (torchvision ResNet-50 and VGG-16, a ViT-B/16). Results are written to
  JSON committed beside the script, and the figure builder reads that JSON with the standard library,
  so rebuilding a figure never needs torch.

Paper-scale numbers (ImageNet accuracy, training curves at full size) come **only** from the ledger.
Nothing is trained at ImageNet scale here, and no toy result is ever presented as the paper's. Each
pretrained checkpoint's licence is recorded before its output appears in a figure.

## Open decisions for the user

1. **Two series or one?** Recommended: two (see *Why two series*). The adjacent option is one series
   with two tracks, which costs one word.
2. **The name.** "Foundational Architectures", not "Foundation Models" — see above.
3. **Tier B labs.** They need torch (CPU) installed through `uv`, which departs from the stdlib-only
   labs so far. Without them, V4 (measured), V5, V6 and V8 (pretrained) become computed-only or
   drop, and the series loses its "measured" pillar.
4. **Optional parts 15–18:** which, if any, are committed.
5. **First build:** Part 1 is recommended. The adjacent option is to start with ResNet Part 1
   (Part 7), restating the counting rules briefly.

## What this series will not cover

Detection and segmentation heads (the R-CNN family, YOLO); U-Net and diffusion backbones
(diffusion-models owns them); GANs and VAEs; graph neural networks; reinforcement learning;
training-recipe tuning as a subject; framework tutorials; GPU and hardware behaviour (nvidia-stack
owns it); and any model from the frontier series. Each part also declines to reproduce
ImageNet-scale training — the machine cannot, and a toy run labelled as the real one would be the
worst error this series could make.
