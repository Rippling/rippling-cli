import os
import subprocess
import sys

import click

from rippling_cli.exceptions.build_exceptions import PythonCreationFailed
from rippling_cli.utils.build_utils import create_pyproject_toml, get_run_config_xml_content
from rippling_cli.utils.file_utils import create_directory_inside_path


# TODO: Since run configuration cannot be transferred from import/export settings , it lies inside .idea folder in \
#  the project directory. This should be a separate command
def create_run_configurations(project_name: str):
    # Create the .idea directory if it doesn't exist
    create_directory_inside_path(os.getcwd(), ".idea")

    # Create the runConfigurations directory inside .idea
    create_directory_inside_path(f"{os.getcwd()}/.idea", "runConfigurations")

    # Create the Flask__flux_dev_tools_server_flask_.xml file
    xml_file_path = os.path.join(f"{os.getcwd()}/.idea/runConfigurations", "Flask__flux_dev_tools_server_flask_.xml")
    with open(xml_file_path, "w") as xml_file:
        xml_file.write(get_run_config_xml_content(project_name))


def setup_project(name=None, email=None):
    # Check if pip is available
    try:
        subprocess.check_output(["pip", "--version"])
    except FileNotFoundError:
        click.echo("pip is not installed. Installing Python and pip...")

        # Install Python
        install_python()

        # Check if Python installation was successful
        try:
            subprocess.check_output(["python", "--version"])
        except FileNotFoundError:
            click.echo("Python installation failed. Please install Python manually.")
            return

        # Install pip using ensurepip
        subprocess.run([sys.executable, "-m", "ensurepip", "--default-pip"])
        click.echo("pip has been installed.")

    # Check if Poetry is installed
    try:
        subprocess.check_output(["poetry", "--version"])
        click.echo("Poetry is already installed.")
    except FileNotFoundError:
        click.echo("Poetry is not installed. Installing Poetry...")

        # Install Poetry using pip
        subprocess.run(["pip", "install", "poetry"])
        click.echo("Poetry has been installed.")

    # Check if Poetry is installed successfully
    try:
        subprocess.check_output(["poetry", "--version"])
    except FileNotFoundError:
        click.echo("Poetry installation failed. Please install Poetry manually.")
        return

    # Check if pyproject.toml already exists
    if os.path.exists("pyproject.toml"):
        click.echo("pyproject.toml already exists. Aborting setup.")
        return

    authors = "developer <developer@example.com>"
    if name and email:
        authors = f"{name} <{email}>"  # Use provided name and email

    # Get the current working directory
    current_directory = os.getcwd()

    project_name = os.path.basename(current_directory)  # Default project name
    project_name.replace("-", "_")

    # Create pyproject.toml file with default content
    create_pyproject_toml(project_name, authors)

    # Install dependencies
    click.echo("Installing dependencies...")
    subprocess.run(["poetry", "install"])
    click.echo("Dependencies installed.")


def install_python():
    if sys.platform == "darwin":  # Check if macOS
        # Try installing Python using Homebrew
        try:
            subprocess.run(["brew", "install", "python"])
            return
        except FileNotFoundError:
            pass  # Homebrew not available, fall back to manual installation

        # Prompt the user to install Python manually from python.org
        click.echo("Python is not installed. Please install Python manually from https://www.python.org/downloads/")
        raise PythonCreationFailed()
    elif sys.platform.startswith("linux"):
        # Install Python on Linux using package manager (e.g., apt)
        subprocess.run(["sudo", "apt", "update"])
        subprocess.run(["sudo", "apt", "install", "python3"])
    elif sys.platform.startswith("win"):
        # Install Python on Windows using python.org installer
        click.echo("Please install Python manually from https://www.python.org/downloads/")
        raise PythonCreationFailed()
    else:
        click.echo("Unsupported platform. Please install Python manually.")
        raise PythonCreationFailed()
