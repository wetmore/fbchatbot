import atexit
import logging
from typing import Set, Optional, Dict, TypeVar

import attr
import fbchat

# from .base_plugin import base_plugin
from .util import get_session, save_session
from .chatbot import Chatbot


@attr.s(eq=False)
class ChatbotManager:
    config = attr.ib(kw_only=True)

    # TODO...
    queue = attr.ib(default=None)

    db: Optional[Any] = attr.ib(default=None)

    bots: Set[Chatbot] = attr.ib(factory=set)

    thread_map: Dict[str, Chatbot] = attr.ib(factory=dict)

    def __attrs_post_init__(self):
        # Configure logging
        log_level = getattr(self.config, "LOG_LEVEL", None) or logging.WARNING
        print(f"Using log level {log_level}")
        logging.basicConfig(level=log_level)

    def add_bot(self, name, config=None, db=None) -> Chatbot:
        """Create a bot which is managed by this ChatbotManager

        Args:
            name (str): The name of the bot.
            config (Optional[Any]): Config. Uses the ChatManager's config by default
            db (Optional[peewee.Database]): Database for the bot to use. Uses the ChatManager's
                database by default.
        """
        _config = self.config if config is None else config
        _db = self.db if db is None else db
        bot = Chatbot(manager=self, name=name, config=_config, db=_db)
        self.bots.add(bot)

        return bot

    def assign_thread(self, thread_id: str, bot: Chatbot):
        """Assign a bot to a chat thread"""
        assigned_bot = self.thread_map.get(thread_id, None)
        assert (
            assigned_bot is None or assigned_bot is bot
        ), f"Already assigned {thread_id} to bot {assigned_bot.name}"
        self.thread_map[thread_id] = bot

    def start(self, bot: Optional[Chatbot] = None):
        """Log in to facebook messenger and start listening for and handling events."""
        session, status = get_session(self.config)
        atexit.register(lambda: save_session(session))
        print(f"{status}, user {session.user.id}")

        # TODO Figure out what these kwargs do
        chat_listener = fbchat.Listener(session=session, chat_on=True, foreground=True)

        unassigned_bots = self.bots - set(self.thread_map.values())
        assert (
            len(unassigned_bots) <= 1
        ), "Cannot have more than 1 bot assigned to no threads"
        fallback_bot: Optional[Chatbot] = None
        if len(unassigned_bots) == 1:
            fallback_bot = unassigned_bots.pop()

        available_bots = set([bot]) if bot else self.bots
        bots_for_event = available_bots.copy()

        # Listener event loop
        print("Listening...")
        for event in chat_listener.listen():
            if isinstance(event, fbchat.ThreadEvent):
                b = self.thread_map.get(event.thread, fallback_bot)
                if b:
                    bots_for_event &= set([b])
                else:
                    bots_for_event.clear()
            for b in bots_for_event:
                b.handle(event)
            bots_for_event |= available_bots
