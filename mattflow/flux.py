'''
=============================================================================
@file   flux.py  
@author Thanasis Mattas

Evaluates the total flux entering or leaving a cell.

MattFlow is free software; you may redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version. You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
=============================================================================
'''


from mattflow import config
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


def flux(U, dx, dy):
    """
    evaluates the total flux that enters or leaves a cell, using the \
    Lax-Friedrichs scheme  
    ---------------------  
    @param U    : the state variables 3D matrix  
    @param dx   : x axis discretiazation step  
    @param dy   : y axis discretiazation step
    returns total_flux
    """
    g = 9.81
    Nx = config.Nx
    Ny = config.Ny
    Ng = config.Ng
    total_flux = np.zeros(((3, Ny + 2 * Ng, Nx + 2 * Ng)))

    # Vertical interfaces - Horizontal flux {
    #
    # Max horizontal speed between left and right cells for every interface
    maxHorizontalSpeed = np.maximum(
        # x dim slicing of left values:  Ng - 1: -Ng
        np.abs(U[1, Ng: -Ng, Ng - 1: -Ng] / U[0, Ng: -Ng, Ng - 1: -Ng])
        + np.sqrt(g * np.abs(U[0, Ng: -Ng, Ng - 1: Nx + Ng])),

        # x dim slicing of right values : Ng: Nx + Ng
        np.abs(U[1, Ng: -Ng, Ng: Nx + Ng + 1] / U[0, Ng: -Ng, Ng: Nx + Ng + 1])
        + np.sqrt(g * np.abs(U[0, Ng: -Ng, Ng: Nx + Ng + 1])))

    # Lax-Friedrichs scheme
    # flux = 0.5 * (F_left + F_right) - 0.5 * maxSpeed * (U_right - U_left)
    # flux is calculated on each interface
    horizontalFlux \
        = 0.5 * (F(U[:, Ng: -Ng, Ng - 1: -Ng])
                 + F(U[:, Ng: -Ng, Ng: Nx + Ng + 1])) \
        - 0.5 * maxHorizontalSpeed \
              * (U[:, Ng: -Ng, Ng: Nx + Ng + 1] - U[:, Ng: -Ng, Ng - 1: -Ng])
    horizontalFlux *= dy

    # horizontalFlux is subtracted from the left and added to the right cells
    total_flux[:, Ng: -Ng, Ng - 1: -Ng] -= horizontalFlux
    total_flux[:, Ng: -Ng, Ng: Nx + Ng + 1] += horizontalFlux
    # }


    # Horizontal interfaces - Vertical flux {
    #
    # Max vertical speed between top and bottom cells for every interface
    maxVerticalSpeed = np.maximum(
        # y dim slicing of top values :  Ng - 1: -Ng
        np.abs(U[1, Ng - 1: -Ng, Ng: -Ng] / U[0, Ng - 1: -Ng, Ng: -Ng])
        + np.sqrt(g * np.abs(U[0, Ng - 1: -Ng, Ng: -Ng])),

        # y dim slicing of bottom values: Ng: Nx + Ng + 1
        np.abs(U[1, Ng: Ny + Ng + 1, Ng: -Ng] / U[0, Ng: Ny + Ng + 1, Ng: -Ng])
        + np.sqrt(g * np.abs(U[0, Ng: Ny + Ng + 1, Ng: -Ng])))

    # Lax-Friedrichs scheme
    # flux = 0.5 * (F_top + F_bottom) - 0.5 * maxSpeed * (U_bottom - U_top)
    verticalFlux \
        = 0.5 * (G(U[:, Ng - 1: -Ng, Ng: -Ng])
                 + G(U[:, Ng: Ny + Ng + 1, Ng: -Ng])) \
        - 0.5 * maxVerticalSpeed \
              * (U[:, Ng: Ny + Ng + 1, Ng: -Ng] - U[:, Ng - 1: -Ng, Ng: -Ng])
    verticalFlux *= dx

    # verticalFlux is subtracted from the top and added to the bottom cells
    total_flux[:, Ng - 1: -Ng, Ng: -Ng] -= verticalFlux
    total_flux[:, Ng: Ny + Ng + 1, Ng: -Ng] += verticalFlux
    # }

    # Don't need to return ghost cells --> removes 2*(Nx + Ny) operations stepwise
    return total_flux[:, Ng: -Ng, Ng: -Ng]


def F(U):
    """
    evaluates the x-dimention-fluxes-vector, F  
    ------------------------------------------  
    @param U    : the state variables 3D matrix
    """

    '''
    h = U[0]
    u = U[1] / h
    v = U[2] / h

    # 0.5 * g = 0.5 * 9.81 = 4.905
    return np.array([h * u, h * u**2 + 4.905 * h**2, h * u * v])
    '''
    return np.array([U[1], U[1]**2 / U[0] + 4.905 * U[0]**2, U[1] * U[2] / U[0]])


def G(U):
    """
    evaluates the y-dimention-fluxes-vector, G  
    ------------------------------------------  
    @param U    : the state variables 3D matrix
    """

    '''
    h = U[0]
    u = U[1] / h
    v = U[2] / h

    # 0.5 * g = 0.5 * 9.81 = 4.905
    return np.array([h * v, h * u * v, h * v**2 + 4.905 * h**2])
    '''
    return np.array([U[2], U[1] * U[2] / U[0], U[2]**2 / U[0] + 4.905 * U[0]**2])
