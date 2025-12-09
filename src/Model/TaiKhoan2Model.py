import mysql.connector
from src.config.db_config import DB_CONFIG

class TaiKhoan2Model:
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

    def get_employee_info(self, id_nv):
        """Lấy thông tin của nhân viên đang đăng nhập"""
        self.connect()
        try:
            # JOIN các bảng để lấy đầy đủ tên chức vụ và thông tin tài khoản
            query = """
                SELECT 
                    nv.idNhanVien, nv.hoTen, nv.soDienThoai, nv.email, nv.ngayTao,
                    cv.tenChucVu, 
                    tk.idTaiKhoan, tk.tenDangNhap, tk.matKhauHash
                FROM nhanVien nv
                JOIN chucVu cv ON nv.idChucVu = cv.idChucVu
                JOIN taiKhoanNhanVien tk ON nv.idTaiKhoan = tk.idTaiKhoan
                WHERE nv.idNhanVien = %s
            """
            if self.cursor:
                self.cursor.execute(query, (id_nv,))
                return self.cursor.fetchone()
            return None
        except Exception as e:
            print(f"Lỗi get_employee_info: {e}")
            return None
        finally:
            self.close()

    def update_info(self, id_nv, ho_ten, sdt, email):
        self.connect()
        try:
            query = "UPDATE nhanVien SET hoTen=%s, soDienThoai=%s, email=%s WHERE idNhanVien=%s"
            self.cursor.execute(query, (ho_ten, sdt, email, id_nv))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Lỗi update: {e}")
            return False
        finally:
            self.close()

    def verify_password(self, id_tai_khoan, input_hash):
        self.connect()
        try:
            query = "SELECT idTaiKhoan FROM taiKhoanNhanVien WHERE idTaiKhoan=%s AND matKhauHash=%s"
            self.cursor.execute(query, (id_tai_khoan, input_hash))
            return self.cursor.fetchone() is not None
        finally:
            self.close()

    def change_password(self, id_tai_khoan, new_pass_hash):
        self.connect()
        try:
            query = "UPDATE taiKhoanNhanVien SET matKhauHash=%s WHERE idTaiKhoan=%s"
            self.cursor.execute(query, (new_pass_hash, id_tai_khoan))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Lỗi đổi mật khẩu: {e}")
            return False
        finally:
            self.close()