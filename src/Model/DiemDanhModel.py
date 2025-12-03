import mysql.connector
from src.config.db_config import DB_CONFIG
from datetime import datetime


class DiemDanhModel:
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

    # ================= 1. DANH SÁCH & TRẠNG THÁI (CHO BẢNG BÊN TRÁI) =================
    def get_list_nhan_vien_sorted(self):
        """
        Lấy danh sách nhân viên kèm trạng thái chấm công HÔM NAY.
        Logic Sắp xếp:
        1. Chưa chấm công (status = 0) - Ưu tiên hiển thị
        2. Đang làm (status = 1)
        3. Đã về (status = 2)
        """
        self.connect()
        query = """
            SELECT 
                nv.idNhanVien, 
                nv.hoTen, 
                cv.tenChucVu,
                CASE 
                    WHEN b.gioVao IS NULL THEN 0 -- Chưa chấm (Màu đỏ)
                    WHEN b.gioRa IS NULL THEN 1  -- Đang làm (Màu vàng)
                    ELSE 2                       -- Đã ra (Màu xanh)
                END as trangThai,
                b.gioVao,
                b.gioRa
            FROM nhanVien nv
            JOIN chucVu cv ON nv.idChucVu = cv.idChucVu
            LEFT JOIN bangChamCong b ON nv.idNhanVien = b.idNhanVien AND DATE(b.gioVao) = CURDATE()
            WHERE nv.trangThaiLamViec = 'DangLamViec'
            ORDER BY trangThai ASC, nv.idNhanVien ASC
        """
        try:
            if self.cursor:
                self.cursor.execute(query)
                return self.cursor.fetchall()
            return []
        finally:
            self.close()

    # ================= 2. NHẬT KÝ HOẠT ĐỘNG (CHO BẢNG BÊN PHẢI) =================
    def get_logs_filtered(self, date_str, filter_type):
        """
        Lấy log hoạt động có lọc.
        - filter_type: 'day' (yyyy-mm-dd), 'month' (yyyy-mm), 'year' (yyyy)
        """
        self.connect()
        condition = ""

        # Xây dựng điều kiện lọc SQL động
        if filter_type == 'day':
            condition = "AND DATE(b.gioVao) = %s"
        elif filter_type == 'month':
            condition = "AND DATE_FORMAT(b.gioVao, '%Y-%m') = %s"
        elif filter_type == 'year':
            condition = "AND YEAR(b.gioVao) = %s"

        query = f"""
            SELECT b.gioVao, b.gioRa, nv.hoTen
            FROM bangChamCong b
            JOIN nhanVien nv ON b.idNhanVien = nv.idNhanVien
            WHERE 1=1 {condition}
            ORDER BY b.gioVao DESC
        """
        try:
            if self.cursor:
                self.cursor.execute(query, (date_str,))
                return self.cursor.fetchall()
            return []
        except Exception as e:
            print(f"Lỗi lấy log: {e}")
            return []
        finally:
            self.close()

    # ================= 3. XỬ LÝ CHẤM CÔNG (LOGIC CHÍNH) =================
    def xu_ly_cham_cong(self, idNV):
        """
        Xử lý Check-in / Check-out.
        Quy tắc: Nếu làm > 8.5 tiếng -> Tính là 8 tiếng.
        """
        self.connect()
        try:
            # 1. Tìm bản ghi chấm công gần nhất của nhân viên trong ngày hôm nay
            check_sql = """
                SELECT idChamCong, gioVao 
                FROM bangChamCong 
                WHERE idNhanVien = %s AND DATE(gioVao) = CURDATE()
                ORDER BY idChamCong DESC LIMIT 1
            """
            self.cursor.execute(check_sql, (idNV,))
            record = self.cursor.fetchone()

            # TRƯỜNG HỢP 1: CHECK-IN (Chưa có dữ liệu hôm nay)
            if not record:
                insert_sql = "INSERT INTO bangChamCong (idNhanVien, gioVao) VALUES (%s, NOW())"
                self.cursor.execute(insert_sql, (idNV,))
                self.conn.commit()
                return True, "CHECK-IN", 0.0

            # TRƯỜNG HỢP 2: CHECK-OUT (Cập nhật giờ ra mới nhất)
            else:
                gio_vao = record['gioVao']
                now = datetime.now()

                # Tính khoảng thời gian (giây)
                diff_seconds = (now - gio_vao).total_seconds()
                so_gio_thuc = diff_seconds / 3600.0  # Đổi ra giờ

                # [QUY TẮC NGHIỆP VỤ]
                # Nếu làm > 8.5 giờ (8h30p) thì chỉ tính 8 giờ công
                if so_gio_thuc > 8.5:
                    tong_gio_tinh = 8.0
                else:
                    tong_gio_tinh = round(so_gio_thuc, 2)

                update_sql = """
                    UPDATE bangChamCong 
                    SET gioRa = NOW(), 
                        soGioCong = %s,
                        tongGioLam = %s
                    WHERE idChamCong = %s
                """
                self.cursor.execute(update_sql, (tong_gio_tinh, tong_gio_tinh, record['idChamCong']))
                self.conn.commit()

                return True, "CHECK-OUT", tong_gio_tinh

        except Exception as e:
            print(f"Lỗi chấm công: {e}")
            return False, str(e), 0
        finally:
            self.close()

    # ================= 4. HỖ TRỢ XUẤT EXCEL =================
    def get_employee_details(self, idNV):
        """Lấy thông tin chi tiết nhân viên để ghi vào Header Excel"""
        self.connect()
        query = """
            SELECT nv.idNhanVien, nv.hoTen, nv.soDienThoai, nv.email, cv.tenChucVu
            FROM nhanVien nv
            JOIN chucVu cv ON nv.idChucVu = cv.idChucVu
            WHERE nv.idNhanVien = %s
        """
        try:
            if self.cursor:
                self.cursor.execute(query, (idNV,))
                return self.cursor.fetchone()
            return None
        finally:
            self.close()

    def get_individual_attendance(self, idNV, month, year):
        """Lấy dữ liệu chấm công chi tiết của 1 nhân viên trong tháng"""
        self.connect()
        query = """
            SELECT 
                DATE(gioVao) as Ngay,
                TIME(gioVao) as GioVao,
                TIME(gioRa) as GioRa,
                soGioCong,
                tongGioLam
            FROM bangChamCong
            WHERE idNhanVien = %s 
              AND MONTH(gioVao) = %s 
              AND YEAR(gioVao) = %s
            ORDER BY gioVao ASC
        """
        try:
            if self.cursor:
                self.cursor.execute(query, (idNV, month, year))
                return self.cursor.fetchall()
            return []
        finally:
            self.close()