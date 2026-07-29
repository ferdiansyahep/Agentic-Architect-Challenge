import agents.support_agent as agent_module


def test_support_agent_answers_from_faq(monkeypatch):
    monkeypatch.setattr(
        agent_module.retriever,
        "get_relevant_context",
        lambda question: "Q: How do I reset my password?\nA: Click 'Forgot Password' on the login page.",
    )

    result = agent_module.support_agent.chat(
        session_id="s-1",
        question="How do I reset my password?",
    )

    assert result["success"] is True
    assert "Forgot Password" in result["answer"]
    assert result["used_tool"] == "retriever"


def test_support_agent_remembers_name(monkeypatch):
    monkeypatch.setattr(agent_module.retriever, "get_relevant_context", lambda question: "")

    remember = agent_module.support_agent.chat(
        session_id="s-2",
        question="my name is Budi",
    )
    recall = agent_module.support_agent.chat(
        session_id="s-2",
        question="what is my name?",
    )

    assert remember["success"] is True
    assert "Budi" in remember["answer"]
    assert recall["success"] is True
    assert "Budi" in recall["answer"]


def test_support_agent_uses_calculator_when_needed(monkeypatch):
    monkeypatch.setattr(agent_module.retriever, "get_relevant_context", lambda question: "")

    result = agent_module.support_agent.chat(
        session_id="s-3",
        question="Please calculate 2 + 3 * 4",
    )

    assert result["success"] is True
    assert "14" in result["answer"]
    assert result["used_tool"] == "calculator"
