import config
from fbchatbot import *
from fbchatbot.core_events import CommandEvent, TextMessageEvent


class TestPlugin(Plugin):
    def __init__(self):
        self.counter = 0

    @property
    def name(self):
        return "Test Plugin"

    @command("inc")
    def count(self, event: CommandEvent):
        """increment"""
        self.counter += 1
        event.thread.send_text(f"Counter at {self.counter}")


use_config(config)
bot = add_bot("bot1")
bot.claim_threads(config.THREADS["my_thread"])
bot.load_plugin(TestPlugin())


@bot.listener
def my_echo(e: TextMessageEvent):
    print(e.text)


@bot.command("hi")
def say_hi(e: CommandEvent):
    """Say hi back"""
    e.thread.send_text("Hello")


# bot.listen()
