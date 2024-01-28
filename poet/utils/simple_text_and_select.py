from pathlib import Path

import questionary


def ask_name() -> questionary.Question:
    return questionary.text('Package name:', default=Path.cwd().name)


def ask_version() -> questionary.Question:
    return questionary.text('Version:', default='0.1.0')


def ask_description() -> questionary.Question:
    return questionary.text('Description:')


def ask_readme_file_type() -> questionary.Question:
    return questionary.rawselect('README style:', choices=['README.md', 'README.rst', 'README.txt'])
