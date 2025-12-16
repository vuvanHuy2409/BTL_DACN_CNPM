import unittest
import mysql.connector
import hashlib
import sys
import os

# ==============================================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN (Để Python tìm thấy thư mục src)
# ==============================================================================
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import Controller và Config
try:
    from src.Controller.DangNhapController import DangNhapController
    from src.config.db_config import DB_CONFIG
except ImportError as e:
    raise ImportError(f"Lỗi Import: {e}. Hãy đảm bảo cấu trúc dự án đúng.")


class TestDangNhapIntegration(unittest.TestCase):
    """
    KIỂM THỬ TÍCH HỢP: ĐĂNG NHẬP
    Kết nối DB thật -> Tạo dữ liệu -> Test -> Xóa dữ liệu.
    """

    # Hằng số dữ liệu test
    TEST_USER = "test_integration_user"
    TEST_PASS = "Test@123"
    TEST_EMAIL = "test_integration@cafe.com"

    def setUp(self):
        """CHẠY TRƯỚC MỖI TEST CASE: Tạo dữ liệu mẫu trong DB thật"""
        self.conn = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor()
        self.controller = DangNhapController()

        # 1. Dọn dẹp dữ liệu cũ (tránh lỗi Duplicate)
        self.cleanup_test_data()

        # 2. Đảm bảo có ít nhất 1 chức vụ (để thỏa mãn khóa ngoại)
        self.cursor.execute("SELECT idChucVu FROM chucVu LIMIT 1")
        res = self.cursor.fetchone()
        if res:
            self.id_chuc_vu = res[0]
        else:
            self.cursor.execute("INSERT INTO chucVu (tenChucVu, luongCoBan) VALUES ('TestRole', 100000)")
            self.id_chuc_vu = self.cursor.lastrowid

        # 3. Tạo Tài Khoản (Bảng taiKhoanNhanVien)
        # QUAN TRỌNG: Phải Hash MD5 mật khẩu trước khi Insert thì Controller mới so khớp được
        pass_hash = hashlib.md5(self.TEST_PASS.encode()).hexdigest()

        sql_tk = "INSERT INTO taiKhoanNhanVien (tenDangNhap, matKhauHash, trangThai) VALUES (%s, %s, 1)"
        self.cursor.execute(sql_tk, (self.TEST_USER, pass_hash))
        self.id_tk = self.cursor.lastrowid

        # 4. Tạo Nhân Viên (Bảng nhanVien)
        # QUAN TRỌNG:
        # - phanQuyen='admin' (để test role)
        # - trangThaiLamViec='DangLamViec' (Controller chỉ cho phép trạng thái này đăng nhập)
        sql_nv = """
            INSERT INTO nhanVien 
            (hoTen, email, soDienThoai, idChucVu, idTaiKhoan, phanQuyen, trangThaiLamViec)
            VALUES (%s, %s, %s, %s, %s, 'admin', 'DangLamViec')
        """
        self.cursor.execute(sql_nv, ("Integration User", self.TEST_EMAIL, "0000000000", self.id_chuc_vu, self.id_tk))

        self.conn.commit()

    def tearDown(self):
        """CHẠY SAU MỖI TEST CASE: Xóa dữ liệu rác"""
        self.cleanup_test_data()
        if self.conn.is_connected():
            self.cursor.close()
            self.conn.close()

    def cleanup_test_data(self):
        """Hàm phụ trợ xóa dữ liệu test"""
        try:
            # Xóa nhân viên trước (Khóa ngoại)
            self.cursor.execute("SELECT idNhanVien, idTaiKhoan FROM nhanVien WHERE email = %s", (self.TEST_EMAIL,))
            row = self.cursor.fetchone()

            if row:
                id_nv, id_tk = row
                self.cursor.execute("DELETE FROM nhanVien WHERE idNhanVien = %s", (id_nv,))
                # Sau đó xóa tài khoản
                if id_tk:
                    self.cursor.execute("DELETE FROM taiKhoanNhanVien WHERE idTaiKhoan = %s", (id_tk,))

            # Xóa vét tài khoản nếu chưa gắn nhân viên
            self.cursor.execute("DELETE FROM taiKhoanNhanVien WHERE tenDangNhap = %s", (self.TEST_USER,))
            self.conn.commit()
        except Exception as e:
            print(f"Lỗi dọn dẹp: {e}")

    # ==========================================================================
    # CÁC TEST CASE
    # ==========================================================================

    def test_integration_login_success(self):
        """Test 1: Đăng nhập thành công (Đúng User, Đúng Pass, Đang làm việc)"""
        # Gọi hàm chính xác trong Controller
        result = self.controller.xu_ly_dang_nhap(self.TEST_USER, self.TEST_PASS)

        # Kiểm tra status
        self.assertTrue(result['status'], f"Lỗi đăng nhập: {result.get('message')}")
        self.assertEqual(result['message'], "Đăng nhập thành công")

        # Kiểm tra dữ liệu trả về
        data = result['data']
        # Kiểm tra key 'ho_ten' (đã sửa khớp với controller)
        self.assertEqual(data['ho_ten'], "Integration User")
        self.assertEqual(data['role_name'], "admin")
        self.assertIsNotNone(data['id_nhan_vien'])

    def test_integration_login_wrong_password(self):
        """Test 2: Sai mật khẩu"""
        result = self.controller.xu_ly_dang_nhap(self.TEST_USER, "MatKhauSai123")

        self.assertFalse(result['status'])
        self.assertEqual(result['message'], "Sai tên đăng nhập hoặc mật khẩu!")

    def test_integration_login_wrong_username(self):
        """Test 3: Sai tên đăng nhập"""
        result = self.controller.xu_ly_dang_nhap("UserAoMa", "123")

        self.assertFalse(result['status'])
        self.assertEqual(result['message'], "Sai tên đăng nhập hoặc mật khẩu!")

    def test_integration_sql_injection(self):
        """Test 4: Thử tấn công SQL Injection"""
        # Payload: admin' OR '1'='1
        payload = f"{self.TEST_USER}' OR '1'='1"
        result = self.controller.xu_ly_dang_nhap(payload, "pass_bat_ky")

        self.assertFalse(result['status'], "Hệ thống phải chặn được SQL Injection")


if __name__ == '__main__':
    unittest.main()