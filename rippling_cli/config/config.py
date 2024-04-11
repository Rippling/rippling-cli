import os
import json

# Store the OAuth credentials in environment variables or a config file
from datetime import datetime, timedelta
from pathlib import Path

from rippling_cli.constants import OAUTH_TOKEN_FILE_NAME, RIPPLING_DIRECTORY_NAME

CLIENT_ID = "OJ3RJIYivW34fb0N0amHBwRYY7ldjM9O00hkQdR4"
config_dir = Path.home() / f".{RIPPLING_DIRECTORY_NAME}"


def get_client_id():
    return CLIENT_ID


def get_oauth_token_data():
    # Create the directory if it doesn't exist
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    token_file = config_dir / OAUTH_TOKEN_FILE_NAME
    if token_file.exists():
        with token_file.open("r") as f:
            return json.load(f)
    return None


def save_oauth_token(token, expires_in=3600):

    # Create the directory if it doesn't exist
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    data = {
        "token": str(token),
        "expiration_timestamp": (datetime.now() + timedelta(seconds=expires_in)).timestamp()
    }
    token_file = config_dir / OAUTH_TOKEN_FILE_NAME
    with token_file.open("w") as f:
        json.dump(data, f)
