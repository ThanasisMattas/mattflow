'''
=============================================================================
@file   utilities.py  
@author Thanasis Mattas

Provides some useful-generic functions.

MattFlow is free software; you may redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version. You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
=============================================================================
'''


import os
import math


def delete_logs_dats_images():
    """
    deletes previous log, dat and png files (for debugging)
    """
    files_list = [f for f in os.listdir('.')]
    for f in files_list:
        if f.endswith(".dat") or f.endswith(".log") or f.endswith(".png"):
            os.remove(os.path.join('.', f))

    if os.path.isdir('./data_files'):
        files_list = [f for f in os.listdir('./data_files')]
        for f in files_list:
            if f.endswith(".dat") or f.endswith(".log") or f.endswith(".png"):
                os.remove(os.path.join('./data_files/', f))

    if os.path.isdir('./session'):
        files_list = [f for f in os.listdir('./session')]
        for f in files_list:
            if f.endswith(".dat") or f.endswith(".log") or f.endswith(".png"):
                os.remove(os.path.join('./session/', f))


def secs_to_time(secs):
    """
    converts seconds to hh:mm:ss  
    ----------------------------  
    @param secs        : number of seconds  
    returns time_str   : (string)
    """
    hours = math.floor(secs / 3600)
    mins = math.floor((secs % 3600) / 60)
    secs = math.floor(secs - 3600 * hours - 60 * mins)
    h_zeros = (2 - len(str(hours))) * '0'
    m_zeros = (2 - len(str(mins))) * '0'
    s_zeros = (2 - len(str(secs))) * '0'
    time_str = h_zeros + str(hours) + ':' \
             + m_zeros + str(mins) + ':' \
             + s_zeros + str(secs)
    return time_str
