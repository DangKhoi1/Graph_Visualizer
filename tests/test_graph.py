import itertools
import json
import os
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtCore import QPoint, QPointF
from PyQt5.QtWidgets import QApplication
from graph_visualizer.graph import Graph, connected_components, export_file, import_file
from graph_visualizer.graph_algorithms import (
    hamiltonian_cycle_with_steps,
    hamiltonian_cycle_branch_and_bound,
    hamiltonian_cycle_brute_force,
)

ALGORITHMS = (hamiltonian_cycle_with_steps, hamiltonian_cycle_branch_and_bound, hamiltonian_cycle_brute_force)


def make_graph(names, edges=()):
    graph = Graph()
    for i, name in enumerate(names):
        graph.add_vertex((name, QPoint(i * 40, i * 30)))
    for edge in edges:
        graph.add_edge(edge)
    return graph


class GraphTests(unittest.TestCase):
    def test_all_small_graphs(self):
        for n in range(5):
            names = list("ABCDE"[:n])
            pairs = list(itertools.combinations(names, 2))
            for mask in range(1 << len(pairs)):
                edges = [edge for i, edge in enumerate(pairs) if mask & (1 << i)]
                graph = make_graph(names, edges)
                edge_set = {frozenset(edge) for edge in edges}
                expected = n >= 3 and any(
                    all(frozenset((path[i], path[(i + 1) % n])) in edge_set for i in range(n))
                    for path in itertools.permutations(names)
                )
                for algorithm in ALGORITHMS:
                    result = algorithm(graph)
                    self.assertEqual(result['success'], expected, (algorithm.__name__, edges))
                    self.assertEqual(result['total_steps'], len(result['steps']))
                    if expected:
                        self.assertEqual(len(result['path']), n + 1)
                        self.assertEqual(result['path'][0], result['path'][-1])
                        self.assertEqual(set(result['path']), set(names))

    def test_edge_validation_and_origin(self):
        graph = make_graph('AB', [('A', 'B')])
        self.assertIsNotNone(graph.get_control_point(('A', 'B')))
        for edge in [('A', 'A'), ('A', 'missing')]:
            with self.assertRaises(ValueError):
                graph.add_edge(edge)
        graph.remove_edge(('B', 'A'))
        self.assertEqual(graph.edges, [])
        self.assertEqual(graph.edge_control_points, {})

    def test_import_is_transactional_and_preserves_coordinates(self):
        graph = make_graph(['A-one', 'B'], [('A-one', 'B')])
        graph.vertices[0] = ('A-one', QPointF(1.5, 2.5))
        graph.set_control_point(('A-one', 'B'), QPointF(9.5, 12.5))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'graph.json'
            export_file(graph, path)
            loaded = Graph()
            import_file(loaded, path)
            self.assertEqual(loaded.vertices, graph.vertices)
            self.assertEqual(loaded.edge_control_points, graph.edge_control_points)
            path.write_text(json.dumps({'vertices': [], 'edges': [['bad', 'edge']]}))
            with self.assertRaises(ValueError):
                import_file(loaded, path)
            self.assertEqual(loaded.vertices, graph.vertices)

    def test_large_connected_component(self):
        names = [str(i) for i in range(1500)]
        graph = make_graph(names, zip(names, names[1:]))
        self.assertEqual(connected_components(graph)[0], 1)


class GuiTests(unittest.TestCase):
    def test_direct_entry_points_from_another_directory(self):
        package = Path(__file__).resolve().parents[1] / 'src' / 'graph_visualizer'
        for filename in ('main.py', '__main__.py'):
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as directory:
                script = (
                    'import runpy, sys; '
                    'from PyQt5.QtCore import QTimer; '
                    'from PyQt5.QtWidgets import QApplication; '
                    'original = QApplication.exec_; '
                    'QApplication.exec_ = lambda app: '
                    '(QTimer.singleShot(100, app.quit), original())[1]; '
                    'runpy.run_path(sys.argv[1], run_name="__main__")'
                )
                result = subprocess.run(
                    [sys.executable, '-c', script, str(package / filename)],
                    cwd=directory, capture_output=True, text=True, timeout=20,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_startup_copy_paste_and_render(self):
        from graph_visualizer.gui import GraphGUI
        window = GraphGUI()
        self.addCleanup(window.close)
        self.assertTrue(window.styleSheet())
        self.assertFalse(window.windowIcon().isNull())
        window.graph.add_vertex(('A', QPoint(50, 50)))
        window.graph.add_vertex(('B', QPoint(150, 150)))
        window.graph.add_edge(('A', 'B'))
        area = window.graph_area
        area.area_selected_vertices = ['A', 'B']
        area.copy_selection()
        area.paste_selection()
        self.assertEqual(len(window.graph.vertices), 4)
        self.assertEqual(len(window.graph.edges), 2)
        self.assertIsNotNone(window.graph.get_control_point(('A_1', 'B_1')))
        window.graph.vertices[0] = ('A', QPointF(60.5, 60.5))
        area.update_related_control_points('A')
        window.resize(1200, 800)
        window.show()
        self.app.processEvents()
        self.assertFalse(window.grab().isNull())


if __name__ == '__main__':
    unittest.main()
