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


import numpy as np

from mattflow import (config as conf,
                      dat_writer,
                      initializer,
                      logger,
                      mattflow_post,
                      mattflow_solver,
                      utils)
from mattflow.utils import time_this


@time_this
def main():
    # Uncomment this to delete previous log, dat and png files (for debugging)
    # utils.delete_logs_dats_images_videos()

    # Solution {
    #
    U_array, time_array = mattflow_solver.simulate()

    # Post-processing
    mattflow_post.createAnimation(U_array, time_array)

    # Close the log file
    logger.close()


if __name__ == "__main__":
    main()
