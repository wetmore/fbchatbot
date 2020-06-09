from .plugin import base_plugin
from fbchat import MessageEvent


@base_plugin.listener()
def echo(e: MessageEvent):
    print("base: " + e.message.text)
