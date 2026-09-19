# Frontmatter

The YAML block at the top of `blog.md`. It is the machine-readable half of the post and drives tags, search, cards, and the meta description.

---

## Schema

```yaml
---
title: "Why TCP Slows Down on Wifi"
slug: tcp-slows-down-on-wifi
date: 2026-09-08
updated: 2026-09-08
summary: "TCP reads packet loss as congestion. On wireless links most loss is corruption, so the sender backs off when the network was never full."
tags: [networking, tcp, congestion-control, wireless, transport-layer]
category: networking
tier: L2
difficulty: intermediate
prerequisites: ["TCP basics", "packet switching"]
reading_minutes: 12
cover_image: "COVER"
canonical_url: "https://canery.in/blogs/tcp-slows-down-on-wifi"
---
```

---

## Fields

| Field | Rule |
|---|---|
| `title` | Under 60 characters. Primary keyword near the front. A claim or a question, not a topic label. |
| `slug` | Lowercase, hyphenated, stable. Never change it after publish; the URL depends on it. |
| `date` | First publish date. |
| `updated` | Bump on every edit, including expansions. |
| `summary` | 150–160 characters. Reused as the meta description. Usually the first sentence of Insights, tightened. |
| `tags` | 4–7. Lowercase, hyphenated. See below. |
| `category` | One engineering domain. The top-level organisation of the blog. |
| `tier` | L1–L4. Lets you find posts that are due for expansion. |
| `difficulty` | `beginner`, `intermediate`, or `advanced`. |
| `prerequisites` | What the reader needs first. Drives the "who this is for" line. |
| `reading_minutes` | Words ÷ 220, rounded. |
| `cover_image` | Placeholder until upload, then the object-storage URL. |
| `canonical_url` | The post's home URL. |

---

## Categories

One per post. Keep this list short and stable, because it is the site's top-level navigation.

```
algorithms · data-structures · networking · operating-systems · databases ·
distributed-systems · machine-learning · computer-architecture · compilers ·
security · theory · software-engineering
```

If a topic seems to need a new category, it usually belongs in an existing one. Add a category only when there are at least five posts that would sit in it.

---

## Tags

Tags are how the platform retrieves and personalises. Their consistency matters more than their cleverness.

Rules:
- 4 to 7 per post.
- Lowercase, hyphenated, singular where natural: `hash-table` not `Hash Tables`.
- Reuse an existing tag over inventing a near-duplicate. `tcp` and `tcp-protocol` as separate tags is a bug.
- Mix levels: one or two broad (`networking`), two or three specific (`congestion-control`), one or two crosscutting (`performance`, `debugging`).
- No tags for things the post merely mentions. A tag is a promise that the post teaches that thing.

The first tag should be the category, so tag-only queries still land in the right domain.

---

## Title patterns

| Pattern | Example |
|---|---|
| The claim | "Hash Tables Are Slower Than You Think on Delete" |
| The question | "Why Does Postgres Ignore My Index?" |
| By hand | "Backpropagation by Hand" |
| The visual guide | "A Visual Guide to Consistent Hashing" |
| The mechanism | "How TCP Decides When to Slow Down" |

Avoid: "Understanding X", "Introduction to X", "A Deep Dive into X". They are accurate and they promise nothing.
