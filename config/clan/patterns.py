user_types = {"lead": "clan_leader",
              "dep": "clan_leader_deputy",
              "member": "clan_member"}

channels = {"chat": "chat",
            "voice": "voice",
            "rating": "rating"}

CLAN_CHANNELS_PERMS_ROLES_PATTERN = "data/permissions_and_roles/{user_type}/[{channel_type}]_permissions.json"
