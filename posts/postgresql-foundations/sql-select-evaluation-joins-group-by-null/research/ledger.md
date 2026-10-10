# Source ledger — sql-select-evaluation-joins-group-by-null

Research ran 2026-10-02. Every server-side number comes from one run of `lab/run_lab.py`
(PostgreSQL 18.6 built from the official source release, default `postgresql.conf`, on a
temporary cluster deleted after capture; the shipped run is the one whose captures carry the
timestamp quoted in `lab/captures.md`). Documentation claims were checked against the
PostgreSQL 18 documentation pages below, saved and read in full. Source-code claims were read
in the files of tag `REL_18_6`. Every paper claim was checked against a full text we fetched and
read, not an abstract or a snippet.

Three things research changed about the plan:

- **NOT IN is also a performance trap, for the same reason it is a correctness trap.** The
  planner cannot turn NOT IN into an anti-join because it cannot tell FALSE from NULL under a NOT
  (L27), and a 1,000,000-row subquery does not fit the default hash memory (L28), so the lab's
  NOT IN took about two minutes against 50 ms for NOT EXISTS. The post states the number once
  and leaves the measurement to the slow-query part of the series, which owns it. PostgreSQL 19,
  in beta, converts NOT IN to an anti-join only when it can prove no NULLs (L24).
- **"NOT EXISTS gives the right answer" needed a qualifier.** The literature does not agree
  on what the right answer is once a NULL is present (L32–L36). The post says what each query
  returns, why, and which one to use, and names the disagreement instead of settling it.
- **The tie at LIMIT 2 is not hypothetical.** IN and JP tie on paid revenue, and the second
  row of the same query changed from IN to JP when the plan changed (L47). The plan said
  "LIMIT 10 with ties"; the data's tie sits at position 2 of the country report and at 5/6 of
  the country-and-status report, so the post uses those.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S1 | T2 | PostgreSQL 18 docs, SQL Commands: SELECT (Description; WHERE, GROUP BY, HAVING, SELECT List, DISTINCT, UNION, ORDER BY and LIMIT clauses) | — | 2025 | — | official-docs | https://www.postgresql.org/docs/18/sql-select.html | 2026-10-02 |
| S2 | T2 | PostgreSQL 18 docs, §7.2 Table Expressions (§7.2.1.1 Joined Tables, §7.2.2 WHERE, §7.2.3 GROUP BY and HAVING) | — | 2025 | — | official-docs | https://www.postgresql.org/docs/18/queries-table-expressions.html | 2026-10-02 |
| S3 | T2 | PostgreSQL 18 docs, §7.3 Select Lists (§7.3.3 DISTINCT) | — | 2025 | — | official-docs | https://www.postgresql.org/docs/18/queries-select-lists.html | 2026-10-02 |
| S4 | T2 | PostgreSQL 18 docs, §7.4 Combining Queries (UNION, INTERSECT, EXCEPT) | — | 2025 | — | official-docs | https://www.postgresql.org/docs/18/queries-union.html | 2026-10-02 |
| S5 | T2 | PostgreSQL 18 docs, §7.5 Sorting Rows (ORDER BY) | — | 2025 | — | official-docs | https://www.postgresql.org/docs/18/queries-order.html | 2026-10-02 |
| S6 | T2 | PostgreSQL 18 docs, §7.6 LIMIT and OFFSET | — | 2025 | — | official-docs | https://www.postgresql.org/docs/18/queries-limit.html | 2026-10-02 |
| S7 | T2 | PostgreSQL 18 docs, §9.24 Subquery Expressions (EXISTS, IN, NOT IN, ANY, ALL) | — | 2025 | — | official-docs | https://www.postgresql.org/docs/18/functions-subquery.html | 2026-10-02 |
| S8 | T2 | PostgreSQL 18 docs, §4.2.7 Aggregate Expressions (FILTER) | — | 2025 | — | official-docs | https://www.postgresql.org/docs/18/sql-expressions.html | 2026-10-02 |
| S9 | T2 | PostgreSQL 18 docs, §19.4.1 Memory (work_mem, hash_mem_multiplier) | — | 2025 | — | official-docs | https://www.postgresql.org/docs/18/runtime-config-resource.html | 2026-10-02 |
| S10 | T2 | PostgreSQL docs, Release 13 notes | — | 2020 | — | official-docs | https://www.postgresql.org/docs/18/release-13.html | 2026-10-02 |
| S13 | T2 | PostgreSQL 19 docs, Release 19 notes ("as of 2026-09-14", release date not yet set; 19 is in beta) | — | 2026 | — | official-docs | https://www.postgresql.org/docs/19/release-19.html | 2026-10-02 |
| S14 | T2 | PostgreSQL versioning policy page (current minor releases) and news archive (19 Beta 4, 2026-09-24) | — | 2026 | — | official-docs | https://www.postgresql.org/support/versioning/ | 2026-10-02 |
| S15 | T3 | PostgreSQL REL_18_6, `src/backend/optimizer/plan/planner.c` (moving HAVING clauses into WHERE) | — | 2026 | REL_18_6 | source | https://github.com/postgres/postgres/blob/REL_18_6/src/backend/optimizer/plan/planner.c | 2026-10-02 |
| S16 | T3 | PostgreSQL REL_18_6, `src/backend/optimizer/prep/prepjointree.c` (`pull_up_sublinks`) | — | 2026 | REL_18_6 | source | https://github.com/postgres/postgres/blob/REL_18_6/src/backend/optimizer/prep/prepjointree.c | 2026-10-02 |
| S17 | T3 | PostgreSQL REL_18_6, `src/backend/optimizer/plan/subselect.c` (`subplan_is_hashable`) | — | 2026 | REL_18_6 | source | https://github.com/postgres/postgres/blob/REL_18_6/src/backend/optimizer/plan/subselect.c | 2026-10-02 |
| S18 | T1 | Date, C. J. "A Critique of the SQL Database Language" | ACM SIGMOD Record 14(3), pp. 8–54 | 1984 | 10.1145/984549.984551 | peer-reviewed | https://sigmodrecord.org/1984/11/01/a-critique-of-the-sql-database-language/ | 2026-10-02 |
| S19 | T1 | Rubinson, C. "Nulls, Three-Valued Logic, and Ambiguity in SQL: Critiquing Date's Critique" | ACM SIGMOD Record 36(4), pp. 13–17 | 2007 | 10.1145/1361348.1361350 | peer-reviewed | https://sigmodrecord.org/2007/12/27/nulls-three-valued-logic-and-ambiguity-in-sql/ | 2026-10-02 |
| S20 | T1 | Date, C. J. "A Critique of Claude Rubinson's Paper Nulls, Three-Valued Logic, and Ambiguity in SQL" | ACM SIGMOD Record 37(3), pp. 20–22 | 2008 | 10.1145/1462571.1462574 | peer-reviewed | https://sigmodrecord.org/2008/09/25/a-critique-of-claude-rubinsons-paper-nulls-three-valued-logic-and-ambiguity-in-sql/ | 2026-10-02 |
| S21 | T1 | Grant, J. "Null Values in SQL" | ACM SIGMOD Record 37(3), pp. 23–25 | 2008 | 10.1145/1462571.1462575 | peer-reviewed | https://sigmodrecord.org/2008/09/25/null-values-in-sql/ | 2026-10-02 |
| S22 | T1 | Libkin, L. "SQL's Three-Valued Logic and Certain Answers" (CC BY) | ICDT 2015, LIPIcs 31, pp. 94–109 | 2015 | 10.4230/LIPIcs.ICDT.2015.94 | peer-reviewed | https://drops.dagstuhl.de/storage/00lipics/lipics-vol031-icdt2015/LIPIcs.ICDT.2015.94/LIPIcs.ICDT.2015.94.pdf | 2026-10-02 |
| S23 | T1 | Guagliardo, P., Libkin, L. "A Formal Semantics of SQL Queries, Its Validation, and Applications" | PVLDB 11(1), pp. 27–39 | 2017 | 10.14778/3151113.3151116 | peer-reviewed | https://www.vldb.org/pvldb/vol11/p27-guagliardo.pdf | 2026-10-02 |
| S24 | T1 | Libkin, L., Peterfreund, L. "SQL Nulls and Two-Valued Logic" (read as arXiv:2012.13198v3) | PODS 2023, pp. 11–20 | 2023 | 10.1145/3584372.3588661 | peer-reviewed | https://arxiv.org/abs/2012.13198v3 | 2026-10-02 |
| S25 | T1 | Ricciotti, W., Cheney, J. "A Formalization of SQL with Nulls" (read as arXiv:2003.11331v2) | Journal of Automated Reasoning 66(4), pp. 989–1030 | 2022 | 10.1007/s10817-022-09632-4 | peer-reviewed | https://arxiv.org/abs/2003.11331v2 | 2026-10-02 |
| S26 | T1 | Taipalus, T., Siponen, M., Vartiainen, T. "Errors and Complications in SQL Query Formulation" (read as the accepted manuscript) | ACM Transactions on Computing Education 18(3), pp. 1–29 | 2018 | 10.1145/3231712 | peer-reviewed | https://osuva.uwasa.fi/handle/10024/10191 | 2026-10-02 |
| S27 | T3 | This post's lab: `lab/run_lab.py`, `lab/shopgen.py`, `lab/sample.sql`, captures of 2026-10-02 | — | 2026 | lab/captures.json | source | (downloadable lab) | 2026-10-02 |

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | OpenAlex | 18 title searches: incomplete-data survey, SQL nulls and certain answers, formal SQL semantics, SQL error studies, the 1984–2008 NULL critiques, outer joins, nested-query unnesting, semi-joins | located the PODS 2020 survey (Console, Guagliardo, Libkin, Toussaint), Libkin ICDT 2015 / TODS 2016, Guagliardo & Libkin PVLDB 2017 and PODS 2016, Taipalus et al. 2018, Miedema et al. 2021, Brass & Goldberg 2006, the four NULL critiques, Codd 1979, Kim 1982, Ganski & Wong 1987, Bernstein & Chiu 1981 |
| 2 | 1 | Google Scholar | "Coping with incomplete data" recent advances Libkin | the survey first: PODS 2020, cited by 30; Scholar links only the ACM copy |
| 3 | 1 | OpenAlex | DOI lookups for open copies of eight papers | alternative copies at HAL, Edinburgh's research portal, Vaasa (Taipalus), TU/e (Miedema) and vldb.org (Guagliardo & Libkin 2017) |
| 4 | 1 | HAL, Edinburgh research portal, Sapienza IRIS | full text of the survey and of PODS 2016 / TODS 2016 | refused automated fetches (an Anubis bot challenge at HAL, 403 at the other two); not read, and no claim rests on them |
| 5 | 1 | arXiv | ti:"SQL" AND ti:nulls; ti:"incomplete data" AND au:libkin | Ricciotti & Cheney (2003.11331), Libkin & Peterfreund (2012.13198), Franconi & Tessaris (2202.10898) |
| 6 | 1 | Semantic Scholar | three title searches for the survey and the NULL papers | HTTP 429 on every request; unavailable this session, as in earlier parts |
| 7 | 1 | DBLP | "Coping with Incomplete Data Recent Advances" | bot-challenge page (Anubis); unavailable |
| 8 | 1 | SIGMOD Record archive | issues of November 1984, December 2007 and September 2008 | open PDFs of Date 1984, Rubinson 2007, Date 2008 and Grant 2008, the four texts part 4 located but could not read |
| 9 | 1 | Crossref | venue checks for S18–S26 | PODS 2023 pp. 11–20; JAR 66(4) 989–1030; PVLDB 11(1) 27–39; TOCE 18(3) 1–29; the SIGMOD Record pages |
| 10 | 1 | arXiv, Crossref | forward one hop from Guagliardo & Libkin 2017 | Ricciotti & Cheney 2022 mechanise the semantics in Coq (no grouping or aggregation); Libkin & Peterfreund 2023 build a two-valued SQL on it. Both reproduce the NOT IN / NOT EXISTS divergence |
| 11 | 1 | Libkin 2015, reference list | backward one hop from Libkin 2015 | Date's critiques, Codd 1979 (TODS), Imieliński & Lipski 1984 (JACM), Grant 1977; Codd 1979 and Imieliński–Lipski are ACM-only (403) and were not read |
| 12 | 1 | ACM Digital Library | full text of Date 1984, Codd 1979, Rubinson 2007 | 403 to automated fetches; the SIGMOD Record archive (row 8) served three of them |
| 13 | 2 | PostgreSQL 18 docs | SELECT reference; ch. 7 Queries, §7.2–§7.6 | the processing order, ON against WHERE in outer joins, HAVING, NULLs in DISTINCT, UNION, NULL ordering, ties, LIMIT, WITH TIES |
| 14 | 2 | PostgreSQL 18 docs | §9.24 Subquery Expressions; §4.2.7 Aggregate Expressions; §19.4.1 Memory | the NOT IN null rule, EXISTS keeping each outer row once, FILTER, work_mem 4 MB and hash_mem_multiplier 2.0 |
| 15 | 5 | PostgreSQL release notes | 13, 16, 17, 18, and 19 (beta) | WITH TIES (13); right anti joins (16); the SubPlan display (17); right semi joins (18); NOT IN to anti-join when no NULLs, and aggregation before joins (19). Only 13 and 19 carry a claim the post makes |
| 16 | 5 | PostgreSQL REL_18_6 source | planner.c, prepjointree.c, subselect.c, tuplesort.c | HAVING moved into WHERE; NOT IN not pulled up under a NOT; a subplan hashed only when it fits hash memory; a bounded heap discards a tuple that only ties the worst kept one |
| 17 | 3 | Our lab | run_lab.py on PostgreSQL 18.6, four runs | every server number; the last run's captures are shipped. Data values identical in all runs; NOT IN timings 115.9–122.0 s, NOT EXISTS 45–51 ms; the tie went the same way in every run under each setting |
| 18 | 4 | SIGMOD Record | the 1984–2008 debate over SQL's NULL logic | Date and Grant against Rubinson; see L32–L34 |
| 19 | 6 | ACM TOCE | how learners actually get these wrong | Taipalus et al. 2018, 33,000+ student queries, error categories that include this post's traps |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | PostgreSQL's SELECT reference lists the general processing order: WITH queries, then FROM (several items are cross-joined), WHERE, GROUP BY with aggregates and HAVING, the SELECT output expressions, DISTINCT, UNION/INTERSECT/EXCEPT, ORDER BY, LIMIT/OFFSET/FETCH, and last the locking clauses | S1 Description | it describes the result, not the execution |
| L02 | An output column's name can be used in ORDER BY and GROUP BY, but not in WHERE or HAVING, where the expression must be written out | S1 SELECT List | — |
| L03 | The standard says output expressions are computed before DISTINCT, ORDER BY and LIMIT; PostgreSQL evaluates them after sorting and limiting when they are not referenced by DISTINCT, ORDER BY or GROUP BY | S1 SELECT List | since 9.6 |
| L04 | WHERE keeps a row only when its condition is true; a false or null result discards it | S2 §7.2.2; S1 WHERE Clause | — |
| L05 | An inner join has one row for each pair of rows that satisfies the join condition. A left outer join is the inner join plus one row for each unmatched left row, padded with nulls in the right table's columns, so every left row appears at least once. A right join is a left join with the tables swapped; a full join adds the unmatched rows of both sides | S2 §7.2.1.1; S1 FROM Clause | — |
| L06 | A restriction in ON is processed before the join and one in WHERE after it; it makes no difference for inner joins and a large one for outer joins | S2 §7.2.1.1 | — |
| L07 | WHERE filters individual rows before GROUP BY; HAVING filters the group rows GROUP BY created | S1 HAVING Clause | — |
| L08 | In a grouped query, the SELECT list may refer to an ungrouped column only inside an aggregate, or when the grouped columns include the primary key of that column's table | S1 GROUP BY Clause; S2 §7.2.3 | — |
| L09 | Strict SQL groups only by source-table columns; PostgreSQL also accepts output column names in GROUP BY, and on a clash takes the input column, the opposite of ORDER BY | S2 §7.2.3; S1 GROUP BY and ORDER BY Clauses | — |
| L10 | DISTINCT considers null values equal to each other | S3 §7.3.3 | — |
| L11 | UNION removes duplicate rows in the same way as DISTINCT unless ALL is written; UNION ALL is usually much faster | S4 §7.4; S1 UNION Clause | — |
| L12 | Rows equal on every ORDER BY expression come back in an implementation-dependent order | S1 ORDER BY Clause | — |
| L13 | NULLs sort as if larger than every non-null value: NULLS FIRST is the default for DESC and NULLS LAST otherwise | S5 §7.5 | — |
| L14 | LIMIT without an ORDER BY that makes the order unique returns an unpredictable subset; the planner takes LIMIT into account, so different LIMIT values can give inconsistent results and repeated runs can differ | S6 §7.6; S1 LIMIT Clause | — |
| L15 | FETCH FIRST n ROWS WITH TIES also returns the rows that tie with the last one under ORDER BY, which is mandatory with it | S1 LIMIT Clause | — |
| L16 | WITH TIES arrived in PostgreSQL 13 | S10 | — |
| L17 | EXISTS is true when the subquery returns at least one row, and produces at most one output row per outer row however many rows match | S7 §9.24.1 | — |
| L18 | NOT IN is true only if every subquery row is unequal; it is false if any is equal; with no equal value and at least one NULL on the right it is NULL, not true. NOT IN is equivalent to `<> ALL`, IN to `= ANY` | S7 §9.24.3–§9.24.5 | — |
| L19 | IN with no match and a NULL among the subquery's values is NULL, not false | S7 §9.24.2 | — |
| L20 | With FILTER, only the input rows for which the filter clause is true are fed to that aggregate | S8 §4.2.7 | — |
| L23 | work_mem defaults to 4 MB; a hash table, including the one for hash-based IN subqueries, may use work_mem times hash_mem_multiplier, which defaults to 2.0 | S9 §19.4.1 | — |
| L24 | PostgreSQL 19, in beta, converts NOT IN to an anti-join when NULLs are not present, and can aggregate some rows before a join | S13 §E.1.3.1.1 | release notes "as of 2026-09-14"; 19 Beta 4 released 2026-09-24 (S14) |
| L25 | On 2026-10-02 PostgreSQL 18.6 was the current 18.x release and 19 was in beta | S14 | — |
| L26 | The planner moves a HAVING clause into WHERE when it has no aggregates, volatile functions or subplans (and no grouping-set conflict), so that rows are eliminated before aggregation instead of after | S15, comment above the HAVING loop in `subquery_planner` | PostgreSQL 18.6 |
| L27 | The planner turns top-level IN and EXISTS subqueries into semi-joins and NOT EXISTS into an anti-join; an IN under a NOT is left alone, because the planner cannot tell whether it should give FALSE or NULL | S16 `pull_up_sublinks` | PostgreSQL 18.6 |
| L28 | A NOT IN subquery is hashed only when its estimated size, rows times (row width plus a tuple header), fits in hash memory; otherwise its output is materialised and read again for each outer row | S17 `subplan_is_hashable` and the comment above its use | PostgreSQL 18.6 |
| L29 | In 1983 the SQL Date described treated NULLs as duplicates of each other for UNIQUE, DISTINCT and ORDER BY but not for WHERE and GROUP BY, and its UNION always removed duplicates, with no ALL option | S18 pp. 32–33 | IBM's SQL of 1983, not today's standard |
| L30 | Date wrote that a condition such as SUM(QTY) > 1000 cannot go in WHERE, and that the reason for HAVING is not immediately apparent to users, who ask why a WHERE clause will not do | S18 pp. 20–21 | — |
| L31 | Rubinson argues that under three-valued logic "the cities are different" means "we know the cities are different", so SQL answers the question as posed; he still advises non-nullable columns by default and avoiding null-producing operations such as outer joins where possible | S19 §3–§5 | — |
| L32 | Date replies that SQL's logic differs from the logic of the real world, and that a table containing a NULL is not a relation | S20 | — |
| L33 | Grant sides with Date: SQL adopted Codd's truth-table three-valued logic, which Grant had shown in 1977 can give wrong answers, so the fault is in how SQL uses the third value, not in having one | S21 §3, §5 | — |
| L34 | `select R.A from R where R.A not in (select S.A from S)` returns nothing whenever S contains a single NULL, whatever R holds | S22 §1, query (2) | — |
| L35 | SQL evaluates a condition in three-valued logic but returns only the rows where it is true, folding unknown into false; with negation in a subquery (NOT IN, NOT EXISTS) this can return rows that are not certain answers. A certain answer is one that is in the result for every complete database the incomplete one could stand for | S22 §1 | — |
| L36 | With R = {1, NULL} and S = {NULL}, the NOT IN version of R minus S returns nothing, the NOT EXISTS version returns {1, NULL} and EXCEPT returns {1}; the three agree on databases without NULLs | S23 §1 Example 1 | — |
| L37 | SQL tables are bags. A Cartesian product multiplies occurrences, UNION ALL adds them, and UNION is UNION ALL with duplicates removed | S23 §3, Fig. 7 | — |
| L38 | Set operations such as difference and intersection treat two values, NULL included, as equal when they are syntactically the same | S23 §1 | — |
| L39 | Guagliardo and Libkin's semantics matched PostgreSQL and Oracle on 100,000 randomly generated queries | S23 §4 | queries without aggregation |
| L40 | SQL uses NULL in three ways: WHERE keeps only true rows; a constraint holds unless it is false; grouping and set operations treat NULL as a constant, so two NULLs are equal | S24 §1 | — |
| L41 | Rewriting NOT IN as NOT EXISTS is routinely presented as safe, yet the two differ once a NULL is present, and many programmers do not know it | S24 §1 | — |
| L42 | In 33,000+ student queries, the semantic errors included NULL in an IN/ANY/ALL subquery, many duplicate rows, HAVING without GROUP BY, and DISTINCT that may remove needed duplicates; a join written with IN produced duplicate rows less often than an explicit join | S26 §4.2, Table 4 | an introductory course; the categories follow Brass and Goldberg (2006) |
| L43 | Lab: PostgreSQL 18.6, default `postgresql.conf`, 16 CPUs, 14 GB RAM, NVMe. shopgen scale M plus `--orderless 1000`: 101,000 customers (717 pages) and 1,000,000 orders (7,693 pages); each of the first 100,000 customers has exactly 10 orders, the other 1,000 have none | S27 §1 | — |
| L44 | Generator arithmetic: customer_id = 1 + (7,919 × g mod 100,000) for order g; 7,919 shares no factor with 100,000, so each customer is visited once per 100,000 orders, 10 times in 1,000,000; status cycles with g mod 3, giving 333,333 paid orders | S27 `shopgen.py`, §1 | the lab confirms the counts (L43, L45) |
| L45 | Lab: 66,667 customers have 3 paid orders and 33,333 have 4 | S27 §1 | — |
| L46 | Lab: the report's row count after each clause: FROM customers 101,000; JOIN orders 1,000,000; WHERE paid 333,333; GROUP BY country 5. Paid orders and revenue in cents: DE 66,667 / 3,333,366,716; IN 66,667 / 3,333,366,679; JP 66,666 / 3,333,366,679; BR 66,667 / 3,333,266,642; US 66,666 / 3,333,166,605 | S27 §2 | — |
| L47 | Lab: LIMIT 2 returned DE then IN under the default settings, with hash aggregation off, and with both off; DE then JP with parallel workers off or with sorting discouraged. The default plan hands the groups to the final sort in country order (BR, DE, IN, JP, US); with parallel workers off a HashAggregate hands them on in another order, with JP before IN. FETCH FIRST 2 ROWS WITH TIES returned DE, IN and JP. On the sample, the default gave JP second and hash aggregation off gave IN | S27 §2 | reproduced in every lab run on this machine; another machine may differ, which is the point |
| L49 | Lab sample (6 customers, 14 orders): INNER JOIN 14 rows, LEFT JOIN 15, WHERE paid 6, condition in ON 7, 3 groups: DE 3 orders / 9,500, IN 1 / 7,000, JP 2 / 7,000; HAVING count(*) >= 2 keeps DE and JP. Every one matched the count worked by hand | S27 §2–§4 | — |
| L50 | Lab: LEFT JOIN 1,001,000 rows, 1,000 of them padded; LEFT JOIN plus WHERE o.status = 'paid' 333,333; the condition in ON instead 334,333. The plan of the WHERE version has an inner hash join and no left join | S27 §3 | — |
| L51 | Lab: status = 'paid' as WHERE and as HAVING, grouped by country and status, returned the same 5 rows with byte-identical plans: the condition is a Filter on the scan of orders, and the group key is country alone. Logically 333,333 rows reach the grouping step one way and 1,000,000 the other, forming 5 groups against 15 | S27 §4 | — |
| L52 | Lab: count(*) > 66666 in WHERE is rejected ("aggregate functions are not allowed in WHERE"); in HAVING, 10 of the 15 country-and-status groups pass | S27 §4 | — |
| L53 | Lab: a SELECT alias in WHERE is rejected as a column that does not exist; in ORDER BY it works on its own and is rejected inside an expression | S27 §4 | — |
| L54 | Lab: LEFT JOIN grouped by country and status gives 20 groups: the 15 real ones and 5 with a NULL status, one per country, each holding 200 padded rows with count(o.id) 0 and sum NULL. ORDER BY revenue DESC LIMIT 5 returned those five; with NULLS LAST the top five were JP refunded, JP shipped, DE refunded, DE paid and JP paid, and WITH TIES added IN paid, tied at 3,333,366,679 | S27 §5 | — |
| L55 | Lab: customers with a paid order: JOIN 333,333 rows, JOIN with DISTINCT 100,000, IN 100,000, EXISTS 100,000. For EXISTS and IN the plan removes duplicate customer ids with a HashAggregate before an inner hash join | S27 §6 | — |
| L56 | Lab: query A, two joins to orders, produced 1,099,998 rows before grouping; it reported BR's paid revenue as 10,999,670,037 cents against 3,333,266,642 (3.3 times). On the sample it doubled DE's refunded total (4,000 for 2,000) and lost customer 4's paid order (8,000 for 9,500) | S27 §6 | — |
| L57 | Lab: customer ids of paid orders (333,333 rows) UNION ALL those of refunded orders (333,333) gives 666,666 rows; UNION gives 100,000, and the paid list UNIONed with itself also gives 100,000 | S27 §7 | — |
| L58 | Lab, before any NULL: NOT IN, NOT EXISTS, LEFT JOIN … IS NULL and EXCEPT each found the 1,000 customers with no orders. At the default settings NOT IN took 117.5 s; its plan re-reads a materialised copy of orders under a filter. NOT EXISTS took 46.3 ms as a parallel hash right anti join. With work_mem 64 MB, NOT IN's subquery was hashed and it took 191.9 ms | S27 §8 | timings from one run on this laptop; across four runs NOT IN took 115.9–122.0 s |
| L59 | Lab, after order 4242's customer_id is set to NULL: NOT IN finds 0 customers (117.9 s); NOT EXISTS, LEFT JOIN … IS NULL and EXCEPT still find 1,000; NOT IN over `customer_id is not null` finds 1,000 again | S27 §8 | — |
| L60 | Lab: `100001 not in (1, 2, null)` is NULL, `100001 not in (1, 2)` is true, and `100001 <> null` is NULL | S27 §8 | — |
| L61 | Lab, after the NULL: the join count falls to 999,999, GROUP BY customer_id gives 100,001 groups, UNION 100,001 rows; IN still finds 100,000, count(DISTINCT customer_id) is still 100,000, UNION ALL still 666,666. Of the six E3 queries, 1, 3 and 6 change | S27 §8 | — |
| L62 | Lab: R = {1, NULL}, S = {NULL} on PostgreSQL 18.6: NOT IN returns 0 rows, NOT EXISTS returns 1 and NULL, EXCEPT returns 1 | S27 §9 | — |
| L63 | Lab: query C's first draft, `having o.amount_cents >= 90000`, is rejected (the column must appear in GROUP BY or an aggregate); wrapped in max() it runs and reports 200,000 orders per country; the WHERE version reports 20,000 | S27 §8 | 199,999 for JP after the E4 fault, which removes one JP order from the join |
| L64 | Lab: in exercise E4's state, query B (NOT IN) returns 0 and its repair with NOT EXISTS returns 1,000 | S27 §8 | — |

## Figure candidates

No figure from any source is reused. Guagliardo and Libkin 2017, Figure 1 (Kleene's truth tables)
was the one candidate: it states the rules, but the post's own figure carries the same rules on
real rows from the lab, which the paper's cannot. Libkin 2015 (CC BY) has no figure for the
NOT IN example; its example is a query and a sentence. Every figure in the post is original and
drawn from `lab/captures.json` or the hand-worked sample.

## Open questions

- **The 2020 survey was located but not read.** Console, Guagliardo, Libkin and Toussaint,
  "Coping with Incomplete Data: Recent Advances" (PODS 2020, 10.1145/3375395.3387970), is the
  survey this sweep looked for first. Every copy refused an automated fetch (ACM 403, HAL bot
  challenge, Edinburgh 403, Sapienza 403). Libkin 2015 (S22) carried the survey's job for this
  post: its introduction states the problem and the certain-answer framework. No claim rests on
  the survey.
- **Not read, and not cited:** Guagliardo & Libkin PODS 2016 (how often TPC-H queries return
  non-certain answers), Libkin TODS 2016 (the journal version of S22), Miedema et al. ICER 2021
  (novice misconceptions), Brass & Goldberg 2006 (cited only through S26's table), Codd 1979,
  Imieliński & Lipski 1984, Kim 1982 and Ganski & Wong 1987 (the COUNT bug in subquery
  unnesting). The post does not mention them.
- **When GROUP BY began treating NULLs as one group** is not established. Date (S18) records the
  opposite for 1983; PostgreSQL 18 and the literature describe today's rule (L40, L54). The post
  states the two endpoints and nothing between them.
- **PostgreSQL 19's NOT IN conversion is documented, not measured**: the lab runs 18.6.
- **The generator gives all 10 orders of a customer the same amount** (37 × 100,000 is a
  multiple of 100,000). It changes nothing in the post, but it is why query A's broken output
  shows equal paid and refunded columns at full scale.
