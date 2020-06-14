from typing import Any, Callable, Optional

import attr

from .events_handler import EventsHandler


@attr.s
class Plugin(EventsHandler):
    """
    TODO: docs
    """

    #: Name used to refer to the plugin, e.g. when writing config.py for a bot.
    name: str = attr.ib(kw_only=True)

    on_load: Optional[Callable[[Any, Any], None]] = attr.ib(default=None)
