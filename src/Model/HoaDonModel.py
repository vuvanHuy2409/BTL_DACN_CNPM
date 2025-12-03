import mysql.connector
from src.config.db_config import DB_CONFIG

class HoaDonModel:
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

    # ... (Giữ nguyên các hàm get_all_invoices, get_invoice_details, delete_invoice, search_invoice cũ) ...

    def get_all_invoices(self):
        self.connect()
        query = """
            SELECT 
                hd.idHoaDon, hd.ngayTao, hd.ngayCapNhat, hd.tongTien, hd.trangThai,
                COALESCE(kh.hoTen, 'Khách vãng lai') as tenKhachHang,
                nv.hoTen as tenNhanVien
            FROM hoaDon hd
            LEFT JOIN khachHang kh ON hd.idKhachHang = kh.idKhachHang
            LEFT JOIN nhanVien nv ON hd.idNhanVien = nv.idNhanVien
            ORDER BY hd.ngayTao DESC
        """
        try:
            if self.cursor:
                self.cursor.execute(query)
                return self.cursor.fetchall()
            return []
        finally: self.close()

    def get_invoice_details(self, id_hd):
        self.connect()
        query = """
            SELECT sp.tenSanPham, ct.soLuong, ct.donGia, ct.thueVAT, ct.thanhTien
            FROM chiTietHoaDon ct
            JOIN sanPham sp ON ct.idSanPham = sp.idSanPham
            WHERE ct.idHoaDon = %s
        """
        try:
            if self.cursor:
                self.cursor.execute(query, (id_hd,))
                return self.cursor.fetchall()
            return []
        finally: self.close()

    # [MỚI] Hàm cập nhật trạng thái hóa đơn
    def update_invoice_status(self, id_hd, new_status):
        """
        Cập nhật trạng thái.
        MySQL sẽ tự động cập nhật cột 'ngayCapNhat' nếu row có sự thay đổi.
        """
        self.connect()
        query = "UPDATE hoaDon SET trangThai = %s WHERE idHoaDon = %s"
        try:
            if self.cursor:
                self.cursor.execute(query, (new_status, id_hd))
                self.conn.commit()
                return True
            return False
        except Exception as e:
            print(f"Lỗi update: {e}")
            return False
        finally: self.close()

    # ... (Giữ nguyên hàm delete_invoice, search_invoice)
    def delete_invoice(self, id_hd):
        """Xóa hóa đơn (Cascade sẽ tự xóa chi tiết)"""
        self.connect()
        try:
            # Cập nhật trạng thái thành 0 (Hủy) thay vì xóa vĩnh viễn để giữ lịch sử
            # Hoặc xóa hẳn: DELETE FROM hoaDon WHERE idHoaDon = %s
            query = "UPDATE hoaDon SET trangThai = 0 WHERE idHoaDon = %s"
            self.cursor.execute(query, (id_hd,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Lỗi xóa: {e}")
            return False
        finally:
            self.close()

    def search_invoice(self, keyword):
        """Tìm kiếm theo Mã HĐ hoặc Tên Khách"""
        self.connect()
        kw = f"%{keyword}%"
        query = """
            SELECT 
                hd.idHoaDon, hd.ngayTao, hd.tongTien, hd.trangThai,
                COALESCE(kh.hoTen, 'Khách vãng lai') as tenKhachHang,
                nv.hoTen as tenNhanVien
            FROM hoaDon hd
            LEFT JOIN khachHang kh ON hd.idKhachHang = kh.idKhachHang
            LEFT JOIN nhanVien nv ON hd.idNhanVien = nv.idNhanVien
            WHERE hd.idHoaDon LIKE %s OR kh.hoTen LIKE %s
            ORDER BY hd.ngayTao DESC
        """
        try:
            if self.cursor:
                self.cursor.execute(query, (kw, kw))
                return self.cursor.fetchall()
            return []
        finally:
            self.close()