# Series plan — Defensive Security / Blue Team

**Slug:** defensive-security-blue-team · **Shape:** hybrid · **Parts:** 18 (16 committed, 2 optional) ·
**Category:** `security` · **Status:** Checkpoint S — awaiting approval (planned 2026-10-11)
**Display title:** *Defensive Security: The Blue-Team Handbook*

## Why this is a series and not one post

**SEC-2** owns how systems are protected, monitored and recovered: threat modelling, firewalls,
segmentation, intrusion detection, hardening, identity and authorization, logging and detection
engineering, incident response and governance. It is the "firewalls and many more" defensive track.
The seams are hard (no detection engineering before logging; no IR before detection), the budget is
~130,000 words, each part a distinct search intent. Benign throughout — this is the defender's craft.

## Framing

Educational and defence-oriented, like the whole `security` category. Every control is built and
**measured** against a *simulated* condition in an isolated local environment; any adversary
behaviour is a test input, never an operation against a real system. SEC-1 supplies the cryptographic
primitives; SEC-3 supplies the vulnerability classes these controls defend against.

## The angle

Blue-team content is vendor docs and cert cram. Unowned: **build the control and measure it** — a
firewall rule set that works vs one that silently leaks, a seccomp profile that blocks a syscall, an
IDS rule that fires on a simulated pattern, a Sigma rule mapped to ATT&CK — mechanism, not checklist.
Each part corrects a reflex: "a firewall keeps you safe" (it is one layer; defence in depth), "SELinux
is hard, disable it" (no — profile it), "more logging is more security" (signal vs noise and cost),
"MFA is unbreakable" (phishing-resistant vs not).

## Shape and dependencies

Hybrid: a controls ladder (1→2→3) then identity, detection and response arcs. Each part ≤1 lower
parent. Deps: 2←1, 3←2, 4←2, 5←1, 6←1, 7←6, 8←6, 9←1, 10←1, 11←10, 12←1, 13←5, 14←5, 15←11, 16←15,
17←15, 18←1.

## Arcs

| Parts | Arc | Purpose |
|---|---|---|
| 1 | Mindset | Threat modelling. |
| 2–5 | Network and host controls | Firewall, segmentation/zero-trust, IDS/IPS, host hardening. |
| 6–9 | Identity and secrets | Authentication, Kerberos, authorization, secrets management. |
| 10–11 | See it | Logging/SIEM; detection engineering (ATT&CK → Sigma). |
| 12–14 | Keep it safe | Vulnerability management; container/K8s; cloud posture. |
| 15–16 | Respond and govern | Incident response; GRC frameworks. |
| 17–18 | Optional | Forensics; the SOC and its metrics. |

## Reader objectives

| # | After this the reader can ... | Part |
|---|---|---|
| 1 | threat-model a system (STRIDE, attack trees) | 1 |
| 2 | write a correct stateful firewall policy | 2 |
| 3 | segment a network and reason about zero trust | 3 |
| 4 | deploy and tune intrusion detection | 4 |
| 5 | harden a host with least privilege and sandboxing | 5 |
| 6 | choose and configure authentication (MFA/OAuth/OIDC/SAML) | 6 |
| 7 | explain Kerberos in an enterprise | 7 |
| 8 | design authorization (RBAC/ABAC) | 8 |
| 9 | manage secrets safely | 9 |
| 10 | build a logging/audit pipeline | 10 |
| 11 | write detections mapped to ATT&CK | 11 |
| 12 | run vulnerability management and patching | 12 |
| 13 | secure containers and Kubernetes | 13 |
| 14 | assess cloud security posture | 14 |
| 15 | run an incident response | 15 |
| 16 | map controls to GRC frameworks | 16 |

## Parts

### Part 1 — Thinking Like a Defender: Threat Modelling
- **Slug:** threat-modeling-stride · L3 · intermediate · ~6,000 · 9 figs
- **Answers:** how do you find what to defend, before you buy a single control?
- **Assumes:** none. **Hands off:** each control to its part; developer threat modelling to SEC-3.
- **Worked example:** STRIDE and attack trees applied to a small system; data-flow diagrams and trust boundaries; prioritising by risk; turning threats into concrete controls and tests.
- **Lab:** G1 · E1–E3 · none.
- **Search intent:** "threat modeling", "stride methodology", "attack trees"

### Part 2 — The Firewall: Stateless, Stateful and Connection Tracking
- **Slug:** firewall-stateful-nftables · L4 · advanced · ~7,000 · 11 figs
- **Answers:** how does a firewall actually decide, and how do you write rules that don't silently leak?
- **Assumes:** Part 1 (links networking). **Hands off:** segmentation to 3.
- **Worked example:** stateless vs stateful filtering; nftables rules built and tested in isolated netns; connection tracking (conntrack) shown; default-deny; a common misordering that leaks, caught by testing; logging drops.
- **Lab:** G2 · E1–E5 · isolated Docker/netns (container AR).
- **Search intent:** "how firewalls work", "nftables tutorial", "stateful firewall conntrack"

### Part 3 — Network Segmentation and Zero Trust
- **Slug:** network-segmentation-zero-trust · L3 · intermediate · ~6,000 · 9 figs
- **Answers:** how do you limit blast radius with segmentation, and what does "zero trust" actually mean?
- **Assumes:** Part 2. **Hands off:** identity to 6.
- **Worked example:** segments/VLANs/microsegmentation in netns; east-west vs north-south; the flat-network failure (one foothold → everything) shown and fixed; zero-trust principles (verify, least privilege, assume breach) made concrete.
- **Lab:** G2 · E1–E4 · segmented netns (container AR).
- **Search intent:** "network segmentation", "zero trust architecture", "microsegmentation"

### Part 4 — Intrusion Detection and Prevention
- **Slug:** ids-ips-detection · L4 · advanced · ~7,000 · 11 figs
- **Answers:** how do you detect malicious activity on the network, by signature and by anomaly?
- **Assumes:** Part 2. **Hands off:** detection engineering to 11.
- **Worked example:** signature detection (a Suricata/Zeek rule firing on a simulated pattern in netns) vs anomaly/behaviour; false-positive tuning; mapping alerts to MITRE ATT&CK; IDS vs IPS placement; the evasion/limits named defensively.
- **Lab:** G2 · E1–E5 · IDS in netns on local traffic (container AR).
- **Search intent:** "ids vs ips", "suricata rules", "network intrusion detection"

### Part 5 — Host Hardening: Least Privilege and Sandboxing
- **Slug:** host-hardening-sandboxing · L4 · advanced · ~7,000 · 11 figs
- **Answers:** how do you shrink what a process can do, so a compromise is contained?
- **Assumes:** Part 1 (links operating-systems). **Hands off:** containers to 13.
- **Worked example:** Linux capabilities, seccomp (a profile blocking a syscall, shown), namespaces and cgroups, AppArmor/SELinux (a policy confining a service); the principle of least privilege made concrete; CIS-benchmark-style hardening with the measured reduction in attack surface.
- **Lab:** G2 · E1–E5 · isolated host/container (container AR).
- **Search intent:** "linux hardening", "seccomp profile", "selinux apparmor", "least privilege"

### Part 6 — Authentication: MFA, OAuth, OIDC and SAML
- **Slug:** authentication-oauth-oidc · L4 · advanced · ~7,000 · 11 figs
- **Answers:** how do modern authentication protocols work, and what makes MFA phishing-resistant or not?
- **Assumes:** Part 1 (links SEC-1 for the crypto). **Hands off:** Kerberos to 7; authorization to 8.
- **Worked example:** passwords + MFA (TOTP vs WebAuthn/passkeys, and why one resists phishing); the OAuth 2.0 / OIDC flows traced (authorization code + PKCE); SAML assertions; session management; the token-handling pitfalls stated defensively.
- **Lab:** G2 · E1–E4 · local IdP + client in netns (container AR).
- **Search intent:** "oauth vs oidc vs saml", "how mfa works", "webauthn passkeys"

### Part 7 — Kerberos and Enterprise Authentication
- **Slug:** kerberos-authentication · L3 · advanced · ~6,000 · 9 figs
- **Answers:** how does single sign-on work inside an enterprise, ticket by ticket?
- **Assumes:** Part 6.
- **Worked example:** the Kerberos exchange (AS, TGS, service ticket) traced on a local KDC; tickets and delegation; why it avoids sending passwords; the common misconfigurations named defensively.
- **Lab:** G2 · E1–E4 · local KDC in netns (container AR).
- **Search intent:** "how kerberos works", "kerberos tickets", "enterprise sso"

### Part 8 — Authorization: RBAC, ABAC and Policy
- **Slug:** authorization-rbac-abac · L3 · intermediate · ~6,000 · 9 figs
- **Answers:** once you know who someone is, how do you decide what they may do?
- **Assumes:** Part 6 (links AG-2 semantic authz).
- **Worked example:** RBAC vs ABAC vs ReBAC; policy as code (a small OPA/Rego-style policy evaluated); least privilege and separation of duties; the role-explosion and over-permission traps; testing an authz policy.
- **Lab:** G1 · E1–E4 · none (policy engine locally).
- **Search intent:** "rbac vs abac", "policy as code", "authorization models"

### Part 9 — Secrets Management
- **Slug:** secrets-management · L3 · intermediate · ~6,000 · 9 figs
- **Answers:** where do credentials live so they aren't in code, logs or history?
- **Assumes:** Part 1 (links SEC-1 key management). **Hands off:** secrets-in-code detection to SEC-3.
- **Worked example:** the secret-sprawl problem; a secrets manager's model (dynamic/short-lived secrets, leasing, rotation) run locally; detecting secrets in a repo; env-var and file pitfalls; the blast radius of a leaked long-lived credential.
- **Lab:** G2 · E1–E4 · local secrets store (container AR).
- **Search intent:** "secrets management", "vault dynamic secrets", "credential rotation"

### Part 10 — Logging, SIEM and the Audit Trail
- **Slug:** logging-siem · L3 · intermediate · ~6,000 · 9 figs
- **Answers:** what do you log, where does it go, and how do you keep it useful (and affordable)?
- **Assumes:** Part 1. **Hands off:** detections to 11.
- **Worked example:** what security-relevant events to capture; log pipeline and normalisation; the signal/noise and cost trade; tamper-evident audit logs; building a query that answers "what did this account do?" on a local log set.
- **Lab:** G2 · E1–E4 · local log pipeline (container AR).
- **Search intent:** "security logging", "siem explained", "audit log design"

### Part 11 — Detection Engineering: From ATT&CK to Sigma Rules
- **Slug:** detection-engineering-sigma · L4 · advanced · ~7,000 · 11 figs
- **Answers:** how do you turn attacker techniques into detections that fire on the right thing?
- **Assumes:** Part 10. **Hands off:** IR to 15.
- **Worked example:** the MITRE ATT&CK matrix as a coverage map; writing a Sigma rule for a technique and testing it against simulated telemetry; detection-as-code and CI for rules; measuring detection coverage and tuning false positives — all on local data.
- **Lab:** G2 · E1–E5 · local telemetry + rules (container AR).
- **Search intent:** "detection engineering", "sigma rules", "mitre attack detection"

### Part 12 — Vulnerability Management and Patching
- **Slug:** vulnerability-management · L3 · intermediate · ~6,000 · 9 figs
- **Answers:** how do you find, prioritise and fix vulnerabilities at scale without drowning?
- **Assumes:** Part 1 (links SEC-3). **Hands off:** dependency/supply-chain depth to SEC-3.
- **Worked example:** scanning; CVSS and why it is not priority on its own (exploitability, exposure, EPSS); the patch/risk-accept decision; SLAs; the asset-inventory prerequisite; measuring mean-time-to-remediate.
- **Lab:** G2 · E1–E4 · local scan of a known-vulnerable image (container AR).
- **Search intent:** "vulnerability management", "cvss explained", "patch prioritization"

### Part 13 — Container and Kubernetes Security
- **Slug:** container-k8s-security · L4 · advanced · ~7,000 · 11 figs
- **Answers:** what is the attack surface of containers and orchestration, and how do you reduce it?
- **Assumes:** Part 5. **Hands off:** cloud to 14.
- **Worked example:** the container isolation model and its limits; image minimisation and scanning; the Kubernetes security context, network policies, RBAC, and admission control; the common misconfigurations (privileged pods, exposed dashboards) hardened — defensive, in a local cluster.
- **Lab:** G3 · E1–E4 · local kind/k3s cluster (container AR; needs the capability).
- **Search intent:** "container security", "kubernetes security", "pod security"

### Part 14 — Cloud Security Posture
- **Slug:** cloud-security-posture · L3 · intermediate · ~6,000 · 9 figs
- **Answers:** what are the recurring cloud failure modes, and how do you assess posture?
- **Assumes:** Part 5.
- **Worked example:** the shared-responsibility model; IAM least privilege and the over-permissioned role; public-exposure misconfigurations; posture management and guardrails (policy-as-code) — illustrated with a local model of cloud resources, concepts not a product tutorial.
- **Lab:** G1 · E1–E4 · none (local policy model).
- **Search intent:** "cloud security posture", "iam least privilege", "cspm"

### Part 15 — Incident Response: The Lifecycle
- **Slug:** incident-response-lifecycle · L4 · advanced · ~7,000 · 11 figs
- **Answers:** when something happens, what do you do, in what order, and how do you learn from it?
- **Assumes:** Part 11 (links AG-2 agent IR). **Hands off:** forensics to 17.
- **Worked example:** the IR lifecycle (prepare, detect, contain, eradicate, recover, learn) rehearsed on a simulated incident in a local environment; containment vs eradication; the post-mortem and the control that prevents recurrence; the runbook.
- **Lab:** G2 · E1–E5 · simulated incident in netns (container AR).
- **Search intent:** "incident response lifecycle", "incident response plan", "containment eradication"

### Part 16 — GRC: Frameworks, Compliance and Risk
- **Slug:** grc-frameworks-compliance · L3 · intermediate · ~6,000 · 9 figs
- **Answers:** how do the frameworks fit together, and how do you prove controls to an auditor?
- **Assumes:** Part 1 (and links across). **Hands off:** nothing; capstone.
- **Worked example:** NIST CSF, ISO 27001, SOC 2, and the regulatory set (named); mapping the controls built in this series to a framework; risk registers; evidence and continuous compliance; treating compliance as an output of good engineering.
- **Lab:** G1 · E1–E3 · none.
- **Search intent:** "nist csf", "iso 27001 vs soc 2", "security compliance frameworks"

### Part 17 (optional) — Digital Forensics Basics
- **Slug:** digital-forensics-basics · L3 · advanced · ~5,500 · 8 figs
- **Answers:** after an incident, how do you find out what happened without destroying the evidence?
- **Assumes:** Part 15.
- **Worked example:** order of volatility; acquiring and hashing an image; timeline analysis; artefacts on disk/memory; chain of custody — on a local disposable image.
- **Lab:** G2 · E1–E4 · local disposable image (container AR).
- **Search intent:** "digital forensics", "incident forensics", "order of volatility"

### Part 18 (optional) — The SOC and Its Metrics
- **Slug:** soc-metrics · L3 · intermediate · ~5,500 · 8 figs
- **Answers:** how does a security operations centre run, and what do you measure to know it works?
- **Assumes:** Part 11.
- **Worked example:** the SOC workflow (triage → investigate → respond); the alert-fatigue problem; MTTR/MTTD, detection coverage, false-positive rate; automation/SOAR; the metrics that actually drive improvement.
- **Lab:** G1 · E1–E3 · none.
- **Search intent:** "security operations center", "soc metrics", "mttr mttd"

## Publication order and cadence

Strict prerequisite order; waves follow the arcs. One part per week.

## Cross-links

Assumes SEC-1 for cryptographic primitives; references SEC-3 for the vulnerability classes these
controls defend against, AG-2 for agent-specific IR/authz, and networking (NET-1/2) for the substrate.
Links from the later part only.

## Lab policy

**G2/G3 — isolated Docker networks / namespaces**, sharing the container-capability access request
(the probe shows Docker unusable; one request covers networking and the Docker-dependent security
series). Every control is **built and measured locally** against a *simulated* condition — a firewall
rule tested, a seccomp profile blocking a syscall, an IDS/Sigma rule firing on local telemetry — never
against a real or remote system. A few parts (authz, cloud posture, GRC, SOC) are G1. If the capability
is declined, the Docker-dependent labs ship as documented configs plus captures from one granted run.
`access.md` created at build time.

## Key sources (confirm per part at research)

NIST CSF and the 800-series (800-53, 800-61 IR, 800-207 zero trust); MITRE ATT&CK; CIS Benchmarks; the
Sigma specification; the netfilter/nftables, Suricata/Zeek, and seccomp/SELinux docs; OWASP (for the
SEC-3 cross-reference).

## What this series will not cover

- **Cryptographic primitives** — SEC-1.
- **Application vulnerability classes and their code-level fixes** — SEC-3.
- **Agent-specific security** — AG-2.
- **Offensive operations / penetration-testing procedures against real systems** — out of scope entirely.
- **Vendor product tutorials and certification cram.**

## Open decisions for the owner

1. 18 parts (16 + 2 optional) or 16-part core.
2. Shares the container/netns capability request with networking and SEC-3/AG-2.
3. Title.
