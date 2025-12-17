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

from src.Controller.SanPhamController import SanPhamController
from src.config.db_config import DB_CONFIG


class TestSanPhamIntegration(unittest.TestCase):
    """
    KIỂM THỬ TÍCH HỢP: QUẢN LÝ SẢN PHẨM & ẢNH
    """

    # Dữ liệu test
    TEST_PROD_NAME = "Integration Test Coffee"
    TEST_PRICE = 45000
    DUMMY_IMG_NAME = "temp_test_image.jpg"

    def setUp(self):
        """CHẠY TRƯỚC MỖI TEST: Tạo dữ liệu phụ thuộc & File ảnh giả"""
        self.conn = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor(dictionary=True)
        self.controller = SanPhamController()

        # 1. Tạo file ảnh giả để test upload
        # Tạo một file rỗng hoặc chứa text để giả lập ảnh
        with open(self.DUMMY_IMG_NAME, "wb") as f:
            f.write(b"This is a fake image content for testing.")

        # 2. Dọn dẹp DB
        self.cleanup_db_data()

        # 3. Tạo Nhà Cung Cấp (Để có Nguyên liệu)
        self.cursor.execute("INSERT INTO nhaCungCap (tenNhaCungCap, isActive) VALUES ('NCC Test SP', 1)")
        self.id_ncc = self.cursor.lastrowid

        # 4. Tạo Nguyên Liệu
        self.cursor.execute("""
            INSERT INTO khoNguyenLieu (tenNguyenLieu, giaNhap, soLuongTon, donViTinh, idNhaCungCap, isActive)
            VALUES ('Hat Cafe Test', 10000, 100, 'kg', %s, 1)
        """, (self.id_ncc,))
        self.id_nl = self.cursor.lastrowid

        # 5. Tạo Danh Mục
        self.cursor.execute("INSERT INTO danhMuc (tenDanhMuc) VALUES ('Category Test SP')")
        self.id_dm = self.cursor.lastrowid

        self.conn.commit()

        # List để theo dõi các file ảnh đã tạo ra để xóa sau khi test
        self.created_files = []

    def tearDown(self):
        """CHẠY SAU MỖI TEST: Dọn dẹp"""
        # 1. Xóa dữ liệu DB
        self.cleanup_db_data()
        if self.conn.is_connected():
            self.cursor.close()
            self.conn.close()

        # 2. Xóa file ảnh nguồn giả
        if os.path.exists(self.DUMMY_IMG_NAME):
            os.remove(self.DUMMY_IMG_NAME)

        # 3. Xóa các file ảnh đã được Controller copy vào src/images
        for f_path in self.created_files:
            # Đường dẫn trong DB lưu tương đối hoặc tuyệt đối, cần xử lý để xóa
            # Controller trả về: src/images/ten_timestamp.jpg
            abs_path = os.path.join(project_root, f_path) if not os.path.isabs(f_path) else f_path
            if os.path.exists(abs_path):
                try:
                    os.remove(abs_path)
                except:
                    pass

    def cleanup_db_data(self):
        """Xóa dữ liệu theo thứ tự khóa ngoại"""
        try:
            self.cursor.execute("DELETE FROM sanPham WHERE tenSanPham = %s", (self.TEST_PROD_NAME,))
            self.cursor.execute("DELETE FROM sanPham WHERE tenSanPham = 'Updated Coffee Name'")

            if hasattr(self, 'id_nl'): self.cursor.execute("DELETE FROM khoNguyenLieu WHERE idNguyenLieu = %s",
                                                           (self.id_nl,))
            if hasattr(self, 'id_dm'): self.cursor.execute("DELETE FROM danhMuc WHERE idDanhMuc = %s", (self.id_dm,))
            if hasattr(self, 'id_ncc'): self.cursor.execute("DELETE FROM nhaCungCap WHERE idNhaCungCap = %s",
                                                            (self.id_ncc,))

            self.conn.commit()
        except Exception as e:
            print(f"Cleanup Error: {e}")

    # ==========================================================================
    # TEST CASES
    # ==========================================================================

    def test_add_product_with_image_upload(self):
        """Test 1: Thêm sản phẩm + Upload ảnh thành công"""

        # Thực hiện thêm
        # hinh_anh_path trỏ tới file giả tạo ở setUp
        success, msg = self.controller.them_san_pham(
            self.TEST_PROD_NAME, self.TEST_PRICE, self.DUMMY_IMG_NAME, self.id_dm, self.id_nl
        )

        self.assertTrue(success, f"Thêm thất bại: {msg}")

        # [VERIFY DB]
        self.cursor.execute("SELECT * FROM sanPham WHERE tenSanPham = %s", (self.TEST_PROD_NAME,))
        prod = self.cursor.fetchone()

        self.assertIsNotNone(prod)
        self.assertEqual(float(prod['giaBan']), self.TEST_PRICE)
        self.assertEqual(prod['idDanhMuc'], self.id_dm)
        self.assertEqual(prod['isActive'], 1)

        # [VERIFY FILE SYSTEM]
        # Kiểm tra xem đường dẫn ảnh trong DB có tồn tại thật không
        db_img_path = prod['hinhAnhUrl']  # VD: src/images/temp_test_image_170000.jpg
        self.created_files.append(db_img_path)  # Đánh dấu để tearDown xóa

        # Kiểm tra đường dẫn có chứa thư mục images không
        self.assertIn("src/images", db_img_path.replace("\\", "/"))

        # Kiểm tra file có tồn tại trên ổ cứng không
        full_path = os.path.abspath(db_img_path)
        self.assertTrue(os.path.exists(full_path), f"File ảnh không được copy vào đích: {full_path}")

    def test_toggle_status_product(self):
        """Test 3: Ẩn / Hiện sản phẩm"""
        # 1. Thêm sản phẩm (Mặc định isActive = 1)
        self.controller.them_san_pham(self.TEST_PROD_NAME, 30000, "", self.id_dm, self.id_nl)

        # Lấy ID của sản phẩm vừa tạo
        self.cursor.execute("SELECT idSanPham, isActive FROM sanPham WHERE tenSanPham = %s", (self.TEST_PROD_NAME,))
        res = self.cursor.fetchone()
        id_sp = res['idSanPham']

        # Kiểm tra trạng thái ban đầu
        self.assertEqual(res['isActive'], 1)

        # 2. Gọi Controller để Đổi trạng thái (1 -> 0)
        success, msg = self.controller.doi_trang_thai(id_sp)
        self.assertTrue(success, f"Đổi trạng thái thất bại: {msg}")

        # [QUAN TRỌNG] Commit kết nối của Test để làm mới dữ liệu (Refresh Snapshot)
        # Nếu thiếu dòng này, Test vẫn nhìn thấy dữ liệu cũ (isActive=1)
        self.conn.commit()

        # 3. Kiểm tra lại trong DB
        self.cursor.execute("SELECT isActive FROM sanPham WHERE idSanPham = %s", (id_sp,))
        new_status = self.cursor.fetchone()['isActive']

        self.assertEqual(new_status, 0, "Trạng thái phải chuyển thành 0 (Ẩn) sau khi toggle")

    def test_toggle_status_product(self):
        """Test 3: Ẩn / Hiện sản phẩm"""
        # 1. Thêm sản phẩm (Mặc định isActive = 1)
        self.controller.them_san_pham(self.TEST_PROD_NAME, 30000, "", self.id_dm, self.id_nl)

        # Lấy ID của sản phẩm vừa tạo
        self.cursor.execute("SELECT idSanPham, isActive FROM sanPham WHERE tenSanPham = %s", (self.TEST_PROD_NAME,))
        res = self.cursor.fetchone()
        id_sp = res['idSanPham']

        # Kiểm tra trạng thái ban đầu
        self.assertEqual(res['isActive'], 1)

        # 2. Gọi Controller để Đổi trạng thái (1 -> 0)
        # Controller sẽ tự mở kết nối riêng, update và commit.
        success, msg = self.controller.doi_trang_thai(id_sp)
        self.assertTrue(success, f"Đổi trạng thái lỗi: {msg}")

        # [QUAN TRỌNG]: Commit kết nối của Test để làm mới dữ liệu (Refresh Snapshot)
        # Nếu thiếu dòng này, Test vẫn nhìn thấy dữ liệu cũ (isActive=1)
        self.conn.commit()

        # 3. Kiểm tra lại trong DB
        self.cursor.execute("SELECT isActive FROM sanPham WHERE idSanPham = %s", (id_sp,))
        new_status = self.cursor.fetchone()['isActive']

        self.assertEqual(new_status, 0, "Trạng thái phải chuyển thành 0 (Ẩn)")

    def test_validate_input(self):
        """Test 4: Validate giá âm và tên rỗng"""
        # Tên rỗng
        success, msg = self.controller.them_san_pham("", 10000, "", self.id_dm, self.id_nl)
        self.assertFalse(success)
        self.assertEqual(msg, "Tên sản phẩm không được trống")

        # Giá âm
        success, msg = self.controller.them_san_pham("Bad Price", -5000, "", self.id_dm, self.id_nl)
        self.assertFalse(success)
        self.assertEqual(msg, "Giá bán không hợp lệ")


if __name__ == '__main__':
    unittest.main()