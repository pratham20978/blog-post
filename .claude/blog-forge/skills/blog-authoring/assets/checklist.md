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
- [ ] Are benchmark numbers reported with their setup?
- [ ] Is anything contested labelled as contested?
- [ ] Are all quotes under fifteen words, and is there at most one per source?
- [ ] Is every reference reachable, with an access date where the page can change?

## Public boundary

- [ ] Can a reader understand the concept with only `blog.md` and its rendered images?
- [ ] Does the article avoid linking to outlines, manifests, ledgers, asset sources, or any unpublished local artifact?
- [ ] Are every definition, reasoning step, expected result, and core example in the article itself?
- [ ] If a runnable lab exists, is only the lab published to a public GitHub repository?
- [ ] Is the public GitHub lab introduced at the first relevant mention with what it contains and when to use it?
- [ ] Do all lab and file links use resolved public GitHub URLs rather than relative local paths?
- [ ] Does every non-anchor link resolve to a public site route or verified public HTTP(S) page?
- [ ] At publish time, does every image use an absolute public HTTP(S) URL?

## Terminology

- [ ] Is every technical term introduced before later sentences rely on it?
- [ ] Does its first meaningful use give the correct canonical name and expand any acronym?
- [ ] Does that introduction say what the term is, why it is used here, and when it matters?
- [ ] Are commonly confused terms distinguished where the confusion could occur?
- [ ] Does an abstract definition get an immediate concrete example?
- [ ] Is every required explanation in the article itself rather than only in a link, public lab, or private file?

## Math

- [ ] Is every symbol defined on first use?
- [ ] Does every equation have a plain-language sentence after it?
- [ ] Are $O$, $\Theta$, and $\Omega$ used correctly?
- [ ] Is the case named for every complexity claim: worst, average, amortised?
- [ ] Are long derivations collapsed?

## Figures

- [ ] Is every figure our own work, not redrawn from a paper or textbook?
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
- [ ] `updated` bumped

## Handoff

- [ ] Every placeholder listed in `manifest.md`
- [ ] When a lab exists, `LAB_REPO` is listed in `manifest.md` and replaced with its public GitHub URL
- [ ] Figure source files kept in `assets/` so they can be edited later
- [ ] `cover-prompt.md` written
- [ ] `linkedin-prompts.md` contains 4–10 coherent, self-contained prompts
- [ ] `linkedin.md` contains carousel order, alt-text checklist, and first-comment link
- [ ] No unresolved placeholders once URLs are filled
- [ ] `validate_post.py --publish` reports no local links, unresolved lab URL, or non-public image targets
