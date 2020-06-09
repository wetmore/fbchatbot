from .events_handler import EventsHandler
from .core_events import CommandEvent
from .types_util import Bot


def register_core_commands(bot: EventsHandler):
    @bot.command("help")
    def help_cmd(event: CommandEvent, bot: Bot):
        """
        Show all commands, or use '.help <cmd>' to show help for the command with name <cmd>.
        """
        command = event.command_body
        commands = bot.get_all_commands(command)

        message = ""
        for name, doc in commands:
            message = message + f"*{name}*\n{doc}\n"

        if not message:
            message = f"No command found with name *{command}*."

        event.thread.send_text(message)

    @bot.command("ping")
    def ping_cmd(event: CommandEvent):
        """Ping the bot. Useful to see if it's working."""
        event.thread.send_text("PONG")
