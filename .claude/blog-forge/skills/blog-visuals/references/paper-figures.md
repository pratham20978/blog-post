# Reusing a figure from a research paper

Use this workflow before drawing a figure whose subject comes from a cited paper. The goal is to
reuse the paper's original explanatory figure when it is the best evidence, not to collect every
image in the paper.

## 1. Relevance gate

Inspect the full paper, including its figures and captions. A figure takes the `source` route only
when all of these are true:

- it directly explains the one point taught in the target section;
- it contains information the surrounding prose would not communicate as clearly;
- the prose will discuss and refer to this specific figure;
- it is not decorative, merely adjacent to the topic, or a duplicate of another selected figure.

Select only the relevant figure or figures. Never extract every figure from a paper. If none pass
this gate, reuse none.

## 2. Rights gate

Verify reuse rights on the paper, publisher page, figure credit, or an explicit permission record.
Accept public domain, a licence that allows this use, or documented permission from the rights
holder. Record the exact licence or permission; a DOI, open-access label, or citation by itself is
not a reuse licence.

If the relevant figure does not have verified reuse rights, do not copy it. Do not generate,
trace, or redraw a lookalike merely to evade this gate. Use prose, or make an original teaching
figure only when it expresses our own analysis or worked example rather than reproducing the
paper's composition.

## 3. Extraction

Use the highest-quality official or author-hosted copy available. Extract the complete figure as
published, including panel labels that the caption or prose relies on. Cropping page margins is
fine; changing data, labels, colours, geometry, or removing inconvenient panels is not. Do not
send the figure through an image generator or restyle it into the house visual system.

Name the local image `fig-NN-<descriptive-name>.<ext>`. Keep the extracted original at that path;
there is no editable redraw source for this route.

## 4. Attribution and handoff

The blog caption must include:

- “Reproduced from”;
- paper title or short citation and the paper's original figure number;
- a public link to the paper or official figure source;
- the licence or permission and any attribution wording that licence requires.

In `manifest.md`, set Route to `source`, explain the relevance under Why, and fill both Source
credit and Rights. Alt text describes what the figure shows; it is not a substitute for credit.
