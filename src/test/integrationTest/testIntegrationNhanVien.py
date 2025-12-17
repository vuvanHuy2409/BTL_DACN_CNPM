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

from src.Controller.NhanVienController import NhanVienController
from src.config.db_config import DB_CONFIG


class TestNhanVienIntegration(unittest.TestCase):
    """
    KIỂM THỬ TÍCH HỢP: QUẢN LÝ NHÂN VIÊN & CHỨC VỤ
    """

    # Dữ liệu Test
    TEST_ROLE_NAME = "Integration Test Role"
    TEST_NV_NAME = "Nhan Vien Test"
    TEST_EMAIL = "test_nv@gmail.com"
    TEST_PHONE = "0999888777"

    # [FIX] Đổi "staff" thành "admin" để khớp với ENUM trong Database
    VALID_ROLE_ENUM = "admin"

    def setUp(self):
        """CHẠY TRƯỚC MỖI TEST: Tạo dữ liệu nền"""
        self.conn = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor(dictionary=True)
        self.controller = NhanVienController()

        self.cleanup_db()

        # [FIX] Tạo Chức vụ nền tảng cho các test nhân viên (Get or Create)
        self.cursor.execute("SELECT idChucVu FROM chucVu WHERE tenChucVu = %s", (self.TEST_ROLE_NAME,))
        res = self.cursor.fetchone()
        if res:
            self.id_cv_setup = res['idChucVu']
        else:
            self.cursor.execute("INSERT INTO chucVu (tenChucVu, luongCoBan) VALUES (%s, 5000)", (self.TEST_ROLE_NAME,))
            self.id_cv_setup = self.cursor.lastrowid

        self.conn.commit()

    def tearDown(self):
        """CHẠY SAU MỖI TEST"""
        self.cleanup_db()
        if self.conn.is_connected():
            self.cursor.close()
            self.conn.close()

    def cleanup_db(self):
        """Xóa dữ liệu test sạch sẽ"""
        try:
            # 1. Xóa Nhân viên test
            self.cursor.execute("DELETE FROM nhanVien WHERE email = %s", (self.TEST_EMAIL,))
            self.cursor.execute("DELETE FROM nhanVien WHERE email = 'updated_email@gmail.com'")
            self.cursor.execute("DELETE FROM nhanVien WHERE email = 'invalid_email.com'")

            # 2. Xóa Chức vụ test
            # (Lưu ý: Chỉ xóa các chức vụ test cụ thể, không xóa lung tung)
            # Do ràng buộc khóa ngoại, phải xóa NV trước rồi mới xóa Chức vụ được
            self.cursor.execute("DELETE FROM chucVu WHERE tenChucVu = %s", (self.TEST_ROLE_NAME,))
            self.cursor.execute("DELETE FROM chucVu WHERE tenChucVu = 'Lifecycle Role Name'")
            self.cursor.execute("DELETE FROM chucVu WHERE tenChucVu = 'Updated Lifecycle Role'")

            self.conn.commit()
        except Exception as e:
            # print(f"Cleanup warning: {e}")
            pass

    # ==========================================================================
    # TEST CASES: QUẢN LÝ CHỨC VỤ
    # ==========================================================================

    def test_chuc_vu_lifecycle(self):
        """Test 1: Thêm và Sửa Chức vụ (Độc lập với setup)"""
        role_name = "Lifecycle Role Name"

        # A. THÊM CHỨC VỤ
        success, msg = self.controller.them_chuc_vu(role_name, 5000)
        self.assertTrue(success, f"Thêm chức vụ lỗi: {msg}")

        self.conn.commit()

        # Verify DB
        self.cursor.execute("SELECT idChucVu, luongCoBan FROM chucVu WHERE tenChucVu = %s", (role_name,))
        role = self.cursor.fetchone()
        self.assertIsNotNone(role)
        self.assertEqual(float(role['luongCoBan']), 5000.0)
        id_cv = role['idChucVu']

        # B. SỬA CHỨC VỤ
        new_name = "Updated Lifecycle Role"
        new_salary = 10000
        success, msg = self.controller.sua_chuc_vu(id_cv, new_name, new_salary)
        self.assertTrue(success)

        self.conn.commit()

        # Verify DB Update
        self.cursor.execute("SELECT tenChucVu, luongCoBan FROM chucVu WHERE idChucVu = %s", (id_cv,))
        updated_role = self.cursor.fetchone()
        self.assertEqual(updated_role['tenChucVu'], new_name)
        self.assertEqual(float(updated_role['luongCoBan']), 10000.0)

    # ==========================================================================
    # TEST CASES: QUẢN LÝ NHÂN VIÊN
    # ==========================================================================

    def test_add_nhan_vien_success(self):
        """Test 2: Thêm nhân viên thành công"""

        # Sử dụng id_cv_setup đã tạo ở setUp
        success, msg = self.controller.add_nhan_vien(
            ten=self.TEST_NV_NAME,
            email=self.TEST_EMAIL,
            sdt=self.TEST_PHONE,
            phan_quyen=self.VALID_ROLE_ENUM,  # [FIX] Dùng 'admin' thay vì 'staff'
            id_chuc_vu=self.id_cv_setup
        )
        self.assertTrue(success, f"Thêm NV thất bại: {msg}")

        self.conn.commit()

        # Verify DB
        self.cursor.execute("SELECT * FROM nhanVien WHERE email = %s", (self.TEST_EMAIL,))
        nv = self.cursor.fetchone()

        self.assertIsNotNone(nv, "Không tìm thấy nhân viên trong DB sau khi thêm")
        self.assertEqual(nv['hoTen'], self.TEST_NV_NAME)
        self.assertEqual(nv['idChucVu'], self.id_cv_setup)

    def test_nhan_vien_validation(self):
        """Test 3: Validate Email sai và Trùng lặp"""

        # 1. Test Email sai định dạng (thiếu @)
        success, msg = self.controller.add_nhan_vien(
            "Name", "invalid_email.com", "000", self.VALID_ROLE_ENUM, self.id_cv_setup
        )
        self.assertFalse(success)
        self.assertEqual(msg, "Email không hợp lệ!")

        # 2. Test Trùng Email/SĐT
        # Thêm lần 1 (OK)
        self.controller.add_nhan_vien("User 1", self.TEST_EMAIL, self.TEST_PHONE, self.VALID_ROLE_ENUM,
                                      self.id_cv_setup)
        self.conn.commit()  # Quan trọng: Commit để lần insert sau thấy được dữ liệu trùng

        # Thêm lần 2 (Trùng Email) -> Phải Fail
        success, msg = self.controller.add_nhan_vien("User 2", self.TEST_EMAIL, "0999111222", self.VALID_ROLE_ENUM,
                                                     self.id_cv_setup)
        self.assertFalse(success)
        self.assertEqual(msg, "Email hoặc SĐT đã tồn tại!")

    def test_update_and_toggle_status(self):
        """Test 4: Cập nhật thông tin và Đổi trạng thái"""

        # 1. Setup Data: Thêm 1 nhân viên
        self.controller.add_nhan_vien(self.TEST_NV_NAME, self.TEST_EMAIL, self.TEST_PHONE, self.VALID_ROLE_ENUM,
                                      self.id_cv_setup)
        self.conn.commit()

        self.cursor.execute("SELECT idNhanVien, trangThaiLamViec FROM nhanVien WHERE email = %s", (self.TEST_EMAIL,))
        res = self.cursor.fetchone()

        # [FIX] Kiểm tra res tồn tại trước khi truy cập
        self.assertIsNotNone(res, "Setup dữ liệu thất bại: Không tạo được nhân viên để update")

        id_nv = res['idNhanVien']
        status_goc = res['trangThaiLamViec']

        # 2. Update Thông tin
        new_email = "updated_email@gmail.com"
        success, msg = self.controller.update_nhan_vien(id_nv, "New Name", new_email, self.TEST_PHONE,
                                                        self.VALID_ROLE_ENUM, self.id_cv_setup)
        self.assertTrue(success, f"Update lỗi: {msg}")

        self.conn.commit()

        # Verify Update
        self.cursor.execute("SELECT hoTen, email FROM nhanVien WHERE idNhanVien = %s", (id_nv,))
        updated_nv = self.cursor.fetchone()
        self.assertEqual(updated_nv['email'], new_email)
        self.assertEqual(updated_nv['hoTen'], "New Name")

        # 3. Toggle Status (Đổi trạng thái)
        success, msg = self.controller.doi_trang_thai(id_nv)
        self.assertTrue(success)

        self.conn.commit()

        # Verify Status Changed
        self.cursor.execute("SELECT trangThaiLamViec FROM nhanVien WHERE idNhanVien = %s", (id_nv,))
        new_status = self.cursor.fetchone()['trangThaiLamViec']

        self.assertNotEqual(new_status, status_goc, "Trạng thái chưa thay đổi")


if __name__ == '__main__':
    unittest.main()