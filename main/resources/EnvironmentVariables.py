import json

from resources.paths import RESOURCES_DIR

_prod_env = RESOURCES_DIR / "prod.json"
_dev_env = RESOURCES_DIR / "test.json"

_env_file = _dev_env if _dev_env.exists() else _prod_env
with open(_env_file) as _f:
    _vars = json.load(_f)


def get_var(var_input: str):
    return _vars[var_input]


BOT_SPAM_CHANNEL_ID = int(_vars["bot_spam_channel_id"])
MOD_CHANNEL_ID = int(_vars["mod_channel_id"])
MOD_ROLE_ID = int(_vars["mod_role_id"])
RANKED_BOT_CHANNEL_ID = int(_vars["ranked_bot_channel_id"])
MM_BUTTON_CHANNEL_ID = int(_vars["mm_button_channel_id"])
MM_MATCH_CHANNEL_ID = int(_vars["mm_match_channel_id"])
# Roles pinged when a player is waiting for a match. Read with a fallback to the
# prod role IDs so a config file that predates these keys still boots.
MM_STARS_OFF_ROLE_ID = int(_vars.get("mm_stars_off_role_id", 998791156794150943))
MM_STARS_ON_ROLE_ID = int(_vars.get("mm_stars_on_role_id", 998791464630898808))
# Discord user allowed to approve/deny manual game submissions. Fallback keeps
# the bot working if the config file predates this key.
MANUAL_SUBMIT_APPROVER_ID = int(_vars.get("manual_submit_approver_id", 117697656519786497))
