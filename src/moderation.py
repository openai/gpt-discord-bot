from openai._compat import model_dump

from src.constants import (
    SERVER_TO_MODERATION_CHANNEL,
    MODERATION_VALUES_FOR_BLOCKED,
    MODERATION_VALUES_FOR_FLAGGED,
)
from openai import OpenAI

client = OpenAI()
from typing import Optional, Tuple
import discord
from src.utils import logger


def moderate_message(
    message: str, user: str
) -> Tuple[str, str]:  # [flagged_str, blocked_str]
    moderation_response = client.moderations.create(
        input=message, model="text-moderation-latest"
    )
    category_scores = moderation_response.results[0].category_scores or {}

    category_score_items = model_dump(category_scores)

    blocked_str = ""
    flagged_str = ""
    for category, score in category_score_items.items():
        if score > MODERATION_VALUES_FOR_BLOCKED.get(category, 1.0):
            blocked_str += f"({category}: {score})"
            logger.info(f"blocked {user} {category} {score}")
            break
        if score > MODERATION_VALUES_FOR_FLAGGED.get(category, 1.0):
            flagged_str += f"({category}: {score})"
            logger.info(f"flagged {user} {category} {score}")
    return (flagged_str, blocked_str)


async def fetch_moderation_channel(
    guild: Optional[discord.Guild],
) -> Optional[discord.abc.GuildChannel]:
    if not guild or not guild.id:
        return None
    moderation_channel = SERVER_TO_MODERATION_CHANNEL.get(guild.id, None)
    if moderation_channel:
        channel = await guild.fetch_channel(moderation_channel)
        return channel
    return None


async def send_moderation_flagged_message(
    guild: Optional[discord.Guild],
    user: str,
    flagged_str: Optional[str],
    message: Optional[str],
    url: Optional[str],
):
    if guild and flagged_str and len(flagged_str) > 0:
        moderation_channel = await fetch_moderation_channel(guild=guild)
        if moderation_channel:
            message = message[:100] if message else None
            await moderation_channel.send(
                f"⚠️ {user} - {flagged_str} - {message} - {url}"
            )


async def send_moderation_blocked_message(
    guild: Optional[discord.Guild],
    user: str,
    blocked_str: Optional[str],
    message: Optional[str],
):
    if guild and blocked_str and len(blocked_str) > 0:
        moderation_channel = await fetch_moderation_channel(guild=guild)
        if moderation_channel:
            message = message[:500] if message else None
            await moderation_channel.send(f"❌ {user} - {blocked_str} - {message}")
