from math import hypot
from copy import deepcopy
from PyQt5.QtWidgets import QWidget, QInputDialog, QPushButton
from PyQt5.QtCore import Qt, QRect, QPointF
from PyQt5.QtGui import QPainter, QBrush, QColor, QPen, QPainterPath
import random  

class GraphArea(QWidget):
    def __init__(self, graph, mode_getter, parent=None):
        super().__init__(parent)
        self.graph = graph
        self.get_mode = mode_getter
        self.setFocusPolicy(Qt.StrongFocus)
        self.selected_vertex_idx = None
        self.selected_vertices = []
        self.selecting_area = False
        self.selection_start = QPointF()
        self.selection_end = QPointF()
        self.area_selected_vertices = []
        self.area_selected_edges = []
        self.last_mouse_pos = None

        self.undo_stack = []
        self.redo_stack = []

        self.selected_control_point = None
        self.dragging_control_point = False
        self.control_point_radius = 6

        self.hamilton_path = None
        self.dragging_area_selection = False
        self.current_step_index = -1
        self.hamilton_steps = []
        
        # các nút điều khiển giải thuật
        self.btn_next_step = QPushButton("Bước tiếp", self)
        self.btn_next_step.adjustSize()
        self.btn_next_step.setVisible(False)
        self.btn_prev_step = QPushButton("Quay lại", self)
        self.btn_prev_step.adjustSize()
        self.btn_prev_step.setVisible(False)
        self.btn_exit_step_mode = QPushButton("Thoát", self)
        self.btn_exit_step_mode.adjustSize()
        self.btn_exit_step_mode.setVisible(False)
        self.btn_exit_step_mode.setObjectName("btn_exit_step_mode")

        # Nút dừng giải thuật
        self.btn_stop = QPushButton("Dừng", self)
        self.btn_stop.adjustSize()
        self.btn_stop.setVisible(False)
        self.btn_stop.setObjectName("btn_stop")

        # Thêm màu cho liên thông
        self.component_colors = None
        self.vertex_to_component = None

        # Nút kết nối
        self.btn_next_step.clicked.connect(self.show_next_step)
        self.btn_prev_step.clicked.connect(self.show_prev_step)
        self.btn_exit_step_mode.clicked.connect(self.exit_step_mode)
        self.btn_stop.clicked.connect(self.stop_algorithm)

    def resizeEvent(self, event):
        """Vị trí các nút trên vùng vẽ"""
        super().resizeEvent(event)
        self.btn_next_step.move(self.width() - 110, self.height() - 60)
        self.btn_prev_step.move(self.width() - 220, self.height() - 60)
        self.btn_exit_step_mode.move(self.width() - 80, self.height() - 500)
        self.btn_stop.move(self.width() - 80, 10) 

    def clear_hamilton_visualization(self):
        """Xóa tất cả thông tin về đường đi Hamilton"""
        self.hamilton_path = None
        self.current_step_index = -1
        self.hamilton_steps = []
        self.btn_next_step.setVisible(False)
        self.btn_prev_step.setVisible(False)
        self.btn_exit_step_mode.setVisible(False)
        self.btn_stop.setVisible(False)
        self.update()

    def set_hamilton_visualization(self, path):
        """Cài đặt đường đi Hamilton"""
        self.hamilton_path = path
        self.current_step_index = -1
        self.hamilton_steps = []
        self.btn_next_step.setVisible(False)
        self.btn_prev_step.setVisible(False)
        self.btn_exit_step_mode.setVisible(False)
        self.btn_stop.setVisible(True)
        self.update()

    def set_hamilton_steps(self, steps):
        """Các bước trực quan của giải thuật Hamilton"""
        self.hamilton_steps = steps
        self.current_step_index = -1
        if steps:
            self.btn_next_step.setVisible(True)
            self.btn_prev_step.setVisible(True)
            self.btn_exit_step_mode.setVisible(True)
            self.btn_stop.setVisible(False)
            self.show_next_step()
        else:
            self.btn_next_step.setVisible(False)
            self.btn_prev_step.setVisible(False)
            self.btn_exit_step_mode.setVisible(False)
            self.btn_stop.setVisible(False)
        self.update()

    def show_next_step(self):
        """Hiển thị bước kế tiếp của giải thuật"""
        if self.current_step_index < len(self.hamilton_steps) - 1:
            self.current_step_index += 1
            self.hamilton_path = self.hamilton_steps[self.current_step_index]['path']
            self.update()
            self.parent().update_step_display(self.current_step_index)

    def show_prev_step(self):
        """Hiển thị bước quay lại của giải thuật"""
        if self.current_step_index > 0:
            self.current_step_index -= 1
            self.hamilton_path = self.hamilton_steps[self.current_step_index]['path']
            self.update()
            self.parent().update_step_display(self.current_step_index)

    def exit_step_mode(self):
        """Thoát chế độ từng bước"""
        self.clear_hamilton_visualization()
        self.parent().exit_step_mode()

    def stop_algorithm(self):
        """Dừng chế độ hiện tại: tô màu liên thông hoặc thuật toán Hamilton"""
        if self.component_colors is not None:
            self.clear_components()
            self.btn_stop.setVisible(False)
            self.parent().components.setPlainText("Dừng kiểm tra miền liên thông.")
            return
        
        # Code gốc cho Hamilton
        self.clear_hamilton_visualization()
        self.parent().result_output.setPlainText("Đã dừng thuật toán.")

    def is_edge_in_hamilton_path(self, edge_start, edge_end):
        """Kiểm tra xem cạnh có nằm trong đường đi Hamilton hay không"""
        if not self.hamilton_path or len(self.hamilton_path) < 2:
            return False
        
        for i in range(len(self.hamilton_path) - 1):
            path_start = self.hamilton_path[i]
            path_end = self.hamilton_path[i + 1]
            if (edge_start == path_start and edge_end == path_end) or \
               (edge_start == path_end and edge_end == path_start):
                return True
        return False

    #Thiết lập màu cho các thành phần liên thông
    def set_components(self, component_list):
        self.component_colors = []
        self.vertex_to_component = {}
        for i, comp in enumerate(component_list):
            # tạo màu ngẫu nhiên cho mỗi thành phần
            color = QColor(random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
            self.component_colors.append(color)
            for v in comp:
                self.vertex_to_component[v] = i
        self.update()

    #Xóa màu của các thành phần liên thông
    def clear_components(self):
        self.component_colors = None
        self.vertex_to_component = None
        self.update()

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.push_undo()
            self.delete_selected()
        elif event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_C:
            self.copy_selection()
        elif event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_V:
            self.push_undo()
            self.paste_selection()
        elif event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_Z:
            self.undo()
        elif event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_Y:
            self.redo()

        if self.get_mode() == "Thêm cạnh" and event.key() == Qt.Key_Shift:
            self.selected_vertices.clear()
            self.update()

    def push_undo(self):
        state = (
            deepcopy(self.graph.vertices),
            deepcopy(self.graph.edges),
            deepcopy(self.graph.edge_control_points)
        )
        self.undo_stack.append(state)
        self.redo_stack.clear()
    
    def undo(self):
        if self.undo_stack:
            current_state = (
                deepcopy(self.graph.vertices),
                deepcopy(self.graph.edges),
                deepcopy(self.graph.edge_control_points)
            )
            self.redo_stack.append(current_state)
            vertices, edges, control_points = self.undo_stack.pop()
            self.graph.vertices = vertices
            self.graph.edges = edges
            self.graph.edge_control_points = control_points
            self.update()
            self.parent().update_vertex_combo()

    def redo(self):
        if not self.redo_stack:
            return
        current_state = (
            deepcopy(self.graph.vertices),
            deepcopy(self.graph.edges),
            deepcopy(self.graph.edge_control_points)
        )
        self.undo_stack.append(current_state)
        vertices, edges, control_points = self.redo_stack.pop()
        self.graph.vertices = vertices
        self.graph.edges = edges
        self.graph.edge_control_points = control_points
        self.update()
        self.parent().update_vertex_combo()

    def find_control_point_at_pos(self, pos):
        for edge in self.graph.edges:
            name1, name2 = edge
            pos1 = next((pos for n, pos in self.graph.vertices if n == name1), None)
            pos2 = next((pos for n, pos in self.graph.vertices if n == name2), None)
            if not pos1 or not pos2 or name1 == name2:
                continue
            control_point = self.graph.get_control_point(edge)
            if control_point:
                if self.is_point_near_curve(pos, pos1, pos2, control_point, 15):
                    return edge
            else:
                if self.is_point_near_line(pos, pos1, pos2, 15):
                    return edge
        return None

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return

        pos = event.pos()
        self.last_mouse_pos = pos
        mode = self.get_mode()

        clicked_vertex = False
        clicked_vertex_name = None
        for i, (name, vpos) in enumerate(self.graph.vertices):
            if (pos - vpos).manhattanLength() <= 20:
                self.selected_vertex_idx = i
                clicked_vertex = True
                clicked_vertex_name = name
                break

        if clicked_vertex and clicked_vertex_name in self.area_selected_vertices:
            self.dragging_area_selection = True
            self.push_undo()
            return

        if not (clicked_vertex and clicked_vertex_name in self.area_selected_vertices):
            self.area_selected_vertices.clear()
            self.area_selected_edges.clear()

        if not clicked_vertex and mode not in ["Xóa"]:
            control_edge = self.find_control_point_at_pos(pos)
            if control_edge:
                self.selected_control_point = control_edge
                self.dragging_control_point = True
                self.push_undo()
                if not self.graph.get_control_point(control_edge):
                    self.graph.set_control_point(control_edge, pos)
                self.update()
                return

        if not clicked_vertex and not self.dragging_control_point:
            self.selected_vertex_idx = None
            self.selecting_area = True
            self.selection_start = pos
            self.selection_end = pos
            self.update()

        if mode == "Thêm đỉnh" and event.type() == event.MouseButtonDblClick:
            name, ok = QInputDialog.getText(self, "Thêm đỉnh", "Nhập tên đỉnh:")
            if ok and name:
                self.push_undo()
                self.graph.add_vertex((name, pos))
                self.update()
                self.parent().update_vertex_combo()


        if mode == "Thêm cạnh":
            for name, vpos in self.graph.vertices:
                if (pos - vpos).manhattanLength() <= 20:
                    if event.modifiers() & Qt.ShiftModifier:
                        self.selected_vertices.append(name)
                        if len(self.selected_vertices) == 2:
                            self.push_undo()
                            self.graph.add_edge(tuple(self.selected_vertices))
                            self.selected_vertices.clear()
                        self.update()
                    return

        if mode == "Xóa":
            for i, (name, vpos) in enumerate(self.graph.vertices):
                if (pos - vpos).manhattanLength() <= 20:
                    self.push_undo()
                    self.graph.remove_vertex((name, vpos))
                    self.selected_vertices.clear()
                    self.update()
                    self.parent().update_vertex_combo()
                    return
            # Xóa cạnh nếu click vào cạnh
            for edge in self.graph.edges:
                name1, name2 = edge
                pos1 = next((p for n, p in self.graph.vertices if n == name1), None)
                pos2 = next((p for n, p in self.graph.vertices if n == name2), None)
                if pos1 and pos2:
                    control_point = self.graph.get_control_point(edge)
                    if control_point:
                        if self.is_point_near_curve(pos, pos1, pos2, control_point, 10):
                            self.push_undo()
                            self.graph.remove_edge(edge)
                            self.update()
                            return
                    else:
                        if self.is_point_near_line(pos, pos1, pos2, 10):
                            self.push_undo()
                            self.graph.remove_edge(edge)
                            self.update()
                            return
                        
    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return

        updated = False

        # Kéo control point để chỉnh cong cạnh
        if self.dragging_control_point and self.selected_control_point:
            self.graph.set_control_point(self.selected_control_point, event.pos())
            updated = True

        # Kéo nhóm đỉnh đã chọn (area selection)
        elif self.dragging_area_selection and self.area_selected_vertices and self.last_mouse_pos:
            dx = event.pos().x() - self.last_mouse_pos.x()
            dy = event.pos().y() - self.last_mouse_pos.y()
            for i, (name, pos) in enumerate(self.graph.vertices):
                if name in self.area_selected_vertices:
                    self.graph.vertices[i] = (name, QPointF(pos.x() +   dx, pos.y() + dy))
            self.update_all_related_control_points()
            self.last_mouse_pos = event.pos()
            updated = True

        # Kéo một đỉnh đơn lẻ
        elif self.selected_vertex_idx is not None and 0 <= self.selected_vertex_idx < len(self.graph.vertices):
            name, _ = self.graph.vertices[self.selected_vertex_idx]
            self.graph.vertices[self.selected_vertex_idx] = (name, event.pos())
            self.update_related_control_points(name)
            updated = True

        # Vẽ vùng chọn (chuột kéo để chọn nhiều đỉnh/cạnh)
        elif self.selecting_area:
            self.selection_end = event.pos()
            updated = True

        if updated:
            self.update()

    def update_all_related_control_points(self):
        for edge in list(self.graph.edge_control_points.keys()):
            name1, name2 = edge
            if name1 in self.area_selected_vertices and name2 in self.area_selected_vertices:
                self.update_control_point_for_edge(edge)

    def update_related_control_points(self, vertex_name):
        new_pos = next((p for n, p in self.graph.vertices if n == vertex_name), None)
        if not new_pos:
            return
        for edge in list(self.graph.edge_control_points.keys()):
            if vertex_name in edge:
                self.update_control_point_for_edge(edge)

    def update_control_point_for_edge(self, edge):
        name1, name2 = edge
        pos1 = next((p for n, p in self.graph.vertices if n == name1), None)
        pos2 = next((p for n, p in self.graph.vertices if n == name2), None)
        if not pos1 or not pos2 or (pos1 == pos2):
            return
        control_point = self.graph.get_control_point(edge)
        if not control_point:
            return

        # Vector từ pos1 đến pos2
        edge_vec = pos2 - pos1
        if edge_vec.x() == 0 and edge_vec.y() == 0:
            return

        # Vector vuông góc đơn vị
        perp = QPointF(-edge_vec.y(), edge_vec.x())
        length = (perp.x() ** 2 + perp.y() ** 2) ** 0.5
        if length == 0:
            return
        perp /= length

        # Trung điểm cạnh
        mid = (pos1 + pos2) * 0.5

        # Khoảng cách từ control_point đến đường thẳng, theo hướng vuông góc
        dist = (control_point - mid).x() * perp.x() + (control_point - mid).y() * perp.y()

        # Đặt lại control_point theo khoảng cách này
        new_cp = mid + perp * dist
        self.graph.set_control_point(edge, new_cp)

    def mouseReleaseEvent(self, event):
        self.selected_vertex_idx = None
        self.dragging_control_point = False
        self.selected_control_point = None
        self.dragging_area_selection = False
        if self.selecting_area:
            self.selecting_area = False
            self.area_selected_vertices.clear()
            self.area_selected_edges.clear()
            rect = QRect(
                self.selection_start.toPoint() if isinstance(self.selection_start, QPointF) else self.selection_start,
                self.selection_end.toPoint() if isinstance(self.selection_end, QPointF) else self.selection_end
            ).normalized()
            for name, pos in self.graph.vertices:
                if rect.contains(pos.toPoint() if isinstance(pos, QPointF) else pos):
                    self.area_selected_vertices.append(name)
            for name1, name2 in self.graph.edges:
                pos1 = next((p for n, p in self.graph.vertices if n == name1), None)
                pos2 = next((p for n, p in self.graph.vertices if n == name2), None)
                if pos1 and pos2 and rect.contains(pos1.toPoint() if isinstance(pos1, QPointF) else pos1) \
                        and rect.contains(pos2.toPoint() if isinstance(pos2, QPointF) else pos2):
                    self.area_selected_edges.append((name1, name2))
            self.update()

    def delete_selected(self):
        self.graph.vertices = [(n, p) for (n, p) in self.graph.vertices if n not in self.area_selected_vertices]
        self.graph.edges = [(a, b) for (a, b) in self.graph.edges if a not in self.area_selected_vertices and b not in self.area_selected_vertices]
        edges_to_remove = []
        for edge in self.graph.edge_control_points:
            if edge[0] in self.area_selected_vertices or edge[1] in self.area_selected_vertices:
                edges_to_remove.append(edge)
        for edge in edges_to_remove:
            self.graph.edge_control_points.pop(edge, None)
        self.area_selected_vertices.clear()
        self.area_selected_edges.clear()
        self.update()
        self.parent().update_vertex_combo()

    def copy_selection(self):
        self._copied = [
            (name, pos) for name, pos in self.graph.vertices if name in self.area_selected_vertices
        ]

    def paste_selection(self):
        if not hasattr(self, '_copied') or not self._copied:
            return
        offset = QPointF(40, 40)
        new_names = []
        base_names = set(n for n, _ in self.graph.vertices)
        for name, pos in self._copied:
            new_name = name
            i = 1
            while new_name in base_names:
                new_name = f"{name}_{i}"
                i += 1
            base_names.add(new_name)
            self.graph.vertices.append((new_name, pos + offset))
            new_names.append((name, new_name))
        old_to_new = dict(new_names)
        for a, b in self.graph.edges:
            if a in old_to_new and b in old_to_new:
                self.graph.edges.append((old_to_new[a], old_to_new[b]))
        self.update()
        self.parent().update_vertex_combo()

    def is_point_near_line(self, p, a, b, tolerance=10):
        ab = b - a
        ap = p - a
        ab_len_sq = ab.x() ** 2 + ab.y() ** 2
        if ab_len_sq == 0:
            return (p - a).manhattanLength() <= tolerance
        t = max(0, min(1, (ap.x() * ab.x() + ap.y() * ab.y()) / ab_len_sq))
        projection = a + ab * t
        dx = projection.x() - p.x()
        dy = projection.y() - p.y()
        return hypot(dx, dy) <= tolerance

    def is_point_near_curve(self, point, start, end, control, tolerance=10):
        for t in [i/20.0 for i in range(21)]:
            curve_point = QPointF(
                (1-t)**2 * start.x() + 2*(1-t)*t * control.x() + t**2 * end.x(),
                (1-t)**2 * start.y() + 2*(1-t)*t * control.y() + t**2 * end.y()
            )
            if (point - curve_point).manhattanLength() <= tolerance:
                return True
        return False

    def draw_bezier_curve(self, painter, start, end, control):
        path = QPainterPath()
        path.moveTo(start)
        path.quadTo(control, end)
        painter.drawPath(path)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), Qt.white)

        # vẽ các cạnh với màu sắc khác nhau cho thành phần liên thông nếu hợp lệ
        for start, end in self.graph.edges:
            pos1 = next((p for n, p in self.graph.vertices if n == start), None)
            pos2 = next((p for n, p in self.graph.vertices if n == end), None)
            if not pos1 or not pos2:
                continue
            is_hamilton_edge = self.is_edge_in_hamilton_path(start, end)
            if is_hamilton_edge:
                painter.setPen(QPen(QColor("green"), 5))
            elif (start, end) in self.area_selected_edges or (end, start) in self.area_selected_edges:
                painter.setPen(QPen(QColor("deepskyblue"), 3))
            elif self.component_colors and start in self.vertex_to_component and end in self.vertex_to_component:
                comp_id = self.vertex_to_component[start] 
                color = self.component_colors[comp_id]
                painter.setPen(QPen(color, 2))
            else:
                painter.setPen(QPen(Qt.black, 2))
            if start == end:
                path = QPainterPath()
                path.moveTo(pos1)
                ctrl1 = QPointF(pos1.x() + 60, pos1.y() - 60)
                ctrl2 = QPointF(pos1.x() - 60, pos1.y() - 60)
                path.cubicTo(ctrl1, ctrl2, pos1)
                painter.drawPath(path)
            else:
                control_point = self.graph.get_control_point((start, end))
                if control_point:
                    self.draw_bezier_curve(painter, pos1, pos2, control_point)
                else:
                    painter.drawLine(pos1, pos2)

        # Draw vertices with component colors if available
        highlight = self.selected_vertices if self.get_mode() == "Thêm cạnh" else []
        for name, pos in self.graph.vertices:
            if name in highlight:
                pen = QPen(Qt.red, 4)
                brush = QBrush(QColor("yellow"))
            elif name in self.area_selected_vertices:
                pen = QPen(QColor("deepskyblue"), 4)
                brush = QBrush(Qt.white)
            elif self.hamilton_path and name in self.hamilton_path:
                pen = QPen(QColor("green"), 4)
                brush = QBrush(QColor("lightgreen"))
            elif self.component_colors and name in self.vertex_to_component:
                comp_id = self.vertex_to_component[name]
                color = self.component_colors[comp_id]
                pen = QPen(color.darker(150), 2)  # Darker border for visibility
                brush = QBrush(color.lighter(150))  # Lighter fill for vertices
            else:
                pen = QPen(Qt.black, 2)
                brush = QBrush(Qt.white)
            painter.setPen(pen)
            painter.setBrush(brush)
            painter.drawEllipse(pos, 20, 20)
            label_rect = QRect(int(pos.x()) - 20, int(pos.y()) - 20, 40, 40)
            font = painter.font()
            font.setBold(True)
            painter.setFont(font)
            if self.hamilton_path and name in self.hamilton_path:
                painter.setPen(QPen(Qt.darkGreen, 2))
            else:
                painter.setPen(QPen(Qt.black, 2))
            painter.drawText(label_rect, Qt.AlignCenter, name)

        if self.selecting_area:
            painter.setPen(QPen(QColor(0, 120, 215, 200), 1, Qt.SolidLine))
            painter.setBrush(QBrush(QColor(0, 120, 215, 60)))
            selection_rect = QRect(
                self.selection_start.toPoint() if isinstance(self.selection_start, QPointF) else self.selection_start,
                self.selection_end.toPoint() if isinstance(self.selection_end, QPointF) else self.selection_end
            ).normalized()
            painter.drawRect(selection_rect)