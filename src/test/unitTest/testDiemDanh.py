import unittest
import sys
import os
import shutil
from datetime import datetime
from unittest.mock import patch, MagicMock, ANY

# ==============================================================================
# FIX ĐƯỜNG DẪN (Để Python tìm thấy src)
# ==============================================================================
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.Model.DiemDanhModel import DiemDanhModel
    from src.Controller.DiemDanhController import DiemDanhController
except ImportError as e:
    raise ImportError(f"Lỗi Import: {e}")


# ==============================================================================
# TEST CASES
# ==============================================================================

class TestDiemDanhModel(unittest.TestCase):
    """Kiểm tra Logic Database và Nghiệp vụ Chấm công"""

    def setUp(self):
        self.model = DiemDanhModel()

    @patch('src.Model.DiemDanhModel.mysql.connector.connect')
    def test_xu_ly_cham_cong_check_in(self, mock_connect):
        """Test trường hợp Check-in (Chưa có dữ liệu trong ngày)"""
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value

        # Giả lập: Không tìm thấy bản ghi nào hôm nay
        mock_cursor.fetchone.return_value = None

        # Act
        success, type_cc, hours = self.model.xu_ly_cham_cong(1)

        # Assert
        self.assertTrue(success)
        self.assertEqual(type_cc, "CHECK-IN")
        self.assertEqual(hours, 0.0)

        # Kiểm tra lệnh INSERT được gọi
        call_args = mock_cursor.execute.call_args_list
        self.assertIn("INSERT INTO bangChamCong", call_args[1][0][0])

    @patch('src.Model.DiemDanhModel.mysql.connector.connect')
    @patch('src.Model.DiemDanhModel.datetime')
    def test_xu_ly_cham_cong_check_out_normal(self, mock_datetime, mock_connect):
        """Test Check-out bình thường (< 8.5 tiếng)"""
        mock_cursor = mock_connect.return_value.cursor.return_value

        # Setup thời gian: Vào lúc 8:00, Ra lúc 12:00 (Làm 4 tiếng)
        fake_now = datetime(2025, 12, 16, 12, 0, 0)
        gio_vao = datetime(2025, 12, 16, 8, 0, 0)

        # Mock datetime.now()
        mock_datetime.now.return_value = fake_now

        # Giả lập DB trả về bản ghi Check-in
        mock_cursor.fetchone.return_value = {'idChamCong': 10, 'gioVao': gio_vao}

        # Act
        success, type_cc, hours = self.model.xu_ly_cham_cong(1)

        # Assert
        self.assertTrue(success)
        self.assertEqual(type_cc, "CHECK-OUT")
        self.assertEqual(hours, 4.0)

    @patch('src.Model.DiemDanhModel.mysql.connector.connect')
    @patch('src.Model.DiemDanhModel.datetime')
    def test_xu_ly_cham_cong_check_out_overtime(self, mock_datetime, mock_connect):
        """Test Check-out > 8.5 tiếng -> Chỉ tính 8 tiếng"""
        mock_cursor = mock_connect.return_value.cursor.return_value

        # Setup: Làm 10 tiếng
        fake_now = datetime(2025, 12, 16, 18, 0, 0)
        gio_vao = datetime(2025, 12, 16, 8, 0, 0)

        mock_datetime.now.return_value = fake_now
        mock_cursor.fetchone.return_value = {'idChamCong': 10, 'gioVao': gio_vao}

        # Act
        success, type_cc, hours = self.model.xu_ly_cham_cong(1)

        # Assert
        self.assertEqual(hours, 8.0)  # Phải bị cắt xuống 8.0


class TestDiemDanhController(unittest.TestCase):
    """Kiểm tra Logic Controller (File, Train model, Excel)"""

    def setUp(self):
        # Mock các thư viện nặng trước khi khởi tạo Controller
        with patch('src.Controller.DiemDanhController.cv2'), \
                patch('src.Controller.DiemDanhController.os.makedirs'):
            self.controller = DiemDanhController()
            self.controller.model = MagicMock()  # Mock Model

    # --- Test 1: Tiện ích ---
    def test_remove_accents(self):
        self.assertEqual(self.controller.remove_accents("Nguyễn Văn A"), "Nguyen Van A")
        self.assertEqual(self.controller.remove_accents("Đường Đời"), "Duong Doi")

    # --- Test 2: Xóa dữ liệu khuôn mặt ---
    @patch('src.Controller.DiemDanhController.shutil.rmtree')
    @patch('src.Controller.DiemDanhController.os.path.exists')
    def test_delete_face_data_success(self, mock_exists, mock_rmtree):
        """Test xóa dữ liệu thành công"""
        mock_exists.return_value = True  # Giả lập thư mục tồn tại

        # Mock hàm train_model để không chạy thật
        self.controller.train_model = MagicMock(return_value=True)

        success, msg = self.controller.delete_face_data(1)

        self.assertTrue(success)
        mock_rmtree.assert_called_once()  # Phải gọi lệnh xóa thư mục
        self.controller.train_model.assert_called_once()  # Phải gọi train lại

    @patch('src.Controller.DiemDanhController.os.path.exists')
    def test_delete_face_data_not_found(self, mock_exists):
        """Test xóa nhân viên không có dữ liệu"""
        mock_exists.return_value = False
        success, msg = self.controller.delete_face_data(999)
        self.assertFalse(success)
        self.assertIn("chưa có dữ liệu", msg)

    # --- Test 3: Train Model ---
    @patch('src.Controller.DiemDanhController.os.walk')
    @patch('src.Controller.DiemDanhController.os.remove')
    @patch('src.Controller.DiemDanhController.os.path.exists')
    def test_train_model_no_faces(self, mock_exists, mock_remove, mock_walk):
        """Test trường hợp không còn ảnh nào -> Phải xóa file model"""
        # Giả lập os.walk không trả về file nào
        mock_walk.return_value = []
        mock_exists.return_value = True  # File model cũ đang tồn tại

        self.controller.train_model()

        # Kiểm tra xem có xóa file model cũ không
        mock_remove.assert_called_with(self.controller.TRAINER_FILE)

    # --- Test 4: Xuất Excel ---
    @patch('src.Controller.DiemDanhController.pd.DataFrame')
    def test_export_excel(self, mock_df):
        """Test xuất Excel"""
        # [SỬA LẠI ĐOẠN NÀY] Cung cấp đầy đủ dữ liệu giả lập cho Mock
        fake_data = [{
            'Ngay': '2025-01-01',
            'GioVao': '08:00:00',  # Thêm trường này
            'GioRa': '17:00:00',  # Thêm trường này
            'tongGioLam': 8.0  # Thêm trường này
        }]
        self.controller.model.get_individual_attendance.return_value = fake_data

        success, msg = self.controller.export_excel_individual(1, "Huy", "12/2025")

        self.assertTrue(success)
        mock_df.return_value.to_excel.assert_called_once()


if __name__ == '__main__':
    unittest.main()