from src.Model.LuongModel import LuongModel
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os


class LuongController:
    def __init__(self):
        self.model = LuongModel()

    # [ĐÃ SỬA TÊN HÀM] Từ get_bang_luong -> get_list_salary
    def get_list_salary(self, month_year):
        """
        Lấy danh sách lương theo tháng.
        Input: 'Tháng 12/2025'
        """
        try:
            parts = month_year.split('/')
            month = int(parts[0].replace("Tháng ", ""))
            year = int(parts[1])
            return self.model.get_bang_luong_thang(month, year)
        except Exception as e:
            print(f"Lỗi parse tháng: {e}")
            return []

    def thanh_toan_luong(self, idNV, month_str):
        if not idNV:
            return False, "Vui lòng chọn nhân viên!"

        try:
            parts = month_str.split('/')
            month = int(parts[0].replace("Tháng ", ""))
            year = int(parts[1])

            if self.model.update_payment_status(idNV, month, year):
                return True, "Đã xác nhận thanh toán lương!"
            else:
                return False, "Không có dữ liệu cần thanh toán hoặc lỗi hệ thống."
        except:
            return False, "Lỗi định dạng tháng!"

    # ================= XUẤT EXCEL =================
    def export_excel(self, month_year, save_path):
        # [CẬP NHẬT] Gọi đúng tên hàm mới get_list_salary
        data = self.get_list_salary(month_year)

        if not data: return False, "Không có dữ liệu để xuất!"

        try:
            # Chuẩn bị dữ liệu
            export_list = []
            total_money = 0

            for row in data:
                thuc_lanh = float(row['thucLanh'])
                total_money += thuc_lanh
                export_list.append({
                    "Mã NV": row['idNhanVien'],
                    "Họ Tên": row['hoTen'],
                    "Chức Vụ": row['tenChucVu'],
                    "Lương Cơ Bản": float(row['luongCoBan']),
                    "Tổng Giờ Làm": float(row['tongGioLamThang']),
                    "Thực Lãnh": thuc_lanh,
                    "Trạng Thái": "Đã thanh toán" if row['trangThai'] == 'DaThanhToan' else "Chưa thanh toán"
                })

            # Dòng tổng
            export_list.append({
                "Mã NV": "", "Họ Tên": "TỔNG CỘNG", "Chức Vụ": "",
                "Lương Cơ Bản": "", "Tổng Giờ Làm": "",
                "Thực Lãnh": total_money, "Trạng Thái": ""
            })

            # Xuất file
            df = pd.DataFrame(export_list)
            if not save_path.endswith(".xlsx"): save_path += ".xlsx"
            df.to_excel(save_path, index=False)

            return True, f"Đã xuất Excel: {save_path}"
        except Exception as e:
            return False, f"Lỗi xuất Excel: {e}"

    # ================= XUẤT PDF =================
    def export_pdf(self, month_year, save_path):
        # [CẬP NHẬT] Gọi đúng tên hàm mới get_list_salary
        data = self.get_list_salary(month_year)

        if not data: return False, "Không có dữ liệu!"

        try:
            if not save_path.endswith(".pdf"): save_path += ".pdf"

            c = canvas.Canvas(save_path, pagesize=A4)
            width, height = A4

            try:
                font_path = "C:/Windows/Fonts/arial.ttf"
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('Arial', font_path))
                    c.setFont("Arial", 12)
                else:
                    c.setFont("Helvetica", 12)
            except:
                c.setFont("Helvetica", 12)

            y = height - 50

            # Header
            c.drawString(200, y, f"BANG LUONG - {month_year.upper()}")
            y -= 40

            headers = ["ID", "HO TEN", "CHUC VU", "GIO", "THUC LANH"]
            x_positions = [30, 80, 250, 380, 450]

            for i, h in enumerate(headers):
                c.drawString(x_positions[i], y, h)

            y -= 10
            c.line(30, y, 550, y)
            y -= 20

            # Data
            total_money = 0
            for row in data:
                thuc_lanh = float(row['thucLanh'])
                total_money += thuc_lanh

                c.drawString(x_positions[0], y, str(row['idNhanVien']))
                c.drawString(x_positions[1], y, str(row['hoTen']))  # Cẩn thận tiếng Việt nếu dùng Helvetica
                c.drawString(x_positions[2], y, str(row['tenChucVu']))
                c.drawString(x_positions[3], y, str(row['tongGioLamThang']))
                c.drawString(x_positions[4], y, "{:,.0f}".format(thuc_lanh))

                y -= 20
                if y < 50:
                    c.showPage()
                    y = height - 50

            c.line(30, y, 550, y)
            y -= 20
            c.drawString(300, y, "TONG CONG:")
            c.drawString(450, y, "{:,.0f}".format(total_money))

            c.save()
            return True, f"Đã xuất PDF: {save_path}"

        except Exception as e:
            return False, f"Lỗi xuất PDF: {e}"