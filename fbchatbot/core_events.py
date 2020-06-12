"""
Events core to 
"""

from typing import Optional, TYPE_CHECKING
import re

import attr
import fbchat

from .types_util import Bot


@attr.s(slots=True, kw_only=True, frozen=True)
class MessageEvent(fbchat.MessageEvent):
    """
    Represents a message event sent by someone that isn't the bot. Also merges fbchat.MessageEvent and
    fbchat.MessageReplyEvent, so that if a message has a reply it will still trigger event handlers listening
    to MessageEvents.
    """

    replied_to: Optional[fbchat.MessageData] = attr.ib(None)


@attr.s(slots=True, kw_only=True, frozen=True)
class MentionEvent(MessageEvent):
    """Represents an event where the bot is mentioned in a message."""

    #: The Mention object mentioning the bot
    mention: fbchat.Mention = attr.ib()


@attr.s(slots=True, kw_only=True, frozen=True)
class CommandEvent(MessageEvent):
    """
    Represents a command to the bot. Commands can be issued by referencing the bot in the beginning of the message,
    or just by starting the message with a period (which can be typed using a phone keyboard without needing to
    tap into the symbols keyboard).
    """

    #: The command string
    command: str = attr.ib()

    #: The body of the command, ie text after the command string.
    command_body: str = attr.ib()


def _fbMessage_to_message(event: fbchat.MessageEvent, bot: Bot):
    bot_id = event.thread.session.user.id
    if event.author.id != bot_id:
        bot.handle(
            MessageEvent(  # type: ignore
                author=event.author,
                thread=event.thread,
                message=event.message,
                at=event.at,
            )
        )


def _fbMessageReply_to_message(event: fbchat.MessageReplyEvent, bot: Bot):
    bot_id = event.thread.session.user.id
    if event.author.id != bot_id:
        bot.handle(
            MessageEvent(  # type: ignore
                author=event.author,
                thread=event.thread,
                message=event.message,
                at=event.message.created_at,
                # BUG this doesn't seem to be populated when you reply to yourself
                replied_to=event.replied_to,
            )
        )


def _message_to_mention(event: MessageEvent, bot: Bot):
    bot_id = event.thread.session.user.id
    for mention in event.message.mentions:
        if mention.thread_id == str(bot_id):
            bot.handle(
                MentionEvent(  # type: ignore
                    author=event.author,
                    thread=event.thread,
                    message=event.message,
                    at=event.at,
                    mention=mention,
                )
            )


cmd_regex = re.compile("^(\w+)(.*)")
cmd_regex_dot = re.compile("^\.(\w+)(.*)")


def _mention_to_command(event: MentionEvent, bot: Bot):
    if event.mention.offset == 0:
        match = cmd_regex.match(event.message.text[event.mention.length :].strip())
        if match:
            command, body = match.groups()
            bot.handle(
                CommandEvent(  # type: ignore
                    author=event.author,
                    thread=event.thread,
                    message=event.message,
                    at=event.at,
                    command=command,
                    command_body=body.strip(),
                )
            )


def _message_to_command(event: MessageEvent, bot: Bot):
    match = cmd_regex_dot.match(event.message.text)
    if match:
        command, body = match.groups()
        bot.handle(
            CommandEvent(  # type: ignore
                author=event.author,
                thread=event.thread,
                message=event.message,
                at=event.at,
                command=command,
                command_body=body.strip(),
            )
        )


core_listeners = [
    _fbMessage_to_message,
    _fbMessageReply_to_message,
    _message_to_mention,
    _mention_to_command,
    _message_to_command,
]
