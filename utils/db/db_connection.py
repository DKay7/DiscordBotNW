from sqlite3 import connect, PARSE_DECLTYPES
from config.db.db_config import DB_PATH

conn = connect(DB_PATH, detect_types=PARSE_DECLTYPES)
cursor = conn.cursor()
