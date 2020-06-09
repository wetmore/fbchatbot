import config
from fbchat import MessageEvent
from patrick import Patrick, CommandEvent


bot = Patrick(config=config)


@bot.listener()
def my_echo(e: MessageEvent):
    print("bot: " + e.message.text)


@bot.command("hi")
def say_hi(e: CommandEvent):
    """Say hi back"""
    e.thread.send_text("Hello")


# bot.listen()
