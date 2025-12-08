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

    # --- LẤY DỮ LIỆU & LỌC ---

    def get_all_invoices(self):
        """Lấy tất cả hóa đơn (gọi lại hàm filter rỗng)"""
        return self.filter_invoices()

    def filter_invoices(self, day=None, month=None, year=None, keyword=None):
        """
        Lọc hóa đơn theo thời gian và từ khóa.
        Sửa lỗi: Join qua chiTietHoaDon để lấy thông tin Ngân hàng.
        """
        self.connect()
        try:
            # SQL Query: Join bảng hd -> ct -> nganHang
            query = """
                SELECT 
                    hd.idHoaDon, 
                    hd.noiDungCK,
                    hd.ngayTao, 
                    hd.ngayCapNhat, 
                    hd.tongTien, 
                    hd.trangThai,
                    COALESCE(kh.hoTen, 'Khách vãng lai') as tenKhachHang,
                    nv.hoTen as tenNhanVien,
                    GROUP_CONCAT(DISTINCT nh.tenNganHang SEPARATOR ', ') as tenNganHang,
                    GROUP_CONCAT(DISTINCT nh.soTaiKhoan SEPARATOR ', ') as soTaiKhoan
                FROM hoaDon hd
                LEFT JOIN khachHang kh ON hd.idKhachHang = kh.idKhachHang
                JOIN nhanVien nv ON hd.idNhanVien = nv.idNhanVien
                LEFT JOIN chiTietHoaDon cthd ON hd.idHoaDon = cthd.idHoaDon
                LEFT JOIN nganHang nh ON cthd.idNganHang = nh.idNganHang
                WHERE 1=1 
            """
            params = []

            # 1. Lọc theo thời gian
            if year and str(year).strip():
                query += " AND YEAR(hd.ngayTao) = %s"
                params.append(year)
            if month and str(month) != "Tất cả":
                query += " AND MONTH(hd.ngayTao) = %s"
                params.append(month)
            if day and str(day) != "Tất cả":
                query += " AND DAY(hd.ngayTao) = %s"
                params.append(day)

            # 2. Lọc theo từ khóa (Mã HĐ hoặc Tên KH)
            if keyword:
                kw = f"%{keyword}%"
                query += " AND (hd.idHoaDon LIKE %s OR kh.hoTen LIKE %s)"
                params.append(kw)
                params.append(kw)

            # Group By là bắt buộc vì ta dùng GROUP_CONCAT và quan hệ 1-N
            query += " GROUP BY hd.idHoaDon ORDER BY hd.ngayTao DESC"

            self.cursor.execute(query, tuple(params))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Lỗi Filter: {e}")
            return []
        finally:
            self.close()

    def get_invoice_details(self, id_hd):
        """Lấy chi tiết sản phẩm của hóa đơn"""
        self.connect()
        query = """
            SELECT 
                ct.idSanPham, 
                sp.tenSanPham, 
                ct.soLuong, 
                ct.donGia, 
                ct.thueVAT, 
                ct.thanhTien
            FROM chiTietHoaDon ct
            JOIN sanPham sp ON ct.idSanPham = sp.idSanPham
            WHERE ct.idHoaDon = %s
        """
        try:
            self.cursor.execute(query, (id_hd,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Lỗi get details: {e}")
            return []
        finally:
            self.close()

    # --- CẬP NHẬT DỮ LIỆU ---

    def update_invoice_status(self, id_hd, new_status):
        """Cập nhật trạng thái đơn giản"""
        self.connect()
        query = "UPDATE hoaDon SET trangThai = %s WHERE idHoaDon = %s"
        try:
            self.cursor.execute(query, (new_status, id_hd))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Lỗi update status: {e}")
            return False
        finally:
            self.close()

    def delete_invoice(self, id_hd):
        """Hủy hóa đơn (Set trạng thái = 0)"""
        return self.update_invoice_status(id_hd, 0)

    def update_invoice_full_transaction(self, id_hd, new_status, items):
        """
        Cập nhật toàn bộ: Trạng thái + Danh sách món + Tổng tiền.
        Sử dụng Transaction để đảm bảo an toàn dữ liệu.
        items: List dict [{'idSanPham': 1, 'soLuong': 2, 'donGia': 25000}, ...]
        """
        self.connect()
        try:
            self.conn.start_transaction()

            # 1. Cập nhật trạng thái
            self.cursor.execute("UPDATE hoaDon SET trangThai = %s WHERE idHoaDon = %s", (new_status, id_hd))

            # 2. Xóa chi tiết cũ
            self.cursor.execute("DELETE FROM chiTietHoaDon WHERE idHoaDon = %s", (id_hd,))

            total_money = 0

            # 3. Insert chi tiết mới
            # Lưu ý: Giả sử update này không có chọn ngân hàng -> idNganHang để NULL
            insert_sql = """
                INSERT INTO chiTietHoaDon (idHoaDon, idSanPham, soLuong, donGia, thueVAT, isActive) 
                VALUES (%s, %s, %s, %s, 10, 1)
            """

            for item in items:
                sl = int(item['soLuong'])
                gia = float(item['donGia'])
                if sl > 0:
                    # Tính tổng tiền để update vào bảng cha (Giá * SL * 1.1 VAT)
                    item_total = sl * gia * 1.1
                    total_money += item_total

                    self.cursor.execute(insert_sql, (id_hd, item['idSanPham'], sl, gia))

            # 4. Cập nhật Tổng tiền mới vào bảng Hóa Đơn
            self.cursor.execute("UPDATE hoaDon SET tongTien = %s WHERE idHoaDon = %s", (total_money, id_hd))

            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Lỗi update full transaction: {e}")
            return False
        finally:
            self.close()

    def search_invoice(self, keyword):
        """Wrapper cho tìm kiếm nhanh"""
        return self.filter_invoices(keyword=keyword)