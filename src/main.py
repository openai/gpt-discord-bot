from bs4 import BeautifulSoup
import requests
import discord
import openai
from discord import Message as DiscordMessage
import logging
from src.base import Message, Conversation
from src.constants import (
    BOT_INVITE_URL,
    CONFIG,
    DISCORD_BOT_TOKEN,
    ACTIVATE_THREAD_PREFX,
    MAX_THREAD_MESSAGES,
    SECONDS_DELAY_RECEIVING_MSG,
)
import asyncio
from src.utils import (
    logger,
    should_allow,
    close_thread,
    is_last_message_stale,
    discord_message_to_message,
)
from src import completion
from src.completion import generate_completion_response, process_response

logging.basicConfig(
    format="[%(asctime)s] [%(filename)s:%(lineno)d] %(message)s", level=logging.INFO
)

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)


@client.event
async def on_ready():
    logger.info(
        f"We have logged in as {client.user}. Invite URL: {BOT_INVITE_URL}")
    await tree.sync()


@tree.command(name="cornerstone", description="Print out wenard's prime directives.")
@discord.app_commands.checks.has_permissions(send_messages=True)
@discord.app_commands.checks.has_permissions(view_channel=True)
@discord.app_commands.checks.bot_has_permissions(send_messages=True)
@discord.app_commands.checks.bot_has_permissions(view_channel=True)
@discord.app_commands.checks.bot_has_permissions(manage_threads=True)
async def cornerstone_command(interaction: discord.Interaction):
    try:
        if not isinstance(interaction.channel, discord.TextChannel):
            return
        if not should_allow(guild=interaction.guild):
            return
        embed = discord.Embed(
            description=f"🤖💬 My name is wenard and my primary directive is:\n`{CONFIG.instructions}`",
            color=discord.Color.blue(),
        )
        embed.add_field(name=interaction.user.name,
                        value=f"For a full list of my configuration, go to https://github.com/wmedrano/wenard/blob/main/src/config.yaml.")
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        logger.exception(e)


@tree.command(name="wenard", description="wenard will reply to the last comment.")
@discord.app_commands.checks.has_permissions(send_messages=True)
@discord.app_commands.checks.has_permissions(view_channel=True)
@discord.app_commands.checks.bot_has_permissions(send_messages=True)
@discord.app_commands.checks.bot_has_permissions(view_channel=True)
async def wenard_command(interaction: discord.Interaction):
    try:
        if not should_allow(guild=interaction.guild):
            return
        async with interaction.channel.typing():
            last_message_id = interaction.channel.last_message_id
            if last_message_id is None:
                await interaction.response.send_message("Sorry, I couldn't find the last message.")
                return
            last_message = await interaction.channel.fetch_message(last_message_id)
            logger.info(
                f"/wenard triggered by {interaction.user} for ({interaction.channel.last_message_id}) {last_message.author.name}: {last_message.content[:20]}")
            await interaction.response.defer()
            message = Message(
                user=last_message.author.name, text=last_message.content)
            response_data = await generate_completion_response(messages=[message], user=interaction.user)
            reply = ''
            if response_data.status == completion.CompletionResult.OK:
                reply = response_data.reply_text
            else:
                reply = f"I've hit my limits. {response_data.status_text}"
            await interaction.followup.send(content=reply)
    except Exception as e:
        logger.exception(e)


@tree.command(name="chat", description="Create a new thread for conversation.")
@discord.app_commands.checks.has_permissions(send_messages=True)
@discord.app_commands.checks.has_permissions(view_channel=True)
@discord.app_commands.checks.bot_has_permissions(send_messages=True)
@discord.app_commands.checks.bot_has_permissions(view_channel=True)
@discord.app_commands.checks.bot_has_permissions(manage_threads=True)
async def chat_command(interaction: discord.Interaction, message: str):
    try:
        if not isinstance(interaction.channel, discord.TextChannel):
            return
        if not should_allow(guild=interaction.guild):
            return

        user = interaction.user
        logger.info(f"/chat triggered by {user} {message[:20]}")
        try:
            embed = discord.Embed(
                description=f"<@{user.id}> wants to chat! 🤖💬",
                color=discord.Color.green(),
            )
            embed.add_field(name=user.name, value=message)

            await interaction.response.send_message(embed=embed)
            response = await interaction.original_response()

        except Exception as e:
            logger.exception(e)
            await interaction.response.send_message(
                f"Failed to start chat {str(e)}", ephemeral=True
            )
            return

        # create the thread
        thread = await response.create_thread(
            name=f"{ACTIVATE_THREAD_PREFX} {user.name[:20]} - {message[:30]}",
            slowmode_delay=1,
            reason="gpt-bot",
            auto_archive_duration=60,
        )
        async with thread.typing():
            # fetch completion
            messages = [Message(user=user.name, text=message)]
            response_data = await generate_completion_response(
                messages=messages, user=user
            )
            # send the result
            await process_response(
                thread=thread, response_data=response_data
            )
    except Exception as e:
        logger.exception(e)
        await interaction.response.send_message(
            f"Failed to start chat {str(e)}", ephemeral=True
        )


async def summary(url: str) -> str:
    """Summarize the text."""
    response = requests.get(url)
    content = BeautifulSoup(response.text, features='lxml').get_text()
    rendered = f"Summarize the following web page:\n<|endoftext|>{content}<|endoftext|>"
    gpt_response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=rendered,
        temperature=1.0,
        top_p=0.9,
        max_tokens=512,
        stop=["<|endoftext|>"],
    )
    return gpt_response.choices[0].text.strip()


@tree.command(name="summarize", description="beta - Summarize the contents of a url.")
@discord.app_commands.checks.has_permissions(send_messages=True)
@discord.app_commands.checks.has_permissions(view_channel=True)
@discord.app_commands.checks.bot_has_permissions(send_messages=True)
@discord.app_commands.checks.bot_has_permissions(view_channel=True)
@discord.app_commands.checks.bot_has_permissions(manage_threads=True)
async def summarize_command(interaction: discord.Interaction, message: str):
    try:
        if not isinstance(interaction.channel, discord.TextChannel):
            return
        if not should_allow(guild=interaction.guild):
            return

        logger.info(
            f"/summarize triggered by {interaction.user} {message[:20]}")
        await interaction.response.defer()
        try:
            await interaction.followup.send(content=await summary(message.strip()))
        except:
            await interaction.followup.send(content="The content was too much for me! I'm sorry.")

    except Exception as e:
        logger.exception(e)


# calls for each message
@client.event
async def on_message(message: DiscordMessage):
    try:
        if not should_allow(guild=message.guild):
            return

        # ignore messages from the bot
        if message.author == client.user:
            return

        # ignore messages not in a thread
        channel = message.channel
        if not isinstance(channel, discord.Thread):
            return

        # ignore threads not created by the bot
        thread = channel
        if thread.owner_id != client.user.id:
            return

        # ignore threads that are archived locked or title is not what we want
        if (
            thread.archived
            or thread.locked
            or not thread.name.startswith(ACTIVATE_THREAD_PREFX)
        ):
            return

        if thread.message_count > MAX_THREAD_MESSAGES:
            # too many messages, no longer going to reply
            await close_thread(thread=thread)
            return

        # wait a bit in case user has more messages
        if SECONDS_DELAY_RECEIVING_MSG > 0:
            await asyncio.sleep(SECONDS_DELAY_RECEIVING_MSG)
            if is_last_message_stale(
                interaction_message=message,
                last_message=thread.last_message,
                bot_id=client.user.id,
            ):
                # there is another message, so ignore this one
                return

        logger.info(
            f"Thread message to process - {message.author}: {message.content[:50]} - {thread.name} {thread.jump_url}"
        )

        channel_messages = [
            discord_message_to_message(message)
            async for message in thread.history(limit=MAX_THREAD_MESSAGES)
        ]
        channel_messages = [x for x in channel_messages if x is not None]
        channel_messages.reverse()

        # generate the response
        async with thread.typing():
            response_data = await generate_completion_response(
                messages=channel_messages, user=message.author
            )

        if is_last_message_stale(
            interaction_message=message,
            last_message=thread.last_message,
            bot_id=client.user.id,
        ):
            # there is another message and its not from us, so ignore this response
            return

        # send response
        await process_response(
            thread=thread, response_data=response_data)
    except Exception as e:
        logger.exception(e)

client.run(DISCORD_BOT_TOKEN)
