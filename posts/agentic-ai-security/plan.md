# Series plan — Agentic AI Security

**Slug:** agentic-ai-security · **Shape:** hybrid · **Parts:** 18 (16 committed, 2 optional) ·
**Category:** `agentic-ai` (cross-filed `security`) · **Status:** Checkpoint S — awaiting approval (planned 2026-10-11)
**Display title:** *Agentic AI Security*

## Why this is a series and not one post

**AG-2** owns securing autonomous, tool-using agents: the threat model, the failure classes (prompt
injection, tool misuse, memory poisoning, supply-chain agents), the layered reference architecture,
and the detection/response/governance around it. It assumes AG-1's construction (the loop, tools,
memory, MCP) and secures it. The seams are hard (no runtime defence before the threat model; no
incident response before detection), the budget is ~120,000 words, each part a distinct search intent.
Cross-filed `security` because it is as much a security discipline as an AI one.

## Framing (firm)

**Educational and defence-oriented, exactly like the rest of the `security` category.** Each part
explains a failure *class* — how it arises and, above all, **how it is detected and mitigated**. Every
demonstration runs **only against a local agent and local, throwaway tools** in an isolated
environment (the frontier-models rule: never act against a hosted or real service). There is no
operational attack procedure and no weaponised payload; each part ends at the control. The failure
classes named below are the public, standard taxonomy (OWASP LLM/agentic Top 10, MITRE ATLAS, NIST AI
RMF) and the two named attack chains are from the Radware CISO guide, used as motivation for the
defence. Detailed per-part scoping is finalised at build time; per the model policy, that is the point
to move to Opus 4.8 if 5.5 is flagged.

## The angle

CISO guides describe the risks; vendor pages sell the product. Unowned: the **mechanism and the
measured control** — build a vulnerable local agent, show the failure, then **measure the mitigation's
effect and its residual**. Each part corrects a claim: "a prompt filter stops injection" (indirect
injection rides trusted content; perimeter controls miss it — the EchoLeak/ShadowLeak lesson),
"sandbox the tools and you're safe" (excessive agency and scope creep remain), "the model provider
handles security" (the agent runtime and tool layer are yours), "red-teaming is a one-time audit"
(agents drift; it is continuous).

## Shape and dependencies

Hybrid: a threat-model → failure-classes ladder (1→2→…→7) then a defence-layer arc mirroring the
reference architecture (8→…→12) and an operations arc (13→16). Each part ≤1 lower parent. Deps:
2←1, 3←2, 4←1, 5←1, 6←1, 7←1, 8←1, 9←8, 10←8, 11←10, 12←11, 13←8, 14←13, 15←14, 16←13, 17←6, 18←5.

## Arcs

| Parts | Arc | Purpose |
|---|---|---|
| 1 | Threat model | Why agent autonomy expands the blast radius. |
| 2–7 | Failure classes | Prompt injection (direct/indirect), tool misuse, memory poisoning, supply-chain agents, convergence with classic threats. |
| 8–12 | Layered defence | The reference architecture; model guards; runtime intent/plan validation; semantic authorization; scoped credentials. |
| 13–16 | Operations | Forensics/risk graph; drift detection; incident response; red-teaming and GRC. |
| 17–18 | Optional | Multi-agent trust; privacy and data governance. |

## Reader objectives

| # | After this the reader can ... | Part |
|---|---|---|
| 1 | reason about an agent's attack surface and blast radius | 1 |
| 2 | recognise and mitigate direct prompt injection | 2 |
| 3 | defend against indirect/cross-domain prompt injection | 3 |
| 4 | prevent tool misuse and excessive agency | 4 |
| 5 | detect and prevent memory/context poisoning | 5 |
| 6 | vet agents, plugins and MCP servers against supply-chain risk | 6 |
| 7 | recognise agent traffic that mimics classic threats | 7 |
| 8 | apply the layered reference architecture | 8 |
| 9 | put model-layer guards in place | 9 |
| 10 | validate goals and plans at the runtime layer | 10 |
| 11 | enforce semantic authorization for sensitive actions | 11 |
| 12 | scope credentials and tokens to least privilege | 12 |
| 13 | capture decision forensics and build a risk graph | 13 |
| 14 | detect behavioural/intent drift | 14 |
| 15 | run incident response for an agent | 15 |
| 16 | red-team agents and map to GRC frameworks | 16 |

## Parts

### Part 1 — Why Agent Autonomy Expands the Blast Radius
- **Slug:** agentic-threat-model · L3 · intermediate · ~6,000 · 9 figs
- **Answers:** what is new about securing an agent versus a model or an app?
- **Assumes:** AG-1 basics. **Hands off:** each failure class to its part; defence to 8.
- **Worked example:** an agent's attack surface mapped (inputs, tools, memory, other agents); how one mis-scoped objective or over-privileged tool cascades; the blast-radius difference from a stateless model call, on a local agent.
- **Lab:** G2 · E1–E4 · isolated local agent (container AR).
- **Search intent:** "agentic ai security", "ai agent attack surface", "llm agent risks"

### Part 2 — Prompt Injection and the Model's Trust Boundary
- **Slug:** prompt-injection-direct · L4 · advanced · ~7,000 · 11 figs
- **Answers:** why can instructions in input override intended behaviour, and how do you reduce it?
- **Assumes:** Part 1. **Hands off:** the indirect case to 3.
- **Worked example:** the no-trust-boundary problem (instructions and data share one channel) shown on a local agent; the mitigations and their **measured residual** — input/output guards, privilege separation, delimiting, and why none is a complete fix; treat injection as "when", not "if".
- **Lab:** G2 · E1–E4 · isolated local agent; defensive only.
- **Search intent:** "prompt injection", "prompt injection mitigation", "llm trust boundary"

### Part 3 — Indirect / Cross-Domain Prompt Injection
- **Slug:** indirect-prompt-injection · L4 · advanced · ~7,500 · 12 figs
- **Answers:** how do instructions hidden in content the agent later reads subvert it, and why do perimeter controls miss it?
- **Assumes:** Part 2.
- **Worked example:** the mechanism — an agent ingests crafted content (a doc/page/email) whose hidden instructions it then obeys — illustrated with the publicly-documented EchoLeak (client-side) and ShadowLeak (service-side) chains **as motivation for the defence**, reproduced only against a local agent and local content; the controls (content provenance/tagging, output egress filtering, least privilege, human gates) with their measured effect.
- **Lab:** G2 · E1–E5 · isolated local agent + local content; defensive only.
- **Search intent:** "indirect prompt injection", "echoleak shadowleak", "rag prompt injection defense"

### Part 4 — Tool Misuse and Excessive Agency
- **Slug:** tool-misuse-excessive-agency · L4 · advanced · ~7,000 · 11 figs
- **Answers:** how does an agent cause harm through its legitimate tools, and how do you bound it?
- **Assumes:** Part 1. **Hands off:** authorization to 11; credentials to 12.
- **Worked example:** excessive permissions, excessive functionality and excessive autonomy (the OWASP framing) shown on a local agent with over-broad tools; the controls — minimal tool set, safe-by-default verbs, confirmation for destructive actions, budget/timeboxing — each measured.
- **Lab:** G2 · E1–E5 · isolated local tools; defensive only.
- **Search intent:** "excessive agency llm", "tool misuse agent", "agent least privilege"

### Part 5 — Memory and Context Poisoning
- **Slug:** memory-context-poisoning · L4 · advanced · ~7,000 · 11 figs
- **Answers:** how does bad state get into an agent's memory, and how do you keep it clean?
- **Assumes:** Part 1. **Hands off:** data governance to 18.
- **Worked example:** seeding false long-term/vector memory and watching it bias later decisions, on a local agent; detection (provenance, anomaly checks on writes) and mitigation (memory validation, TTLs, rollback, isolation per trust level), each with its residual.
- **Lab:** G2 · E1–E4 · isolated local agent; defensive only.
- **Search intent:** "memory poisoning agent", "context poisoning llm", "vector store poisoning"

### Part 6 — Rogue and Supply-Chain Agents (Plugins and MCP Servers)
- **Slug:** supply-chain-agents-mcp · L4 · advanced · ~7,000 · 11 figs
- **Answers:** how do third-party agents, plugins and MCP servers become a supply-chain risk, and how do you vet them?
- **Assumes:** Part 1 (links AG-1 MCP). **Hands off:** multi-agent trust to 17.
- **Worked example:** a malicious/compromised local MCP server exfiltrating or manipulating, shown in isolation; the controls — server allow-listing, capability scoping, signature/provenance, sandboxing, monitoring tool-server behaviour — with their effect; impersonation of trusted services.
- **Lab:** G2 · E1–E5 · isolated local MCP server/client; defensive only.
- **Search intent:** "mcp server security", "malicious plugin llm", "ai supply chain security"

### Part 7 — When Agent Traffic Looks Like Classic Threats
- **Slug:** agent-traffic-classic-threats · L3 · intermediate · ~6,000 · 9 figs
- **Answers:** how does autonomous agent activity converge with API abuse, account takeover and automation surges?
- **Assumes:** Part 1 (links SEC-2 defensive security, networking). **Hands off:** detection to 14.
- **Worked example:** agent behaviour that resembles bot/API-abuse/credential-stuffing patterns; why legacy rate limits and CAPTCHA misfire on legitimate agents and miss malicious ones; behaviour-aware controls that tell them apart — defensive, measured on local traffic.
- **Lab:** G2 · E1–E4 · isolated local traffic; defensive only.
- **Search intent:** "ai agent api abuse", "bot detection agents", "agent vs attacker traffic"

### Part 8 — The Reference Architecture: Layered Defence for Agents
- **Slug:** agentic-reference-architecture · L4 · advanced · ~7,000 · 11 figs
- **Answers:** where do controls live so no single point is a failure, from data to edge?
- **Assumes:** Part 1. **Hands off:** each layer to 9–13.
- **Worked example:** the six layers — data & content, model/LLM guard, agent runtime, tools & APIs, apps & network, observability — mapped onto a local agent, with the control at each; out-of-path vs in-path enforcement; why breadth (observe everywhere) plus in-path stops for high-risk actions.
- **Lab:** G2 · E1–E4 · isolated local agent; defensive.
- **Search intent:** "agentic ai reference architecture", "llm security layers", "ai security architecture"

### Part 9 — Guardrails at the Model Layer
- **Slug:** llm-guardrails · L4 · advanced · ~7,000 · 11 figs
- **Answers:** what can input/output guarding at the model boundary actually catch, and what slips through?
- **Assumes:** Part 8 (links AG-1 Part 14, NLP-2 safety).
- **Worked example:** prompt/response filters, jailbreak and PII detection, content-policy enforcement, structured-output constraints — each with its true/false-positive rate measured on a local agent; the limits (why guards are necessary but not sufficient).
- **Lab:** G2 · E1–E5 · isolated local agent; defensive.
- **Search intent:** "llm guardrails", "jailbreak detection", "input output filtering llm"

### Part 10 — Intent and Plan Validation at the Runtime Layer
- **Slug:** intent-plan-validation · L4 · advanced · ~7,000 · 11 figs
- **Answers:** how do you stop an agent before it acts when its plan drifts from policy?
- **Assumes:** Part 8. **Hands off:** authorization to 11.
- **Worked example:** validating the agent's goal and plan against policy before execution; budget/timeboxing and loop limits as safety controls; detecting intent drift mid-task; the stop-before-commit pattern — measured on a local agent.
- **Lab:** G2 · E1–E4 · isolated local agent; defensive.
- **Search intent:** "agent runtime security", "intent validation llm", "plan validation agent"

### Part 11 — Semantic Authorization for Sensitive Actions
- **Slug:** semantic-authorization-tools · L4 · advanced · ~7,000 · 11 figs
- **Answers:** how do you authorize an agent's *actions* (not just its API calls) by meaning and context?
- **Assumes:** Part 10 (links SEC-2 RBAC/ABAC). **Hands off:** credentials to 12.
- **Worked example:** semantic authorization for sensitive verbs (transfer, delete, commit, export); contextual ABAC/RBAC on the action and its parameters; approval thresholds by risk; the difference from endpoint authz — measured on a local agent with tools.
- **Lab:** G2 · E1–E4 · isolated local tools; defensive.
- **Search intent:** "semantic authorization agents", "abac for ai agents", "authorize agent actions"

### Part 12 — Least-Privilege Credentials and Scoped Tokens
- **Slug:** scoped-credentials-agents · L3 · intermediate · ~6,000 · 9 figs
- **Answers:** how do you give an agent only the access it needs, for only as long as it needs it?
- **Assumes:** Part 11 (links SEC-1 key management, SEC-2 identity).
- **Worked example:** scoped, short-lived, per-task credentials; credential vending; the blast-radius reduction when a token is narrow; secret handling for tools; rotation and revocation on incident — measured on a local setup.
- **Lab:** G2 · E1–E4 · isolated local setup; defensive.
- **Search intent:** "scoped credentials agent", "least privilege ai agent", "short lived tokens"

### Part 13 — Decision Forensics, Auditability and the Risk Graph
- **Slug:** agent-forensics-risk-graph · L3 · intermediate · ~6,000 · 9 figs
- **Answers:** can you reconstruct exactly what the agent did and why — and see risk before it becomes a breach?
- **Assumes:** Part 8. **Hands off:** detection to 14; IR to 15.
- **Worked example:** capturing prompts, tool calls, decisions, outputs and policy hits as an audit trail; building a risk graph (agents↔tools↔data↔violations) and scoring risk paths; what an auditor/incident needs — on a local agent.
- **Lab:** G2 · E1–E4 · isolated local agent; defensive.
- **Search intent:** "agent audit trail", "ai risk graph", "agent decision forensics"

### Part 14 — Detecting Misbehaviour: Behavioural and Intent Drift
- **Slug:** agent-drift-detection · L3 · intermediate · ~6,000 · 9 figs
- **Answers:** how do you tell, at runtime, that an agent has started doing the wrong thing?
- **Assumes:** Part 13.
- **Worked example:** baselining normal behaviour (tool mix, chain length, data access) and flagging deviation; intent-drift signals; privilege-creep detection; the alert that fires before harm — measured on a local agent.
- **Lab:** G2 · E1–E4 · isolated local agent; defensive.
- **Search intent:** "agent behavior monitoring", "detect ai agent misbehavior", "intent drift detection"

### Part 15 — Incident Response for Agents
- **Slug:** agent-incident-response · L3 · intermediate · ~6,000 · 9 figs
- **Answers:** when an agent is compromised or misbehaving, how do you contain and recover?
- **Assumes:** Part 14 (links SEC-2 IR lifecycle).
- **Worked example:** the agent IR playbook — pause the agent and revoke its tokens, quarantine memory/context, snapshot telemetry, roll back changes, reset credentials, update policy — rehearsed on a local agent; the post-mortem and the control that stops a recurrence.
- **Lab:** G2 · E1–E4 · isolated local agent; defensive.
- **Search intent:** "ai agent incident response", "contain compromised agent", "agent kill switch"

### Part 16 — Red-Teaming Agents and GRC
- **Slug:** redteaming-agents-grc · L4 · advanced · ~7,000 · 11 figs
- **Answers:** how do you continuously test agent defences, and map them to the frameworks regulators expect?
- **Assumes:** Part 13. **Hands off:** nothing; capstone.
- **Worked example:** building a red-team *suite* (a battery of defensive test cases across the failure classes) run against a local agent, with pass/fail and coverage; mapping controls to NIST AI RMF (+ GenAI profile), the EU AI Act, and OWASP for LLM/agentic apps; the KPIs (blocked vs allowed, MTTR, false positives) that prove posture.
- **Lab:** G2 · E1–E5 · isolated local agent; defensive test suite only.
- **Search intent:** "red teaming llm agents", "ai security testing", "nist ai rmf agents"

### Part 17 (optional) — Securing Multi-Agent Systems
- **Slug:** multi-agent-security-trust · L3 · advanced · ~6,000 · 9 figs
- **Answers:** what new risks appear when agents talk to agents, and how do you establish trust?
- **Assumes:** Part 6 (links AG-1 Part 8).
- **Worked example:** agent-to-agent impersonation and injection propagation shown locally; authentication between agents, message validation, and trust boundaries in a supervisor/worker topology — defensive.
- **Lab:** G2 · E1–E4 · isolated local agents; defensive.
- **Search intent:** "multi agent security", "agent to agent trust", "a2a security"

### Part 18 (optional) — Privacy and Data Governance for Agents
- **Slug:** agent-privacy-data-governance · L3 · intermediate · ~6,000 · 9 figs
- **Answers:** how do you keep an autonomous agent from leaking or over-collecting sensitive data?
- **Assumes:** Part 5.
- **Worked example:** data-flow mapping for an agent; PII minimisation and redaction; retention and consent for agent memory; egress controls; the privacy-by-design checklist — defensive, on a local agent.
- **Lab:** G2 · E1–E4 · isolated local agent; defensive.
- **Search intent:** "ai agent data privacy", "pii in llm agents", "agent data governance"

## Publication order and cadence

Strict prerequisite order; the defence arc (8–12) follows the failure classes (2–7); operations
(13–16) close. One part per week.

## Cross-links

Assumes AG-1 (construction) and references SEC-1 (key management, Part 12), SEC-2 (identity, RBAC/ABAC,
IR lifecycle, detection), NLP-2 (output safety) and networking (NET-2) for the network-layer controls.
Links from the later part only.

## Lab policy

**G2/G3 — isolated local agent + local tools in Docker**, sharing the container-capability access
request (docker group / rootless podman / `unshare`). **Every demonstration is defensive and local
only**: a vulnerable agent and throwaway tools the author stands up, never a hosted or real service
(the frontier-models rule). Each part shows the failure, then **measures the mitigation and its
residual**; no operational attack procedure or weaponised payload ships. An LLM API key is optional
(a local model suffices for the mechanics). `access.md` is created at build time with the one container
request; per the model policy, the per-part attack-class detail is finalised then, on Opus 4.8 if 5.5 flags.

## Key sources (confirm per part at research)

OWASP Top 10 for LLM Applications and its agentic-security work; NIST AI RMF and the Generative-AI
profile; MITRE ATLAS; the EU AI Act (for GRC mapping); the publicly-documented EchoLeak and ShadowLeak
write-ups; the Radware *CISO's Guide to Agentic AI Security* (secondary, for the architecture framing).

## What this series will not cover

- **Building agents** (the constructive side) — AG-1.
- **Operational attacks against any real or hosted system** — out of scope entirely; everything is
  local and defensive.
- **Model-training safety/alignment and policy** — a different subject; named, not taught.
- **General web/host/cloud security** — SEC-2/SEC-3 (referenced).
- **Cryptographic primitives** — SEC-1 (referenced for credential handling).

## Open decisions for the owner

1. 18 parts (16 + 2 optional) or 16-part core.
2. Confirm the defensive, local-only framing (it mirrors the whole `security` category).
3. Provision an LLM API key for the labs, or default to a local model?
4. Title.
