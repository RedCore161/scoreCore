import errno
import fnmatch
import os
import pathlib
import random
import shutil
import string
import time
from datetime import datetime
from time import strftime, gmtime

from colorama import Fore, Style
from colorama.ansi import AnsiFore
from loguru import logger

INFO_FILE_NAME = "infofile.txt"
MAX_LOG_LENGTH = 2500


# ######################################################################## #
# #####  H E L P E R - F U N C T I O N S ################################# #
# ######################################################################## #


def _cleaned_msg(*msg):
    _msg = ' '.join(str(x) for x in msg)
    if len(_msg) > MAX_LOG_LENGTH:
        return f"[SHORTED len={ len(_msg) }] { _msg[:MAX_LOG_LENGTH] }..."
    return _msg


def _log(*msg, color: AnsiFore, tag, active):
    """
    blue console-output
    :param msg: message to be printed
    :param color: color of output
    :param tag: leading tag for the print line
    """
    if active:
        _now = time.time()
        time_with_ms = "%s.%03d" % (time.strftime('%X', time.localtime(_now)), _now % 1 * 1000)
        print(color, time_with_ms, f"{tag: <15}", *msg, Style.RESET_ALL)


def dlog(*msg, tag: str = "[DEBUG]", active=True, logger=None):
    _msg = _cleaned_msg(*msg)
    _log(_msg, color=Fore.WHITE, tag=tag, active=active)
    if logger:
        logger.debug(f"{tag: <15} {_msg}")


def ilog(*msg, tag: str = "[INFO]", active=True, logger=None):
    _msg = _cleaned_msg(*msg)
    _log(_msg, color=Fore.BLUE, tag=tag, active=active)
    if logger:
        logger.info(f"{tag: <15} {_msg}")


def elog(*msg, tag: str = "[ERROR]", active=True, logger=None):
    _msg = _cleaned_msg(*msg)
    _log(_msg, color=Fore.RED, tag=tag, active=active)
    if logger:
        logger.error(f"{tag: <15} {_msg}")


def flog(*msg, tag: str = "[FATAL]", active=True, logger=None):
    _msg = _cleaned_msg(*msg)
    _log(_msg, color=Fore.RED, tag=tag, active=active)
    if logger:
        logger.fatal(f"{tag: <15} {_msg}")


def okaylog(*msg, tag: str = "[OK]", active=True, logger=None):
    _msg = _cleaned_msg(*msg)
    _log(_msg, color=Fore.GREEN, tag=tag, active=active)
    if logger:
        logger.info(f"{tag: <15} {_msg}")


def wlog(*msg, tag: str = "[???]", active=True, logger=None):
    _msg = _cleaned_msg(*msg)
    _log(_msg, color=Fore.YELLOW, tag=tag, active=active)
    if logger:
        logger.warning(f"{tag: <15} {_msg}")


def breaklog(show_time=False):
    """
    blue console-output
    """
    if show_time:
        ilog(f'{strftime("%Y-%m-%d %H:%M:%S", gmtime())}\n', tag="#")
    ilog("=====================================================\n\n", tag="#")


def set_logging_file(_log_filename="default.log"):
    logger.add(os.path.join(get_path_logs(), _log_filename), rotation="100 MB")


# ##############################################################


def save_check_dir(*dirs):
    for _d in dirs:
        if not os.path.isdir(_d):
            dlog(_d, tag="[CREATED]")
            pathlib.Path(_d).mkdir(parents=True, exist_ok=True)


def _get_path(name, *args) -> str:
    from server.settings import DEFAULT_DIRS
    return os.path.join(DEFAULT_DIRS.get(name), *args)


def get_path_videos(*args) -> str:
    return _get_path("upload", "video", args)


def get_path_upload(*args) -> str:
    return _get_path("upload", args)


def get_path_setup(*args) -> str:
    return _get_path("setup", args)


def get_path_backup(*args) -> str:
    return _get_path("backup", args)


def get_path_logs(*args) -> str:
    return _get_path("logs", args)


def get_path_projects(*args) -> str:
    return _get_path("projects", args)


def get_project_evaluation_dir(project_id) -> str:
    _path = build_abs_path(["evaluations", project_id])
    save_check_dir(_path)
    return _path


def build_abs_path(path_list: list) -> str:
    from server.settings import MEDIA_ROOT
    _abs_path = os.path.abspath(MEDIA_ROOT)
    return os.path.join(_abs_path, *path_list)


def get_rel_path(_path, _dir="media") -> str:
    _index = _path.find(_dir)
    return _path[_index:]


def random_string(letter_count, digit_count):
    str1 = "".join((random.choice(string.ascii_letters) for _ in range(letter_count)))
    str1 += "".join((random.choice(string.digits) for _ in range(digit_count)))

    sam_list = list(str1)       # it converts the string to list.
    random.shuffle(sam_list)    # It uses a random.shuffle() function to shuffle the string.
    return "".join(sam_list)

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


def get_fields_from_bit(_bit):
    if _bit == 0:
        return {}

    binary_str = bin(_bit)[:1:-1]
    return [int(bit) for bit in binary_str]


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


def is_image(filename):
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    _, ext = os.path.splitext(filename)
    return ext.lower() in image_extensions


def is_video(filename):
    image_extensions = {'.mp4', '.wepm'}
    _, ext = os.path.splitext(filename)
    return ext.lower() in image_extensions


def find_uploaded_file(base_dir, filename_pattern):
    _base_name = os.path.basename(filename_pattern)
    for root, _, files in os.walk(base_dir):
        for filename in fnmatch.filter(files, _base_name):
            return os.path.join(root, filename)
    return None


def count_images_in_folder(folder_path):
    # Initialize image counter
    image_count = 0
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if is_image(file):
                image_count += 1
    return image_count


def pretty_sizeof(num, suffix="b"):
    if abs(num) < 1024.0:
        return f"{(num/1024):3.1f}K{suffix}"
    for unit in ["", "K", "M", "G", "T"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Y{suffix}"


def pretty_now():
    return str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
