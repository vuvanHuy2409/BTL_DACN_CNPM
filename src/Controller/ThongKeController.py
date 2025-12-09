from src.Model.ThongKeModel import ThongKeModel
from datetime import datetime
import pandas as pd  # <--- Import pandas


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
                return dt.strftime("%d/%m/%Y")  # Format đầy đủ năm cho Excel đẹp
        except:
            return str(date_str)

    def get_dashboard_summary(self, month, year):
        m = int(month) if month != "Tất cả" else None
        y = int(year)
        data = self.model.get_overview_stats(m, y)
        return {
            "doanh_thu": self.format_money(data['doanhThu']),
            "tong_don": f"{data['tongDon']} Đơn",
            "khach_moi": f"{data['khachMoi']} Khách",
            "raw_revenue": data['doanhThu'] or 0,  # Lưu số thô để tính toán nếu cần
            "raw_orders": data['tongDon'] or 0
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

            # Label cho biểu đồ (ngắn gọn)
            label_chart = self.format_date_vn(dt_raw, mode="year" if mode_filter == "year" else "day")

            chart_labels.append(label_chart)
            chart_values.append(revenue)

            # Label cho bảng (chi tiết hơn)
            table_rows.append((
                label_chart,
                row['soDonHang'],
                self.format_money(revenue)
            ))

        return chart_labels, chart_values, table_rows

    # ================= [MỚI] XUẤT EXCEL =================
    def export_report_to_excel(self, filepath, mode_filter, month, year):
        try:
            # 1. Lấy dữ liệu Tổng quan
            summary = self.get_dashboard_summary(month, year)

            # 2. Lấy dữ liệu Chi tiết (Gọi lại Model để lấy data raw chưa format tiền tệ)
            m = int(month) if month and month != "Tất cả" else None
            y = int(year) if year else datetime.now().year
            raw_details = self.model.get_detailed_stats(mode_filter, m, y)

            # 3. Tạo DataFrame cho Sheet Tổng quan
            df_summary = pd.DataFrame([{
                "Tiêu chí": "Doanh thu tổng", "Giá trị": summary['doanh_thu']
            }, {
                "Tiêu chí": "Tổng số đơn", "Giá trị": summary['tong_don']
            }, {
                "Tiêu chí": "Khách hàng mới", "Giá trị": summary['khach_moi']
            }, {
                "Tiêu chí": "Thời gian lọc", "Giá trị": f"Tháng {month} - Năm {year}"
            }])

            # 4. Tạo DataFrame cho Sheet Chi tiết
            data_rows = []
            for row in raw_details:
                dt_str = self.format_date_vn(row['thoiGian'], mode="year" if mode_filter == "year" else "day")
                data_rows.append({
                    "Thời Gian": dt_str,
                    "Số Lượng Đơn": row['soDonHang'],
                    "Doanh Thu (VNĐ)": float(row['doanhThu']) if row['doanhThu'] else 0
                })

            df_details = pd.DataFrame(data_rows)

            # 5. Ghi ra file Excel (Dùng ExcelWriter để ghi nhiều sheet)
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df_summary.to_excel(writer, sheet_name='Tổng Quan', index=False)
                df_details.to_excel(writer, sheet_name='Chi Tiết Doanh Thu', index=False)

                # Tùy chỉnh độ rộng cột (Optional)
                worksheet = writer.sheets['Chi Tiết Doanh Thu']
                worksheet.column_dimensions['A'].width = 20
                worksheet.column_dimensions['C'].width = 20

            return True, f"Xuất Excel thành công!\nĐường dẫn: {filepath}"
        except Exception as e:
            return False, f"Lỗi xuất Excel: {str(e)}"