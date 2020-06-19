import inspect
from typing import Optional, Protocol, Type
from types import MethodType

import attr
from fbchat import Event

from .types_util import Bot
from .util import Colors


class ListenerHandler(Protocol):
    def __call__(self, event: Event, bot: Optional[Bot] = None):
        ...


@attr.s
class EventListener:
    """A function associated with an event type which triggers it."""

    #: The type of event which triggers `func`.
    event: Type[Event] = attr.ib()

    #: The callback triggered when an event of type `event` occurs. Passed the event
    # instance and a reference to the `Bot` which received the event.
    func: ListenerHandler = attr.ib()

    def bind(self, obj):
        self.func = MethodType(self.func, obj)

    def execute(self, event: Event, bot: Bot):
        spec = inspect.getfullargspec(self.func)
        if type(self.func) == MethodType:
            needs_bot_arg = len(spec.args) == 3
        else:
            needs_bot_arg = len(spec.args) == 2
        self.func(event, bot) if needs_bot_arg else self.func(event)

    def pretty(self):
        """Pretty print event handler, for info-level logging."""
        return (
            f"{Colors.blue(self.event.__name__)} ⟶  {Colors.green(self.func.__name__)}"
        )


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


def listener(arg):
    """Decorator for defining event listeners.

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

    def decorator(func: ListenerHandler):
        spec = inspect.getfullargspec(func)
        assert len(spec.args) >= 1, _listener_arity_error
        # Try to get the type annotation from the event argument
        ann = spec.annotations.get(spec.args[0], None)

        _event_type = event_type
        if _event_type is None:
            _event_type = ann
        elif ann is not None:
            assert ann == _event_type, _mismatch_error

        assert _event_type is not None, _no_event_type_error

        return EventListener(event=_event_type, func=func)

    if event_in_decorator:
        return decorator
    else:
        return decorator(arg)
