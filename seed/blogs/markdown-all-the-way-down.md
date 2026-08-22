---
title: "Markdown All the Way Down"
slug: "markdown-all-the-way-down"
summary: "Storing the source and never a rendered copy keeps one representation honest and the ETag meaningful."
categories: ["engineering", "open-source"]
---
Canerly stores the Markdown source and never a rendered copy. Not as a
purity exercise — it removes a class of bug that is otherwise permanent.

## Two representations, one of them wrong

The moment you cache rendered HTML alongside the source, you own a
synchronisation problem. Change the renderer and every cached copy is stale.
Fix a sanitiser bug and the vulnerable HTML is still sitting in the cache.

There is no version of this that stays correct without a re-render pass you
have to remember to run.

## What the hash buys

The body hashes to a `content_sha256` at publish time. That hash is the ETag,
so a conditional request is answered without touching the object store:

```http
GET /api/v1/blogs/markdown-all-the-way-down/content
If-None-Match: "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"

304 Not Modified
```

It is a *strong* ETag, and it can be, because it is a hash of the exact bytes
served rather than a timestamp that approximates them.

### Headings are the exception

Section anchors are stored in the database, not derived at render time. They
have to be: reading positions and cross-references point at them through a
foreign key, so an anchor that changed because the renderer changed would break
a reference that was valid yesterday.

## The one cost

Rendering happens per request. It is a few milliseconds for an article of this
size, and it buys a system where the source is the only thing that can be
wrong.
