from services.retriever import RetrieverService


def test_retriever_returns_relevant_pair(tmp_path):
    faq = tmp_path / "faq.txt"
    faq.write_text(
        "Q: How do I reset my password?\nA: Use the reset link.\n\n"
        "Q: Where are invoices?\nA: Open Billing.\n",
        encoding="utf-8",
    )
    retriever = RetrieverService(str(faq))

    result = retriever.search("reset password")

    assert result is not None
    assert result.answer == "Use the reset link."
    assert result.score > 0
    assert result.source == str(faq)


def test_retriever_returns_none_when_document_is_irrelevant(tmp_path):
    faq = tmp_path / "faq.txt"
    faq.write_text("Q: How do I reset my password?\nA: Use the reset link.\n", encoding="utf-8")
    retriever = RetrieverService(str(faq))

    assert retriever.search("Who won the football match yesterday?") is None
    assert retriever.get_relevant_context("Who won the football match yesterday?") == ""