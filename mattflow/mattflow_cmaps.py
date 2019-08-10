'''
=============================================================================
@file   mattflow_cmaps.py  
@author Thanasis Mattas

Creates some color maps (currently unused).

MattFlow is free software; you may redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version. You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
=============================================================================
'''


import numpy as np
from matplotlib.colors import ListedColormap, LinearSegmentedColormap


# TODO add LightSource-shade
# unfortunately, when using cmpa instead of a single coloer, shade is disabled


def deepWater_cmap():
    """
    Creates a deep water color-map out of shades of blue, adding transparency to
    colors that lie at greater hights (water drops)
    """
    # deep water color-map (darker)
    water_colors = np.zeros((256, 4))
    water_colors[:, 0] = np.append(np.zeros(255), [12], 0) / 255     # r
    water_colors[:, 1] = np.linspace(71, 164, 256) / 255             # g
    water_colors[:, 2] = np.linspace(114, 255, 256) / 255            # b
    # make last 120 (lighter) transparent (a water drop is transparent)
    water_colors[:, 3] = np.append(np.ones(136),
                        np.ones(120) * np.linspace(0.9, 0.3, 120))  # a
    # make last 100 (ligher) colors an interpolation between indexis 156 to 176
    water_colors[156:, 1] \
        = np.linspace(water_colors[156, 1], water_colors[176, 1], 100)
    mattDeepWater = ListedColormap(water_colors)
    '''
    water_colors = np.array([[ 0,  71, 114, 255],
                             ...
                             [12 ,164, 255, 255]]) / 255
    '''
    return mattDeepWater


def shallowWater_cmap():
    """
    Creates a shallow water color-map out of shades of blue, adding transparency
    to colors that lie at greater hights (water drops)
    """
    # shallow water color-map (lighter)
    water_colors = np.zeros((256, 4))
    water_colors[:, 0] = np.append(np.zeros(255), [12], 0) / 255     # r
    water_colors[:, 1] = np.linspace(103, 164, 256) / 255            # g
    water_colors[:, 2] = np.linspace(165, 255, 256) / 255            # b
    # make last 120 (lighter) transparent (a water drop is transparent)
    water_colors[:, 3] = np.append(np.ones(136),
                        np.ones(120) * np.linspace(0.9, 0.3, 120))  # a
    mattShallowWater = ListedColormap(water_colors)
    '''
    water_colors = np.array([[ 0, 119, 190, 255],
                             ...
                             [12, 164, 255, 255]]) / 255
    '''
    return mattShallowWater
