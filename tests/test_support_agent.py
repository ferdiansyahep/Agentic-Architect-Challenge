import agents.support_agent as agent_module


class FakeGemini:
    is_configured = True

    def __init__(self, response):
        self.response = response
        self.prompts = []

    def generate(self, prompt):
        self.prompts.append(prompt)
        return {"success": True, "response": self.response}


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


def test_support_agent_understands_indonesian_name(monkeypatch):
    monkeypatch.setattr(agent_module.retriever, "get_relevant_context", lambda question: "")
    result = agent_module.support_agent.chat("s-id", "nama saya Ayu")
    recall = agent_module.support_agent.chat("s-id", "siapa nama saya?")

    assert result["used_tool"] == "memory"
    assert "Ayu" in recall["answer"]


def test_support_agent_does_not_treat_status_as_name(monkeypatch):
    monkeypatch.setattr(agent_module.retriever, "get_relevant_context", lambda question: "")
    result = agent_module.support_agent.chat("s-status", "I am having trouble logging in")

    assert result["used_tool"] is None


def test_support_agent_uses_previous_answer_for_follow_up(monkeypatch):
    contexts = iter([
        "Q: How do I reset my password?\nA: Use Forgot Password on the login page.",
        "",
    ])
    monkeypatch.setattr(agent_module.retriever, "get_relevant_context", lambda question: next(contexts))

    agent_module.support_agent.chat("s-follow", "How do I reset my password?")
    result = agent_module.support_agent.chat("s-follow", "Where is that link?")

    assert "login page" in result["answer"]
    assert result["used_tool"] == "memory"


def test_support_agent_refuses_unanswerable_question(monkeypatch):
    monkeypatch.setattr(agent_module.retriever, "get_relevant_context", lambda question: "")
    result = agent_module.support_agent.chat("s-unknown", "Who won the football match?")

    assert result["used_tool"] is None
    assert "provided document" in result["answer"]


def test_gemini_answers_using_document_and_history(monkeypatch):
    fake = FakeGemini(
        '{"action":"answer","answer":"Use Forgot Password on the login page.","expression":""}'
    )
    monkeypatch.setattr(agent_module, "gemini", fake)
    monkeypatch.setattr(
        agent_module.retriever,
        "get_document_content",
        lambda: "Q: Reset password?\nA: Use Forgot Password on the login page.",
    )

    result = agent_module.support_agent.chat("s-gemini-answer", "How can I reset it?")

    assert result["answer"] == "Use Forgot Password on the login page."
    assert result["used_tool"] == "retriever"
    assert result["decision_source"] == "gemini"
    assert "DOCUMENT:" in fake.prompts[0]


def test_gemini_decides_to_call_calculator(monkeypatch):
    fake = FakeGemini('{"action":"calculator","answer":"","expression":"12 / 3"}')
    monkeypatch.setattr(agent_module, "gemini", fake)
    monkeypatch.setattr(agent_module.retriever, "get_document_content", lambda: "sample FAQ")

    result = agent_module.support_agent.chat("s-gemini-calc", "What is twelve divided by three?")

    assert result["answer"] == "The calculation result is 4.0."
    assert result["used_tool"] == "calculator"
    assert result["tool_input"] == {"expression": "12 / 3"}
    assert result["decision_source"] == "gemini"


def test_invalid_gemini_response_uses_local_fallback(monkeypatch):
    fake = FakeGemini("not-json")
    monkeypatch.setattr(agent_module, "gemini", fake)
    monkeypatch.setattr(agent_module.retriever, "get_document_content", lambda: "sample FAQ")

    result = agent_module.support_agent.chat("s-gemini-fallback", "Please calculate 2 + 2")

    assert result["answer"] == "The calculation result is 4."
    assert result["used_tool"] == "calculator"
    assert "decision_source" not in result