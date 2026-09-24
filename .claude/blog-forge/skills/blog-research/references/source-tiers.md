# Source tiers

How to rank a source, and where to look per subject.

---

## T1 — Primary authoritative

Usable for any claim.

- Peer-reviewed conference and journal papers (SIGCOMM, SOSP, OSDI, VLDB, SIGMOD, NeurIPS, ICML, POPL, PLDI, S&P, CCS)
- Standards: IETF RFCs, IEEE 802.x, ISO, POSIX, ECMA, W3C
- Established textbooks: CLRS, Sipser, Hennessy and Patterson, Tanenbaum, Kleppmann, the dragon book
- Formal specifications and reference models

Note on arXiv: a preprint is T1 in content and unreviewed in status. Check whether it was published at a venue. If not, label it a preprint in the post. DBLP is the fastest way to check — search the title or the author and its publication record shows whether the preprint reached a venue, under what final title, and in which year.

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

## Scholarly databases

Where the literature sweep runs. Each one is good at something the others are not, and each one has a characteristic way of handing you something that looks like a source and is not. The trap column is the part that matters.

| Database | Good for | The trap |
|---|---|---|
| Google Scholar | Breadth across every venue at once, citation counts, and the "Cited by" graph that makes forward chasing possible | No quality filter whatsoever. It indexes predatory journals, other people's seminar slide decks, and duplicate uploads next to SOSP papers. A high citation count is popularity, not correctness — check the venue before the count. |
| arXiv | The newest work, often a year before it reaches a venue, and free full text | Unreviewed and version-mutable: v1 and v3 can disagree on the headline number. Cite the version id (`arXiv:2006.11239v2`), and label it a preprint unless DBLP shows a venue. |
| Semantic Scholar | A structured citation graph, influential-citation ranking that separates real intellectual debt from citation padding, and a free API for walking references in both directions | Metadata is machine-extracted, so venues, years and author lists are sometimes wrong. Confirm the venue against DBLP or the publisher before the row goes in the ledger. |
| DBLP | The authoritative venue and publication record for computer science. The place to settle whether a preprint was ever actually published, and where | Bibliography only — no abstracts, no full text, no citation counts. Coverage outside CS is thin. |
| ACM Digital Library, IEEE Xplore | The venues of record, with the canonical DOI, the final page numbers, and the published version rather than the submitted one | Paywalled. The free abstract and metadata are enough to establish venue, year and DOI, and that is all they are enough for. Never cite a paper whose method section you have not read — look for the author's own copy first. |
| USENIX, PMLR, OpenReview, IACR ePrint, ECCC | Free full text for systems, ML, crypto and theory, with reviews attached where the venue is open | OpenReview carries rejected and withdrawn submissions alongside accepted ones. Read the decision before citing, and read the reviews — they often name the weakness the paper does not. |
| Papers with Code | Reproductions, leaderboards, and the link from a paper to a working implementation | Leaderboard numbers are self-reported and rarely re-run by anyone. Treat a leaderboard as evidence about a claim, not the claim, and cite the paper. |
| Industrial lab publication pages: Google Research, Google DeepMind, Meta AI (FAIR), Microsoft Research, NVIDIA Research, OpenAI, Anthropic, Allen AI | The system paper, the model card, the errata and the release notes for a proprietary system, where no third-party paper exists. Frequently the primary source for a system a post is describing | The lab's blog post about the paper is T4 marketing; the paper it links to is T1. Follow the link. Announcements round numbers up, quote the best configuration, and drop the ablation that did not work. |

Finding a source in one of these does not set its tier. A paper is T1 because it was reviewed at a real venue, not because Google Scholar returned it, and a slide deck stays T5 no matter which database surfaced it.

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
