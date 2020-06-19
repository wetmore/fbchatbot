from typing import Protocol, Any

from fbchat import Event


class Bot(Protocol):
    db: Any

    def handle(self, event: Event):
        ...

    def get_all_commands(self, specified_command: str = ""):
        ...
