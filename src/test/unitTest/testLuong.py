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
    from src.Controller.LuongController import LuongController
    from src.Model.LuongModel import LuongModel
except ImportError as e:
    raise ImportError(f"Lỗi Import. Root: {project_root}. Details: {e}")


# ==============================================================================
# 2. TEST MODEL (DATABASE LOGIC)
# ==============================================================================

class TestLuongModel(unittest.TestCase):

    def setUp(self):
        self.model = LuongModel()

    @patch('src.Model.LuongModel.mysql.connector.connect')
    def test_sync_monthly_salary_logic(self, mock_connect):
        """Test: Logic đồng bộ lương (INSERT ... SELECT)"""
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value

        # Act
        self.model.sync_monthly_salary(12, 2025)

        # Assert
        call_args = mock_cursor.execute.call_args[0]
        sql_query = call_args[0]
        params = call_args[1]

        # Kiểm tra câu SQL phải là INSERT (Tính toán lương mới)
        self.assertIn("INSERT INTO luong", sql_query)
        # Kiểm tra có tính toán tiền lương không
        self.assertIn("ROUND((cv.luongCoBan / 26 / 8)", sql_query)
        # Kiểm tra tham số ngày tháng
        self.assertEqual(params, (12, 2025))

        mock_conn.commit.assert_called_once()

    @patch('src.Model.LuongModel.mysql.connector.connect')
    def test_update_payment_status(self, mock_connect):
        """Test: Cập nhật trạng thái thanh toán"""
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value

        # Giả lập update thành công 1 dòng
        mock_cursor.rowcount = 1

        result = self.model.update_payment_status(1, 12, 2025)

        self.assertTrue(result)

        sql_query = mock_cursor.execute.call_args[0][0]
        self.assertIn("SET l.ttThanhToan = 'DaThanhToan'", sql_query)


# ==============================================================================
# 3. TEST CONTROLLER (LOGIC NGHIỆP VỤ & EXPORT)
# ==============================================================================

class TestLuongController(unittest.TestCase):

    def setUp(self):
        self.controller = LuongController()
        self.controller.model = MagicMock()  # Mock Model

    # --- Test 1: Hàm Helper Parse Ngày Tháng ---
    def test_parse_month_year_valid(self):
        m, y = self.controller._parse_month_year("Tháng 12/2025")
        self.assertEqual(m, 12)
        self.assertEqual(y, 2025)

    def test_parse_month_year_invalid(self):
        m, y = self.controller._parse_month_year("Chuoi Linh Tinh")
        self.assertIsNone(m)
        self.assertIsNone(y)

    # --- Test 2: Thanh Toán Lương ---
    def test_thanh_toan_luong_thanh_cong(self):
        self.controller.model.update_payment_status.return_value = True

        success, msg = self.controller.thanh_toan_luong(1, "Tháng 10/2025")

        self.assertTrue(success)
        self.assertIn("Đã cập nhật trạng thái", msg)
        # Kiểm tra gọi model đúng tham số
        self.controller.model.update_payment_status.assert_called_with(1, 10, 2025)

    def test_thanh_toan_luong_loi_dinh_dang(self):
        success, msg = self.controller.thanh_toan_luong(1, "Sai Format")
        self.assertFalse(success)
        self.assertEqual(msg, "Lỗi định dạng tháng!")

    # --- Test 3: Xuất Excel (Mock Pandas) ---
    @patch('src.Controller.LuongController.pd.DataFrame')
    def test_export_excel_success(self, mock_df):
        """Test xuất Excel"""
        # Giả lập dữ liệu trả về từ model
        fake_data = [{
            'idNhanVien': 1, 'hoTen': 'A', 'tenChucVu': 'Staff',
            'luongCoBanSnapshot': 5000000, 'tongGioLamThang': 200,
            'thucLanh': 6000000, 'trangThai': 'ChuaThanhToan'
        }]
        self.controller.model.get_bang_luong_thang.return_value = fake_data

        # Act
        success, msg = self.controller.export_excel("Tháng 12/2025", "salary.xlsx")

        # Assert
        self.assertTrue(success)
        mock_df.return_value.to_excel.assert_called_once()

        # Kiểm tra dữ liệu được đưa vào DataFrame có đúng logic map không
        args, _ = mock_df.call_args
        data_sent_to_df = args[0]

        # Row 1: Nhân viên
        self.assertEqual(data_sent_to_df[0]['Thực Lãnh'], 6000000.0)
        self.assertEqual(data_sent_to_df[0]['Trạng Thái'], "Chưa thanh toán")

        # Row 2: Tổng cộng (Logic controller tự thêm dòng tổng)
        self.assertEqual(data_sent_to_df[-1]['Họ Tên'], "TỔNG CỘNG")
        self.assertEqual(data_sent_to_df[-1]['Thực Lãnh'], 6000000.0)

    # --- Test 4: Xuất PDF (Mock ReportLab) ---
    @patch('src.Controller.LuongController.canvas.Canvas')
    @patch('src.Controller.LuongController.os.path.exists')  # Mock check font
    def test_export_pdf_success(self, mock_exists, mock_canvas):
        """Test xuất PDF"""
        mock_exists.return_value = False  # Giả lập không có font để dùng Helvetica
        mock_pdf = mock_canvas.return_value

        # Giả lập dữ liệu
        fake_data = [{
            'idNhanVien': 1, 'hoTen': 'Nguyen Van A', 'tenChucVu': 'Quan Ly',
            'luongCoBanSnapshot': 10000000, 'tongGioLamThang': 100,
            'thucLanh': 5000000, 'trangThai': 'DaThanhToan'
        }]
        self.controller.model.get_bang_luong_thang.return_value = fake_data

        # Act
        success, msg = self.controller.export_pdf("Tháng 12/2025", "salary.pdf")

        # Assert
        self.assertTrue(success)

        # Lấy các text đã vẽ
        calls = mock_pdf.drawString.call_args_list
        drawn_texts = [call[0][2] for call in calls]

        # Kiểm tra các thông tin quan trọng có trên PDF
        self.assertTrue(any("NGUYEN VAN A" in txt or "Nguyen Van A" in txt for txt in drawn_texts))
        self.assertTrue(any("Quan Ly" in txt for txt in drawn_texts))
        self.assertTrue(any("5,000,000" in txt for txt in drawn_texts))  # Format tiền

        # Kiểm tra tiêu đề
        # drawCentredString là hàm khác drawString, cần check riêng nếu muốn kỹ
        # Nhưng check drawString dữ liệu là đủ chứng minh loop chạy đúng.

        mock_pdf.save.assert_called_once()

    def test_export_pdf_no_data(self):
        self.controller.model.get_bang_luong_thang.return_value = []
        success, msg = self.controller.export_pdf("Tháng 12/2025", "test.pdf")
        self.assertFalse(success)
        self.assertEqual(msg, "Không có dữ liệu!")


if __name__ == '__main__':
    unittest.main()