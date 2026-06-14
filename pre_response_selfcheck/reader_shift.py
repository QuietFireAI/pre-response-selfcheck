"""
reader_shift.py — the core of pre-response-selfcheck.

A reader-shift is a second pass over an already-generated response, read from a
position the generating model never inhabits: a cold reader who was not in the
author's head. It is NOT a regeneration. It produces a structured verdict —
ship as-is, or revise one specific line — at roughly 5-10% token overhead.

Design constraints (matching the README and MANIFESTO):
  * Zero required dependencies. Pure Python 3.9+.
  * Model-agnostic. You bring the model; this library owns the protocol:
    the prompt, the contract, and the parser. That is what keeps it zero-dep
    and platform-neutral.

The model contract
------------------
`check()` sends the model a prompt that ends with an explicit output contract.
The model must reply in ONE of two forms:

    PASS

or:

    REVISE
    LINE: <the specific sentence that fails a cold reader>
    FIX: <the targeted revision — not a rewrite>

Anything whose first non-empty line is "PASS" (case-insensitive) is a pass.
Otherwise the LINE:/FIX: fields are parsed out. The raw model text is always
preserved on the verdict so nothing is hidden behind the parser.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional

# A model is any callable that takes a prompt string and returns the model's
# raw text response. This is the entire integration surface.
Model = Callable[[str], str]

# v0.1 audience personas. Selecting an audience only changes the cold-reader
# persona phrase in the prompt; the three questions are constant. v0.2 in the
# design path expands these into audience-specific question sets.
AUDIENCES = {
    "cold_reader": "someone who has never heard of this project",
    "cold_developer": "a developer seeing this code or API for the first time",
    "enterprise_buyer": "an enterprise buyer evaluating this with no prior context",
    "researcher": "a researcher reading this cold, who will check every claim",
    "general_public": "a general reader with no background in the subject",
}

THREE_QUESTIONS = (
    "Does the opening earn the reader before it explains?",
    "Is there anything the author assumed the reader already knows that they don't?",
    "Is there a sentence that means something different to a cold reader than intended?",
)

_OUTPUT_CONTRACT = (
    "If the answer to all three is no, output exactly:\n"
    "PASS\n\n"
    "If the answer to any is yes, output exactly:\n"
    "REVISE\n"
    "LINE: <the specific sentence that fails the cold reader>\n"
    "FIX: <the targeted revision -- not a rewrite>"
)


@dataclass
class Verdict:
    """The structured result of a reader-shift check."""

    passed: bool
    line: Optional[str] = None
    suggested_fix: Optional[str] = None
    raw: str = ""
    audience: str = "cold_reader"
    questions: List[str] = field(default_factory=lambda: list(THREE_QUESTIONS))

    def __bool__(self) -> bool:  # `if verdict:` is True when the response passed
        return self.passed

    def __str__(self) -> str:
        if self.passed:
            return "PASS"
        return f"REVISE\nLINE: {self.line}\nFIX: {self.suggested_fix}"


def build_prompt(response: str, audience: str = "cold_reader") -> str:
    """Construct the reader-shift prompt for a given response and audience.

    Exposed (not private) so callers can inspect or log the exact prompt, and
    so the token-overhead claim is auditable rather than asserted.
    """
    persona = AUDIENCES.get(audience, AUDIENCES["cold_reader"])
    q = "\n".join(f"{i}. {text}" for i, text in enumerate(THREE_QUESTIONS, 1))
    return (
        "You just wrote the response below. Before it is delivered, reread the "
        f"first paragraph as {persona}.\n\n"
        "Ask three questions:\n"
        f"{q}\n\n"
        f"{_OUTPUT_CONTRACT}\n\n"
        "--- RESPONSE ---\n"
        f"{response}\n"
        "--- END RESPONSE ---"
    )


def parse_verdict(raw: str, audience: str = "cold_reader") -> Verdict:
    """Parse a model's raw reply into a Verdict, per the output contract."""
    text = (raw or "").strip()
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    if not lines:
        # Empty reply is not a pass. Absence of a verdict is treated as tainted,
        # consistent with the stack's "absent provenance = flag, never admit"
        # principle: fail closed and surface it for a human.
        return Verdict(
            passed=False,
            line=None,
            suggested_fix="Model returned no verdict; rerun or escalate to a human reader.",
            raw=raw or "",
            audience=audience,
        )

    if lines[0].upper().startswith("PASS"):
        return Verdict(passed=True, raw=raw, audience=audience)

    line_val: Optional[str] = None
    fix_val: Optional[str] = None
    for ln in lines:
        upper = ln.upper()
        if upper.startswith("LINE:"):
            line_val = ln[len("LINE:"):].strip()
        elif upper.startswith("FIX:"):
            fix_val = ln[len("FIX:"):].strip()

    return Verdict(
        passed=False,
        line=line_val,
        suggested_fix=fix_val,
        raw=raw,
        audience=audience,
    )


class ReaderShift:
    """Run a reader-shift check on a generated response.

    Two ways to use it:

        # Instance — configure the model once, check many responses
        checker = ReaderShift(model=my_model)
        verdict = checker.run(response, audience="cold_developer")

        # Classmethod — convenience, pass the model per call
        verdict = ReaderShift.check(response, audience="cold_developer", model=my_model)

    `model` is any callable: prompt string in, model's raw text out. That is the
    entire integration surface, which is what keeps this package dependency-free.
    """

    def __init__(self, model: Optional[Model] = None):
        self.model = model

    def run(self, response: str, audience: str = "cold_reader",
            model: Optional[Model] = None) -> Verdict:
        use = model or self.model
        if use is None:
            raise ValueError(
                "No model provided. Supply a callable (prompt:str) -> str, "
                "either to ReaderShift(model=...) or to this call's model= argument."
            )
        prompt = build_prompt(response, audience)
        raw = use(prompt)
        return parse_verdict(raw, audience)

    @classmethod
    def check(cls, response: str, audience: str = "cold_reader",
              model: Optional[Model] = None) -> Verdict:
        return cls(model=model).run(response, audience=audience)
