import click

from poet.commands.init import init


@click.version_option('0.1.0', message='%(prog)s version %(version)s')
@click.group(context_settings={'help_option_names': ['-h', '--help']})
def cli():
    """Dummy command to mimic "poetry init" command."""


cli.add_command(init)
