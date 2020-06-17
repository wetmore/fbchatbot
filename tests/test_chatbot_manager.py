import logging

from fbchat import Event, ThreadEvent
import pytest
from unittest.mock import Mock, patch, call

from fbchatbot.chatbot_manager import ChatbotManager
from fbchatbot.chatbot import Chatbot


def test_create_chatbot_manager():
    config = {}
    manager = ChatbotManager(config=config)

    assert logging.getLogger().level == logging.WARNING


def test_add_bot():
    config = {}
    manager = ChatbotManager(config=config)

    bot1 = manager.add_bot("bot1")
    assert len(manager.bots) == 1
    assert bot1 in manager.bots
    assert bot1.config is config

    bot2 = manager.add_bot("bot2", config={})
    assert len(manager.bots) == 2
    assert bot2.config is not config


def test_assign_thread():
    config = {}
    manager = ChatbotManager(config=config)

    bot1 = manager.add_bot("bot1")
    bot2 = manager.add_bot("bot2")

    manager.assign_thread("1234567", bot1)
    assert manager.thread_map["1234567"] is bot1

    with pytest.raises(AssertionError):
        manager.assign_thread("1234567", bot2)

    manager.assign_thread("1234567", bot1)
    assert manager.thread_map["1234567"] is bot1


def test_start(monkeypatch):
    manager = ChatbotManager(config={})

    # Create two bots, assign them to different threads, and mock their handle methods.
    bot1 = manager.add_bot("bot1")
    manager.assign_thread("123", bot1)
    handle1 = Mock()
    monkeypatch.setattr(bot1, "handle", handle1)

    bot2 = manager.add_bot("bot2")
    manager.assign_thread("456", bot2)
    handle2 = Mock()
    monkeypatch.setattr(bot2, "handle", handle2)

    # Mock the chat session.
    session = Mock()
    session.user.id = "fake id"
    get_session = Mock()
    get_session.return_value = (session, "fake status")
    save_session = Mock()
    monkeypatch.setattr("atexit.register", Mock())
    monkeypatch.setattr("fbchatbot.chatbot_manager.get_session", get_session)
    monkeypatch.setattr("fbchatbot.chatbot_manager.save_session", save_session)

    # Create 3 mock events
    e1 = Mock(spec=Event)
    e2 = Mock(spec=ThreadEvent)
    e2.thread.id = "123"
    e3 = Mock(spec=ThreadEvent)
    e3.thread.id = "456"

    with patch("fbchat.Listener") as mock:
        instance = mock.return_value
        instance.listen = lambda: [e1, e2, e3]

        manager.start()

        # Both bots should handle e1. bot1 should handle e2, and bot2 should handle e3.
        handle1.assert_has_calls([call(e1), call(e2)])
        handle2.assert_has_calls([call(e1), call(e3)])


def test_start_specific_bot(monkeypatch):
    manager = ChatbotManager(config={})

    # Create two bots, assign them to different threads, and mock their handle methods.
    bot1 = manager.add_bot("bot1")
    manager.assign_thread("123", bot1)
    handle1 = Mock()
    monkeypatch.setattr(bot1, "handle", handle1)

    bot2 = manager.add_bot("bot2")
    manager.assign_thread("456", bot2)
    handle2 = Mock()
    monkeypatch.setattr(bot2, "handle", handle2)

    # Mock the chat session.
    session = Mock()
    session.user.id = "fake id"
    get_session = Mock()
    get_session.return_value = (session, "fake status")
    save_session = Mock()
    monkeypatch.setattr("atexit.register", Mock())
    monkeypatch.setattr("fbchatbot.chatbot_manager.get_session", get_session)
    monkeypatch.setattr("fbchatbot.chatbot_manager.save_session", save_session)

    # Create 3 mock events
    e1 = Mock(spec=Event)
    e2 = Mock(spec=ThreadEvent)
    e2.thread.id = "123"
    e3 = Mock(spec=ThreadEvent)
    e3.thread.id = "456"

    with patch("fbchat.Listener") as mock:
        instance = mock.return_value
        instance.listen = lambda: [e1, e2, e3]

        manager.start(bot1)

        # Only bot1 should handle calls
        handle1.assert_has_calls([call(e1), call(e2)])
        handle2.assert_not_called()


def test_start_one_unassigned(monkeypatch):
    manager = ChatbotManager(config={})

    # Create two bots, only assign one to a thread, and mock their handle methods.
    bot1 = manager.add_bot("bot1")
    manager.assign_thread("123", bot1)
    handle1 = Mock()
    monkeypatch.setattr(bot1, "handle", handle1)

    bot2 = manager.add_bot("bot2")
    handle2 = Mock()
    monkeypatch.setattr(bot2, "handle", handle2)

    # Mock the chat session.
    session = Mock()
    session.user.id = "fake id"
    get_session = Mock()
    get_session.return_value = (session, "fake status")
    save_session = Mock()
    monkeypatch.setattr("atexit.register", Mock())
    monkeypatch.setattr("fbchatbot.chatbot_manager.get_session", get_session)
    monkeypatch.setattr("fbchatbot.chatbot_manager.save_session", save_session)

    # Create 4 mock events
    e1 = Mock(spec=Event)
    e2 = Mock(spec=ThreadEvent)
    e2.thread.id = "123"
    e3 = Mock(spec=ThreadEvent)
    e3.thread.id = "456"
    e4 = Mock(spec=ThreadEvent)
    e4.thread.id = "789"

    with patch("fbchat.Listener") as mock:
        instance = mock.return_value
        instance.listen = lambda: [e1, e2, e3, e4]

        manager.start()

        # bot1 should handle e1 and e2. bot2 should handle e1, and e3 and e4 because
        # no bot is explicitly assigned to threads 456 and 789.
        handle1.assert_has_calls([call(e1), call(e2)])
        handle2.assert_has_calls([call(e1), call(e3), call(e4)])


def test_start_too_many_unassigned(monkeypatch):
    manager = ChatbotManager(config={})

    # Create two bots but don't assign them
    bot1 = manager.add_bot("bot1")
    bot2 = manager.add_bot("bot2")

    # Mock the chat session.
    session = Mock()
    session.user.id = "fake id"
    get_session = Mock()
    get_session.return_value = (session, "fake status")
    save_session = Mock()
    monkeypatch.setattr("atexit.register", Mock())
    monkeypatch.setattr("fbchatbot.chatbot_manager.get_session", get_session)
    monkeypatch.setattr("fbchatbot.chatbot_manager.save_session", save_session)

    with patch("fbchat.Listener") as mock:
        instance = mock.return_value
        instance.listen = lambda: []

        with pytest.raises(AssertionError):
            # This should raise an AssertionError because two bots are unassigned.
            manager.start()
