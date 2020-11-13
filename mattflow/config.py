# config.py is part of MattFlow
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
"""Configures the simulation, providing global constants"""

# TODO simple API: configuring options on a small window popup

#                  x
#          0 1 2 3 4 5 6 7 8 9
#        0 G G G G G G G G G G
#        1 G G G G G G G G G G
#        2 G G - - - - - - G G
#        3 G G - - - - - - G G
#      y 4 G G - - - - - - G G
#        5 G G - - - - - - G G
#        6 G G - - - - - - G G
#        7 G G - - - - - - G G
#        8 G G G G G G G G G G
#        9 G G G G G G G G G G

import os


# Pre-processing configuration {
#
# Number of cells on x and y axis
Nx = None
Ny = None

# Number of ghost cells (used for applying Boundary Conditions)
# Depends on the used numerical scheme
Ng = None

# Domain (basin) limits
MIN_X = None
MAX_X = None
MIN_Y = None
MAX_Y = None

# Spatial discretization steps (structured/Cartesian mesh)
dx = None
dy = None

# cell centers along the x and y axes
CX = None
CY = None
#
# }

# Solution configuration {
#
# Ending conditions of the simulation
STOPPING_TIME = 30000
MAX_ITERS = 650

# saving <CONSECUTIVE_FRAMES> frames every <FRAME_SAVE_FREQ> iters
# - resulting to a lighter animation (less fps)
# - visualizing and debugging long simulations
#   e.g. MAX_ITERS = 10000, FREQ = 500, CONSECUTIVE_FRAMES = 25
FRAME_SAVE_FREQ = 3
CONSECUTIVE_FRAMES = 1

# Number of workers for multiprocessing
WORKERS = 1

# Pre-allocate and dump a binary memmap, used by all the workers
DUMP_MEMMAP = False
MEMMAP_DIR = os.path.join(os.getcwd(), "flux_memmap")

# Courant number
# --------------
# dx * COURANT = 0.015 for a more realistic result, in the current fps range
#
#
# dt_sim = dt * COURANT
# dt_sim = dx / wave_vel * COURANT
# dx * COURANT = dt_sim * wave_vel (= dx_sim?)
#
# where:
#   - dt is the time that the slowest wave component (represented by the
#     velocity eagenvector with the min eagenvalue at the jacobian of the
#     non-conservative form of the vectorized representation of the system)
#     takes to travel for dx.
#   - dt_sim is the time that the simulation covers dx
#
COURANT = None

# Surface level
SURFACE_LEVEL = 1

# Simulation modes (initialization types)
# ---------------------------------------
# Supported:
# 1. 'single drop': modeled via a gaussian distribution
# 1. 'drops'      : configure N_DROPS and ITERS_FOR_NEXT_DROP
# 1. 'rain'       : random drops
MODE = 'drops'

# Default max number of drops
# (it will be overwritten if ITERS_BETWEEN_DROPS_MODE in ["random", "custom"])
MAX_N_DROPS = 5

# Number of iterations between drops
# ----------------------------------
# Options:
# 1. 'fixed'  : fixed every 105 iters
# 2. 'custom' : periodically selected from a list of 10 custom iter intervals
# 3. 'random' : between 60 - 120 iters
ITERS_BETWEEN_DROPS_MODE = "random"

FIXED_ITERS_BETWEEN_DROPS = 105
CUSTOM_ITERS_BETWEEN_DROPS = [120, 150, 140, 130, 210, 60, 180, 220, 140, 130]

RANDOM_DROP_CENTERS = True
# Dimensionless x, y drop centers
DIMLESS_DCX = [0, -0.56, 0.28, -0.25, 0.48, -0.42, 0.90, 0.24, -0.78, 0.84]
DIMLESS_DCY = [0, 0.25, 0.48, -0.24, -0.59, -0.64, 0.05, -0.40, 0.63, -0.40]
DROPS_CX = None
DROPS_CY = None

# Boundary conditions
# -------------------
# Supported:
# 1. 'reflective'
BOUNDARY_CONDITIONS = 'reflective'

# Finite Volume Numerical Methods
# -------------------------------
# Supported:
# 1. 'Lax-Friedrichs Riemann'   : 1st order in time: O(Δt, Δx^2, Δy^2)
# 2. '2-stage Runge-Kutta'      : 2nd order in time: O(Δt^2, Δx^2, Δy^2)
# 3. 'MacCormack experimental'  : 2nd order in time: O(Δt^2, Δx^2, Δy^2)
SOLVER_TYPE = '2-stage Runge-Kutta'

# Select whether to save a memmap with the simulation data or not
SAVE_DS_FOR_ML = False
#
# }


# Post-processing configuration {
#
# Plotting style
# Options: water, contour, wireframe
PLOTTING_STYLE = 'wireframe'

# frames per sec
FPS = 20
# dots per inch
DPI = 80
# figure size in inches
# golden ratio: 1.618
FIGSIZE = (10 * 1.618, 10)

# resolution = figsize * dpi
# --------------------------
# example:
# figsize = (9.6, 5.4), dpi=200
# resolution: 1920x1080 (1920/200=9.6)

# Rotate the domain at each frame
ROTATION = True

# Render the basin that contains the fluid
SHOW_BASIN = False

# Show the animation
SHOW_ANIMATION = True

# Saving the animation
SAVE_ANIMATION = False

# Path to ffmpeg
PATH_TO_FFMPEG = '/usr/bin/ffmpeg'

# Animation video format
# ----------------------
# Supported:
# 1. 'mp4'
# 2. 'gif'
VID_FORMAT = 'mp4'

# Writing dat files mode
# ----------------------
# Select whether dat files are generated or not
WRITE_DAT = False


# Select whether a .log file will be generateo or not
LOGGING_MODE = False
#
# }
