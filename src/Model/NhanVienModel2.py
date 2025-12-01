import mysql.connector
from src.config.db_config import DB_CONFIG


class NhanVienModel2:
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
        """Lấy danh sách đầy đủ thông tin"""
        self.connect()
        query = """
            SELECT nv.*, cv.tenChucVu, cv.luongCoBan
            FROM nhanVien nv
            LEFT JOIN chucVu cv ON nv.idChucVu = cv.idChucVu
            ORDER BY nv.trangThaiLamViec ASC, nv.idNhanVien DESC
        """
        try:
            if self.cursor:
                self.cursor.execute(query)
                return self.cursor.fetchall()
            return []
        finally:
            self.close()

    def check_exist(self, email, sdt):
        self.connect()
        query = "SELECT idNhanVien FROM nhanVien WHERE email = %s OR soDienThoai = %s"
        try:
            if self.cursor:
                self.cursor.execute(query, (email, sdt))
                return self.cursor.fetchone() is not None
            return False
        finally:
            self.close()

    def insert(self, data):
        """Thêm nhân viên (Ngày tạo tự động bởi SQL DEFAULT CURRENT_TIMESTAMP)"""
        self.connect()
        query = """
            INSERT INTO nhanVien (hoTen, email, soDienThoai, idChucVu, phanQuyen, trangThaiLamViec)
            VALUES (%s, %s, %s, %s, %s, 'DangLamViec')
        """
        try:
            if self.cursor:
                self.cursor.execute(query, (
                    data['hoTen'],
                    data['email'],
                    data['soDienThoai'],
                    data['idChucVu'],
                    data['phanQuyen']
                ))
                self.conn.commit()
                return True
            return False
        except Exception as e:
            print(f"Lỗi insert: {e}")
            return False
        finally:
            self.close()

    def update(self, idNV, data):
        self.connect()
        query = """
            UPDATE nhanVien 
            SET hoTen=%s, email=%s, soDienThoai=%s, idChucVu=%s, phanQuyen=%s
            WHERE idNhanVien=%s
        """
        try:
            if self.cursor:
                self.cursor.execute(query, (
                    data['hoTen'],
                    data['email'],
                    data['soDienThoai'],
                    data['idChucVu'],
                    data['phanQuyen'],
                    idNV
                ))
                self.conn.commit()
                return True
            return False
        finally:
            self.close()

    def toggle_status(self, idNV):
        """Đổi trạng thái: DangLamViec <-> DaNghiViec"""
        self.connect()
        # Lấy trạng thái hiện tại
        get_status_query = "SELECT trangThaiLamViec FROM nhanVien WHERE idNhanVien = %s"
        update_query = "UPDATE nhanVien SET trangThaiLamViec = %s WHERE idNhanVien = %s"

        try:
            if self.cursor:
                self.cursor.execute(get_status_query, (idNV,))
                res = self.cursor.fetchone()
                if res:
                    current_status = res['trangThaiLamViec']
                    new_status = 'DaNghiViec' if current_status == 'DangLamViec' else 'DangLamViec'

                    self.cursor.execute(update_query, (new_status, idNV))
                    self.conn.commit()
                    return True
            return False
        except Exception as e:
            print(f"Lỗi toggle: {e}")
            return False
        finally:
            self.close()

    def search(self, keyword):
        self.connect()
        query = """
            SELECT nv.*, cv.tenChucVu 
            FROM nhanVien nv
            LEFT JOIN chucVu cv ON nv.idChucVu = cv.idChucVu
            WHERE nv.hoTen LIKE %s OR nv.soDienThoai LIKE %s OR nv.email LIKE %s
        """
        try:
            if self.cursor:
                kw = f"%{keyword}%"
                self.cursor.execute(query, (kw, kw, kw))
                return self.cursor.fetchall()
            return []
        finally:
            self.close()

    # ================= QUẢN LÝ CHỨC VỤ =================
    def get_all_chucvu(self):
        self.connect()
        query = "SELECT * FROM chucVu"
        try:
            if self.cursor:
                self.cursor.execute(query)
                return self.cursor.fetchall()
            return []
        finally:
            self.close()

    def add_chucvu(self, ten, luong):
        self.connect()
        query = "INSERT INTO chucVu (tenChucVu, luongCoBan) VALUES (%s, %s)"
        try:
            if self.cursor:
                self.cursor.execute(query, (ten, luong))
                self.conn.commit()
                return True
            return False
        finally:
            self.close()

    def update_chucvu(self, idCV, ten, luong):
        self.connect()
        query = "UPDATE chucVu SET tenChucVu=%s, luongCoBan=%s WHERE idChucVu=%s"
        try:
            if self.cursor:
                self.cursor.execute(query, (ten, luong, idCV))
                self.conn.commit()
                return True
            return False
        finally:
            self.close()