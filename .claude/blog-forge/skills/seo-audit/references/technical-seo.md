# Technical SEO rules

- One stable indexable URL owns each article: `https://canery.in/blogs/<slug>`.
- The page shell owns the only H1. Markdown body headings begin at H2.
- The canonical, Open Graph URL, sitemap URL, internal links, and structured data URL must agree.
- `robots.txt` advertises the sitemap. It must not reveal secret admin paths.
- The sitemap contains only canonical, indexable routes and includes each published article's last modification time when known.
- Article JSON-LD must reflect visible content. Never invent author, rating, date, or image values.
- A redirect preserves old `/p/<slug>` links, but new content must never emit that route.
- Network failures are reported as verification warnings; they are not proof that a page is absent from an index.
