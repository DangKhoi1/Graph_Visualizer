from collections import deque
import math
import random
from PyQt5.QtCore import QPoint, QPointF
import json


class Graph:
    def __init__(self):
        self.vertices = []
        self.edges = []
        self.edge_control_points = {}

    def add_vertex(self, vertex):
        name, _ = vertex
        if name not in [v[0] for v in self.vertices]:
            self.vertices.append(vertex)

    def add_edge(self, edge):
        name1, name2 = edge
        if edge not in self.edges and (name2, name1) not in self.edges:
            self.edges.append(edge)
            self.create_default_control_point(edge)

    def create_default_control_point(self, edge):
        name1, name2 = edge
        pos1 = next((pos for n, pos in self.vertices if n == name1), None)
        pos2 = next((pos for n, pos in self.vertices if n == name2), None)
        
        if pos1 and pos2:
            mid_x = (pos1.x() + pos2.x()) / 2
            mid_y = (pos1.y() + pos2.y()) / 2 - 30
            control_point = QPointF(mid_x, mid_y)
            
            self.edge_control_points[edge] = control_point
            self.edge_control_points[(name2, name1)] = control_point

    def get_control_point(self, edge):
        return self.edge_control_points.get(edge, None)

    def set_control_point(self, edge, point):
        name1, name2 = edge
        self.edge_control_points[edge] = point
        self.edge_control_points[(name2, name1)] = point

    def remove_vertex(self, vertex):
        name, _ = vertex
        self.vertices = [v for v in self.vertices if v[0] != name]
        edges_to_remove = [e for e in self.edges if name in e]
        for edge in edges_to_remove:
            self.edges.remove(edge)
            self.edge_control_points.pop(edge, None)
            reverse_edge = (edge[1], edge[0])
            self.edge_control_points.pop(reverse_edge, None)

    def remove_edge(self, edge):
        if edge in self.edges:
            self.edges.remove(edge)
            self.edge_control_points.pop(edge, None)
            self.edge_control_points.pop((edge[1], edge[0]), None)

    def clear(self):
        self.vertices.clear()
        self.edges.clear()
        self.edge_control_points.clear()

def connected_components(graph):
    vertices = [v[0] for v in graph.vertices]
    adjacency = {v: set() for v in vertices}
    for u, v in graph.edges:
        adjacency[u].add(v)
        adjacency[v].add(u)

    visited = set()
    components = []

    def dfs(u, component):
        visited.add(u)
        component.append(u)
        for v in adjacency[u]:
            if v not in visited:
    if num_vertices is None:
        num_vertices = random.randint(3, 6)
    graph.clear()
    spacing = 360 / num_vertices
    center_x, center_y = width // 2, height // 2
    radius = min(center_x, center_y) - 60

    for i in range(num_vertices):
        name = chr(65 + i)
        angle_rad = math.radians(i * spacing)
        x = center_x + int(radius * math.cos(angle_rad))
        y = center_y + int(radius * math.sin(angle_rad))
        graph.add_vertex((name, QPoint(x, y)))

    vertices = [v[0] for v in graph.vertices]
    for i in range(num_vertices):
        for j in range(i + 1, num_vertices):
            if random.random() < edge_probability:
                graph.add_edge((vertices[i], vertices[j]))


def format_graph_circular(graph, width=600, height=500):
    if not graph.vertices:
        return
    
    num_vertices = len(graph.vertices)
    center_x, center_y = width // 2, height // 2
    radius = min(center_x, center_y) - 80
    
    for i, (name, _) in enumerate(graph.vertices):
        angle = 2 * math.pi * i / num_vertices
        x = center_x + int(radius * math.cos(angle))
        y = center_y + int(radius * math.sin(angle))
        graph.vertices[i] = (name, QPoint(x, y))
    
    for edge in graph.edges:
        graph.create_default_control_point(edge)

def export_file(graph, file_path):
    if not file_path:
        return

    data = {
        "vertices": [
            {"name": name, "x": pos.x(), "y": pos.y()}
            for name, pos in graph.vertices
        ],
        "edges": [
            [v1, v2] for v1, v2 in graph.edges
        ],
        "control_points": {
            f"{edge[0]}-{edge[1]}": {"x": point.x(), "y": point.y()}
            for edge, point in graph.edge_control_points.items()
        }
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def import_file(graph, file_path):
    if not file_path:
        return

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    graph.clear()
    
    for v in data.get("vertices", []):
        name = v["name"]
        pos = QPoint(v["x"], v["y"])
        graph.add_vertex((name, pos))
    
    for edge in data.get("edges", []):
        if len(edge) == 2:
            graph.add_edge(tuple(edge))
    
    control_points = data.get("control_points", {})
    for edge_key, point_data in control_points.items():
        if "-" in edge_key:
            parts = edge_key.split("-")
            if len(parts) == 2:
                edge = (parts[0], parts[1])
                control_point = QPointF(point_data["x"], point_data["y"])
                graph.set_control_point(edge, control_point)






