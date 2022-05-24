import errno
import math
import os
import pathlib
import random
import shutil
import string
import time
from time import strftime, gmtime

from colorama import Fore, Style
from colorama.ansi import AnsiFore

from server.settings import MEDIA_ROOT, BACKUP_DIR, SETUP_DIR

# ######################################################################## #
# #####  H E L P E R - F U N C T I O N S ################################# #
# ######################################################################## #


def _log(*msg, color: AnsiFore, tag, active):
    """
    blue console-output
    :param msg: message to be printed
    :param color: color of output
    :param tag: leading tag for the print line
    """
    if len(msg) and active:
        if type(msg[0]) == str and msg[0].startswith(tag):
            print(color, *msg, Style.RESET_ALL)
        else:
            print(color, tag, *msg, Style.RESET_ALL)


def dlog(*msg, tag="[DEBUG]", active=True):
    _log(*msg, color=Fore.WHITE, tag=tag, active=active)


def ilog(*msg, tag="[INFO]", active=True):
    _log(*msg, color=Fore.BLUE, tag=tag, active=active)


def elog(*msg, tag="[ERROR]", active=True):
    _log(*msg, color=Fore.RED, tag=tag, active=active)


def okaylog(*msg, tag="[OK]", active=True):
    _log(*msg, color=Fore.GREEN, tag=tag, active=active)


def breaklog(show_time=False):
    """
    blue console-output
    """
    if show_time:
        ilog(f'{strftime("%Y-%m-%d %H:%M:%S", gmtime())}\n', tag="#")
    ilog("=====================================================\n\n", tag="#")


# ##############################################################

def save_check_dir(*dirs):
    for _d in dirs:
        if not os.path.isdir(_d):
            print(f"Created {_d}")
            pathlib.Path(_d).mkdir(parents=True, exist_ok=True)


def get_media_path() -> str:
    return "media"


def get_path_setup() -> str:
    return SETUP_DIR


def get_path_backup() -> str:
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

# ##############################################################


def copy(src, dst, exists_okay=True):
    try:
        shutil.copytree(src, dst, dirs_exist_ok=exists_okay)
    except OSError as exc:
        if exc.errno in (errno.ENOTDIR, errno.EINVAL):
            shutil.copy(src, dst)
        else:
            raise


def delete_file(_file, acknowledge=False):
    """
    deletes the file
    """
    try:
        os.remove(_file)
        if acknowledge:
            ilog(f"Deleted: '{_file}'")
    except FileNotFoundError as e:
        elog(f"Can not delete File: '{_file}'")
        elog("[ERROR]", e)
    except PermissionError as e:
        elog(f"Can not delete File: '{_file}'")
        elog("[ERROR]", e)


def clear_dir(_dir):
    if os.path.isdir(_dir):
        for f in os.listdir(_dir):
            delete_file(os.path.join(_dir, f))


def sleep_ms(delay=0, msg=None):
    """
    sleeps for a specific amount of ms
    :param msg:
    :param delay: Delay as String in ms or 'None' as string
    """
    if msg:
        dlog(f"Sleep for {delay} | From: {msg}")

    if delay == 0 or delay == '---':
        time.sleep(3)
    else:
        time.sleep(int(delay) / 1000)
