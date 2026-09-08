# Source ledger — every-search-algorithm-is-the-same-algorithm

Tier L2. Target 8–15 sources. 13 recorded.
Sources marked **read** were fetched and read directly, not taken from a search snippet.

## Sources

| ID | Tier | Source | URL | Accessed |
|---|---|---|---|---|
| S1 | T1 | Dijkstra, "A Note on Two Problems in Connexion with Graphs", Numer. Math. 1, 269–271 (1959) — **read** | https://ir.cwi.nl/pub/9256/9256D.pdf | 2026-09-08 |
| S2 | T1 | Hart, Nilsson, Raphael, "A Formal Basis for the Heuristic Determination of Minimum Cost Paths", IEEE Trans. Syst. Sci. Cybern. 4(2):100–107 (1968) | https://www.semanticscholar.org/paper/221aa3be55a4ead8fc2aa83b12aac370bfba72f5 | 2026-09-08 |
| S3 | T1 | Hart, Nilsson, Raphael, "Correction to 'A Formal Basis…'", SIGART Newsletter 37:28–29 (1972) | https://dl.acm.org/doi/10.1145/1056777.1056779 | 2026-09-08 |
| S4 | T1 | Dechter, Pearl, "Generalized best-first search strategies and the optimality of A*", J. ACM 32(3):505–536 (1985) | https://dl.acm.org/doi/10.1145/3828.3830 | 2026-09-08 |
| S5 | T1 | Knuth, Morris, Pratt, "Fast Pattern Matching in Strings", SIAM J. Comput. 6(2):323–350 (June 1977) — **read** | https://www.cs.jhu.edu/~misha/ReadingSeminar/Papers/Knuth77.pdf | 2026-09-08 |
| S6 | T1 | Boyer, Moore, "A Fast String Searching Algorithm", CACM 20(10):762–772 (1977) | https://www.cs.utexas.edu/~moore/publications/fstrpos.pdf | 2026-09-08 |
| S7 | T1 | Cole, "Tight Bounds on the Complexity of the Boyer–Moore String Matching Algorithm", SIAM J. Comput. 23(5):1075–1091 (1994) | https://epubs.siam.org/doi/10.1137/S0097539791195543 | 2026-09-08 |
| S8 | T3 | Bloch, "Extra, Extra — Read All About It: Nearly All Binary Searches and Mergesorts are Broken", Google Research blog (June 2006) — **read**; primary disclosure by the author of the JDK code | https://research.google/blog/extra-extra-read-all-about-it-nearly-all-binary-searches-and-mergesorts-are-broken/ | 2026-09-08 |
| S9 | T1 | Khuong, Morin, "Array Layouts for Comparison-Based Searching", ACM J. Exp. Algorithmics 22 (2017); arXiv:1509.05053v3, 14 March 2017 — **read** | https://arxiv.org/pdf/1509.05053 | 2026-09-08 |
| S10 | T1 | Malkov, Yashunin, "Efficient and Robust ANN Search Using Hierarchical Navigable Small World Graphs", IEEE TPAMI 42(4):824–836 (April 2020); arXiv:1603.09320, submitted 30 March 2016 | https://arxiv.org/abs/1603.09320 | 2026-09-08 |
| S11 | T1 | Fredman, Tarjan, "Fibonacci heaps and their uses in improved network optimization algorithms", J. ACM 34(3):596–615 (1987); FOCS 1984 | https://dl.acm.org/doi/10.1145/28869.28874 | 2026-09-08 |
| S12 | T1 | Aumüller, Bernhardsson, Faithfull, "ANN-Benchmarks: A benchmarking tool for approximate nearest neighbor algorithms", Information Systems 87 (2020); SISAP 2017 | https://arxiv.org/abs/1807.05614 | 2026-09-08 |
| S13 | T1 | Knuth, *The Art of Computer Programming, Vol. 3: Sorting and Searching*, 2nd ed. (1998), §6.2.1 | — | 2026-09-08 |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | Dijkstra's paper states two problems; Problem 2 is finding the minimum-length path between two given nodes P and Q, not all nodes | S1 p.270 | the paper's own framing; the all-destinations version is a later reading |
| L02 | The procedure stops once Q is transferred to the set of nodes with known minimum paths | S1 p.270 | single-pair formulation |
| L03 | The method rests on optimal substructure: if R lies on the minimal path P→Q, the minimal path P→R is known too | S1 p.270 | — |
| L04 | Nodes are held in three sets — known, frontier, unreached — and the next node is the frontier member at minimum distance | S1 p.270 | — |
| L05 | No priority queue, heap, or asymptotic analysis appears anywhere in the original paper | S1 pp.269–271 | verified by reading the full three pages |
| L06 | Dijkstra's stated justification is storage: only sets I and II are held, always fewer than n branches | S1 p.271 | his comparison is against Ford's and Berge's presentations |
| L07 | Paper received 11 June 1959, Numerische Mathematik 1, pages 269–271 | S1 | — |
| L08 | Fibonacci heaps give O(m + n log n) for single-source shortest paths with non-negative weights | S11 | non-negative edge weights; amortised bounds |
| L09 | A* was published in 1968 in IEEE Trans. Systems Science and Cybernetics 4(2):100–107 | S2 | — |
| L10 | If the heuristic never overestimates the true remaining cost (admissibility), A* returns a least-cost path | S2 | admissibility alone suffices for optimality of the *result* |
| L11 | The stronger 1968 claim — that A* expands no more nodes than any comparable algorithm — required the consistency assumption, and the authors issued a correction in 1972 | S3 | the correction is the reason the "optimally efficient" claim is usually stated with conditions |
| L12 | Dechter and Pearl later pinned down the precise class in which A* is optimal: with merely admissible estimates A* is not optimal, with consistent ones it is | S4 | J. ACM 32(3), 1985 |
| L13 | KMP: SIAM J. Comput. 6(2):323–350, June 1977; received 29 Aug 1974, revised 7 April 1976 | S5 p.323 | — |
| L14 | KMP finds all occurrences of a length-m pattern in a length-n text in O(m + n) time without backing up the text pointer | S5 p.323 | — |
| L15 | Naive matching of pattern a^n b against text a^2n b costs about (n+1)^2 character comparisons | S5 p.323 | the paper's own worst-case illustration |
| L16 | The skip works because the current position in the pattern already encodes the text characters just scanned | S5 p.324 | this is the paper's informal justification, our paraphrase |
| L17 | KMP's constants of proportionality do not depend on alphabet size | S5 p.323 | — |
| L18 | Boyer–Moore was published in CACM 20(10):762–772 (1977) and scans the pattern right to left | S6 | — |
| L19 | Boyer–Moore is sublinear in the sense that it generally inspects fewer characters than it passes over, and gets faster as the pattern gets longer | S6 | "generally" — this is average behaviour, not a worst-case bound |
| L20 | Boyer–Moore performs roughly 3n character comparisons in the worst case, and that bound is tight | S7 | Cole 1994; for the search phase, pattern not present or with the Galil modification |
| L21 | The unmodified Boyer–Moore is not linear when the pattern occurs many times; Galil's variant restores a linear worst case | S7, S6 | multiple-occurrence texts |
| L22 | Computing the midpoint as (low + high) / 2 overflows once the sum exceeds 2^31 − 1, producing a negative index | S8 | 32-bit signed int arithmetic |
| L23 | The same defect sat undetected in the JDK's java.util.Arrays.binarySearch for about nine years, and earlier in Bentley's *Programming Pearls* implementation | S8 | reported to Sun after it crashed a program |
| L24 | The fix is low + ((high − low) / 2), or the unsigned shift (low + high) >>> 1 | S8 | — |
| L25 | Any comparison-based search of a sorted array of n items needs at least about log2(n) comparisons in the worst case | S13 §6.2.1 | comparison model only; decision-tree argument |
| L26 | For large n the Eytzinger (breadth-first) layout is usually the fastest of the layouts tested, beating sorted order with binary search | S9 abstract | many queries against one in-RAM array; "after extensive testing on a wide variety of modern hardware" |
| L27 | For small n, plain sorted order with a good binary search implementation still wins | S9 abstract | same setup |
| L28 | This result contradicted earlier experimental work by Brodal, Fagerberg and Jacob (SODA 2003), which found B-tree and van Emde Boas layouts faster at large n | S9 abstract | a live disagreement between two experimental papers, not a settled result |
| L29 | The fast implementations use conditional moves to avoid branch mispredictions and explicit prefetching to hide cache latency | S9 abstract | C++ implementations, specific compilers |
| L30 | HNSW builds a multi-layer proximity graph; the top layer at which an element appears is drawn from an exponentially decaying distribution | S10 | — |
| L31 | HNSW's "logarithmic complexity scaling" is presented as a design and empirical property, not as a proven worst-case bound | S10 abstract | the abstract's wording is "allows a logarithmic complexity scaling" |
| L32 | HNSW: arXiv preprint submitted 30 March 2016; published in IEEE TPAMI 42(4):824–836, April 2020 | S10 | — |
| L33 | Approximate nearest-neighbour methods are compared on a recall-versus-throughput curve, not a single speed number | S12 | in-memory ANN algorithms, standard datasets |

## Open questions

- The specific cycle cost of a branch misprediction is widely quoted at 10–20 cycles, but Khuong and Morin's abstract does not state a number and I did not verify one in a vendor manual. The post avoids quoting a cycle count.
- Whether HNSW's logarithmic scaling holds under adversarial or very high intrinsic-dimension data is not settled by S10. The post states the claim as the authors state it and labels it as such (L31).
- Moore's own retrospective (cs.utexas.edu) dates the invention to "about 1975", but this is recollection rather than a dated record. The post uses only the 1977 publication date (L18).
