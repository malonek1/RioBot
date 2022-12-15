import json


def get_var(var_input: str):
    with open('resources/prod.json') as config:
        env_vars = json.loads(config.read())
        return env_vars[var_input]
