import unittest
import mysql.connector
import os
import sys
from datetime import date

# ==============================================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN
# ==============================================================================
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.Controller.KhachHangController import KhachHangController
from src.config.db_config import DB_CONFIG


class TestKhachHangIntegration(unittest.TestCase):
    """
    KIỂM THỬ TÍCH HỢP: QUẢN LÝ KHÁCH HÀNG
    """

    # Dữ liệu test
    TEST_PHONE = "0999888777"
    TEST_NAME = "Integration Customer"
    TEST_DOB_INPUT = "01/01/2000"  # Định dạng đầu vào dd/mm/yyyy
    TEST_DOB_DB = date(2000, 1, 1)  # Định dạng mong đợi từ DB (yyyy-mm-dd)

    def setUp(self):
        """CHẠY TRƯỚC MỖI TEST CASE"""
        self.conn = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor(dictionary=True)
        self.controller = KhachHangController()

        # Dọn dẹp dữ liệu cũ để môi trường sạch sẽ
        self.cleanup_test_data()

    def tearDown(self):
        """CHẠY SAU MỖI TEST CASE"""
        self.cleanup_test_data()
        if self.conn.is_connected():
            self.cursor.close()
            self.conn.close()

    def cleanup_test_data(self):
        """Xóa khách hàng test dựa trên số điện thoại"""
        try:
            # Lưu ý: Nếu khách hàng này đã có hóa đơn, cần xóa hóa đơn trước (nếu có ràng buộc FK)
            # Tuy nhiên ở đây ta giả định khách hàng mới tạo chưa mua hàng
            self.cursor.execute("DELETE FROM khachHang WHERE soDienThoai = %s", (self.TEST_PHONE,))
            self.conn.commit()
        except Exception as e:
            print(f"Cleanup Error: {e}")

    # ==========================================================================
    # TEST CASES
    # ==========================================================================

    def test_add_customer_success(self):
        """Test 1: Thêm khách hàng thành công (Happy Path)"""
        success, msg = self.controller.them_khach_hang(self.TEST_NAME, self.TEST_PHONE, self.TEST_DOB_INPUT)

        self.assertTrue(success, f"Thêm thất bại: {msg}")
        self.assertEqual(msg, "Thêm khách hàng thành công!")

        # Verify DB
        self.cursor.execute("SELECT * FROM khachHang WHERE soDienThoai = %s", (self.TEST_PHONE,))
        cust = self.cursor.fetchone()

        self.assertIsNotNone(cust)
        self.assertEqual(cust['hoTen'], self.TEST_NAME)
        self.assertEqual(cust['ngaySinh'], self.TEST_DOB_DB)
        self.assertEqual(cust['diemTichLuy'], 0)

    def test_add_customer_duplicate_phone(self):
        """Test 2: Chặn trùng số điện thoại"""
        # Bước 1: Thêm lần đầu -> Thành công
        self.controller.them_khach_hang(self.TEST_NAME, self.TEST_PHONE, self.TEST_DOB_INPUT)

        # Bước 2: Thêm lần hai với cùng SĐT -> Phải thất bại
        success, msg = self.controller.them_khach_hang("Name Duplicate", self.TEST_PHONE, "02/02/2000")

        self.assertFalse(success)
        self.assertEqual(msg, "Số điện thoại này đã tồn tại!")

    def test_add_customer_invalid_date(self):
        """Test 3: Validate ngày sinh sai định dạng"""
        # Ngày 31/02 không tồn tại
        success, msg = self.controller.them_khach_hang(self.TEST_NAME, "0123456789", "31/02/2023")

        self.assertFalse(success)
        self.assertEqual(msg, "Ngày sinh không hợp lệ!")

    def test_update_customer_info(self):
        """Test 4: Cập nhật thông tin và điểm tích lũy"""
        # 1. Tạo khách hàng trước
        self.controller.them_khach_hang(self.TEST_NAME, self.TEST_PHONE, self.TEST_DOB_INPUT)

        # Lấy ID vừa tạo
        self.cursor.execute("SELECT idKhachHang FROM khachHang WHERE soDienThoai = %s", (self.TEST_PHONE,))
        cust_id = self.cursor.fetchone()['idKhachHang']

        # 2. Thực hiện cập nhật (Controller sẽ dùng kết nối riêng để update)
        new_name = "Updated Name"
        new_dob_str = "15/05/1995"
        new_dob_db = date(1995, 5, 15)
        new_points = 500

        success, msg = self.controller.sua_khach_hang(cust_id, new_name, self.TEST_PHONE, new_dob_str, new_points)

        self.assertTrue(success, f"Cập nhật thất bại: {msg}")

        # [FIX QUAN TRỌNG]: Commit kết nối của Test để làm mới dữ liệu (Refresh Snapshot)
        # Nếu không có dòng này, MySQL sẽ trả về dữ liệu cũ do cơ chế Repeatable Read
        self.conn.commit()

        # 3. Verify DB
        self.cursor.execute("SELECT * FROM khachHang WHERE idKhachHang = %s", (cust_id,))
        updated_cust = self.cursor.fetchone()

        self.assertEqual(updated_cust['hoTen'], new_name)
        self.assertEqual(updated_cust['diemTichLuy'], 500)
        self.assertEqual(updated_cust['ngaySinh'], new_dob_db)

    def test_search_customer(self):
        """Test 5: Tìm kiếm khách hàng"""
        self.controller.them_khach_hang(self.TEST_NAME, self.TEST_PHONE, self.TEST_DOB_INPUT)

        # Tìm theo SĐT
        results = self.controller.tim_kiem_khach_hang(self.TEST_PHONE)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]['hoTen'], self.TEST_NAME)

        # Tìm theo Tên (Gần đúng)
        results_name = self.controller.tim_kiem_khach_hang("Integration")
        self.assertGreater(len(results_name), 0)


if __name__ == '__main__':
    unittest.main()