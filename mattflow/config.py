'''
=============================================================================
@file   config.py
@author Thanasis Mattas

Configuration of the simulation

MattFlow is free software; you may redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version. You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
=============================================================================
'''


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


# Pre-processing configuration {
#
# Number of cells on x and y axis
Nx = 105
Ny = 105

# Number of ghost cells (used for applying Boundary Conditions)
# Depends on the used numerical scheme
Ng = 1

# Domain (basin) limits
MIN_X = -1.2
MAX_X = 1.2
MIN_Y = -1.2
MAX_Y = 1.2
#
# }


# Solution configuration {
#
# Ending conditions of the simulation
STOPPING_TIME = 3
MAX_ITERS = 800

# Courant number
COURANT = 0.6

# Surface level
SURFACE_LEVEL = 1

# Simulation modes (initialization types)
# ---------------------------------------
# Supported:
# 1. 'single drop': modeled via a gaussian distribution
# 1. 'drops'      : configure N_DROPS and ITERS_FOR_NEXT_DROP
# 1. 'rain'       : random drops
MODE = 'drops'

# Number of drops
N_DROPS = 6

# Number of iterations between drops
ITERS_FOR_NEXT_DROP = 100

# Boundary conditions
# -------------------
# Supported:
# 1. 'reflective'
BOUNDARY_CONDITIONS = 'reflective'

# Finite Volume Numerical Methods
# -------------------------------
# Supported:
# 1. 'Lax-Friedrichs Riemann'     : 1st order in time: O(Δt, Δx^2, Δy^2)
# 2. '2-stage Runge-Kutta'        : 2nd order in time: O(Δt^2, Δx^2, Δy^2)
# 2. 'MacCormack experimental'    : 2nd order in time: O(Δt^2, Δx^2, Δy^2)
SOLVER_TYPE = '2-stage Runge-Kutta'
#
# }


# Post-processing configuration {
#
# Plotting style
# Options: water, contour, wireframe
PLOTTING_STYLE = 'wireframe'

# Render the basin that contains the fluid
# Options: 'ON', 'OF'
SHOW_BASIN = 'OF'

# Show the animation
# Options: 'ON', 'OF'
SHOW_ANIMATION = 'ON'

# Saving the animation
# Options: 'ON', 'OF'
SAVE_ANIMATION = 'OF'

# Directory where ffmpeg is installed
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
# Options: 'ON', 'OF'
DAT_WRITING_MODE = 'OF'
#
# }
