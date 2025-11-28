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
            print("Lỗi kết nối DB:", err)

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    # =============================
    # LẤY DANH SÁCH
    # =============================
    def get_all(self):
        self.connect()
        query = "SELECT * FROM khachHang ORDER BY idKhachHang DESC"
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print("Lỗi get_all:", e)
            return []
        finally:
            self.close()

    # =============================
    # THÊM KHÁCH HÀNG
    # =============================
    def insert(self, data):
        self.connect()
        query = """
            INSERT INTO khachHang(hoTen, soDienThoai, ngaySinh, diemTichLuy)
            VALUES (%s, %s, %s, %s)
        """
        try:
            self.cursor.execute(query, (
                data["hoTen"],
                data["soDienThoai"],
                data["ngaySinh"],
                data["diemTichLuy"]
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print("Lỗi insert:", e)
            return False
        finally:
            self.close()

    # =============================
    # CẬP NHẬT KHÁCH HÀNG
    # =============================
    def update(self, idKH, data):
        self.connect()
        query = """
            UPDATE khachHang
            SET hoTen=%s, soDienThoai=%s, ngaySinh=%s, diemTichLuy=%s
            WHERE idKhachHang=%s
        """
        try:
            self.cursor.execute(query, (
                data["hoTen"],
                data["soDienThoai"],
                data["ngaySinh"],
                data["diemTichLuy"],
                idKH
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print("Lỗi update:", e)
            return False
        finally:
            self.close()

    # =============================
    # XÓA KHÁCH HÀNG
    # =============================
    def delete(self, idKH):
        self.connect()
        query = "DELETE FROM khachHang WHERE idKhachHang=%s"
        try:
            self.cursor.execute(query, (idKH,))
            self.conn.commit()
            return True
        except Exception as e:
            print("Lỗi delete:", e)
            return False
        finally:
            self.close()

    # =============================
    # TÌM KIẾM
    # =============================
    def search(self, keyword):
        self.connect()
        query = """
            SELECT * FROM khachHang
            WHERE hoTen LIKE %s OR soDienThoai LIKE %s
            ORDER BY idKhachHang DESC
        """
        try:
            kw = f"%{keyword}%"
            self.cursor.execute(query, (kw, kw))
            return self.cursor.fetchall()
        except Exception as e:
            print("Lỗi search:", e)
            return []
        finally:
            self.close()
