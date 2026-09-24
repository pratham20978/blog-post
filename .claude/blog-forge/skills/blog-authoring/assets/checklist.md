# Pre-publish checklist

Run after `validate_post.py` passes. The script checks structure; this checks judgment. Answer each honestly. One "no" blocks publish.

---

## Substance

- [ ] Does Insights state an actual finding, not a description of the post?
- [ ] Could a reader who reads only Insights explain one true thing afterwards?
- [ ] Is the problem stated before the solution appears?
- [ ] Does the worked example use real numbers, and show intermediate values?
- [ ] Is the worked example small enough to follow by hand?
- [ ] Does every body section teach something the others do not?
- [ ] For each section: what can the reader do now that they could not before? If any two answers match, one is padding.
- [ ] Does the Limitations section contain real failure modes, not generic caution?

## Sources

- [ ] Does every number, date, version, complexity bound, and named result trace to a ledger entry?
- [ ] Is every ledger source tier T1–T3, except where used only for framing?
- [ ] Did the literature sweep actually run, and does `## Search log` record the queries?
- [ ] Was a survey or review looked for before the individual papers?
- [ ] Were citations chased forward from the two central papers, not only backward?
- [ ] Does the post rest on the tier's floor of peer-reviewed or standard sources, or does a `## Literature note` say honestly why the topic has none?
- [ ] Does every peer-reviewed source carry a venue, a year, and a DOI or arXiv id?
- [ ] Is every preprint labelled a preprint in the post, and was DBLP checked for a published version?
- [ ] Are benchmark numbers reported with their setup?
- [ ] Is anything contested labelled as contested?
- [ ] Are all quotes under fifteen words, and is there at most one per source?
- [ ] Is every reference reachable, with an access date where the page can change?

## Public boundary

- [ ] Can a reader understand the concept with only `blog.md` and its rendered images?
- [ ] Does the article avoid linking to outlines, manifests, ledgers, asset sources, or any unpublished local artifact?
- [ ] Are every definition, reasoning step, expected result, and core example in the article itself?
- [ ] If a runnable lab exists, is each publishable file under `lab/` and listed exactly once in `manifest.md`?
- [ ] Does the body point to the final Lab downloads section instead of linking local files?
- [ ] Are all lab links grouped under `### Lab downloads` in the final References section?
- [ ] Does every lab link name the file and explain its purpose?
- [ ] Do resolved lab links use public `https://minio.canery.in/media/` URLs?
- [ ] Does every non-anchor link resolve to a public site route or verified public HTTP(S) page?
- [ ] At publish time, does every image use an absolute public HTTP(S) URL?

## Terminology

- [ ] Is every technical term introduced before later sentences rely on it?
- [ ] Does its first meaningful use give the correct canonical name and expand any acronym?
- [ ] Does that introduction say what the term is, why it is used here, and when it matters?
- [ ] Are commonly confused terms distinguished where the confusion could occur?
- [ ] Does an abstract definition get an immediate concrete example?
- [ ] Is every required explanation in the article itself rather than only in a download or private file?

## Math

- [ ] Is every symbol defined on first use?
- [ ] Does every equation have a plain-language sentence after it?
- [ ] Are $O$, $\Theta$, and $\Omega$ used correctly?
- [ ] Is the case named for every complexity claim: worst, average, amortised?
- [ ] Are long derivations collapsed?

## Figures

- [ ] Did the route gate run for every figure, and is the route and its reason recorded in `manifest.md`?
- [ ] For every paper-backed section, were the paper's figures inspected before a replacement was drawn?
- [ ] Is each `source` figure directly necessary to its section—not merely related—and are irrelevant paper images omitted?
- [ ] Does each `source` figure record its paper, original figure number, public source, and verified rights in the manifest and caption?
- [ ] Was every `source` figure preserved unchanged rather than regenerated, traced, or restyled?
- [ ] Is any figure hand-placed only because nodes, edge labels, or a whole branch were dropped to make it fit? That one is a `mermaid` figure.
- [ ] Does every node carry its real name and its shape, type, or value — on Mermaid routes as well as placed ones?
- [ ] Does every edge carry a label saying what travels along it?
- [ ] Does each `mermaid` route have a kept `.mmd`, and each `placed` or `chart` route a kept `.html`?
- [ ] Is every non-`source` figure our own analysis rather than a lookalike redraw of a paper or textbook figure?
- [ ] Does the prose refer to every figure?
- [ ] Does every figure have a number, a caption, and descriptive alt text?
- [ ] Does each figure sit next to the text explaining it?
- [ ] Would removing any figure lose information? If not, remove it.
- [ ] Is the figure count within the tier's range?

## Prose

- [ ] Does the opening sentence carry information, not throat-clearing?
- [ ] Are there section-closing summary sentences? Remove them.
- [ ] Any hedging stacks, "it is worth noting", or headings restated as first sentences?
- [ ] Any list of three where the third item was invented for symmetry?
- [ ] Any "as you probably know" or "this should be obvious"? Remove.

## Metadata

- [ ] Title under 60 characters, keyword near the front, promises something specific
- [ ] Summary 150–160 characters and usable as a meta description
- [ ] 4–7 tags, first one matches the category, no near-duplicates of existing tags
- [ ] `tier`, `difficulty`, `prerequisites`, `reading_minutes` all set
- [ ] Does the difficulty match what the post actually demands, rather than what the tier implies?
- [ ] For a series part: are `series` and `series_position` both present and correct?
- [ ] Does the member live at `posts/<series-slug>/<post-slug>/`, beside the series `plan.md` and `context.md`?
- [ ] Was `context.md` read before this part was researched or outlined?
- [ ] Does the part answer only the question the series plan gave it, and defer what the plan defers?
- [ ] After the gate, was `context.md` updated from the final artifacts with completed knowledge, durable decisions, open threads, and the next-part brief?
- [ ] Is the series context under 2,000 words and free of copied prose, outlines, ledgers, and source dumps?
- [ ] Does it link the parts it depends on by canonical URL and anchor, never by local path?
- [ ] `updated` bumped

## Handoff

- [ ] Every placeholder listed in `manifest.md`
- [ ] Every publishable lab file has one contiguous `LAB_XX` placeholder and one MinIO object URL
- [ ] Multi-file labs include `README.md`; caches, secrets, virtual environments, and generated files are excluded
- [ ] Figure source files kept in `assets/`; `source` figures keep the exact extracted original plus credit and rights
- [ ] `cover-prompt.md` written
- [ ] `linkedin-prompts.md` contains 4–10 coherent, self-contained prompts
- [ ] New posts have `social.md`, 5–8 shared feed cards, and 3–5 Story frames
- [ ] Every social frame has the full Canery lockup and matching HTML/SVG/PNG files
- [ ] Every technical social card uses an article-specific technical artefact
- [ ] `social.md` contains platform copy, Story overlays/CTA, image titles, transcripts, alt text, long descriptions, keywords, and canonical URL
- [ ] Legacy posts without `social.md` retain a valid `linkedin.md` handoff
- [ ] No unresolved placeholders once URLs are filled
- [ ] `validate_post.py --publish` reports no local links, unresolved lab downloads, non-MinIO lab URLs, or non-public image targets
