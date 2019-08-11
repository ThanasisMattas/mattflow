'''
=============================================================================
@file   __main__.py  
@author Thanasis Mattas

Script that executes all the required processes for the simulation.

MattFlow is free software; you may redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version. You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
=============================================================================
'''


'''
    Welcome to MattFlow!
                        '''


from mattflow import config as conf
from mattflow import utilities as util
from mattflow import logger
from mattflow import initializer
from mattflow import boundaryConditionsManager
from mattflow import mattflow_solver
from mattflow import mattflow_post
import numpy as np
from timeit import default_timer as timer


def main():
    # Recording of the duration of the simulation
    start = timer()

    # Pre-processing {
    #
    # Spatial discretization steps (structured/cartetian mesh)
    dx = (conf.MAX_X - conf.MIN_X) / conf.Nx
    dy = (conf.MAX_Y - conf.MIN_Y) / conf.Ny

    # Cell centers on x and y dimentions
    cx = np.arange(conf.MIN_X + (0.5 - conf.Ng) * dx,
                                 conf.MAX_X + conf.Ng * dx, dx)
    cy = np.arange(conf.MIN_Y + (0.5 - conf.Ng) * dy,
                                 conf.MAX_Y + conf.Ng * dy, dy)
    #
    # }

    # Uncomment this to delete previous log, dat and png files (for debugging)
    util.delete_logs_dats_images()

    # Solution {
    #
    time = 0

    # Initialization
    logger.log('Initialization...')
    U = initializer.initialize(cx, cy)
    drops = 1

    # This will hold the step-wise solutions for the post-processing animation.
    U_stepwise_for_animation = [U[0, conf.Ng: -conf.Ng, conf.Ng: -conf.Ng]]

    # This will hold the step-wise time for the post-processing animation.
    # time * 10 is appended, because space is scaled about x10
    time_array_for_ani = np.array([0])
    update_time_array = lambda t : np.hstack((time_array_for_ani, [t * 10]))

    for iter in range(1, conf.MAX_ITERS):     # conf.MAX_ITERS

        # Time discretization step (CFL condition)
        delta_t = mattflow_solver.dt(U, dx, dy)

        # Update current time
        time += delta_t
        if time > conf.STOPPING_TIME:
            break
        time_array_for_ani = update_time_array(time)

        # Apply boundary conditions (reflective)
        U = boundaryConditionsManager.updateGhostCells(U)

        # Numerical iterative scheme
        U, drops = mattflow_solver.solve(U, dx, cx, dy, cy, delta_t, iter, drops)

        # Append current frame to the list, to be animated at post-processing
        U_stepwise_for_animation = np.append(U_stepwise_for_animation,
            [U[0, conf.Ng: -conf.Ng, conf.Ng: -conf.Ng]], 0)

        spaces = 6 - len(str(iter))     # for vertical printing alignment
        logger.log('iter:' + spaces * ' ' + str(iter) + '    time: '
                   + str('{:0.3f}'.format(time)))
    #
    # }

    # Duration of the solution
    solution_end = timer()
    logger.log('Solution duration' + 11 * '-'
            + util.secs_to_time(solution_end - start))

    # Post-processing
    mattflow_post.createAnimation(U_stepwise_for_animation, cx, cy,
                                  time_array_for_ani)

    # Post-processing duration
    end = timer()
    logger.log('Post-processing duration' + 4 * '-'
            + util.secs_to_time(end - solution_end))

    # Total duration
    logger.log('Total duration' + 14 * '-'
            + util.secs_to_time(end - start))


if __name__ == "__main__":
    main()
