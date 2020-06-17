import config
from fbchatbot import *
from fbchatbot.core_events import CommandEvent, TextMessageEvent


use_config(config)
bot = add_bot("bot1").claim_threads(config.THREADS["my_thread"])


@bot.listener
def my_echo(e: TextMessageEvent):
    print(e.text)


@bot.command("hi")
def say_hi(e: CommandEvent):
    """Say hi back"""
    e.thread.send_text("Hello")


# bot.listen()
