'''
@file   utilities.py
@author Thanasis Mattas

Provides some useful-generic functions.

MattFlow is free software; you may redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version. You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
'''


import os

from mattflow import config as conf


def delete_logs_dats_images_videos():
    """deletes previous log, dat and png files (for debugging)"""
    working_dir = os.getcwd()
    directories = [os.path.join(working_dir, "data_files/"),
                   os.path.join(working_dir, "session/")]
    extensions = (".dat", ".log", ".png", ".gif", ".mp4")
    for f in os.listdir(working_dir):
        if f.endswith(extensions):
            os.remove(f)
    for dir in directories:
        if os.path.isdir(dir):
            os.rmdir(dir)


def delete_memmap():
    import shutil

    try:
        shutil.rmtree(conf.MEMMAP_DIR)
    except FileNotFoundError:
        print("Could not clean-up the memmap folder")
