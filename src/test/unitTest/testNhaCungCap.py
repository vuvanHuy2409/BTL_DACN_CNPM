import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# ==============================================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN TỰ ĐỘNG (Fix lỗi ModuleNotFoundError)
# ==============================================================================
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.Controller.NhaCungCapController import NhaCungCapController
    from src.Model.NhaCungCapModel import NhaCungCapModel
except ImportError as e:
    raise ImportError(f"Lỗi Import. Root: {project_root}. Details: {e}")


# ==============================================================================
# 2. TEST MODEL (Kiểm tra SQL)
# ==============================================================================

class TestNhaCungCapModel(unittest.TestCase):

    def setUp(self):
        self.model = NhaCungCapModel()

    @patch('src.Model.NhaCungCapModel.mysql.connector.connect')
    def test_insert_curdate(self, mock_connect):
        """Test: Lệnh INSERT phải có CURDATE() để lấy ngày hiện tại"""
        mock_cursor = mock_connect.return_value.cursor.return_value

        self.model.insert("NCC A", "0909", "HCM")

        # Lấy câu SQL đã thực thi
        call_args = mock_cursor.execute.call_args[0]
        sql_query = call_args[0]

        # Kiểm tra logic SQL
        self.assertIn("INSERT INTO nhaCungCap", sql_query)
        self.assertIn("CURDATE()", sql_query)  # Quan trọng: Phải có hàm ngày tháng
        self.assertIn("isActive", sql_query)

    @patch('src.Model.NhaCungCapModel.mysql.connector.connect')
    def test_update_curdate(self, mock_connect):
        """Test: Lệnh UPDATE phải cập nhật ngayCapNhat = CURDATE()"""
        mock_cursor = mock_connect.return_value.cursor.return_value

        self.model.update(1, "NCC B", "0808", "HN")

        sql_query = mock_cursor.execute.call_args[0][0]

        self.assertIn("UPDATE nhaCungCap", sql_query)
        self.assertIn("ngayCapNhat=CURDATE()", sql_query)  # Quan trọng

    @patch('src.Model.NhaCungCapModel.mysql.connector.connect')
    def test_get_all_with_ingredients_query(self, mock_connect):
        """Test: Query lấy danh sách phải có JOIN và GROUP_CONCAT"""
        mock_cursor = mock_connect.return_value.cursor.return_value

        self.model.get_all_with_ingredients()

        sql_query = mock_cursor.execute.call_args[0][0]

        self.assertIn("GROUP_CONCAT", sql_query)  # Kiểm tra logic gộp nguyên liệu
        self.assertIn("LEFT JOIN khoNguyenLieu", sql_query)


# ==============================================================================
# 3. TEST CONTROLLER (Logic Nghiệp vụ & Excel)
# ==============================================================================

class TestNhaCungCapController(unittest.TestCase):

    def setUp(self):
        self.controller = NhaCungCapController()
        self.controller.model = MagicMock()  # Mock Model

    # --- Test Validate Thêm/Sửa ---
    def test_them_ncc_thieu_thong_tin(self):
        # Case 1: Thiếu tên
        success, msg = self.controller.them_ncc("", "0909", "Dia chi")
        self.assertFalse(success)
        self.assertIn("bắt buộc", msg)

        # Case 2: Thiếu SĐT
        success, msg = self.controller.them_ncc("Ten", "", "Dia chi")
        self.assertFalse(success)

    def test_them_ncc_thanh_cong_strip(self):
        """Test: Thêm thành công và tự động xóa khoảng trắng thừa"""
        self.controller.model.insert.return_value = True

        # Input có khoảng trắng đầu cuối
        success, msg = self.controller.them_ncc("  Vinamilk  ", " 0909 ", " HCM ")

        self.assertTrue(success)

        # Kiểm tra dữ liệu truyền xuống Model đã sạch chưa
        self.controller.model.insert.assert_called_with("Vinamilk", "0909", "HCM")

    def test_sua_ncc_thanh_cong(self):
        self.controller.model.update.return_value = True

        success, msg = self.controller.sua_ncc(10, "Moi", "0123", "Da Nang")

        self.assertTrue(success)
        self.controller.model.update.assert_called_with(10, "Moi", "0123", "Da Nang")

    # --- Test Xuất Excel (Mock Pandas) ---
    @patch('src.Controller.NhaCungCapController.pd.DataFrame')
    def test_xuat_excel_thanh_cong(self, mock_df):
        """Test xuất Excel sử dụng thư viện Pandas"""
        mock_df_instance = mock_df.return_value

        # Data giả lập
        data_list = [{
            'tenNhaCungCap': 'NCC A',
            'soDienThoai': '0123',
            'diaChi': 'HCM',
            'danhSachNguyenLieu': 'Sữa, Đường',
            'ngayCapNhat': '2025-01-01',
            'isActive': 1
        }]

        success, msg = self.controller.xuat_excel("ds_ncc.xlsx", data_list)

        self.assertTrue(success)

        # Kiểm tra hàm to_excel được gọi
        mock_df_instance.to_excel.assert_called_once()

        # Kiểm tra DataFrame được khởi tạo với dữ liệu đúng form
        args, _ = mock_df.call_args
        created_data = args[0]  # List dictionary truyền vào DataFrame

        self.assertEqual(created_data[0]['Tên Nhà Cung Cấp'], 'NCC A')
        self.assertEqual(created_data[0]['Nguyên liệu cung cấp'], 'Sữa, Đường')

    def test_xuat_excel_khong_co_du_lieu(self):
        success, msg = self.controller.xuat_excel("test.xlsx", [])
        self.assertFalse(success)
        self.assertEqual(msg, "Không có dữ liệu để xuất!")


if __name__ == '__main__':
    unittest.main()