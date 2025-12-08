from src.Model.HoaDonModel import HoaDonModel
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import unicodedata
import os


class HoaDonController:
    def __init__(self):
        self.model = HoaDonModel()

    # =========================================================================
    # 1. CÁC HÀM HỖ TRỢ (HELPER)
    # =========================================================================

    def format_currency(self, value):
        """Định dạng số thành tiền tệ (VD: 100,000 VNĐ)"""
        if value is None: return "0 VNĐ"
        return "{:,.0f} VNĐ".format(float(value))

    def format_date(self, dt_obj):
        """Định dạng ngày tháng"""
        if not dt_obj: return "-"
        if isinstance(dt_obj, str): return dt_obj
        return dt_obj.strftime("%d/%m/%Y %H:%M")

    def remove_accents(self, input_str):
        """Chuyển tiếng Việt có dấu -> không dấu (Dùng khi xuất PDF thiếu font)"""
        if not input_str: return ""
        nfkd = unicodedata.normalize('NFKD', str(input_str))
        return "".join([c for c in nfkd if not unicodedata.combining(c)])

    # =========================================================================
    # 2. XỬ LÝ DỮ LIỆU ĐỂ HIỂN THỊ (CORE LOGIC)
    # =========================================================================

    def process_data(self, data):
        """
        Xử lý dữ liệu thô từ Model để hiển thị đẹp trên View.
        Tại đây xử lý logic: noiDungCK vs ID, PaymentMethod, StatusText
        """
        processed = []
        for row in data:
            item = row.copy()

            # --- 1. Format cơ bản ---
            item['tongTienFmt'] = self.format_currency(item['tongTien'])
            item['ngayTaoFmt'] = self.format_date(item['ngayTao'])

            # --- 2. Xử lý Mã hiển thị (Yêu cầu mới) ---
            # Nếu có nội dung chuyển khoản -> Hiển thị nội dung đó
            # Nếu không -> Hiển thị ID hóa đơn (#123)
            ck_content = item.get('noiDungCK')
            if ck_content and str(ck_content).strip():
                item['maHienThi'] = str(ck_content)
            else:
                item['maHienThi'] = f"#{item['idHoaDon']}"

            # --- 3. Xử lý Trạng thái & Hình thức thanh toán ---
            trang_thai = item['trangThai']

            # Map trạng thái sang chữ
            status_map = {0: "Đã hủy", 1: "Chờ thanh toán", 2: "Đã thanh toán"}
            item['statusText'] = status_map.get(trang_thai, "Khác")

            # Logic hiển thị Phương thức thanh toán (Payment Method)
            if trang_thai != 2:
                item['paymentMethod'] = "-"  # Chưa thanh toán xong thì để trống
            else:
                # Kiểm tra dữ liệu Ngân hàng được JOIN từ Model
                bank_name = item.get('tenNganHang')
                acc_num = item.get('soTaiKhoan')

                if bank_name:
                    # Rút gọn số tài khoản nếu quá dài
                    tk_short = f"...{acc_num[-4:]}" if (acc_num and len(str(acc_num)) > 4) else str(acc_num)
                    item['paymentMethod'] = f"CK ({bank_name} - {tk_short})"
                else:
                    item['paymentMethod'] = "Tiền mặt"

            processed.append(item)

        return processed

    # =========================================================================
    # 3. CÁC HÀM GỌI MODEL (GET DATA)
    # =========================================================================

    def get_list_invoices(self):
        """Lấy danh sách mặc định (gọi filter rỗng)"""
        data = self.model.filter_invoices()
        return self.process_data(data)

    def filter_invoices(self, day, month, year, keyword):
        """Lọc hóa đơn theo tiêu chí"""
        data = self.model.filter_invoices(day, month, year, keyword)
        return self.process_data(data)

    def get_details(self, id_hd):
        """Lấy chi tiết sản phẩm để hiển thị popup"""
        details = self.model.get_invoice_details(id_hd)
        for row in details:
            row['donGiaFmt'] = self.format_currency(row['donGia'])
            row['thanhTienFmt'] = self.format_currency(row['thanhTien'])
        return details

    # =========================================================================
    # 4. CÁC HÀM THAO TÁC (CRUD)
    # =========================================================================

    def delete_invoice(self, id_hd):
        """Hủy hóa đơn"""
        return self.model.delete_invoice(id_hd)

    def save_edited_invoice(self, id_hd, status_text, items_list):
        """Lưu lại hóa đơn sau khi sửa"""
        status_map = {"Đã hủy": 0, "Chờ thanh toán": 1, "Đã thanh toán": 2}
        status_code = status_map.get(status_text)

        if status_code is None: return False, "Trạng thái không hợp lệ!"
        if not items_list and status_code != 0: return False, "Hóa đơn phải có ít nhất 1 món!"

        if self.model.update_invoice_full_transaction(id_hd, status_code, items_list):
            return True, "Cập nhật thành công!"
        return False, "Lỗi cập nhật Database!"

    # =========================================================================
    # 5. CHỨC NĂNG XUẤT PDF
    # =========================================================================

    def export_invoice_pdf(self, id_hd, save_path):
        try:
            # 1. Lấy dữ liệu Header & Detail
            # Lọc chính xác theo ID
            header_raw = self.model.filter_invoices(keyword=str(id_hd))
            # Tìm đúng ID trong list kết quả (vì keyword '1' có thể ra '10', '11')
            header_item = next((item for item in header_raw if str(item['idHoaDon']) == str(id_hd)), None)

            if not header_item: return False, "Không tìm thấy thông tin hóa đơn!"

            # Xử lý data header để có các text hiển thị (PaymentMethod, etc.)
            header = self.process_data([header_item])[0]
            details = self.model.get_invoice_details(id_hd)

            if not save_path.endswith(".pdf"): save_path += ".pdf"

            # 2. Cấu hình Font chữ (Arial để gõ tiếng Việt)
            c = canvas.Canvas(save_path, pagesize=A4)
            width, height = A4

            font_path = "arial.ttf"  # Cần file này ở thư mục gốc project
            has_unicode = False

            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('Arial', font_path))
                    c.setFont("Arial", 12)
                    has_unicode = True
                except:
                    pass

            if not has_unicode: c.setFont("Helvetica", 12)

            # Hàm nội bộ: Chọn text có dấu hoặc không dấu tùy font
            def txt(text):
                return str(text) if has_unicode else self.remove_accents(text)

            # 3. Vẽ PDF
            y = height - 50

            # --- Header Quán ---
            c.setFont("Arial" if has_unicode else "Helvetica-Bold", 20)
            c.drawCentredString(width / 2, y, txt("HÓA ĐƠN THANH TOÁN"))
            y -= 30
            c.setFont("Arial" if has_unicode else "Helvetica", 12)
            c.drawCentredString(width / 2, y, txt("Coffee Shop Manager System"))

            # --- Thông tin Hóa đơn ---
            y -= 50
            x_left = 50
            c.drawString(x_left, y, txt(f"Mã hóa đơn: #{id_hd}"))

            # Nếu có nội dung CK thì hiển thị thêm dòng này trong PDF
            if header.get('noiDungCK'):
                c.drawString(x_left + 250, y, txt(f"Ref: {header['noiDungCK']}"))

            y -= 20
            c.drawString(x_left, y, txt(f"Ngày tạo: {header['ngayTaoFmt']}"))
            y -= 20
            c.drawString(x_left, y, txt(f"Khách hàng: {header['tenKhachHang']}"))
            y -= 20
            c.drawString(x_left, y, txt(f"Nhân viên: {header['tenNhanVien']}"))

            # --- Bảng Sản phẩm ---
            y -= 40
            # Vẽ tiêu đề bảng
            c.line(x_left, y + 15, width - 50, y + 15)
            c.setFont("Arial" if has_unicode else "Helvetica-Bold", 11)

            c.drawString(x_left, y, txt("Tên Món"))
            c.drawString(320, y, txt("SL"))
            c.drawRightString(430, y, txt("Đơn Giá"))  # Căn phải
            c.drawRightString(540, y, txt("Thành Tiền"))  # Căn phải

            c.line(x_left, y - 5, width - 50, y - 5)

            # Vẽ từng dòng sản phẩm
            c.setFont("Arial" if has_unicode else "Helvetica", 11)
            y -= 25
            for item in details:
                name = txt(item['tenSanPham'])
                if len(name) > 40: name = name[:37] + "..."  # Cắt tên dài

                c.drawString(x_left, y, name)
                c.drawString(320, y, str(item['soLuong']))

                # Format số tiền không có chữ VNĐ để căn thẳng hàng
                don_gia = "{:,.0f}".format(item['donGia'])
                thanh_tien = "{:,.0f}".format(item['thanhTien'])

                c.drawRightString(430, y, don_gia)
                c.drawRightString(540, y, thanh_tien)
                y -= 20

            # --- Tổng kết ---
            y -= 10
            c.line(x_left, y, width - 50, y)
            y -= 30

            c.setFont("Arial" if has_unicode else "Helvetica-Bold", 14)
            c.drawString(300, y, txt("TỔNG CỘNG:"))
            c.drawRightString(540, y, header['tongTienFmt'])  # Có chữ VNĐ

            y -= 30
            c.setFont("Arial" if has_unicode else "Helvetica-Oblique", 11)
            c.drawString(x_left, y, txt(f"Hình thức TT: {header['paymentMethod']}"))

            # --- Footer ---
            c.setFont("Arial" if has_unicode else "Helvetica", 10)
            c.drawCentredString(width / 2, 50, txt("Cảm ơn quý khách & Hẹn gặp lại!"))

            c.save()
            return True, f"Đã xuất file PDF thành công!\n{save_path}"

        except Exception as e:
            return False, f"Lỗi xuất PDF: {str(e)}"