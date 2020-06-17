from typing import Callable, Optional

import attr
from fbchat import MessageData

from .types_util import Bot
from .core_events import CommandEvent
from .util import Colors


@attr.s
class Command:
    #: The string which triggers the command
    command: str = attr.ib()

    #: Help string documenting the command
    docs: str = attr.ib()

    #: Function invoked when command is called.
    func: Callable[[CommandEvent, Bot], None] = attr.ib()

    def pretty(self):
        """Pretty print command, for info-level logging."""
        return f"{Colors.blue(self.command)} ⟶  {Colors.green(self.func.__name__)}"
