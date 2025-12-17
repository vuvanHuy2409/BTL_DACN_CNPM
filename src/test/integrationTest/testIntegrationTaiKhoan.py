import unittest
import mysql.connector
import os
import sys
import hashlib

# ==============================================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN (Để Python tìm thấy thư mục src)
# ==============================================================================
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.Controller.TaiKhoanController import TaiKhoanController
from src.config.db_config import DB_CONFIG


class TestTaiKhoanIntegration(unittest.TestCase):
    """
    KIỂM THỬ TÍCH HỢP: QUẢN LÝ TÀI KHOẢN (CẤP QUYỀN)
    """

    # Dữ liệu Test
    TEST_USER = "test_acc_user"
    TEST_PASS = "123456"
    TEST_EMAIL = "acc_test@gmail.com"

    def setUp(self):
        """CHẠY TRƯỚC MỖI TEST: Tạo dữ liệu (Chức vụ, Nhân viên chưa có TK)"""
        self.conn = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor(dictionary=True)
        self.controller = TaiKhoanController()

        self.cleanup_db()

        # 1. Tạo Chức vụ (Logic Get or Create để tránh lỗi Duplicate)
        self.cursor.execute("SELECT idChucVu FROM chucVu WHERE tenChucVu = 'TestRole'")
        res_cv = self.cursor.fetchone()
        if res_cv:
            self.id_cv = res_cv['idChucVu']
        else:
            self.cursor.execute("INSERT INTO chucVu (tenChucVu, luongCoBan) VALUES ('TestRole', 1000)")
            self.id_cv = self.cursor.lastrowid

        # 2. Tạo Nhân viên (Ban đầu CHƯA CÓ tài khoản - idTaiKhoan NULL)
        # Xóa nhân viên cũ nếu còn sót
        self.cursor.execute("DELETE FROM nhanVien WHERE email = %s", (self.TEST_EMAIL,))

        self.cursor.execute("""
            INSERT INTO nhanVien (hoTen, email, soDienThoai, idChucVu, idTaiKhoan, trangThaiLamViec) 
            VALUES ('Account Test Staff', %s, '0000', %s, NULL, 'DangLamViec')
        """, (self.TEST_EMAIL, self.id_cv))
        self.id_nv = self.cursor.lastrowid

        self.conn.commit()

    def tearDown(self):
        """CHẠY SAU MỖI TEST: Dọn dẹp"""
        self.cleanup_db()
        if self.conn.is_connected():
            self.cursor.close()
            self.conn.close()

    def cleanup_db(self):
        """Xóa dữ liệu test sạch sẽ"""
        try:
            # 1. Lấy ID tài khoản của nhân viên test (nếu đã được cấp)
            id_tk = None
            if hasattr(self, 'id_nv'):
                self.cursor.execute("SELECT idTaiKhoan FROM nhanVien WHERE idNhanVien = %s", (self.id_nv,))
                res = self.cursor.fetchone()
                if res and res['idTaiKhoan']:
                    id_tk = res['idTaiKhoan']

            # 2. Xóa Nhân viên trước (để gỡ khóa ngoại FK)
            if hasattr(self, 'id_nv'):
                self.cursor.execute("DELETE FROM nhanVien WHERE idNhanVien = %s", (self.id_nv,))
            else:
                self.cursor.execute("DELETE FROM nhanVien WHERE email = %s", (self.TEST_EMAIL,))

            # 3. Xóa Tài khoản
            if id_tk:
                self.cursor.execute("DELETE FROM taiKhoanNhanVien WHERE idTaiKhoan = %s", (id_tk,))

            # Xóa vét theo tên đăng nhập (đề phòng test search tạo thêm user khác)
            self.cursor.execute("DELETE FROM taiKhoanNhanVien WHERE tenDangNhap LIKE 'unique_search%'")
            self.cursor.execute("DELETE FROM taiKhoanNhanVien WHERE tenDangNhap = %s", (self.TEST_USER,))

            self.conn.commit()
        except Exception:
            pass

    # ==========================================================================
    # CÁC TEST CASE
    # ==========================================================================

    def test_create_account_success(self):
        """Test 1: Cấp tài khoản mới cho nhân viên"""

        # Gọi Controller tạo tài khoản
        success, msg = self.controller.save_account(
            id_nhan_vien=self.id_nv,
            has_account=False,
            name="Account Test Staff",
            username=self.TEST_USER,
            password=self.TEST_PASS,
            email=self.TEST_EMAIL,
            role_text="TestRole"
        )

        self.assertTrue(success, f"Tạo tài khoản thất bại: {msg}")

        # [QUAN TRỌNG] Commit để Test nhìn thấy dữ liệu mới (Refresh Snapshot)
        self.conn.commit()

        # Verify DB
        # 1. Kiểm tra bảng nhanVien đã được update idTaiKhoan chưa
        self.cursor.execute("SELECT idTaiKhoan FROM nhanVien WHERE idNhanVien = %s", (self.id_nv,))
        res_nv = self.cursor.fetchone()
        self.assertIsNotNone(res_nv['idTaiKhoan'], "Cột idTaiKhoan trong bảng nhanVien vẫn là NULL")
        new_tk_id = res_nv['idTaiKhoan']

        # 2. Kiểm tra bảng taiKhoanNhanVien đã có dòng mới chưa
        self.cursor.execute("SELECT * FROM taiKhoanNhanVien WHERE idTaiKhoan = %s", (new_tk_id,))
        res_tk = self.cursor.fetchone()
        self.assertEqual(res_tk['tenDangNhap'], self.TEST_USER)

        # 3. Kiểm tra Hash mật khẩu
        expected_hash = hashlib.md5(self.TEST_PASS.encode()).hexdigest()
        self.assertEqual(res_tk['matKhauHash'], expected_hash)

    def test_update_password(self):
        """Test 2: Cập nhật mật khẩu cho tài khoản đã có"""
        # B1: Tạo tài khoản trước
        self.controller.save_account(self.id_nv, False, "Name", self.TEST_USER, "oldpass", self.TEST_EMAIL, "Role")

        # B2: Cập nhật mật khẩu mới
        new_pass = "newpassword123"
        success, msg = self.controller.save_account(
            id_nhan_vien=self.id_nv,
            has_account=True,  # Flag True nghĩa là update
            name="Account Test Staff",
            username=self.TEST_USER,
            password=new_pass,
            email=self.TEST_EMAIL,
            role_text="TestRole"
        )
        self.assertTrue(success)

        # [QUAN TRỌNG] Commit để refresh dữ liệu
        self.conn.commit()

        # B3: Verify DB Hash mới
        self.cursor.execute("SELECT matKhauHash FROM taiKhoanNhanVien WHERE tenDangNhap = %s", (self.TEST_USER,))
        row = self.cursor.fetchone()

        current_hash = row['matKhauHash']
        expected_hash = hashlib.md5(new_pass.encode()).hexdigest()

        self.assertEqual(current_hash, expected_hash, "Mật khẩu trong DB chưa được cập nhật!")

    def test_delete_account_only(self):
        """Test 3: Xóa tài khoản (Gỡ quyền truy cập) nhưng giữ nhân viên"""
        # B1: Tạo tài khoản
        self.controller.save_account(self.id_nv, False, "Name", self.TEST_USER, self.TEST_PASS, self.TEST_EMAIL, "Role")

        # B2: Lấy ID tài khoản để kiểm tra sau này
        self.cursor.execute("SELECT idTaiKhoan FROM nhanVien WHERE idNhanVien = %s", (self.id_nv,))
        tk_id = self.cursor.fetchone()['idTaiKhoan']
        self.assertIsNotNone(tk_id)

        # B3: Xóa tài khoản
        success, msg = self.controller.delete_account_only(self.id_nv)
        self.assertTrue(success)

        # [QUAN TRỌNG] Commit connection test để refresh snapshot dữ liệu
        # Nếu thiếu dòng này, Test vẫn nhìn thấy idTaiKhoan cũ
        self.conn.commit()

        # B4: Verify DB
        # - Trong bảng nhanVien: idTaiKhoan phải về NULL
        self.cursor.execute("SELECT idTaiKhoan FROM nhanVien WHERE idNhanVien = %s", (self.id_nv,))
        res = self.cursor.fetchone()
        self.assertIsNone(res['idTaiKhoan'], "idTaiKhoan trong bảng nhanVien chưa về NULL")

        # - Trong bảng taiKhoanNhanVien: Dòng đó phải biến mất
        self.cursor.execute("SELECT * FROM taiKhoanNhanVien WHERE idTaiKhoan = %s", (tk_id,))
        self.assertIsNone(self.cursor.fetchone(), "Dòng trong bảng taiKhoanNhanVien chưa bị xóa")

    def test_search_account(self):
        """Test 4: Tìm kiếm tài khoản theo Username"""
        # Tạo tài khoản với tên đặc biệt
        search_user = "unique_search_user"
        self.controller.save_account(self.id_nv, False, "Name", search_user, "pass", "email", "Role")

        # Commit để đảm bảo dữ liệu đã vào DB trước khi search
        self.conn.commit()

        # Tìm kiếm
        results = self.controller.tim_kiem_tai_khoan("unique_search")

        self.assertGreater(len(results), 0)

        # Kiểm tra xem có đúng user vừa tạo không
        found = False
        for r in results:
            if r['tenDangNhap'] == search_user:
                found = True
                break
        self.assertTrue(found, "Không tìm thấy user vừa tạo trong kết quả tìm kiếm")


if __name__ == '__main__':
    unittest.main()