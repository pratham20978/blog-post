---
title: "Errors Are a Contract"
slug: "errors-are-a-contract"
summary: "A closed set of error categories, each mapped to one status, turns failure handling from guesswork into a lookup."
categories: ["engineering"]
series: "foundations"
series_position: 3
---
Failure handling goes wrong in a predictable way: every call site invents its
own interpretation of what went wrong, and the interpretations disagree.

## A closed set

Canerly's API has one error shape and a closed enumeration of categories. Every
category maps to exactly one HTTP status, in one table, and nothing else in the
system decides a status.

```python
HTTP_STATUS_BY_ERROR_CATEGORY: Final[Mapping[ErrorCategory, int]] = {
    ErrorCategory.BLOG_NOT_FOUND: 404,
    ErrorCategory.VALIDATION_FAILED: 400,
    ErrorCategory.AUTH_REQUIRED: 401,
    ErrorCategory.RATE_LIMITED: 429,
}
```

## Why the client branches on category

Status codes are too coarse to act on. A 400 could be a malformed body, a
rejected field, or a request that is well-formed but not allowed yet — and the
right response differs in each case.

| Category | What the UI does |
| --- | --- |
| `BLOG_NOT_FOUND` | Render the not-found screen |
| `VALIDATION_FAILED` | Attach messages to the named fields |
| `AUTH_REQUIRED` | Prompt to sign in, preserving the return path |
| `RATE_LIMITED` | Count down, disable submit |

### Validation is 400, not 422

422 is reserved for the semantically impossible — a request that parsed, made
sense, and still cannot be honoured. A rejected field is not that. Keeping the
two apart means a 422 in the logs is always worth reading.

## What it costs

One thing: the enumeration can only grow, and removing a member is a breaking
change. That has been worth it every time.
