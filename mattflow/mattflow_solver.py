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

import numpy as np

from mattflow import boundaryConditionsManager
from mattflow import config as conf
from mattflow import dat_writer
from mattflow import flux
from mattflow import initializer
from mattflow import logger
from mattflow import mattflow_post


def solve(U, delta_t, it, drops_count):
    """evaluates the state variables (h, hu, hv) at a new time-step

    it can be used in a for/while loop, iterating through each time-step

    Args:
        U (3D array)      :  the state variables, populating a x,y grid
        delta_t (float)   :  time discretization step
        it (int)          :  current iteration
        drops_count (int) :  number of drops been generated

    Returns:
        U, drops
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
        if conf.FIXED_ITERS_BETWEEN_DROPS:
            drop_condition = (it % conf.FIXED_ITERS_TO_NEXT_DROP == 0
                              and drops_count < conf.N_DROPS)
        else:
            drop_condition = (it == conf.ITERS_TO_NEXT_DROP[drops_count]
                              and drops_count < conf.N_DROPS)
        if drop_condition:
            U[0, :, :] = initializer.drop(U[0, :, :], drops_count + 1)
            drops_count += 1
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
    return U, drops_count

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


def simulate():
    time = 0
    dx = conf.dx
    dy = conf.dy

    # Initialization
    logger.log('Initialization...')
    U = initializer.initialize()
    drops_count = 1

    # This will hold the step-wise solutions for the post-processing animation.
    # (save a frame every 3 iters)
    U_array = np.zeros([conf.MAX_ITERS // 3, conf.Nx, conf.Ny])
    U_array[0] = U[0, conf.Ng: -conf.Ng, conf.Ng: -conf.Ng]

    # This will hold the step-wise time for the post-processing animation.
    # (time * 10 is appended, because space is scaled about x10)
    time_array = np.array([0])

    for it in range(1, conf.MAX_ITERS):

        # Time discretization step (CFL condition)
        delta_t = dt(U)

        # Update current time
        time += delta_t
        if time > conf.STOPPING_TIME:
            break
        time_array = np.hstack((time_array, [time * 10]))

        # Apply boundary conditions (reflective)
        U = boundaryConditionsManager.updateGhostCells(U)

        # Numerical iterative scheme
        U, drops_count = solve(U, delta_t, it, drops_count)

        # write dat | default: False
        if conf.DAT_WRITING_MODE:
            dat_writer.writeDat(
                U[0, conf.Ng: conf.Ny + conf.Ng, conf.Ng: conf.Nx + conf.Ng],
                time, it
            )
            mattflow_post.plotFromDat(time, it)
        elif not conf.DAT_WRITING_MODE:
            # Append current frame to the list, to be animated at post-processing
            if not (it - 1) % 3:
                try:
                    U_array[(it - 1) // 3] = \
                        U[0, conf.Ng: -conf.Ng, conf.Ng: -conf.Ng]
                except IndexError:
                    pass
        else:
            logger.log("Configure DAT_WRITING_MODE | Options: True, False")

        logger.log_timestep(it, time)
    #
    # }

    # clean-up memap
    if conf.DUMP_MEMMAP and conf.WORKERS > 1:
        utils.delete_memmap()

    return U_array, time_array


