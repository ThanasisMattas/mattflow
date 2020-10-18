# __main__.py is part of MattFlow
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
"""Executes pre-processing, solution and post-processing"""


"""
    Welcome to MattFlow!
                        """


from timeit import default_timer as timer

import numpy as np

from mattflow import boundaryConditionsManager
from mattflow import config as conf
from mattflow import dat_writer
from mattflow import initializer
from mattflow import logger
from mattflow import mattflow_post
from mattflow import mattflow_solver
from mattflow import utils


def main():

    start = timer()

    # Pre-processing {
    #
    # Spatial discretization steps (structured/Cartesian mesh)
    dx = conf.dx
    dy = conf.dy
    # Cell centers on x and y dimensions
    cx, cy = utils.cell_centers()
    # }

    # Uncomment this to delete previous log, dat and png files (for debugging)
    # utils.delete_logs_dats_images_videos()

    # Solution {
    #
    time = 0

    # Initialization
    logger.log('Initialization...')
    U = initializer.initialize(cx, cy)
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
        delta_t = mattflow_solver.dt(U, dx, dy)

        # Update current time
        time += delta_t
        if time > conf.STOPPING_TIME:
            break
        time_array = np.hstack((time_array, [time * 10]))

        # Apply boundary conditions (reflective)
        U = boundaryConditionsManager.updateGhostCells(U)

        # Numerical iterative scheme
        U, drops_count = mattflow_solver.solve(U, dx, cx, dy, cy, delta_t,
                                               it, drops_count)

        # write dat | default: False
        if conf.DAT_WRITING_MODE:
            dat_writer.writeDat(
                U[0, conf.Ng: conf.Ny + conf.Ng, conf.Ng: conf.Nx + conf.Ng],
                cx, cy, time, it
            )
            mattflow_post.plotFromDat(time, it, cx, cy)
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

    # Duration of the solution
    solution_end = timer()
    logger.log_duration(start, solution_end, "solution")
    utils.print_duration(start, solution_end, "solution")

    # Post-processing
    mattflow_post.createAnimation(U_array, cx, cy, time_array)

    # Post-processing duration
    end = timer()
    logger.log_duration(solution_end, end, "post-processing")
    utils.print_duration(solution_end, end, "post-processing")

    # Total duration
    logger.log_duration(start, end, "total")
    utils.print_duration(start, end, "total")

    # Close the log file
    logger.close()


if __name__ == "__main__":
    main()
