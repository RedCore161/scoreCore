import os
import pathlib
import random
import string

from server.settings import MEDIA_ROOT, BACKUP_DIR, SETUP_DIR


def save_check_dir(*dirs):
    for _d in dirs:
        if not os.path.isdir(_d):
            print(f"Created {_d}")
            pathlib.Path(_d).mkdir(parents=True, exist_ok=True)


def get_media_path() -> str:
    return "media"


def get_setup_path() -> str:
    return SETUP_DIR


def get_backup_path() -> str:
    return BACKUP_DIR


def get_project_evaluation_dir(project_id) -> str:
    _path = build_abs_path(["evaluations", project_id])
    save_check_dir(_path)
    return _path


def build_abs_path(path_list: list) -> str:
    _abs_path = os.path.abspath(MEDIA_ROOT)
    return os.path.join(_abs_path, *path_list)


def random_string(letter_count, digit_count):
    str1 = ''.join((random.choice(string.ascii_letters) for x in range(letter_count)))
    str1 += ''.join((random.choice(string.digits) for x in range(digit_count)))

    sam_list = list(str1)       # it converts the string to list.
    random.shuffle(sam_list)    # It uses a random.shuffle() function to shuffle the string.
    return ''.join(sam_list)
