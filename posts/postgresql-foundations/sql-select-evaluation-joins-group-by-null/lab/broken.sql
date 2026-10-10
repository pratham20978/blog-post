-- Three queries that run without an error and return the wrong answer.
-- Exercise E4 in README.md: copy this file to fixed.sql, repair each query in place, and mark
-- your repairs with `python3 check.py e4 --verify`. Keep the three marker lines exactly as
-- they are; check.py finds each query by them. Run `python3 check.py e4 --break` first: the
-- answers are only wrong in the state that sets up.

-- A. Paid and refunded revenue per country, side by side.
select c.country,
       sum(p.amount_cents) as paid_cents,
       sum(r.amount_cents) as refunded_cents
from customers c
join orders p on p.customer_id = c.id and p.status = 'paid'
join orders r on r.customer_id = c.id and r.status = 'refunded'
group by c.country
order by c.country;

-- B. How many customers have never placed an order?
select count(*) as customers_without_orders
from customers
where id not in (select customer_id from orders);

-- C. How many orders of at least 90,000 cents did each country receive?
-- (The first version had `having o.amount_cents >= 90000`, which PostgreSQL rejected, so
-- the author wrapped the column in max() until the error went away.)
select c.country, count(*) as big_orders
from customers c
join orders o on o.customer_id = c.id
group by c.country
having max(o.amount_cents) >= 90000
order by c.country;
