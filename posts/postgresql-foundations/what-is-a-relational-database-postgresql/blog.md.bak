---
title: "What a Relational Database Actually Does"
slug: what-is-a-relational-database-postgresql
date: 2026-10-01
updated: 2026-10-01
summary: "A relational database stores rows as sets and turns every query into a plan. One real PostgreSQL 18 query, followed from text to rows, and two silent data bugs."
tags: [databases, postgresql, relational-model, sql, query-execution]
category: databases
categories: [databases]
series: postgresql-foundations
series_position: 4
tier: L2
difficulty: beginner
prerequisites: ["a terminal"]
reading_minutes: 23
cover_image_url: "COVER"
cover_image_alt: "Two grids of square tiles joined by a thin line, one row of the right grid shown twice in tangerine, four dots in a row beneath"
canonical_url: "https://canery.in/blogs/what-is-a-relational-database-postgresql"
---

> [!NOTE]
> **Insights** — A relational database keeps data as relations, which are sets of rows over named columns, and you ask it for *what* you want, never *how* to fetch it. Between your query and its rows, PostgreSQL runs four stages you can watch: it parses the text, rewrites it, plans the cheapest route and executes the plan. <!-- L12 --> It enforces only what you declared. On a table of 1,000,000 orders, an exact copy of one order went in without an error and moved one country's revenue by 56,954 cents, because nobody had declared a key. <!-- L31 --> <!-- L38 -->

**Level:** beginner · **You need:** a terminal; no SQL and no database experience · **Time:** ~23 min

This is part 4 of PostgreSQL Foundations, and the first part written for someone who has never used a database. It assumes nothing from the parts before it.

> [!TIP]
> **Runnable lab:** the files are listed under [Lab downloads](#lab-downloads) at the end. The post explains everything; the lab reproduces it.

Every server number below comes from one run of that lab: PostgreSQL 18.6 built from source, default configuration, on a laptop with 16 CPUs, 14 GB of RAM and an NVMe disk. The data is the series' shop: 100,000 customers and 1,000,000 orders. <!-- L31 --> Data values are exact on any machine; the cost figures shown later move by a fraction of a percent between runs. <!-- L36 -->

**Jump to:** [The problem](#the-problem) · [Worked example](#worked-example) · [Intuition](#intuition) · [What is a relation?](#what-is-a-relation-really) · [From query to rows](#what-happens-between-the-query-and-the-rows) · [Two surprises](#two-surprises-on-real-rows) · [The math](#the-math) · [Implementation](#implementation) · [Limitations](#limitations-and-common-mistakes) · [Try it yourself](#try-it-yourself)

## Why this matters

A report says revenue for one country rose overnight by 56,954 cents. Nobody deployed anything, nothing was logged as an error, and every query is the same as yesterday. The cause, which this post reproduces on real rows, is one row stored twice in a table that never promised its rows were different. <!-- L38 --> Finding it takes knowing what a relational database promises, and what it leaves to you.

That knowledge does not go out of date. E. F. Codd described the relational model in June 1970, at IBM's research laboratory in San Jose. <!-- L43 --> In 2024 Michael Stonebraker and Andrew Pavlo reviewed the alternatives proposed since, and concluded that it still dominates, and that SQL, the language used to query it, keeps absorbing its challengers' good ideas. <!-- L30 -->

## The problem

The shop has two kinds of thing. A customer has an id, a name and a country, and there are 100,000 of them. An order has an id, the customer who placed it, an amount in cents, a timestamp, and a status of `paid`, `shipped` or `refunded`; there are 1,000,000 of them. <!-- L31 --> The question is simple to say: for paid orders only, how much revenue did each country bring in?

Without a database you would write a program. It opens the customers file and reads every line into memory, opens the orders file, and for each paid order looks up the customer and adds the amount to that customer's country. It works, until the data changes underneath it.

Codd's paper opened with exactly this problem. A program written against stored records tends to depend on three things it should not: the order the records are stored in, which indexes exist, and the paths from one record to a related one. An **index** is a separate structure that finds records by the value of a field without reading all of them; you meet indexes when a lookup is too slow. Change any of the three and the programs break. Codd called the property he wanted, programs that keep working when the storage changes, *data independence*. <!-- L05 -->

The hard part does not go away. Something still has to decide which records to read first, whether an index would help, and how to pair each order with its customer. In a relational database that something is the database itself. A user of System R, IBM's 1970s relational prototype, did not say which access path to use or in which order to combine tables; the system chose both. <!-- L11 -->

## Worked example

Start with the tables. **SQL** (Structured Query Language) is the standard language of relational databases: you use it to define tables, to change their rows and to ask questions of them. PostgreSQL, the database server this post runs, implements most of the standard: at least 170 of its 177 mandatory core features. <!-- L26 --> In SQL a **table** is declared with `create table`, and these are the two declarations the lab runs, the same ones the earlier parts of this series used:

```sql
create table customers (
    id       int primary key,
    name     text not null,
    country  char(2) not null
) with (fillfactor = 90);

create table orders (
    id           int not null,
    customer_id  int not null,
    amount_cents int not null,
    created      timestamptz not null,
    status       text not null
);
```

Each line inside the parentheses declares a **column**: its name, its type, and any rule it must obey. `int` is a whole number, `text` a string of any length, `char(2)` exactly two characters, and `timestamptz` a point in time. `not null` says the column may never be left without a value. `customers.id` is declared the table's `primary key`, the column that identifies each row; `orders.id` is not. Hold on to that difference. The `with (fillfactor = 90)` clause is a storage setting that does not matter here.

A **query** is a request for data. In SQL it describes the result, not the steps to get it:

```sql
select c.country,
       sum(o.amount_cents) as revenue_cents,
       count(*)            as paid_orders
from customers c
join orders o on o.customer_id = c.id
where o.status = 'paid'
group by c.country
order by revenue_cents desc;
```

Read it clause by clause; the order in which the server evaluates the clauses comes later in this series.

- `from customers c join orders o on o.customer_id = c.id` pairs every order with the customer who placed it. That pairing is a **join**, and `c` and `o` are short names for the two tables.
- `where o.status = 'paid'` keeps paid orders only.
- `group by c.country` puts the remaining rows into one group per country.
- `sum(...)` and `count(*)` are **aggregates**, functions that turn a group of rows into one value: here, the total cents and the number of orders.
- `select` names the columns of the answer, and `order by revenue_cents desc` sorts it, largest first.

This is the answer the lab got:

```text
 country | revenue_cents | paid_orders
---------+---------------+-------------
 DE      |    3333366716 |       66667
 IN      |    3333366679 |       66667
 JP      |    3333366679 |       66666
 BR      |    3333266642 |       66667
 US      |    3333166605 |       66666
(5 rows)
```

Five rows, one per country: 333,333 paid orders and 16,666,533,321 cents in all. <!-- L33 --> The query never said which table to read first, whether to use an index, or how to find each order's customer. It named *what*; the server decided *how*.

To see what it decided, put `EXPLAIN ANALYZE` in front of the query. `EXPLAIN` is a command that prints the plan the server chose for a query, without running it. `EXPLAIN ANALYZE` runs the query as well, and prints what actually happened beside each estimate. It is the tool you reach for whenever a query is slow or returns something you did not expect. Here is its output, trimmed to the lines this post explains:

```text
Sort  (cost=18285.78..18285.79 rows=5 width=19) (actual rows=5.00 loops=1)
  ->  Finalize GroupAggregate  (actual rows=5.00 loops=1)
        ->  Gather Merge  (actual rows=15.00 loops=1)
              Workers Planned: 2
              Workers Launched: 2
              ->  Sort  (actual rows=5.00 loops=3)
                    ->  Partial HashAggregate  (actual rows=5.00 loops=3)
                          ->  Hash Join  (actual rows=111111.00 loops=3)
                                Hash Cond: (o.customer_id = c.id)
                                ->  Parallel Seq Scan on orders o  (cost=0.00..12901.33 rows=140514 width=8) (actual rows=111111.00 loops=3)
                                      Filter: (status = 'paid'::text)
                                      Buffers: shared hit=7693
                                ->  Hash  (actual rows=100000.00 loops=3)
                                      ->  Seq Scan on customers c  (actual rows=100000.00 loops=3)
```

<details>
<summary>The full output, all 37 lines</summary>

```text
 Sort  (cost=18285.78..18285.79 rows=5 width=19) (actual rows=5.00 loops=1)
   Sort Key: (sum(o.amount_cents)) DESC
   Sort Method: quicksort  Memory: 25kB
   Buffers: shared hit=9840
   ->  Finalize GroupAggregate  (cost=18284.18..18285.72 rows=5 width=19) (actual rows=5.00 loops=1)
         Group Key: c.country
         Buffers: shared hit=9837
         ->  Gather Merge  (cost=18284.18..18285.58 rows=12 width=19) (actual rows=15.00 loops=1)
               Workers Planned: 2
               Workers Launched: 2
               Buffers: shared hit=9837
               ->  Sort  (cost=17284.16..17284.17 rows=5 width=19) (actual rows=5.00 loops=3)
                     Sort Key: c.country
                     Sort Method: quicksort  Memory: 25kB
                     Buffers: shared hit=9837
                     Worker 0:  Sort Method: quicksort  Memory: 25kB
                     Worker 1:  Sort Method: quicksort  Memory: 25kB
                     ->  Partial HashAggregate  (cost=17284.05..17284.10 rows=5 width=19) (actual rows=5.00 loops=3)
                           Group Key: c.country
                           Batches: 1  Memory Usage: 32kB
                           Buffers: shared hit=9823
                           Worker 0:  Batches: 1  Memory Usage: 32kB
                           Worker 1:  Batches: 1  Memory Usage: 32kB
                           ->  Hash Join  (cost=2960.00..16230.19 rows=140514 width=7) (actual rows=111111.00 loops=3)
                                 Hash Cond: (o.customer_id = c.id)
                                 Buffers: shared hit=9823
                                 ->  Parallel Seq Scan on orders o  (cost=0.00..12901.33 rows=140514 width=8) (actual rows=111111.00 loops=3)
                                       Filter: (status = 'paid'::text)
                                       Rows Removed by Filter: 222222
                                       Buffers: shared hit=7693
                                 ->  Hash  (cost=1710.00..1710.00 rows=100000 width=7) (actual rows=100000.00 loops=3)
                                       Buckets: 131072  Batches: 1  Memory Usage: 4931kB
                                       Buffers: shared hit=2130
                                       ->  Seq Scan on customers c  (cost=0.00..1710.00 rows=100000 width=7) (actual rows=100000.00 loops=3)
                                             Buffers: shared hit=2130
 Planning:
   Buffers: shared hit=212
(37 rows)
```

</details>

It looks like a list, but it is a tree, and Figure 1 redraws it as one. Each line is one step, a **plan node**, and the arrows say which step feeds which. Rows start at the two scans at the bottom and flow upward, each step handing its output to the one above it.

![The revenue query's plan drawn as a tree: scans of orders and customers at the bottom feed a hash join, then a partial aggregate and a sort in each of three processes, then a gather merge, a final aggregate and a sort at the top, with estimated and actual row counts beside each step](FIG_01)

*Figure 1 — The plan PostgreSQL chose for the revenue question, read from the bottom up. Three processes run the lower half; the top three steps combine their results. The numbers beside each step are the planner's estimate and what actually happened.*

## Intuition

Two ideas carry the rest of the post.

The first is that a table is meant to be a **set** of rows. A set has no order and no duplicates: {Ann, Bo} is the same set as {Bo, Ann}, and adding Ann again does not make a third member. Codd's definition says this outright. In his picture of a relation as a grid, the order of the rows does not matter, and all rows are distinct. <!-- L02 --> Order and uniqueness are the two things a program over files leans on, and they are the two things the model refuses to promise or to tolerate. Remember the word *distinct*: the first surprise comes from it.

The second idea is that the server does not read your query the way you read it. It treats the query the way a compiler treats a program: as text to be checked, translated and optimised before anything runs. PostgreSQL does this in four stages, called the parser, the rewriter, the planner and the executor, and each one takes the previous one's output. <!-- L12 -->

A restaurant is a fair picture of the split between *what* and *how*. You name the dish, not the recipe, and the kitchen decides which cook, which pan and in which order. The picture breaks at the first step. A waiter takes your order in one go, but PostgreSQL checks it twice: once for grammar, using fixed rules and nothing else, and only then for meaning, by looking up every name you used. <!-- L52 --> So a misspelt keyword and a misspelt column fail at different moments, with different errors, and the section after next shows both.

## What is a relation, really?

Codd's paper defines it in one sentence. Take some sets of values: for `customers`, the possible ids, the possible names and the two-letter country codes. Codd calls each such set a **domain**, and SQL calls it a type. A **relation** on those domains is a set of rows, each taking its first value from the first domain, its second from the second, and so on. <!-- L01 --> The number of domains is the relation's **degree**: 3 for `customers` and 5 for `orders`. <!-- L32 -->

The model's words map one-to-one onto those of SQL and of psql, the command-line program for typing SQL:

| Relational model | SQL and PostgreSQL | In `orders` |
|---|---|---|
| relation | table | `orders` |
| tuple (one member of the relation) | row | order 4242 |
| attribute (one named position) | column | `amount_cents` |
| domain | type | `int` |
| degree | number of columns | 5 |

Codd also gave rows a way to be told apart. A **primary key** is a column, or a combination of columns, whose value identifies each row uniquely. <!-- L04 --> In PostgreSQL, declaring one creates a **constraint**: a rule the server checks on every insert and update, from every program that connects. A primary key must be unique and never missing, and a table can have at most one. <!-- L23 --> `customers.id` has one, which psql lists as `customers_pkey`; `orders` has none. <!-- L46 -->

A **foreign key** is a column whose values are another relation's primary-key values. <!-- L45 --> `orders.customer_id` is one in fact, pointing at `customers.id`, but nothing declares it, so nothing checks it. Figure 2 marks what is declared and what is not.

![The customers and orders tables drawn as grids of rows: customers.id marked as its declared primary key, orders with no key at all, and an arrow from orders.customer_id to customers.id marked as a foreign key that nothing declares or checks](FIG_02)

*Figure 2 — What the two tables declare. `customers` has a primary key; `orders` has none, and its link to `customers` exists only in the data.*

Declaring keys is where the later part of this series on schema design begins.

### The schema is stored as data

PostgreSQL records the fact that `orders` has five columns and no key in tables of its own. A **system catalog** is one of the tables in which the server records every table, column, type and constraint. You query it with ordinary SQL, whenever you need to know what a database actually contains rather than what someone remembers it contains. `pg_class` has a row for every table, and for everything else that has columns, such as indexes. <!-- L21 --> `pg_attribute` has a row for every column of each. <!-- L22 --> This is the lab's query against the first:

```sql
select relname, relkind, relnatts, relpages, reltuples::bigint as reltuples,
       relhasindex, pg_size_pretty(pg_relation_size(oid)) as size
from pg_class
where relname in ('customers','orders')
order by relname;
```

```text
  relname  | relkind | relnatts | relpages | reltuples | relhasindex |  size
-----------+---------+----------+----------+-----------+-------------+---------
 customers | r       |        3 |      710 |    100000 | t           | 5680 kB
 orders    | r       |        5 |     7693 |   1000000 | f           | 60 MB
(2 rows)
```

`relkind` is `r` for an ordinary table, and `relnatts` is the number of columns. `relpages` and `reltuples` are the planner's last estimates of the table's size in pages and in rows, refreshed by the maintenance commands `VACUUM` and `ANALYZE`. <!-- L21 --> A **page** is the 8 KB block in which PostgreSQL stores rows and moves them between disk and memory; *How PostgreSQL Uses Memory*, part 1 of this series, is about pages and the memory that holds them. <!-- L31 --> `relhasindex` is true for `customers`, whose primary key is an index, and false for `orders`, which has no index at all. <!-- L46 -->

The catalog describes itself as well: `pg_class` has a row for `pg_class`, with 34 columns, and one for `pg_attribute`, with 25. <!-- L32 --> Figure 3 draws those rows as pointers.

![The customers and orders tables each pointing to their own row in pg_class and to one row per column in pg_attribute, with the pg_class table pointing to its own row in pg_class](FIG_03)

*Figure 3 — The catalog describes your tables, and itself, as rows. `orders` is one row in `pg_class` and five in `pg_attribute`; `pg_class` is one row in `pg_class`, with 34 columns.*

## What happens between the query and the rows?

PostgreSQL's documentation describes the path of every query in four stages. Figure 4 lays them out, with what each stage receives and what it hands on. <!-- L12 -->

![Four stages left to right, parser, rewriter, planner and executor, with SQL text going in, a query tree passed from the parser to the rewriter, a rewritten query tree passed to the planner, a plan tree passed to the executor and rows coming out, and the system catalog consulted by the parser and the rewriter](FIG_04)

*Figure 4 — The path of every query in PostgreSQL. Each stage hands its output to the next; the executor is the one that reads the rows and returns them.*

### Stage 1: the parser checks the grammar, then the names

The **parser** turns the query text into a tree, the *query tree*, in two passes. <!-- L52 --> A misspelt keyword fails the first pass, which checks only the shape of the text against SQL's grammar:

```text
ERROR:  syntax error at or near "selec"
LINE 1: selec c.country from customers c;
        ^
```

A misspelt column passes the first pass and fails the second, which looks every name up in the system catalog:

```text
ERROR:  column c.nosuchcolumn does not exist
LINE 1: select c.nosuchcolumn from customers c;
               ^
```

The first error points at a position; the second names something missing. <!-- L34 --> The passes are separate because the catalog can only be read inside a **transaction**, a group of statements that succeed or fail together, and the server will not start one before it knows whether the text is itself a `BEGIN` or a `ROLLBACK`, the commands that open and cancel a transaction. <!-- L53 -->

### Stage 2: the rewriter expands views

A **view** is a stored query with a name, which you can query as if it were a table. The lab saves the revenue question as one:

```sql
create view paid_revenue as
select c.country, sum(o.amount_cents) as revenue_cents, count(*) as paid_orders
from customers c join orders o on o.customer_id = c.id
where o.status = 'paid'
group by c.country;
```

The **rewriter** replaces a view with its definition, so that the query runs against the underlying tables. <!-- L13 --> The plan for `select * from paid_revenue order by revenue_cents desc` is identical, line for line and cost for cost, to the plan for the original query. <!-- L35 --> By the time the planner sees the query the view is gone, which is why querying a view adds nothing to the plan.

### Stage 3: the planner picks the cheapest path

The **planner**, also called the optimizer, decides *how*. It works out the possible ways to produce the result, estimates the cost of each, and keeps the cheapest. <!-- L14 --> For our join it chose a **hash join**: load `customers` into an in-memory lookup table keyed on `id`, then stream the orders past it and look up each order's customer. <!-- L48 --> That lookup table is the `Hash` step in Figure 1.

Each step carries two costs, as in `cost=0.00..12901.33` on the scan of `orders`: the estimated cost before its first row, and the estimated cost of running it to completion. <!-- L16 --> The unit is not milliseconds. It is arbitrary, anchored on the cost of reading one page of a table in order, which is set to 1.0. <!-- L17 -->

To see what the choice saved, the lab turns hash joins off for its connection with `set enable_hashjoin = off`. The planner's next-best plan then costs 41,515.08, against 18,285.79 for the plan it chose: 2.27 times as much. <!-- L36 --> How costs are computed, and what happens when the estimates behind them are wrong, comes later in this series.

### Stage 4: the executor runs the tree

The **executor** walks the plan tree and produces the rows. <!-- L15 --> `EXPLAIN ANALYZE` prints, beside each estimate, the rows each step actually produced and how many times it ran, its *loops*. <!-- L18 --> Two things stand out in Figure 1.

The plan ran in three processes at once, the main one and two helpers: that is what `Workers Launched: 2` and `loops=3` mean. Where those helpers come from is the subject of *How PostgreSQL Uses Processes*, part 2 of this series. Each process scanned a share of `orders`, joined its paid orders to their customers and computed partial totals for the five countries. `Gather Merge` collected those 15 partial rows, and `Finalize GroupAggregate` combined them into 5. <!-- L42 -->

And the estimates were off. The planner expected 140,514 paid orders per process; each found 111,111, which is 333,333 in all. <!-- L41 --> The answer was still right: every path the planner considers produces the same result, <!-- L14 --> so an estimate decides *how* a query runs, never *what* it returns.

Two things in this output are new in PostgreSQL 18: actual row counts with two decimals, `rows=5.00` rather than `rows=5`, <!-- L28 --> and the `Buffers` lines, which 16 and 17 print only for `EXPLAIN (ANALYZE, BUFFERS)`. <!-- L27 --> Those lines count pages: `shared hit=7693` on the scan of `orders` means the scan touched each of the table's 7,693 pages once. <!-- L37 -->

### The same four stages in 1979, almost

In 1979 the System R team described four phases for every SQL statement: parsing, optimization, code generation and execution. <!-- L08 --> Its optimizer, like PostgreSQL's planner, picked the access path with the lowest estimated cost. <!-- L10 --> Figure 5 lines the two lists up.

![System R's four phases from 1979, parsing, optimization, code generation and execution, aligned above PostgreSQL's four stages, parser, rewriter, planner and executor, with parsing, optimization and execution matched, code generation unmatched after optimization, and the rewriter unmatched before the planner](FIG_05)

*Figure 5 — Four phases in 1979 and four stages now, but not the same four. Each list has one step the other lacks.*

System R generated code after optimizing; PostgreSQL's executor works from the plan tree itself, and PostgreSQL instead rewrites views before planning. <!-- L08 --> <!-- L12 --> <!-- L15 --> Even the name lookups moved: System R's optimizer did them, <!-- L09 --> and PostgreSQL's parser does them in its second pass. <!-- L52 -->

## Two surprises on real rows

### Surprise one: the table accepted a duplicate

Order 4242 belongs to customer 92399, whose country is JP, and is paid, for 56,954 cents. <!-- L47 --> The lab inserts an exact copy of it:

```sql
insert into orders (id, customer_id, amount_cents, created, status)
select id, customer_id, amount_cents, created, status from orders where id = 4242;
```

PostgreSQL accepts it without a warning, and order 4242 now comes back twice:

```text
  id  | customer_id | amount_cents | status
------+-------------+--------------+--------
 4242 |       92399 |        56954 | paid
 4242 |       92399 |        56954 | paid
(2 rows)
```

Rerun the revenue question and JP reads 3,333,423,633 cents instead of 3,333,366,679: exactly 56,954 more, with one more paid order. <!-- L38 --> Figure 6 shows why. Both copies match customer 92399 in the join, so the sum adds the amount twice. Nothing errored, the query did not change, and no single number looks wrong on its own.

![Two identical rows for order 4242 in orders, both joined to customer 92399 in JP, so the sum for JP adds 56,954 cents twice and the country's total rises from 3,333,366,679 to 3,333,423,633](FIG_06)

*Figure 6 — How one duplicate moves a total. Each copy of order 4242 finds the same customer, so the join produces two rows and the sum counts the amount twice.*

In Codd's model this cannot happen: a relation is a set, and its rows are distinct. <!-- L02 --> A SQL table without a primary key is closer to a *bag*, a collection that can hold the same member twice. The question was open from the start. SEQUEL, the 1974 ancestor of SQL from the same IBM laboratory, <!-- L44 --> made removing duplicates a default, not a law, skipped when a function such as an average was applied to the result, and either default could be overridden. <!-- L06 --> PostgreSQL's documentation is plain about its own position. Relational theory says every table needs a primary key, and the rule is "not enforced by PostgreSQL". <!-- L24 -->

The fix usually arrives after the damage, and the key cannot be declared while the duplicate is there:

```sql
alter table orders add primary key (id);
```

```text
ERROR:  could not create unique index "orders_pkey"
DETAIL:  Key (id)=(4242) is duplicated.
```

Delete one copy and the same statement succeeds. Insert the copy again, and now the server refuses it: <!-- L39 -->

```text
ERROR:  duplicate key value violates unique constraint "orders_pkey"
DETAIL:  Key (id)=(4242) already exists.
```

Both messages name `orders_pkey`, the unique index that declaring the key built. The key itself is now a row in the catalog `pg_constraint`, <!-- L39 --> and on PostgreSQL 18 so is each column's not-null rule, which earlier versions did not record there. <!-- L29 --> A constraint binds every program that connects, including one written next year by someone who never saw this table's history. A check inside your application cannot promise that.

### Surprise two: NULL is not a value

**NULL** is SQL's marker for a missing or unknown value. It is not zero and not an empty string; it means there is no value. <!-- L49 --> Because `amount_cents` was declared `not null`, the lab first drops that rule, then blanks one amount: <!-- L40 -->

```sql
alter table orders alter column amount_cents drop not null;
update orders set amount_cents = null where id = 4242;
```

Now `select count(*), count(amount_cents) from orders` returns two different numbers:

```text
  count  | count
---------+--------
 1000000 | 999999
(1 row)
```

`count(*)` counts rows; `count(amount_cents)` counts the rows whose `amount_cents` is not null. <!-- L19 --> <!-- L40 --> Every other aggregate behaves like the second: `sum` and `avg` skip nulls instead of returning null. <!-- L20 --> An average of the paid orders is now an average of the paid orders *that have an amount*, which may not be what you meant.

The blanked row is also hard to find again: `where amount_cents = null` matches 0 rows, and `where amount_cents is null` matches 1. <!-- L40 --> A comparison with null is neither true nor false: `7 = NULL` is null, meaning unknown. <!-- L49 --> A `where` clause keeps a row only when its condition is *true*, and discards it when the result is false or null. <!-- L50 --> Figure 7 puts the counts and the comparisons side by side.

![On the left, the comparison amount_cents = NULL evaluating to unknown for every row so that WHERE keeps none, while IS NULL evaluates to true for the one blanked row; on the right, count(*) counting 1,000,000 rows and count(amount_cents) counting 999,999 non-null values](FIG_07)

*Figure 7 — NULL in a comparison and in a count. `= NULL` is never true, so it matches nothing; `count(column)` skips the row whose value is unknown.*

One trap sits where the two surprises meet. A unique constraint treats two nulls as different, so even under a unique constraint, rows can repeat when one of the constrained columns holds a null. <!-- L25 -->

## The math

Two pieces of formalism explain both surprises.

| Symbol | Meaning |
|---|---|
| $S_j$ | the $j$-th domain: the set of values the $j$-th column may take |
| $n$ | the degree: the number of columns |
| $R$ | a relation |
| $t$ | one row of a relation |
| $\top$, $\bot$, $U$ | the truth values true, false and unknown; SQL writes unknown as NULL |

**A relation is a set.** Codd's definition, written as one line:

$$
R \subseteq S_1 \times S_2 \times \cdots \times S_n
$$

A relation is some subset of all the rows you could build by picking one value from each domain. <!-- L01 --> For `customers`, $n = 3$: $S_1$ is the whole numbers, $S_2$ the strings and $S_3$ the two-character codes, and one member of $R$ is the row $(92399,\ \text{'customer 92399'},\ \text{'JP'})$. <!-- L47 -->

Because $R$ is a set, adding a row it already contains changes nothing:

$$
t \in R \implies R \cup \{t\} = R
$$

Inserting a row that is already there leaves a relation unchanged. A table without a key is a bag instead: every insert adds a copy, and a sum counts every copy. With order 4242 stored twice, JP's revenue becomes

$$
3{,}333{,}366{,}679 + 56{,}954 = 3{,}333{,}423{,}633
$$

which is the number the lab printed. <!-- L38 -->

**Three-valued logic.** SQL's conditions have three possible results, not two. <!-- L51 --> A comparison with NULL on either side is $U$, so `amount_cents = null` is $U$ on all 1,000,000 rows, even the one whose amount is NULL. <!-- L49 --> A `where` clause keeps a row only when its condition is $\top$, so $U$ is discarded exactly like $\bot$. <!-- L50 --> The two counts apply the same idea to aggregates:

$$
\operatorname{count}(*) = |R| \qquad \operatorname{count}(a) = \bigl|\{\, t \in R : t.a \text{ is not NULL} \,\}\bigr|
$$

`count(*)` is the number of rows, and `count(a)` is the number of rows whose column $a$ is not NULL. With one amount blanked, those are 1,000,000 and 999,999. <!-- L19 --> <!-- L40 -->

<details>
<summary>The full truth tables for AND, OR and NOT</summary>

These are the rules SQL uses to combine conditions when one of them is unknown. <!-- L51 -->

| $a$ | $b$ | $a$ AND $b$ | $a$ OR $b$ |
|---|---|---|---|
| true | true | true | true |
| true | false | false | true |
| true | NULL | NULL | true |
| false | false | false | false |
| false | NULL | false | NULL |
| NULL | NULL | NULL | NULL |

NOT true is false, NOT false is true, and NOT NULL is NULL, so `where not (amount_cents = null)` matches nothing either.

</details>

## Implementation

Every statement this post runs is shown above. The lab packages them: `shopgen.py` loads the two tables, `run_lab.py` runs every query here and saves the output, and `check.py` marks your run against the author's.

They need Python 3 with no extra packages, and a PostgreSQL server you start yourself. A **database cluster** is the directory of databases one server manages: `initdb` creates an empty one, `pg_ctl` starts a server on it, and `-h ''` turns network connections off, so the server listens only on a local socket file:

```bash
initdb -D /path/pgdata -U postgres --encoding=UTF8 --locale=C.UTF-8
pg_ctl -D /path/pgdata -o "-k /path/sock -h ''" -l /path/server.log -w start
PGBIN=/path/to/postgres/bin PGSOCK=/path/sock python3 run_lab.py
```

When you are done, stop the server and delete the directory, which removes the cluster and everything in it:

```bash
pg_ctl -D /path/pgdata -m fast stop
rm -rf /path/pgdata /path/sock
```

> [!WARNING]
> The lab inserts a duplicate row, drops a not-null rule and adds a primary key. Run it only against a server you created for it, never against a database you care about.

The captures were made on 2026-10-01 with PostgreSQL 18.6 and its default configuration. The two tables came out at 710 and 7,693 pages, the same sizes the earlier parts of this series measured on PostgreSQL 16.2. <!-- L31 --> The files are under [Lab downloads](#lab-downloads).

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** treating a table as a set. Without a declared key, a table stores an exact duplicate silently. Every total that touches that row is then wrong by the row's own values, and no error, log line or failing query points at the cause. Declare the primary key when you create the table, not after the first incident.

- **Costs are not times.** Comparing two plans' costs tells you which one the planner prefers. Comparing a cost with a stopwatch tells you nothing, because the unit is arbitrary. <!-- L17 -->
- **One machine, one dataset.** The plan here, three processes and a hash join, is what this data produced on this machine. Fewer CPUs, a smaller table or different settings can give a different plan that returns the same rows.
- **NULL reaches further than counting.** This post shows NULL in counts and comparisons only. It also changes how joins and grouping behave, which comes later in this series.

## Key takeaways

- A relation is a set of rows; a table behaves like one only once you declare a primary key, and without one PostgreSQL stores exact duplicates silently.
- You write *what* you want and the server decides *how*, in four stages you can inspect: the parser, the rewriter, the planner and the executor.
- `EXPLAIN` shows the chosen plan with estimated costs in arbitrary units; `EXPLAIN ANALYZE` runs it and prints actual rows beside the estimates.
- The schema is data: every table, column and constraint is a row in a system catalog you can query with ordinary SQL.
- NULL means unknown, not empty: `count(*)` counts rows, `count(column)` counts non-null values, and `= NULL` never matches anything.

## Try it yourself

The lab's README has four exercises, each with a self-check that `check.py` marks for you. Load fresh data before each one with `python3 shopgen.py --scale M --db shoplab --drop`, because `run_lab.py` and E3 both change it.

1. **E1, reproduce.** Run `python3 check.py e1`. Self-check: your five revenue rows match the worked example's, to the cent.
2. **E2, inspect.** Compare the `Buffers` line on the scan of `orders` with `relpages` for `orders`, then run `python3 check.py e2`. Self-check: the two are equal.
3. **E3, predict.** Before you blank one amount, write down what `count(*)`, `count(amount_cents)` and `sum(amount_cents)` will do; then run the NULL section's two statements and `python3 check.py e3`. Self-check: the numbers and the reasons are right.
4. **E4, diagnose.** Run `python3 check.py e4 --break`. Find which country's revenue moved, by how much and why, make the server refuse the cause, then run `python3 check.py e4 --verify`. Self-check: symptom, cause, proof, and a fix the server enforces.

<details><summary>Answers</summary>

**E1:** DE 3,333,366,716 · IN 3,333,366,679 · JP 3,333,366,679 · BR 3,333,266,642 · US 3,333,166,605. <!-- L33 --> **E2:** 7,693 and 7,693; on PostgreSQL 16 or 17, ask for the lines with `EXPLAIN (ANALYZE, BUFFERS)`. <!-- L37 --> <!-- L27 --> **E3:** 1,000,000 and 999,999, because `count(amount_cents)` counts only non-null values; `sum` falls by that order's 56,954 cents, because it skips nulls. <!-- L19 --> <!-- L20 --> <!-- L47 --> **E4:** JP rose by 56,954 cents because `orders` has no primary key and an exact copy of order 4242 went in; `select count(*) from orders where id = 4242` returns 2. Delete one copy, then `alter table orders add primary key (id)`. Deleting alone fails the checker's third test: it repairs the incident and prevents nothing. <!-- L38 --> <!-- L39 -->

</details>

## References

### Lab downloads

- [`README.md`](LAB_01) — what the lab needs, how to run it, the four exercises in full, and how to clean up.
- [`shopgen.py`](LAB_02) — creates the database and loads `customers` and `orders` from the series' table declarations.
- [`run_lab.py`](LAB_03) — runs every query in this post and writes the two capture files.
- [`check.py`](LAB_04) — marks your own run against the author's, one exercise at a time.
- [`captures.md`](LAB_05) — the author's run: every statement and its output, verbatim.
- [`captures.json`](LAB_06) — the same run as numbers, which `check.py` reads.

### Sources

All web pages accessed 2026-10-01.

1. Codd, E. F. "A Relational Model of Data for Large Shared Data Banks." *Communications of the ACM* 13(6), 377–387, 1970. https://doi.org/10.1145/362384.362685
2. Chamberlin, D. D., and Boyce, R. F. "SEQUEL: A Structured English Query Language." *Proceedings of the 1974 ACM SIGFIDET Workshop on Data Description, Access and Control*, 249–264, 1974. https://doi.org/10.1145/800296.811515
3. Selinger, P. G., Astrahan, M. M., Chamberlin, D. D., Lorie, R. A., and Price, T. G. "Access Path Selection in a Relational Database Management System." *Proceedings of the 1979 ACM SIGMOD International Conference on Management of Data*, 23–34, 1979. https://doi.org/10.1145/582095.582099
4. Stonebraker, M., and Pavlo, A. "What Goes Around Comes Around... And Around..." *ACM SIGMOD Record* 53(2), 21–37, 2024. https://doi.org/10.1145/3685980.3685984
5. PostgreSQL 18 documentation, §51.1 The Path of a Query. https://www.postgresql.org/docs/18/query-path.html
6. PostgreSQL 18 documentation, §51.3 The Parser Stage. https://www.postgresql.org/docs/18/parser-stage.html
7. PostgreSQL 18 documentation, §51.5 Planner/Optimizer. https://www.postgresql.org/docs/18/planner-optimizer.html
8. PostgreSQL 18 documentation, §14.1 Using EXPLAIN. https://www.postgresql.org/docs/18/using-explain.html
9. PostgreSQL 18 documentation, §5.5 Constraints. https://www.postgresql.org/docs/18/ddl-constraints.html
10. PostgreSQL 18 documentation, §52.11 pg_class. https://www.postgresql.org/docs/18/catalog-pg-class.html
11. PostgreSQL 18 documentation, §52.7 pg_attribute. https://www.postgresql.org/docs/18/catalog-pg-attribute.html
12. PostgreSQL 18 documentation, §9.21 Aggregate Functions. https://www.postgresql.org/docs/18/functions-aggregate.html
13. PostgreSQL 18 documentation, §9.1 Logical Operators. https://www.postgresql.org/docs/18/functions-logical.html
14. PostgreSQL 18 documentation, §9.2 Comparison Functions and Operators. https://www.postgresql.org/docs/18/functions-comparison.html
15. PostgreSQL 18 documentation, §7.2.2 The WHERE Clause. https://www.postgresql.org/docs/18/queries-table-expressions.html
16. PostgreSQL 18 documentation, Appendix D, SQL Conformance. https://www.postgresql.org/docs/18/features.html
17. PostgreSQL 18 documentation, Appendix E.6, Release 18. https://www.postgresql.org/docs/18/release-18.html
