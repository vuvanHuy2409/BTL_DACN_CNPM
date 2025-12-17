import unittest
import mysql.connector
import os
import sys

# ==============================================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN
# ==============================================================================
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.Controller.NganHangController import NganHangController
from src.config.db_config import DB_CONFIG


class TestNganHangIntegration(unittest.TestCase):
    """
    KIỂM THỬ TÍCH HỢP: QUẢN LÝ NGÂN HÀNG
    """

    # Dữ liệu Test
    TEST_CODE = "TEST_BANK_MB"
    TEST_NAME = "MB Bank Test"
    TEST_ACC_NUM = "999988887777"
    TEST_OWNER = "NGUYEN VAN TEST"

    def setUp(self):
        """CHẠY TRƯỚC MỖI TEST"""
        self.conn = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor(dictionary=True)
        self.controller = NganHangController()

        self.cleanup_db()

    def tearDown(self):
        """CHẠY SAU MỖI TEST"""
        self.cleanup_db()
        if self.conn.is_connected():
            self.cursor.close()
            self.conn.close()

    def cleanup_db(self):
        """Xóa dữ liệu test sạch sẽ"""
        try:
            # Xóa các ngân hàng được tạo ra trong quá trình test
            self.cursor.execute("DELETE FROM nganHang WHERE maNganHang = %s", (self.TEST_CODE,))
            self.cursor.execute("DELETE FROM nganHang WHERE soTaiKhoan = %s", (self.TEST_ACC_NUM,))
            self.cursor.execute("DELETE FROM nganHang WHERE tenTaiKhoan = 'UPDATED OWNER'")

            self.conn.commit()
        except Exception:
            pass

    # ==========================================================================
    # TEST CASES
    # ==========================================================================

    def test_add_bank_success(self):
        """Test 1: Thêm ngân hàng thành công"""

        success, msg = self.controller.them_ngan_hang(
            self.TEST_CODE, self.TEST_NAME, self.TEST_ACC_NUM, self.TEST_OWNER
        )
        self.assertTrue(success, f"Thêm thất bại: {msg}")

        # [FIX] Commit để thấy dữ liệu mới
        self.conn.commit()

        # Verify DB
        self.cursor.execute("SELECT * FROM nganHang WHERE maNganHang = %s AND soTaiKhoan = %s",
                            (self.TEST_CODE, self.TEST_ACC_NUM))
        bank = self.cursor.fetchone()

        self.assertIsNotNone(bank)
        self.assertEqual(bank['tenNganHang'], self.TEST_NAME)
        self.assertEqual(bank['tenTaiKhoan'], self.TEST_OWNER)
        self.assertEqual(bank['isActive'], 1)  # Mặc định phải là 1

    def test_add_duplicate_prevention(self):
        """Test 2: Chặn trùng lặp (Mã NH + Số TK)"""

        # 1. Thêm lần đầu (Thành công)
        self.controller.them_ngan_hang(self.TEST_CODE, self.TEST_NAME, self.TEST_ACC_NUM, self.TEST_OWNER)

        # [FIX] Commit để DB lưu lại
        self.conn.commit()

        # 2. Thêm lần hai (Trùng khớp hoàn toàn) -> Phải thất bại
        success, msg = self.controller.them_ngan_hang(self.TEST_CODE, "Another Name", self.TEST_ACC_NUM,
                                                      "Another Owner")

        self.assertFalse(success)
        # Kiểm tra thông báo lỗi có chứa thông tin trùng lặp
        self.assertIn("đã tồn tại", msg)

    def test_update_bank_info(self):
        """Test 3: Cập nhật thông tin ngân hàng"""

        # 1. Setup
        self.controller.them_ngan_hang(self.TEST_CODE, self.TEST_NAME, self.TEST_ACC_NUM, self.TEST_OWNER)
        self.conn.commit()

        self.cursor.execute("SELECT idNganHang FROM nganHang WHERE soTaiKhoan = %s", (self.TEST_ACC_NUM,))
        id_nh = self.cursor.fetchone()['idNganHang']

        # 2. Update
        new_owner = "UPDATED OWNER"
        success, msg = self.controller.sua_ngan_hang(id_nh, self.TEST_CODE, self.TEST_NAME, self.TEST_ACC_NUM,
                                                     new_owner)
        self.assertTrue(success)

        # [FIX] Refresh
        self.conn.commit()

        # 3. Verify
        self.cursor.execute("SELECT tenTaiKhoan FROM nganHang WHERE idNganHang = %s", (id_nh,))
        updated = self.cursor.fetchone()
        self.assertEqual(updated['tenTaiKhoan'], new_owner)

    def test_toggle_status(self):
        """Test 4: Ẩn / Hiện ngân hàng"""

        # 1. Setup (Mặc định isActive = 1)
        self.controller.them_ngan_hang(self.TEST_CODE, self.TEST_NAME, self.TEST_ACC_NUM, self.TEST_OWNER)
        self.conn.commit()

        self.cursor.execute("SELECT idNganHang, isActive FROM nganHang WHERE soTaiKhoan = %s", (self.TEST_ACC_NUM,))
        row = self.cursor.fetchone()
        id_nh = row['idNganHang']
        self.assertEqual(row['isActive'], 1)

        # 2. Toggle lần 1 -> Thành 0 (Ẩn)
        success, msg = self.controller.doi_trang_thai(id_nh)
        self.assertTrue(success)
        self.conn.commit()  # Refresh

        self.cursor.execute("SELECT isActive FROM nganHang WHERE idNganHang = %s", (id_nh,))
        self.assertEqual(self.cursor.fetchone()['isActive'], 0)

        # 3. Toggle lần 2 -> Thành 1 (Hiện)
        self.controller.doi_trang_thai(id_nh)
        self.conn.commit()  # Refresh

        self.cursor.execute("SELECT isActive FROM nganHang WHERE idNganHang = %s", (id_nh,))
        self.assertEqual(self.cursor.fetchone()['isActive'], 1)

    def test_search_bank(self):
        """Test 5: Tìm kiếm theo số tài khoản"""
        self.controller.them_ngan_hang(self.TEST_CODE, self.TEST_NAME, self.TEST_ACC_NUM, self.TEST_OWNER)
        self.conn.commit()

        # Tìm kiếm bằng 1 phần số tài khoản
        partial_acc = self.TEST_ACC_NUM[:5]  # "99998"
        results = self.controller.tim_kiem_ngan_hang(partial_acc)

        self.assertGreater(len(results), 0)
        found = False
        for r in results:
            if r['soTaiKhoan'] == self.TEST_ACC_NUM:
                found = True
                break
        self.assertTrue(found, "Không tìm thấy ngân hàng vừa tạo")


if __name__ == '__main__':
    unittest.main()