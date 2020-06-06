import inspect
from functools import wraps

import attr

from .listeners import EventListener, EventListeners, Handler


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


@attr.s
class Plugin:
    """
    you register commands, listeners, and derivers on instances of Plugin.
    Patrick also inherits from Plugin, so you can register listeners on a patrick
    instance.
    """

    #: Name used to refer to the plugin, e.g. when writing config.py for a bot.
    name: str = attr.ib()

    #: Event listeners registered to the plugin with @plugin.listener()
    _listeners: EventListeners = attr.ib(attr.Factory(EventListeners))
    # _commands = attr.ib([])
    # _event_derivers = attr.ib([])

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

        def decorator(func: Handler):
            spec = inspect.getfullargspec(func)
            assert len(spec.args) >= 1, _listener_arity_error
            # Try to get the type annotation from the event argument
            try:
                ann = spec.annotations[spec.args[0]]
            except:
                ann = None

            _event_type = event_type
            if _event_type == None:
                _event_type = ann
            elif ann != None:
                assert ann == _event_type, _mismatch_error

            assert _event_type != None, _no_event_type_error

            @wraps(func)
            def handler(event, bot):
                func(event) if len(spec.args) == 1 else func(event, bot)

            print(f"adding {handler} to {self.name}")
            self._listeners.add_listener(EventListener(event=_event_type, func=handler))
            return func  # TODO should i return something else?

        return decorator
