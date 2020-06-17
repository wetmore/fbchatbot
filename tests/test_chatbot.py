import pytest

from fbchatbot.chatbot_manager import ChatbotManager
from fbchatbot.chatbot import Chatbot


def test_claim_threads():
    manager = ChatbotManager(config={})
    bot = manager.add_bot("bot")
    bot.claim_threads("123", "456")

    assert manager.thread_map["123"] is bot
    assert manager.thread_map["456"] is bot
    with pytest.raises(KeyError):
        manager.thread_map["789"]

    bot2 = manager.add_bot("bot2")

    with pytest.raises(AssertionError):
        bot2.claim_threads("123")
