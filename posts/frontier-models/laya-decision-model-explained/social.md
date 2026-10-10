---
social_schema: 2
canonical_url: "https://canery.in/blogs/laya-decision-model-explained"
---

# Social publishing package — laya-decision-model-explained

## LinkedIn post

A decision model never writes its answer. It scores the options you give it.

Convai's Laya, an open 421M-parameter decision model, puts a [MASK] token in front of every option, runs the question and the state through ModernBERT-large and a small head, and reads one score off each [MASK]. A softmax within the question turns the scores into the answer.

We traced one support ticket through it on a laptop CPU, every number printed:

→ The route question's billing option scores a logit of 4.196. Divided by a fitted temperature of 1.760 and softmaxed against three other teams, it comes back as 0.847. Output tokens: 0.
→ "One forward pass" is one batch with one row per question, and every row carries the whole ticket. Three questions over an 88-token ticket cost 399 input tokens, 264 of them the same ticket.
→ Laya returns two fields called confidence. For billing, the probability is 0.847 and the entropy-based confidence is 0.577.
→ act_probability reads 1.0 on every row. The head's output is never normalised, and the act head saturates. Convai's own card says it carries no usable signal yet.
→ 421,293,827 parameters: a 394.8M encoder plus a 26.5M decision head.

The option-marker idea is not new: UniMC used one in 2022, and GLiNER, GLiClass and GLiGuard followed. Laya's new part is the typed contract, one row per question and its training objective.

Part 1 of Frontier Models, and the first of three parts on Laya.

## LinkedIn first comment

The format guarantee is real: a decision model's answer is always one of your options. It says nothing about whether it is the right one.

Read the full article on Canery: https://canery.in/blogs/laya-decision-model-explained

## Instagram caption

A decision model never writes a word. It scores the options you give it. Swipe through Laya, Convai's open decision model, traced on one support ticket: a [MASK] in front of every option, one row per question, a softmax within each question, two different fields called confidence, an act head that always says act, and where the 421 million parameters live.

Every number comes from one run of the model on a laptop CPU.

Link in bio.

#machinelearning #ai #transformers #nlp #llm #deeplearning #python

## Shared feed order

1. `assets/social/feed-01-a-decision-model-scores-options.png` — Laya scores each option at its own [MASK]; billing wins at 0.847 with zero output tokens
2. `assets/social/feed-02-one-pass-is-not-one-read.png` — one row per question, each carrying the whole ticket: 264 of 399 input tokens are the ticket
3. `assets/social/feed-03-from-logit-to-0-847.png` — logits, divided by a fitted temperature, softmaxed within the question
4. `assets/social/feed-04-two-fields-called-confidence.png` — confidence measures spread; answer_confidence is the answer's probability
5. `assets/social/feed-05-act-probability-is-always-one.png` — the unnormalised [CLS] vector saturates the act head
6. `assets/social/feed-06-where-421-million-parameters-live.png` — 394.8M encoder plus 26.5M decision head, counted
7. `assets/social/feed-07-option-markers-are-not-new.png` — the lineage from BERT to Laya, and what is new
8. `assets/social/feed-08-read-the-article.png` — what the article covers, and the CTA

## Instagram Story

- CTA: A decision model never writes a word. See what it computes instead — tap the link.
- Link sticker label: Read the article
- Link sticker URL: https://canery.in/blogs/laya-decision-model-explained

### Story order

1. `assets/social/story-01-a-decision-model-scores-options.png` — Overlay: It scores. It never writes.
2. `assets/social/story-02-one-pass-is-not-one-read.png` — Overlay: The ticket, read three times.
3. `assets/social/story-03-act-probability-is-always-one.png` — Overlay: Don't gate on this field.
4. `assets/social/story-04-read-the-article.png` — Overlay: The full trace. Link below.

## Asset metadata

### feed-01-a-decision-model-scores-options

- File: `assets/social/feed-01-a-decision-model-scores-options.png`
- Title: A decision model scores your options
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: Laya scores each declared option at its own [MASK] and returns a probability per option instead of text
- Technical source: Worked example, Figures 1 and 3; Insights (our run)
- Visual structure: lockup and counter; serif title; one-line deck; a panel with a strip of token tiles in which four marker tiles each drop a line to one bar of the route question's probabilities, billing in the accent; provenance and output-token count along the panel's foot; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 08 · A decision model scores your options. It never writes them. · Laya puts a [MASK] in front of every option and reads a score off each one. · 0.847 · 0.078 · 0.043 · 0.033 · billing · technical · account · sales · OUR RUN · LAYA 0.3.20 · CPU · FP32 · output_tokens = 0 · A softmax over those scores is the answer: billing 0.847 for our support ticket, with zero output tokens. · LAYA, PART 1 · CANERY.IN
- Alt text: A token strip whose four MASK slots each feed one probability bar: billing 0.847, technical 0.078, account 0.043, sales 0.033, zero output tokens
- Long description: A row of coloured token tiles represents one question's input: question tiles, then four option blocks each opened by a marker tile, then the ticket. The first marker, in orange, belongs to billing. A line drops from each marker to a bar: billing 0.847, technical 0.078, account 0.043, sales 0.033, the probabilities Laya returned for the route question on our support ticket. The panel notes the result came from our own run of laya 0.3.20 on a CPU in FP32, and that the model produced zero output tokens. The takeaway is that the answer is a softmax over the scores of the declared options.
- Keywords: decision model, Laya, MASK token, option markers, softmax, ModernBERT, zero output tokens
- Canonical URL: https://canery.in/blogs/laya-decision-model-explained

### feed-02-one-pass-is-not-one-read

- File: `assets/social/feed-02-one-pass-is-not-one-read.png`
- Title: One forward pass is not one read of the ticket
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: each question is its own row carrying a full copy of the state, so input tokens grow with questions × state length
- Technical source: Worked example step 2, Figure 2; How does Laya lay out a question? (L20)
- Visual structure: lockup and counter; serif title; two-line deck; a panel with three horizontal rows to scale, each a blue prefix and a green ticket band of 88 tokens; below, a bar of the 399 reported input tokens split 135 plus three 88s; a sentence; provenance; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 08 · One forward pass is not one read of the ticket. · Laya builds one row per question, and every row carries the whole ticket. The rows run as one batch. · route · 141 tokens · ticket · 88 · urgency · 136 tokens · ticket · 88 · refund · 122 tokens · ticket · 88 · INPUT TOKENS REPORTED · 135 · 88 · 88 · 88 · 264 of 399 are the same ticket, three times · OUR RUN · LAYA 0.3.20 · CPU · FP32 · Three questions over an 88-token ticket: 399 input tokens. The cost grows with questions × state length. · LAYA, PART 1 · CANERY.IN
- Alt text: Three rows of 141, 136 and 122 tokens, each with the same 88-token ticket; 264 of the 399 reported input tokens are the ticket
- Long description: Laya answers three questions about one support ticket by building three sequences, one per question. The rows are 141, 136 and 122 tokens long, and each contains the same 88-token ticket after its question and options. A bar beneath splits the 399 input tokens Laya reported into 135 question, option and special tokens plus three copies of the 88-token ticket, 264 tokens in all. The rows run as one batch, which is what "one forward pass" means, but the ticket is read once per question. Cost therefore grows with the number of questions times the state's length.
- Keywords: Laya, forward pass, batch, input tokens, token cost, decision model, state length
- Canonical URL: https://canery.in/blogs/laya-decision-model-explained

### feed-03-from-logit-to-0-847

- File: `assets/social/feed-03-from-logit-to-0-847.png`
- Title: From a logit of 4.196 to 0.847
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: option logits are divided by a fitted temperature and softmaxed within the question
- Technical source: Worked example step 4; Option-marker scoring, Figure 6; The math, equation (4) (L23, L24)
- Visual structure: lockup and counter; serif title; two-line deck; a panel with a three-row grid (logit, divided by T = 1.760, softmax) across four option columns, billing's softmax cell in the accent; the substituted softmax formula; provenance; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 08 · From a logit of 4.196 to 0.847. · Each option's [MASK] is scored, the scores are divided by a fitted temperature, and a softmax runs within the question. · OPTION · billing · technical · account · sales · LOGIT · 4.196 · −0.012 · −1.069 · −1.512 · ÷ T = 1.760 · 2.384 · −0.007 · −0.607 · −0.859 · SOFTMAX · 0.847 · 0.078 · 0.043 · 0.033 · e^2.384 ÷ (e^2.384 + e^−0.007 + e^−0.607 + e^−0.859) = 1 ÷ 1.181 = 0.847 · OUR RUN · LAYA 0.3.20 · CPU · FP32 · Options compete only inside their own question. Three questions, three separate distributions. · LAYA, PART 1 · CANERY.IN
- Alt text: Route logits 4.196, −0.012, −1.069, −1.512 divided by 1.760 and softmaxed to 0.847, 0.078, 0.043 and 0.033
- Long description: The card follows the route question's four options through the last steps of Laya's scoring. The scorer's logits are 4.196 for billing, −0.012 for technical, −1.069 for account and −1.512 for sales. Laya divides them by the temperature Convai fitted for a three-to-five-option choice, 1.760, giving 2.384, −0.007, −0.607 and −0.859, and a softmax turns those into 0.847, 0.078, 0.043 and 0.033. The substituted formula shows billing's share as 1 divided by 1.181. Options compete only with the other options of their own question.
- Keywords: softmax, logits, temperature, option-marker scoring, Laya, calibration, decision model
- Canonical URL: https://canery.in/blogs/laya-decision-model-explained

### feed-04-two-fields-called-confidence

- File: `assets/social/feed-04-two-fields-called-confidence.png`
- Title: Two fields called confidence
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Laya's confidence field measures the spread of the distribution, while answer_confidence is the answer's probability
- Technical source: Option-marker scoring, Figure 7; The math, equation (6) (L23)
- Visual structure: lockup and counter; serif title; two-line deck; a panel with a three-row table of question, confidence and answer_confidence, the entropy-based values in the accent; the definition in one line; provenance; takeaway; footer
- Visible-text transcript: Canery.in · 04 / 08 · Two fields called confidence. · For choice and score questions, confidence measures how spread the distribution is. answer_confidence is the answer's probability. · QUESTION · CONFIDENCE · ANSWER_CONFIDENCE · route · 0.577 · 0.847 · urgency · 0.324 · 0.530 · refund · 0.859 · 0.859 · confidence = 1 − H(p) / ln k for choice and score; max(p) for noul · OUR RUN · LAYA 0.3.20 · CPU · FP32 · Billing has probability 0.847, but confidence 0.577. Know which one your code thresholds on. · LAYA, PART 1 · CANERY.IN
- Alt text: Table of Laya's two confidence fields: route 0.577 vs 0.847, urgency 0.324 vs 0.530, refund 0.859 for both
- Long description: Laya's response carries two numbers named confidence. For choice and score questions, confidence is one minus the entropy of the returned distribution divided by the log of the option count, a measure of how concentrated the distribution is; for a noul it is the larger of the two probabilities. answer_confidence is the probability of the returned answer for every type. On our ticket, route has confidence 0.577 and answer_confidence 0.847, urgency 0.324 and 0.530, and refund 0.859 for both. Code that thresholds on "confidence" should know which one it reads.
- Keywords: confidence, entropy, answer_confidence, Laya, thresholding, decision model, probability
- Canonical URL: https://canery.in/blogs/laya-decision-model-explained

### feed-05-act-probability-is-always-one

- File: `assets/social/feed-05-act-probability-is-always-one.png`
- Title: act_probability is always 1.0
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the unnormalised [CLS] vector leaving the head saturates the act head, so act_probability is 1.0 on every row
- Technical source: Why act_probability is always 1.0, Figure 10 (L07, L08, L53)
- Visual structure: lockup and counter; serif title; two-line deck; a panel with the route row's [CLS] vector length after the backbone and after the head, the head value in the accent; below a rule, the act and escalate logits; the resulting act_probability; provenance naming issue #185; takeaway; footer
- Visible-text transcript: Canery.in · 05 / 08 · act_probability is always 1.0. · The head's pre-norm layers leave the [CLS] vector unnormalised, and the act head reads it raw. It saturates. · [CLS] VECTOR LENGTH, ROUTE ROW · after the backbone · 35.7 · after the two head layers · 10,377.6 · ACT HEAD LOGITS · act · 4,355.7 · escalate · −3,561.1 · softmax → act_probability 1.0000, on every row · OUR RUN · LAYA 0.3.20 · CPU · FP32 · MECHANISM: LAYA ISSUE #185 · Convai's own card: no usable signal yet. Gate on confidence, never on act_probability. · LAYA, PART 1 · CANERY.IN
- Alt text: The CLS vector grows from 35.7 to 10,377.6 through the head; act logits 4,355.7 vs −3,561.1 give act_probability 1.0000
- Long description: Laya's act/escalate head is meant to say when a decision is safe to automate. On the route row of our ticket, the [CLS] vector's length is 35.7 after the ModernBERT backbone and 10,377.6 after the two decision-head layers, because those pre-norm layers never normalise their output. The act head reads that vector without normalisation, producing logits of 4,355.7 for act and −3,561.1 for escalate, whose softmax is 1.0000. The same happens on every row. Convai's card states the head carries no usable signal yet; the mechanism was first reported in laya issue #185. Gate on confidence instead.
- Keywords: act_probability, escalation, LayerNorm, pre-norm, saturation, Laya, decision head
- Canonical URL: https://canery.in/blogs/laya-decision-model-explained

### feed-06-where-421-million-parameters-live

- File: `assets/social/feed-06-where-421-million-parameters-live.png`
- Title: Where Laya's 421 million parameters live
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: 421,293,827 parameters reconcile as a 394.8M ModernBERT-large encoder plus a 26.5M decision head
- Technical source: Where do the 421 million parameters live?, Figure 11 (L03, L25)
- Visual structure: lockup and counter; serif title; two-line deck; a panel with one stacked bar to scale (embeddings, attention, GeGLU feed-forward, head in the accent); a list of each component's count including norms, a rule and the total; provenance; takeaway; footer
- Visible-text transcript: Canery.in · 06 / 08 · Where Laya's 421 million parameters live. · A 394.8M ModernBERT-large encoder, without BERT's vocabulary head, plus a 26.5M decision head trained from scratch. · embeddings · 51,577,856 · attention · 117,440,512 · GeGLU feed-forward · 225,705,984 · head · 26,512,131 · norms (too thin to draw) · 57,344 · total · 421,293,827 · COUNTED FROM THE LOADED CHECKPOINT (OUR RUN) · The decision head is 6.3% of the model. More than half of Laya is feed-forward weight. · LAYA, PART 1 · CANERY.IN
- Alt text: Stacked bar of Laya's 421,293,827 parameters: embeddings, attention and GeGLU feed-forward, with the 26.5M decision head in orange
- Long description: A single bar drawn to scale splits Laya's parameters by component, counted from the loaded checkpoint: token embeddings 51,577,856, attention across 28 layers 117,440,512, GeGLU feed-forward 225,705,984, and the decision head 26,512,131. Norms add 57,344, too few to draw. Together they total 421,293,827, which matches the card's 421M. The encoder alone is 394,781,696, the card's 395M, and it has no masked-language-model head. The decision head is 6.3% of the model, and more than half of all weights sit in the feed-forward layers.
- Keywords: parameter count, ModernBERT-large, decision head, GeGLU, Laya, model size, 421M
- Canonical URL: https://canery.in/blogs/laya-decision-model-explained

### feed-07-option-markers-are-not-new

- File: `assets/social/feed-07-option-markers-are-not-new.png`
- Title: Option markers are not new
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: one marker per option in one sequence predates Laya; its new part is the contract, the rows and the objective
- Technical source: Where did option markers come from?, Figure 13 (L33, L35–L39)
- Visual structure: lockup and counter; serif title; two-line deck; a panel listing six years, methods and their input format in one line each, Laya's row in the accent; provenance; takeaway; footer
- Visible-text transcript: Canery.in · 07 / 08 · Option markers are not new. · UniMC put a marker before every option in one sequence in 2022. GLiNER, GLiClass and GLiGuard carried the idea on. · 2019 · BERT · 4 sequences, one per option · 2021 · PET · one [MASK], a verbalizer maps words to labels · 2022 · UniMC · [O-MASK] before each option, one sequence · 2024 · GLiNER · [ENT] before each entity type · 2025 · GLiClass · «LABEL» before each label · 2026 · Laya · [MASK] before each option, one row per question · FROM THE CITED PAPERS AND LAYA'S CODE · Laya's new part is the typed contract, one row per question, and its training objective. · LAYA, PART 1 · CANERY.IN
- Alt text: Timeline of marker-based classification from BERT 2019 through PET, UniMC, GLiNER and GLiClass to Laya 2026
- Long description: The card lists how earlier methods fed options to an encoder. BERT in 2019 built one sequence per option. PET in 2021 used one [MASK] and a verbalizer mapping words to labels. UniMC in 2022 put an [O-MASK] marker before each option in a single sequence. GLiNER in 2024 placed an [ENT] marker before each entity type, and GLiClass in 2025 a «LABEL» marker before each label. Laya in 2026 places a [MASK] before each option and builds one row per question. The option-marker layout is inherited; Laya's new contributions are its typed contract, one row per question and its training objective.
- Keywords: UniMC, GLiNER, GLiClass, PET, BERT, option markers, lineage
- Canonical URL: https://canery.in/blogs/laya-decision-model-explained

### feed-08-read-the-article

- File: `assets/social/feed-08-read-the-article.png`
- Title: What a decision model is, traced through Laya
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: what the article covers, and where to read it
- Technical source: the article as a whole; Implementation and Lab downloads
- Visual structure: lockup and counter; serif title; two-line deck; a panel with four headed items (the trace, the model, the traps, the lab), each with two lines; takeaway; CTA footer in the accent
- Visible-text transcript: Canery.in · 08 / 08 · What a decision model is, traced through Laya. · The first part of Frontier Models, and the first of three on Convai's open decision model. · the trace · one ticket, three typed questions, every number · tokens, markers, shapes, logits, softmax, JSON · the model · ModernBERT-large + a decision head built from scratch · 421,293,827 parameters, reconciled by hand · the traps · three checkpoints are three models · act_probability, confidence, option names · the lab · a CPU script that reproduces it all · laya 0.3.20 · checks every probability · The full walk-through, with the lab to run it yourself on a laptop CPU. · READ IT AT CANERY.IN/BLOGS/LAYA-DECISION-MODEL-EXPLAINED
- Alt text: Summary card listing the trace, the model, the traps and the lab, with a link to the article on canery.in
- Long description: The closing card summarises the article in four items. The trace follows one ticket and three typed questions through every number: tokens, markers, shapes, logits, softmax and the returned JSON. The model is ModernBERT-large plus a decision head built from scratch, 421,293,827 parameters reconciled by hand. The traps are that the three checkpoints are three different models, and that act_probability, the confidence fields and option names can mislead. The lab is a CPU script with laya 0.3.20 that reproduces the numbers and checks every probability. The footer gives the article's address.
- Keywords: Laya, decision model, Frontier Models, lab, ModernBERT, trace, Canery
- Canonical URL: https://canery.in/blogs/laya-decision-model-explained

### story-01-a-decision-model-scores-options

- File: `assets/social/story-01-a-decision-model-scores-options.png`
- Title: A decision model never writes a word
- Platforms: Instagram Story
- Role: cover
- Dimensions: 1080×1920
- Narrative beat: Laya scores declared options and returns probabilities with zero output tokens
- Technical source: Worked example, Figure 3 (our run)
- Visual structure: lockup and counter; serif title; two-line deck; four large bars of the route probabilities, billing in the accent; provenance and output-token count; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 04 · A decision model never writes a word. · It scores the options you declare, one [MASK] per option. · 0.847 · 0.078 · 0.043 · 0.033 · billing · technical · account · sales · OUR RUN · LAYA 0.3.20 · CPU · FP32 · output_tokens = 0 · Our support ticket: billing at 0.847, with zero output tokens. · LAYA, PART 1 · CANERY.IN
- Alt text: Four bars of Laya's route answer, billing 0.847, technical 0.078, account 0.043, sales 0.033, with zero output tokens
- Long description: A vertical Story frame shows the probabilities Laya returned when asked which team should own our support ticket: billing 0.847, technical 0.078, account 0.043 and sales 0.033. The model scores the options declared in the request, one [MASK] per option, and writes no text: output tokens are zero. The numbers come from our own run of laya 0.3.20 on a CPU in FP32.
- Keywords: decision model, Laya, zero output tokens, probabilities, MASK token, routing
- Canonical URL: https://canery.in/blogs/laya-decision-model-explained

### story-02-one-pass-is-not-one-read

- File: `assets/social/story-02-one-pass-is-not-one-read.png`
- Title: One pass is not one read
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: each question gets a row with the whole ticket, so 264 of 399 input tokens are the ticket
- Technical source: Worked example step 2, Figure 2 (L20)
- Visual structure: lockup and counter; serif title; two-line deck; three rows to scale, each a prefix and an 88-token ticket band; a sentence with the token totals; provenance; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 04 · One pass is not one read. · Each question gets its own row, and every row carries the ticket. · route · 141 tokens · ticket · 88 · urgency · 136 tokens · ticket · 88 · refund · 122 tokens · ticket · 88 · 399 input tokens: 264 are the ticket · OUR RUN · LAYA 0.3.20 · CPU · FP32 · Cost grows with questions × state length. · LAYA, PART 1 · CANERY.IN
- Alt text: Three rows of 141, 136 and 122 tokens each holding the same 88-token ticket; 264 of 399 input tokens are the ticket
- Long description: Laya's single forward pass is a batch of three rows, one per question, of 141, 136 and 122 tokens. Each row contains the same 88-token support ticket, so of the 399 input tokens Laya reported, 264 are the ticket read three times. The cost of a request grows with the number of questions multiplied by the length of the state. Our own run of laya 0.3.20 on a CPU.
- Keywords: Laya, input tokens, batch, forward pass, token cost, decision model
- Canonical URL: https://canery.in/blogs/laya-decision-model-explained

### story-03-act-probability-is-always-one

- File: `assets/social/story-03-act-probability-is-always-one.png`
- Title: act_probability is 1.0, always
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: the act head saturates on an unnormalised vector, so gate on confidence instead
- Technical source: Why act_probability is always 1.0, Figure 10 (L07, L08)
- Visual structure: lockup and counter; serif title; two-line deck; a panel with the [CLS] vector length after the backbone and after the head, then act_probability 1.0000 in the accent; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 04 · act_probability: 1.0, always. · The act head reads an unnormalised vector and saturates. · [CLS] VECTOR LENGTH · after the backbone · 35.7 · after the head · 10,377.6 · act_probability · 1.0000 · on every row, whatever the ticket says · Gate on confidence instead, as Convai's card advises. · LAYA, PART 1 · CANERY.IN
- Alt text: The CLS vector grows from 35.7 to 10,377.6 through Laya's head, and act_probability reads 1.0000 on every row
- Long description: Laya's act/escalate head reads the [CLS] vector after the two decision-head layers, which never normalise their output. On our route row the vector's length grows from 35.7 after the backbone to 10,377.6 after the head, and the act head's softmax saturates at 1.0000. It does so on every row whatever the ticket says, so the field carries no information. Convai's card advises gating on confidence instead.
- Keywords: act_probability, escalation, saturation, LayerNorm, Laya, decision head
- Canonical URL: https://canery.in/blogs/laya-decision-model-explained

### story-04-read-the-article

- File: `assets/social/story-04-read-the-article.png`
- Title: A decision model, traced
- Platforms: Instagram Story
- Role: cta
- Dimensions: 1080×1920
- Narrative beat: the four ideas the article traces, and the link
- Technical source: the article as a whole
- Visual structure: lockup and counter; serif title; two-line deck; an accent-tinted panel with four numbered lines; takeaway; CTA footer pointing to the link sticker
- Visible-text transcript: Canery.in · 04 / 04 · A decision model, traced. · Every number from one run of Laya on a laptop CPU. · 1 · one [MASK] per option · 2 · one row per question · 3 · one softmax per question · 4 · 421,293,827 parameters · The full walk-through is on Canery. · LINK IN THE STICKER ABOVE
- Alt text: Four numbered points: one MASK per option, one row per question, one softmax per question, 421,293,827 parameters
- Long description: The closing Story frame lists the four ideas the article traces through Laya: one [MASK] token per option, one input row per question, one softmax per question, and 421,293,827 parameters reconciled by hand. Every number in the article comes from one run of the model on a laptop CPU. The footer points to the link sticker for the full walk-through on canery.in.
- Keywords: Laya, decision model, MASK token, softmax, parameters, Canery
- Canonical URL: https://canery.in/blogs/laya-decision-model-explained
