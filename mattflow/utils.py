# utils.py is part of MattFlow
#
# MattFlow is free software; you may redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version. You should have received a copy of the GNU
# General Public License along with this program. If not, see
# <https://www.gnu.org/licenses/>.
#
# (C) 2019 Athanasios Mattas
# ======================================================================
"""Provides some helper functions"""

from datetime import timedelta
import os
import shutil

import numpy as np

from mattflow import config as conf


def cell_centers():
    """generates the cell centers along the x and y axes"""
    cx = np.arange(conf.MIN_X + (0.5 - conf.Ng) * conf.dx,
                   conf.MAX_X + conf.Ng * conf.dx,
                   conf.dx)
    cy = np.arange(conf.MIN_Y + (0.5 - conf.Ng) * conf.dy,
                   conf.MAX_Y + conf.Ng * conf.dy,
                   conf.dy)
    return cx, cy


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
            shutil.rmtree(dir)


def delete_memmap():
    try:
        shutil.rmtree(conf.MEMMAP_DIR)
    except FileNotFoundError:
        print("Could not clean-up the memmap folder")


def print_duration(start, end, process):
  """prints the duration of a process"""
  dashes = (19 - len(process)) * '-'
  print(process.capitalize() + " duration"
        + dashes
        + str(timedelta(seconds=end - start))[:10])


def create_child_dir(dirname):
  """create a directory under the current working directory"""
  try:
      if os.path.isdir(os.path.join(os.getcwd(), dirname)):
          pass
      else:
          os.mkdir(os.path.join(os.getcwd(), dirname))
  except OSError:
      print("Unable to create ./" + dirname + " directory")
