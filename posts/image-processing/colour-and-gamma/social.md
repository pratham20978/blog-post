---
social_schema: 2
canonical_url: "https://canery.in/blogs/colour-and-gamma"
---

# Social publishing package — colour-and-gamma

## LinkedIn post

Average code 40 and code 200 and you get 120. Average the light they send and you get code 148.7.

An 8-bit pixel value is a code on the sRGB curve, not an amount of light. Worked by hand on one pixel and one 5×5 patch, here is what that changes.

→ Code 128 sends 21.6% of white's light. The grey that looks halfway is code 119, at 18.4%; half the light needs code 187.5.
→ Blurs, resizes and composites on codes come out darker. On the patch's step the blur gives 78.2 on codes and 109.4 in light.
→ cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) weighs the codes with BT.601's 0.299, 0.587 and 0.114. That is luma, not luminance. On the azure (40, 200, 255) it gives 158; the grey of equal light is 186.
→ Those weights come from the 1953 NTSC primaries with Illuminant C, not from BT.601's own primaries. sRGB's own luminance weights are 0.2126, 0.7152 and 0.0722.
→ Lab depends on its white: the same pixel lands 5.8 ΔE apart in D65 Lab and in CSS's D50 Lab.

Part 13 of Image Processing by Hand. Every number is worked on paper; nothing was run against an image.

## LinkedIn first comment

A pixel value is a code, not light: decode before you average, and know which grey your library returns.

Read the full article on Canery: https://canery.in/blogs/colour-and-gamma

## Instagram caption

Averaging codes darkens the image. Swipe through colour and gamma worked by hand: why code 128 sends 21.6% of white's light, why a blur on codes comes out darker than the same blur on light, why BGR2GRAY returns luma and not luminance, where 0.299, 0.587 and 0.114 come from, why 8 bits need a curve at all, and which library calls decode sRGB before they compute.

Every number is worked from the article's own pixel and patch. Nothing was run against an image.

Link in bio.

#computervision #imageprocessing #opencv #colour #gamma #srgb #python

## Shared feed order

1. `assets/social/feed-01-averaging-codes-darkens.png` — codes 40 and 200 averaged as numbers (120) and as light (148.7), with the stripes example
2. `assets/social/feed-02-bgr2gray-is-luma.png` — the azure (40, 200, 255), its luma grey 158 and its luminance grey 186
3. `assets/social/feed-03-where-0-299-comes-from.png` — the NTSC 1953 and BT.709 triangles on the CIE diagram and the weights each implies
4. `assets/social/feed-04-why-8-bits-need-a-curve.png` — codes per tenth of lightness for sRGB and for linear 8-bit coding
5. `assets/social/feed-05-the-same-blur-two-answers.png` — row r0 of the patch blurred on codes and on light, as true greys
6. `assets/social/feed-06-luma-is-off-by-70.png` — luma against the luminance grey for nine colours, and the range over all 8-bit colours
7. `assets/social/feed-07-five-calls-two-decode.png` — five library calls on the azure and which two decode sRGB first
8. `assets/social/feed-08-read-the-article.png` — the four ideas of the post, and the CTA

## Instagram Story

- CTA: Code 128 is not half of white. One pixel, worked by hand — tap the link.
- Link sticker label: Read the article
- Link sticker URL: https://canery.in/blogs/colour-and-gamma

### Story order

1. `assets/social/story-01-code-128-is-not-half.png` — Overlay: Code 128 sends 21.6% of white's light.
2. `assets/social/story-02-158-or-186.png` — Overlay: BGR2GRAY gives 158; the grey of equal light is 186.
3. `assets/social/story-03-averaging-codes-darkens.png` — Overlay: Averaging codes darkens: 120, not 148.7.
4. `assets/social/story-04-read-the-article.png` — Overlay: Colour and gamma, by hand. Link below.

## Asset metadata

### feed-01-averaging-codes-darkens

- File: `assets/social/feed-01-averaging-codes-darkens.png`
- Title: Averaging codes darkens the image
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: the patch's codes 40 and 200 average to 120 as numbers but to code 148.7 as light, because code 120 sends only 18.8% of white's light; the same rule makes black and white stripes halve to 127.5 instead of 187.5
- Technical source: Worked example, step 5; Which operations need linear light?; Figures 3 and 8
- Visual structure: lockup and counter; serif title; deck; a panel with two input swatches (40 and 200), an arrow, and two output swatches (120 framed tangerine, 148.7 framed blue), then three lines of numbers; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 08 · Averaging codes darkens the image. · Code 40 and code 200, averaged two ways: as numbers, and as the light they send. · two codes from the patch · 40 · 200 · sends 2.1% of white · sends 57.8% of white · averaged · → · 120 · 148.7 · as codes · as light · code 120 sends 18.8% of white's light; · the average of the two lights is 29.9%, code 148.7. · one-pixel black and white stripes, halved: · codes give 127.5 (21.4% of white); light gives 187.5 (50%) · average = a blur, a resize, a composite · An 8-bit value is a code on the sRGB curve, not an amount of light. Decode first. · COLOUR AND GAMMA · CANERY.IN
- Alt text: Grey swatches for codes 40 and 200, and their averages: 120 as numbers, framed tangerine, beside a lighter 148.7 as light, framed blue.
- Long description: Two grey swatches show sRGB codes 40 and 200, which send 2.1% and 57.8% of white's light. Averaged as numbers they give code 120; averaged as light (29.9%) and encoded back they give code 148.7, a visibly lighter grey. Code 120 sends only 18.8% of white's light. One-pixel black and white stripes halved the same two ways give code 127.5, which sends 21.4% of white, against code 187.5, which sends 50%. Averaging covers blurs, resizes and composites. The takeaway: an 8-bit value is a code on the sRGB curve, not an amount of light, so decode first.
- Keywords: sRGB, gamma, linear light, averaging, blur, resize, image processing
- Canonical URL: https://canery.in/blogs/colour-and-gamma

### feed-02-bgr2gray-is-luma

- File: `assets/social/feed-02-bgr2gray-is-luma.png`
- Title: BGR2GRAY returns luma, not luminance
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the azure (40, 200, 255) becomes 158 under BGR2GRAY's weights on codes and 186 as the grey of equal luminance; the luma grey is 10.2 units of L* darker than the colour
- Technical source: Worked example, step 4; Figure 2; ledger L15, L27
- Visual structure: lockup and counter; serif title; deck; the azure swatch beside two grey swatches (158 framed tangerine, 186 framed blue) with their names; two formula lines; an L* comparison; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 08 · BGR2GRAY returns luma, not luminance. · One pixel, two greys: weights on the codes, or weights on the light they encode. · 158 · 186 · the azure · (40, 200, 255) · luma: BGR2GRAY · weights on codes · luminance grey · weights on light · 0.299·40 + 0.587·200 + 0.114·255 = 158.4 · decode → Y = 0.4898 → encode → 185.8 · L*: azure 75.4 · luma grey 65.3 · luminance grey 75.4 · The luma grey is 10.2 units of L* darker than the colour it came from. · COLOUR AND GAMMA · CANERY.IN
- Alt text: The azure swatch beside two greys, 158 from BGR2GRAY's weights on codes and a lighter 186 that sends the same light as the azure.
- Long description: The azure, sRGB (40, 200, 255), is turned to grey two ways. OpenCV's BGR2GRAY applies BT.601's weights to the codes: 0.299 × 40 + 0.587 × 200 + 0.114 × 255 = 158.4, stored as 158, which is luma. Luminance decodes the codes, weighs the light (Y = 0.4898) and encodes the result back to code 185.8, stored as 186. In lightness the azure and the luminance grey are both L* 75.4, while the luma grey is L* 65.3, 10.2 units darker.
- Keywords: luma, luminance, BGR2GRAY, OpenCV, BT.601, sRGB, grayscale
- Canonical URL: https://canery.in/blogs/colour-and-gamma

### feed-03-where-0-299-comes-from

- File: `assets/social/feed-03-where-0-299-comes-from.png`
- Title: Where 0.299, 0.587 and 0.114 come from
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the luminance weights are the middle row of the matrix a display's primaries and white fix; the 1953 NTSC primaries with Illuminant C give BT.601's 0.299/0.587/0.114, BT.709's give sRGB's 0.2126/0.7152/0.0722, and BT.601's own primaries would give 0.222/0.707/0.071
- Technical source: Where do the grey weights come from?; Figure 5; ledger L03, L16, L17, L19, L20, L42
- Visual structure: lockup and counter; serif title; deck; a CIE xy horseshoe with the NTSC 1953 triangle in tangerine and the BT.709 triangle in blue and their whites; beside it three labelled weight rows and a credit line; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 08 · Where 0.299, 0.587 and 0.114 come from. · Luminance weights are fixed by a display's primaries and its white point. · NTSC 1953, white C · 0.299 · 0.587 · 0.114 · = BT.601's luma weights · BT.709 and sRGB, D65 · 0.2126 · 0.7152 · 0.0722 · = sRGB's luminance weights · BT.601's own primaries · 0.222 · 0.707 · 0.071 · 625-line, with D65 · CIE 1931 xy; horseshoe from the CIE's table (CC BY-SA 4.0) · BT.601 still codes with the 1953 NTSC weights, not those of its own primaries. · COLOUR AND GAMMA · CANERY.IN
- Alt text: A CIE xy horseshoe with the 1953 NTSC and BT.709 primary triangles, and the luminance weights each implies, 0.299/0.587/0.114 and 0.2126/0.7152/0.0722.
- Long description: On the CIE 1931 chromaticity diagram, plotted from the CIE's table, the 1953 NTSC primaries form a wider triangle than BT.709's. Each triangle with its white fixes a matrix whose middle row is the luminance weights: NTSC 1953 with Illuminant C gives 0.299, 0.587 and 0.114, BT.601's luma weights; BT.709 and sRGB with D65 give 0.2126, 0.7152 and 0.0722; BT.601's own 625-line primaries with D65 would give 0.222, 0.707 and 0.071. BT.601 still codes with the 1953 weights.
- Keywords: BT.601, BT.709, NTSC, primaries, white point, chromaticity, luminance weights
- Canonical URL: https://canery.in/blogs/colour-and-gamma

### feed-04-why-8-bits-need-a-curve

- File: `assets/social/feed-04-why-8-bits-need-a-curve.png`
- Title: Why 8 bits need a curve
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: along the sRGB curve every tenth of lightness gets 21 to 29 of the 256 codes; spread evenly in light, the darkest tenth gets 3 and the brightest 61
- Technical source: Why is a pixel value an encoding?; Figure 4; ledger L09, L10, L12
- Visual structure: lockup and counter; serif title; deck; paired bars per tenth of L*, tangerine for sRGB and blue for linear 8-bit, with counts; a two-part key; takeaway; footer
- Visible-text transcript: Canery.in · 04 / 08 · Why 8 bits need a curve. · 256 codes spread over lightness: along the sRGB curve, or evenly in light. · codes per tenth of lightness L* · 28 3 · 21 5 · 22 8 · 24 13 · 24 18 · 26 25 · 27 32 · 27 41 · 28 50 · 29 61 · 0–10 · 10–20 · 20–30 · 30–40 · 40–50 · 50–60 · 60–70 · 70–80 · 80–90 · 90–100 · sRGB · 21 to 29 per tenth · linear 8-bit · 3 to 61 · Linear 8-bit coding spends 3 codes on the darkest tenth and 61 on the brightest. · COLOUR AND GAMMA · CANERY.IN
- Alt text: Paired bars of codes per tenth of lightness: sRGB stays between 21 and 29, linear 8-bit coding climbs from 3 to 61.
- Long description: The 256 codes of an 8-bit channel, counted per tenth of CIE lightness L*. Along the sRGB curve the counts are 28, 21, 22, 24, 24, 26, 27, 27, 28 and 29, close to the even 25.6. Spread evenly in light they are 3, 5, 8, 13, 18, 25, 32, 41, 50 and 61: three codes for the darkest tenth, where each step is visible, and 61 for the brightest, where neighbours are hard to tell apart. That is why stored images use a curve.
- Keywords: gamma, perceptual uniformity, 8-bit, quantisation, lightness, sRGB, banding
- Canonical URL: https://canery.in/blogs/colour-and-gamma

### feed-05-the-same-blur-two-answers

- File: `assets/social/feed-05-the-same-blur-two-answers.png`
- Title: The same blur, two answers
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: row r0 of the patch, 40 40 40 200 200, blurred with the series' Gaussian gives 78.2 and 161.8 at the edge on codes and 109.4 and 177.9 when the blur runs on light
- Technical source: Worked example, step 5; Figure 3
- Visual structure: lockup and counter; serif title; deck; three rows of five true-grey cells with their values (the original row, blurred as codes, blurred as light); the kernel weights; takeaway; footer
- Visible-text transcript: Canery.in · 05 / 08 · The same blur, two answers. · Row r0 of the patch blurred with the series' Gaussian: on codes, and on decoded light. · row r0 of the patch · 40 · 40 · 40 · 200 · 200 · blurred as codes · 40 · 40 · 78.2 · 161.8 · 200 · blurred as light · 40 · 40 · 109.4 · 177.9 · 200 · weights 0.239 · 0.522 · 0.239: the series' Gaussian · On codes the edge comes out darker: 78.2 against 109.4 on the dark side. · COLOUR AND GAMMA · CANERY.IN
- Alt text: Three rows of grey cells: the step 40 40 40 200 200, its blur on codes (78.2, 161.8) and its blur on light (109.4, 177.9).
- Long description: Row r0 of the series' 5×5 patch, codes 40 40 40 200 200, is blurred with the series' 3-tap Gaussian, weights 0.239, 0.522 and 0.239. Blurring the codes gives 40, 40, 78.2, 161.8, 200. Decoding to light, blurring and encoding back gives 40, 40, 109.4, 177.9, 200. The code-domain blur is darker on both sides of the edge: 31 codes darker at c2 and 16 at c3.
- Keywords: Gaussian blur, linear light, sRGB, edge, gamma-correct blur, image processing
- Canonical URL: https://canery.in/blogs/colour-and-gamma

### feed-06-luma-is-off-by-70

- File: `assets/social/feed-06-luma-is-off-by-70.png`
- Title: Luma is off by up to 70 grey levels
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: BGR2GRAY's luma against the grey of equal luminance for nine colours; over all 16,777,216 8-bit colours the difference runs from −70.2 at pure green to +5.9 at (255, 172, 255), and is exactly 0 on greys
- Technical source: How wrong is luma?; Figure 6
- Visual structure: lockup and counter; serif title; deck; nine colour swatches, each above a pair of grey swatches framed tangerine (luma) and blue (luminance grey) with their codes; a two-item key; three lines on the all-colour range; takeaway; footer
- Visible-text transcript: Canery.in · 06 / 08 · Luma is off by up to 70 grey levels. · BGR2GRAY against the grey of equal luminance, for every 8-bit colour. · red 76 127 · green 150 220 · blue 29 76 · yellow 226 247 · cyan 179 229 · magenta 105 145 · azure 158 186 · pink 206 200 · grey 128 128 · luma (BGR2GRAY) · luminance grey · over all 16,777,216 8-bit colours: · luma − luminance grey runs from −70.2 · (pure green) to +5.9 (255, 172, 255) · exactly 0 on every grey · Equal on greys, darker on saturated colours, a little brighter on pale pinks. · COLOUR AND GAMMA · CANERY.IN
- Alt text: Nine colours with their luma and luminance greys; luma is darker on most, equal on grey, slightly brighter on a pale pink.
- Long description: For nine colours, BT.601 luma (BGR2GRAY) and the luminance-matched grey are: red 76 and 127, green 150 and 220, blue 29 and 76, yellow 226 and 247, cyan 179 and 229, magenta 105 and 145, the azure 158 and 186, the pink (255, 172, 255) 206 and 200, and grey 128 and 128. Over all 16,777,216 8-bit colours, luma minus the luminance grey runs from −70.2 at pure green to +5.9 at (255, 172, 255), and is exactly 0 on every grey.
- Keywords: luma, luminance, grayscale conversion, BGR2GRAY, colour error, sRGB
- Canonical URL: https://canery.in/blogs/colour-and-gamma

### feed-07-five-calls-two-decode

- File: `assets/social/feed-07-five-calls-two-decode.png`
- Title: Five calls on one pixel; two decode it
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: on the azure, OpenCV's BGR2GRAY gives 158, BGR2XYZ's Y 170 and BGR2Lab's L* 75.4; scikit-image's rgb2gray gives 0.6665 and rgb2xyz's Y 0.4897; only BGR2Lab and rgb2xyz decode sRGB first
- Technical source: Implementation: the tooling map; Figure 9; ledger L27, L29, L30, L33, L34, L43
- Visual structure: lockup and counter; serif title; deck; five rows, each with library, call, the value on the azure and a note, coloured tangerine for calls on codes and blue for calls that decode; takeaway; footer
- Visible-text transcript: Canery.in · 07 / 08 · Five calls on one pixel. Two decode it. · The azure (40, 200, 255) through OpenCV and scikit-image, read from source, not run. · OpenCV · COLOR_BGR2GRAY · 158 · luma of the codes · OpenCV · COLOR_BGR2XYZ, Y · 170 · the matrix on codes, no decode · OpenCV · COLOR_BGR2Lab, L* · 75.4 · decodes first, undocumented · scikit-image · rgb2gray · 0.6665 · documented as luminance · scikit-image · rgb2xyz, Y · 0.4897 · decodes first: luminance · Only the calls that decode sRGB first work on light: Lab, and rgb2xyz. · COLOUR AND GAMMA · CANERY.IN
- Alt text: Five library calls on the azure with their results; only OpenCV's BGR2Lab and scikit-image's rgb2xyz decode sRGB first.
- Long description: The azure (40, 200, 255) through five calls, read from source at pinned commits and not run. OpenCV's COLOR_BGR2GRAY gives 158, luma of the codes. COLOR_BGR2XYZ's Y is 170 of 255, the matrix applied to codes without decoding. COLOR_BGR2Lab gives L* 75.4 because it decodes sRGB first, a step its documentation does not mention. scikit-image's rgb2gray gives 0.6665, BT.709-style weights on codes, documented as luminance; its rgb2xyz decodes first and gives Y = 0.4897, the luminance.
- Keywords: OpenCV, scikit-image, cvtColor, rgb2gray, rgb2xyz, Lab, XYZ, sRGB decode
- Canonical URL: https://canery.in/blogs/colour-and-gamma

### feed-08-read-the-article

- File: `assets/social/feed-08-read-the-article.png`
- Title: Colour and gamma, by hand
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: the four ideas of the post, then the call to read the article
- Technical source: Key takeaways
- Visual structure: lockup and counter; serif title; deck; four headed items (codes, luma, weights, Lab) each with a fact and a rule; takeaway; CTA footer with the URL
- Visible-text transcript: Canery.in · 08 / 08 · Colour and gamma, by hand. · Luma, luminance and the spaces in between, on one pixel and one 5×5 patch. · codes · code 128 sends 21.6% of white's light · decode before you blur, resize or blend · luma · BGR2GRAY: 158; luminance grey: 186 · weights on codes, or on light · weights · 0.299 · 0.587 · 0.114 date from 1953 · sRGB's own: 0.2126 · 0.7152 · 0.0722 · Lab · D65 or D50: 5.8 ΔE apart · a Lab number needs its white · The full walk-through, every number worked by hand, and the tooling map. · READ IT AT CANERY.IN/BLOGS/COLOUR-AND-GAMMA
- Alt text: A summary card listing codes, luma, weights and Lab, each with one fact from the article, and the link to read it.
- Long description: Four takeaways: code 128 sends 21.6% of white's light, so decode before you blur, resize or blend; BGR2GRAY gives 158 on the azure while the luminance grey is 186, weights on codes against weights on light; 0.299, 0.587 and 0.114 date from 1953, while sRGB's own weights are 0.2126, 0.7152 and 0.0722; and D65 and D50 Lab put the same pixel 5.8 ΔE apart, so a Lab number needs its white. The card links to the full article.
- Keywords: colour, gamma, luma, luminance, sRGB, Lab, image processing
- Canonical URL: https://canery.in/blogs/colour-and-gamma

### story-01-code-128-is-not-half

- File: `assets/social/story-01-code-128-is-not-half.png`
- Title: Code 128 is not half of white
- Platforms: Instagram Story
- Role: cover
- Dimensions: 1080×1920
- Narrative beat: code 128 sends 21.6% of white's light; half of the light needs code 187.5
- Technical source: Worked example, step 1; Figure 1; Why this matters
- Visual structure: lockup and counter; serif title; one-line deck; a grey ramp of sRGB codes with 128 (tangerine) and 187.5 (blue) joined by lines to a light ruler at 21.6% and 50%; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 04 · Code 128 is not half of white. · It sends 21.6% of white's light. · sRGB code · 128 · 187.5 · light it sends · 21.6% · 50% · 0 · 100% · Half of the light needs code 187.5. · COLOUR AND GAMMA · CANERY.IN
- Alt text: A grey ramp of sRGB codes with 128 joined to 21.6% of white's light and 187.5 joined to 50%.
- Long description: A horizontal ramp of sRGB codes from 0 to 255 sits above a ruler of linear light from 0 to 100%. A tangerine line joins code 128 to 21.6% of white's light, and a blue line joins code 187.5 to 50%. The middle of the code range is far below half of the light; half of the light needs code 187.5.
- Keywords: sRGB, gamma, code value, linear light, grey ramp
- Canonical URL: https://canery.in/blogs/colour-and-gamma

### story-02-158-or-186

- File: `assets/social/story-02-158-or-186.png`
- Title: 158 or 186?
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: one azure pixel becomes 158 under BGR2GRAY (luma) and 186 as the grey of equal light (luminance)
- Technical source: Worked example, step 4; Figure 2
- Visual structure: lockup and counter; serif title; deck; a large azure swatch beside two grey swatches, 158 framed tangerine and 186 framed blue, with labels; a two-line explanation; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 04 · 158 or 186? · One azure pixel, two ways to make it grey. · 158 · 186 · luma · luminance · the azure (40, 200, 255) · BGR2GRAY weighs the codes; luminance weighs the light. · BGR2GRAY gives luma, 158. The grey of equal light is 186. · COLOUR AND GAMMA · CANERY.IN
- Alt text: A large azure swatch beside a 158 grey from BGR2GRAY and a lighter 186 grey that sends the same light as the azure.
- Long description: The azure pixel, sRGB (40, 200, 255), beside its two greys. BGR2GRAY weighs the codes with BT.601's weights and returns 158, luma. Weighing the decoded light and encoding the luminance back gives 186, the grey that sends the same light as the azure.
- Keywords: luma, luminance, BGR2GRAY, grayscale, sRGB
- Canonical URL: https://canery.in/blogs/colour-and-gamma

### story-03-averaging-codes-darkens

- File: `assets/social/story-03-averaging-codes-darkens.png`
- Title: Averaging codes darkens
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: codes 40 and 200 average to 120 as numbers and to 148.7 as light
- Technical source: Worked example, step 5; Figure 8
- Visual structure: lockup and counter; serif title; deck; two input swatches (40 and 200), then two wide output swatches, 120 framed tangerine and 148.7 framed blue, with labels; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 04 · Averaging codes darkens. · Code 40 and code 200, averaged two ways. · 40 · 200 · averaged: · 120 · 148.7 · average of the codes · average of the light · Decode, average, encode: 148.7, not 120. · COLOUR AND GAMMA · CANERY.IN
- Alt text: Codes 40 and 200 averaged two ways: 120 as numbers, framed tangerine, and a lighter 148.7 as light, framed blue.
- Long description: Two grey swatches for sRGB codes 40 and 200 sit above their two averages. Averaging the codes gives 120. Decoding them to light, averaging and encoding back gives 148.7, a lighter grey. The rule for any blur, resize or composite: decode, average, encode.
- Keywords: sRGB, averaging, linear light, gamma, blur
- Canonical URL: https://canery.in/blogs/colour-and-gamma

### story-04-read-the-article

- File: `assets/social/story-04-read-the-article.png`
- Title: Colour and gamma
- Platforms: Instagram Story
- Role: cta
- Dimensions: 1080×1920
- Narrative beat: the four ideas of the post as a numbered list, then the link
- Technical source: Key takeaways
- Visual structure: lockup and counter; serif title; deck; a tinted panel with four numbered lines; takeaway; CTA footer pointing to the link sticker
- Visible-text transcript: Canery.in · 04 / 04 · Colour and gamma. · Worked on one pixel and one 5×5 patch. · 1 a pixel value is a code, not light · 2 decode, average, then encode · 3 BGR2GRAY is luma, not luminance · 4 Lab needs its white · The full walk-through is on Canery. · LINK IN THE STICKER ABOVE
- Alt text: A numbered list of the article's four ideas, from codes not being light to Lab needing its white, above the link prompt.
- Long description: Four ideas in order: a pixel value is a code, not light; decode, average, then encode; BGR2GRAY is luma, not luminance; and Lab needs its white. The frame points to the link sticker for the full article on Canery.
- Keywords: colour, gamma, luma, luminance, Lab, image processing
- Canonical URL: https://canery.in/blogs/colour-and-gamma
