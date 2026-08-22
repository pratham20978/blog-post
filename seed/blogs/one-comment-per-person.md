---
title: "One Comment Per Person"
slug: "one-comment-per-person"
summary: "Making a rule unrepresentable in the schema beats checking it in the service."
categories: ["product", "engineering"]
---
The rule was simple: one top-level comment per person per article. Replies are
unlimited; the opening statement is not.

## Checking it in the service

The first implementation did what you would expect — read, decide, write:

```python
existing = await repo.find_root_comment(blog_id, author_id)
if existing is not None:
    raise BlogPlatformError(ErrorCategory.COMMENT_ALREADY_EXISTS)
await repo.insert(comment)
```

This is wrong under concurrency, and it is wrong in the boring way: two
requests both read "no existing comment" before either writes.

## Making it unrepresentable

The database can express the rule directly, as a partial unique index over
root comments only:

```sql
CREATE UNIQUE INDEX one_root_comment_per_author
    ON comments (blog_id, author_id)
 WHERE parent_id IS NULL
   AND deleted_at IS NULL;
```

The service now attempts the insert and translates a unique violation into the
same error category it used to raise by hand. The check did not move — it
stopped being a check.

## The general shape

If a rule is invariant, put it where invariants live. A constraint in the
schema is enforced against every writer, including the migration you run at
2am and the script nobody remembered was still in cron.
