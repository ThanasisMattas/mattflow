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
from random import randint, uniform

import numpy as np
from numpy.lib.format import open_memmap

from mattflow import config as conf, dat_writer, logger, utils


def _variance():
    """use small variance to make the distribution steep and sharp, for a
    better representation of a drop"""
    # > 0.0004
    variance = {
        "single drop": randint(5, 8) / 10000,
        "drops": randint(5, 8) / 10000,
        "rain": 0.0002
    }
    return variance[conf.MODE]


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


def _drop_heights_correction(drop_heights):
    """subtracts the fluid volume that the drop adds to the domain

    For a few thousands of iterations the fluid level rises quite subtly, but
    after a point the volume adds up to be significant.

    Args:
        drop_heights (2D array) :  the gaussian distribution modeling the drop

    Returns:
        drop_correction (2D array) :  the extra fluid volume of the drop,
                                      distributed to the whole domain, divided
                                      by a divisor for a smoother transition
                                      to the next time_step
    """
    divisor = 2
    drop_correction = np.empty_like(drop_heights)
    drop_heights_sum = drop_heights.sum()
    drop_correction.fill(drop_heights_sum / drop_heights.size / divisor)
    return drop_correction


def drop(h_hist, drops_count=None):
    """Generates a drop

    Drop is modeled as a gaussian distribution

    Args:
        h_hist (array)   :  the 0th state variable, U[0, :, :]
        drops_count(int) :  drop counter

    Returns:
        h_hist(2D array) :  drop is added to the input h_hist
    """
    # multiply with 3 / 2 for a small stone droping
    #          with 1 / 5 for a water drop with a considerable momentum build
    #          with 1 / 8 for a soft water drop
    if conf.MODE == 'single drop' or conf.MODE == 'drops':
        factor = randint(6, 12) / 10
    elif conf.MODE == 'rain':
        factor = 1 / 6
    else:
        print("Configure MODE | options: 'single drop', 'drops', 'rain'")
    variance = _variance()
    drop_heights = factor * _gaussian(variance, drops_count)
    drop_correction = _drop_heights_correction(drop_heights)
    h_hist += drop_heights - drop_correction
    return h_hist


def _init_U():
    """creates and initializes the state-variables 3D matrix, U"""
    cx = conf.CX
    cy = conf.CY
    U = np.zeros((utils.U_shape()))
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


def _init_h_hist(U):
    """creates and initializes h_hist

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
    h_hist = np.zeros((num_states_to_save, conf.Nx, conf.Ny))
    h_hist[0] = U[0, conf.Ng: -conf.Ng, conf.Ng: -conf.Ng]
    return h_hist


def _init_U_ds(U):
    dss = utils.ds_shape()
    ds_name = f"mattflow_data_{dss[0]}x{dss[1]}x{dss[2]}x{dss[3]}.npy"
    U_ds = open_memmap(os.path.join(os.getcwd(), ds_name),
                       mode='w+',
                       dtype=np.dtype('float64'),
                       shape=dss)
    U_ds[0] = U[:, conf.Ng: - conf.Ng, conf.Ng: - conf.Ng]
    return U_ds


def initialize():
    """wraper that initializes and returns all necessary data_structures

    Returns
        U (3D array)   :  the state-variables-3D-matrix (populating a x,y grid)
                          - shape: (3, Nx + 2 * Ng, Ny + 2 * Ng)
                          - U[0] : state varables [h, hu, hv]
                          - U[1] : y dimention (rows)
                          - U[2] : x dimention (columns)
        h_hist (array) :  holds the step-wise height solutions for the
                                 post-processing animation
        t_hist (array) :  holds the step-wise times for the post-
                          processing animation
        U_ds (memmap)  :  holds the state-variables 3D matrix data for all
                          the timesteps
                          (conf.MAX_ITERS, 3, Nx + 2 * Ng, Ny + 2 * Ng)
    """
    logger.log('Initialization...')

    U = _init_U()
    h_hist = _init_h_hist(U)
    t_hist = t_hist = np.zeros(len(h_hist))
    if conf.SAVE_DS_FOR_ML:
        U_ds = _init_U_ds(U)
    else:
        U_ds = None
    return U, h_hist, t_hist, U_ds
