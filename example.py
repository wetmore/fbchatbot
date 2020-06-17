import config
from fbchatbot import ChatbotManager
from fbchatbot.core_events import CommandEvent, TextMessageEvent


bots = ChatbotManager(config=config)
bot = bots.add_bot("bot1")


@bot.listener
def my_echo(e: TextMessageEvent):
    print(e.text)


@bot.command("hi")
def say_hi(e: CommandEvent):
    """Say hi back"""
    e.thread.send_text("Hello")


# bot.listen()
