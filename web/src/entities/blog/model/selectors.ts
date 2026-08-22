import type { BlogSummary, Series } from "@/shared/contracts";

/**
 * The discovery rails on the feed.
 *
 * None of these are backend concepts. Trending exists server-side but only
 * behind the secret admin prefix, and `Series` carries no status or dates — so
 * "blog of the day", "trending", "current series" and "upcoming series" are
 * all derived here from published data.
 *
 * They live alone in this file, pure and tested, for one reason: when a public
 * `/trending` endpoint lands, replacing a derivation with a real signal should
 * touch this file and nothing else.
 */

export interface FeedSections {
  /** The lead article. Null only when nothing is published at all. */
  readonly featured: BlogSummary | null;
  /** Beneath the lead — the next most recent, excluding it. */
  readonly trending: readonly BlogSummary[];
  /** The series the newest article belongs to, with its blogs in order. */
  readonly currentSeries: SeriesWithBlogs | null;
  /** Series that exist but have published nothing yet. */
  readonly upcomingSeries: readonly Series[];
  /** Everything, newest first — the paginated body of the page. */
  readonly all: readonly BlogSummary[];
}

export interface SeriesWithBlogs {
  readonly series: Series;
  readonly blogs: readonly BlogSummary[];
}

const TRENDING_COUNT = 3;

/**
 * Sort newest-first.
 *
 * The feed already arrives in `published_at DESC, id DESC` order, but the
 * selectors must not depend on that: they also run over the merged pages of an
 * infinite query, and over filtered subsets. Articles with no `published_at`
 * sort last — the feed only serves published articles, so that is a defensive
 * case rather than an expected one.
 */
export function byNewest(blogs: readonly BlogSummary[]): readonly BlogSummary[] {
  return [...blogs].sort((a, b) => {
    if (!a.published_at) return 1;
    if (!b.published_at) return -1;
    const delta = b.published_at.localeCompare(a.published_at);
    // Tie-break on id so the order is total and stable. Two articles published
    // in the same second would otherwise swap places between renders.
    return delta !== 0 ? delta : b.id.localeCompare(a.id);
  });
}

/** Blogs of one series, in reading order. */
export function seriesBlogs(
  blogs: readonly BlogSummary[],
  seriesId: string,
): readonly BlogSummary[] {
  return blogs
    .filter((blog) => blog.series_id === seriesId)
    .sort((a, b) => (a.series_position ?? 0) - (b.series_position ?? 0));
}

/**
 * Build every rail from one pass over the feed.
 *
 * The rules, stated plainly so they can be argued with:
 *
 *   featured        the most recently published article
 *   trending        the next three, by recency — a stand-in for real
 *                     engagement signal, which is not public
 *   currentSeries   the series the featured article belongs to; failing that,
 *                     the series owning the most recent article that has one.
 *                     "Current" means most recently added to.
 *   upcomingSeries  series with no published article yet — announced but not
 *                     started
 */
export function deriveFeedSections(
  blogs: readonly BlogSummary[],
  series: readonly Series[],
): FeedSections {
  const ordered = byNewest(blogs);
  const [featured = null, ...rest] = ordered;

  const seriesById = new Map(series.map((entry) => [entry.id, entry]));

  // The newest article that belongs to a series — which may not be the
  // featured one, since the lead article often stands alone.
  const anchor = ordered.find((blog) => blog.series_id && seriesById.has(blog.series_id));
  const anchorSeries = anchor?.series_id ? seriesById.get(anchor.series_id) : undefined;

  const currentSeries: SeriesWithBlogs | null = anchorSeries
    ? { series: anchorSeries, blogs: seriesBlogs(ordered, anchorSeries.id) }
    : null;

  const startedSeriesIds = new Set(
    ordered.map((blog) => blog.series_id).filter((id): id is string => Boolean(id)),
  );

  return {
    featured,
    trending: rest.slice(0, TRENDING_COUNT),
    currentSeries,
    upcomingSeries: series.filter((entry) => !startedSeriesIds.has(entry.id)),
    all: ordered,
  };
}

/** How many published articles each series has — for the series index. */
export function seriesBlogCounts(
  blogs: readonly BlogSummary[],
): ReadonlyMap<string, number> {
  const counts = new Map<string, number>();
  for (const blog of blogs) {
    if (!blog.series_id) continue;
    counts.set(blog.series_id, (counts.get(blog.series_id) ?? 0) + 1);
  }
  return counts;
}

/**
 * The neighbours of an article within its series, for "next in series".
 * Ordered by `series_position`, so it follows the author's reading order
 * rather than publication order.
 */
export function seriesNeighbours(
  blogs: readonly BlogSummary[],
  current: Pick<BlogSummary, "id" | "series_id">,
): { previous: BlogSummary | null; next: BlogSummary | null } {
  if (!current.series_id) return { previous: null, next: null };

  const ordered = seriesBlogs(blogs, current.series_id);
  const index = ordered.findIndex((blog) => blog.id === current.id);
  if (index === -1) return { previous: null, next: null };

  return {
    previous: ordered[index - 1] ?? null,
    next: ordered[index + 1] ?? null,
  };
}
