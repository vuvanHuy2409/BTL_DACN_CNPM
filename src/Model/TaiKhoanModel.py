import mysql.connector
from src.config.db_config import DB_CONFIG


class TaiKhoanModel:
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

    def get_all(self):
        self.connect()
        # Lấy danh sách nhân viên + thông tin tài khoản (nếu có)
        query = """
            SELECT 
                nv.idNhanVien, nv.hoTen, nv.email, cv.tenChucVu,
                tk.idTaiKhoan, tk.tenDangNhap, tk.matKhauHash, 
                tk.vectorKhuonMat, tk.hinhAnhUrl
            FROM nhanVien nv
            LEFT JOIN taiKhoanNhanVien tk ON nv.idTaiKhoan = tk.idTaiKhoan
            JOIN chucVu cv ON nv.idChucVu = cv.idChucVu
            WHERE nv.trangThaiLamViec = 'DangLamViec'
            ORDER BY (tk.idTaiKhoan IS NULL) DESC, nv.idNhanVien DESC
        """
        try:
            if self.cursor:
                self.cursor.execute(query)
                return self.cursor.fetchall()
            return []
        finally:
            self.close()

    def get_role_id(self, role_name):
        self.connect()
        query = "SELECT idChucVu FROM chucVu WHERE tenChucVu = %s"
        try:
            if self.cursor:
                self.cursor.execute(query, (role_name,))
                res = self.cursor.fetchone()
                return res['idChucVu'] if res else None
            return None
        finally:
            self.close()

    def check_user_exist(self, username):
        self.connect()
        query = "SELECT idTaiKhoan FROM taiKhoanNhanVien WHERE tenDangNhap = %s"
        try:
            if self.cursor:
                self.cursor.execute(query, (username,))
                return self.cursor.fetchone() is not None
            return False
        finally:
            self.close()

    # --- CÁC HÀM XỬ LÝ DỮ LIỆU ---

    def create_account_for_existing(self, idNV, data):
        """Cấp tài khoản cho nhân viên ĐÃ CÓ (nhưng chưa có TK)"""
        self.connect()
        try:
            self.conn.start_transaction()
            # 1. Tạo TK mới
            sql_tk = """
                INSERT INTO taiKhoanNhanVien (tenDangNhap, matKhauHash, vectorKhuonMat, hinhAnhUrl) 
                VALUES (%s, %s, %s, %s)
            """
            self.cursor.execute(sql_tk, (data['user'], data['pass'], data['avatar_blob'], data['image_path']))
            id_tk = self.cursor.lastrowid

            # 2. Update NV để link tới TK vừa tạo
            sql_update = "UPDATE nhanVien SET idTaiKhoan = %s WHERE idNhanVien = %s"
            self.cursor.execute(sql_update, (id_tk, idNV))

            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Lỗi create link: {e}")
            return False
        finally:
            self.close()

    def update_info(self, idNV, data):
        """Cập nhật thông tin khi ĐÃ CÓ tài khoản"""
        self.connect()
        try:
            self.conn.start_transaction()

            # Lấy idTaiKhoan
            self.cursor.execute("SELECT idTaiKhoan FROM nhanVien WHERE idNhanVien = %s", (idNV,))
            res = self.cursor.fetchone()
            if not res or not res['idTaiKhoan']: return False
            id_tk = res['idTaiKhoan']

            # Update TK
            # Nếu có ảnh mới (blob khác None) thì update cả ảnh, ngược lại giữ nguyên
            if data['avatar_blob'] is not None:
                sql_tk = """
                    UPDATE taiKhoanNhanVien 
                    SET tenDangNhap=%s, matKhauHash=%s, vectorKhuonMat=%s, hinhAnhUrl=%s 
                    WHERE idTaiKhoan=%s
                """
                val_tk = (data['user'], data['pass'], data['avatar_blob'], data['image_path'], id_tk)
            else:
                # Không đổi ảnh -> Giữ nguyên Url và Blob cũ
                sql_tk = "UPDATE taiKhoanNhanVien SET tenDangNhap=%s, matKhauHash=%s WHERE idTaiKhoan=%s"
                val_tk = (data['user'], data['pass'], id_tk)

            self.cursor.execute(sql_tk, val_tk)

            # Update NV
            sql_nv = "UPDATE nhanVien SET hoTen=%s, email=%s, idChucVu=%s WHERE idNhanVien=%s"
            self.cursor.execute(sql_nv, (data['name'], data['email'], data['role_id'], idNV))

            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Lỗi update info: {e}")
            return False
        finally:
            self.close()

    def remove_account(self, idNV):
        """Xóa tài khoản (Unlink NV -> Delete TK)"""
        self.connect()
        try:
            self.conn.start_transaction()
            self.cursor.execute("SELECT idTaiKhoan FROM nhanVien WHERE idNhanVien = %s", (idNV,))
            res = self.cursor.fetchone()
            if not res or not res['idTaiKhoan']: return False
            id_tk = res['idTaiKhoan']

            self.cursor.execute("UPDATE nhanVien SET idTaiKhoan = NULL WHERE idNhanVien = %s", (idNV,))
            self.cursor.execute("DELETE FROM taiKhoanNhanVien WHERE idTaiKhoan = %s", (id_tk,))

            self.conn.commit()
            return True
        except Exception:
            self.conn.rollback()
            return False
        finally:
            self.close()