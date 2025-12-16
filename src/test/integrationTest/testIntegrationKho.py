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

from src.Controller.KhoController import KhoController
from src.config.db_config import DB_CONFIG


class TestKhoIntegration(unittest.TestCase):
    """
    KIỂM THỬ TÍCH HỢP: QUẢN LÝ KHO NGUYÊN LIỆU
    """

    # Hằng số dữ liệu Test
    TEST_NL_NAME = "Test Ingredient Auto"
    TEST_DVT = "kg"

    def setUp(self):
        """CHẠY TRƯỚC MỖI TEST: Tạo dữ liệu phụ thuộc (NCC, Nhân viên)"""
        self.conn = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor(dictionary=True)
        self.controller = KhoController()

        # Dọn dẹp trước
        self.cleanup_test_data()

        # 1. Tạo Nhà Cung Cấp mẫu (Vì bảng khoNguyenLieu cần idNhaCungCap)
        self.cursor.execute(
            "INSERT INTO nhaCungCap (tenNhaCungCap, soDienThoai, isActive) VALUES ('Test Supplier', '0000', 1)")
        self.id_ncc = self.cursor.lastrowid

        # 2. Tạo Nhân viên mẫu (Để có người nhập kho)
        # Cần tạo chức vụ trước nếu chưa có
        self.cursor.execute("SELECT idChucVu FROM chucVu LIMIT 1")
        res_cv = self.cursor.fetchone()
        if res_cv:
            self.id_chuc_vu = res_cv['idChucVu']
        else:
            self.cursor.execute("INSERT INTO chucVu (tenChucVu, luongCoBan) VALUES ('TestRole', 1000)")
            self.id_chuc_vu = self.cursor.lastrowid

        self.cursor.execute("""
            INSERT INTO nhanVien (hoTen, email, soDienThoai, idChucVu, trangThaiLamViec)
            VALUES ('Staff Kho Test', 'kho@test.com', '111', %s, 'DangLamViec')
        """, (self.id_chuc_vu,))
        self.id_nv = self.cursor.lastrowid

        self.conn.commit()

    def tearDown(self):
        """CHẠY SAU MỖI TEST"""
        self.cleanup_test_data()
        if self.conn.is_connected():
            self.cursor.close()
            self.conn.close()

    def cleanup_test_data(self):
        """Xóa dữ liệu test theo thứ tự khóa ngoại"""
        try:
            # Xóa nguyên liệu test trước
            self.cursor.execute("DELETE FROM khoNguyenLieu WHERE tenNguyenLieu LIKE 'Test Ingredient%'")

            # Xóa dữ liệu phụ thuộc
            if hasattr(self, 'id_ncc'): self.cursor.execute("DELETE FROM nhaCungCap WHERE idNhaCungCap = %s",
                                                            (self.id_ncc,))
            if hasattr(self, 'id_nv'): self.cursor.execute("DELETE FROM nhanVien WHERE idNhanVien = %s", (self.id_nv,))

            self.conn.commit()
        except Exception as e:
            print(f"Cleanup Error: {e}")

    # ==========================================================================
    # TEST CASES
    # ==========================================================================

    def test_add_nguyen_lieu_auto_active(self):
        """Test 1: Thêm mới với số lượng > 0 -> Tự động Active (1)"""
        # Thêm với số lượng 100
        success, msg = self.controller.add_nguyen_lieu(
            self.TEST_NL_NAME, 50000, 100, self.TEST_DVT, self.id_ncc, self.id_nv
        )
        self.assertTrue(success, f"Thêm thất bại: {msg}")

        # Verify DB
        self.cursor.execute("SELECT * FROM khoNguyenLieu WHERE tenNguyenLieu = %s", (self.TEST_NL_NAME,))
        item = self.cursor.fetchone()

        self.assertIsNotNone(item)
        self.assertEqual(item['soLuongTon'], 100)
        self.assertEqual(item['isActive'], 1, "Số lượng > 0 thì trạng thái phải là 1")

    def test_add_nguyen_lieu_auto_hide(self):
        """Test 2: Thêm mới với số lượng = 0 -> Tự động Ẩn (0)"""
        name_zero = "Test Ingredient Zero"

        # Thêm với số lượng 0
        success, msg = self.controller.add_nguyen_lieu(
            name_zero, 50000, 0, self.TEST_DVT, self.id_ncc, self.id_nv
        )
        self.assertTrue(success)

        # Verify DB
        self.cursor.execute("SELECT isActive FROM khoNguyenLieu WHERE tenNguyenLieu = %s", (name_zero,))
        item = self.cursor.fetchone()

        self.assertEqual(item['isActive'], 0, "Số lượng = 0 thì trạng thái phải là 0")

    def test_update_logic_auto_status(self):
        """Test 3: Cập nhật số lượng -> Trạng thái tự động thay đổi"""
        # Bước 1: Tạo nguyên liệu đang có hàng (SL: 50 -> Active: 1)
        self.controller.add_nguyen_lieu(self.TEST_NL_NAME, 50000, 50, self.TEST_DVT, self.id_ncc, self.id_nv)

        self.cursor.execute("SELECT idNguyenLieu FROM khoNguyenLieu WHERE tenNguyenLieu = %s", (self.TEST_NL_NAME,))
        id_nl = self.cursor.fetchone()['idNguyenLieu']

        # Bước 2: Cập nhật về 0 -> Kiểm tra xem có tự Ẩn không
        self.controller.update_nguyen_lieu(id_nl, self.TEST_NL_NAME, 50000, 0, self.TEST_DVT, self.id_ncc)
        self.conn.commit()  # Quan trọng: commit để test connection thấy thay đổi

        self.cursor.execute("SELECT isActive FROM khoNguyenLieu WHERE idNguyenLieu = %s", (id_nl,))
        status_step_2 = self.cursor.fetchone()['isActive']
        self.assertEqual(status_step_2, 0, "Cập nhật SL về 0 -> Phải tự động Ẩn")

        # Bước 3: Cập nhật lên 100 -> Kiểm tra xem có tự Hiện không
        self.controller.update_nguyen_lieu(id_nl, self.TEST_NL_NAME, 50000, 100, self.TEST_DVT, self.id_ncc)
        self.conn.commit()

        self.cursor.execute("SELECT isActive FROM khoNguyenLieu WHERE idNguyenLieu = %s", (id_nl,))
        status_step_3 = self.cursor.fetchone()['isActive']
        self.assertEqual(status_step_3, 1, "Cập nhật SL > 0 -> Phải tự động Hiện")

    def test_duplicate_check(self):
        """Test 4: Chặn trùng tên nguyên liệu"""
        # Thêm lần 1
        self.controller.add_nguyen_lieu(self.TEST_NL_NAME, 50000, 10, self.TEST_DVT, self.id_ncc, self.id_nv)

        # Thêm lần 2 (Cố tình trùng tên)
        success, msg = self.controller.add_nguyen_lieu(self.TEST_NL_NAME, 99999, 5, "chai", self.id_ncc, self.id_nv)

        self.assertFalse(success)
        self.assertEqual(msg, "Tên nguyên liệu đã tồn tại!")

    def test_validation_input(self):
        """Test 5: Nhập chữ vào ô Giá/Số lượng"""
        success, msg = self.controller.add_nguyen_lieu(
            "Wrong Input Item", "Năm mươi nghìn", "Mười cái", self.TEST_DVT, self.id_ncc, self.id_nv
        )

        self.assertFalse(success)
        self.assertIn("phải là số", msg)


if __name__ == '__main__':
    unittest.main()