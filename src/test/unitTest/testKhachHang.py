import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# ==============================================================================
# PHẦN FIX LỖI ĐƯỜNG DẪN (QUAN TRỌNG NHẤT)
# ==============================================================================
# 1. Lấy vị trí của file hiện tại (src/test/unitTest/testKhachHang.py)
current_file_path = os.path.abspath(__file__)

# 2. Lấy thư mục chứa file này (src/test/unitTest)
current_dir = os.path.dirname(current_file_path)

# 3. Đi ngược lên 3 cấp để tìm thư mục gốc dự án (BTL_DACN_CNPM)
#    unitTest -> test -> src -> BTL_DACN_CNPM
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

# 4. Thêm thư mục gốc vào danh sách tìm kiếm của Python
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"DEBUG: Đã thêm đường dẫn gốc vào hệ thống: {project_root}")

# ==============================================================================
# HẾT PHẦN FIX LỖI - BẮT ĐẦU CODE TEST
# ==============================================================================

# Bây giờ Python đã nhìn thấy 'src', ta import bình thường
try:
    from src.Controller.KhachHangController import KhachHangController
    from src.Model.KhachHangModel import KhachHangModel
except ImportError as e:
    print("\n-------------------------------------------------------------")
    print("VẪN LỖI IMPORT! Hãy kiểm tra xem trong thư mục 'src' có file __init__.py chưa?")
    print(f"Chi tiết lỗi: {e}")
    print("-------------------------------------------------------------\n")
    raise e


class TestKhachHangModel(unittest.TestCase):
    """Kiểm tra các hàm thao tác Database trong Model"""

    def setUp(self):
        self.model = KhachHangModel()

    @patch('src.Model.KhachHangModel.mysql.connector.connect')
    def test_check_exist_true(self, mock_connect):
        """Test kiểm tra SĐT tồn tại"""
        mock_cursor = mock_connect.return_value.cursor.return_value
        mock_cursor.fetchone.return_value = (1,)  # Giả lập tìm thấy 1 dòng

        result = self.model.check_exist("0912345678")
        self.assertTrue(result)

    @patch('src.Model.KhachHangModel.mysql.connector.connect')
    def test_insert_khach_hang(self, mock_connect):
        """Test lệnh INSERT"""
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value

        data = {'hoTen': 'A', 'soDienThoai': '0123', 'ngaySinh': '2000-01-01', 'diemTichLuy': 0}

        result = self.model.insert(data)
        self.assertTrue(result)
        mock_conn.commit.assert_called_once()


class TestKhachHangController(unittest.TestCase):
    """Kiểm tra Logic nghiệp vụ trong Controller"""

    def setUp(self):
        self.controller = KhachHangController()
        self.controller.model = MagicMock()  # Mock Model

    # --- Test Validate ---
    def test_format_date_sql(self):
        self.assertEqual(self.controller.format_date_sql("01/05/2000"), "2000-05-01")
        self.assertIsNone(self.controller.format_date_sql("99/99/2000"))

    def test_them_khach_hang_rong_ten(self):
        success, msg = self.controller.them_khach_hang("", "09123", "01/01/2000")
        self.assertFalse(success)

    def test_them_khach_hang_trung_sdt(self):
        self.controller.model.check_exist.return_value = True  # Giả lập SĐT trùng
        success, msg = self.controller.them_khach_hang("Huy", "0912345678", "01/01/2000")
        self.assertFalse(success)
        self.assertIn("đã tồn tại", msg)

    def test_them_khach_hang_thanh_cong(self):
        self.controller.model.check_exist.return_value = False
        self.controller.model.insert.return_value = True

        success, msg = self.controller.them_khach_hang("Huy", "0912345678", "01/05/2000")
        self.assertTrue(success)


if __name__ == '__main__':
    unittest.main()