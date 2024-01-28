import click
import questionary

from poet.utils.scraper import find_relevant_packages


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
