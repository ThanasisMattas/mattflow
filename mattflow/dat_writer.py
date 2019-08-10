'''
=============================================================================
@file   dat_writer.py  
@author Thanasis Mattas

Saves the step-wise solution at a .dat file.

MattFlow is free software; you may redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version. You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
=============================================================================
'''


from mattflow import config as conf
# from datetime import datetime
import os


# file_name = str(datetime.now())[:19]
# file_name = file_name[:10] + '_' + file_name[11:] + '.dat'

def writeDat(hights_list, cx, cy, time, iter):
    """
    writes solution data to a dat file
    -----------------------------------
    @param hights_list  : the 0th state variable, U[0, :, :]  
    @param cx           : cell center along the x axis  
    @param cy           : cell center along the y axis  
    @param time         : current time  
    @param imter        : current iter
    """
    try:
        if os.path.isdir('./data_files'):
            pass
        else:
            os.mkdir('./data_files')
    except OSError:
        print("Unable to create data_files directory")
    try:
        zeros_left = (4 - len(str(iter))) * '0'
        file_name = './data_files/solution' + zeros_left + str(iter) + '.dat'
        fw = open(file_name, 'w')
        fw.write('xCells: ' + str(conf.Nx) + '\n'
                 + 'yCells: ' + str(conf.Ny) + '\n'
                 + 'ghostCells: ' + str(conf.Ng) + '\n'
                 + 'time: ' + "{0:.3f}".format(time) + '\n')
        for j in range(len(hights_list)):
            for i in range(len(hights_list[0])):
                # if-else used for comumn-wise alignment
                fw.write(  ("{0:.15f}".format(cx[i + conf.Ng]) \
                            if cx[i + conf.Ng] < 0 \
                            else ' ' + "{0:.15f}".format(cx[i + conf.Ng])) + ' '

                         + ("{0:.15f}".format(cy[j + conf.Ng]) \
                            if cy[j + conf.Ng] < 0 \
                            else ' ' + "{0:.15f}".format(cy[j + conf.Ng])) + ' '

                         + ("{0:.15f}".format(hights_list[j, i]) \
                            if hights_list[j, i] < 0 \
                            else ' ' + "{0:.15f}".format(hights_list[j, i])) + ' '
                         # In case the whole U (3D array) is passed and you need
                         # to write all 3 state variables, use the following:
                         # + ("{0:.15f}".format(U[0, j, i]) if U[0, j, i] < 0 \
                         #     else ' ' + "{0:.15f}".format(U[0, j, i])) + ' '
                         # + ("{0:.15f}".format(U[1, j, i]) if U[1, j, i] < 0 \
                         #     else ' ' + "{0:.15f}".format(U[1, j, i])) + ' '
                         # + ("{0:.15f}".format(U[2, j, i]) if U[2, j, i] < 0 \
                         #     else ' ' + "{0:.15f}".format(U[2, j, i]))
                         + '\n')
    except OSError:
        print("Unable to create data file")
