from dotenv import load_dotenv
import os
import dacite
import yaml
from typing import Dict, List
from src.base import (Config, Conversation)

load_dotenv()


# load config.yaml
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG: Config = dacite.from_dict(
    Config, yaml.safe_load(open(os.path.join(SCRIPT_DIR, "config.yaml"), "r"))
)

BOT_NAME: str = CONFIG.name
BOT_INSTRUCTIONS: str = CONFIG.instructions
EXAMPLE_CONVOS: List[Conversation] = CONFIG.example_conversations

DISCORD_BOT_TOKEN: str = os.environ["DISCORD_BOT_TOKEN"]
DISCORD_CLIENT_ID: str = os.environ["DISCORD_CLIENT_ID"]
OPENAI_API_KEY: str = os.environ["OPENAI_API_KEY"]

ALLOWED_SERVER_IDS: List[int] = [
    int(s) for s in os.environ["ALLOWED_SERVER_IDS"].split(",")]

SERVER_TO_MODERATION_CHANNEL: Dict[int, int] = {}
for s in os.environ.get("SERVER_TO_MODERATION_CHANNEL", "").split(","):
    values = s.split(":")
    SERVER_TO_MODERATION_CHANNEL[int(values[0])] = int(values[1])

# Send Messages, Create Public Threads, Send Messages in Threads, Manage Messages, Manage Threads, Read Message History, Use Slash Command
BOT_INVITE_URL = f"https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&permissions=328565073920&scope=bot"

SECONDS_DELAY_RECEIVING_MSG = (
    3  # give a delay for the bot to respond so it can catch multiple messages
)
MAX_THREAD_MESSAGES = 50
ACTIVATE_THREAD_PREFX = "💬✅"
INACTIVATE_THREAD_PREFIX = "💬❌"
MAX_CHARS_PER_REPLY_MSG = (
    1500  # discord has a 2k limit, we just break message into 1.5k
)
