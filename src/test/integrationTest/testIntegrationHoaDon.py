import unittest
import mysql.connector
import os
import sys
import shutil
from datetime import datetime

# ==============================================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN
# ==============================================================================
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.Controller.HoaDonController import HoaDonController
from src.config.db_config import DB_CONFIG


class TestHoaDonIntegration(unittest.TestCase):
    """
    KIỂM THỬ TÍCH HỢP: QUẢN LÝ HÓA ĐƠN
    (Bao gồm: Filter, Transaction Update, PDF Export)
    """

    def setUp(self):
        """CHẠY TRƯỚC MỖI TEST: Tạo dữ liệu môi trường đầy đủ"""
        self.conn = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor(dictionary=True)
        self.controller = HoaDonController()

        # [QUAN TRỌNG] Dọn dẹp sạch sẽ dữ liệu cũ/rác trước khi tạo mới
        self.cleanup_db()

        # --- 1. Tạo Dữ liệu Master ---

        # A. Chức vụ (Get or Create)
        self.cursor.execute("SELECT idChucVu FROM chucVu WHERE tenChucVu = 'TestRole'")
        res_cv = self.cursor.fetchone()
        if res_cv:
            self.id_cv = res_cv['idChucVu']
        else:
            self.cursor.execute("INSERT INTO chucVu (tenChucVu, luongCoBan) VALUES ('TestRole', 1000)")
            self.id_cv = self.cursor.lastrowid

        # B. Nhân viên (Đảm bảo không trùng SĐT 111 hoặc Email)
        self.cursor.execute("""
            INSERT INTO nhanVien (hoTen, email, soDienThoai, idChucVu, trangThaiLamViec) 
            VALUES ('Staff HD Test', 'hd@test.com', '111', %s, 'DangLamViec')
        """, (self.id_cv,))
        self.id_nv = self.cursor.lastrowid

        # C. Khách hàng
        self.cursor.execute("INSERT INTO khachHang (hoTen, soDienThoai) VALUES ('Customer HD Test', '0999')")
        self.id_kh = self.cursor.lastrowid

        # D. Danh mục
        self.cursor.execute("SELECT idDanhMuc FROM danhMuc WHERE tenDanhMuc = 'Test Cat'")
        res_dm = self.cursor.fetchone()
        if res_dm:
            self.id_dm = res_dm['idDanhMuc']
        else:
            self.cursor.execute("INSERT INTO danhMuc (tenDanhMuc) VALUES ('Test Cat')")
            self.id_dm = self.cursor.lastrowid

        # E. Nhà cung cấp
        self.cursor.execute("SELECT idNhaCungCap FROM nhaCungCap WHERE tenNhaCungCap = 'NCC Test'")
        res_ncc = self.cursor.fetchone()
        if res_ncc:
            self.id_ncc = res_ncc['idNhaCungCap']
        else:
            self.cursor.execute("INSERT INTO nhaCungCap (tenNhaCungCap, isActive) VALUES ('NCC Test', 1)")
            self.id_ncc = self.cursor.lastrowid

        # F. Nguyên liệu
        self.cursor.execute("""
            INSERT INTO khoNguyenLieu (tenNguyenLieu, giaNhap, soLuongTon, donViTinh, idNhaCungCap, isActive) 
            VALUES ('NL Test', 100, 100, 'kg', %s, 1)
        """, (self.id_ncc,))
        self.id_nl = self.cursor.lastrowid

        # G. Sản phẩm
        self.cursor.execute(
            "INSERT INTO sanPham (tenSanPham, giaBan, idDanhMuc, idNguyenLieu, isActive) VALUES ('Product A', 10000, %s, %s, 1)",
            (self.id_dm, self.id_nl))
        self.id_sp_a = self.cursor.lastrowid

        self.cursor.execute(
            "INSERT INTO sanPham (tenSanPham, giaBan, idDanhMuc, idNguyenLieu, isActive) VALUES ('Product B', 20000, %s, %s, 1)",
            (self.id_dm, self.id_nl))
        self.id_sp_b = self.cursor.lastrowid

        # H. Ngân hàng
        self.cursor.execute("SELECT idNganHang FROM nganHang WHERE soTaiKhoan = '88889999'")
        res_bank = self.cursor.fetchone()
        if res_bank:
            self.id_bank = res_bank['idNganHang']
        else:
            self.cursor.execute(
                "INSERT INTO nganHang (tenNganHang, soTaiKhoan, isActive) VALUES ('TestBank', '88889999', 1)")
            self.id_bank = self.cursor.lastrowid

        # Commit toàn bộ dữ liệu chuẩn bị
        self.conn.commit()
        self.generated_files = []

    def tearDown(self):
        """CHẠY SAU MỖI TEST"""
        self.cleanup_db()
        for f in self.generated_files:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass
        if self.conn.is_connected():
            self.cursor.close()
            self.conn.close()

    def cleanup_db(self):
        """Xóa dữ liệu test sạch sẽ để tránh lỗi Duplicate"""
        try:
            # 1. Xóa Hóa đơn và Chi tiết (Liên quan đến Nhân viên cần xóa)
            # Tìm tất cả hóa đơn của nhân viên test hoặc khách hàng test
            self.cursor.execute("""
                SELECT idHoaDon FROM hoaDon 
                WHERE idNhanVien = (SELECT idNhanVien FROM nhanVien WHERE soDienThoai = '111')
                   OR idKhachHang = (SELECT idKhachHang FROM khachHang WHERE soDienThoai = '0999')
            """)
            hds = self.cursor.fetchall()
            for hd in hds:
                self.cursor.execute("DELETE FROM chiTietHoaDon WHERE idHoaDon = %s", (hd['idHoaDon'],))
                self.cursor.execute("DELETE FROM hoaDon WHERE idHoaDon = %s", (hd['idHoaDon'],))

            # 2. Xóa dữ liệu Master
            self.cursor.execute("DELETE FROM sanPham WHERE tenSanPham IN ('Product A', 'Product B')")
            self.cursor.execute("DELETE FROM khoNguyenLieu WHERE tenNguyenLieu = 'NL Test'")

            # [FIX QUAN TRỌNG] Xóa Khách hàng và Nhân viên theo SĐT để tránh trùng lặp
            self.cursor.execute("DELETE FROM khachHang WHERE soDienThoai = '0999'")

            # Xóa nhân viên theo cả Email và SĐT
            self.cursor.execute("DELETE FROM nhanVien WHERE email = 'hd@test.com'")
            self.cursor.execute("DELETE FROM nhanVien WHERE soDienThoai = '111'")

            self.conn.commit()
        except Exception as e:
            # print(f"Cleanup warning: {e}")
            pass

    # ==========================================================================
    # TEST CASES
    # ==========================================================================

    def test_filter_and_display_logic(self):
        """Test: Tạo hóa đơn CK -> Lọc -> Kiểm tra Controller hiển thị đúng định dạng"""

        # 1. Tạo hóa đơn giả lập
        sql_hd = "INSERT INTO hoaDon (idNhanVien, idKhachHang, tongTien, trangThai, ngayTao) VALUES (%s, %s, 11000, 2, NOW())"
        self.cursor.execute(sql_hd, (self.id_nv, self.id_kh))
        id_hd = self.cursor.lastrowid

        # Insert chi tiết (Không insert cột thanhTien)
        sql_ct = "INSERT INTO chiTietHoaDon (idHoaDon, idSanPham, soLuong, donGia, thueVAT, idNganHang) VALUES (%s, %s, 1, 10000, 10, %s)"
        self.cursor.execute(sql_ct, (id_hd, self.id_sp_a, self.id_bank))
        self.conn.commit()

        # 2. Gọi Controller để lọc
        results = self.controller.filter_invoices(day="Tất cả", month="Tất cả", year="", keyword=str(id_hd))

        # 3. Assert Logic hiển thị
        self.assertEqual(len(results), 1)
        invoice = results[0]

        # Kiểm tra format
        self.assertEqual(invoice['tongTienFmt'], "11,000 VNĐ")
        self.assertIn("CK", invoice['paymentMethod'])
        self.assertIn("TestBank", invoice['paymentMethod'])
        self.assertEqual(invoice['maHienThi'], f"#{id_hd}")

    def test_transaction_update_invoice(self):
        """Test: Sửa hóa đơn (Xóa món A, Thêm món B) -> Tổng tiền tự cập nhật"""

        # 1. Tạo hóa đơn ban đầu
        sql_hd = "INSERT INTO hoaDon (idNhanVien, tongTien, trangThai) VALUES (%s, 11000, 1)"
        self.cursor.execute(sql_hd, (self.id_nv,))
        id_hd = self.cursor.lastrowid

        # Insert chi tiết món A
        sql_ct = "INSERT INTO chiTietHoaDon (idHoaDon, idSanPham, soLuong, donGia, thueVAT) VALUES (%s, %s, 1, 10000, 10)"
        self.cursor.execute(sql_ct, (id_hd, self.id_sp_a))
        self.conn.commit()

        # 2. Chuẩn bị dữ liệu mới: Món B (20k, SL=2)
        new_items = [
            {'idSanPham': self.id_sp_b, 'soLuong': 2, 'donGia': 20000}
        ]

        # 3. Gọi Controller để Lưu
        success, msg = self.controller.save_edited_invoice(id_hd, "Đã thanh toán", new_items)
        self.assertTrue(success, f"Update lỗi: {msg}")

        # Commit để refresh snapshot
        self.conn.commit()

        # 4. Verify DB
        self.cursor.execute("SELECT tongTien, trangThai FROM hoaDon WHERE idHoaDon = %s", (id_hd,))
        header = self.cursor.fetchone()

        # Kiểm tra tổng tiền: 2 * 20000 * 1.1 = 44000
        self.assertEqual(float(header['tongTien']), 44000.0)
        self.assertEqual(header['trangThai'], 2)

        # Kiểm tra chi tiết: Món A mất, Món B xuất hiện
        self.cursor.execute("SELECT idSanPham, soLuong FROM chiTietHoaDon WHERE idHoaDon = %s", (id_hd,))
        details = self.cursor.fetchall()

        self.assertEqual(len(details), 1)
        self.assertEqual(details[0]['idSanPham'], self.id_sp_b)
        self.assertEqual(details[0]['soLuong'], 2)

    def test_export_pdf(self):
        """Test: Xuất hóa đơn ra file PDF"""
        sql_hd = "INSERT INTO hoaDon (idNhanVien, tongTien, trangThai, ngayTao) VALUES (%s, 11000, 2, NOW())"
        self.cursor.execute(sql_hd, (self.id_nv,))
        id_hd = self.cursor.lastrowid
        self.conn.commit()

        pdf_path = f"test_invoice_{id_hd}.pdf"
        self.generated_files.append(pdf_path)

        success, msg = self.controller.export_invoice_pdf(id_hd, pdf_path)

        self.assertTrue(success, f"Xuất PDF thất bại: {msg}")
        self.assertTrue(os.path.exists(pdf_path), "File PDF không tồn tại trên ổ cứng")


if __name__ == '__main__':
    unittest.main()