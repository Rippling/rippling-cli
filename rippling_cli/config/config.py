import json
import os

# Store the OAuth credentials in environment variables or a config file
from datetime import datetime, timedelta
from pathlib import Path

from rippling_cli.constants import APP_CONFIG_FILE, OAUTH_TOKEN_FILE_NAME, RIPPLING_DIRECTORY_NAME

CLIENT_ID = "AgvGDwoBRb0BJAnL2CQ8dNbE6J2fgCFIchEOyr5S"
global_config_dir = Path.home() / RIPPLING_DIRECTORY_NAME


def get_client_id():
    return CLIENT_ID


def create_base_directory_if_not_exists(config_dir=global_config_dir):
    # Create the directory if it doesn't exist
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)


def get_oauth_token_data():
    create_base_directory_if_not_exists()

    token_file = global_config_dir / OAUTH_TOKEN_FILE_NAME
    if token_file.exists():
        with token_file.open("r") as f:
            return json.load(f)
    return None


def save_oauth_token(token, expires_in=3600):
    create_base_directory_if_not_exists()

    data = {
        "token": str(token),
        "expiration_timestamp": (datetime.now() + timedelta(seconds=expires_in)).timestamp()
    }
    token_file = global_config_dir / OAUTH_TOKEN_FILE_NAME
    with token_file.open("w") as f:
        json.dump(data, f)


def get_app_config_dir(start_dir):
    """
    Find the nearest directory containing the app configuration.

    Args:
        start_dir (str): The starting directory to begin the search.

    Returns:
        str: The path to the directory containing the app configuration, or None if not found.
    """
    current_dir = start_dir
    while True:
        config_dir = os.path.join(current_dir, RIPPLING_DIRECTORY_NAME)
        config_file = os.path.join(config_dir, APP_CONFIG_FILE)
        if os.path.isdir(config_dir) and os.path.isfile(config_file):
            return config_dir
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            return None
        current_dir = parent_dir


def get_app_config():
    """
    Load the app configuration from the specified directory.

    Returns:
        dict: The app configuration data.
    """
    config_dir = get_app_config_dir(os.getcwd())
    if not config_dir:
        return {}

    config_file = os.path.join(config_dir, APP_CONFIG_FILE)
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            return json.load(f)
    return {}


def save_app_config(app_id: str, app_name: str):
    """
    Save the app configuration to the specified directory.
    Args:
        :param app_name:
        :param app_id:
    """
    config_dir = Path.cwd() / RIPPLING_DIRECTORY_NAME
    create_base_directory_if_not_exists(config_dir)

    app_config = {
        "id": app_id,
        "displayName": app_name
    }

    config_file = config_dir / APP_CONFIG_FILE
    with config_file.open("w") as f:
        json.dump(app_config, f)
