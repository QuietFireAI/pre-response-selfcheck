"""
basic.py — run pre-response-selfcheck against a tiny stub model.

No API key needed: `stub_model` stands in for a real LLM call so the example
runs anywhere. Swap it for a real callable that takes a prompt and returns the
model's text (e.g. an OpenAI/Anthropic/local-model wrapper).

    python examples/basic.py
"""

from pre_response_selfcheck import ReaderShift


def stub_model(prompt: str) -> str:
    # A real model would read the RESPONSE block in `prompt` and judge it.
    # This stub flags any response that opens with a bare pronoun as failing a
    # cold reader, and passes everything else — just enough to show both paths.
    response_block = prompt.split("--- RESPONSE ---", 1)[-1]
    first = response_block.strip().splitlines()[0] if response_block.strip() else ""
    if first[:3].lower() in ("it ", "thi", "the"):
        return (
            "REVISE\n"
            f"LINE: {first}\n"
            "FIX: Name the subject explicitly instead of opening with a pronoun."
        )
    return "PASS"


if __name__ == "__main__":
    clean = "pre-response-selfcheck rereads output as a cold reader before delivery."
    muddy = "It runs after generation, before delivery."

    for label, text in (("clean", clean), ("muddy", muddy)):
        verdict = ReaderShift.check(text, audience="cold_developer", model=stub_model)
        print(f"\n[{label}] -> {'PASS' if verdict.passed else 'REVISE'}")
        if not verdict.passed:
            print(f"  LINE: {verdict.line}")
            print(f"  FIX:  {verdict.suggested_fix}")
