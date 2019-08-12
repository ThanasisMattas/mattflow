'''
@file   mattflow_solver.py  
@author Thanasis Mattas

Handles the solution of the simulation.

MattFlow is free software; you may redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version. You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
'''


from mattflow import config as conf
from mattflow import logger
from mattflow import flux
from mattflow import initializer
from mattflow import dat_writer
import random
import numpy as np


# TODO implement high order schemes


def solve(U, dx, cx, dy, cy, delta_t, iter, drops):
    """
    evaluates the state variables (h, hu, hv) at a new time-step
    ------------------------------------------------------------
    it can be used in a for/while loop, iterating through each time-step

    @param U          : 3D matrix of the state variables, populating a x,y grid  
    @param dx         : spatial discretization step on x axis  
    @param cx         : cell centers on x axis  
    @param dy         : spatial discretization step on y axis  
    @param cy         : cell centers on y axis  
    @param delta_t    : time discretization step  
    @param iter       : current iteration  
    @param drops      : number of drops been generated  
    returns U, drops
    """
    # Simulation mode
    # ---------------
    # 'single drop': handled at the initialization
    if conf.MODE == 'single drop':
        pass
    # 'drops': specified number of drops are generated at specified frequency
    elif conf.MODE == 'drops':
        if iter % conf.ITERS_FOR_NEXT_DROP == 0 and drops < conf.N_DROPS:
            U[0, :, :] = initializer.drop(U[0, :, :], cx, cy)
            drops += 1
    # 'rain': random number of drops are generated at random frequency
    elif conf.MODE == 'rain':
        if iter % random.randrange(1, 15) == 0:
            for simultaneous_drops in range(random.randrange(1, 2)):
                U[0, :, :] = initializer.drop(U[0, :, :], cx, cy)
    else:
        logger.log("Configure MODE | options: 'single drop', 'drops', 'rain'")

    cellArea = dx * dy
    Nx = conf.Nx
    Ny = conf.Ny
    Ng = conf.Ng

    # Numerical scheme
    # flux.flux(U) returns the total flux entering and leaving each cell
    if conf.SOLVER_TYPE == 'Lax-Friedrichs Riemann':
        U[:, Ng: -Ng, Ng: -Ng] \
            += delta_t / cellArea * flux.flux(U, dx, dy)
    elif conf.SOLVER_TYPE == '2-stage Runge-Kutta':
        # 1st stage
        U_pred = U
        U_pred[:, Ng: -Ng, Ng: -Ng] += delta_t / cellArea * flux.flux(U, dx, dy)

        # 2nd stage
        U[:, Ng: -Ng, Ng: -Ng] = 0.5 * (U[:, Ng: -Ng, Ng: -Ng]
                               + U_pred[:, Ng: -Ng, Ng: -Ng]
                               + delta_t / cellArea * flux.flux(U_pred, dx, dy))
    else:
        looger.log("Configure SOLVER_TYPE | Options: 'Lax-Friedrichs Riemann',",
                   "' 2-stage Runge-Kutta'")
    return U, drops


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

    # write dat | default: False
    if conf.DAT_WRITING_MODE is False:
        pass
    elif conf.DAT_WRITING_MODE is True:
        time = iter * delta_t
        dat_writer.writeDat(U[0, Ng: Ny + Ng, Ng: Nx + Ng], cx, cy, time, iter)
        # mattFlow_post.plotFromDat(time=0, iter=0)
    else:
        logger.log("Configure DAT_WRITING_MODE | Options: True, False")


def dt(U, dx, dy):
    """
    evaluates the time discretization step of the current iteration
    ---------------------------------------------------------------
    The stability condition of the numerical simulation (Known as
    Courant–Friedrichs–Lewy or CFL condition) describes that the solution velocity
    (dx/dt) has to be greater than the wave velocity. Namely, the simulation has
    to run faster than the information, in order to evaluate it. The wave velocity
    used is the greatest velocity of the waves that contribute to the fluid,
    which is the greatest eagenvalue of the Jacobian matrix df(U)/dU (|u| + c),
    along the x axis, and dG(U)/dU (|v| + c), along the y axis.

    We equate    
                      dx/dt = wave_vel => dt = dx / wave_vel
    
    and the magnitude that the solution velocity is greater than the wave velocity
    is handled by the Courant number (<= 1). Namely, 
    
                             dt_final = dt * Courant.

    The velocity varies at each point of the grid, consisting the velocity field.
    So, dt is evaluated at every cell, as the mean of the dt's at x and y
    directions. Finally, the minimum dt of all cells is returned, as the time-step
    of the current iteration.

    The velocity field is step-wisely changing and, thus, the calculation of dt
    is repeated at each iteration, preserving consistency with the CFL condition.

    @param U          : 3D matrix of the state variables, populating a x,y grid  
    @param dx         : spatial discretization step on x axis  
    @param dy         : spatial discretization step on y axis  
    returns dt        : time discretization step 
    """
    # h = U[0]
    # u = U[1] / h
    # v = U[2] / h
    # g = 9.81
    # c = np.sqrt(abs(g * h))

    # dt_x = dx / (abs(u) + c)
    # dt_y = dy / (abs(v) + c)

    dt_x = dx / (np.abs(U[1] / U[0]) + np.sqrt(np.abs(9.81 * U[0])))
    dt_y = dy / (np.abs(U[2] / U[0]) + np.sqrt(np.abs(9.81 * U[0])))
    dt = 1.0 / (1.0 / dt_x + 1.0 / dt_y)
    return np.min(dt) * conf.COURANT
