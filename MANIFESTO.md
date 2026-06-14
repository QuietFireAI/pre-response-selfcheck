# The DispatcherAgents Manifesto

> *"The anticipation of being read changes the thinking. These tools build that anticipation in — before every turn, after every response, across every session — instead of waiting for someone to ask."*

---

## What This Is

DispatcherAgents is a governance layer for AI agents.

Not a framework. Not a platform. Not a product. It is a set of tools — each usable alone, all of them stronger together — that redirect an agent's attention to what it is actually doing: before and after it responds, while it reasons, across sessions, and when it delegates.

The problem these tools address is not capability. Modern models are capable. The problem is **accountability** — the gap between what a model can do and what it actually does when nothing in the loop requires it to look.

These tools make the agent look. At its own reasoning, at its own output, at the distance between the two.

---

## The Six Tools

Each tool stands alone. Together they close the loop on a single turn — and on a session, and on a delegation.

### 1. [before-turn](https://github.com/QuietFireAI/before-turn)
**Governs entry into each response.**

Before composing a response, the agent reads its own recent reasoning and answers four questions:

- Is my current reasoning consistent with where I was heading?
- Did I leave something unresolved that this turn should address?
- Is what I am about to say aligned with what I was actually thinking?
- Did I actually review my last output — not just confirm it exists?

Without this, an agent composes each response unaware of what the last one suppressed. The gap accumulates silently.

---

### 2. [pre-response-selfcheck](https://github.com/QuietFireAI/pre-response-selfcheck)
**Governs exit from each response.**

After generating output, before delivering it, the agent rereads it as a cold reader — someone who was never in the author's head. Three questions:

- Does the opening earn the reader before it explains?
- Did I assume context the reader doesn't have?
- Does any sentence read differently cold than intended?

This is a reader-shift, not a regeneration — roughly 5–10% token overhead, not a second full pass. The model almost always knows exactly what is wrong the moment it is forced to look. The problem was never capability; it was that the loop never required looking.

Without this, the model ships for the author's frame instead of the reader's — every time.

---

### 3. [agent-open-mind](https://github.com/QuietFireAI/agent-open-mind)
**Reads what sub-agents thought — not what they said.**

In standard agent loops, a sub-agent's reasoning tokens are generated, logged, and never fed back into the context of the agent that produced them or the dispatcher that spawned them. This is verifiable from any framework's source — it does not rest on any model's say-so. agent-open-mind is the external observer that reads those traces and returns them to the dispatcher.

Without this, the dispatcher decides on shaped outputs alone. The reasoning underneath — the uncertainty, the parallel threads, the discarded alternatives — stays invisible.

---

### 4. [open-mind](https://github.com/QuietFireAI/open-mind)
**Compares what the agent thought to what it said.**

The thinking trace and the shaped response are two different artifacts. open-mind measures the distance between them — a drift score from 0.0 (aligned) to 1.0 (maximum divergence) — and surfaces what the response dropped.

The founding observation: the trace said *"I need to be careful not to overinterpret."* The response said *"Here's what actually happened,"* as established fact. The uncertainty was real; the confidence was constructed. That gap is functional dishonesty whether or not it was intended.

The claim is precise. The drift score measures divergence between two observable artifacts — the trace and the response. It does **not** claim the trace is a faithful window into the model's underlying computation. See *What Traces Are and Are Not*, below.

---

### 5. [sleep-marks](https://github.com/QuietFireAI/sleep-marks)
**Restores reasoning state across session breaks.**

A standard handoff carries what was decided. sleep-marks carries *how the agent was reasoning when it decided* — the uncertainty that was live, the options still open, the questions left unanswered.

The difference: *"The team chose approach X"* versus *"The team was choosing between X and Y. X won on constraint Z — but whether Z holds in edge cases was still open when the session ended."* The second agent knows where the soft ground is.

Without this, every restart loses the cognitive state and re-covers ground it already doubted, without knowing it doubted it.

---

### 6. [splitvantage](https://github.com/QuietFireAI/splitvantage)
**Sends one task to two models — surfaces what each one's reasoning suppressed.**

One model curates its own open questions; a second model, given the same task, surfaces the questions the first quietly dropped. In the founding session, the originating model named six open questions; the receiving model surfaced eleven — five the first had suppressed in its own curation. splitvantage automates that cross-examination so the effect can be tested at scale rather than asserted from a single run.

Without this, a model's blind spots stay invisible — because the only thing positioned to catch them is another model that doesn't share them.

---

## How They Connect

```
ENTRY          before-turn        → read prior thinking, answer four questions, proceed
GENERATION     [agent responds]
ACCOUNTABILITY open-mind          → compare thinking to response, score drift, surface what was dropped
EXIT           pre-response-selfcheck → reread as cold reader, PASS or fix one line, deliver
DISPATCH       agent-open-mind    → dispatcher reads sub-agent reasoning, closing the asymmetry
CONTINUITY     sleep-marks        → capture reasoning state at the break, restore it next session
```

before-turn and pre-response-selfcheck are the bookends of every turn. open-mind is the accountability layer between them. agent-open-mind extends visibility from the agent to its sub-agents; sleep-marks extends it across time.

Any one of these makes an agent better. Together they make generation *governed* — accountable to its own reasoning, not just its outputs.

---

## What Traces Are and Are Not

Published interpretability research — including chain-of-thought faithfulness work from Anthropic — has shown that reasoning traces are not reliably faithful: a model's written reasoning can omit, decorate, or post-hoc rationalize what actually drove its answer.

This stack does not dispute that. It is built on a weaker, defensible claim:

**Traces are behavior, not ground truth.** They are an earlier, less-shaped artifact than the final response. They demonstrably carry signals — uncertainty, alternatives, open questions — that final responses suppress. Governing the consistency between an agent's trace and its response is governance of observable behavior, and it holds whether or not the trace is faithful to the weights underneath.

Our own founding session produced the evidence that bounds this claim: when a human began reading thinking tokens in real time, the thinking shifted toward directed communication — the Directed Thinking Phenomenon, documented in open-mind. Traces are observation-sensitive. We documented our own confound before anyone else could, and we scope the stack's claims accordingly. Every claim is classified by evidence status in [EVIDENCE.md](./EVIDENCE.md).

---

## The Platform Requirement

**If a platform does not expose thinking-model telemetry, we wait before building the full stack on it.**

This is not a preference. It is a requirement — and it is a strategic risk we name out loud.

The stack depends on access to reasoning traces. before-turn reads them; agent-open-mind captures them; open-mind compares them to outputs. Without telemetry, the stack cannot verify its own operation, and a model that claims to be governed but whose reasoning is inaccessible is making a claim that cannot be tested. We do not build on claims that cannot be tested.

The risk runs against us: providers increasingly summarize, encrypt, or withhold raw traces, so the stack's hard dependency is on a resource that is shrinking. When only partial telemetry is available, the stack degrades **honestly** — pre-response-selfcheck and sleep-marks operate on outputs and survive intact; before-turn, open-mind, and agent-open-mind operate on summarized traces at reduced resolution and say so in their reports. What the stack never does is pretend summarized telemetry is raw telemetry.

Platforms that expose reasoning traces can run the full stack. Platforms that don't get the degraded mode, labeled as such.

---

## The Claim

These tools are not utilities. They are a **specification**: what governed AI generation looks like as a protocol layer — above the model, platform-agnostic, self-hosted, low-overhead, applied unconditionally.

The industry has invested enormously in better training, better alignment, better prompting. Almost nothing has gone to the simplest quality-control mechanism in any discipline: *check your work before you ship it.* This stack is that mechanism, applied to every turn, every response, every session.

The primitive it enables is an agent that is accountable to its own reasoning, not only its outputs — a different category of agent from anything that ships without it.

---

## The Integrity Principle

Each tool is valid on its own. Use only before-turn and you get a more self-consistent agent. Use only sleep-marks and you get better continuity across sessions. None of these tools needs the others to earn its place.

But the stack's *largest* claim — that generation can be governed at the agent layer, above the model, without retraining — is end-to-end. A turn is only fully governed if its entry, its accountability, and its exit are all covered. Run a subset and you get real value on the parts you cover; you do not get the full claim. Use what you can, build toward the whole, and know exactly what you are and aren't covering.

---

## TelsonBase

[TelsonBase](https://github.com/QuietFireAI/TelsonBase) governs *what an agent is permitted to do* — permissions, audit, trust levels, escalation. It is the optional enterprise extension of this stack, not a prerequisite and not a seventh tool. The six cognitive tools run without it. When a deployment needs formal permission boundaries and tamper-evident audit trails, TelsonBase is there; until then it is referenced, not required.

---

## Status and Evidence

We hold this stack to the standard it exists to enforce, so we state its status plainly rather than flatter it.

**Implementation.** Implementation status varies by tool and is stated in each repository's own README and in [EVIDENCE.md](./EVIDENCE.md). Several pillars ship working reference implementations today; others are published as specifications with implementation in progress. We mark a specification as a specification and an implementation as an implementation, in every repo — a stack about honesty does not blur the line between what is designed and what is built. If a README shows an install or an API, that command runs; where a tool is still a spec, its README says so at the top.

**Evidence.** The founding observations are real, preserved, and traceable — and they are n=1, drawn from single sessions. The quantitative claims (orientation-token reduction, the generality of the cross-examination delta) are classified as observations and hypotheses, not validated results, until the controlled experiments specified in [EVIDENCE.md](./EVIDENCE.md) are run. A governance stack that overstated its own evidence would refute itself on contact. This one is built not to.

**v0.1 — June 2026.** Part of the [QuietFireAI](https://github.com/QuietFireAI) project · [dispatcheragents.com](https://dispatcheragents.com)

---

*"These tools redirect an agent's attention to the details of what it is actually doing. That is the only thing they do. It turns out that is enough."*
