import unittest
from unittest.mock import patch, MagicMock, ANY
import sys
import os
import hashlib

# --- CẤU HÌNH ĐƯỜNG DẪN ---
# Để Python tìm thấy thư mục 'src'
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../..'))
sys.path.insert(0, project_root)
# ---------------------------

# Import các class cần test
from src.Model.QuenMKModel import QuenMKModel
from src.Controller.QuenMKController import QuenMKController


class TestQuenMKModel(unittest.TestCase):
    """Kiểm tra phần Model (Tương tác Database)"""

    def setUp(self):
        self.model = QuenMKModel()

    @patch('src.Model.QuenMKModel.mysql.connector.connect')
    def test_check_user_email_found(self, mock_connect):
        """Test tìm thấy user và email hợp lệ"""
        # 1. Giả lập kết nối và cursor
        mock_cursor = mock_connect.return_value.cursor.return_value

        # 2. Giả lập DB trả về kết quả (idTaiKhoan = 5)
        mock_cursor.fetchone.return_value = {'idTaiKhoan': 5}

        # 3. Chạy hàm
        result = self.model.check_user_email("user_test", "test@gmail.com")

        # 4. Kiểm tra
        self.assertEqual(result, 5)
        # Kiểm tra xem query có đúng tham số không
        query_args = mock_cursor.execute.call_args[0][1]
        self.assertEqual(query_args, ("user_test", "test@gmail.com"))

    @patch('src.Model.QuenMKModel.mysql.connector.connect')
    def test_check_user_email_not_found(self, mock_connect):
        """Test không tìm thấy user"""
        mock_cursor = mock_connect.return_value.cursor.return_value
        mock_cursor.fetchone.return_value = None  # DB trả về rỗng

        result = self.model.check_user_email("user_ao", "email_ao")
        self.assertIsNone(result)

    @patch('src.Model.QuenMKModel.mysql.connector.connect')
    def test_reset_password_success(self, mock_connect):
        """Test cập nhật mật khẩu thành công"""
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value

        result = self.model.reset_password(5, "new_hash_pass")

        self.assertTrue(result)
        # Kiểm tra xem có commit transaction không
        mock_conn.commit.assert_called_once()


class TestQuenMKController(unittest.TestCase):
    """Kiểm tra phần Controller (Logic nghiệp vụ & Email)"""

    def setUp(self):
        self.controller = QuenMKController()
        # MOCK MODEL: Thay vì dùng Model thật (kết nối DB), ta dùng bản giả
        self.controller.model = MagicMock()

    # --- Test 1: Gửi mã xác nhận ---

    # Patch hàm send_email_otp để không gửi email thật khi test logic gui_ma_xac_nhan
    @patch('src.Controller.QuenMKController.QuenMKController.send_email_otp')
    def test_gui_ma_xac_nhan_thanh_cong(self, mock_send_email):
        # Setup: Giả lập Model tìm thấy User ID = 10
        self.controller.model.check_user_email.return_value = 10
        mock_send_email.return_value = True

        # Act
        success, message = self.controller.gui_ma_xac_nhan("huy", "huy@gmail.com")

        # Assert
        self.assertTrue(success)
        self.assertEqual(message, "Mã xác nhận đã được gửi đến Email của bạn!")
        self.assertIsNotNone(self.controller.current_otp)  # OTP phải được sinh ra
        self.assertEqual(self.controller.current_id_tk, 10)  # ID phải được lưu session

    def test_gui_ma_xac_nhan_sai_thong_tin(self):
        # Setup: Giả lập Model KHÔNG tìm thấy user
        self.controller.model.check_user_email.return_value = None

        # Act
        success, message = self.controller.gui_ma_xac_nhan("sai", "sai@gmail.com")

        # Assert
        self.assertFalse(success)
        self.assertIn("không tồn tại", message)

    # --- Test 2: Chức năng Gửi Email (Mock SMTP) ---
    @patch('smtplib.SMTP_SSL')  # Chặn thư viện SMTP
    def test_send_email_otp_function(self, mock_smtp):
        # Setup: Giả lập server SMTP đăng nhập thành công
        server_instance = mock_smtp.return_value

        # Act
        result = self.controller.send_email_otp("khach@gmail.com", "123456")

        # Assert
        self.assertTrue(result)
        # Kiểm tra xem code có gọi hàm login không
        server_instance.login.assert_called_with("huyberrrrr@gmail.com", "jsjebyuxxmewcyzv")
        # Kiểm tra xem code có gửi thư không
        server_instance.send_message.assert_called()
        # Kiểm tra xem code có thoát (quit) server không
        server_instance.quit.assert_called()

    # --- Test 3: Xác thực OTP ---
    def test_xac_thuc_otp_dung(self):
        self.controller.current_otp = "123456"  # Giả lập session đang có mã này

        success, msg = self.controller.xac_thuc_otp("123456")
        self.assertTrue(success)

    def test_xac_thuc_otp_sai(self):
        self.controller.current_otp = "123456"

        success, msg = self.controller.xac_thuc_otp("999999")  # Nhập sai
        self.assertFalse(success)
        self.assertEqual(msg, "Mã xác nhận không đúng!")

    def test_xac_thuc_otp_khi_chua_gui(self):
        self.controller.current_otp = None  # Chưa gửi mã

        success, msg = self.controller.xac_thuc_otp("123456")
        self.assertFalse(success)
        self.assertIn("Hết phiên làm việc", msg)

    # --- Test 4: Lưu mật khẩu mới ---
    def test_luu_mat_khau_moi_thanh_cong(self):
        # Setup session
        self.controller.current_id_tk = 10
        # Giả lập Model update thành công
        self.controller.model.reset_password.return_value = True

        # Act
        success, msg = self.controller.luu_mat_khau_moi("123456", "123456")

        # Assert
        self.assertTrue(success)
        self.assertIsNone(self.controller.current_id_tk)  # Phải xóa session sau khi đổi
        self.assertIsNone(self.controller.current_otp)

    def test_luu_mat_khau_moi_ngan(self):
        self.controller.current_id_tk = 10
        success, msg = self.controller.luu_mat_khau_moi("123", "123")
        self.assertFalse(success)
        self.assertIn("6 ký tự", msg)

    def test_luu_mat_khau_khong_khop(self):
        self.controller.current_id_tk = 10
        success, msg = self.controller.luu_mat_khau_moi("123456", "654321")
        self.assertFalse(success)
        self.assertIn("không khớp", msg)


if __name__ == '__main__':
    unittest.main()