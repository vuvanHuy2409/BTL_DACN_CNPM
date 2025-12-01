import mysql.connector
from src.config.db_config import DB_CONFIG

class NhaCungCapModel:
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

    def get_all_with_ingredients(self):
        self.connect()
        query = """
            SELECT n.*, 
                   GROUP_CONCAT(k.tenNguyenLieu SEPARATOR ', ') as danhSachNguyenLieu
            FROM nhaCungCap n
            LEFT JOIN khoNguyenLieu k ON n.idNhaCungCap = k.idNhaCungCap
            GROUP BY n.idNhaCungCap
            ORDER BY n.isActive DESC, n.ngayCapNhat DESC, n.idNhaCungCap DESC
        """
        # Đã thêm sắp xếp theo ngayCapNhat mới nhất
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

    def search(self, keyword):
        self.connect()
        kw = f"%{keyword}%"
        query = """
            SELECT n.*, 
                   GROUP_CONCAT(k.tenNguyenLieu SEPARATOR ', ') as danhSachNguyenLieu
            FROM nhaCungCap n
            LEFT JOIN khoNguyenLieu k ON n.idNhaCungCap = k.idNhaCungCap
            WHERE n.tenNhaCungCap LIKE %s OR n.soDienThoai LIKE %s
            GROUP BY n.idNhaCungCap
            ORDER BY n.isActive DESC, n.ngayCapNhat DESC
        """
        try:
            if self.cursor:
                self.cursor.execute(query, (kw, kw))
                return self.cursor.fetchall()
            return []
        except Exception as e:
            print(f"Lỗi search: {e}")
            return []
        finally:
            self.close()

    def insert(self, ten, sdt, dia_chi):
        self.connect()
        # Thêm CURDATE() vào câu lệnh INSERT để lấy ngày hiện tại
        query = """
            INSERT INTO nhaCungCap (tenNhaCungCap, soDienThoai, diaChi, ngayCapNhat, isActive) 
            VALUES (%s, %s, %s, CURDATE(), 1)
        """
        try:
            if self.cursor:
                self.cursor.execute(query, (ten, sdt, dia_chi))
                self.conn.commit()
                return True
            return False
        except Exception as e:
            print(f"Lỗi insert: {e}")
            return False
        finally:
            self.close()

    def update(self, idNCC, ten, sdt, dia_chi):
        self.connect()
        # Thêm ngayCapNhat = CURDATE() vào câu lệnh UPDATE
        query = """
            UPDATE nhaCungCap 
            SET tenNhaCungCap=%s, soDienThoai=%s, diaChi=%s, ngayCapNhat=CURDATE() 
            WHERE idNhaCungCap=%s
        """
        try:
            if self.cursor:
                self.cursor.execute(query, (ten, sdt, dia_chi, idNCC))
                self.conn.commit()
                return True
            return False
        except Exception as e:
            print(f"Lỗi update: {e}")
            return False
        finally:
            self.close()

    def toggle_status(self, idNCC):
        self.connect()
        query = "UPDATE nhaCungCap SET isActive = NOT isActive WHERE idNhaCungCap=%s"
        try:
            if self.cursor:
                self.cursor.execute(query, (idNCC,))
                self.conn.commit()
                return True
            return False
        except Exception as e:
            print(f"Lỗi toggle_status: {e}")
            return False
        finally:
            self.close()