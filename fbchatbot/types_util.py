from typing import Protocol, Optional

from fbchat import Event


class Bot(Protocol):
    def handle(self, event: Event):
        ...

    def get_all_commands(self, command: Optional[str] = None):
        ...
