from typing import Any, List, Optional, Tuple, TYPE_CHECKING
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
class Chatbot:
    name: str = attr.ib(kw_only=True)

    manager: "ChatbotManager" = attr.ib(kw_only=True)

    events_handler: EventsHandler = attr.ib(kw_only=True)

    # TODO start as none instead of making optional arg?
    db: Optional[Any] = attr.ib(kw_only=True, default=None)

    plugins: List[Plugin] = attr.ib(factory=list)

    @classmethod
    def create(
        cls, name: str, manager: "ChatbotManager", db: Optional[Any]
    ) -> "Chatbot":
        """Create a new Chatbot."""
        events_handler = EventsHandler(f"{name} handler")

        # Register core event listeners and commands
        events_handler.register_command_listener()
        for listener in core_listeners:
            events_handler.listener(listener)
        for cmd_name, handler in core_commands.items():
            events_handler.command(cmd_name)(handler)

        return cls(name=name, manager=manager, events_handler=events_handler, db=db)

    def listener(self, arg):
        return self.events_handler.listener(arg)

    def command(self, command_name):
        return self.events_handler.command(command_name)

    def claim_threads(self, *threads) -> "Chatbot":
        """Assign this bot to chat threads. Returns the bot for chaining."""
        for thread_id in threads:
            self.manager.assign_thread(thread_id, self)

        return self

    def load_plugin(self, plugin: Plugin) -> "Chatbot":
        """Load a plugin. Returns the bot for chaining."""
        if plugin.on_load:
            plugin.on_load(plugin, self)
        self.plugins.append(plugin)

        return self

    def handle(self, event):
        """Handle an event."""
        print(self)
        print(f"{datetime.now().strftime('%b %d %Y %H:%M:%S')} [{self.name}]")
        print(event)
        self.events_handler.handle_event(event, self)
        for plugin in self.plugins:
            plugin.handle_event(event, self)

    def get_all_commands(self, command: str = "") -> List[Tuple[str, str]]:
        """Return a list of every command handled by this bot along with their docs."""
        commands = self.events_handler.get_commands(command)
        for plugin in self.plugins:
            commands = commands + plugin.get_commands(command)

        return commands

    def start(self):
        """Log into messenger and start listening to events for this bot."""
        self.manager.start(self)
