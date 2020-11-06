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


from mattflow import (logger,
                      mattflow_post,
                      mattflow_solver,
                      utils)
from mattflow.utils import time_this


@time_this
def main():
    # Uncomment this to delete previous log, dat and png files (for debugging)
    # utils.delete_prev_runs_data()

    # Pre-processing (mesh construction)
    utils.preprocessing(Nx=90, Ny=90, Ng=1,
                        max_x=0.7, min_x=-0.7,
                        max_y=0.7, min_y=-0.7)

    # Solution
    h_hist, t_hist, U_ds = mattflow_solver.simulate()

    # Post-processing
    mattflow_post.animate(h_hist, t_hist)


if __name__ == "__main__":
    main()

    # Close the log file
    logger.close()
