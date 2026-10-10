---
social_schema: 2
canonical_url: "https://canery.in/blogs/sql-select-evaluation-joins-group-by-null"
---

# Social publishing package — sql-select-evaluation-joins-group-by-null

## LinkedIn post

SQL does not evaluate your SELECT in the order you write it. SELECT is written first and evaluated fifth, after FROM, WHERE, GROUP BY and HAVING.

I built one report on PostgreSQL 18, clause by clause, and counted the rows after each: 1,000,000 joined rows, 333,333 paid orders, 5 countries, 2 shown. Then the traps:

· The "top two countries" report returned DE and IN with default settings, and DE and JP with parallel workers off. Same query, same data. IN and JP tie, and the query never said how to break the tie.
· A LEFT JOIN kept 1,000 customers who had never ordered, until a WHERE on the orders table dropped them again.
· One order lost its customer, and NOT IN's count of customers who never ordered went from 1,000 to 0. NOT EXISTS still found all 1,000.

Part 5 of PostgreSQL Foundations, with a runnable lab. Swipe through the six cards; the link is in the first comment.

## LinkedIn first comment

Know the logical order and every row count becomes predictable. And wherever a NULL can appear, write NOT EXISTS, not NOT IN.

Read the full article on Canery: https://canery.in/blogs/sql-select-evaluation-joins-group-by-null

## Instagram caption

SQL evaluates SELECT fifth. One PostgreSQL 18 report, built clause by clause: a tie that changes the top two between plans, a WHERE that undoes a LEFT JOIN, and one NULL that empties NOT IN. Part 5 of PostgreSQL Foundations. Full article on canery.in, link in bio.

## Shared feed order

1. `assets/social/feed-01-logical-order.png` — SQL's logical order evaluates SELECT fifth, and the row count after each clause follows from it.
2. `assets/social/feed-02-tie.png` — A tie at the LIMIT boundary let the plan choose the second row: IN with defaults, JP without parallel workers.
3. `assets/social/feed-03-left-join.png` — A WHERE on the right-hand table drops a left join's padded rows; the same condition in ON keeps them.
4. `assets/social/feed-04-null-first.png` — NULL sorts as larger than every value, so in a descending sort the five empty groups take the top five places.
5. `assets/social/feed-05-not-in.png` — NOT IN is a chain of ANDed inequalities, so one NULL in the subquery makes it unknown for every customer.
6. `assets/social/feed-06-read-the-post.png` — Fan-out: a join repeats a customer once per paid order, EXISTS keeps it once, and UNION removes repeats that UNION ALL keeps.

## Instagram Story

- CTA: Read how SQL evaluates a SELECT, clause by clause
- Link sticker label: Read the article
- Link sticker URL: https://canery.in/blogs/sql-select-evaluation-joins-group-by-null

### Story order

1. `assets/social/story-01-logical-order.png` — Overlay: The order SQL really evaluates your SELECT
2. `assets/social/story-02-tie.png` — Overlay: Same query, same rows, a different second place
3. `assets/social/story-03-not-in.png` — Overlay: Why NOT IN returned zero rows
4. `assets/social/story-04-read-the-post.png` — Overlay: Read how →

## Asset metadata

### feed-01-logical-order

- File: `assets/social/feed-01-logical-order.png`
- Title: SELECT comes fifth
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: SQL's logical order evaluates SELECT fifth, and the row count after each clause follows from it.
- Technical source: The problem; Worked example; Figure 2; ledger L01, L46
- Visual structure: Headline and setup; eight rows in evaluation order, each with its written position and the full shop's row count after it, SELECT highlighted; takeaway and footer.
- Visible-text transcript: SELECT comes fifth · SQL evaluates a query's clauses in a fixed order, not the order you write them. · evaluated · written · rows after it · 1 FROM · JOIN · 2nd · 1,000,000 · 2 WHERE · 3rd · 333,333 · 3 GROUP BY · 4th · 5 groups · 4 HAVING · 5th · 5 · 5 SELECT · 1st · 5 · 6 DISTINCT · with SELECT · 5 · 7 ORDER BY · 6th · 5, sorted · 8 LIMIT 2 · 7th · 2 · Know the order and you can predict every row count. · POSTGRESQL FOUNDATIONS · PART 5 · CANERY.IN
- Alt text: The eight clauses of a SELECT in evaluation order, with where each is written and the rows left after it, from 1,000,000 to 2.
- Long description: Cover card. The clauses in the order SQL evaluates them, with their written position and the row count after each, for the report 'paid revenue per country, top two' on PostgreSQL 18.6: FROM and JOIN (written 2nd) 1,000,000 rows; WHERE (3rd) 333,333; GROUP BY (4th) 5 groups; HAVING (5th) 5; SELECT (written 1st, evaluated 5th, highlighted) 5; DISTINCT 5; ORDER BY (6th) 5 sorted; LIMIT 2 (7th) 2. Lab measurement.
- Keywords: SQL, PostgreSQL, SELECT, SQL order of execution, logical query processing
- Canonical URL: https://canery.in/blogs/sql-select-evaluation-joins-group-by-null

### feed-02-tie

- File: `assets/social/feed-02-tie.png`
- Title: Which country is second?
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: A tie at the LIMIT boundary let the plan choose the second row: IN with defaults, JP without parallel workers.
- Technical source: Worked example; Figure 3; ledger L12, L46, L47, L15
- Visual structure: Headline and setup; five countries ranked by paid revenue, IN and JP tinted as tied, a dashed LIMIT 2 line between them; three outcomes with the rows each returned; takeaway and footer.
- Visible-text transcript: Which country is second? · IN and JP tie on paid revenue, so LIMIT 2 has no unique answer. · order by revenue_cents desc limit 2 · 1 · DE · 3,333,366,716 · 2 or 3 · IN · 3,333,366,679 · 2 or 3 · JP · 3,333,366,679 · 4 · BR · 3,333,266,642 · 5 · US · 3,333,166,605 · LIMIT 2 · default settings · DE, IN · parallel workers off · DE, JP · fetch first 2 rows with ties · DE, IN, JP · A top-N query needs a tiebreaker or WITH TIES. · POSTGRESQL FOUNDATIONS · PART 5 · CANERY.IN
- Alt text: Five countries ranked by paid revenue with IN and JP tied on the LIMIT 2 line; defaults return DE, IN and no parallelism DE, JP.
- Long description: Paid revenue per country on PostgreSQL 18.6: DE 3,333,366,716 cents, then IN and JP tied at 3,333,366,679, BR and US below. ORDER BY revenue DESC LIMIT 2 returned DE, IN with default settings and DE, JP with max_parallel_workers_per_gather = 0, on the same data. FETCH FIRST 2 ROWS WITH TIES returned DE, IN, JP. Rows equal on every sort key come back in an implementation-dependent order. Lab measurement.
- Keywords: SQL, PostgreSQL, SELECT, ORDER BY, LIMIT, WITH TIES, top-N query
- Canonical URL: https://canery.in/blogs/sql-select-evaluation-joins-group-by-null

### feed-03-left-join

- File: `assets/social/feed-03-left-join.png`
- Title: The WHERE that undoes a LEFT JOIN
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: A WHERE on the right-hand table drops a left join's padded rows; the same condition in ON keeps them.
- Technical source: What does FROM build?; Figures 4 and 5; ledger L05, L06, L50
- Visual structure: Headline and setup; four stacked boxes, each a join form with its row count and what happened to the padded rows; takeaway and footer.
- Visible-text transcript: The WHERE that undoes a LEFT JOIN · 1,000 customers have never ordered. A WHERE on orders makes them vanish. · customers join orders · 1,000,000 · every order has a customer · customers left join orders · 1,001,000 · +1,000 padded rows, one per customer with no orders · left join … where o.status = 'paid' · 333,333 · padded rows dropped: NULL = 'paid' is unknown · left join … on … and o.status = 'paid' · 334,333 · padded rows kept: the condition only decides the match · Put conditions for an outer join in ON. · POSTGRESQL FOUNDATIONS · PART 5 · CANERY.IN
- Alt text: Four join forms and their row counts: inner 1,000,000, left 1,001,000, left plus WHERE 333,333, left with ON 334,333.
- Long description: customers join orders: 1,000,000 rows. customers left join orders: 1,001,000, one padded row for each of the 1,000 customers with no orders. Adding where o.status = 'paid' gives 333,333, the same as an inner join, because each padded row's status is NULL and NULL = 'paid' is unknown. Moving the condition into the ON clause gives 334,333: the padded rows survive. PostgreSQL 18.6, lab measurement.
- Keywords: SQL, PostgreSQL, SELECT, LEFT JOIN, INNER JOIN, outer join, ON vs WHERE
- Canonical URL: https://canery.in/blogs/sql-select-evaluation-joins-group-by-null

### feed-04-null-first

- File: `assets/social/feed-04-null-first.png`
- Title: NULLs sort first
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: NULL sorts as larger than every value, so in a descending sort the five empty groups take the top five places.
- Technical source: WHERE or HAVING, and where does NULL land?; Figure 7; ledger L13, L40, L54
- Visual structure: Headline and setup; the five rows LIMIT 5 returns, all with NULL status and revenue; the five rows NULLS LAST returns, with the tie for fifth tinted; takeaway and footer.
- Visible-text transcript: NULLs sort first · Group a left join by country and status, then sort by revenue, largest first. · order by revenue_cents desc limit 5 · DE · status NULL · revenue NULL · BR · status NULL · revenue NULL · US · status NULL · revenue NULL · JP · status NULL · revenue NULL · IN · status NULL · revenue NULL · … desc nulls last, first 5 with ties · JP · refunded · 3,333,499,963 · JP · shipped · 3,333,433,358 · DE · refunded · 3,333,399,963 · DE · paid · 3,333,366,716 · JP · paid · 3,333,366,679 · IN · paid · 3,333,366,679 · JP paid and IN paid tie for fifth · Write NULLS LAST, or the empty groups win. · POSTGRESQL FOUNDATIONS · PART 5 · CANERY.IN
- Alt text: A descending sort's top five: five groups with NULL status and revenue; with NULLS LAST, real totals, and JP paid tied with IN paid.
- Long description: After a left join grouped by country and status, each country has one group whose status is NULL, holding its customers with no orders; its revenue is NULL. ORDER BY revenue_cents DESC LIMIT 5 returns those five groups, because PostgreSQL sorts NULL as if larger than every value. With NULLS LAST the top five are JP refunded, JP shipped, DE refunded, DE paid and JP paid, and IN paid ties JP paid at 3,333,366,679 cents. PostgreSQL 18.6, lab measurement.
- Keywords: SQL, PostgreSQL, SELECT, NULL, ORDER BY, NULLS LAST, GROUP BY
- Canonical URL: https://canery.in/blogs/sql-select-evaluation-joins-group-by-null

### feed-05-not-in

- File: `assets/social/feed-05-not-in.png`
- Title: One NULL empties NOT IN
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: NOT IN is a chain of ANDed inequalities, so one NULL in the subquery makes it unknown for every customer.
- Technical source: Why does NOT IN return nothing once a NULL appears?; Figure 8; ledger L18, L34, L58, L59, L60
- Visual structure: Headline and setup; two boxes with the NOT IN and NOT EXISTS counts before and after the NULL; the comparisons NOT IN makes for one customer, the last one unknown; takeaway and footer.
- Visible-text transcript: One NULL empties NOT IN · Customers who never ordered, before and after one order lost its customer. · where id not in (select customer_id …) · 1,000 → 0 · customers with no orders · where not exists (… customer_id = c.id) · 1,000 → 1,000 · customers with no orders · NOT IN for customer 100,001, after the NULL: · 100001 <> 7920 · true · 100001 <> 15839 · true · … 999,997 more · true · 100001 <> NULL · unknown · true AND … AND unknown is unknown: the row is dropped · Write NOT EXISTS, and declare NOT NULL. · POSTGRESQL FOUNDATIONS · PART 5 · CANERY.IN
- Alt text: NOT IN's count of customers with no orders falls from 1,000 to 0 after one NULL; NOT EXISTS stays at 1,000.
- Long description: Customers who have never placed an order: NOT IN and NOT EXISTS both find 1,000. After one order's customer_id is set to NULL, NOT IN finds 0 and NOT EXISTS still finds 1,000. For customer 100,001, NOT IN compares 100001 with every customer_id: 999,999 comparisons are true and 100001 <> NULL is unknown, so the AND of all of them is unknown and WHERE drops the row. NOT EXISTS only asks whether a matching order exists. PostgreSQL 18.6, lab measurement.
- Keywords: SQL, PostgreSQL, SELECT, NOT IN, NOT EXISTS, NULL, three-valued logic
- Canonical URL: https://canery.in/blogs/sql-select-evaluation-joins-group-by-null

### feed-06-read-the-post

- File: `assets/social/feed-06-read-the-post.png`
- Title: Where duplicates come from
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: Fan-out: a join repeats a customer once per paid order, EXISTS keeps it once, and UNION removes repeats that UNION ALL keeps.
- Technical source: Where do duplicate rows come from?; Figures 9 and 10; ledger L45, L55, L57
- Visual structure: Headline and setup; two pairs of count boxes, join against EXISTS and UNION ALL against UNION; the arithmetic behind 333,333; call to action and footer.
- Visible-text transcript: Where duplicates come from · A join repeats a row once per match; EXISTS keeps it once. · join orders … paid · 333,333 · one row per paid order · exists (… paid) · 100,000 · one row per customer · union all · 666,666 · 333,333 + 333,333 rows · union · 100,000 · duplicates removed, inside each input too · 66,667 customers × 3 paid + 33,333 × 4 = 333,333 · Read the full post on canery.in → · POSTGRESQL FOUNDATIONS · PART 5 · CANERY.IN
- Alt text: Join gives 333,333 rows and EXISTS 100,000; UNION ALL gives 666,666 rows and UNION 100,000.
- Long description: Closing card. Customers with a paid order: a join returns 333,333 rows, one per paid order, because 66,667 customers have 3 paid orders and 33,333 have 4; EXISTS returns 100,000, one per customer. The customer ids of paid and of refunded orders, 333,333 rows each: UNION ALL returns 666,666, UNION returns 100,000, because it removes duplicates inside each input as well as across them. Call to action: read the full post on canery.in.
- Keywords: SQL, PostgreSQL, SELECT, JOIN, EXISTS, UNION, UNION ALL, duplicates
- Canonical URL: https://canery.in/blogs/sql-select-evaluation-joins-group-by-null

### story-01-logical-order

- File: `assets/social/story-01-logical-order.png`
- Title: SELECT comes fifth
- Platforms: Instagram Story
- Role: cover
- Dimensions: 1080×1920
- Narrative beat: Story opener: the logical order of a SELECT, with the row count after each clause.
- Technical source: The problem; Worked example; Figure 2; ledger L01, L46
- Visual structure: Hook headline, setup line, a tall panel with the eight clauses in evaluation order, their written positions and row counts, takeaway, footer.
- Visible-text transcript: SELECT comes fifth · The order SQL evaluates a query. · evaluated · written · rows after it · 1 FROM · JOIN · 2nd · 1,000,000 · 2 WHERE · 3rd · 333,333 · 3 GROUP BY · 4th · 5 groups · 4 HAVING · 5th · 5 · 5 SELECT · 1st · 5 · 6 DISTINCT · with SELECT · 5 · 7 ORDER BY · 6th · 5, sorted · 8 LIMIT 2 · 7th · 2 · Every row count follows from it. · POSTGRESQL FOUNDATIONS · PART 5 · CANERY.IN
- Alt text: Story cover: the eight clauses of a SELECT in evaluation order, SELECT fifth, with the rows left after each clause.
- Long description: Story cover, recomposed for 9:16. The clauses in the order SQL evaluates them, with their written position and the row count after each, for the report 'paid revenue per country, top two' on PostgreSQL 18.6: FROM and JOIN (written 2nd) 1,000,000 rows; WHERE (3rd) 333,333; GROUP BY (4th) 5 groups; HAVING (5th) 5; SELECT (written 1st, evaluated 5th, highlighted) 5; DISTINCT 5; ORDER BY (6th) 5 sorted; LIMIT 2 (7th) 2. Lab measurement.
- Keywords: SQL, PostgreSQL, SELECT, SQL order of execution, logical query processing
- Canonical URL: https://canery.in/blogs/sql-select-evaluation-joins-group-by-null

### story-02-tie

- File: `assets/social/story-02-tie.png`
- Title: Which country is second?
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: Story beat: a tie at the LIMIT boundary lets the plan pick the second row.
- Technical source: Worked example; Figure 3; ledger L12, L46, L47, L15
- Visual structure: Headline and setup; five countries ranked by paid revenue, IN and JP tinted as tied, a dashed LIMIT 2 line between them; three outcomes with the rows each returned; takeaway and footer.
- Visible-text transcript: Which country is second? · IN and JP tie on paid revenue. · order by revenue_cents desc limit 2 · 1 · DE · 3,333,366,716 · 2 or 3 · IN · 3,333,366,679 · 2 or 3 · JP · 3,333,366,679 · 4 · BR · 3,333,266,642 · 5 · US · 3,333,166,605 · LIMIT 2 · default settings · DE, IN · parallel workers off · DE, JP · fetch first 2 rows with ties · DE, IN, JP · Add a tiebreaker or WITH TIES. · POSTGRESQL FOUNDATIONS · PART 5 · CANERY.IN
- Alt text: Story frame: IN and JP tied on the LIMIT 2 line; default settings keep IN, no parallel workers keep JP, WITH TIES keeps both.
- Long description: Story frame, recomposed for 9:16. Paid revenue per country on PostgreSQL 18.6: DE 3,333,366,716 cents, then IN and JP tied at 3,333,366,679, BR and US below. ORDER BY revenue DESC LIMIT 2 returned DE, IN with default settings and DE, JP with max_parallel_workers_per_gather = 0, on the same data. FETCH FIRST 2 ROWS WITH TIES returned DE, IN, JP. Rows equal on every sort key come back in an implementation-dependent order. Lab measurement.
- Keywords: SQL, PostgreSQL, SELECT, ORDER BY, LIMIT, WITH TIES, top-N query
- Canonical URL: https://canery.in/blogs/sql-select-evaluation-joins-group-by-null

### story-03-not-in

- File: `assets/social/story-03-not-in.png`
- Title: One NULL empties NOT IN
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: Story beat: one NULL in the subquery makes NOT IN unknown for every customer.
- Technical source: Why does NOT IN return nothing once a NULL appears?; Figure 8; ledger L18, L34, L58, L59, L60
- Visual structure: Headline and setup; two boxes with the NOT IN and NOT EXISTS counts before and after the NULL; the comparisons NOT IN makes for one customer, the last one unknown; takeaway and footer.
- Visible-text transcript: One NULL empties NOT IN · 1,000 customers have never ordered. · where id not in (select customer_id …) · 1,000 → 0 · customers with no orders · where not exists (… customer_id = c.id) · 1,000 → 1,000 · customers with no orders · NOT IN for customer 100,001, after the NULL: · 100001 <> 7920 · true · 100001 <> 15839 · true · … 999,997 more · true · 100001 <> NULL · unknown · true AND … AND unknown is unknown: the row is dropped · NOT EXISTS still finds all 1,000. · POSTGRESQL FOUNDATIONS · PART 5 · CANERY.IN
- Alt text: Story frame: NOT IN falls from 1,000 customers to 0 after one NULL, NOT EXISTS stays at 1,000, and the comparison that turns unknown.
- Long description: Story frame, recomposed for 9:16. Customers who have never placed an order: NOT IN and NOT EXISTS both find 1,000. After one order's customer_id is set to NULL, NOT IN finds 0 and NOT EXISTS still finds 1,000. For customer 100,001, NOT IN compares 100001 with every customer_id: 999,999 comparisons are true and 100001 <> NULL is unknown, so the AND of all of them is unknown and WHERE drops the row. NOT EXISTS only asks whether a matching order exists. PostgreSQL 18.6, lab measurement.
- Keywords: SQL, PostgreSQL, SELECT, NOT IN, NOT EXISTS, NULL, three-valued logic
- Canonical URL: https://canery.in/blogs/sql-select-evaluation-joins-group-by-null

### story-04-read-the-post

- File: `assets/social/story-04-read-the-post.png`
- Title: The WHERE that undoes a LEFT JOIN
- Platforms: Instagram Story
- Role: cta
- Dimensions: 1080×1920
- Narrative beat: Story close: the WHERE that turns a left join back into an inner join, and the call to action.
- Technical source: What does FROM build?; Figures 4 and 5; ledger L05, L06, L50
- Visual structure: Headline and setup; four stacked boxes, each a join form with its row count and what happened to the padded rows; takeaway and footer.
- Visible-text transcript: The WHERE that undoes a LEFT JOIN · Conditions for an outer join belong in ON. · customers join orders · 1,000,000 · every order has a customer · customers left join orders · 1,001,000 · +1,000 padded rows, one per customer with no orders · left join … where o.status = 'paid' · 333,333 · padded rows dropped: NULL = 'paid' is unknown · left join … on … and o.status = 'paid' · 334,333 · padded rows kept: the condition only decides the match · Read how → canery.in · POSTGRESQL FOUNDATIONS · PART 5 · CANERY.IN
- Alt text: Closing story frame: inner and left join row counts, the left join undone by WHERE, and kept when the condition is in ON.
- Long description: Closing story frame, recomposed for 9:16, with the call to action. customers join orders: 1,000,000 rows. customers left join orders: 1,001,000, one padded row for each of the 1,000 customers with no orders. Adding where o.status = 'paid' gives 333,333, the same as an inner join, because each padded row's status is NULL and NULL = 'paid' is unknown. Moving the condition into the ON clause gives 334,333: the padded rows survive. PostgreSQL 18.6, lab measurement.
- Keywords: SQL, PostgreSQL, SELECT, LEFT JOIN, INNER JOIN, outer join, ON vs WHERE
- Canonical URL: https://canery.in/blogs/sql-select-evaluation-joins-group-by-null
