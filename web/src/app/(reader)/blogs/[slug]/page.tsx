import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import {
  fetchBlog,
  fetchCategories,
  fetchContent,
  fetchFeed,
  fetchSeries,
} from "@/entities/blog/api/server";
import { seriesNeighbours } from "@/entities/blog/model/selectors";
import { BlogCover } from "@/entities/blog/ui/BlogCover";
import { extractCover } from "@/shared/lib/cover";
import { formatDate, formatReadingTime, toDateAttribute } from "@/shared/lib/date";
import { Article } from "@/shared/lib/markdown";
import { Container, Eyebrow, MetaRow, Rule } from "@/shared/ui/primitives";
import { TableOfContents } from "@/widgets/ArticleShell/TableOfContents";

type Params = Promise<{ slug: string }>;

export async function generateMetadata({ params }: { params: Params }): Promise<Metadata> {
  const { slug } = await params;
  const blog = await fetchBlog(slug);

  if (!blog) return { title: "Not found" };

  return {
    title: blog.title,
    description: blog.summary ?? undefined,
    openGraph: {
      type: "article",
      title: blog.title,
      description: blog.summary ?? undefined,
      publishedTime: blog.published_at ?? undefined,
      modifiedTime: blog.updated_at,
    },
    alternates: { canonical: `/blogs/${blog.slug}` },
  };
}

export default async function ArticlePage({ params }: { params: Params }) {
  const { slug } = await params;

  const [blog, content] = await Promise.all([fetchBlog(slug), fetchContent(slug)]);

  // A slug that does not resolve is a 404 whether it never existed, is a
  // draft, or was archived — the backend deliberately does not distinguish, so
  // neither does this.
  if (!blog) notFound();

  const [categories, series, feed] = await Promise.all([
    fetchCategories(),
    fetchSeries(),
    // Only needed to compute series navigation.
    blog.series_id ? fetchFeed({ series_id: blog.series_id, limit: 100 }) : null,
  ]);

  const categoryLabels = new Map(categories.map((entry) => [entry.key, entry.label]));
  const currentSeries = series.find((entry) => entry.id === blog.series_id) ?? null;

  const { previous, next } = feed
    ? seriesNeighbours(feed.items, blog)
    : { previous: null, next: null };

  const cover = content ? extractCover(content.markdown, blog.title) : null;

  const labels = blog.category_keys
    .map((key) => categoryLabels.get(key))
    .filter((value): value is string => Boolean(value));

  return (
    <article>
      {/* Hero. Only shown when the body actually opens with an image — a
          generated cover at full bleed above the title would be a large grey
          slab, which is worse than no hero at all. */}
      {cover && (
        <Container width="wide" className="pt-8">
          <BlogCover
            blog={blog}
            cover={cover}
            priority
            sizes="(min-width: 1280px) 1200px, 100vw"
            className="aspect-[21/9] w-full"
          />
        </Container>
      )}

      <Container width="wide" className="pt-10 sm:pt-14">
        <header className="mx-auto max-w-[var(--measure)]">
          {labels.length > 0 && <Eyebrow>{labels.join(" · ")}</Eyebrow>}

          <h1 className="mt-4 text-display font-semibold leading-display tracking-display text-fg">
            {blog.title}
          </h1>

          {blog.summary && (
            <p className="mt-5 font-serif text-[1.25rem] leading-relaxed text-muted">
              {blog.summary}
            </p>
          )}

          <MetaRow
            className="mt-6"
            items={[
              blog.published_at ? (
                <time key="date" dateTime={toDateAttribute(blog.published_at)}>
                  {formatDate(blog.published_at)}
                </time>
              ) : null,
              formatReadingTime(blog.reading_minutes),
              currentSeries && blog.series_position
                ? `${currentSeries.title} · Part ${blog.series_position}`
                : currentSeries?.title,
            ]}
          />
        </header>

        <Rule className="mx-auto mt-10 max-w-[var(--measure)]" />

        {/*
          The article column stays centred in the page; the table of contents
          is placed in a right-hand track that only exists above 1280px. Laid
          out as a grid rather than a sticky sidebar so the prose does not
          shift position when the TOC is absent.
        */}
        <div className="mt-10 grid grid-cols-1 gap-12 xl:grid-cols-[1fr_minmax(0,var(--measure))_1fr]">
          <div className="hidden xl:block" />

          <div className="mx-auto w-full max-w-[var(--measure)] xl:mx-0">
            {content ? (
              <Article markdown={content.markdown} sections={blog.sections} />
            ) : (
              <p className="border border-rule bg-surface px-5 py-6 text-[0.9375rem] text-muted">
                This article&rsquo;s body could not be loaded. The metadata is
                current, so this is a storage problem rather than a missing
                article — try again shortly.
              </p>
            )}
          </div>

          <div className="hidden xl:block">
            <TableOfContents sections={blog.sections} className="sticky top-24" />
          </div>
        </div>

        {(previous || next) && currentSeries && (
          <nav
            aria-label="Series navigation"
            className="mx-auto mt-16 max-w-[var(--measure)] border-t border-rule pt-8"
          >
            <Eyebrow>{currentSeries.title}</Eyebrow>
            <div className="mt-4 grid gap-6 sm:grid-cols-2">
              {previous && (
                <Link href={`/blogs/${previous.slug}`} className="group block">
                  <p className="text-meta text-muted">Previous</p>
                  <p className="mt-1 font-medium text-fg transition-colors group-hover:text-muted">
                    {previous.title}
                  </p>
                </Link>
              )}
              {next && (
                <Link
                  href={`/blogs/${next.slug}`}
                  className="group block sm:text-right sm:[grid-column:2]"
                >
                  <p className="text-meta text-muted">Next</p>
                  <p className="mt-1 font-medium text-fg transition-colors group-hover:text-muted">
                    {next.title}
                  </p>
                </Link>
              )}
            </div>
          </nav>
        )}
      </Container>
    </article>
  );
}
