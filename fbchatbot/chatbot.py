from typing import List, Tuple, TYPE_CHECKING
from datetime import datetime

import attr

# from .base_plugin import base_plugin
from .events_handler import EventsHandler
from .core_events import core_listeners
from .core_commands import core_commands
from .plugin import Plugin

if TYPE_CHECKING:
    from .chatbot_manager import ChatbotManager


@attr.s(eq=False)
class Chatbot(EventsHandler):

    manager: "ChatbotManager" = attr.ib(kw_only=True)

    config = attr.ib(kw_only=True)

    db = attr.ib(default=None)

    plugins: List[Plugin] = attr.ib(factory=list)

    def __attrs_post_init__(self):
        # Register core event listeners and commands
        super().__attrs_post_init__()  # This sets up the command listener
        for listener in core_listeners:
            self.listener(listener)
        for name, handler in core_commands.items():
            self.command(name)(handler)

    def claim_threads(self, *threads):
        """Assign this bot to chat threads."""
        for thread_id in threads:
            self.manager.assign_thread(thread_id, self)

    def load_plugin(self, plugin: Plugin):
        """Load a plugin."""
        if plugin.on_load:
            plugin.on_load(plugin, self)
        self.plugins.append(plugin)

    def handle(self, event):
        """Handle an event"""
        print(f"{datetime.now().strftime('%b %d %Y %H:%M:%S')} [{self.name}]")
        print(event)
        self.handle_event(event, self)
        for plugin in self.plugins:
            plugin.handle_event(event, self)

    def get_all_commands(self, command: str = "") -> List[Tuple[str, str]]:
        """Return a list of every command handled by this bot along with their docs."""
        commands = self.get_commands(command)
        for plugin in self.plugins:
            commands = commands + plugin.get_commands(command)
        return commands

    def start(self):
        """Log into messenger and start listening to events for this bot."""
        self.manager.start(self)
