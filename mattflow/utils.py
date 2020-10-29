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
from functools import wraps
import os
import random
import shutil
from timeit import default_timer as timer

import numpy as np

from mattflow import config as conf, logger


def cell_centers():
    """generates the cell centers along the x and y axes"""
    cx = np.arange(conf.MIN_X + (0.5 - conf.Ng) * conf.dx,
                   conf.MAX_X + conf.Ng * conf.dx,
                   conf.dx)
    cy = np.arange(conf.MIN_Y + (0.5 - conf.Ng) * conf.dy,
                   conf.MAX_Y + conf.Ng * conf.dy,
                   conf.dy)
    return cx, cy


def delete_prev_runs_data():
    """deletes previous log, dat and png files (for debugging)"""
    working_dir = os.getcwd()
    directories = [os.path.join(working_dir, "data_files/"),
                   os.path.join(working_dir, "session/")]
    extensions = (".dat", ".log", ".png", ".gif", ".mp4", ".npy")
    for f in os.listdir(working_dir):
        if f.endswith(extensions):
            os.remove(f)
    for dir in directories:
        if os.path.isdir(dir):
            shutil.rmtree(dir)


def U_shape():
    return (3, conf.Nx + 2 * conf.Ng, conf.Ny + 2 * conf.Ng)


def ds_shape():
    return (conf.MAX_ITERS, 3, conf.Nx, conf.Ny)


def delete_memmap():
    try:
        shutil.rmtree(conf.MEMMAP_DIR)
    except FileNotFoundError:
        print("Could not clean-up the memmap folder")


def print_duration(start, end, process):
    """prints the duration of a process"""
    process_name = {
        "main": "Total",
        "simulate": "Solution",
        "createAnimation": "Post-processing"
    }
    if process in process_name:
        process = process_name[process]
    prefix = f"{process.capitalize()} duration"
    duration = timedelta(seconds=end - start)
    print(f"{prefix:-<30}{duration}"[:40])


def create_child_dir(dirname):
    """create a directory under the current working directory"""
    try:
        if os.path.isdir(os.path.join(os.getcwd(), dirname)):
            pass
        else:
            os.mkdir(os.path.join(os.getcwd(), dirname))
    except OSError:
        print("Unable to create ./" + dirname + " directory")


def time_this(f):
    """function timer decorator

    - Uses wraps to preserve the metadata of the decorated function
      (__name__ and __doc__)
    - logs the duration
    - prints the duration

    Args:
        f(funtion)      : the function to be decorated

    Returns:
        wrap (function) : returns the result of the decorated function
    """
    @wraps(f)
    def wrap(*args, **kwargs):
        start = timer()
        result = f(*args, **kwargs)
        end = timer()
        logger.log_duration(start, end, f.__name__)
        print_duration(start, end, f.__name__)
        return result
    return wrap


def preprocessing(Nx, Ny, Ng, max_x, min_x, max_y, min_y):
    """constructs the mesh

    - dx, dy: Spatial discretization steps (structured/Cartesian mesh)
    - cy, cy: Cell centers on x and y dimensions
    """
    conf.Nx = Nx
    conf.Ny = Ny
    conf.Ng = Ng
    conf.MAX_X = max_x
    conf.MIN_X = min_x
    conf.MAX_Y = max_y
    conf.MIN_Y = min_y
    conf.dx = (max_x - min_x) / Nx
    conf.dy = (max_y - min_y) / Ny
    conf.CX, conf.CY = cell_centers()
    conf.COURANT = min(0.9, 0.015 / min(conf.dx, conf.dy))
    conf.DROPS_CX = [x * max_x for x in conf.DIMLESS_DCX]
    conf.DROPS_CY = [y * max_y for y in conf.DIMLESS_DCY]


def drop_iters_list():
    """list with the simulation iters at which a drop is going to fall"""
    drop_iters = [0]
    iters_cumsum = 0
    i = 0
    if conf.ITERS_BETWEEN_DROPS_MODE == "custom":
        while iters_cumsum <= conf.MAX_ITERS:
            iters_cumsum += conf.CUSTOM_ITERS_BETWEEN_DROPS[i % 10]
            drop_iters.append(iters_cumsum)
            i += 1
    elif conf.ITERS_BETWEEN_DROPS_MODE == "random":
        while iters_cumsum <= conf.MAX_ITERS:
            iters_cumsum += random.randint(60, 120)
            drop_iters.append(iters_cumsum)
    else:
        logger.log("Configure ITERS_BETWEEN_DROPS_MODE | options:"
                   " 'fixed', 'custom', 'random'")
    # Overwrite max number of drops
    conf.MAX_N_DROPS = len(drop_iters)

    if conf.SAVE_DS_FOR_ML:
        # It is needed to retrieve the new drop frames, because these frames
        # cannot be used as labels (the previous frame cannot know when and
        # where a new drop will fall).
        # ds_shape
        dss = ds_shape()
        file_name = f"drop_iters_list_{dss[0]}x{dss[1]}x{dss[2]}x{dss[3]}.npy"
        np.save(os.path.join(os.getcwd(), file_name), drop_iters)
    return drop_iters
