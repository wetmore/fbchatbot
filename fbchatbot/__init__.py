"""Yadda yadda yadda
"""

#: Expose the Chatbot class, used to define a bot
from .fbchatbot import Chatbot

#: Expose the Plugin class, used to define bot plugins
from .plugin import Plugin


__version__ = "0.1.0"
__all__ = [
    "Chatbot",
    "Plugin",
]
