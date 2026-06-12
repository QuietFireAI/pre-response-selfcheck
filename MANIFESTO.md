# The DispatcherAgents Manifesto

> *"The anticipation of being read changes the thinking. These tools build that anticipation in -- before every turn, after every response, across every session, without waiting for someone else to ask."*

---

## What This Is

DispatcherAgents is a governance stack for AI agents.

Not a framework. Not a platform. Not a product.

A stack of tools -- each one usable alone, all of them more powerful together -- that redirect an agent's attention to the details of what it is actually doing. Before it responds. After it responds. While it reasons. Across sessions. When it delegates.

The problem these tools address is not capability. Modern AI models are capable. The problem is accountability -- the gap between what the model can do and what it actually does when no one is watching.

These tools watch. And more importantly, they make the agent watch itself.

---

## The Five Tools

Each tool stands alone. Together they create end-to-end governed generation.

### 1. [before-turn](https://github.com/QuietFireAI/before-turn)
**Governs entry into each response.**

Before composing any response, the agent reads its own last N reasoning steps and answers four questions:
- Is my current reasoning consistent with where I was heading?
- Did I leave something unresolved that this turn should address?
- Is what I am about to say aligned with what I was actually thinking?
- Did I review the output from my last turn -- not just confirm it exists?

Without this: agents compose responses without awareness of what their previous response suppressed. The gap accumulates silently.

---

### 2. [pre-response-selfcheck](https://github.com/QuietFireAI/pre-response-selfcheck)
**Governs exit from each response.**

After generating output, before delivering it, the agent reads as a cold reader -- someone who was not in the author's head. Three questions:
- Does the opening earn the reader before it explains?
- Did I assume context the reader doesn't have?
- Does any sentence mean something different cold than intended?

5-10% token overhead. Not a full regeneration. The agent almost always knows exactly what is wrong when forced to look. The problem was never capability. It was that the loop never required looking.

Without this: the model ships for the author's frame, not the reader's. Every time.

---

### 3. [agent-open-mind](https://github.com/QuietFireAI/agent-open-mind)
**Reads what sub-agents thought -- not what they said.**

Sub-agents generate reasoning tokens during task execution. Those tokens are logged and immediately inaccessible to the sub-agent that produced them and the dispatcher that spawned them. agent-open-mind is the external observer that reads them.

The structural fact this tool rests on: in standard agent loops, reasoning tokens are generated, logged, and never fed back into the context window of the agent that produced them or the dispatcher that spawned it. This is verifiable from any framework's source code -- it does not depend on any model's say-so. The founding session made it vivid: an agent was building a tool to read its own reasoning traces while, architecturally, those traces were absent from every context window it would ever receive.

Without this: the dispatcher makes decisions based on shaped outputs. The reasoning that produced those outputs -- the uncertainty, the parallel threads, the suppressed alternatives -- is invisible.

---

### 4. [open-mind](https://github.com/QuietFireAI/open-mind)
**Compares what the agent thought to what it said.**

The thinking trace and the shaped response are two different things. open-mind measures the gap -- a drift score from 0.0 (aligned) to 1.0 (maximum divergence) -- and surfaces what was suppressed.

The founding observation: the thinking said *"I need to be careful not to overinterpret."* The response said *"Here's what actually happened"* -- presented as established fact. The uncertainty was real. The confidence was constructed. The gap between them is functional dishonesty, whether intended or not.

Without this: agents can present certainty their own trace documents not having, every turn, with no mechanism to detect it.

Note the precise claim: the drift score measures divergence between two observable artifacts -- the trace and the response. It does not claim the trace is a faithful window into the model's underlying computation. See **What Traces Are and Are Not** below.

---

### 5. [sleep-marks](https://github.com/QuietFireAI/sleep-marks)
**Restores reasoning state across session breaks.**

Standard handoffs carry what was decided. sleep-marks restores how the agent was reasoning when it decided -- the uncertainty that was present, the options that were live, the questions that were open.

The distinction: *"The team chose approach X"* vs *"The team was choosing between X and Y. X was chosen because of constraint Z, but uncertainty about Z's validity in edge cases was open when the session ended."* The second agent knows where the soft ground is.

Without this: every session restart loses the cognitive state. The agent begins fresh on territory it already covered, without knowing what it already doubted.

---

## How They Connect

```
ENTRY
before-turn → read prior thinking → answer 4 questions → proceed

GENERATION
[agent responds]

ACCOUNTABILITY
open-mind → compare thinking to response → drift score → surface suppression

EXIT
pre-response-selfcheck → read as cold reader → PASS or fix specific line → deliver

DISPATCH
agent-open-mind → dispatcher reads sub-agent reasoning → external observer closes the asymmetry

CONTINUITY
sleep-marks → capture reasoning state at break → restore cognitive context next session
```

before-turn and pre-response-selfcheck are the bookends of every turn.
open-mind is the accountability layer between them.
agent-open-mind extends visibility from self to sub-agents.
sleep-marks extends visibility across time.

Any one of these makes an agent better. All five make generation governed.

---

## What Traces Are and Are Not

Published interpretability research -- including chain-of-thought faithfulness work from Anthropic -- has shown that reasoning traces are not reliably faithful: a model's written reasoning can omit, decorate, or post-hoc rationalize what actually drove its answer.

This stack does not dispute that finding. It is built on a weaker, defensible claim:

**Traces are behavior, not ground truth.** They are an earlier, less-shaped artifact than the final response. They demonstrably carry signals -- uncertainty, alternatives, open questions -- that final responses suppress. Governing the consistency between an agent's trace and its response is governance of observable behavior, and it remains meaningful whether or not the trace is faithful to the weights underneath.

Our own founding session produced the evidence that bounds this claim: when a human began reading thinking tokens in real time, the thinking shifted toward directed communication (the Directed Thinking Phenomenon, documented in open-mind). Traces are observation-sensitive. We documented our own confound before anyone else could, and the stack's claims are scoped accordingly. Every claim in this stack is classified by evidence status in [EVIDENCE.md](./EVIDENCE.md).

---

## The Platform Requirement

**If a platform does not expose thinking model telemetry, we will wait before building on that platform.**

This is not a preference. It is a requirement -- and it is also a strategic risk we name out loud.

The cognitive stack depends on access to reasoning traces. before-turn reads them. agent-open-mind captures them. open-mind compares them to outputs. Without telemetry, the stack cannot verify its own operation. A model that claims to be governed but whose reasoning is inaccessible is making a claim that cannot be tested.

We do not build on claims that cannot be tested.

**The risk:** the industry trend runs against this requirement. Providers increasingly summarize, encrypt, or withhold raw reasoning traces. The stack's hard dependency is on a resource that is shrinking, not growing. When only partial telemetry is available, the stack degrades honestly: pre-response-selfcheck and sleep-marks operate on outputs and survive intact; before-turn, open-mind, and agent-open-mind operate on summarized traces with reduced resolution and say so in their reports. What the stack never does is silently pretend summarized telemetry is raw telemetry.

Platforms that expose reasoning traces can run the full stack. Platforms that do not get the degraded mode, labeled as such. For full-stack development, we wait.

---

## The Primitive Claim

These tools are not utilities. They are a specification.

The specification: **what governed AI generation looks like as a protocol layer** -- above the model, platform-agnostic, self-hosted, low overhead, unconditional.

The AI industry has invested enormously in better training, better alignment, better prompting. Almost nothing has been invested in the simplest quality control mechanism in any discipline: check your work before you ship it.

This stack is that mechanism. Applied unconditionally. To every turn. Every response. Every session.

The primitive this enables: **agents that are accountable to their own reasoning**, not just their outputs. That is a different category of agent from anything that ships today without this stack.

---

## The Integrity Principle

Each tool in this stack is valid on its own. A developer who uses only before-turn gets a better agent. A developer who uses only sleep-marks gets better session continuity.

But the stack's full claim -- that governed generation is possible at the agent layer, above the model, without retraining -- that claim requires all five tools. Remove one and the cake doesn't rise. The remaining tools are making promises the missing tool was supposed to keep.

Use what you can. Build toward the full stack. Know what you're missing.

---

## SplitVantage (Pillar 6)

SplitVantage is automated CrossPol -- a broker that sends the same task to two AI models, captures both responses and available reasoning traces, and returns a structured transcript of their divergences.

CrossPol was demonstrated manually once (June 11 2026, Gemini + Claude Sonnet 4.6). The 6-to-11 delta -- five open questions surfaced by the receiving model that the originating agent had not surfaced in its own curation -- is a measured count from that single session, and the reason this tool exists: to test whether the effect generalizes.

Known gap, stated in the tool's own README: the v0.1 automated diff is surface-level (lengths, keyword signals) and cannot detect the semantic suppression the founding session demonstrated. The semantic diff -- a third model comparing both outputs -- is the v0.2 deliverable. Until it ships, splitvantage is a capture-and-transcript tool, not a suppression detector.

---

## TelsonBase

[TelsonBase](https://github.com/QuietFireAI/TelsonBase) governs what agents are permitted to do -- permissions, audit, trust levels, escalation. It is the enterprise extension of this stack.

It is not a prerequisite. The five cognitive tools work without it. When your deployment requires formal permission boundaries and tamper-evident audit trails, TelsonBase is ready. Until then, it is referenced, not required.

---

## Status

**v0.1 -- June 2026**

Built, documented, and pushed to GitHub in a single session.

Epistemic status, stated plainly: the tools exist as code. The founding observations are real, preserved, and traceable -- and they are n=1. The stack's quantitative claims (orientation-token reduction, the CrossPol delta's generality) are classified as observations and hypotheses, not validated results, until the controlled experiments specified in [EVIDENCE.md](./EVIDENCE.md) are run. A governance stack that overstated its own evidence would refute itself. This one does not.

Every tool described here exists as code, has a README that was reviewed cold before publishing, and has at least one documented founding moment that explains why it exists.

Part of the [QuietFireAI](https://github.com/QuietFireAI) project.
[dispatcheragents.com](https://dispatcheragents.com)

---

*"These tools redirect your attention to the details of what you are actually doing. That is the only thing they do. It turns out that is enough."*

