import unittest
import mysql.connector
import os
import sys
import pandas as pd
from datetime import datetime, timedelta

# ==============================================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN
# ==============================================================================
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.Controller.ThongKeController import ThongKeController
from src.config.db_config import DB_CONFIG


class TestThongKeIntegration(unittest.TestCase):
    """
    KIỂM THỬ TÍCH HỢP: THỐNG KÊ & BÁO CÁO
    """

    # Định nghĩa hằng số cho dữ liệu test để dễ quản lý dọn dẹp
    TEST_PHONE_NV = '111'
    TEST_EMAIL_NV = 'tk@test.com'
    TEST_PHONE_KH = '0999'

    def setUp(self):
        """CHẠY TRƯỚC MỖI TEST: Tạo dữ liệu hóa đơn giả lập"""
        self.conn = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor(dictionary=True)
        self.controller = ThongKeController()

        # [QUAN TRỌNG] Dọn dẹp SẠCH SẼ dữ liệu cũ/rác
        self.cleanup_db()
        self.generated_files = []

        # --- TẠO DỮ LIỆU MẪU ---

        # 1. Tạo Nhân viên & Khách hàng (Foreign Key)
        # Check xem chức vụ có chưa
        self.cursor.execute("SELECT idChucVu FROM chucVu WHERE tenChucVu = 'TestRole'")
        res_cv = self.cursor.fetchone()
        if res_cv:
            id_cv = res_cv['idChucVu']
        else:
            self.cursor.execute("INSERT INTO chucVu (tenChucVu, luongCoBan) VALUES ('TestRole', 1000)")
            id_cv = self.cursor.lastrowid

        # Insert Nhân viên (SĐT '111' đã được dọn sạch ở cleanup_db nên không lo trùng)
        self.cursor.execute("""
            INSERT INTO nhanVien (hoTen, email, soDienThoai, idChucVu, trangThaiLamViec) 
            VALUES ('Staff TK', %s, %s, %s, 'DangLamViec')
        """, (self.TEST_EMAIL_NV, self.TEST_PHONE_NV, id_cv))
        self.id_nv = self.cursor.lastrowid

        # Insert Khách hàng
        self.cursor.execute("""
            INSERT INTO khachHang (hoTen, soDienThoai) 
            VALUES ('Customer TK', %s)
        """, (self.TEST_PHONE_KH,))
        self.id_kh = self.cursor.lastrowid

        self.conn.commit()

        # 2. Insert Hóa đơn (Quan trọng: TrangThai = 2 là đã thanh toán)

        # Hóa đơn A: Hôm nay, Đã thanh toán (100k)
        self.create_invoice(100000, 2, datetime.now())

        # Hóa đơn B: Hôm qua, Đã thanh toán (200k)
        yesterday = datetime.now() - timedelta(days=1)
        self.create_invoice(200000, 2, yesterday)

        # Hóa đơn C: 10 ngày trước, Đã thanh toán (300k) -> Để test bộ lọc 7 ngày (Sẽ bị loại)
        ten_days_ago = datetime.now() - timedelta(days=10)
        self.create_invoice(300000, 2, ten_days_ago)

        # Hóa đơn D: Hôm nay, CHƯA thanh toán (500k) -> Phải bị LOẠI BỎ khỏi thống kê
        self.create_invoice(500000, 1, datetime.now())

        # Hóa đơn E: Hôm nay, Đã HỦY (50k) -> Phải bị LOẠI BỎ
        self.create_invoice(50000, 0, datetime.now())

    def create_invoice(self, total, status, date_obj):
        """Helper để insert hóa đơn nhanh"""
        sql = "INSERT INTO hoaDon (idNhanVien, idKhachHang, tongTien, trangThai, ngayTao) VALUES (%s, %s, %s, %s, %s)"
        self.cursor.execute(sql, (self.id_nv, self.id_kh, total, status, date_obj))
        self.conn.commit()

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
        """
        [FIX QUAN TRỌNG] Xóa dữ liệu theo thông tin UNIQUE (SĐT, Email)
        để tránh lỗi Duplicate Entry khi chạy lại test.
        """
        try:
            # 1. Xóa bảng con (chiTietHoaDon) - Dù test này ko tạo chi tiết nhưng cứ xóa cho chắc
            self.cursor.execute("DELETE FROM chiTietHoaDon")

            # 2. Xóa TOÀN BỘ hóa đơn (Để đảm bảo tính toán thống kê chính xác, ko bị cộng dồn dữ liệu cũ)
            self.cursor.execute("DELETE FROM hoaDon")

            # 3. Xóa Nhân viên theo ID, Email VÀ Số điện thoại (Khắc phục lỗi Duplicate '111')
            if hasattr(self, 'id_nv'):
                self.cursor.execute("DELETE FROM nhanVien WHERE idNhanVien = %s", (self.id_nv,))
            self.cursor.execute("DELETE FROM nhanVien WHERE email = %s", (self.TEST_EMAIL_NV,))
            self.cursor.execute("DELETE FROM nhanVien WHERE soDienThoai = %s", (self.TEST_PHONE_NV,))

            # 4. Xóa Khách hàng
            if hasattr(self, 'id_kh'):
                self.cursor.execute("DELETE FROM khachHang WHERE idKhachHang = %s", (self.id_kh,))
            self.cursor.execute("DELETE FROM khachHang WHERE soDienThoai = %s", (self.TEST_PHONE_KH,))

            # 5. Xóa Chức vụ test
            self.cursor.execute("DELETE FROM chucVu WHERE tenChucVu = 'TestRole'")

            self.conn.commit()
        except Exception as e:
            # print(f"Cleanup warning: {e}")
            pass

    # ==========================================================================
    # TEST CASES
    # ==========================================================================

    def test_overview_stats_accuracy(self):
        """Test 1: Kiểm tra tính chính xác của Tổng quan (Doanh thu, Số đơn)"""

        now = datetime.now()
        summary = self.controller.get_dashboard_summary(month="Tất cả", year=now.year)

        # Kỳ vọng:
        # - Hóa đơn A (100k, status 2) -> Tính
        # - Hóa đơn B (200k, status 2) -> Tính
        # - Hóa đơn C (300k, status 2) -> Tính
        # -> Tổng: 600,000

        expected_total_money = 100000 + 200000 + 300000
        expected_count = 3

        # Assert
        self.assertEqual(float(summary['raw_revenue']), float(expected_total_money))
        self.assertEqual(summary['raw_orders'], expected_count)

        self.assertIn("600,000", summary['doanh_thu'])

    def test_filter_7_days(self):
        """Test 2: Kiểm tra bộ lọc '7 ngày qua'"""
        # Mode "7_days" sẽ lấy: Hôm nay (A), Hôm qua (B).
        # Phải LOẠI BỎ: 10 ngày trước (C)

        labels, values, rows = self.controller.get_chart_and_table_data(mode_filter="7_days", month=None, year=None)

        total_revenue_7_days = sum(values)

        # Kỳ vọng: 100k (A) + 200k (B) = 300k
        # Nếu DB còn rác thì con số này sẽ sai -> Hàm cleanup_db đã fix điều đó
        self.assertEqual(total_revenue_7_days, 300000)

    def test_filter_month_year(self):
        """Test 3: Kiểm tra bộ lọc theo Tháng/Năm"""
        now = datetime.now()

        # Lấy data theo tháng hiện tại
        labels, values, rows = self.controller.get_chart_and_table_data(
            mode_filter="month", month=now.month, year=now.year
        )

        self.assertGreater(len(rows), 0)

        # Test lọc tháng sai (Tháng sau) -> Phải rỗng
        next_month = now.month + 1 if now.month < 12 else 1
        year_next = now.year if now.month < 12 else now.year + 1

        labels_empty, values_empty, rows_empty = self.controller.get_chart_and_table_data(
            mode_filter="month", month=next_month, year=year_next
        )

        self.assertEqual(len(rows_empty), 0, "Lọc tháng tương lai phải không có dữ liệu")

    def test_export_excel(self):
        """Test 4: Xuất báo cáo ra Excel"""
        now = datetime.now()
        file_path = "test_report_thongke.xlsx"
        self.generated_files.append(file_path)

        success, msg = self.controller.export_report_to_excel(
            filepath=file_path,
            mode_filter="month",
            month=now.month,
            year=now.year
        )

        self.assertTrue(success, f"Xuất Excel thất bại: {msg}")
        self.assertTrue(os.path.exists(file_path), "File Excel không được tạo ra trên ổ cứng")

        try:
            df = pd.read_excel(file_path, sheet_name='Tổng Quan')
            self.assertTrue('Doanh thu tổng' in df['Tiêu chí'].values)
        except Exception as e:
            self.fail(f"File Excel tạo ra bị lỗi format: {e}")


if __name__ == '__main__':
    unittest.main()