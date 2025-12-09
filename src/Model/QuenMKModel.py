import mysql.connector
from src.config.db_config import DB_CONFIG

class QuenMKModel:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor(dictionary=True)
        except mysql.connector.Error as err:
            print(f"Lỗi kết nối DB: {err}")

    def close(self):
        if self.cursor: self.cursor.close()
        if self.conn: self.conn.close()

    def check_user_email(self, username, email):
        self.connect()
        try:
            query = """
                SELECT tk.idTaiKhoan 
                FROM taiKhoanNhanVien tk
                JOIN nhanVien nv ON tk.idTaiKhoan = nv.idTaiKhoan
                WHERE tk.tenDangNhap = %s AND nv.email = %s
            """
            self.cursor.execute(query, (username, email))
            result = self.cursor.fetchone()
            return result['idTaiKhoan'] if result else None
        finally:
            self.close()

    def reset_password(self, id_tai_khoan, new_password_hash):
        """Đổi mật khẩu và kích hoạt tài khoản (trangThai = 1)"""
        self.connect()
        try:
            # [QUAN TRỌNG] Set trạng thái = 1 vì đã đổi xong
            query = "UPDATE taiKhoanNhanVien SET matKhauHash = %s, trangThai = 1 WHERE idTaiKhoan = %s"
            self.cursor.execute(query, (new_password_hash, id_tai_khoan))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Lỗi update: {e}")
            return False
        finally:
            self.close()