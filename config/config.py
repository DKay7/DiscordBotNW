from environs import Env

env = Env()
env.read_env()

# BOT CONFIGS
PREFIX = '\\'
TOKEN = env.str('TOKEN')
OWNER_IDS = env.list('OWNER_IDS')
NUM_WARNS_TO_TEMP_BAN = 3
TIME_TO_TEMP_BAN = "24h"
GUILD_ID = env.int("GUILD_ID")
WARS_CHANNEL_ID = 838043159409590343
COMMON_RATING_CHANNEL_ID = 838043054698921985

# DIRECTORIES
COGS_DIR = r"bot/cogs/*.py"

# EMBEDS DIRECTORIES
TEMP_BAN_EMBEDS_DIR = r"data/embeds/temp_ban_embeds.json"
BAN_EMBEDS_DIR = r"data/embeds/ban_embeds.json"
KICK_EMBEDS_DIR = r"data/embeds/kick_embeds.json"
WARN_EMBEDS_DIR = r"data/embeds/warn_embeds.json"
MUTE_EMBEDS_DIR = r"data/embeds/mute_embeds.json"
UNMUTE_EMBEDS_DIR = r"data/embeds/unmute_embeds.json"

# MESSAGES DIRECTORIES
CLAN_LEADER_OFFER_MESSAGE_DIR = r"data/messages/clan_leader_offer.json"

# ROLES PERMISSION DIRECTORY
CLAN_LEADER_ROLE = r"data/permissions_and_roles/clan_leader/role_config.json"
CLAN_MEMBER_ROLE = r"data/permissions_and_roles/clan_leader_deputy/role_config.json"
CLAN_DEP_ROLE = r"data/permissions_and_roles/clan_member/role_config.json"

# CLAN'S CHATS PERMISSION DIRECTORY
user_types = ["clan_leader", "clan_leader_deputy", "clan_member"]
channels = ["chat", "voice", "rating"]
CLAN_CHANNELS_PERMS_PATTERN = "data/permissions_and_roles/{user_type}/[{channel_type}]_permissions.json"

# DATABASE CONFIGS
WARN_NUM_STORED_REASONS = 10
DB_PATH = r"data/db/database.db"
BUILD_PATH = r"data/db/build.sql"
