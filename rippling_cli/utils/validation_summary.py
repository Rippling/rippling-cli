from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import click


@dataclass
class Validation:
    """
    Validation dataclass.
    """
    name: str
    is_successful: bool
    error_count: int
    warning_count: int
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    log_file_url: Optional[str]


class ValidationSummary:
    """
    Validation summary class.
    """
    def __init__(self, validations: Dict[str, Validation]):
        self.validations = validations

    def print_summary(self):
        """
        Print the summary of the validations by iterating through the validations and printing the success or failure
        :return:
        """
        for name, validation in self.validations.items():
            if not validation.is_successful:
                self.print_failure_step(name, validation)
            else:
                self.print_success_step(name)

    @staticmethod
    def print_failure_step(name: str, validation: Validation):
        """
        Print the failure step with the name and the errors
        :param name:
        :param validation:
        :return:
        """
        click.echo(click.style(f"[FAILURE] {name} validation failed ", fg="red", bold=True))
        for error in validation.errors:
            error_detail: dict = error.get("detail", {})
            if "file_path" in error_detail:
                error_json = error_detail.get("detail", {})
                click.echo(click.style(f"  - Error: {error_json.get('message')} in {error_json.get('path')} at \
line {error_json.get('line')} column {error_json.get('column')}", fg="red"))
            else:
                click.echo(click.style(f"  - Error: {error_detail.get('message')} (Details: \
{error_detail.get('error_message')})", fg="red"))
        if validation.log_file_url:
            click.echo(click.style(f"  Full log: {validation.log_file_url}", fg="blue", underline=True))

    @staticmethod
    def print_success_step(name: str):
        """
        Print the success step with the name
        :param name:
        :return:
        """
        click.echo(click.style(f"[SUCCESS] {name} validation successful", fg="green"))
