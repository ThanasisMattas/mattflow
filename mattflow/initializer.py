'''
=============================================================================
@file   initializer.py
@author Thanasis Mattas

Handles the initialization of the simulation.

MattFlow is free software; you may redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version. You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
=============================================================================
'''


from mattflow import config as conf
from mattflow import dat_writer
import numpy as np
import random


#                  x
#          0 1 2 3 4 5 6 7 8 9
#        0 G G G G G G G G G G
#        1 G G G G G G G G G G
#        2 G G - - - - - - G G
#        3 G G - - - - - - G G
#      y 4 G G - - - - - - G G
#        5 G G - - - - - - G G
#        6 G G - - - - - - G G
#        7 G G - - - - - - G G
#        8 G G G G G G G G G G
#        9 G G G G G G G G G G


def initialize(cx, cy):
    """
    creates and initializes a state-variables-3D-matrix, U
    ------------------------------------------------------
    1st dimention is the state varables [h, hu, hv], populating the x,y grid
    2nd and 3rd dimentions consist the x,y grid
    @param cx    : centers of the cells along the x axis  
    @param cy    : centers of the cells along the y axis  
    returns U    : state-variables-3D-matrix
    """

    U = np.zeros(((3, conf.Ny + 2 * conf.Ng, conf.Nx + 2 * conf.Ng)))

    # 1st drop
    U[0, :, :] = conf.SURFACE_LEVEL + drop(U[0, :, :], cx, cy)

    # write dat | default: 'OF'
    if conf.DAT_WRITING_MODE == 'OF':
        pass
    elif conf.DAT_WRITING_MODE == 'ON':
        dat_writer.writeDat(U[0, conf.Ng: -conf.Ng, conf.Ng: -conf.Ng], cx, cy,
                            time=0, iter=0)
        from mattflow import mattFlow_post
        mattFlow_post.plotFromDat(time=0, iter=0)
    else:
        print("Configure DAT_WRITING_MODE | Options: 'ON', 'OF'")
    return U


def drop(hights_list, cx, cy):
    """
    Generates a drop
    ----------------
    Drop is modeled as a gaussian distribution

    @param hights_list    : the 0th state variable, U[0, :, :]  
    @param cx             : centers of the cells along the x axis  
    @param cy             : centers of the cells along the y axis  
    returns hights_list   : drop is added to the input hights_list
    """
    # grid of the cell centers
    CX, CY = np.meshgrid(cx, cy)

    # random pick of drop center dimentions (mean or expectation of the gaussian
    # distribution)
    DROP_CENTER_X = random.uniform(conf.MIN_X, conf.MAX_X)
    DROP_CENTER_Y = random.uniform(conf.MIN_Y, conf.MAX_Y)

    # squared distance of each cell from the mean value of the distribution
    radiousSquared = (CX - DROP_CENTER_X)**2 + (CY - DROP_CENTER_Y)**2

    # gaussian distribution formula
    # multiply with 3 / 2 for a small stone droping
    #          with 2 / 3 for a water drop with a considerable momentum build
    #          with 1 / 4 for a soft water drop
    if conf.MODE == 'single drop' or conf.MODE == 'drops':
        variance = 0.03**2
        hights_list += 3 / 2 / np.sqrt(2 * np.pi * variance) \
                       * np.exp(- radiousSquared / 2 / variance)
    elif conf.MODE == 'rain':
        variance = 0.01**2
        hights_list += 1 / 4 / np.sqrt(2 * np.pi * variance) \
                       * np.exp(- radiousSquared / 2 / variance)
    else:
        print("Configure MODE | options: 'single drop', 'drops', 'rain'")
    return hights_list