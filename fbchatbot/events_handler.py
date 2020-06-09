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


class ListenerHandler(Protocol):
    def __call__(self, event: Event, bot: Optional[Bot] = None):
        ...


class CommandHandler(Protocol):
    def __call__(self, event: Event, bot: Optional[Bot] = None):
        ...


@attr.s
class EventListener:
    """A function associated with an event type which triggers it."""

    event: Type[Event] = attr.ib()
    func: Callable[[Event, Bot], None] = attr.ib()


@attr.s
class EventsHandler:
    """
    An EventsHandler instance provides `listener()` and `command()` decorators, which
    are used to register event listener and commands to the instance. This class is a
    base for both a bot and for a plugin.
    """

    #: Name, used for logging
    name: str = attr.ib()

    #: Event listeners registered to the EventsHandler with @handler.listener()
    _listeners: DefaultDict[Type[Event], List[EventListener]] = attr.ib(
        defaultdict(list)
    )

    #: Commands registered to the EventsHandler with @handler.command('command')
    # TODO make str map to a single command
    _commands: DefaultDict[str, List[Command]] = attr.ib(defaultdict(list))

    def __attrs_post_init__(self):
        self._register_command_listener()

    def _register_command_listener(self):
        """Register a listener to handle commands."""

        @self.listener()
        def handle_command(event: CommandEvent, bot: Bot):
            for command in self._commands[event.command]:
                command.func(event, bot)

    def get_commands(self, specified_command: str = "") -> List[Tuple[str, str]]:
        """Return a list of commands and their docs registered to this EventsListener."""
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

    def listener(self, event_type=None):
        """
        Decorator for defining event listeners for a plugin. An event listener is
        a function which is called whenever a particular type of event occurs.
        The argument is an instance of that event type. The type of event the
        listener responds to can be specified by passing it to the listener:

        ```
        @plugin.listener(fbchat.MessageEvent)
        def handle_message(event):
            print(event.message.text)
        ```

        or simply by annotating the event argument (preferred):

        ```
        @plugin.listener()
        def handle_message(event: fbchat.MessageEvent):
            print(event.message.text)
        ```

        Either method may be used, but if the event type is specified using both
        methods at the same time, the provided types must match.
        """

        def decorator(func: ListenerHandler):
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

            return func  # TODO should i return something else?

        return decorator

    def command(self, cmd_name: str):
        def decorator(func: CommandHandler):
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
