---
title: "Keyset Pagination, and Why OFFSET Drifts"
slug: "keyset-pagination"
summary: "On an append-heavy table, page two is not what it was a second ago. Cursors fix that and get faster as they go deeper."
categories: ["engineering", "infrastructure"]
series: "foundations"
series_position: 2
---
On an append-heavy table, page two is not what it was a second ago.

## The drift

`OFFSET 20` means "skip the first twenty rows of the result *as it is now*".
Publish an article between the two requests and every row shifts down by one:
the reader sees the last item of page one again at the top of page two, and
never sees the item that got pushed across the boundary.

It is not a race condition in the usual sense. Nothing is corrupted. The reader
simply gets a slightly wrong list, quietly, and only on a busy table.

## Cursors

A keyset cursor encodes the sort key of the last row you saw, and the next
query asks for rows strictly after it:

```sql
SELECT id, slug, title, published_at
FROM blogs
WHERE status = 'published'
  AND (published_at, id) < (:last_published_at, :last_id)
ORDER BY published_at DESC, id DESC
LIMIT :limit;
```

The tuple comparison is doing the real work. Sorting on `published_at` alone
is ambiguous when two articles share a timestamp, and the id breaks the tie
deterministically.

### It gets faster, not slower

`OFFSET 10000` makes the database produce ten thousand rows and throw them
away. The keyset query seeks straight into the index and reads the page. Deep
pagination costs the same as shallow pagination.

## What you give up

Page numbers. There is no "jump to page 7", and no total count without a second
query. For a feed nobody was going to page 7 of, that is not a loss — and the
API is honest about it: the response is `{items, next_cursor, has_more}`, with
no `total` to tempt anyone.
