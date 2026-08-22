# Canerly — logo

Monochrome black. All files are outlined SVG: no font dependency, no external
references, scales cleanly to any size.

| File | Use |
| --- | --- |
| `canerly-symbol.svg` | Symbol alone — avatars, favicons, tight spaces, app chrome |
| `canerly-wordmark.svg` | Wordmark alone — when the bird already appears nearby |
| `canerly-lockup-horizontal.svg` | Primary logo — site headers, docs, signatures |
| `canerly-lockup-stacked.svg` | Vertical spaces — cards, merch, centred layouts |
| `canerly-app-icon.svg` | Bird reversed out of a black squircle — app / social tile |

## The mark

A crested canary in side profile, facing right. It's one closed silhouette with
the eye knocked out (`fill-rule="evenodd"`), so it works on any background without
a second colour. The beak points into the wordmark, leading the eye toward the name.

The wordmark is Manrope 800, tracked to −0.035em, with one custom letter: the `y`
descender sweeps into a tail flick that echoes the bird's tail. That flick is what
makes it a wordmark rather than a name typed in a typeface — keep it.

## Colour

Black `#000000` on light, white `#FFFFFF` on dark. To reverse, set `fill` on the
`<svg>` — the paths inherit it:

```html
<img src="canerly-lockup-horizontal.svg" alt="Canerly">   <!-- black, as shipped -->
```

Inline, for a colour that follows the theme, swap `fill="#000"` on the root
`<svg>` for `fill="currentColor"`.

## Clear space

Keep clear space on all sides equal to **half the symbol's height**. Nothing —
type, rules, image edges — inside that.

## Minimum sizes

| | Minimum |
| --- | --- |
| Symbol | 16 px tall |
| Horizontal lockup | 100 px wide |
| Stacked lockup | 84 px wide |

Below 16 px the tail thins out; use the app icon instead.

## Don't

- Recolour to anything but black or white
- Rebuild the lockup by hand — the symbol-to-wordmark gap and sizing are set
- Stretch, rotate, outline, or add effects
- Set "Canerly" in another typeface and call it the wordmark
