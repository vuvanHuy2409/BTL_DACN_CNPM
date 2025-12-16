import unittest
import sys
import os
import hashlib
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
    from src.Controller.TaiKhoan2Controller import TaiKhoan2Controller
    from src.Model.TaiKhoan2Model import TaiKhoan2Model
except ImportError as e:
    raise ImportError(f"Lỗi Import. Root: {project_root}. Details: {e}")


# ==============================================================================
# 2. TEST MODEL (DATABASE & SQL)
# ==============================================================================

class TestTaiKhoan2Model(unittest.TestCase):

    def setUp(self):
        self.model = TaiKhoan2Model()

    @patch('src.Model.TaiKhoan2Model.mysql.connector.connect')
    def test_get_employee_info_join(self, mock_connect):
        """Test: Query lấy thông tin phải JOIN 3 bảng (NV, CV, TK)"""
        mock_cursor = mock_connect.return_value.cursor.return_value

        # Act
        self.model.get_employee_info(1)

        # Assert logic SQL
        call_args = mock_cursor.execute.call_args[0]
        sql_query = call_args[0]

        self.assertIn("JOIN chucVu", sql_query)
        self.assertIn("JOIN taiKhoanNhanVien", sql_query)
        self.assertIn("WHERE nv.idNhanVien = %s", sql_query)

    @patch('src.Model.TaiKhoan2Model.mysql.connector.connect')
    def test_verify_password(self, mock_connect):
        """Test: Kiểm tra mật khẩu cũ"""
        mock_cursor = mock_connect.return_value.cursor.return_value

        # Case 1: Đúng (Tìm thấy dòng dữ liệu)
        mock_cursor.fetchone.return_value = (1,)
        self.assertTrue(self.model.verify_password(10, "hash_pass"))

        # Case 2: Sai (Không tìm thấy)
        mock_cursor.fetchone.return_value = None
        self.assertFalse(self.model.verify_password(10, "wrong_hash"))

    @patch('src.Model.TaiKhoan2Model.mysql.connector.connect')
    def test_change_password_query(self, mock_connect):
        """Test: Query đổi mật khẩu"""
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value

        self.model.change_password(10, "new_hash")

        mock_conn.commit.assert_called_once()
        sql_query = mock_cursor.execute.call_args[0][0]
        self.assertIn("UPDATE taiKhoanNhanVien SET matKhauHash", sql_query)


# ==============================================================================
# 3. TEST CONTROLLER (LOGIC NGHIỆP VỤ & BẢO MẬT)
# ==============================================================================

class TestTaiKhoan2Controller(unittest.TestCase):

    def setUp(self):
        self.controller = TaiKhoan2Controller()
        self.controller.model = MagicMock()  # Mock Model

    # --- Test 1: Cập nhật thông tin ---
    def test_save_info_empty(self):
        success, msg = self.controller.save_info(1, "", "", "email")
        self.assertFalse(success)
        self.assertEqual(msg, "Họ tên và SĐT không được để trống!")

    def test_save_info_success(self):
        self.controller.model.update_info.return_value = True

        success, msg = self.controller.save_info(1, "Huy", "0909", "huy@gmail.com")

        self.assertTrue(success)
        self.controller.model.update_info.assert_called_with(1, "Huy", "0909", "huy@gmail.com")

    # --- Test 2: Đổi Mật Khẩu (Logic Phức Tạp) ---

    def test_change_pass_empty(self):
        """Lỗi: Nhập thiếu"""
        success, msg = self.controller.change_password(1, "", "new", "new")
        self.assertFalse(success)
        self.assertIn("Vui lòng nhập đầy đủ", msg)

    def test_change_pass_mismatch(self):
        """Lỗi: Mật khẩu xác nhận không khớp"""
        success, msg = self.controller.change_password(1, "old", "new123", "new456")
        self.assertFalse(success)
        self.assertEqual(msg, "Mật khẩu xác nhận không khớp!")

    def test_change_pass_short(self):
        """Lỗi: Mật khẩu quá ngắn"""
        success, msg = self.controller.change_password(1, "old", "123", "123")
        self.assertFalse(success)
        self.assertIn("từ 6 ký tự", msg)

    def test_change_pass_wrong_old(self):
        """Lỗi: Mật khẩu cũ không đúng"""
        # Giả lập Model báo sai mật khẩu cũ
        self.controller.model.verify_password.return_value = False

        success, msg = self.controller.change_password(1, "old_wrong", "new123456", "new123456")

        self.assertFalse(success)
        self.assertEqual(msg, "Mật khẩu cũ không chính xác!")

    def test_change_pass_success(self):
        """Thành công: Đúng pass cũ, pass mới khớp, độ dài OK"""
        # 1. Giả lập pass cũ đúng
        self.controller.model.verify_password.return_value = True
        # 2. Giả lập update DB thành công
        self.controller.model.change_password.return_value = True

        old_raw = "123456"
        new_raw = "abcdef"

        success, msg = self.controller.change_password(1, old_raw, new_raw, new_raw)

        self.assertTrue(success)
        self.assertEqual(msg, "Đổi mật khẩu thành công!")

        # --- QUAN TRỌNG: Kiểm tra Controller có mã hóa MD5 trước khi gửi xuống Model không ---
        expected_old_hash = hashlib.md5(old_raw.encode()).hexdigest()
        expected_new_hash = hashlib.md5(new_raw.encode()).hexdigest()

        # Kiểm tra bước verify dùng hash
        self.controller.model.verify_password.assert_called_with(1, expected_old_hash)
        # Kiểm tra bước update dùng hash
        self.controller.model.change_password.assert_called_with(1, expected_new_hash)


if __name__ == '__main__':
    unittest.main()