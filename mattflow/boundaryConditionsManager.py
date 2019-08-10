'''
=============================================================================
@file   boundaryConditionsManager.py  
@author Thanasis Mattas

Handles the boundary conditions.

MattFlow is free software; you may redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version. You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
=============================================================================
'''


from mattflow import config as conf
import numpy as np

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


def updateGhostCells(U):
    """
    implements boundary conditions
    ------------------------------
    @param U    : state-variables-3D-array  
    returns U
    """
    if conf.BOUNDARY_CONDITIONS == 'reflective':
        # left wall (0 <= x < Ng)
        U[0, :, :conf.Ng] = np.flip(U[0, :, conf.Ng: 2 * conf.Ng], 1)
        U[1, :, :conf.Ng] = - np.flip(U[1, :, conf.Ng: 2 * conf.Ng], 1)
        U[2, :, :conf.Ng] = np.flip(U[2, :, conf.Ng: 2 * conf.Ng], 1)

        # right wall (Nx + Ng <= x < Nx + 2Ng)
        U[0, :, conf.Nx + conf.Ng: conf.Nx + 2 * conf.Ng] \
            = np.flip(U[0, :, conf.Nx: conf.Nx + conf.Ng], 1)
        U[1, :, conf.Nx + conf.Ng: conf.Nx + 2 * conf.Ng] \
            = - np.flip(U[1, :, conf.Nx: conf.Nx + conf.Ng], 1)
        U[2, :, conf.Nx + conf.Ng: conf.Nx + 2 * conf.Ng] \
            = np.flip(U[2, :, conf.Nx: conf.Nx + conf.Ng], 1)

        # left wall (0 <= y < Ng)
        U[0, :conf.Ng, :] = np.flip(U[0, conf.Ng: 2 * conf.Ng, :], 0)
        U[1, :conf.Ng, :] = np.flip(U[1, conf.Ng: 2 * conf.Ng, :], 0)
        U[2, :conf.Ng, :] = - np.flip(U[2, conf.Ng: 2 * conf.Ng, :], 0)

        # right wall (Ny + Ng <= y < Ny + 2Ng)
        U[0, conf.Ny + conf.Ng: conf.Ny + 2 * conf.Ng, :] \
            = np.flip(U[0, conf.Ny: conf.Ny + conf.Ng, :], 0)
        U[1, conf.Ny + conf.Ng: conf.Ny + 2 * conf.Ng, :] \
            = np.flip(U[1, conf.Ny: conf.Ny + conf.Ng, :], 0)
        U[2, conf.Ny + conf.Ng: conf.Ny + 2 * conf.Ng, :] \
            = - np.flip(U[2, conf.Ny: conf.Ny + conf.Ng, :], 0)
    return U
