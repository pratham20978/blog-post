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
- [ ] Figure source files kept in `assets/` so they can be edited later
- [ ] `cover-prompt.md` written
- [ ] `linkedin-prompts.md` contains 4–10 coherent, self-contained prompts
- [ ] `linkedin.md` contains carousel order, alt-text checklist, and first-comment link
- [ ] No unresolved placeholders once URLs are filled
