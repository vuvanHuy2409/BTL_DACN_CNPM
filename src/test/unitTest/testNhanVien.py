import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# ==============================================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN TỰ ĐỘNG
# ==============================================================================
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.Controller.NhanVienController import NhanVienController
    from src.Model.NhanVienModel2 import NhanVienModel2
except ImportError as e:
    raise ImportError(f"Lỗi Import. Root: {project_root}. Details: {e}")


# ==============================================================================
# 2. TEST MODEL (LOGIC DATABASE)
# ==============================================================================

class TestNhanVienModel(unittest.TestCase):

    def setUp(self):
        self.model = NhanVienModel2()

    @patch('src.Model.NhanVienModel2.mysql.connector.connect')
    def test_toggle_status_to_nghi_viec(self, mock_connect):
        """Test: Đang làm việc -> Đã nghỉ việc"""
        mock_cursor = mock_connect.return_value.cursor.return_value

        # Giả lập DB trả về trạng thái hiện tại là 'DangLamViec'
        mock_cursor.fetchone.return_value = {'trangThaiLamViec': 'DangLamViec'}

        self.model.toggle_status(1)

        # Kiểm tra lệnh UPDATE sau đó
        call_args = mock_cursor.execute.call_args_list
        update_query = call_args[1][0][0]  # Lần gọi thứ 2 (Lần 1 là SELECT)
        update_params = call_args[1][0][1]

        self.assertIn("UPDATE nhanVien SET trangThaiLamViec", update_query)
        self.assertEqual(update_params[0], 'DaNghiViec')  # Kỳ vọng chuyển sang Nghỉ

    @patch('src.Model.NhanVienModel2.mysql.connector.connect')
    def test_toggle_status_to_lam_viec(self, mock_connect):
        """Test: Đã nghỉ việc -> Đang làm việc"""
        mock_cursor = mock_connect.return_value.cursor.return_value

        # Giả lập DB trả về trạng thái hiện tại là 'DaNghiViec'
        mock_cursor.fetchone.return_value = {'trangThaiLamViec': 'DaNghiViec'}

        self.model.toggle_status(1)

        update_params = mock_cursor.execute.call_args_list[1][0][1]
        self.assertEqual(update_params[0], 'DangLamViec')  # Kỳ vọng chuyển sang Làm

    @patch('src.Model.NhanVienModel2.mysql.connector.connect')
    def test_insert_default_status(self, mock_connect):
        """Test: Thêm nhân viên mới phải mặc định là 'DangLamViec'"""
        mock_cursor = mock_connect.return_value.cursor.return_value

        data = {'hoTen': 'A', 'email': 'a@a.com', 'soDienThoai': '123', 'idChucVu': 1, 'phanQuyen': 'admin'}
        self.model.insert(data)

        sql_query = mock_cursor.execute.call_args[0][0]
        self.assertIn("'DangLamViec'", sql_query)  # Kiểm tra hardcode trong SQL


# ==============================================================================
# 3. TEST CONTROLLER (LOGIC VALIDATE & REGEX)
# ==============================================================================

class TestNhanVienController(unittest.TestCase):

    def setUp(self):
        self.controller = NhanVienController()
        self.controller.model = MagicMock()  # Mock Model

    # --- Test 1: Validate Email (Regex) ---
    def test_is_valid_email(self):
        # Case đúng
        self.assertTrue(self.controller.is_valid_email("huy@gmail.com"))
        self.assertTrue(self.controller.is_valid_email("admin.coffee@company.vn"))

        # Case sai
        self.assertFalse(self.controller.is_valid_email("huygmail.com"))  # Thiếu @
        self.assertFalse(self.controller.is_valid_email("huy@gmailcom"))  # Thiếu .
        self.assertFalse(self.controller.is_valid_email("huy@.com"))  # Thiếu domain

    # --- Test 2: Thêm Nhân Viên ---
    def test_add_nhan_vien_thieu_thong_tin(self):
        success, msg = self.controller.add_nhan_vien("", "email", "sdt", "role", 1)
        self.assertFalse(success)
        self.assertEqual(msg, "Thiếu thông tin bắt buộc!")

    def test_add_nhan_vien_email_sai(self):
        success, msg = self.controller.add_nhan_vien("Ten", "email_sai", "0909", "role", 1)
        self.assertFalse(success)
        self.assertEqual(msg, "Email không hợp lệ!")

    def test_add_nhan_vien_chua_chon_chuc_vu(self):
        # id_chuc_vu = None
        success, msg = self.controller.add_nhan_vien("Ten", "a@g.com", "0909", "role", None)
        self.assertFalse(success)
        self.assertEqual(msg, "Vui lòng chọn chức vụ!")

    def test_add_nhan_vien_trung_lap(self):
        # Giả lập Model báo trùng
        self.controller.model.check_exist.return_value = True

        success, msg = self.controller.add_nhan_vien("Ten", "a@g.com", "0909", "role", 1)
        self.assertFalse(success)
        self.assertIn("đã tồn tại", msg)

    def test_add_nhan_vien_thanh_cong(self):
        # Giả lập mọi thứ OK
        self.controller.model.check_exist.return_value = False
        self.controller.model.insert.return_value = True

        success, msg = self.controller.add_nhan_vien("Huy", "huy@gmail.com", "0909", "admin", 1)

        self.assertTrue(success)
        self.assertEqual(msg, "Thêm thành công!")

        # Kiểm tra data gửi xuống Model
        expected_data = {
            "hoTen": "Huy", "email": "huy@gmail.com",
            "soDienThoai": "0909", "phanQuyen": "admin", "idChucVu": 1
        }
        self.controller.model.insert.assert_called_with(expected_data)

    # --- Test 3: Quản lý Chức Vụ ---
    def test_them_chuc_vu_luong_sai(self):
        success, msg = self.controller.them_chuc_vu("Quan ly", "muoi trieu")
        self.assertFalse(success)
        self.assertEqual(msg, "Lương phải là số!")

    def test_them_chuc_vu_thanh_cong(self):
        self.controller.model.add_chucvu.return_value = True

        success, msg = self.controller.them_chuc_vu("Quan ly", "15000000")

        self.assertTrue(success)
        # Kiểm tra ép kiểu float
        self.controller.model.add_chucvu.assert_called_with("Quan ly", 15000000.0)


if __name__ == '__main__':
    unittest.main()