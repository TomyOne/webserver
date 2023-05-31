import os

def get_bool_env(var, default=False):
    return bool(os.getenv(var, default))
