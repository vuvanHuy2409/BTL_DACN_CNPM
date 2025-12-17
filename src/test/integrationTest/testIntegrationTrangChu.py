import unittest
import mysql.connector
import os
import sys
import shutil

# ==============================================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN
# ==============================================================================
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.Controller.TrangChuController import TrangChuController
from src.config.db_config import DB_CONFIG


class TestTrangChuIntegration(unittest.TestCase):
    """
    KIỂM THỬ TÍCH HỢP: TRANG CHỦ (BÁN HÀNG)
    """

    # Hằng số dữ liệu Test
    TEST_TABLE_ID = 999
    TEST_PROD_PRICE = 50000.0  # Float để tránh lỗi Decimal
    VAT_RATE = 1.1
    TEST_PHONE_NV = '0000'
    TEST_EMAIL_NV = 'test@staff.com'

    def setUp(self):
        """CHẠY TRƯỚC MỖI TEST: Tạo dữ liệu giả lập an toàn"""
        self.conn = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor(dictionary=True)
        self.controller = TrangChuController()

        if not os.path.exists(self.controller.invoice_dir):
            os.makedirs(self.controller.invoice_dir)

        self.cleanup_test_data()

        # 1. TẠO BÀN ĂN
        try:
            self.cursor.execute(
                "INSERT INTO banAn (idBan, tenBan, trangThai, isActive) VALUES (%s, 'Bàn Test 999', 'Trong', 1)",
                (self.TEST_TABLE_ID,))
        except:
            try:
                self.cursor.execute(
                    "INSERT INTO banAn (idBanAn, tenBan, trangThai, isActive) VALUES (%s, 'Bàn Test 999', 'Trong', 1)",
                    (self.TEST_TABLE_ID,))
            except:
                pass

            # 2. CHỨC VỤ
        self.cursor.execute("SELECT idChucVu FROM chucVu WHERE tenChucVu = 'TestRole'")
        res_cv = self.cursor.fetchone()
        if res_cv:
            self.id_chuc_vu = res_cv['idChucVu']
        else:
            self.cursor.execute("INSERT INTO chucVu (tenChucVu, luongCoBan) VALUES ('TestRole', 1000)")
            self.id_chuc_vu = self.cursor.lastrowid

        # 3. NHÂN VIÊN
        self.cursor.execute("""
            INSERT INTO nhanVien (hoTen, email, soDienThoai, idChucVu, trangThaiLamViec)
            VALUES ('Staff Test', %s, %s, %s, 'DangLamViec')
        """, (self.TEST_EMAIL_NV, self.TEST_PHONE_NV, self.id_chuc_vu,))
        self.id_nv = self.cursor.lastrowid

        # 4. DANH MỤC
        self.cursor.execute("SELECT idDanhMuc FROM danhMuc WHERE tenDanhMuc = 'Test Category'")
        res_dm = self.cursor.fetchone()
        if res_dm:
            self.id_danh_muc = res_dm['idDanhMuc']
        else:
            self.cursor.execute("INSERT INTO danhMuc (tenDanhMuc) VALUES ('Test Category')")
            self.id_danh_muc = self.cursor.lastrowid

        # 5. TẠO NGUYÊN LIỆU & TỒN KHO
        self.cursor.execute("SELECT idNhaCungCap FROM nhaCungCap WHERE tenNhaCungCap = 'NCC Test'")
        res_ncc = self.cursor.fetchone()
        if res_ncc:
            self.id_ncc = res_ncc['idNhaCungCap']
        else:
            self.cursor.execute("INSERT INTO nhaCungCap (tenNhaCungCap, isActive) VALUES ('NCC Test', 1)")
            self.id_ncc = self.cursor.lastrowid

        self.cursor.execute("""
            INSERT INTO khoNguyenLieu (tenNguyenLieu, giaNhap, soLuongTon, donViTinh, idNhaCungCap, isActive) 
            VALUES ('NL Cafe Test', 100, 5000, 'kg', %s, 1)
        """, (self.id_ncc,))
        self.id_nl = self.cursor.lastrowid

        # 6. SẢN PHẨM
        self.cursor.execute("""
            INSERT INTO sanPham (tenSanPham, giaBan, idDanhMuc, idNguyenLieu, isActive)
            VALUES ('Cafe Test', %s, %s, %s, 1)
        """, (self.TEST_PROD_PRICE, self.id_danh_muc, self.id_nl))
        self.id_sp = self.cursor.lastrowid
        self.conn.commit()

        # [FIX] CHUẨN HÓA DỮ LIỆU SẢN PHẨM TEST
        # Lấy row từ DB
        self.cursor.execute("SELECT * FROM sanPham WHERE idSanPham = %s", (self.id_sp,))
        row = self.cursor.fetchone()

        # Tạo dictionary thủ công để đảm bảo kiểu dữ liệu chuẩn (float/int) thay vì Decimal
        self.test_product = {
            'idSanPham': row['idSanPham'],
            'tenSanPham': row['tenSanPham'],
            'giaBan': float(row['giaBan']),  # Chuyển Decimal -> float
            'donGia': float(row['giaBan']),  # Alias cho giaBan (phòng trường hợp Controller dùng key này)
            'price': float(row['giaBan']),  # Alias khác
            'idNguyenLieu': row['idNguyenLieu'],
            'soLuongTon': 5000,
            'tenDonViTinh': 'kg'
        }

        # 7. NGÂN HÀNG
        self.cursor.execute("SELECT idNganHang FROM nganHang WHERE maNganHang = 'TESTBANK'")
        res_nh = self.cursor.fetchone()
        if res_nh:
            self.id_ngan_hang = res_nh['idNganHang']
        else:
            self.cursor.execute("""
                INSERT INTO nganHang (maNganHang, tenNganHang, soTaiKhoan, isActive)
                VALUES ('TESTBANK', 'Test Bank', '1111', 1)
            """)
            self.id_ngan_hang = self.cursor.lastrowid

        self.test_bank_info = {'idNganHang': self.id_ngan_hang, 'maNganHang': 'TESTBANK', 'soTaiKhoan': '1111',
                               'tenTaiKhoan': 'Test'}

        # 8. KHÁCH HÀNG
        self.cursor.execute("""
            INSERT INTO khachHang (hoTen, soDienThoai, diemTichLuy)
            VALUES ('Customer Test', '0999999999', 0)
        """)
        self.id_kh = self.cursor.lastrowid

        self.conn.commit()
        self.generated_files = []

    def tearDown(self):
        self.cleanup_test_data()
        for f in self.generated_files:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass
        if self.conn.is_connected():
            self.cursor.close()
            self.conn.close()

    def cleanup_test_data(self):
        try:
            if hasattr(self, 'id_sp'):
                self.cursor.execute("DELETE FROM chiTietHoaDon WHERE idSanPham = %s", (self.id_sp,))
            self.cursor.execute("DELETE FROM hoaDon WHERE idBan = %s", (self.TEST_TABLE_ID,))

            if hasattr(self, 'id_nv'): self.cursor.execute("DELETE FROM nhanVien WHERE idNhanVien = %s", (self.id_nv,))
            self.cursor.execute("DELETE FROM nhanVien WHERE email = %s", (self.TEST_EMAIL_NV,))
            self.cursor.execute("DELETE FROM nhanVien WHERE soDienThoai = %s", (self.TEST_PHONE_NV,))

            if hasattr(self, 'id_kh'): self.cursor.execute("DELETE FROM khachHang WHERE idKhachHang = %s",
                                                           (self.id_kh,))
            self.cursor.execute("DELETE FROM khachHang WHERE soDienThoai = '0999999999'")

            if hasattr(self, 'id_sp'): self.cursor.execute("DELETE FROM sanPham WHERE idSanPham = %s", (self.id_sp,))
            self.cursor.execute("DELETE FROM sanPham WHERE tenSanPham = 'Cafe Test'")

            if hasattr(self, 'id_nl'): self.cursor.execute(
                "DELETE FROM khoNguyenLieu WHERE tenNguyenLieu = 'NL Cafe Test'")

            try:
                self.cursor.execute("DELETE FROM banAn WHERE idBan = %s", (self.TEST_TABLE_ID,))
            except:
                self.cursor.execute("DELETE FROM banAn WHERE idBanAn = %s", (self.TEST_TABLE_ID,))

            self.conn.commit()
        except Exception as e:
            pass

    # ==========================================================================
    # TEST CASES
    # ==========================================================================

    def test_full_process_cash_payment(self):
        """Test: Chọn bàn -> Thêm món -> Tính tiền -> Thanh toán tiền mặt -> PDF"""

        # 1. Chọn bàn
        self.controller.select_table(self.TEST_TABLE_ID)

        # 2. Thêm món
        res1 = self.controller.add_to_cart(self.test_product, self.id_nv)
        if res1 is False or (isinstance(res1, tuple) and not res1[0]):
            self.fail(f"Lỗi: Không thể thêm món 1")

        res2 = self.controller.add_to_cart(self.test_product, self.id_nv)
        if res2 is False:
            self.fail("Lỗi: Không thể thêm món 2")

        # 3. Tính toán
        _, _, final_total, _, _ = self.controller.calculate_cart_totals()

        # Tính thêm 10% VAT
        expected_total = self.TEST_PROD_PRICE * 2 * self.VAT_RATE

        # 4. Kiểm tra tổng tiền

        # 5. Thanh toán
        success, msg = self.controller.process_payment(method="TienMat", id_nv=self.id_nv)
        self.assertTrue(success, f"Thanh toán thất bại: {msg}")

        if "File: " in msg:
            pdf_path = msg.split("File: ")[1].strip()
            self.generated_files.append(pdf_path)

        # 6. Verify DB
        self.cursor.execute("SELECT * FROM hoaDon WHERE idBan = %s ORDER BY idHoaDon DESC LIMIT 1",
                            (self.TEST_TABLE_ID,))
        invoice = self.cursor.fetchone()

        self.assertIsNotNone(invoice, "Hóa đơn phải được tạo trong DB")
        self.assertEqual(invoice['trangThai'], 2, "Trạng thái hóa đơn phải là 2 (Đã thanh toán)")
        self.assertAlmostEqual(float(invoice['tongTien']), expected_total, delta=1.0)
        self.assertTrue(os.path.exists(pdf_path), "File PDF hóa đơn phải được tạo ra")

    def test_loyalty_points_flow(self):
        """Test: Khách VIP -> Giảm giá -> Trừ điểm -> Cộng điểm mới"""
        self.cursor.execute("UPDATE khachHang SET diemTichLuy = 250 WHERE idKhachHang = %s", (self.id_kh,))
        self.conn.commit()

        self.controller.select_table(self.TEST_TABLE_ID)
        self.controller.add_to_cart(self.test_product, self.id_nv)
        self.controller.find_and_assign_customer('0999999999', self.id_nv)

        _, subtotal, discount, final_total, is_applied = self.controller.calculate_cart_totals()
        self.assertTrue(is_applied, "Khách VIP phải được áp dụng giảm giá")

        expected_discount = (self.TEST_PROD_PRICE * self.VAT_RATE) * 0.1
        self.assertAlmostEqual(discount, expected_discount, delta=1.0)

        success, msg = self.controller.process_payment(method="TienMat", id_nv=self.id_nv)
        self.assertTrue(success)

        self.cursor.execute("SELECT diemTichLuy FROM khachHang WHERE idKhachHang = %s", (self.id_kh,))
        new_points = self.cursor.fetchone()['diemTichLuy']

        self.assertGreater(new_points, 0)

        if "File: " in msg: self.generated_files.append(msg.split("File: ")[1].strip())

    def test_bank_transfer_payment(self):
        """Test: Thanh toán CK -> Lưu nội dung CK"""
        self.controller.select_table(self.TEST_TABLE_ID)
        self.controller.add_to_cart(self.test_product, self.id_nv)

        ck_content = "TEST_CK_CODE_123"

        success, msg = self.controller.process_payment(
            method="ChuyenKhoan",
            id_nv=self.id_nv,
            bank_info=self.test_bank_info,
            noi_dung_ck=ck_content
        )
        self.assertTrue(success)

        self.cursor.execute("SELECT idHoaDon, noiDungCK FROM hoaDon WHERE idBan = %s ORDER BY idHoaDon DESC LIMIT 1",
                            (self.TEST_TABLE_ID,))
        invoice = self.cursor.fetchone()
        self.assertEqual(invoice['noiDungCK'], ck_content)

        if "File: " in msg: self.generated_files.append(msg.split("File: ")[1].strip())


if __name__ == '__main__':
    unittest.main()