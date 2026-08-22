---
title: "The Cost of a Vector Database"
slug: "the-cost-of-a-vector-database"
summary: "What you actually pay for, and when it is worth paying."
categories: ["infrastructure"]
series: "retrieval"
series_position: 1
---
A vector database is not expensive because of what it charges. It is expensive
because of what it obliges you to keep doing.

## What you actually pay for

The invoice is the small part. The real costs are:

- **A model version.** Re-embedding a corpus is a migration, and it is one you
  cannot do incrementally without keeping both models alive.
- **An index to keep warm.** Recall degrades quietly as the index drifts.
- **A second source of truth.** Now the article exists in two places, and one
  of them is a lossy projection of the other.

## When it is worth paying

When conceptual recall is the product rather than a nicety. Semantic search
over a large, messy, vocabulary-mismatched corpus is a real problem and vectors
are a real answer to it.

For an archive you can list on one page, the answer is [full-text and a linear
reranker](/blogs/retrieval-without-embeddings).

## The rule we settled on

> Add the index when you can name three queries it fixes that the current path
> gets wrong.

Not "when the corpus grows", not "when search feels slow" — three named
queries. It is a low bar and it has still not been met here.
