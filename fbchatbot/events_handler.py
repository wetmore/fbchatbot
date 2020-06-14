from collections import defaultdict
from functools import wraps
import inspect
import logging
from typing import Callable, Optional, Protocol, DefaultDict, Type, List, Tuple

import attr
from fbchat import Event

from .command import Command
from .core_events import CommandEvent
from .types_util import Bot


_listener_arity_error = """
    Event listener must have at least one argument. The first argument
    represents the event instance which the listener is responding to.
"""
_no_event_type_error = """
    Event type must be specified in decorator or, as a type annotation
    on the argument of the decorated function.
"""
_mismatch_error = """
    Event type in listener decorator must match type annotation in decorated
    function.
"""
_must_subclass_event_error = """
    Event used in listener decorator must be a subclass of fbchat.Event
"""


class _ListenerHandler(Protocol):
    def __call__(self, event: Event, bot: Optional[Bot] = None):
        ...


class _CommandHandler(Protocol):
    def __call__(self, event: Event, bot: Optional[Bot] = None):
        ...


@attr.s
class EventListener:
    """A function associated with an event type which triggers it."""

    #: The type of event which triggers `func`.
    event: Type[Event] = attr.ib()

    #: The callback triggered when an event of type `event` occurs. Passed the event instance
    #: and a reference to the `Bot` which received the event.
    func: Callable[[Event, Bot], None] = attr.ib()


CommandMap = DefaultDict[str, List[Command]]
ListenerMap = DefaultDict[Type[Event], List[EventListener]]


@attr.s
class EventsHandler:
    """
    An EventsHandler instance provides `listener` and `command` decorators, which
    are used to register event listener and commands to the instance. This class is a
    base for both a bot and for a plugin.
    """

    #: Name of the EventsHandler; used for logging. Subclasses may use the name for more.
    name: str = attr.ib()

    #: Event listeners registered to the EventsHandler with @handler.listener.
    _listeners: ListenerMap = attr.ib(factory=lambda: defaultdict(list))

    #: Commands registered to the EventsHandler with @handler.command('command').
    # TODO make str map to a single command
    _commands: CommandMap = attr.ib(factory=lambda: defaultdict(list))

    def __attrs_post_init__(self):
        self._register_command_listener

    def _register_command_listener(self):
        """Register a listener to handle commands."""

        @self.listener
        def handle_command(event: CommandEvent, bot: Bot):
            for command in self._commands[event.command]:
                command.func(event, bot)

    def get_commands(self, specified_command: str = "") -> List[Tuple[str, str]]:
        """Return a list of commands and their docs registered to this EventsListener.
        
        Args:
            specified_command: If present, only return info for this command.

        Returns:


        """
        names_and_docs = []
        for name, command in self._commands.items():
            if specified_command and name != specified_command:
                continue
            names_and_docs.append((name, command[0].docs))
        return names_and_docs

    def handle_event(self, event: Event, bot: Bot):
        """Call every registered listener for a provided event."""
        for listener in self._listeners[type(event)]:
            listener.func(event, bot)

    def listener(self, arg):
        """Decorator for defining event listeners for an EventsHandler.
        
        An event listener is  a function which is called whenever a particular type of
        event occurs. The argument is an instance of that event type. The type of event
        the listener responds to can be specified by passing it to the listener, or
        simply by annotating the event argument (preferred). Either method may be used,
        but if the event type is specified using both methods at the same time, the
        provided types must match.

        Examples:
            Using type hints to specify the events listened for:

            >>> @plugin.listener
            >>> def handle_message(event: fbchat.MessageEvent):
            >>>     print(event.message.text)

            Passing an event type to the decorator to specify the events listened for:

            >>> @plugin.listener(fbchat.MessageEvent)
            >>> def handle_message(event):
            >>>     print(event.message.text)

        """

        event_type = None
        event_in_decorator = False
        if inspect.isclass(arg):
            assert issubclass(arg, Event), _must_subclass_event_error
            # The argument is the event
            event_in_decorator = True
            event_type = arg

        def decorator(func: _ListenerHandler):
            spec = inspect.getfullargspec(func)
            assert len(spec.args) >= 1, _listener_arity_error
            # Try to get the type annotation from the event argument
            ann = spec.annotations.get(spec.args[0], None)

            _event_type = event_type
            if _event_type == None:
                _event_type = ann
            elif ann != None:
                assert ann == _event_type, _mismatch_error

            assert _event_type != None, _no_event_type_error

            @wraps(func)
            def handler(event: Event, bot: Bot):
                func(event) if len(spec.args) == 1 else func(event, bot)

            event_listener = EventListener(event=_event_type, func=handler)

            self._listeners[_event_type].append(event_listener)

            logging.info(f"Registered {event_listener} on {self.name}")
            # TODO Remove this printf, which is being used while developing the chat logging module
            print(f"Registered {event_listener} on {self.name}")

            return func  # TODO should i return something else?

        if event_in_decorator:
            return decorator
        else:
            return decorator(arg)

    def command(self, cmd_name: str):
        """Decorator for defining commands for an `EventsHandler`.

        Args:
            cmd_name (str): The string used to invoke the command in a chat session.

        Decorate a callback function to call it when a user issues a command to the bot.
        The decorated function may take either 1 or 2 arguments; either just the
        `core_events.CommandEvent` which triggered the callback, or the `core_events.CommandEvent` and a reference
        to the `fbchatbot.types_util.Bot` which received the event. The docstring for the callback will
        be used to provide the docs for the command, which are shown when the core
        event `help_cmd` is invoked.

        Examples:
            Create an event which echos its argument: e.g.
                User: .echo this string

                Bot: this string

            >>> @bot.command("echo")
            >>> def echo(e: CommandEvent):
            >>>     \"\"\"Echo provided string\"\"\"
            >>>     e.thread.send_text(e.command_body)

            Trigger an event in response to the command:

            >>> @bot.command("trigger_event")
            >>> def trigger_event(e: CommandEvent, b: Bot):
            >>>     \"\"\"Trigger event\"\"\"
            >>>     b.handle(MyEvent())

        """

        def decorator(func: _CommandHandler):
            spec = inspect.getfullargspec(func)

            # TODO add assertions?

            @wraps(func)
            def handler(event: CommandEvent, bot: Bot):
                func(event) if len(spec.args) == 1 else func(event, bot)

            # Strip any indentation on the docstring
            docs = (func.__doc__ or "").strip()

            command = Command(command=cmd_name, docs=docs, func=handler)

            self._commands[cmd_name].append(command)

            logging.info(f"Registered {command} on {self.name}")

            return func

        return decorator
