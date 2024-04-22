import os
import zipfile
from pathlib import Path
from typing import Optional

import click
import requests  # type: ignore

from rippling_cli.exceptions.build_exceptions import DirectoryCreationFailed


def create_directory_inside_path(path: str, dir_name: str):
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
    """Extracts the contents of a ZIP archive to a new directory with the same name as the archive inside the current
    working directory. """
    # Get the current working directory
    cwd = os.getcwd()

    # Get the directory name from the cwd
    dir_name = os.path.basename(cwd)

    # Replace any hyphens in the directory name with underscores
    dir_name = dir_name.replace('-', '_')
    # Create a new directory with same name inside the current working directory
    create_directory_inside_path(cwd, dir_name)

    output_path = Path.cwd() / dir_name  # Path to the new directory

    # Create the __init__.py file inside the new directory to make it a package
    init_file_path = os.path.join(output_path, "__init__.py")
    open(init_file_path, "w").close()

    file_path = Path.cwd() / filename  # Path to the zip file
    if filename.endswith(".zip"):
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(output_path)
            click.echo("ZIP archive extracted successfully.")

    delete_zip_file(file_path)


def download_file_using_url(url: str, app_display_name: Optional[str] = None):
    filename = app_display_name if app_display_name else url.split("/")[-1]
    output_path = Path.cwd()
    output_file = output_path / filename
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
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
        raise FileNotFoundError(f"File {zip_file_path} not found.")
