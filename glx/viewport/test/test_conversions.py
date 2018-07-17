import networkx as nx
import numpy as np
from numpy.testing import assert_allclose
from rectangle import Rect

from ..ortho_projection import OrthoProjection
from ..ortho_view import OrthoView
from ...transformations import four_components


def all_paths(g):
    """
    Returns a generator of all possible path lists such that each path list has
    the same start and end points.
    """
    for x in g:
        for y in g:
            paths = list(nx.all_simple_paths(g, x, y))
            if not paths:
                continue
            yield paths


def create_graph_from_space_converter(space_converter):
    methods = [(method, method.split('_to_'))
               for method in dir(type(space_converter))
               if '_to_' in method]

    g = nx.DiGraph()
    for method, path in methods:
        g.add_edge(*path, method=method)

    return g


def check_paths_consistent(g,
                           start_position,
                           space_converter,
                           paths,
                           iterate):
    # print("Checking", type(space_converter).__name__, paths)
    final_position = None
    for path in paths:
        position = start_position
        for edge_start, edge_end in zip(path, path[1:]):
            method = g[edge_start][edge_end]['method']
            position = iterate(position, getattr(space_converter, method))

        if final_position is None:
            final_position = position
            continue

        assert_allclose(final_position, position)


def process(space_converter, start_position_f, iterate,
            desired_total_path_lengths):
    g = create_graph_from_space_converter(space_converter)
    total_path_lengths = 0
    for paths in all_paths(g):
        total_path_lengths += len(paths)
        start_position = start_position_f(space_converter, paths[0][0])
        check_paths_consistent(g,
                               start_position,
                               space_converter,
                               paths,
                               iterate)
    assert total_path_lengths == desired_total_path_lengths


def iterate_rect(rect, t):
    return rect.transformed(t).rectified()


def iterate_vector(position, t):
    return t.dot(position)


def test_projection():
    space_converter = OrthoProjection(Rect([-10.0, -15.0],
                                           [40.0, 45.0]))

    def start_position_f(space_converter, space):
        return four_components(np.random.uniform(size=2))
    process(space_converter, start_position_f, iterate_vector, 2)


def test_view():
    space_converter = OrthoView(zoom=[2.4, 31.2],
                                scroll=[8, 3])
    space_converter.device_pixel_ratio = 3.0

    def start_position_f(space_converter, space):
        return four_components(np.random.uniform(size=2))
    process(space_converter, start_position_f, iterate_vector, 39)
