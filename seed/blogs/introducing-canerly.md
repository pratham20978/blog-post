---
title: "Introducing Canerly"
slug: "introducing-canerly"
summary: "A publishing platform where the article is a Markdown file, the reader has an identity before an account, and every failure has a name."
categories: ["product", "engineering"]
---
Canerly is a place to publish long-form writing, built on one decision that
everything else follows from: the article *is* a Markdown file. Not a row with
a Markdown column, not a document that was Markdown before an editor got to it.
The file is the source of truth, and every other thing the platform knows is
derived from it.

## What Canerly is

A writer commits a Markdown file. The publish pipeline parses it, extracts the
headings, counts the words, hashes the body, and stores the bytes unchanged in
object storage. The database holds what you need to *find* an article. The
object store holds the article.

That split is the whole design. It means the rendered page can always be thrown
away and rebuilt, and it means there is exactly one representation to keep
honest.

## The three decisions

Most of what is interesting about the platform comes from three choices made
early, each of which closed off a category of bug rather than solving one.

| Decision | What it buys |
| --- | --- |
| Markdown is the only stored form | One representation, a meaningful ETag |
| Readers have an identity before an account | History that survives signup |
| Errors are a closed set | Failure handling becomes a lookup |

### Markdown is the only representation

There is no rendered copy in the database, and no cached HTML that can fall out
of step with the source. The body hashes to a `content_sha256`, which becomes
the ETag, so a conditional request is answered without reading the object at
all:

```python
class ContractModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_assignment=True,
    )
```

> Storing a second representation is storing a second thing that can be wrong.

Headings are the one exception, and they are stored *alongside* the body rather
than derived from it at read time — because reading positions and cross-article
references point at anchors, and those anchors have to survive a re-render.
[Markdown all the way down](/blogs/markdown-all-the-way-down) covers why.

## What is not built yet

Being honest about the edges is cheaper than discovering them later:

1. Email delivery. Codes are generated, but nothing sends them yet.
2. Full-text search. The index exists; the query path does not.
3. Tags. The vocabulary is not settled, and a field stored under a definition
   nobody agreed on looks authoritative to whoever finds it next.

None of these are hard. They are simply not done, and the platform says so
rather than pretending otherwise.
