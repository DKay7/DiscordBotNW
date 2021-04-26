from environs import Env

env = Env()
env.read_env()

# BOT CONFIGS
PREFIX = '\\'
TOKEN = env.str('TOKEN')
OWNER_IDS = env.list('OWNER_IDS')


# DIRECTORIES
COGS_DIR = r"bot/cogs/*.py"
TEMP_BAN_EMBEDS_DIR = r"data/embeds/temp_ban_embeds.json"
BAN_EMBEDS_DIR = r"data/embeds/ban_embeds.json"
WARN_EMBEDS_DIR = r"data/embeds/warn_embeds.json"


# DATABASE CONFIGS
DB_PATH = r"data/db/database.db"
BUILD_PATH = r"data/db/build.sql"
