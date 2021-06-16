from utils.db.db_connection import cursor, conn
from utils.db.db_build import with_commit
from utils.clan_economy.sql_addition_functions import check_money, append_roles_to_shop, remove_roles_from_shop
from utils.clan_economy.sql_addition_functions import get_roles_and_costs, add_roles_to_shop

conn.create_function("CHECK_MONEY", 1, check_money)
conn.create_function("APPEND_ROLE_TO_SHOP", 3, append_roles_to_shop)
conn.create_function("REMOVE_ROLE_FROM_SHOP", 2, remove_roles_from_shop)
conn.create_function("ADD_ROLES_TO_SHOP", 2, add_roles_to_shop)


@with_commit
def add_money(user_id, group_channel_id, money):
    cursor.execute("INSERT INTO clan_economy VALUES (?, ?, CHECK_MONEY(?))"
                   "ON CONFLICT(UserID, GroupChannelID) DO UPDATE "
                   "SET Money=CHECK_MONEY(Money+?)",
                   (user_id, group_channel_id, money, money))


def get_money(user_id, group_channel_id):
    money = cursor.execute("Select Money FROM clan_economy "
                           "WHERE (UserId=? AND GroupChannelId=?)",
                           (user_id, group_channel_id)).fetchone()

    if money:
        return money[0]
    else:
        return 0


@with_commit
def withdraw_money(group_channel_id, user_id, money_to_take):
    cursor.execute("UPDATE clan_economy  SET Money=Money-? "
                   "WHERE (GroupChannelId=? and UserId=?)",
                   (money_to_take, group_channel_id, user_id))


def get_shop_roles(group_channel_id):
    roles_and_costs = cursor.execute("SELECT RolesAndCosts "
                                     "FROM clan_shops "
                                     "WHERE (GroupChannelId=?)",
                                     (group_channel_id,)).fetchone()

    if roles_and_costs:
        return get_roles_and_costs(roles_and_costs[0])
    else:
        return False


@with_commit
def add_shop_roles(group_channel_id, new_role, new_cost):
    cursor.execute("INSERT INTO clan_shops VALUES(?, ADD_ROLES_TO_SHOP(?, ?))"
                   "ON CONFLICT(GroupChannelId) DO UPDATE "
                   "SET RolesAndCosts=APPEND_ROLE_TO_SHOP(RolesAndCosts, ?, ?) ",
                   (group_channel_id, new_role, new_cost, new_role, new_cost))


@with_commit
def delete_shop_roles(group_channel_id, role_to_delete):
    cursor.execute("UPDATE clan_shops  SET RolesAndCosts=REMOVE_ROLE_FROM_SHOP(RolesAndCosts, ?) "
                   "WHERE GroupChannelId=?",
                   (role_to_delete, group_channel_id))
