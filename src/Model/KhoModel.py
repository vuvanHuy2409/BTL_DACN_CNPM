import mysql.connector
from src.config.db_config import DB_CONFIG


class KhoModel:
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
        """Lấy danh sách, ưu tiên hàng Đang hiện (1) lên trước"""
        self.connect()
        query = """
            SELECT k.*, ncc.tenNhaCungCap 
            FROM khoNguyenLieu k
            LEFT JOIN nhaCungCap ncc ON k.idNhaCungCap = ncc.idNhaCungCap
            ORDER BY k.isActive DESC, k.idNguyenLieu DESC
        """
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

    def check_exist(self, ten_nl):
        self.connect()
        query = "SELECT idNguyenLieu FROM khoNguyenLieu WHERE tenNguyenLieu = %s"
        try:
            if self.cursor:
                self.cursor.execute(query, (ten_nl,))
                return self.cursor.fetchone() is not None
            return False
        finally:
            self.close()

    def insert(self, data):
        self.connect()

        # LOGIC TỰ ĐỘNG: Nếu số lượng <= 0 thì Tự động Ẩn (0), ngược lại Hiện (1)
        trang_thai = 0 if float(data['sl']) <= 0 else 1

        query = """
            INSERT INTO khoNguyenLieu (tenNguyenLieu, giaNhap, soLuongTon, donViTinh, ngayNhap, idNhaCungCap, idNhanVien, isActive)
            VALUES (%s, %s, %s, %s, CURDATE(), %s, %s, %s)
        """
        try:
            if self.cursor:
                self.cursor.execute(query, (
                    data['ten'],
                    data['gia'],
                    data['sl'],
                    data['dvt'],
                    data['idNCC'],
                    data['idNV'],
                    trang_thai
                ))
                self.conn.commit()
                return True
            return False
        except Exception as e:
            print(f"Lỗi insert: {e}")
            return False
        finally:
            self.close()

    def update(self, idNL, data):
        self.connect()

        # LOGIC TỰ ĐỘNG: Cập nhật số lượng -> Cập nhật luôn trạng thái
        trang_thai = 0 if float(data['sl']) <= 0 else 1

        query = """
            UPDATE khoNguyenLieu 
            SET tenNguyenLieu=%s, giaNhap=%s, soLuongTon=%s, donViTinh=%s, idNhaCungCap=%s, isActive=%s
            WHERE idNguyenLieu=%s
        """
        try:
            if self.cursor:
                self.cursor.execute(query, (
                    data['ten'],
                    data['gia'],
                    data['sl'],
                    data['dvt'],
                    data['idNCC'],
                    trang_thai,  # Cập nhật trạng thái tự động
                    idNL
                ))
                self.conn.commit()
                return True
            return False
        finally:
            self.close()

    def toggle_status(self, idNL):
        """Đảo ngược trạng thái Ẩn/Hiện (Nút thủ công)"""
        self.connect()
        query = "UPDATE khoNguyenLieu SET isActive = NOT isActive WHERE idNguyenLieu = %s"
        try:
            if self.cursor:
                self.cursor.execute(query, (idNL,))
                self.conn.commit()
                return True
            return False
        finally:
            self.close()

    def search(self, keyword):
        self.connect()
        query = """
            SELECT k.*, ncc.tenNhaCungCap 
            FROM khoNguyenLieu k
            LEFT JOIN nhaCungCap ncc ON k.idNhaCungCap = ncc.idNhaCungCap
            WHERE k.tenNguyenLieu LIKE %s
            ORDER BY k.isActive DESC
        """
        try:
            if self.cursor:
                kw = f"%{keyword}%"
                self.cursor.execute(query, (kw,))
                return self.cursor.fetchall()
            return []
        finally:
            self.close()

    def get_ncc_options(self):
        self.connect()
        query = "SELECT idNhaCungCap, tenNhaCungCap FROM nhaCungCap WHERE isActive = 1"
        try:
            if self.cursor:
                self.cursor.execute(query)
                return self.cursor.fetchall()
            return []
        finally:
            self.close()