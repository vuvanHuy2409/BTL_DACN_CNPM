import sys
import os

# 1. Lấy đường dẫn thư mục gốc
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# 2. Thêm thư mục View vào đường dẫn tìm kiếm (để sửa lỗi ModuleNotFoundError: sideBar)
view_path = os.path.join(project_root, 'src', 'View')
sys.path.append(view_path)

# 3. Import Class MainApp và CHẠY NÓ
try:
    from src.View.main import MainApp
    print("--> Đang khởi động ứng dụng...")
    app = MainApp() # Dòng này sẽ kích hoạt cửa sổ phần mềm
except Exception as e:
    print(f"Lỗi khởi chạy: {e}")
    input("Nhấn Enter để thoát...")
