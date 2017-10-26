import numpy as np
import pytest
from numpy.testing import assert_array_almost_equal, assert_array_equal

from .transformations import clip_matrix


@pytest.fixture
def setup_numpy(scope='module'):
    np.set_printoptions(suppress=True, precision=5)
    yield


def test_clip_matrix(random_state):
    frustum = random_state.random_sample(6)
    frustum[1] += frustum[0]
    frustum[3] += frustum[2]
    frustum[5] += frustum[4]

    cm = clip_matrix(perspective=False, *frustum)
    assert_array_equal(
        np.dot(cm, [frustum[0], frustum[2], frustum[4], 1]),
        [-1., -1., -1., 1.])
    assert_array_equal(
        np.dot(cm, [frustum[1], frustum[3], frustum[5], 1]),
        [1., 1., 1., 1.])

    cm = clip_matrix(perspective=True, *frustum)
    v = np.dot(cm, [frustum[0], frustum[2], frustum[4], 1])
    assert_array_almost_equal(v / v[3],
                              [-1., -1., -1., 1.])
    v = np.dot(cm, [frustum[1], frustum[3], frustum[4], 1])
    assert_array_almost_equal(v / v[3],
                              [1., 1., -1., 1.])
