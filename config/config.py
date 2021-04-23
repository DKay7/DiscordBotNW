from environs import Env

env = Env()
env.read_env()

# BOT CONFIGS
PREFIX = '\\'
TOKEN = env.str('TOKEN')
OWNER_IDS = env.list('OWNER_IDS')
COGS_DIR = r"bot/cogs/*.py"


# DATABASE CONFIGS
DB_PATH = r"data/db/database.db"
BUILD_PATH = r"data/db/build.sql"
