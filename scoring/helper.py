import os
import pathlib

from server.settings import MEDIA_ROOT


def save_check_dir(*dirs):
    for _d in dirs:
        if not os.path.isdir(_d):
            print(f"Created {_d}")
            pathlib.Path(_d).mkdir(parents=True, exist_ok=True)


def get_media_path() -> str:
    return "media"


def build_abs_path(path_list: list) -> str:
    _abs_path = os.path.abspath(MEDIA_ROOT)
    return os.path.join(_abs_path, *path_list)
