import config
from fbchatbot import Chatbot
from fbchatbot.core_events import CommandEvent, TextMessageEvent


bot = Chatbot(config=config)


@bot.listener
def my_echo(e: TextMessageEvent):
    print(e.text)


@bot.command("hi")
def say_hi(e: CommandEvent):
    """Say hi back"""
    e.thread.send_text("Hello")


# bot.listen()
