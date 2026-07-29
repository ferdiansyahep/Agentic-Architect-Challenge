from memory.memory import ConversationMemory


def test_memory_is_isolated_and_bounded():
    memory = ConversationMemory(max_turns=2)
    memory.try_store_name("one", "my name is Budi")
    memory.remember_turn("one", "q1", "a1")
    memory.remember_turn("one", "q2", "a2")
    memory.remember_turn("one", "q3", "a3")

    assert memory.get_name("one") == "Budi"
    assert memory.get_name("two") is None
    assert [turn["question"] for turn in memory.get_history("one")] == ["q2", "q3"]


def test_memory_can_clear_session():
    memory = ConversationMemory()
    memory.try_store_name("one", "nama saya Ayu")
    memory.clear("one")

    assert memory.get_name("one") is None