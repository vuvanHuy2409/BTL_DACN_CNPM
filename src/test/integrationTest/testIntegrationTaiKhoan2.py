import unittest
import mysql.connector
import os
import sys
import hashlib

# ==============================================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN
# ==============================================================================
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.Controller.TaiKhoan2Controller import TaiKhoan2Controller
from src.config.db_config import DB_CONFIG


class TestTaiKhoan2Integration(unittest.TestCase):
    """
    KIỂM THỬ TÍCH HỢP: THÔNG TIN CÁ NHÂN & ĐỔI MẬT KHẨU
    """

    # Dữ liệu Test
    TEST_USER = "profile_test_user"
    TEST_PASS_OLD = "old_password_123"
    TEST_PASS_NEW = "new_password_456"
    TEST_EMAIL = "profile@test.com"
    TEST_NAME = "Nguyen Van Profile"

    def setUp(self):
        """CHẠY TRƯỚC MỖI TEST: Tạo bộ dữ liệu (Chức vụ -> TK -> NV)"""
        self.conn = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor(dictionary=True)
        self.controller = TaiKhoan2Controller()

        self.cleanup_db()

        # 1. Tạo Chức vụ (Get or Create)
        self.cursor.execute("SELECT idChucVu FROM chucVu WHERE tenChucVu = 'TestRole'")
        res_cv = self.cursor.fetchone()
        if res_cv:
            self.id_cv = res_cv['idChucVu']
        else:
            self.cursor.execute("INSERT INTO chucVu (tenChucVu, luongCoBan) VALUES ('TestRole', 1000)")
            self.id_cv = self.cursor.lastrowid

        # 2. Tạo Tài khoản (Với mật khẩu cũ đã Hash)
        old_hash = hashlib.md5(self.TEST_PASS_OLD.encode()).hexdigest()
        self.cursor.execute("""
            INSERT INTO taiKhoanNhanVien (tenDangNhap, matKhauHash, trangThai) 
            VALUES (%s, %s, 1)
        """, (self.TEST_USER, old_hash))
        self.id_tk = self.cursor.lastrowid

        # 3. Tạo Nhân viên (Liên kết với TK và CV)
        self.cursor.execute("""
            INSERT INTO nhanVien (hoTen, email, soDienThoai, idChucVu, idTaiKhoan, trangThaiLamViec) 
            VALUES (%s, %s, '0909123456', %s, %s, 'DangLamViec')
        """, (self.TEST_NAME, self.TEST_EMAIL, self.id_cv, self.id_tk))
        self.id_nv = self.cursor.lastrowid

        self.conn.commit()

    def tearDown(self):
        """CHẠY SAU MỖI TEST"""
        try:
            # Cố gắng rollback nếu có transaction đang treo
            if self.conn.is_connected():
                self.conn.rollback()
        except:
            pass

        self.cleanup_db()

        if self.conn.is_connected():
            self.cursor.close()
            self.conn.close()

    def cleanup_db(self):
        try:
            # Xóa theo thứ tự FK: NV -> TK -> CV
            if hasattr(self, 'id_nv'):
                self.cursor.execute("DELETE FROM nhanVien WHERE idNhanVien = %s", (self.id_nv,))
            else:
                self.cursor.execute("DELETE FROM nhanVien WHERE email = %s", (self.TEST_EMAIL,))

            if hasattr(self, 'id_tk'):
                self.cursor.execute("DELETE FROM taiKhoanNhanVien WHERE idTaiKhoan = %s", (self.id_tk,))

            # Xóa vét theo tên đăng nhập
            self.cursor.execute("DELETE FROM taiKhoanNhanVien WHERE tenDangNhap = %s", (self.TEST_USER,))

            self.conn.commit()
        except mysql.connector.Error as e:
            # Nếu gặp lỗi Lock wait ở đây, thử rollback rồi xóa lại
            print(f"Cleanup Error: {e}")
            try:
                self.conn.rollback()
            except:
                pass

    # ==========================================================================
    # TEST CASES
    # ==========================================================================

    def test_get_employee_info(self):
        """Test 1: Lấy thông tin cá nhân (Kiểm tra JOIN bảng)"""

        info = self.controller.get_info(self.id_nv)

        self.assertIsNotNone(info)
        # Kiểm tra thông tin từ bảng nhanVien
        self.assertEqual(info['hoTen'], self.TEST_NAME)
        self.assertEqual(info['email'], self.TEST_EMAIL)

        # Kiểm tra thông tin từ bảng chucVu
        self.assertEqual(info['tenChucVu'], 'TestRole')

        # Kiểm tra thông tin từ bảng taiKhoanNhanVien
        self.assertEqual(info['tenDangNhap'], self.TEST_USER)

    def test_update_personal_info(self):
        """Test 2: Cập nhật thông tin (Họ tên, SĐT, Email)"""

        new_name = "Updated Profile Name"
        new_phone = "0888999000"
        new_email = "updated_profile@test.com"

        success, msg = self.controller.save_info(self.id_nv, new_name, new_phone, new_email)
        self.assertTrue(success, f"Update lỗi: {msg}")

        # [FIX] Commit để refresh dữ liệu
        self.conn.commit()

        # Verify DB
        self.cursor.execute("SELECT hoTen, soDienThoai, email FROM nhanVien WHERE idNhanVien = %s", (self.id_nv,))
        updated = self.cursor.fetchone()

        self.assertEqual(updated['hoTen'], new_name)
        self.assertEqual(updated['soDienThoai'], new_phone)
        self.assertEqual(updated['email'], new_email)

    def test_change_password_success(self):
        """Test 3: Đổi mật khẩu thành công (Đúng pass cũ)"""

        success, msg = self.controller.change_password(
            id_tai_khoan=self.id_tk,
            old_pass=self.TEST_PASS_OLD,
            new_pass=self.TEST_PASS_NEW,
            confirm_pass=self.TEST_PASS_NEW
        )
        self.assertTrue(success, f"Đổi pass thất bại: {msg}")

        # [FIX] Commit
        self.conn.commit()

        # Verify DB
        self.cursor.execute("SELECT matKhauHash FROM taiKhoanNhanVien WHERE idTaiKhoan = %s", (self.id_tk,))
        current_hash = self.cursor.fetchone()['matKhauHash']

        expected_hash = hashlib.md5(self.TEST_PASS_NEW.encode()).hexdigest()
        self.assertEqual(current_hash, expected_hash, "Hash mật khẩu trong DB chưa đổi")

    def test_change_password_fail_wrong_old(self):
        """Test 4: Đổi mật khẩu thất bại do sai pass cũ"""

        success, msg = self.controller.change_password(
            id_tai_khoan=self.id_tk,
            old_pass="WRONG_PASSWORD",
            new_pass=self.TEST_PASS_NEW,
            confirm_pass=self.TEST_PASS_NEW
        )

        self.assertFalse(success)
        self.assertEqual(msg, "Mật khẩu cũ không chính xác!")

    def test_change_password_fail_mismatch(self):
        """Test 5: Đổi mật khẩu thất bại do xác nhận không khớp"""

        success, msg = self.controller.change_password(
            id_tai_khoan=self.id_tk,
            old_pass=self.TEST_PASS_OLD,
            new_pass=self.TEST_PASS_NEW,
            confirm_pass="MISMATCH_PASS"
        )

        self.assertFalse(success)
        self.assertEqual(msg, "Mật khẩu xác nhận không khớp!")


if __name__ == '__main__':
    unittest.main()