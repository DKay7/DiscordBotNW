from config.config import DB_PATH
from sqlite3 import connect

conn = connect(DB_PATH)
cursor = conn.cursor()
