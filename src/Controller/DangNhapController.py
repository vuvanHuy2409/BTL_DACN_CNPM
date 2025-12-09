import mysql.connector
import hashlib
from src.config.db_config import DB_CONFIG


class DangNhapController:
    def __init__(self):
        pass

    def hash_password(self, password):
        return hashlib.md5(password.encode()).hexdigest()

    def xu_ly_dang_nhap(self, username, password):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)

            # Hash mật khẩu nhập vào để so sánh
            pass_hash = self.hash_password(password)

            # [QUAN TRỌNG] Phải SELECT idNhanVien từ bảng nhanVien thông qua bảng taiKhoanNhanVien
            # Giả sử cấu trúc DB: taiKhoanNhanVien(idTaiKhoan, ...) và nhanVien(idNhanVien, idTaiKhoan, ...)
            query = """
                SELECT nv.idNhanVien 
                FROM taiKhoanNhanVien tk
                JOIN nhanVien nv ON tk.idTaiKhoan = nv.idTaiKhoan
                WHERE tk.tenDangNhap = %s AND tk.matKhauHash = %s AND tk.trangThai = 1
            """

            cursor.execute(query, (username, pass_hash))
            result = cursor.fetchone()

            cursor.close()
            conn.close()

            if result:
                # Đăng nhập thành công -> Trả về ID
                return {
                    "status": True,
                    "message": "Đăng nhập thành công",
                    "id_nhan_vien": result['idNhanVien']  # <--- Trả về ID ở đây
                }
            else:
                return {
                    "status": False,
                    "message": "Sai tên đăng nhập hoặc mật khẩu!"
                }

        except mysql.connector.Error as err:
            return {
                "status": False,
                "message": f"Lỗi kết nối CSDL: {err}"
            }