import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# ==============================================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN TỰ ĐỘNG
# ==============================================================================
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.Controller.NganHangController import NganHangController
    from src.Model.NganHangModel import NganHangModel
except ImportError as e:
    raise ImportError(f"Lỗi Import. Root: {project_root}. Details: {e}")


# ==============================================================================
# 2. TEST MODEL (DATABASE & SQL)
# ==============================================================================

class TestNganHangModel(unittest.TestCase):

    def setUp(self):
        self.model = NganHangModel()

    @patch('src.Model.NganHangModel.mysql.connector.connect')
    def test_check_exist_true(self, mock_connect):
        """Test: Kiểm tra trùng lặp (DB trả về dữ liệu -> True)"""
        mock_cursor = mock_connect.return_value.cursor.return_value

        # Giả lập DB tìm thấy 1 dòng
        mock_cursor.fetchone.return_value = (1,)

        result = self.model.check_exist("VCB", "123456789")

        self.assertTrue(result)

        # Kiểm tra SQL có đúng điều kiện AND không
        call_args = mock_cursor.execute.call_args
        sql_query = call_args[0][0]
        params = call_args[0][1]

        self.assertIn("maNganHang = %s", sql_query)
        self.assertIn("AND soTaiKhoan = %s", sql_query)
        self.assertEqual(params, ("VCB", "123456789"))

    @patch('src.Model.NganHangModel.mysql.connector.connect')
    def test_insert_success(self, mock_connect):
        """Test: Lệnh INSERT hoạt động đúng"""
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value

        data = {
            "maNganHang": "MB", "tenNganHang": "MB Bank",
            "soTaiKhoan": "999", "tenTaiKhoan": "HUY", "isActive": 1
        }

        result = self.model.insert(data)

        self.assertTrue(result)
        mock_conn.commit.assert_called_once()

        # Kiểm tra SQL
        sql_query = mock_cursor.execute.call_args[0][0]
        self.assertIn("INSERT INTO nganHang", sql_query)

    @patch('src.Model.NganHangModel.mysql.connector.connect')
    def test_toggle_status(self, mock_connect):
        """Test: Logic ẩn/hiện (NOT isActive)"""
        mock_cursor = mock_connect.return_value.cursor.return_value

        self.model.toggle_status(10)

        sql_query = mock_cursor.execute.call_args[0][0]
        self.assertIn("SET isActive = NOT isActive", sql_query)


# ==============================================================================
# 3. TEST CONTROLLER (LOGIC NGHIỆP VỤ)
# ==============================================================================

class TestNganHangController(unittest.TestCase):

    def setUp(self):
        self.controller = NganHangController()
        # Mock Model để không gọi vào DB thật
        self.controller.model = MagicMock()

        # --- Test 1: Tìm kiếm ---

    def test_tim_kiem_rong(self):
        """Nếu từ khóa rỗng -> Gọi get_all"""
        self.controller.tim_kiem_ngan_hang("")
        self.controller.model.get_all.assert_called_once()
        self.controller.model.search.assert_not_called()

    def test_tim_kiem_co_tukhoa(self):
        """Nếu có từ khóa -> Gọi search"""
        self.controller.tim_kiem_ngan_hang("VCB")
        self.controller.model.search.assert_called_with("VCB")

    # --- Test 2: Thêm Ngân Hàng (Validate & Logic) ---
    def test_them_thieu_thong_tin(self):
        """Test validate dữ liệu rỗng"""
        # Thiếu số tài khoản
        success, msg = self.controller.them_ngan_hang("VCB", "Vietcombank", "", "Huy")

        self.assertFalse(success)
        self.assertEqual(msg, "Vui lòng điền đầy đủ thông tin!")

    def test_them_trung_lap(self):
        """Test logic kiểm tra trùng lặp"""
        # Giả lập Model trả về True (Đã tồn tại)
        self.controller.model.check_exist.return_value = True

        success, msg = self.controller.them_ngan_hang("VCB", "Vietcombank", "012345", "Huy")

        self.assertFalse(success)
        # Kiểm tra thông báo lỗi chứa đúng thông tin
        self.assertIn("VCB", msg)
        self.assertIn("012345", msg)
        self.assertIn("đã tồn tại", msg)

    def test_them_thanh_cong_va_format(self):
        """Test thêm thành công và kiểm tra logic Format dữ liệu (Upper, Strip)"""
        # Giả lập chưa tồn tại
        self.controller.model.check_exist.return_value = False
        self.controller.model.insert.return_value = True

        # Input: Có khoảng trắng thừa, chữ thường
        # "  vcb  " -> "VCB"
        # "  huy  " -> "HUY"
        success, msg = self.controller.them_ngan_hang("  vcb  ", " Vietcom ", " 123 ", " huy ")

        self.assertTrue(success)
        self.assertEqual(msg, "Thêm ngân hàng thành công")

        # Kiểm tra dữ liệu gửi xuống Model đã được xử lý chưa
        expected_data = {
            "maNganHang": "VCB",  # Upper + Strip
            "tenNganHang": "Vietcom",  # Strip
            "soTaiKhoan": "123",  # Strip
            "tenTaiKhoan": "HUY",  # Upper + Strip
            "isActive": 1
        }
        self.controller.model.insert.assert_called_with(expected_data)

    # --- Test 3: Sửa Ngân Hàng ---
    def test_sua_ngan_hang_thanh_cong(self):
        self.controller.model.update.return_value = True

        success, msg = self.controller.sua_ngan_hang(1, "MB", "Quan Doi", "999", "Minh")

        self.assertTrue(success)

        expected_data = {
            "maNganHang": "MB",
            "tenNganHang": "Quan Doi",
            "soTaiKhoan": "999",
            "tenTaiKhoan": "MINH"  # Upper
        }
        self.controller.model.update.assert_called_with(1, expected_data)

    def test_sua_ngan_hang_khong_chon_id(self):
        success, msg = self.controller.sua_ngan_hang(None, "A", "B", "C", "D")
        self.assertFalse(success)
        self.assertIn("Chưa chọn ngân hàng", msg)

    # --- Test 4: Đổi trạng thái ---
    def test_doi_trang_thai(self):
        self.controller.model.toggle_status.return_value = True

        success, msg = self.controller.doi_trang_thai(5)

        self.assertTrue(success)
        self.controller.model.toggle_status.assert_called_with(5)


if __name__ == '__main__':
    unittest.main()