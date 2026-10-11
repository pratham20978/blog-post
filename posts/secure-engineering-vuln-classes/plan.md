# Series plan — Secure Engineering: Vulnerability Classes & Defenses

**Slug:** secure-engineering-vuln-classes · **Shape:** hybrid · **Parts:** 18 (16 committed, 2 optional) ·
**Category:** `security` · **Status:** Checkpoint S — awaiting approval (planned 2026-10-11)
**Display title:** *Secure Engineering: Vulnerability Classes & Their Defenses*

## Why this is a series and not one post

**SEC-3** owns the common software weakness *classes* and, above all, their *defenses*: how each
class arises in code, how it is detected, and the concrete fix. It is the developer-facing security
track — a defender who understands the mechanism writes safer code and better detections. The seams
are hard (no output encoding before the injection mindset; no SDLC before the classes it automates),
the budget is ~120,000 words, each part a distinct search intent, each catalogued by OWASP/CWE.

## Framing (firm)

**Strictly educational and defense-first.** Each part explains how a weakness *class* arises, **how it
is detected, and the exact fix and control** — and ends at the fix. Demonstrations use a **tiny,
intentionally-flawed app the author writes and then repairs**, run only in an isolated local
environment; there is **no step-by-step attack procedure and no weaponised payload**. The classes are
the public OWASP Top 10 / ASVS and CWE taxonomy. Per the model policy, the per-part scoping is
finalised at build time on Opus 4.8 if 5.5 is flagged; this plan stays at the class-and-defense level.

## The angle

Appsec content splits into checklists and exploit tutorials; neither helps an engineer ship safe
code. Unowned: the **mechanism in code** and the **fix with a test that proves it** — show how the
weakness appears in a small code sample, how a scanner flags it, and the concrete remediation plus a
**regression test** that stays green. Each part corrects a reflex: "sanitize inputs" (context decides —
parameterise or output-encode, don't blocklist), "a WAF fixes it" (defence in depth, not a fix),
"we'll add security later" (design-time is cheapest), "it's internal, so it's safe" (assume breach).

## Shape and dependencies

Hybrid: a mindset root (1) feeding class spokes (2–12), then a synthesis and SDLC arc. Each part ≤1
lower parent. Deps: 2←1, 3←1, 4←1, 5←1, 6←1, 7←1, 8←1, 9←1, 10←1, 11←1, 12←1, 13←2, 14←1, 15←14,
16←15, 17←13, 18←13.

## Arcs

| Parts | Arc | Purpose |
|---|---|---|
| 1 | Mindset | Trust boundaries and how weaknesses arise. |
| 2–8 | Web/app classes | Injection, XSS, auth/session, access control, CSRF, SSRF, deserialization — each with its fix. |
| 9–12 | Systemic classes | Memory-safety classes and mitigations; crypto misuse; misconfiguration; supply chain. |
| 13–14 | Synthesis | The OWASP Top 10 mapped to defenses; secure design. |
| 15–16 | Build it in | The secure-development lifecycle (SAST/DAST/SCA); a vulnerable app, fixed. |
| 17–18 | Optional | API security; responsible disclosure and the vulnerability lifecycle. |

## Reader objectives

| # | After this the reader can ... | Part |
|---|---|---|
| 1 | reason about trust boundaries and how weaknesses arise | 1 |
| 2 | prevent injection by separating code from data | 2 |
| 3 | prevent XSS with context-aware encoding and CSP | 3 |
| 4 | build authentication/session handling that resists common flaws | 4 |
| 5 | enforce access control and avoid IDOR | 5 |
| 6 | defend against CSRF using the same-origin model | 6 |
| 7 | defend against SSRF | 7 |
| 8 | avoid insecure deserialization | 8 |
| 9 | reason about memory-safety classes and their mitigations | 9 |
| 10 | avoid secrets-in-code and cryptographic misuse | 10 |
| 11 | prevent security misconfiguration | 11 |
| 12 | manage dependency and supply-chain risk | 12 |
| 13 | apply the OWASP Top 10 as defenses | 13 |
| 14 | threat-model and design securely as a developer | 14 |
| 15 | automate security in the SDLC (SAST/DAST/SCA) | 15 |
| 16 | take a vulnerable app and make it safe, with tests | 16 |

## Parts

### Part 1 — How Vulnerabilities Happen: Trust Boundaries and the Weakness Mindset
- **Slug:** trust-boundaries-weakness-mindset · L3 · intermediate · ~6,000 · 9 figs
- **Answers:** what do most vulnerabilities have in common, and how do you learn to see them?
- **Assumes:** none. **Hands off:** each class to its part.
- **Worked example:** the recurring pattern — untrusted data crossing a trust boundary into a powerful context; CWE as a taxonomy; the defender's questions (where does input come from, what does it reach); why defense-in-depth and secure defaults; mapping to the OWASP Top 10.
- **Lab:** G1 · E1–E3 · none.
- **Search intent:** "how vulnerabilities happen", "trust boundary", "secure coding mindset"

### Part 2 — Input Validation and Injection, as a Class
- **Slug:** injection-class-defenses · L4 · advanced · ~7,000 · 11 figs
- **Answers:** why does untrusted input reaching an interpreter cause injection, and what is the universal fix?
- **Assumes:** Part 1. **Hands off:** the HTML-context case (XSS) to 3.
- **Worked example:** the class — data interpreted as code (SQL, OS command, LDAP) — shown in a small flawed code sample; the universal fix (separate code from data: parameterised queries, safe APIs), not blocklisting; input validation as defense-in-depth; a regression test proving the fix. No attack steps.
- **Lab:** G2 · E1–E5 · local flawed-then-fixed app (container AR); defensive only.
- **Search intent:** "sql injection prevention", "parameterized queries", "command injection defense"

### Part 3 — Cross-Site Scripting and Output Encoding
- **Slug:** xss-output-encoding · L4 · advanced · ~7,000 · 11 figs
- **Answers:** why does untrusted data in a page execute, and how do you stop it by output context?
- **Assumes:** Part 1. **Hands off:** CSRF to 6.
- **Worked example:** stored/reflected/DOM XSS as one class (data in an HTML/JS/attribute context); the fix — context-aware output encoding, a templating auto-escape, and Content-Security-Policy as defense-in-depth — shown on a flawed-then-fixed app with a test. No payloads beyond an inert marker.
- **Lab:** G2 · E1–E5 · local flawed-then-fixed app (container AR); defensive only.
- **Search intent:** "xss prevention", "output encoding", "content security policy"

### Part 4 — Authentication and Session Weaknesses
- **Slug:** auth-session-weaknesses · L4 · advanced · ~7,000 · 11 figs
- **Answers:** how do authentication and session handling go wrong, and how do you build them correctly?
- **Assumes:** Part 1 (links SEC-2 authentication). **Hands off:** access control to 5.
- **Worked example:** weak credential storage (→ SEC-1 password hashing), session fixation/weak tokens, missing rate limiting, insecure password reset — each as a class with the fix (secure session management, strong hashing, MFA, lockout); a flawed-then-fixed login with tests.
- **Lab:** G2 · E1–E5 · local flawed-then-fixed app (container AR); defensive only.
- **Search intent:** "authentication vulnerabilities", "session management security", "session fixation defense"

### Part 5 — Access Control Flaws and IDOR
- **Slug:** access-control-idor · L4 · advanced · ~7,000 · 11 figs
- **Answers:** why is broken access control the most common serious flaw, and how do you get it right?
- **Assumes:** Part 1 (links SEC-2 authorization). **Hands off:** nothing.
- **Worked example:** missing function-level checks, insecure direct object references, privilege escalation paths — as a class; the fix (deny by default, check on every request at the server, ownership checks, centralised authorization); a flawed-then-fixed API with tests.
- **Lab:** G2 · E1–E5 · local flawed-then-fixed app (container AR); defensive only.
- **Search intent:** "broken access control", "idor prevention", "authorization checks"

### Part 6 — CSRF and the Same-Origin Model
- **Slug:** csrf-same-origin · L3 · intermediate · ~6,000 · 9 figs
- **Answers:** how can a page make requests as you, and how do the browser's defenses stop it?
- **Assumes:** Part 1. **Hands off:** SSRF to 7.
- **Worked example:** the ambient-credential problem; the same-origin policy and CORS; the fixes — SameSite cookies, anti-CSRF tokens, re-authentication for sensitive actions — on a flawed-then-fixed app with tests.
- **Lab:** G2 · E1–E4 · local flawed-then-fixed app (container AR); defensive only.
- **Search intent:** "csrf prevention", "samesite cookies", "same origin policy cors"

### Part 7 — Server-Side Request Forgery
- **Slug:** ssrf-defenses · L3 · intermediate · ~6,000 · 9 figs
- **Answers:** why is "fetch this URL" dangerous, and how do you make it safe?
- **Assumes:** Part 1 (links networking). **Hands off:** nothing.
- **Worked example:** the SSRF class (server fetches an attacker-influenced URL, reaching internal services/metadata); the fixes — allow-listing, blocking internal ranges, disabling redirects, network egress controls — on a flawed-then-fixed fetcher with tests.
- **Lab:** G2 · E1–E4 · local flawed-then-fixed app in netns (container AR); defensive only.
- **Search intent:** "ssrf prevention", "server side request forgery", "ssrf defense"

### Part 8 — Insecure Deserialization and Object Injection
- **Slug:** deserialization-defenses · L3 · advanced · ~6,000 · 9 figs
- **Answers:** why is deserialising untrusted data dangerous, and what is the safe pattern?
- **Assumes:** Part 1. **Hands off:** nothing.
- **Worked example:** the class (untrusted serialized data instantiating objects / invoking code paths); the fixes — avoid native deserialization of untrusted input, use data-only formats with schemas, integrity-check, allow-list types — on a flawed-then-fixed sample with tests.
- **Lab:** G2 · E1–E4 · local flawed-then-fixed app (container AR); defensive only.
- **Search intent:** "insecure deserialization", "object injection defense", "safe deserialization"

### Part 9 — Memory-Safety Classes and Their Mitigations
- **Slug:** memory-safety-mitigations · L4 · advanced · ~7,000 · 11 figs
- **Answers:** what are the memory-safety weakness classes, and what actually mitigates them?
- **Assumes:** Part 1 (links computer-architecture/OS). **Hands off:** nothing.
- **Worked example:** the classes conceptually — buffer overflow, use-after-free, integer overflow — as *why they arise* (no exploit development); the layered mitigations (bounds checking, ASLR, DEP/NX, stack canaries, CFI) explained, and the strongest fix: memory-safe languages and safe APIs; a before/after in a small sample showing the bug and its safe rewrite.
- **Lab:** G1 · E1–E4 · none (safe-rewrite demonstration; no exploitation).
- **Search intent:** "memory safety", "buffer overflow mitigation", "use after free", "aslr dep"

### Part 10 — Secrets in Code and Cryptographic Misuse
- **Slug:** secrets-crypto-misuse · L3 · intermediate · ~6,000 · 9 figs
- **Answers:** how do secrets leak into code, and how is cryptography commonly misused — and fixed?
- **Assumes:** Part 1 (links SEC-1, SEC-2 secrets management). **Hands off:** key management to SEC-1.
- **Worked example:** hardcoded secrets and history leaks (detection with a scanner, remediation, rotation); crypto misuse patterns (weak hash for passwords, ECB, hardcoded IV/nonce reuse, home-rolled crypto) each named with the correct SEC-1 primitive as the fix, on a flawed-then-fixed sample.
- **Lab:** G1 · E1–E4 · none.
- **Search intent:** "secrets in code", "cryptographic failures owasp", "hardcoded credentials"

### Part 11 — Security Misconfiguration and Hardening Defaults
- **Slug:** security-misconfiguration · L3 · intermediate · ~6,000 · 9 figs
- **Answers:** why is "it works" not "it's secure", and how do you ship safe defaults?
- **Assumes:** Part 1 (links SEC-2 hardening).
- **Worked example:** default credentials, verbose errors, open admin endpoints, missing security headers, permissive CORS — as a class; the fix (secure defaults, least functionality, hardening baselines, security headers) applied and tested on a small app.
- **Lab:** G2 · E1–E4 · local flawed-then-fixed app (container AR); defensive only.
- **Search intent:** "security misconfiguration", "security headers", "secure defaults"

### Part 12 — Dependency and Supply-Chain Risk
- **Slug:** dependency-supply-chain · L4 · advanced · ~7,000 · 11 figs
- **Answers:** how does risk enter through the code you didn't write, and how do you manage it?
- **Assumes:** Part 1 (links SEC-2 vuln management). **Hands off:** nothing.
- **Worked example:** vulnerable/compromised dependencies, typosquatting, build-pipeline risk; the defenses — SCA scanning, pinning and lockfiles, an SBOM, artifact signing/verification (SLSA), least-privilege CI — applied to a small project with a test; the known supply-chain incident *classes* named defensively.
- **Lab:** G2 · E1–E4 · local project with SCA (container AR).
- **Search intent:** "software supply chain security", "sca sbom", "dependency vulnerability"

### Part 13 — The OWASP Top 10, Mapped to Defenses
- **Slug:** owasp-top-10-defenses · L3 · intermediate · ~6,500 · 10 figs
- **Answers:** how do the ten most common risk categories relate, and what is the defense for each?
- **Assumes:** Part 2 (and links across). **Hands off:** SDLC to 15.
- **Worked example:** the current OWASP Top 10 walked as *defenses* (each category → the control that addresses it → where it was covered in Parts 2–12); the overlaps; a checklist derived from mechanism, not cargo cult.
- **Lab:** G1 · E1–E3 · none.
- **Search intent:** "owasp top 10", "owasp top 10 defenses", "web application security"

### Part 14 — Secure Design and Threat Modelling for Developers
- **Slug:** secure-design-threat-modeling · L3 · intermediate · ~6,000 · 9 figs
- **Answers:** how do you prevent whole classes of bug at design time, before any code?
- **Assumes:** Part 1 (links SEC-2 threat modelling). **Hands off:** automation to 15.
- **Worked example:** developer threat modelling on a feature; secure-design patterns (fail closed, complete mediation, least privilege, defense in depth); abuse cases; designing out a class rather than patching instances.
- **Lab:** G1 · E1–E3 · none.
- **Search intent:** "secure design principles", "threat modeling for developers", "secure by design"

### Part 15 — The Secure Development Lifecycle: SAST, DAST and Shift-Left
- **Slug:** secure-development-lifecycle · L4 · advanced · ~7,000 · 11 figs
- **Answers:** how do you catch these classes automatically, continuously, in the pipeline?
- **Assumes:** Part 14 (links NIST SSDF). **Hands off:** the build to 16.
- **Worked example:** SAST, DAST, SCA and secret scanning placed in CI; their false-positive/coverage trade; the NIST SSDF; gating vs informational; building a security pipeline on a small repo and measuring what it catches (and misses).
- **Lab:** G2 · E1–E5 · local CI with the scanners (container AR).
- **Search intent:** "sast vs dast", "shift left security", "secure sdlc"

### Part 16 — Building Security In: A Vulnerable App, Fixed
- **Slug:** secure-app-end-to-end · L4 · advanced · ~7,500 · 12 figs
- **Answers:** how do the classes and defenses combine to turn a flawed app into a safe one?
- **Assumes:** Part 15 (and links across). **Hands off:** nothing; capstone.
- **Worked example:** a deliberately-vulnerable small app (the author's own) carried through the series' defenses one class at a time — each weakness identified, fixed, and locked down with a regression test and a pipeline check — ending with a hardened app and a passing security CI. Defensive throughout.
- **Lab:** G2 · E1–E5 · local flawed-then-fixed app + CI (container AR); defensive only.
- **Search intent:** "secure coding example", "fix vulnerable app", "application security hardening"

### Part 17 (optional) — API Security
- **Slug:** api-security · L3 · advanced · ~6,000 · 9 figs
- **Answers:** how do the classes shift for APIs, and what defends them?
- **Assumes:** Part 13 (links SD-1 API design). **Hands off:** nothing.
- **Worked example:** the OWASP API Top 10 themes (object/function-level authz, mass assignment, rate limiting); the defenses on a small API with tests; schema validation and least exposure.
- **Lab:** G2 · E1–E4 · local flawed-then-fixed API (container AR); defensive only.
- **Search intent:** "api security", "owasp api top 10", "secure rest api"

### Part 18 (optional) — Responsible Disclosure and the Vulnerability Lifecycle
- **Slug:** responsible-disclosure · L3 · intermediate · ~5,500 · 8 figs
- **Answers:** how does a vulnerability move from discovery to a fixed, disclosed CVE — responsibly?
- **Assumes:** Part 13.
- **Worked example:** the coordinated-disclosure process; CVE/CVSS/CWE; a security.txt and a disclosure policy; bug-bounty basics; how maintainers should receive and triage reports — the ethical, constructive side.
- **Lab:** G1 · E1–E3 · none.
- **Search intent:** "responsible disclosure", "coordinated vulnerability disclosure", "how cve works"

## Publication order and cadence

Strict prerequisite order; the synthesis (13) and SDLC (15–16) follow the classes. One part per week.

## Cross-links

Assumes nothing but Part 1; references SEC-1 (crypto primitives for the correct fixes), SEC-2
(operational controls, threat modelling, vuln management), SD-1 (API design), and AG-2 (agent-specific
weaknesses). Links from the later part only.

## Lab policy

**G2/G3 — isolated Docker**, sharing the container-capability access request. The signature is a
**tiny, intentionally-flawed app the author writes and then fixes**, run only locally; each part
shows the class, how a scanner detects it, and the fix with a **regression test that stays green**.
**No step-by-step attack procedure and no weaponised payload ships** — every part ends at the defense.
A few parts (memory-safety concepts, crypto misuse, OWASP synthesis, secure design, disclosure) are
G1. If the capability is declined, labs ship as flawed-then-fixed code samples plus test output from
one granted run. `access.md` created at build time; per the model policy, finalise the per-part detail
on Opus 4.8 if 5.5 is flagged.

## Key sources (confirm per part at research)

OWASP (Top 10, ASVS, the Cheat Sheet Series, API Top 10); CWE and the CWE Top 25; NIST SSDF
(SP 800-218); the SLSA framework; the language/framework security guides; SEC-1 and SEC-2 for the
primitives and operational controls.

## What this series will not cover

- **Cryptographic primitives** — SEC-1. **Operational defence (firewalls, IDS, IR, SIEM)** — SEC-2.
- **Agent-specific weaknesses** — AG-2.
- **Exploit development, penetration-testing procedures, or any operation against a real system** —
  out of scope entirely; everything is flawed-then-fixed code, run locally, ending at the defense.
- **Reverse engineering and malware analysis.**

## Open decisions for the owner

1. 18 parts (16 + 2 optional) or 16-part core.
2. Confirm the defense-first, flawed-then-fixed, local-only framing (it mirrors the category).
3. Shares the container capability request with networking and SEC-2/AG-2.
4. Title.
