# Captures - what a relational database actually does

Captured 2026-10-01T09:50:49+00:00 on Linux 7.0.0-31-generic, 16 CPUs.

`PostgreSQL 18.6 on x86_64-pc-linux-gnu, compiled by gcc (Ubuntu 15.2.0-16ubuntu1) 15.2.0, 64-bit`, default `postgresql.conf`.


## 1. Two tables, and the same two tables as rows in the catalog

The schema is data. Every table in this database has a row in `pg_class`, and every column has a row in `pg_attribute` - including the tables that store `pg_class` and `pg_attribute` themselves.

**The customers table as psql describes it**

```sql
\d customers
```

```text
                Table "public.customers"
 Column  |     Type     | Collation | Nullable | Default 
---------+--------------+-----------+----------+---------
 id      | integer      |           | not null | 
 name    | text         |           | not null | 
 country | character(2) |           | not null | 
Indexes:
    "customers_pkey" PRIMARY KEY, btree (id)
```

**The orders table - note what it does not have**

```sql
\d orders
```

```text
                          Table "public.orders"
    Column    |           Type           | Collation | Nullable | Default 
--------------+--------------------------+-----------+----------+---------
 id           | integer                  |           | not null | 
 customer_id  | integer                  |           | not null | 
 amount_cents | integer                  |           | not null | 
 created      | timestamp with time zone |           | not null | 
 status       | text                     |           | not null | 
```

**The two tables, as rows in pg_class**

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

`relpages` and `reltuples` are the planner's estimates, refreshed by VACUUM and ANALYZE - shopgen ran both.

**The columns of orders, as rows in pg_attribute**

```sql
select attname, atttypid::regtype as type, attnum, attlen, attnotnull
from pg_attribute
where attrelid = 'orders'::regclass and attnum > 0
order by attnum;
```

```text
   attname    |           type           | attnum | attlen | attnotnull 
--------------+--------------------------+--------+--------+------------
 id           | integer                  |      1 |      4 | t
 customer_id  | integer                  |      2 |      4 | t
 amount_cents | integer                  |      3 |      4 | t
 created      | timestamp with time zone |      4 |      8 | t
 status       | text                     |      5 |     -1 | t
(5 rows)
```

Ordinary columns are numbered from 1 up; the system columns, such as `ctid`, have negative attnum and are filtered out here.

**pg_class has a row for pg_class**

```sql
select relname, relkind, relnatts
from pg_class
where relname in ('pg_class','pg_attribute')
order by relname;
```

```text
   relname    | relkind | relnatts 
--------------+---------+----------
 pg_attribute | r       |       25
 pg_class     | r       |       34
(2 rows)
```

The catalog describes itself. That is Codd's point made concrete: there is one kind of thing in the database, and it is the relation.


## 2. One business question, asked once

Revenue in cents per country, for paid orders only.

**The question, and its answer**

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


## 3. What the server did with it: parse, rewrite, plan, execute

The four stages are PostgreSQL's own (docs ch. 51, 'The Path of a Query'). Each one can be made to show itself.

**Stage 1a, the parser: a syntax error**

```sql
selec c.country from customers c;
```

```text
ERROR:  syntax error at or near "selec"
LINE 1: selec c.country from customers c;
        ^
```

The parser only checks the shape of the text. It has not looked anything up yet, which is why it reports a position and not a name.

**Stage 1b, the transformation: a name that does not exist**

```sql
select c.nosuchcolumn from customers c;
```

```text
ERROR:  column c.nosuchcolumn does not exist
LINE 1: select c.nosuchcolumn from customers c;
               ^
```

This is the second half of the parser stage. Now the server has consulted the catalog, found `customers`, and failed to find a column in it.

**Stage 2, the rewriter: define a view**

```sql
create view paid_revenue as
select c.country, sum(o.amount_cents) as revenue_cents, count(*) as paid_orders
from customers c join orders o on o.customer_id = c.id
where o.status = 'paid'
group by c.country;
```

```text

```

**Stage 2, the rewriter: the view is gone by planning time**

```sql
explain (costs off) select * from paid_revenue order by revenue_cents desc;
```

```text
                              QUERY PLAN                               
-----------------------------------------------------------------------
 Sort
   Sort Key: (sum(o.amount_cents)) DESC
   ->  Finalize GroupAggregate
         Group Key: c.country
         ->  Gather Merge
               Workers Planned: 2
               ->  Sort
                     Sort Key: c.country
                     ->  Partial HashAggregate
                           Group Key: c.country
                           ->  Hash Join
                                 Hash Cond: (o.customer_id = c.id)
                                 ->  Parallel Seq Scan on orders o
                                       Filter: (status = 'paid'::text)
                                 ->  Hash
                                       ->  Seq Scan on customers c
(16 rows)
```

There is no 'view scan' node. The rewriter replaced `paid_revenue` with its definition before the planner ever saw the query.

**Stage 3, the planner: the same plan, with costs**

```sql
explain select * from paid_revenue order by revenue_cents desc;
```

```text
                                                  QUERY PLAN                                                  
--------------------------------------------------------------------------------------------------------------
 Sort  (cost=18285.78..18285.79 rows=5 width=19)
   Sort Key: (sum(o.amount_cents)) DESC
   ->  Finalize GroupAggregate  (cost=18284.18..18285.72 rows=5 width=19)
         Group Key: c.country
         ->  Gather Merge  (cost=18284.18..18285.58 rows=12 width=19)
               Workers Planned: 2
               ->  Sort  (cost=17284.16..17284.17 rows=5 width=19)
                     Sort Key: c.country
                     ->  Partial HashAggregate  (cost=17284.05..17284.10 rows=5 width=19)
                           Group Key: c.country
                           ->  Hash Join  (cost=2960.00..16230.19 rows=140514 width=7)
                                 Hash Cond: (o.customer_id = c.id)
                                 ->  Parallel Seq Scan on orders o  (cost=0.00..12901.33 rows=140514 width=8)
                                       Filter: (status = 'paid'::text)
                                 ->  Hash  (cost=1710.00..1710.00 rows=100000 width=7)
                                       ->  Seq Scan on customers c  (cost=0.00..1710.00 rows=100000 width=7)
(16 rows)
```

**Stage 3, the planner: the plan it chose for our query**

```sql
explain select c.country,
       sum(o.amount_cents) as revenue_cents,
       count(*)            as paid_orders
from customers c
join orders o on o.customer_id = c.id
where o.status = 'paid'
group by c.country
order by revenue_cents desc;
```

```text
                                                  QUERY PLAN                                                  
--------------------------------------------------------------------------------------------------------------
 Sort  (cost=18285.78..18285.79 rows=5 width=19)
   Sort Key: (sum(o.amount_cents)) DESC
   ->  Finalize GroupAggregate  (cost=18284.18..18285.72 rows=5 width=19)
         Group Key: c.country
         ->  Gather Merge  (cost=18284.18..18285.58 rows=12 width=19)
               Workers Planned: 2
               ->  Sort  (cost=17284.16..17284.17 rows=5 width=19)
                     Sort Key: c.country
                     ->  Partial HashAggregate  (cost=17284.05..17284.10 rows=5 width=19)
                           Group Key: c.country
                           ->  Hash Join  (cost=2960.00..16230.19 rows=140514 width=7)
                                 Hash Cond: (o.customer_id = c.id)
                                 ->  Parallel Seq Scan on orders o  (cost=0.00..12901.33 rows=140514 width=8)
                                       Filter: (status = 'paid'::text)
                                 ->  Hash  (cost=1710.00..1710.00 rows=100000 width=7)
                                       ->  Seq Scan on customers c  (cost=0.00..1710.00 rows=100000 width=7)
(16 rows)
```

Two numbers per node: the cost before the first row, and the cost of running the node to completion. The units are arbitrary, anchored at `seq_page_cost = 1`.

**Stage 4, the executor: the same plan, actually run**

```sql
explain (analyze, timing off, summary off) select c.country,
       sum(o.amount_cents) as revenue_cents,
       count(*)            as paid_orders
from customers c
join orders o on o.customer_id = c.id
where o.status = 'paid'
group by c.country
order by revenue_cents desc;
```

```text
                                                                  QUERY PLAN                                                                  
----------------------------------------------------------------------------------------------------------------------------------------------
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

`actual rows` beside `rows` is the planner's estimate graded against reality. PostgreSQL 18 prints those actual row counts with two decimal places, and includes BUFFERS by default; on 16 and 17 you ask for buffers explicitly.

**Stage 3 again: take the cheapest plan away**

```sql
set enable_hashjoin = off;
```

```text

```

**The planner's second choice, and what it costs**

```sql
explain select c.country,
       sum(o.amount_cents) as revenue_cents,
       count(*)            as paid_orders
from customers c
join orders o on o.customer_id = c.id
where o.status = 'paid'
group by c.country
order by revenue_cents desc;
```

```text
                                                  QUERY PLAN                                                  
--------------------------------------------------------------------------------------------------------------
 Sort  (cost=18285.78..18285.79 rows=5 width=19)
   Sort Key: (sum(o.amount_cents)) DESC
   ->  Finalize GroupAggregate  (cost=18284.18..18285.72 rows=5 width=19)
         Group Key: c.country
         ->  Gather Merge  (cost=18284.18..18285.58 rows=12 width=19)
               Workers Planned: 2
               ->  Sort  (cost=17284.16..17284.17 rows=5 width=19)
                     Sort Key: c.country
                     ->  Partial HashAggregate  (cost=17284.05..17284.10 rows=5 width=19)
                           Group Key: c.country
                           ->  Hash Join  (cost=2960.00..16230.19 rows=140514 width=7)
                                 Hash Cond: (o.customer_id = c.id)
                                 ->  Parallel Seq Scan on orders o  (cost=0.00..12901.33 rows=140514 width=8)
                                       Filter: (status = 'paid'::text)
                                 ->  Hash  (cost=1710.00..1710.00 rows=100000 width=7)
                                       ->  Seq Scan on customers c  (cost=0.00..1710.00 rows=100000 width=7)
(16 rows)
```

Turning off the hash join does not forbid an answer, it forbids one path to it. The cost the planner reports here is what it avoided by choosing the first plan. How those costs are computed is part 14.


## 4. The first surprise: orders has no primary key

A relation, in Codd's sense, is a set: no two rows are the same. A SQL table is not a set unless you say so.

**Row 4242, once**

```sql
select id, customer_id, amount_cents, status from orders where id = 4242;
```

```text
  id  | customer_id | amount_cents | status 
------+-------------+--------------+--------
 4242 |       92399 |        56954 | paid
(1 row)
```

**Insert it again, unchanged. Nothing stops this.**

```sql
insert into orders (id, customer_id, amount_cents, created, status)
select id, customer_id, amount_cents, created, status from orders where id = 4242;
```

```text

```

**Row 4242, twice**

```sql
select id, customer_id, amount_cents, status from orders where id = 4242;
```

```text
  id  | customer_id | amount_cents | status 
------+-------------+--------------+--------
 4242 |       92399 |        56954 | paid
 4242 |       92399 |        56954 | paid
(2 rows)
```

Two rows, identical in every column. `id` was never promised to be unique.

**The same question, the same word 'revenue', a different answer**

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

```text
 country | revenue_cents | paid_orders 
---------+---------------+-------------
 JP      |    3333423633 |       66667
 DE      |    3333366716 |       66667
 IN      |    3333366679 |       66667
 BR      |    3333266642 |       66667
 US      |    3333166605 |       66666
(5 rows)
```

One country's revenue moved. There are two order rows now, each matching the same customer, so that order's amount is added twice. Nothing errored, nothing in the query changed, and no row count looks wrong on its own.


## 5. The constraint that would have stopped it

**Try to declare what you meant all along**

```sql
alter table orders add primary key (id);
```

```text
ERROR:  could not create unique index "orders_pkey"
DETAIL:  Key (id)=(4242) is duplicated.
```

The constraint cannot be added while the data already violates it. This is the usual order of events: the duplicate arrives first, the constraint second.

**Remove the duplicate, keeping one copy**

```sql
delete from orders o
where o.ctid <> (select min(i.ctid) from orders i where i.id = o.id)
  and o.id = 4242;
```

```text

```

**Now it can be declared**

```sql
alter table orders add primary key (id);
```

```text

```

**Insert the duplicate again**

```sql
insert into orders (id, customer_id, amount_cents, created, status)
select id, customer_id, amount_cents, created, status from orders where id = 4242;
```

```text
ERROR:  duplicate key value violates unique constraint "orders_pkey"
DETAIL:  Key (id)=(4242) already exists.
```

Rejected by the server, in the server, for every client that will ever connect to it. That is the difference between a rule in your application and a rule in your database.

**The constraint, as a row in the catalog**

```sql
select conname, contype, pg_get_constraintdef(oid) as definition
from pg_constraint where conrelid = 'orders'::regclass;
```

```text
           conname            | contype |      definition       
------------------------------+---------+-----------------------
 orders_id_not_null           | n       | NOT NULL id
 orders_customer_id_not_null  | n       | NOT NULL customer_id
 orders_amount_cents_not_null | n       | NOT NULL amount_cents
 orders_created_not_null      | n       | NOT NULL created
 orders_status_not_null       | n       | NOT NULL status
 orders_pkey                  | p       | PRIMARY KEY (id)
(6 rows)
```

Declaring it also built an index: a primary key is enforced by a unique index, which is why the check costs nothing on lookup.


## 6. The second surprise: NULL is not a value

Both counts below count the same rows. They disagree because one of them is not counting rows.

**Before: the two counts agree**

```sql
select count(*), count(amount_cents) from orders where id = 4242;
```

```text
 count | count 
-------+-------
     1 |     1
(1 row)
```

**Drop the constraint that was preventing this**

```sql
alter table orders alter column amount_cents drop not null;
```

```text

```

`amount_cents` was declared `not null` by shopgen. Removing it is a deliberate act, and it is the only reason the next statement works.

**One amount is now unknown**

```sql
update orders set amount_cents = null where id = 4242;
```

```text

```

**After: count(*) and count(amount_cents) differ by one**

```sql
select count(*), count(amount_cents) from orders;
```

```text
  count  | count  
---------+--------
 1000000 | 999999
(1 row)
```

`count(*)` counts rows. `count(amount_cents)` counts rows where that column is not null. They were never the same function.

**And the row cannot be found by asking for it**

```sql
select count(*) as rows_matching
from orders where amount_cents = null;
```

```text
 rows_matching 
---------------
             0
(1 row)
```

`= null` is never true. It is not false either: it is unknown, and a WHERE clause keeps only rows for which the condition is true.

**`is null` is the operator that asks the question**

```sql
select count(*) as rows_matching
from orders where amount_cents is null;
```

```text
 rows_matching 
---------------
             1
(1 row)
```

**Every aggregate but count(*) skips the unknown**

```sql
select sum(amount_cents) as sum_ignores_null,
       avg(amount_cents)::numeric(12,2) as avg_ignores_null,
       count(*) as rows
from orders where status = 'paid';
```

```text
 sum_ignores_null | avg_ignores_null |  rows  
------------------+------------------+--------
      16666476367 |         49999.63 | 333333
(1 row)
```

The average is over the rows that have an amount, not over the paid orders. Whether that is what you meant is a question SQL cannot ask you.

