import mysql.connector
from datetime import datetime, timedelta
from src.config.db_config import DB_CONFIG


class ThongKeModel:
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

    # ================= 1. THẺ TỔNG QUAN =================
    def get_overview_stats(self, month=None, year=None):
        self.connect()
        try:
            params = []
            where_clause = "WHERE trangThai = 2"

            if year:
                where_clause += " AND YEAR(ngayTao) = %s"
                params.append(year)
                if month:
                    where_clause += " AND MONTH(ngayTao) = %s"
                    params.append(month)

            sql = f"""
                SELECT 
                    SUM(tongTien) as doanhThu, 
                    COUNT(idHoaDon) as tongDon,
                    COUNT(DISTINCT idKhachHang) as khachMoi
                FROM hoaDon 
                {where_clause}
            """
            self.cursor.execute(sql, tuple(params))
            res = self.cursor.fetchone()

            return {
                "doanhThu": res['doanhThu'] if res['doanhThu'] else 0,
                "tongDon": res['tongDon'] if res['tongDon'] else 0,
                "khachMoi": res['khachMoi'] if res['khachMoi'] else 0
            }
        finally:
            self.close()

    # ================= 2. DỮ LIỆU BIỂU ĐỒ & BẢNG (ĐÃ TỐI ƯU) =================
    def get_detailed_stats(self, mode="7_days", month=None, year=None):
        """
        Chỉ lấy Doanh thu và Số đơn (Bỏ chi phí, lợi nhuận)
        """
        self.connect()
        try:
            group_format = "%Y-%m-%d"
            select_date = "DATE(ngayTao)"
            where_sql = "WHERE trangThai = 2"
            params = []

            today = datetime.now()

            if mode == "7_days":
                seven_days_ago = today - timedelta(days=6)
                where_sql += " AND ngayTao >= %s"
                params.append(seven_days_ago.strftime('%Y-%m-%d'))

            elif mode == "month":
                if year:
                    where_sql += " AND YEAR(ngayTao) = %s";
                    params.append(year)
                if month:
                    where_sql += " AND MONTH(ngayTao) = %s";
                    params.append(month)

            elif mode == "year":
                select_date = "DATE_FORMAT(ngayTao, '%Y-%m')"
                if year:
                    where_sql += " AND YEAR(ngayTao) = %s";
                    params.append(year)

            # Câu Query đơn giản hơn rất nhiều (Không JOIN)
            query = f"""
                SELECT 
                    {select_date} as thoiGian,
                    COUNT(idHoaDon) as soDonHang,
                    SUM(tongTien) as doanhThu
                FROM hoaDon
                {where_sql}
                GROUP BY thoiGian
                ORDER BY thoiGian ASC
            """

            self.cursor.execute(query, tuple(params))
            return self.cursor.fetchall()

        except Exception as e:
            print(f"Lỗi Statistical: {e}")
            return []
        finally:
            self.close()