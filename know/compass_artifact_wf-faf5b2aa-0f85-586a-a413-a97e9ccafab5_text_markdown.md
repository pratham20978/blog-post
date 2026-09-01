# Implementation Research Report: Backend Personalized Tag-Based Blog Search & Recommendation Platform

## TL;DR
- Within the locked constraints (raw-SQL Postgres, no embeddings, lexical/set-based only), the strongest design keeps the linear reranker as a transparent baseline but adds three high-leverage, battle-tested edges: **Reciprocal Rank Fusion (RRF, Cormack, Clarke & Buettcher, SIGIR 2009, k≈60)** to combine heterogeneous signals; the **smlar extension (Bartunov & Sigaev, PGCon 2012)** with TF-IDF set similarity plus the **Tversky index (Tversky 1977)** for asymmetric query⊆document tag matching; and **team-draft interleaving (Radlinski, Kurup & Joachims, CIKM 2008)** for evaluation at low traffic — 10-100× more sensitive than A/B.
- For login-time cold start, the compliant, proven pattern is **preference elicitation + attribute/demographic mapping onto the closed tag vocabulary** (lexical/gazetteer + BM25-over-tag-descriptions, snapped via pg_trgm+levenshtein), wrapped in **empirical-Bayes/Beta-Binomial shrinkage priors** that decay as real engagement arrives, with **Thompson sampling (Beta-Bernoulli)** for exploration. A third narrow gated constrained-JSON LLM use (bio→allowed tags) is justified but must have a fully non-LLM fallback; "OSINT"/third-party enrichment is legally risky under India's DPDP Act 2023 and GDPR and should be dropped in favor of consented progressive profiling.
- The "no embeddings" constraint costs measurable recall on semantic/paraphrase queries; the best compensations are Postgres thesaurus/synonym dictionaries, tag co-occurrence expansion (PMI/FolkRank), and true BM25 via a Postgres-native extension. Corpus cold-start (tens-hundreds of posts) is the binding limit early on, so Bayesian quality smoothing and diversity caps matter more than index choice until ~10k+ posts.

## Key Findings

### The "edge" shortlist (verified, maintained as of 2026)
1. **RRF (Cormack, Clarke & Buettcher, SIGIR 2009)** — replace the fragile weighted-sum of incommensurable scores with rank fusion. Trivially expressible in one SQL CTE. k=60 default is robust.
2. **smlar extension** (Oleg Bartunov & Teodor Sigaev, PGCon 2012) — in-database set similarity with cosine/**TF-IDF**/overlap modes and GiST/GIN index support. Direct fit for the tag-set matching core; the only mature Postgres extension that does IDF-weighted array similarity with an index.
3. **True BM25 in Postgres** — two options: ParadeDB **pg_search** (AGPLv3 + commercial, Tantivy-based, mature) and TigerData **pg_textsearch v1.0** (released 2026-04-03, **PostgreSQL license**, benchmarked faster than ParadeDB). This fixes ts_rank_cd's lack of corpus statistics and length normalization.
4. **RUM index** (Postgres Professional) — stores lexeme positions in the index so `ORDER BY tsvector <=> tsquery LIMIT n` is an index scan, not a heap-scan-then-sort. Fixes the classic "computed ORDER BY + LIMIT" killer for lexical rank.
5. **Tversky index (Tversky, "Features of similarity," Psychological Review 1977)** — asymmetric set similarity, ideal for query⊆document tag matching.
6. **FolkRank / personalized PageRank on the tag co-occurrence graph (Hotho, Jäschke, Schmitz & Stumme, ESWC 2006)** — proven query expansion for tag search; precomputable offline.
7. **Team-draft interleaving (Radlinski, Kurup & Joachims, CIKM 2008; validated Chapelle, Joachims, Radlinski & Yue, ACM TOIS 2012)** — 10-100× more data-efficient than A/B for a small new site.
8. **Wilson score lower bound (Evan Miller 2009) / Beta-Binomial Bayesian smoothing** for quality.
9. **Thompson sampling, Beta-Bernoulli** for new-user exploration — better regret than ε-greedy, implementable in raw SQL.
10. **Postgres thesaurus + synonym dictionaries** — native synonym expansion at index/query time (the no-embeddings compensation).
11. **pg_ivm (incremental view maintenance)** and **LISTEN/NOTIFY** for low-latency queue wakeup.
12. **Decay-relative-to-fixed-epoch** so incremental and full-recompute affinity paths are provably identical.

---

## Details (organized by area)

### COLD-START FEATURE (researched hardest)

**1. Preference elicitation / onboarding interview.**
Canonical: Rashid, Albert, Cosley, Lam, McNee, Konstan & Riedl, "Getting to know you: learning new user preferences in recommender systems," IUI 2002 (studied six item-selection strategies: popularity, entropy, popularity×entropy, log(popularity)×entropy [HELF], item-item personalized, and random). Follow-up: Rashid, Karypis & Riedl, "Learning preferences of new users… an information theoretic approach," SIGKDD Explorations 10(2), 2008. Decision-tree interview: Golbandi, Koren & Lempel, "Adaptive bootstrapping of recommender systems using decision trees," WSDM 2011; functional matrix factorization (Zhou et al., "Functional matrix factorizations for cold-start recommendation," SIGIR 2011) associates latent profiles with each tree node.
- Finding on # of questions: pure popularity produces items users can rate but that carry little information; pure entropy picks informative-but-obscure items users can't rate; **popularity×entropy and HELF balance both**. Rashid 2008 shows accuracy gains flatten after a modest number of items; the MovieLens live study had users rate ~20 items and users did not find it burdensome.
- **Adapt to TAGS not items:** run the interview over *tags/topics* (e.g., "Which of these do you work with? [Python] [Distributed Systems] [LLMs] [Kubernetes]…") selected by popularity×entropy over the current tag vocabulary. This is cheaper and directly seeds the tag-affinity vector. **ADOPT NOW** (2-6 topic chips at signup). Verdict: transparent, no ML needed at small scale.

**2. Content-based / demographic / attribute mapping onto the closed vocabulary (no embeddings).**
- **Lexical/dictionary/gazetteer mapping:** maintain a synonym/alias table (tag → surface forms) and match declared role/skills/bio tokens against it; snap unmatched phrases to nearest allowed tag with **pg_trgm similarity() / word_similarity()** + **levenshtein** (fuzzystrmatch). This is the same closed-set snapping the spec already mandates for LLM output.
- **BM25/TF-IDF over a tag-description index:** build one short "document" per tag (its description + aliases + example post titles) and retrieve tags by scoring the user's bio against that index. BM25 (Robertson & Zaragoza) or smlar TF-IDF.
- **Keyword extraction from bio:** YAKE! (Campos et al., Information Sciences 2020) is unsupervised, corpus-independent, single-document, and in the paper outperforms TF-IDF, RAKE, TextRank, TopicRank, KP-Miner on 20 datasets (F1@10); RAKE and YAKE are the fastest. Extract candidate phrases, then snap to the closed vocabulary. TextRank/TopicRank are graph-based alternatives.
- **Taxonomy mapping (ESCO/O*NET/Wikipedia/DBpedia):** useful to map job titles→skills→tags, but adds heavy external dependencies; for a one-person team, a hand-curated role→tag seed table is more maintainable. Verdict: **ADOPT** dictionary+trgm snapping + YAKE now; **SKIP** external taxonomy graphs initially (revisit if role data gets rich).

**3. LLM with constrained JSON for signup profile → allowed tags.**
Literature: ONCE (Liu et al., "ONCE: Boosting Content-based Recommendation with Both Open- and Closed-source LLMs," WSDM 2024) uses closed-source LLMs as content summarizers and **user profilers**; GENRE (same line) generates user profiles for cold-start news rec; "LLMs as Data Augmenters for Cold-Start Item Recommendation" (Wang et al., WWW 2024 companion) shows LLM-inferred preferences lift cold-start recall. Survey: "Cold-Start Recommendation towards the Era of LLMs" (arXiv 2501.01945, 2025).
- **Verdict on adding a THIRD gated LLM use:** Justified. It is the same shape as the two allowed uses (constrained JSON, closed-set validated, admin-gated). Prompt: "Given this bio/role/education, output tags ONLY from this allowed list with confidence 0-1; output {} if unsure." Enforce with grammar/JSON-schema constrained decoding, closed-set validation, abstention, and snap hallucinated tags via pg_trgm+levenshtein. Keep it cheap: call once per signup, cache, cap tokens.
- **Mandatory non-LLM fallback:** the dictionary + YAKE + BM25-over-tag-descriptions path must produce a profile on its own so the system never depends on the LLM and works when the admin key is absent. **ADOPT LATER** (LLM as enhancement); **ADOPT NOW** the deterministic path.

**4. Statistical treatment of a cold profile (priors + shrinkage).**
- **Beta-Binomial per-tag prior:** model per-tag affinity as engagement rate with a Beta(α₀,β₀) prior; posterior mean = (positives + α₀)/(impressions + α₀ + β₀). Set the prior from the declared/segment profile (pseudo-counts).
- **Empirical Bayes / James-Stein shrinkage:** shrink a new user's per-tag estimates toward a **segment mean** (e.g., "backend engineers") or the global mean; shrinkage weight ∝ prior strength / (prior strength + observed count).
- **Blending declared prior with first real signals:** affinity(t) = (m·μ_declared(t) + Σ engagement signals) / (m + n_signals), where m = prior strength (pseudo-count, start m≈5-20 impressions-equivalent) that **decays** as evidence accumulates. This is the same C-smoothing form the spec already uses for Quality — reuse it. Confirmed analog: Hu, Koren & Volinsky, "Collaborative Filtering for Implicit Feedback Datasets," ICDM 2008 (DOI 10.1109/ICDM.2008.22) proposed confidence-weighted implicit feedback c_ui = 1 + α·r_ui with α = 40 in their experiments — the same "stronger signal → higher confidence weight" principle your click/dwell/complete/save weights already encode. **ADOPT NOW.**

**5. Exploration for new users.**
- **Thompson sampling (Beta-Bernoulli):** per candidate/tag, sample θ~Beta(positives+α, negatives+β), rank by sample. Near-optimal regret, trivial in SQL (draw from Beta via a small pl/pgsql gamma sampler or precomputed draws). Preferred over ε-greedy.
- **UCB1 / LinUCB:** Li, Chu, Langford & Schapire, "A Contextual-Bandit Approach to Personalized News Article Recommendation," WWW 2010 — on "a Yahoo! Front Page Today Module dataset containing over 33 million events. Results showed a **12.5% click lift compared to a standard context-free bandit algorithm, and the advantage becomes even greater when data gets more scarce**" — directly relevant to cold start. LinUCB needs per-arm matrix inversion (A⁻¹), heavy for raw SQL; **UCB1** (score = mean + √(2·ln N / n)) is SQL-friendly.
- **Bounding exploration so first impressions aren't ruined:** cap exploration slots (e.g., 1-2 of the top 10), keep ε small (spec's ε≈0.1 is reasonable; literature supports small ε), and never explore in the top 3 positions. **ADOPT** Thompson sampling for the exploration slots; **ADOPT LATER** LinUCB only if you outgrow SQL.

**6. Privacy/compliance guardrails.**
- **India DPDP Act 2023** (Rules notified 13 Nov 2025; core obligations effective ~13 May 2027): consent must be **free, specific, informed, unconditional, unambiguous** with clear affirmative action (Section 6); a **standalone plain-language notice** must accompany consent (itemized data, purpose, how to withdraw, how to complain); **purpose limitation** (Section 5) — data used only for the stated purpose; data-principal rights: access, correction, erasure, grievance, nomination; penalties up to ₹250 crore per instance.
- **GDPR:** Art. 6 lawful basis, Art. 13/14 notice, Art. 22 (automated decision-making), purpose limitation, data minimisation.
- **Application:** (a) OAuth-provided fields — process only with consent and only fields you disclosed; (b) direct onboarding questions — fine with notice + consent; (c) third-party enrichment / "OSINT" on a person — **legally risky**: fails purpose limitation, transparency (Art. 14 / DPDP notice), and data minimisation; recommend **dropping it**.
- **Compliant design:** progressive profiling, explicit onboarding, OAuth scopes with consent, user-supplied links only, and a transparent, editable **"Your interests / why am I seeing this"** panel.
- **Lead-generation flag:** the stated intent to collect data for later lead-gen makes purpose limitation and consent notice *especially* important — lead-gen is a **separate purpose** requiring its own consent and notice; do not bundle it with the personalization consent. **ADOPT** consented progressive profiling; **SKIP** OSINT.

**7. Engineering shape (don't make the user wait).**
- **Async enqueue + immediate good first page:** on signup, synchronously compute the cheap deterministic profile (dictionary+trgm snap of declared tags — sub-10ms) and render an **Audience-A-lite** first page immediately; enqueue the heavier derivation (YAKE, BM25-over-tags, optional LLM) via the Postgres job queue; when it completes, the *next* page is fully personalized.
- **Fallback for the very first page:** if no profile yet, serve the **Audience B** ranking (freshness + quality + lexical) — already "good." Latency budget: p95 first page < ~200ms using precomputed static-quality columns and RRF over two candidate lists. **ADOPT NOW.**

---

### A. RANKING & RERANKING THEORY

**BM25 / BM25F (Robertson & Zaragoza, "The Probabilistic Relevance Framework: BM25 and Beyond," Foundations & Trends in IR, 2009).**
Formula (Robertson-Walker/ATIRE variant):
score(q,d) = Σ_{t∈q} IDF(t) · [ tf · (k₁+1) ] / [ tf + k₁·(1 − b + b·(L_d / L_avg)) ], with IDF(t)=ln(N/df_t) (or the +0.5-smoothed RSJ form ln[(N−df+0.5)/(df+0.5)+1]).
- **Defaults:** k₁ = 1.2-2.0 (start 1.2 or 1.5), b = 0.75. (Xapian uses k₁=1, b=0.5 as its own defaults.)
- **Why it beats ts_rank_cd:** ts_rank/ts_rank_cd have **no corpus IDF** and **no true document-length normalization** — they only reward within-document term frequency/proximity. BM25 adds saturating tf, IDF, and length normalization.
- **Postgres-native BM25 options:** (1) **ParadeDB pg_search** — `CREATE INDEX … USING bm25`, mature, Tantivy/Rust, **AGPLv3** (or commercial); (2) **TigerData pg_textsearch v1.0** (2026), **PostgreSQL license**, benchmarked faster than ParadeDB; (3) **hand-rolled BM25** over tsvector statistics + a term-stats table (portable, no extension, but you maintain df/avgdl yourself); (4) **smlar TF-IDF** as a set-similarity proxy. Verdict: **ADOPT LATER** pg_textsearch (license fit) once corpus > a few thousand; hand-rolled BM25 is fine at small scale.

**Fixing/replacing ts_rank_cd:** use setweight A/B/C/D (title=A, headings=B, body=C/D), pick the ts_rank normalization bitmask deliberately (see F), or move to RUM/BM25. **ADOPT** setweight + RUM now.

**Rank fusion vs weighted linear blend.**
- **RRF (Cormack, Clarke & Buettcher, SIGIR 2009):** score(d) = Σ_i 1/(k + rank_i(d)), k=60 default. Rank-based, so it needs **no score normalization** and is immune to the BM25-vs-Jaccard scale mismatch. Weighted variant: Σ_i α_i/(k+rank_i(d)).
- **CombSUM/CombMNZ (Fox & Shaw 1994):** sum normalized scores (CombSUM) or multiply by # nonzero lists (CombMNZ) — require min-max or z-score normalization.
- **Verdict:** The user's weighted-sum of five heterogeneous [0,1] terms is fragile because normalization is unstable at small corpus. **ADOPT RRF to fuse the candidate lists** (lexical list, tag-match list, personalization list, freshness/quality list), then optionally apply a light weighted-RRF. Keep the linear model as an interpretable secondary. This is a top "edge."

**Learning to rank (when click data exists).**
Pointwise/pairwise/listwise; RankNet→LambdaRank→LambdaMART (Burges); XGBoost/LightGBM rankers. **Start with the transparent linear model** and tune weights by grid search / coordinate ascent on offline **NDCG**. Graduate to LambdaMART once you have enough judged/click data. **ADOPT LATER.**

**Position bias & counterfactual LTR.**
- Joachims, Swaminathan & Schnabel, "Unbiased Learning-to-Rank with Biased Feedback," WSDM 2017 (Best Paper): **Propensity SVM-Rank**. IPS-weighted empirical risk: R̂_IPS(S) = (1/N) Σ_i Σ_{y: clicked & relevant} rank(y|S(x_i)) / Q(observation | x_i, ȳ_i), where Q = examination propensity at the shown position. Unbiased if positivity (Q>0) and unconfoundedness hold.
- Click models (Craswell, Zoeter, Taylor & Ramsey, "An experimental comparison of click position-bias models," WSDM 2008): **examination/position-based model** P(click)=P(examined|position)·P(relevant); **cascade model** (best for early ranks): examination of rank k = Π_{i<k}(1−rel_i).
- **What to LOG NOW to enable this later:** the full **presented ranking with positions**, the query/context features, **clicks (which result, which position)**, and enough to reconstruct **examination propensity** per shown position; add a small **randomization** (e.g., occasionally swap a lower result to top) so propensities are estimable. The spec's append-only engagement log already captures impressions+position — ensure position and the presented set are stored. **ADOPT NOW** (logging only); **ADOPT LATER** (the LTR itself).

**Quality/popularity scoring math.**
- **Wilson score lower bound (Evan Miller, "How Not To Sort By Average Rating," 2009):** (p̂ + z²/2n − z·√[p̂(1−p̂)/n + z²/4n²]) / (1 + z²/n); z=1.96 for 95%. Postgres one-liner exists.
- **Bayesian average / Beta-Binomial:** (positives + C·m)/(impressions + C) — **this is exactly the user's Quality formula**, which is sound; m = global mean rate, C = prior strength (start C≈ the median impressions-per-post, e.g., 20-100).
- **Hacker News:** (upvotes−1)^0.8 / (age_hours+2)^1.8. **Reddit "hot":** log10(score) + sign·seconds/45000. **Hawkes process** for bursty attention (advanced).
- **Verdict:** Keep the Bayesian-smoothed rate (correct); optionally compute **Wilson lower bound** as an alternative conservative quality column. **ADOPT NOW.**

**Freshness/recency.**
- User's Freshness = 1/(age_hours+2)^1.8 is a Hacker-News-style power-law — reasonable.
- **Elasticsearch decay functions** (gauss/exp/linear with origin, scale, offset, decay) are a proven parameterization: exp decay λ from a chosen half-life. For **daily publishing**, a half-life of ~3-7 days for the freshness term keeps the feed lively without burying good evergreen posts (tune with interleaving). **ADOPT NOW**, tune later.

**Diversity.**
- **MMR (Carbonell & Goldstein, SIGIR 1998):** argmax_d [ λ·Rel(d) − (1−λ)·max_{d'∈S} Sim(d,d') ]. User's λ≈0.7, tag-Jaccard similarity, over top ~50 — sound.
- **xQuAD, IA-Select** (query-aspect diversification); **DPPs** (determinantal point processes) for diverse rec — heavier.
- **Simple production alternatives:** per-tag/per-category caps, round-robin by category, "no more than N from one series." At small corpus, **caps + MMR** are worth it; DPP/xQuAD are not yet. **ADOPT** MMR + caps now.

**Serendipity/novelty/coverage:** measure novelty (−log popularity), coverage (% catalog surfaced), and serendipity (relevant & unexpected) to detect filter-bubble collapse. **ADOPT LATER** (metrics).

---

### B. TAG MATHEMATICS & VOCABULARY LAYER

**Set-similarity measures.**
- Jaccard |A∩B|/|A∪B|; Dice 2|A∩B|/(|A|+|B|); **overlap/Szymkiewicz-Simpson** |A∩B|/min(|A|,|B|); cosine over binary sets |A∩B|/√(|A||B|); **Tversky** S(A,B)=|A∩B|/(|A∩B|+α|A−B|+β|B−A|).
- **Tversky special cases:** α=β=1 → Jaccard; α=β=0.5 → Dice; α≠β → asymmetric (Tversky, "Features of similarity," Psychological Review 84(4), 1977).
- **Edge for query⊆doc:** with A=query, B=doc, penalize **missing query tags** heavily (large α) and **forgive extra doc tags** (small β→0); as β→0, α=1 this becomes |Q∩D|/|Q| = fraction of query covered — exactly right for subset matching. (Note the argument-order dependence: put the query in the A slot.) This *improves on* the spec's overlap-coefficient primary. **ADOPT** Tversky (asymmetric) for query→doc; keep overlap-coefficient for draft dedup.
- Failure modes: overlap coefficient =1 whenever one set ⊆ other (over-matches tiny sets); Jaccard/Dice deflate when doc has many extra tags.

**IDF variants for tags.**
- Classic idf=ln(N/df); user's idf(t)=ln(1+N/df(t)) is a fine smoothed variant; probabilistic/BM25 idf ln[(N−df+0.5)/(df+0.5)]. Weight rare tags up. Zipf/power-law tag distributions: Halpin, Robu & Shepherd, "The Complex Dynamics of Collaborative Tagging," WWW 2007; Golder & Huberman, "Usage Patterns of Collaborative Tagging Systems," J. Information Science 2006. **ADOPT** user's idf (validated as reasonable).

**Tag co-occurrence & relatedness (allowed — this is NOT embeddings).**
- **PMI** log[P(a,b)/(P(a)P(b))], normalized PMI; **log-likelihood ratio (Dunning 1993)**; chi-square; association-rule lift/confidence/support (Apriori, FP-Growth); **Adamic-Adar**; cosine over sparse **co-occurrence count vectors**.
- **Critical distinction:** sparse count-based co-occurrence similarity is explicitly **allowed** (it's exact set/count math, not learned dense embeddings). The line: allowed = deterministic counts over tags/lexemes; disallowed = learned dense vector representations (word2vec/BERT/pgvector). **ADOPT** PMI/co-occurrence for relatedness.

**Tag hierarchy induction (directly answers the user's worry).**
- **Sanderson & Croft, "Deriving concept hierarchies from text," SIGIR 1999** — subsumption: t₁ subsumes t₂ if P(t₁|t₂) ≥ threshold (≈0.8) and P(t₂|t₁) < 1.
- **Heymann & Garcia-Molina, "Collaborative Creation of Communal Hierarchical Taxonomies in Social Tagging Systems," Stanford tech report 2006** — order tags by graph **centrality** (cosine similarity graph), greedily attach each tag as child of most-similar existing node or root by threshold.
- **Schmitz 2006** — conditional-probability subsumption model. Hierarchical clustering of co-occurrence is an alternative.
- **Storage comparison in Postgres:**
  - *Adjacency list + recursive CTE:* simplest; ancestor/descendant via `WITH RECURSIVE`; fine at small scale; deep queries cost more.
  - *ltree extension:* materialized path, GiST-indexed; **fast subtree/ancestor queries** (`@>`, `<@`, `~` lquery); cheap reads, moderate rebalancing cost on moves. **Best fit for tag subtree expansion at query time.**
  - *Closure table:* stores all ancestor-descendant pairs; O(1) lookups, expensive writes/storage.
  - *Nested sets:* fast reads, very expensive inserts/rebalancing.
- **Verdict:** Because the vocabulary changes rarely and is admin-controlled, and subtree expansion at query time is the hot path, **ADOPT ltree** (or adjacency+recursive CTE if you want zero extensions). Induce candidate hierarchy offline with Heymann/Sanderson-Croft, then **admin curates** — this keeps it manageable as volume grows.

**Query expansion via the tag graph.**
- **FolkRank (Hotho, Jäschke, Schmitz & Stumme, "Information Retrieval in Folksonomies: Search and Ranking," ESWC 2006)** — PageRank-style weight-spreading on the tripartite user-tag-resource graph, with a preference vector to focus around query tags; personalized rankings. Also **spreading activation**, **personalized PageRank / random-walk-with-restart** on the tag co-occurrence graph. Precompute offline (materialized adjacency + iterative update job, or recursive CTE for shallow spread). **ADOPT LATER** (start with 1-hop co-occurrence expansion; graduate to FolkRank).
- **Pseudo-relevance feedback:** Rocchio; RM3 relevance model — expand query with top terms from top-k results, no embeddings. **ADOPT LATER.**

**Tag normalization/dedup.**
- Stemming/lemmatization: Porter/Snowball (Postgres 'english' config uses Snowball).
- String similarity: Levenshtein, Damerau-Levenshtein, Jaro-Winkler, **trigram/Dice on q-grams (pg_trgm)**, Soundex/Metaphone/Double Metaphone (fuzzystrmatch).
- Practical thresholds: pg_trgm similarity() ≥ 0.3 default is loose; for tag canonicalization use ≥ 0.5-0.6; word_similarity() for substring matches. **ADOPT** pg_trgm + levenshtein for canonicalization/snapping (spec already mandates this).

**Controlled-vocabulary maintenance (information science).**
- **SKOS** (W3C); thesaurus standards **ISO 25964 / ANSI-NISO Z39.19** (preferred terms, USE/UF for synonyms, BT/NT/RT for hierarchy/relatedness).
- **What a one-person team should adopt:** preferred-term + alt-label (USE/UF) table (maps directly to your synonym gazetteer) and BT/NT (maps to ltree hierarchy); skip the full standard. Guidance: keep tags-per-document modest (literature suggests ~3-8 focused tags beats many noisy ones); enforce a tag-culling policy (merge/retire low-df tags). **ADOPT** the USE/UF + BT/NT subset.

---

### C. POSTGRES-NATIVE PERFORMANCE EDGE

**RUM index (Postgres Professional, pgxn/rum).** Stores lexeme positions/timestamps in the posting tree → fast `ORDER BY tsvector <=> tsquery` (ranked retrieval) and `ORDER BY timestamp` as index scans; its ranking function combines ts_rank and ts_rank_cd and handles OR queries better. **Trade-off:** slower build/insert and larger index than GIN (write amplification). Maintained, available on Supabase/AlloyDB. **Verdict: ADOPT** for the ranked-lexical hot path if writes are modest (daily publishing = low write rate → RUM is a great fit).

**smlar (Bartunov & Sigaev).** float4 smlar(anyarray,anyarray); `%` operator (similarity > smlar.threshold); modes cosine (default)/**tfidf**/overlap; GiST+GIN index support; tf methods n/log/const; needs a stats table for tfidf (value, ndoc). `tsvector2textarray()` converts tsvector→array. **Maintenance note:** original repo is sigaev.ru; active mirrors (jirutka/smlar) and packaged for Postgres 13+ (meniam/pg_smlar); it's an established but niche extension — verify build against your PG major version. **Verdict: ADOPT** for IDF-weighted tag-set matching with an index (strong edge), *if* you can install extensions; else fall back to intarray + hand-computed IDF.

**BM25 extensions:** pg_search (AGPLv3/commercial, mature), pg_textsearch v1.0 (PostgreSQL license, 2026, faster in TigerData's benchmarks), VectorChord-bm25, **pg_bigm** (2-gram FTS, good for CJK — not needed, English only), **PGroonga** (multilingual FTS, heavier). Verdict: **pg_textsearch** best license/perf fit; **SKIP** pg_bigm/PGroonga (English-only).

**intarray.** Map tag_keys → int ids; GIN on int[] with fast `&&` (overlap) / `@>` (contains). Very fast candidate generation. **roaringbitmap** extension for very fast large set ops. **ADOPT** intarray for the tag_keys candidate-gen path (the spec's `tag_keys && mapped_query_tags`).

**GIN vs GiST vs BRIN.**
- tsvector: **GIN** (default) or **RUM**; GiST only for special cases.
- text[]/int[] tag arrays: **GIN** (gin__int_ops via intarray) for overlap/containment.
- trigram: **gin_trgm_ops** (faster lookups, bigger index) vs **gist_trgm_ops** (supports distance/KNN ordering, smaller); use GIN for filtering, GiST when you need `<->` ordering.
- time-series engagement log: **BRIN** on occurred_at (tiny, perfect for append-only time-ordered partitions) + btree on (user_id, occurred_at) and (blog_id, occurred_at).
- Tune **GIN fastupdate** and **gin_pending_list_limit** on hot queue/log tables; use partial indexes (`WHERE status='pending'`) and covering indexes (INCLUDE) for index-only scans. **ADOPT.**

**Making "ORDER BY score LIMIT 20" fast.** The classic killer is a computed ORDER BY over the whole candidate set. Fixes: precomputed **static-quality/freshness columns**, materialized ranking columns, **two-phase retrieve-then-rerank in one round trip** via CTE + **LATERAL** (candidate-gen with indexable predicate + LIMIT 500, then rerank only those 500), index-only scans, and RUM for the lexical order. **ADOPT** the CTE+LATERAL two-phase pattern (matches the spec's candidate→rerank design).

**Postgres full-text specifics.**
- **websearch_to_tsquery** (user-friendly, quotes/OR/-) vs plainto_tsquery (AND all) vs phraseto_tsquery (order-sensitive). Spec's websearch choice is correct.
- **ts_rank normalization bitmask:** 0=none; 1=÷(1+log doc length); 2=÷doc length; 4=mean harmonic distance (ts_rank_cd only); 8=÷unique words; 16=÷(1+log unique words); 32=÷(rank+1). For length-normalized ranking use 2 or 32 (or combine, e.g., 1|32). Spec's ts_rank_cd without a normalization flag is weak — **add a normalization flag** or move to BM25/RUM.
- **setweight A/B/C/D** (A weight 1.0 default, down to D 0.1): title=A, headings=B, body=C. Generated/stored tsvector column (`GENERATED ALWAYS AS`), custom text search config, **unaccent**, and **thesaurus/synonym dictionaries** for native synonym expansion at index/query time — the primary no-embeddings compensation for paraphrase/synonym recall. **ADOPT** stored weighted tsvector + synonym dictionary now.

**Incremental aggregation.**
- Materialized views + **REFRESH MATERIALIZED VIEW CONCURRENTLY** (needs a unique index); **pg_ivm** for true incremental view maintenance (updates only changed rows via triggers); rollup tables updated by triggers or the outbox worker; **pg_partman** + monthly partitions + BRIN + retention/detach for the engagement log. **ADOPT** pg_ivm or trigger rollups for IDF/quality tables; pg_partman for the log.

**Postgres as a queue done right.**
- **FOR UPDATE SKIP LOCKED** (PG 9.5+): atomic claim-one-and-mark-processing in a single UPDATE…WHERE id IN (SELECT … FOR UPDATE SKIP LOCKED LIMIT n) RETURNING; index `(status, created_at) WHERE status='pending'`. Widely validated (Crunchy Data, Neon).
- **pgmq** extension for a batteries-included queue; **LISTEN/NOTIFY** for low-latency wakeup instead of pure polling (poll as fallback).
- **Transactional outbox** (Chris Richardson, microservices.io): write event in the same tx as the business change; poller relays via SKIP LOCKED — guarantees event iff business row committed. Idempotent consumers + dedup table (consumer offsets/processed-ids); at-least-once is realistic (exactly-once is hard) → make consumers idempotent; dead-letter table for poison messages.
- **Pitfalls:** table bloat + autovacuum tuning on hot queue tables (aggressive autovacuum, fillfactor), avoid long-running transactions (they block vacuum and hold locks), keep claim transactions short. **pg_cron** for the scheduler (due-jobs poll). **ADOPT** SKIP LOCKED + outbox + LISTEN/NOTIFY + pg_cron; consider advisory locks (pg_advisory_xact_lock) only for critical serialized sections.

**Bounded fan-out for a vocabulary change reassigning many blogs (open question).** When one vocabulary change re-tags N blogs and triggers N affinity recomputes: enqueue a **single "vocabulary_changed" job** that (a) writes affected blog_ids into a work table, (b) the worker processes them in **bounded batches** (e.g., 100/tx) via SKIP LOCKED, (c) each affected user's affinity recompute is itself enqueued and **deduplicated** (unique on user_id in a pending set) so a user is recomputed once, not once-per-blog. This caps concurrency and prevents a thundering-herd recompute. **ADOPT.**

**Connection/latency.** **PgBouncer** (transaction pooling), server-side **prepared statements**, **statement_timeout**, realistic **p95 targets: 20-80ms** for candidate-gen+rerank at small corpus, <150-200ms at 10k-100k posts with the two-phase plan.

**Caching without Redis.** **UNLOGGED tables** for ephemeral caches/result caches; materialized result caches; HTTP **ETag/Cache-Control** for anonymous (Audience B) pages; **in-process application caches** for the tag vocabulary and IDF table (refresh on vocabulary-change notify). **ADOPT.**

---

### D. ENGAGEMENT / IMPLICIT FEEDBACK MATH

**Implicit feedback modeling.**
- **Hu, Koren & Volinsky, "Collaborative Filtering for Implicit Feedback Datasets," ICDM 2008 (DOI 10.1109/ICDM.2008.22):** confidence c_ui = 1 + α·r_ui, with α = 40 in their experiments. **Rendle et al. BPR** (UAI 2009) pairwise. What transfers to the weighted-count affinity model: treat stronger signals as higher confidence/weight (the spec's click+1, dwell+2, complete+3, save+5 is a confidence-weighting scheme — sound).

**Dwell time as relevance.**
- Yi, Hong, Zhong, Liu & Rajan (Yahoo), "Beyond Clicks: Dwell Time for Personalization," RecSys 2014 — dwell time normalized by content length is a strong personalization signal. Kim, Hassan, White & Zitouni, "Modeling dwell time to predict click-level satisfaction," WSDM 2014. The "~30 seconds" satisfied-click heuristic and length-normalized dwell are established.
- **Reading speed:** Brysbaert, "How many words do we read per minute? A review and meta-analysis of reading rate," Journal of Memory and Language vol. 109, 2019 — **238 wpm** silent reading of English **non-fiction** (190 studies, 18,573 participants; SD 51.2, 95% CI 230-246; non-fiction range 175-300 wpm). **The spec's 238 wpm is directly validated.** Secondary syntheses of that data place dense technical/academic material near ~100-150 wpm — consider 175-200 wpm for dense AI/ML posts. Expected-read-time = word_count/238 min; valid dwell if actual ≥ some fraction (e.g., 0.5×) of expected.
- Scroll-depth vs dwell vs completion: log all three; completion is the strongest positive. **ADOPT** (validated).

**Time decay.**
- Exponential/half-life: w = 0.5^(Δt/H). User's **half-life ≈45 days**: reasonable for a technical audience whose interests persist; for fast-moving AI topics 30-45 days is defensible, tune with cohort analysis. Ebbinghaus-style forgetting curves motivate exponential.
- **Implement decay WITHOUT rewriting rows:** store the raw signal + its timestamp and **compute decay at read time** relative to a **fixed global epoch**: contribution = weight · 0.5^((now − t)/H), or keep an aggregate in **log-space relative to epoch** to avoid float underflow: store S = Σ wᵢ·0.5^((tᵢ−epoch)/H); at read time multiply by 0.5^((now−epoch)/H). **ADOPT** — this is also the key to convergence (below).

**Proving incremental = full-recompute convergence.**
- Express every contribution relative to a **fixed epoch** (not "now"). Then the affinity aggregate is a **sum of terms each independent of evaluation time**, i.e., a commutative/associative **monoid** (order-independent, idempotent given dedup). Incremental (add each event's epoch-relative term as it arrives) and full recompute (sum all epoch-relative terms) produce **identical** stored S; the read-time global decay factor is applied equally to both. This is why decay MUST be epoch-relative — "decay from now" makes the two paths diverge. Test: property-based test that random event orderings yield the same S. **ADOPT** (this is a named edge).

**Negative signals & feedback loops.**
- Impression −0.1, quick-bounce −0.5 (spec) are modest — good; keep negatives small to avoid punishing exploration.
- **Popularity bias / feedback loops:** Chaney, Stewart & Engelhardt, "How Algorithmic Confounding in Recommendation Systems Increases Homogeneity and Decreases Utility," RecSys 2018; Abdollahpouri et al. on popularity bias. Mitigations: exploration (Thompson/ε), diversity (MMR/caps), **IDF-style down-weighting of popular tags**, and de-biasing quality by impressions (Wilson/Bayesian). **ADOPT** mitigations.

**Affinity vector normalization.**
- L1 share (percent) vs L2 vs softmax vs rank-based; cap weights; top-N pruning (spec keeps top ~50 — reasonable, prunes tail noise).
- Interaction with the reranker's [0,1] requirement: **L1-normalize** the affinity vector so Personalization = Σ_{tags on blog} affinity(u,t) is naturally in [0,1]-ish; then min-max or squash to [0,1]. Rank-based is most robust to outliers. **ADOPT** L1 + squash; top-50 pruning validated.

---

### E. EVALUATION & MEASUREMENT

**Offline metrics.**
- **NDCG@k:** DCG@k = Σ_{i=1}^k (2^{rel_i} − 1)/log₂(i+1); NDCG = DCG/IDCG. **MAP** (mean average precision), **MRR** (mean reciprocal rank), **Recall@k**, **Precision@k**, **ERR** (expected reciprocal rank). For implicit feedback, use clicks/dwell as graded relevance; prefer NDCG (graded) and MRR (first relevant). **ADOPT** NDCG@10 as primary tuning metric.

**Online evaluation at low traffic (major edge).**
- **Team-draft interleaving (Radlinski, Kurup & Joachims, "How does clickthrough data reflect retrieval quality?" CIKM 2008; validated Chapelle, Joachims, Radlinski & Yue, "Large-Scale Validation and Analysis of Interleaved Search Evaluation," ACM TOIS 2012).** Algorithm: for each impression flip a fair coin to decide which ranker "drafts" first; alternately each ranker contributes its top not-yet-included result; record which ranker (team) contributed each shown doc; attribute clicks to the contributing team; the ranker with more click-credit wins (test significance).
- **Sensitivity:** interleaving is roughly **1-2 orders of magnitude (≈10-100×) more data-efficient than A/B testing.** Schuth, Hofmann & Radlinski, "Predicting Search Satisfaction Metrics with Interleaved Comparisons," SIGIR 2015 (from 38 experiments, >3 billion clicks) report "maintaining sensitivity of one to two orders of magnitude above the AB tests"; Radlinski & Craswell, SIGIR 2010 established the factor; Airbnb's Tang et al., "Harnessing the Power of Interleaving and Counterfactual Evaluation for Airbnb Search Ranking" (arXiv 2508.00751, 2025) report "about 50X speedup from A/B" in production. This is the single biggest evaluation edge for a small new site. **ADOPT NOW** — implement by generating two rankings (candidate reranker vs current), interleaving in the app layer, and logging team membership per position.

**Cheap golden set / labels.**
- Build a small relevance-judgement set by hand (sanity-check queries with known-good results); derive labels from click models (cascade/DBN) once you have clicks; regression-test ranking changes against the golden set on every deploy. **ADOPT.**

**Personalization-specific metrics.** Personalized vs non-personalized lift on the same users (A/A-style or interleaved), tag-profile coverage (% of a user's engagement explained by their top-50 tags), cold-start→warm transition time (impressions until profile stabilizes). **ADOPT.**

**Search diagnostics.** Zero-result rate, low-result rate, abandonment, reformulation rate, click-through position distribution. **ADOPT** (cheap, high-value).

---

### F. PIPELINE / DATA ARCHITECTURE

**Markdown ingestion.** Frontmatter parsing (YAML), deterministic slug generation + collision handling (append -2, -3), **content hashing** (sha256 of normalized body) for change detection, store raw .md in **MinIO** (spec) and derived/rendered HTML cached; render-on-publish + cache (not render-on-read) for a daily-cadence blog. **ADOPT** render-on-publish.

**Structure extraction for search.** Parse heading anchors; consider **section-level indexing** for highlight-to-search and reference pins. **Passage retrieval without embeddings:** BM25/tsvector over passages (sliding windows or per-section rows) — changes schema to a sections table (blog_id, section_anchor, tsvector). Worth it once posts are long and users deep-link. **ADOPT LATER** (document-level first; add sections when needed).

**Idempotency & processing.** Event versioning/schema evolution (version column + upcasters), consumer offsets/dedup table (processed_event_id unique), outbox poller with bounded batch sizes and backpressure (limit in-flight), at-least-once + idempotent consumers. Bounded fan-out design: see section C. **ADOPT.**

**Observability.** Structured event logging (JSON logs), trace the search request (candidate count, rerank time, fusion inputs), minimal metric set (p50/p95 latency, zero-result rate, queue depth, outbox lag). **ADOPT.**

---

### G. OVERLAP / DUPLICATE DETECTION

**Near-duplicate without embeddings.**
- **MinHash (Broder 1997/1998)** estimates Jaccard via min-hash signatures; **SimHash (Charikar 2002)** for cosine via Hamming distance of fingerprints; **LSH banding** for scale: P(candidate)=1−(1−s^r)^b.
- **Scaling story:** for a few hundred to few thousand docs, **exact set math is fine** (compute pairwise overlap/Jaccard over tag sets and trigram title sim directly — O(n²) is trivial at n<~5k, and candidate-gen via GIN `&&` prunes most pairs). Introduce MinHash/LSH only past ~tens of thousands. Thresholds: title trigram sim ≥ 0.5, tag overlap-coefficient ≥ 0.7, full-text similarity high → flag.
- **Verdict:** **ADOPT exact** (tag overlap-coefficient primary, Jaccard secondary, IDF-weighted rare tags, ts_rank_cd lexical, pg_trgm title — exactly the spec) now; **ADOPT LATER** MinHash/LSH at scale.

**Calibrated blended risk score.** duplication_risk = w₁·title_trgm + w₂·tag_overlap + w₃·fulltext_sim; calibrate w's and the decision threshold on a **small hand-labelled set** of known dup/non-dup draft pairs (logistic regression or manual grid). **ADOPT.**

---

### H. EMAIL PIPELINE

**Proven patterns.**
- Separate **transactional vs bulk** streams (different IPs/subdomains); idempotency keys; **exponential backoff with jitter** (AWS Architecture Blog, "Exponential Backoff And Jitter" — full jitter: sleep = random(0, min(cap, base·2^attempt))); dead-letter queue; **double opt-in**; **RFC 8058 one-click unsubscribe** (List-Unsubscribe + List-Unsubscribe-Post headers); SPF/DKIM/DMARC alignment; IP/domain warm-up ramps; engagement-based sunsetting; send-time optimization.
- **Google/Yahoo bulk-sender requirements (Feb 2024, enforced through 2025-2026):** for senders >5,000 msgs/day to their users — SPF **and** DKIM, published DMARC (≥ p=none), one-click unsubscribe (RFC 8058, processed within 2 days), **spam-complaint rate < 0.3%** (Gmail "Email sender guidelines": keep spam rates in Postmaster Tools below 0.3%; rates ≥0.3% trigger graduated enforcement, and Google advises acting once rates reach 0.1%), valid PTR/forward-confirmed DNS, TLS, RFC 5322 formatting, From-domain alignment. Enforcement escalated to permanent rejections from November 2025; Microsoft added parallel rules (May 2025). **Confirmed current as of 2026.** **ADOPT** all.

**Segmentation as JSONB boolean rule tree.** Store rule tree in JSONB; **safely compile to parameterized SQL** (whitelist of allowed fields/operators, bind all values as parameters — never string-concatenate → prevents injection); index precomputed rolling activity aggregates (last_30d_opens etc.). **ADOPT** (compile with a strict allowlist).

**LLM email content grounding (2nd allowed LLM use).** JSON-schema constrained output; **link-equality checks** (every URL in output must exist in the allowed source set); prompt-injection defence when source is user/author content (treat content as data, delimit, instruction-guard, validate output); deterministic template fallback when validation fails. **ADOPT.**

---

## Recommendations (staged)

**Stage 0 — foundation (build now):**
1. Candidate gen via GIN (tsvector + intarray tag_keys), LIMIT 500, two-phase **CTE + LATERAL** rerank.
2. Replace weighted-sum with **RRF fusion** of lexical/tag/personalization/freshness-quality lists (k=60); keep linear model as interpretable secondary.
3. **Tversky (asymmetric)** for query→doc tag match; keep overlap-coefficient for dedup.
4. Weighted stored tsvector (setweight A/B/C) + **synonym/thesaurus dictionary** + unaccent.
5. Quality = Bayesian-smoothed rate (keep) + optional **Wilson lower bound**; Freshness power-law (keep, tune half-life 3-7d).
6. Affinity: epoch-relative exponential decay (H=45d), L1-normalize, top-50 prune; **prove convergence** via epoch-relative monoid + property tests.
7. Cold start: deterministic profile (dictionary+trgm snap of declared tags + YAKE on bio + BM25-over-tag-descriptions) with **Beta-Binomial priors** (pseudo-count m≈5-20 decaying); async enqueue heavy work; serve Audience-B page instantly.
8. **DPDP/GDPR-compliant** consented progressive profiling; **drop OSINT**; separate consent for lead-gen; editable "your interests" panel.
9. Postgres queue: **SKIP LOCKED + outbox + LISTEN/NOTIFY + pg_cron**; bounded fan-out for vocabulary changes.
10. Email: RFC 8058 one-click unsubscribe, SPF/DKIM/DMARC, <0.3% complaint rate, exponential backoff w/ jitter, JSONB→parameterized-SQL segmentation.
11. **Log now for the future:** presented ranking + positions, clicks, dwell, propensity-enabling data; add small randomization.

**Stage 1 — once you have traffic/corpus (hundreds→thousands):**
12. **Team-draft interleaving** for every ranking change (10-100× A/B sensitivity).
13. **RUM index** for ranked lexical retrieval; add **smlar TF-IDF** for tag-set matching.
14. Thompson-sampling exploration slots (bounded, never top-3).
15. Tag hierarchy via **ltree**, induced offline (Heymann/Sanderson-Croft) + admin curation; 1-hop co-occurrence (PMI) query expansion.
16. Optional **third gated LLM use** (bio→allowed tags) with full non-LLM fallback.
17. pg_ivm/trigger rollups for IDF/quality; pg_partman for engagement log.

**Stage 2 — at scale (10k+ posts / real click volume):**
18. True BM25 via **pg_textsearch** (PostgreSQL-licensed) or pg_search.
19. **FolkRank / personalized PageRank** query expansion.
20. **Counterfactual LTR (IPS, Joachims 2017)** → LambdaMART, using the data you've been logging.
21. Passage/section-level indexing; MinHash/LSH dedup.

**Benchmarks that change the plan:** p95 search latency > 200ms → adopt RUM/materialized ranking sooner; zero-result rate > ~10% → prioritize synonym dictionary + query expansion; corpus > ~5k posts → BM25 extension; click volume enough for significant NDCG deltas → graduate to LTR; complaint rate approaching 0.3% → tighten opt-in/sunsetting.

## Caveats
- **"No embeddings" has a real quality cost** on semantic/paraphrase/synonym queries and on relating tags that never co-occur — lexical/set methods can't bridge vocabulary gaps they've never seen together. Quantify: expect lower recall on tail/paraphrase queries vs a dense retriever; best compensations (synonym dictionaries, PMI/FolkRank co-occurrence expansion, BM25) recover much but not all. **If the constraint were ever lifted:** a single pgvector column for a re-ranking or recall-boost stage, fused via the same RRF you already run, would be the minimal-change upgrade — nothing else in the design would change.
- **Corpus cold-start dominates early:** with tens-hundreds of posts, IDF and co-occurrence statistics are noisy; lean on Bayesian smoothing, priors, and diversity caps, and don't over-tune weights until you have data.
- **Parameter values** (0.35/0.25/0.20/0.10/0.10, ε=0.1, λ=0.7, LIMIT 500, top-50) are reasonable defaults but are *unvalidated for this corpus* — treat them as starting points and tune via interleaving + offline NDCG. 238 wpm and half-life 45d are the best-supported (238 wpm directly validated by Brysbaert 2019; α=40 confidence weight from Hu-Koren-Volinsky 2008).
- **Extension availability risk:** smlar, RUM, pg_search/pg_textsearch, pg_ivm, pgmq require install rights; on managed Postgres verify availability (Supabase/AlloyDB/Neon support varies). All-native fallbacks exist for each (intarray+manual IDF; GIN; hand-rolled BM25; trigger rollups; SKIP LOCKED table).
- **Legal:** DPDP core obligations phase in toward ~May 2027; design for compliance now. Third-party "OSINT" enrichment is the highest-risk element and is recommended against.
- Some cited figures (interleaving 10-100× / Airbnb ~50× sensitivity; technical-reading wpm) come partly from secondary/industry sources; the core papers (Radlinski 2008, Schuth 2015, Chapelle 2012, Li 2010, Brysbaert 2019, Hu-Koren-Volinsky 2008) are primary and verified.