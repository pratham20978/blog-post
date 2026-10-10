---
social_schema: 2
canonical_url: "https://canery.in/blogs/what-is-a-relational-database-postgresql"
---

# Social publishing package — what-is-a-relational-database-postgresql

## LinkedIn post

What does a relational database actually do between your query and its rows? I ran one business question on PostgreSQL 18 and watched.

You write what you want: revenue per country for paid orders. The server decides how, in four stages: the parser checks the grammar and then the names, the rewriter expands views, the planner estimates each path and keeps the cheapest, and the executor runs it. Its estimate for the next-best plan was 2.27 times the cost of the one it picked.

Then two surprises on the same tables. The orders table had no primary key, so an exact copy of one order went in without a warning and moved one country's revenue by 56,954 cents. And after one amount was set to NULL, count(*) said 1,000,000 while count(amount_cents) said 999,999.

Part 4 of PostgreSQL Foundations, the first written for someone who has never used a database. Swipe through the six cards; the link is in the first comment.

## LinkedIn first comment

A table is a set of rows only once you declare a key, and NULL is a marker for unknown, not a value. Both rules are cheap to learn and expensive to learn late.

Read the full article on Canery: https://canery.in/blogs/what-is-a-relational-database-postgresql

## Instagram caption

What a relational database actually does: you say what, it decides how, in four stages you can watch. Plus two silent bugs on real rows: a duplicate order that moved revenue by 56,954 cents, and a NULL that made count(*) and count(amount_cents) disagree. Part 4 of PostgreSQL Foundations. Full article on canery.in, link in bio.

## Shared feed order

1. `assets/social/feed-01-what-and-how.png` — A relational database separates what you ask for from how it is fetched, in four visible stages.
2. `assets/social/feed-02-duplicate.png` — Without a primary key, PostgreSQL stores an exact duplicate and the revenue total silently moves.
3. `assets/social/feed-03-the-fix.png` — Declaring the primary key fails until the duplicate is removed, then refuses the copy for good.
4. `assets/social/feed-04-cheapest-plan.png` — The planner chose a hash join over a plan it estimated at 2.27 times the cost, despite a wrong row estimate.
5. `assets/social/feed-05-null.png` — One NULL makes count(*) and count(column) differ and makes = NULL match nothing.
6. `assets/social/feed-06-read-the-post.png` — The schema is data: pg_class has a row for every table, pg_class included.

## Instagram Story

- CTA: Read what PostgreSQL does between your query and its rows
- Link sticker label: Read the article
- Link sticker URL: https://canery.in/blogs/what-is-a-relational-database-postgresql

### Story order

1. `assets/social/story-01-what-and-how.png` — Overlay: What a relational database actually does
2. `assets/social/story-02-duplicate.png` — Overlay: One copied row moved revenue by 56,954 cents
3. `assets/social/story-03-null.png` — Overlay: Why count(*) and count(column) disagree
4. `assets/social/story-04-read-the-post.png` — Overlay: Read how →

## Asset metadata

### feed-01-what-and-how

- File: `assets/social/feed-01-what-and-how.png`
- Title: You say what. It decides how.
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: A relational database separates what you ask for from how it is fetched, in four visible stages.
- Technical source: Intuition; What happens between the query and the rows?; Figure 4; ledger L12, L05
- Visual structure: Headline and setup; a vertical flow from the SQL query through four stage boxes (planner highlighted), each edge labelled with what it carries, to five result rows; takeaway and footer.
- Visible-text transcript: You say what. It decides how. · Four stages stand between your query and its rows. · your SQL query · parser checks the grammar, then looks up every name · rewriter replaces each view with its definition · planner estimates every path, keeps the cheapest · executor walks the plan tree and returns rows · query tree · rewritten query tree · plan tree · 5 rows: revenue per country · Your query never names an index, an order or a path. · POSTGRESQL FOUNDATIONS · PART 4 · CANERY.IN
- Alt text: A SQL query passing through PostgreSQL's four stages, parser, rewriter, planner and executor, to five result rows.
- Long description: Cover card. A vertical flow: the SQL query enters the parser, which checks the grammar and then looks up every name; a query tree goes to the rewriter, which replaces views with their definitions; the rewritten query tree goes to the planner, highlighted, which estimates every path and keeps the cheapest; the plan tree goes to the executor, which returns five rows of revenue per country. The query itself never says which index, order or path to use.
- Keywords: PostgreSQL, relational database, SQL, query planner, parser, executor
- Canonical URL: https://canery.in/blogs/what-is-a-relational-database-postgresql

### feed-02-duplicate

- File: `assets/social/feed-02-duplicate.png`
- Title: One duplicate, no error
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Without a primary key, PostgreSQL stores an exact duplicate and the revenue total silently moves.
- Technical source: Surprise one: the table accepted a duplicate; Figure 6; ledger L38, L47
- Visual structure: Headline and setup; the duplicated order row drawn twice under its column names; revenue for JP before and after, the difference called out; takeaway and footer.
- Visible-text transcript: One duplicate, no error · orders has no primary key, so an exact copy of order 4242 went in. · orders · no primary key · id · customer_id · amount_cents · status · 4242 · 92399 · 56,954 · paid · 4242 · 92399 · 56,954 · paid · the same row, twice: accepted without a warning · revenue for JP · 3,333,366,679 · before · 3,333,423,633 · after the copy · +56,954 cents · +1 paid order · same query · A table is a set only once you declare a key. · POSTGRESQL FOUNDATIONS · PART 4 · CANERY.IN
- Alt text: Order 4242 stored twice in a table with no key, raising revenue for JP from 3,333,366,679 to 3,333,423,633 cents.
- Long description: The orders table has no primary key, so inserting an exact copy of order 4242 (customer 92399, 56,954 cents, paid) succeeds without a warning. Both copies join to the same customer, so the revenue for JP rises from 3,333,366,679 to 3,333,423,633 cents, exactly 56,954 more, with one more paid order. The query is unchanged and nothing errors. PostgreSQL 18.6, lab measurement.
- Keywords: PostgreSQL, relational database, SQL, primary key, duplicate rows, data integrity
- Canonical URL: https://canery.in/blogs/what-is-a-relational-database-postgresql

### feed-03-the-fix

- File: `assets/social/feed-03-the-fix.png`
- Title: The key that stops it
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Declaring the primary key fails until the duplicate is removed, then refuses the copy for good.
- Technical source: Surprise one: the table accepted a duplicate; ledger L39, L23
- Visual structure: Headline and setup; three numbered steps with the statement, the verdict and the server's message; takeaway and footer.
- Visible-text transcript: The key that stops it · The constraint cannot go on while the copy is there. · 1 · alter table orders add primary key (id); · refused while the copy exists · could not create unique index "orders_pkey" · 2 · delete one copy, then add the key again · accepted · 3 · insert the copy again · refused, for every program that connects · duplicate key value violates unique constraint "orders_pkey" · A constraint binds every program; an app check binds one. · POSTGRESQL FOUNDATIONS · PART 4 · CANERY.IN
- Alt text: Three steps: adding the primary key is refused while the duplicate exists, accepted after deleting it, then refuses the copy.
- Long description: Step 1: alter table orders add primary key (id) fails with could not create unique index "orders_pkey", because order 4242 is duplicated. Step 2: after one copy is deleted, the same statement succeeds. Step 3: inserting the copy again is refused with duplicate key value violates unique constraint "orders_pkey", for every program that connects. PostgreSQL 18.6, lab measurement.
- Keywords: PostgreSQL, relational database, SQL, primary key, constraint, unique index
- Canonical URL: https://canery.in/blogs/what-is-a-relational-database-postgresql

### feed-04-cheapest-plan

- File: `assets/social/feed-04-cheapest-plan.png`
- Title: The planner picks the cheapest
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: The planner chose a hash join over a plan it estimated at 2.27 times the cost, despite a wrong row estimate.
- Technical source: Stage 3 and Stage 4; Figure 1; ledger L36, L41, L17
- Visual structure: Headline and setup; two proportional cost bars, chosen and next-best; the cost ratio; the per-process estimate against the actual count; takeaway and footer.
- Visible-text transcript: The planner picks the cheapest · It estimated the cost of each way to answer the question. · hash join plan · chosen · cost 18,285.79 · next-best plan · hash joins off · cost 41,515.08 · 2.27× the estimated cost · estimated 140,514 paid orders per process; each found 111,111 · units are arbitrary: compare plans, never clocks · Estimates decide how a query runs, never what it returns. · POSTGRESQL FOUNDATIONS · PART 4 · CANERY.IN
- Alt text: Two cost bars: the chosen hash join plan at 18,285.79 and the next-best plan at 41,515.08, 2.27 times the cost.
- Long description: For the revenue query, the planner's chosen plan, a hash join, has an estimated cost of 18,285.79. With hash joins turned off, the next-best plan costs 41,515.08, 2.27 times as much. The planner estimated 140,514 paid orders per process; each process found 111,111. Cost units are arbitrary, so they compare plans with each other, not with a clock. PostgreSQL 18.6, lab measurement.
- Keywords: PostgreSQL, relational database, SQL, query planner, EXPLAIN, hash join, cost estimate
- Canonical URL: https://canery.in/blogs/what-is-a-relational-database-postgresql

### feed-05-null

- File: `assets/social/feed-05-null.png`
- Title: NULL is not a value
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: One NULL makes count(*) and count(column) differ and makes = NULL match nothing.
- Technical source: Surprise two: NULL is not a value; Figure 7; ledger L19, L40, L49, L50
- Visual structure: Headline and setup; two count boxes with their values; two WHERE clauses with the rows each matches; a one-line reason; takeaway and footer.
- Visible-text transcript: NULL is not a value · Blank one amount, and two counts that look alike disagree. · count(*) · 1,000,000 · counts rows · count(amount_cents) · 999,999 · counts values that are not NULL · where amount_cents = null · 0 rows · where amount_cents is null · 1 row · a comparison with NULL is unknown, and WHERE keeps only true · count(*) counts rows. count(column) counts values. · POSTGRESQL FOUNDATIONS · PART 4 · CANERY.IN
- Alt text: count(*) returns 1,000,000 and count(amount_cents) 999,999; = null matches 0 rows and is null matches 1.
- Long description: After one order's amount is set to NULL, count(*) returns 1,000,000 because it counts rows, while count(amount_cents) returns 999,999 because it counts only non-NULL values. where amount_cents = null matches 0 rows, because a comparison with NULL is unknown and WHERE keeps only rows whose condition is true; where amount_cents is null matches 1. PostgreSQL 18.6, lab measurement.
- Keywords: PostgreSQL, relational database, SQL, NULL, three-valued logic, count, aggregate
- Canonical URL: https://canery.in/blogs/what-is-a-relational-database-postgresql

### feed-06-read-the-post

- File: `assets/social/feed-06-read-the-post.png`
- Title: Even the catalog is a table
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: The schema is data: pg_class has a row for every table, pg_class included.
- Technical source: The schema is stored as data; Figure 3; ledger L21, L32
- Visual structure: Headline and setup; four rows of pg_class with their kind and column count, pg_class's own row highlighted; call to action and footer.
- Visible-text transcript: Even the catalog is a table · PostgreSQL stores its schema as rows, including its own. · pg_class · four of its rows · relname · relkind · relnatts · customers · r · 3 · orders · r · 5 · pg_attribute · r · 25 · pg_class · r · 34 · pg_class is a table, so it has a row in pg_class · every table, column and constraint is a row you can query · Read the full post on canery.in → · POSTGRESQL FOUNDATIONS · PART 4 · CANERY.IN
- Alt text: The pg_class catalog listing customers, orders, pg_attribute and pg_class itself, with 3, 5, 25 and 34 columns.
- Long description: Closing card. Four rows of the pg_class catalog: customers (3 columns), orders (5), pg_attribute (25) and pg_class itself (34), all ordinary tables of kind r. The catalog describes itself in the same form it describes your tables. Call to action: read the full post on canery.in.
- Keywords: PostgreSQL, relational database, SQL, system catalog, pg_class, schema
- Canonical URL: https://canery.in/blogs/what-is-a-relational-database-postgresql

### story-01-what-and-how

- File: `assets/social/story-01-what-and-how.png`
- Title: You say what. It decides how.
- Platforms: Instagram Story
- Role: cover
- Dimensions: 1080×1920
- Narrative beat: Story opener: the four stages a query passes through.
- Technical source: Intuition; What happens between the query and the rows?; Figure 4; ledger L12, L05
- Visual structure: Hook headline, setup line, a tall panel with the four stage boxes and labelled edges, takeaway, footer.
- Visible-text transcript: You say what. It decides how. · Four stages between your query and its rows. · your SQL query · parser checks the grammar, then looks up every name · rewriter replaces each view with its definition · planner estimates every path, keeps the cheapest · executor walks the plan tree and returns rows · query tree · rewritten query tree · plan tree · 5 rows: revenue per country · Watch each one in the post. · POSTGRESQL FOUNDATIONS · PART 4 · CANERY.IN
- Alt text: Story cover: a SQL query passing through the parser, rewriter, planner and executor to five result rows.
- Long description: Story cover, recomposed for 9:16. The SQL query flows through four stage boxes: the parser (grammar, then names), the rewriter (views replaced), the planner (highlighted; cheapest estimated path) and the executor (walks the plan tree), ending in five rows of revenue per country.
- Keywords: PostgreSQL, relational database, SQL, query planner, parser, executor
- Canonical URL: https://canery.in/blogs/what-is-a-relational-database-postgresql

### story-02-duplicate

- File: `assets/social/story-02-duplicate.png`
- Title: One duplicate, no error
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: Story beat: a duplicate row silently moved a revenue total.
- Technical source: Surprise one: the table accepted a duplicate; Figure 6; ledger L38, L47
- Visual structure: Headline and setup; the duplicated order row drawn twice under its column names; revenue for JP before and after, the difference called out; takeaway and footer.
- Visible-text transcript: One duplicate, no error · No primary key, so the copy went in. · orders · no primary key · id · customer_id · amount_cents · status · 4242 · 92399 · 56,954 · paid · 4242 · 92399 · 56,954 · paid · the same row, twice: accepted without a warning · revenue for JP · 3,333,366,679 · before · 3,333,423,633 · after the copy · +56,954 cents · +1 paid order · same query · Declare the key before the incident. · POSTGRESQL FOUNDATIONS · PART 4 · CANERY.IN
- Alt text: Story frame: the same order row stored twice, and revenue for JP rising from 3,333,366,679 to 3,333,423,633 cents.
- Long description: Story frame, recomposed for 9:16. The orders table has no primary key, so order 4242 (customer 92399, 56,954 cents, paid) appears twice, identical in every column. Revenue for JP is shown before (3,333,366,679 cents) and after the copy (3,333,423,633 cents): 56,954 cents and one paid order more, with the same query and no error. The takeaway: declare the key before the incident.
- Keywords: PostgreSQL, relational database, SQL, primary key, duplicate rows, data integrity
- Canonical URL: https://canery.in/blogs/what-is-a-relational-database-postgresql

### story-03-null

- File: `assets/social/story-03-null.png`
- Title: NULL is not a value
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: Story beat: one NULL splits two counts and hides its row from = NULL.
- Technical source: Surprise two: NULL is not a value; Figure 7; ledger L19, L40, L49, L50
- Visual structure: Headline and setup; two count boxes with their values; two WHERE clauses with the rows each matches; a one-line reason; takeaway and footer.
- Visible-text transcript: NULL is not a value · Two counts that look alike disagree. · count(*) · 1,000,000 · counts rows · count(amount_cents) · 999,999 · counts values that are not NULL · where amount_cents = null · 0 rows · where amount_cents is null · 1 row · a comparison with NULL is unknown, and WHERE keeps only true · count(column) skips the unknown. · POSTGRESQL FOUNDATIONS · PART 4 · CANERY.IN
- Alt text: Story frame: count(*) at 1,000,000 against count(amount_cents) at 999,999, and = null matching no rows.
- Long description: Story frame, recomposed for 9:16. With one amount set to NULL, count(*) returns 1,000,000 because it counts rows, and count(amount_cents) returns 999,999 because it counts only values that are not NULL. where amount_cents = null matches 0 rows and where amount_cents is null matches 1, because a comparison with NULL is unknown and WHERE keeps only rows whose condition is true.
- Keywords: PostgreSQL, relational database, SQL, NULL, three-valued logic, count, aggregate
- Canonical URL: https://canery.in/blogs/what-is-a-relational-database-postgresql

### story-04-read-the-post

- File: `assets/social/story-04-read-the-post.png`
- Title: The key that stops it
- Platforms: Instagram Story
- Role: cta
- Dimensions: 1080×1920
- Narrative beat: Story close: the constraint that would have stopped the duplicate, and the call to action.
- Technical source: Surprise one: the table accepted a duplicate; ledger L39, L23
- Visual structure: Headline and setup; three numbered steps with the statement, the verdict and the server's message; takeaway and footer.
- Visible-text transcript: The key that stops it · Declared once, enforced for every program. · 1 · alter table orders add primary key (id); · refused while the copy exists · could not create unique index "orders_pkey" · 2 · delete one copy, then add the key again · accepted · 3 · insert the copy again · refused, for every program that connects · duplicate key value violates unique constraint "orders_pkey" · Read how → canery.in · POSTGRESQL FOUNDATIONS · PART 4 · CANERY.IN
- Alt text: Closing story frame: the primary key refused while the duplicate exists, accepted once it is gone, then refusing the copy.
- Long description: Closing story frame, recomposed for 9:16, with the call to action. Step 1: alter table orders add primary key (id) is refused with could not create unique index "orders_pkey" while order 4242 is duplicated. Step 2: after one copy is deleted, the key is accepted. Step 3: inserting the copy again is refused with duplicate key value violates unique constraint "orders_pkey", for every program that connects. Call to action: read how on canery.in.
- Keywords: PostgreSQL, relational database, SQL, primary key, constraint, unique index
- Canonical URL: https://canery.in/blogs/what-is-a-relational-database-postgresql
