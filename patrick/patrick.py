import atexit
from typing import List, TYPE_CHECKING
from datetime import datetime

import attr
import fbchat

# from .base_plugin import base_plugin
from .util import get_session, save_session
from .event_handler import EventsHandler
from .core_events import create_core_event_listeners
from .plugin import Plugin


@attr.s
class Patrick(EventsHandler):
    config = attr.ib(kw_only=True)

    # TODO...
    queue = attr.ib(default=None)

    plugins: List[Plugin] = attr.ib([])

    def __attrs_post_init__(self):
        # Load base plugin
        #  self.load_plugin(base_plugin)
        self._attach_command_listener()
        create_core_event_listeners(self)

    def load_plugin(self, plugin: Plugin):
        """Load a plugin."""
        self.plugins.append(plugin)

    def handle(self, event):
        print(datetime.now().strftime("%b %d %Y %H:%M:%S"), "\n", event)
        self.handle_event(event, self)
        for plugin in self.plugins:
            plugin.handle_event(event, self)

    def listen(self):
        """Log in to facebook messenger and start listening for and handling events."""
        session, status = get_session(self.config)
        atexit.register(lambda: save_session(session))
        print(f"{status}, user {session.user.id}")

        # TODO Figure out what these kwargs do
        chat_listener = fbchat.Listener(session=session, chat_on=True, foreground=True)

        # Listener event loop
        print("Listening...")
        for event in chat_listener.listen():
            # TODO Add thread filtering
            self.handle(event)
