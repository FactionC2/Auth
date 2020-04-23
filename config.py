import os
import json
from logger import log

global_config = os.environ.get("FACTION_CONFIG_PATH", "/opt/faction/global/config.json")
local_config = "./config.json"


def get_config():
    if os.path.exists(global_config):
        config_file_path = global_config
    elif os.path.exists(local_config):
        config_file_path = local_config

    if config_file_path:
        try:
            with open(config_file_path) as f:
                config = json.load(f)
            return config
        except Exception as e:
            log("config.py", f"Error: {str(e)} - {str(type(e))}")
            log("config.py", "Could not load config file: {0}".format(config_file_path))
            exit(1)
    else:
        try:
            config = dict()
            config["FLASK_SECRET"] = os.environ["FLASK_SECRET"]
            config["POSTGRES_DATABASE"] = os.environ["POSTGRES_DATABASE"]
            config["POSTGRES_USERNAME"] = os.environ["POSTGRES_USERNAME"]
            config["POSTGRES_PASSWORD"] = os.environ["POSTGRES_PASSWORD"]
            config["POSTGRES_HOST"] = os.environ["POSTGRES_HOST"]
            config["ADMIN_PASSWORD"] = os.environ["ADMIN_PASSWORD"]
            config["SYSTEM_PASSWORD"] = os.environ["SYSTEM_PASSWORD"]
            return config
        except KeyError as e:
            log("config.py", "Config value not  in environment: {0}".format(str(e)))
            exit(1)
        except Exception as e:
            log("config.py", "Unknown error: {0}".format(str(e)))
            exit(1)


FACTION_CONFIG = get_config()
SECRET_KEY = FACTION_CONFIG["FLASK_SECRET"]
DB_USER = FACTION_CONFIG["POSTGRES_USERNAME"]
DB_PASSWORD = FACTION_CONFIG["POSTGRES_PASSWORD"]
DB_HOST = FACTION_CONFIG["POSTGRES_HOST"]
DB_NAME = FACTION_CONFIG["POSTGRES_DATABASE"]
DB_URI = "postgresql://{}:{}@{}/{}?client_encoding=utf8".format(
    DB_USER, DB_PASSWORD, DB_HOST, DB_NAME
)
ADMIN_PASSWORD = FACTION_CONFIG["ADMIN_PASSWORD"]
SYSTEM_PASSWORD = FACTION_CONFIG["SYSTEM_PASSWORD"]
