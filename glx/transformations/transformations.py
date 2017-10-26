import numpy as np

__all__ = ['four_components',
           'translation_matrix',
           'clip_matrix']


def four_components(x):
    "Pads x to four components using [0, 0, 1].  I.e., [2] -> [2, 0, 0, 1]."
    return np.concatenate((x, [0, 0, 1][len(x) - 1:]), axis=0)


def translation_matrix(direction):
    "Returns a matrix that translates in the given direction"
    direction = np.asarray(direction)
    if direction.shape != (3,):
        raise ValueError("direction has invalid shape")
    retval = np.identity(4)
    retval[:3, 3] = direction[:3]
    return retval


def clip_matrix(left, right, bottom, top, near, far, perspective=False):
    """Returns a matrix to obtain normalized device coordinates from a
    frustum.

    The frustum bounds are axis-aligned along x (left, right),
    y (bottom, top) and z (near, far).

    Normalized device coordinates are in the range [-1, 1] if the coordinates
    are inside the frustum.

    If perspective is true, the frustum is a truncated pyramid with the
    perspective point at origin and direction along z axis, otherwise it is an
    orthographic canonical view volume (a box).

    Homogeneous coordinates transformed by the perspective clip matrix
    need to be dehomogenized (divided by the w coordinate).
    """
    if left >= right:
        raise ValueError("invalid frustum: left ≥ right")
    if bottom >= top:
        raise ValueError("invalid frustum: bottom ≥ top")
    if near >= far:
        raise ValueError("invalid frustum: near ≥ far")
    if perspective:
        if near <= 1e-6:
            raise ValueError("invalid frustum: near <= 0")
        t = 2.0 * near
        m = [[t / (left - right), 0.0, (right + left) / (right - left), 0.0],
             [0.0, t / (bottom - top), (top + bottom) / (top - bottom), 0.0],
             [0.0, 0.0, (far + near) / (near - far), t * far / (far - near)],
             [0.0, 0.0, -1.0, 0.0]]
    else:
        m = [[2.0 / (right - left), 0.0, 0.0, (right + left) / (left - right)],
             [0.0, 2.0 / (top - bottom), 0.0, (top + bottom) / (bottom - top)],
             [0.0, 0.0, 2.0 / (far - near), (far + near) / (near - far)],
             [0.0, 0.0, 0.0, 1.0]]
    return np.array(m)
