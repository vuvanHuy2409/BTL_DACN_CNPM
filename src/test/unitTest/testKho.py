import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# ==============================================================================
# PHẦN FIX LỖI ĐƯỜNG DẪN (Để Python tìm thấy thư mục src)
# ==============================================================================
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import Module
try:
    from src.Controller.KhoController import KhoController
    from src.Model.KhoModel import KhoModel
except ImportError as e:
    raise ImportError(f"Không tìm thấy module. Hãy đảm bảo project root là: {project_root}. Lỗi: {e}")


# ==============================================================================
# BẮT ĐẦU TEST
# ==============================================================================

class TestKhoModel(unittest.TestCase):
    """Kiểm tra Logic Database trong Model (Đặc biệt là logic tự động set isActive)"""

    def setUp(self):
        self.model = KhoModel()

    @patch('src.Model.KhoModel.mysql.connector.connect')
    def test_insert_status_active(self, mock_connect):
        """Test: Thêm nguyên liệu với số lượng > 0 -> isActive phải là 1"""
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value

        data = {
            'ten': 'Cafe Hat', 'gia': 100000, 'sl': 10,  # Số lượng dương
            'dvt': 'kg', 'idNCC': 1, 'idNV': 1
        }

        self.model.insert(data)

        # Lấy tham số đã truyền vào câu SQL
        call_args = mock_cursor.execute.call_args[0][1]
        # Tham số cuối cùng trong câu query INSERT của bạn là isActive
        trang_thai_luu_db = call_args[6]

        self.assertEqual(trang_thai_luu_db, 1, "Số lượng > 0 thì trạng thái phải là 1")

    @patch('src.Model.KhoModel.mysql.connector.connect')
    def test_insert_status_inactive(self, mock_connect):
        """Test: Thêm nguyên liệu với số lượng = 0 -> isActive phải là 0"""
        mock_cursor = mock_connect.return_value.cursor.return_value

        data = {
            'ten': 'Cafe Het Hang', 'gia': 100000, 'sl': 0,  # Số lượng bằng 0
            'dvt': 'kg', 'idNCC': 1, 'idNV': 1
        }

        self.model.insert(data)

        call_args = mock_cursor.execute.call_args[0][1]
        trang_thai_luu_db = call_args[6]

        self.assertEqual(trang_thai_luu_db, 0, "Số lượng = 0 thì trạng thái phải là 0 (Tự động ẩn)")

    @patch('src.Model.KhoModel.mysql.connector.connect')
    def test_update_logic(self, mock_connect):
        """Test: Cập nhật số lượng cũng phải cập nhật trạng thái"""
        mock_cursor = mock_connect.return_value.cursor.return_value

        # Case: Cập nhật số lượng về âm (-5)
        data = {
            'ten': 'A', 'gia': 1, 'sl': -5,
            'dvt': 'kg', 'idNCC': 1
        }
        self.model.update(10, data)

        call_args = mock_cursor.execute.call_args[0][1]
        # Trong query UPDATE: ..., isActive=%s WHERE idNguyenLieu=%s
        # isActive là tham số thứ 6 (index 5)
        trang_thai_luu_db = call_args[5]

        self.assertEqual(trang_thai_luu_db, 0, "Số lượng âm thì trạng thái phải là 0")


class TestKhoController(unittest.TestCase):
    """Kiểm tra Logic Validate và Thông báo trong Controller"""

    def setUp(self):
        self.controller = KhoController()
        self.controller.model = MagicMock()  # Mock Model

    # --- Test Thêm Nguyên Liệu ---
    def test_add_thieu_thong_tin(self):
        """Test validate thiếu tên hoặc đơn vị tính"""
        success, msg = self.controller.add_nguyen_lieu("", 100, 10, "kg", 1)
        self.assertFalse(success)
        self.assertEqual(msg, "Thiếu thông tin bắt buộc!")

    def test_add_trung_ten(self):
        """Test validate tên đã tồn tại"""
        self.controller.model.check_exist.return_value = True  # Giả lập tên trùng

        success, msg = self.controller.add_nguyen_lieu("Cafe", 100, 10, "kg", 1)

        self.assertFalse(success)
        self.assertEqual(msg, "Tên nguyên liệu đã tồn tại!")

    def test_add_sai_dinh_dang_so(self):
        """Test nhập giá là chữ"""
        self.controller.model.check_exist.return_value = False

        success, msg = self.controller.add_nguyen_lieu("Cafe", "mot_tram_nghin", 10, "kg", 1)

        self.assertFalse(success)
        self.assertIn("phải là số", msg)

    def test_add_thanh_cong(self):
        """Test thêm thành công"""
        self.controller.model.check_exist.return_value = False
        self.controller.model.insert.return_value = True

        success, msg = self.controller.add_nguyen_lieu("Cafe Ngon", "50000", "10", "kg", 1)

        self.assertTrue(success)

        # Kiểm tra dữ liệu đẩy xuống Model đã được ép kiểu float chưa
        expected_data = {
            "ten": "Cafe Ngon", "gia": 50000.0, "sl": 10.0,
            "dvt": "kg", "idNCC": 1, "idNV": 1
        }
        self.controller.model.insert.assert_called_with(expected_data)

    # --- Test Cập Nhật Nguyên Liệu ---
    def test_update_thong_bao_het_hang(self):
        """Test thông báo đặc biệt khi cập nhật số lượng về 0"""
        self.controller.model.update.return_value = True

        # Cập nhật số lượng về 0
        success, msg = self.controller.update_nguyen_lieu(1, "Ten", 100, 0, "kg", 1)

        self.assertTrue(success)
        # Kiểm tra thông báo có chứa câu cảnh báo không
        self.assertIn("(Nguyên liệu đã tự động ẨN do hết hàng)", msg)

    def test_update_binh_thuong(self):
        """Test cập nhật số lượng dương -> Thông báo bình thường"""
        self.controller.model.update.return_value = True

        success, msg = self.controller.update_nguyen_lieu(1, "Ten", 100, 5, "kg", 1)

        self.assertTrue(success)
        self.assertEqual(msg, "Cập nhật thành công!")
        # Không được chứa thông báo ẩn
        self.assertNotIn("tự động ẨN", msg)


if __name__ == '__main__':
    unittest.main()