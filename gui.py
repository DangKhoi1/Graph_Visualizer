from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QTextEdit, QSizePolicy, QFileDialog, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from graph_area import GraphArea
from graph import Graph
from graph import generate_random_graph, export_file, import_file, format_graph_circular
from graph_algorithms import hamiltonian_cycle_with_steps, hamiltonian_cycle_branch_and_bound, hamiltonian_cycle_brute_force, check_dirac_condition, check_ore_condition
from graph import connected_components
from PyQt5.QtGui import QIcon
import pathlib
import random

class GraphGUI(QWidget):
    def __init__(self):
        super().__init__()

        css_path = pathlib.Path(__file__).parent / "style.css"
        try:
            self.setStyleSheet(css_path.read_text(encoding="utf-8"))
        except:
            pass
            
        self.graph = Graph()
        self.setWindowTitle("Giải thuật tìm chu trình Hamilton")
        self.hamilton_steps = [] 
        self.is_step_mode = False

        outer_layout = QVBoxLayout(self)
        heading = QLabel("ỨNG DỤNG VẼ VÀ XỬ LÝ ĐỒ THỊ VÔ HƯỚNG - ÁP DỤNG GIẢI THUẬT TÌM CHU TRÌNH HAMILTON")
        heading.setAlignment(Qt.AlignCenter)
        outer_layout.addWidget(heading)
        heading.setObjectName("heading")
        try:
            icon_path = str(pathlib.Path(__file__).parent / "4fe7b638f74885de07d05000191aad3d_t.jpeg")
            self.setWindowIcon(QIcon(icon_path))
        except:
            pass

        main_layout = QHBoxLayout()
        outer_layout.addLayout(main_layout, stretch=4) 

        center_layout = QVBoxLayout()
        main_layout.addLayout(center_layout, stretch=8)

        self.graph_area = GraphArea(self.graph, lambda: self.draw_combo.currentText(), self)
        self.graph_area.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        self.graph_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        center_layout.addWidget(self.graph_area, stretch=3)

        bottom_layout = QHBoxLayout()
        center_layout.addLayout(bottom_layout, stretch=2)

        result_layout = QVBoxLayout()
        bottom_layout.addLayout(result_layout, stretch=1)

        label_result = QLabel("Kết quả xử lý đồ thị:")
        label_result.setStyleSheet("font-weight: bold;")
        result_layout.addWidget(label_result)

        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        result_layout.addWidget(self.result_output)

        info_layout = QVBoxLayout()
        bottom_layout.addLayout(info_layout, stretch=1)

        label_info = QLabel("Thông tin đồ thị:")
        label_info.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(label_info)

        self.info_box = QTextEdit()
        self.info_box.setReadOnly(True)
        self.info_box.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        info_layout.addWidget(self.info_box)

        component_layout = QVBoxLayout()
        bottom_layout.addLayout(component_layout, stretch=1)

        label_components = QLabel("Miền liên thông:")
        label_components.setStyleSheet("font-weight: bold;")
        component_layout.addWidget(label_components)

        self.components = QTextEdit()
        self.components.setReadOnly(True)
        self.components.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        component_layout.addWidget(self.components)

        control_panel = QVBoxLayout()
        control_panel.setAlignment(Qt.AlignTop)
        main_layout.addLayout(control_panel, stretch=2)

        label_algo = QLabel("Chọn giải thuật")
        label_algo.setObjectName("label_algo")
        control_panel.addWidget(label_algo) 
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(["Quay lui", "Nhánh cận", "Brute Force"])
        self.algorithm_combo.setStyleSheet("padding-left: 15px;")
        self.algorithm_combo.setObjectName("algorithm_combo")
        control_panel.addWidget(self.algorithm_combo)

        label_draw = QLabel("Lựa chọn vẽ")
        label_draw.setObjectName("label_draw")
        control_panel.addWidget(label_draw)
        self.draw_combo = QComboBox()
        self.draw_combo.addItems(["Thêm đỉnh", "Thêm cạnh", "Xóa"])
        self.draw_combo.setStyleSheet("padding-left: 15px;")
        self.draw_combo.setObjectName("draw_combo")
        control_panel.addWidget(self.draw_combo)

        self.instruction_label = QLabel("")
        self.instruction_label.setWordWrap(True)
        self.instruction_label.setStyleSheet("color: #666; font-size: 11px; margin: 5px;")
        control_panel.addWidget(self.instruction_label)

        control_panel.addSpacing(10)
        self.btn_execute = QPushButton("Thực hiện")
        self.btn_components = QPushButton("Miền liên thông")
        self.btn_random = QPushButton("Đồ thị ngẫu nhiên")
        self.btn_format = QPushButton("Format đồ thị")
        self.btn_clear = QPushButton("Xóa đồ thị")
        self.btn_check_condition = QPushButton("Kiểm tra đồ thị")

        for btn in [self.btn_execute, self.btn_components, self.btn_random, self.btn_format, self.btn_clear, self.btn_check_condition]:
            control_panel.addSpacing(15)
            btn.setFixedHeight(30)
            control_panel.addWidget(btn)
            if btn == self.btn_execute:
                btn.setObjectName("btn_execute")
            elif btn == self.btn_components:
                btn.setObjectName("btn_components")
            elif btn == self.btn_random:
                btn.setObjectName("btn_random")
            elif btn == self.btn_format:
                btn.setObjectName("btn_format")
            elif btn == self.btn_clear:
                btn.setObjectName("btn_clear")
            elif btn == self.btn_check_condition:
                self.btn_check_condition.setObjectName("btn_check_condition")


        control_panel.addSpacing(30)
        options_panel = QLabel("Tùy chọn")
        options_panel.setObjectName("options_panel")
        control_panel.addWidget(options_panel)
        self.options_combo = QComboBox()
        self.options_combo.addItems(["Chọn tùy chọn", "Xuất file", "Nhập file", "Xuất ảnh", "Xem thông tin đồ thị", "Thực hiện từng bước"])
        self.options_combo.setStyleSheet("padding-left: 15px;")
        control_panel.addWidget(self.options_combo)

        control_panel.addSpacing(10)
        label_start_vertex = QLabel("Chọn đỉnh bắt đầu")
        label_start_vertex.setObjectName("label_start_vertex")
        control_panel.addWidget(label_start_vertex)
        self.start_vertex_combo = QComboBox()
        self.start_vertex_combo.addItem("Mặc định")
        self.start_vertex_combo.setStyleSheet("padding-left: 15px;")
        self.start_vertex_combo.setObjectName("start_vertex_combo")
        control_panel.addWidget(self.start_vertex_combo)
        
        control_panel.addStretch()


    #Kết nối logic xử lý
        self.btn_random.clicked.connect(self.generate_random_graph)
        self.btn_clear.clicked.connect(self.clear_graph)
        self.btn_execute.clicked.connect(self.run_algorithm)
        self.draw_combo.currentTextChanged.connect(self.on_draw_mode_changed)
        self.options_combo.currentTextChanged.connect(self.handle_option_change)
        self.btn_components.clicked.connect(self.run_connected_components)
        self.btn_format.clicked.connect(self.auto_format_graph)
        self.btn_check_condition.clicked.connect(self.check_condition_graph)
        self.update_instructions()
        self.update_vertex_combo()

    def update_instructions(self):
        mode = self.draw_combo.currentText()
        instructions = {
            "Thêm đỉnh": "Double-click để thêm đỉnh mới",
            "Thêm cạnh": "Giữ Shift + click chọn 2 đỉnh để nối cạnh",
            "Xóa": "Click vào đỉnh hoặc cạnh để xóa"
        }
        base_instruction = instructions.get(mode, "")
        curve_instruction = "Kéo trên cạnh để làm cong"
        self.instruction_label.setText(f"{base_instruction}\n{curve_instruction}")

    def update_vertex_combo(self):
        """Cập nhật combo box chọn đỉnh với các đỉnh hiện tại của đồ thị."""
        current_start = self.start_vertex_combo.currentText()
        self.start_vertex_combo.clear()
        self.start_vertex_combo.addItem("Mặc định")
        for name, _ in self.graph.vertices:
            self.start_vertex_combo.addItem(name)
        if current_start in [name for name, _ in self.graph.vertices] or current_start == "Mặc định":
            self.start_vertex_combo.setCurrentText(current_start)

    def exit_step_mode(self):
        """Khởi động lại chế độ thực hiện từng bước và xóa kết quả hiển thị"""
        self.is_step_mode = False
        self.hamilton_steps = []
        self.result_output.setPlainText("")

    def auto_format_graph(self):
        if not self.graph.vertices:
            QMessageBox.information(self, "Thông báo", "Không có đồ thị để format.")
            return
        self.graph_area.push_undo()
        width = self.graph_area.width()
        height = self.graph_area.height()
        format_graph_circular(self.graph, width, height)
        layout_name = "Hình tròn"
        self.graph_area.update()
        self.update_vertex_combo()
        QMessageBox.information(self, "Thành công", f"Đã format đồ thị theo kiểu {layout_name}.")

    def generate_random_graph(self):
        self.graph_area.push_undo()
        generate_random_graph(self.graph, num_vertices=random.randint(3,6))
        self.graph_area.selected_vertices.clear()
        self.graph_area.clear_hamilton_visualization()
        self.graph_area.update()
        self.result_output.clear()
        self.components.clear()
        self.info_box.clear()
        self.hamilton_steps = []
        self.is_step_mode = False
        self.update_vertex_combo()
        self.graph_area.clear_components()

    def on_draw_mode_changed(self, mode):
        self.graph_area.selected_vertices.clear()
        self.graph_area.update()
        self.update_instructions()

    def clear_graph(self):
        self.graph_area.push_undo()
        self.graph.clear()
        self.graph_area.selected_vertices.clear()
        self.graph_area.clear_hamilton_visualization()
        self.graph_area.update()
        self.result_output.clear()
        self.components.clear()
        self.info_box.clear()
        self.hamilton_steps = []
        self.is_step_mode = False
        self.update_vertex_combo()
        self.graph_area.clear_components()

    def check_condition_graph(self):
        
        if not self.graph.vertices:
            self.result_output.setPlainText("Không có đồ thị để kiểm tra.")
            return
        if connected_components(self.graph)[0] > 1:
            self.result_output.setPlainText( 
            "Đồ thị không liên thông nên không thể có chu trình Hamilton.\n"
            "Vì vậy không cần kiểm các định lý đủ Dirac/Ore (chúng chắc chắn không thỏa).")
            return
        
        check1 = check_dirac_condition(self.graph)
        check2 = check_ore_condition(self.graph)
        
        output = "Kết quả kiểm tra điều kiện:\n\n"
        
        output += "Định lý Dirac:\n"
        output += check1[1] + "\n\n"

        output += "Định lý Ore:\n"
        output += check2[1] + "\n\n"

        if check1[0] or check2[0]:
            output += "Kết luận: Đồ thị chắc chắn tồn tại chu trình Hamilton (vì thỏa ít nhất một định lý đủ)."
        else:
            output += "Kết luận: Không thỏa các định lý đủ Dirac hoặc Ore, nhưng chu trình Hamilton có thể vẫn tồn tại (cần chạy thuật toán để kiểm tra)."
        
        self.result_output.setPlainText(output)
                
        

    def run_algorithm(self):
        if not self.graph.vertices:
            self.result_output.setPlainText("Không có đồ thị để thực hiện.")
            self.graph_area.clear_hamilton_visualization()
            self.hamilton_steps = []
            self.is_step_mode = False
            return
        algo = self.algorithm_combo.currentText()
        start_vertex = self.start_vertex_combo.currentText()
        if start_vertex == "Mặc định":
            start_vertex = None
        if algo == "Quay lui":
            result = hamiltonian_cycle_with_steps(self.graph, start_vertex=start_vertex)
        elif algo == "Nhánh cận":
            result = hamiltonian_cycle_branch_and_bound(self.graph, start_vertex=start_vertex)
        elif algo == "Brute Force":
            result = hamiltonian_cycle_brute_force(self.graph, start_vertex=start_vertex)
        self.hamilton_steps = result.get('steps', [])
        if self.is_step_mode:
            self.graph_area.set_hamilton_steps(self.hamilton_steps)
            self.update_step_display(0)
        else:
            self.graph_area.set_hamilton_visualization(result.get('path', []))
            if result.get('success'):
                output = "Chu trình Hamilton tìm được:\n" + " → ".join(result.get('path', [])) + "\n\n"
                output += "Các bước thực hiện:\n"
                for step in self.hamilton_steps:
                    output += f"Bước {step.get('step', '')}: {step.get('action', '')}\n"
                output += f"\nTổng số bước: {result.get('total_steps', len(self.hamilton_steps))}"
                self.result_output.setPlainText(output)
            else:
                output = "Không tìm thấy chu trình Hamilton.\n\nBởi vì:\n"
                for step in self.hamilton_steps:
                    output += f"Bước {step.get('step', '')}: {step.get('action', '')}\n"
                output += f"\nTổng số bước: {result.get('total_steps', len(self.hamilton_steps))}"
                self.result_output.setPlainText(output)

    def update_step_display(self, step_index):
        """Cập nhật kết quả dựa trên bước đi hiện tại"""
        if not self.hamilton_steps or step_index < 0 or step_index >= len(self.hamilton_steps):
            self.result_output.setPlainText("")
            return
        step = self.hamilton_steps[step_index]
        output = f"Bước {step['step']}: {step['action']}\n"
        output += f"Đường đi hiện tại: {' → '.join(step['path']) if step['path'] else 'Rỗng'}\n"
        output += f"Tổng số bước: {len(self.hamilton_steps)}"
        self.result_output.setPlainText(output)

    def run_exportfile(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Lưu đồ thị", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            export_file(self.graph, file_path)
            QMessageBox.information(self, "Thành công", "Lưu đồ thị thành công!")
    
    def run_importfile(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Nhập đồ thị", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            try:
                self.graph_area.push_undo()
                import_file(self.graph, file_path)
                self.graph_area.selected_vertices.clear()
                self.graph_area.clear_hamilton_visualization()
                self.graph_area.update()
                self.result_output.clear()
                self.components.clear()
                self.hamilton_steps = []
                self.is_step_mode = False
                self.update_vertex_combo()
                self.graph_area.clear_components()
                QMessageBox.information(self, "Thành công", "Nhập đồ thị thành công!")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể nhập file: {str(e)}")


    def update_graph_info(self):
        if not self.graph.vertices:
            self.info_box.setPlainText("Không có đồ thị để hiển thị thông tin.")
            return

        # 1) Đảm bảo font monospace để các cột thẳng hàng
        mono = QFont("Consolas")
        if not mono.fixedPitch():
            mono = QFont("Courier New")
        self.info_box.setFont(mono)

        num_vertices = len(self.graph.vertices)
        num_edges = len(self.graph.edges)
        vertex_names = [name for name, _ in self.graph.vertices]

        # 2) Danh sách cạnh: hỗ trợ cả 2-tuples và 3-tuples
        def edge_uv(e):
            return (e[0], e[1]) if len(e) >= 2 else e

        edge_list = [f"{u}-{v}" for e in self.graph.edges for (u, v) in [edge_uv(e)]]

        # 3) Ma trận + định dạng cột theo độ rộng lớn nhất
        matrix, headers = self.build_adjacency_matrix()

        col_w = max(3, max((len(h) for h in headers), default=1))
        def cell(s): return str(s).ljust(col_w)
        def head(s): return str(s).ljust(col_w)

        lines = []
        lines.append(f"Số đỉnh: {num_vertices}")
        lines.append(f"Số cạnh: {num_edges}")
        lines.append(f"Danh sách đỉnh: {', '.join(vertex_names)}")
        if edge_list:
            lines.append(f"Danh sách cạnh: {', '.join(edge_list)}")

        lines.append("")
        lines.append("Ma trận kề:")
        # Hàng tiêu đề
        lines.append(" " * (col_w + 1) + " ".join(head(h) for h in headers))
        # Các hàng dữ liệu
        for i, row in enumerate(matrix):
            lines.append(head(headers[i]) + " " + " ".join(cell(x) for x in row))

        # 4) Bậc đỉnh
        lines.append("")
        lines.append("Bậc của từng đỉnh:")
        for i, row in enumerate(matrix):
            degree = sum(row)
            lines.append(f"Đỉnh {headers[i]}: {degree}")

        self.info_box.setPlainText("\n".join(lines))


    def build_adjacency_matrix(self):
        # Hỗ trợ đồ thị vô hướng; edges có thể là (u,v) hoặc (u,v,control)
        vertices = [name for name, _ in self.graph.vertices]
        idx = {name: i for i, name in enumerate(vertices)}
        n = len(vertices)
        A = [[0]*n for _ in range(n)]

        for e in self.graph.edges:
            if len(e) < 2:
                continue
            u, v = e[0], e[1]
            if u in idx and v in idx:
                i, j = idx[u], idx[v]
                A[i][j] = 1
                A[j][i] = 1  # nếu vô hướng

        return A, vertices


    def handle_option_change(self, option):
        if option == "Xuất file":
            self.run_exportfile()
            self.options_combo.setCurrentIndex(0)
        elif option == "Nhập file":
            self.run_importfile()
            self.options_combo.setCurrentIndex(0)
        elif option == "Xuất ảnh":
            self.run_export_image()
            self.options_combo.setCurrentIndex(0)
        elif option == "Xem thông tin đồ thị":
            self.update_graph_info()
            self.options_combo.setCurrentIndex(0)
        elif option == "Thực hiện từng bước":
            self.is_step_mode = True
            self.run_algorithm()
            self.options_combo.setCurrentIndex(0)

    def run_connected_components(self):
        if not self.graph.vertices:
            self.components.setPlainText("Không có đồ thị để kiểm tra.")
            return
        num_components, component_list = connected_components(self.graph)
        output = f"Số miền liên thông: {num_components}\n\n"
        for i, comp in enumerate(component_list, 1):
            output += f"Miền {i}: {', '.join(comp)}\n"
        self.components.setPlainText(output)
        self.graph_area.set_components(component_list)
        self.graph_area.btn_stop.setVisible(True) 
    
    def run_export_image(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Lưu ảnh đồ thị",
            "",
            "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;All Files (*)"
        )
        if file_path:
            if file_path.lower().endswith(('.jpg', '.jpeg')):
                image_format = "JPEG"
            else:
                image_format = "PNG"
            self.graph_area.grab().save(file_path, image_format)
            QMessageBox.information(self, "Thành công", "Đã lưu ảnh đồ thị thành công!")