from .db_connection import conn, cursor
from .db_build_utils import with_commit
from json import loads, dumps
from config.config import WARN_NUM_STORED_REASONS


def get_warn_entry(user_id):
    cursor.execute("SELECT * FROM warns WHERE UserID=?", (user_id, ))

    return cursor.fetchone()


@with_commit
def update_warn_entry(user_id, new_reason):
    num_warns = 1
    reasons = list()

    if entry := get_warn_entry(user_id):
        _, num_warns, reasons = entry
        num_warns += 1
        reasons = loads(reasons)
        reasons.append(new_reason)
        reasons = dumps(reasons[-WARN_NUM_STORED_REASONS:])
        cursor.execute("UPDATE warns SET NumWarns=?, LastReasons=? WHERE UserID=?", (num_warns, reasons, user_id))

    else:
        reasons.append(new_reason)
        reasons = dumps(reasons)
        cursor.execute("INSERT INTO warns VALUES (?, ?, ?)", (user_id, num_warns, reasons))

