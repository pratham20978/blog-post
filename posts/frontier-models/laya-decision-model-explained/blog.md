---
title: "Laya, Part 1: What a Decision Model Is, Traced Through Laya"
slug: laya-decision-model-explained
date: 2026-09-26
updated: 2026-09-26
summary: "A decision model scores options you declare instead of writing text. Laya traced end to end: a [MASK] per option, one softmax per question, zero output tokens."
tags: [machine-learning, decision-model, transformer, text-classification, model-architecture, deep-learning]
category: machine-learning
categories: [machine-learning]
series: frontier-models
series_position: 1
tier: L4
difficulty: intermediate
prerequisites: ["the Transformer encoder: self-attention, residual connections, LayerNorm", "softmax", "reading a JSON request"]
reading_minutes: 41
cover_image_url: "COVER"
cover_image_alt: "A row of token tiles in which four tiles glow as masked slots, each feeding one bar of a small probability chart"
canonical_url: "https://canery.in/blogs/laya-decision-model-explained"
---

> [!NOTE]
> **Insights** — A decision model answers typed questions about a piece of state by scoring the options you declare in the request, and it returns a probability for each option instead of writing text. Laya, Convai's open 421-million-parameter decision model, builds one sequence per question: the question, a `[MASK]` token in front of every option, then the state. It runs those sequences as one batch through a ModernBERT-large encoder and a small head, and reads a score off each `[MASK]`. On the support ticket traced here, the billing option's logit of 4.196 becomes a returned probability of 0.847, and the model writes zero output tokens. The format guarantees that the answer is one of your options. It says nothing about whether it is the right one.

**Level:** intermediate · **You need:** the Transformer encoder (self-attention, residual connections, LayerNorm), softmax, and enough Python to read a JSON request · **Time:** ~41 min

This is the first part of *Frontier Models* and the first of three parts on Laya. It traces one request through the open `laya` checkpoint, the set of trained weights Convai published, on a laptop CPU and prints every number on the way. Latency, calibration and failure modes each get a later part of their own.

> [!IMPORTANT]
> Every Laya number in this post carries one of three labels. **Our run** means we measured it: laya 0.3.20 on a CPU in 32-bit floating point (FP32), checkpoint commit `55cf4c4e`, one call to the library's own `predict()`. The probabilities it returned were recomputed from the captured logits and agree to four decimals. **Vendor-reported** means the number comes from Convai's model card. **Third-party** numbers name who measured them. The three are never mixed in one figure without a legend.

**Jump to:** [The problem](#the-problem) · [Worked example](#worked-example) · [Intuition](#intuition) · [What a decision model is](#what-a-decision-model-is) · [Layout](#how-does-laya-lay-out-a-question) · [Option-marker scoring](#option-marker-scoring) · [Inside Laya](#what-is-inside-laya) · [Parameters](#where-do-the-421-million-parameters-live) · [Lineage](#where-did-option-markers-come-from) · [The math](#the-math) · [Implementation](#implementation) · [Limitations](#limitations-and-common-mistakes)

## Why this matters

Two decision models launched three days apart. TypeSafe AI released its hosted model, Jev, on 15 September 2026 and called it the first "System One model". <!-- L14 --> On 18 September Convai Innovations answered with Laya, which has open weights under Apache-2.0. <!-- L01 --> Teams are now putting these models where an LLM in JSON mode used to sit: routing tickets, triaging email, gating an agent's next step. The appeal is simple. The model returns a typed answer with a probability, not text to parse. <!-- L02 -->

Three misreadings are already common, and each one costs something. "One forward pass" sounds as if the state is read once. In Laya, every question carries its own copy of the state, so ten questions over a 400-token email are ten rows of about 400 tokens. `act_probability` sounds like the signal for handing a case to a human. On Laya it reads 1.0 for almost every input. <!-- L07 --> And "can't hallucinate" sounds like "can't be wrong". Tracing one request through the model, number by number, settles all three.

## The problem

A customer writes in:

> **Subject:** Charged twice after upgrading, and the app keeps logging us out
>
> Hi, we upgraded to the Team plan on 3 March and our card was charged twice (2 x $49). Since the upgrade the desktop app logs everyone out every few minutes, so nobody on the team can work. Please refund the duplicate charge and fix the logouts today. We have a client demo tomorrow morning.

Your support software needs three answers it can branch on:

- **Route.** Which team owns the ticket: billing, technical, account or sales?
- **Urgency.** One of five ordered levels, from "no action needed" to "immediately, work is blocked".
- **Refund.** Does the customer ask for a refund, yes or no?

The ticket is built to be slightly awkward. It is about a charge and a bug. It asks for a refund and a fix. It names a deadline. A good answer should come with some doubt attached, and your code needs to see that doubt as a number.

Two tools already do this job, and each gives up something you want.

**A fine-tuned classifier.** Put an encoder under a linear output layer with one row per label, and train it on labelled tickets. This is how BERT is fine-tuned: the `[CLS]` token's final vector feeds a small classification layer that is new at fine-tuning time. <!-- L32 --> A classifier is fast and returns a real probability distribution, but its label set is frozen into its weights. A routing layer over a 1,024-number vector is a 1,024 × 4 matrix plus 4 biases: 4,100 numbers, one row per team. A fifth team means a new row, new labels and a new training run. Each of your three questions needs its own head.

**An LLM in JSON mode.** Declare a schema in the prompt. Constrained decoding then masks, at every generation step, every token that would break the schema. <!-- L42 --> The options live in the request, so adding a team costs nothing. But the answer has to be written out. `{"route": "billing", "urgency": 3, "refund": true}` is 19 tokens under the tokenizer Laya uses. An LLM's own tokenizer would give a different count, but still one token at a time, each needing a pass through the decoder after the prompt is read.

The only probability the LLM can give you is its probability for the next token, given the tokens before it. That is a statement about text, not a decision. It can also be badly calibrated. OpenAI reported that GPT-4's pre-trained model was well calibrated on a subset of MMLU, a multiple-choice knowledge benchmark, and that post-training reduced this calibration. <!-- L43 --> Constraining the format does not, by itself, make an LLM worse at classifying. One study found JSON mode competitive with free-text answers on classification tasks, and sometimes better, even though it hurt reasoning. <!-- L41 --> The costs of the LLM route are the sequential decode and the meaning of the probability, not accuracy.

What you want is the classifier's output with the LLM's interface. That means one distribution per question over exactly that question's options, with the options declared in the request, any number of them, and nothing retrained. The obstacle is the classifier's output layer: it has one row per label, and the rows are fixed when training ends. A model that never saw the label "sales" has no row for it.

Laya's answer is to stop storing labels in the output layer and to put them in the input instead. Every option becomes a position in the sequence, and the model scores positions.

## Worked example

Here is the whole request, in the request shape Laya shares with TypeSafe's API:

```json
{
  "state": {
    "subject": "Charged twice after upgrading, and the app keeps logging us out",
    "body": "Hi, we upgraded to the Team plan on 3 March and our card was charged twice (2 x $49). Since the upgrade the desktop app logs everyone out every few minutes, so nobody on the team can work. Please refund the duplicate charge and fix the logouts today. We have a client demo tomorrow morning."
  },
  "questions": {
    "route":   {"type": "choice", "instructions": "Which support team should own this ticket?",
                "criteria": {"billing":   "charges, invoices and refunds",
                             "technical": "bugs, crashes, login and sync errors",
                             "account":   "plan changes, seats and permissions",
                             "sales":     "pricing questions and new contracts"}},
    "urgency": {"type": "score", "instructions": "How urgent is this ticket?",
                "criteria": ["no action needed", "within a week", "within two days",
                             "today", "immediately, work is blocked"]},
    "refund":  {"type": "noul", "instructions": "Does the customer ask for a refund?"}
  }
}
```

The **state** is the thing being judged; here it is a JSON object. Each **question** has a type and a list of **options**, the answers it is allowed to give. The three types are *choice* (pick one option), *score* (pick a level on an ordered scale) and *noul* (yes or no). They are TypeSafe's primitives, and Laya uses the same names. <!-- L15 -->

Laya first turns the state object into one string with Python's `json.dumps`, then splits it into **tokens** with ModernBERT's tokenizer. A tokenizer is the fixed rule that cuts text into the units a model reads. This one is a byte-pair encoder with a 50,368-entry vocabulary. <!-- L25 --> The ticket comes to **88 tokens** (our run).

### Step 1: one sequence per question

Laya builds a separate sequence for each question. Three special tokens do the bookkeeping. `[CLS]` opens a sequence, `[SEP]` separates its parts, and `[MASK]` is the token BERT-style models were pre-trained to fill in. Laya places one `[MASK]` in front of every option, so each option gets its own marked slot. <!-- L04 --> <!-- L19 -->

The options are rendered as text first. A choice option becomes `billing: charges, invoices and refunds`. A score level becomes `level 3: today`. A noul question given no wording gets two default options, `false: no, the statement does not hold` and `true: yes, the statement holds`. <!-- L21 -->

Figure 1 is the route question's sequence, token by token.

![The route row's 141 tokens in a grid coloured as question, option, marker and state, with MASK markers at 13, 23, 34 and 43](FIG_01)
*Figure 1. The route row is 141 tokens: `[CLS]`, 11 question tokens, `[SEP]`, four options that each open with a `[MASK]` (positions 13, 23, 34 and 43), `[SEP]`, the ticket's 88 tokens at positions 52 to 139, and a final `[SEP]`. The `Ġ` prefix is how this tokenizer marks a leading space. Our run.*

The route row adds up exactly: 1 + 11 + 1 + 38 option tokens + 1 + 88 + 1 = 141. The urgency row has 9 question tokens and five options, with markers at 11, 18, 25, 32 and 37, for 136 tokens. The refund row has 12 question tokens (the tokenizer splits "noul" in two) and two options, with markers at 14 and 24, for 122 tokens.

### Step 2: one batch

The three rows are stacked into one tensor. Shorter rows are filled with `[PAD]` tokens to the longest row's length. An **attention mask** of ones and zeros tells the model which positions are real. Figure 2 draws the batch to scale.

![Three token rows of 141, 136 and 122 real tokens padded to 141, with the same 88-token ticket band repeated in every row](FIG_02)
*Figure 2. "One forward pass" is one batch of shape `[3, 141]`. Each row holds its own copy of the ticket, so the 399 input tokens that Laya reports include the same 88 tokens three times: 264 of the 399. Our run.*

The library counts every real position in every row. For this request it reports `input_tokens: 399` and `output_tokens: 0`. <!-- L20 --> Two-thirds of that input is one ticket, read three times.

### Step 3: through the model

The batch then goes through four stages. Each stage keeps the batch and position axes and changes only what sits at each position.

1. The **backbone**, a 28-layer ModernBERT-large encoder, turns `[3, 141]` token ids into `[3, 141, 1024]`: one 1,024-number **hidden state** per position. <!-- L25 -->
2. The **decision head** adds a learned vector for the question's type (choice, score or noul) to every position, then runs two more Transformer layers. The shape stays `[3, 141, 1024]`. <!-- L22 -->
3. Laya then **gathers** the hidden states at the marker positions, giving `[3, 5, 1024]`. The 5 is the most options any question has (urgency's five levels). Route fills four of the slots and refund fills two. The rest are empty slots, marked unused.
4. The **option scorer**, a small two-layer network, turns each gathered vector into one number, a **logit**: an unnormalised score where higher means a better fit. The result is `[3, 5]`.

These are the logits the scorer produced (our run):

| Question | Option logits |
|---|---|
| route | billing **4.196** · technical −0.012 · account −1.069 · sales −1.512 |
| urgency | level 0 −2.715 · level 1 −0.301 · level 2 1.537 · level 3 2.643 · level 4 **3.320** |
| refund | false −2.392 · true **1.186** |

### Step 4: a softmax per question

A **softmax** turns a list of logits into probabilities: exponentiate each one, then divide by the total. Laya does this separately for each question, so route's options compete only with each other. First it divides every logit by a **temperature** $T$ that Convai fitted for each question type and option count. The English checkpoint ships $T = 1.760$ for a choice with 3 to 5 options, $1.251$ for a score with 3 to 5 levels, and $1.983$ for a noul. <!-- L23 --> <!-- L24 -->

For route, dividing by 1.760 gives 2.384, −0.007, −0.607 and −0.859. Exponentiating relative to the largest gives 1, 0.092, 0.050 and 0.039, which sum to 1.181. So billing's probability is 1 / 1.181 = **0.847**. Technical gets 0.078, account 0.043 and sales 0.033. At $T = 1$, billing would have been 0.977. The fitted temperature softens a model that Convai says ships over-confident <!-- L54 -->, and why it is fitted that way belongs to the calibration part of this series.

![Bar charts of the returned probabilities for route, urgency and refund, each option's T equals 1 probability marked beside it](FIG_03)
*Figure 3. The decision readout. Filled bars are what Laya returns; open ticks are the same logits softmaxed at T = 1. Route is billing at 0.847, urgency is spread across its top three levels, and refund is yes at 0.859. Our run.*

### Step 5: the returned JSON

Laya then assembles typed answers from the three distributions. This is the response, trimmed:

```json
{
  "answers": {
    "route":   {"type": "choice", "choice": "billing",
                "probabilities": {"billing": 0.8468, "technical": 0.0776, "account": 0.0426, "sales": 0.0331},
                "confidence": 0.5772, "answer_confidence": 0.8468, "action": {"act_probability": 1.0}},
    "urgency": {"type": "score", "score": 3.3312,
                "probabilities": {"0": 0.0043, "1": 0.0294, "2": 0.1275, "3": 0.3086, "4": 0.5303},
                "confidence": 0.3236, "answer_confidence": 0.5303, "action": {"act_probability": 1.0}},
    "refund":  {"type": "noul", "noul": 0.8586,
                "confidence": 0.8586, "answer_confidence": 0.8586, "action": {"act_probability": 1.0}}
  },
  "usage": {"input_tokens": 399, "output_tokens": 0}
}
```

The choice answer is the most probable option, billing. The score answer, 3.331, is the **expected level**: 0 × 0.004 + 1 × 0.029 + 2 × 0.128 + 3 × 0.309 + 4 × 0.530. That falls between "today" and "immediately", while the single most probable level is 4. The noul answer, 0.859, is the probability of the second option, `true`. <!-- L23 --> The two confidence fields and the constant `act_probability` of 1.0 each get their own section below.

Every number in this section came from one call to the library's `predict()`, with hooks recording what each module produced during that same call.

## Intuition

A **bidirectional encoder** lets every position look at every other position, before and after it, and rewrite its own vector from what it sees. Laya's backbone does this 28 times. By the end, the vector at a `[MASK]` no longer means "blank". It is a summary of the slot's neighbourhood: the option text right after it, the question before it, and the whole ticket.

That is what BERT's pre-training rewards. BERT hides 15% of the tokens in each training sequence, replacing most of them with `[MASK]`, and learns to predict what was there. <!-- L32 --> The encoder learns to gather evidence at a `[MASK]` about what belongs in the slot. Laya keeps that token but not BERT's vocabulary-prediction head. Its own scorer asks each `[MASK]` one question: *how well does the option after you fit this ticket, for this question?*

Why not use `[CLS]`, the usual classification token? A sequence has one `[CLS]`, so it yields one vector. One vector is enough for a classifier with a fixed set of labels. A decision needs one vector per option, and one `[MASK]` in front of each option gives exactly that.

Think of a judge scoring a shortlist, with each candidate standing at a numbered podium. The judge listens to each candidate in the context of the whole case and writes down a score, and the scores are then turned into shares of one vote. The picture breaks in two places. First, the candidates hear each other. Laya adds no attention rule that keeps options apart <!-- L22 -->, so each option's slot is shaped partly by its neighbours, and order and neighbours can move the scores. Second, the vote is only among the candidates present. Billing's 0.847 says billing beat the three alternatives you listed. It does not say billing is correct. Remove "billing" from the options and its share goes to whichever of the rest scores best.

## What a decision model is

A **decision model** is a function from a state and a set of typed questions to one probability distribution per question, over options that the question itself declares. For a question $q$ with options $o_1, \dots, o_k$, the model returns $p_1, \dots, p_k$ with $p_i \ge 0$ and $\sum_i p_i = 1$. The options arrive with the request. The model has no label set of its own.

The three question types fix how that distribution is read. The contract is TypeSafe's, and Laya copies its field names: <!-- L15 -->

| Type | Asks | Options | Returns |
|---|---|---|---|
| choice | which one? | named options, each with an optional description | the most probable option, every probability, a confidence |
| score | how much, on an ordered scale? | ordered levels 0 to k − 1 | the expected level, every probability, a confidence |
| noul | is this true? | `false`, `true` | the probability of `true` |

**System One** is TypeSafe's name for the category. It comes from Daniel Kahneman's "System 1", the fast and intuitive mode of thought, as opposed to the slower, deliberate "System 2". <!-- L14 --> The name is a metaphor for speed and scope. What the analogy does and does not claim is Jev's part of this series.

Laya is **Jev-compatible** in a narrow sense. Its server, `laya-serve`, accepts the request TypeSafe's `POST /v1/systemone` endpoint accepts and returns the same response shape. A TypeSafe client can switch by changing its base URL. <!-- L13 --> <!-- L16 --> Same shape does not mean same model. Laya is Convai's model, and its weights are open. Jev is TypeSafe's, and its architecture is not public.

Figure 4 sets the three ways of getting the ticket's answers side by side.

![Three columns comparing a classifier, an LLM in JSON mode and Laya by who declares options, passes, output tokens and probabilities](FIG_04)
*Figure 4. The same three answers, three ways. The classifier needs a trained head per question. The LLM writes 19 tokens one decoder step at a time and offers only next-token probabilities. Laya scores declared options in one batch and writes nothing. Laya's numbers are our run; the 19-token count uses Laya's tokenizer, and an LLM's own tokenizer would differ.*

| | Fine-tuned classifier | LLM in JSON mode | Decision model (Laya) |
|---|---|---|---|
| Who declares the options | training data, fixed in the weights | the request | the request |
| Output | a distribution over trained labels | tokens, masked to a schema | one distribution per question over declared options |
| Work for our three answers | one encoder pass per trained head | prompt read, then about 19 decode steps | one batch of 3 rows |
| What the probability means | the probability of a label | the probability of the next token given the text so far | the probability of each declared option, within its question |
| New option | retrain | free | free |

What the format guarantees is narrow and real. A decision model's answer is always one of the options you declared, because it takes the largest of the scores it computed for exactly those options. There is no text to parse and no invented label to catch. TypeSafe describes this as its model being unable to hallucinate, and ties it to type safety. <!-- L17 --> Its own documentation adds that calibration is measured across groups of predictions and does not make any single answer correct. <!-- L18 --> A decision model can return a well-formed "sales" for a billing ticket. The guarantee covers the shape of the answer, not its truth.

## How does Laya lay out a question?

Laya's sequence layout is a short rule, and it decides both what the model can see and what each request costs. From laya 0.3.20's `build_sequence`: <!-- L19 --> <!-- L21 -->

1. **Order.** `[CLS]`, then `<type> question: <instructions>`, then `[SEP]`, then `[MASK]` plus the option text for each option in turn, then `[SEP]`, the state, and a final `[SEP]`.
2. **Budgets.** The English checkpoint's sequences are at most 512 tokens. The question and its options share a budget of 192 of them, and the state gets whatever is left: 512 minus everything before it, minus the final `[SEP]`. The other two checkpoints use 1,024 and 256. <!-- L05 -->
3. **Long options.** Each option's text is capped at 48 tokens. If the options together overflow the budget, every option is cut to the same length, `max(4, (budget − 16) // k)` tokens, counting its `[MASK]`. The question keeps at least 8 tokens.
4. **A long state** is cut from the end. A state given as a list of conversation turns is cut from the start instead, so the newest turn survives. <!-- L20 -->
5. **Rows.** One sequence per question, each with the full state. <!-- L20 -->

The fifth rule is the one to remember. TypeSafe's docs say that the questions in one request are evaluated independently, in parallel, against the same state. <!-- L49 --> Laya implements this literally: each question gets a private copy of the state, so no question can see another. The price is that the number of tokens the encoder reads grows with (number of questions) × (state length). What that costs in milliseconds is the next part's subject.

The third rule has a consequence that is easy to miss. Figure 5 runs Laya's own `build_sequence` on the route question with 1 to 140 options, each about the length of our route options.

![Line charts of tokens per option, question tokens and state room against option count for the 512 and 1,024 token budgets](FIG_05)
*Figure 5. How options eat the sequence. On the English budget (512 / 192), options start shrinking at 13 and fall to 4 tokens each (the `[MASK]` plus three tokens of text) at 36; every option after that takes four more tokens from the state. At 125 options the state gets 0 tokens and Laya still answers. At 127 it raises an error. Computed by laya 0.3.20's own `build_sequence`.*

With four options of this length, a long ticket would get 441 tokens of room. At 77 options, the size of the Banking77 intent set, each label keeps three tokens of text and the state has room for 192 tokens. Convai's card blames this budget, at its 256-token setting, for Laya's 0.425 on Banking77. The comparison it gives is 0.870 that a third party published for Jev, on 72 of the labels. <!-- L11 --> At 125 options the question's options fill the whole sequence and the state gets nothing. The library does not warn you, because its check only counts markers.

## Option-marker scoring

Option-marker scoring is the step that turns hidden states into answers, and it is simple enough to write out in full. For each question row:

1. **Gather.** Take the hidden state at each `[MASK]` position: route's positions 13, 23, 34 and 43 give four vectors of 1,024 numbers.
2. **Score.** Pass each vector through the scorer: a LayerNorm, a 1,024 × 1,024 linear layer, a GELU, and a linear layer down to one number. <!-- L22 --> **LayerNorm** rescales a vector to zero mean and unit variance before a learned scale and shift. **GELU** is a smooth activation function that lets positive values through and damps negative ones.
3. **Mask.** Set the logit of every unused slot to −10,000, so it gets zero probability. <!-- L22 --> Route's fifth slot and refund's last three slots are unused.
4. **Divide by the temperature** for the question's type and option count. Laya clamps any shipped temperature to between 0.5 and 5. <!-- L23 -->
5. **Softmax within the question.**

Figure 6 shows the numbers passing through the last four steps for all three rows.

![Three small grids per question showing logits, masked slots, logits divided by temperature and the resulting probabilities](FIG_06)
*Figure 6. Option-marker scoring on the ticket. Each row is scored separately: a masked slot becomes −10,000 and then exactly 0, the temperature pulls the logits together, and each row's probabilities sum to 1. Our run.*

The per-question softmax matters. Route's four options compete with one another, and refund's two compete with one another, but billing never competes with `true`. The request returns three independent distributions, not one distribution over eleven slots.

Each type then reads its distribution differently. A choice returns the most probable option. A score returns the expected level, which is a number and not necessarily a level: 3.331 here. If your code needs a level, decide whether it means the rounded expectation (3) or the most probable level (4), because the two can disagree, as they do here. A noul returns the probability of `true`.

Laya also returns two confidence numbers, and they measure different things. <!-- L23 -->

- `confidence` is, for choice and score, one minus the distribution's **entropy** divided by $\ln k$. Entropy is a measure of spread: it is 0 when one option has all the probability and $\ln k$ when all $k$ options are equal. So this field says how concentrated the whole distribution is. For a noul it is simply the larger of the two probabilities.
- `answer_confidence` is the probability of the returned answer, the largest $p_i$, for every type.

For route, `confidence` is 0.577 while `answer_confidence` is 0.847. For urgency they are 0.324 and 0.530. The entropy-based field depends on how the leftover probability is spread, not only on the top option, so Figure 7 draws it as a band against the top probability.

![Bands of entropy-based confidence against top probability for 4 and 5 options beside the identity line, with our three answers marked](FIG_07)
*Figure 7. Two fields named confidence. With four options, a top probability of 0.847 gives an entropy-based confidence of only 0.577, because the other three options still hold 15% between them. Each band's lower edge spreads the leftover probability evenly; its upper edge gives it all to one rival. Exact computation; our three answers are marked from our run.*

Which one to threshold on is a decision with consequences, and a later part chooses it from data. Here the point is only that they differ, and that `confidence` in Laya's JSON is a statement about spread, not the probability of being right.

## What is inside Laya?

Figure 8 is the whole model on one page. It has a shape on every edge and a parameter count on every module.

![Laya end to end: token ids, ModernBERT-large, type embedding, two head layers, marker gather, scorer, softmax, and an act head off CLS](FIG_08)
*Figure 8. Laya end to end, for our three-question request. The main path runs down the middle; the act/escalate head branches off the `[CLS]` position. Parameter counts are from the loaded checkpoint (our run); the architecture is from the model card and laya 0.3.20's source.*

### The backbone: ModernBERT-large

The backbone is a Transformer encoder, a stack of blocks that each apply multi-head self-attention and then a feed-forward network, each wrapped in a residual connection and a normalization. <!-- L52 --> ModernBERT-large has 28 such blocks, 1,024 dimensions, 16 attention heads and a 50,368-token vocabulary. It was trained on 2 trillion tokens and handles 8,192 tokens natively. <!-- L25 --> Laya fine-tunes all of it. <!-- L03 -->

ModernBERT changes four things from BERT. Laya only uses them, and later parts of this series derive them:

- **Rotary position embedding (RoPE)** encodes a token's position by rotating pairs of numbers in its query and key vectors, so attention scores depend on how far apart two tokens are. <!-- L27 --> ModernBERT uses rotation base θ = 160,000 in its global layers and 10,000 in its local ones. <!-- L25 -->
- **GeGLU** is a feed-forward layer with a gate: one projection is passed through GELU and multiplies a second one. <!-- L28 --> Here the input 1,024 is projected to 2 × 2,624, gated down to 2,624, and projected back to 1,024.
- **Alternating attention.** Every third layer (layers 0, 3, 6 and so on up to 27, ten layers in all) attends globally. The other 18 attend only within a sliding local window. <!-- L25 --> <!-- L29 -->
- **Unpadding.** On a GPU with FlashAttention, a fused attention kernel that accepts sequences of different lengths, ModernBERT removes the padding tokens before the first layer and runs the batch as one long jagged sequence. <!-- L26 -->

ModernBERT also normalizes before each sublayer rather than after, and drops the bias terms from its linear layers. <!-- L25 -->

The local window is concrete on our ticket. In the transformers library version we ran, a local layer lets position *i* attend to position *j* only when they are at most 64 apart. <!-- L30 --> Figure 9 draws both masks for the route row.

![Two 141 by 141 attention masks for the route row, a band of half-width 64 and a full block, with the billing marker's row highlighted](FIG_09)
*Figure 9. Local and global attention on the route row. In a local layer the billing marker at position 13 sees positions 0 to 77, which covers the question, all four options and only the first 26 of the ticket's 88 tokens. The rest of the ticket reaches it through the 10 global layers. Computed from the checkpoint's configuration and the library's mask rule.*

The same library runs our CPU batch padded, as the `[3, 141]` tensor with masks, rather than unpadded. <!-- L30 --> That is why every shape in this post includes the padding.

### The decision head

The decision head is new, trained from scratch, and has four parts. <!-- L03 --> <!-- L22 -->

- **A question-type embedding.** A 3 × 1,024 table with one row each for choice, score and noul. The row for the question's type is added to every position, so the rest of the head knows what kind of answer it is scoring.
- **Two Transformer layers.** These are PyTorch's standard `nn.TransformerEncoderLayer`: 16 heads, a 4,096-wide feed-forward network with ReLU, which zeroes negative values (our run), biases on, and normalization before each sublayer.
- **The option scorer.** The gather-and-score step described above.
- **The act/escalate head.** It reads the `[CLS]` vector plus four numbers summarising the option distribution: the top probability, the gap to the second, the normalised entropy, and the option count divided by 255. From these it outputs two logits, *act* or *escalate*.

### Why act_probability is always 1.0

The act/escalate head is meant to say when a decision is safe to automate. Convai's card says it carries no usable signal yet: it reads 1.0 for almost every input, and its raw logits score an AUROC of 0.30 on 396 labelled decisions, against 0.77 for `confidence`. <!-- L07 --> AUROC, the area under the receiver operating characteristic (ROC) curve, is the chance that a randomly chosen correct decision gets a higher score than a randomly chosen wrong one. 0.5 is a coin flip, so 0.30 is worse than no signal at all. The mechanism is visible in the architecture.

In a **pre-norm** layer, the normalization sits inside the residual branch. Each sublayer normalises its own input and adds its output back to the running sum, the **residual stream**, and that sum is never normalised. A pre-norm stack therefore needs one final normalization at the end. <!-- L53 --> ModernBERT has one. Laya's two head layers do not.

An issue on Laya's tracker measured the consequence: the head's output is about 300 times the encoder's scale. <!-- L08 --> The scorer starts with its own LayerNorm, so option probabilities are unaffected. The act head reads the `[CLS]` vector with no normalization at all, so it saturates. Figure 10 shows the same thing on our ticket.

![Log-scale bars of the CLS vector norm after the backbone and after the head for each question row, and the act and escalate logits](FIG_10)
*Figure 10. The `[CLS]` vector's length grows from about 36 after the backbone to about 10,000 after the two head layers. The act logits come out near +4,000 and −3,500, and their softmax is 1.0000 to four decimals on every row. Log scale. Our run.*

The card's advice follows directly: gate on `confidence`, not on `act_probability`. <!-- L07 -->

## Where do the 421 million parameters live?

Convai's card gives 395M for the backbone and 421M in total. <!-- L03 --> Counting the loaded checkpoint module by module reconciles both. Figure 11 draws the count to scale.

![Horizontal bar of Laya's parameters by component, GeGLU MLP largest, then attention, embeddings and the decision head, totalling 421,293,827](FIG_11)
*Figure 11. Where the parameters are. The feed-forward layers hold more than half, and the whole decision head is 6.3%. Counted from the loaded checkpoint (our run), against the card's 395M and 421M.*

| Component | Arithmetic | Parameters |
|---|---|---|
| Token embeddings + their norm | 50,368 × 1,024 + 1,024 | 51,577,856 |
| Attention, 28 layers | 28 × (1,024 × 3,072 + 1,024 × 1,024) | 117,440,512 |
| GeGLU feed-forward, 28 layers | 28 × (1,024 × 5,248 + 2,624 × 1,024) | 225,705,984 |
| Norms (27 attention, 28 feed-forward, 1 final) | 56 × 1,024 | 57,344 |
| **Backbone** | | **394,781,696** |
| Two head layers | 2 × 12,596,224 | 25,192,448 |
| Option scorer | 1,024² + 4 × 1,024 + 1 | 1,052,673 |
| Act/escalate head | 1,028 × 256 + 256 + 256 × 2 + 2 | 263,938 |
| Question-type embedding | 3 × 1,024 | 3,072 |
| **Decision head** | | **26,512,131** |
| **Total** | | **421,293,827** |

The backbone's 394,781,696 rounds to the card's and the paper's 395M. <!-- L25 --> ModernBERT's layer 0 has no attention norm of its own, and the embedding norm sits directly before it, so there are 27 attention norms rather than 28 (our run). BERT's vocabulary-prediction head is not in the checkpoint at all (our run). The `[MASK]` token survives, but the head that turned it back into a word does not. For scale, BERT-large has 340M parameters. <!-- L32 --> The file on disk stores the weights in 16-bit floating point (FP16): 842,609,210 bytes, which is 421 million numbers at 2 bytes each (our run).

### Three checkpoints, three models

"Laya" names three checkpoints, and they are not three sizes of one model. <!-- L06 -->

| | `laya` | `laya-multilingual` | `laya-typed-decisions` |
|---|---|---|---|
| Backbone | ModernBERT-large | mmBERT-base | ModernBERT-large |
| Layers × width | 28 × 1,024 | 22 × 768 | 28 × 1,024 |
| Vocabulary | 50,368 | 256,000 | 50,368 |
| Parameters (our count) | 421,293,827 | 321,908,995 | 421,293,827 |
| Sequence length | 512 | 1,024; 8,192 on request | 1,024 |
| Question + options budget | 192 | 256 | 256 |
| Temperatures shipped | fitted | none (all 1.0) | fitted |
| Trained for | English | 100+ languages | four business workflows |

mmBERT uses ModernBERT's architecture with a larger multilingual tokenizer. Its preprint reports training on 3 trillion tokens covering more than 1,800 languages, and a base model of 307M parameters. <!-- L31 --> The multilingual checkpoint reads 1,024 tokens by default and up to 8,192 when asked with `max_len=8192`. <!-- L50 --> Its configuration ships a temperature of 1.0 for every question type. <!-- L24 --> Laya's `Router` picks a checkpoint by script and language, and sends non-English text to the multilingual one. <!-- L51 --> The reason is on the card: the English checkpoint fails on non-Latin scripts while staying confident, scoring 0.000 accuracy at 0.952 confidence on Khmer. <!-- L12 -->

Figure 12 sends our ticket through all three.

![Small multiples of route, urgency and refund probabilities for the laya, laya-multilingual and laya-typed-decisions checkpoints](FIG_12)
*Figure 12. One ticket, three checkpoints. All three pick billing and say yes to the refund. They disagree on urgency and on how sure they are: the multilingual checkpoint returns billing at 1.0000 because its logit gap is 14.7 and it ships no temperature, while the typed-decisions checkpoint gives billing 0.458. Our run.*

## Where did option markers come from?

Laya's architecture has one source: its model card and its code. No paper describes it. Its repository ships inference code and a fine-tuning notebook, but not the code that trained it. <!-- L46 --> The idea underneath it has a longer history. Figure 13 lines up eight input formats, Laya's included, each written for our ticket.

![Timeline from BERT 2019 to Laya 2026 showing each method's input format for the route question, with marker tokens highlighted](FIG_13)
*Figure 13. From one fixed head to one marker per option. Each row writes the route question in that method's format. Laya's layout is UniMC's from 2022, with the question moved in front of the options and the state copied into one row per question. From the cited papers; the formats are paraphrased onto our ticket.*

- **BERT, 2019.** For multiple-choice questions, BERT built one sequence per candidate answer and softmaxed a learned score of each sequence's `[CLS]` vector. <!-- L33 --> Four options meant four sequences.
- **Yin, Hay and Roth, 2019.** Zero-shot classification, into labels never seen in training, framed as entailment: each label becomes a hypothesis tested against the text, one pass per label. <!-- L34 -->
- **PET, 2021.** Classification rewritten as a fill-in-the-blank question. BERT predicts the word at a `[MASK]`, and a fixed list, the *verbalizer*, maps words to labels. <!-- L35 --> It is one branch of a wider family of prompt-based methods. <!-- L40 -->
- **UniMC, 2022.** Every option goes into one sequence behind its own `[O-MASK]` token. The model predicts yes or no at each, and a softmax runs across the options. An attention rule stops the options from seeing each other. <!-- L36 -->
- **GLiNER, 2024.** Named-entity recognition with an `[ENT]` marker before each entity type. The types and the text are encoded together in one pass. <!-- L37 -->
- **GLiClass, 2025, a preprint.** A `«LABEL»` marker before each class, labels and text in one pass, and a reinforcement-learning variant for training. <!-- L38 -->
- **GLiGuard, May 2026, a preprint.** Task definitions and labels written into the input as token schemas, with many safety checks run in one pass of a 0.3B-parameter encoder. <!-- L39 -->

Laya's author took a different route first. The author's earlier SalesRLAgent, a March 2025 preprint, scored sales conversations from 3,072-dimensional embeddings produced by another model, and the author's write-up says that design could not take new questions at run time. <!-- L47 --> Laya puts the questions and options in the input.

So Laya inherits option markers. What is new is the rest:

- the typed contract, with three types including an ordinal score read as an expected level, behind an API that TypeSafe's clients already speak;
- one row per question, so that questions cannot see each other;
- a head trained from scratch on top of a fully fine-tuned encoder;
- training by reinforcement learning against proper scoring rules, rewards that only honest probabilities maximise, which Convai calls RLCD, together with shipped temperatures. <!-- L45 -->

The last item is the calibration story, and it has its own part.

## The math

The walk-through above, written as equations and then collapsed back onto the ticket.

| Symbol | Meaning |
|---|---|
| $s$ | the state's tokens, $\lvert s \rvert = 88$ here |
| $q$ | a question, with type $t_q \in$ {choice, score, noul} and options $o_{q,1}, \dots, o_{q,k_q}$ |
| $x_q$ | question $q$'s token sequence, of length $L_q$ |
| $m_{q,i}$ | the position of option $i$'s `[MASK]` in $x_q$ |
| $d$ | hidden width, 1,024 |
| $H_q$ | the head's output for $x_q$, an $L_q \times d$ matrix; $h_{q,j}$ is its row $j$ |
| $e_t$ | the question-type embedding for type $t$ |
| $z_{q,i}$ | option $i$'s logit |
| $T_q$ | the shipped temperature for $q$'s type and option count |
| $p_{q,i}$ | option $i$'s returned probability |

The sequence for question $q$ joins its parts end to end:

$$
x_q = \texttt{[CLS]} \,\Vert\, \text{text}(q) \,\Vert\, \texttt{[SEP]} \,\Vert\, \big(\texttt{[MASK]} \,\Vert\, o_{q,1}\big) \,\Vert\, \cdots \,\Vert\, \big(\texttt{[MASK]} \,\Vert\, o_{q,k_q}\big) \,\Vert\, \texttt{[SEP]} \,\Vert\, s \,\Vert\, \texttt{[SEP]} \tag{1}
$$

Every question gets its own sequence, and every sequence contains all of $s$.

The encoder and the head map the sequence to one vector per position:

$$
H_q = \mathrm{Head}\big(\mathrm{Enc}(x_q) + \mathbf{1}\, e_{t_q}^{\top}\big) \in \mathbb{R}^{L_q \times d} \tag{2}
$$

The type embedding is added to every row, which is what the column of ones $\mathbf{1}$ does.

Each option's logit is read from its marker's row:

$$
z_{q,i} = w_2^{\top}\, \mathrm{GELU}\big(W_1\, \mathrm{LN}(h_{q,\, m_{q,i}}) + b_1\big) + b_2 \tag{3}
$$

The same small network scores every option of every question; only the row it reads changes.

The probabilities are a temperature-scaled softmax within the question:

$$
p_{q,i} = \frac{\exp(z_{q,i} / T_q)}{\sum_{j=1}^{k_q} \exp(z_{q,j} / T_q)} \tag{4}
$$

Options compete only with options of the same question, and a larger $T_q$ spreads the probability more evenly.

The three readouts and the entropy-based confidence are:

$$
\text{choice} = \arg\max_i p_{q,i}, \qquad \text{score} = \sum_{i=0}^{k_q - 1} i \, p_{q,i}, \qquad \text{noul} = p_{q,\texttt{true}} \tag{5}
$$

A choice returns its most probable option, a score its expected level with levels numbered from 0, and a noul the probability of `true`, the second of its two options.

$$
\text{confidence}_q = 1 - \frac{-\sum_i p_{q,i} \ln p_{q,i}}{\ln k_q} \tag{6}
$$

This confidence is 1 when one option holds all the probability and 0 when all $k_q$ options are equal. It is the `confidence` field for choice and score questions.

**Back on the ticket.** Route has $k = 4$, logits $z = (4.196, -0.012, -1.069, -1.512)$ and $T = 1.760$. Equation (4) gives $e^{2.384} / (e^{2.384} + e^{-0.007} + e^{-0.607} + e^{-0.859}) = 1 / 1.181 = 0.847$. Its entropy is $0.586$ nats (entropy measured with the natural logarithm), and $\ln 4 = 1.386$, so equation (6) gives $1 - 0.586 / 1.386 = 0.577$. Urgency's expected level from equation (5) is 3.331.

**Tokens read.** Row $q$ has length $L_q = P_q + \lvert s \rvert + 1$, where $P_q$ is everything before the state. The encoder reads

$$
N = \sum_q L_q = \sum_q P_q + n\,(\lvert s \rvert + 1) \tag{7}
$$

tokens for $n$ questions, as long as each row fits its budget. Here $P = 52, 47, 33$, so $N = 132 + 3 \times 89 = 399$. The state term grows with the number of questions, which is the cost of keeping questions independent.

<details>
<summary>Deriving the parameter counts</summary>

With vocabulary $V$, width $d$, $L$ backbone layers and GeGLU width $f$:

- **Embeddings:** $Vd + d$. The $+d$ is the embedding norm, which has a scale and no bias.
- **Attention per layer:** one fused query-key-value projection, $d \times 3d$, and one output projection, $d \times d$, with no biases: $4d^2$.
- **GeGLU per layer:** an input projection to $2f$ (value and gate), $d \times 2f$, and an output projection $f \times d$: $3df$.
- **Norms:** $(2L - 1) + 1$ vectors of $d$. Layer 0 skips its attention norm, and one final norm follows the last layer.

At $V = 50{,}368$, $d = 1{,}024$, $L = 28$, $f = 2{,}624$ this gives $51{,}577{,}856 + 28 \times 4{,}194{,}304 + 28 \times 8{,}060{,}928 + 57{,}344 = 394{,}781{,}696$.

One PyTorch `nn.TransformerEncoderLayer` with biases and a $4d$ feed-forward has $4d^2 + 4d$ in attention, $8d^2 + 5d$ in the feed-forward and $4d$ in two norms: $12d^2 + 13d = 12{,}596{,}224$ at $d = 1{,}024$. The scorer is $2d + (d^2 + d) + (d + 1) = d^2 + 4d + 1 = 1{,}052{,}673$. The act head is $(d + 4) \cdot 256 + 256 + 256 \cdot 2 + 2 = 263{,}938$, and the type embedding is $3d = 3{,}072$.

</details>

## Implementation

The public call is three lines:

```python
import laya

agent = laya.load("convaiinnovations/laya", device="cpu")
result = agent.predict(state, questions)   # state, questions: the request above
```

To see the logits, run the pieces `predict()` runs yourself. The underscore methods below are laya 0.3.20 internals, so pin that version:

```python
import numpy as np
import torch
from laya.common import QTYPES, collate_items, temp_bucket

ids = list(questions)
internal = {q: agent._to_internal(questions[q]) for q in ids}
items = agent._encode_state(state, ids, internal)           # one row per question
batch = collate_items([items], agent.tok.pad_token_id)      # [3, 141] for the ticket

with torch.no_grad():
    logits, _ = agent.model(batch["input_ids"], batch["attention_mask"],
                            batch["marker_pos"], batch["marker_mask"], batch["qtype"])

for r, q in enumerate(ids):
    k = len(items[r]["markers"])
    qt = QTYPES[internal[q]["t"]]
    T = agent.temperature_by_options.get(temp_bucket(qt, k), agent.temperature[qt])
    z = logits[r, :k].numpy() / T
    p = np.exp(z - z.max()); p /= p.sum()
    print(q, np.round(logits[r, :k].numpy(), 4), round(T, 4), np.round(p, 4))
```

On the ticket it prints the logits from the worked example and the probabilities from the returned JSON:

```text
route [ 4.1957 -0.0121 -1.0685 -1.5121] 1.7602 [0.8468 0.0776 0.0426 0.0331]
urgency [-2.715  -0.3012  1.5369  2.6428  3.3203] 1.2514 [0.0043 0.0294 0.1275 0.3086 0.5303]
refund [-2.3921  1.1858] 1.9834 [0.1414 0.8586]
```

The lab in [Lab downloads](#lab-downloads) does the same thing through the public `predict()`. It records every intermediate shape with forward hooks, checks that the batch it built is the batch `predict()` ran, counts the parameters, sweeps the option budget, and repeats the trace on the other two checkpoints. It needs about 1 GB of Python packages and downloads 0.8 to 2.3 GB of weights, depending on how many checkpoints you trace. It runs on a CPU.

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** reading "one forward pass" as "the state is read once". Laya gives each question its own row holding the whole state, so the tokens the encoder reads grow with questions × state length. Our three questions over an 88-token ticket read 399 tokens, 264 of them the ticket three times. Budget and cost with the number of questions in mind, not just the state's length.

- **The base checkpoints are close to chance on typed business decisions.** On Convai's typed-decisions benchmark, the English checkpoint scores 0.362 accuracy, below the 0.461 you would get by always answering each question's most common label. The checkpoint fine-tuned on that benchmark scores 0.766. <!-- L10 --> Treat Laya as a fast base to fine-tune, not a ready-made judge.
- **`act_probability` is always 1.0.** The previous section showed why. Do not gate on it. <!-- L07 -->
- **An option's name can outvote its meaning.** A noul renders its options as `false:` and `true:`, and on the English checkpoint that pair of words can decide the answer regardless of the state. <!-- L09 --> A preprint found that renaming two options from 0/1 to no/yes, with the rubric text unchanged, changed 70.4 answers per hundred across Jev and two open Jev-like models. <!-- L44 --> Our refund question came out right. Test your own label words before trusting them. How this can be exploited, and defended, is a later part's subject.
- **Many options starve the labels, then the state.** Past about 36 options on the English checkpoint, every label keeps three tokens of text. At 125 options the state gets none, and the library does not warn you (Figure 5). Split very large option sets into a coarse choice followed by a fine one.
- **The three checkpoints are three models.** They differ in backbone, vocabulary, context and shipped temperatures, and they disagreed about our ticket's urgency. The multilingual checkpoint ships no fitted temperature, so its raw logit gap of 14.7 comes through as billing at 1.0000. <!-- L24 --> The English checkpoint is confidently wrong on non-Latin scripts. <!-- L12 -->
- **The probabilities depend on fitted temperatures.** Convai says the checkpoints ship over-confident and should have their temperatures refitted on your own data. <!-- L54 --> What that fitting does, and how to check the result, is the calibration part.
- **"Can't hallucinate" is a format guarantee.** The answer is always one of your options. Whether it is the right one is an empirical question, answered over many decisions, not one. <!-- L18 -->

## Key takeaways

- A decision model maps a state and typed questions to one probability distribution per question, over options declared in the request. The answer is always one of those options, which is a guarantee about format, not correctness.
- Laya scores each option at its own `[MASK]`. Thirty encoder and head layers turn that slot into a 1,024-number summary, a small network turns it into a logit, and a temperature-scaled softmax within the question turns logits into the returned probabilities: billing's 4.196 becomes 0.847.
- "One forward pass" is one batch with one row per question, and every row carries the whole state. Three questions over our 88-token ticket cost 399 input tokens.
- Laya's 421,293,827 parameters are a 394,781,696-parameter ModernBERT-large encoder, without BERT's vocabulary head, plus a 26,512,131-parameter decision head. The multilingual checkpoint is a different 321,908,995-parameter model.
- Option markers are inherited: UniMC in 2022, then GLiNER, GLiClass and GLiGuard. Laya's new part is the typed contract, one row per question and its training objective.

## Try it yourself

1. Softmax route's logits (4.196, −0.012, −1.069, −1.512) at $T = 1$. What did the shipped temperature of 1.760 do to billing's probability?

<details><summary>Answer</summary>

At $T = 1$ the probabilities are 0.977, 0.015, 0.005 and 0.003. Dividing by 1.760 pulls the logits together and lowers billing to 0.847. The other three options gain what billing loses.

</details>

2. Keep the three questions but make the ticket 400 tokens long. How many input tokens does the request use? What happens at 480 tokens?

<details><summary>Answer</summary>

Each row is its prefix, plus the state, plus one `[SEP]`: 52 + 401, 47 + 401 and 33 + 401, which is 453 + 448 + 434 = **1,335** tokens. At 480 tokens, no row fits 512. Each state is cut to its row's room: 459 tokens for route, 464 for urgency and 478 for refund. That is 1,536 tokens in all, and each question sees a slightly different amount of the ticket.

</details>

3. Count the parameters of one decision-head layer on the multilingual checkpoint, where $d = 768$. Then check the whole multilingual head against 14,969,347.

<details><summary>Answer</summary>

One layer is $12d^2 + 13d = 7{,}077{,}888 + 9{,}984 = 7{,}087{,}872$, so two layers are 14,175,744. Add the type embedding ($3d = 2{,}304$), the scorer ($d^2 + 4d + 1 = 592{,}897$) and the act head ($772 \times 256 + 256 + 514 = 198{,}402$). The total is 14,969,347.

</details>

## References

### Lab downloads

- [`README.md`](LAB_01) — the environment, run order, expected output, download sizes and cleanup.
- [`requirements.txt`](LAB_02) — pinned packages: laya 0.3.20, CPU PyTorch 2.14.0, transformers 5.17.0.
- [`trace_laya.py`](LAB_03) — traces the ticket through Laya with forward hooks, checks every returned probability against the captured logits, counts parameters, sweeps the option budget and, with `--all`, traces the other two checkpoints.
- [`trace.json`](LAB_04) — the captured output of `trace_laya.py --all`: tokens, segments, marker positions, shapes, logits, probabilities, parameter counts and the budget sweep.

### Sources

1. Convai Innovations. *Laya* model card and checkpoint files, commit 55cf4c4e. Hugging Face, 2026. <https://huggingface.co/convaiinnovations/laya> (accessed 2026-09-26)
2. Convai Innovations. *laya-multilingual* model card. Hugging Face, 2026. <https://huggingface.co/convaiinnovations/laya-multilingual> (accessed 2026-09-26)
3. Convai Innovations. *laya-typed-decisions* model card. Hugging Face, 2026. <https://huggingface.co/convaiinnovations/laya-typed-decisions> (accessed 2026-09-26)
4. `laya` 0.3.20, Python package source (`laya/common.py`, `laya/agent.py`). PyPI, 2026. <https://pypi.org/project/laya/0.3.20/> (accessed 2026-09-26)
5. NandhaKishorM/laya repository, commit 4066d5d. GitHub, 2026. <https://github.com/NandhaKishorM/laya/tree/4066d5d5fbf08b66c6757ddeedbd797bd7655bc0> (accessed 2026-09-26)
6. Laya issue #185, "The decision head's output is unnormalized". GitHub, 2026. <https://github.com/NandhaKishorM/laya/issues/185> (accessed 2026-09-26)
7. Laya issue #156, "`noul` returns the negative label regardless of state". GitHub, 2026. <https://github.com/NandhaKishorM/laya/issues/156> (accessed 2026-09-26)
8. Nandakishor M. "I built non-autoregressive decision models a year ago…". DEV Community, 18 September 2026. <https://dev.to/nandakishor_m_6cc0adfde9f/i-built-non-autoregressive-decision-models-a-year-ago-then-a-frontier-lab-called-it-a-18me> (accessed 2026-09-26)
9. Nandakishor M. "SalesRLAgent: A Reinforcement Learning Approach for Real-Time Sales Conversion Prediction and Optimization." Preprint, 2025. [arXiv:2503.23303](https://arxiv.org/abs/2503.23303)
10. TypeSafe AI. "Introducing System One Models & Jev." 15 September 2026. <https://typesafe.ai/blog/introducing-system-one-models-and-jev> (accessed 2026-09-26)
11. TypeSafe AI. Documentation: System One, Primitives (Choice, Score, Noul), Quick start. <https://docs.typesafe.ai/concepts/system-one> (accessed 2026-09-26)
12. Devlin, J., Chang, M.-W., Lee, K., and Toutanova, K. "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding." *NAACL-HLT*, 2019. [doi:10.18653/v1/N19-1423](https://doi.org/10.18653/v1/N19-1423)
13. Vaswani, A., et al. "Attention Is All You Need." *NeurIPS*, 2017. [arXiv:1706.03762](https://arxiv.org/abs/1706.03762)
14. Warner, B., et al. "Smarter, Better, Faster, Longer: A Modern Bidirectional Encoder for Fast, Memory Efficient, and Long Context Finetuning and Inference." *ACL*, 2025. [doi:10.18653/v1/2025.acl-long.127](https://doi.org/10.18653/v1/2025.acl-long.127)
15. Marone, M., et al. "mmBERT: A Modern Multilingual Encoder with Annealed Language Learning." Preprint, 2025. [arXiv:2509.06888](https://arxiv.org/abs/2509.06888)
16. Su, J., et al. "RoFormer: Enhanced Transformer with Rotary Position Embedding." *Neurocomputing* 568, 2024. [doi:10.1016/j.neucom.2023.127063](https://doi.org/10.1016/j.neucom.2023.127063)
17. Shazeer, N. "GLU Variants Improve Transformer." Preprint, 2020. [arXiv:2002.05202](https://arxiv.org/abs/2002.05202)
18. Beltagy, I., Peters, M. E., and Cohan, A. "Longformer: The Long-Document Transformer." Preprint, 2020. [arXiv:2004.05150](https://arxiv.org/abs/2004.05150)
19. Xiong, R., et al. "On Layer Normalization in the Transformer Architecture." *ICML*, PMLR 119, 2020. [arXiv:2002.04745](https://arxiv.org/abs/2002.04745)
20. Yin, W., Hay, J., and Roth, D. "Benchmarking Zero-shot Text Classification: Datasets, Evaluation and Entailment Approach." *EMNLP-IJCNLP*, 2019. [doi:10.18653/v1/D19-1404](https://doi.org/10.18653/v1/D19-1404)
21. Schick, T., and Schütze, H. "Exploiting Cloze-Questions for Few-Shot Text Classification and Natural Language Inference." *EACL*, 2021. [doi:10.18653/v1/2021.eacl-main.20](https://doi.org/10.18653/v1/2021.eacl-main.20)
22. Yang, P., et al. "Zero-Shot Learners for Natural Language Understanding via a Unified Multiple Choice Perspective." *EMNLP*, 2022. [doi:10.18653/v1/2022.emnlp-main.474](https://doi.org/10.18653/v1/2022.emnlp-main.474)
23. Zaratiana, U., Tomeh, N., Holat, P., and Charnois, T. "GLiNER: Generalist Model for Named Entity Recognition using Bidirectional Transformer." *NAACL*, 2024. [doi:10.18653/v1/2024.naacl-long.300](https://doi.org/10.18653/v1/2024.naacl-long.300)
24. Stepanov, I., et al. "GLiClass: Generalist Lightweight Model for Sequence Classification Tasks." Preprint, 2025. [arXiv:2508.07662](https://arxiv.org/abs/2508.07662)
25. Zaratiana, U., et al. "GLiGuard: Schema-Conditioned Classification for LLM Safeguard." Preprint, 2026. [arXiv:2605.07982](https://arxiv.org/abs/2605.07982)
26. Liu, P., et al. "Pre-train, Prompt, and Predict: A Systematic Survey of Prompting Methods in Natural Language Processing." *ACM Computing Surveys* 55(9), 2023. [doi:10.1145/3560815](https://doi.org/10.1145/3560815)
27. Tam, Z. R., et al. "Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of Large Language Models." *EMNLP Industry Track*, 2024. [doi:10.18653/v1/2024.emnlp-industry.91](https://doi.org/10.18653/v1/2024.emnlp-industry.91)
28. Willard, B. T., and Louf, R. "Efficient Guided Generation for Large Language Models." Preprint, 2023. [arXiv:2307.09702](https://arxiv.org/abs/2307.09702)
29. Geng, S., Josifoski, M., Peyrard, M., and West, R. "Grammar-Constrained Decoding for Structured NLP Tasks without Finetuning." *EMNLP*, 2023. [doi:10.18653/v1/2023.emnlp-main.674](https://doi.org/10.18653/v1/2023.emnlp-main.674)
30. OpenAI. "GPT-4 Technical Report." Preprint, 2023. [arXiv:2303.08774](https://arxiv.org/abs/2303.08774)
31. Sun, Y., Xu, J.-H., Shi, J.-J., and Yang, Z.-J. "Type-Safe Is Not Error-Free: A Constrained Decision Head Follows the Option Name, Not the Rubric Bound to It." Preprint, 2026. [arXiv:2609.26758](https://arxiv.org/abs/2609.26758)
32. Hugging Face. `transformers` 5.17.0, ModernBERT implementation and attention-mask utilities. PyPI, 2026. <https://pypi.org/project/transformers/5.17.0/> (accessed 2026-09-26)
