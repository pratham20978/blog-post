import type { BlogContent, BlogDetail, BlogSection, BlogSummary } from "@/shared/contracts";

const AUTHOR = "0198f0e2-3b7a-7c31-9f52-0000000000aa";

function id(n: number): string {
  return `0198f0e2-3b7a-7c31-9f52-1000000000${n.toString().padStart(2, "0")}`;
}

/**
 * The feed, newest first — the order the backend's `blogs_feed` index returns.
 *
 * Deliberately mixed: some articles belong to a series and some do not, one
 * series has nothing published (so it derives as "upcoming"), and titles vary
 * in length so the card layouts are exercised rather than flattered.
 */
export const blogSummaries: readonly BlogSummary[] = [
  {
    id: id(9),
    slug: "scaling-how-we-build-and-test",
    title: "Scaling How We Build and Test Our Most Advanced Systems",
    summary:
      "Reliability, security and user protections matter more the larger a system gets. What we changed in how we ship.",
    status: "published",
    series_id: null,
    series_position: null,
    category_keys: ["engineering", "research"],
    word_count: 1904,
    reading_minutes: 8,
    published_at: "2026-08-18T09:00:00Z",
    updated_at: "2026-08-18T09:00:00Z",
  },
  {
    id: id(8),
    slug: "retrieval-without-embeddings",
    title: "Retrieval Without Embeddings",
    summary:
      "Full-text search, trigram matching and a linear reranker get you further than the vector-first reflex suggests.",
    status: "published",
    series_id: "0198f0e2-3b7a-7c31-9f52-000000000002",
    series_position: 2,
    category_keys: ["research", "engineering"],
    word_count: 2380,
    reading_minutes: 10,
    published_at: "2026-08-11T09:00:00Z",
    updated_at: "2026-08-12T14:20:00Z",
  },
  {
    id: id(7),
    slug: "the-cost-of-a-vector-database",
    title: "The Cost of a Vector Database",
    summary: "What you actually pay for, and when it is worth paying.",
    status: "published",
    series_id: "0198f0e2-3b7a-7c31-9f52-000000000002",
    series_position: 1,
    category_keys: ["infrastructure"],
    word_count: 1428,
    reading_minutes: 6,
    published_at: "2026-08-04T09:00:00Z",
    updated_at: "2026-08-04T09:00:00Z",
  },
  {
    id: id(6),
    slug: "errors-are-a-contract",
    title: "Errors Are a Contract",
    summary:
      "A closed set of error categories, each mapped to one status, turns failure handling from guesswork into a lookup.",
    status: "published",
    series_id: "0198f0e2-3b7a-7c31-9f52-000000000001",
    series_position: 3,
    category_keys: ["engineering"],
    word_count: 1666,
    reading_minutes: 7,
    published_at: "2026-07-28T09:00:00Z",
    updated_at: "2026-07-28T09:00:00Z",
  },
  {
    id: id(5),
    slug: "keyset-pagination",
    title: "Keyset Pagination, and Why OFFSET Drifts",
    summary:
      "On an append-heavy table, page two is not what it was a second ago. Cursors fix that and get faster as they go deeper.",
    status: "published",
    series_id: "0198f0e2-3b7a-7c31-9f52-000000000001",
    series_position: 2,
    category_keys: ["engineering", "infrastructure"],
    word_count: 1190,
    reading_minutes: 5,
    published_at: "2026-07-21T09:00:00Z",
    updated_at: "2026-07-21T09:00:00Z",
  },
  {
    id: id(4),
    slug: "identity-before-the-account",
    title: "Identity Before the Account",
    summary:
      "Giving every visitor a server-issued actor id means reading history exists before signup — and survives it.",
    status: "published",
    series_id: "0198f0e2-3b7a-7c31-9f52-000000000001",
    series_position: 1,
    category_keys: ["engineering", "product"],
    word_count: 2142,
    reading_minutes: 9,
    published_at: "2026-07-14T09:00:00Z",
    updated_at: "2026-07-15T11:00:00Z",
  },
  {
    id: id(3),
    slug: "one-comment-per-person",
    title: "One Comment Per Person",
    summary: "Making a rule unrepresentable in the schema beats checking it in the service.",
    status: "published",
    series_id: null,
    series_position: null,
    category_keys: ["product", "engineering"],
    word_count: 952,
    reading_minutes: 4,
    published_at: "2026-07-07T09:00:00Z",
    updated_at: "2026-07-07T09:00:00Z",
  },
  {
    id: id(2),
    slug: "markdown-all-the-way-down",
    title: "Markdown All the Way Down",
    summary:
      "Storing the source and never a rendered copy keeps one representation honest and the ETag meaningful.",
    status: "published",
    series_id: null,
    series_position: null,
    category_keys: ["engineering", "open-source"],
    word_count: 1309,
    reading_minutes: 6,
    published_at: "2026-06-30T09:00:00Z",
    updated_at: "2026-06-30T09:00:00Z",
  },
];

const SECTIONS: readonly BlogSection[] = [
  { anchor: "the-problem", ordinal: 0, level: 2, title: "The problem", char_start: 0, char_end: 620 },
  {
    anchor: "what-we-changed",
    ordinal: 1,
    level: 2,
    title: "What we changed",
    char_start: 620,
    char_end: 1480,
  },
  {
    anchor: "measuring-it",
    ordinal: 2,
    level: 3,
    title: "Measuring it",
    char_start: 1480,
    char_end: 2010,
  },
  {
    anchor: "what-we-would-do-differently",
    ordinal: 3,
    level: 2,
    title: "What we would do differently",
    char_start: 2010,
    char_end: 2740,
  },
];

/** Detail for the lead article, used by the article-page fixtures. */
export const blogDetail: BlogDetail = {
  id: id(9),
  slug: "scaling-how-we-build-and-test",
  title: "Scaling How We Build and Test Our Most Advanced Systems",
  summary:
    "Reliability, security and user protections matter more the larger a system gets. What we changed in how we ship.",
  status: "published",
  author_id: AUTHOR,
  series_id: null,
  series_position: null,
  category_keys: ["engineering", "research"],
  sections: SECTIONS,
  // An internal object-store URI. Not browser-fetchable — the body comes from
  // the content route. Present here because the real contract has it.
  markdown_uri:
    "s3://blogs/blogs/0198f0e2-3b7a-7c31-9f52-100000000009/9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08.md",
  content_sha256: "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
  word_count: 1904,
  reading_minutes: 8,
  published_at: "2026-08-18T09:00:00Z",
  created_at: "2026-08-15T10:30:00Z",
  updated_at: "2026-08-18T09:00:00Z",
};

/**
 * A body with frontmatter already stripped, as the publish pipeline stores it,
 * and with no leading image — so the typographic cover path is what renders by
 * default. Exercises headings, lists, a quote, a table, code and inline links.
 */
export const blogContent: BlogContent = {
  blog_id: blogDetail.id,
  slug: blogDetail.slug,
  content_sha256: blogDetail.content_sha256,
  markdown: `A system that ships once a quarter and a system that ships hourly fail in
different ways. The first fails loudly and rarely. The second fails quietly and
often, and the difference is entirely in what you built to notice.

## The problem

For most of the last two years our release process was a checklist. It worked,
in the sense that nothing catastrophic reached production. It also meant that
the slowest step in shipping a change was waiting for a person to read.

Three things made the checklist untenable:

- **Volume.** Changes per week roughly tripled while the review capacity did not.
- **Surface.** Each change touched more of the system than it used to.
- **Coupling.** A change that looked local frequently was not.

> Reliability, security, and user protections are more important than ever —
> and they are properties of the process, not of any individual review.

## What we changed

We stopped treating verification as a stage and started treating it as a
property of the artifact. Concretely, every change now carries the evidence
that it is safe to deploy, and the pipeline refuses anything that does not.

| Stage | Before | After |
| --- | --- | --- |
| Contract check | Manual review | Generated from the schema |
| Load profile | Sampled weekly | Per-change, against last week's traffic |
| Rollback plan | Written if asked | Required, and exercised |

The contract check is the one that mattered most. Our API contracts forbid
unknown fields, which means a renamed field is an error at the boundary rather
than a default silently read three services downstream:

\`\`\`python
class ContractModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_assignment=True,
    )
\`\`\`

### Measuring it

The metric we chose was not deploy frequency. It was the time between a change
being wrong and somebody knowing — which turned out to be the only number that
moved anything else. See [keyset pagination](/blogs/keyset-pagination) for a
related case where the measurement changed the design.

1. Instrument the failure, not the success.
2. Give the signal a home before you need it.
3. Delete the dashboard nobody opened.

## What we would do differently

We would build the rollback exercise first. It was the last piece we added and
the one that made the rest trustworthy — every earlier guarantee was a claim
about what would happen, and this was the only one we had actually seen.

We would also resist the urge to make the pipeline clever. Each conditional we
added to skip a slow check eventually cost more in debugging than the check had
ever cost in time.
`,
};

/** Content for a second article, whose body opens with an image — this is the
 *  case that exercises the derived-cover path. */
export const blogContentWithImage: BlogContent = {
  blog_id: id(8),
  slug: "retrieval-without-embeddings",
  content_sha256: "3b1a2f4e5d6c7b8a9f0e1d2c3b4a5968778695a4b3c2d1e0f9a8b7c6d5e4f3a2",
  markdown: `![A ranking pipeline: query understanding, candidate generation, linear rerank](/media/retrieval-pipeline.png)

Reaching for a vector database is the default move, and for a corpus of a few
thousand documents it is usually the wrong one.

## The problem

Embeddings buy you conceptual matching. They cost you an index to maintain, a
model to version, and a retrieval path nobody on the team can debug by reading
it.
`,
};

export const blogContents: Readonly<Record<string, BlogContent>> = {
  [blogContent.slug]: blogContent,
  [blogContentWithImage.slug]: blogContentWithImage,
};

/** Build a plausible `BlogDetail` for any summary, for screens that need one. */
export function detailFor(summary: BlogSummary): BlogDetail {
  if (summary.slug === blogDetail.slug) return blogDetail;

  return {
    ...summary,
    author_id: AUTHOR,
    sections: SECTIONS,
    markdown_uri: `s3://blogs/blogs/${summary.id}/${"0".repeat(64)}.md`,
    content_sha256: "0".repeat(64),
    created_at: summary.published_at ?? summary.updated_at,
  };
}
