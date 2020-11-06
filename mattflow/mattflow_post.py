# mattflow_post.py is part of MattFlow
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
"""Handles the post-processing of the simulation"""

from datetime import datetime
import os

import numpy as np
import matplotlib.animation as animation
import matplotlib.pyplot as plt

from mattflow import config as conf, logger, utils
from mattflow.utils import time_this


def _plot_basin(sub):
    """plots the basin that contains the fluid

    Args:
        sub (subplot) : Axes3D subplot object
    """
    if conf.SHOW_BASIN is True:
        # make basin a bit wider, because water appears to be out of the basin
        # because of the perspective mode
        X_bas, Y_bas = np.meshgrid(conf.CX[conf.Ng - 1: conf.Nx + conf.Ng + 1],
                                   conf.CY[conf.Ng - 1: conf.Ny + conf.Ng + 1])
        # BASIN
        BASIN = np.zeros((conf.Ny + 2, conf.Nx + 2))
        # left-right walls
        BASIN[:, 0] = 2.5
        BASIN[:, conf.Nx + 1] = 2.5
        # top-bottom walls
        BASIN[0, :] = 2.5
        BASIN[conf.Ny + 1, :] = 2.5
        sub.plot_surface(X_bas, Y_bas, BASIN, rstride=2, cstride=2, linewidth=0,
                         color=(0.4, 0.4, 0.5, 0.1))
    elif conf.SHOW_BASIN is False:
        pass
    else:
        logger.log("Configure SHOW_BASIN. Options: True, False")


def _data_from_dat(it):
    """pulls solution data from a dat file"""
    zeros_left = (4 - len(str(it))) * '0'
    file_name = 'solution' + zeros_left + str(it) + '.dat'

    dat_path = os.path.join(os.getcwd(), "data_files", file_name)
    with open(dat_path, 'r') as fr:
        Nx = int(fr.readline().split(":")[1])
        Ny = int(fr.readline().split(":")[1])
        # Ng = int(fr.readline().split(":")[1])
        time = float(fr.readline().split(":")[1])

    # hu and hv are not written in the dat file, to reduce the overhead
    # x, y, h, hu, hv = np.loadtxt('./data_files/' + file_name, skiprows = 4,
    #                              unpack = True)
    x, y, h = np.loadtxt('./data_files/' + file_name, skiprows=4, unpack=True)
    # unpack the row-major vectors into matrices
    X = x.reshape(Ny, Nx)
    Y = y.reshape(Ny, Nx)
    Z = h.reshape(Ny, Nx)
    return X, Y, Z, Nx, Ny


def plot_from_dat(time, it):
    """creates and saves a frame as png, reading data from a dat file

    Args:
        time (float) : current time
        it (int)     : current itereration
    """
    # create ./session directory for saving the results
    utils.create_child_dir("session")

    # extract data from dat
    X, Y, Z, Nx, Ny = _data_from_dat(it)

    # plot {
    #
    fig = plt.figure(figsize=(9.6, 6.4), dpi=112)  # 1080x720
    sub = fig.add_subplot(111, projection="3d")
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)

    if conf.PLOTTING_STYLE == 'water':
        if conf.ROTATION:
            # rotate the domain:
            # horizontally every 8 frames and vetically every 20 frames
            horizontal_rotate = 45 + it / 8
            vertical_rotate = 55 - it / 20
            sub.view_init(vertical_rotate, horizontal_rotate)
        else:
            sub.view_init(45, 55)
        sub.plot_surface(X, Y, Z,
                         rstride=1, cstride=1, linewidth=0,
                         color=(0.251, 0.643, 0.875, 0.95),
                         shade=True, antialiased=False)
    elif conf.PLOTTING_STYLE == 'contour':
        sub.view_init(45, 55)
        sub.contour3D(X, Y, Z, 140, cmap='plasma', vmin=0.6, vmax=1.4)
    elif conf.PLOTTING_STYLE == 'wireframe':
        if conf.ROTATION:
            # rotate the domain:
            # horizontally every 3 frames and vetically every 4 frames
            horizontal_rotate = 45 + it / 3
            vertical_rotate = 55 - it / 4
            sub.view_init(vertical_rotate, horizontal_rotate)
        else:
            sub.view_init(45, 55)
        sub.plot_wireframe(X, Y, Z, rstride=2, cstride=2, linewidth=1,)
    else:
        logger.log("Configure PLOTTING_STYLE | options: 'water', 'contour',",
                   "'wireframe'")

    fig.gca().set_zlim([-0.5, 4])
    plt.title(f"time: {time: >{6}.3f}\titer: {it: >{4}d}", y=0.8, fontsize=18)
    sub.title.set_position([0.51, 0.80])
    plt.rcParams.update({'font.size': 20})
    plt.axis('off')

    # render the basin that contains the fluid
    _plot_basin(sub)

    # save
    # fig.tight_layout()
    fig_file = os.path.join("session", f"iter_{it:0>{4}}.png")
    plt.savefig(fig_file)
    plt.close()
    #
    # }


def _save_ani(ani, fps, dpi):
    """saves the animation

    Args:
        ani (obj) : animation.FuncAnimation() object
        fps (int) : frames per second
        dpi (int) : dots per inch
    """
    if conf.SAVE_ANIMATION is True:
        # file name
        date_n_time = str(datetime.now())[:19]
        # replace : with - for windows file name format
        date_n_time = date_n_time.replace(':', '-').replace(' ', '_')
        file_name = conf.MODE + '_animation_' + date_n_time

        # configure the writer
        plt.rcParams['animation.ffmpeg_path'] = conf.PATH_TO_FFMPEG
        FFwriter = animation.FFMpegWriter(
            fps=fps, bitrate=-1,
            extra_args=['-r', str(fps), '-pix_fmt', 'yuv420p', '-vcodec',
                        'libx264', '-qscale:v', '1']
        )

        # save
        try:
            ani.save(file_name + '.' + conf.VID_FORMAT,
                     writer=FFwriter, dpi=dpi)

            # log only if a log file is already initialzed
            if logger.find_log() and logger.is_open(logger.find_log()):
                logger.log('Animation saved as: ' + file_name + '.'
                           + conf.VID_FORMAT + ' | fps: ' + str(fps))

            # convert to a lighter gif
            cmd = 'ffmpeg -i ' + file_name + '.' + conf.VID_FORMAT + ' -vf '   \
                  '"fps=' + str(fps) + ',scale=240:-1:flags=lanczos,split'     \
                  '[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" -hide_banner' \
                  ' -loglevel panic -loop 0 ' + file_name + '.gif'
            os.system(cmd)
            if logger.find_log() and logger.is_open(logger.find_log()):
                logger.log('Animation saved as: ' + file_name + '.gif'
                           + ' | fps: ' + str(fps))
        except FileNotFoundError:
            logger.log('Configure PATH_TO_FFMPEG')
    elif conf.SAVE_ANIMATION is False:
        pass
    else:
        logger.log("Configure SAVE_ANIMATION | Options: True, False")


def _update_plot(frame_number, X, Y, Z, plot, fig, sub, t_hist, ani_title):
    """plots a single frame

    used from FuncAnimation to iteratively create a timelapse animation

    Args:
        frame_number (int)  : current frame
        X, Y, Z (2D arrays) : meshgrid and values
        plot (list)         : list holding current plot
        fig (figure)        : activated plt.figure
        sub (subplot)       : Axes3D subplot object
        t_hist (list)   : holds the iter-wise times
        ani_title (str)     : to be formated with the frame_number
    """
    if conf.PLOTTING_STYLE == 'water':
        plot[0].remove()
        if conf.ROTATION:
            # rotate the domain:
            # horizontally every 2 frames and vetically every 4 frames
            horizontal_rotate = 45 + frame_number / 2
            vertical_rotate = 55 - frame_number / 4
            sub.view_init(vertical_rotate, horizontal_rotate)
        plot[0] = sub.plot_surface(X, Y, Z[frame_number],
                                   rstride=1, cstride=1, linewidth=0,
                                   color=(0.251, 0.643, 0.875, 0.95),
                                   shade=True, antialiased=False)
    elif conf.PLOTTING_STYLE == 'contour':
        # Bliting with contour is not supported (because the corresponding
        # attributes are not artists), so the subplot has to be re-built.
        # That's why fig is passed.
        sub.clear()
        sub.view_init(45, 55)
        plt.subplots_adjust(left=0, bottom=0, right=1, top=1,
                            wspace=0, hspace=0)
        fig.gca().set_zlim([-0.5, 4])
        plt.axis('off')
        plot[0] = sub.contour3D(X, Y, Z[frame_number], 120, cmap='ocean',
                                vmin=0.5, vmax=1.5)
    elif conf.PLOTTING_STYLE == 'wireframe':
        plot[0].remove()
        if conf.ROTATION:
            # rotate the domain:
            # horizontally every 3 frames and vetically every 2 frames
            horizontal_rotate = 45 + frame_number / 2
            vertical_rotate = 55 - frame_number / 4
            sub.view_init(vertical_rotate, horizontal_rotate)
        plot[0] = sub.plot_wireframe(X, Y, Z[frame_number],
                                     rstride=2, cstride=2, linewidth=1)

    # reverse engineer the iteration
    it = (
        frame_number
        + ((frame_number // conf.CONSECUTIVE_FRAMES)
           * (conf.FRAME_SAVE_FREQ - conf.CONSECUTIVE_FRAMES))
    )

    # frame title
    if t_hist is not None:
        ani_title = \
            f"time: {t_hist[frame_number]: >{6}.3f}    iter: {it: >{4}d}"
    plt.title(ani_title, y=0.8, fontsize=18)
    sub.title.set_position([0.51, 0.80])


@time_this
def animate(h_hist, t_hist=None):
    """generates and saves a timelapse of the simulation

        h_hist (array) :  array of iter-wise heights solutions
        t_hist (array) :  holds the iter-wise times
    """
    # resolution = figsize * dpi
    # --------------------------
    # example:
    # figsize = (9.6, 5.4), dpi=200
    # resolution: 1920x1080 (1920/200=9.6)
    fps = conf.FPS
    dpi = conf.DPI
    figsize = conf.FIGSIZE

    # total frames
    frames = len(h_hist)

    # X, Y, Z
    X, Y = np.meshgrid(conf.CX[conf.Ng: -conf.Ng], conf.CY[conf.Ng: -conf.Ng])
    Z = h_hist

    # plot configuration
    fig = plt.figure(figsize=figsize, dpi=dpi)
    sub = fig.add_subplot(111, projection="3d")
    sub.view_init(45, 55)
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
    fig.gca().set_zlim([-0.5, 4])
    plt.axis('off')
    if t_hist is None:
        ani_title = f"mesh: {conf.Nx}x{conf.Ny}    solver: {conf.SOLVER_TYPE}"
    else:
        ani_title = f"time: {t_hist[0]: >{6}.3f}    iter: {0: >{5}d}"
    plt.title(ani_title, y=0.8, fontsize=18)
    sub.title.set_position([0.51, 0.80])
    plt.rcParams.update({'font.size': 20})

    # initialization plot
    if conf.PLOTTING_STYLE == 'water':
        plot = [sub.plot_surface(X, Y, Z[0],
                                 rstride=1, cstride=1, linewidth=0,
                                 color=(0.251, 0.643, 0.875, 0.9),
                                 shade=True, antialiased=False)]
    elif conf.PLOTTING_STYLE == 'contour':
        plot = [sub.contour3D(X, Y, Z[0], 150, cmap='ocean',
                              vmin=0.5, vmax=1.5)]
    elif conf.PLOTTING_STYLE == 'wireframe':
        plot = [sub.plot_wireframe(X, Y, Z[0], rstride=2, cstride=2,
                                   linewidth=1)]
    else:
        logger.log("Configure PLOTTING_STYLE | options: 'water', 'contour',",
                   "'wireframe'")
    # render the basin that contains the fluid
    _plot_basin(sub)

    # generate the animation
    ani = animation.FuncAnimation(
        fig, _update_plot, frames,
        fargs=(X, Y, Z, plot, fig, sub, t_hist, ani_title),
        interval=1000 / fps,
        repeat=True
    )

    # save the animation
    _save_ani(ani, fps, dpi)

    # Play the animation
    if conf.SHOW_ANIMATION is True:
        logger.log('Playing animation...')
        try:
            # In case of jupyter notebook, don't run plt.show(), to prevent
            # displaying a static figure. Instead, return the ani object.
            get_ipython()
            return ani
        except NameError:
            plt.show()
    elif conf.SHOW_ANIMATION is False:
        pass
    else:
        logger.log("Configure SHOW_ANIMATION | Options: True, False")
