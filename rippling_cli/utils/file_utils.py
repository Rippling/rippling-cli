import os
import zipfile
from http import client
from pathlib import Path
from typing import Optional

import click
import requests  # type: ignore

from rippling_cli.exceptions.build_exceptions import DirectoryCreationFailed


def create_directory_inside_path(path: str, dir_name: str):
    """
    Creates a new directory inside the specified path.
    :param path:
    :param dir_name:
    :return:
    """
    # Construct the path for the new directory
    new_dir_path = os.path.join(path, dir_name)

    # Create the new directory
    try:
        os.mkdir(new_dir_path)
    except FileExistsError:
        return
    except Exception:
        raise DirectoryCreationFailed()


def extract_zip_to_current_cwd(filename):
    """
    Extracts the contents of a zip file to the current working directory.
    :param filename:
    :return:
    """

    output_path = Path.cwd()  # Path to the new directory

    file_path = Path.cwd() / filename  # Path to the zip file
    if filename.endswith(".zip"):
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(output_path)
            click.echo("Starter package extracted successfully.")

    delete_zip_file(file_path)


def download_file_using_url(url: str, filename: Optional[str] = None):
    """
    Downloads a file from a URL and saves it to the current working directory.
    :param url:
    :param filename:
    :return:
    """
    filename = url.split("/")[-1] if not filename else filename
    output_path = Path.cwd()
    output_file = output_path / filename
    try:
        response = requests.get(url, stream=True)
        if response.status_code != client.OK:
            return False
        with open(output_file, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
    except Exception:
        click.echo("Failed to download file")
        return False
    return True


def delete_zip_file(zip_file_path):
    """
    Delete the zip file after it has been extracted.

    Args:
        zip_file_path (str): The path to the zip file to delete.
    """
    try:
        os.remove(zip_file_path)
    except FileNotFoundError:
        pass
