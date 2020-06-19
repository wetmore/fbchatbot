"""Events core to the operation of Chatbots.

This module contains events which make working with `fbchat` easier for the purposes of
writing a chatbot, as well as events which power the command-handling functionality
of `fbchatbot`.
"""

from typing import List, Optional
import re
from datetime import datetime

import attr
import fbchat

from .event_listener import listener, EventListener
from .types_util import Bot


@attr.s(slots=True, kw_only=True, frozen=True)
class MessageEvent(fbchat.MessageEvent):
    """
    Represents a message event sent by someone that isn't the bot. Also merges
    fbchat.MessageEvent and fbchat.MessageReplyEvent, so that if a message is a reply it
    will still trigger event handlers listening to MessageEvents.
    """

    # TODO a few of the events which inherit don't pass this through
    replied_to: Optional[fbchat.MessageData] = attr.ib(None)


@attr.s(slots=True, kw_only=True, frozen=True)
class TextMessageEvent(MessageEvent):
    """Represents a message which contains text"""

    #: The text in the message
    text: str = attr.ib()


@attr.s(slots=True, kw_only=True, frozen=True)
class ImageMessageEvent(MessageEvent):
    """Represents a message which consists of one or more images"""

    #: The image attachments in the message. See fbchat.ImageAttachment for details.
    image_attachments: List[fbchat.ImageAttachment] = attr.ib()


@attr.s(slots=True, kw_only=True, frozen=True)
class EmojiMessageEvent(MessageEvent):
    """Represents a message which is only an emoji. May have a size"""

    # TODO should I normalize the thumbs up to be an emoji?

    #: The images in the message
    emoji: str = attr.ib()

    #: The size of the emoji
    emoji_size: Optional[fbchat.EmojiSize] = attr.ib()


@attr.s(slots=True, kw_only=True, frozen=True)
class StickerMessageEvent(MessageEvent):
    """Represents a message which is a sticker"""

    #: The sticker
    sticker: fbchat.Sticker = attr.ib()


@attr.s(slots=True, kw_only=True, frozen=True)
class OtherMessageEvent(MessageEvent):
    """
    Represents a message which can not be characterised as one of the other
    `fbchatbot.MessageEvent`s
    """

    #: The sticker
    sticker: fbchat.Sticker = attr.ib()


@attr.s(slots=True, kw_only=True, frozen=True)
class MentionEvent(MessageEvent):
    """Represents an event where the bot is mentioned in a message."""

    #: The Mention object mentioning the bot
    mention: fbchat.Mention = attr.ib()


@attr.s(slots=True, kw_only=True, frozen=True)
class CommandEvent(MessageEvent):
    """
    Represents a command to the bot. Commands can be issued by referencing the bot in
    the beginning of the message, or just by starting the message with a period (which
    can be typed using a phone keyboard without needing to tap into the symbols
    keyboard).
    """

    #: The command string
    command: str = attr.ib()

    #: The body of the command, ie text after the command string.
    command_body: str = attr.ib()


@attr.s(slots=True, kw_only=True, frozen=True)
class ReactionEvent(fbchat.ReactionEvent):
    """Represents a reaction to a message.

    Same as fbchat.ReactionEvent, but with added `at` attribute.
    """

    #: When the reaction was recorded
    at: datetime = attr.ib()


def parse_event_from_message(
    event: fbchat.MessageEvent, reply: Optional[fbchat.MessageData] = None
) -> MessageEvent:
    message: fbchat.MessageData = event.message
    if message.text:
        # TODO: create EmojiMessage, but that's somewhat complicated
        # (see https://stackoverflow.com/a/39425959/1055926)
        # might be able to leverege emojis package
        return TextMessageEvent(  # type: ignore
            author=event.author,
            thread=event.thread,
            message=event.message,
            at=event.at,
            replied_to=reply,
            text=event.message.text,
        )
    if message.sticker:
        return StickerMessageEvent(  # type: ignore
            author=event.author,
            thread=event.thread,
            message=event.message,
            at=event.at,
            replied_to=reply,
            sticker=message.sticker,
        )
    images = []
    for attachment in message.attachments:
        if isinstance(attachment, fbchat.ImageAttachment):
            images.append(attachment)
    if images:
        return ImageMessageEvent(  # type: ignore
            author=event.author,
            thread=event.thread,
            message=event.message,
            at=event.at,
            replied_to=reply,
            image_attachments=images,
        )
    return OtherMessageEvent(  # type: ignore
        author=event.author,
        thread=event.thread,
        message=event.message,
        at=event.at,
        replied_to=reply,
    )


@listener
def _fbReaction_to_reaction(event: fbchat.ReactionEvent, bot: Bot):
    at = datetime.utcnow()
    bot.handle(
        ReactionEvent(  # type: ignore
            author=event.author,
            thread=event.thread,
            message=event.message,
            reaction=event.reaction,
            at=at,
        )
    )


@listener
def _fbMessage_to_message(event: fbchat.MessageEvent, bot: Bot):
    bot_id = event.thread.session.user.id
    if event.author.id != bot_id:
        bot.handle(parse_event_from_message(event))


@listener
def _fbMessageReply_to_message(event: fbchat.MessageReplyEvent, bot: Bot):
    bot_id = event.thread.session.user.id
    if event.author.id != bot_id:
        bot.handle(
            parse_event_from_message(
                fbchat.MessageEvent(  # type: ignore
                    author=event.author,
                    thread=event.thread,
                    message=event.message,
                    at=event.message.created_at,
                ),
                # BUG this doesn't seem to be populated when you reply to yourself
                reply=event.replied_to,
            )
        )


@listener
def _message_to_mention(event: TextMessageEvent, bot: Bot):
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


cmd_regex = re.compile("^(\S+)(.*)")
cmd_regex_dot = re.compile("^\.(\S+)(.*)")


@listener
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


@listener
def _message_to_command(event: TextMessageEvent, bot: Bot):
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


core_listeners: List[EventListener] = [
    _fbMessage_to_message,
    _fbMessageReply_to_message,
    _fbReaction_to_reaction,
    _message_to_mention,
    _mention_to_command,
    _message_to_command,
]
