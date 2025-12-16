import unittest
import sys
import os
import hashlib
from unittest.mock import patch, MagicMock, ANY

# ==============================================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN TỰ ĐỘNG
# ==============================================================================
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.Controller.TaiKhoanController import TaiKhoanController
    from src.Model.TaiKhoanModel import TaiKhoanModel
except ImportError as e:
    raise ImportError(f"Lỗi Import. Root: {project_root}. Details: {e}")


# ==============================================================================
# 2. TEST CONTROLLER (Logic phức tạp nằm ở đây)
# ==============================================================================

class TestTaiKhoanController(unittest.TestCase):

    def setUp(self):
        self.controller = TaiKhoanController()

    # --- Test 1: Tìm kiếm tài khoản ---
    @patch('src.Controller.TaiKhoanController.mysql.connector.connect')
    def test_tim_kiem_tai_khoan(self, mock_connect):
        """Test tìm kiếm với từ khóa"""
        mock_cursor = mock_connect.return_value.cursor.return_value

        # Act
        self.controller.tim_kiem_tai_khoan("Huy")

        # Assert
        call_args = mock_cursor.execute.call_args[0]
        sql_query = call_args[0]
        params = call_args[1]

        # Kiểm tra logic SQL
        self.assertIn("LIKE %s", sql_query)
        # Kiểm tra tham số truyền vào phải có %...%
        self.assertEqual(params, ("%Huy%", "%Huy%", "%Huy%"))

    # --- Test 2: Lưu tài khoản (INSERT - Tạo mới) ---
    @patch('src.Controller.TaiKhoanController.mysql.connector.connect')
    def test_save_account_create_new(self, mock_connect):
        """Test tạo tài khoản mới: Insert TK -> Update NV -> Commit"""
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value

        # Giả lập ID tài khoản mới vừa tạo là 100
        mock_cursor.lastrowid = 100

        # Act
        # id_nv=1, has_account=False (Tạo mới), user='admin', pass='123'
        success, msg = self.controller.save_account(1, False, "Name", "admin", "123", "email", "Role")

        # Assert
        self.assertTrue(success)

        # 1. Kiểm tra mã hóa mật khẩu MD5
        expected_hash = hashlib.md5("123".encode()).hexdigest()

        # 2. Kiểm tra lệnh INSERT vào bảng taiKhoanNhanVien
        calls = mock_cursor.execute.call_args_list
        insert_call = calls[0][0]  # Lần gọi đầu tiên
        self.assertIn("INSERT INTO taiKhoanNhanVien", insert_call[0])
        self.assertIn(expected_hash, insert_call[1])  # Phải chứa pass đã hash

        # 3. Kiểm tra lệnh UPDATE vào bảng nhanVien (Gán idTaiKhoan = 100)
        update_call = calls[1][0]  # Lần gọi thứ 2
        self.assertIn("UPDATE nhanVien SET idTaiKhoan", update_call[0])
        self.assertIn(100, update_call[1])  # Phải chứa ID 100

        # 4. Kiểm tra commit
        mock_conn.commit.assert_called_once()

    # --- Test 3: Lưu tài khoản (UPDATE - Đổi mật khẩu) ---
    @patch('src.Controller.TaiKhoanController.mysql.connector.connect')
    def test_save_account_update_with_pass(self, mock_connect):
        """Test cập nhật tài khoản CÓ đổi mật khẩu"""
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value

        # Act: has_account=True, password="new_pass"
        success, msg = self.controller.save_account(1, True, "Name", "admin", "new_pass", "email", "Role")

        self.assertTrue(success)

        # Kiểm tra SQL Update có chứa trường matKhauHash
        sql_query = mock_cursor.execute.call_args[0][0]
        self.assertIn("UPDATE taiKhoanNhanVien", sql_query)
        self.assertIn("matKhauHash = %s", sql_query)

    # --- Test 4: Lưu tài khoản (UPDATE - Không đổi mật khẩu) ---
    @patch('src.Controller.TaiKhoanController.mysql.connector.connect')
    def test_save_account_update_no_pass(self, mock_connect):
        """Test cập nhật tài khoản KHÔNG đổi mật khẩu"""
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value

        # Act: password="" (Rỗng)
        success, msg = self.controller.save_account(1, True, "Name", "admin", "", "email", "Role")

        self.assertTrue(success)

        # Kiểm tra SQL Update KHÔNG được chứa trường matKhauHash
        sql_query = mock_cursor.execute.call_args[0][0]
        self.assertIn("UPDATE taiKhoanNhanVien", sql_query)
        self.assertNotIn("matKhauHash", sql_query)

    # --- Test 5: Validate dữ liệu ---
    @patch('src.Controller.TaiKhoanController.mysql.connector.connect')
    def test_save_account_missing_info(self, mock_connect):
        # Case 1: Thiếu username
        success, msg = self.controller.save_account(1, False, "Name", "", "123", "email", "Role")
        self.assertFalse(success)
        self.assertEqual(msg, "Tên đăng nhập không được để trống!")

        # Case 2: Tạo mới mà thiếu password
        success, msg = self.controller.save_account(1, False, "Name", "admin", "", "email", "Role")
        self.assertFalse(success)
        self.assertIn("nhập mật khẩu", msg)

    # --- Test 6: Xóa tài khoản ---
    @patch('src.Controller.TaiKhoanController.mysql.connector.connect')
    def test_delete_account_success(self, mock_connect):
        """Test xóa tài khoản: Lấy ID -> Gỡ liên kết -> Xóa"""
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value

        # Giả lập: Nhân viên ID=1 đang gắn với Tài khoản ID=50
        mock_cursor.fetchone.return_value = (50,)

        # Act
        success, msg = self.controller.delete_account_only(1)

        # Assert
        self.assertTrue(success)

        # Kiểm tra trình tự gọi
        calls = [str(call[0][0]) for call in mock_cursor.execute.call_args_list]

        # 1. Select lấy ID
        self.assertTrue(any("SELECT idTaiKhoan" in s for s in calls))
        # 2. Update set NULL
        self.assertTrue(any("UPDATE nhanVien SET idTaiKhoan = NULL" in s for s in calls))
        # 3. Delete
        self.assertTrue(any("DELETE FROM taiKhoanNhanVien" in s for s in calls))

        mock_conn.commit.assert_called_once()


# ==============================================================================
# 3. TEST MODEL
# ==============================================================================

class TestTaiKhoanModel(unittest.TestCase):

    def setUp(self):
        self.model = TaiKhoanModel()

    @patch('src.Model.TaiKhoanModel.mysql.connector.connect')
    def test_check_user_exist(self, mock_connect):
        mock_cursor = mock_connect.return_value.cursor.return_value

        # Case True
        mock_cursor.fetchone.return_value = (1,)
        self.assertTrue(self.model.check_user_exist("admin"))

        # Case False
        mock_cursor.fetchone.return_value = None
        self.assertFalse(self.model.check_user_exist("new_user"))

    @patch('src.Model.TaiKhoanModel.mysql.connector.connect')
    def test_create_account_for_existing_transaction(self, mock_connect):
        """Test Model tạo tài khoản và liên kết (Transaction)"""
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value

        data = {'user': 'test', 'pass': 'hash123'}

        result = self.model.create_account_for_existing(10, data)

        self.assertTrue(result)
        mock_conn.start_transaction.assert_called_once()
        mock_conn.commit.assert_called_once()

        # Kiểm tra Insert và Update
        calls = mock_cursor.execute.call_args_list
        self.assertIn("INSERT INTO taiKhoanNhanVien", calls[0][0][0])
        self.assertIn("UPDATE nhanVien", calls[1][0][0])


if __name__ == '__main__':
    unittest.main()