import unittest
import sys
import os
from unittest.mock import patch, MagicMock, ANY
from datetime import datetime

# ==============================================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN TỰ ĐỘNG
# ==============================================================================
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.Controller.HoaDonController import HoaDonController
    from src.Model.HoaDonModel import HoaDonModel
except ImportError as e:
    raise ImportError(f"Lỗi Import. Root: {project_root}. Details: {e}")


# ==============================================================================
# 2. TEST MODEL (DATABASE & TRANSACTION)
# ==============================================================================

class TestHoaDonModel(unittest.TestCase):

    def setUp(self):
        self.model = HoaDonModel()

    @patch('src.Model.HoaDonModel.mysql.connector.connect')
    def test_filter_invoices_query_builder(self, mock_connect):
        """Test xem SQL động có được tạo đúng khi lọc theo Năm và Từ khóa không"""
        mock_cursor = mock_connect.return_value.cursor.return_value

        # Act: Lọc theo năm 2025 và từ khóa "HD01"
        self.model.filter_invoices(year="2025", keyword="HD01")

        # Assert: Kiểm tra câu SQL được thực thi
        call_args = mock_cursor.execute.call_args[0]
        sql_query = call_args[0]
        params = call_args[1]

        # SQL phải chứa điều kiện lọc năm và tìm kiếm
        self.assertIn("YEAR(hd.ngayTao) =", sql_query)
        self.assertIn("LIKE %s", sql_query)

        # Params phải chứa đúng giá trị
        self.assertIn("2025", params)
        self.assertIn("%HD01%", params)

    @patch('src.Model.HoaDonModel.mysql.connector.connect')
    def test_update_invoice_full_transaction_success(self, mock_connect):
        """
        Test cập nhật hóa đơn (Sửa món).
        Logic quan trọng: Phải chạy trong Transaction (Start -> Update -> Delete -> Insert -> Commit)
        """
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value

        # Data giả lập: Hóa đơn ID 1, Trạng thái 2, Mua 2 món
        items = [
            {'idSanPham': 10, 'soLuong': 2, 'donGia': 50000},  # 100k
            {'idSanPham': 20, 'soLuong': 1, 'donGia': 30000}  # 30k
        ]

        # Act
        result = self.model.update_invoice_full_transaction(1, 2, items)

        # Assert
        self.assertTrue(result)

        # 1. Kiểm tra Transaction được bắt đầu và commit
        mock_conn.start_transaction.assert_called_once()
        mock_conn.commit.assert_called_once()

        # 2. Kiểm tra trình tự gọi SQL
        # Lấy danh sách các câu lệnh SQL đã chạy
        calls = [str(call[0][0]).strip() for call in mock_cursor.execute.call_args_list]

        # Phải có UPDATE trạng thái
        self.assertTrue(any("UPDATE hoaDon SET trangThai" in s for s in calls))
        # Phải có DELETE chi tiết cũ
        self.assertTrue(any("DELETE FROM chiTietHoaDon" in s for s in calls))
        # Phải có INSERT chi tiết mới
        self.assertTrue(any("INSERT INTO chiTietHoaDon" in s for s in calls))
        # Phải có UPDATE tổng tiền (100k + 30k + VAT)
        self.assertTrue(any("UPDATE hoaDon SET tongTien" in s for s in calls))

    @patch('src.Model.HoaDonModel.mysql.connector.connect')
    def test_update_invoice_rollback(self, mock_connect):
        """Test Rollback: Nếu Insert bị lỗi thì Database phải hoàn tác"""
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value

        # Giả lập: Lệnh execute bị lỗi ở bất kỳ bước nào
        mock_cursor.execute.side_effect = Exception("DB Error")

        result = self.model.update_invoice_full_transaction(1, 2, [])

        self.assertFalse(result)
        mock_conn.rollback.assert_called_once()  # Phải gọi Rollback


# ==============================================================================
# 3. TEST CONTROLLER (LOGIC HIỂN THỊ & PDF)
# ==============================================================================

class TestHoaDonController(unittest.TestCase):

    def setUp(self):
        self.controller = HoaDonController()
        self.controller.model = MagicMock()  # Mock Model

    # --- Test Logic Process Data (Hiển thị) ---

    def test_process_data_ck_hien_thi_noi_dung(self):
        """Test: Nếu có nội dung CK thì hiển thị nó thay vì ID hóa đơn"""
        raw_data = [{
            'idHoaDon': 10, 'noiDungCK': 'MOMO-1234',
            'ngayTao': datetime(2025, 1, 1), 'tongTien': 50000,
            'trangThai': 2, 'tenNganHang': 'MB', 'soTaiKhoan': '9999'
        }]

        processed = self.controller.process_data(raw_data)
        item = processed[0]

        # Kiểm tra logic ưu tiên NoiDungCK
        self.assertEqual(item['maHienThi'], 'MOMO-1234')
        # Kiểm tra hiển thị phương thức thanh toán
        self.assertIn("CK (MB", item['paymentMethod'])

    def test_process_data_tien_mat(self):
        """Test: Nếu không có ngân hàng -> Tiền mặt"""
        raw_data = [{
            'idHoaDon': 11, 'noiDungCK': None,
            'ngayTao': datetime(2025, 1, 1), 'tongTien': 100000,
            'trangThai': 2, 'tenNganHang': None, 'soTaiKhoan': None
        }]

        processed = self.controller.process_data(raw_data)
        item = processed[0]

        self.assertEqual(item['maHienThi'], '#11')  # Fallback về ID
        self.assertEqual(item['paymentMethod'], 'Tiền mặt')
        self.assertEqual(item['statusText'], 'Đã thanh toán')
        self.assertEqual(item['tongTienFmt'], '100,000 VNĐ')

    # --- Test Logic Sửa Hóa Đơn ---

    def test_save_edited_invoice_validation(self):
        """Test validate dữ liệu đầu vào khi sửa"""
        # Case: Trạng thái không hợp lệ
        success, msg = self.controller.save_edited_invoice(1, "Trạng thái lạ", [])
        self.assertFalse(success)
        self.assertEqual(msg, "Trạng thái không hợp lệ!")

        # Case: Xóa hết món nhưng vẫn để trạng thái 'Đã thanh toán' (Logic sai)
        success, msg = self.controller.save_edited_invoice(1, "Đã thanh toán", [])  # List rỗng
        self.assertFalse(success)
        self.assertIn("ít nhất 1 món", msg)

    def test_save_edited_invoice_success(self):
        """Test gọi Model update thành công"""
        self.controller.model.update_invoice_full_transaction.return_value = True

        items = [{'id': 1, 'qty': 1}]
        success, msg = self.controller.save_edited_invoice(1, "Đã thanh toán", items)

        self.assertTrue(success)
        # Kiểm tra status text được map sang code (Đã thanh toán -> 2)
        self.controller.model.update_invoice_full_transaction.assert_called_with(1, 2, items)

    # --- Test Xuất PDF (Mock ReportLab) ---

    @patch('src.Controller.HoaDonController.canvas.Canvas')
    @patch('src.Controller.HoaDonController.os.path.exists')
    def test_export_invoice_pdf_success(self, mock_exists, mock_canvas):
        """Test luồng xuất PDF thành công"""
        # 1. Setup Mock
        mock_exists.return_value = False  # Giả lập KHÔNG có font -> Chuyển sang KHÔNG DẤU
        mock_pdf = mock_canvas.return_value

        # Mock dữ liệu: ID là 123
        self.controller.model.filter_invoices.return_value = [{
            'idHoaDon': 123,
            'noiDungCK': 'CK-CODE',
            'ngayTao': datetime.now(), 'tongTien': 50000,
            'trangThai': 2, 'tenNganHang': 'VCB', 'soTaiKhoan': '123',
            'tenKhachHang': 'Huy', 'tenNhanVien': 'Staff'
        }]
        self.controller.model.get_invoice_details.return_value = [
            {'tenSanPham': 'Cafe', 'soLuong': 1, 'donGia': 25000, 'thanhTien': 25000}
        ]

        # 2. Act
        success, msg = self.controller.export_invoice_pdf(123, "test_invoice.pdf")

        # 3. Assert
        self.assertTrue(success)

        # Lấy danh sách text được vẽ lên PDF
        calls = mock_pdf.drawString.call_args_list
        drawn_texts = [call[0][2] for call in calls]

        print("\n[DEBUG] Các dòng chữ được vẽ lên PDF:", drawn_texts)

        # [SỬA LẠI]: Tìm chuỗi "Ma hoa đon" (chữ đ) thay vì "don"
        self.assertTrue(any("Ma hoa đon: #123" in txt for txt in drawn_texts),
                        f"Không tìm thấy ID #123. Danh sách text: {drawn_texts}")

        self.assertTrue(any("Ref: CK-CODE" in txt for txt in drawn_texts))
        self.assertTrue(any("Cafe" in txt for txt in drawn_texts))

        mock_pdf.save.assert_called_once()

    def test_export_invoice_pdf_not_found(self):
        """Test trường hợp ID không tồn tại"""
        self.controller.model.filter_invoices.return_value = []  # Không tìm thấy

        success, msg = self.controller.export_invoice_pdf(999, "abc.pdf")

        self.assertFalse(success)
        self.assertIn("Không tìm thấy", msg)


if __name__ == '__main__':
    unittest.main()