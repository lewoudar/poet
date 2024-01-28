import click
import questionary

from poet.utils import (
    ask_name,
    ask_version,
    ask_description,
    ask_author_information,
    ask_license_information,
    ask_python_version,
    ask_readme_file_type,
    ask_main_dependencies,
    ask_development_dependencies,
    handle_pyproject_file_creation
)


@click.command()
def init():
    """Initialize the pyproject.toml with correct metadata."""
    form = questionary.form(
        name=ask_name(),
        version=ask_version(),
        description=ask_description(),
        author=ask_author_information(),
        license=ask_license_information(),
        readme=ask_readme_file_type(),
        python=ask_python_version(),
    ).ask()
    main_dependencies = ask_main_dependencies()
    development_dependencies = ask_development_dependencies()
    handle_pyproject_file_creation(form, main_dependencies, development_dependencies)
