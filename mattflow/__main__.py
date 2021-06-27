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
"""Executes pre-processing, solution and post-processing."""

import click

from mattflow import (config as conf,
                      logger,
                      mattflow_post,
                      mattflow_solver,
                      utils)
from mattflow.utils import time_this


def _configure(**kwargs):
    conf.MODE = kwargs.get("mode", "drops")
    conf.MAX_N_DROPS = kwargs.get("drops", 5)
    conf.MAX_ITERS = 90 * conf.MAX_N_DROPS + 150
    conf.PLOTTING_STYLE = kwargs.get("style", "wireframe")
    conf.ROTATION = kwargs.get("rotation", True)
    conf.SHOW_BASIN = kwargs.get("basin", False)
    conf.SHOW_ANIMATION = kwargs.get("show", True)
    conf.SAVE_ANIMATION = kwargs.get("save", False)
    conf.VID_FORMAT = kwargs.get("format", "mp4")
    conf.FPS = kwargs.get("fps", 18)
    conf.DPI = kwargs.get("dpi", 75)
    conf.FIG_HEIGHT = kwargs.get("fig_height", 18)


@click.command()
@click.option('-m', "--mode", default="drops", show_default=True,
              type=click.Choice(["drop", "drops", "rain"],
                                case_sensitive=False))
@click.option('-d', "--drops", type=click.INT, default=5, show_default=True,
              help="number of drops to generate")
@click.option('-s', "--style", default="wireframe", show_default=True,
              type=click.Choice(["water", "contour", "wireframe"],
                                case_sensitive=False))
@click.option("--rotation/--no-rotation", default=True, show_default=True,
              help="rotate the domain")
@click.option('-b', "--basin", is_flag=True, help="render the fluid basin")
@click.option("--show/--no-show", default=True, show_default=True)
@click.option("--save", is_flag=True)
@click.option("--format", default="mp4", show_default=True,
              type=click.Choice(["mp4", "gif"], case_sensitive=False))
@click.option("--fps", type=click.INT, default=18, show_default=True)
@click.option("--dpi", type=click.INT, default=75, show_default=True)
@click.option("--fig-height", type=click.INT, default=18, show_default=True,
              help="figure height (width is 1.618 * height)")
@time_this
def main(**kwargs):
    _configure(**kwargs)
    # Uncomment this to delete previous log, dat and png files (for debugging).
    # utils.delete_prev_runs_data()

    # Pre-processing (mesh construction)
    utils.preprocessing(kwargs.get("mode", "drops"))

    # Solution
    h_hist, t_hist, U_ds = mattflow_solver.simulate()

    # Post-processing
    mattflow_post.animate(h_hist, t_hist)


if __name__ == "__main__":
    main()

    # Close the log file
    logger.close()
