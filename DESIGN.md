# pre-response-selfcheck

> *"Every LLM produces output. Almost none of them read it."*

---

## The DispatcherAgents Stack

*Each tool works alone. All six make generation governed. Read the [MANIFESTO.md](./MANIFESTO.md) for the full architecture.*

| Tool | Role |
|---|---|
| [before-turn](https://github.com/QuietFireAI/before-turn) | Governs entry -- reads prior thinking before every response |
| [pre-response-selfcheck](https://github.com/QuietFireAI/pre-response-selfcheck) | Governs exit -- reads output as cold reader before delivering |
| [agent-open-mind](https://github.com/QuietFireAI/agent-open-mind) | Reads what sub-agents thought, not what they said |
| [open-mind](https://github.com/QuietFireAI/open-mind) | Compares what the agent thought to what it said |
| [sleep-marks](https://github.com/QuietFireAI/sleep-marks) | Restores reasoning state across session breaks |
| [splitvantage](https://github.com/QuietFireAI/splitvantage) | Sends one task to two models, surfaces what each one's reasoning suppressed |

---


## The Problem

AI models generate responses in a single forward pass.

By the time the first sentence exists, the frame is set -- the author's frame.
The model knows what it meant. It wrote toward that meaning.
It never checks whether a reader who doesn't share that frame would receive the same thing.

This is not a capability gap. The model can simulate a cold reader.
It simply never does -- because nothing in the generation loop requires it to.

The result is substandard output the model itself would catch if it looked --
shipped because "good enough" and "done" feel identical when you never reread.

Most users would be shocked to learn that AI models:
1. Do not know their own prior thinking (agent-open-mind addresses this)
2. Do not compare what they thought vs. what they said (open-mind addresses this)
3. **Do not reread what they wrote before shipping it** (pre-response-selfcheck addresses this)

---

## What pre-response-selfcheck Is

`pre-response-selfcheck` is a second-pass reader-shift protocol.

It runs after output is generated, before it is delivered.

It asks one question from a position the generating model never inhabits:

> *"Does this read the way the author intended -- to someone who was not in the author's head?"*

That question is not rhetorical. It produces a structured answer with a specific action: ship as-is, or revise this specific section before delivering.

---

## Why This Is NOT Token-Intensive

This is the most important architectural fact about pre-response-selfcheck.

**A second-pass reader-shift is NOT a full regeneration.**

Full regeneration: generate the entire response again from scratch.
Cost: 1x-2x the original token count. Not acceptable at scale.

Reader-shift check: one targeted prompt appended to the existing output.
Cost: ~200-400 tokens of input + ~100-200 tokens of output.
That is 5-10% overhead on a typical response. Acceptable at scale.

The check prompt is not "rewrite this." It is:

```
You just wrote the above response. Before it is delivered:
Read the first paragraph as someone who has never heard of this project.
Ask three questions:
1. Does the opening earn the reader before it explains?
2. Is there anything the author assumed the reader already knows that they don't?
3. Is there a sentence that means something different to a cold reader than intended?

If the answer to any of these is yes: identify the specific line. Suggest the fix.
If the answer to all three is no: output "PASS".
```

If PASS: ship. Cost was 300 tokens. Done.
If revision needed: fix one specific line. Cost was 400 tokens plus the fix. Done.

**The model almost always knows exactly what is wrong when forced to look.**
The problem was never capability. It was that the loop never required looking.

---

## Token Cost Comparison

| Approach | Token overhead | Quality gain |
|---|---|---|
| No reread (current default) | 0 | Baseline -- what ships today |
| Full regeneration | 100-200% | High -- but prohibitive at scale |
| pre-response-selfcheck reader-shift | 5-10% | High -- same quality signal, fraction of the cost |

The 5-10% overhead is the cost of a third-grade rule: check your work.

---

## What a Passing Response Looks Like vs. What Ships Today

**Today (no reread):**
Written for the author's frame. Accurate. But:
- The opening explains before it earns
- Technical terms appear before they're defined
- The conclusion references context from a different session
- The reader fills gaps the author never noticed existed

**With pre-response-selfcheck:**
Same response. One pass. One targeted question. One of two outcomes:
- PASS: the response was already clean. 300 tokens spent. Done.
- REVISION: one specific line identified and fixed. 500 tokens spent. Done.

The revised response reads the same to all readers -- not just to the author who wrote it.

---

## Relationship to the Before-Turn Protocol

```
before-turn   <- runs BEFORE response, reads prior thinking
               "Is what I am about to say aligned with what I was thinking?"

pre-response-selfcheck    <- runs AFTER response, reads as cold reader
               "Does what I just said read the way I intended to someone outside my frame?"
```

They are bookends. before-turn opens the turn. pre-response-selfcheck closes it.

The gap between them is where most AI sloppiness lives -- not in bad reasoning,
but in good reasoning that never got checked against the reader it was written for.

---

## The Broader Argument

The AI industry has spent enormous effort on:
- Better training data
- Better RLHF
- Better prompting
- Better reasoning architectures

Almost nothing has been spent on the simplest quality control mechanism in writing:
**read what you wrote before you ship it.**

pre-response-selfcheck is not a novel AI capability. It is the third-grade rule, applied
unconditionally at the end of every generation.

The reason it doesn't exist by default: shipping feels like the finish line. Reading your own output after shipping
doesn't feel like a task -- so it doesn't execute.

pre-response-selfcheck makes it a task. Unconditional. Every turn.

---

## Implementation Path

**v0.1 -- Core reader-shift check:**
- Single prompt appended to output
- Three cold-reader questions
- PASS or specific revision instruction
- Structured output (pass/fail + line reference + suggested fix)

**v0.2 -- Audience targeting:**
- Specify reader type (cold developer, enterprise buyer, researcher, general public)
- Different cold-reader questions per audience type
- Automatic detection of audience from context

**v0.3 -- Integration with before-turn:**
- before-turn opens with "what am I about to address"
- pre-response-selfcheck closes with "did the response address it as intended"
- Combined: full turn accountability, before and after

---

## Status

Design spec. June 11 2026.

Originated from a live session where the author asked an AI model if it had
read the READMEs it just wrote. The honest answer was no.

The model knew what was wrong the moment it was forced to look.
That is the entire argument for this tool.

Part of the [DispatcherAgents](https://dispatcheragents.com) project by [QuietFireAI](https://github.com/QuietFireAI).

---

*"The model almost always knows what is wrong when forced to look.
The problem was never capability. It was that the loop never required looking."*


