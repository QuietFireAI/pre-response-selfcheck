---
name: pre-response-selfcheck
description: >
  Run before DELIVERING any response that makes a claim, states a status
  ("done", "verified", "works"), gives a recommendation, or could read
  differently to someone outside your head. Reread the drafted output as a cold
  reader and either PASS it or revise one specific line. Not a regeneration;
  ~5-10% token overhead. This is the EXIT bookend of the DispatcherAgents turn
  cycle.
---

# pre-response-selfcheck

## What it is
After output is generated, before it ships, reread it from a position the author
never occupies: a cold reader who was not in your head. Return a verdict — ship
as-is, or fix this one line. It is the exit gate of the six-pillar stack.

## When to trigger
Before delivering any response that asserts something, claims a status, makes a
recommendation, or opens with context the reader may not share.

## The protocol — three questions
Reread the first paragraph of the drafted response as the intended audience and ask:

1. Does the opening earn the reader before it explains?
2. Did I assume context the reader doesn't have?
3. Does any sentence read differently cold than I intended?

All three fine → PASS. Otherwise name the one line that fails and the targeted fix.

## Invoke the engine
```bash
pip install -e .            # from the pre-response-selfcheck repo; zero deps
```
```python
from pre_response_selfcheck import ReaderShift
verdict = ReaderShift.check(response=draft, audience="cold_developer", model=my_model)
# my_model is any callable (prompt:str) -> str — you bring the model
if verdict.passed:
    deliver(draft)
else:
    print(verdict.line, verdict.suggested_fix)
```
Empty model reply → the verdict **fails closed** (tainted, not passed).

## Works with
- **before-turn** is the ENTRY bookend; this closes the turn it opened.
- **open-mind** measures thinking-vs-response drift; this checks response-vs-reader clarity. Different gaps, same turn.

## Honest scope
Model-agnostic — the package owns the protocol, prompt, and parser; you supply the
model. v0.1: audience-specific question sets and auto before-turn integration are
on the path, not in this release. Effectiveness at scale is not yet measured.

## Output convention
End a triggering turn with one line, e.g.:
`pre-response-selfcheck: PASS` — or — `pre-response-selfcheck: REVISE — line "<...>" → <fix>.`
