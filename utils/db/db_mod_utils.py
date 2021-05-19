import sqlite3
from ..mod_utils.add_reason_sql import append_warn_reason, add_warn_reason, remove_warn_reason
from .db_build_utils import with_commit
from .db_connection import cursor, conn


conn.create_function("APPEND_REASON", 2, append_warn_reason)
conn.create_function("REMOVE_REASON", 1, remove_warn_reason)
conn.create_function("ADD_REASON", 1, add_warn_reason)


def get_warn_entry(user_id, guild_id):
    cursor.execute("SELECT * FROM warns WHERE (UserID=? AND GuildID=?)", (user_id, guild_id))
    return cursor.fetchone()


@with_commit
def update_warn_entry(user_id, guild_id, new_reason):
    num_warns = 1

    cursor.execute("INSERT INTO warns VALUES (?, ?, ?, ADD_REASON(?))"
                   "ON CONFLICT(UserID, GuildID) DO UPDATE "
                   "SET NumWarns=NumWarns+1, LastReasons=APPEND_REASON(LastReasons, ?)",
                   (user_id, guild_id, num_warns, new_reason, new_reason))


@with_commit
def unwarn_entry(user_id, guild_id):
    cursor.execute("UPDATE warns SET NumWarns=NumWarns-1, LastReasons=REMOVE_REASON(LastReasons) "
                   "WHERE (UserID=? AND GuildID=?)",
                   (user_id, guild_id))

    cursor.execute("DELETE FROM warns WHERE NumWarns <= 0")


@with_commit
def add_temp_ban_entry(user_id, end_time, guild_id):
    cursor.execute("INSERT OR REPLACE INTO temp_bans VALUES (?, ?, ?)",
                   (user_id, guild_id, end_time))


@with_commit
def delete_temp_ban_entry(user_id, guild_id):
    cursor.execute("DELETE FROM temp_bans WHERE (UserID=? AND GuildID=?)",
                   (user_id, guild_id))


def get_temp_ban_entry(user_id, guild_id):
    cursor.execute("SELECT * FROM temp_bans WHERE (UserID=? AND GuildID=?)",
                   (user_id, guild_id))
    return cursor.fetchone()


def get_all_temp_ban_entries():
    try:
        cursor.execute("SELECT * FROM temp_bans")
        return cursor.fetchall()

    except sqlite3.OperationalError:
        pass


@with_commit
def add_temp_mute_entry(user_id, end_time, mute_type, guild_id):
    cursor.execute("INSERT OR REPLACE INTO temp_mutes VALUES (?, ?, ?, ?)",
                   (user_id, guild_id, end_time, mute_type))


@with_commit
def delete_temp_mute_entry(user_id, guild_id):
    cursor.execute("DELETE FROM temp_mutes WHERE (UserID=? AND GuildID=?)",
                   (user_id, guild_id))


def get_temp_mute_entry(user_id, guild_id):
    cursor.execute("SELECT * FROM temp_mutes WHERE (UserID=? AND GuildID=?)",
                   (user_id, guild_id))
    return cursor.fetchone()


def get_all_temp_mute_entries():
    try:
        cursor.execute("SELECT * FROM temp_mutes")
        return cursor.fetchall()

    except sqlite3.OperationalError:
        pass


@with_commit
def add_temp_role_entry(user_id, end_time, role_id, guild_id):
    cursor.execute("INSERT OR REPLACE INTO temp_roles VALUES (?, ?, ?, ?)",
                   (user_id, guild_id, end_time, role_id))


@with_commit
def delete_temp_role_entry(user_id, guild_id):
    cursor.execute("DELETE FROM temp_roles WHERE (UserID=? AND GuildID=?)",
                   (user_id, guild_id))


def get_temp_role_entry(user_id, guild_id):
    cursor.execute("SELECT * FROM temp_roles WHERE (UserID=? AND GuildID=?)",
                   (user_id, guild_id))
    return cursor.fetchone()


def get_all_temp_role_entries():
    try:
        cursor.execute("SELECT * FROM temp_roles")
        return cursor.fetchall()

    except sqlite3.OperationalError:
        pass
