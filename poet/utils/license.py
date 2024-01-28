import questionary


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
