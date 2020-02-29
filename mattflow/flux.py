'''
@file   flux.py
@author Thanasis Mattas

Evaluates the total flux entering or leaving a cell.

MattFlow is free software; you may redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version. You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
'''


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
#
#          -----     -----
#               -----     -----
#
# current example: 4 slices (workers) with window of 5 for parallel solving
#                  (last column will be removed)


import os

from joblib import Parallel, delayed, dump, load
import numpy as np

from mattflow import config as conf


def flux_batch(U, dx, dy, window, sl, flux_out=None, idx=None):
    """evaluates the total flux that enters or leaves a cell, using the \
    Lax-Friedrichs scheme

    It runs by each joblib worker.

    Args:
        U (3D array)   : the state variables 3D matrix
        dx (float)     : x axis discretiazation step
        dy (float)     : y axis discretiazation step

    Returns:
        total_flux (3D array)
    """
    g = 9.81
    Nx = conf.Nx
    Ny = conf.Ny
    Ng = conf.Ng
    U_batch = U[:, :, sl]
    total_flux = np.zeros(((3, Ny + 2 * Ng, window + 2)))

    # Vertical interfaces - Horizontal flux {
    #
    # Max horizontal speed between left and right cells for every interface
    maxHorizontalSpeed = np.maximum(
        # x dim slicing of left values:  0: -1
        np.abs(U_batch[1, Ng: -Ng, 0: -1] / U_batch[0, Ng: -Ng, 0: -1])
        + np.sqrt(g * np.abs(U_batch[0, Ng: -Ng, 0: -1])),

        # x dim slicing of right values:  1:
        np.abs(U_batch[1, Ng: -Ng, 1:] / U_batch[0, Ng: -Ng, 1:])
        + np.sqrt(g * np.abs(U_batch[0, Ng: -Ng, 1:]))
    )

    # Lax-Friedrichs scheme
    # flux = 0.5 * (F_left + F_right) - 0.5 * maxSpeed * (U_right - U_left)
    # flux is calculated on each interface
    horizontalFlux \
        = 0.5 * (F(U_batch[:, Ng: -Ng, 0: -1])
                 + F(U_batch[:, Ng: -Ng, 1:])) \
        - 0.5 * maxHorizontalSpeed \
              * (U_batch[:, Ng: -Ng, 1:] - U_batch[:, Ng: -Ng, 0: -1])
    horizontalFlux *= dy

    # horizontalFlux is subtracted from the left and added to the right cells
    total_flux[:, Ng: -Ng, 0: U_batch.shape[2] - 1] -= horizontalFlux
    total_flux[:, Ng: -Ng, 1: U_batch.shape[2]] += horizontalFlux
    # }


    # Horizontal interfaces - Vertical flux {
    #
    # Max vertical speed between top and bottom cells for every interface
    # (for the vertical calculations the extra horizontal cells are not needed)
    maxVerticalSpeed = np.maximum(
        # y dim slicing of top values:  Ng - 1: -Ng
        np.abs(U_batch[1, Ng - 1: -Ng, 1: -1] / U_batch[0, Ng - 1: -Ng, 1: -1])
        + np.sqrt(g * np.abs(U_batch[0, Ng - 1: -Ng, 1: -1])),

        # y dim slicing of bottom values:  Ng: Nx + Ng + 1
        np.abs(U_batch[1, Ng: Ny + Ng + 1, 1: -1]
               / U_batch[0, Ng: Ny + Ng + 1, 1: -1])
        + np.sqrt(g * np.abs(U_batch[0, Ng: Ny + Ng + 1, 1: -1]))
    )

    # Lax-Friedrichs scheme
    # flux = 0.5 * (F_top + F_bottom) - 0.5 * maxSpeed * (U_bottom - U_top)
    verticalFlux \
        = 0.5 * (G(U_batch[:, Ng - 1: -Ng, 1: -1])
                 + G(U_batch[:, Ng: Ny + Ng + 1, 1: -1])) \
        - 0.5 * maxVerticalSpeed \
              * (U_batch[:, Ng: Ny + Ng + 1, 1: -1]
                 - U_batch[:, Ng - 1: -Ng, 1: -1])
    verticalFlux *= dx

    # verticalFlux is subtracted from the top and added to the bottom cells
    total_flux[:, Ng - 1: -Ng, 1: U_batch.shape[2] - 1] -= verticalFlux
    total_flux[:, Ng: Ny + Ng + 1, 1: U_batch.shape[2] - 1] += verticalFlux
    # }

    # No need to keep ghost cells --> removes 2*(Nx + Ny) operations stepwise
    # Also, the 1st and the 2 last nodes of each column are removed (they
    # were only needed from the scheme, to calculate the others)
    if flux_out is not None:
        flux_out[idx] = total_flux[:, Ng: -Ng, 1: -1]
    else:
        return total_flux[:, Ng: -Ng, 1: -1]


def flux(U, dx, dy):
    """evaluates the total flux that enters or leaves a cell, using the \
    Lax-Friedrichs scheme

    parallel implementation

    Args:
        U (3D array)   : the state variables 3D matrix
        dx (float)     : x axis discretiazation step
        dy (float)     : y axis discretiazation step

    Returns:
        total_flux (3D array)
    """
    # Although joblib.Parallel can work single-processing, the following
    # implementaion is much faster
    if conf.WORKERS == 1:
        return flux_serial(U, dx, dy)

    Nx = conf.Nx
    Ny = conf.Ny
    Ng = conf.Ng
    workers = conf.WORKERS
    # slice the column dimention (x) to the number of workers
    # devide-ceil
    window = -(-(Nx + 2 * Ng) // workers)
    window = 5

    # the extra cells at the two ends are required by the iterative scheme
    #
    # say Ng =2, window = 30:
    # [slice(1, 33, slice(31, 63), slice(61, 63), ...]
    slices = [slice(start - 1, start + window + 1)
              for start in range(Ng, Nx + 2 * Ng, window)]

    if conf.DUMP_MEMMAP:
        # pre-allocate a writeable shared memory map as a container for the
        # results of the parallel computation
        try:
            os.mkdir(conf.MEMMAP_DIR)
        except FileExistsError:
            pass
        memmap_file = os.path.join(conf.MEMMAP_DIR, "flux_memmap")
        flux_out = np.memmap(memmap_file, dtype=np.dtype('float64'),
                             shape=(len(slices), 3, Ny, window),
                             mode="w+")

        Parallel(n_jobs=workers)(
            delayed(flux_batch)(U, dx, dy, window, sl, flux_out, idx)
            for idx, sl in enumerate(slices)
        )
    else:
        flux_out = np.zeros([len(slices), 3, Ny, window])

        flux_out = Parallel(n_jobs=workers)(
            delayed(flux_batch)(U, dx, dy, window, sl)
            for sl in slices
        )

    total_flux = np.concatenate(flux_out, axis=2)

    # Ghost cells are not needed for the calculations.
    # Also, last slice appended some extra columns that must be left out.
    return total_flux[:, :, : Nx]  # Ng: - Ng]


def flux_serial(U, dx, dy):
    """evaluates the total flux that enters or leaves a cell, using the \
    Lax-Friedrichs scheme

    NOT-parallel implementation

    Args:
        U (3D array)   : the state variables 3D matrix
        dx (float)     : x axis discretiazation step
        dy (float)     : y axis discretiazation step

    Returns:
        total_flux (3D array)
    """
    g = 9.81
    Nx = conf.Nx
    Ny = conf.Ny
    Ng = conf.Ng
    total_flux = np.zeros(((3, Ny + 2 * Ng, Nx + 2 * Ng)))

    # Vertical interfaces - Horizontal flux {
    #
    # Max horizontal speed between left and right cells for every interface
    maxHorizontalSpeed = np.maximum(
        # x dim slicing of left values:  Ng - 1: -Ng
        np.abs(U[1, Ng: -Ng, Ng - 1: -Ng] / U[0, Ng: -Ng, Ng - 1: -Ng])
        + np.sqrt(g * np.abs(U[0, Ng: -Ng, Ng - 1: Nx + Ng])),

        # x dim slicing of right values:  Ng: Nx + Ng + 1
        np.abs(U[1, Ng: -Ng, Ng: Nx + Ng + 1] / U[0, Ng: -Ng, Ng: Nx + Ng + 1])
        + np.sqrt(g * np.abs(U[0, Ng: -Ng, Ng: Nx + Ng + 1]))
    )

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
        # y dim slicing of top values:  Ng - 1: -Ng
        np.abs(U[1, Ng - 1: -Ng, Ng: -Ng] / U[0, Ng - 1: -Ng, Ng: -Ng])
        + np.sqrt(g * np.abs(U[0, Ng - 1: -Ng, Ng: -Ng])),

        # y dim slicing of bottom values:  Ng: Nx + Ng + 1
        np.abs(U[1, Ng: Ny + Ng + 1, Ng: -Ng] / U[0, Ng: Ny + Ng + 1, Ng: -Ng])
        + np.sqrt(g * np.abs(U[0, Ng: Ny + Ng + 1, Ng: -Ng]))
    )

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

    # No need to return ghost cells --> removes 2*(Nx + Ny) operations stepwise
    return total_flux[:, Ng: -Ng, Ng: -Ng]


def F(U):
    """evaluates the x-dimention-fluxes-vector, F
    Args:
        U (3D array) : the state variables 3D matrix
    """

    '''
    h = U[0]
    u = U[1] / h
    v = U[2] / h

    # 0.5 * g = 0.5 * 9.81 = 4.905
    return np.array([h * u, h * u**2 + 4.905 * h**2, h * u * v])
    '''
    return np.array([U[1],
                     U[1]**2 / U[0] + 4.905 * U[0]**2,
                     U[1] * U[2] / U[0]])


def G(U):
    """evaluates the y-dimention-fluxes-vector, G
    Args:
        U (3D array) : the state variables 3D matrix
    """

    '''
    h = U[0]
    u = U[1] / h
    v = U[2] / h

    # 0.5 * g = 0.5 * 9.81 = 4.905
    return np.array([h * v, h * u * v, h * v**2 + 4.905 * h**2])
    '''
    return np.array([U[2],
                     U[1] * U[2] / U[0],
                     U[2]**2 / U[0] + 4.905 * U[0]**2])
