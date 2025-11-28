import mysql.connector
from src.config.db_config import DB_CONFIG

class NhanVienModel:
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

    def tim_tai_khoan(self, username):
        self.connect()
        # Join bảng Tài khoản và Nhân viên để lấy mật khẩu và quyền
        query = """
        SELECT tk.matKhauHash, nv.hoTen, nv.phanQuyen, nv.trangThaiLamViec, nv.idNhanVien
        FROM taiKhoanNhanVien tk
        JOIN nhanVien nv ON tk.idTaiKhoan = nv.idTaiKhoan
        WHERE tk.tenDangNhap = %s
        """
        try:
            self.cursor.execute(query, (username,))
            result = self.cursor.fetchone()
            return result
        except Exception as e:
            print(e)
            return None
        finally:
            self.close()