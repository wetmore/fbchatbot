import inspect
from typing import Callable, Dict, List, Type

import attr
from fbchat import Event

Handler = Callable[[Event], None]


@attr.s
class EventListener:
    event: Type[Event] = attr.ib()
    func: Handler = attr.ib()


@attr.s
class EventListeners:
    _listeners_dict: Dict[Type[Event], List[EventListener]] = attr.ib({})

    def add_listener(self, listener: EventListener):
        try:
            listeners_for_event = self._listeners_dict[listener.event]
        except KeyError:
            listeners_for_event = []
        listeners_for_event.append(listener)
        self._listeners_dict[listener.event] = listeners_for_event

    def add_listeners(self, listeners: List[EventListener]):
        for listener in listeners:
            self.add_listener(listener)

    def handle(self, event: Event):
        try:
            listeners_for_event = self._listeners_dict[type(event)]
            for listener in listeners_for_event:
                listener.func(event)
        except KeyError:
            pass  # No handler for that type registered


_listener_arity_error = """
    Event listener must have exactly one argument. This argument represents the
    event instance which the listener is responding to.
"""
_no_event_type_error = """
    Event type must be specified in decorator or, as a type annotation
    on the argument of the decorated function.
"""
_mismatch_error = """
    Event type in listener decorator must match type annotation in decorated
    function.
"""


def listener(event_type=None):
    """
        Decorator for defining event listeners for the bot. An event listener is
        a function which is called whenever a particular type of event occurs.
        The argument is an instance of that event type. The type of event the
        listener responds to can be specified by passing it to the listener:

        ```
        @listener(fbchat.MessageEvent)
        def handle_message(event):
            print(event.message.text)
        ```

        or simply by annotating the event argument:

        ```
        @listener()
        def handle_message(event: fbchat.MessageEvent):
            print(event.message.text)
        ```

        Either method may be used, but if the event type is specified using both
        methods at the same time, the provided types must match.
    """

    def decorator(func):
        spec = inspect.getfullargspec(func)
        assert len(spec.args) == 1, _listener_arity_error
        # Get the type annotation from the event argument, if it exists
        try:
            ann = spec.annotations[spec.args[0]]
        except:
            ann = None

        # If
        _event_type = event_type
        if _event_type == None:
            _event_type = ann
        elif ann != None:
            assert ann == _event_type, _mismatch_error

        assert _event_type != None, _no_event_type_error
        return EventListener(event=_event_type, func=func)

    return decorator
