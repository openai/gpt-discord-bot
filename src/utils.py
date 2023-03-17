import logging
import discord
import re
from src.base import Message
from discord import Message as DiscordMessage
from typing import Optional, List
from src.constants import (
    ALLOWED_SERVER_IDS,
)
from src.constants import MAX_CHARS_PER_REPLY_MSG, INACTIVATE_THREAD_PREFIX


logger = logging.getLogger(__name__)


def discord_message_to_message(
        message: DiscordMessage,
        bot_name: str) -> Optional[Message]:
    if (
        message.type == discord.MessageType.thread_starter_message
        and message.reference.cached_message
        and len(message.reference.cached_message.embeds) > 0
        and len(message.reference.cached_message.embeds[0].fields) > 0
    ):
        field = message.reference.cached_message.embeds[0].fields[0]
        logger.info(
            f"field.name - {field.name}"
        )
        return Message(user="system", text=field.value)
    else:
        if message.content:
            user_name = "assistant" if message.author == bot_name else "user"
            return Message(user=user_name, text=message.content)
    return None


def split_into_shorter_messages(message: str) -> List[str]:
    indices_object = re.finditer(
        pattern='```',
        string=message)

    indices = [index.start() for index in indices_object]
    indices[1::2] = [x + 4 for x in indices[1::2]]
    indices.insert(0, 0)
    indices.append(len(message))

    result = []
    for i in range(1, len(indices)):
        result.append(message[indices[i-1]:indices[i]])

    return result


def is_last_message_stale(
    interaction_message: DiscordMessage, last_message: DiscordMessage, bot_id: str
) -> bool:
    return (
        last_message
        and last_message.id != interaction_message.id
        and last_message.author
        and last_message.author.id != bot_id
    )


async def close_thread(thread: discord.Thread):
    await thread.edit(name=INACTIVATE_THREAD_PREFIX)
    await thread.send(
        embed=discord.Embed(
            description="**Thread closed** - Context limit reached, closing...",
            color=discord.Color.blue(),
        )
    )
    await thread.edit(archived=True, locked=True)


def should_block(guild: Optional[discord.Guild]) -> bool:
    if guild is None:
        # dm's not supported
        logger.info(f"DM not supported")
        return True

    if guild.id and guild.id not in ALLOWED_SERVER_IDS:
        # not allowed in this server
        logger.info(f"Guild {guild} not allowed")
        return True
    return False
