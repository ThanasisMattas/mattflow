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

  def teardown_method(self):
    conf.MODE = self.old_mode
    conf.Nx = self.old_nx
    conf.Ny = self.old_ny
    conf.Ng = self.old_ng
    del self.h_history
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
    utils.preprocessing(mode="drops", max_len=0.1, N=9)

  def teardown_method(self):
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
    assert_array_almost_equal(drop_iters, drop_iters_expected)


class TestBcmanager():
  """bcmanager.py tests"""

  def setup_method(self):
    utils.preprocessing(mode="drops", max_len=0.1, N=5)
    self.U_ = np.array(
      [[[2.2657156, 2.2657156, 2.253398, 2.2343802,
         2.21266, 2.1988487, 2.1988487],
        [2.2657156, 2.1992939, 2.1868532, 2.1697948,
         2.1533852, 2.144444, 2.1988487],
        [2.2266014, 2.1764033, 2.1639748, 2.1462896,
         2.128803, 2.1188493, 2.1579635],
        [2.135454, 2.121841, 2.1105056, 2.0922544,
         2.0725465, 2.059794, 2.0652397],
        [1.9963144, 2.03645, 2.0284894, 2.011012,
         1.9889272, 1.9717735, 1.9287541],
        [1.8737274, 1.9598783, 1.9562473, 1.9401051,
         1.9164627, 1.895112, 1.8112943],
        [1.8737274, 1.8737274, 1.8757049, 1.8629198,
         1.8371153, 1.8112943, 1.8112943]],

       [[-0.0386809, 0.0386809, 0.0595752, 0.10824296,
         0.11708391, 0.03453719, -0.03453719],
        [-0.0386809, 0.04609778, 0.07631601, 0.12097389,
         0.12148945, 0.03538336, -0.03453719],
        [-0.0217734, 0.03147381, 0.05890764, 0.10676077,
         0.11549389, 0.04021141, -0.03914568],
        [0.00885441, 0.0029346, 0.02228841, 0.07638465,
         0.10218683, 0.04805681, -0.04528352],
        [0.04344957, -0.03351239, -0.02361635, 0.03831967,
         0.08548081, 0.05802898, -0.05164351],
        [0.06724989, -0.06239687, -0.05857066, 0.00910301,
         0.07213843, 0.06605287, -0.05571622],
        [0.06724989, -0.06724989, -0.07572492, -0.0140384,
         0.05140896, 0.05571622, -0.05571622]],

       [[-0.61991954, -0.61991954, -0.6143542, -0.60563844,
         -0.5964889, -0.59121823, -0.59121823],
        [0.61991954, 0.5917232, 0.5858375, 0.5782364,
         0.57132876, 0.56843126, 0.59121823],
        [1.6210319, 1.5722902, 1.557693, 1.5367452,
         1.5204405, 1.5126007, 1.5478977],
        [2.1372514, 2.137276, 2.1166012, 2.083918,
         2.058113, 2.0434089, 2.0306606],
        [1.8609889, 1.9370515, 1.917395, 1.8849705,
         1.8578848, 1.8398389, 1.760214],
        [0.7792303, 0.8336257, 0.8219294, 0.8069412,
         0.7953553, 0.78840643, 0.73449546],
        [-0.7792303, -0.77923036, -0.77177703, -0.75726956,
         -0.7452003, -0.73449546, -0.73449546]]],
      dtype=np.dtype("float32")
    )

  def teardown_method(self):
    del self.U_

  def test_update_ghost_cells(self):
    U_expected = np.array(
      [[[2.1992939, 2.1992939, 2.1868532, 2.1697948,
         2.1533852, 2.1444440, 2.144444],
        [2.1992939, 2.1992939, 2.1868532, 2.1697948,
         2.1533852, 2.1444440, 2.144444],
        [2.1764033, 2.1764033, 2.1639748, 2.1462896,
         2.1288030, 2.1188493, 2.1188493],
        [2.1218410, 2.1218410, 2.1105056, 2.0922544,
         2.0725465, 2.0597940, 2.059794],
        [2.0364500, 2.0364500, 2.0284894, 2.011012,
         1.9889272, 1.9717735, 1.9717735],
        [1.9598783, 1.9598783, 1.9562473, 1.9401051,
         1.9164627, 1.8951120, 1.895112],
        [1.9598783, 1.9598783, 1.9562473, 1.9401051,
         1.9164627, 1.8951120, 1.895112]],

       [[-0.04609778, 0.04609778, 0.07631601, 0.12097389,
         0.12148945, 0.03538336, -0.03538336],
        [-0.04609778, 0.04609778, 0.07631601, 0.12097389,
         0.12148945, 0.03538336, -0.03538336],
        [-0.03147381, 0.03147381, 0.05890764, 0.10676077,
         0.11549389, 0.04021141, -0.04021141],
        [-0.0029346, 0.00293460, 0.02228841, 0.07638465,
         0.10218683, 0.04805681, -0.04805681],
        [0.03351239, -0.03351239, -0.02361635, 0.03831967,
         0.08548081, 0.05802898, -0.05802898],
        [0.06239687, -0.06239687, -0.05857066, 0.00910301,
         0.07213843, 0.06605287, -0.06605287],
        [0.06239687, -0.06239687, -0.05857066, 0.00910301,
         0.07213843, 0.06605287, -0.06605287]],

       [[-0.5917232, -0.5917232, -0.5858375, -0.5782364,
         -0.57132876, -0.56843126, -0.56843126],
        [0.59172320, 0.59172320, 0.58583750, 0.5782364,
         0.57132876, 0.56843126, 0.56843126],
        [1.5722902, 1.5722902, 1.557693, 1.5367452,
         1.5204405, 1.5126007, 1.5126007],
        [2.1372760, 2.137276, 2.1166012, 2.083918,
         2.0581130, 2.0434089, 2.0434089],
        [1.9370515, 1.9370515, 1.917395, 1.8849705,
         1.8578848, 1.8398389, 1.8398389],
        [0.8336257, 0.8336257, 0.8219294, 0.8069412,
         0.7953553, 0.78840643, 0.78840643],
        [-0.8336257, -0.8336257, -0.8219294, -0.8069412,
         -0.7953553, -0.78840643, -0.78840643]]],
      dtype=np.dtype("float32")
    )
    U_ = bcmanager.update_ghost_cells(self.U_)
    assert_array_almost_equal(U_, U_expected)


class TestMattflowSolver():
  """mattflow_solver.py tests"""

  def setup_method(self):
    conf.MAX_ITERS = 5
    utils.preprocessing(mode="drops", max_len=0.1, N=5)
    self.U_ = np.array(
      [[[2.2657156, 2.2657156, 2.2533980, 2.2343802,
         2.2126600, 2.1988487, 2.1988487],
        [2.2657156, 2.1992939, 2.1868532, 2.1697948,
         2.1533852, 2.1444440, 2.1988487],
        [2.2266014, 2.1764033, 2.1639748, 2.1462896,
         2.1288030, 2.1188493, 2.1579635],
        [2.1354540, 2.1218410, 2.1105056, 2.0922544,
         2.0725465, 2.0597940, 2.0652397],
        [1.9963144, 2.0364500, 2.0284894, 2.0110120,
         1.9889272, 1.9717735, 1.9287541],
        [1.8737274, 1.9598783, 1.9562473, 1.9401051,
         1.9164627, 1.8951120, 1.8112943],
        [1.8737274, 1.8737274, 1.8757049, 1.8629198,
         1.8371153, 1.8112943, 1.8112943]],

       [[-0.0386809, 0.03868090, 0.05957520, 0.10824296,
         0.11708391, 0.03453719, -0.03453719],
        [-0.0386809, 0.04609778, 0.07631601, 0.12097389,
         0.12148945, 0.03538336, -0.03453719],
        [-0.0217734, 0.03147381, 0.05890764, 0.10676077,
         0.11549389, 0.04021141, -0.03914568],
        [0.00885441, 0.00293460, 0.02228841, 0.07638465,
         0.10218683, 0.04805681, -0.04528352],
        [0.04344957, -0.03351239, -0.02361635, 0.03831967,
         0.08548081, 0.05802898, -0.05164351],
        [0.06724989, -0.06239687, -0.05857066, 0.00910301,
         0.07213843, 0.06605287, -0.05571622],
        [0.06724989, -0.06724989, -0.07572492, -0.01403840,
         0.05140896, 0.05571622, -0.05571622]],

       [[-0.61991954, -0.61991954, -0.61435420, -0.60563844,
         -0.5964889, -0.59121823, -0.59121823],
        [0.61991954, 0.59172320, 0.58583750, 0.5782364,
         0.57132876, 0.56843126, 0.59121823],
        [1.62103190, 1.57229020, 1.55769300, 1.5367452,
         1.52044050, 1.51260070, 1.54789770],
        [2.13725140, 2.13727600, 2.11660120, 2.083918,
         2.05811300, 2.04340890, 2.03066060],
        [1.86098890, 1.93705150, 1.91739500, 1.8849705,
         1.85788480, 1.83983890, 1.76021400],
        [0.77923036, 0.83362570, 0.82192940, 0.8069412,
         0.79535530, 0.78840643, 0.73449546],
        [-0.77923036, -0.77923036, -0.77177703, -0.75726956,
         -0.74520030, -0.73449546, -0.73449546]]],
      dtype=np.dtype("float32")
    )

  def teardown_method(self):
    del self.U_

  def test_dt(self, epsilon=1e-4):
    dt_expected = 0.001477
    dt = mattflow_solver._dt(self.U_, epsilon=epsilon)
    dt = round(dt * 1e6) / 1e6
    assert dt == dt_expected

  def test_solve(self):
    conf.RANDOM_DROP_CENTERS = False
    dt = 0.001783
    it = 100
    drops_count = 1
    drop_its_iterator = iter([50, 100, 150])
    next_drop_it = 105
    U_, dc, dii, ndi = mattflow_solver._solve(self.U_,
                                              dt,
                                              it,
                                              drops_count,
                                              drop_its_iterator,
                                              next_drop_it)
    U_expected = np.array(
      [[[2.265716, 2.265716, 2.253398, 2.234380,
         2.212660, 2.198849, 2.198849],
        [2.265716, 2.142474, 2.121917, 2.106767,
         2.095638, 2.097623, 2.198849],
        [2.226601, 2.125890, 2.106579, 2.090932,
         2.079214, 2.079356, 2.157964],
        [2.135454, 2.105225, 2.090809, 2.073869,
         2.059310, 2.052314, 2.065240],
        [1.996314, 2.073545, 2.067764, 2.049927,
         2.031563, 2.013683, 1.928754],
        [1.873727, 2.033693, 2.036091, 2.018517,
         1.996811, 1.969538, 1.811294],
        [1.873727, 1.873727, 1.875705, 1.862920,
         1.837115, 1.811294, 1.811294]],

       [[-0.038681, 0.038681, 0.059575, 0.108243,
         0.117084, 0.034537, -0.034537],
        [-0.038681, 0.096728, 0.093085, 0.128394,
         0.117706, -0.001042, -0.034537],
        [-0.021773, 0.077391, 0.080878, 0.119748,
         0.115628, 0.012494, -0.039146],
        [0.008854, 0.027160, 0.048449, 0.096730,
         0.110042, 0.045107, -0.045284],
        [0.043450, -0.043857, 0.003202, 0.065059,
         0.102794, 0.089755, -0.051644],
        [0.067250, -0.100397, -0.037687, 0.034823,
         0.093436, 0.120846, -0.055716],
        [0.067250, -0.067250, -0.075725, -0.014038,
         0.051409, 0.055716, -0.055716]],

       [[-0.619920, -0.619920, -0.614354, -0.605638,
         -0.596489, -0.591218, -0.591218],
        [0.619920, 0.594617, 0.586972, 0.579118,
         0.571344, 0.569064, 0.591218],
        [1.621032, 1.497677, 1.475009, 1.458078,
         1.448320, 1.452861, 1.547898],
        [2.137251, 2.076686, 2.051381, 2.023597,
         2.006567, 2.002613, 2.030661],
        [1.860989, 1.941344, 1.924393, 1.894164,
         1.873734, 1.858264, 1.760214],
        [0.779230, 0.906403, 0.898084, 0.882192,
         0.873324, 0.864135, 0.734495],
        [-0.779230, -0.779230, -0.771777, -0.757270,
         -0.745200, -0.734495, -0.734495]]],
      dtype=np.dtype("float32")
    )
    assert_array_almost_equal(U_, U_expected)
    assert drops_count == dc
    assert dii == drop_its_iterator
    assert ndi == next_drop_it

  @mock.patch("mattflow.initializer._variance", return_value=0.1)
  @mock.patch("mattflow.initializer.uniform", return_value=0)
  @mock.patch("mattflow.initializer.randint", return_value=10)
  def test_simulate(self, mock_randint, mock_uniform, mock_variance):
    """Can also be regarded as integration test."""
    conf.RANDOM_DROP_CENTERS = False
    h_hist, t_hist, U_ds = mattflow_solver.simulate()
    h_hist_expected = np.array(
      [[[1.608689, 1.610595, 1.593548, 1.558355, 1.506661],
        [1.649861, 1.651833, 1.634196, 1.597786, 1.544305],
        [1.672231, 1.674239, 1.656282, 1.619211, 1.564758],
        [1.674742, 1.676754, 1.658760, 1.621615, 1.567053],
        [1.657273, 1.659257, 1.641514, 1.604885, 1.551082]],
       [[1.624658, 1.619051, 1.601293, 1.573089, 1.545764],
        [1.642868, 1.636539, 1.618507, 1.590551, 1.564204],
        [1.658777, 1.652079, 1.633820, 1.605770, 1.579657],
        [1.664113, 1.657498, 1.639163, 1.610902, 1.584465],
        [1.661089, 1.654912, 1.636628, 1.607942, 1.580575]]],
      dtype=conf.DTYPE
    )
    t_hist_expected = np.array([0.000000, 0.055501])
    assert_array_almost_equal(h_hist, h_hist_expected)
    assert_array_almost_equal(t_hist, t_hist_expected)
