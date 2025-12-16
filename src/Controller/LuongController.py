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

    def _parse_month_year(self, month_str):
        """
        Hàm phụ trợ: Chuyển chuỗi 'Tháng 12/2025' thành (12, 2025)
        """
        try:
            # Chuỗi vào: "Tháng 12/2025"
            parts = month_str.split('/')
            month = int(parts[0].replace("Tháng ", "").strip())
            year = int(parts[1].strip())
            return month, year
        except Exception:
            return None, None

    def get_list_salary(self, month_year_str):
        """
        Lấy danh sách lương để hiển thị lên bảng.
        Logic: Gọi Model để đồng bộ snapshot trước, sau đó lấy dữ liệu về.
        """
        month, year = self._parse_month_year(month_year_str)
        if not month or not year:
            print("Lỗi định dạng tháng năm!")
            return []

        # Gọi Model lấy dữ liệu
        return self.model.get_bang_luong_thang(month, year)

    def thanh_toan_luong(self, idNV, month_year_str):
        """
        Xử lý sự kiện nút 'Thanh Toán'.
        """
        if not idNV:
            return False, "Vui lòng chọn nhân viên cần thanh toán!"

        month, year = self._parse_month_year(month_year_str)
        if not month:
            return False, "Lỗi định dạng tháng!"

        # Gọi Model update trạng thái
        success = self.model.update_payment_status(idNV, month, year)

        if success:
            return True, f"Đã cập nhật trạng thái 'Đã Thanh Toán' cho nhân viên ID {idNV}!"
        else:
            return False, "Không thể cập nhật (Có thể đã thanh toán rồi hoặc lỗi DB)."

    # ================= XUẤT EXCEL =================
    def export_excel(self, month_year_str, save_path):
        data = self.get_list_salary(month_year_str)

        if not data:
            return False, "Không có dữ liệu để xuất!"

        try:
            export_list = []
            total_money = 0

            # 1. Chuẩn bị dữ liệu cho DataFrame
            for row in data:
                # Xử lý các giá trị None hoặc Decimal từ SQL
                thuc_lanh = float(row['thucLanh']) if row['thucLanh'] else 0
                luong_snapshot = float(row['luongCoBanSnapshot']) if row['luongCoBanSnapshot'] else 0
                tong_gio = float(row['tongGioLamThang']) if row['tongGioLamThang'] else 0

                total_money += thuc_lanh

                # Map tên cột tiếng Việt
                export_list.append({
                    "Mã NV": row['idNhanVien'],
                    "Họ Tên": row['hoTen'],
                    "Chức Vụ": row['tenChucVu'],
                    "Lương Cơ Bản (Lưu)": luong_snapshot,
                    "Tổng Giờ Làm": tong_gio,
                    "Thực Lãnh": thuc_lanh,
                    "Trạng Thái": "Đã thanh toán" if row['trangThai'] == 'DaThanhToan' else "Chưa thanh toán"
                })

            # 2. Thêm dòng Tổng cộng ở cuối
            export_list.append({
                "Mã NV": "", "Họ Tên": "TỔNG CỘNG", "Chức Vụ": "",
                "Lương Cơ Bản (Lưu)": "", "Tổng Giờ Làm": "",
                "Thực Lãnh": total_money, "Trạng Thái": ""
            })

            # 3. Tạo DataFrame và lưu
            df = pd.DataFrame(export_list)

            # Đảm bảo đuôi file
            if not save_path.endswith(".xlsx"):
                save_path += ".xlsx"

            df.to_excel(save_path, index=False)

            return True, f"Đã xuất file thành công tại:\n{save_path}"
        except Exception as e:
            return False, f"Lỗi xuất Excel: {e}"

    # ================= XUẤT PDF =================
    def export_pdf(self, month_year_str, save_path):
        data = self.get_list_salary(month_year_str)

        if not data:
            return False, "Không có dữ liệu!"

        try:
            if not save_path.endswith(".pdf"):
                save_path += ".pdf"

            c = canvas.Canvas(save_path, pagesize=A4)
            width, height = A4

            # --- Cấu hình Font chữ (Hỗ trợ tiếng Việt) ---
            # Lưu ý: Cần trỏ đúng đường dẫn font trên máy tính của bạn
            font_name = "Helvetica"  # Mặc định nếu không tìm thấy font Việt
            try:
                # Đường dẫn font phổ biến trên Windows
                font_path = "C:/Windows/Fonts/arial.ttf"
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('Arial', font_path))
                    font_name = "Arial"
            except:
                pass  # Dùng font mặc định nếu lỗi

            c.setFont(font_name, 14)

            # --- Vẽ Tiêu Đề ---
            y = height - 50
            c.drawCentredString(width / 2, y, f"BẢNG LƯƠNG NHÂN VIÊN - {month_year_str.upper()}")

            y -= 30
            c.setFont(font_name, 10)
            c.drawString(30, y, f"Ngày xuất: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}")

            # --- Vẽ Header Bảng ---
            y -= 30
            c.setFont(font_name, 10)
            # Tọa độ X cho các cột
            x_pos = {
                "id": 30, "ten": 70, "chucvu": 220,
                "luong_luu": 320, "gio": 400, "thuc_lanh": 460
            }

            c.drawString(x_pos["id"], y, "ID")
            c.drawString(x_pos["ten"], y, "HỌ TÊN")
            c.drawString(x_pos["chucvu"], y, "CHỨC VỤ")
            c.drawString(x_pos["luong_luu"], y, "LƯƠNG GỐC")
            c.drawString(x_pos["gio"], y, "GIỜ")
            c.drawString(x_pos["thuc_lanh"], y, "THỰC LÃNH")

            # Kẻ đường gạch dưới header
            y -= 10
            c.line(30, y, 560, y)
            y -= 20

            # --- Vẽ Dữ Liệu ---
            total_money = 0

            for row in data:
                thuc_lanh = float(row['thucLanh']) if row['thucLanh'] else 0
                luong_snapshot = float(row['luongCoBanSnapshot']) if row['luongCoBanSnapshot'] else 0
                tong_gio = float(row['tongGioLamThang']) if row['tongGioLamThang'] else 0

                total_money += thuc_lanh

                c.drawString(x_pos["id"], y, str(row['idNhanVien']))
                c.drawString(x_pos["ten"], y, str(row['hoTen']))
                c.drawString(x_pos["chucvu"], y, str(row['tenChucVu']))

                # Format số tiền
                c.drawString(x_pos["luong_luu"], y, "{:,.0f}".format(luong_snapshot))
                c.drawString(x_pos["gio"], y, "{:,.2f}".format(tong_gio))
                c.drawString(x_pos["thuc_lanh"], y, "{:,.0f}".format(thuc_lanh))

                y -= 20

                # Nếu hết trang thì tạo trang mới
                if y < 50:
                    c.showPage()
                    c.setFont(font_name, 10)
                    y = height - 50

            # --- Vẽ Tổng Kết ---
            c.line(30, y + 10, 560, y + 10)
            y -= 10
            c.setFont(font_name, 12)
            c.drawString(320, y, "TỔNG CỘNG:")
            c.drawString(460, y, "{:,.0f} VNĐ".format(total_money))

            c.save()
            return True, f"Đã xuất PDF thành công tại:\n{save_path}"

        except Exception as e:
            return False, f"Lỗi xuất PDF: {e}"