import mysql.connector
from src.config.db_config import DB_CONFIG


class LuongModel:
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

    def get_bang_luong_thang(self, month, year):
        """
        Lấy bảng lương tổng hợp.
        [FIXED] Đã thêm logic tính cột 'trangThai'
        """
        self.connect()
        query = """
            SELECT 
                nv.idNhanVien, 
                nv.hoTen, 
                cv.tenChucVu,
                cv.luongCoBan,

                -- Tổng giờ làm trong tháng
                COALESCE(SUM(b.tongGioLam), 0) as tongGioLamThang,

                -- Tính lương thực lãnh
                ROUND((cv.luongCoBan / 26 / 8) * COALESCE(SUM(b.tongGioLam), 0)) as thucLanh,

                -- [QUAN TRỌNG] Logic xác định trạng thái:
                -- Nếu có bất kỳ dòng lương nào trong tháng là 'ChuaThanhToan' -> Trạng thái chung là Chưa TT
                CASE 
                    WHEN COUNT(b.idChamCong) = 0 THEN 'DaThanhToan' -- Không đi làm thì coi như xong
                    WHEN SUM(CASE WHEN l.ttThanhToan = 'ChuaThanhToan' THEN 1 ELSE 0 END) > 0 THEN 'ChuaThanhToan'
                    ELSE 'DaThanhToan'
                END as trangThai

            FROM nhanVien nv
            JOIN chucVu cv ON nv.idChucVu = cv.idChucVu

            -- Join bảng chấm công theo tháng/năm
            LEFT JOIN bangChamCong b ON nv.idNhanVien = b.idNhanVien 
                 AND MONTH(b.gioVao) = %s AND YEAR(b.gioVao) = %s

            -- Join bảng lương để lấy trạng thái thanh toán
            LEFT JOIN luong l ON b.idChamCong = l.idChamCong

            WHERE nv.trangThaiLamViec = 'DangLamViec'
            GROUP BY nv.idNhanVien, cv.tenChucVu, cv.luongCoBan
            ORDER BY nv.idNhanVien ASC
        """
        try:
            if self.cursor:
                self.cursor.execute(query, (month, year))
                return self.cursor.fetchall()
            return []
        except Exception as e:
            print(f"Lỗi SQL Lương: {e}")
            return []
        finally:
            self.close()

    def update_payment_status(self, idNV, month, year):
        """
        Cập nhật tất cả các dòng lương trong tháng của NV đó thành 'DaThanhToan'
        """
        self.connect()
        query = """
            UPDATE luong l
            JOIN bangChamCong b ON l.idChamCong = b.idChamCong
            SET l.ttThanhToan = 'DaThanhToan'
            WHERE l.idNhanVien = %s 
              AND MONTH(b.gioVao) = %s 
              AND YEAR(b.gioVao) = %s
              AND l.ttThanhToan = 'ChuaThanhToan'
        """
        try:
            if self.cursor:
                self.cursor.execute(query, (idNV, month, year))
                self.conn.commit()
                # Kiểm tra xem có dòng nào được update không
                if self.cursor.rowcount > 0:
                    return True
                return False  # Không có dòng nào cần update (có thể đã thanh toán rồi)
        except Exception as e:
            print(f"Lỗi thanh toán: {e}")
            return False
        finally:
            self.close()