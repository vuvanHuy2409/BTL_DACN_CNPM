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
    TEST_TABLE_ID = 999  # Giả lập bàn số 999
    TEST_PROD_PRICE = 50000
    VAT_RATE = 1.1  # 10% VAT -> Nhân 1.1

    def setUp(self):
        """CHẠY TRƯỚC MỖI TEST: Tạo dữ liệu giả lập an toàn"""
        self.conn = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor(dictionary=True)
        self.controller = TrangChuController()

        # Đảm bảo thư mục hóa đơn tồn tại
        if not os.path.exists(self.controller.invoice_dir):
            os.makedirs(self.controller.invoice_dir)

        # 1. Xử lý CHỨC VỤ
        self.cursor.execute("SELECT idChucVu FROM chucVu WHERE tenChucVu = 'TestRole'")
        res_cv = self.cursor.fetchone()
        if res_cv:
            self.id_chuc_vu = res_cv['idChucVu']
        else:
            self.cursor.execute("INSERT INTO chucVu (tenChucVu, luongCoBan) VALUES ('TestRole', 1000)")
            self.id_chuc_vu = self.cursor.lastrowid

        # 2. Xử lý NHÂN VIÊN
        self.cursor.execute("DELETE FROM nhanVien WHERE email = 'test@staff.com'")
        self.cursor.execute("""
            INSERT INTO nhanVien (hoTen, email, soDienThoai, idChucVu, trangThaiLamViec)
            VALUES ('Staff Test', 'test@staff.com', '0000', %s, 'DangLamViec')
        """, (self.id_chuc_vu,))
        self.id_nv = self.cursor.lastrowid

        # 3. Xử lý DANH MỤC
        self.cursor.execute("SELECT idDanhMuc FROM danhMuc WHERE tenDanhMuc = 'Test Category'")
        res_dm = self.cursor.fetchone()
        if res_dm:
            self.id_danh_muc = res_dm['idDanhMuc']
        else:
            self.cursor.execute("INSERT INTO danhMuc (tenDanhMuc) VALUES ('Test Category')")
            self.id_danh_muc = self.cursor.lastrowid

        # 4. Xử lý SẢN PHẨM
        self.cursor.execute("DELETE FROM sanPham WHERE tenSanPham = 'Cafe Test'")
        self.cursor.execute("""
            INSERT INTO sanPham (tenSanPham, giaBan, idDanhMuc, isActive)
            VALUES ('Cafe Test', %s, %s, 1)
        """, (self.TEST_PROD_PRICE, self.id_danh_muc))
        self.id_sp = self.cursor.lastrowid

        self.test_product = {
            'idSanPham': self.id_sp,
            'tenSanPham': 'Cafe Test',
            'giaBan': self.TEST_PROD_PRICE
        }

        # 5. Xử lý NGÂN HÀNG
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

        # 6. Xử lý KHÁCH HÀNG
        self.cursor.execute("DELETE FROM khachHang WHERE soDienThoai = '0999999999'")
        self.cursor.execute("""
            INSERT INTO khachHang (hoTen, soDienThoai, diemTichLuy)
            VALUES ('Customer Test', '0999999999', 0)
        """)
        self.id_kh = self.cursor.lastrowid

        # Dọn dẹp hóa đơn cũ
        self.cursor.execute("DELETE FROM hoaDon WHERE idBan = %s", (self.TEST_TABLE_ID,))
        self.conn.commit()

        self.generated_files = []

    def tearDown(self):
        """CHẠY SAU MỖI TEST: Xóa dữ liệu & File rác"""
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
            if hasattr(self, 'id_kh'): self.cursor.execute("DELETE FROM khachHang WHERE idKhachHang = %s",
                                                           (self.id_kh,))
            if hasattr(self, 'id_sp'): self.cursor.execute("DELETE FROM sanPham WHERE idSanPham = %s", (self.id_sp,))
            self.conn.commit()
        except Exception as e:
            print(f"Cleanup Error: {e}")

    # ==========================================================================
    # TEST CASES
    # ==========================================================================

    def test_full_process_cash_payment(self):
        """Test: Chọn bàn -> Thêm món -> Tính tiền -> Thanh toán tiền mặt -> PDF"""
        self.controller.select_table(self.TEST_TABLE_ID)
        self.controller.add_to_cart(self.test_product, self.id_nv)
        self.controller.add_to_cart(self.test_product, self.id_nv)

        _, _, final_total, _, _ = self.controller.calculate_cart_totals()

        # [SỬA] Tính thêm 10% VAT
        expected_total = self.TEST_PROD_PRICE * 2 * self.VAT_RATE

        # Dùng assertAlmostEqual để tránh lỗi làm tròn số thực (float)
        self.assertAlmostEqual(final_total, expected_total, delta=1.0, msg="Tổng tiền trên RAM phải đúng (bao gồm VAT)")

        success, msg = self.controller.process_payment(method="TienMat", id_nv=self.id_nv)
        self.assertTrue(success, f"Thanh toán thất bại: {msg}")

        if "File: " in msg:
            pdf_path = msg.split("File: ")[1].strip()
            self.generated_files.append(pdf_path)

        self.cursor.execute("SELECT * FROM hoaDon WHERE idBan = %s ORDER BY idHoaDon DESC LIMIT 1",
                            (self.TEST_TABLE_ID,))
        invoice = self.cursor.fetchone()

        self.assertIsNotNone(invoice, "Hóa đơn phải được tạo trong DB")
        self.assertEqual(invoice['trangThai'], 2, "Trạng thái hóa đơn phải là 2 (Đã thanh toán)")
        self.assertAlmostEqual(float(invoice['tongTien']), expected_total, delta=1.0,
                               msg="Tổng tiền trong DB phải đúng")
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

        # [SỬA] Giảm giá 10% trên tổng tiền ĐÃ CÓ VAT
        # Giá gốc 50k -> Có VAT 55k -> Giảm 10% của 55k = 5.5k
        expected_discount = (self.TEST_PROD_PRICE * self.VAT_RATE) * 0.1

        self.assertAlmostEqual(discount, expected_discount, delta=1.0,
                               msg="Giảm giá phải là 10% của tổng tiền (có VAT)")

        success, msg = self.controller.process_payment(method="TienMat", id_nv=self.id_nv)
        self.assertTrue(success)

        self.cursor.execute("SELECT diemTichLuy FROM khachHang WHERE idKhachHang = %s", (self.id_kh,))
        new_points = self.cursor.fetchone()['diemTichLuy']

        # 250 - 200 + 10 = 60
        self.assertEqual(new_points, 60, "Logic cộng trừ điểm tích lũy sai")
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
        self.assertEqual(invoice['noiDungCK'], ck_content, "Nội dung chuyển khoản chưa lưu")

        self.cursor.execute("SELECT idNganHang FROM chiTietHoaDon WHERE idHoaDon = %s", (invoice['idHoaDon'],))
        detail = self.cursor.fetchone()
        self.assertEqual(detail['idNganHang'], self.id_ngan_hang, "ID Ngân hàng chưa lưu vào chi tiết")

        if "File: " in msg: self.generated_files.append(msg.split("File: ")[1].strip())


if __name__ == '__main__':
    unittest.main()