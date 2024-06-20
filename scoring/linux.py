import os
import platform
import subprocess

from django.utils.timezone import make_aware

from scoring.helper import elog, dlog

import re
from datetime import datetime


def extract_date_from_filename(filename):
    # Define the regex pattern to match the date and time in the filename
    pattern = r"\d{4}-\d{2}-\d{2}-\d{6}"

    # Search for the pattern in the filename
    match = re.search(pattern, filename)

    if match:
        # Extract the date string
        date_str = match.group()
        # Convert the date string to a datetime object
        return make_aware(datetime.strptime(date_str, "%Y-%m-%d-%H%M%S"))
    else:
        return None


def change_file_owner(file_path, new_owner=None):
    if platform.system() == "Linux":
        if os.geteuid() != 0:
            elog("You need to have root privileges to change the file owner.")
            return
        new_owner = os.getenv("SYS_USER", new_owner if new_owner else "user")

        try:
            subprocess.run(["chown", new_owner, file_path], check=True)
            dlog(f"The owner of the file '{file_path}' has been changed to '{new_owner}'.")
        except subprocess.CalledProcessError as e:
            elog(f"Error changing owner: {e}")
    else:
        elog("This system is not running Linux.")
