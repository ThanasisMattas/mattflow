'''
@file   boundaryConditionsManager.py  
@author Thanasis Mattas

Handles the boundary conditions.

MattFlow is free software; you may redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version. You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
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

    @param U    : 3D matrix of the state variables, populating a x,y grid  
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

        # top wall (0 <= y < Ng)
        U[0, :conf.Ng, :] = np.flip(U[0, conf.Ng: 2 * conf.Ng, :], 0)
        U[1, :conf.Ng, :] = np.flip(U[1, conf.Ng: 2 * conf.Ng, :], 0)
        U[2, :conf.Ng, :] = - np.flip(U[2, conf.Ng: 2 * conf.Ng, :], 0)

        # bottom wall (Ny + Ng <= y < Ny + 2Ng)
        U[0, conf.Ny + conf.Ng: conf.Ny + 2 * conf.Ng, :] \
            = np.flip(U[0, conf.Ny: conf.Ny + conf.Ng, :], 0)
        U[1, conf.Ny + conf.Ng: conf.Ny + 2 * conf.Ng, :] \
            = np.flip(U[1, conf.Ny: conf.Ny + conf.Ng, :], 0)
        U[2, conf.Ny + conf.Ng: conf.Ny + 2 * conf.Ng, :] \
            = - np.flip(U[2, conf.Ny: conf.Ny + conf.Ng, :], 0)
    return U
