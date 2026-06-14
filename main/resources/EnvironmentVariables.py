import json
from os.path import exists

prod_env = 'resources/prod.json'
dev_env = 'resources/test.json'

_env_file = dev_env if exists(dev_env) else prod_env
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