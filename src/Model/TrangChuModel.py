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
        try:
            self.cursor.execute("SELECT * FROM danhMuc")
            return self.cursor.fetchall()
        finally:
            self.close()

    def get_products_by_category(self, id_danh_muc):
        self.connect()
        try:
            query = "SELECT idSanPham, tenSanPham, giaBan, hinhAnhUrl, idDanhMuc FROM sanPham WHERE idDanhMuc = %s AND isActive = 1"
            self.cursor.execute(query, (id_danh_muc,))
            return self.cursor.fetchall()
        finally:
            self.close()

    def get_all_products_full(self):
        self.connect()
        try:
            self.cursor.execute(
                "SELECT idSanPham, tenSanPham, giaBan, hinhAnhUrl, idDanhMuc FROM sanPham WHERE isActive = 1")
            return self.cursor.fetchall()
        finally:
            self.close()

    def get_product_by_name(self, name):
        self.connect()
        try:
            self.cursor.execute("SELECT * FROM sanPham WHERE tenSanPham = %s AND isActive = 1", (name,))
            return self.cursor.fetchone()
        finally:
            self.close()

    # ================= QUẢN LÝ KHÁCH HÀNG =================
    def search_customer(self, sdt):
        self.connect()
        try:
            self.cursor.execute("SELECT * FROM khachHang WHERE soDienThoai = %s", (sdt,))
            return self.cursor.fetchone()
        finally:
            self.close()

    def add_customer(self, ten, sdt, ngay_sinh):
        self.connect()
        try:
            self.cursor.execute(
                "INSERT INTO khachHang (hoTen, soDienThoai, ngaySinh, diemTichLuy) VALUES (%s, %s, %s, 0)",
                (ten, sdt, ngay_sinh))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(e);
            return None
        finally:
            self.close()

    def add_loyalty_points(self, id_kh, points=10):
        self.connect()
        try:
            self.cursor.execute("UPDATE khachHang SET diemTichLuy = diemTichLuy + %s WHERE idKhachHang = %s",
                                (points, id_kh))
            self.conn.commit()
            return True
        except:
            return False
        finally:
            self.close()

    def suggest_customers_by_phone(self, sdt_part):
        self.connect()
        try:
            # Gợi ý khách hàng khi nhập 1 phần sđt
            query = "SELECT * FROM khachHang WHERE soDienThoai LIKE %s LIMIT 5"
            param = (f"%{sdt_part}%",)
            self.cursor.execute(query, param)
            return self.cursor.fetchall()
        except:
            return []
        finally:
            self.close()

    # ================= THANH TOÁN & HÓA ĐƠN =================

    def get_active_banks(self):
        self.connect()
        try:
            self.cursor.execute("SELECT * FROM nganHang WHERE isActive = 1")
            return self.cursor.fetchall()
        finally:
            self.close()

    def get_active_invoice_id(self, table_id):
        """Lấy ID hóa đơn đang phục vụ của bàn"""
        self.connect()
        try:
            query = "SELECT idHoaDon FROM hoaDon WHERE idBan = %s AND trangThai = 1 LIMIT 1"
            self.cursor.execute(query, (table_id,))
            res = self.cursor.fetchone()
            return res['idHoaDon'] if res else None
        finally:
            self.close()

    def create_invoice_for_table(self, id_nv, table_id):
        """Tạo hóa đơn mới gắn với bàn (Trạng thái 1 - Đang phục vụ)"""
        self.connect()
        try:
            # Khi mới tạo, noiDungCK để NULL
            query = "INSERT INTO hoaDon (idNhanVien, idBan, tongTien, trangThai) VALUES (%s, %s, 0, 1)"
            self.cursor.execute(query, (id_nv, table_id))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(e);
            return None
        finally:
            self.close()

    def add_or_update_item(self, id_hd, id_sp, qty, price):
        """Thêm hoặc cập nhật món vào chi tiết hóa đơn"""
        self.connect()
        try:
            # 1. Kiểm tra món đã có chưa
            self.cursor.execute("SELECT soLuong FROM chiTietHoaDon WHERE idHoaDon = %s AND idSanPham = %s",
                                (id_hd, id_sp))
            exist = self.cursor.fetchone()

            if exist:
                new_qty = exist['soLuong'] + qty
                if new_qty <= 0:
                    self.cursor.execute("DELETE FROM chiTietHoaDon WHERE idHoaDon=%s AND idSanPham=%s", (id_hd, id_sp))
                else:
                    self.cursor.execute("UPDATE chiTietHoaDon SET soLuong=%s WHERE idHoaDon=%s AND idSanPham=%s",
                                        (new_qty, id_hd, id_sp))
            elif qty > 0:
                # Insert mới (isActive mặc định là 1, VAT 10)
                self.cursor.execute(
                    "INSERT INTO chiTietHoaDon (idHoaDon, idSanPham, soLuong, donGia, thueVAT, isActive) VALUES (%s, %s, %s, %s, 10, 1)",
                    (id_hd, id_sp, qty, price))

            self.conn.commit()
            return True
        except Exception as e:
            print(e);
            return False
        finally:
            self.close()

    def update_invoice_total_money(self, id_hd):
        """Tính lại tổng tiền hóa đơn và update vào bảng hoaDon"""
        self.connect()
        try:
            # Tổng tiền = SUM(thanhTien) trong bảng chiTietHoaDon (cột thanhTien là generated column)
            query_sum = "SELECT SUM(thanhTien) as total FROM chiTietHoaDon WHERE idHoaDon = %s"
            self.cursor.execute(query_sum, (id_hd,))
            res = self.cursor.fetchone()
            total = res['total'] if res and res['total'] else 0

            self.cursor.execute("UPDATE hoaDon SET tongTien = %s WHERE idHoaDon = %s", (total, id_hd))
            self.conn.commit()
        except:
            pass
        finally:
            self.close()

    def get_invoice_details(self, id_hd):
        """Lấy danh sách món của hóa đơn"""
        self.connect()
        try:
            query = """
                SELECT ct.idSanPham, sp.tenSanPham, ct.soLuong, ct.donGia, ct.thanhTien, ct.thueVAT
                FROM chiTietHoaDon ct 
                JOIN sanPham sp ON ct.idSanPham = sp.idSanPham 
                WHERE ct.idHoaDon = %s
            """
            self.cursor.execute(query, (id_hd,))
            return self.cursor.fetchall()
        finally:
            self.close()

    def get_active_tables(self):
        """Lấy danh sách ID các bàn đang hoạt động"""
        self.connect()
        try:
            self.cursor.execute("SELECT DISTINCT idBan FROM hoaDon WHERE trangThai = 1 AND idBan IS NOT NULL")
            res = self.cursor.fetchall()
            return [r['idBan'] for r in res]
        finally:
            self.close()

    def get_active_tables_info(self):
        """Lấy thông tin (ID, Tổng tiền) các bàn đang hoạt động"""
        self.connect()
        try:
            self.cursor.execute("SELECT idBan, tongTien FROM hoaDon WHERE trangThai = 1 AND idBan IS NOT NULL")
            return self.cursor.fetchall()
        finally:
            self.close()

    def update_invoice_customer(self, id_hd, id_kh):
        self.connect()
        try:
            self.cursor.execute("UPDATE hoaDon SET idKhachHang=%s WHERE idHoaDon=%s", (id_kh, id_hd))
            self.conn.commit()
        except:
            pass
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

    # [CẬP NHẬT QUAN TRỌNG] Hàm thanh toán
    def finalize_invoice(self, id_hd, status, total_money=0, id_ngan_hang=None, noi_dung_ck=None):
        """
        Thanh toán (status=2) hoặc Hủy (status=0).
        - Nếu thanh toán: Cập nhật noiDungCK vào bảng hoaDon.
        - Nếu có id_ngan_hang: Cập nhật idNganHang vào bảng chiTietHoaDon (theo cấu trúc DB mới).
        """
        self.connect()
        try:
            self.conn.start_transaction()

            if status == 2:
                # 1. Cập nhật bảng hoaDon: trạng thái, tổng tiền, nội dung CK
                query_hd = "UPDATE hoaDon SET trangThai=%s, tongTien=%s, noiDungCK=%s WHERE idHoaDon=%s"
                self.cursor.execute(query_hd, (status, total_money, noi_dung_ck, id_hd))

                # 2. Nếu có chọn ngân hàng, cập nhật idNganHang cho các món trong chiTietHoaDon
                # (Vì DB thiết kế idNganHang nằm ở bảng chi tiết)
                if id_ngan_hang:
                    query_ct = "UPDATE chiTietHoaDon SET idNganHang=%s WHERE idHoaDon=%s"
                    self.cursor.execute(query_ct, (id_ngan_hang, id_hd))
            else:
                # Hủy hóa đơn
                self.cursor.execute("UPDATE hoaDon SET trangThai=%s WHERE idHoaDon=%s", (status, id_hd))

            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Lỗi finalize_invoice: {e}")
            return False
        finally:
            self.close()

    def cancel_invoice(self, id_hd):
        return self.finalize_invoice(id_hd, 0)

    # [CẬP NHẬT] Hàm tạo hóa đơn nhanh (Mang về / Không dùng bàn)
    def create_invoice(self, id_nv, id_kh, total_money, cart_items, id_ngan_hang=None, noi_dung_ck=None):
        """
        Tạo hóa đơn hoàn tất ngay lập tức (Status 2).
        Hỗ trợ lưu noiDungCK và idNganHang.
        """
        self.connect()
        try:
            self.conn.start_transaction()

            # 1. Insert Hóa Đơn (Bảng cha) -> Có noiDungCK
            sql_hd = "INSERT INTO hoaDon (idNhanVien, idKhachHang, tongTien, trangThai, noiDungCK) VALUES (%s, %s, %s, 2, %s)"
            self.cursor.execute(sql_hd, (id_nv, id_kh, total_money, noi_dung_ck))
            id_hd = self.cursor.lastrowid

            # 2. Insert Chi Tiết (Bảng con) -> Có idNganHang
            # Lưu ý: isActive mặc định 1
            sql_ct = "INSERT INTO chiTietHoaDon (idHoaDon, idSanPham, soLuong, donGia, thueVAT, idNganHang, isActive) VALUES (%s, %s, %s, %s, 10, %s, 1)"

            for item in cart_items:
                self.cursor.execute(sql_ct, (id_hd, item['id_sp'], item['sl'], item['gia'], id_ngan_hang))

            self.conn.commit()
            return True, id_hd
        except Exception as e:
            self.conn.rollback()
            print(f"Lỗi create_invoice: {str(e)}")
            return False, str(e)
        finally:
            self.close()

    def get_invoice_general_info(self, id_hd):
        """Lấy thông tin chung: Ngày tạo, Nhân viên, Khách hàng"""
        self.connect()
        try:
            query = """
                SELECT hd.ngayTao, nv.hoTen as tenNhanVien, kh.hoTen as tenKhachHang
                FROM hoaDon hd
                JOIN nhanVien nv ON hd.idNhanVien = nv.idNhanVien
                LEFT JOIN khachHang kh ON hd.idKhachHang = kh.idKhachHang
                WHERE hd.idHoaDon = %s
            """
            self.cursor.execute(query, (id_hd,))
            return self.cursor.fetchone()
        finally:
            self.close()

    def reset_loyalty_points(self, id_kh):
        """Reset điểm tích lũy về 0 khi khách dùng để giảm giá"""
        self.connect()
        try:
            self.cursor.execute("UPDATE khachHang SET diemTichLuy = 0 WHERE idKhachHang = %s", (id_kh,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Lỗi reset điểm: {e}")
            return False
        finally:
            self.close()