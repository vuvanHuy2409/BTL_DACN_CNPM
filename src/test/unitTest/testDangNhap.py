import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# --- CẤU HÌNH ĐƯỜNG DẪN (QUAN TRỌNG) ---
# Đoạn này giúp Python tìm thấy thư mục gốc 'src' dù file test nằm sâu bên trong.
# Chúng ta lấy đường dẫn hiện tại, đi ngược lên 3 cấp để về thư mục gốc dự án.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../..'))
sys.path.insert(0, project_root)
# ---------------------------------------

# Bây giờ mới import được Controller từ src
from src.Controller.DangNhapController import DangNhapController
import mysql.connector
import hashlib


class TestDangNhapController(unittest.TestCase):

    def setUp(self):
        """Khởi tạo đối tượng trước mỗi bài test"""
        self.controller = DangNhapController()

    # --- TEST 1: Kiểm tra hàm băm mật khẩu ---
    def test_hash_password(self):
        password = "123"
        # Mã MD5 chuẩn của "123"
        expected_hash = hashlib.md5(password.encode()).hexdigest()

        result = self.controller.hash_password(password)

        self.assertEqual(result, expected_hash, "Hàm băm mật khẩu hoạt động sai")

    # --- TEST 2: Đăng nhập thành công (Mock DB) ---
    @patch('src.Controller.DangNhapController.mysql.connector.connect')
    # Lưu ý: Patch đường dẫn phải trỏ tới nơi module được SỬ DỤNG (trong DangNhapController)
    def test_dang_nhap_thanh_cong(self, mock_connect):
        # 1. SETUP GIẢ LẬP
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Giả lập dữ liệu trả về từ DB khớp với câu SQL của bạn
        fake_user_data = {
            'idNhanVien': 10,
            'hoTen': 'Tran Van A',
            'phanQuyen': 'admin'  # Giả lập quyền admin
        }
        mock_cursor.fetchone.return_value = fake_user_data

        # 2. ACT (Chạy hàm)
        result = self.controller.xu_ly_dang_nhap("admin", "123")

        # 3. ASSERT (Kiểm tra)
        self.assertTrue(result['status'])
        self.assertEqual(result['message'], "Đăng nhập thành công")
        self.assertEqual(result['data']['role_name'], 'admin')  # Kiểm tra xem có lấy đúng quyền không

    # --- TEST 3: Đăng nhập thất bại (Sai user/pass) ---
    @patch('src.Controller.DangNhapController.mysql.connector.connect')
    def test_dang_nhap_that_bai(self, mock_connect):
        # 1. SETUP
        mock_cursor = mock_connect.return_value.cursor.return_value
        # Giả lập DB trả về None (không tìm thấy user)
        mock_cursor.fetchone.return_value = None

        # 2. ACT
        result = self.controller.xu_ly_dang_nhap("user_khong_ton_tai", "123")

        # 3. ASSERT
        self.assertFalse(result['status'])
        self.assertEqual(result['message'], "Sai tên đăng nhập hoặc mật khẩu!")

    # --- TEST 4: Lỗi kết nối Database ---
    @patch('src.Controller.DangNhapController.mysql.connector.connect')
    def test_loi_ket_noi_db(self, mock_connect):
        # 1. SETUP: Giả lập hàm connect bị lỗi
        mock_connect.side_effect = mysql.connector.Error("Lỗi mạng")

        # 2. ACT
        result = self.controller.xu_ly_dang_nhap("admin", "123")

        # 3. ASSERT
        self.assertFalse(result['status'])
        self.assertIn("Lỗi kết nối CSDL", result['message'])


if __name__ == '__main__':
    unittest.main()