from typing import Protocol

from fbchat import Event


class Bot(Protocol):
    def handle(self, event: Event):
        ...
