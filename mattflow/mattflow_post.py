'''
@file   mattflow_post.py  
@author Thanasis Mattas

Handles the post-processing of the simulation.

MattFlow is free software; you may redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version. You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
'''


from mattflow import config as conf
from mattflow import logger
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime
import os


def plotFromDat(time, iter, cx, cy):
    """
    creates and saves a frame as png, reading data from a dat file
    --------------------------------------------------------------
    @param time        : current time  
    @param iter        : current iter
    """
    # create ./session directory for saving the results
    try:
        if os.path.isdir('./session'):
            pass
        else:
            os.mkdir('./session')
    except OSError:
        logger.log("Unable to create data_files directory")

    # extract data from dat
    X, Y, Z, Nx, Ny = dataFromDat()

    # plot {
    #
    fig = plt.figure(figsize=(9.6, 6.4), dpi = 112) # 1080x720
    plt.rcParams.update({'font.size': 8})
    sub = fig.add_subplot(111, projection="3d")
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)

    if conf.PLOTTING_STYLE == 'water':
        sub.plot_surface(X, Y, Z[0], rstride=1, cstride=1, linewidth=0,
            color=(0.251, 0.643, 0.875, 0.9), antialiased=False)
    elif conf.PLOTTING_STYLE == 'contour':
        sub.contour3D(X, Y, Z[0], 140, cmap='plasma',
            vmin=0.6, vmax=1.4)
    elif conf.PLOTTING_STYLE == 'wireframe':
        sub.plot_wireframe(X, Y, Z[0], rstride=2, cstride=2,
            linewidth=0.5,)
    else:
        logger.log("Configure PLOTTING_STYLE | options: 'water', 'contour',",
                   "'wireframe'")

    fig.gca().set_zlim([-0.5, 4])
    plt.title('time: {0:.3f}'.format(time))
    sub.title.set_position([0.51, 0.8])
    plt.axis('off')
    sub.view_init(50, 45)

    # render the basin that contains the fluid
    plotBasin(cx, cy, sub)

    # save
    zeros_left = (4 - len(str(iter))) * '0'
    # fig.tight_layout()
    plt.savefig('session/iter_' + zeros_left + str(iter) + '.png')
    plt.close()
    #
    # }


def dataFromDat():
    """pulls solution data from a dat file
    """
    zeros_left = (4 - len(str(iter))) * '0'
    file_name = 'solution' + zeros_left + str(iter) + '.dat'

    fr = open('./data_files/' + file_name, 'r')
    Nx = int(fr.readline().split(":")[1])
    Ny = int(fr.readline().split(":")[1])
    # Ng = int(fr.readline().split(":")[1])
    time = float(fr.readline().split(":")[1])
    fr.close()

    # hu and hv are not written in the dat file, to reduce the overhead
    # x, y, h, hu, hv = np.loadtxt('./data_files/' + file_name, skiprows = 4,
    #                              unpack = True)
    x, y, h = np.loadtxt('./data_files/' + file_name, skiprows = 4, unpack = True)
    # unpack the row-major vectors into matrices
    X = x.reshape(Ny, Nx)
    Y = y.reshape(Ny, Nx)
    Z = h.reshape(Ny, Nx)
    return X, Y, Z, Nx, Ny


def update_plot(frame_number, X, Y, Z, plot, fig, sub, time_array):
    """
    plots a single frame
    -------------------------------------------------------------------  
    used from FuncAnimation to iteratively create a timelapse animation  

    @param frame_number    : current frame  
    @param X, Y, Z         : meshgrid and values  
    @param plot            : list holding current plot  
    @param fig             : activated plt.figure  
    @param sub             : Axes3D subplot object  
    @time_array            : holds the iter-wise times
    """
    if conf.PLOTTING_STYLE == 'water':
        plot[0].remove()
        # rotate the domain every 3 frames
        horizontal_rotate = 45 + frame_number / 8
        sub.view_init(55, horizontal_rotate)
        plot[0] = sub.plot_surface(X, Y, Z[frame_number], rstride=1, cstride=1,
                                   linewidth=0, color=(0.251, 0.643, 0.875, 0.95),
                                   shade=True, antialiased=False)
    elif conf.PLOTTING_STYLE == 'contour':
        # Bliting with contour is not supported (because the corresponding
        # attributes are not artists), so the subplot has to be re-built. That's
        # why fig is passed.
        sub.clear()
        sub.view_init(50, 45)
        plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        fig.gca().set_zlim([-0.5, 4])
        plt.title('time: {0:.3f}'.format(time_array[frame_number]))
        sub.title.set_position([0.51, 0.8])
        plt.axis('off')
        plot[0] = sub.contour3D(X, Y, Z[frame_number], 120, cmap='ocean',
                                vmin=0.5, vmax=1.5)
    elif conf.PLOTTING_STYLE == 'wireframe':
        plot[0].remove()
        # rotate the domain every 3 frames
        horizontal_rotate = 45 + frame_number / 8
        sub.view_init(55, horizontal_rotate)
        plot[0] = sub.plot_wireframe(X, Y, Z[frame_number], rstride=2, cstride=2,
                                     linewidth=1)

    # frame title
    plt.title('time: {0:.3f}'.format(time_array[frame_number]))
    sub.title.set_position([0.51, 0.83])


def createAnimation(U_stepwise_for_animation, cx, cy, time_array):
    """
    generates and saves a timelapse of the simulation
    -------------------------------------------------
    @param U_stepwise_for_animation    : list of iter-wise solutions  
    @param cx                          : x axis cell centers  
    @param cy                          : y axis cell centers  
    @time_array                        : holds the iter-wise times
    """
    # frames per sec
    fps = 60
    # dots per inch
    dpi = 50
    # figure size in inches
    # golden ratio: 1.618
    figsize = (12.944, 8)

    # resolution = figsize * dpi
    # --------------------------
    # example:
    # figsize = (9.6, 5.4), dpi=200
    # resolution: 1920x1080 (1920/200=9.6)

    # total frames
    frames = len(U_stepwise_for_animation)

    # X, Y, Z
    X,Y = np.meshgrid(cx[conf.Ng: -conf.Ng], cy[conf.Ng: -conf.Ng])
    Z = U_stepwise_for_animation

    # plot configuration
    fig = plt.figure(figsize=figsize, dpi=dpi)
    sub = fig.add_subplot(111, projection="3d")
    sub.view_init(55, 45)
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
    fig.gca().set_zlim([-0.5, 4])
    plt.axis('off')
    sub.title.set_position([0.51, 0.83])
    plt.rcParams.update({'font.size': 20})

    # initialization plot {
    if conf.PLOTTING_STYLE == 'water':
        plot = [sub.plot_surface(X, Y, Z[0], rstride=1, cstride=1, linewidth=0,
            color=(0.251, 0.643, 0.875, 0.9), shade=True, antialiased=False)]
    elif conf.PLOTTING_STYLE == 'contour':
        plot = [sub.contour3D(X, Y, Z[0], 150, cmap='ocean', vmin=0.5, vmax=1.5)]
    elif conf.PLOTTING_STYLE == 'wireframe':
        plot = [sub.plot_wireframe(X, Y, Z[0], rstride=2, cstride=2,
                                   linewidth=1)]
    else:
        logger.log("Configure PLOTTING_STYLE | options: 'water', 'contour',",
                   "'wireframe'")
    plt.title('time: {0:.3f}'.format(time_array[0]))
    # }

    # render the basin that contains the fluid
    plotBasin(cx, cy, sub)

    # generate the animation
    ani = animation.FuncAnimation(fig, update_plot, frames,
        fargs=(X, Y, Z, plot, fig, sub, time_array),
        interval=1000 / fps, repeat=True)

    # save the animation
    saveAni(ani, fps, dpi)

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


def plotBasin(cx, cy, sub):
    """
    plots the basin that contains the fluid
    ---------------------------------------
    @param cx        : x axis cell centers  
    @param cy        : y axis cell centers  
    @param sub       : Axes3D subplot object  
    """
    if conf.SHOW_BASIN is True:
        # make basin a bit wider, because water appears to be out of the basin
        # because of the perspective mode
        X_bas,Y_bas = np.meshgrid(cx[conf.Ng - 1: conf.Nx + 2],
                                  cy[conf.Ng - 1: conf.Ny + 2])
        # BASIN
        BASIN = np.zeros((conf.Ny + 2 * conf.Ng, conf.Nx + 2 * conf.Ng))
        # left-right walls
        BASIN[:, 0] = 2.5
        BASIN[:, conf.Nx + 2 * conf.Ng - 1] = 2.5
        # top-bottom walls
        BASIN[0, :] = 2.5
        BASIN[conf.Ny + 2 * conf.Ng - 1, :] = 2.5
        sub.plot_surface(X_bas, Y_bas, BASIN, rstride=2, cstride=2, linewidth=0,
                         color=(0.4, 0.4, 0.5, 0.1))
    elif conf.SHOW_BASIN is False:
        pass
    else:
        logger.log("Configure SHOW_BASIN. Options: True, False")


def saveAni(ani, fps, dpi):
    """
    saves the animation
    -------------------
    @param ani             : animation.FuncAnimation() object  
    @param fps             : frames per second  
    @param dpi             : dots per inch
    """
    if conf.SAVE_ANIMATION is True:
        # file name
        date_n_time = str(datetime.now())[:19]
        date_n_time = date_n_time[:10] + '_' + date_n_time[11:-3]
        file_name = conf.MODE + '_animation_' + date_n_time

        # configure the writer
        plt.rcParams['animation.ffmpeg_path'] = conf.PATH_TO_FFMPEG
        FFwriter = animation.FFMpegWriter(fps=fps, bitrate=-1,
            extra_args=['-r', str(fps), '-pix_fmt', 'yuv420p', '-vcodec',
                        'libx264', '-qscale:v', '1'])

        # save
        try:
            ani.save(file_name + '.' + conf.VID_FORMAT,
                    writer=FFwriter, dpi=dpi)

            logger.log('Animation saved as: ' + file_name + '.'
                    + conf.VID_FORMAT + ' | fps: ' + str(fps))

            # convert to a lighter gif
            cmd = 'ffmpeg -i ' + file_name + '.' + conf.VID_FORMAT + ' -vf ' \
                '"fps=' + str(fps) + ',scale=240:-1:flags=lanczos,split[s0][s1];' \
                '[s0]palettegen[p];[s1][p]paletteuse"' \
                ' -hide_banner -loglevel panic -loop 0 ' + file_name + '.gif'
            os.system(cmd)
            logger.log('Animation saved as: ' + file_name + '.gif'
                    + ' | fps: ' + str(fps))
        except FileNotFoundError:
            logger.log('Configure PATH_TO_FFMPEG')
    elif conf.SAVE_ANIMATION is False:
        pass
    else:
        logger.log("Configure SAVE_ANIMATION | Options: True, False")
