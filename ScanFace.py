import mysql.connector
import pickle
import numpy as np
import face_recognition

# Cấu hình kết nối Database
db_config = {
    'user': 'root',  # Thay bằng user của bạn
    'password': '',  # Thay bằng pass của bạn
    'host': 'localhost',
    'database': 'coffeeShop'
}


# ---------------------------------------------------------
# PHẦN 1: LƯU KHUÔN MẶT VÀO DATABASE (ĐĂNG KÝ)
# ---------------------------------------------------------
def save_face_vector_to_db(user_id, image_path):
    # 1. Xử lý ảnh để lấy vector
    img = face_recognition.load_image_file(image_path)
    try:
        # Lấy encoding (vector 128 chiều)
        face_encoding = face_recognition.face_encodings(img)[0]
    except IndexError:
        print("Lỗi: Không tìm thấy khuôn mặt trong ảnh để lưu!")
        return False

    # 2. Biến đổi vector (numpy array) thành dạng nhị phân (binary)
    # Dùng pickle để đóng gói dữ liệu
    binary_data = pickle.dumps(face_encoding)

    # 3. Lưu vào MySQL
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Câu lệnh SQL Update
        sql = "UPDATE taiKhoanNhanVien SET vectorKhuonMat = %s WHERE idTaiKhoan = %s"
        cursor.execute(sql, (binary_data, user_id))

        conn.commit()
        print(f"Đã lưu vector khuôn mặt cho ID {user_id} thành công!")
        return True
    except mysql.connector.Error as err:
        print(f"Lỗi Database: {err}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# ---------------------------------------------------------
# PHẦN 2: QUÉT VÀ KIỂM TRA ĐĂNG NHẬP (CHECK-IN)
# ---------------------------------------------------------
def check_face_login(current_frame_encoding):
    """
    Input: current_frame_encoding là vector khuôn mặt đang quét từ camera
    Output: ID nhân viên nếu trùng khớp, None nếu không tìm thấy
    """
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # 1. Lấy tất cả vector khuôn mặt đã lưu trong DB
        # Chỉ lấy những tài khoản đã có dữ liệu khuôn mặt
        sql = "SELECT idTaiKhoan, vectorKhuonMat, tenDangNhap FROM taiKhoanNhanVien WHERE vectorKhuonMat IS NOT NULL"
        cursor.execute(sql)
        results = cursor.fetchall()

        # 2. Duyệt qua từng nhân viên trong DB để so sánh
        for (user_id, db_blob, username) in results:
            # Giải nén binary từ DB thành numpy array
            known_encoding = pickle.loads(db_blob)

            # So sánh (dùng hàm của thư viện face_recognition)
            # tolerance=0.5 là độ chính xác (càng thấp càng khắt khe)
            matches = face_recognition.compare_faces([known_encoding], current_frame_encoding, tolerance=0.5)

            if matches[0]:
                print(f"Đăng nhập thành công! Xin chào: {username} (ID: {user_id})")
                return user_id, username

        print("Không nhận diện được người này trong hệ thống.")
        return None, None

    except mysql.connector.Error as err:
        print(f"Lỗi Database: {err}")
        return None, None
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


# ---------------------------------------------------------
# VÍ DỤ CÁCH DÙNG (TEST)
# ---------------------------------------------------------
if __name__ == "__main__":
    # GIẢ SỬ: Bạn muốn lưu mặt cho nhân viên có idTaiKhoan = 1 (admin)
    # save_face_vector_to_db(1, "images/admin_face.jpg")

    # GIẢ SỬ: Đang chạy Camera và có một khuôn mặt
    # (Đoạn này mô phỏng việc lấy từ webcam)
    print("--- Đang mô phỏng quét camera ---")

    # Giả lập load ảnh từ camera (thực tế sẽ dùng cv2.VideoCapture)
    # Bạn cần có 1 ảnh test để chạy thử
    test_img = face_recognition.load_image_file("images/admin_face.jpg")
    try:
        unknown_encoding = face_recognition.face_encodings(test_img)[0]

        # Gọi hàm kiểm tra với DB
        found_id, found_name = check_face_login(unknown_encoding)

        if found_id:
            print(f"--> Mở cửa / Chấm công cho ID: {found_id}")
        else:
            print("--> Cảnh báo: Người lạ!")

    except IndexError:
        print("Không thấy mặt trong ảnh test")