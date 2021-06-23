from utils.db.db_connection import cursor, conn
from utils.db.db_build import with_commit
from utils.clan_economy.sql_addition_functions import check_money

conn.create_function("CHECK_MONEY", 1, check_money)


@with_commit
def add_clan_money(user_id, group_channel_id, money):
    cursor.execute("INSERT INTO clan_economy VALUES (?, ?, CHECK_MONEY(?))"
                   "ON CONFLICT(UserID, GroupChannelID) DO UPDATE "
                   "SET Money=CHECK_MONEY(Money+?)",
                   (user_id, group_channel_id, money, money))


def get_clan_money(user_id, group_channel_id):
    money = cursor.execute("Select Money FROM clan_economy "
                           "WHERE (UserId=? AND GroupChannelId=?)",
                           (user_id, group_channel_id)).fetchone()

    if money:
        return money[0]
    else:
        return 0


@with_commit
def withdraw_clan_money(group_channel_id, user_id, money_to_take):
    cursor.execute("UPDATE clan_economy  SET Money=Money-? "
                   "WHERE (GroupChannelId=? and UserId=?)",
                   (money_to_take, group_channel_id, user_id))


def get_all_clan_shop_roles(group_channel_id):
    roles_and_costs = cursor.execute("SELECT * "
                                     "FROM clan_shops "
                                     "WHERE (GroupChannelId=?)",
                                     (group_channel_id,)).fetchall()

    return roles_and_costs


def get_clan_shop_role_cost(group_channel_id, role_id):
    cost = cursor.execute("SELECT Cost "
                          "FROM clan_shops "
                          "WHERE (GroupChannelId=? AND RoleID=?)",
                          (group_channel_id, role_id)).fetchone()

    if cost:
        return cost[0]


@with_commit
def add_clan_shop_roles(group_channel_id, new_role_id, new_cost):
    cursor.execute("INSERT INTO clan_shops VALUES(?, ?, ?)"
                   "ON CONFLICT(GroupChannelID, RoleID) DO UPDATE "
                   "SET Cost=? ",
                   (group_channel_id, new_role_id, new_cost, new_cost))


@with_commit
def delete_clan_shop_roles(group_channel_id, role_to_delete_id):
    cursor.execute("DELETE FROM clan_shops "
                   "WHERE GroupChannelId=? AND RoleID=?",
                   (group_channel_id, role_to_delete_id))
