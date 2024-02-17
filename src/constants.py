from dotenv import load_dotenv
import os
import dacite
import yaml
from typing import Dict, List, Literal

from src.base import Config

load_dotenv()


# load config.yaml
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG: Config = dacite.from_dict(
    Config, yaml.safe_load(open(os.path.join(SCRIPT_DIR, "config.yaml"), "r"))
)

BOT_NAME = CONFIG.name
BOT_INSTRUCTIONS = CONFIG.instructions
EXAMPLE_CONVOS = CONFIG.example_conversations

DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
DISCORD_CLIENT_ID = os.environ["DISCORD_CLIENT_ID"]
OPENAI_API_BASE = os.environ["OPENAI_API_BASE"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
DEFAULT_MODEL = os.environ["DEFAULT_MODEL"]

ALLOWED_SERVER_IDS: List[int] = []
server_ids = os.environ["ALLOWED_SERVER_IDS"].split(",")
for s in server_ids:
    ALLOWED_SERVER_IDS.append(int(s))

SERVER_TO_MODERATION_CHANNEL: Dict[int, int] = {}
server_channels = os.environ.get("SERVER_TO_MODERATION_CHANNEL", "").split(",")
for s in server_channels:
    values = s.split(":")
    SERVER_TO_MODERATION_CHANNEL[int(values[0])] = int(values[1])

# Send Messages, Create Public Threads, Send Messages in Threads, Manage Messages, Manage Threads, Read Message History, Use Slash Command
BOT_INVITE_URL = f"https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&permissions=328565073920&scope=bot"

MODERATION_VALUES_FOR_BLOCKED = {
    "harassment": 1.0,
    "harassment/threatening": 1.0,
    "hate": 1.0,
    "hate/threatening": 1.0,
    "self-harm": 1.0,
    "self-harm/instructions": 1.0,
    "self-harm/intent": 1.0,
    "sexual": 1.0,
    "sexual/minors": 1.0,
    "violence": 1.0,
    "violence/graphic": 1.0,
}

MODERATION_VALUES_FOR_FLAGGED = {
    "harassment": 1.0,
    "harassment/threatening": 1.0,
    "hate": 1.0,
    "hate/threatening": 1.0,
    "self-harm": 1.0,
    "self-harm/instructions": 1.0,
    "self-harm/intent": 1.0,
    "sexual": 1.0,
    "sexual/minors": 1.0,
    "violence": 1.0,
    "violence/graphic": 1.0,
}

SECONDS_DELAY_RECEIVING_MSG = (
    3  # give a delay for the bot to respond so it can catch multiple messages
)
MAX_THREAD_MESSAGES = 200
ACTIVATE_THREAD_PREFX = "💬✅"
INACTIVATE_THREAD_PREFIX = "💬❌"
MAX_CHARS_PER_REPLY_MSG = (
    1500  # discord has a 2k limit, we just break message into 1.5k
)

AVAILABLE_MODELS = Literal["gpt-3.5-turbo", "gpt-4", "gpt-4-1106-preview", "gpt-4-32k", "LoneStriker_OrcaMaid-v3-13b-32k-5.0bpw-h6-exl2"]
