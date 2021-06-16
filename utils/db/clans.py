from utils.db.db_build import with_commit
from utils.db.db_connection import cursor


@with_commit
def add_clan_to_db(clan_name, group_channel_id, clan_roles):

    cursor.execute("INSERT OR IGNORE INTO clans VALUES (?, ?, ?, ?, ?, ?)",
                   (clan_name, group_channel_id, 0, *map(lambda role: role.id, clan_roles)))


def get_clan_role_ids(group_channel_id):
    role_ids = cursor.execute("SELECT LeaderRoleId, DepRoleId, MemberRoleId "
                              "FROM clans WHERE GroupChannelID=?", (group_channel_id,)).fetchone()

    if role_ids:
        return role_ids


@with_commit
def write_win(clan_name):
    cursor.execute("UPDATE clans SET WinPoints=WinPoints+1 "
                   "WHERE (ClanName=?)",
                   (clan_name,))

    num_affected_rows = cursor.rowcount
    return num_affected_rows


def get_top_10_clans():
    entries = cursor.execute("SELECT ClanName, RowNum, WinPoints FROM ("
                             "    SELECT ROW_NUMBER() OVER("
                             "          ORDER BY WinPoints DESC"
                             "     ) RowNum,"
                             "       ClanName,"
                             "       WinPoints"
                             "    FROM clans"
                             ") LIMIT 10").fetchall()

    if entries:
        return entries


@with_commit
def add_clan_response(target_id, guild_id, message_id, type_, channel_id, clan_name=""):
    assert type_ in ["leader", "dep_leader", "member"]

    cursor.execute("INSERT INTO clan_asks "
                   "VALUES(?, ?, ?, ?, ?, ?) "
                   "ON CONFLICT(GuildID, TargetID, Type, ClanName) DO UPDATE "
                   "SET AskerMessageID=?",
                   (target_id, guild_id, message_id, channel_id, clan_name, type_, message_id))


@with_commit
def delete_clan_response(target_id, guild_id, type_, clan_name=""):
    assert type_ in ["leader", "dep_leader", "member"]

    cursor.execute("DELETE FROM clan_asks "
                   "WHERE (TargetID=? and GuildID=? and ClanName=? and Type=?)",
                   (target_id, guild_id, clan_name, type_))


def get_clan_name_from_response(target_id, type_, message_id):
    clan_name = cursor.execute("SELECT ClanName FROM clan_asks "
                               "WHERE (TargetId=? AND Type=? AND AskerMessageID=?)",
                               (target_id, type_, message_id)).fetchone()

    if clan_name:
        return clan_name[0]


def get_channel_id_from_response(target_id, type_, message_id):
    channel_id = cursor.execute("SELECT ChannelID FROM clan_asks "
                                "WHERE (TargetId=? AND Type=? AND AskerMessageID=?)",
                                (target_id, type_, message_id)).fetchone()

    if channel_id:
        return channel_id[0]


def find_duel_response(target_id, message_id):
    entry = cursor.execute("SELECT UserID, Bet FROM duel_asks "
                           "WHERE (TargetId=? AND AskerMessageID=?)",
                           (target_id, message_id)).fetchone()

    return entry


@with_commit
def delete_duel_response(user_id, target_id):
    cursor.execute("DELETE FROM duel_asks "
                   "WHERE (UserID=? and TargetID=?) ",
                   (user_id, target_id))


@with_commit
def add_duel_response(user_id, target_id, message_id, bet):
    cursor.execute("INSERT INTO duel_asks "
                   "VALUES(?, ?, ?, ?) "
                   "ON CONFLICT(UserID, TargetID) DO UPDATE "
                   "SET AskerMessageID=?, Bet=?",
                   (user_id, target_id, message_id, bet, message_id, bet))


def get_all_clan_ids():
    ids = cursor.execute("SELECT GroupChannelID "
                         "FROM clans").fetchall()

    if ids:
        return list(map(lambda id_: id_[0], ids))

    return []