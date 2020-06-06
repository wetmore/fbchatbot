import inspect
from typing import Callable, Dict, Iterator, List, Type, Optional, TYPE_CHECKING

import attr

from .type_util import Event, Bot


Handler = Callable[[Event, Optional[Bot]], None]


@attr.s
class EventListener:
    """A function associated with an event type which triggers it."""

    event: Type[Event] = attr.ib()
    func: Handler = attr.ib()


@attr.s
class EventListeners:
    """A group of multiple event listeners."""

    _registry: Dict[Type[Event], List[EventListener]] = attr.ib(attr.Factory(dict))

    def add_listener(self, listener: EventListener):
        """Add a listener to the listener registry."""
        try:
            listeners_for_event = self._registry[listener.event]
        except KeyError:
            listeners_for_event = []
        listeners_for_event.append(listener)
        self._registry[listener.event] = listeners_for_event

    def add_listeners(self, listeners: Iterator[EventListener]):
        """Add all listeners in an iterator to the listener registry."""
        for listener in listeners:
            self.add_listener(listener)

    def handle(self, event: Event, bot: Bot):
        """Call all registered listeners for a given event."""
        try:
            listeners_for_event = self._registry[type(event)]
            for listener in listeners_for_event:
                listener.func(event, bot)
        except KeyError:
            pass  # No handler for that type registered
