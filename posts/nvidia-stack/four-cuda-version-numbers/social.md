---
social_schema: 2
canonical_url: "https://canery.in/blogs/four-cuda-version-numbers"
---

# Social publishing package — four-cuda-version-numbers

## LinkedIn post

`nvidia-smi` prints a CUDA version. `nvcc --version` prints a different one. `torch.version.cuda` prints a third. Every one of them is correct, and none of them answers the question you actually have: will this wheel run on this driver?

There are four CUDA version numbers on a machine, each owned by a different artifact:

→ the kernel-mode driver, e.g. 580.65.06 — no CUDA in it at all
→ the CUDA user-mode driver, `libcuda.so.1` — a *ceiling*, not an inventory
→ the CUDA runtime in your wheel — a constant compiled into the binary
→ `nvcc` — a compiler that may not even be installed

Only the middle two are ever compared against each other. NVIDIA renamed the `nvidia-smi` field to `CUDA UMD Version` precisely because the old name implied an inventory it never was.

Two things that surprised me while writing this up:

1. A CUDA 13.4 application runs on a driver reporting 13.0. Being *ahead* of the ceiling is the case minor version compatibility was built for. Leaving the major family is the failure.
2. The whole compatibility matrix collapses to three numbers — driver 450 for CUDA 11.x, 525 for 12.x, 580 for 13.x.

And the forward-compatibility package, which everyone reaches for when a driver is frozen, only works on data center GPUs, select NGC Server Ready RTX SKUs, and Jetson boards. An ordinary consumer card is not on that list.

The lab needs no GPU. Two of the four numbers live in files you can read before installing anything, and `cudaRuntimeGetVersion` answers on a machine with no driver at all — because since CUDA 12.0 it returns a compile-time constant. I tested that rather than quoting it.

## LinkedIn first comment

The number you check first — `nvcc --version` — takes no part in whether a pre-built wheel runs. It describes a compiler that was not involved.

Read the full article on Canery: https://canery.in/blogs/four-cuda-version-numbers

## Instagram caption

Four different numbers on one machine are all correctly called "the CUDA version". Only two of them decide whether your code runs, and the one most people check first is neither.

Swipe for the four artifacts, the ceiling that isn't an inventory, and the three driver numbers that replace every compatibility matrix you've bookmarked.

Everything in here was verified against the shipped artifacts — the headers inside the wheel, not a summary of them. The lab runs on a laptop with no NVIDIA GPU.

Link in bio.

#cuda #nvidia #gpu #machinelearning #pytorch #mlops #devops #softwareengineering

## Shared feed order

1. `assets/social/feed-01-four-numbers.png` — the four artifacts, each with its own version number
2. `assets/social/feed-02-a-ceiling-not-an-inventory.png` — what `nvidia-smi`'s CUDA field actually reports
3. `assets/social/feed-03-ahead-of-the-ceiling.png` — a newer runtime on an older driver, running
4. `assets/social/feed-04-three-floors.png` — the whole compatibility table in three driver numbers
5. `assets/social/feed-05-forward-compat-preconditions.png` — what the compat package requires
6. `assets/social/feed-06-read-the-article.png` — six version strings from one install, and the CTA

## Instagram Story

- CTA: Four numbers, one word — and only two of them decide whether your code runs. Tap through for the full breakdown.
- Link sticker label: Read the article
- Link sticker URL: https://canery.in/blogs/four-cuda-version-numbers

### Story order

1. `assets/social/story-01-three-answers.png` — Overlay: One machine. Three commands. Three different CUDA versions, all correct.
2. `assets/social/story-02-a-ceiling.png` — Overlay: It is a ceiling, not an inventory — NVIDIA renamed the field to say so.
3. `assets/social/story-03-three-floors.png` — Overlay: 450, 525, 580. That is the entire compatibility table.
4. `assets/social/story-04-read-the-article.png` — Overlay: Read the version out of the wheel before you install it. Link above.

## Asset metadata

### feed-01-four-numbers

- File: `assets/social/feed-01-four-numbers.png`
- Title: Four CUDA version numbers, one word
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: Four separately versioned artifacts all share the name "the CUDA version", and only two of them are decisive.
- Technical source: Article section "The problem: four numbers, one word" and Figure 1; ledger claims L01–L04.
- Visual structure: Serif headline over a two-line deck, then four stacked full-width plates read top to bottom, the middle two tinted; a single accent line beneath them, then the takeaway above the footer.
- Visible-text transcript: Four numbers, one word. / Kernel driver, user-mode driver, runtime, compiler. All four are correctly called "the CUDA version". / 1 KERNEL-MODE DRIVER — nvidia.ko 580.65.06 / 2 CUDA USER-MODE DRIVER — libcuda.so.1 13.0 / 3 CUDA RUNTIME, IN THE WHEEL — libcudart.so.13 13.0 / 4 TOOLKIT COMPILER — nvcc 13.4 / only the middle two decide whether your code runs / Two of them decide whether you run. The one you check first is not either. / THE FOUR CUDA VERSION NUMBERS · CANERY.IN
- Alt text: Four stacked rows naming the kernel-mode driver, libcuda.so.1, libcudart.so.13 and nvcc with their version numbers, the middle two highlighted.
- Long description: A branded 1080×1350 card. Four rows list, in order, the kernel-mode driver `nvidia.ko` at 580.65.06, the CUDA user-mode driver `libcuda.so.1` at 13.0, the CUDA runtime `libcudart.so.13` at 13.0, and the Toolkit compiler `nvcc` at 13.4. Rows two and three carry the accent tint and border, marking them as the only pair compared against each other at launch. The takeaway states that the number most people check first — the compiler — is not one of the two.
- Keywords: CUDA, nvidia-smi, libcuda.so.1, libcudart.so.13, nvcc, kernel-mode driver, versioning
- Canonical URL: https://canery.in/blogs/four-cuda-version-numbers

### feed-02-a-ceiling-not-an-inventory

- File: `assets/social/feed-02-a-ceiling-not-an-inventory.png`
- Title: A ceiling, not an inventory
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: The CUDA version nvidia-smi prints is the newest CUDA the driver will serve, not a list of what is installed.
- Technical source: NVIDIA's nvidia-smi field definitions for `CUDA Version` and `CUDA UMD Version`; ledger claims L02, L03, L05.
- Visual structure: Headline and deck, then one wide accent card, then two half-width cards side by side contrasting what the number means against what it does not, then a narrow strip with the sharpest consequence.
- Visible-text transcript: It is a ceiling, not an inventory. / NVIDIA deprecated the field name to say exactly this. It is now CUDA UMD Version — user-mode driver. / THE NUMBER EVERYONE MISREADS — nvidia-smi says CUDA 13.0 — that is a ceiling, not an inventory; NVIDIA renamed the field CUDA UMD Version / A CEILING — what it means: the newest CUDA this driver will serve / NOT AN INVENTORY — what it does not: say a Toolkit is installed anywhere / a wheel-only box has no Toolkit at all / Your driver reporting 13.0 has not installed CUDA 13.0 anywhere. / THE FOUR CUDA VERSION NUMBERS · CANERY.IN
- Alt text: A card contrasting what nvidia-smi's CUDA number means — the newest CUDA the driver will serve — against what it does not mean.
- Long description: A branded 1080×1350 card. The focal panel states that `nvidia-smi` reporting CUDA 13.0 is a ceiling and that NVIDIA renamed the field to `CUDA UMD Version`, for user-mode driver. Two panels beneath split the distinction: the number means the newest CUDA the installed driver will serve; it does not mean a Toolkit is installed anywhere. A closing strip notes that a machine set up from wheels alone has no Toolkit at all, which is the common case for a PyTorch install.
- Keywords: nvidia-smi, CUDA UMD Version, user-mode driver, driver ceiling, CUDA Toolkit
- Canonical URL: https://canery.in/blogs/four-cuda-version-numbers

### feed-03-ahead-of-the-ceiling

- File: `assets/social/feed-03-ahead-of-the-ceiling.png`
- Title: Newer than the driver, and fine
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: An application runtime ahead of the driver's reported ceiling still runs, so long as the major version matches.
- Technical source: NVIDIA's own minor-version-compatibility transcript — Tesla T4, driver 580.65.06, deviceQuery reporting 13.0 / 13.4 and PASS; ledger claims L45, L20.
- Visual structure: Headline and deck, then a three-row panel reading driver ceiling, application runtime, verdict, with the values right-aligned in a column; then a wide accent card carrying the correction.
- Visible-text transcript: Newer than the driver, and fine. / A CUDA 13.4 build on a driver reporting 13.0. NVIDIA publishes this exact case as a passing run. / ONE HOST, ONE APPLICATION, ONE COMPARISON / DRIVER CEILING — 13.0 — from libcuda.so.1 / APPLICATION RUNTIME — 13.4 — a compile-time constant / VERDICT — runs — minor version compatibility / NOT THE FAILURE CASE — The runtime is AHEAD of the ceiling — and that is the case the rule was built for; so long as the major version matches / Leaving the major family is the failure. Being ahead of the ceiling is not. / THE FOUR CUDA VERSION NUMBERS · CANERY.IN
- Alt text: A panel showing a driver ceiling of 13.0 against an application runtime of 13.4, with the verdict that the program runs.
- Long description: A branded 1080×1350 card built on NVIDIA's own published transcript. The driver ceiling, read from `libcuda.so.1`, is 13.0. The application's runtime constant is 13.4 — a higher number. The verdict is that it runs, under minor version compatibility. The accent card names the common misreading directly: a runtime ahead of the ceiling is the case the rule exists for, not a fault. The real failure condition is crossing into a different major family.
- Keywords: minor version compatibility, CUDA runtime, driver ceiling, Tesla T4, deviceQuery
- Canonical URL: https://canery.in/blogs/four-cuda-version-numbers

### feed-04-three-floors

- File: `assets/social/feed-04-three-floors.png`
- Title: Three floors, not a matrix
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: The minimum driver is declared per CUDA major family, so the whole compatibility matrix reduces to three numbers.
- Technical source: NVIDIA CUDA Compatibility, Minor Version Compatibility driver-range table, restated in the CUDA Toolkit Release Notes Table 3; ledger claim L19.
- Visual structure: Headline and deck, then three left-aligned bands of increasing width, one per major family, the widest tinted; then a wide accent card naming what actually changed.
- Visible-text transcript: Three floors. That is the table. / Every release-by-release compatibility matrix you have bookmarked collapses into three driver branches. / MINIMUM DRIVER BRANCH, BY CUDA MAJOR FAMILY / CUDA 11.x — driver ≥ 450 / CUDA 12.x — driver ≥ 525 / CUDA 13.x — driver ≥ 580 / WHAT TO MEMORISE — Three numbers, not a matrix — the minimum is per major FAMILY, not per release; which is what changed at CUDA 11 / 450, 525, 580. Clear the floor for your major family and the minor version is free. / THE FOUR CUDA VERSION NUMBERS · CANERY.IN
- Alt text: Three bands of increasing width giving the minimum driver branch per CUDA major family: 450 for 11.x, 525 for 12.x, 580 for 13.x.
- Long description: A branded 1080×1350 card. Three bands, each wider than the last, give the minimum NVIDIA driver branch for each CUDA major family: 450 for CUDA 11.x, 525 for 12.x, and 580 for 13.x, with the 13.x band carrying the accent. The accent card explains the mechanism: the minimum is declared per major family rather than per release, which is the change introduced at CUDA 11 and the reason a release-by-release matrix is no longer the right mental model.
- Keywords: CUDA compatibility, minimum driver version, driver branch, CUDA 13, minor version compatibility
- Canonical URL: https://canery.in/blogs/four-cuda-version-numbers

### feed-05-forward-compat-preconditions

- File: `assets/social/feed-05-forward-compat-preconditions.png`
- Title: The forward-compatibility package has four preconditions
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: The compat package spans the kernel-driver boundary and carries hardware, configuration and feature restrictions that summaries drop.
- Technical source: NVIDIA CUDA Compatibility, Forward Compatibility — the supported-hardware warning, the LD_LIBRARY_PATH note, the feature-exception table and the support matrix; ledger claims L26, L29, L30, L33, L34.
- Visual structure: Headline and deck, then one accent card naming the package and what it swaps, then a four-item list panel, then a single accent line carrying the precondition people miss.
- Visible-text transcript: The package has four preconditions. / Forward compatibility spans a different boundary — kernel driver to CUDA driver, not runtime to driver. / THE FORWARD-COMPATIBILITY PACKAGE — cuda-compat-13-4 — replaces libcuda.so.1, leaves nvidia.ko alone; which is why change control can accept it / AND THE PRECONDITIONS NOBODY QUOTES — data center GPUs, some NGC RTX SKUs, Jetson — that is the list / installing it does nothing until you set LD_LIBRARY_PATH / no CUDA–OpenGL or Vulkan interop, in any major family / an older package is unsupported on a newer driver / an ordinary consumer card is not on that list / It is a datacenter answer to a frozen driver, not a general fix for an old one. / THE FOUR CUDA VERSION NUMBERS · CANERY.IN
- Alt text: A card naming the cuda-compat package and listing its four preconditions: hardware, LD_LIBRARY_PATH, no graphics interop, and driver age.
- Long description: A branded 1080×1350 card. The focal panel names `cuda-compat-13-4` and states that it replaces `libcuda.so.1` while leaving the kernel module `nvidia.ko` untouched, which is what makes it acceptable under change control. Four listed preconditions follow: it is supported only on data center GPUs, select NGC Server Ready RTX SKUs and Jetson boards; installing it changes nothing until `LD_LIBRARY_PATH` is set; CUDA–OpenGL and Vulkan interop do not work under it in any major family; and an older package is unsupported on a newer driver. The closing line notes that an ordinary consumer card is not on the hardware list.
- Keywords: cuda-compat, forward compatibility, LD_LIBRARY_PATH, data center GPU, Jetson, OpenGL interop
- Canonical URL: https://canery.in/blogs/four-cuda-version-numbers

### feed-06-read-the-article

- File: `assets/social/feed-06-read-the-article.png`
- Title: Six version strings, one install
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: One pip install produces six version strings from six namespaces, and only one of them is ever compared against anything.
- Technical source: Article section "Limitations and common mistakes" and Figure 8; ledger claims L12, L14, L15, L16, L17, L41.
- Visual structure: Headline and deck, then a single panel of six rows pairing a version string on the left with its namespace on the right, two rows in the accent; then an accent card and the article call to action.
- Visible-text transcript: Six strings. One install. / Which of them your program is actually checked against — and the three floors that decide it. / ONE PIP INSTALL TORCH, SIX VERSION STRINGS / 2.14.0 — PyPI distribution / 2.14.0+cu130 — torch.__version__ / 13.0 — torch.version.cuda / 13.0.3 — cuda-toolkit pin / 13.0.96 — nvidia-cuda-runtime pin / 13000 — CUDART_VERSION / Only the last one is compared — against anything at all / The full article walks all four numbers to the file that produced each one. / READ IT AT CANERY.IN/BLOGS/FOUR-CUDA-VERSION-NUMBERS
- Alt text: Six version strings from one pip install torch, each paired with the namespace that produced it, with CUDART_VERSION highlighted.
- Long description: A branded 1080×1350 closing card. Six rows pair a version string with its namespace: 2.14.0 from the PyPI distribution, 2.14.0+cu130 from `torch.__version__`, 13.0 from `torch.version.cuda`, 13.0.3 from the `cuda-toolkit` pin, 13.0.96 from the `nvidia-cuda-runtime` pin, and 13000 from `CUDART_VERSION`. The local label and the constant carry the accent — the first because it is routinely read as a requirement it is not, the second because it is the only one of the six compared against anything at run time. The card closes with the article URL.
- Keywords: PEP 440, local version label, CUDART_VERSION, torch.version.cuda, cuda-toolkit, PyPI
- Canonical URL: https://canery.in/blogs/four-cuda-version-numbers

### story-01-three-answers

- File: `assets/social/story-01-three-answers.png`
- Title: One machine, three answers
- Platforms: Instagram Story
- Role: cover
- Dimensions: 1080×1920
- Narrative beat: Three commands on one machine report three different CUDA versions and every one of them is telling the truth.
- Technical source: Article section "Why this matters"; the three readouts are the post's opening worked case.
- Visual structure: Lockup and frame counter, serif headline over a deck, then one accent card holding the three commands and one plain card holding the consequence, then an accent line and the takeaway.
- Visible-text transcript: One machine, three answers. / Every command is telling the truth about a different artifact. That is the whole problem. / ONE MACHINE, THREE ANSWERS — nvidia-smi says 13.0 — nvcc --version says 13.4; torch.version.cuda says 13.0 / THE UNHELPFUL TRUTH — All three are correct. — and none of them answers the question you actually have: will this wheel run on this driver? / four numbers, and only two decide / Two of the four decide whether your code runs. / THE FOUR CUDA VERSION NUMBERS · CANERY.IN
- Alt text: A Story frame listing three commands on one machine reporting three different CUDA versions, all of them correct.
- Long description: A branded 1080×1920 Story frame. The focal card gives three readouts from a single machine: `nvidia-smi` reporting 13.0, `nvcc --version` reporting 13.4, and `torch.version.cuda` reporting 13.0. The second card states that all three are correct and that none answers whether a given wheel will run on that driver. The takeaway narrows the field: of the four version numbers on the machine, two decide whether the code runs.
- Keywords: nvidia-smi, nvcc, torch.version.cuda, CUDA version, compatibility
- Canonical URL: https://canery.in/blogs/four-cuda-version-numbers

### story-02-a-ceiling

- File: `assets/social/story-02-a-ceiling.png`
- Title: A ceiling, not an inventory
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: NVIDIA's own definition of the field is the newest CUDA the driver supports, which is a limit rather than a list.
- Technical source: NVIDIA nvidia-smi documentation, the `CUDA UMD Version` field definition; ledger claims L02, L03.
- Visual structure: Lockup and counter, three-line serif headline over a deck, then a bordered panel quoting the field definition, then an accent card giving the reading, then the takeaway.
- Visible-text transcript: A ceiling, not an inventory. / NVIDIA deprecated the old field name to say exactly this. / WHAT NVIDIA-SMI IS ACTUALLY REPORTING — CUDA UMD VERSION — the latest CUDA version supported by the driver — NVIDIA's own wording / READ IT THIS WAY — It is a ceiling. — Not a list of what is installed. A wheel-only box has no Toolkit at all. / Your driver reporting 13.0 has not installed CUDA 13.0 anywhere. / THE FOUR CUDA VERSION NUMBERS · CANERY.IN
- Alt text: A Story frame quoting NVIDIA's definition of CUDA UMD Version as the latest CUDA version supported by the driver.
- Long description: A branded 1080×1920 Story frame. A bordered panel carries NVIDIA's own wording for the `CUDA UMD Version` field — the latest CUDA version supported by the driver — attributed as their phrasing rather than a paraphrase. The accent card converts it into a reading rule: the number is a ceiling, not a list of what is installed, and a machine built from wheels alone has no CUDA Toolkit at all. The takeaway states the consequence directly.
- Keywords: CUDA UMD Version, nvidia-smi, user-mode driver, driver ceiling
- Canonical URL: https://canery.in/blogs/four-cuda-version-numbers

### story-03-three-floors

- File: `assets/social/story-03-three-floors.png`
- Title: Three floors, the whole table
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: The minimum driver branch is declared per CUDA major family, so three numbers replace the compatibility matrix.
- Technical source: NVIDIA CUDA Compatibility, Minor Version Compatibility driver-range table; ledger claim L19.
- Visual structure: Lockup and counter, two-line serif headline over a deck, then three stacked full-width bands one per major family with the last in the accent, then two centred lines and the takeaway.
- Visible-text transcript: Three floors. That is the table. / A CUDA 13.4 build runs on a driver reporting 13.0. By design. / THE ENTIRE COMPATIBILITY TABLE / CUDA 11.X — driver ≥ 450 / CUDA 12.X — driver ≥ 525 / CUDA 13.X — driver ≥ 580 / per major family, never per release / and the minor version is then free / Clear your major family's floor and the minor version stops mattering. / THE FOUR CUDA VERSION NUMBERS · CANERY.IN
- Alt text: A Story frame giving the minimum driver branch for each CUDA major family: 450 for 11.x, 525 for 12.x, and 580 for 13.x.
- Long description: A branded 1080×1920 Story frame. Three stacked bands give the minimum NVIDIA driver branch per CUDA major family — 450 for 11.x, 525 for 12.x, 580 for 13.x — with the 13.x row carrying the accent. Two centred lines state the rule that makes the reduction valid: the minimum is declared per major family, never per release, and once the floor is cleared the minor version no longer participates. The deck cites the published case of a CUDA 13.4 build running on a driver reporting 13.0.
- Keywords: minimum driver version, CUDA major family, driver branch, minor version compatibility
- Canonical URL: https://canery.in/blogs/four-cuda-version-numbers

### story-04-read-the-article

- File: `assets/social/story-04-read-the-article.png`
- Title: Predict it before you install
- Platforms: Instagram Story
- Role: cta
- Dimensions: 1080×1920
- Narrative beat: The runtime version can be read out of the wheel and confirmed by loading the library, on a machine with no NVIDIA driver.
- Technical source: Article section "Implementation: predict the answer before you install" and the lab's `cuda_versions.py` transcript; ledger claims L08, L12.
- Visual structure: Lockup and counter, two-line serif headline over a deck, then one accent card with the instruction, then a bordered panel holding the captured output, then the CTA line.
- Visible-text transcript: Predict it before you install. / Two scripts, no GPU required, and every number in the article traced to a file. / PREDICT, DO NOT DIAGNOSE — Read CUDART_VERSION — out of the wheel, before you install it; then compare it with the driver's ceiling / THE LAB NEEDS NO GPU, NO DRIVER, NO TOOLKIT / CUDART_VERSION 13000 / cudaRuntimeGetVersion() / -> 13000, on a machine / with no NVIDIA driver / The full article is on Canery. / LINK IN THE STICKER ABOVE
- Alt text: A Story frame showing CUDART_VERSION read as 13000 from a wheel, confirmed by a call that runs without an NVIDIA driver.
- Long description: A branded 1080×1920 closing Story frame. The accent card gives the method: read `CUDART_VERSION` out of the wheel before installing, then compare it with the driver's reported ceiling. The panel below carries the captured result — `CUDART_VERSION` defined as 13000 in the shipped header, and `cudaRuntimeGetVersion()` returning the same 13000 when the extracted library is loaded on a machine with no NVIDIA driver. That agreement is the observable consequence of the runtime version being a compile-time constant. The frame closes with a pointer to the link sticker.
- Keywords: CUDART_VERSION, cudaRuntimeGetVersion, compile-time constant, wheel inspection, no GPU
- Canonical URL: https://canery.in/blogs/four-cuda-version-numbers
