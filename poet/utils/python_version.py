import re
import sys

import questionary
from prompt_toolkit.document import Document


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
