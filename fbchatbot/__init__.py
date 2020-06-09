
# Expose the Chatbot class, used to define a bot
from .fbchatbot import Chatbot

# Expose the Plugin class, used to define bot plugins
from .plugin import Plugin

# Expose events
from .core_events import (MessageEvent, MentionEvent, CommandEvent)

__version__ = "0.1.0"
