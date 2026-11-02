# Graph Visualizer

Ứng dụng trực quan hóa và xử lý đồ thị vô hướng bằng Python và PyQt5, hỗ trợ vẽ đồ thị, kiểm tra điều kiện Hamilton và tìm chu trình Hamilton theo các thuật toán khác nhau.

## Mô tả dự án

Project này là một ứng dụng desktop giúp người dùng:

- Vẽ và chỉnh sửa đồ thị vô hướng trực quan trên giao diện
- Thêm/xóa đỉnh và cạnh bằng thao tác chuột
- Tạo đồ thị ngẫu nhiên
- Sắp xếp đồ thị theo dạng hình tròn
- Kiểm tra tính liên thông của đồ thị
- Kiểm tra điều kiện đủ của định lý Dirac và Ore
- Tìm chu trình Hamilton bằng các thuật toán:
  - Quay lui (Backtracking)
  - Nhánh cận (Branch and Bound)
  - Brute Force
- Hiển thị từng bước thực hiện thuật toán để minh họa quá trình tìm lời giải
- Xuất/nhập dữ liệu đồ thị từ file JSON
- Xuất ảnh đồ thị ra file PNG/JPG
- Xem thông tin chi tiết của đồ thị: số đỉnh, số cạnh, danh sách đỉnh, danh sách cạnh, ma trận kề, bậc của từng đỉnh

## Tính năng chính

### 1. Vẽ và chỉnh sửa đồ thị
- Chế độ Thêm đỉnh: double-click vào vùng vẽ để thêm đỉnh
- Chế độ Thêm cạnh: giữ Shift và chọn 2 đỉnh để nối cạnh
- Chế độ Xóa: click vào đỉnh hoặc cạnh để xóa
- Có thể kéo cong cạnh bằng cách kéo điểm điều khiển trên cạnh
- Hỗ trợ undo/redo bằng Ctrl+Z / Ctrl+Y

### 2. Xử lý đồ thị
- Tạo đồ thị ngẫu nhiên với số lượng đỉnh ngẫu nhiên
- Format đồ thị theo hình tròn
- Xóa toàn bộ đồ thị
- Kiểm tra miền liên thông
- Kiểm tra định lý Dirac và Ore

### 3. Tìm chu trình Hamilton
- Thuật toán Quay lui
- Thuật toán Nhánh cận
- Brute Force
- Hiển thị từng bước giải thuật để người dùng dễ hiểu quá trình tìm đường đi Hamilton

### 4. Xuất nhập dữ liệu
- Xuất đồ thị ra file JSON
- Nhập đồ thị từ file JSON
- Xuất ảnh màn hình đồ thị ra file hình

## Cấu trúc thư mục

```text
graph-visualizer/
??? pyproject.toml
??? requirements.txt
??? README.md
??? .gitignore
??? src/
?   ??? graph_visualizer/
?       ??? __init__.py
?       ??? __main__.py
?       ??? main.py
?       ??? gui.py
?       ??? graph.py
?       ??? graph_area.py
?       ??? graph_algorithms.py
?       ??? assets/
?           ??? style.qss
?           ??? icon.jpeg
??? tests/
    ??? test_graph.py
```

## Yêu cầu hệ thống

- Python 3.9+
- PyQt5
- Hệ điều hành: Windows, Linux, macOS

## Cài đặt

### 1. Tạo môi trường ảo (khuyến nghị)

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Cài đặt dependency

```bash
python -m pip install -e .
```

## Chạy ứng dụng

Từ thư mục gốc của dự án:

```bash
python -m graph_visualizer
```

Hoặc nếu đang ở thư mục gốc, có thể chạy trực tiếp:

```bash
graph-visualizer
```

## Hướng dẫn sử dụng

1. Mở ứng dụng.
2. Chọn chế độ vẽ đồ thị trong danh sách "Lựa chọn vẽ".
3. Vẽ đồ thị bằng cách:
   - Thêm đỉnh bằng double-click
   - Chọn 2 đỉnh và giữ Shift để tạo cạnh
   - Chọn "Xóa" để xoá đỉnh/cạnh
4. Chọn thuật toán muốn thực thi trong "Chọn giải thuật".
5. Chọn đỉnh bắt đầu nếu cần.
6. Nhấn "Thực hiện" để chạy thuật toán.
7. Hoặc chọn "Thực hiện từng bước" để xem quá trình tìm chu trình Hamilton từng bước.
8. Sử dụng "Kiểm tra đồ thị" để kiểm tra điều kiện Dirac/Ore và tính liên thông.
9. Sử dụng "Xuất file", "Nhập file" hoặc "Xuất ảnh" trong tùy chọn để lưu và tải dữ liệu đồ thị.

## Giải thích thuật toán

### Hamiltonian cycle
Chu trình Hamilton là một chu trình đi qua mỗi đỉnh của đồ thị đúng một lần và quay lại đỉnh bắt đầu.

Ứng dụng kiểm tra và tìm chu trình Hamilton trên đồ thị vô hướng bằng các cách sau:

- Backtracking: thử từng lựa chọn, quay lui khi không hợp lệ
- Branch and Bound: cắt tỉa các nhánh không khả thi để giảm số lượng xét duyệt
- Brute Force: xét tất cả các hoán vị có thể có

### Định lý Dirac và Ore
- Dirac: nếu mọi đỉnh có bậc tối thiểu bằng n/2 thì đồ thị chắc chắn có chu trình Hamilton.
- Ore: nếu mọi cặp đỉnh không kề có tổng bậc lớn hơn hoặc bằng n thì đồ thị chắc chắn có chu trình Hamilton.

## Ghi chú

- Chạy kiểm thử từ thư mục gốc: `python -m unittest discover -s tests -v`.
- Ứng dụng hỗ trợ đồ thị đơn vô hướng: không có cạnh khuyên hoặc cạnh song song; chu trình Hamilton cần ít nhất 3 đỉnh.
- Các thuật toán Hamilton có độ phức tạp tăng nhanh theo số đỉnh. Việc ghi lại từng bước vẫn có thể tốn nhiều bộ nhớ và thời gian với đồ thị lớn.

- Ứng dụng hiện tại chủ yếu hỗ trợ đồ thị vô hướng.
- Dữ liệu đồ thị được lưu dưới dạng JSON.
- Tên đỉnh mặc định được tạo theo ký tự A, B, C, ... theo thứ tự tăng dần.

## Tác giả

Dự án được phát triển nhằm nghiên cứu và minh họa các thuật toán đồ thị, đặc biệt là bài toán chu trình Hamilton.

