import unittest
import sys
import os
from unittest.mock import patch, MagicMock, ANY
from datetime import datetime

# ==============================================================================
# 1. FIX ĐƯỜNG DẪN TỰ ĐỘNG
# ==============================================================================
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.Controller.ThongKeController import ThongKeController
    from src.Model.ThongKeModel import ThongKeModel
except ImportError as e:
    raise ImportError(f"Lỗi Import. Root: {project_root}. Details: {e}")


# ==============================================================================
# 2. TEST MODEL
# ==============================================================================

class TestThongKeModel(unittest.TestCase):

    def setUp(self):
        self.model = ThongKeModel()

    @patch('src.Model.ThongKeModel.mysql.connector.connect')
    def test_get_overview_stats_full_params(self, mock_connect):
        """Test query SQL khi lọc đầy đủ Tháng và Năm"""
        mock_cursor = mock_connect.return_value.cursor.return_value

        # Giả lập kết quả trả về từ DB
        mock_cursor.fetchone.return_value = {'doanhThu': 100, 'tongDon': 10, 'khachMoi': 5}

        result = self.model.get_overview_stats(month=12, year=2025)

        # Kiểm tra logic SQL
        call_args = mock_cursor.execute.call_args
        sql_query = call_args[0][0]
        params = call_args[0][1]

        self.assertIn("YEAR(ngayTao) =", sql_query)
        self.assertIn("MONTH(ngayTao) =", sql_query)
        self.assertEqual(params, (2025, 12))

        self.assertEqual(result['doanhThu'], 100)

    @patch('src.Model.ThongKeModel.mysql.connector.connect')
    def test_get_detailed_stats_7_days(self, mock_connect):
        """Test logic lọc 7 ngày gần nhất"""
        mock_cursor = mock_connect.return_value.cursor.return_value

        self.model.get_detailed_stats(mode="7_days")

        sql_query = mock_cursor.execute.call_args[0][0]

        # Phải có điều kiện >= ngày_cách_đây_7_hôm
        self.assertIn("ngayTao >=", sql_query)

    @patch('src.Model.ThongKeModel.mysql.connector.connect')
    def test_get_detailed_stats_year_mode(self, mock_connect):
        """Test logic lọc theo Năm (Format ngày phải là YYYY-MM)"""
        mock_cursor = mock_connect.return_value.cursor.return_value

        self.model.get_detailed_stats(mode="year", year=2025)

        sql_query = mock_cursor.execute.call_args[0][0]

        # Phải dùng DATE_FORMAT để gom nhóm theo tháng
        self.assertIn("DATE_FORMAT(ngayTao, '%Y-%m')", sql_query)


# ==============================================================================
# 3. TEST CONTROLLER
# ==============================================================================

class TestThongKeController(unittest.TestCase):

    def setUp(self):
        self.controller = ThongKeController()
        self.controller.model = MagicMock()  # Mock Model

    # --- Test 1: Tiện ích Format ---
    def test_format_money(self):
        self.assertEqual(self.controller.format_money(1000000), "1,000,000 ₫")
        self.assertEqual(self.controller.format_money(0), "0 ₫")
        self.assertEqual(self.controller.format_money(None), "0 ₫")

    def test_format_date_vn(self):
        # Mode ngày thường
        self.assertEqual(self.controller.format_date_vn("2025-12-01", "day"), "01/12/2025")
        # Mode năm (Group by month)
        self.assertEqual(self.controller.format_date_vn("2025-12", "year"), "T12")
        # Sai định dạng -> Trả về nguyên gốc
        self.assertEqual(self.controller.format_date_vn("abc", "day"), "abc")

    # --- Test 2: Get Dashboard Summary ---
    def test_get_dashboard_summary(self):
        # Setup Mock Model
        self.controller.model.get_overview_stats.return_value = {
            'doanhThu': 500000, 'tongDon': 20, 'khachMoi': 5
        }

        # Act
        summary = self.controller.get_dashboard_summary("12", "2025")

        # Assert
        self.assertEqual(summary['doanh_thu'], "500,000 ₫")
        self.assertEqual(summary['tong_don'], "20 Đơn")
        # Kiểm tra gọi model đúng tham số
        self.controller.model.get_overview_stats.assert_called_with(12, 2025)

    # --- Test 3: Get Chart Data ---
    def test_get_chart_and_table_data(self):
        # Setup Data trả về từ DB: 2 dòng
        fake_db_data = [
            {'thoiGian': '2025-12-01', 'soDonHang': 5, 'doanhThu': 100000},
            {'thoiGian': '2025-12-02', 'soDonHang': 8, 'doanhThu': 200000}
        ]
        self.controller.model.get_detailed_stats.return_value = fake_db_data

        # Act: Lọc theo tháng
        labels, values, rows = self.controller.get_chart_and_table_data("month", "12", "2025")

        # Assert
        # 1. Labels phải format ra ngày VN
        self.assertEqual(labels, ['01/12/2025', '02/12/2025'])
        # 2. Values là doanh thu (float)
        self.assertEqual(values, [100000.0, 200000.0])
        # 3. Rows cho bảng
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][2], "100,000 ₫")  # Cột thứ 3 là tiền đã format

    # --- Test 4: Xuất Excel (Mock Pandas) ---
    @patch('src.Controller.ThongKeController.pd.ExcelWriter')  # Mock hàm ghi file
    @patch('src.Controller.ThongKeController.pd.DataFrame')  # Mock cấu trúc bảng
    def test_export_excel_success(self, mock_df, mock_writer):
        """Test xuất Excel nhiều sheet"""

        # Setup dữ liệu giả
        self.controller.model.get_overview_stats.return_value = {'doanhThu': 0, 'tongDon': 0, 'khachMoi': 0}
        self.controller.model.get_detailed_stats.return_value = []

        # Act
        success, msg = self.controller.export_report_to_excel("report.xlsx", "month", "12", "2025")

        # Assert
        self.assertTrue(success)
        self.assertIn("thành công", msg)

        # Kiểm tra quy trình ghi file Excel
        # 1. Phải khởi tạo ExcelWriter
        mock_writer.assert_called_with("report.xlsx", engine='openpyxl')

        # 2. Phải ghi 2 sheet: Tổng quan và Chi tiết
        # mock_df() tạo ra instance DataFrame giả
        df_instance = mock_df.return_value
        # Kiểm tra xem hàm to_excel có được gọi ít nhất 2 lần không (cho 2 sheet)
        self.assertTrue(df_instance.to_excel.call_count >= 2)

    def test_export_excel_fail(self):
        """Test trường hợp lỗi (ví dụ file đang mở)"""
        # Giả lập lỗi khi gọi Model
        self.controller.model.get_overview_stats.side_effect = Exception("Disk Error")

        success, msg = self.controller.export_report_to_excel("report.xlsx", "month", "12", "2025")

        self.assertFalse(success)
        self.assertIn("Lỗi xuất Excel", msg)


if __name__ == '__main__':
    unittest.main()