# Series context — Applied Cryptography

> Private build memory. Read before starting a member post; update only after a member passes its gate. Keep under 2,000 words.

## Series invariants

- **Audience:** working engineers and security practitioners who must *use* cryptography correctly
  and know why it holds — not cryptographers proving new schemes. Expert standard; every part opens
  with a worked instance before any formalism, so a reader can enter at any primitive.
- **Shape:** hybrid — six arcs (Foundations, Symmetric, Integrity/keys, Public-key, Trust/protocols,
  Frontier/practice) plus two optional spokes; see `plan.md`.
- **Shared promise:** the reader can choose, use and reason about the primitive for a given job, and
  name the exact misuse that breaks it.
- **Terminology and notation (decisions to keep):** say "nonce" for number-used-once and "IV" only
  where the standard does; write bit/byte lengths explicitly; GF(2⁸) for AES, GF(2¹²⁸) for GHASH;
  "key" vs "secret" per Kerckhoffs; distinguish preimage / second-preimage / collision resistance
  precisely; "AEAD" not "authenticated mode"; sizes in bits for keys, bytes for blocks/tags.
- **Recurring example or lab:** the **standard's own test vector** for each primitive (FIPS-197 AES
  block, SHA-256("abc"), RFC 8439 ChaCha20-Poly1305, the RSA toy key p=61/q=53/n=3233/e=17/d=2753,
  the toy curve y²=x³+2x+2 over F₁₇ order 19, RFC 8448 TLS trace). Every by-hand implementation is
  verified against its vector. **Lab grade G1 for the whole series** — see `access.md` (no requests).

## The security-category boundary (keep this)

- **This series (SEC-1) is constructive and benign.** Primitives are built and verified, never
  attacked. "What breaks it" appears only as the **defensive condition** to avoid (nonce reuse, ECB,
  textbook RSA, repeated ECDSA nonce, non-constant-time compare), demonstrated on the author's **own
  local toy keys/data**, never a real or remote system, and always ending at the fix.
- **Operational attack and defence belong to the siblings:** SEC-2 Defensive/Blue-Team (firewalls,
  detection, IR), SEC-3 Secure Engineering (vuln classes + fixes). This series hands them the
  primitives and references them where a misuse is their ground (e.g. token/signature misuse → SEC-3).
- **Model/framing:** work on `security` stays on Opus 5.5; switch to 4.8 only if 5.5 is flagged. For
  this series that is unlikely — it is constructive cryptography, not attack content — but the rule
  stands for the category.

## Part status

| # | Slug | Status | Owns | Actual handoff |
|---|---|---|---|---|
| 1–18 | see `plan.md` | planned | one primitive/question each | — |

## Knowledge established

None yet. After each completed part, add its heading and no more than eight durable bullets (the
worked numbers it fixed, the vector it verified against, the misuse condition it stated, the term it
introduced), so the next part reuses them instead of re-deriving.

## Decisions to preserve

- Every primitive ships a pure-Python by-hand implementation **and** the production-library call,
  with the by-hand version verified against the standard's test vector; a figure that disagrees with
  the vector fails the build.
- "Don't roll your own crypto" is honoured: the series builds primitives to *understand* them and
  says plainly to ship the vetted library; Part 16 closes on this.
- Numbers presented as measured (AES throughput, Argon2 cost, the Part 17 timing histogram) come from
  a shipped run with a provenance line; nothing is invented.
- Versions (OpenSSL 3.5.5, `cryptography` ≈50.x, `argon2-cffi`, PQC names) are pinned per part at
  research time against the dated FIPS/RFC, not from the plan.

## Open threads

- Checkpoint S not passed: the 18-part cut (vs the 16-part core) and the title await the owner.
- `security` category row does not exist in the live DB; needed only at publish time (production write).
- Confirm at research: OpenSSL 3.5's exact ML-KEM/ML-DSA surface for Part 15, and whether
  `cryptography` exposes PQC at the pinned version or liboqs bindings are needed.

## Next part brief

- **Part:** 1 — What Cryptography Actually Guarantees (`what-cryptography-guarantees`); build after Checkpoint S.
- **Can assume:** no prior part; basic modular arithmetic and XOR.
- **Must teach:** the goals (confidentiality/integrity/authenticity), the threat/adversary model and
  what "secure" means operationally (IND-CPA/CCA as intuition), Kerckhoffs's principle.
- **Must not repeat:** nothing yet; this is the root. Keep the primitive specifics (AES, RSA, etc.)
  for their own parts — Part 1 only frames the goals and the one-time pad.
- **Evidence still needed:** everything — no research has run. Candidate sources: Katz & Lindell
  ch. 1–3, Boneh & Shoup ch. 2–3, Shannon 1949.
- **Handoff:** randomness to Part 2; the symmetric construction to 3–5; integrity to 6–8; public-key to 9–12.
