# flux.py is part of MattFlow
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
"""Evaluates the total flux entering or leaving a cell"""

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
#            _ - - - _
#                  _ - - - _
#
# example: 2 slices (workers) with window of 3, for parallel solving
#          (the 'underscore' cells are required by the numerical scheme)

import os

from joblib import Parallel, delayed
from numba import njit
import numpy as np

from mattflow import config as conf


@njit(cache=True, nogil=True)
def _max_horizontal_speed(U, Nx, Ng, parallel=True):
    """Max horizontal speed between left and right cells for every vertical
    interface"""
    g = 9.81
    if parallel:
        max_h_speed = np.maximum(
            # x dim slicing of left values:  0: -1
            np.abs(U[1, Ng: -Ng, 0: -1] / U[0, Ng: -Ng, 0: -1])
            + np.sqrt(g * np.abs(U[0, Ng: -Ng, 0: -1])),

            # x dim slicing of right values:  1:
            np.abs(U[1, Ng: -Ng, 1:] / U[0, Ng: -Ng, 1:])
            + np.sqrt(g * np.abs(U[0, Ng: -Ng, 1:]))
        )
    else:
        max_h_speed = np.maximum(
            # x dim slicing of left values:  Ng - 1: -Ng
            np.abs(U[1, Ng: -Ng, Ng - 1: -Ng] / U[0, Ng: -Ng, Ng - 1: -Ng])
            + np.sqrt(g * np.abs(U[0, Ng: -Ng, Ng - 1: Nx + Ng])),

            # x dim slicing of right values:  Ng: Nx + Ng + 1
            np.abs(U[1, Ng: -Ng, Ng: Nx + Ng + 1]
                   / U[0, Ng: -Ng, Ng: Nx + Ng + 1])
            + np.sqrt(g * np.abs(U[0, Ng: -Ng, Ng: Nx + Ng + 1]))
        )
    return max_h_speed


@njit(cache=True, nogil=True)
def _max_vertical_speed(U, Ny, Ng, parallel=True):
    """Max vertical speed between top and bottom cells for every horizontal
    interface"""
    g = 9.81
    if parallel:
        x_limit = 1
    else:
        x_limit = Ng

    max_v_speed = np.maximum(
        # y dim slicing of top values:  Ng - 1: -Ng
        np.abs(U[1, Ng - 1: -Ng, x_limit: -x_limit]
               / U[0, Ng - 1: -Ng, x_limit: -x_limit])
        + np.sqrt(g * np.abs(U[0, Ng - 1: -Ng, x_limit: -x_limit])),

        # y dim slicing of bottom values:  Ng: Nx + Ng + 1
        np.abs(U[1, Ng: Ny + Ng + 1, x_limit: -x_limit]
               / U[0, Ng: Ny + Ng + 1, x_limit: -x_limit])
        + np.sqrt(g * np.abs(U[0, Ng: Ny + Ng + 1, x_limit: -x_limit]))
    )
    return max_v_speed


def _F(U):
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


def _G(U):
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


def _horizontal_flux(U, Nx, Ng, dy, maxHorizontalSpeed, parallel=True):
    """Lax-Friedrichs scheme (flux is calculated on each vertical interface)

    flux = 0.5 * (F_left + F_right) - 0.5 * maxSpeed * (U_right - U_left)
    """
    if parallel:
        h_flux = (
            0.5 * (_F(U[:, Ng: -Ng, 0: -1]) + _F(U[:, Ng: -Ng, 1:]))
            - 0.5 * maxHorizontalSpeed * (U[:, Ng: -Ng, 1:]
                                          - U[:, Ng: -Ng, 0: -1])
        )
    else:
        h_flux = (
            0.5 * (_F(U[:, Ng: -Ng, Ng - 1: -Ng])
                   + _F(U[:, Ng: -Ng, Ng: Nx + Ng + 1]))
            - 0.5 * maxHorizontalSpeed * (U[:, Ng: -Ng, Ng: Nx + Ng + 1]
                                          - U[:, Ng: -Ng, Ng - 1: -Ng])
        )
    h_flux *= dy
    return h_flux


def _vertical_flux(U, Ny, Ng, dx, maxVerticalSpeed, parallel=True):
    """Lax-Friedrichs scheme (flux is calculated on each horizontal interface)

    flux = 0.5 * (F_top + F_bottom) - 0.5 * maxSpeed * (U_bottom - U_top)
    """
    if parallel:
        x_limit = 1
    else:
        x_limit = Ng

    v_flux = (
        0.5 * dx * (_G(U[:, Ng - 1: -Ng, x_limit: -x_limit])
                    + _G(U[:, Ng: Ny + Ng + 1, x_limit: -x_limit]))
        - 0.5 * dx * maxVerticalSpeed
            * (U[:, Ng: Ny + Ng + 1, x_limit: -x_limit]
                - U[:, Ng - 1: -Ng, x_limit: -x_limit])
    )
    return v_flux


def _flux_batch(U, window=None, slicing_obj=None,
                flux_out=None, idx=None, parallel=True):
    """evaluates the total flux that enters or leaves a cell, using the \
    Lax-Friedrichs scheme

    It runs by each joblib worker on a slice of the domain
    (the horizontal [x] axis is sliced)

    Args:
        U (3D array)        : the state variables 3D matrix
        window (int)        : the effective width of a slice
                              (default None, in case of single-processing)
        slicing_obj (slice) : slice of the domain (1 + window + 1)
                              (default None, in case of single-processing)
        flux_out (3D array) : container of the results of each worker
                              (default None, in case of single-processing)
        idx (int)           : the index in flux_out of the current results
                              (default None, in case of single-processing)
        parallel (bool)     : multi or single processing

    Returns:
        total_flux (3D array)
    """
    g = 9.81
    Nx = conf.Nx
    Ny = conf.Ny
    Ng = conf.Ng
    dx = conf.dx
    dy = conf.dy

    if parallel:
        x_limit = 1
        U_batch = U[:, :, slicing_obj]
        total_flux = np.zeros(((3, Ny + 2 * Ng, window + 2)))
    else:
        x_limit = Ng
        U_batch = U
        total_flux = np.zeros(((3, Ny + 2 * Ng, Nx + 2 * Ng)))

    # Vertical interfaces - Horizontal flux {
    #
    # Max horizontal speed between left and right cells for every interface
    maxHorizontalSpeed = _max_horizontal_speed(U_batch, Nx, Ng,
                                               parallel=parallel)

    # Lax-Friedrichs scheme
    # flux = 0.5 * (F_left + F_right) - 0.5 * maxSpeed * (U_right - U_left)
    # flux is calculated on each interface
    horizontalFlux = _horizontal_flux(U_batch, Nx, Ng, dy, maxHorizontalSpeed,
                                      parallel=parallel)

    # horizontalFlux is subtracted from the left and added to the right cells
    if parallel:
        total_flux[:, Ng: -Ng, 0: U_batch.shape[2] - 1] -= horizontalFlux
        total_flux[:, Ng: -Ng, 1: U_batch.shape[2]] += horizontalFlux
    else:
        total_flux[:, Ng: -Ng, Ng - 1: -Ng] -= horizontalFlux
        total_flux[:, Ng: -Ng, Ng: Nx + Ng + 1] += horizontalFlux
    # }

    # Horizontal interfaces - Vertical flux {
    #
    # Max vertical speed between top and bottom cells for every interface
    # (for the vertical calculations the extra horizontal cells are not needed)
    maxVerticalSpeed = _max_vertical_speed(U_batch, Ny, Ng, parallel=parallel)

    # Lax-Friedrichs scheme
    # flux = 0.5 * (F_top + F_bottom) - 0.5 * maxSpeed * (U_bottom - U_top)
    verticalFlux = _vertical_flux(U_batch, Ny, Ng, dx, maxVerticalSpeed,
                                  parallel=parallel)

    # verticalFlux is subtracted from the top and added to the bottom cells
    if parallel:
        total_flux[:, Ng - 1: -Ng, 1: U_batch.shape[2] - 1] -= verticalFlux
        total_flux[:, Ng: Ny + Ng + 1, 1: U_batch.shape[2] - 1] += verticalFlux
    else:
        total_flux[:, Ng - 1: -Ng, Ng: -Ng] -= verticalFlux
        total_flux[:, Ng: Ny + Ng + 1, Ng: -Ng] += verticalFlux
    # }

    # No need to keep ghost cells --> removes 2*(Nx + Ny) operations stepwise
    # Also, 1st and last nodes of each column are removed (they were only
    # needed from the numerical scheme, to calculate the others)
    if flux_out is not None:
        flux_out[idx] = total_flux[:, Ng: -Ng, x_limit: -x_limit]
    else:
        return total_flux[:, Ng: -Ng, x_limit: -x_limit]


def flux(U):
    """evaluates the total flux that enters or leaves a cell, using the \
    Lax-Friedrichs scheme

    parallel implementation

    Args:
        U (3D array)   : the state variables 3D matrix

    Returns:
        total_flux (3D array)
    """
    Nx = conf.Nx
    Ny = conf.Ny
    Ng = conf.Ng
    workers = conf.WORKERS

    # Although joblib.Parallel can work single-processing, passing the whole
    # state-matrix directly to _flux_batch() is much faster
    if workers == 1:
        return _flux_batch(U, parallel=False)

    # slice the column dimention (x) to the number of workers
    # (divide-ceil)
    window = -(-(Nx + 2 * Ng) // workers)

    # the extra cells at the two ends are required by the numerical scheme
    #
    # say Ng = 2, window = 30:
    # slices = [slice(1, 33, slice(31, 63), slice(61, 63), ...]
    slices = [slice(start - 1, start + window + 1)
              for start in range(Ng, Nx + 2 * Ng, window)]

    if conf.DUMP_MEMMAP:
        # pre-allocate a writeable shared memory map as a container for the
        # results of the parallel computation, to be shared by all workers
        try:
            os.mkdir(conf.MEMMAP_DIR)
        except FileExistsError:
            pass
        memmap_file = os.path.join(conf.MEMMAP_DIR, "flux_memmap")
        flux_out = np.memmap(memmap_file, dtype=np.dtype('float64'),
                             shape=(len(slices), 3, Ny, window),
                             mode="w+")

        Parallel(n_jobs=workers)(
            delayed(_flux_batch)(U, window, slicing_obj, flux_out, idx)
            for idx, slicing_obj in enumerate(slices)
        )
    else:
        flux_out = np.zeros([len(slices), 3, Ny, window])

        flux_out = Parallel(n_jobs=workers)(
            delayed(_flux_batch)(U, window, slicing_obj)
            for slicing_obj in slices
        )

    total_flux = np.concatenate(flux_out, axis=2)

    # Ghost cells are not needed for the calculations.
    # Also, last slice appended some extra columns that must be left out.
    return total_flux[:, :, : Nx]
