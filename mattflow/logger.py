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
from datetime import datetime
import os


file_name = str(datetime.now())[:19]
file_name = file_name[:10] + '_' + file_name[11:] + '.log'
welcome_msg = 'Welcome to MattFlow!'
author_msg = 'Author: Thanasis Mattas, 2019'
license_msg = 'GNU General Public License | Version 3'


def log(state):
    """
    appends a state-message at a new line of the log file
    -----------------------------------------------------
    If a log file does not exist, it creates one, printing the simulation info.  
    @param state    : the string to be logged
    """
    # Check if a log file is already created (update the 1st encountered)
    here = os.path.abspath(os.path.dirname(__file__))
    files_list = [f for f in os.listdir(here) if f.endswith(".log")]
    if files_list:
        # Append the state
        with open(files_list[0], 'a') as fa:
            fa.write(state + '\n')
        # Rename log to current time
        os.rename(files_list[0], file_name)

    # If a log file isn't created yet
    else:
        fw = open(file_name, 'w')
        fw.write(welcome_msg + '\n' + author_msg + '\n' + license_msg + '\n'
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
