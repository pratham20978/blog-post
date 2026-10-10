---
social_schema: 2
canonical_url: "https://canery.in/blogs/what-the-nvidia-stack-actually-is"
---
# Social publishing package — what-the-nvidia-stack-actually-is

## LinkedIn post

You type `pip install torch`, several gigabytes land in a virtualenv, and you still cannot answer whether the box needs the CUDA Toolkit.

That is not ignorance. It is a missing map. “CUDA” is used for at least five separately built, separately versioned, separately shipped artifacts, and none of them announces which one you are looking at.

I resolved the whole dependency graph of one `pip install torch` on a laptop with no NVIDIA GPU. It comes to 32 packages, 90 shared libraries and 4.86 GB of compiled code — and not one byte of it is the library that actually talks to the GPU.

What the carousel covers:

- the seven layers, each with the file it puts on disk and the product that ships it;
- one matrix multiply traced down nine steps, from `torch.matmul` to `cublasSgemm`;
- why nothing installs this stack — the dynamic loader assembles it inside site-packages at import time;
- why cuBLAS, which runs your matmul, is not a declared dependency of PyTorch at all;
- the rule that falls out of it: you need the Toolkit to build device code, not to run someone else's.

Everything above the driver is negotiable. The driver is not.

## LinkedIn first comment

The lab needs nothing but `python3` and a network connection — no GPU, no driver, no Toolkit. It lists a 554 MB wheel after transferring 1.2 MB, then maps every library the binaries request to the wheel that provides it. Exactly one comes back unresolved, and that one is the whole argument.

Read the full article on Canery: https://canery.in/blogs/what-the-nvidia-stack-actually-is

## Instagram caption

There is no single artifact called CUDA.

It is a kernel driver, a user-mode driver library, a runtime, a compiler toolchain and a portfolio of math libraries — built by different teams, released on different schedules, delivered by four different products.

Only one of them has to come from your machine. Everything else arrives in a Python wheel and gets stitched together by the dynamic loader the moment you import torch.

Swipe for the map, the traced call, and the one library pip can never give you.

Full article and the no-GPU lab on Canery — link in bio.

#CUDA #NVIDIA #PyTorch #GPU #MLSystems #Python

## Shared feed order

1. `assets/social/feed-01-there-is-no-cuda.png` — One word covers five separately built, separately versioned artifacts shipped by four different products.
2. `assets/social/feed-02-only-one-layer-is-mandatory.png` — Thirty-two packages resolve inside the virtualenv; the library at the bottom of every chain does not.
3. `assets/social/feed-03-nothing-installs-this-stack.png` — The dynamic loader assembles the CUDA stack from sibling directories inside site-packages at import time.
4. `assets/social/feed-04-one-release-three-majors.png` — Component wheels inside one CUDA Toolkit release carry major numbers 10, 12 and 13.
5. `assets/social/feed-05-cublas-arrives-sideways.png` — cuBLAS runs the matrix multiply and reaches the machine as a dependency of cuDNN, not of PyTorch.
6. `assets/social/feed-06-read-the-wheel-first.png` — A 554 MB wheel can be listed in full after 1.2 MB of transfer, with no GPU present.

Post as one carousel on Instagram and the same six images on LinkedIn. The ordering is an
argument: name the problem, state the thesis, show the mechanism, prove it, surprise, then hand
over the tool.

## Instagram Story

Run the four frames as a sequence within a day of the feed post. Frame 4 carries the link sticker.

- CTA: Read the full article on Canery
- Link sticker label: Read the article
- Link sticker URL: https://canery.in/blogs/what-the-nvidia-stack-actually-is

### Story order

1. `assets/social/story-01-five-things-called-cuda.png` — Overlay: Five things are called “CUDA”.
2. `assets/social/story-02-the-layer-map.png` — Overlay: Seven layers. Four shippers.
3. `assets/social/story-03-read-the-wheel.png` — Overlay: The summary and the wheel disagree.
4. `assets/social/story-04-read-the-full-article.png` — Overlay: Learn the map before the failures.

## Asset metadata

### feed-01-there-is-no-cuda

- File: `assets/social/feed-01-there-is-no-cuda.png`
- Title: There is no single CUDA
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: The word covers five separately versioned artifacts shipped by four different products.
- Technical source: The problem: five different things are called “CUDA”; Figure 1
- Visual structure: Canery lockup and sequence number lead into a two-line hook, five stacked artifact rows with the two host-supplied ones in the accent, and a closing rule.
- Visible-text transcript: Canery.in; 01 / 06; There is no single CUDA.; A kernel driver, a user-mode driver, a runtime, a compiler and a library portfolio. Four shippers, four schedules.; KERNEL MODULES; nvidia.ko · nvidia-uvm.ko; USER-MODE DRIVER; libcuda.so.1; CUDA RUNTIME; libcudart.so.13; COMPILER TOOLCHAIN; nvcc · ptxas · nvlink; ACCELERATED LIBRARIES; libcublas.so.13 · libcudnn.so.9; five separately versioned artifacts, one word; Stop asking which CUDA version you have. Ask which artifact you are looking at.; WHAT THE NVIDIA STACK ACTUALLY IS · CANERY.IN
- Alt text: Five rows naming the artifacts called CUDA, with the kernel modules and libcuda.so.1 highlighted as the two that must come from the host.
- Long description: Five labelled rows list the artifacts the word CUDA covers: kernel modules, the user-mode driver, the CUDA runtime, the compiler toolchain and the accelerated libraries, each with the file it puts on disk. The top two rows are highlighted because they are the only ones the host machine must supply.
- Keywords: NVIDIA software stack, CUDA driver, CUDA runtime, CUDA Toolkit, libcuda.so
- Canonical URL: https://canery.in/blogs/what-the-nvidia-stack-actually-is

### feed-02-only-one-layer-is-mandatory

- File: `assets/social/feed-02-only-one-layer-is-mandatory.png`
- Title: Only one layer must be on the box
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Thirty-two packages resolve inside the virtualenv; the library at the bottom of every chain does not.
- Technical source: Intuition: nothing installs this stack; Figure 7
- Visual structure: A focal card for libcuda.so.1, two contrasting cards for what pip can and cannot deliver, and a measured footer.
- Visible-text transcript: Canery.in; 02 / 06; Only one layer must be on the box.; Thirty-two packages resolve inside the virtualenv. The library at the bottom of every chain does not.; the host must supply this; libcuda.so.1; named by your framework's binaries; shipped by no wheel, ever; negotiable; pip can deliver; cuBLAS · cuDNN · NCCL; the CUDA runtime; nvcc, if you ask; not negotiable; pip cannot; the kernel modules; the user-mode driver; nothing substitutes; 4.86 GB of wheels; and none of it talks to the GPU; Everything above the driver is negotiable. The driver is not.; WHAT THE NVIDIA STACK ACTUALLY IS · CANERY.IN
- Alt text: libcuda.so.1 shown as the one library no Python wheel ships, beside lists of what pip can and cannot deliver.
- Long description: A highlighted card names libcuda.so.1 as the library PyTorch's binaries require and no wheel provides. Two cards below split the stack into what pip can deliver, including cuBLAS, cuDNN, NCCL and the CUDA runtime, and what it cannot: the kernel modules and the user-mode driver. A footer records 4.86 GB of wheels, none of which talks to the GPU.
- Keywords: libcuda.so.1, NVIDIA driver, pip wheels, CUDA runtime, GPU dependencies
- Canonical URL: https://canery.in/blogs/what-the-nvidia-stack-actually-is

### feed-03-nothing-installs-this-stack

- File: `assets/social/feed-03-nothing-installs-this-stack.png`
- Title: Nothing installs this stack
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: The dynamic loader assembles the CUDA stack inside site-packages at import time.
- Technical source: Intuition: nothing installs this stack; Implementation
- Visual structure: A code panel showing the real DT_RPATH entries from PyTorch's libraries, then a focal card naming the mechanism.
- Visible-text transcript: Canery.in; 03 / 06; Nothing installs this stack.; Your CUDA install is a set of independently downloaded wheels that the dynamic loader stitches together.; what pytorch's own libraries carry; DT_RPATH; $ORIGIN/../../nvidia/cudnn/lib; $ORIGIN/../../nvidia/nccl/lib; $ORIGIN/../../nvidia/cu13/lib; $ORIGIN; every time you import torch; The loader assembles it; not the installer, not pip; resolved again, at import, by filename; Resolution happens twice: once by pip, once by the loader, on different rules.; WHAT THE NVIDIA STACK ACTUALLY IS · CANERY.IN
- Alt text: The DT_RPATH entries baked into PyTorch's shared libraries, all pointing at sibling directories inside site-packages.
- Long description: A code panel lists the DT_RPATH search path compiled into PyTorch's own shared libraries: four nvidia subdirectories under site-packages plus $ORIGIN. A card below explains that the dynamic loader, not the installer, assembles the CUDA stack from those directories each time torch is imported.
- Keywords: DT_RPATH, dynamic loader, site-packages, PyTorch CUDA, shared libraries
- Canonical URL: https://canery.in/blogs/what-the-nvidia-stack-actually-is

### feed-04-one-release-three-majors

- File: `assets/social/feed-04-one-release-three-majors.png`
- Title: One Toolkit, nine version streams
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Component versions inside a single CUDA Toolkit release carry major numbers 10, 12 and 13.
- Technical source: What is in the CUDA Toolkit, and do you need it?; Figure 5
- Visual structure: Five component rows from the cuda-toolkit meta-package with their own versions, the highest and lowest in the accent.
- Visible-text transcript: Canery.in; 04 / 06; One Toolkit. Nine version streams.; Every component of a CUDA release carries its own version number, and they disagree with the release.; inside cuda-toolkit==13.0.3; nvidia-cublas; 13.1.1.3; nvidia-cuda-runtime; 13.0.96; nvidia-cusparse; 12.6.3.3; nvidia-cufft; 12.0.0.61; nvidia-curand; 10.4.0.35; majors 10, 12 and 13 in one release; No single number is “the CUDA version”. Name the artifact, then name its version.; WHAT THE NVIDIA STACK ACTUALLY IS · CANERY.IN
- Alt text: Five CUDA Toolkit component wheels listed with versions ranging from 10.4.0.35 to 13.1.1.3 inside one 13.0.3 release.
- Long description: Five component wheels from the cuda-toolkit 13.0.3 meta-package are listed with their own version numbers: cuBLAS at 13.1.1.3, the CUDA runtime at 13.0.96, cuSPARSE at 12.6.3.3, cuFFT at 12.0.0.61 and cuRAND at 10.4.0.35. The highest and lowest are highlighted to show that three different major numbers ship inside one release.
- Keywords: CUDA Toolkit versions, cuda-toolkit meta-package, cuBLAS version, component wheels
- Canonical URL: https://canery.in/blogs/what-the-nvidia-stack-actually-is

### feed-05-cublas-arrives-sideways

- File: `assets/social/feed-05-cublas-arrives-sideways.png`
- Title: cuBLAS is not a dependency of torch
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: The library that runs the matrix multiply arrives transitively through cuDNN.
- Technical source: What is CUDA-X, and which of it are you already using?; Figure 6
- Visual structure: Three stacked cards tracing torch to cuDNN to cuBLAS, with the last in the accent.
- Visible-text transcript: Canery.in; 05 / 06; cuBLAS is not a dependency of torch.; The library that actually multiplies your matrices arrives because cuDNN happens to depend on it.; what you installed; torch; declares cuda-toolkit[…11] and four -cu13 wheels; pulled in; nvidia-cudnn-cu13; declared by torch, for convolutions; never asked for; nvidia-cublas; 545 MB of libcublasLt.so.13; the library that runs your matmul; You are already using CUDA-X libraries you never installed and cannot name.; WHAT THE NVIDIA STACK ACTUALLY IS · CANERY.IN
- Alt text: A three-step dependency chain from torch through nvidia-cudnn-cu13 to nvidia-cublas, which no one declared directly.
- Long description: Three stacked cards trace a dependency chain: torch declares cuda-toolkit with eleven extras and four suffixed wheels, one of which is nvidia-cudnn-cu13, which in turn depends on nvidia-cublas. The final card is highlighted because cuBLAS, the library that executes the matrix multiply, is never requested directly.
- Keywords: cuBLAS, cuDNN, transitive dependency, CUDA-X, PyTorch packaging
- Canonical URL: https://canery.in/blogs/what-the-nvidia-stack-actually-is

### feed-06-read-the-wheel-first

- File: `assets/social/feed-06-read-the-wheel-first.png`
- Title: List a 554 MB wheel with 1.2 MB
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: The whole stack can be inspected before any of it is installed, with no GPU present.
- Technical source: Implementation: read the stack before you install it; Lab downloads
- Visual structure: A terminal panel with the real captured output, then a focal card naming the three techniques.
- Visible-text transcript: Canery.in; 06 / 06; List a 554 MB wheel with 1.2 MB.; The whole stack can be inspected before any of it is installed, on a laptop with no NVIDIA GPU.; no gpu, no driver, no toolkit; $ python3 inspect_wheel.py torch 2.14.0; download size  554.6 MB; entries        13,043; cost to list   3 range requests, 1.2 MB; tier a lab; Read it before you install it; a zip's central directory sits at the end of the file; so an HTTP Range request lists all of it; DT_NEEDED tells you what the loader will want; Read Requires-Dist from the wheel, not from the API that describes it.; WHAT THE NVIDIA STACK ACTUALLY IS · CANERY.IN
- Alt text: Captured terminal output listing all 13,043 entries of a 554.6 MB PyTorch wheel after transferring 1.2 MB.
- Long description: A terminal panel shows real captured output from the post's lab script: a 554.6 MB torch wheel with 13,043 entries, listed in full after three HTTP range requests and 1.2 MB of transfer. A card below explains the technique and points at DT_NEEDED as the way to see what the loader will require.
- Keywords: HTTP range request, Python wheel inspection, DT_NEEDED, no-GPU lab, PyPI metadata
- Canonical URL: https://canery.in/blogs/what-the-nvidia-stack-actually-is

### story-01-five-things-called-cuda

- File: `assets/social/story-01-five-things-called-cuda.png`
- Title: Five things are called CUDA
- Platforms: Instagram Story
- Role: cover
- Dimensions: 1080×1920
- Narrative beat: pip install torch lands gigabytes and the reader still cannot answer whether they need the Toolkit.
- Technical source: Why this matters; The problem
- Visual structure: A focal card for what pip just did, a card for the question it leaves open, and a one-line hook.
- Visible-text transcript: Canery.in; 01 / 04; Five things are called “CUDA”.; A kernel driver, a user-mode driver, a runtime, a compiler toolchain and a library portfolio.; what just happened; pip install torch; 4.86 GB across 32 packages; 90 shared libraries; the question you still cannot answer; Do I need the CUDA Toolkit?; the most searched question in this stack; and it cannot be answered without a map; of what those gigabytes actually are; five different things are called CUDA; None of them announces which one you are looking at.; WHAT THE NVIDIA STACK ACTUALLY IS · CANERY.IN
- Alt text: A card showing pip install torch pulling 4.86 GB across 32 packages, above the question of whether the CUDA Toolkit is needed.
- Long description: The opening Story frame pairs what a pip install of PyTorch actually does, 4.86 GB across 32 packages and 90 shared libraries, with the question it leaves unanswered: whether the CUDA Toolkit is required at all.
- Keywords: pip install torch, CUDA Toolkit, NVIDIA stack, GPU setup
- Canonical URL: https://canery.in/blogs/what-the-nvidia-stack-actually-is

### story-02-the-layer-map

- File: `assets/social/story-02-the-layer-map.png`
- Title: Seven layers, four shippers
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: The layer map with the artifact and the shipper for each row.
- Technical source: The problem: five different things are called “CUDA”; Figure 1
- Visual structure: Six rows from serving down to the kernel module, each with its file and its shipper, the bottom two in the accent.
- Visible-text transcript: Canery.in; 02 / 04; Seven layers. Four shippers.; Read the right-hand column first. The layers are released separately, by different products.; SERVING; a container image; separate products; FRAMEWORK; libtorch_cuda.so; pip wheel; LIBRARIES; libcublas.so.13; Toolkit or wheels; RUNTIME; libcudart.so.13; Toolkit or wheel; DRIVER; libcuda.so.1; NVIDIA driver; KERNEL; nvidia.ko; NVIDIA driver; Only the bottom two must come from the machine itself.; WHAT THE NVIDIA STACK ACTUALLY IS · CANERY.IN
- Alt text: Six stack layers from serving products down to the kernel module, each labelled with its file on disk and the product that ships it.
- Long description: Six rows map the stack from serving products at the top to the kernel module at the bottom. Each row names the file it puts on disk and the product that ships it. The driver and kernel rows are highlighted as the only two the host machine must supply.
- Keywords: NVIDIA layer map, libcudart, libtorch_cuda, NVIDIA driver, CUDA stack
- Canonical URL: https://canery.in/blogs/what-the-nvidia-stack-actually-is

### story-03-read-the-wheel

- File: `assets/social/story-03-read-the-wheel.png`
- Title: cuBLAS hides inside a bracket
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: cuBLAS is requested under a package name that no nvidia- prefix filter will match.
- Technical source: Limitations and common mistakes; Implementation
- Visual structure: A focal card for what the wheel lacks, a card for what it declares, and a boxed warning about the prefix filter.
- Visible-text transcript: Canery.in; 03 / 04; cuBLAS hides inside a bracket.; Filter a dependency list on the prefix nvidia- and cuBLAS vanishes. It did not go anywhere.; torch 2.14.0, 554.6 MB; What the wheel does NOT contain; no cuBLAS, no cuDNN, no cudart, no cuFFT; 13 shared objects, and not one of them is a math library; requires-dist, from the archive itself; What it declares instead; cuda-toolkit[cublas,cudart,cufft,cufile,cupti,; curand,cusolver,cusparse,nvjitlink,nvrtc,nvtx]; no package name here begins with nvidia-; read the whole line, from the wheel itself; Two independent passes of this research made that exact mistake.; WHAT THE NVIDIA STACK ACTUALLY IS · CANERY.IN
- Alt text: A comparison showing the torch wheel contains no CUDA math libraries but declares cuda-toolkit with eleven extras.
- Long description: One card records that the torch wheel ships thirteen shared objects and no CUDA math library. A second shows the cuda-toolkit dependency with eleven extras that the wheel's own metadata declares. A boxed warning notes that no package name on that line begins with nvidia-, so a prefix filter misses cuBLAS entirely.
- Keywords: Requires-Dist, PyPI JSON API, cuda-toolkit extras, wheel metadata
- Canonical URL: https://canery.in/blogs/what-the-nvidia-stack-actually-is

### story-04-read-the-full-article

- File: `assets/social/story-04-read-the-full-article.png`
- Title: Learn the map before the failures
- Platforms: Instagram Story
- Role: cta
- Dimensions: 1080×1920
- Narrative beat: Closing frame: what the article covers, the no-GPU lab, and what part 2 takes up.
- Technical source: the whole article
- Visual structure: A focal card summarising the article, two cards for the lab and the next part, and a dark call-to-action block.
- Visible-text transcript: Canery.in; 04 / 04; Learn the map before the failures.; Every hard failure in this stack gets diagnosed at the wrong layer by someone who never had the map.; 18-minute read, part 1 of the series; Inside the article; the layer map · one matmul traced down nine steps; what the driver installs · installer, wheel or container; tier a lab; Runnable, no GPU; inspect_wheel.py; resolve_stack.py; python3 and a network; part 2; Next in the series; the four CUDA; version numbers; and which one decides; Read the full article on Canery; use the link sticker below; Name the layer. Name the artifact. Then decide what to install.; LINK STICKER · READ THE ARTICLE
- Alt text: Closing frame listing what the article covers, the no-GPU lab scripts, and the next part in the series.
- Long description: The closing Story frame summarises the article's contents, names the two runnable lab scripts that need no GPU, previews part 2 on the four CUDA version numbers, and carries a call to action to read the full article on Canery.
- Keywords: NVIDIA stack series, CUDA explained, GPU engineering, Canery
- Canonical URL: https://canery.in/blogs/what-the-nvidia-stack-actually-is
