# Captures - how a SELECT is evaluated

Captured 2026-10-02T08:41:05+00:00 on Linux 7.0.0-31-generic, 16 CPUs.

`PostgreSQL 18.6 on x86_64-pc-linux-gnu, compiled by gcc (Ubuntu 15.2.0-16ubuntu1) 15.2.0, 64-bit`, default `postgresql.conf`.


## 1. The data: the full shop and the 20-row sample

shopgen built the series' two tables at scale M and added 1,000 customers who have never ordered. sample.sql built the 20-row sample by hand.

**Customers in the full shop** (shoplab)

```sql
select count(*) as customers,
       count(*) filter (where id > 100000) as added_without_orders
from customers;
```

```text
 customers | added_without_orders 
-----------+----------------------
    101000 |                 1000
(1 row)
```

**How many orders each customer has placed** (shoplab)

```sql
select orders_placed, count(*) as customers
from (select c.id, count(o.id) as orders_placed
      from customers c left join orders o on o.customer_id = c.id
      group by c.id) per_customer
group by orders_placed
order by orders_placed;
```

```text
 orders_placed | customers 
---------------+-----------
             0 |      1000
            10 |    100000
(2 rows)
```

Every one of the original 100,000 customers has exactly 10 orders: the generator's multiplier 7,919 shares no factor with 100,000, so customer_id visits every customer once in every 100,000 orders.

**The sample's customers** (shopsample)

```sql
table customers;
```

```text
 id |    name    | country 
----+------------+---------
  1 | customer 1 | DE
  2 | customer 2 | IN
  3 | customer 3 | JP
  4 | customer 4 | DE
  5 | customer 5 | JP
  6 | customer 6 | IN
(6 rows)
```

**The sample's orders** (shopsample)

```sql
table orders order by id;
```

```text
 id  | customer_id | amount_cents |        created         |  status  
-----+-------------+--------------+------------------------+----------
 101 |           1 |         5000 | 2026-01-01 00:00:01+00 | paid
 102 |           1 |         3000 | 2026-01-01 00:00:02+00 | paid
 103 |           1 |         2000 | 2026-01-01 00:00:03+00 | refunded
 104 |           2 |         7000 | 2026-01-01 00:00:04+00 | paid
 105 |           2 |         1000 | 2026-01-01 00:00:05+00 | shipped
 106 |           2 |         4000 | 2026-01-01 00:00:06+00 | refunded
 107 |           3 |         6000 | 2026-01-01 00:00:07+00 | paid
 108 |           3 |         2500 | 2026-01-01 00:00:08+00 | shipped
 109 |           4 |         9000 | 2026-01-01 00:00:09+00 | shipped
 110 |           4 |         1500 | 2026-01-01 00:00:10+00 | paid
 111 |           5 |         1000 | 2026-01-01 00:00:11+00 | paid
 112 |           5 |         3500 | 2026-01-01 00:00:12+00 | refunded
 113 |           5 |         5500 | 2026-01-01 00:00:13+00 | shipped
 114 |           3 |         8000 | 2026-01-01 00:00:14+00 | refunded
(14 rows)
```


## 2. One report, clause by clause

Paid revenue per country, top two. Each step adds one clause, and the row count is taken after it, on the sample and on the full shop.

**The report** (shoplab)

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

```text
 country | paid_orders | revenue_cents 
---------+-------------+---------------
 DE      |       66667 |    3333366716
 IN      |       66667 |    3333366679
(2 rows)
```

**The report on the sample** (shopsample)

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

```text
 country | paid_orders | revenue_cents 
---------+-------------+---------------
 DE      |           3 |          9500
 JP      |           2 |          7000
(2 rows)
```

Row counts after each clause:

- `customers`: sample 6 (by hand 6), full 101,000

- `inner_join`: sample 14 (by hand 14), full 1,000,000

- `where_paid`: sample 6 (by hand 6), full 333,333

- `groups`: sample 3 (by hand 3), full 5

**ORDER BY without LIMIT: IN and JP have the same revenue** (shoplab)

```sql
select c.country,
       count(*)            as paid_orders,
       sum(o.amount_cents) as revenue_cents
from customers c
join orders o on o.customer_id = c.id
where o.status = 'paid'
group by c.country
order by revenue_cents desc;
```

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

**FETCH FIRST 2 ROWS WITH TIES keeps both tied rows** (shoplab)

```sql
select c.country,
       count(*)            as paid_orders,
       sum(o.amount_cents) as revenue_cents
from customers c
join orders o on o.customer_id = c.id
where o.status = 'paid'
group by c.country
order by revenue_cents desc
fetch first 2 rows with ties;
```

```text
 country | paid_orders | revenue_cents 
---------+-------------+---------------
 DE      |       66667 |    3333366716
 IN      |       66667 |    3333366679
 JP      |       66666 |    3333366679
(3 rows)
```

**The plan: a top-N sort under the limit** (shoplab)

```sql
explain (costs off) select c.country,
       count(*)            as paid_orders,
       sum(o.amount_cents) as revenue_cents
from customers c
join orders o on o.customer_id = c.id
where o.status = 'paid'
group by c.country
order by revenue_cents desc
limit 2;
```

```text
                                 QUERY PLAN                                  
-----------------------------------------------------------------------------
 Limit
   ->  Sort
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
(17 rows)
```

Second row of `LIMIT 2` under different planner settings: default: **IN**, enable_hashagg = off: **IN**, max_parallel_workers_per_gather = 0: **JP**, both: **IN**, enable_sort = off: **JP**

**With parallel workers off: a hash aggregate, and no sort by country before it** (shoplab)

```sql
set max_parallel_workers_per_gather = 0;
explain (costs off) select c.country,
       count(*)            as paid_orders,
       sum(o.amount_cents) as revenue_cents
from customers c
join orders o on o.customer_id = c.id
where o.status = 'paid'
group by c.country
order by revenue_cents desc
limit 2;
```

```text
                        QUERY PLAN                         
-----------------------------------------------------------
 Limit
   ->  Sort
         Sort Key: (sum(o.amount_cents)) DESC
         ->  HashAggregate
               Group Key: c.country
               ->  Hash Join
                     Hash Cond: (o.customer_id = c.id)
                     ->  Seq Scan on orders o
                           Filter: (status = 'paid'::text)
                     ->  Hash
                           ->  Seq Scan on customers c
(11 rows)
```

**The order the default plan hands the five groups on** (shoplab)

```sql
select c.country,
       count(*)            as paid_orders,
       sum(o.amount_cents) as revenue_cents
from customers c
join orders o on o.customer_id = c.id
where o.status = 'paid'
group by c.country;
```

```text
 country | paid_orders | revenue_cents 
---------+-------------+---------------
 BR      |       66667 |    3333266642
 DE      |       66667 |    3333366716
 IN      |       66667 |    3333366679
 JP      |       66666 |    3333366679
 US      |       66666 |    3333166605
(5 rows)
```

**The order the hash aggregate hands them on** (shoplab)

```sql
set max_parallel_workers_per_gather = 0;
select c.country,
       count(*)            as paid_orders,
       sum(o.amount_cents) as revenue_cents
from customers c
join orders o on o.customer_id = c.id
where o.status = 'paid'
group by c.country;
```

```text
 country | paid_orders | revenue_cents 
---------+-------------+---------------
 US      |       66666 |    3333166605
 BR      |       66667 |    3333266642
 JP      |       66666 |    3333366679
 IN      |       66667 |    3333366679
 DE      |       66667 |    3333366716
(5 rows)
```

Same, on the sample: default: **JP**, enable_hashagg = off: **IN**, max_parallel_workers_per_gather = 0: **JP**, both: **IN**, enable_sort = off: **JP**


## 3. FROM: inner join, left join, and the WHERE that undoes one

- `left_join`: sample 15 (by hand 15), full 1,001,000

- `left_join_where_paid`: sample 6 (by hand 6), full 333,333

- `left_join_on_paid`: sample 7 (by hand 7), full 334,333

**Customer 6 after the LEFT JOIN: one row, padded with NULLs** (shopsample)

```sql
select c.id, c.country, o.id as order_id, o.amount_cents, o.status
from customers c
left join orders o on o.customer_id = c.id
where c.id = 6;
```

```text
 id | country | order_id | amount_cents | status 
----+---------+----------+--------------+--------
  6 | IN      |          |              | 
(1 row)
```

**The full shop: 1,000 padded rows** (shoplab)

```sql
select count(*) filter (where o.id is null) as padded_rows,
       count(*) as all_rows
from customers c left join orders o on o.customer_id = c.id;
```

```text
 padded_rows | all_rows 
-------------+----------
        1000 |  1001000
(1 row)
```

**LEFT JOIN, then WHERE on the right table: customer 6 is gone again** (shopsample)

```sql
select c.country, count(o.id) as paid_orders
from customers c
left join orders o on o.customer_id = c.id
where o.status = 'paid'
group by c.country order by c.country;
```

```text
 country | paid_orders 
---------+-------------
 DE      |           3
 IN      |           1
 JP      |           2
(3 rows)
```

**The same condition in ON: customer 6 stays, with 0 paid orders** (shopsample)

```sql
select c.country, count(o.id) as paid_orders
from customers c
left join orders o on o.customer_id = c.id and o.status = 'paid'
group by c.country order by c.country;
```

```text
 country | paid_orders 
---------+-------------
 DE      |           3
 IN      |           1
 JP      |           2
(3 rows)
```

**The planner agrees: a LEFT JOIN with that WHERE is an inner join** (shoplab)

```sql
explain (costs off) select count(*) from customers c left join orders o on o.customer_id = c.id where o.status = 'paid';
```

```text
                                         QUERY PLAN                                         
--------------------------------------------------------------------------------------------
 Finalize Aggregate
   ->  Gather
         Workers Planned: 2
         ->  Partial Aggregate
               ->  Parallel Hash Join
                     Hash Cond: (o.customer_id = c.id)
                     ->  Parallel Seq Scan on orders o
                           Filter: (status = 'paid'::text)
                     ->  Parallel Hash
                           ->  Parallel Index Only Scan using customers_pkey on customers c
(10 rows)
```

No Left Join node: the WHERE clause rejects every padded row, so the planner reduced the outer join to an inner one.


## 4. WHERE filters rows, HAVING filters groups

**status = 'paid' in WHERE** (shoplab)

```sql
select c.country, o.status, count(*) as orders
from customers c join orders o on o.customer_id = c.id
where o.status = 'paid'
group by c.country, o.status
order by c.country;
```

```text
 country | status | orders 
---------+--------+--------
 BR      | paid   |  66667
 DE      | paid   |  66667
 IN      | paid   |  66667
 JP      | paid   |  66666
 US      | paid   |  66666
(5 rows)
```

**The same predicate in HAVING** (shoplab)

```sql
select c.country, o.status, count(*) as orders
from customers c join orders o on o.customer_id = c.id
group by c.country, o.status
having o.status = 'paid'
order by c.country;
```

```text
 country | status | orders 
---------+--------+--------
 BR      | paid   |  66667
 DE      | paid   |  66667
 IN      | paid   |  66667
 JP      | paid   |  66666
 US      | paid   |  66666
(5 rows)
```

**Plan with WHERE** (shoplab)

```sql
explain (costs off) select c.country, o.status, count(*) as orders
from customers c join orders o on o.customer_id = c.id
where o.status = 'paid'
group by c.country, o.status
order by c.country;
```

```text
                           QUERY PLAN                            
-----------------------------------------------------------------
 Finalize GroupAggregate
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
(14 rows)
```

**Plan with HAVING** (shoplab)

```sql
explain (costs off) select c.country, o.status, count(*) as orders
from customers c join orders o on o.customer_id = c.id
group by c.country, o.status
having o.status = 'paid'
order by c.country;
```

```text
                           QUERY PLAN                            
-----------------------------------------------------------------
 Finalize GroupAggregate
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
(14 rows)
```

Identical. The planner moved a HAVING condition that uses no aggregate into WHERE, so the rows are filtered before they are grouped.

**A condition on an aggregate cannot go in WHERE** (shoplab)

```sql
select c.country, count(*) as orders
from customers c join orders o on o.customer_id = c.id
where count(*) > 66666
group by c.country;
```

```text
ERROR:  aggregate functions are not allowed in WHERE
LINE 3: where count(*) > 66666
              ^
```

**It goes in HAVING: 10 of the 15 groups pass** (shoplab)

```sql
select c.country, o.status, count(*) as orders
from customers c join orders o on o.customer_id = c.id
group by c.country, o.status
having count(*) > 66666
order by c.country, o.status;
```

```text
 country |  status  | orders 
---------+----------+--------
 BR      | paid     |  66667
 BR      | refunded |  66667
 DE      | paid     |  66667
 DE      | shipped  |  66667
 IN      | paid     |  66667
 IN      | shipped  |  66667
 JP      | refunded |  66667
 JP      | shipped  |  66667
 US      | refunded |  66667
 US      | shipped  |  66667
(10 rows)
```

**A SELECT alias does not exist yet in WHERE** (shoplab)

```sql
select c.country, sum(o.amount_cents) as revenue_cents
from customers c join orders o on o.customer_id = c.id
where revenue_cents > 3333300000
group by c.country;
```

```text
ERROR:  column "revenue_cents" does not exist
LINE 3: where revenue_cents > 3333300000
              ^
```

**It does exist in ORDER BY** (shoplab)

```sql
select c.country, sum(o.amount_cents) as revenue_cents
from customers c join orders o on o.customer_id = c.id
group by c.country
order by revenue_cents desc;
```

```text
 country | revenue_cents 
---------+---------------
 JP      |   10000300000
 DE      |   10000100000
 IN      |    9999900000
 BR      |    9999700000
 US      |    9999500000
(5 rows)
```

**But only on its own, not inside an expression** (shoplab)

```sql
select c.country, sum(o.amount_cents) as revenue_cents
from customers c join orders o on o.customer_id = c.id
group by c.country
order by revenue_cents / 100 desc;
```

```text
ERROR:  column "revenue_cents" does not exist
LINE 4: order by revenue_cents / 100 desc;
                 ^
```


## 5. GROUP BY puts the NULLs in one group, and DESC sorts them first

- `groups_country_status_inner`: sample 9 (by hand 9), full 15

- `groups_country_status_left`: sample 10 (by hand 10), full 20

**The five groups whose status is NULL** (shoplab)

```sql
select c.country, o.status, count(*) as rows_in_group,
       count(o.id) as orders, sum(o.amount_cents) as revenue_cents
from customers c
left join orders o on o.customer_id = c.id
group by c.country, o.status
having o.status is null
order by c.country;
```

```text
 country | status | rows_in_group | orders | revenue_cents 
---------+--------+---------------+--------+---------------
 BR      |        |           200 |      0 |              
 DE      |        |           200 |      0 |              
 IN      |        |           200 |      0 |              
 JP      |        |           200 |      0 |              
 US      |        |           200 |      0 |              
(5 rows)
```

Each holds 200 padded rows: count(*) counts them, count(o.id) does not, and sum over no values is NULL.

**Top five by revenue: the NULL groups come first** (shoplab)

```sql
select c.country, o.status,
       count(o.id)         as orders,
       sum(o.amount_cents) as revenue_cents
from customers c
left join orders o on o.customer_id = c.id
group by c.country, o.status
order by revenue_cents desc
limit 5;
```

```text
 country | status | orders | revenue_cents 
---------+--------+--------+---------------
 DE      |        |      0 |              
 BR      |        |      0 |              
 US      |        |      0 |              
 JP      |        |      0 |              
 IN      |        |      0 |              
(5 rows)
```

NULLS FIRST is the default for DESC: a NULL sorts as if larger than every value.

**With NULLS LAST** (shoplab)

```sql
select c.country, o.status,
       count(o.id)         as orders,
       sum(o.amount_cents) as revenue_cents
from customers c
left join orders o on o.customer_id = c.id
group by c.country, o.status
order by revenue_cents desc nulls last
limit 5;
```

```text
 country |  status  | orders | revenue_cents 
---------+----------+--------+---------------
 JP      | refunded |  66667 |    3333499963
 JP      | shipped  |  66667 |    3333433358
 DE      | refunded |  66666 |    3333399963
 DE      | paid     |  66667 |    3333366716
 JP      | paid     |  66666 |    3333366679
(5 rows)
```

**NULLS LAST, five rows with ties** (shoplab)

```sql
select c.country, o.status,
       count(o.id)         as orders,
       sum(o.amount_cents) as revenue_cents
from customers c
left join orders o on o.customer_id = c.id
group by c.country, o.status
order by revenue_cents desc nulls last
fetch first 5 rows with ties;
```

```text
 country |  status  | orders | revenue_cents 
---------+----------+--------+---------------
 JP      | refunded |  66667 |    3333499963
 JP      | shipped  |  66667 |    3333433358
 DE      | refunded |  66666 |    3333399963
 DE      | paid     |  66667 |    3333366716
 JP      | paid     |  66666 |    3333366679
 IN      | paid     |  66667 |    3333366679
(6 rows)
```

**The sample: one NULL group, first** (shopsample)

```sql
select c.country, o.status, count(o.id) as orders, sum(o.amount_cents) as revenue_cents
from customers c left join orders o on o.customer_id = c.id
group by c.country, o.status order by revenue_cents desc;
```

```text
 country |  status  | orders | revenue_cents 
---------+----------+--------+---------------
 IN      |          |      0 |              
 JP      | refunded |      2 |         11500
 DE      | paid     |      3 |          9500
 DE      | shipped  |      1 |          9000
 JP      | shipped  |      2 |          8000
 JP      | paid     |      2 |          7000
 IN      | paid     |      1 |          7000
 IN      | refunded |      1 |          4000
 DE      | refunded |      1 |          2000
 IN      | shipped  |      1 |          1000
(10 rows)
```


## 6. EXISTS and IN keep each customer once; a JOIN repeats it

- `join_paid`: sample 6 (by hand 6), full 333,333

- `join_paid_distinct`: sample 5 (by hand 5), full 100,000

- `in_paid`: sample 5 (by hand 5), full 100,000

- `exists_paid`: sample 5 (by hand 5), full 100,000

**EXISTS: the planner removes duplicate customer ids before it joins** (shoplab)

```sql
explain (costs off) select c.id from customers c
where exists (select 1 from orders o where o.customer_id = c.id and o.status = 'paid');
```

```text
                     QUERY PLAN                      
-----------------------------------------------------
 Hash Join
   Hash Cond: (c.id = o.customer_id)
   ->  Seq Scan on customers c
   ->  Hash
         ->  HashAggregate
               Group Key: o.customer_id
               ->  Seq Scan on orders o
                     Filter: (status = 'paid'::text)
(8 rows)
```

The HashAggregate grouped by o.customer_id keeps each customer id once, so the join above it can match each customer at most once: a semi-join.

**IN gets the same plan** (shoplab)

```sql
explain (costs off) select c.id from customers c
where c.id in (select customer_id from orders where status = 'paid');
```

```text
                     QUERY PLAN                      
-----------------------------------------------------
 Hash Join
   Hash Cond: (c.id = orders.customer_id)
   ->  Seq Scan on customers c
   ->  Hash
         ->  HashAggregate
               Group Key: orders.customer_id
               ->  Seq Scan on orders
                     Filter: (status = 'paid'::text)
(8 rows)
```

**Customer 1 appears twice after the join** (shopsample)

```sql
select c.id, count(*) as rows_after_join
from customers c join orders o on o.customer_id = c.id
where o.status = 'paid'
group by c.id order by c.id;
```

```text
 id | rows_after_join 
----+-----------------
  1 |               2
  2 |               1
  3 |               1
  4 |               1
  5 |               1
(5 rows)
```

**Two joins to orders multiply each other** (shoplab)

```sql
select c.country,
       sum(p.amount_cents) as paid_cents,
       sum(r.amount_cents) as refunded_cents
from customers c
join orders p on p.customer_id = c.id and p.status = 'paid'
join orders r on r.customer_id = c.id and r.status = 'refunded'
group by c.country
order by c.country;
```

```text
 country | paid_cents  | refunded_cents 
---------+-------------+----------------
 BR      | 10999670037 |    10999670037
 DE      | 11000210037 |    11000210037
 IN      | 10999790148 |    10999790148
 JP      | 11000329926 |    11000329926
 US      | 10999549815 |    10999549815
(5 rows)
```

**One join, two filtered sums** (shoplab)

```sql
select c.country,
       sum(o.amount_cents) filter (where o.status = 'paid')     as paid_cents,
       sum(o.amount_cents) filter (where o.status = 'refunded') as refunded_cents
from customers c
join orders o on o.customer_id = c.id
group by c.country
order by c.country;
```

```text
 country | paid_cents | refunded_cents 
---------+------------+----------------
 BR      | 3333266642 |     3333200037
 DE      | 3333366716 |     3333399963
 IN      | 3333366679 |     3333200037
 JP      | 3333366679 |     3333499963
 US      | 3333166605 |     3333200000
(5 rows)
```

**Query A on the sample** (shopsample)

```sql
select c.country,
       sum(p.amount_cents) as paid_cents,
       sum(r.amount_cents) as refunded_cents
from customers c
join orders p on p.customer_id = c.id and p.status = 'paid'
join orders r on r.customer_id = c.id and r.status = 'refunded'
group by c.country
order by c.country;
```

```text
 country | paid_cents | refunded_cents 
---------+------------+----------------
 DE      |       8000 |           4000
 IN      |       7000 |           4000
 JP      |       7000 |          11500
(3 rows)
```

**Its repair on the sample** (shopsample)

```sql
select c.country,
       sum(o.amount_cents) filter (where o.status = 'paid')     as paid_cents,
       sum(o.amount_cents) filter (where o.status = 'refunded') as refunded_cents
from customers c
join orders o on o.customer_id = c.id
group by c.country
order by c.country;
```

```text
 country | paid_cents | refunded_cents 
---------+------------+----------------
 DE      |       9500 |           2000
 IN      |       7000 |           4000
 JP      |       7000 |          11500
(3 rows)
```


## 7. UNION removes duplicates, inside each input as well as across them

- `union_all`: sample 10 (by hand 10), full 666,666

- `union`: sample 5 (by hand 5), full 100,000

**UNION ALL keeps every row** (shoplab)

```sql
select count(*) from (select customer_id from orders where status = 'paid'
union all
select customer_id from orders where status = 'refunded') u;
```

```text
 count  
--------
 666666
(1 row)
```

**UNION keeps each distinct value once** (shoplab)

```sql
select count(*) from (select customer_id from orders where status = 'paid'
union
select customer_id from orders where status = 'refunded') u;
```

```text
 count  
--------
 100000
(1 row)
```

**Even a query UNIONed with itself is deduplicated** (shoplab)

```sql
select count(*) from (select customer_id from orders where status = 'paid' union select customer_id from orders where status = 'paid') u;
```

```text
 count  
--------
 100000
(1 row)
```


## 8. NOT IN and NOT EXISTS agree, until one NULL appears

**Customers with no orders, by NOT IN (default settings, timed)** (shoplab)

```sql
\timing on
select count(*) from customers where id not in (select customer_id from orders);
```

```text
 count 
-------
  1000
(1 row)

Time: 117526.877 ms (01:57.527)
```

**By NOT EXISTS (timed)** (shoplab)

```sql
\timing on
select count(*) from customers c where not exists (select 1 from orders o where o.customer_id = c.id);
```

```text
 count 
-------
  1000
(1 row)

Time: 46.298 ms
```

**NOT IN stays a filter, and its subquery is re-read, not hashed** (shoplab)

```sql
explain (costs off) select count(*) from customers where id not in (select customer_id from orders);
```

```text
                                  QUERY PLAN                                  
------------------------------------------------------------------------------
 Finalize Aggregate
   ->  Gather
         Workers Planned: 2
         ->  Partial Aggregate
               ->  Parallel Index Only Scan using customers_pkey on customers
                     Filter: (NOT (ANY (id = (SubPlan 1).col1)))
                     SubPlan 1
                       ->  Materialize
                             ->  Seq Scan on orders
(9 rows)
```

Not hashed: 1,000,000 rows of about 32 bytes each do not fit in 4 MB x hash_mem_multiplier 2, so the Materialize node is scanned for each customer.

**NOT EXISTS becomes an anti-join** (shoplab)

```sql
explain (costs off) select count(*) from customers c where not exists (select 1 from orders o where o.customer_id = c.id);
```

```text
                                         QUERY PLAN                                         
--------------------------------------------------------------------------------------------
 Finalize Aggregate
   ->  Gather
         Workers Planned: 2
         ->  Partial Aggregate
               ->  Parallel Hash Right Anti Join
                     Hash Cond: (o.customer_id = c.id)
                     ->  Parallel Seq Scan on orders o
                     ->  Parallel Hash
                           ->  Parallel Index Only Scan using customers_pkey on customers c
(9 rows)
```

**NOT IN again, with work_mem = 64MB for this session (timed)** (shoplab)

```sql
\timing on
set work_mem = '64MB';
select count(*) from customers where id not in (select customer_id from orders);
```

```text
Time: 0.092 ms
 count 
-------
  1000
(1 row)

Time: 191.920 ms
```

**With 64 MB the subquery is hashed** (shoplab)

```sql
set work_mem = '64MB';
explain (costs off) select count(*) from customers where id not in (select customer_id from orders);
```

```text
                         QUERY PLAN                         
------------------------------------------------------------
 Aggregate
   ->  Seq Scan on customers
         Filter: (NOT (ANY (id = (hashed SubPlan 1).col1)))
         SubPlan 1
           ->  Seq Scan on orders
(5 rows)
```

**Let customer_id be NULL** (shoplab)

```sql
alter table orders alter column customer_id drop not null;
```

```text

```

shopgen declared it NOT NULL; this is the one change that lets the next statement work.

**Order 4242 loses its customer** (shoplab)

```sql
update orders set customer_id = null where id = 4242;
```

```text

```

**In the sample, order 105 loses its customer** (shopsample)

```sql
update orders set customer_id = null where id = 105;
```

```text

```

**NOT IN now finds no one (default settings, timed)** (shoplab)

```sql
\timing on
select count(*) from customers where id not in (select customer_id from orders);
```

```text
 count 
-------
     0
(1 row)

Time: 117924.868 ms (01:57.925)
```

**NOT EXISTS still finds the same 1,000 (timed)** (shoplab)

```sql
\timing on
select count(*) from customers c where not exists (select 1 from orders o where o.customer_id = c.id);
```

```text
 count 
-------
  1000
(1 row)

Time: 50.547 ms
```

**NOT IN works again once the NULL is filtered out of the subquery (work_mem = 64MB for speed)** (shoplab)

```sql
set work_mem = '64MB';
select count(*) from customers where id not in (select customer_id from orders
                                         where customer_id is not null);
```

```text
 count 
-------
  1000
(1 row)
```

**Why: NOT IN is a chain of <> comparisons joined by AND** (shoplab)

```sql
select 100001 not in (1, 2, null) as one_null,
       100001 not in (1, 2)       as no_null,
       100001 <> null              as compare_with_null;
```

```text
 one_null | no_null | compare_with_null 
----------+---------+-------------------
          | t       | 
(1 row)
```

**GROUP BY gives the NULL a group of its own** (shoplab)

```sql
select count(*) as groups from (select customer_id from orders
                              group by customer_id) g;
```

```text
 groups 
--------
 100001
(1 row)
```

**UNION keeps one NULL** (shoplab)

```sql
select count(*) from (select customer_id from orders where status = 'paid' union select customer_id from orders where status = 'refunded') u;
```

```text
 count  
--------
 100001
(1 row)
```

The six queries of exercise E3, before and after the NULL:

- `q1_join_count`: 1,000,000 → 999,999

- `q2_in`: 100,000 → 100,000

- `q3_not_in`: 1,000 → 0

- `q4_not_exists`: 1,000 → 1,000

- `q5_count_distinct`: 100,000 → 100,000

- `q6_groups`: 100,000 → 100,001

**Query B's repair** (shoplab)

```sql
select count(*) as customers_without_orders
from customers c
where not exists (select 1 from orders o where o.customer_id = c.id);
```

```text
 customers_without_orders 
--------------------------
                     1000
(1 row)
```

**Query C's first draft, and the error that started it** (shoplab)

```sql
select c.country, count(*) as big_orders
from customers c join orders o on o.customer_id = c.id
group by c.country
having o.amount_cents >= 90000;
```

```text
ERROR:  column "o.amount_cents" must appear in the GROUP BY clause or be used in an aggregate function
LINE 4: having o.amount_cents >= 90000;
               ^
```

**Query C as shipped** (shoplab)

```sql
select c.country, count(*) as big_orders
from customers c
join orders o on o.customer_id = c.id
group by c.country
having max(o.amount_cents) >= 90000
order by c.country;
```

```text
 country | big_orders 
---------+------------
 BR      |     200000
 DE      |     200000
 IN      |     200000
 JP      |     199999
 US      |     200000
(5 rows)
```

**Its repair** (shoplab)

```sql
select c.country, count(*) as big_orders
from customers c
join orders o on o.customer_id = c.id
where o.amount_cents >= 90000
group by c.country
order by c.country;
```

```text
 country | big_orders 
---------+------------
 BR      |      20000
 DE      |      20000
 IN      |      20000
 JP      |      20000
 US      |      20000
(5 rows)
```


## 9. Three ways to write R minus S, three answers

The example from Guagliardo and Libkin (PVLDB 2017): R = {1, NULL}, S = {NULL}.

**R minus S by NOT IN** (postgres)

```sql
with r(a) as (values (1), (null::int)), s(a) as (values (null::int))
select a from r where a not in (select a from s) order by a;
```

```text
 a 
---
(0 rows)
```

**R minus S by NOT EXISTS** (postgres)

```sql
with r(a) as (values (1), (null::int)), s(a) as (values (null::int))
select a from r where not exists (select 1 from s where s.a = r.a) order by a;
```

```text
 a 
---
 1
  
(2 rows)
```

**R minus S by EXCEPT** (postgres)

```sql
with r(a) as (values (1), (null::int)), s(a) as (values (null::int))
select a from r except select a from s order by a;
```

```text
 a 
---
 1
(1 row)
```

