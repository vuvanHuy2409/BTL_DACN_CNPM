import unittest
import mysql.connector
import os
import sys
import pandas as pd
from datetime import datetime

# ==============================================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN
# ==============================================================================
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.Controller.LuongController import LuongController
from src.config.db_config import DB_CONFIG


class TestLuongIntegration(unittest.TestCase):
    """
    KIỂM THỬ TÍCH HỢP: TÍNH LƯƠNG & THANH TOÁN
    """

    # Dữ liệu Test: 5,200,000 / 26 / 8 = 25,000 VNĐ/giờ
    TEST_BASE_SALARY = 5200000
    TEST_MONTH_STR = "Tháng 12/2025"
    TEST_MONTH = 12
    TEST_YEAR = 2025

    def setUp(self):
        """CHẠY TRƯỚC MỖI TEST: Tạo dữ liệu Chấm công giả lập"""
        self.conn = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor(dictionary=True)
        self.controller = LuongController()

        self.cleanup_db()
        self.generated_files = []

        # 1. Tạo Chức vụ (Lương 5.2tr)
        self.cursor.execute("INSERT INTO chucVu (tenChucVu, luongCoBan) VALUES ('Test Salary Role', %s)",
                            (self.TEST_BASE_SALARY,))
        self.id_cv = self.cursor.lastrowid

        # 2. Tạo Nhân viên
        self.cursor.execute(
            "INSERT INTO nhanVien (hoTen, email, soDienThoai, idChucVu, trangThaiLamViec) VALUES ('Staff Luong', 'luong@test.com', '111', %s, 'DangLamViec')",
            (self.id_cv,))
        self.id_nv = self.cursor.lastrowid

        # 3. Tạo Dữ liệu Chấm công (BangChamCong) - Tổng 12 tiếng
        sql_cc = """
            INSERT INTO bangChamCong (idNhanVien, gioVao, gioRa, tongGioLam) 
            VALUES (%s, %s, %s, %s)
        """
        # Ca 1: 8 tiếng
        self.cursor.execute(sql_cc, (self.id_nv, '2025-12-01 08:00:00', '2025-12-01 17:00:00', 8.0))
        # Ca 2: 4 tiếng
        self.cursor.execute(sql_cc, (self.id_nv, '2025-12-02 08:00:00', '2025-12-02 12:00:00', 4.0))

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
        try:
            # Xóa theo ID nhân viên test để tránh ảnh hưởng dữ liệu thật (Huy ADMIN)
            if hasattr(self, 'id_nv'):
                self.cursor.execute("DELETE FROM luong WHERE idNhanVien = %s", (self.id_nv,))
                self.cursor.execute("DELETE FROM bangChamCong WHERE idNhanVien = %s", (self.id_nv,))
                self.cursor.execute("DELETE FROM nhanVien WHERE idNhanVien = %s", (self.id_nv,))

            self.cursor.execute("DELETE FROM chucVu WHERE tenChucVu = 'Test Salary Role'")
            self.conn.commit()
        except Exception:
            pass

    # [FIX] Hàm phụ trợ để tìm đúng nhân viên test trong danh sách trả về
    # (Tránh lấy nhầm ông 'Huy ADMIN')
    def get_test_item(self, data_list):
        for item in data_list:
            if item['idNhanVien'] == self.id_nv:
                return item
        return None

    # ==========================================================================
    # TEST CASES
    # ==========================================================================

    def test_salary_calculation_logic(self):
        """Test 1: Kiểm tra tính toán lương và Đồng bộ (Sync)"""

        data = self.controller.get_list_salary(self.TEST_MONTH_STR)

        # [FIX] Tìm đúng nhân viên test, không dùng data[0] bừa bãi
        item = self.get_test_item(data)
        self.assertIsNotNone(item, "Không tìm thấy nhân viên test trong bảng lương")

        # 1. Kiểm tra thông tin cơ bản
        self.assertEqual(item['hoTen'], 'Staff Luong')
        self.assertEqual(float(item['luongCoBanSnapshot']), self.TEST_BASE_SALARY)

        # 2. Kiểm tra Tổng giờ làm (8 + 4 = 12)
        self.assertEqual(float(item['tongGioLamThang']), 12.0)

        # 3. Kiểm tra Thực lãnh: (5,200,000 / 26 / 8) * 12 = 300,000
        self.assertEqual(float(item['thucLanh']), 300000)
        self.assertEqual(item['trangThai'], 'ChuaThanhToan')

    def test_salary_snapshot_mechanism(self):
        """Test 2: Kiểm tra cơ chế Snapshot (Lương cũ không đổi khi tăng lương cơ bản)"""

        # B1: Tính lương lần đầu (Snapshot mức 5.2tr)
        self.controller.get_list_salary(self.TEST_MONTH_STR)

        # B2: Tăng lương cơ bản của chức vụ lên 15 triệu (như lỗi của bạn)
        self.cursor.execute("UPDATE chucVu SET luongCoBan = 15000000 WHERE idChucVu = %s", (self.id_cv,))
        self.conn.commit()

        # B3: Lấy lại bảng lương tháng cũ
        data = self.controller.get_list_salary(self.TEST_MONTH_STR)

        # [FIX] Tìm đúng nhân viên test
        item = self.get_test_item(data)

        # Verify: Snapshot vẫn là 5.2tr, không được nhảy lên 15tr
        self.assertEqual(float(item['luongCoBanSnapshot']), self.TEST_BASE_SALARY)
        self.assertEqual(float(item['thucLanh']), 300000)

    def test_payment_status_update(self):
        """Test 3: Thanh toán lương"""

        # 1. Sync dữ liệu
        self.controller.get_list_salary(self.TEST_MONTH_STR)

        # 2. Thực hiện thanh toán
        success, msg = self.controller.thanh_toan_luong(self.id_nv, self.TEST_MONTH_STR)
        self.assertTrue(success, f"Thanh toán thất bại: {msg}")

        # [FIX] Commit để refresh snapshot DB
        self.conn.commit()

        # 3. Kiểm tra lại dữ liệu
        data = self.controller.get_list_salary(self.TEST_MONTH_STR)
        item = self.get_test_item(data)  # [FIX] Tìm đúng nhân viên

        self.assertEqual(item['trangThai'], 'DaThanhToan')

    def test_export_files(self):
        """Test 4: Xuất Excel và PDF"""
        self.controller.get_list_salary(self.TEST_MONTH_STR)

        # Test Excel
        excel_path = "test_luong.xlsx"
        self.generated_files.append(excel_path)
        success, msg = self.controller.export_excel(self.TEST_MONTH_STR, excel_path)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(excel_path))

        # Test PDF
        pdf_path = "test_luong.pdf"
        self.generated_files.append(pdf_path)
        success, msg = self.controller.export_pdf(self.TEST_MONTH_STR, pdf_path)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(pdf_path))


if __name__ == '__main__':
    unittest.main()