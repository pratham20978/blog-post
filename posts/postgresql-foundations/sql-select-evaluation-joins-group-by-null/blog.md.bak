---
title: "How a SELECT Is Evaluated: Joins, Grouping and NULL"
slug: sql-select-evaluation-joins-group-by-null
date: 2026-10-02
updated: 2026-10-02
summary: "SQL evaluates a SELECT's clauses in a fixed logical order, not the order you write them. One PostgreSQL 18 report, clause by clause, and where NULL breaks it."
tags: [databases, postgresql, sql, joins, three-valued-logic, query-execution]
category: databases
categories: [databases]
series: postgresql-foundations
series_position: 5
tier: L3
difficulty: beginner
prerequisites: ["part 4 of this series, or a first SQL course"]
reading_minutes: 29
cover_image_url: "COVER"
cover_image_alt: "Rows of tiles narrowing from twelve to two; in the last row a tangerine tile and a dashed one tie for one place; eight dots beneath"
canonical_url: "https://canery.in/blogs/sql-select-evaluation-joins-group-by-null"
---

> [!NOTE]
> **Insights** — SQL evaluates a SELECT in a fixed logical order: FROM, WHERE, GROUP BY, HAVING, SELECT, DISTINCT, ORDER BY, LIMIT. <!-- L01 --> Each clause takes a table and hands on another, so the order predicts every row count: on PostgreSQL 18, one report went from 1,000,000 joined rows to 333,333 paid orders, then 5 countries, then the top 2. <!-- L46 --> The second of those two changed from IN to JP when the plan changed, because the two countries tie. <!-- L47 --> And one NULL turned NOT IN's count of customers who never ordered from 1,000 to 0, while NOT EXISTS still found all 1,000. <!-- L59 -->

**Level:** beginner · **You need:** part 4's tables and EXPLAIN, or a first SQL course · **Time:** ~29 min

This is part 5 of PostgreSQL Foundations. It builds on part 4, *What a Relational Database Actually Does*, which introduced the shop's two tables, the four stages a query goes through, and NULL. This part opens up the query itself, one clause at a time.

> [!TIP]
> **Runnable lab:** the files are listed under [Lab downloads](#lab-downloads) at the end. The post explains everything; the lab reproduces it.

Every server number below comes from one run of that lab: PostgreSQL 18.6, the current release, built from source with its default configuration, on a laptop with 16 CPUs, 14 GB of RAM and an NVMe disk. <!-- L25 --> <!-- L43 --> The data is the series' shop, 100,000 customers and 1,000,000 orders, plus 1,000 new customers who have never ordered. <!-- L43 --> Row counts are exact on any machine; timings, and the order of tied rows, are not.

**Jump to:** [The problem](#the-problem) · [Worked example](#worked-example) · [Intuition](#intuition) · [FROM](#what-does-from-build) · [WHERE or HAVING](#where-or-having-and-where-does-null-land) · [NOT IN](#why-does-not-in-return-nothing-once-a-null-appears) · [Duplicates](#where-do-duplicate-rows-come-from) · [The math](#the-math) · [Limitations](#limitations-and-common-mistakes) · [Try it yourself](#try-it-yourself)

## Why this matters

Ask PostgreSQL for the two countries with the most paid revenue, and it answers DE and IN. Switch off its parallel workers, the helper processes that let one query use several CPUs, and the same query on the same rows answers DE and JP. <!-- L47 --> Nothing is broken. IN and JP have exactly the same revenue, and the query never said which of them comes first.

Ask for the customers who have never placed an order, and it answers 1,000. Change one order so that its customer is unknown, and the same question written with NOT IN answers 0, while written with NOT EXISTS it still answers 1,000. <!-- L59 --> Nothing is broken here either. Both answers follow from rules that fit on a page, and this post is that page: the order in which SQL evaluates the clauses of a SELECT, and what each clause does to the rows, NULLs included.

## The problem

You write a SELECT in one order and SQL evaluates it in another. A **clause** is one keyword-led part of the statement, such as WHERE or ORDER BY. The written order puts SELECT first. PostgreSQL's reference for SELECT defines the result in a different order, the **logical order** of evaluation: <!-- L01 -->

| Step | Clause | What it does to the table | Written |
|---|---|---|---|
| 1 | FROM, JOIN | builds one table from the tables named, pairing their rows | 2nd |
| 2 | WHERE | keeps the rows for which a condition is true | 3rd |
| 3 | GROUP BY | collapses rows that share values into one row per group, and computes the totals | 4th |
| 4 | HAVING | keeps the groups for which a condition is true | 5th |
| 5 | SELECT | computes the output columns | 1st |
| 6 | DISTINCT | removes duplicate output rows | with SELECT |
| 7 | ORDER BY | sorts the rows | 6th |
| 8 | LIMIT, OFFSET, FETCH | keeps a slice of them | 7th |

UNION and its relatives combine whole SELECTs between steps 6 and 7, and WITH, which comes later in this series, runs before step 1. <!-- L01 -->

Three consequences follow. The first is about names. An **alias** is a name you give an output column in SELECT, as in `sum(o.amount_cents) as revenue_cents`. It is created at step 5, so at step 2 it does not exist yet: PostgreSQL rejects `where revenue_cents > …` with *column "revenue_cents" does not exist*, and accepts the same name in ORDER BY, at step 7. <!-- L02 --> <!-- L53 --> PostgreSQL also accepts an alias in GROUP BY, which strict SQL does not. <!-- L09 -->

The second is about totals. An **aggregate** is a function such as `count` or `sum` that turns a group of rows into one value, and a condition on one, such as `count(*) > 66666`, cannot go in WHERE, because at step 2 there is no group yet to count. PostgreSQL says *aggregate functions are not allowed in WHERE*. <!-- L52 --> The third is about order. Until step 7 the rows have none, and after it they have only as much as the sort keys give them: rows that are equal on every key come back in an order PostgreSQL does not promise. <!-- L12 -->

So the problem is concrete. Given a query and its tables, predict how many rows survive each step, and which ones, including where a NULL changes the answer.

One boundary first. The logical order defines what the result must be, not the order in which the server does the work. PostgreSQL's own reference says that where it can, it computes the SELECT list after sorting and limiting, which is step 5 after step 8. <!-- L03 --> The rows are the same either way, and the rows are the only promise. How the server actually runs a query comes later in this series.

## Worked example

Start small enough to check by hand. The lab's sample is 20 rows: 6 customers and 14 orders, with the same columns as the full tables. It is built by hand so that each effect in this post happens at least once. Figure 1 shows all 20.

![The 20-row sample: six customers, customer 6 marked as having no orders, and fourteen orders, customer 1's two paid orders marked](FIG_01)

*Figure 1 — The 20-row sample. Customer 6 has never ordered, customer 1 has two paid orders, and IN and JP end up with the same paid revenue, 7,000 cents each.*

The report is the one part 4 asked, cut to the top two: paid revenue per country.

```sql
select c.country,
       count(*)            as paid_orders,
       sum(o.amount_cents) as revenue_cents
from customers c
join orders o on o.customer_id = c.id
where o.status = 'paid'
group by c.country
order by revenue_cents desc
limit 2;
```

Evaluate it in the logical order and count the rows after each step.

1. **FROM and JOIN.** A **join** pairs each row of one table with the rows of another for which a **join condition** is true, here `o.customer_id = c.id`. Each of the 14 orders finds its one customer: 14 rows. Customer 6 has no order, pairs with nothing, and is not among them.
2. **WHERE.** `o.status = 'paid'` is true for orders 101, 102, 104, 107, 110 and 111: 6 rows.
3. **GROUP BY.** The 6 rows have three countries, so they collapse into 3 groups. DE has orders 101, 102 and 110: 3 orders, 9,500 cents. IN has order 104: 1 order, 7,000 cents. JP has 107 and 111: 2 orders, 7,000 cents. `count(*)` and `sum(...)` are computed once per group. <!-- L49 -->
4. **HAVING** is absent, so all 3 groups pass.
5. **SELECT** computes three columns per group and names the third `revenue_cents`.
6. **ORDER BY** sorts by revenue, largest first: DE, then IN and JP, tied at 7,000.
7. **LIMIT 2** keeps the first two rows.

The lab runs the same steps on the full shop, whose tables need one addition first. The series' generator gives order number *g* to customer 1 + (7,919 × *g* mod 100,000). Because 7,919 shares no factor with 100,000, each run of 100,000 consecutive orders picks every customer exactly once, so each of the 100,000 customers has exactly 10 orders. <!-- L44 --> A left join, the subject of the next section, would then have nothing to show, so the lab adds 1,000 customers who have never ordered. <!-- L43 --> Figure 2 lines up the steps, where each is written, and the row count after each on both datasets.

![The eight clauses in evaluation order, FROM to LIMIT, each with its written position and the row count after it, sample and full](FIG_02)

*Figure 2 — The logical order, with the report's row count after each clause. SELECT is written first and evaluated fifth.*

At full scale the counts are 101,000 customers, 1,000,000 rows after the join because every order has a customer, 333,333 after WHERE because every third order is paid, and 5 groups, one per country. <!-- L44 --> <!-- L46 --> Every count on the sample matched the hand count above; the lab's runner stops if one does not. <!-- L49 --> This is the full result before LIMIT:

```text
 country | paid_orders | revenue_cents
---------+-------------+---------------
 DE      |       66667 |    3333366716
 IN      |       66667 |    3333366679
 JP      |       66666 |    3333366679
 BR      |       66667 |    3333266642
 US      |       66666 |    3333166605
(5 rows)
```

IN and JP have exactly the same paid revenue, 3,333,366,679 cents, at full scale as in the sample. <!-- L46 --> So which country is second? The query does not say, and PostgreSQL's reference is explicit: rows equal on every ORDER BY expression come back in an implementation-dependent order. <!-- L12 --> LIMIT 2 keeps whichever of the two reaches second place, and that depends on how the server computed the groups.

The lab asked the same question under five planner settings. With the defaults it got DE and IN. With `max_parallel_workers_per_gather = 0`, which stops PostgreSQL splitting the query across helper processes, it got DE and JP. <!-- L47 --> Who those helpers are is the subject of *How PostgreSQL Uses Processes*, part 2 of this series. The default plan hands the five country totals to the final sort in alphabetical order, BR, DE, IN, JP, US. The plan without helpers builds the totals in a hash table and hands them on as US, BR, JP, IN, DE, with JP ahead of IN. <!-- L47 --> The data did not change and neither answer is wrong. Figure 3 shows the boundary.

![Five country totals by paid revenue, IN and JP tied on the LIMIT 2 line; the default plan keeps IN, the plan without parallel workers JP](FIG_03)

*Figure 3 — A tie on the boundary. LIMIT 2 keeps whichever tied row the sort placed second, and that depends on the plan; WITH TIES keeps both.*

Two changes make the answer definite. A **tiebreaker** is a second sort key that makes the order unique: `order by revenue_cents desc, c.country` always puts IN before JP. The other admits the tie: `fetch first 2 rows with ties`, available since PostgreSQL 13, returns every row that ties with the last one kept, here DE, IN and JP. <!-- L15 --> <!-- L16 --> <!-- L47 --> Which one is right depends on the report. A LIMIT with neither leaves the choice to the plan, and PostgreSQL's documentation warns that such a query can return different rows on different runs. <!-- L14 -->

## Intuition

Think of a SELECT as a pipeline. Each clause takes a table and hands a new one to the next: FROM builds it, WHERE thins it, GROUP BY collapses it, HAVING thins the groups, SELECT reshapes the columns, ORDER BY arranges the rows and LIMIT cuts them. To predict a query, walk the pipeline and ask at each step what table comes out.

Three rules carry most of what follows.

- **FROM builds the rows, and a join can multiply them.** A row of one table appears once for every row of the other that it matches. Nothing later in the pipeline can tell a repeated row from one stored twice.
- **WHERE and HAVING keep only true.** A condition can be true, false or unknown, and unknown is what any comparison with NULL gives, as part 4 showed with `= NULL`. A row or a group survives only when its condition is true. <!-- L04 -->
- **Order exists only from ORDER BY on,** and only as far as its keys go.

The pipeline picture breaks at one point, and the point matters. The logical order says what the result must be, not what the server does first. Part 4 followed a query through PostgreSQL's planner, the stage that chooses how to compute a result, and the planner may reorder the work freely as long as the same rows come out. The lab caught it once: PostgreSQL moved a HAVING condition into WHERE so that it ran before grouping. <!-- L26 --> <!-- L51 --> The documentation names another case: it computes the SELECT list after LIMIT when it can. <!-- L03 --> PostgreSQL 19, in beta, will even aggregate some rows before joining them. <!-- L24 --> Use the pipeline to predict *what* comes out, never *how* or *how fast*.

## What does FROM build?

An **inner join**, written as plain `join`, returns one row for each pair of rows that satisfies the join condition. <!-- L05 --> A customer with no orders matches nothing and disappears. Sometimes that is the point; in a report of all customers it is a bug.

A **left join**, in full a LEFT OUTER JOIN, keeps every row of the table on its left. It starts from the inner join and adds one row for each left row that matched nothing, with NULL in every column from the right-hand table. <!-- L05 --> Call that added row a **padded row**: it is how NULLs enter a result from tables that store none. Reach for a left join when the question says "including those with none". Figure 4 shows both joins on the sample.

![The sample's left join: the inner join's 14 rows plus customer 6's row padded with NULLs, 15 in all](FIG_04)

*Figure 4 — Inner join against left join. The left join adds one row for each customer with no match, padded with NULLs.*

On the full shop the inner join gives 1,000,000 rows and the left join 1,001,000: one padded row for each of the 1,000 new customers. <!-- L50 -->

The trap comes when you filter. Put the paid condition back:

```sql
select count(*)
from customers c
left join orders o on o.customer_id = c.id
where o.status = 'paid';
```

This returns 333,333, the same as the inner join. <!-- L50 --> Each padded row has a NULL status, `NULL = 'paid'` is unknown, and WHERE drops the row. The WHERE clause has undone the left join, and PostgreSQL agrees: its plan for this query has an ordinary inner hash join and no left join at all. <!-- L50 -->

Move the condition into the join's ON clause and the left join survives:

```sql
select count(*)
from customers c
left join orders o on o.customer_id = c.id and o.status = 'paid';
```

This returns 334,333: the 333,333 paid rows, plus one padded row for each of the 1,000 customers who have never ordered. <!-- L50 --> The queries differ only in where one condition sits. A condition in ON decides which rows count as a match, before the padding; a condition in WHERE filters after it. <!-- L06 --> For an inner join that makes no difference, and for an outer join it is the whole difference. Figure 5 follows customer 6 through both.

![Customer 6's padded row: kept when status = 'paid' is in ON, dropped when it is in WHERE because NULL = 'paid' is unknown](FIG_05)

*Figure 5 — The same condition in two places. In ON it decides what counts as a match; in WHERE it filters afterwards, and every padded row fails it.*

A right join is a left join with the tables swapped, and a full join pads both sides; the same rules apply to both. <!-- L05 -->

## WHERE or HAVING, and where does NULL land?

WHERE filters rows before they are grouped. **HAVING** filters the groups that GROUP BY creates. <!-- L07 --> Some conditions could go in either. Here is the paid condition both ways, in a report grouped by country and status:

```sql
select c.country, o.status, count(*)
from customers c join orders o on o.customer_id = c.id
where o.status = 'paid'
group by c.country, o.status;

select c.country, o.status, count(*)
from customers c join orders o on o.customer_id = c.id
group by c.country, o.status
having o.status = 'paid';
```

Both return the same 5 rows, but logically they do different work. The WHERE version groups 333,333 rows into 5 groups. The HAVING version groups all 1,000,000 rows into 15 groups, five countries times three statuses, and then discards 10 of them. <!-- L51 --> Figure 6 draws both paths.

![Two logical paths for one condition: WHERE filters 1,000,000 rows to 333,333 before grouping, HAVING groups first; one identical plan](FIG_06)

*Figure 6 — WHERE against HAVING on the same condition: logically different work, the same answer and, in PostgreSQL, the same plan.*

Physically, PostgreSQL did the same work both times. The two plans are identical line for line: the condition is a `Filter` on the scan of `orders`, below the grouping. <!-- L51 --> The planner moves a HAVING condition into WHERE whenever it uses no aggregate, so that rows are discarded before grouping instead of after. <!-- L26 --> Exercise E2 has you find it in the plan.

A condition on an aggregate has no such choice. `count(*) > 66666` is an error in WHERE, and in HAVING it keeps 10 of the 15 groups, the ones with 66,667 orders. <!-- L52 --> In a long critique of SQL in 1984, C. J. Date wrote that the reason for HAVING is not apparent to a user, who asks why a WHERE clause will not do. <!-- L30 --> The logical order is the answer: WHERE runs before any group exists.

### Where does NULL land in GROUP BY?

Group the left join instead, and the padded rows must go somewhere:

```sql
select c.country, o.status,
       count(o.id)         as orders,
       sum(o.amount_cents) as revenue_cents
from customers c
left join orders o on o.customer_id = c.id
group by c.country, o.status;
```

This gives 20 groups: the 15 real ones, plus 5 whose status is NULL, one per country. <!-- L54 --> Each NULL group holds the 200 padded rows of that country's new customers. `count(o.id)` is 0 for it, and `sum(o.amount_cents)` is NULL, because every amount it sees is NULL. <!-- L54 --> GROUP BY put each country's NULLs into a single group, although `NULL = NULL` is not true. SQL treats NULL in three ways: WHERE keeps only rows whose condition is true, a constraint holds unless it is false, and grouping and set operations treat two NULLs as equal. <!-- L40 --> It was not always so for grouping. In the SQL Date described in 1984, nulls counted as duplicates for DISTINCT and ORDER BY but not for GROUP BY. <!-- L29 -->

Now sort that report by revenue, largest first, and keep five rows: add `order by revenue_cents desc limit 5`. The top five are the five NULL groups. <!-- L54 --> PostgreSQL sorts NULL as if it were larger than every value, so NULLs come first in a descending sort and last in an ascending one. <!-- L13 --> Figure 7 shows the ranking.

![Twenty groups ranked by revenue descending: the five NULL groups on top, then the real ones, with JP paid and IN paid tied](FIG_07)

*Figure 7 — NULLs sort first in a descending sort. The report's top five are the five empty groups unless the query says NULLS LAST.*

Write `order by revenue_cents desc nulls last` and the top five are JP refunded, JP shipped, DE refunded, DE paid and JP paid. With ties allowed, IN paid joins them, level with JP paid at 3,333,366,679 cents: the same tie as before. <!-- L54 -->

## Why does NOT IN return nothing once a NULL appears?

A **subquery** is a SELECT inside another statement. Two ways of testing against one look interchangeable. `x IN (subquery)` is true when `x` equals some value the subquery returns, and NOT IN is its negation. `EXISTS (subquery)` is true when the subquery returns at least one row, and NOT EXISTS is its negation. <!-- L17 --> <!-- L18 --> Here are both, asking which customers have never placed an order:

```sql
select count(*) from customers
where id not in (select customer_id from orders);

select count(*) from customers c
where not exists (select 1 from orders o where o.customer_id = c.id);
```

Both answer 1,000: the new customers. So do a left join that keeps only the padded rows, with `where o.id is null`, and `select id from customers except select customer_id from orders`. <!-- L58 -->

Now let one order lose its customer, as happens in real data when a value was never recorded. The lab drops the NOT NULL rule on `orders.customer_id` and sets it to NULL on order 4242, whose customer has nine other orders. NOT EXISTS, the left join and EXCEPT still answer 1,000. NOT IN answers 0. <!-- L59 -->

The reason is in what NOT IN means. `x NOT IN (a, b, c)` is the same as `x <> a AND x <> b AND x <> c`, so it is true only if every comparison is true. <!-- L18 --> For customer 100,001 that is a million comparisons. 999,999 of them are true, and one is `100001 <> NULL`, which is unknown. True AND unknown is unknown, so the whole test is unknown, and WHERE keeps only true. <!-- L04 --> The lab checks the pieces directly: `100001 not in (1, 2)` is true and `100001 not in (1, 2, null)` is NULL. <!-- L60 --> The same happens to every customer at once. As Leonid Libkin put it, NOT IN against a subquery holding a single NULL returns nothing, whatever the outer table holds. <!-- L34 -->

NOT EXISTS asks a different question: is there a row in `orders` whose `customer_id` equals this customer's `id`? For customer 100,001 there is none, because the NULL order equals nothing, so NOT EXISTS is true and the customer is kept. Figure 8 puts the two side by side. IN, by contrast, is safe here: a customer with a matching order is true, and one without is NULL instead of false, which WHERE drops all the same. <!-- L19 -->

![NOT IN for customer 100,001 unrolled into ANDed comparisons, one against NULL and unknown; beside it NOT EXISTS finds no match](FIG_08)

*Figure 8 — One NULL in the list makes NOT IN unknown for every customer. NOT EXISTS never compares anything with the NULL; it looks for a matching row.*

This is not a quirk of the lab's data. On two tiny tables, R = {1, NULL} and S = {NULL}, the three usual ways of writing "R minus S" give three different answers. The example is Paolo Guagliardo and Libkin's, whose formal semantics of SQL matched PostgreSQL and Oracle on 100,000 random queries, <!-- L36 --> <!-- L39 --> and the lab ran it on PostgreSQL 18.6: <!-- L62 -->

| Query (R = {1, NULL}, S = {NULL}) | Rows returned |
|---|---|
| `select a from r where a not in (select a from s)` | none |
| `select a from r where not exists (select 1 from s where s.a = r.a)` | 1 and NULL |
| `select a from r except select a from s` | 1 |

### Which answer is right?

That is argued, and has been for decades. If the NULL means "this order's customer is unknown", any of the 1,000 new customers might be that customer, and NOT IN's empty answer is the cautious one. If it means "this order has no customer", NOT EXISTS is right. Claude Rubinson argued in 2007 that SQL answers exactly the question it is asked: under three-valued logic, a condition such as "the cities are different" means "the cities are *known* to be different". <!-- L31 --> By that reading, NOT IN asks for the customers *known* not to be in the list, and with a NULL in the list there are none. Date and John Grant replied that the result differs from the answer in the real world, and Grant put the fault in how SQL uses its third value rather than in having one. <!-- L32 --> <!-- L33 --> Database theory frames the question with **certain answers**: a row is a certain answer if it is in the result however the NULLs are filled in. Libkin showed that SQL's answers are not certain answers in general: with negation in a subquery, SQL can return rows that are not certain. <!-- L35 -->

The practical rule is less contested. Write NOT EXISTS when you mean "has no matching row", and declare NOT NULL on any column that must have a value; Rubinson's own advice was non-nullable columns by default. <!-- L31 --> Rewriting NOT IN as NOT EXISTS is often presented as harmless, and Libkin and Liat Peterfreund note that many programmers do not know it changes the answer once a NULL appears. <!-- L41 -->

There is a second reason, physical rather than logical. The planner turns IN and EXISTS into a **semi-join**, a join that keeps each left row once if it has a match, and NOT EXISTS into an **anti-join**, which keeps each left row that has none. It leaves NOT IN alone, because inside a NOT it cannot tell a false comparison from an unknown one. <!-- L27 --> It then keeps the subquery's values in an in-memory hash table only if they fit in hash memory, by default `work_mem`'s 4 MB times a `hash_mem_multiplier` of 2. <!-- L23 --> <!-- L28 --> `work_mem` is the per-operation memory budget described in *How PostgreSQL Uses Memory*, part 1 of this series. A million customer ids do not fit, so PostgreSQL re-read the subquery's rows for each customer. In this lab NOT IN took 117.5 seconds, NOT EXISTS took 46.3 milliseconds, and NOT IN with `work_mem` raised to 64 MB took 191.9 milliseconds. <!-- L58 --> PostgreSQL 19, in beta, turns NOT IN into an anti-join when it can prove that no NULL is present. <!-- L24 --> Finding and fixing slow queries comes later in this series.

## Where do duplicate rows come from?

Ask which customers have a paid order, three ways:

```sql
select count(*) from customers c
join orders o on o.customer_id = c.id
where o.status = 'paid';

select count(*) from customers c
where c.id in (select customer_id from orders where status = 'paid');

select count(*) from customers c
where exists (select 1 from orders o
              where o.customer_id = c.id and o.status = 'paid');
```

The join returns 333,333 rows, one per paid order, because 66,667 customers have 3 paid orders and 33,333 have 4. IN and EXISTS return 100,000, one per customer. <!-- L45 --> <!-- L55 --> That repetition is called **fan-out**: a join repeats a row of one table once for every row it matches in the other. <!-- L37 --> EXISTS cannot fan out, because it produces at most one row per outer row however many rows match. <!-- L17 --> PostgreSQL's plans show how it keeps that promise: for both EXISTS and IN it first reduces the paid orders to their distinct customer ids, and only then joins. <!-- L55 -->

`select distinct` over the join also gives 100,000, by removing the repeats after creating them. In more than 33,000 queries written by students, Toni Taipalus and colleagues found both failure modes, results with many duplicate rows and a DISTINCT that might remove duplicates that matter, and found that joins written with IN produced duplicate rows less often than explicit joins. <!-- L42 -->

Fan-out does its real damage inside a total. Say you want paid and refunded revenue side by side, and you join `orders` twice:

```sql
select c.country,
       sum(p.amount_cents) as paid_cents,
       sum(r.amount_cents) as refunded_cents
from customers c
join orders p on p.customer_id = c.id and p.status = 'paid'
join orders r on r.customer_id = c.id and r.status = 'refunded'
group by c.country;
```

A customer with 3 paid and 4 refunded orders now produces 12 rows, and each paid amount is added 4 times. The two joins produced 1,099,998 rows from 1,000,000 orders, and BR's paid revenue came out at 10,999,670,037 cents instead of 3,333,266,642: 3.3 times too high. <!-- L56 --> On the sample, in Figure 9, the same query doubles DE's refunded total and drops customer 4's paid order, because customer 4 has no refunded order to pair with. <!-- L56 --> The repair is one join and two filtered sums. `sum(o.amount_cents) filter (where o.status = 'paid')` adds only the rows its FILTER condition is true for. <!-- L20 -->

![A join repeats customer 1 once per paid order while EXISTS keeps it once; two joins to orders count its refunded amount twice](FIG_09)

*Figure 9 — Fan-out. A join repeats a row once per match; two joins to the same table multiply, and every total computed after them is inflated.*

### UNION and UNION ALL

UNION stacks the rows of two queries, and removes duplicates exactly as DISTINCT does unless you write UNION ALL. <!-- L11 --> The customer ids of the paid orders are 333,333 rows, and so are those of the refunded orders. UNION ALL returns 666,666 rows; UNION returns 100,000. <!-- L57 --> The 100,000 is not the overlap between the two lists. UNION removes duplicates inside each input as well as across them, so the paid list UNIONed with itself also returns 100,000. <!-- L57 --> Figure 10 shows it on the sample. In the SQL Date described in 1984, UNION always removed duplicates and had no ALL option at all. <!-- L29 -->

![Paid-order ids 1, 1, 2, 3, 4, 5 and refunded-order ids 1, 2, 5, 3: UNION ALL keeps all ten, UNION keeps five](FIG_10)

*Figure 10 — UNION ALL keeps every row; UNION removes duplicates inside each input as well as across them.*

UNION also treats NULLs as equal, as DISTINCT does. <!-- L10 --> <!-- L38 --> After order 4242 lost its customer, the paid list held one NULL, and UNION returned 100,001 rows: the 100,000 ids and one NULL. <!-- L61 --> Use UNION ALL unless you want duplicates removed; PostgreSQL's documentation notes that it is usually much faster. <!-- L11 -->

## The math

Two pieces of formalism account for the counts in this post.

**Tables are bags.** A **bag** is a collection in which the same row can occur more than once, and an SQL table is a bag unless a key forbids it. Write $\#(t, T)$ for the number of times row $t$ occurs in table $T$. Guagliardo and Libkin define the operations used here by what they do to those counts. <!-- L37 --> For a product of two tables:

$$
\#\big((t_1, t_2),\ T_1 \times T_2\big) = \#(t_1, T_1)\cdot\#(t_2, T_2)
$$

A pair occurs as many times as the product of its parts' counts. A join is a product followed by a filter, so a customer with $p_c$ matching orders appears $p_c$ times, and the join of customers to their paid orders has

$$
\sum_c p_c = 66{,}667 \times 3 + 33{,}333 \times 4 = 333{,}333
$$

rows, the count the lab printed. <!-- L45 --> <!-- L55 --> The double join multiplies two such counts per customer, $\sum_c p_c\, r_c$ for $r_c$ refunded orders, which came to 1,099,998. <!-- L56 --> UNION ALL adds counts and UNION caps each count at 1:

$$
\#(t,\ A \cup_{\text{all}} B) = \#(t, A) + \#(t, B) \qquad \#(t,\ A \cup B) = \min\bigl(1,\ \#(t, A) + \#(t, B)\bigr)
$$

which is why the paid ids UNIONed with themselves come back as 100,000 rows, not 333,333. <!-- L57 -->

**NOT IN is a conjunction.** Write $\top$, $\bot$ and $U$ for true, false and unknown. For a value $x$ and a subquery returning $v_1, \dots, v_n$:

$$
x \notin \{v_1, \dots, v_n\} \;\equiv\; (x \ne v_1) \wedge (x \ne v_2) \wedge \cdots \wedge (x \ne v_n)
$$

NOT IN is a chain of inequalities joined by AND. <!-- L18 --> AND is $\top$ only when every term is $\top$, and $x \ne \text{NULL}$ is $U$ for every $x$. So once one $v_i$ is NULL, the result is $\bot$ if some $v_j$ equals $x$ and $U$ otherwise. It is never $\top$, and WHERE keeps nothing. <!-- L34 --> For customer 100,001 the chain has a million terms, 999,999 of them $\top$ and one $U$, and the result is $U$.

<details>
<summary>Certain answers, in one definition</summary>

Write $D$ for a database with NULLs, and $\llbracket D \rrbracket$ for the set of complete databases obtained by replacing each NULL with a value. The certain answers to a query $Q$ are the rows that are in its result in every one of them: <!-- L35 -->

$$
\operatorname{certain}(Q, D) = \bigcap_{D' \in \llbracket D \rrbracket} Q(D')
$$

In the lab, order 4242's NULL could be replaced by any customer id. Replace it with 100,001 and customer 100,001 has an order, so none of the new customers is *certainly* without orders, and the certain answer to "customers with no orders" is empty. That happens to be what NOT IN returned. NOT EXISTS returned the 1,000 customers who have no order in the data as stored. Neither is a bug; they answer different questions about the same NULL.

</details>

## Implementation

The lab packages every query in this post. `shopgen.py` loads the two tables, with `--orderless 1000` for the new customers. `sample.sql` loads the 20-row sample. `run_lab.py` runs every query in this post and saves the output, `check.py` marks your exercises, and `broken.sql` holds the three broken queries of exercise E4.

You need Python 3 with no extra packages, and a PostgreSQL server you start yourself on a throwaway data directory:

```bash
initdb -D /path/pgdata -U postgres --encoding=UTF8 --locale=C.UTF-8
pg_ctl -D /path/pgdata -o "-k /path/sock -h ''" -l /path/server.log -w start
PGBIN=/path/to/postgres/bin PGSOCK=/path/sock python3 run_lab.py
```

The run takes about four and a half minutes, and nearly all of it is the two NOT IN queries above. Every other NOT IN in the lab raises `work_mem` for its own session so that it takes a fraction of a second, which changes the plan and not the answer. <!-- L58 --> When you are done, stop the server and delete the directory:

```bash
pg_ctl -D /path/pgdata -m fast stop
rm -rf /path/pgdata /path/sock
```

> [!WARNING]
> The lab drops a NOT NULL rule and sets one order's customer to NULL. Run it only against a server you created for it, never against a database you care about.

The captures were made on 2026-10-02 with PostgreSQL 18.6 and its default configuration, on a temporary server deleted after the run. <!-- L43 --> The files are under [Lab downloads](#lab-downloads).

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** `NOT IN (select …)` over a column that can hold NULL. It returns the right answer until the column holds its first NULL; then it returns no rows, raises no error, and a dashboard quietly reads zero. Write NOT EXISTS, and declare NOT NULL wherever a value is required.

- **A WHERE on the right-hand table of a LEFT JOIN** turns it back into an inner join. The symptom is a report that silently drops the very rows it was written to include. Put the condition in ON.
- **Wrapping a column in `max()` to silence the GROUP BY error.** In a grouped query, a column that is not grouped may appear only inside an aggregate, unless the grouping includes its table's primary key, so `having o.amount_cents >= 90000` is rejected. <!-- L08 --> `having max(o.amount_cents) >= 90000` runs, and asks a different question: in the lab it reported 200,000 big orders per country instead of 20,000. <!-- L63 --> A condition about rows belongs in WHERE.
- **DISTINCT as the fix for a join that repeats rows.** It hides the repetition in a list of names and does nothing for a total computed before it. <!-- L42 -->
- **LIMIT without a unique ORDER BY.** Ties make the result depend on the plan, as the IN and JP rows showed. <!-- L14 -->
- **Reading the logical order as the execution order.** It predicts what comes out, not what runs first or how long it takes.
- **One machine, one plan.** On another machine the tie in this post may fall the other way. That is the lesson, not a flaw in the measurement.

## Key takeaways

- SQL evaluates a SELECT in a fixed logical order, FROM, WHERE, GROUP BY, HAVING, SELECT, DISTINCT, ORDER BY, LIMIT, so an alias exists in ORDER BY but not in WHERE, and a condition on a total works only in HAVING.
- FROM builds the rows, and a join repeats a row once per match; EXISTS and IN never do, and a second join to the same table multiplies every total after it.
- WHERE and HAVING keep only rows whose condition is true, so a WHERE on the right-hand table of a LEFT JOIN discards every padded row; conditions for an outer join belong in ON.
- One NULL in a NOT IN subquery makes it return nothing; NOT EXISTS asks whether a matching row exists and is unaffected.
- Rows that tie on every ORDER BY key come back in no promised order, so a top-N query needs a tiebreaker or WITH TIES.

## Try it yourself

The lab's README has four exercises, each with a self-check that `check.py` marks for you. Start each one from fresh data with `python3 shopgen.py --scale M --orderless 1000 --db shoplab --drop`.

1. **E1, reproduce.** Run `python3 check.py e1`. Self-check: the row count after each clause, and the five revenue rows, match the worked example.
2. **E2, inspect.** EXPLAIN the HAVING version of the paid-status query and find where `status = 'paid'` is applied; then run `python3 check.py e2`. Self-check: you can name the plan node, and the plan equals the WHERE version's.
3. **E3, predict.** `python3 check.py e3` prints six queries. Write down which of them will change when order 4242 loses its customer, then run `python3 check.py e3 --predict <numbers>`. Self-check: the right set, for the right reasons.
4. **E4, diagnose.** `python3 check.py e4 --break` injects the NULL. Repair the three queries in `broken.sql` and run `python3 check.py e4 --verify`. Self-check: a symptom, a cause, a proof and a repair for each.

<details><summary>Answers</summary>

**E1:** 101,000; 1,000,000; 333,333; 5 groups; DE 3,333,366,716 · IN 3,333,366,679 · JP 3,333,366,679 · BR 3,333,266,642 · US 3,333,166,605. <!-- L46 --> **E2:** a Filter on the scan of `orders`, below the aggregate; the two plans are identical. <!-- L51 --> **E3:** queries 1, 3 and 6. The join count falls by one, NOT IN falls to 0, and GROUP BY customer_id gains a group for the NULL. <!-- L61 --> **E4:** query A multiplies two joins, and FILTER repairs it; B is NOT IN over a NULL, and NOT EXISTS repairs it, returning 1,000; C filters groups where it meant rows, and WHERE repairs it. <!-- L56 --> <!-- L64 --> <!-- L63 -->

</details>

## References

### Lab downloads

- [`README.md`](LAB_01) — what the lab needs, how to run it, the four exercises in full, and how to clean up.
- [`shopgen.py`](LAB_02) — creates the database and loads `customers` and `orders`; `--orderless` adds the customers who never ordered.
- [`sample.sql`](LAB_03) — the 20-row sample from the worked example.
- [`run_lab.py`](LAB_04) — runs every query in this post and writes the two capture files.
- [`check.py`](LAB_05) — marks your own run against the author's, one exercise at a time.
- [`broken.sql`](LAB_06) — the three broken queries of exercise E4.
- [`captures.md`](LAB_07) — the author's run: every statement and its output, verbatim.
- [`captures.json`](LAB_08) — the same run as numbers, which `check.py` reads.
- [Complete lab](https://minio.canery.in/media/lab-sql-select-evaluation-joins-group-by-null.zip) — every file above in one zip.

### Sources

All web pages accessed 2026-10-02.

1. Date, C. J. "A Critique of the SQL Database Language." *ACM SIGMOD Record* 14(3), 8–54, 1984. https://doi.org/10.1145/984549.984551
2. Rubinson, C. "Nulls, Three-Valued Logic, and Ambiguity in SQL: Critiquing Date's Critique." *ACM SIGMOD Record* 36(4), 13–17, 2007. https://doi.org/10.1145/1361348.1361350
3. Date, C. J. "A Critique of Claude Rubinson's Paper Nulls, Three-Valued Logic, and Ambiguity in SQL: Critiquing Date's Critique." *ACM SIGMOD Record* 37(3), 20–22, 2008. https://doi.org/10.1145/1462571.1462574
4. Grant, J. "Null Values in SQL." *ACM SIGMOD Record* 37(3), 23–25, 2008. https://doi.org/10.1145/1462571.1462575
5. Libkin, L. "SQL's Three-Valued Logic and Certain Answers." *18th International Conference on Database Theory (ICDT 2015)*, LIPIcs 31, 94–109, 2015. https://doi.org/10.4230/LIPIcs.ICDT.2015.94
6. Guagliardo, P., and Libkin, L. "A Formal Semantics of SQL Queries, Its Validation, and Applications." *Proceedings of the VLDB Endowment* 11(1), 27–39, 2017. https://doi.org/10.14778/3151113.3151116
7. Libkin, L., and Peterfreund, L. "SQL Nulls and Two-Valued Logic." *Proceedings of the 42nd ACM Symposium on Principles of Database Systems (PODS 2023)*, 11–20, 2023. https://doi.org/10.1145/3584372.3588661
8. Taipalus, T., Siponen, M., and Vartiainen, T. "Errors and Complications in SQL Query Formulation." *ACM Transactions on Computing Education* 18(3), 1–29, 2018. https://doi.org/10.1145/3231712
9. PostgreSQL 18 documentation, SELECT. https://www.postgresql.org/docs/18/sql-select.html
10. PostgreSQL 18 documentation, §7.2 Table Expressions. https://www.postgresql.org/docs/18/queries-table-expressions.html
11. PostgreSQL 18 documentation, §7.3 Select Lists. https://www.postgresql.org/docs/18/queries-select-lists.html
12. PostgreSQL 18 documentation, §7.4 Combining Queries. https://www.postgresql.org/docs/18/queries-union.html
13. PostgreSQL 18 documentation, §7.5 Sorting Rows. https://www.postgresql.org/docs/18/queries-order.html
14. PostgreSQL 18 documentation, §7.6 LIMIT and OFFSET. https://www.postgresql.org/docs/18/queries-limit.html
15. PostgreSQL 18 documentation, §9.24 Subquery Expressions. https://www.postgresql.org/docs/18/functions-subquery.html
16. PostgreSQL 18 documentation, §4.2.7 Aggregate Expressions. https://www.postgresql.org/docs/18/sql-expressions.html
17. PostgreSQL 18 documentation, §19.4 Resource Consumption. https://www.postgresql.org/docs/18/runtime-config-resource.html
18. PostgreSQL 13 release notes. https://www.postgresql.org/docs/18/release-13.html
19. PostgreSQL 19 release notes, beta. https://www.postgresql.org/docs/19/release-19.html
20. PostgreSQL versioning policy. https://www.postgresql.org/support/versioning/
21. PostgreSQL 18.6 source, `planner.c`. https://github.com/postgres/postgres/blob/REL_18_6/src/backend/optimizer/plan/planner.c
22. PostgreSQL 18.6 source, `prepjointree.c`. https://github.com/postgres/postgres/blob/REL_18_6/src/backend/optimizer/prep/prepjointree.c
23. PostgreSQL 18.6 source, `subselect.c`. https://github.com/postgres/postgres/blob/REL_18_6/src/backend/optimizer/plan/subselect.c
