from typing import (
    Any,
    Optional,
    DefaultDict,
    Type,
    List,
    Tuple,
    Iterable,
    TYPE_CHECKING,
)
from datetime import datetime
from collections import defaultdict
import logging
import inspect

import attr
from fbchat import Client

# from .base_plugin import base_plugin
from .event_listener import listener, EventListener
from .command import command, Command
from .core_events import core_listeners, CommandEvent
from .core_commands import core_commands
from .plugin import Plugin
from .types_util import Bot
from .util import Colors

if TYPE_CHECKING:
    from .chatbot_manager import ChatbotManager

logger = logging.getLogger("fbchatbot")

# Type synonyms
CommandName = str
Source = str
CommandMap = DefaultDict[CommandName, List[Tuple[Command, Source]]]
ListenerMap = DefaultDict[Type[Any], List[Tuple[EventListener, Source]]]


@attr.s(eq=False)
class Chatbot:
    name: str = attr.ib(kw_only=True)

    manager: "ChatbotManager" = attr.ib(kw_only=True)

    # TODO start as none instead of making optional arg?
    db: Optional[Any] = attr.ib(kw_only=True, default=None)

    plugins: List[Plugin] = attr.ib(factory=list)

    listeners: ListenerMap = attr.ib(factory=lambda: defaultdict(list))

    commands: CommandMap = attr.ib(factory=lambda: defaultdict(list))

    has_loaded: bool = attr.ib(False)

    client: Optional[Client] = attr.ib(None)

    @classmethod
    def create(
        cls, name: str, manager: "ChatbotManager", db: Optional[Any]
    ) -> "Chatbot":
        """Create a new Chatbot."""
        chatbot = cls(name=name, manager=manager, db=db)

        # Register core event listeners and commands
        @listener
        def handle_command(event: CommandEvent, bot: Bot):
            for command, _ in chatbot.commands[event.command]:
                command.execute(event, bot)

        chatbot.add_listener(handle_command, "core")
        chatbot.add_listeners(core_listeners, "core")
        chatbot.add_commands(core_commands, "core")

        return chatbot

    def add_command(self, command: Command, source: Source):
        self.commands[command.name].append((command, source))
        logger.info(
            f"Registered Command {command.pretty()} on {Colors.yellow(self.name)} from {Colors.yellow(source)}"
        )
        logger.debug(command)

    def add_listener(self, listener: EventListener, source: Source):
        self.listeners[listener.event].append((listener, source))
        logger.info(
            f"Registered EventListener {listener.pretty()} on {Colors.yellow(self.name)} from {Colors.yellow(source)}"
        )
        logger.debug(listener)

        # TODO Remove this printf, which is being used while developing the chat
        # logging module.
        # print(f"Registered EventListener {event_listener.pretty()} on {self.name}")

    def add_commands(self, commands: Iterable[Command], source: Source):
        for command in commands:
            self.add_command(command, source)

    def add_listeners(self, listeners: Iterable[EventListener], source: Source):
        for listener in listeners:
            self.add_listener(listener, source)

    def get_all_commands(self, specified_command: str = "") -> List[Tuple[str, str]]:
        """Return a list of commands and their docs registered to this EventsListener.

        Args:
            specified_command: If present, only return info for this command.

        Returns:


        """
        names_and_docs = []
        for name, commands in self.commands.items():
            if specified_command and name != specified_command:
                continue
            command, source = commands[0]
            names_and_docs.append((name, command.docs))
        return names_and_docs

    def handle(self, event: Any):
        """Call every registered listener for a provided event."""
        print(f"{datetime.now().strftime('%b %d %Y %H:%M:%S')} [{self.name}]")
        print(event)
        for listener, _ in self.listeners[type(event)]:
            listener.execute(event, self)

    # TODO make property?
    def get_client(self) -> Client:
        """Return a client, used to interact with facebook."""
        assert (
            self.client is not None
        ), "Cannot call get_client until bot has started listening."
        return self.client  # type: ignore

    def listener(self, arg):
        """Convenience decorator for creating a listener and adding it to the bot."""
        source = inspect.stack()[1].filename

        def dec(x):
            y = listener(arg)(x)
            self.add_listener(y, source)

        return dec

    def command(self, command_name):
        """Convenience decorator for creating a command and adding it to the bot.

        Use the decorator on a command handler.

        Examples:

            >>> bot = add_bot('bot')
            >>> bot.command('echo')
            >>> def echo(e: CommandEvent):
            >>>     e.thread.send_text(e.command_body)
        """
        source = inspect.stack()[1].filename

        def dec(x):
            y = command(command_name)(x)
            self.add_command(y, source)

        return dec

    def claim_threads(self, *threads) -> "Chatbot":
        """Assign this bot to chat threads. Returns the bot for chaining."""
        for thread_id in threads:
            self.manager.assign_thread(thread_id, self)

        return self

    def load_plugin(self, plugin: Plugin) -> "Chatbot":
        """Add a plugin to the bot. Returns the bot for chaining."""
        plugin.on_load(self)

        # Load any "method" listeners or commands, which depend on an instance of
        # the plugin they are defined on. These are defined by using the @listener
        # decorator on top of a method in a plugin definition.
        method_listeners = []
        method_commands = []
        for attrib in dir(plugin):
            # TODO I guess it's more pythonic to get rid of the isinstance branching,
            # add them all to one list, and then determine if they are a command or a
            # listener by checking presence of 'event' vs 'command' attrs?
            if isinstance(getattr(plugin, attrib), EventListener):
                method_listener = getattr(plugin, attrib)
                method_listener.bind(plugin)
                method_listeners.append(method_listener)
            if isinstance(getattr(plugin, attrib), Command):
                method_command = getattr(plugin, attrib)
                method_command.bind(plugin)
                method_commands.append(method_command)

        self.add_listeners(plugin.listeners + method_listeners, plugin.name)
        self.add_commands(plugin.commands + method_commands, plugin.name)

        self.plugins.append(plugin)

        return self

    def start(self):
        """Log into messenger and start listening to events for this bot.
        
        This is a blocking method.
        """
        self.manager.start(self)
