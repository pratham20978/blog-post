---
title: "Retrieval Without Embeddings"
slug: "retrieval-without-embeddings"
summary: "Full-text search, trigram matching and a linear reranker get you further than the vector-first reflex suggests."
categories: ["research", "engineering"]
series: "retrieval"
series_position: 2
---
![A ranking pipeline: query understanding, candidate generation, linear rerank](/media/retrieval-pipeline.png)

Reaching for a vector database is the default move, and for a corpus of a few
thousand documents it is usually the wrong one.

## The problem

Embeddings buy you conceptual matching. They cost you an index to maintain, a
model to version, and a retrieval path nobody on the team can debug by reading
it. For Canerly's own archive — a few hundred articles — that trade is plainly
bad.

## What we used instead

Three stages, each of which a person can inspect:

1. **Query understanding.** Normalise, drop stop words, keep the rare terms.
2. **Candidate generation.** Full-text match, unioned with trigram similarity
   so a typo still finds the article.
3. **Rerank.** A linear model over six features. All six are readable.

The reranker is the part people expect to be complicated. It is not:

```sql
SELECT id,
       ts_rank(search_vector, query) * 2.0
     + similarity(title, :q)         * 1.5
     + recency_decay(published_at)   * 0.5 AS score
FROM blogs, plainto_tsquery('english', :q) query
WHERE search_vector @@ query
ORDER BY score DESC
LIMIT 20;
```

## When embeddings do win

At a corpus size where lexical recall genuinely falls apart, or when the
queries and the documents share no vocabulary — support tickets against
engineering docs, say. Neither is true here.

The honest summary: start lexical, measure the misses, and add the vector path
when you can name the queries it would fix.
