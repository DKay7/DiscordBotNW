from json import loads, dumps


def check_money(money):
    return money if money > 0 else 0


def add_roles_to_shop(new_role, new_cost):
    new_role_and_cost = dumps({new_role: new_cost})

    return new_role_and_cost


def append_roles_to_shop(roles_and_costs, new_role, new_cost):
    roles_and_costs = loads(roles_and_costs)
    roles_and_costs.update({new_role: new_cost})

    roles_and_costs = dumps(roles_and_costs)
    return roles_and_costs


def remove_roles_from_shop(roles_and_costs, role_to_delete):
    roles_and_costs = loads(roles_and_costs)
    if str(role_to_delete) in roles_and_costs.keys():
        roles_and_costs.pop(str(role_to_delete))

    roles_and_costs = dumps(roles_and_costs)

    return roles_and_costs


def get_roles_and_costs(roles_and_costs):
    roles_and_costs = loads(roles_and_costs)
    return roles_and_costs
