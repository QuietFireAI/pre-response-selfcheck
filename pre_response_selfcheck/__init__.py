"""
pre-response-selfcheck — a second-pass reader-shift protocol for AI agents.

Run a reader-shift after a model generates a response and before it is
delivered: reread the output as a cold reader and either PASS it or revise one
specific line. Not a regeneration; ~5-10% token overhead.

    from pre_response_selfcheck import ReaderShift

    verdict = ReaderShift.check(
        response="Your model's drafted output goes here.",
        audience="cold_developer",
        model=my_model,            # any callable: (prompt:str) -> str
    )

    if verdict.passed:
        deliver(response)
    else:
        print(verdict.line)         # the sentence that fails a cold reader
        print(verdict.suggested_fix) # the targeted fix -- not a rewrite

Part of the DispatcherAgents stack by QuietFireAI.
"""

from .reader_shift import (
    AUDIENCES,
    THREE_QUESTIONS,
    Model,
    ReaderShift,
    Verdict,
    build_prompt,
    parse_verdict,
)

__version__ = "0.1.0"

__all__ = [
    "ReaderShift",
    "Verdict",
    "Model",
    "AUDIENCES",
    "THREE_QUESTIONS",
    "build_prompt",
    "parse_verdict",
    "__version__",
]
