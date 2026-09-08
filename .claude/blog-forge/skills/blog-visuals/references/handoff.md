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

| Placeholder | File | Suggested path | Alt text |
|---|---|---|---|
| COVER | cover.png | blog/tcp-slows-down-on-wifi/cover-v1.png | Abstract illustration of a wireless link dropping packets |
| FIG_01 | fig-01-handshake.png | blog/tcp-slows-down-on-wifi/fig-01-v1.png | Three-way handshake with sequence numbers on each arrow |
| FIG_02 | fig-02-cwnd.png | blog/tcp-slows-down-on-wifi/fig-02-v1.png | Congestion window over time, sawtooth on loss |

Upload each file to the suggested path, then write the resulting URLs into
urls.txt in the same order and run:

    python3 scripts/fill_urls.py posts/tcp-slows-down-on-wifi/ urls.txt
```

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
```

`fill_urls.py` replaces every placeholder in `blog.md`, including the frontmatter `cover_image`. It refuses to write if the line count does not match the manifest, and reports any placeholder left unresolved.

---

## Keeping figures editable

The post folder keeps, for every figure:

- `.mmd` — the Mermaid source, when Mermaid was used
- `.html` — the diagram-design output, which is the real source of truth
- `.svg` — vector export
- `.png` — what ships

Six months later a figure will need a correction. With the `.html` kept, that is a two-minute edit and a re-export. Without it, the figure is redrawn from scratch and looks slightly different from its neighbours.
