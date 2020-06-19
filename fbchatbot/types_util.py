from typing import Protocol

from fbchat import Event


class Bot(Protocol):
    def handle(self, event: Event):
        ...

    def get_all_commands(self, specified_command: str = ""):
        ...
