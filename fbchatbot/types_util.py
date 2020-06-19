from typing import Protocol, Any


class Bot(Protocol):
    db: Any

    def handle(self, event: Any):
        ...

    def get_all_commands(self, specified_command: str = ""):
        ...
