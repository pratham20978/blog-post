# Series plan — Applied Cryptography

**Slug:** applied-cryptography · **Shape:** hybrid · **Parts:** 18 (16 committed, 2 optional) ·
**Category:** `security` for every part · **Status:** Checkpoint S — awaiting approval (planned 2026-10-11)
**Display title (platform):** *Applied Cryptography: From the Bytes Up*

## Why this is a series and not one post

The reader objective is to *use cryptography correctly and know why it holds* — and that splits at
hard prerequisite seams. You cannot explain authenticated encryption until the reader has a block
cipher and a mode; you cannot explain a MAC until there is a hash; you cannot explain a certificate
until there is a signature, and you cannot trace a TLS handshake until all of those exist. Budgeted
as one article the committed objectives come to roughly 120,000 words and well past 200 figures —
sixteen prerequisite-separated groups, each with its own worked example and its own search audience
("how does AES work", "what is HMAC", "RSA by hand", "TLS 1.3 handshake explained" are four
different readers). That is a series by every one of the skill's three tests.

This is **SEC-1**, the benign and foundational series of the `security` category (siblings: SEC-2
Defensive Security, SEC-3 Secure Engineering). It is entirely constructive — primitives built and
verified, never attacked. The one place attacker behaviour appears is as a *defensive condition*:
the exact input that breaks a primitive when it is misused (a reused GCM nonce, an ECDSA nonce
repeat, textbook RSA, a non-constant-time compare), always stated as "how to not get this wrong,"
never as a procedure against a real system.

## The angle, and why it is not another intro-to-crypto course

Introductory cryptography is saturated: Boneh's course, Katz & Lindell, Aumasson's *Serious
Cryptography*, *Crypto 101*, and the cryptopals set own the block diagram and the headline equation.
Restating them is worthless. Each part's literature sweep must confirm this for its own primitive,
but what those sources mostly do not do is the four things this series is built on:

1. **Reconcile on the real bytes.** Compute the thing on the standard's own test vector: one AES
   round on the FIPS-197 vector, the SHA-256 compression on `"abc"`, an RSA signature on real
   numbers, a TLS 1.3 key schedule from RFC 8448. The reader checks every intermediate.
2. **Derive the condition, not just the result.** Show *why* ECB leaks (equal blocks → equal
   ciphertext, on an actual image), *why* a nonce must not repeat (the keystream/authenticator
   algebra), *why* textbook RSA is malleable — on numbers the reader can redo.
3. **Measure what is measurable on a laptop.** Hash throughput, Argon2 parameter cost in real
   milliseconds, and a timing difference between a constant-time and a naive comparison, each
   labelled as this machine's number with its provenance line.
4. **Trace on the wire.** The TLS 1.3 handshake and a certificate chain shown as the actual
   records and fields, parsed, not redrawn as a cartoon.

Every part does all four, or says which one it omits and why. Each part also **corrects one claim**
that usually circulates without its condition — e.g. "SHA-256 is slow" (it is hardware-accelerated;
the slow thing you want for passwords is Argon2), "AES is unbreakable" (the cipher is not the attack
surface; mode, nonce and key management are), "RSA encrypts with the public key" (textbook RSA
without padding is broken; real RSA encrypts a key under OAEP).

## Shape

Neither a pure ladder (one subject at rising depth) nor a flat decomposition. It is a stack of
primitives that build on each other, so: six arcs, cut at prerequisite seams, with short ladders
inside the symmetric and public-key arcs and spokes elsewhere. Each part names at most one parent,
and every parent sits at a lower position, so publication order 1→18 never links backward to an
unpublished part. Dependencies: 2←1, 3←1, 4←3, 5←4, 6←1, 7←6, 8←7, 9←1, 10←9, 11←10, 12←11,
13←12, 14←13, 15←9, 16←5, 17←7, 18←11.

Why a series and not one post: see above. Adjacent options the owner can overrule in one word:
(a) a **12-part core** (1–14 minus 7/8/13 folded as sections) that defers MACs/KDFs/PKI into their
neighbours — rejected, because each is a distinct search intent and a distinct failure surface;
(b) split the public-key arc (9–12) into its own series — possible, but signatures and TLS need it
inline, so the seam is weaker than the symmetric/public-key boundary already drawn.

## Arcs

| Parts | Arc | Purpose |
|---|---|---|
| 1–2 | Foundations | What cryptography guarantees and against whom; and the randomness every primitive stands on. |
| 3–5 | Symmetric encryption | The block cipher, the modes that turn it into a usable cipher, and authenticated encryption — a ladder. |
| 6–8 | Integrity and keys | Hashing, message authentication, and turning passwords and shared secrets into keys. |
| 9–12 | Public-key cryptography | RSA, Diffie–Hellman, elliptic curves and the signatures built on them — a ladder. |
| 13–14 | Trust and protocols | Certificates and the chain of trust, then the TLS 1.3 handshake that uses the whole stack. |
| 15–16 | Frontier and practice | Post-quantum cryptography, and how keys are actually managed in a real system. |
| 17–18 | Optional | Side channels and constant-time code; and the double ratchet behind modern secure messaging. |

## Reading paths

- **From scratch:** 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8, then the public-key arc 9 → 10 → 11 → 12, then 13 → 14.
- **"I just need to encrypt data correctly":** 1 → 4 → 5 → 8 → 16.
- **"I need to understand TLS":** 1 → 5 → 6 → 10 → 11 → 12 → 13 → 14.
- **"Passwords and tokens":** 1 → 6 → 7 → 8 (and SEC-3 for where tokens go wrong).
- **Post-quantum migration:** 9 → 11 → 15.

## Reader objectives

| # | After this the reader can ... | Part |
|---|---|---|
| 1 | state the goals (confidentiality, integrity, authenticity) and the threat model, and say what "secure" means operationally | 1 |
| 2 | apply Kerckhoffs's principle and tell a key from a secret algorithm | 1 |
| 3 | tell a CSPRNG from a PRNG, and name what breaks when a seed or nonce is predictable or reused | 2 |
| 4 | trace one AES-128 round on the FIPS-197 vector and reconstruct the key schedule | 3 |
| 5 | say why ECB leaks structure and CTR does not, and why unauthenticated encryption is malleable | 4 |
| 6 | encrypt and decrypt with AES-GCM and ChaCha20-Poly1305, and state the nonce rule that must never break | 5 |
| 7 | compute a SHA-256 compression step, and name preimage, second-preimage and collision resistance correctly | 6 |
| 8 | build and verify an HMAC, and say why the verification must be constant-time | 7 |
| 9 | choose a password hash and its parameters, and derive subkeys with HKDF | 8 |
| 10 | run RSA keygen, encryption and decryption on real numbers, and say why textbook RSA is broken | 9 |
| 11 | agree a shared secret over a public channel, and explain forward secrecy and the MITM it does not stop | 10 |
| 12 | add points on a small elliptic curve by hand, and say why ECDH gives the same security with smaller keys | 11 |
| 13 | produce and verify RSA-PSS, ECDSA and Ed25519 signatures, and say why an ECDSA nonce must never repeat | 12 |
| 14 | parse an X.509 certificate, validate a chain to a trust anchor, and explain revocation and transparency | 13 |
| 15 | trace a TLS 1.3 handshake record by record and derive its traffic keys from the key schedule | 14 |
| 16 | say why Shor breaks RSA and ECC, and deploy ML-KEM and ML-DSA in a hybrid | 15 |
| 17 | design envelope encryption with a key hierarchy, and rotate a key without re-encrypting the world | 16 |
| 18 | (opt) measure a timing side channel and write a constant-time comparison | 17 |
| 19 | (opt) explain the double ratchet's forward secrecy and post-compromise security | 18 |

## Parts

### Part 1 — What Cryptography Actually Guarantees

- **Slug:** what-cryptography-guarantees · **Arc:** Foundations · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,000 · **Figures:** 9
- **Answers:** What does "secure" mean, precisely, and what is the adversary allowed to do?
- **Assumes:** No prior part. Basic modular arithmetic and XOR. No prior cryptography.
- **Hands off:** Randomness to 2; the symmetric construction to 3–5; integrity to 6–8; public-key to 9–12.
- **Worked example:** The one-time pad on a short message, by hand, as the only provably secret
  cipher — then why its key length makes it unusable, which is the whole reason the rest of the
  series exists. The same message reused under one pad key shows the two-time-pad break (XOR of
  ciphertexts = XOR of plaintexts), the first concrete "misuse breaks it." Confidentiality vs
  integrity vs authenticity are separated on one tampered message. Kerckhoffs's principle stated
  against "security by obscurity." The adversary ladder (ciphertext-only → known-plaintext →
  chosen-plaintext → chosen-ciphertext) and IND-CPA/IND-CCA given as "the game the scheme must win,"
  intuitively, not as a formal reduction.
- **Lab:** G1 · runs anywhere · ladder E1–E4 · access: none. Pure-Python XOR pad and the two-time-pad
  recovery; no library needed.
- **Key sources (confirm at research):** Katz & Lindell ch. 1–3; Boneh & Shoup ch. 2–3; Shannon 1949.
- **Search intent:** "what does cryptography guarantee", "confidentiality integrity authenticity",
  "kerckhoffs principle", "ind-cpa explained"

### Part 2 — Randomness You Can Bet On

- **Slug:** cryptographic-randomness-csprng · **Arc:** Foundations · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,000 · **Figures:** 9
- **Answers:** Where do cryptographic keys and nonces come from, and what makes a random number
  generator safe to use for them?
- **Assumes:** Part 1's threat model.
- **Hands off:** Nonce discipline to 5; signature nonces to 12; key generation to 9–11.
- **Worked example:** A linear congruential generator reproduced in a few lines, then its state
  recovered from a short output run — the reason `random()` is never a key source. Contrasted with a
  CSPRNG (ChaCha20-based `secrets`/`getrandom`): entropy sources, seeding, `/dev/urandom` vs
  `/dev/random`, fork safety, and reseeding. The birthday bound computed for a 96-bit nonce to show
  when random nonces start colliding. The worked break is predictability, not an attack on a system.
- **Lab:** G1 · runs anywhere · ladder E1–E4 · access: none. The LCG and its state recovery in stdlib;
  `secrets`/`os.urandom` for contrast; a birthday-collision simulation.
- **Key sources:** NIST SP 800-90A/B; `getrandom(2)`; Aumasson ch. 2.
- **Search intent:** "csprng vs prng", "is random() secure", "/dev/urandom vs /dev/random", "nonce collision birthday bound"

### Part 3 — Inside AES: A Block Cipher, Round by Round

- **Slug:** aes-block-cipher-internals · **Arc:** Symmetric encryption · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 8,500 · **Figures:** 14
- **Answers:** What does a block cipher actually compute, transformation by transformation?
- **Assumes:** Part 1. Finite-field arithmetic is introduced here, not assumed.
- **Hands off:** Turning one-block AES into a cipher for real data to 4; authenticated modes to 5;
  AES in key wrapping to 16.
- **Worked example:** One AES-128 encryption of the FIPS-197 Appendix-B block (input
  `3243f6a8…0370734`, key `2b7e1516…cf4f3c`), showing the state after SubBytes, ShiftRows, MixColumns
  and AddRoundKey in round 1, the full key schedule's first round words, and the final ciphertext
  `3925841d…196a0b32` matched to the standard. GF(2⁸) multiplication for MixColumns worked by hand;
  the S-box as inverse-plus-affine, not a magic table. Confusion and diffusion shown by flipping one
  input bit and counting changed output bits (the avalanche). AES-NI named as why this is fast in
  practice, with the throughput measured.
- **Lab:** G1 · runs anywhere · ladder E1–E5 · access: none. A pure-Python AES-128 block that prints
  every intermediate state, verified against the FIPS-197 vector; avalanche counter; a timing read of
  the library's AES-NI path.
- **Key sources:** FIPS-197 (Rijndael); Daemen & Rijmen, *The Design of Rijndael*.
- **Search intent:** "how does aes work", "aes round steps", "aes s-box explained", "aes mixcolumns gf(2^8)"

### Part 4 — Modes of Operation: Why ECB Leaks and CTR Doesn't

- **Slug:** block-cipher-modes-of-operation · **Arc:** Symmetric encryption · **Status:** planned
- **Tier:** L4 · **Difficulty:** intermediate · **Est. words:** 8,000 · **Figures:** 14
- **Answers:** A block cipher encrypts 16 bytes; how do you safely encrypt a megabyte, and why do
  some ways of doing it leak?
- **Assumes:** Part 3's one-block AES.
- **Hands off:** Adding authentication to 5 (this part's whole point is that confidentiality is not
  enough); disk/key-wrap modes to 16.
- **Worked example:** The same bitmap encrypted under ECB and under CTR — ECB keeps the visible
  outline (equal plaintext blocks → equal ciphertext blocks), CTR does not, the canonical image shown
  both ways. CBC with PKCS#7 padding worked byte by byte, including the padding-oracle *condition*
  (why an unauthenticated CBC decryptor that distinguishes bad padding from bad MAC leaks plaintext)
  stated defensively as the reason to authenticate, with no attack procedure. CTR built from AES as a
  keystream, and the catastrophe of reusing a (key, counter) pair shown as keystream reuse. IV/nonce
  requirements per mode tabulated. This part deliberately ends on "and none of this detects
  tampering" to motivate Part 5.
- **Lab:** G1 · runs anywhere · ladder E1–E5 · access: none. ECB-vs-CTR on a bitmap; CBC padding by
  hand; CTR keystream-reuse demonstration — all on local data.
- **Key sources:** NIST SP 800-38A; the ECB-penguin as cited illustration.
- **Search intent:** "ecb vs cbc vs ctr", "why is ecb insecure", "cbc padding explained", "ctr mode nonce reuse"

### Part 5 — Authenticated Encryption: GCM, ChaCha20-Poly1305 and the Nonce That Breaks Them

- **Slug:** authenticated-encryption-aead · **Arc:** Symmetric encryption · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 8,500 · **Figures:** 14
- **Answers:** How do you get confidentiality and integrity in one primitive, and what single mistake
  destroys both?
- **Assumes:** Part 4's CTR mode.
- **Hands off:** The Poly1305 MAC's standalone use to 7; key derivation for per-message keys to 8;
  AEAD inside TLS to 14; envelope use to 16.
- **Worked example:** AES-GCM on a short message with associated data: CTR for confidentiality, GHASH
  (a polynomial MAC in GF(2¹²⁸)) for the tag, computed on small numbers, the tag verified and then a
  single ciphertext bit flipped to show verification fail-closed. ChaCha20-Poly1305 (RFC 8439) on its
  own test vector, the quarter-round and Poly1305 evaluation shown. The nonce rule stated as law:
  reusing a GCM nonce under one key leaks the authentication subkey and forges tags — shown as the
  algebra, defensively, as the reason nonces are counters or random-96-bit-with-limits. Encrypt-then-MAC
  vs the AEAD construction; why "MAC-then-encrypt" caused historical trouble, named not reproduced.
- **Lab:** G1 · runs anywhere · ladder E1–E5 · access: none. `cryptography` AESGCM/ChaCha20Poly1305 on
  RFC vectors; a from-scratch GHASH and Poly1305 on small inputs; tamper-detection check.
- **Key sources:** NIST SP 800-38D (GCM); RFC 8439 (ChaCha20-Poly1305); Rogaway on AEAD.
- **Search intent:** "what is aead", "aes-gcm explained", "chacha20 poly1305", "gcm nonce reuse danger"

### Part 6 — Cryptographic Hashing: Merkle–Damgård, the Sponge, and SHA-256 by Hand

- **Slug:** cryptographic-hash-functions · **Arc:** Integrity and keys · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 8,500 · **Figures:** 14
- **Answers:** What is a cryptographic hash, how is one built, and what does "collision-resistant"
  actually promise?
- **Assumes:** Part 1.
- **Hands off:** Keyed hashing (MACs) to 7; password hashing to 8; hashes inside signatures to 12;
  hashes inside TLS/HKDF to 8 and 14.
- **Worked example:** SHA-256 of `"abc"`: the padding, the message schedule W[0..63], and the first
  compression rounds' working variables shown by hand, the final digest `ba7816bf…f20015ad` matched
  to the NIST vector. Merkle–Damgård construction and its length-extension property stated
  defensively (why `H(secret‖message)` is not a MAC, which motivates Part 7), with SHA-3/Keccak's
  sponge shown as the construction that does not have it. The three resistances (preimage,
  second-preimage, collision) separated with the birthday bound (why a 256-bit hash gives 128-bit
  collision resistance). MD5/SHA-1 named as collision-broken, with dates, as the reason to use SHA-256/3.
- **Lab:** G1 · runs anywhere · ladder E1–E5 · access: none. A pure-Python SHA-256 printing the
  schedule and round variables, verified against the vector; a birthday-collision search on a
  truncated hash; a length-extension demonstration against a naive `H(secret‖msg)` construction.
- **Key sources:** FIPS-180-4 (SHA-2); FIPS-202 (SHA-3/Keccak); Merkle 1979.
- **Search intent:** "how does sha-256 work", "merkle damgard construction", "hash collision resistance", "length extension attack"

### Part 7 — Message Authentication: HMAC, Poly1305 and Constant-Time Verification

- **Slug:** message-authentication-codes-hmac · **Arc:** Integrity and keys · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,000 · **Figures:** 9
- **Answers:** How do you prove a message was not altered and came from someone holding the key?
- **Assumes:** Part 6's hash functions.
- **Hands off:** MAC inside AEAD back-reference to 5; HKDF to 8; HMAC inside TLS to 14; the
  constant-time theme to 17.
- **Worked example:** HMAC-SHA256 on a message, the inner/outer pad construction shown and verified
  against the RFC 4231 vector, with the explanation of *why* the nested construction defeats the
  length-extension of Part 6. Poly1305 as a one-time MAC contrasted with HMAC's many-time use.
  Verification must be constant-time: a timing-safe compare vs `==`, with the *reason* (a byte-by-byte
  early-return leaks how many bytes matched) stated defensively and measured in Part 17. The MAC's
  security goal (existential unforgeability under chosen message) stated plainly.
- **Lab:** G1 · runs anywhere · ladder E1–E4 · access: none. HMAC from a hash primitive verified
  against RFC 4231; `hmac.compare_digest` vs naive compare; a Poly1305 one-time MAC.
- **Key sources:** RFC 2104 and FIPS-198-1 (HMAC); RFC 4231 (vectors); Bernstein (Poly1305).
- **Search intent:** "what is an hmac", "hmac vs hash", "constant time comparison", "message authentication code explained"

### Part 8 — Passwords and Key Derivation: PBKDF2 to Argon2, and HKDF

- **Slug:** key-derivation-password-hashing · **Arc:** Integrity and keys · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,500 · **Figures:** 10
- **Answers:** How do you turn a password or a shared secret into a key, so that a stolen database or
  a single secret does not hand over everything?
- **Assumes:** Part 7's HMAC.
- **Hands off:** HKDF's use inside TLS to 14; envelope/key-hierarchy use to 16.
- **Worked example:** Why a raw hash is the wrong tool for passwords (it is fast, so it is fast for the
  attacker too) — the distinction from Part 6 made concrete. Salting against precomputation, worked
  on two users with the same password. The memory-hard progression PBKDF2 → bcrypt → scrypt → Argon2,
  with Argon2's time/memory/parallelism parameters chosen against a measured target (e.g. ~250 ms on
  this CPU), the cost table shipped as the lab's number. Then HKDF (RFC 5869): extract-then-expand,
  deriving several independent subkeys from one shared secret with distinct `info` labels — the
  pattern Part 14 uses. Peppers and server-side secrets named.
- **Lab:** G1 · runs anywhere · ladder E1–E4 · access: none. Argon2 (argon2-cffi) parameter sweep with
  timings captured; PBKDF2/scrypt for contrast; HKDF deriving labelled subkeys, verified against RFC 5869.
- **Key sources:** RFC 9106 (Argon2); RFC 5869 (HKDF); NIST SP 800-132 (PBKDF2); the PHC results.
- **Search intent:** "how to store passwords", "argon2 vs bcrypt vs pbkdf2", "what is hkdf", "password salt pepper"

### Part 9 — RSA on Real Numbers: The Trapdoor, and Why Textbook RSA Is Broken

- **Slug:** rsa-cryptography-explained · **Arc:** Public-key cryptography · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 8,500 · **Figures:** 13
- **Answers:** How can two parties who never met communicate secretly, and how does RSA make that a
  one-way street out of arithmetic?
- **Assumes:** Part 1. Modular exponentiation and Euler's theorem introduced here.
- **Hands off:** Agreement without encryption to 10; signatures to 12; post-quantum replacement to 15.
- **Worked example:** RSA end to end on small-but-real numbers: p=61, q=53, n=3233, φ=3120, e=17,
  d=2753; encrypt m=65 → c=65¹⁷ mod 3233 = 2790; decrypt 2790²⁷⁵³ mod 3233 = 65 — every step by hand
  with fast modular exponentiation shown. The trapdoor framed as factoring (recovering d needs φ needs
  the factors of n). Then why **textbook RSA is broken**: it is deterministic (same message → same
  ciphertext) and malleable, shown on the toy key, which is the reason real RSA uses OAEP for
  encryption and encrypts a symmetric key, not data. Key sizes (why 2048/3072-bit) and the cost of
  factoring named with dates. RSA-PSS is deferred to Part 12.
- **Lab:** G1 · runs anywhere · ladder E1–E5 · access: none. Pure-Python RSA on the toy key (keygen by
  trial primes, square-and-multiply modexp); a determinism/malleability demonstration on textbook RSA;
  `cryptography` OAEP for the real construction.
- **Key sources:** Rivest, Shamir & Adleman 1978; RFC 8017 (PKCS#1, OAEP); Boneh "Twenty Years of RSA".
- **Search intent:** "how does rsa work", "rsa example by hand", "why is textbook rsa insecure", "rsa oaep padding"

### Part 10 — Diffie–Hellman and Forward Secrecy

- **Slug:** diffie-hellman-key-exchange · **Arc:** Public-key cryptography · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,500 · **Figures:** 10
- **Answers:** How do two parties agree on a shared secret over a channel an eavesdropper is reading,
  and why does using a fresh one each time protect yesterday's traffic?
- **Assumes:** Part 9's modular exponentiation and hard-problem framing.
- **Hands off:** The elliptic-curve version to 11; DH inside the TLS handshake to 14.
- **Worked example:** Diffie–Hellman on small numbers (a safe prime p, generator g, private a and b),
  both sides computing gᵃᵇ mod p by hand, with the discrete-log problem as the wall the eavesdropper
  hits. **Forward secrecy** made concrete: a static-key exchange exposes all past sessions if the
  long-term key leaks, an ephemeral exchange (DHE) does not — the same message tried both ways. The
  man-in-the-middle that unauthenticated DH does *not* stop, shown as the reason DH needs signatures
  (Part 12) and certificates (Part 13). Small-subgroup and parameter-validation pitfalls named defensively.
- **Lab:** G1 · runs anywhere · ladder E1–E4 · access: none. DH on a toy safe prime by hand and in
  Python; an ephemeral-vs-static forward-secrecy demonstration; the unauthenticated-MITM shown on two
  local "parties."
- **Key sources:** Diffie & Hellman 1976; RFC 7919 (FFDHE groups); Logjam write-up (for parameter hygiene, cited).
- **Search intent:** "how does diffie hellman work", "forward secrecy explained", "dhe vs static dh", "diffie hellman man in the middle"

### Part 11 — Elliptic-Curve Cryptography: The Group Law, ECDH and Curve25519

- **Slug:** elliptic-curve-cryptography · **Arc:** Public-key cryptography · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,000 · **Figures:** 14
- **Answers:** Why can elliptic curves give the same security as RSA with a quarter of the key size,
  and what is the "addition" that makes them work?
- **Assumes:** Part 10's Diffie–Hellman.
- **Hands off:** ECDSA/Ed25519 to 12; X25519 inside TLS to 14; the quantum break to 15.
- **Worked example:** Point addition and doubling on the toy curve y² = x³ + 2x + 2 over F₁₇
  (order 19), the chord-and-tangent geometry and the field formulas both shown, a full scalar
  multiplication kP computed by double-and-add. ECDH on that curve, giving the same shared-secret
  picture as Part 10 with far smaller numbers, and why (the ECDLP is harder per bit than integer DLP).
  Curve25519/X25519 (RFC 7748) introduced as the modern, misuse-resistant choice — Montgomery ladder,
  clamping, why it avoids the point-validation footguns. Named defensively: invalid-curve and
  small-subgroup conditions, and how X25519's design removes them.
- **Lab:** G1 · runs anywhere · ladder E1–E5 · access: none. Pure-Python group law on the toy curve
  with every intermediate; double-and-add scalar mult; `cryptography` X25519 for a real exchange,
  verified against RFC 7748.
- **Key sources:** Koblitz 1987 and Miller 1985; Bernstein (Curve25519); RFC 7748; NIST SP 800-186.
- **Search intent:** "elliptic curve cryptography explained", "ecc point addition", "why ecc smaller keys", "curve25519 x25519"

### Part 12 — Digital Signatures: RSA-PSS, ECDSA and Ed25519

- **Slug:** digital-signatures-explained · **Arc:** Public-key cryptography · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 8,500 · **Figures:** 13
- **Answers:** How do you prove a message came from a specific key holder and was not changed — the
  reverse of encryption — and what nonce mistake has leaked real private keys?
- **Assumes:** Part 11's elliptic curves (and links Part 9's RSA and Part 6's hashing).
- **Hands off:** Signatures binding identities to keys (certificates) to 13; signatures in the TLS
  handshake to 14; post-quantum signatures to 15.
- **Worked example:** Sign-then-verify with RSA-PSS on the toy key from Part 9 (hash, encode, the
  randomised padding), contrasted with why PKCS#1 v1.5 needed care. ECDSA on the Part 11 curve, worked
  through, with the **nonce catastrophe** shown as algebra: a repeated per-signature nonce k lets
  anyone solve for the private key from two signatures — the defensive reason to use RFC 6979
  deterministic nonces or Ed25519. Ed25519 (RFC 8032) as the deterministic, misuse-resistant default,
  verified against its test vector. Signatures vs MACs (public verifiability, non-repudiation) made explicit.
- **Lab:** G1 · runs anywhere · ladder E1–E5 · access: none. RSA-PSS, ECDSA and Ed25519 via
  `cryptography` on published vectors; the ECDSA repeated-nonce key-recovery shown on the toy curve
  (local keys only, as the reason deterministic nonces exist).
- **Key sources:** FIPS-186-5; RFC 8032 (EdDSA); RFC 6979 (deterministic ECDSA); RFC 8017 (PSS).
- **Search intent:** "how do digital signatures work", "ecdsa vs ed25519", "ecdsa nonce reuse", "rsa-pss vs pkcs1"

### Part 13 — Certificates and the Chain of Trust

- **Slug:** x509-certificates-pki · **Arc:** Trust and protocols · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 7,000 · **Figures:** 11
- **Answers:** A signature proves a key signed something — but how do you know the key belongs to the
  server you meant, and not an impostor?
- **Assumes:** Part 12's signatures.
- **Hands off:** The certificate's use in the handshake to 14.
- **Worked example:** A real certificate (a self-issued chain the author generates locally with
  OpenSSL) parsed field by field: subject, issuer, validity, SAN, key usage, the signature over the
  TBSCertificate. A three-link chain (root → intermediate → leaf) validated step by step: each
  certificate's signature checked with the issuer's public key up to a trust anchor, name and validity
  and basic-constraints checks included. Revocation (CRL and OCSP, and OCSP stapling) and why it is
  hard. Certificate Transparency logs as the detective control against mis-issuance. The whole thing
  is why Part 10's MITM is stopped in practice. No attacks on CAs — only how validation is supposed to work.
- **Lab:** G2 · local service · ladder E1–E4 · access: none (a disposable local CA is self-provisioned).
  OpenSSL builds a local root/intermediate/leaf; a Python validator walks the chain; `openssl x509`/`asn1parse`
  reads the fields. Nothing leaves the machine.
- **Key sources:** RFC 5280 (X.509); RFC 6960 (OCSP); RFC 6962 (Certificate Transparency); the CA/Browser Forum BRs.
- **Search intent:** "how do tls certificates work", "x509 certificate explained", "certificate chain validation", "what is certificate transparency"

### Part 14 — The TLS 1.3 Handshake, Traced

- **Slug:** tls-1-3-handshake-explained · **Arc:** Trust and protocols · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,000 · **Figures:** 15
- **Answers:** How do all of these primitives combine, in order, to turn an open TCP connection into
  an authenticated, confidential channel in one round trip?
- **Assumes:** Part 13's certificates (and links 5 AEAD, 11 X25519, 12 signatures, 8 HKDF).
- **Hands off:** 0-RTT replay caveat forward-linked to SEC-2/SEC-3 where request replay is a defensive
  topic; nothing else — this is the arc's capstone.
- **Worked example:** A TLS 1.3 handshake traced against RFC 8448's worked transcript and a live local
  capture (`openssl s_client`/`s_server` on loopback): ClientHello with key_share (X25519) → ServerHello
  → {EncryptedExtensions, Certificate, CertificateVerify (a signature over the transcript),
  Finished} → client Finished. The key schedule derived step by step with HKDF-Expand-Label — early,
  handshake and application traffic secrets — showing exactly where Parts 8, 11, 12 and 5 each plug in.
  1-RTT vs 0-RTT, and why 0-RTT data is replayable (stated defensively). Downgrade protection. The TLS
  1.2 differences named, not re-taught. This part is the "trace on the wire" the whole series builds toward.
- **Lab:** G2 · local service · ladder E1–E5 · access: none. `openssl s_server`/`s_client` on 127.0.0.1
  with `-keylogfile`; a Python parser walks the records; the key schedule reproduced from RFC 8448
  inputs and checked. Loopback only.
- **Key sources:** RFC 8446 (TLS 1.3); RFC 8448 (worked traces); RFC 5869 (HKDF); the TLS 1.3 analysis papers.
- **Search intent:** "tls 1.3 handshake explained", "tls 1.3 key schedule", "tls 1.3 vs 1.2", "tls 0-rtt replay"

### Part 15 — Post-Quantum Cryptography: Why Shor Breaks RSA, and What Replaces It

- **Slug:** post-quantum-cryptography · **Arc:** Frontier and practice · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 8,500 · **Figures:** 13
- **Answers:** Why does a large quantum computer break RSA and elliptic curves, and what are the
  standardised replacements and how do you deploy them today?
- **Assumes:** Part 9's RSA and (link) Part 11's ECC.
- **Hands off:** Nothing; closes the public-key story.
- **Worked example:** Shor's algorithm at the level that matters — it turns factoring/discrete-log into
  period-finding, so RSA and ECC fall together, while symmetric and hash primitives only lose a
  Grover factor (why AES-256 and SHA-384 are the conservative choices). Lattice intuition: the
  shortest-vector / learning-with-errors problem as the new wall, worked on a tiny LWE instance.
  ML-KEM (Kyber, FIPS-203) for key encapsulation and ML-DSA (Dilithium, FIPS-204) for signatures,
  with their sizes contrasted against X25519/Ed25519, run locally (OpenSSL 3.5 ships ML-KEM). Hybrid
  deployment (X25519+ML-KEM) and the "harvest now, decrypt later" reason to migrate, with dates.
- **Lab:** G1 · runs anywhere · ladder E1–E5 · access: none. ML-KEM/ML-DSA via OpenSSL 3.5 / liboqs
  bindings; a toy LWE example by hand; a size/latency comparison table captured on this machine.
- **Key sources:** Shor 1994; FIPS-203/204/205; Regev (LWE); NIST PQC project; the X25519+ML-KEM hybrid drafts.
- **Search intent:** "post quantum cryptography explained", "why does shor break rsa", "ml-kem kyber", "harvest now decrypt later"

### Part 16 — Encryption in Practice: Envelope Encryption, Key Hierarchies and Rotation

- **Slug:** key-management-envelope-encryption · **Arc:** Frontier and practice · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,500 · **Figures:** 10
- **Answers:** In a real system with millions of records and keys that must rotate, where do keys
  live, how is data encrypted at scale, and how do you rotate a key without re-encrypting everything?
- **Assumes:** Part 5's AEAD (and links Part 8's KDF).
- **Hands off:** Nothing; closes the series. Operational detection of key misuse is SEC-2's ground.
- **Worked example:** Envelope encryption built locally: a per-record data key wraps the data with
  AES-GCM, and a key-encryption key wraps the data keys — so rotating the KEK re-wraps only the data
  keys, not the data, shown with counts. A key hierarchy (root → KEK → DEK), rotation and versioning
  (every ciphertext carries its key id), and why. KMS/HSM as where the root key lives and never
  leaves, modelled locally (no cloud account), with the API shape named. Choosing a misuse-resistant
  library (libsodium/`cryptography`) over hand-rolled constructions, tying back every footgun the
  series named. Secrets in configuration, and what not to put in source control.
- **Lab:** G1 · runs anywhere · ladder E1–E4 · access: none. A local envelope-encryption implementation
  with KEK rotation counted; a versioned-key decryption path; a local "KMS" shim modelling the boundary.
- **Key sources:** NIST SP 800-57 (key management); the AWS/GCP KMS envelope-encryption docs (cited as
  design, not a product tutorial); libsodium documentation.
- **Search intent:** "what is envelope encryption", "key rotation without re-encrypting", "data encryption key vs key encryption key", "kms explained"

### Part 17 (optional) — Side Channels: Timing, and Why Constant-Time Code Matters

- **Slug:** cryptographic-side-channels-constant-time · **Arc:** Optional · **Status:** planned
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 6,000 · **Figures:** 9
- **Answers:** If the math is sound, how does a secret still leak — and how do you write code that does not?
- **Assumes:** Part 7's constant-time theme.
- **Worked example:** A naive string compare vs `compare_digest`, with the timing difference *measured*
  on this CPU as a histogram — the concrete version of Part 7's rule. Why table lookups and branches on
  secret data leak (cache and timing), at a conceptual level, and how constant-time code avoids them
  (no secret-dependent branch, index or early return). Blinding for RSA/ECC named. This is defensive
  engineering, measured locally on the author's own code — no attack on any system.
- **Lab:** G1 · runs anywhere · ladder E1–E4 · access: none. A timing harness over naive vs constant-time
  compare (many trials, percentiles reported with the provenance line); a constant-time select.
- **Key sources:** Kocher 1996; the constant-time coding guidelines (BearSSL, HACL*); `hmac.compare_digest` docs.
- **Search intent:** "timing attack explained", "constant time comparison", "why is == insecure for macs", "cache timing side channel"

### Part 18 (optional) — Secure Messaging: The Double Ratchet

- **Slug:** double-ratchet-secure-messaging · **Arc:** Optional · **Status:** planned
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 6,000 · **Figures:** 9
- **Answers:** How does a messaging app give every single message its own key, so that one stolen key
  exposes neither the past nor the future?
- **Assumes:** Part 11's X25519 (and links Part 8's HKDF, Part 5's AEAD).
- **Worked example:** The double ratchet assembled from pieces the series already built: a Diffie–Hellman
  ratchet (new X25519 exchange per round trip) and a symmetric-key ratchet (HKDF chain), giving forward
  secrecy and post-compromise security — shown as a message sequence where a key compromised at step N
  protects steps before and after. X3DH for the initial agreement, named. Where Signal/WhatsApp/Matrix
  use it. Conceptual and constructive; no attack content.
- **Lab:** G1 · runs anywhere · ladder E1–E4 · access: none. A minimal double-ratchet between two local
  parties (X25519 + HKDF + AEAD), showing per-message keys and the forward-secrecy property on a transcript.
- **Key sources:** the Signal double-ratchet and X3DH specifications; Marlinspike & Perrin; Cohn-Gordon et al. (analysis).
- **Search intent:** "how does the double ratchet work", "signal protocol explained", "forward secrecy messaging", "post-compromise security"

## Publication order and cadence

Strict prerequisite order; a part may publish once the one part it names under **Assumes** is live.
The six arcs are the natural release waves: Foundations (1–2), Symmetric (3–5), Integrity (6–8),
Public-key (9–12), Trust (13–14), Frontier/practice (15–16), then the two optional spokes. One part
per week keeps the arcs coherent in the feed. Versions (OpenSSL, `cryptography`, library pins) are
fixed per part at research time from the dated standard, never from this plan.

## Cross-links

Within the series, each part links back to the one part it assumes, by the published anchor, once
that part is live (owner inserts links; parts name earlier parts in plain text until then). Across
the `security` category: SEC-2 (Defensive) references this series for the primitives behind TLS,
password storage and at-rest encryption; SEC-3 (Secure Engineering) references Parts 6–8 and 12 where
weak hashing, missing salts and signature/token misuse are the defensive lesson; AG-2 (Agentic
Security) references Part 16 for scoped-credential handling. Links run only from the later-published
part; published parts are never edited to add forward links.

## Lab policy

Every part is **G1 — runs anywhere**, self-provisioned, no access request. The toolchain is a `uv`
environment pinning `cryptography` (≈50.x) and `argon2-cffi`, plus OpenSSL 3.5 already on the machine
for the certificate, TLS and post-quantum parts. Pattern for every primitive: a pure-Python,
by-hand implementation that prints intermediates and is **verified against the standard's own test
vector**, beside the production library call — so prose, figure and lab cannot disagree, and the
reader sees both the mechanism and the right way to use it. Two parts stand up a **local** service on
loopback only (13 a disposable CA, 14 `openssl s_server`), which is G2 by grade but needs nothing
beyond user space. No number is invented; measured timings (AES throughput, Argon2 cost, the Part 17
histogram) ship with a provenance line. Every "what breaks it" is demonstrated **against the author's
own local toy keys and data**, never a real or remote system, and is framed as the condition to
avoid.

### Access requests

None. The probe (see `access.md`) shows everything this series needs is present or user-space
installable. This is why SEC-1 is recommended as the first series to build.

## What this series will not cover

- **Breaking real systems.** No exploit code, no attack procedure against any deployed service, no
  key-recovery against anything but the author's own toy parameters. Misuse is shown only as the
  defensive condition to avoid. Operational attack and defence live in SEC-2 and SEC-3.
- **The formal proofs.** Security games and reductions are given as intuition (what the scheme must
  win), not as theorems. Provable-security as a discipline is named, not taught.
- **Cryptanalysis as a craft** (differential/linear cryptanalysis, lattice reduction algorithms,
  factoring algorithm internals beyond naming them).
- **Protocol zoo beyond TLS and the double ratchet:** SSH, IPsec, Noise, Kerberos crypto internals,
  PGP/GPG, Tor — named where relevant, not given parts. (Kerberos-as-authentication is SEC-2.)
- **Blockchain and zero-knowledge** (zk-SNARKs/STARKs, commitment schemes beyond a mention, MPC,
  homomorphic encryption) — a possible future series, not this one.
- **Hardware crypto** (TPM/secure-enclave internals, side-channel *hardware* attacks like power/EM
  beyond the conceptual timing part).
- **Standards archaeology and deprecated primitives** beyond naming MD5/SHA-1/DES/RC4/3DES and why
  they are retired.
- **Regulatory/compliance mapping** (FIPS validation process, Common Criteria) beyond naming the
  standards a primitive comes from.

## Risks

- **Overlap with `security` siblings.** The boundary with SEC-2/SEC-3 (misuse shown as a condition
  here; operational attack/defence there) must be recorded in `context.md` at Checkpoint S and kept.
- **By-hand implementations must match vectors exactly.** Every toy primitive is verified against the
  standard's published test vector in the lab; a figure that disagrees with the vector fails the build.
- **"Don't roll your own crypto" tension.** The series teaches by building primitives, which could be
  misread as endorsing hand-rolled production crypto. Every part states plainly: build it to
  understand it, ship the vetted library — and Part 16 closes on exactly that.
- **Version/standard currency.** PQC names (ML-KEM/ML-DSA) and OpenSSL/`cryptography` behaviour are
  recent; pin versions per part at research time against the dated FIPS/RFC, not this plan.
- **Difficulty drift.** Several parts are advanced (3, 5, 6, 9, 11, 12, 14, 15); each must still open
  with a worked instance before the formalism, per the house rule, so an engineer can enter at any primitive.

## Open decisions for the owner

1. **18 parts (16 + 2 optional), or the 16-part core?** Recommendation: commit 16, build the two
   optional spokes if the arc lands well.
2. **Category row.** Publishing any part needs a `security` category in the DB (live DB lacks it) —
   a production write, your call at publish time. The plan and build need nothing.
3. **Title.** *Applied Cryptography: From the Bytes Up* — one word to overrule.
