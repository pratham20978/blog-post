# Subject playbooks

Read the entry for the post's subject at brief time. Each names the sources that count, the figures that carry the topic, and the mistakes that show up in bad writing about it.

Contents: algorithms · data structures · networking · operating systems · databases · distributed systems · machine learning · computer architecture · compilers · security · theory

---

## Algorithms

**Sources.** Original papers first. CLRS and Sedgewick for standard material. Complexity claims must match the paper, not folklore.

**Figures.** A trace of the algorithm on a tiny input, step by step. A recursion tree. A growth-rate chart from real measurements, not from plotting the asymptotic form.

**Mistakes to avoid.** Writing $O$ when the bound is tight. Omitting the case, so a worst-case bound reads as typical. Ignoring constants when they decide practice: a $O(n \log n)$ algorithm with a bad constant loses to $O(n^2)$ on real input sizes, and that is usually the interesting part of the story.

**Best worked example.** An input of 8 to 16 elements, traced fully.

---

## Data structures

**Sources.** Papers for anything past the textbook set. Standard library implementation source for real behaviour.

**Figures.** Memory layout. Before and after a mutation. A pointer diagram for linked structures.

**Mistakes to avoid.** Describing the abstract structure while claiming concrete performance. Cache behaviour usually decides real speed, and it does not appear in the asymptotic analysis. Say which one you are talking about.

---

## Networking

**Sources.** RFCs are primary and authoritative; cite by number and section. IETF drafts for in-progress work. Vendor documentation for implementation-specific behaviour only.

**Figures.** Sequence diagrams for handshakes and message exchange. A packet or header layout. A state machine for connection state. A timeline for anything where timing is the point.

**Mistakes to avoid.** Describing the standard rather than what implementations do. Ignoring the layer boundary, so a claim about TCP is really a claim about the NIC. Treating an RFC as describing current deployment; a lot of the RFC set is not what runs.

**Best worked example.** One connection, traced packet by packet with real sequence numbers.

---

## Operating systems

**Sources.** POSIX for interface behaviour. Kernel documentation and source for real behaviour. Man pages for the contract.

**Figures.** State machine for process or thread lifecycle. Address space layout. A sequence diagram across the syscall boundary.

**Mistakes to avoid.** Generalising Linux behaviour to "operating systems". Confusing the specified behaviour with the observed behaviour. Describing scheduling without naming the scheduler and version.

---

## Databases

**Sources.** Papers for the mechanisms. Postgres and SQLite documentation are unusually good and are primary sources for their own behaviour. Query planner output for claims about plans.

**Figures.** B-tree structure and a split. A query plan as a tree. An ER diagram for the schema being discussed. A timeline for concurrency and isolation.

**Mistakes to avoid.** Claiming a plan without showing `EXPLAIN`. Stating isolation-level behaviour without naming the engine, since the same level name means different things across engines. Benchmark numbers without hardware, dataset size, and configuration.

**Best worked example.** A real table, a real query, real `EXPLAIN` output.

---

## Distributed systems

**Sources.** Papers, and the original ones: Lamport, Paxos, Raft, Dynamo, Spanner. Formal specs where they exist.

**Figures.** Sequence diagram with several nodes and a failure. A timeline showing message reordering. A state machine per node.

**Mistakes to avoid.** Using CAP loosely; state the precise claim or leave it out. Describing consensus without naming the failure model. Skipping the partition case, which is the only interesting case.

---

## Machine learning

**Sources.** arXiv, but check whether the paper was ever peer reviewed and say so. Official implementation repositories. Benchmark numbers only from the paper or a reproduction, never from memory.

**Figures.** Architecture diagram. Loss or metric curves from real runs. Tensor shape flow through the network. A worked forward pass on tiny numbers.

**Mistakes to avoid.** Reporting benchmark numbers without the setup. Presenting a result as settled when it has one paper behind it. Explaining architectures without shapes, which is where most confusion actually lives.

**Best worked example.** A forward and backward pass on a 2-by-2 example, done by hand.

---

## Computer architecture

**Sources.** Vendor architecture manuals: Intel SDM, ARM ARM. Hennessy and Patterson for the fundamentals. Real measurements for anything about performance.

**Figures.** Pipeline diagram with stages and stalls. Cache hierarchy with sizes and latencies. Memory layout.

**Mistakes to avoid.** Quoting cycle counts without the microarchitecture. Treating a textbook five-stage pipeline as how modern CPUs work. Ignoring the memory hierarchy, which dominates.

---

## Compilers

**Sources.** LLVM and GCC documentation and source. The dragon book for fundamentals. Language specifications for semantics.

**Figures.** AST for a small expression. IR before and after a pass. A pipeline of compilation stages.

**Mistakes to avoid.** Claiming an optimisation happens without showing the generated code. Confusing undefined behaviour with unspecified behaviour. Describing a pass in isolation when its effect depends on pass ordering.

---

## Security

**Sources.** NIST publications, OWASP, CVE and CWE entries, original disclosure writeups. Vendor advisories for specific products.

**Figures.** Trust boundaries. Attack sequence as a sequence diagram. A control matrix.

**Mistakes to avoid.** Explaining an attack without the mitigation. Vague severity language when CVSS scores exist. Writing anything that reads as an operational how-to rather than an explanation of the mechanism and its defence. Explain how a class of vulnerability works and how it is fixed; do not write working exploit code.

---

## Theory

**Sources.** Original papers. Standard textbooks: Sipser, Arora and Barak.

**Figures.** Reduction as a diagram. A machine or automaton state diagram. A complexity class containment diagram.

**Mistakes to avoid.** Stating containments as known when they are open. Loose use of "NP-hard". Proof sketches presented as proofs; say which one it is.
