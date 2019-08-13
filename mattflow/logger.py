'''
@file   logger.py  
@author Thanasis Mattas

Handles the logging precess.

MattFlow is free software; you may redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version. You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
'''


from mattflow import config as conf
from mattflow import __version__, __author__, __license__
from datetime import datetime
import os


file_name = str(datetime.now())[:19]
# replace : with - for windows file name format
file_name = file_name[:10] + '_' + file_name[11:13] + '-' + file_name[14:16] \
            + '-' + file_name[17:19] + '.log'
version_msg = 'MattFlow v' + __version__
author_msg = 'Author: ' + __author__ + ', 2019'
license_msg = __license__


def log(state):
    """
    appends a state-message at a new line of the log file
    -----------------------------------------------------
    If a log file does not exist, it creates one, printing the simulation info.  
    @param state    : the string to be logged
    """
    # log file object, if there is one
    # False , if ther isn't
    log_file_object = find_log()

    # check if a log file is already created or if the log file is from previous
    # simulation
    if log_file_object:
        # append the state
        with open(log_file_object, 'a') as fa:
            fa.write(state + '\n')
        # rename log to current time
        os.rename(log_file_object, file_name)

    # if a log file isn't created yet
    else:
        fw = open(file_name, 'w')
        fw.write(version_msg + '\n' + author_msg + '\n' + license_msg + '\n'
            + len(license_msg) * '-' + '\n'
            + str(datetime.now())[:19] + '\n\n'
            + 'Configuration of the simulation' + '\n'
            + 31 * '-' + '\n'
            + 'Number of cells        : ' + str(conf.Nx * conf.Ny) + '\n'
            + 'Number of ghost cells  : ' + str(conf.Ng) + '\n'
            + 'Courant number         : ' + str(conf.COURANT) + '\n'
            + 'Simulation mode        : ' + str(conf.MODE) + '\n'
            + 'Boundary conditions    : ' + str(conf.BOUNDARY_CONDITIONS) + '\n'
            + 'Solver type            : ' + str(conf.SOLVER_TYPE) + '\n'
            + 'Plotting style         : ' + str(conf.PLOTTING_STYLE) + '\n\n')

        fw.write(state + '\n')
        fw.close()


def find_log():
    """
    finds an open log file, if any, at the working directory (1st encountered)
    --------------------------------------------------------------------------
    returns the log file object, if there is one or False, if there isn't
    """
    working_dir = os.getcwd()
    files_list = []
    files_list = [f for f in os.listdir(working_dir)
                  if f.endswith(".log") and is_open(f)]
    if files_list:
        return files_list[0]
    else:
        return False


def close():
    """
    closes the log file, appending '_done' to the file name
    """
    log_file_object = find_log()
    if log_file_object:
        # append blank line
        with open(log_file_object, 'a') as fa:
            fa.write('\n')
        # append '_done' at the file name
        os.rename(log_file_object, file_name[:-4] + '_done' + file_name[-4:])
    else:
        fw = open(file_name, 'w')
        fw.write('Trying to close a log file that does not exist...\n\n')
        fw.close()
        log_file_object = find_log()
        os.rename(log_file_object, file_name[:-4] + '_errored' + file_name[-4:])


def is_open(log_file_object):
    """
    checks whether a log file object is open or not
    -----------------------------------------------
    @ param log_file_object  
    returns True if a log file is οpen, False if it is not
    """
    if log_file_object[-9:-4] != '_done':
        return True
    else:
        return False
