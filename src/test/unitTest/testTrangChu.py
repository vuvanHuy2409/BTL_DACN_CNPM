import unittest
from unittest.mock import patch, MagicMock, ANY, call
import sys
import os

# --- CẤU HÌNH ĐƯỜNG DẪN ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../..'))
sys.path.insert(0, project_root)
# ---------------------------

from src.Controller.TrangChuController import TrangChuController
from src.Model.TrangChuModel import TrangChuModel


class TestTrangChuModel(unittest.TestCase):
    """Kiểm tra các hàm thao tác Database trong Model"""

    def setUp(self):
        self.model = TrangChuModel()

    @patch('src.Model.TrangChuModel.mysql.connector.connect')
    def test_get_active_invoice_id(self, mock_connect):
        """Test lấy ID hóa đơn đang hoạt động"""
        mock_cursor = mock_connect.return_value.cursor.return_value
        # Giả lập DB trả về kết quả
        mock_cursor.fetchone.return_value = {'idHoaDon': 100}

        result = self.model.get_active_invoice_id(5)  # Bàn số 5

        self.assertEqual(result, 100)
        # Kiểm tra query
        query_args = mock_cursor.execute.call_args[0][1]
        self.assertEqual(query_args, (5,))

    @patch('src.Model.TrangChuModel.mysql.connector.connect')
    def test_add_or_update_item_insert_new(self, mock_connect):
        """Test thêm món mới (chưa tồn tại trong hóa đơn)"""
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value

        # Giả lập chưa có món này
        mock_cursor.fetchone.return_value = None

        self.model.add_or_update_item(1, 10, 2, 50000)

        # Kiểm tra gọi lệnh INSERT
        # Lấy tất cả các lần gọi execute
        calls = mock_cursor.execute.call_args_list
        # Lần gọi cuối cùng phải là INSERT
        last_call_query = calls[-1][0][0]
        self.assertIn("INSERT INTO chiTietHoaDon", last_call_query)
        mock_conn.commit.assert_called()

    @patch('src.Model.TrangChuModel.mysql.connector.connect')
    def test_add_or_update_item_update_existing(self, mock_connect):
        """Test cập nhật số lượng món đã có"""
        mock_cursor = mock_connect.return_value.cursor.return_value

        # Giả lập đã có 1 món
        mock_cursor.fetchone.return_value = {'soLuong': 1}

        self.model.add_or_update_item(1, 10, 2, 50000)  # Thêm 2 món nữa

        # Kiểm tra logic cộng dồn: 1 + 2 = 3
        calls = mock_cursor.execute.call_args_list
        update_args = calls[-1][0][1]  # Lấy tham số của lệnh UPDATE
        self.assertEqual(update_args[0], 3)  # new_qty phải là 3


class TestTrangChuController(unittest.TestCase):
    """Kiểm tra Logic nghiệp vụ trong Controller"""

    def setUp(self):
        self.controller = TrangChuController()
        # MOCK MODEL: Thay thế model thật bằng bản giả để không đụng DB
        self.controller.model = MagicMock()
        # Mock thư mục hóa đơn để không tạo file thật
        self.controller.invoice_dir = "/tmp_test"

    # --- 1. Test các hàm tiện ích (Utils) ---
        def test_remove_accents(self):
            self.assertEqual(self.controller.remove_accents("Cà Phê Sữa"), "Ca Phe Sua")
            self.assertEqual(self.controller.remove_accents("Đường"), "Duong")
    def test_format_money(self):
        self.assertEqual(self.controller.format_money(50000), "50,000")
        self.assertEqual(self.controller.format_money(1000000), "1,000,000")

    # --- 2. Test Logic Giỏ hàng & Tính tiền ---
    def test_add_to_cart_no_table(self):
        """Test thêm vào giỏ khi chưa chọn bàn"""
        self.controller.selected_table_id = None
        success, msg = self.controller.add_to_cart({}, 1)
        self.assertFalse(success)
        self.assertEqual(msg, "Chưa chọn bàn!")

    def test_calculate_cart_totals_normal(self):
        """Test tính tiền khách thường (Không giảm giá)"""
        self.controller.selected_table_id = 1
        # Giả lập ID hóa đơn
        self.controller.model.get_active_invoice_id.return_value = 100

        # Giả lập chi tiết hóa đơn (thanhTien đã có VAT từ DB generated column)
        self.controller.model.get_invoice_details.return_value = [
            {'tenSanPham': 'Cafe', 'soLuong': 2, 'thanhTien': 50000},  # 2 ly
            {'tenSanPham': 'Tra', 'soLuong': 1, 'thanhTien': 30000}  # 1 ly
        ]

        # Giả lập khách hàng (Điểm thấp < 200)
        self.controller.model.get_invoice_customer.return_value = {'diemTichLuy': 50}

        # Act
        items, subtotal, discount, final_total, is_applied = self.controller.calculate_cart_totals()

        # Assert
        self.assertEqual(subtotal, 80000)  # 50k + 30k
        self.assertEqual(discount, 0)
        self.assertEqual(final_total, 80000)
        self.assertFalse(is_applied)

    def test_calculate_cart_totals_vip(self):
        """Test tính tiền khách VIP (Giảm 10%)"""
        self.controller.selected_table_id = 1
        self.controller.model.get_active_invoice_id.return_value = 100

        self.controller.model.get_invoice_details.return_value = [
            {'tenSanPham': 'Cafe', 'soLuong': 1, 'thanhTien': 100000}
        ]

        # Giả lập khách VIP (Điểm >= 200)
        self.controller.model.get_invoice_customer.return_value = {'diemTichLuy': 250}

        # Act
        items, subtotal, discount, final_total, is_applied = self.controller.calculate_cart_totals()

        # Assert
        self.assertEqual(subtotal, 100000)
        self.assertEqual(discount, 10000)  # 10% của 100k
        self.assertEqual(final_total, 90000)
        self.assertTrue(is_applied)

    # --- 3. Test Quy trình thanh toán (Quan trọng nhất) ---

    # Patch requests để không gọi API VietQR thật
    # Patch canvas để không tạo file PDF thật
    @patch('src.Controller.TrangChuController.requests.get')
    @patch('src.Controller.TrangChuController.canvas.Canvas')
    def test_process_payment_vip(self, mock_canvas, mock_requests):
        """Test thanh toán cho khách VIP: Trừ điểm và Cộng điểm"""
        # Setup
        self.controller.selected_table_id = 1
        self.controller.model.get_active_invoice_id.return_value = 999
        self.controller.model.get_invoice_general_info.return_value = {
            'tenNhanVien': 'NV A', 'tenKhachHang': 'Khach VIP'
        }

        # Giả lập hóa đơn 100k, khách VIP
        self.controller.model.get_invoice_details.return_value = [
            {'tenSanPham': 'A', 'soLuong': 1, 'thanhTien': 100000}
        ]
        mock_customer = {'idKhachHang': 555, 'diemTichLuy': 300}
        self.controller.model.get_invoice_customer.return_value = mock_customer

        # Giả lập Model update DB thành công
        self.controller.model.finalize_invoice.return_value = True

        # Act
        success, msg = self.controller.process_payment(method="TienMat")

        # Assert
        self.assertTrue(success)

        # [QUAN TRỌNG] Kiểm tra logic điểm thưởng
        # Phải gọi trừ 200 điểm (do VIP) và cộng 10 điểm (do mua hàng)
        expected_calls = [
            call(555, -200),  # Trừ điểm VIP
            call(555, 10)  # Cộng điểm mua hàng
        ]
        self.controller.model.add_loyalty_points.assert_has_calls(expected_calls, any_order=True)

        # Kiểm tra logic chốt hóa đơn
        # Phải gọi finalize_invoice với status=2 (Đã thanh toán)
        self.controller.model.finalize_invoice.assert_called_with(
            999, 2, 90000.0, None, ANY  # Tổng tiền sau giảm là 90k
        )

        # Kiểm tra PDF có được "vẽ" không
        mock_canvas.assert_called()

    @patch('src.Controller.TrangChuController.canvas.Canvas')
    def test_create_pdf_fail(self, mock_canvas):
        """Test trường hợp tạo PDF bị lỗi"""
        # Giả lập Canvas ném lỗi
        mock_canvas.side_effect = Exception("Disk full")

        result = self.controller.create_pdf("test.pdf", {}, [], {})
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()