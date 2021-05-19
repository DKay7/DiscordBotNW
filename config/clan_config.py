CLAN_LEADER_OFFER_MESSAGE_DIR = r"data/messages/clan_leader_offer.json"
CLAN_LEADER_ROLE = r"data/permissions_and_roles/clan_leader/role_config.json"
CLAN_MEMBER_ROLE = r"data/permissions_and_roles/clan_member/role_config.json"
CLAN_DEP_ROLE = r"data/permissions_and_roles/clan_leader_deputy/role_config.json"
user_types = {"lead": "clan_leader",
              "dep": "clan_leader_deputy",
              "member": "clan_member"}
channels = {"chat": "chat",
            "voice": "voice",
            "rating": "rating"}
CLAN_CHANNELS_PERMS_ROLES_PATTERN = "data/permissions_and_roles/{user_type}/[{channel_type}]_permissions.json"
