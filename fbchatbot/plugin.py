from abc import ABC, abstractmethod
from typing import List

from .command import Command
from .event_listener import EventListener
from .types_util import Bot


class Plugin(ABC):
    """TODO: docs
    """

    @property
    @abstractmethod
    def name(self) -> str:
        # TODO Should I just use `type(plugin_instance).__name__` instead of this?
        raise NotImplementedError

    @property
    def listeners(self) -> List[EventListener]:
        return []

    @property
    def commands(self) -> List[Command]:
        return []

    def on_load(self, bot: Bot):
        # Do nothing by default
        pass
