# Handoff

The skill produces files. The user uploads them. A script fills the URLs. Nothing here touches object storage.

---

## Placeholders

`blog.md` references figures by placeholder:

```markdown
![Three-way handshake: client SYN, server SYN-ACK, client ACK, with sequence numbers](FIG_01)
*Figure 1. The connection is established after the second message; the third only confirms it to the server.*
```

The cover uses `COVER`, in both frontmatter and the image line.

Placeholders are deliberately not valid URLs. A missed one fails visibly rather than rendering a broken image in production.

---

## manifest.md

```markdown
# Asset manifest — tcp-slows-down-on-wifi

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | cover.png | generated | cover | — | — | blog/tcp-slows-down-on-wifi/cover-v1.png | Abstract illustration of a wireless link dropping packets |
| FIG_01 | fig-01-paper-model.png | source | the section explains this exact model figure | Author et al., Paper title, Figure 2, https://... | CC BY 4.0 | blog/tcp-slows-down-on-wifi/fig-01-v1.png | The paper's model architecture with its three processing stages |
| FIG_02 | fig-02-handshake.png | mermaid | 3 participants, strict message order | — | — | blog/tcp-slows-down-on-wifi/fig-02-v1.png | Three-way handshake with sequence numbers on each arrow |
| FIG_03 | fig-03-cwnd.png | chart | measured cwnd, ledger rows L-07 to L-09 | — | — | blog/tcp-slows-down-on-wifi/fig-03-v1.png | Congestion window over time, sawtooth on loss |
| FIG_04 | fig-04-segment.png | placed | header fields must be drawn to scale | — | — | blog/tcp-slows-down-on-wifi/fig-04-v1.png | TCP segment header with field widths proportional to their bit counts |

Upload each file to the suggested object key, then write the resulting URLs into
urls.txt in the same order and run:

    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/fill_urls.py" posts/tcp-slows-down-on-wifi/ urls.txt
```

Route and Why are kept in the manifest for two reasons. They are the record that the route gate
was run on this figure rather than skipped, which is the only way an audit can tell a reasoned
`placed` from a lazy one. And they tell the next editor which source file to open — a `.mmd` for
`mermaid`, a `.html` for `placed` and `chart`, a `.py` or `.svg` for `plot`.
For `source`, Source credit and Rights are mandatory: they record the paper, original figure
number, public source, and verified reuse basis.

---

## Version suffixes

Every stored path ends in `-vN`:

```
blog/<slug>/cover-v1.png
blog/<slug>/fig-01-v1.png
```

When a figure is corrected, upload as `-v2` and update the post. Do not overwrite the old object.

The reason: images are cached hard, sometimes for a year, by browsers, CDNs, and third-party image proxies. Overwriting an object at the same path leaves an unknown number of caches serving the old picture with no way to flush them. A new path is the only reliable invalidation.

---

## urls.txt

One URL per line, in manifest order, blank lines and `#` comments ignored:

```
https://cdn.example.com/blog/tcp-slows-down-on-wifi/cover-v1.png
https://cdn.example.com/blog/tcp-slows-down-on-wifi/fig-01-v1.png
https://cdn.example.com/blog/tcp-slows-down-on-wifi/fig-02-v1.png
https://cdn.example.com/blog/tcp-slows-down-on-wifi/fig-03-v1.png
```

`fill_urls.py` replaces every placeholder in `blog.md`, including the frontmatter `cover_image`. It refuses to write if the line count does not match the manifest, and reports any placeholder left unresolved.

---

## Keeping figures editable

What the post folder keeps depends on the route, and the Route column is how you know which file to open:

| Route | Editable source kept | Exports |
|---|---|---|
| `source` | the unchanged extracted image plus manifest credit and rights; no redraw source | the same image, or a format conversion that does not alter its content |
| `mermaid` | `.mmd` — the graph, re-laid-out by one command | `.svg`, `.png` |
| `placed`, `chart` | `.html` — the diagram-design output, the real source of truth | `.svg`, `.png` |
| `plot` | `.py`, or the hand-authored `.svg` | `.svg`, `.png` |
| `capture` | the command or query that produced it, in the caption | `.png` |
| `generated` | the prompt in `cover-prompt.md` | `.png` |

Six months later a figure will need a correction. With its source kept, that is a two-minute edit and a re-export. Without it, the figure is redrawn from scratch and looks slightly different from its neighbours.
