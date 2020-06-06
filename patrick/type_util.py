from typing import Protocol

import fbchat

Event = fbchat.Event


class Bot(Protocol):
    def handle_event(self, event: Event) -> None:
        ...
