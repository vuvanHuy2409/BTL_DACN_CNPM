import mysql.connector
from src.config.db_config import DB_CONFIG


class TrangChuModel:
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

    # ================= QUẢN LÝ MENU =================
    def get_all_categories(self):
        self.connect()
        query = "SELECT * FROM danhMuc"
        try:
            if self.cursor:
                self.cursor.execute(query)
                return self.cursor.fetchall()
            return []
        finally:
            self.close()

    def get_products_by_category(self, id_danh_muc):
        self.connect()
        query = "SELECT idSanPham, tenSanPham, giaBan, hinhAnhUrl, idDanhMuc FROM sanPham WHERE idDanhMuc = %s AND isActive = 1"
        try:
            if self.cursor:
                self.cursor.execute(query, (id_danh_muc,))
                return self.cursor.fetchall()
            return []
        finally:
            self.close()

    def get_all_products_full(self):
        self.connect()
        query = "SELECT idSanPham, tenSanPham, giaBan, hinhAnhUrl, idDanhMuc FROM sanPham WHERE isActive = 1"
        try:
            if self.cursor:
                self.cursor.execute(query)
                return self.cursor.fetchall()
            return []
        finally:
            self.close()

    def get_product_by_name(self, name):
        self.connect()
        query = "SELECT * FROM sanPham WHERE tenSanPham = %s AND isActive = 1"
        try:
            if self.cursor:
                self.cursor.execute(query, (name,))
                return self.cursor.fetchone()
            return None
        finally:
            self.close()

    # ================= QUẢN LÝ KHÁCH HÀNG =================
    def search_customer(self, sdt):
        self.connect()
        query = "SELECT * FROM khachHang WHERE soDienThoai = %s"
        try:
            if self.cursor:
                self.cursor.execute(query, (sdt,))
                return self.cursor.fetchone()
            return None
        finally:
            self.close()

    def add_customer(self, ten, sdt, ngay_sinh):
        self.connect()
        query = "INSERT INTO khachHang (hoTen, soDienThoai, ngaySinh, diemTichLuy) VALUES (%s, %s, %s, 0)"
        try:
            if self.cursor:
                self.cursor.execute(query, (ten, sdt, ngay_sinh))
                self.conn.commit()
                return self.cursor.lastrowid
            return None
        except Exception as e:
            print(f"Lỗi thêm khách: {e}")
            return None
        finally:
            self.close()

    def add_loyalty_points(self, id_kh, points=10):
        self.connect()
        query = "UPDATE khachHang SET diemTichLuy = diemTichLuy + %s WHERE idKhachHang = %s"
        try:
            if self.cursor:
                self.cursor.execute(query, (points, id_kh))
                self.conn.commit()
                return True
            return False
        except:
            return False
        finally:
            self.close()

    # ================= THANH TOÁN & HÓA ĐƠN =================

    def get_active_banks(self):
        self.connect()
        query = "SELECT * FROM nganHang WHERE isActive = 1"
        try:
            if self.cursor:
                self.cursor.execute(query)
                return self.cursor.fetchall()
            return []
        finally:
            self.close()

    def get_active_invoice_id(self, table_id):
        """Lấy ID hóa đơn đang phục vụ của bàn"""
        self.connect()
        query = "SELECT idHoaDon FROM hoaDon WHERE idBan = %s AND trangThai = 1 LIMIT 1"
        try:
            if self.cursor:
                self.cursor.execute(query, (table_id,))
                res = self.cursor.fetchone()
                return res['idHoaDon'] if res else None
            return None
        finally:
            self.close()

    def create_new_invoice(self, id_nv, table_id):
        """Tạo hóa đơn tạm (Trạng thái 1: Chưa thanh toán)"""
        self.connect()
        try:
            sql = "INSERT INTO hoaDon (idNhanVien, idBan, tongTien, trangThai) VALUES (%s, %s, 0, 1)"
            self.cursor.execute(sql, (id_nv, table_id))
            self.conn.commit()
            return self.cursor.lastrowid
        except:
            return None
        finally:
            self.close()

    def add_item_to_invoice(self, id_hd, id_sp, qty, price):
        """Thêm món vào chi tiết hóa đơn"""
        self.connect()
        try:
            # Check tồn tại
            check_sql = "SELECT soLuong FROM chiTietHoaDon WHERE idHoaDon = %s AND idSanPham = %s"
            self.cursor.execute(check_sql, (id_hd, id_sp))
            exist = self.cursor.fetchone()

            if exist:
                new_qty = exist['soLuong'] + qty
                if new_qty <= 0:
                    self.cursor.execute("DELETE FROM chiTietHoaDon WHERE idHoaDon=%s AND idSanPham=%s", (id_hd, id_sp))
                else:
                    self.cursor.execute("UPDATE chiTietHoaDon SET soLuong=%s WHERE idHoaDon=%s AND idSanPham=%s",
                                        (new_qty, id_hd, id_sp))
            elif qty > 0:
                # Mặc định thuế 10%
                self.cursor.execute(
                    "INSERT INTO chiTietHoaDon (idHoaDon, idSanPham, soLuong, donGia, thueVAT) VALUES (%s, %s, %s, %s, 10)",
                    (id_hd, id_sp, qty, price))

            self.conn.commit()
            return True
        except:
            return False
        finally:
            self.close()

    def get_invoice_details(self, id_hd):
        self.connect()
        query = """
            SELECT ct.idSanPham, sp.tenSanPham, ct.soLuong, ct.donGia, ct.thueVAT 
            FROM chiTietHoaDon ct 
            JOIN sanPham sp ON ct.idSanPham = sp.idSanPham 
            WHERE ct.idHoaDon = %s
        """
        try:
            if self.cursor:
                self.cursor.execute(query, (id_hd,))
                return self.cursor.fetchall()
            return []
        finally:
            self.close()

    def get_active_tables(self):
        self.connect()
        try:
            if self.cursor:
                self.cursor.execute("SELECT DISTINCT idBan FROM hoaDon WHERE trangThai = 1")
                res = self.cursor.fetchall()
                return [r['idBan'] for r in res]
            return []
        finally:
            self.close()

    def cancel_invoice(self, id_hd):
        self.connect()
        try:
            self.cursor.execute("UPDATE hoaDon SET trangThai=0 WHERE idHoaDon=%s", (id_hd,))
            self.conn.commit()
            return True
        except:
            return False
        finally:
            self.close()

    def get_invoice_customer(self, id_hd):
        self.connect()
        try:
            query = "SELECT k.* FROM khachHang k JOIN hoaDon h ON h.idKhachHang = k.idKhachHang WHERE h.idHoaDon=%s"
            self.cursor.execute(query, (id_hd,))
            return self.cursor.fetchone()
        finally:
            self.close()

    def update_customer_for_invoice(self, id_hd, id_kh):
        self.connect()
        try:
            self.cursor.execute("UPDATE hoaDon SET idKhachHang=%s WHERE idHoaDon=%s", (id_kh, id_hd))
            self.conn.commit()
        except:
            pass
        finally:
            self.close()

    # [FIXED] Đây là hàm mà Controller đang gọi bị lỗi.
    # Tôi đặt tên là create_invoice để khớp với Controller.
    def create_invoice(self, id_nv, id_kh, total_money, cart_items, payment_method):
        """
        Lưu hóa đơn chính thức (Thanh toán luôn).
        Thường dùng cho trường hợp thanh toán nhanh hoặc update hóa đơn tạm thành chính thức.
        """
        self.connect()
        try:
            self.conn.start_transaction()

            # 1. Tạo Hóa Đơn (Trạng thái 2: Đã thanh toán)
            # Lưu ý: Nếu bạn muốn update hóa đơn tạm có sẵn thì cần logic khác ở Controller,
            # nhưng hàm này dùng để Insert mới hoàn toàn.
            sql_hd = "INSERT INTO hoaDon (idNhanVien, idKhachHang, tongTien, trangThai) VALUES (%s, %s, %s, 2)"
            self.cursor.execute(sql_hd, (id_nv, id_kh, total_money))
            id_hd = self.cursor.lastrowid

            # 2. Insert Chi Tiết (mặc định thuế 10%)
            sql_ct = "INSERT INTO chiTietHoaDon (idHoaDon, idSanPham, soLuong, donGia, thueVAT) VALUES (%s, %s, %s, %s, 10)"
            for item in cart_items:
                self.cursor.execute(sql_ct, (id_hd, item['id_sp'], item['sl'], item['gia']))

            self.conn.commit()
            return True, id_hd
        except Exception as e:
            self.conn.rollback()
            return False, str(e)
        finally:
            self.close()