from typing import Any

import click
import questionary
import tomlkit


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
