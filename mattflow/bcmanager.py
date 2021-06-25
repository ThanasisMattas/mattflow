# bcmanager.py is part of MattFlow
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
"""Handles the boundary conditions."""

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


import numpy as np

from mattflow import config as conf


def update_ghost_cells(U):
    """Implements the boundary conditions.

    reflective boundary conditions:

    + vertical walls (x=X_MIN, x=X_max)
        - h : dh/dx = 0 (Neumann)     h_0 = h_-1   (1 ghost cell)
                                      h_1 = h_-2   (2 ghost cells)

        - u : u = 0    (Dirichlet)    u_0 = -u_-1  (1 ghost cell)
                                      u_1 = -u_-2  (2 ghost cells)

        - v : dv/dx = 0 (Neumann)     v_0 = v_-1   (1 ghost cell)
                                      v_1 = v_-2   (2 ghost cells)

    + horizontal walls (y=Y_MIN, y=Y_max)
        - h : dh/dy = 0 (Neumann)     h_0 = h_-1   (1 ghost cell)
                                      h_1 = h_-2   (2 ghost cells)

        - u : du/dy = 0 (Neumann)     u_0 = u_-1   (1 ghost cell)
                                      u_1 = u_-2   (2 ghost cells)

        - v : v = 0    (Dirichlet)    v_0 = -v_-1  (1 ghost cell)
                                      v_1 = -v_-2  (2 ghost cells)

    Args:
        U (3D array) :  the state variables, populating a x,y grid

    Returns:
        U
    """
    Nx = conf.Nx
    Ny = conf.Ny
    Ng = conf.Ng

    if conf.BOUNDARY_CONDITIONS == 'reflective':
        # left wall (0 <= x < Ng)
        U[0, :, :Ng] = np.flip(U[0, :, Ng: 2 * Ng], 1)
        U[1, :, :Ng] = - np.flip(U[1, :, Ng: 2 * Ng], 1)
        U[2, :, :Ng] = np.flip(U[2, :, Ng: 2 * Ng], 1)

        # right wall (Nx + Ng <= x < Nx + 2Ng)
        U[0, :, Nx + Ng: Nx + 2 * Ng] \
            = np.flip(U[0, :, Nx: Nx + Ng], 1)
        U[1, :, Nx + Ng: Nx + 2 * Ng] \
            = - np.flip(U[1, :, Nx: Nx + Ng], 1)
        U[2, :, Nx + Ng: Nx + 2 * Ng] \
            = np.flip(U[2, :, Nx: Nx + Ng], 1)

        # top wall (0 <= y < Ng)
        U[0, :Ng, :] = np.flip(U[0, Ng: 2 * Ng, :], 0)
        U[1, :Ng, :] = np.flip(U[1, Ng: 2 * Ng, :], 0)
        U[2, :Ng, :] = - np.flip(U[2, Ng: 2 * Ng, :], 0)

        # bottom wall (Ny + Ng <= y < Ny + 2Ng)
        U[0, Ny + Ng: Ny + 2 * Ng, :] \
            = np.flip(U[0, Ny: Ny + Ng, :], 0)
        U[1, Ny + Ng: Ny + 2 * Ng, :] \
            = np.flip(U[1, Ny: Ny + Ng, :], 0)
        U[2, Ny + Ng: Ny + 2 * Ng, :] \
            = - np.flip(U[2, Ny: Ny + Ng, :], 0)
    return U
