# mattflow_test.py is part of MattFlow
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
"""Houses all the tests"""

from unittest import mock

import numpy as np
from numpy.testing import assert_array_almost_equal
import pytest

from mattflow import config as conf, initializer

np.set_printoptions(suppress=True, formatter={"float": "{: 0.6f}".format})


@pytest.mark.parametrize("mode, factor",
                         [("drop", 1.), ("rain", 1 / 6)])
@mock.patch("mattflow.initializer._variance", return_value=0.1)
@mock.patch("mattflow.initializer.uniform", return_value=0)
@mock.patch("mattflow.initializer.randint", return_value=10)
class TestInitializer:
  """initializer.py tests"""

  def setup_method(self):
    conf.Nx = conf.Ny = 9
    conf.Ng = 1
    self.N = conf.Nx + 2 * conf.Ng
    self.old_mode = conf.MODE
    self.old_nx = conf.Nx
    self.old_ny = conf.Ny
    self.old_ng = conf.Ng
    self.h_history = np.ones((self.N, self.N))

    conf.CX = np.linspace(-1, 1, self.N)
    conf.CY = np.linspace(-1, 1, self.N)

    conf.MAX_ITERS = 500
    conf.FRAME_SAVE_FREQ = 3
    conf.FRAMES_PER_PERIOD = 1

    # 11 x 11, variance = 0.1, center = (0, 0), {: 0.8f}
    self.gaussian = np.array(
      [[0.00005728, 0.00034649, 0.00140510, 0.00381946, 0.00695951, 0.00850037,
        0.00695951, 0.00381946, 0.00140510, 0.00034649, 0.00005728],
       [0.00034649, 0.00209616, 0.00850037, 0.02310639, 0.04210259, 0.05142422,
        0.04210259, 0.02310639, 0.00850037, 0.00209616, 0.00034649],
       [0.00140510, 0.00850037, 0.03447069, 0.09370104, 0.17073443, 0.20853550,
        0.17073443, 0.09370104, 0.03447069, 0.00850037, 0.00140510],
       [0.00381946, 0.02310639, 0.09370104, 0.25470584, 0.46410429, 0.56685826,
        0.46410429, 0.25470584, 0.09370104, 0.02310639, 0.00381946],
       [0.00695951, 0.04210259, 0.17073443, 0.46410429, 0.84565315, 1.03288309,
        0.84565315, 0.46410429, 0.17073443, 0.04210259, 0.00695951],
       [0.00850037, 0.05142422, 0.20853550, 0.56685826, 1.03288309, 1.26156626,
        1.03288309, 0.56685826, 0.20853550, 0.05142422, 0.00850037],
       [0.00695951, 0.04210259, 0.17073443, 0.46410429, 0.84565315, 1.03288309,
        0.84565315, 0.46410429, 0.17073443, 0.04210259, 0.00695951],
       [0.00381946, 0.02310639, 0.09370104, 0.25470584, 0.46410429, 0.56685826,
        0.46410429, 0.25470584, 0.09370104, 0.02310639, 0.00381946],
       [0.00140510, 0.00850037, 0.03447069, 0.09370104, 0.17073443, 0.20853550,
        0.17073443, 0.09370104, 0.03447069, 0.00850037, 0.00140510],
       [0.00034649, 0.00209616, 0.00850037, 0.02310639, 0.04210259, 0.05142422,
        0.04210259, 0.02310639, 0.00850037, 0.00209616, 0.00034649],
       [0.00005728, 0.00034649, 0.00140510, 0.00381946, 0.00695951, 0.00850037,
        0.00695951, 0.00381946, 0.00140510, 0.00034649, 0.00005728]])

  def tear_down_method(self):
    conf.MODE = self.old_mode
    conf.Nx = self.old_nx
    conf.Ny = self.old_ny
    conf.Ng = self.old_ng
    del self.h_history
    del self.cx
    del self.cy
    del self.gaussian

  def test_drop(self,
                mock_randint, mock_uniform, mock_variance,
                mode, factor):
    conf.MODE = mode

    drop_heights_expected = factor * self.gaussian
    drop_correction_expected = \
        drop_heights_expected.sum() / drop_heights_expected.size / 2
    drop_expected = \
        self.h_history + drop_heights_expected - drop_correction_expected
    drop_ = initializer.drop(self.h_history)
    assert_array_almost_equal(drop_, drop_expected, decimal=6)

  def test_initialize(self,
                      mock_randint, mock_uniform, mock_variance,
                      mode, factor):
    conf.MODE = mode

    # U
    drop_heights_expected = factor * self.gaussian
    drop_correction_expected = \
        drop_heights_expected.sum() / drop_heights_expected.size / 2
    U_expected = np.zeros((3, self.N, self.N), dtype=conf.DTYPE)
    U_expected[0, :, :] = \
        conf.SURFACE_LEVEL + drop_heights_expected - drop_correction_expected

    # h_hist
    num_states = 167
    h_hist_expected = np.zeros((num_states, conf.Nx, conf.Ny),
                               dtype=conf.DTYPE)
    h_hist_expected[0] = U_expected[0, conf.Ng: - conf.Ng, conf.Ng: -conf.Ng]

    # t_hist
    t_hist_expected = np.zeros(len(h_hist_expected), dtype=conf.DTYPE)

    U, h_hist, t_hist, _ = initializer.initialize()
    assert_array_almost_equal(U, U_expected, decimal=6)
    assert_array_almost_equal(h_hist, h_hist_expected, decimal=6)
    assert_array_almost_equal(t_hist, t_hist_expected, decimal=6)
