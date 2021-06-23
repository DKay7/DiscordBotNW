from utils.db.db_connection import cursor, conn
from utils.db.db_build import with_commit
from utils.clan_economy.sql_addition_functions import check_money

conn.create_function("CHECK_MONEY", 1, check_money)


@with_commit
def add_money(user_id, guild_id, money):
    cursor.execute("INSERT INTO economy VALUES (?, ?, ?) "
                   "ON CONFLICT(UserID, GuildID) DO UPDATE "
                   "SET Money=CHECK_MONEY(Money+?)",
                   (user_id, guild_id, money, money))


def get_money(user_id, guild_id):
    money = cursor.execute("Select Money FROM economy "
                           "WHERE (UserId=? AND GuildID=?)",
                           (user_id, guild_id)).fetchone()

    if money:
        return money[0]
    else:
        return 0


@with_commit
def reset_money(user_id, guild_id):
    cursor.execute("UPDATE economy "
                   "SET Money=0 "
                   "WHERE (UserId=? AND GuildID=?)",
                   (user_id, guild_id))


@with_commit
def withdraw_money(user_id, guild_id, money_to_take):
    cursor.execute("UPDATE economy SET Money=Money-? "
                   "WHERE (GuildId=? AND UserId=?)",
                   (money_to_take, guild_id, user_id))


@with_commit
def delete_user_from_economy(user_id, guild_id):
    cursor.execute("DELETE FROM economy "
                   "WHERE (GuildId=? AND UserId=?)",
                   (guild_id, user_id))


def get_all_shop_roles(guild_id):
    roles_and_costs = cursor.execute("SELECT * "
                                     "FROM shop "
                                     "WHERE GuildID=?",
                                     (guild_id, )).fetchall()

    return roles_and_costs


def get_shop_role_cost(guild_id, role_id):
    costs = cursor.execute("SELECT cost "
                           "FROM shop "
                           "WHERE RoleID=? AND GuildID=?",
                           (role_id, guild_id)).fetchone()

    if costs:
        return costs[0]


@with_commit
def add_shop_roles(guild_id, new_role_id, new_cost):
    cursor.execute("INSERT INTO shop VALUES(?, ?, ?)"
                   "ON CONFLICT(RoleID, GuildID) DO UPDATE "
                   "SET Cost=? ",
                   (guild_id, new_role_id, new_cost, new_cost))


@with_commit
def delete_shop_roles(guild_id, role_to_delete_id):
    cursor.execute("DELETE FROM shop "
                   "WHERE RoleID=? and GuildId=?",
                   (role_to_delete_id, guild_id))


@with_commit
def add_money_symbol(guild_id, symbol):
    cursor.execute("INSERT INTO money_symbols "
                   "VALUES (?, ?)"
                   "ON CONFLICT(GuildId) DO UPDATE "
                   "SET Symbol=?",
                   (guild_id, symbol, symbol))


def get_money_symbol(guild_id):
    symbol = cursor.execute("SELECT Symbol FROM money_symbols "
                            "WHERE GuildID=?",
                            (guild_id, )).fetchone()

    if symbol:
        return symbol[0]


def get_top_10_users_by_economy():
    entries = cursor.execute("SELECT UserId, RowNum, Money FROM ("
                             "    SELECT ROW_NUMBER() OVER("
                             "          ORDER BY Money DESC"
                             "     ) RowNum,"
                             "       UserId,"
                             "       Money"
                             "    FROM economy"
                             ") LIMIT 15").fetchall()

    if entries:
        return entries


@with_commit
def add_money_deposit(user_id, guild_id, money):
    cursor.execute("INSERT INTO deposit VALUES (?, ?, ?) "
                   "ON CONFLICT(UserID, GuildID) DO UPDATE "
                   "SET DepositMoney=CHECK_MONEY(DepositMoney+?)",
                   (user_id, guild_id, money, money))


def get_money_deposit(user_id, guild_id):
    money = cursor.execute("Select DepositMoney FROM deposit "
                           "WHERE (UserId=? AND GuildID=?)",
                           (user_id, guild_id)).fetchone()

    if money:
        return money[0]
    else:
        return 0


@with_commit
def withdraw_money_deposit(user_id, guild_id, money_to_take):
    cursor.execute("UPDATE deposit SET DepositMoney=DepositMoney-? "
                   "WHERE (GuildId=? AND UserId=?)",
                   (money_to_take, guild_id, user_id))

