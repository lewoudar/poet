import subprocess

import email_validator
import questionary
from prompt_toolkit.document import Document


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
