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

    def sync_monthly_salary(self, month, year):
        """
        [LOGIC MỚI] Tự động tạo dữ liệu lương cho tháng.
        - Tìm các ca làm việc trong bangChamCong chưa có trong bang Luong.
        - INSERT vào bang Luong, lấy luongCoBan HIỆN TẠI lưu vào luongNV (Snapshot).
        """
        self.connect()
        try:
            # Câu lệnh này chỉ thêm những ca chưa được tính lương
            # luongNV = Lương cơ bản hiện tại (Lưu cứng)
            # tongLuong = (Lương cơ bản / 26 / 8) * số giờ làm
            sql_sync = """
                INSERT INTO luong (idNhanVien, idChamCong, luongNV, soGioCong, tongLuong, ttThanhToan)
                SELECT 
                    b.idNhanVien,
                    b.idChamCong,
                    cv.luongCoBan, 
                    b.tongGioLam,
                    ROUND((cv.luongCoBan / 26 / 8) * b.tongGioLam, 0),
                    'ChuaThanhToan'
                FROM bangChamCong b
                JOIN nhanVien nv ON b.idNhanVien = nv.idNhanVien
                JOIN chucVu cv ON nv.idChucVu = cv.idChucVu
                WHERE MONTH(b.gioVao) = %s AND YEAR(b.gioVao) = %s
                AND b.idChamCong NOT IN (SELECT idChamCong FROM luong)
            """
            self.cursor.execute(sql_sync, (month, year))
            self.conn.commit()
        except Exception as e:
            print(f"Lỗi đồng bộ lương: {e}")
        finally:
            self.close()

    def get_bang_luong_thang(self, month, year):
        """
        Lấy dữ liệu TỪ BẢNG LUONG (đã lưu snapshot) để hiển thị.
        """
        self.connect()
        # Bước 1: Đồng bộ dữ liệu mới nhất trước
        # (Để đảm bảo nếu vừa có chấm công mới thì lương sẽ cập nhật ngay)
        self.close()  # Đóng để sync mở kết nối mới
        self.sync_monthly_salary(month, year)

        self.connect()  # Mở lại để select
        query = """
            SELECT 
                l.idNhanVien, 
                nv.hoTen, 
                cv.tenChucVu,

                -- Lấy mức lương cơ bản đã lưu trong bảng lương (Trung bình hoặc Max đều được vì trong 1 tháng thường không đổi)
                MAX(l.luongNV) as luongCoBanSnapshot,

                -- Tổng hợp từ chi tiết lương
                SUM(l.soGioCong) as tongGioLamThang,
                SUM(l.tongLuong) as thucLanh,

                -- Logic trạng thái: Nếu còn bất kỳ dòng nào chưa TT -> Chưa TT
                CASE 
                    WHEN SUM(CASE WHEN l.ttThanhToan = 'ChuaThanhToan' THEN 1 ELSE 0 END) > 0 THEN 'ChuaThanhToan'
                    ELSE 'DaThanhToan'
                END as trangThai

            FROM luong l
            JOIN nhanVien nv ON l.idNhanVien = nv.idNhanVien
            JOIN bangChamCong b ON l.idChamCong = b.idChamCong
            JOIN chucVu cv ON nv.idChucVu = cv.idChucVu
            WHERE MONTH(b.gioVao) = %s AND YEAR(b.gioVao) = %s
            GROUP BY l.idNhanVien, nv.hoTen, cv.tenChucVu
            ORDER BY l.idNhanVien ASC
        """
        try:
            self.cursor.execute(query, (month, year))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Lỗi lấy bảng lương: {e}")
            return []
        finally:
            self.close()

    def update_payment_status(self, idNV, month, year):
        """
        Cập nhật trạng thái thanh toán trong bảng LUONG
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
            self.cursor.execute(query, (idNV, month, year))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Lỗi thanh toán: {e}")
            return False
        finally:
            self.close()