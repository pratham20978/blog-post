# The Non-Embedding Search & Retrieval Catalog

## A Book-Like Reference for Lexical, Statistical, Set-Based, String, Graph, and Learning-to-Rank Retrieval — with a Comparative Embedding Half

**TL;DR**

- For a PostgreSQL-only, no-embeddings, no-Redis blog platform, the operationally important stack is: tsvector/GIN full-text + pg_trgm fuzzy + integer/array tag-set filtering + RRF/weighted fusion for multi-signal ranking + a derived sparse tag-affinity profile updated with time decay + Personalized PageRank / random-walk personalization computed incrementally in SQL. Every one of these is implementable in raw SQL with no external infrastructure.
- The single biggest honest caveat: Postgres native `ts_rank`/`ts_rank_cd` is NOT BM25 — it has no IDF (inverse document frequency), so rare, discriminating terms are not up-weighted. If ranking quality becomes a limiter, the cheapest upgrade path that stays inside Postgres is the ParadeDB `pg_search` (Tantivy/BM25) or VectorChord-BM25 extension.
- Embeddings buy semantic recall on paraphrase/vocabulary-mismatch queries — neural methods outperform BM25 on in-domain MS MARCO by 7–18 points (Thakur et al., "BEIR," NeurIPS 2021) — but at the cost of index build time, memory, model drift, re-embedding on edits, and weak explainability. BM25's zero-shot BEIR average is nDCG@10 ≈ 43.42 and the BEIR paper's headline finding is that "BM25 is a robust baseline," so NOT using embeddings is defensible for a tag-organized, keyword-friendly corpus.

---

## TABLE OF CONTENTS

- Part I. Foundations / IR Theory
- Part II. Index Data Structures & Algorithms
- Part III. String Matching / Fuzzy / Approximate
- Part IV. PostgreSQL-Native Search (deep)
- Part V. Tag / Taxonomy / Faceted Search
- Part VI. Query Understanding & Expansion
- Part VII. Ranking, Re-ranking & Learning to Rank
- Part VIII. Personalization & Recommendation Without Embeddings
- Part IX. Embedding-Based Search (comparative)
- Part X. Implementations / Systems Catalog
- Part XI. Experiments, Benchmarks & Empirical Results
- Part XII. Practical Engineering Concerns
- Comparison Tables & Recommendations

Legend: ✅ PG-NATIVE = works under strict "PostgreSQL only, raw SQL, no embeddings, no Redis, no external engine"; ⚙️ PG-EXT = needs a Postgres extension; 🚀 INFRA = needs infrastructure beyond Postgres.

---

# PART I — FOUNDATIONS / IR THEORY

**The retrieval problem.** Given a query q and a corpus D, produce a ranking by estimated relevance. Documents/queries are bags of terms after tokenization/normalization. The central difficulty is **vocabulary mismatch**: user words differ from document words (synonymy, morphology, paraphrase). Lexical methods attack this with normalization, stemming, expansion, fuzzy matching; embeddings with learned semantic similarity.

**Zipf's law** (freq ∝ 1/rank) and **Heaps' law** (V ≈ k·N^β, β≈0.4–0.6) explain why inverted indexes are efficient. **IDF works** because term informativeness is roughly log-inverse to document frequency.

### Boolean model ✅

AND/OR/NOT over posting lists. Exact, no ranking. tsquery is exactly this.

### Extended Boolean / p-norm

Softens Boolean with weights and a p-norm. Rarely used now.

### Vector Space Model (TF-IDF, cosine)

tf-idf: w(t,d) = tf(t,d)·log(N/df(t)); Cosine cos(q,d)=(q·d)/(‖q‖‖d‖). **Pivoted length normalization** (Singhal 1996): normalize by (1−s)+s·(dl/avgdl).

### Probabilistic Relevance Framework → BM25 (the workhorse)

From the Binary Independence Model and Robertson–Spärck Jones weight. **Okapi BM25** (Robertson & Zaragoza, "The Probabilistic Relevance Framework: BM25 and Beyond", 2009):

BM25(q,d) = Σ_{t∈q} IDF(t) · [ f(t,d)·(k1+1) ] / [ f(t,d) + k1·(1 − b + b·|d|/avgdl) ]

IDF(t) = log( (N − n(t) + 0.5) / (n(t) + 0.5) ) (Lucene adds +1 in the log to keep IDF non-negative).

- k1 = **term-frequency saturation** (default 1.2; range 1.2–2.0); b = **length normalization** (default 0.75; b∈[0,1]).
- Anserini/Pyserini use k1=0.9, b=0.4 for MS MARCO (Karpukhin et al. 2020). Xapian defaults k1=1, k2=0, k3=1, b=0.5.
- **Variants**: BM25L (Lv & Zhai 2011, adds δ; b∈0.3–0.6), BM25+ (lower-bound δ for long docs), BM25-adpt (per-term k1), BM25F (fielded — combine per-field weighted tf BEFORE saturation). Kamphuis et al., "Which BM25 Do You Mean?" (ECIR 2020): variants differ by <1 nDCG point; tuning k1/b matters far more.
- **Lucene's BM25** quantizes doc length to 1 byte (256 lengths) and precomputes k1·(1−b+b·dl/avgdl).

### Language-Modeling approaches ✅ (implementable in SQL for small corpora)

Rank by query likelihood P(q|d) under a smoothed model.

- **Jelinek–Mercer**: P(w|d)=(1−λ)·f(w,d)/|d| + λ·P(w|C). Good for long queries; sensitive to λ.
- **Dirichlet** (best general default): P(w|d)=(f(w,d)+μ·P(w|C))/(|d|+μ) = JM with λ=μ/(μ+|d|). μ≈2000–2500 stable (Zhai & Lafferty 2004).
- **Absolute discounting**: subtract fixed δ, redistribute to unseen.

### DFR, DPH, PL2

Non-parametric (Amati & van Rijsbergen); DPH parameter-free; in Terrier.

### Axiomatic IR

Term-frequency/length/IDF constraints a ranker must satisfy (BM25+ came from a lower-bound constraint).

### Evaluation theory

- **P@k, Recall@k, MAP, MRR** (mean 1/rank of first relevant), **nDCG@k** (DCG=Σ(2^rel−1)/log2(i+1), normalized — dominant metric, graded & rank-aware), **ERR** (cascade).
- **Cranfield/TREC**: corpus + topics + pooled judgments. **Pooling bias**: unjudged = non-relevant.
- **Significance**: paired t-test, Wilcoxon, permutation; p<0.05.
- **Online**: A/B, **interleaving** (team-draft). **Counterfactual/off-policy** from clicks: correct **position bias** via the **examination hypothesis** (click = examined × relevant). **Click models**: PBM, Cascade, DBN. **Inverse Propensity Scoring** reweights clicks by 1/propensity.

	

1. First understand the evaluation problem

Suppose a user searches:

query = "postgres vacuum"

Your search engine returns:

Rank 1 → Document A
Rank 2 → Document B
Rank 3 → Document C
Rank 4 → Document D
Rank 5 → Document E

But which documents are actually useful?

Suppose humans have judged:

A → relevant
B → not relevant
C → relevant
D → not relevant
E → relevant

Then:

Ranking:

1  A  ✓
2  B  ✗
3  C  ✓
4  D  ✗
5  E  ✓

Now we can measure different things.

And different metrics answer different questions.

2. The fundamental vocabulary

Before P@k, Recall@k, etc., understand these:

Query

What the user searches for.

"postgres vacuum"
Document

A searchable item.

PostgreSQL VACUUM documentation
Relevant document

A document judged useful for that query.

Ranking

The order in which the search engine returns documents.

1 → A
2 → B
3 → C
...
Relevance judgment

Usually:

0 = irrelevant
1 = relevant
2 = highly relevant
3 = extremely relevant

This distinction becomes important for nDCG.

3. Binary vs graded relevance

There are two major forms of relevance judgments.

Binary
0 = irrelevant
1 = relevant

Example:

A → 1
B → 0
C → 1
D → 0

Metrics such as:

Precision
Recall
MAP
MRR

are commonly explained using binary relevance.

Graded

Instead of:

relevant / irrelevant

we can say:

0 → irrelevant
1 → somewhat relevant
2 → relevant
3 → highly relevant

Example:

Rank     Document    Relevance
1        A           3
2        B           0
3        C           2
4        D           1
5        E           3

This is important for:

nDCG
ERR

because not all relevant documents are equally useful.

4. Precision@k

Let's start with the simplest.

Suppose your search engine returns:

k = 5

1 → ✓
2 → ✗
3 → ✓
4 → ✗
5 → ✓

There are:

3 relevant documents

among the top 5.

Therefore:

Precision@5=
5
relevant documents in top 5
	

=
5
3
	

=
0.6
	

or:

60%
	

5. What question does Precision@k answer?

It answers:

"Of the results I showed the user, how many were relevant?"

This is extremely important for search.

If the user only looks at the first 5 results, then:

P@5

is often more meaningful than overall precision.

6. Precision@1

Suppose:

1 → relevant

Then:

P@1=1

If:

1 → irrelevant

then:

P@1=0

This is useful for systems where users mostly care about the first result.

7. Recall@k

Precision asks:

How many retrieved results were relevant?

Recall asks:

How many of all relevant documents did we manage to retrieve?

Suppose there are actually:

10 relevant documents

in the entire corpus.

Your top 5 results contain:

3 relevant documents

Then:

Recall@5=
10
3
	

=
0.3
	

or:

30%
8. Precision vs Recall

This distinction is fundamental.

Suppose:

Corpus contains 100 relevant documents.

System A:

returns 5 documents
5 are relevant

Then:

P@5=1

Excellent precision.

But:

Recall@5=
100
5
	

=0.05

Very poor recall.

System B:

returns 5 documents
2 are relevant

Then:

P@5=0.4

and:

Recall@5=0.02

So precision and recall tell you different things.

9. Why Recall@k becomes tricky

Recall requires knowing:

all relevant documents

But in a huge corpus, how do we know every relevant document?

That's one of the major problems in information retrieval evaluation.

We'll come back to this when we discuss:

Cranfield / TREC / pooling

10. MAP — Mean Average Precision

This one is more interesting.

First understand:

Average Precision

Suppose:

Rank:

1 → ✓
2 → ✗
3 → ✓
4 → ✗
5 → ✓

Calculate precision every time we encounter a relevant document.

At rank 1:

P@1=1

At rank 3:

P@3=
3
2
	

At rank 5:

P@5=
5
3
	

Then:

AP=
3
P@1+P@3+P@5
	

So:

AP=
3
1+
3
2
	

5
3
	

	

AP≈0.756
11. Why is AP interesting?

Notice what happened.

If relevant results appear early:

✓
✓
✗
✗

you get high precision early.

If relevant results appear late:

✗
✗
✗
✓
✓

you get lower AP.

So AP rewards:

retrieving relevant documents early.

12. MAP

Now suppose you have multiple queries.

Query 1 → AP = 0.80
Query 2 → AP = 0.60
Query 3 → AP = 0.90
Query 4 → AP = 0.70

Then:

MAP=
4
0.8+0.6+0.9+0.7
	

=
0.75
	

So:

MAP=Mean(Average Precision)
	

MAP is simply:

Average AP across queries.

13. MRR — Mean Reciprocal Rank

MRR asks a much narrower question:

Where is the first relevant result?

Suppose:

1 → ✗
2 → ✗
3 → ✓

First relevant result is at rank 3.

Reciprocal rank:

RR=
3
1
	

Now suppose:

1 → ✓

Then:

RR=1

If:

1 → ✗
2 → ✓

then:

RR=
2
1
	

=0.5
14. MRR across queries

Suppose:

Query 1 → first relevant at rank 1
Query 2 → first relevant at rank 2
Query 3 → first relevant at rank 4

Then:

MRR=
3
1+
2
1
	

4
1
	

	

=
3
1.75
	

0.5833
	

15. When is MRR useful?

MRR is excellent when the user primarily needs one correct answer.

Examples:

"Who is the CEO of Nvidia?"

"What is the capital of France?"

"What is the syntax for PostgreSQL VACUUM?"

You care about:

How quickly did I find the first useful answer?

16. MRR has a major limitation

Suppose:

System A:

1 → ✓
2 → ✗
3 → ✗
4 → ✗
5 → ✗

MRR:

1

System B:

1 → ✓
2 → ✓
3 → ✓
4 → ✓
5 → ✓

MRR:

1

They get the same MRR.

But obviously System B is much better if the user wants many useful results.

That's why MRR is focused on:

first relevant result
	

17. nDCG@k

Now we reach one of the most important ranking metrics.

nDCG = normalized Discounted Cumulative Gain.

This metric handles:

relevance grade
ranking position

This is why it's so powerful.

18. Why do we need graded relevance?

Suppose:

Rank 1 → relevance 3
Rank 2 → relevance 1
Rank 3 → relevance 2

All three are technically relevant.

But:

relevance 3

is much better than:

relevance 1

Binary metrics lose this information.

nDCG doesn't.

19. DCG

Your formula:

DCG@k=
i=1
∑
k
	

log
2
	

(i+1)
2
rel
i
	

−1
	

Let's calculate it.

Suppose:

Rank     relevance
1        3
2        2
3        0
4        1

At rank 1:

log
2
	

(2)
2
3
−1
	

=
1
7
	

=7

Rank 2:

log
2
	

(3)
2
2
−1
	

=
1.585
3
	

≈1.893

Rank 3:

log
2
	

(4)
2
0
−1
	

=0

Rank 4:

log
2
	

(5)
2
1
−1
	

≈0.431

Therefore:

DCG≈7+1.893+0+0.431
DCG≈9.324
	

20. Why 2^rel - 1?

This makes relevance differences nonlinear.

For:

rel = 0
2
0
−1=0

For:

rel = 1
2
1
−1=1

For:

rel = 2
2
2
−1=3

For:

rel = 3
2
3
−1=7

So:

0 → 0
1 → 1
2 → 3
3 → 7

A highly relevant result gets dramatically more gain.

21. Why divide by log2(i+1)?

This is the discount.

Users generally pay less attention to lower-ranked results.

So:

Rank 1 → full value
Rank 2 → discounted
Rank 3 → more discounted
Rank 10 → heavily discounted

The formula:

log
2
	

(i+1)
1
	

implements that idea mathematically.

So DCG captures:

relevance×position importance
	

22. Why normalize?

Raw DCG isn't easy to compare between queries.

Suppose:

Query A
maximum possible relevance = high

Query B
maximum possible relevance = low

Their DCG scales differ.

So we calculate ideal DCG:

IDCG@k

This means:

What would DCG be if we sorted the documents in the perfect order?

Then:

nDCG@k=
IDCG@k
DCG@k
	

Therefore:

0≤nDCG≤1
	

Usually.

And:

nDCG=1
	

means the ranking is ideal for those judgments.

23. Why nDCG is often the dominant search-ranking metric

Because it simultaneously handles:

Relevance grade
       +
Ranking position
       +
Normalization

So for modern search systems:

P@k
Recall@k
MAP
MRR
nDCG

nDCG is often particularly useful when your judgments are graded.

24. ERR — Expected Reciprocal Rank

ERR takes a different approach.

Instead of simply saying:

"Rank 1 is worth X, rank 2 is worth Y."

it models a user browsing results.

The intuition is:

User sees result 1
       ↓
Is it satisfying?
       │
    ┌──┴──┐
    │     │
   YES    NO
    │     │
 stop    continue
          ↓
       result 2

This is called a cascade model.

25. ERR intuition

Suppose:

Rank 1 → highly relevant

The user may stop immediately.

Therefore, results below it matter less.

But if rank 1 is bad:

Rank 1 → bad

the user continues.

Then rank 2 matters.

Then rank 3.

So ERR models:

P(user reaches rank i)

and:

P(user is satisfied at rank i)
26. ERR formula

A common formulation is:

ERR=
i=1
∑
k
	

i
1
	

P(user reaches i)R
i
	

where R
i
	

 represents the probability that the user is satisfied with result i.

The reach probability is recursively determined by previous dissatisfaction.

Conceptually:

P(reach i)=
j=1
∏
i−1
	

(1−R
j
	

)

So:

ERR=
i=1
∑
k
	

i
1
	

[
j=1
∏
i−1
	

(1−R
j
	

)]R
i
	

That's the key mathematical idea.

27. Comparing the ranking metrics

Think of them like this:

Metric	Main question
Precision@k	How many top-k results are relevant?
Recall@k	How many relevant documents did we retrieve?
MAP	How well are relevant documents distributed throughout ranking?
MRR	How quickly do we find the first relevant result?
nDCG@k	How good is the graded ranking?
ERR	How likely is the user to find satisfaction while browsing?
28. Now: Cranfield evaluation

This is the foundation of offline information retrieval evaluation.

The basic setup:

Corpus
  +
Queries/topics
  +
Relevance judgments
  ↓
Evaluate search systems

Suppose we have:

1,000,000 documents

and:

100 search topics

For each topic, humans judge which documents are relevant.

Then we can run:

System A
System B
System C

against exactly the same evaluation set.

Now comparison is controlled.

29. Why is this called the Cranfield paradigm?

The Cranfield approach established the idea of evaluating retrieval systems using:

collection
+
queries
+
relevance judgments
+
retrieval system

This separates:

the retrieval algorithm

from:

the evaluation collection and judgments

That's extremely useful scientifically.

30. TREC

TREC = Text REtrieval Conference.

It applies this idea at large scale.

A TREC-style evaluation provides:

Corpus
Topics
Qrels
Corpus

Documents.

Topics

Queries/information needs.

Qrels

Relevance judgments.

For example:

query  document  relevance

101     D123      2
101     D456      0
101     D789      1

These are the ground truth used to evaluate systems.

31. The pooling problem

Here's a fascinating problem.

Suppose:

System A → top 100 documents
System B → top 100 documents
System C → top 100 documents

There are millions of documents.

Humans can't judge every document.

So researchers create a pool.

Take top results from multiple systems:

A top 100
B top 100
C top 100
D top 100

Combine them:

POOL
 ↓
unique documents
 ↓
human judges

Now we have relevance judgments.

32. Pooling bias

Here's the problem.

Suppose the true relevant documents are:

A
B
C
D
E
F

But none of the systems retrieve:

F

Then F may never enter the pool.

So:

F = unjudged

But many evaluation setups effectively treat unjudged documents as:

not relevant

That creates pooling bias.

This is why:

"Not judged"

doesn't necessarily mean:

"Not relevant."

33. Why this matters

Imagine:

System X

discovers completely new relevant documents.

But those documents aren't in the judgment pool.

The evaluation may incorrectly penalize X.

Therefore offline evaluation has limitations.

34. Statistical significance

Suppose:

System A nDCG = 0.421
System B nDCG = 0.427

Is B actually better?

Maybe.

Or maybe the difference happened because of random variation across queries.

We need statistical testing.

35. Paired t-test

Suppose for each query we calculate:

A_q
B_q

Then calculate:

d
q
	

=A
q
	

−B
q
	

For example:

Query 1 → +0.02
Query 2 → -0.01
Query 3 → +0.04
Query 4 → +0.01

The paired t-test asks whether the mean difference is significantly different from zero.

t=
s
d
	

/
n
	

d
ˉ
	

where:

d
ˉ
 = mean difference
s
d
	

 = standard deviation of differences
n = number of queries
36. Why paired?

Because both systems are evaluated on the same queries.

So we don't treat them as unrelated samples.

We compare:

Query 1:
A vs B

Query 2:
A vs B

Query 3:
A vs B

That's a paired comparison.

37. Wilcoxon signed-rank test

The paired t-test assumes certain distributional properties.

Wilcoxon signed-rank is a non-parametric alternative.

Instead of relying directly on the mean and normality assumptions, it looks at the ranks of the paired differences.

Useful when:

metric differences

are not well modeled by a normal distribution.

38. Permutation test

This is conceptually beautiful.

Suppose:

A beats B

We ask:

If A and B were actually equivalent, how often could we observe a difference this large just by randomly swapping their labels?

We repeatedly randomize:

A/B labels

and build a null distribution.

Then:

p=P(difference at least this extreme∣H
0
	

)

This is often very intuitive for IR evaluation.

39. What does p < 0.05 mean?

Usually:

p<0.05

means:

Under the null hypothesis, results at least this extreme would be relatively unlikely.

It does not mean:

There is a 95% probability that my new system is better.

That's a very common statistical mistake.

40. Offline vs online evaluation

Now we've covered:

OFFLINE
│
├── P@k
├── Recall@k
├── MAP
├── MRR
├── nDCG
├── ERR
├── TREC
├── qrels
└── significance tests

But there's another world:

ONLINE

where real users interact with the system.

41. A/B testing

Suppose you have:

A = current search engine
B = new search engine

Randomly assign users:

50% → A
50% → B

Then measure:

click rate
query success
conversion
time to success
reformulation rate
etc.

This is an online experiment.

42. Why A/B testing is powerful

Offline:

documents + judgments

Online:

real users
real queries
real behavior

So online testing captures things offline judgments may miss.

But it is expensive and can be noisy.

43. Interleaving

Instead of:

User A → system A
User B → system B

we can combine results from A and B into one ranking.

For example:

A result 1
B result 1
A result 2
B result 2
...

Then observe which system's results receive more interactions.

One popular approach is:

Team Draft Interleaving

44. Team Draft Interleaving

Imagine:

System A:
A1 A2 A3 A4

System B:
B1 B2 B3 B4

The interleaver creates something like:

A1
B1
A2
B2
A3
B3

Users interact with the mixed list.

If users disproportionately click A's documents:

A wins

If they favor B:

B wins

The advantage is that A and B compete within the same user/query context.

45. But clicks aren't relevance

This is a very important transition.

Suppose:

Rank 1 → clicked
Rank 5 → not clicked

Can we conclude:

Rank 1 relevant
Rank 5 irrelevant

No.

Why?

Because the user may never have examined rank 5.

This leads to:

Position bias

Users tend to examine higher-ranked results more often.

So:

P(click∣rank=1)>P(click∣rank=10)

even if the documents have identical relevance.

46. Examination hypothesis

A simple model is:

Click=Examination×Relevance

More probabilistically:

P(C
i
	

=1)=P(E
i
	

=1)×P(R
i
	

=1)

where:

C
i
	

 = click
E
i
	

 = user examined result
R
i
	

 = result is relevant

This is the intuition behind the examination hypothesis.

A user can't click something they never examined.

47. Position-Based Model — PBM

The Position-Based Model says examination probability mainly depends on position.

For example:

Position:

1 → 0.95
2 → 0.80
3 → 0.70
4 → 0.60
5 → 0.50
...

Then:

P(C
i
	

)=P(E
i
	

∣position
i
	

)P(R
i
	

)

So if result 5 gets fewer clicks, that doesn't necessarily mean it's worse.

Maybe:

P(E
5
	

)

is simply low.

48. Cascade model

The cascade model says users examine results sequentially.

Conceptually:

result 1
   ↓
satisfying?
   │
  no
   ↓
result 2
   ↓
satisfying?
   │
  no
   ↓
result 3

If a result satisfies the user, they stop.

Therefore:

P(E
i
	

)

depends on whether the user continued past earlier results.

This makes the model more behavioral than a simple position model.

49. DBN — Dynamic Bayesian Network

DBN models are more sophisticated click models.

They distinguish things such as:

examination
click
satisfaction
continuation

For example:

Examine
   ↓
Click?
   ↓
Satisfied?
   ↓
Continue?

This lets the model represent behaviors like:

User clicked a result but then continued searching because the result wasn't satisfying.

That's much more informative than treating every click as success.

50. Counterfactual evaluation

Now we get into a much harder idea.

Suppose your existing search engine produced:

rank 1 → A
rank 2 → B
rank 3 → C

You observed clicks.

But you want to know:

What would have happened if I had shown B at rank 1?

That's a counterfactual question.

You didn't actually observe that world.

This is where off-policy evaluation comes in.

51. Propensity

Suppose your logging system tells you:

P(examined result at rank 1) = 0.9
P(examined result at rank 2) = 0.7
P(examined result at rank 3) = 0.5

These are propensities.

Generally:

p
i
	

=P(observed interaction∣context)
52. Inverse Propensity Scoring — IPS

Suppose an event has propensity:

p=0.2

It happened.

Instead of counting:

1

IPS gives it weight:

p
1
	

=
0.2
1
	

=5

So:

rarely observed event
       ↓
large weight

while:

very common event
       ↓
small weight
53. Why does IPS work conceptually?

Suppose an event is observed only 20% of the time.

If you simply count observations, you underestimate its true frequency.

But:

E[
p
I
	

]

where I is the observation indicator.

Since:

E[I]=p

we get:

E[
p
I
	

]=
p
E[I]
	

=
p
p
	

=1

That's the mathematical intuition behind inverse-propensity correction.

54. IPS in search

Suppose:

Document A

is shown at rank 10.

It gets clicked.

But rank 10 has:

p=0.1

Then its IPS weight is:

0.1
1
	

=10

So the click provides stronger evidence because it occurred despite low exposure probability.

55. But IPS has a dangerous property

If:

p→0

then:

p
1
	

→∞

So tiny propensities create huge weights.

That produces:

high variance

and unstable estimates.

This is one of the major practical problems with IPS.

Methods such as propensity clipping can trade some bias for lower variance.

56. The complete evaluation architecture

Now put everything together.

                       SEARCH SYSTEM
                            │
                  ┌─────────┴─────────┐
                  │                   │
               OFFLINE              ONLINE
                  │                   │
          ┌───────┴───────┐       ┌───┴────────┐
          │               │       │            │
       Retrieval       Ranking   A/B       Interleaving
          │               │       │            │
       Recall          nDCG     CTR          clicks
       Precision        MAP
       MRR              ERR
          │
          ▼
      TREC/Cranfield
          │
          ▼
        QRELS
          │
          ▼
   Statistical testing
          │
   ┌──────┼─────────┐
   │      │         │
   t-test Wilcoxon permutation

And then:

ONLINE CLICKS
      │
      ▼
  position bias
      │
      ▼
click models
      │
 ┌────┼──────────┐
 │    │          │
PBM Cascade     DBN
 │
 ▼
propensity
 │
 ▼
IPS
 │
 ▼
counterfactual evaluation
57. The most important conceptual distinction

I would divide everything you listed into four layers:

Layer 1 — Retrieval quality

Did we retrieve relevant things?

Precision@k
Recall@k
Layer 2 — Ranking quality

Did we put the good results at the top?

MAP
MRR
nDCG
ERR
Layer 3 — Experimental validity

Is the observed improvement actually statistically meaningful?

paired t-test
Wilcoxon
permutation test
Layer 4 — Real-user evaluation

Does the search engine actually help users?

A/B testing
interleaving
click models
position bias
counterfactual evaluation
IPS
58. And here's the mathematical progression

Since you like the math, this is the path I'd recommend:

Precision→Recall→AP→MAP→MRR→DCG→nDCG→ERR
	

Then:

Relevance Judgments→Cranfield→TREC→Pooling→Qrels
	

Then statistics:

Difference→paired tests→p-value→confidence/uncertainty
	

Then online:

Clicks→position bias→examination hypothesis→click models→propensity→IPS
	

And finally:

offline evaluation+online evaluation+counterfactual evaluation
	

= a much more complete search-evaluation framework.

The next thing I'd drill into is the first mathematical block: take one tiny ranking such as ✓ ✗ ✓ ✗ ✓, and calculate P@1, P@3, P@5, Recall@k, AP, MAP, MRR, DCG, IDCG, nDCG, and ERR by hand. Once you can calculate all of them yourself, their differences become extremely intuitive.

---

# PART II — INDEX DATA STRUCTURES & ALGORITHMS

### Inverted index construction

**BSBI**, **SPIMI** (single-pass in-memory), **LSM-style segment merging** (Lucene immutable segments).

### Posting list compression

**Variable byte**, **Elias gamma/delta**, **Simple9/16**, **PForDelta**, **SIMD-BP128**, **Elias-Fano** (quasi-succinct, fast nextGEQ), **Roaring bitmaps** (standard for set intersection). **Skip pointers** for galloping/nextGEQ.

### Query evaluation & dynamic pruning

- **TAAT vs DAAT**; DAAT dominates for top-k.
- **MaxScore** (Turtle & Flood 1995): essential/non-essential term split via max upper bounds; best for long queries.
- **WAND** (Broder et al. 2003): per-list max upper bound, pivot selection, skip docs that can't enter top-k — reduced full evaluations >90% on TREC Web with negligible loss.
- **Block-Max WAND (BMW)** (Ding & Suel 2011): per-block max, block skipping. **Variable BMW** (Mallia et al. SIGIR 2017): variable blocks, up to 37% faster on short queries. Lucene 8 (March 2019) adopted BMW.
- **Block-Max MaxScore**, **JASS/anytime ranking** (score-at-a-time, time budget), **impact-ordered indexes**, **tiering**.

### Suffix arrays, suffix trees/automata, FM-index/BWT, wavelet trees

Full-text substring/regex indexes; beat inverted indexes when no fixed tokenization (DNA, code). FM-index = BWT + wavelet tree, backward search O(m).

### Tries, radix/PATRICIA, DAWG/FST

**Lucene stores its term dictionary as an FST**; DAWG dedups suffixes.

### Signature files, Bloom/XOR filters

Probabilistic candidate prefilters (Bloom: no false negatives).

---

# PART III — STRING MATCHING / FUZZY / APPROXIMATE

### Exact

**KMP** (O(n+m)), **Boyer–Moore** (sublinear), **BM–Horspool**, **Rabin–Karp** (rolling hash), **Aho–Corasick** (trie+failure links; all patterns in O(n+matches) — ideal for gazetteer/tag matching), **Commentz-Walter**, **bitap/Shift-Or** (bitparallel).

### Edit-distance

**Levenshtein**, **Damerau–Levenshtein** (+transposition), **Needleman–Wunsch** (global), **Smith–Waterman** (local), **Hamming**, **Jaro/Jaro–Winkler** (names, prefix bonus). DP O(mn); **Ukkonen cutoff**/**banded DP** → O(kn) for small k.

- **Levenshtein automata**: DFA of all strings within distance k, intersect with dictionary. **Lucene's fuzzy query uses Levenshtein automata** intersected with its FST; capped at edit distance 2.
- **BK-trees** (metric trees on edit distance). **SymSpell** (Wolf Garbe, Symmetric Delete): precompute only deletes; claimed 1M× faster than naive, ~100× faster than BK-trees; a 5-letter word needs only 25 deletes for distance 3. Space grows fast for large distances.
- **Norvig's corrector** (edits within 1–2 + frequency dict); **noisy-channel** (argmax P(c)·P(w|c)).

### n-gram/q-gram/shingling

Char trigrams, positional n-grams, k-gram indexes for wildcard/fuzzy; similarity joins use **count filter**, **length filter**, **position filter**.

### Set similarity & joins

**Jaccard** |A∩B|/|A∪B|; **Dice** 2|A∩B|/(|A|+|B|); **Overlap** |A∩B|/min; **cosine** |A∩B|/√(|A||B|); **containment** |A∩B|/|A|. **Prefix filtering**, **PPJoin/PPJoin+**, **AllPairs**, size-aware filters.

### MinHash/LSH/SimHash (non-embedding approximate)

- **MinHash**: σ(d)=(min h_i over shingles); Pr[σ_i(A)=σ_i(B)]=J(A,B); unbiased, std err √(J(1−J)/k) (k=64→≈0.06 at J=0.5).
- **LSH banding**: k=b·r; candidate if any band matches; candidate prob = 1−(1−s^r)^b (tunable S-curve). Example k=112, b=14, r=8, τ=0.8.
- **b-bit minwise hashing**; **SimHash** (Charikar, random hyperplanes for cosine; Google web near-dup via 64-bit Hamming). These hash surface tokens, not semantics.

### Phonetic

**Soundex** (crude), **Metaphone/Double Metaphone** (better), **NYSIIS**, **Caverphone**. Indic/multilingual needs transliteration + edit distance.

### Tokenization/stemming

**Porter**, **Porter2/Snowball**, **Lancaster** (aggressive), **Krovetz** (dictionary). Lemmatization, stopwords, decompounding, CJK segmentation, Unicode NFC/NFKC, case/accent folding. Stemming/stopwords give modest real gains and interact with the ranker; because BM25 IDF down-weights common words, stopword removal matters less with BM25 than with Postgres `ts_rank` (no IDF, so `english` removes stopwords to compensate).

---

# PART IV — POSTGRESQL-NATIVE SEARCH (DEEP)

### tsvector / tsquery ✅

A `tsvector` = sorted distinct lexemes + positions + optional weights; `tsquery` = boolean/phrase expression; `@@` matches.

- **Configs/dictionaries**: `simple`, `english` (Snowball+stopwords), `synonym`, `thesaurus`, `ispell`, `unaccent`. Parsers classify token types.
- **Constructors**: `to_tsvector`, `to_tsquery`, `plainto_tsquery`, `phraseto_tsquery`, `websearch_to_tsquery`.
- **Phrase**: `<->` and `<N>` distance. **Weights** A/B/C/D via `setweight` → default multipliers {A:1.0,B:0.4,C:0.2,D:0.1}.
- **Ranking**: `ts_rank` (weighted tf) and `ts_rank_cd` (cover density — proximity aware). Normalization bitmask (OR with `|`): 0 ignore length; 1 ÷(1+log len); 2 ÷length; 4 ÷mean harmonic distance between extents (cd only); 8 ÷unique words; 16 ÷(1+log unique); 32 rank/(rank+1). Applied in listed order.
- **CRITICAL**: Postgres FTS ranking is **NOT BM25** — **no IDF**, and it must read every matching row's tsvector to rank (no top-k short-circuit) → slow on large result sets. The key limitation to design around.
- `ts_headline` (highlighting) is expensive — run only on the final page.
- **Storage**: generated column (`GENERATED ALWAYS AS (to_tsvector(...)) STORED`) cleanest; trigger-maintained is the pre-PG12 pattern.
- **Indexes**: GIN (fast lookups, slow build/update, no positions → phrase/rank recheck), GiST (lossy signatures, faster update, false positives), **RUM** extension (stores positions + timestamps → fast phrase, fast in-index ranking without heap fetch, `ORDER BY tsvector <=> tsquery` distance).
- **GIN tuning**: `gin_fuzzy_search_limit`, `fastupdate` (off for read-heavy search), `gin_pending_list_limit`, `maintenance_work_mem` (bigger = faster build). Index-only scans mostly don't help FTS (ranking needs the heap tsvector).

```sql
ALTER TABLE articles ADD COLUMN search tsvector
  GENERATED ALWAYS AS (
    setweight(to_tsvector('english', coalesce(title,'')), 'A') ||
    setweight(to_tsvector('english', coalesce(summary,'')), 'B') ||
    setweight(to_tsvector('english', coalesce(body,'')), 'C')) STORED;
CREATE INDEX idx_articles_search ON articles USING GIN (search);
```

### pg_trgm ⚙️ (contrib, trivially available)

Trigram extraction pads with 2 leading + 1 trailing space: "hello" → {" h"," he","hel","ell","llo","lo "}.

- `similarity(a,b)` = Jaccard on trigram sets; `word_similarity`/`strict_word_similarity` find best substring extent.
- Operators `%` (≥ `pg_trgm.similarity_threshold`, default 0.3), `<%` (default 0.6), `<<%`; distances `<->`,`<<->`.
- GIN faster lookup; GiST supports k-NN `<->` and cheaper updates. Accelerates `LIKE`/`ILIKE`/regex.
- **Performance cliff**: GIN trigram index doesn't store string length → short query vs many long strings returns huge candidate sets that fail recheck (the "5555 rows → 7 rows" case). Mitigate with length filters, higher thresholds, GiST for small answer sets.

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_tag_trgm ON tags USING GIN (name gin_trgm_ops);
SELECT name, similarity(name, :q) AS sim FROM tags WHERE name % :q ORDER BY sim DESC LIMIT 10;
```

### Other features

- **fuzzystrmatch** ⚙️ (`levenshtein`, `soundex`, `metaphone`, `dmetaphone`), **unaccent** ⚙️, **citext** ⚙️.
- **btree_gin/btree_gist** ⚙️: combine scalar filter + GIN FTS in one index. **intarray** ⚙️: int tag-set ops + GIN. **ltree** ⚙️: hierarchy paths with `<@`/`@>`/lquery.
- **hstore/JSONB** ✅ GIN; **array operators** ✅ `@>`/`&&`/`<@` on `tags text[]` with GIN — the tag-matching backbone.
- **Materialized views** ✅ (feeds/facets), **LATERAL** ✅ (per-group top-k), **window functions** ✅, **recursive CTEs** ✅ (closure/graph), **partitioning** ✅.

### BM25-in-Postgres extensions

- **ParadeDB `pg_search`** ⚙️: embeds **Tantivy** as custom index/operator (`@@@`) → real BM25, Block-Max WAND, fuzzy, phrase, faceting. Vendor benchmark: ~20× faster ranking and ~50s faster indexing than tsvector on 1M rows; one BM25 index replaces ~11 GIN+trgm indexes. AGPL/enterprise.
- **VectorChord-BM25 / pg_bestmatch** ⚙️: Block-WeakAnd BM25 custom operator/type; claims 3× faster than Elasticsearch in its own benchmark; own syntax.
- **Timescale `pg_textsearch`** ⚙️: OSS BM25; disk segments, Block-Max WAND + SIMD compression (41% smaller index), parallel builds (138M docs < 18 min), 2.4–6.5× faster than ParadeDB for 2–4 term queries at 138M scale (own benchmark); inherits tsvector's 2047-char word / 1MB lexeme caps.
- **pg_bigm** ⚙️ (2-gram, CJK). **ZomboDB** 🚀 (bridges to Elasticsearch).
- **Candid take**: native tsvector wins on zero dependencies and "good enough" relevance for a keyword-friendly blog; move to `pg_search` only when IDF-aware ranking or top-k latency is a measured bottleneck. ParadeDB-vs-native benchmarks were criticized on Hacker News for initially testing native FTS **without a GIN index**; properly indexed native FTS (`fastupdate=off`) is far faster than those first numbers.

```sql
-- multi-signal (FTS + trgm + tags + recency), keyset paginated
SELECT a.id, a.title,
  ( 0.6*ts_rank_cd(a.search, q)
  + 0.2*similarity(a.title, :raw)
  + 0.2*exp(-extract(epoch from now()-a.published_at)/(86400*30)) ) AS score
FROM articles a, websearch_to_tsquery('english', :raw) q
WHERE a.search @@ q AND a.tags && :tag_filter::text[]
  AND (a.published_at, a.id) < (:last_ts, :last_id)
ORDER BY score DESC, a.published_at DESC, a.id DESC LIMIT 20;
```

EXPLAIN ANALYZE guidance: ensure a Bitmap Index Scan on GIN feeds the filter; push tag/status filters into indexes with btree_gin; never `ORDER BY ts_rank` without first restricting via `@@`.

---

# PART V — TAG / TAXONOMY / FACETED SEARCH (central)

### Vocabularies & structure

- **Controlled vocabulary** vs **folksonomy**. For students+pros SE content: controlled vocabulary + synonym rings (alias table) + SKOS broader/narrower.
- Hierarchy representations/costs: **adjacency list** (recursive CTE), **materialized path/ltree** (fast subtree `<@`), **nested set** (fast reads, costly writes), **closure table** (fast both ways, more storage). Mostly-read tag tree → ltree or closure table.

### Tag statistics ✅ (plain SQL)

- **Co-occurrence**; **PMI** = log(P(a,b)/(P(a)P(b))); **NPMI** = PMI/(−log P(a,b)) ∈[−1,1]; **log-likelihood ratio** (Dunning, robust for rare tags); **chi-square**; **TF-IDF over tags**.
- Tag clustering / community detection (Louvain/label propagation); tag suggestion via co-occurrence/NPMI; duplicate detection via trigram similarity + Jaccard on co-occurrence vectors — no embeddings.

### Set-based retrieval ✅

- Inverted tag index = GIN on `tags text[]`; boolean facets via `@>`/`&&`. **Roaring-bitmap** intersection for huge corpora.
- Score Q vs T: IDF-weighted overlap Σ_{t∈Q∩T} idf(t), or Jaccard/overlap — IDF weighting so a rare tag counts more than a common one.
- **Facet counts at scale**: precompute per-tag counts in a summary table / materialized view, incrementally via triggers/outbox.

### Query → tag mapping WITHOUT embeddings ✅

1. Normalize + segment. 2. **Aho–Corasick**/gazetteer match of the whole vocabulary + alias table in one pass. 3. **Trigram fuzzy** fallback for typos. 4. Optional **gated LLM re-ranker** over the top-K candidate tags only (never invents tags).

```sql
WITH cand AS (
  SELECT tag_id, name, 1.0 AS s FROM tag_alias WHERE alias = lower(:q)
  UNION ALL
  SELECT tag_id, name, similarity(name, :q) FROM tags WHERE name % :q)
SELECT tag_id, name, max(s) AS score FROM cand GROUP BY 1,2 ORDER BY 3 DESC LIMIT 8;
```

---

# PART VI — QUERY UNDERSTANDING & EXPANSION (non-embedding)

- Parsing/segmentation/spelling/rewriting/field boosting front the pipeline.
- **Pseudo-relevance feedback**: assume top-k relevant, mine expansion terms.
  - **Rocchio**: q' = α·q + β·(mean relevant) − γ·(mean non-relevant).
  - **RM3** (interpolate expansion LM with query LM, λ≈0.6, ~3 docs, ~10 terms). Reliably lifts MAP/recall on TREC ad-hoc; **but hurts on hard/sparse queries** (drift): on tip-of-the-tongue, RM3/Bo1/KL all underperformed BM25, RM3 Recall@1000 collapsing 0.77→0.51. Gate behind a query-performance predictor.
  - **DFR expansion**: Bo1, Bo2, KL (Terrier).
- **Thesaurus/synonym** ✅ via tsquery OR-expansion or `synonym`/`thesaurus` dict.
- **Query performance prediction** (max/avg IDF, clarity; score variance); **intent classification**; session/context reformulation.

---

# PART VII — RANKING, RE-RANKING & LEARNING TO RANK

### Multi-signal scoring ✅

Lexical + recency + popularity/quality/authority.

- **Recency decay**: exponential exp(−Δt/τ) (τ=half-life/ln2), Gaussian, linear. Blogs: exponential, τ ~ weeks.
- **Score normalization** before fusion: min-max, z-score. **Raw score fusion is dangerous** — BM25 (unbounded) vs cosine ([−1,1]) live on different scales.

### Rank fusion ✅ (backbone of hybrid & multi-signal)

- **CombSUM/CombMNZ/CombANZ**.
- **RRF** — Cormack, Clarke & Büttcher, SIGIR '09, verbatim title "Reciprocal Rank Fusion outperforms Condorcet and Individual Rank Learning Methods": RRF(d)=Σ_i 1/(k+rank_i(d)); per the paper "The constant k mitigates the impact of high rankings by outlier systems," with k=60 in their experiments (robust k∈[40,80]); ranks 1-indexed; a doc missing from a list contributes 0. No normalization/training. Weighted: Σ_i α_i/(k+rank_i). Recommended for blending tsvector/trigram/tag rankings.
- **Borda count**, **Condorcet fusion**, **probabilistic fusion**.

```sql
WITH fts AS (SELECT id, row_number() OVER (ORDER BY ts_rank_cd(search,q) DESC) r
             FROM articles, websearch_to_tsquery('english',:raw) q WHERE search @@ q LIMIT 200),
     trg AS (SELECT id, row_number() OVER (ORDER BY similarity(title,:raw) DESC) r
             FROM articles WHERE title % :raw LIMIT 200),
     tag AS (SELECT id, row_number() OVER (ORDER BY cardinality(tags & :qt) DESC) r
             FROM articles WHERE tags && :qt LIMIT 200)
SELECT id, SUM(1.0/(60+r)) AS rrf
FROM (SELECT * FROM fts UNION ALL SELECT * FROM trg UNION ALL SELECT * FROM tag) u
GROUP BY id ORDER BY rrf DESC LIMIT 20;
```

### Learning to Rank

- **Pointwise** (regression/classification), **Pairwise** (RankNet, RankSVM, LambdaRank), **Listwise** (LambdaMART, ListNet, AdaRank, SoftRank).
- **GBDT** (LightGBM `lambdarank`, XGBoost `rank:*`) are practical winners; features = BM25 per field, recency, popularity, tag overlap, click stats.
- **Benchmarks**: LETOR, **MSLR-WEB10K/30K**, **Istella**, **Yahoo! LTR Challenge** (LambdaMART won). Later-stage for this product; score a stored model in the app layer, no infra.

### Cascading multi-stage

Candidate generation (BM25/tags) → rerank (LTR/cross-encoder) → policy (diversity/business rules).

### Diversification

**MMR** (Carbonell & Goldstein, SIGIR 1998): argmax [ λ·Rel(d,q) − (1−λ)·max_{s∈S} Sim(d,s) ]. Also **xQuAD**, **PM-2**, **IA-Select**, **submodular coverage**. Prevents a top-10 of near-duplicate posts.

---

# PART VIII — PERSONALIZATION & RECOMMENDATION WITHOUT EMBEDDINGS

### Sparse weighted tag/term profile ✅

- p_u = weighted sum of tags from interactions with **exponential time decay** exp(−Δt/τ); blend long-term + short-term. **Rocchio update**: p_u ← α·p_u + β·(liked) − γ·(disliked). Store as `(user_id, tag_id, weight)`; re-rank by dot product with article tag vector — pure SQL. Tune τ so 2–4-week-old interactions retain ~half weight.

### Collaborative filtering without embeddings ✅

- **Item-item kNN** (cosine/adjusted-cosine/Pearson), **user-user kNN**, **significance weighting** & **shrinkage**, **Slope One**. **Association rules** (Apriori, FP-growth): **lift** P(a,b)/(P(a)P(b)), **confidence** P(b|a). **Co-visitation graphs**.
- **Reproducibility check**: Ferrari Dacrema, Cremonesi & Jannach, "Are We Really Making Much Progress?" (RecSys 2019) — of 18 top neural methods, only 7 reproducible; 6 of those beaten by well-tuned kNN/graph baselines; only 1/7 consistently beat simple baselines. Justifies shipping item-kNN + popularity first.

### Graph-based personalization ✅ (SQL-incremental)

- **Personalized PageRank / RWR**: π = α·e_u + (1−α)·π·P, e_u = restart vector on the user's seeds, α restart prob (~0.15 global; ~0.5 in Pixie). Power iteration = few sparse mat-vec products → iterated SQL over a user–tag–item bipartite graph.
- **Pixie** (Eksombatchai et al., "Pixie," WWW 2018): pure random walks over the Pinterest object graph (3B nodes / 17B edges), α=0.5, ~100,000 steps with early stopping. Verbatim: "recommendations provided by Pixie lead up to 50% higher user engagement when compared to the previous Hadoop-based production system," with "a single server executes 1,200 recommendation requests per second with 60 millisecond latency." Proof random-walk personalization scales without embeddings.
- **SimRank**, **HITS**, **ItemRank**, **label propagation/adsorption**. RWR handles cold-start sparsity via indirect connections.

### Bandits & exploration ✅ (app-layer)

- **ε-greedy**, **UCB1** (argmax x̄_i + √(2 ln t / n_i)), **Thompson sampling** (Beta-Bernoulli — great for CTR), **LinUCB/contextual**. Essential for cold-start and freshness.

### Cold start ✅

- **Content bootstrap** from declared bio/education: run the same query→tag mapping over signup text to seed the affinity profile. **Onboarding tag elicitation**; **demographic priors**.
- **Popularity priors with shrinkage**:
  - **Wilson score lower bound** (Reddit "best"/Evan Miller): (p̂ + z²/2n − z·√(p̂(1−p̂)/n + z²/4n²))/(1 + z²/n), z=1.96. Ranks by lower bound so few-vote items aren't over-trusted.
  - **Hacker News**: (upvotes−1)^0.8 / (age_hours + 2)^1.8 · penalties (gravity 1.8).
  - **Reddit hot**: log10(max(|s|,1)) + sign(s)·(t−t0)/45000.
  - **Bayesian average** (IMDb): (v·R + m·C)/(v+m) — pull small samples toward global mean C.

### Feedback loops & calibration ✅

Guard against filter bubbles/popularity bias: exploration (bandits), diversify (MMR), calibrate the result tag mix to the user's true tag distribution (Steck). Keep a random/novel slot for serendipity.

---

# PART IX — EMBEDDING-BASED SEARCH (comparative half)

### Dense retrieval theory

- **Bi-encoders** (DPR, ANCE — mines hard negatives from the index), **cross-encoders** (joint encoding, rerank only), **ColBERT/ColBERTv2** (late interaction, MaxSim, multi-vector), **Sentence-Transformers**, instruction-tuned, **Matryoshka** (truncatable dims).

### Learned SPARSE retrieval — the bridge ("no vectors, better relevance")

Sparse term weights in a normal inverted index: **DeepCT/HDCT**, **doc2query/docT5query** (per Thakur et al. 2021, docT5query "outperforms BM25 on 11/18 datasets while providing a competitive performance on the remaining datasets"), **doc2query--** (filter hallucinations), **TILDE**, **DeepImpact**, **uniCOIL**, **SPLADE/v2/++** (MLM expansion + FLOPS sparsification). MS MARCO dev MRR@10: BM25 (Anserini) = 0.184; SPLADE++SD = 37.6, and SPLADE-v3 = 40.2 ("gets more than 40 MRR@10 on the MS MARCO dev set," Lassance et al., "SPLADE-v3," arXiv:2403.06789). BEIR: SPLADE ~51 vs BM25 ~43. Run on Lucene/PISA inverted indexes — semantic gain **without ANN infra** (but need a model at index+query time).

### ANN index algorithms

- **HNSW** (graph; M default 16, ef_construction 64–200, ef_search at query). **IVFFlat/IVFPQ** (`lists`, `nprobe`), **PQ/scalar/binary quantization**, **DiskANN/Vamana**, **ScaNN**, **Annoy**, **LSH for cosine**.
- pgvector-observed at ~0.998 recall: IVFFlat 128s build / 257MB / 2.6 QPS vs HNSW 4065s / 729MB / 40.5 QPS — HNSW ~15× faster queries, ~32× slower build, 2.8× more space; IVFFlat recall degrades on updates.

### pgvector in depth ⚙️ (comparison only — excluded by his constraints)

- Types `vector`/`halfvec`/`bit`/`sparsevec`; ops `<->` L2, `<=>` cosine, `<#>` neg IP, `<+>` L1.
- `ivfflat` (`lists`≈rows/1000 up to 1M then √rows; `probes`≈√lists) vs `hnsw` (`m`, `ef_construction`, `hnsw.ef_search`). Indexed `vector` dim limit 2000. Binary-quant HNSW (v0.7.0) ~150× faster build than v0.5.0 on dbpedia-1M.
- **Filtering + ANN**: pre- vs post-filter problem; pgvectorscale/StreamingDiskANN and iterative scans address it. Memory/build dominate at tens of millions of vectors.

### Hybrid search

BM25/tsvector + vector via **RRF** (default in Elasticsearch/OpenSearch/Azure AI Search/Weaviate/MongoDB Atlas) or weighted normalized sum. Hybrid raises recall ~15–30% and beats either alone on many BEIR tasks — e.g., hybrid raised BEIR nDCG@10 "from 43.42 (BM25) to 52.59" (Yerramsetti et al., "From Retrieval to Generation," arXiv:2502.20245). On financial docs BM25 alone beat dense, and two-stage hybrid+rerank hit Recall@5 0.816 / MRR@3 0.605.

### Honest cost/benefit — why NOT embeddings can be right

- Dense/hybrid gains real (in-domain MS MARCO +7–18 nDCG over BM25) but shrink/reverse out-of-domain; **BEIR's headline finding: a well-tuned BM25 is a robust baseline, competitive or better than early dense models out-of-domain**.
- Embedding costs: GPU/model dependency, index build/memory, **re-embedding on every edit**, model drift/versioning, poor explainability, worse cold-start for new tags. For an editable, keyword-friendly, tag-organized SE blog with an explainability expectation, staying lexical + tag-based is defensible, cheaper, more transparent — with learned-sparse as the future upgrade that still lives in an inverted index.

---

# PART X — IMPLEMENTATIONS / SYSTEMS CATALOG

Real BM25 (Lucene family & others): **Apache Lucene** (BM25 default since 6.0; FST term dict; BMW since v8), **Elasticsearch** & **OpenSearch** (Lucene; RRF hybrid; ES BM25 default since 5.0), **Solr**, **Vespa** (BM25 + tensor/ANN), **Tantivy** (Rust; powers ParadeDB), **Anserini/Pyserini** (Lucene; standard for reproducible BM25), **PISA** (research; WAND/BMW/VBMW; fastest experimental), **Xapian** (own k1/k2/k3/b), **Terrier** (DFR/PL2/DPH/BM25), **Manticore/Sphinx**, **SQLite FTS5** (built-in Okapi BM25 `bm25()` — negated so smaller=better; equal column weights default; k1=1.2, b=0.75 in source), **DuckDB FTS** (BM25), **MongoDB Atlas Search** (Lucene), **Redis Search** 🚀 (BM25; Redis excluded), **Meilisearch**/**Typesense** (typo-tolerant custom ranking, not classic BM25 default), **Bleve** (Go; TF-IDF/BM25), **Whoosh** (Python BM25F, unmaintained), **Zinc/Zincsearch**, **Quickwit** (Tantivy, logs), **ClickHouse** (token/ngram bloom skip indexes, not full BM25), **MySQL FULLTEXT** (own TF-IDF-ish, not BM25), **Algolia** 🚀 (proprietary, custom tie-broken ranking). **Postgres**: native tsvector = NOT BM25; `pg_search`/VectorChord-BM25/pg_textsearch = real BM25 via extension.

---

# PART XI — EXPERIMENTS, BENCHMARKS & EMPIRICAL RESULTS

### Retrieval benchmarks (with sources)

- **BEIR** (Thakur et al., NeurIPS 2021): avg nDCG@10 — BM25 ≈ 43.42; early dense (DPR) often **below** BM25 out-of-domain; docT5query beats BM25 on 11/18 sets; SPLADE ≈ 51; modern dense (OpenAI text-embedding-3-large ~64.6, Qwen3-Embedding-8B ~70.6 on MTEB) now clearly exceed BM25 — the gap widened since 2021 (talk of a "BEIR-2").
- **MS MARCO passage dev MRR@10**: BM25 (Anserini) = 0.184 (0.186 on Test; RepBERT, arXiv:2006.15498); docT5query ≈ 0.28; SPLADE++SD = 37.6; SPLADE-v3 = 40.2; strong dense ≈ 0.38–0.40.
- **Per-dataset BM25 nDCG@10**: FEVER 75.3, HotpotQA 60.3, TREC-COVID 65.6, FiQA 23.6, ArguAna 31.5 (BM25's high domain variance).
- **TREC-COVID**: ANCE 0.654 (just below BM25) → 0.735 after fine-tuning (+6.7); ColBERT +5.8.
- **"BM25 is hard to beat"**: Kamphuis et al. (ECIR 2020, variants <1 pt); Lin, "The Neural Hype and Comparisons Against Weak Baselines" (SIGIR Forum 2019).
- **Cross-encoder rerank**: large precision lift on top-k (monoBERT improves with rerank depth) at high latency.

### Recommender benchmarks

MovieLens/Amazon/Yelp; RecSys 2019 critique above; item-kNN and TopPopular repeatedly competitive; P3α/RP3β (random-walk) strong and cheap.

### System latency/throughput

- **pg_search vs tsvector**: ~20× faster ranking, ~50s faster build on 1M rows (ParadeDB); Block-Max-WAND skips blocks tsvector must fully score.
- **pg_trgm**: GIN turns a `LIKE '%..%'` seq scan (e.g., 180ms) into a Bitmap Index Scan, far faster, but the short-string/long-candidate recheck cliff remains.
- **pgvector**: IVFFlat vs HNSW numbers above.

### Industrial case studies (named, sourced)

- **Discourse** ✅ Postgres-only: search runs entirely on PostgreSQL FTS (`to_tsvector`/`to_tsquery`, GIN, `ts_rank_cd`); tsvectors in `post_search_data`; reindex via `rake search:reindex`; CJK segmented in Ruby; category "search priorities" weighting (v2.3). Optional external `discourse-algolia` plugin exists but native is Postgres. (Discourse repo `lib/search.rb`; Meta.)
- **GitHub code search "Blackbird"** (GitHub Blog, Feb 6 2023): custom Rust engine, **ngram "sparse gram" inverted index** (not fixed trigrams), sharded by blob SHA; **15.5B documents, 45M repos, 115TB code**; **p99 ~100ms/shard**, **~640 QPS per 64-core host** (vs 0.01 QPS grep), **~120,000 docs/s ingest**, full reindex ~18h with delta indexing, **~25TB** index (¼ of raw). Solr → Elasticsearch (2013) → Blackbird. Lexical, not embeddings.
- **Stack Overflow** (Nick Craver "The Architecture — 2016"; SO Blog "Unified Search" 2021): "Our site search is powered by Elasticsearch"; 3-node clusters, 192GB RAM/node, SQL Server source-of-truth, ROWVERSION sync. (Contrast: external Lucene, BM25.)
- **Instacart** (InfoQ, Aug 2025): consolidated search onto PostgreSQL, phasing out Elasticsearch, combining keyword + embedding retrieval in one Postgres system to cut sync overhead (hybrid, not pure tsvector).
- **Wikipedia/CirrusSearch**: MediaWiki extension backed by Elasticsearch/OpenSearch.
- **Smaller "replaced ES with Postgres"**: p50 35ms (ES) → 45ms (PG) on a few-million-row corpus (Sezer); "within a 200ms budget" (Xata) — with the caveat ES pulls ahead at very large scale / heavy aggregations.
- **SQLite FTS5** (official docs): "The built-in auxiliary function bm25() returns a real value… the better the match, the numerically smaller the value returned." Real Okapi BM25; equal column weights default; k1=1.2/b=0.75 in source (not tunable).

---

# PART XII — PRACTICAL ENGINEERING CONCERNS

- **Index freshness/incremental update** ✅: generated tsvector columns update on write; for derived tag affinities use a **Postgres-backed outbox/queue** — enqueue recompute on interaction, batch-process. Near-real-time is fine for a blog.
- **Tag vocabulary changes invalidating affinities**: version the vocabulary; on rename/merge remap affinity rows in a transaction; on delete redistribute weight to parent (ltree). Trigger batch recompute of affected users via the outbox.
- **Caching without Redis** ✅: Postgres materialized views / summary tables for feeds & facet counts; app-level in-process LRU; HTTP caching (ETag/Cache-Control) for anonymous feeds; precomputed "hot" feed on a schedule.
- **Scaling** ✅: read replicas for search; time partitioning; **keyset/cursor pagination** (WHERE (sort_key,id) < (:last)) not OFFSET; top-k per partition via LATERAL.
- **Observability** ✅: log queries, zero-result rate, CTR, abandonment, latency percentiles; a **golden query set** + offline nDCG@10/MRR harness for relevance regression testing before shipping ranking changes.
- **Multilingual/Indic/Unicode** ✅: NFC normalization, unaccent, per-language tsconfig; transliteration + trigram for Indic; `simple` config for languages without a stemmer.
- **Security/abuse** ✅: never interpolate user text into `to_tsquery` (throws/injectable) — use `websearch_to_tsquery`/`plainto_tsquery` + parameter binding; cap trigram/regex cost (length limits, statement_timeout); rate-limit fuzzy/regex endpoints.

---

# COMPARISON TABLES

### Lexical vs Learned-Sparse vs Dense vs Hybrid

|                        | Lexical (BM25/tsvector) | Learned Sparse   | Dense bi-encoder | Hybrid (RRF) |
| ---------------------- | ----------------------- | ---------------- | ---------------- | ------------ |
| Index                  | Inverted                | Inverted         | ANN              | Both         |
| Infra                  | Minimal (Postgres)      | Inverted + model | GPU + vector DB  | Most         |
| Semantic recall        | Low                     | Med-High         | High             | Highest      |
| Out-of-domain          | Robust                  | Robust           | Fragile          | Robust       |
| Explainable            | Yes                     | Partly           | No               | Partly       |
| Cold-start new content | Instant                 | Needs encode     | Needs embed      | Mixed        |
| MS MARCO MRR@10        | ~0.184                  | ~0.38–0.40      | ~0.38            | ~0.40        |

### GIN vs GiST vs RUM

|              | GIN                      | GiST           | RUM             |
| ------------ | ------------------------ | -------------- | --------------- |
| Lookup       | Fast                     | Slower (lossy) | Fast            |
| Build/update | Slow build; pending list | Fast update    | Slower build    |
| Positions    | No                       | No             | Yes             |
| Phrase       | Heap recheck             | Heap recheck   | In-index        |
| Ranking      | Heap fetch               | Heap fetch     | In-index`<=>` |
| In core      | Yes                      | Yes            | No (extension)  |

### tsvector vs pg_trgm vs pg_search vs Elasticsearch

|                | tsvector ✅              | pg_trgm ⚙️       | pg_search ⚙️        | Elasticsearch 🚀   |
| -------------- | ------------------------ | ------------------ | --------------------- | ------------------ |
| Model          | Boolean+ts_rank (no IDF) | Trigram Jaccard    | BM25 (Tantivy)        | BM25 (Lucene)      |
| Typo tolerance | No                       | Yes                | Yes                   | Yes                |
| Top-k pruning  | No                       | No                 | Block-Max WAND        | Block-Max WAND     |
| Infra cost     | None                     | None               | Extension             | Cluster            |
| Best for       | Keyword FTS in-DB        | Fuzzy names/titles | Elastic-quality in-DB | Scale/aggregations |

### Personalization vs cold-start vs cost

| Approach                     | Cold-start fit            | Cost (PG raw SQL)     | Notes                       |
| ---------------------------- | ------------------------- | --------------------- | --------------------------- |
| Content tag profile + decay  | Excellent (from bio)      | Low                   | Start here                  |
| Popularity + Wilson/Bayesian | Excellent                 | Low                   | Non-personalized prior      |
| Item-kNN CF                  | Poor (needs interactions) | Medium                | Strong baseline (RecSys'19) |
| Assoc. rules / co-visitation | Medium                    | Medium                | "Others also read"          |
| Personalized PageRank / RWR  | Good (sparsity)           | Medium (iterated SQL) | Pixie-proven, scalable      |
| Contextual bandits           | Excellent (exploration)   | Medium (app layer)    | Freshness/serendipity       |

---

# RECOMMENDATIONS (staged, with thresholds)

**Stage 0 — MVP (pure Postgres):**

- tsvector generated column (weighted A/B/C over title/summary/body) + GIN; `websearch_to_tsquery`.
- Tags as `text[]` + GIN (`@>`,`&&`); IDF-weighted tag-overlap scoring.
- Query→tag mapping: Aho–Corasick over the vocabulary + pg_trgm fuzzy fallback + alias table.
- Multi-signal score = ts_rank_cd + tag-overlap-IDF + exponential recency, fused with RRF (k=60).
- Cold-start: derive initial tag affinity from bio via the same mapping; popularity prior via Wilson lower bound / Bayesian average.
- Keyset pagination; statement_timeout; `plainto_/websearch_to_tsquery` only (injection safety).

**Stage 1 — Personalization (after interaction logs):**

- Derived sparse tag-affinity profile with exponential decay (short+long term), updated via the Postgres outbox.
- Re-rank candidates by profile·article-tags dot product blended into the RRF.
- Item-kNN "others also read" and MMR diversification on the feed.
- ε-greedy/Thompson exploration slot for freshness.

**Stage 2 — Graph personalization & tuning:**

- Personalized PageRank / RWR over the user–tag–item graph, computed incrementally (iterated SQL/materialized), Pixie-style.
- Golden-query set + offline nDCG harness; tune recency τ and RRF weights against it.

**Upgrade thresholds:**

- **Add `pg_search` (BM25) or VectorChord-BM25** when offline nDCG@10 on your golden set is limited by missing IDF, OR top-k latency on low-selectivity queries exceeds budget because `ts_rank` scores every match. Benchmark first with a properly GIN-indexed native baseline (`fastupdate=off`).
- **Consider learned-sparse (docT5query/SPLADE-doc)** — still inverted-index, no ANN — when semantic recall on paraphrase queries is the measured gap but you want to avoid vector infra.
- **Only then consider embeddings/pgvector or hybrid** if paraphrase/semantic recall remains the dominant failure mode AND you can absorb re-embedding-on-edit, memory, explainability costs. Even then, RRF-fuse with the existing lexical signal, don't replace it.

---

# CAVEATS

- Postgres `ts_rank`/`ts_rank_cd` is not BM25 (no IDF, no top-k pruning) — biggest quality/perf caveat.
- Several benchmark numbers are vendor-reported (ParadeDB/VectorChord/Timescale) or from secondary blogs (the "replaced ES" p50/p99 figures, Instacart via InfoQ); treat as directional and re-benchmark on your own data.
- Leaderboards move fast; the dense-vs-BM25 gap on BEIR widened since 2021, but BM25's out-of-domain robustness remains repeatedly confirmed.
- MinHash/LSH, SimHash, phonetic methods are approximate — always verify candidates with the exact measure.
- PRF (RM3)/aggressive expansion can hurt on hard/sparse queries (drift); gate behind a performance predictor.
- SQLite FTS5's k1=1.2/b=0.75 come from source, not the doc page; Discourse lacks a published latency figure.
