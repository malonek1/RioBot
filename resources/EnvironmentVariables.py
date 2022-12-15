import json
from os.path import exists

prod_env = 'resources/prod.json'
dev_env = 'resources/test.json'


def get_var(var_input: str):
    env = prod_env
    if exists(dev_env):
        env = dev_env

    with open(env) as config:
        env_vars = json.loads(config.read())
        return env_vars[var_input]
