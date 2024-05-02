import os
import sys
from http import HTTPStatus

from rippling_cli.constants import RIPPLING_API
from rippling_cli.core.api_client import APIClient


def source_venv():
    """
    Source the virtual environment by modifying the PATH environment variable.
    """
    platform = sys.platform
    if platform == "linux" or platform == "linux2":
        venv_dir = os.path.join(os.getcwd(), ".venv/bin")
    elif platform == "darwin":
        venv_dir = os.path.join(os.getcwd(), ".venv/bin")
    elif platform == "win32":
        venv_dir = os.path.join(os.getcwd(), ".venv/Scripts")
    else:
        raise RuntimeError(f"Unsupported platform: {platform}")

    venv_path = os.path.join(venv_dir)

    # Modify the PATH environment variable
    os.environ["PATH"] = venv_path + os.pathsep + os.environ.get("PATH", "")


def set_forwarding_url(app_install_id, public_url, timeout, oauth_token):
    """
    Set the forwarding URL with the specified timeout.
    :param oauth_token:
    :param app_install_id:
    :param public_url:
    :param timeout:
    :return:
    """
    api_client = APIClient(base_url=RIPPLING_API, headers={"Authorization": f"Bearer {oauth_token}"})
    endpoint = "/apps/api/flux_spoke_owner_debugging_info/save"
    data = {
        "app_install_id": app_install_id,
        "enabled": True,
        "enabled_time_seconds": int(timeout),
        "endpoint_url": public_url
    }
    response = api_client.post(endpoint, json=data)
    message = None
    if response.status_code == HTTPStatus.BAD_REQUEST:
        message = response.json().get("message")
    return response.status_code == HTTPStatus.OK, message


def validate_forwarding_url_set(forwarding_url):
    # Assuming forwarding_url_set is a string representing the URL to validate
    api_client = APIClient(base_url=forwarding_url)
    response = api_client.get(endpoint="/")

    if response.status_code != HTTPStatus.OK:
        return False

    json_data = response.json()
    if "app" in json_data and json_data.get("app") == "Rippling Flux Server":
        return True
    return False
