-- The 20-row sample: 6 customers and 14 orders, with the same two table declarations as the
-- full shop. It is built by hand, not by shopgen, so that every effect in the post shows up
-- at least once in rows you can count on paper:
--   customer 6 has placed no order, so LEFT JOIN and INNER JOIN differ by one row;
--   customer 1 has two paid orders, so a join repeats it and EXISTS does not;
--   IN and JP have the same paid revenue, 7,000 cents, so "top 2" has a tie at the boundary.
-- run_lab.py loads it into its own database, shopsample, and runs the same queries on it.

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

insert into customers (id, name, country) values
    (1, 'customer 1', 'DE'),
    (2, 'customer 2', 'IN'),
    (3, 'customer 3', 'JP'),
    (4, 'customer 4', 'DE'),
    (5, 'customer 5', 'JP'),
    (6, 'customer 6', 'IN');

insert into orders (id, customer_id, amount_cents, created, status) values
    (101, 1, 5000, '2026-01-01 00:00:01+00', 'paid'),
    (102, 1, 3000, '2026-01-01 00:00:02+00', 'paid'),
    (103, 1, 2000, '2026-01-01 00:00:03+00', 'refunded'),
    (104, 2, 7000, '2026-01-01 00:00:04+00', 'paid'),
    (105, 2, 1000, '2026-01-01 00:00:05+00', 'shipped'),
    (106, 2, 4000, '2026-01-01 00:00:06+00', 'refunded'),
    (107, 3, 6000, '2026-01-01 00:00:07+00', 'paid'),
    (108, 3, 2500, '2026-01-01 00:00:08+00', 'shipped'),
    (109, 4, 9000, '2026-01-01 00:00:09+00', 'shipped'),
    (110, 4, 1500, '2026-01-01 00:00:10+00', 'paid'),
    (111, 5, 1000, '2026-01-01 00:00:11+00', 'paid'),
    (112, 5, 3500, '2026-01-01 00:00:12+00', 'refunded'),
    (113, 5, 5500, '2026-01-01 00:00:13+00', 'shipped'),
    (114, 3, 8000, '2026-01-01 00:00:14+00', 'refunded');

vacuum analyze customers;
vacuum analyze orders;
