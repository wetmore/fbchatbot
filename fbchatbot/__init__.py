"""Yadda yadda yadda
"""

from .chatbot_manager import ChatbotManager

#: Expose the Plugin class, used to define bot plugins
from .plugin import Plugin

default_manager = ChatbotManager()

use_config = default_manager.use_config
add_bot = default_manager.add_bot
assign_thread = default_manager.assign_thread
start = default_manager.start


__version__ = "0.1.0"
__all__ = [
    "Plugin",
    "use_config",
    "add_bot",
    "assign_thread",
    "start",
]
