import config
from fbchat import MessageEvent
from fbchatbot import Chatbot, CommandEvent


bot = Chatbot(config=config)


@bot.listener()
def my_echo(e: MessageEvent):
    print("bot: " + e.message.text)


@bot.command("hi")
def say_hi(e: CommandEvent):
    """Say hi back"""
    e.thread.send_text("Hello")


# bot.listen()
