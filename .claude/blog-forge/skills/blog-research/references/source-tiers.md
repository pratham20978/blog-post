# Source tiers

How to rank a source, and where to look per subject.

---

## T1 — Primary authoritative

Usable for any claim.

- Peer-reviewed conference and journal papers (SIGCOMM, SOSP, OSDI, VLDB, SIGMOD, NeurIPS, ICML, POPL, PLDI, S&P, CCS)
- Standards: IETF RFCs, IEEE 802.x, ISO, POSIX, ECMA, W3C
- Established textbooks: CLRS, Sipser, Hennessy and Patterson, Tanenbaum, Kleppmann, the dragon book
- Formal specifications and reference models

Note on arXiv: a preprint is T1 in content and unreviewed in status. Check whether it was published at a venue. If not, label it a preprint in the post.

## T2 — Official documentation

Usable for any claim **about that system**.

- Language specifications
- Vendor architecture manuals: Intel SDM, ARM ARM
- Project documentation: Postgres, Linux kernel docs, LLVM, Kubernetes
- Man pages
- MDN for web platform behaviour
- Security catalogues: NIST publications, OWASP, CVE, CWE

T2 tells you what a system does. It does not tell you what is generally true. Postgres docs are authoritative about Postgres and say nothing about MySQL.

## T3 — Primary implementation evidence

Usable for behaviour claims.

- Source code in the official repository
- Release notes and changelogs
- Issue trackers and mailing list threads where maintainers respond
- Reproducible benchmark harnesses

Cite with a permalink to a commit or tag, never to a moving branch.

## T4 — Practitioner writing

Framing and intuition only. Never a source for a fact.

- Distill, Lil'Log, Chris Olah, Julia Evans, Eugene Yan, betterexplained
- Engineering blogs from companies with real systems
- Conference talks

Use these to see how a hard idea has been made clear. When one of them states a fact you want, follow their citation to the primary source and cite that instead. If they have no citation, the fact does not go in the post.

## T5 — Not citable

- SEO content farms, aggregator blogs, tutorial mills
- Forum and Q&A answers, unless a maintainer is answering about their own project, which makes it T3
- AI-generated explanation pages
- Slide decks with no source
- Wikipedia — useful for orientation and for finding primary sources, never cited itself

---

## Where to look, by subject

| Subject | Start here |
|---|---|
| Networking | RFC Editor, IETF datatracker, SIGCOMM proceedings |
| Operating systems | POSIX, kernel.org documentation, man7.org, SOSP and OSDI |
| Databases | VLDB and SIGMOD, Postgres and SQLite docs, the original system papers |
| Distributed systems | Lamport's papers, Raft and Paxos originals, Dynamo, Spanner, DDIA |
| Algorithms and data structures | Original papers, CLRS, Sedgewick |
| Machine learning | arXiv plus venue check, official implementation repos, Papers with Code for reproductions |
| Computer architecture | Intel SDM, ARM ARM, Hennessy and Patterson, ISCA and MICRO |
| Compilers | LLVM and GCC docs and source, language specs, PLDI and POPL |
| Security | NIST, OWASP, CVE and CWE, original disclosure writeups, IEEE S&P and USENIX Security |
| Theory | Original papers, Sipser, Arora and Barak, ECCC |

---

## Verifying a source

Before recording a row, check:

1. **Is it primary?** Does this source establish the fact, or repeat it from somewhere else? Follow the chain to its origin.
2. **Is it current?** Standards get obsoleted. RFCs get updated. Library behaviour changes across versions. Record the version or RFC status.
3. **Does it actually say this?** Read the relevant section, not the abstract. Abstracts overstate; the limitations section is usually where the truth is.
4. **What is the scope?** A result under one workload, model, or hardware is not general. Record the condition alongside the claim.
5. **Who paid for it?** Vendor benchmarks showing the vendor winning need a second source.

---

## Resolving conflicts

When two sources disagree:

1. Prefer the higher tier.
2. Within a tier, prefer the more recent, unless the older one is the defining document.
3. Prefer the source closer to the system in question.
4. If the disagreement is real and unresolved, put both in the post. Two cited positions is stronger writing than one confident wrong one.
