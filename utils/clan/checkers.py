from discord import Member


def check_leader(leader: Member, clan_name: str):
    pass_check = False

    for role in leader.roles:
        role_name = role.name.lower()
        if "leader" in role_name and clan_name.lower() in role_name \
           and "dep" not in role_name:
            pass_check = True
            break

    return pass_check
