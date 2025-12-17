import unittest
import mysql.connector
import os
import sys
import pandas as pd

# ==============================================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN
# ==============================================================================
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.Controller.NhaCungCapController import NhaCungCapController
from src.config.db_config import DB_CONFIG


class TestNhaCungCapIntegration(unittest.TestCase):
    """
    KIỂM THỬ TÍCH HỢP: QUẢN LÝ NHÀ CUNG CẤP
    """

    # Dữ liệu Test
    TEST_NCC_NAME = "Integration Supplier Test"
    TEST_PHONE = "0909000111"
    TEST_ADDR = "123 Test Street"

    def setUp(self):
        """CHẠY TRƯỚC MỖI TEST"""
        self.conn = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor(dictionary=True)
        self.controller = NhaCungCapController()

        self.cleanup_db()
        self.generated_files = []

    def tearDown(self):
        """CHẠY SAU MỖI TEST"""
        self.cleanup_db()

        # Xóa file Excel
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
        """Xóa dữ liệu theo thứ tự khóa ngoại"""
        try:
            # 1. Xóa Nguyên liệu test trước (Vì có FK trỏ về NCC)
            # Tìm ID của NCC test để xóa NL tương ứng
            self.cursor.execute("SELECT idNhaCungCap FROM nhaCungCap WHERE tenNhaCungCap = %s", (self.TEST_NCC_NAME,))
            res = self.cursor.fetchall()
            for row in res:
                self.cursor.execute("DELETE FROM khoNguyenLieu WHERE idNhaCungCap = %s", (row['idNhaCungCap'],))

            # 2. Xóa Nhà cung cấp
            self.cursor.execute("DELETE FROM nhaCungCap WHERE tenNhaCungCap = %s", (self.TEST_NCC_NAME,))
            self.cursor.execute("DELETE FROM nhaCungCap WHERE tenNhaCungCap = 'Updated Supplier Name'")

            self.conn.commit()
        except Exception:
            pass

    # ==========================================================================
    # TEST CASES
    # ==========================================================================

    def test_add_ncc_success(self):
        """Test 1: Thêm nhà cung cấp mới"""
        success, msg = self.controller.them_ncc(self.TEST_NCC_NAME, self.TEST_PHONE, self.TEST_ADDR)

        self.assertTrue(success, f"Thêm thất bại: {msg}")

        # [FIX] Commit để thấy dữ liệu mới
        self.conn.commit()

        # Verify DB
        self.cursor.execute("SELECT * FROM nhaCungCap WHERE tenNhaCungCap = %s", (self.TEST_NCC_NAME,))
        ncc = self.cursor.fetchone()

        self.assertIsNotNone(ncc)
        self.assertEqual(ncc['soDienThoai'], self.TEST_PHONE)
        self.assertEqual(ncc['diaChi'], self.TEST_ADDR)
        self.assertEqual(ncc['isActive'], 1)

    def test_update_ncc(self):
        """Test 2: Cập nhật thông tin NCC"""
        # 1. Tạo trước
        self.controller.them_ncc(self.TEST_NCC_NAME, self.TEST_PHONE, self.TEST_ADDR)
        self.conn.commit()

        self.cursor.execute("SELECT idNhaCungCap FROM nhaCungCap WHERE tenNhaCungCap = %s", (self.TEST_NCC_NAME,))
        id_ncc = self.cursor.fetchone()['idNhaCungCap']

        # 2. Sửa
        new_name = "Updated Supplier Name"
        success, msg = self.controller.sua_ncc(id_ncc, new_name, "0999888777", "New Address")
        self.assertTrue(success)

        # [FIX] Commit
        self.conn.commit()

        # 3. Verify DB
        self.cursor.execute("SELECT * FROM nhaCungCap WHERE idNhaCungCap = %s", (id_ncc,))
        updated = self.cursor.fetchone()

        self.assertEqual(updated['tenNhaCungCap'], new_name)
        self.assertEqual(updated['soDienThoai'], "0999888777")

    def test_toggle_status(self):
        """Test 3: Ẩn/Hiện nhà cung cấp"""
        self.controller.them_ncc(self.TEST_NCC_NAME, self.TEST_PHONE, self.TEST_ADDR)
        self.conn.commit()

        self.cursor.execute("SELECT idNhaCungCap, isActive FROM nhaCungCap WHERE tenNhaCungCap = %s",
                            (self.TEST_NCC_NAME,))
        row = self.cursor.fetchone()
        id_ncc = row['idNhaCungCap']
        self.assertEqual(row['isActive'], 1)

        # Đổi sang Ẩn
        self.controller.doi_trang_thai(id_ncc)
        self.conn.commit()

        self.cursor.execute("SELECT isActive FROM nhaCungCap WHERE idNhaCungCap = %s", (id_ncc,))
        self.assertEqual(self.cursor.fetchone()['isActive'], 0)

    def test_join_ingredients_display(self):
        """Test 4: Kiểm tra hiển thị kèm danh sách nguyên liệu (Logic GROUP_CONCAT)"""
        # 1. Tạo NCC
        self.controller.them_ncc(self.TEST_NCC_NAME, self.TEST_PHONE, self.TEST_ADDR)
        self.conn.commit()

        self.cursor.execute("SELECT idNhaCungCap FROM nhaCungCap WHERE tenNhaCungCap = %s", (self.TEST_NCC_NAME,))
        id_ncc = self.cursor.fetchone()['idNhaCungCap']

        # 2. Tạo 2 Nguyên liệu gắn với NCC này
        # (Giả sử bảng khoNguyenLieu có cấu trúc như các bài trước)
        sql_nl = """
            INSERT INTO khoNguyenLieu (tenNguyenLieu, giaNhap, soLuongTon, donViTinh, idNhaCungCap, isActive)
            VALUES (%s, 100, 10, 'kg', %s, 1)
        """
        self.cursor.execute(sql_nl, ("NL Test 1", id_ncc))
        self.cursor.execute(sql_nl, ("NL Test 2", id_ncc))
        self.conn.commit()

        # 3. Gọi Controller lấy danh sách
        data = self.controller.lay_danh_sach()

        # 4. Tìm NCC vừa tạo trong list kết quả
        target_item = next((item for item in data if item['idNhaCungCap'] == id_ncc), None)
        self.assertIsNotNone(target_item)

        # 5. Kiểm tra chuỗi GROUP_CONCAT
        # Kết quả mong đợi: "NL Test 1, NL Test 2" (Hoặc ngược lại tùy DB sort)

        ing_str = target_item['danhSachNguyenLieu']
        self.assertIn("NL Test 1", ing_str)
        self.assertIn("NL Test 2", ing_str)
        self.assertIn(",", ing_str)

    def test_export_excel(self):
        """Test 5: Xuất file Excel"""
        # Tạo dữ liệu mẫu
        self.controller.them_ncc(self.TEST_NCC_NAME, self.TEST_PHONE, self.TEST_ADDR)
        data = self.controller.lay_danh_sach()

        # Đường dẫn file
        file_path = "test_ncc_export.xlsx"
        self.generated_files.append(file_path)

        # Gọi export
        success, msg = self.controller.xuat_excel(file_path, data)

        self.assertTrue(success, f"Xuất Excel lỗi: {msg}")
        self.assertTrue(os.path.exists(file_path), "File Excel không được tạo ra")

        # (Tùy chọn) Đọc lại file Excel để check nội dung
        df = pd.read_excel(file_path)
        self.assertIn(self.TEST_NCC_NAME, df['Tên Nhà Cung Cấp'].values)


if __name__ == '__main__':
    unittest.main()