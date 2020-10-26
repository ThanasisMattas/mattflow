# mattflow_solver.py is part of MattFlow
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
"""Handles the solution of the simulation"""

# TODO: implement high order schemes

import random
import os

import numpy as np

from mattflow import (boundaryConditionsManager,
                      config as conf,
                      dat_writer,
                      flux,
                      initializer,
                      logger,
                      mattflow_post,
                      utils)
from mattflow.utils import time_this


def solve(U,
          delta_t,
          it,
          drops_count,
          drop_its_iterator,
          next_drop_it):
    """evaluates the state variables (h, hu, hv) at a new time-step

    it can be used in a for/while loop, iterating through each time-step

    Args:
        U (3D array)       :  the state variables, populating a x,y grid
        delta_t (float)    :  time discretization step
        it (int)           :  current iteration
        drops_count (int)  :  number of drops been generated
        drop_its_iterator (iterator)
                           :  iterator of the drop_its list (the list with
                              the iters at which a new drop falls)
        next_drop_it (int) :  the next iteration at which drop will fall

    Returns:
        U, drops_count, drop_its_iterator, next_drop_it
    """
    # Retrieve the mesh
    Ng = conf.Ng
    cx = conf.CX
    cy = conf.CY
    cellArea = conf.dx * conf.dy

    # Simulation mode
    # ---------------
    # 'single drop': handled at the initialization
    if conf.MODE == 'single drop':
        pass

    # 'drops': specified number of drops are generated at specified frequency
    elif conf.MODE == 'drops':
        if conf.ITERS_BETWEEN_DROPS_MODE == "fixed":
            drop_condition = (it % conf.FIXED_ITERS_BETWEEN_DROPS == 0
                              and drops_count < conf.MAX_N_DROPS)
        else:  # conf.ITERS_TO_NEXT_DROP_MODE in ["custom", "random"]
            drop_condition = (it == next_drop_it
                              and drops_count < conf.MAX_N_DROPS)

        if drop_condition:
            U[0, :, :] = initializer.drop(U[0, :, :], drops_count + 1)
            drops_count += 1
            if conf.ITERS_BETWEEN_DROPS_MODE in ["custom", "random"]:
                next_drop_it = next(drop_its_iterator)

    # 'rain': random number of drops are generated at random frequency
    elif conf.MODE == 'rain':
        if it % random.randrange(1, 15) == 0:
            for simultaneous_drops in range(random.randrange(1, 2)):
                U[0, :, :] = initializer.drop(U[0, :, :])
    else:
        logger.log("Configure MODE | options: 'single drop', 'drops', 'rain'")

    # Numerical scheme
    # flux.flux() returns the total flux entering and leaving each cell
    if conf.SOLVER_TYPE == 'Lax-Friedrichs Riemann':
        U[:, Ng: -Ng, Ng: -Ng] += delta_t / cellArea * flux.flux(U)
    elif conf.SOLVER_TYPE == '2-stage Runge-Kutta':
        # 1st stage
        U_pred = U
        U_pred[:, Ng: -Ng, Ng: -Ng] += delta_t / cellArea * flux.flux(U)

        # 2nd stage
        U[:, Ng: -Ng, Ng: -Ng] = \
            0.5 * (U[:, Ng: -Ng, Ng: -Ng]
                   + U_pred[:, Ng: -Ng, Ng: -Ng]
                   + delta_t / cellArea * flux.flux(U_pred)
                   )
    else:
        logger.log("Configure SOLVER_TYPE | Options: 'Lax-Friedrichs Riemann',",
                   "' 2-stage Runge-Kutta'")
    return U, drops_count, drop_its_iterator, next_drop_it

    '''
    # Experimenting on the finite differences form of the MacCormack solver
    # TODO somewhere delta_t/dx becomes the greatest eigenvalue of the jacobian
    elif conf.SOLVER_TYPE == 'MacCormack experimental':
        # 1st step: prediction (FTFS)
        U_pred = U
        U_pred[:, Ng: -Ng, Ng: -Ng] = U[:, Ng: -Ng, Ng: -Ng] \
            - delta_t / dx * (flux.F(U[:, Ng: -Ng, Ng + 1: Nx + Ng + 1]) \
                              - flux.F(U[:, Ng: -Ng, Ng: -Ng])) \
            - delta_t / dy * (flux.G(U[:, Ng + 1: Ny + Ng + 1, Ng: -Ng]) \
                              - flux.G(U[:, Ng: -Ng, Ng: -Ng]))

        U_pred = boundaryConditionsManager.updateGhostCells(U_pred)
        delta_t = dt(U_pred, dx, dy)

        # 2nd step: correction (BTBS)
        U[:, Ng: -Ng, Ng: -Ng] \
            = 0.5 * (U[:, Ng: -Ng, Ng: -Ng] + U_pred[:, Ng: -Ng, Ng: -Ng]) \
            - 0.5 * delta_t / dx * (flux.F(U_pred[:, Ng: -Ng, Ng: -Ng]) \
                - flux.F(U_pred[:, Ng: -Ng, Ng - 1: Nx + Ng - 1])) \
            - 0.5 * delta_t / dy * (flux.G(U_pred[:, Ng: -Ng, Ng: -Ng]) \
                - flux.G(U_pred[:, Ng - 1: Ny + Ng - 1, Ng: -Ng]))
    '''


def dt(U):
    """evaluates the time discretization step of the current iteration

    The stability condition of the numerical simulation (Known as
    Courant–Friedrichs–Lewy or CFL condition) describes that the solution
    velocity (dx/dt) has to be greater than the wave velocity. Namely, the
    simulation has to run faster than the information, in order to evaluate
    it. The wave velocity used is the greatest velocity of the waves that
    contribute to the fluid, which is the greatest eagenvalue of the Jacobian
    matrix df(U)/dU, along the x axis, and dG(U)/dU, along the y axis,
    |u| + c and |v| + c respectively.

    We equate

                      dx/dt = wave_vel => dt = dx / wave_vel

    and the magnitude that the solution velocity is greater than the wave
    velocity is handled by the Courant number (<= 1). Namely,

                             dt_final = dt * Courant.

    The velocity varies at each point of the grid, constituting the velocity
    field. So, dt is evaluated at every cell, as the mean of the dt's at x
    and y directions. Finally, the minimum dt of all cells is returned, as
    the time-step of the current iteration, ensuring that the CFL condition
    is met at all cells.

    The velocity field is step-wisely changing and, thus, the calculation
    of dt is repeated at each iteration, preserving consistency with the
    CFL condition.

    If the CFL condition is not met even at one cell, the simulation will not
    evaluate correctly the state variables there, resulting to discontinuities
    with the neighbor cells. These inconsistencies add up and bleed to nearby
    cells and, eventually the simulation (literally) blows up.

    Args:
        U (3D array) :  the state variables, populating a x,y grid

    Returns:
        dt (float)   :  time discretization step
    """
    # h = U[0]
    # u = U[1] / h
    # v = U[2] / h
    # g = 9.81
    # c = np.sqrt(abs(g * h))

    # dt_x = dx / (abs(u) + c)
    # dt_y = dy / (abs(v) + c)

    dt_x = conf.dx / (np.abs(U[1] / U[0]) + np.sqrt(np.abs(9.81 * U[0])))
    dt_y = conf.dy / (np.abs(U[2] / U[0]) + np.sqrt(np.abs(9.81 * U[0])))
    dt = 1.0 / (1.0 / dt_x + 1.0 / dt_y)
    return np.min(dt) * conf.COURANT


@time_this
def simulate():
    time = 0

    U, heights_array, time_array, U_dataset = initializer.initialize()
    drops_count = 1
    # idx of the frame saved in heights_array
    saving_frame_idx = 0
    # counts up to conf.CONSECUTIVE_FRAMES (1st frame saved at initialization)
    consecutive_frames_counter = 1

    if conf.ITERS_BETWEEN_DROPS_MODE in ["custom", "random"]:
        # list with the simulation iterations at which a drop is going to fall
        drop_its = utils.drop_iters_list()
        # drop the 0th drop
        drop_its_iterator = iter(drop_its[1:])
        # the iteration at which the next drop will fall
        next_drop_it = next(drop_its_iterator)
    else:
        drop_its_iterator = None
        next_drop_it = None

    for it in range(1, conf.MAX_ITERS):

        # Time discretization step (CFL condition)
        delta_t = dt(U)

        # Update current time
        time += delta_t
        if time > conf.STOPPING_TIME:
            break

        # Apply boundary conditions (reflective)
        U = boundaryConditionsManager.updateGhostCells(U)

        # Numerical iterative scheme
        U, drops_count, drop_its_iterator, next_drop_it = solve(
            U=U,
            delta_t=delta_t,
            it=it,
            drops_count=drops_count,
            drop_its_iterator=drop_its_iterator,
            next_drop_it=next_drop_it
        )

        if conf.WRITE_DAT:
            dat_writer.writeDat(
                U[0, conf.Ng: conf.Ny + conf.Ng, conf.Ng: conf.Nx + conf.Ng],
                time, it
            )
            mattflow_post.plotFromDat(time, it)
        elif not conf.WRITE_DAT:
            # Append current frame to the list, to be animated at post-processing
            if it % conf.FRAME_SAVE_FREQ == 0:
                # zero the counter, when a perfect devision occurs
                consecutive_frames_counter = 0
            if consecutive_frames_counter < conf.CONSECUTIVE_FRAMES:
                saving_frame_idx += 1
                heights_array[saving_frame_idx] = \
                    U[0, conf.Ng: -conf.Ng, conf.Ng: -conf.Ng]
                # time * 10 is insertd, because space is scaled about x10
                time_array[saving_frame_idx] = time * 10
                consecutive_frames_counter += 1
            if conf.SAVE_DS_FOR_ML:
                U_dataset[it] = U
        else:
            logger.log("Configure WRITE_DAT | Options: True, False")

        logger.log_timestep(it, time)

    # clean-up memap
    if conf.DUMP_MEMMAP and conf.WORKERS > 1:
        utils.delete_memmap()

    return heights_array, time_array, U_dataset
