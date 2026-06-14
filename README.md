# pre-response-selfcheck

> *"Every LLM produces output. Almost none of them read it."*

---

## The DispatcherAgents Stack

*Six pillars. Each works alone; together they give an agent end-to-end self-consistency — less drift, fewer tokens, an honest record on every turn. Read the [MANIFESTO.md](./MANIFESTO.md) for the full architecture.*

| Tool | Role |
|---|---|
| [before-turn](https://github.com/QuietFireAI/before-turn) | Governs entry — reads prior thinking before every response |
| [pre-response-selfcheck](https://github.com/QuietFireAI/pre-response-selfcheck) | Governs exit — reads output as a cold reader before delivering |
| [agent-open-mind](https://github.com/QuietFireAI/agent-open-mind) | Reads what sub-agents thought, not what they said |
| [open-mind](https://github.com/QuietFireAI/open-mind) | Compares what the agent thought to what it said |
| [sleep-marks](https://github.com/QuietFireAI/sleep-marks) | Restores reasoning state across session breaks |
| [splitvantage](https://github.com/QuietFireAI/splitvantage) | Sends one task to two models, surfaces what each one's reasoning suppressed |

---

## The Problem

AI models generate responses in a single forward pass.

By the time the first sentence exists, the frame is set — the author's frame. The model knows what it meant; it wrote toward that meaning. It never checks whether a reader who doesn't share that frame would receive the same thing.

This is not a capability gap. The model can simulate a cold reader. It simply never does, because nothing in the generation loop requires it to.

The result is substandard output the model itself would catch if it looked — shipped because "good enough" and "done" feel identical when you never reread.

Most people would be surprised to learn that AI models:

1. Do not know their own prior thinking (agent-open-mind addresses this)
2. Do not compare what they thought to what they said (open-mind addresses this)
3. **Do not reread what they wrote before shipping it** (pre-response-selfcheck addresses this)

---

## What It Is

`pre-response-selfcheck` is a second-pass reader-shift protocol. It runs after output is generated, before it is delivered, and asks one question from a position the generating model never inhabits:

> *"Does this read the way the author intended — to someone who was not in the author's head?"*

That question is not rhetorical. It returns a structured verdict with a specific action: ship as-is, or revise this one line before delivering.

---

## Why This Is Not Token-Intensive

A reader-shift is **not** a regeneration.

- Full regeneration re-runs the whole response: 100–200% token overhead. Prohibitive at scale.
- A reader-shift appends one targeted prompt to the existing output: roughly 200–400 input tokens and 100–200 output tokens — about **5–10% overhead** on a typical response.

The check does not say "rewrite this." It asks the model to reread its first paragraph as a cold reader and answer three questions; if all three are fine it returns `PASS`, otherwise it names the one line that fails and suggests the fix. The model almost always knows exactly what is wrong the moment it is forced to look. The problem was never capability — it was that the loop never required looking.

---

## Installation

Install from source (a PyPI release is planned):

```bash
git clone https://github.com/QuietFireAI/pre-response-selfcheck.git
cd pre-response-selfcheck
pip install -e .
```

**Zero required dependencies.** Pure Python 3.9+.

---

## Quick Start

`pre-response-selfcheck` owns the protocol — the prompt, the output contract, and the parser. **You bring the model.** A model is any callable that takes a prompt string and returns the model's text. That single integration point is what keeps the package dependency-free and platform-neutral.

```python
from pre_response_selfcheck import ReaderShift

# A model is any callable: (prompt: str) -> str.
# Wrap whatever you already use — OpenAI, Anthropic, a local model, anything.
def my_model(prompt: str) -> str:
    return call_your_llm(prompt)

verdict = ReaderShift.check(
    response="Your model's drafted output goes here.",
    audience="cold_developer",   # who is this actually for?
    model=my_model,
)

if verdict.passed:
    deliver(response)            # reread clean, ship it
else:
    print(verdict.line)          # the specific sentence that fails a cold reader
    print(verdict.suggested_fix) # the targeted revision -- not a rewrite
```

Reuse one configured checker across many responses:

```python
checker = ReaderShift(model=my_model)
verdict = checker.run(response, audience="enterprise_buyer")
```

---

## API

- **`ReaderShift.check(response, audience="cold_reader", model=...)`** → `Verdict`. Convenience classmethod; pass the model per call.
- **`ReaderShift(model=...).run(response, audience="cold_reader")`** → `Verdict`. Configure the model once, check many responses.
- **`Verdict`** — `passed: bool`, `line: str | None`, `suggested_fix: str | None`, `raw: str` (the model's unparsed reply), `audience: str`, `questions: list[str]`. Truthy when `passed`.
- **`build_prompt(response, audience)`** → the exact prompt string, exposed so the token-overhead claim is auditable rather than asserted.
- **`AUDIENCES`** — built-in personas: `cold_reader`, `cold_developer`, `enterprise_buyer`, `researcher`, `general_public`. An unknown audience falls back to `cold_reader`.

If the model returns an empty reply, the verdict **fails closed** — absence of a verdict is treated as tainted and surfaced for a human, never silently passed. That mirrors the stack-wide rule: missing provenance is flagged, never admitted.

---

## Relationship to before-turn

```
before-turn               runs BEFORE the response, reads prior thinking
                          "Is what I am about to say aligned with what I was thinking?"

pre-response-selfcheck    runs AFTER the response, reads as a cold reader
                          "Does what I just said read the way I intended, to someone outside my frame?"
```

They are bookends. before-turn opens the turn; pre-response-selfcheck closes it. The gap between them is where most AI sloppiness lives — not in bad reasoning, but in good reasoning that never got checked against the reader it was written for.

---

## Status

**v0.1 — implemented and tested. June 2026.**

The core reader-shift check is working code: a dependency-free package with an injectable model, a structured `Verdict`, and a test suite that exercises the PASS path, the revision path, prompt construction, and fail-closed behavior on empty replies. `pip install -e .` and the Quick Start above run as written.

What is **not** yet claimed: audience-specific question sets (v0.2) and automatic before-turn integration (v0.3) are on the path, not in this release. Effectiveness numbers — how often the check changes a response, and whether that improves cold-reader comprehension — are not yet measured at scale and are marked accordingly in [EVIDENCE.md](./EVIDENCE.md). This tool exists because, in a live session, a model was asked whether it had read the READMEs it just wrote, and the honest answer was no. It knew what was wrong the moment it was forced to look. That is the whole argument.

Part of the [DispatcherAgents](https://dispatcheragents.com) project by [QuietFireAI](https://github.com/QuietFireAI).

---

## License

MIT — QuietFireAI / [dispatcheragents.com](https://dispatcheragents.com)

---

*"Every LLM produces output. Almost none of them read it. pre-response-selfcheck makes the model its own first reader."*
