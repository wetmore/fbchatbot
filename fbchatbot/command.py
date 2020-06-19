from typing import Any, Optional, Protocol
import inspect
from types import MethodType

import attr

from .core_events import CommandEvent
from .types_util import Bot
from .util import Colors

# TODO this is technically not complete, as a Command may wrap an unbound method,
# when the @listener decorator is used above a method definition.
class CommandHandler(Protocol):
    def __call__(self, event: CommandEvent, bot: Optional[Bot] = None):
        ...


@attr.s
class Command:
    #: The string which triggers the command
    name: str = attr.ib()

    #: Help string documenting the command
    docs: str = attr.ib()

    #: Function invoked when command is called.
    func: CommandHandler = attr.ib()

    def bind(self, obj):
        self.func = MethodType(self.func, obj)

    def execute(self, event: Any, bot: Bot):
        spec = inspect.getfullargspec(self.func)
        if type(self.func) == MethodType:
            needs_bot_arg = len(spec.args) == 3
        else:
            needs_bot_arg = len(spec.args) == 2
        self.func(event, bot) if needs_bot_arg else self.func(event)

    def pretty(self):
        """Pretty print command, for info-level logging."""
        return f"{Colors.blue(self.name)} ⟶  {Colors.green(self.func.__name__)}"


def command(cmd_name: str):
    """Decorator for defining commands.

    Args:
        cmd_name (str): The string used to invoke the command in a chat session.

    Decorate a callback function to call it when a user issues a command to the bot.
    The decorated function may take either 1 or 2 arguments; either just the
    `core_events.CommandEvent` which triggered the callback, or the
    `core_events.CommandEvent` and a reference to the `fbchatbot.types_util.Bot`
    which received the event. The docstring for the callback will be used to provide
    the docs for the command, which are shown when the core event `help_cmd` is
    invoked.

    Examples:
        Create an event which echos its argument: e.g.
            User: .echo this string

            Bot: this string

        >>> @bot.command("echo")
        >>> def echo(e: CommandEvent):
        >>>     \"\"\"Echo provided string\"\"\"
        >>>     e.thread.send_text(e.command_body)

        Trigger an event in response to the command:

        >>> @bot.command("trigger_event")
        >>> def trigger_event(e: CommandEvent, b: Bot):
        >>>     \"\"\"Trigger event\"\"\"
        >>>     b.handle(MyEvent())

    """

    def decorator(func: CommandHandler):

        # TODO add assertions?

        # Strip any indentation on the docstring
        docs = (func.__doc__ or "").strip()

        return Command(name=cmd_name, docs=docs, func=func)

    return decorator
