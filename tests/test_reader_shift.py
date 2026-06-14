"""Tests for pre-response-selfcheck. No network, no API: the model is faked."""

import pytest

from pre_response_selfcheck import (
    AUDIENCES,
    ReaderShift,
    Verdict,
    build_prompt,
    parse_verdict,
)


# --- fake models: callables (prompt:str) -> str -----------------------------

def model_pass(prompt: str) -> str:
    return "PASS"

def model_revise(prompt: str) -> str:
    return (
        "REVISE\n"
        "LINE: It runs after output is generated, before it is delivered.\n"
        "FIX: Define 'reader-shift' before this sentence so a cold reader isn't lost."
    )

def model_empty(prompt: str) -> str:
    return ""


# --- prompt construction ----------------------------------------------------

def test_prompt_contains_response_and_three_questions():
    p = build_prompt("Hello world.", audience="cold_developer")
    assert "Hello world." in p
    assert "three questions" in p.lower()
    assert AUDIENCES["cold_developer"] in p
    assert "PASS" in p and "REVISE" in p  # output contract present

def test_prompt_unknown_audience_falls_back_to_cold_reader():
    p = build_prompt("x", audience="does_not_exist")
    assert AUDIENCES["cold_reader"] in p


# --- parsing ----------------------------------------------------------------

def test_parse_pass():
    v = parse_verdict("PASS")
    assert v.passed is True
    assert bool(v) is True
    assert v.line is None and v.suggested_fix is None

def test_parse_pass_is_case_and_whitespace_insensitive():
    assert parse_verdict("  pass  ").passed is True

def test_parse_revise_extracts_line_and_fix():
    v = parse_verdict(
        "REVISE\nLINE: the opening sentence\nFIX: define the term first"
    )
    assert v.passed is False
    assert v.line == "the opening sentence"
    assert v.suggested_fix == "define the term first"
    assert v.raw.startswith("REVISE")

def test_empty_reply_fails_closed():
    v = parse_verdict("")
    assert v.passed is False
    assert v.suggested_fix  # tells the caller to rerun/escalate


# --- ReaderShift end to end (with fake models) ------------------------------

def test_check_pass_path():
    v = ReaderShift.check("clean text", audience="cold_developer", model=model_pass)
    assert isinstance(v, Verdict)
    assert v.passed is True
    assert v.audience == "cold_developer"

def test_check_revise_path():
    v = ReaderShift.check("muddy text", model=model_revise)
    assert v.passed is False
    assert "Define" in v.suggested_fix
    assert v.line

def test_instance_reuse():
    checker = ReaderShift(model=model_pass)
    assert checker.run("a").passed
    assert checker.run("b").passed

def test_no_model_raises():
    with pytest.raises(ValueError):
        ReaderShift.check("text")  # no model supplied anywhere

def test_empty_model_reply_yields_failing_verdict():
    v = ReaderShift.check("text", model=model_empty)
    assert v.passed is False
