# MattFlow is free software; you may redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version. You should have received a copy of the GNU
# General Public License along with this program. If not, see
# <https://www.gnu.org/licenses/>.
# ======================================================================
"""
info:
    file        : __main__.py
    author      : Thanasis Mattas
    license     : GNU General Public License v3
    description : Executes pre-processing, solution and post-processing
"""


"""
    Welcome to MattFlow!
                        """


from datetime import timedelta
from timeit import default_timer as timer

import numpy as np

from mattflow import boundaryConditionsManager
from mattflow import config as conf
from mattflow import initializer
from mattflow import logger
from mattflow import mattflow_post
from mattflow import mattflow_solver
from mattflow import utilities as util


def main():
    # Recording of the duration of the simulation
    start = timer()

    # Pre-processing {
    #
    # Spatial discretization steps (structured/cartetian mesh)
    dx = (conf.MAX_X - conf.MIN_X) / conf.Nx
    dy = (conf.MAX_Y - conf.MIN_Y) / conf.Ny

    # Cell centers on x and y dimensions
    cx = np.arange(conf.MIN_X + (0.5 - conf.Ng) * dx,
                   conf.MAX_X + conf.Ng * dx,
                   dx)
    cy = np.arange(conf.MIN_Y + (0.5 - conf.Ng) * dy,
                   conf.MAX_Y + conf.Ng * dy,
                   dy)
    #
    # }

    # Uncomment this to delete previous log, dat and png files (for debugging)
    util.delete_logs_dats_images_videos()

    # Solution {
    #
    time = 0

    # Initialization
    logger.log('Initialization...')
    U = initializer.initialize(cx, cy)
    drops_count = 1

    # This will hold the step-wise solutions for the post-processing animation.
    # (save a frame every 3 iters)
    U_stepwise_for_animation = np.zeros([conf.MAX_ITERS // 3, conf.Nx, conf.Ny])
    U_stepwise_for_animation[0] = U[0, conf.Ng: -conf.Ng, conf.Ng: -conf.Ng]

    # This will hold the step-wise time for the post-processing animation.
    # (time * 10 is appended, because space is scaled about x10)
    time_array_for_animation = np.array([0])

    for iter in range(1, conf.MAX_ITERS):

        # Time discretization step (CFL condition)
        delta_t = mattflow_solver.dt(U, dx, dy)

        # Update current time
        time += delta_t
        if time > conf.STOPPING_TIME:
            break
        time_array_for_animation = np.hstack((time_array_for_animation,
                                              [time * 10]))

        # Apply boundary conditions (reflective)
        U = boundaryConditionsManager.updateGhostCells(U)

        # Numerical iterative scheme
        U, drops_count = mattflow_solver.solve(U, dx, cx, dy, cy, delta_t,
                                               iter, drops_count)
        # Append current frame to the list, to be animated at post-processing
        if not (iter - 1) % 3:
            U_stepwise_for_animation[(iter - 1) // 3] = \
                U[0, conf.Ng: -conf.Ng, conf.Ng: -conf.Ng]

        logger.log_timestep(iter, time)
    #
    # }

    # clean-up memap
    if conf.DUMP_MEMMAP and conf.WORKERS > 1:
        util.delete_memmap()

    # Duration of the solution
    solution_end = timer()
    logger.log('Solution duration' + 11 * '-'
               + str(timedelta(seconds=solution_end - start)))

    # Post-processing
    mattflow_post.createAnimation(U_stepwise_for_animation, cx, cy,
                                  time_array_for_animation)

    # Post-processing duration
    end = timer()
    logger.log('Post-processing duration' + 4 * '-'
               + str(timedelta(seconds=end - solution_end)))

    # Total duration
    logger.log('Total duration' + 14 * '-'
               + str(timedelta(seconds=end - start)))

    # Close the log file
    logger.close()


if __name__ == "__main__":
    main()
