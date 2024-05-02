import json

def load_config(config_file):
    """
    Loads the configuration file.
    """
    with open(config_file) as f:
        config = json.load(f)
    return config

