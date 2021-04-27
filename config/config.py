from environs import Env

env = Env()
env.read_env()

# BOT CONFIGS
PREFIX = '\\'
TOKEN = env.str('TOKEN')
OWNER_IDS = env.list('OWNER_IDS')
NUM_WARNS_TO_TEMP_BAN = 3
TIME_TO_TEMP_BAN = "24h"

# DIRECTORIES
COGS_DIR = r"bot/cogs/*.py"
TEMP_BAN_EMBEDS_DIR = r"data/embeds/temp_ban_embeds.json"
BAN_EMBEDS_DIR = r"data/embeds/ban_embeds.json"
KICK_EMBEDS_DIR = r"data/embeds/kick_embeds.json"
WARN_EMBEDS_DIR = r"data/embeds/warn_embeds.json"
MUTE_EMBEDS_DIR = r"data/embeds/mute_embeds.json"
UNMUTE_EMBEDS_DIR = r"data/embeds/unmute_embeds.json"


# DATABASE CONFIGS
WARN_NUM_STORED_REASONS = 10
DB_PATH = r"data/db/database.db"
BUILD_PATH = r"data/db/build.sql"
