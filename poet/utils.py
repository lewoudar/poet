import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import click
import questionary
import email_validator
import tomlkit
from prompt_toolkit.document import Document

from poet.scraper import find_relevant_packages


def ask_name() -> questionary.Question:
    return questionary.text('Package name:', default=Path.cwd().name)


def ask_version() -> questionary.Question:
    return questionary.text('Version:', default='0.1.0')


def ask_description() -> questionary.Question:
    return questionary.text('Description:')


def run_process(arguments: list) -> str:
    try:
        result = subprocess.run(arguments, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ''


def get_default_author_information() -> str:
    name = run_process(['git', 'config', '--global', 'user.name'])
    email = run_process(['git', 'config', '--global', 'user.email'])
    if not name and not email:
        return ''
    return f'{name} <{email}>'


class AuthorValidator(questionary.Validator):
    @staticmethod
    def _check_composition(author_data: str, parts: list[str]) -> None:
        if len(parts) < 2:
            raise questionary.ValidationError(message='missing email information', cursor_position=len(author_data))

    @staticmethod
    def _get_cursor_position(author_data: str, author_name: str) -> int:
        # it is a best-effort attempt to get the position of where the email starts.
        # - in the best scenario, the format is respected and the email is not correct, so we search "<" in the data
        # - if not we compute the author name and add 2 to consider the space between the author name and the email
        try:
            return author_data.index('<')
        except ValueError:
            return len(author_name) + 2

    @staticmethod
    def _check_email_tag(email: str, cursor_position: int) -> None:
        if not email.startswith('<') or not email.endswith('>'):
            raise questionary.ValidationError(
                message='email must be in the form <EMAIL>', cursor_position=cursor_position
            )

    @staticmethod
    def _check_email_format(email: str, cursor_position: int) -> None:
        try:
            # the second argument is to avoid a DNS check
            email_validator.validate_email(email[1:-1], check_deliverability=False)
        except email_validator.EmailNotValidError as e:
            raise questionary.ValidationError(message=str(e), cursor_position=cursor_position)

    def _check_author_data_is_correct(self, author_data: str) -> None:
        parts = author_data.split()
        self._check_composition(author_data, parts)

        author_name = ' '.join(parts[:-1])
        email = parts[-1]
        cursor_position = self._get_cursor_position(author_data, author_name)
        self._check_email_tag(email, cursor_position)
        self._check_email_format(email, cursor_position)

    def validate(self, document: Document) -> None:
        author_data = document.text.strip()
        # author information is not mandatory
        if not author_data:
            return

        # but if present, we need to validate it
        self._check_author_data_is_correct(author_data)


def ask_author_information() -> questionary.Question:
    return questionary.text('Author:', default=get_default_author_information(), validate=AuthorValidator)


def ask_license_information() -> questionary.Question:
    # information taken from https://choosealicense.com/ (apart the last one)
    metadata = {
        'MIT': 'A short and simple permissive license with conditions only requiring preservation of copyright and'
        ' license notices.',
        'Apache 2.0': 'A permissive license whose main conditions require preservation of copyright and '
        'license notices.',
        'GPLv2': 'The GNU GPL is the most widely used free software license and has a strong copyleft requirement. '
        'When distributing derived works, the source code of the work must be made available '
        'under the same license.',
        'GPLv3': 'Permissions of this strong copyleft license are conditioned on making available complete source'
        ' code of licensed works and modifications, which include larger works using a licensed work, '
        'under the same license',
        'Unlicense': 'A license with no conditions whatsoever which dedicates works to the public domain.',
        'Proprietary': 'Proprietary License',
    }
    return questionary.autocomplete('License:', choices=list(metadata.keys()), meta_information=metadata)


def ask_readme_file_type() -> questionary.Question:
    return questionary.rawselect('README style:', choices=['README.md', 'README.rst', 'README.txt'])


def get_default_python_version() -> str:
    return f'{sys.version_info.major}.{sys.version_info.minor}'


class PythonVersionValidator(questionary.Validator):
    def validate(self, document: Document) -> None:
        pattern = r'^[23]\.\d+'
        if re.match(pattern, document.text) is None:
            raise questionary.ValidationError(
                message='The python version must be in the form 2.X or 3.X where X represents an integer.'
            )


def ask_python_version() -> questionary.Question:
    return questionary.text('Python Version:', default=get_default_python_version(), validate=PythonVersionValidator)


def get_first_ten_packages(packages: dict[str, str]) -> dict[str, str]:
    filtered_items = list(packages.items())[:10]
    return dict(filtered_items)


def get_formatted_package_version(packages: dict[str, str], package: str, package_version: str) -> str:
    if not package_version:
        return f'^{packages[package]}'

    return package_version


def ask_dependencies(dependency_type: str) -> dict:
    dependencies = {}
    user_wants_to_continue = questionary.confirm(
        f'\nWould you like to define your {dependency_type} dependencies interactively?', default=True
    ).ask()
    while user_wants_to_continue:
        package = questionary.text('Add a package (leave blank to skip):').ask()
        if not package:
            break
        packages = find_relevant_packages(package)
        packages_length = len(packages)
        click.echo(f'Found {packages_length} packages matching {package}')
        if packages_length > 10:
            click.echo('Showing the first 10 matches')
            packages = get_first_ten_packages(packages)

        selected_package = questionary.select('Select the package to add', choices=list(packages.keys())).ask()
        package_version = questionary.text(
            'Enter the version constraint to require (or leave blank to use the latest version):'
        ).ask()
        package_version = get_formatted_package_version(packages, selected_package, package_version)

        dependencies[selected_package] = package_version
        click.echo(f'Using version {package_version} for {selected_package}\n')

    return dependencies


def ask_main_dependencies() -> dict:
    return ask_dependencies('main')


def ask_development_dependencies() -> dict:
    return ask_dependencies('development')


def construct_pyproject_file(
    form: dict[str, str], main_dependencies: dict[str, str], development_dependencies: dict[str, str]
) -> dict[str, Any]:
    python_version = form.pop('python')
    author = form.pop('author')
    poetry_dict = {
        'tool': {
            'poetry': {
                'name': form['name'],
                'version': '0.1.0',
                'description': form['description'],
                'authors': [author],
                'license': form['license'],
                'readme': form['readme'],
                'dependencies': {
                    'python': python_version,
                    **main_dependencies,
                },
                'group': {'dev': {'dependencies': development_dependencies}},
            }
        },
        'build-system': {'requires': ['poetry-core'], 'build-backend': 'poetry.core.masonry.api'},
    }

    return poetry_dict


def preview_pyproject_file(pyproject_data: str) -> None:
    click.echo('Generated file\n')
    click.echo(pyproject_data)


def generate_pyproject_file(pyproject_data: str) -> None:
    with open('pyproject.toml', 'w') as f:
        f.write(pyproject_data)


def handle_pyproject_file_creation(
    form: dict[str, str], main_dependencies: dict[str, str], development_dependencies: dict[str, str]
):
    poetry_dict = construct_pyproject_file(form, main_dependencies, development_dependencies)
    pyproject_data = tomlkit.dumps(poetry_dict)
    preview_pyproject_file(pyproject_data)

    user_wants_to_create_file = questionary.confirm('Do you confirm generation?', default=True).ask()
    if user_wants_to_create_file:
        generate_pyproject_file(pyproject_data)
        click.secho('The pyproject toml file was generated!', fg='green')
