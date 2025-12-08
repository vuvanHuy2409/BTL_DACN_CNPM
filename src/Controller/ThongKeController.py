from src.Model.ThongKeModel import ThongKeModel
from datetime import datetime


class ThongKeController:
    def __init__(self):
        self.model = ThongKeModel()

    def format_money(self, value):
        if not value: return "0 ₫"
        return "{:,.0f} ₫".format(float(value))

    def format_date_vn(self, date_str, mode="day"):
        if not date_str: return ""
        try:
            if mode == "year":
                dt = datetime.strptime(str(date_str), "%Y-%m")
                return dt.strftime("T%m")
            else:
                dt = datetime.strptime(str(date_str), "%Y-%m-%d")
                return dt.strftime("%d/%m")
        except:
            return str(date_str)

    def get_dashboard_summary(self, month, year):
        m = int(month) if month != "Tất cả" else None
        y = int(year)
        data = self.model.get_overview_stats(m, y)
        return {
            "doanh_thu": self.format_money(data['doanhThu']),
            "tong_don": f"{data['tongDon']} Đơn",
            "khach_moi": f"{data['khachMoi']} Khách"
        }

    def get_chart_and_table_data(self, mode_filter, month, year):
        m = int(month) if month and month != "Tất cả" else None
        y = int(year) if year else datetime.now().year

        raw_data = self.model.get_detailed_stats(mode_filter, m, y)

        chart_labels = []
        chart_values = []
        table_rows = []

        for row in raw_data:
            dt_raw = row['thoiGian']
            revenue = float(row['doanhThu']) if row['doanhThu'] else 0

            # Format biểu đồ
            label = self.format_date_vn(dt_raw, mode="year" if mode_filter == "year" else "day")
            chart_labels.append(label)
            chart_values.append(revenue)

            # Format Bảng (Chỉ còn 3 cột: Ngày | Số Đơn | Doanh Thu)
            table_rows.append((
                label,
                row['soDonHang'],
                self.format_money(revenue)
            ))

        return chart_labels, chart_values, table_rows