import unittest
import mysql.connector
import os
import sys
import shutil
import time
import cv2
import numpy as np
from datetime import datetime, timedelta

# ==============================================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN
# ==============================================================================
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.Controller.DiemDanhController import DiemDanhController
from src.config.db_config import DB_CONFIG


class TestDiemDanhIntegration(unittest.TestCase):
    """
    KIỂM THỬ TÍCH HỢP: ĐIỂM DANH & NHẬN DIỆN KHUÔN MẶT
    """

    # Hằng số Test Data
    TEST_PHONE = '0000'
    TEST_EMAIL = 'face@test.com'

    def setUp(self):
        """CHẠY TRƯỚC MỖI TEST: Tạo nhân viên test & Môi trường"""
        self.conn = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor(dictionary=True)
        self.controller = DiemDanhController()

        # Tạo thư mục tạm nếu chưa có
        if not os.path.exists(self.controller.FACE_DIR):
            os.makedirs(self.controller.FACE_DIR)

        # 1. [QUAN TRỌNG] Dọn dẹp dữ liệu cũ TRƯỚC KHI TẠO
        self.cleanup_test_data()

        # 2. Tạo Chức vụ (Get or Create)
        self.cursor.execute("SELECT idChucVu FROM chucVu WHERE tenChucVu = 'TestRole'")
        res = self.cursor.fetchone()
        if res:
            self.id_chuc_vu = res['idChucVu']
        else:
            self.cursor.execute("INSERT INTO chucVu (tenChucVu, luongCoBan) VALUES ('TestRole', 1000)")
            self.id_chuc_vu = self.cursor.lastrowid

        # 3. Tạo Nhân viên Test (SĐT 0000)
        # Vì đã chạy cleanup_test_data() nên chắc chắn không bị Duplicate
        self.cursor.execute("""
            INSERT INTO nhanVien (hoTen, email, soDienThoai, idChucVu, trangThaiLamViec)
            VALUES ('Face Test User', %s, %s, %s, 'DangLamViec')
        """, (self.TEST_EMAIL, self.TEST_PHONE, self.id_chuc_vu))
        self.id_nv = self.cursor.lastrowid

        self.conn.commit()

    def tearDown(self):
        """CHẠY SAU MỖI TEST: Xóa dữ liệu & File rác"""
        self.cleanup_test_data()

        # Xóa thư mục face data của nhân viên test (nếu có id_nv)
        if hasattr(self, 'id_nv'):
            user_dir = os.path.join(self.controller.FACE_DIR, f"face_{self.id_nv}")
            if os.path.exists(user_dir):
                shutil.rmtree(user_dir)

        if self.conn.is_connected():
            self.cursor.close()
            self.conn.close()

    def cleanup_test_data(self):
        """Xóa sạch dữ liệu test để tránh lỗi Duplicate"""
        try:
            # Bước 1: Tìm tất cả ID nhân viên có SĐT '0000' hoặc Email test
            # (Phải tìm ID để xóa các bảng liên quan trước)
            self.cursor.execute("""
                SELECT idNhanVien FROM nhanVien 
                WHERE soDienThoai = %s OR email = %s
            """, (self.TEST_PHONE, self.TEST_EMAIL))

            rows = self.cursor.fetchall()

            for row in rows:
                uid = row['idNhanVien']

                # Xóa bảng chấm công (Foreign Key)
                self.cursor.execute("DELETE FROM bangChamCong WHERE idNhanVien = %s", (uid,))

                # Xóa bảng lương (Nếu có test nào lỡ tạo lương)
                self.cursor.execute("DELETE FROM luong WHERE idNhanVien = %s", (uid,))

                # Xóa bảng hóa đơn (Nếu test bán hàng lỡ dùng nhân viên này)
                self.cursor.execute("DELETE FROM hoaDon WHERE idNhanVien = %s", (uid,))

                # Cuối cùng xóa nhân viên
                self.cursor.execute("DELETE FROM nhanVien WHERE idNhanVien = %s", (uid,))

            self.conn.commit()

        except Exception as e:
            print(f"Cleanup Warning: {e}")
            # Cố gắng rollback nếu lỗi để không treo DB
            try:
                self.conn.rollback()
            except:
                pass

    # ==========================================================================
    # PHẦN 1: TEST LOGIC DATABASE (CHECK-IN / CHECK-OUT)
    # ==========================================================================

    def test_attendance_flow_normal(self):
        """Test 1: Luồng Check-in -> Check-out (Giả lập làm việc 1 tiếng)"""

        # 1. Check-in (Lần đầu trong ngày)
        ok, type_cc, hours = self.controller.model.xu_ly_cham_cong(self.id_nv)

        self.assertTrue(ok)
        self.assertEqual(type_cc, "CHECK-IN")
        self.assertEqual(hours, 0.0)

        # Verify DB
        self.cursor.execute("SELECT * FROM bangChamCong WHERE idNhanVien = %s AND DATE(gioVao) = CURDATE()",
                            (self.id_nv,))
        record = self.cursor.fetchone()
        self.assertIsNotNone(record)
        self.assertIsNone(record['gioRa'])

        # [FIX] Update DB lùi giờ vào lại 1 tiếng trước để tính công
        one_hour_ago = datetime.now() - timedelta(hours=1)
        self.cursor.execute("UPDATE bangChamCong SET gioVao = %s WHERE idChamCong = %s",
                            (one_hour_ago, record['idChamCong']))
        self.conn.commit()  # Commit để Controller thấy

        # 2. Check-out
        ok, type_cc, hours = self.controller.model.xu_ly_cham_cong(self.id_nv)

        self.assertTrue(ok)
        self.assertEqual(type_cc, "CHECK-OUT")
        self.assertGreater(hours, 0.9)  # Phải > 0.9 giờ

        # Verify DB
        self.conn.commit()
        self.cursor.execute("SELECT * FROM bangChamCong WHERE idNhanVien = %s AND DATE(gioVao) = CURDATE()",
                            (self.id_nv,))
        record = self.cursor.fetchone()
        self.assertIsNotNone(record['gioRa'])

    def test_attendance_logic_overtime(self):
        """Test 2: Logic giới hạn giờ làm (Làm > 8.5 tiếng chỉ tính 8 tiếng)"""

        # 1. Giả lập Check-in từ 10 tiếng trước
        ten_hours_ago = datetime.now() - timedelta(hours=10)
        str_time = ten_hours_ago.strftime('%Y-%m-%d %H:%M:%S')

        self.cursor.execute("""
            INSERT INTO bangChamCong (idNhanVien, gioVao) VALUES (%s, %s)
        """, (self.id_nv, str_time))
        self.conn.commit()

        # 2. Check-out
        ok, type_cc, hours = self.controller.model.xu_ly_cham_cong(self.id_nv)

        self.assertTrue(ok)
        self.assertEqual(type_cc, "CHECK-OUT")
        self.assertEqual(hours, 8.0, "Hệ thống không giới hạn max 8 tiếng công")

    def test_get_list_sorted_status(self):
        """Test 3: Kiểm tra trạng thái hiển thị (Đỏ - Vàng - Xanh)"""

        # Case A: Chưa chấm công
        list_nv = self.controller.get_list_nv_sorted()
        me = next((x for x in list_nv if x['idNhanVien'] == self.id_nv), None)
        self.assertEqual(me['trangThai'], 0)

        # Case B: Check-in
        self.controller.model.xu_ly_cham_cong(self.id_nv)
        list_nv = self.controller.get_list_nv_sorted()
        me = next((x for x in list_nv if x['idNhanVien'] == self.id_nv), None)
        self.assertEqual(me['trangThai'], 1)

        # Case C: Check-out
        time.sleep(1)  # Delay nhỏ để tránh spam
        self.controller.model.xu_ly_cham_cong(self.id_nv)
        list_nv = self.controller.get_list_nv_sorted()
        me = next((x for x in list_nv if x['idNhanVien'] == self.id_nv), None)
        self.assertEqual(me['trangThai'], 2)

    # ==========================================================================
    # PHẦN 2: TEST FILE SYSTEM (QUẢN LÝ ẢNH & MODEL)
    # ==========================================================================

    def test_face_data_management(self):
        """Test 4: Thêm dữ liệu ảnh -> Train Model -> Xóa dữ liệu"""

        # 1. Giả lập thu thập ảnh
        user_dir = os.path.join(self.controller.FACE_DIR, f"face_{self.id_nv}")
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)

        # Tạo ảnh giả
        dummy_img = np.zeros((100, 100), dtype=np.uint8)
        cv2.imwrite(os.path.join(user_dir, "0.jpg"), dummy_img)

        self.assertTrue(self.controller.check_face_data_exists(self.id_nv))

        # 2. Train Model
        result = self.controller.train_model()
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.controller.TRAINER_FILE))

        # 3. Xóa dữ liệu
        success, msg = self.controller.delete_face_data(self.id_nv)
        self.assertTrue(success)
        self.assertFalse(os.path.exists(user_dir))
        self.assertFalse(self.controller.check_face_data_exists(self.id_nv))


if __name__ == '__main__':
    unittest.main()