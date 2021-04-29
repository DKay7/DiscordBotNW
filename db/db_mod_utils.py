import sqlite3

from config.config import WARN_NUM_STORED_REASONS
from discord.ext.commands import BadArgument
from .db_build_utils import with_commit
from .db_connection import cursor
from json import loads, dumps


def get_warn_entry(user_id, guild_id):
    cursor.execute("SELECT * FROM warns WHERE (UserID=? AND GuildID=?)", (user_id, guild_id))
    return cursor.fetchone()


@with_commit
def update_warn_entry(user_id, guild_id, new_reason):
    num_warns = 1
    reasons = list()

    if entry := get_warn_entry(user_id, guild_id):
        _, num_warns, reasons, _ = entry
        num_warns += 1
        reasons = loads(reasons)
        reasons.append(new_reason)
        reasons = dumps(reasons[-WARN_NUM_STORED_REASONS:])
        cursor.execute("UPDATE warns SET NumWarns=?, LastReasons=? WHERE (UserID=? AND GuildID=?)",
                       (num_warns, reasons, user_id, guild_id))

    else:
        reasons.append(new_reason)
        reasons = dumps(reasons)
        cursor.execute("INSERT INTO warns VALUES (?, ?, ?, ?)", (user_id, num_warns, reasons, guild_id))


@with_commit
def unwarn_entry(user_id, guild_id):
    if entry := get_warn_entry(user_id, guild_id):
        _, num_warns, reasons = entry
        num_warns = num_warns - 1 if num_warns - 1 >= 0 else 0
        reasons = loads(reasons)
        reasons = dumps(reasons[:-1])
        cursor.execute("UPDATE warns SET NumWarns=?, LastReasons=? WHERE (UserID=? AND GuildID=?)",
                       (num_warns, reasons, user_id, guild_id))
    else:
        raise BadArgument


@with_commit
def add_temp_ban_entry(user_id, end_time, guild_id):
    cursor.execute("INSERT OR REPLACE INTO temp_bans VALUES (?, ?, ?)", (user_id, end_time, guild_id))


@with_commit
def delete_temp_ban_entry(user_id, guild_id):
    cursor.execute("DELETE FROM temp_bans WHERE (UserID=? AND GuildID=?)", (user_id, guild_id))


def get_temp_ban_entry(user_id, guild_id):
    cursor.execute("SELECT * FROM temp_bans WHERE (UserID=? AND GuildID=?)", (user_id, guild_id))
    return cursor.fetchone()


def get_all_temp_ban_entries():
    try:
        cursor.execute("SELECT * FROM temp_bans")
        return cursor.fetchall()

    except sqlite3.OperationalError:
        pass


@with_commit
def add_temp_mute_entry(user_id, end_time, mute_type, guild_id):
    cursor.execute("INSERT OR REPLACE INTO temp_mutes VALUES (?, ?, ?, ?)", (user_id, end_time, mute_type, guild_id))


@with_commit
def delete_temp_mute_entry(user_id, guild_id):
    cursor.execute("DELETE FROM temp_mutes WHERE (UserID=? AND GuildID=?)", (user_id, guild_id))


def get_temp_mute_entry(user_id, guild_id):
    cursor.execute("SELECT * FROM temp_mutes WHERE (UserID=? AND GuildID=?)", (user_id, guild_id))
    return cursor.fetchone()


def get_all_temp_mute_entries():
    try:
        cursor.execute("SELECT * FROM temp_mutes")
        return cursor.fetchall()

    except sqlite3.OperationalError:
        pass


@with_commit
def add_temp_role_entry(user_id, end_time, role_id, guild_id):
    cursor.execute("INSERT OR REPLACE INTO temp_roles VALUES (?, ?, ?, ?)", (user_id, end_time, role_id, guild_id))


@with_commit
def delete_temp_role_entry(user_id, guild_id):
    cursor.execute("DELETE FROM temp_roles WHERE (UserID=? AND GuildID=?)", (user_id, guild_id))


def get_temp_role_entry(user_id, guild_id):
    cursor.execute("SELECT * FROM temp_roles WHERE (UserID=? AND GuildID=?)", (user_id, guild_id))
    return cursor.fetchone()


def get_all_temp_role_entries():
    try:
        cursor.execute("SELECT * FROM temp_roles")
        return cursor.fetchall()

    except sqlite3.OperationalError:
        pass
