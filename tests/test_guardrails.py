from tools.guardrails import SummaryGuardrail


def test_trim_source_normalizes_and_trims():
    guardrail = SummaryGuardrail(max_input_chars=20)

    trimmed, was_trimmed = guardrail.trim_source("alpha   beta   gamma   delta")

    assert was_trimmed is True
    assert trimmed == "alpha beta gamma"


def test_build_prompt_includes_metadata():
    guardrail = SummaryGuardrail(max_input_chars=100)

    result = guardrail.build_prompt(
        title="Example Title",
        url="https://example.com",
        content="some content"
    )

    assert result["was_trimmed"] is False
    assert "Example Title" in result["prompt"]
    assert "https://example.com" in result["prompt"]


def test_validate_summary_truncates_overlong_output():
    guardrail = SummaryGuardrail(max_output_words=5)

    summary = guardrail.validate_summary("one two three four five six seven")

    assert summary == "one two three four five..."