# dat_writer.py is part of MattFlow
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
"""Saves the step-wise solution at a .dat file"""

from mattflow import config as conf, utils


def write_dat(h_hist, time, it):
    """writes solution data to a dat file

    Args:
        h_hist (array)  :  the 0th state variable, U[0, :, :]
        time (float)    :  current time
        it (int)        :  current iteration
    """
    utils.create_child_dir("data_files")
    try:
        zeros_left = (4 - len(str(it))) * '0'
        file_name = './data_files/solution' + zeros_left + str(it) + '.dat'
        fw = open(file_name, 'w')
        fw.write('xCells: ' + str(conf.Nx) + '\n'
                 + 'yCells: ' + str(conf.Ny) + '\n'
                 + 'ghostCells: ' + str(conf.Ng) + '\n'
                 + 'time: ' + "{0:.3f}".format(time) + '\n')

        for j in range(len(h_hist)):
            for i in range(len(h_hist[0])):
                # if-else used for comumn-wise alignment
                fw.write(
                    ("{0:.15f}".format(conf.CX[i + conf.Ng])
                     if conf.CX[i + conf.Ng] < 0
                     else ' ' + "{0:.15f}".format(conf.CX[i + conf.Ng])) + ' '

                    + ("{0:.15f}".format(conf.CY[j + conf.Ng])
                       if conf.CY[j + conf.Ng] < 0
                       else ' ' + "{0:.15f}".format(conf.CY[j + conf.Ng])) + ' '

                    + ("{0:.15f}".format(h_hist[j, i])
                       if h_hist[j, i] < 0
                       else ' ' + "{0:.15f}".format(h_hist[j, i])) + ' '
                    # In case the whole U (3D array) is passed and you need
                    # to write all 3 state variables, use the following:
                    # + ("{0:.15f}".format(U[0, j, i]) if U[0, j, i] < 0 \
                    #     else ' ' + "{0:.15f}".format(U[0, j, i])) + ' '
                    # + ("{0:.15f}".format(U[1, j, i]) if U[1, j, i] < 0 \
                    #     else ' ' + "{0:.15f}".format(U[1, j, i])) + ' '
                    # + ("{0:.15f}".format(U[2, j, i]) if U[2, j, i] < 0 \
                    #     else ' ' + "{0:.15f}".format(U[2, j, i]))
                    + '\n'
                )
    except OSError:
        print("Unable to create data file")
