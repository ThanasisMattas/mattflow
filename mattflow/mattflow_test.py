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

import time
from unittest import mock

import numpy as np
from numpy.testing import assert_array_almost_equal
import pytest

from mattflow import (bcmanager,
                      config as conf,
                      initializer,
                      mattflow_solver,
                      utils)

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
        0.00695951, 0.00381946, 0.00140510, 0.00034649, 0.00005728]],
      dtype=np.dtype("float32")
    )

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


class TestUtils():
  """utils.py tests"""

  def setup_method(self):
    conf.MAX_ITERS = 550
    self.max_len = 0.1
    conf.MAX_X = self.max_len
    conf.MIN_X = -self.max_len
    conf.MAX_Y = self.max_len
    conf.MIN_Y = -self.max_len
    conf.Nx = conf.Ny = 9
    conf.Ng = 1
    conf.dx = conf.dy = 2 * self.max_len / conf.Nx

  def tear_down_method(self):
    pass

  def test_cell_centers(self):
    cx_expected = cy_expected = np.array(
      [-0.1111111, -0.088889, -0.0666667, -0.0444444,
       -0.0222222, 2.3841858e-07, 0.0222222, 0.04444447,
       0.06666670, 0.08888893, .1111112],
      dtype=np.dtype("float32")
    )

    cx, cy = utils.cell_centers()
    assert_array_almost_equal(cx, cx_expected)
    assert_array_almost_equal(cy, cy_expected)

  def test_time_this(self, capsys):

    @utils.time_this
    def sleep_for(secs: float):
        time.sleep(secs)

    sleep_for(0.1)
    captured = capsys.readouterr()
    expected_out = "Sleep_for duration------------0:00:00.10\n"
    assert captured.out == expected_out

  @pytest.mark.parametrize(
    "drop_iters_mode, drop_iters_expected",
    [("custom", [0, 120, 270, 410, 540, 750]),
     ("random", np.arange(0, 650, 100)),
     ("fixed", np.arange(0, 650, conf.FIXED_ITERS_BETWEEN_DROPS))]
  )
  @mock.patch("mattflow.utils.random.randint", return_value=100)
  def test_drop_iters_list(self, mock_randint, drop_iters_mode, drop_iters_expected):
    conf.ITERS_BETWEEN_DROPS_MODE = drop_iters_mode
    drop_iters = utils.drop_iters_list()
    print(drop_iters)
    assert_array_almost_equal(drop_iters, drop_iters_expected)


class TestBcmanager():
  """bcmanager.py tests"""

  def setup_method(self):
    conf.MAX_ITERS = 550
    self.max_len = 0.1
    conf.MAX_X = self.max_len
    conf.MIN_X = -self.max_len
    conf.MAX_Y = self.max_len
    conf.MIN_Y = -self.max_len
    conf.Nx = conf.Ny = 5
    conf.Ng = 1
    conf.dx = conf.dy = 2 * self.max_len / conf.Nx
    self.U_ = np.array(
      [[[ 2.2657156 ,  2.2657156 ,  2.253398  ,  2.2343802 ,
          2.21266   ,  2.1988487 ,  2.1988487 ],
        [ 2.2657156 ,  2.1992939 ,  2.1868532 ,  2.1697948 ,
          2.1533852 ,  2.144444  ,  2.1988487 ],
        [ 2.2266014 ,  2.1764033 ,  2.1639748 ,  2.1462896 ,
          2.128803  ,  2.1188493 ,  2.1579635 ],
        [ 2.135454  ,  2.121841  ,  2.1105056 ,  2.0922544 ,
          2.0725465 ,  2.059794  ,  2.0652397 ],
        [ 1.9963144 ,  2.03645   ,  2.0284894 ,  2.011012  ,
          1.9889272 ,  1.9717735 ,  1.9287541 ],
        [ 1.8737274 ,  1.9598783 ,  1.9562473 ,  1.9401051 ,
          1.9164627 ,  1.895112  ,  1.8112943 ],
        [ 1.8737274 ,  1.8737274 ,  1.8757049 ,  1.8629198 ,
          1.8371153 ,  1.8112943 ,  1.8112943 ]],

       [[-0.0386809 ,  0.0386809 ,  0.0595752 ,  0.10824296,
          0.11708391,  0.03453719, -0.03453719],
        [-0.0386809 ,  0.04609778,  0.07631601,  0.12097389,
          0.12148945,  0.03538336, -0.03453719],
        [-0.0217734 ,  0.03147381,  0.05890764,  0.10676077,
          0.11549389,  0.04021141, -0.03914568],
        [ 0.00885441,  0.0029346 ,  0.02228841,  0.07638465,
          0.10218683,  0.04805681, -0.04528352],
        [ 0.04344957, -0.03351239, -0.02361635,  0.03831967,
          0.08548081,  0.05802898, -0.05164351],
        [ 0.06724989, -0.06239687, -0.05857066,  0.00910301,
          0.07213843,  0.06605287, -0.05571622],
        [ 0.06724989, -0.06724989, -0.07572492, -0.0140384 ,
          0.05140896,  0.05571622, -0.05571622]],

       [[-0.61991954, -0.61991954, -0.6143542 , -0.60563844,
         -0.5964889 , -0.59121823, -0.59121823],
        [ 0.61991954,  0.5917232 ,  0.5858375 ,  0.5782364 ,
          0.57132876,  0.56843126,  0.59121823],
        [ 1.6210319 ,  1.5722902 ,  1.557693  ,  1.5367452 ,
          1.5204405 ,  1.5126007 ,  1.5478977 ],
        [ 2.1372514 ,  2.137276  ,  2.1166012 ,  2.083918  ,
          2.058113  ,  2.0434089 ,  2.0306606 ],
        [ 1.8609889 ,  1.9370515 ,  1.917395  ,  1.8849705 ,
          1.8578848 ,  1.8398389 ,  1.760214  ],
        [ 0.77923036,  0.8336257 ,  0.8219294 ,  0.8069412 ,
          0.7953553 ,  0.78840643,  0.73449546],
        [-0.77923036, -0.77923036, -0.77177703, -0.75726956,
         -0.7452003 , -0.73449546, -0.73449546]]],
      dtype=np.dtype("float32")
    )

  def tear_down_method(self):
    del self.U_[:]

  def test_update_ghost_cells(self):
    U_expected = np.array(
      [[[ 2.1992939 ,  2.1992939 ,  2.1868532 ,  2.1697948 ,
          2.1533852 ,  2.144444  ,  2.144444  ],
        [ 2.1992939 ,  2.1992939 ,  2.1868532 ,  2.1697948 ,
          2.1533852 ,  2.144444  ,  2.144444  ],
        [ 2.1764033 ,  2.1764033 ,  2.1639748 ,  2.1462896 ,
          2.128803  ,  2.1188493 ,  2.1188493 ],
        [ 2.121841  ,  2.121841  ,  2.1105056 ,  2.0922544 ,
          2.0725465 ,  2.059794  ,  2.059794  ],
        [ 2.03645   ,  2.03645   ,  2.0284894 ,  2.011012  ,
          1.9889272 ,  1.9717735 ,  1.9717735 ],
        [ 1.9598783 ,  1.9598783 ,  1.9562473 ,  1.9401051 ,
          1.9164627 ,  1.895112  ,  1.895112  ],
        [ 1.9598783 ,  1.9598783 ,  1.9562473 ,  1.9401051 ,
          1.9164627 ,  1.895112  ,  1.895112  ]],

       [[-0.04609778,  0.04609778,  0.07631601,  0.12097389,
          0.12148945,  0.03538336, -0.03538336],
        [-0.04609778,  0.04609778,  0.07631601,  0.12097389,
          0.12148945,  0.03538336, -0.03538336],
        [-0.03147381,  0.03147381,  0.05890764,  0.10676077,
          0.11549389,  0.04021141, -0.04021141],
        [-0.0029346 ,  0.0029346 ,  0.02228841,  0.07638465,
          0.10218683,  0.04805681, -0.04805681],
        [ 0.03351239, -0.03351239, -0.02361635,  0.03831967,
          0.08548081,  0.05802898, -0.05802898],
        [ 0.06239687, -0.06239687, -0.05857066,  0.00910301,
          0.07213843,  0.06605287, -0.06605287],
        [ 0.06239687, -0.06239687, -0.05857066,  0.00910301,
          0.07213843,  0.06605287, -0.06605287]],

       [[-0.5917232 , -0.5917232 , -0.5858375 , -0.5782364 ,
         -0.57132876, -0.56843126, -0.56843126],
        [ 0.5917232 ,  0.5917232 ,  0.5858375 ,  0.5782364 ,
          0.57132876,  0.56843126,  0.56843126],
        [ 1.5722902 ,  1.5722902 ,  1.557693  ,  1.5367452 ,
          1.5204405 ,  1.5126007 ,  1.5126007 ],
        [ 2.137276  ,  2.137276  ,  2.1166012 ,  2.083918  ,
          2.058113  ,  2.0434089 ,  2.0434089 ],
        [ 1.9370515 ,  1.9370515 ,  1.917395  ,  1.8849705 ,
          1.8578848 ,  1.8398389 ,  1.8398389 ],
        [ 0.8336257 ,  0.8336257 ,  0.8219294 ,  0.8069412 ,
          0.7953553 ,  0.78840643,  0.78840643],
        [-0.8336257 , -0.8336257 , -0.8219294 , -0.8069412 ,
         -0.7953553 , -0.78840643, -0.78840643]]],
      dtype=np.dtype("float32")
    )
    U_ = bcmanager.update_ghost_cells(self.U_)
    assert_array_almost_equal(U_, U_expected)


class TestMattflowSolver():
  """mattflow_solver.py tests"""

  def setup_method(self):
    conf.MAX_ITERS = 550
    self.max_len = 0.1
    conf.MAX_X = self.max_len
    conf.MIN_X = -self.max_len
    conf.MAX_Y = self.max_len
    conf.MIN_Y = -self.max_len
    conf.Nx = conf.Ny = 5
    conf.Ng = 1
    conf.dx = conf.dy = 2 * self.max_len / conf.Nx
    conf.COURANT = min(0.9, 0.015 / min(conf.dx, conf.dy))
    self.U_ = np.array(
      [[[ 2.2657156 ,  2.2657156 ,  2.253398  ,  2.2343802 ,
          2.21266   ,  2.1988487 ,  2.1988487 ],
        [ 2.2657156 ,  2.1992939 ,  2.1868532 ,  2.1697948 ,
          2.1533852 ,  2.144444  ,  2.1988487 ],
        [ 2.2266014 ,  2.1764033 ,  2.1639748 ,  2.1462896 ,
          2.128803  ,  2.1188493 ,  2.1579635 ],
        [ 2.135454  ,  2.121841  ,  2.1105056 ,  2.0922544 ,
          2.0725465 ,  2.059794  ,  2.0652397 ],
        [ 1.9963144 ,  2.03645   ,  2.0284894 ,  2.011012  ,
          1.9889272 ,  1.9717735 ,  1.9287541 ],
        [ 1.8737274 ,  1.9598783 ,  1.9562473 ,  1.9401051 ,
          1.9164627 ,  1.895112  ,  1.8112943 ],
        [ 1.8737274 ,  1.8737274 ,  1.8757049 ,  1.8629198 ,
          1.8371153 ,  1.8112943 ,  1.8112943 ]],

       [[-0.0386809 ,  0.0386809 ,  0.0595752 ,  0.10824296,
          0.11708391,  0.03453719, -0.03453719],
        [-0.0386809 ,  0.04609778,  0.07631601,  0.12097389,
          0.12148945,  0.03538336, -0.03453719],
        [-0.0217734 ,  0.03147381,  0.05890764,  0.10676077,
          0.11549389,  0.04021141, -0.03914568],
        [ 0.00885441,  0.0029346 ,  0.02228841,  0.07638465,
          0.10218683,  0.04805681, -0.04528352],
        [ 0.04344957, -0.03351239, -0.02361635,  0.03831967,
          0.08548081,  0.05802898, -0.05164351],
        [ 0.06724989, -0.06239687, -0.05857066,  0.00910301,
          0.07213843,  0.06605287, -0.05571622],
        [ 0.06724989, -0.06724989, -0.07572492, -0.0140384 ,
          0.05140896,  0.05571622, -0.05571622]],

       [[-0.61991954, -0.61991954, -0.6143542 , -0.60563844,
         -0.5964889 , -0.59121823, -0.59121823],
        [ 0.61991954,  0.5917232 ,  0.5858375 ,  0.5782364 ,
          0.57132876,  0.56843126,  0.59121823],
        [ 1.6210319 ,  1.5722902 ,  1.557693  ,  1.5367452 ,
          1.5204405 ,  1.5126007 ,  1.5478977 ],
        [ 2.1372514 ,  2.137276  ,  2.1166012 ,  2.083918  ,
          2.058113  ,  2.0434089 ,  2.0306606 ],
        [ 1.8609889 ,  1.9370515 ,  1.917395  ,  1.8849705 ,
          1.8578848 ,  1.8398389 ,  1.760214  ],
        [ 0.77923036,  0.8336257 ,  0.8219294 ,  0.8069412 ,
          0.7953553 ,  0.78840643,  0.73449546],
        [-0.77923036, -0.77923036, -0.77177703, -0.75726956,
         -0.7452003 , -0.73449546, -0.73449546]]],
      dtype=np.dtype("float32")
    )

  def tear_down_method(self):
    del self.U_[:]

  def test_dt(self, epsilon=1e-4):
    dt_expected = 0.001477
    dt = mattflow_solver._dt(self.U_, epsilon=epsilon)
    dt = round(dt * 1e6) / 1e6
    assert dt == dt_expected
