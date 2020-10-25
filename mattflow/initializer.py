# initializer.py is part of MattFlow
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
"""Handles the initialization of the simulation"""

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


import os
from random import uniform

import numpy as np

from mattflow import config as conf, dat_writer, logger


def _variance(mode):
    """use small variance to make the distribution steep and sharp, for a
    better representation of a drop"""
    variance = {
        "single drop": 0.0009,
        "drops": 0.0009,
        "rain": 0.0001
    }
    return variance[mode]


def _gaussian(variance, drops_count):
    '''produces a bivariate gaussian distribution of a certain variance

    formula: amplitude * np.exp(-exponent)

    Args:
        variance (float) :  target variance of the distribution
        drops_count(int) :  drop counter

    Returs:
        gaussian_distribution (2D array)
    '''
    # random pick of drop center coordinates
    # (mean or expectation of the gaussian distribution)
    if conf.RANDOM_DROP_CENTERS:
        drop_cx = uniform(conf.MIN_X, conf.MAX_X)
        drop_cy = uniform(conf.MIN_Y, conf.MAX_Y)
    else:
        drop_cx = conf.DROPS_CX[drops_count % 10]
        drop_cy = conf.DROPS_CY[drops_count % 10]

    # grid of the cell centers
    CX, CY = np.meshgrid(conf.CX, conf.CY)

    amplitude = 1 / np.sqrt(2 * np.pi * variance)
    exponent = \
        ((CX - drop_cx)**2 + (CY - drop_cy)**2) / (2 * variance)

    gaussian_distribution = amplitude * np.exp(-exponent)
    return gaussian_distribution


def drop(heights_list, drops_count=None):
    """Generates a drop

    Drop is modeled as a gaussian distribution

    Args:
        heights_list (array)   :  the 0th state variable, U[0, :, :]
        drops_count(int)       :  drop counter

    Returns:
        heights_list(2D array) : drop is added to the input heights_list
    """
    # multiply with 3 / 2 for a small stone droping
    #          with 1 / 5 for a water drop with a considerable momentum build
    #          with 1 / 8 for a soft water drop
    if conf.MODE == 'single drop' or conf.MODE == 'drops':
        variance = _variance("single drop")
        heights_list += 3 / 2 * _gaussian(variance, drops_count)
    elif conf.MODE == 'rain':
        variance = _variance("rain")
        heights_list += 1 / 8 * _gaussian(variance, drops_count)
    else:
        print("Configure MODE | options: 'single drop', 'drops', 'rain'")
    return heights_list


def _init_U():
    """creates and initializes the state-variables 3D matrix, U"""
    cx = conf.CX
    cy = conf.CY
    U = np.zeros(((3,
                   conf.Ny + 2 * conf.Ng,
                   conf.Nx + 2 * conf.Ng)))
    # 1st drop
    U[0, :, :] = conf.SURFACE_LEVEL + drop(U[0, :, :], drops_count=1)
    # write dat | default: False
    if conf.WRITE_DAT:
        dat_writer.writeDat(U[0, conf.Ng: -conf.Ng, conf.Ng: -conf.Ng],
                            time=0, it=0)
        from mattflow import mattflow_post
        mattflow_post.plotFromDat(time=0, it=0)
    elif not conf.WRITE_DAT:
        pass
    else:
        print("Configure WRITE_DAT | Options: True, False")
    return U


def _init_heights_array(U):
    """creates and initializes heights_array

    - holds the states of the fluid for post-processing
    -saving <CONSECUTIVE_FRAMES> frames every <FRAME_SAVE_FREQ> iters
    """
    # number of integer divisions with the freq, times the consecutive frames,
    # plus the consecutive frames that we can take from the remainder of the
    # division
    num_states_to_save = (
        conf.MAX_ITERS
        // conf.FRAME_SAVE_FREQ
        * conf.CONSECUTIVE_FRAMES
        + min(conf.MAX_ITERS % conf.FRAME_SAVE_FREQ, conf.CONSECUTIVE_FRAMES)
    )
    heights_array = np.zeros((num_states_to_save, conf.Nx, conf.Ny))
    heights_array[0] = U[0, conf.Ng: -conf.Ng, conf.Ng: -conf.Ng]
    return heights_array


def _init_U_dataset(U):
    dataset_name = "mattflow_data_{0}x{1}x{2}x{3}".format(
        conf.MAX_ITERS, 3, conf.Nx + 2 * conf.Ng, conf.Ny + 2 * conf.Ng)
    memmap_file = os.path.join(os.getcwd(), dataset_name)
    U_dataset = np.memmap(memmap_file, dtype=np.dtype('float64'),
                          shape=(conf.MAX_ITERS,
                                 3,
                                 conf.Nx + 2 * conf.Ng,
                                 conf.Ny + 2 * conf.Ng),
                          mode="w+")
    U_dataset[0] = U
    return U_dataset


def initialize():
    """wraper that initializes and returns all necessary data_structures

    Returns
        U (3D array)          :  the state-variables-3D-matrix (populating a
                                 x,y grid)
                                 - shape: (3, Nx + 2 * Ng, Ny + 2 * Ng)
                                 - U[0] : state varables [h, hu, hv]
                                 - U[1] : y dimention (rows)
                                 - U[2] : x dimention (columns)
        heights_array (array) :  holds the step-wise height solutions for the
                                 post-processing animation
        time_array (array)    :  holds the step-wise times for the post-
                                 processing animation
        U_dataset (memmap)    :  holds the state-variables 3D matrix data for
                                 all the timesteps
                                 (conf.MAX_ITERS, 3, Nx + 2 * Ng, Ny + 2 * Ng)
    """
    logger.log('Initialization...')

    U = _init_U()
    heights_array = _init_heights_array(U)
    time_array = time_array = np.zeros(len(heights_array))
    if conf.SAVE_DS_FOR_ML:
        U_dataset = _init_U_dataset(U)
    else:
        U_dataset = None
    return U, heights_array, time_array, U_dataset
