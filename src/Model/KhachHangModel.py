import mysql.connector
from src.config.db_config import DB_CONFIG

class KhachHangModel:
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
        """Lấy toàn bộ danh sách khách hàng"""
        self.connect()
        query = "SELECT * FROM khachHang ORDER BY idKhachHang DESC"
        try:
            if self.cursor:
                self.cursor.execute(query)
                return self.cursor.fetchall()
            return []
        except Exception as e:
            print(f"Lỗi get_all: {e}")
            return []
        finally:
            self.close()

    def check_exist(self, sdt):
        """Kiểm tra số điện thoại đã tồn tại chưa"""
        self.connect()
        query = "SELECT idKhachHang FROM khachHang WHERE soDienThoai = %s"
        try:
            if self.cursor:
                self.cursor.execute(query, (sdt,))
                return self.cursor.fetchone() is not None
            return False
        finally:
            self.close()

    def insert(self, data):
        self.connect()
        query = """
            INSERT INTO khachHang (hoTen, soDienThoai, ngaySinh, diemTichLuy)
            VALUES (%s, %s, %s, %s)
        """
        try:
            if self.cursor:
                self.cursor.execute(query, (
                    data['hoTen'],
                    data['soDienThoai'],
                    data['ngaySinh'],
                    data.get('diemTichLuy', 0)
                ))
                self.conn.commit()
                return True
            return False
        except Exception as e:
            print(f"Lỗi insert: {e}")
            return False
        finally:
            self.close()

    def update(self, idKH, data):
        self.connect()
        query = """
            UPDATE khachHang 
            SET hoTen=%s, soDienThoai=%s, ngaySinh=%s, diemTichLuy=%s
            WHERE idKhachHang=%s
        """
        try:
            if self.cursor:
                self.cursor.execute(query, (
                    data['hoTen'],
                    data['soDienThoai'],
                    data['ngaySinh'],
                    data['diemTichLuy'],
                    idKH
                ))
                self.conn.commit()
                return True
            return False
        except Exception as e:
            print(f"Lỗi update: {e}")
            return False
        finally:
            self.close()

    def search(self, keyword):
        self.connect()
        query = """
            SELECT * FROM khachHang 
            WHERE hoTen LIKE %s OR soDienThoai LIKE %s
            ORDER BY idKhachHang DESC
        """
        try:
            if self.cursor:
                kw = f"%{keyword}%"
                self.cursor.execute(query, (kw, kw))
                return self.cursor.fetchall()
            return []
        finally:
            self.close()