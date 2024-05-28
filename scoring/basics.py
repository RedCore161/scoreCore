import re

from scoring.helper import elog


def parse_boolean(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        if value.lower() == "true" or value == "1":
            return True
        if value.lower() == "none":
            return None
    return False


def parse_int(value):
    if value == "None" or value is None:
        return None
    return int(value)


def parse_split_str(value: str, split_char) -> list:
    if not value:
        elog("Invalid Value for function 'parse_split_str'!")
        return []
    if split_char in value:
        return value.split(split_char)
    return [value]


def parse_file_name(_data, _default=None):
    if re.match(r'^[a-zA-Z0-9äÄöÖüÜß&()/\-_. ]*$', _data):
        return _data.replace(" ", "_")
    elog(f"Bad Filename: {_data}")
    return _default
