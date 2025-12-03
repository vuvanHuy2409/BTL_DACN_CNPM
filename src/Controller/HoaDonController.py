from src.Model.HoaDonModel import HoaDonModel
from datetime import datetime
import pandas as pd  # Cần cài thư viện pandas và openpyxl


class HoaDonController:
    def __init__(self):
        self.model = HoaDonModel()

    def format_currency(self, value):
        return "{:,.0f} VNĐ".format(float(value))

    def format_date(self, dt_obj):
        if not dt_obj: return ""
        if isinstance(dt_obj, str): return dt_obj
        return dt_obj.strftime("%d/%m/%Y %H:%M")

    def get_list_invoices(self):
        data = self.model.get_all_invoices()
        for row in data:
            row['tongTienFmt'] = self.format_currency(row['tongTien'])
            row['ngayTaoFmt'] = self.format_date(row['ngayTao'])
            # Hiển thị ngày cập nhật
            row['ngaySuaFmt'] = self.format_date(row['ngayCapNhat']) if row['ngayCapNhat'] else "-"

            status_map = {0: "Đã hủy", 1: "Chờ thanh toán", 2: "Đã thanh toán"}
            row['statusText'] = status_map.get(row['trangThai'], "Khác")
        return data

    def get_details(self, id_hd):
        details = self.model.get_invoice_details(id_hd)
        for row in details:
            row['donGiaFmt'] = self.format_currency(row['donGia'])
            row['thanhTienFmt'] = self.format_currency(row['thanhTien'])
        return details

    # [MỚI] Hàm xử lý sửa trạng thái
    def edit_invoice(self, id_hd, status_text):
        # Map text sang ID trạng thái
        status_map = {"Đã hủy": 0, "Chờ thanh toán": 1, "Đã thanh toán": 2}
        status_code = status_map.get(status_text)

        if status_code is None:
            return False, "Trạng thái không hợp lệ!"

        if self.model.update_invoice_status(id_hd, status_code):
            return True, "Cập nhật thành công!"
        return False, "Lỗi cập nhật Database!"

    # [MỚI] Hàm xuất Excel chi tiết 1 hóa đơn
    def export_invoice_detail(self, id_hd, save_path):
        try:
            # 1. Lấy dữ liệu chi tiết
            details = self.model.get_invoice_details(id_hd)

            if not details:
                return False, "Hóa đơn này không có chi tiết món!"

            # 2. Chuẩn bị dữ liệu cho Pandas
            export_data = []
            for item in details:
                export_data.append({
                    "Tên Món": item['tenSanPham'],
                    "Số Lượng": item['soLuong'],
                    "Đơn Giá": float(item['donGia']),
                    "Thuế VAT (%)": float(item['thueVAT']),
                    "Thành Tiền": float(item['thanhTien'])
                })

            # 3. Tạo DataFrame và Xuất
            df = pd.DataFrame(export_data)

            # Đảm bảo đuôi file
            if not save_path.endswith(".xlsx"):
                save_path += ".xlsx"

            df.to_excel(save_path, index=False)
            return True, f"Đã xuất file tại:\n{save_path}"

        except Exception as e:
            return False, f"Lỗi xuất file: {str(e)}"