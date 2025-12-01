import mysql.connector
from src.config.db_config import DB_CONFIG

class SanPhamModel:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor(dictionary=True)
        except mysql.connector.Error as err:
            print(f"Lỗi kết nối: {err}")

    def close(self):
        if self.cursor: self.cursor.close()
        if self.conn: self.conn.close()

    def get_all(self):
        self.connect()
        # Sắp xếp theo Trạng thái (đang bán lên trước) -> ID giảm dần
        query = """
            SELECT s.idSanPham, s.tenSanPham, s.giaBan, s.hinhAnhUrl, s.isActive,
                   s.idDanhMuc, d.tenDanhMuc,
                   s.idNguyenLieu, k.tenNguyenLieu, k.soLuongTon,
                   n.tenNhaCungCap
            FROM sanPham s
            LEFT JOIN danhMuc d ON s.idDanhMuc = d.idDanhMuc
            LEFT JOIN khoNguyenLieu k ON s.idNguyenLieu = k.idNguyenLieu
            LEFT JOIN nhaCungCap n ON k.idNhaCungCap = n.idNhaCungCap
            ORDER BY s.isActive DESC, s.idSanPham DESC
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

    def search(self, keyword):
        self.connect()
        kw = f"%{keyword}%"
        query = """
            SELECT s.idSanPham, s.tenSanPham, s.giaBan, s.hinhAnhUrl, s.isActive,
                   d.tenDanhMuc, k.tenNguyenLieu, k.soLuongTon, n.tenNhaCungCap
            FROM sanPham s
            LEFT JOIN danhMuc d ON s.idDanhMuc = d.idDanhMuc
            LEFT JOIN khoNguyenLieu k ON s.idNguyenLieu = k.idNguyenLieu
            LEFT JOIN nhaCungCap n ON k.idNhaCungCap = n.idNhaCungCap
            WHERE s.tenSanPham LIKE %s 
            ORDER BY s.isActive DESC
        """
        try:
            if self.cursor:
                self.cursor.execute(query, (kw,))
                return self.cursor.fetchall()
            return []
        except Exception:
            return []
        finally:
            self.close()

    # --- INSERT / UPDATE ---
    def insert(self, ten, gia, hinh_anh, id_dm, id_nl):
        self.connect()
        query = """
            INSERT INTO sanPham (tenSanPham, giaBan, hinhAnhUrl, idDanhMuc, idNguyenLieu, isActive)
            VALUES (%s, %s, %s, %s, %s, 1)
        """
        try:
            if self.cursor:
                self.cursor.execute(query, (ten, gia, hinh_anh, id_dm, id_nl))
                self.conn.commit()
                return True
            return False
        except Exception as e:
            print(e); return False
        finally:
            self.close()

    def update(self, id_sp, ten, gia, hinh_anh, id_dm, id_nl):
        self.connect()
        query = """
            UPDATE sanPham 
            SET tenSanPham=%s, giaBan=%s, hinhAnhUrl=%s, idDanhMuc=%s, idNguyenLieu=%s
            WHERE idSanPham=%s
        """
        try:
            if self.cursor:
                self.cursor.execute(query, (ten, gia, hinh_anh, id_dm, id_nl, id_sp))
                self.conn.commit()
                return True
            return False
        except Exception: return False
        finally:
            self.close()

    # --- TOGGLE STATUS (ẨN/HIỆN) ---
    def toggle_status(self, id_sp):
        self.connect()
        query = "UPDATE sanPham SET isActive = NOT isActive WHERE idSanPham=%s"
        try:
            if self.cursor:
                self.cursor.execute(query, (id_sp,))
                self.conn.commit()
                return True
            return False
        except Exception as e:
            print(e); return False
        finally:
            self.close()

    def get_categories(self):
        self.connect()
        try:
            if self.cursor:
                self.cursor.execute("SELECT idDanhMuc, tenDanhMuc FROM danhMuc")
                return self.cursor.fetchall()
            return []
        finally:
            self.close()

    def get_ingredients(self):
        self.connect()
        try:
            if self.cursor:
                self.cursor.execute("SELECT idNguyenLieu, tenNguyenLieu FROM khoNguyenLieu")
                return self.cursor.fetchall()
            return []
        finally:
            self.close()