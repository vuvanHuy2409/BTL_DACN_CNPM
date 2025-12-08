from src.Model.TrangChuModel import TrangChuModel
import os
import random
import string
import requests
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import unicodedata


class TrangChuController:
    def __init__(self):
        self.model = TrangChuModel()
        self.selected_table_id = None

        # Cấu hình Thuế VAT (10%)
        # Logic: Giá bán trong Menu là giá đã bao gồm thuế (Gross Price)
        self.VAT_RATE = 0.10

        # Tạo thư mục lưu hóa đơn
        self.invoice_dir = "src/hoadon"
        if not os.path.exists(self.invoice_dir):
            os.makedirs(self.invoice_dir)

    # ================= 1. CÁC HÀM TIỆN ÍCH (UTILS) =================
    def remove_accents(self, input_str):
        """Chuyển tiếng Việt có dấu thành không dấu (Để xuất PDF không lỗi font)"""
        if not input_str: return ""
        nfkd = unicodedata.normalize('NFKD', str(input_str))
        return "".join([c for c in nfkd if not unicodedata.combining(c)])

    def format_money(self, value):
        """Định dạng tiền tệ: 100000 -> 100,000"""
        return "{:,.0f}".format(value)

    def generate_invoice_code(self):
        """
        Tạo mã hóa đơn: HD-DDMMYYYY-XXXYY
        VD: HD-09122025-123Ab
        """
        date_str = datetime.now().strftime('%d%m%Y')
        # 3 số ngẫu nhiên
        random_digits = f"{random.randint(0, 999):03d}"
        # 2 chữ cái ngẫu nhiên (kết hợp hoa thường)
        random_chars = ''.join(random.choices(string.ascii_letters, k=2))

        return f"HD-{date_str}-{random_digits}{random_chars}"

    # ================= 2. QUẢN LÝ MENU & BÀN =================
    def get_menu_grouped_by_category(self):
        result = []
        categories = self.model.get_all_categories()
        for cat in categories:
            prods = self.model.get_products_by_category(cat['idDanhMuc'])
            if prods:
                result.append({'category_name': cat['tenDanhMuc'], 'products': prods})
        return result

    def select_table(self, table_id):
        self.selected_table_id = table_id

    def get_table_status(self, table_id):
        active_ids = self.model.get_active_tables()
        if table_id == self.selected_table_id: return "selected"
        if table_id in active_ids: return "active"
        return "empty"

    def get_table_total_money(self, table_id):
        active_infos = self.model.get_active_tables_info()
        for row in active_infos:
            if row['idBan'] == table_id:
                return float(row['tongTien']) if row['tongTien'] else 0
        return 0

    # ================= 3. QUẢN LÝ GIỎ HÀNG (CART) =================
    def get_current_invoice_id(self):
        if not self.selected_table_id: return None
        return self.model.get_active_invoice_id(self.selected_table_id)

    def add_to_cart(self, product, id_nv_login):
        if not self.selected_table_id: return False, "Chưa chọn bàn!"

        id_hd = self.get_current_invoice_id()
        if not id_hd:
            id_hd = self.model.create_invoice_for_table(id_nv_login, self.selected_table_id)

        if not id_hd: return False, "Lỗi tạo hóa đơn!"

        ok = self.model.add_or_update_item(id_hd, product['idSanPham'], 1, float(product['giaBan']))
        if ok: self.model.update_invoice_total_money(id_hd)
        return ok, "Thêm thành công"

    def remove_item_from_cart(self, product_name):
        id_hd = self.get_current_invoice_id()
        if not id_hd: return False

        details = self.model.get_invoice_details(id_hd)
        target_id = None
        for d in details:
            if d['tenSanPham'] == product_name:
                target_id = d['idSanPham']
                break

        if target_id:
            ok = self.model.add_or_update_item(id_hd, target_id, -1, 0)
            if ok: self.model.update_invoice_total_money(id_hd)
            return ok
        return False

    def get_cart_display(self):
        """Dữ liệu hiển thị đơn giản cho Treeview (View)"""
        id_hd = self.get_current_invoice_id()
        if not id_hd: return [], "0", 0

        details = self.model.get_invoice_details(id_hd)
        display_list = []
        total_bill = 0
        for item in details:
            money = float(item['thanhTien'])
            total_bill += money
            display_list.append((item['tenSanPham'], item['soLuong'], self.format_money(money)))
        return display_list, self.format_money(total_bill), total_bill

    def get_cart_display_full_info(self):
        """Dữ liệu chi tiết cho PDF (Trả về số thực để tính toán)"""
        id_hd = self.get_current_invoice_id()
        if not id_hd: return [], "0", 0

        details = self.model.get_invoice_details(id_hd)
        display_list = []
        total_bill = 0
        for item in details:
            money = float(item['thanhTien'])
            total_bill += money
            display_list.append((
                item['tenSanPham'],
                item['soLuong'],
                self.format_money(float(item['donGia'])),
                money  # Raw number for PDF calculation
            ))
        return display_list, self.format_money(total_bill), total_bill

    def clear_current_cart(self):
        return self.model.cancel_invoice(self.get_current_invoice_id())

    # ================= 4. KHÁCH HÀNG =================
    def get_current_table_customer(self):
        id_hd = self.get_current_invoice_id()
        if id_hd: return self.model.get_invoice_customer(id_hd)
        return None

    def find_and_assign_customer(self, sdt, id_nv_login=1):
        cust = self.model.search_customer(sdt)
        if cust:
            id_hd = self.get_current_invoice_id()
            if not id_hd:
                id_hd = self.model.create_invoice_for_table(id_nv_login, self.selected_table_id)
            if id_hd:
                self.model.update_invoice_customer(id_hd, cust['idKhachHang'])
                return True, cust
        return False, None

    def create_customer(self, ten, sdt, dob_str):
        try:
            d_obj = datetime.strptime(dob_str, "%d/%m/%Y")
            d_sql = d_obj.strftime("%Y-%m-%d")
            id_new = self.model.add_customer(ten, sdt, d_sql)
            return (True, "Thêm thành công!") if id_new else (False, "Lỗi thêm khách!")
        except:
            return False, "Lỗi ngày sinh!"

    def get_customer_suggestions(self, sdt_part):
        if not sdt_part: return []
        return self.model.suggest_customers_by_phone(sdt_part)

    # ================= 5. THANH TOÁN & PDF & QR =================
    def get_bank_list(self):
        return self.model.get_active_banks()

    def get_qr_image_path(self, bank_info, amount, content):
        """Gọi API VietQR tạo ảnh"""
        try:
            api_url = f"https://img.vietqr.io/image/{bank_info['maNganHang']}-{bank_info['soTaiKhoan']}-compact.png"
            params = {'amount': int(amount), 'addInfo': content, 'accountName': bank_info['tenTaiKhoan']}
            res = requests.get(api_url, params=params)
            if res.status_code == 200:
                path = "temp_qr.png"
                with open(path, "wb") as f: f.write(res.content)
                return path
        except:
            return None
        return None

    def create_pdf(self, filename, invoice_info, items, totals, qr_path=None):
        """
        Tạo PDF hóa đơn chi tiết, đẹp mắt, có xử lý phân trang và QR code.
        """
        try:
            c = canvas.Canvas(filename, pagesize=A4)
            width, height = A4

            # Hàm rút gọn bỏ dấu
            def txt(t):
                return self.remove_accents(str(t))

            # --- HEADER ---
            y = 800
            c.setFont("Helvetica-Bold", 22)
            c.drawCentredString(width / 2, y, "COFFEE SHOP RECEIPT")
            y -= 25
            c.setFont("Helvetica", 10)
            c.drawCentredString(width / 2, y, "Dia chi: 123 Duong ABC, Quan 1, TP.HCM")
            y -= 15
            c.drawCentredString(width / 2, y, "Hotline: 0909 123 456")
            y -= 25
            c.line(50, y, 545, y)  # Kẻ ngang

            # --- THÔNG TIN CHUNG ---
            y -= 25
            c.setFont("Helvetica", 11)

            # Cột trái
            c.drawString(50, y, txt(f"Ma HD: {invoice_info['code']}"))
            c.drawString(50, y - 15, txt(f"Ban: {invoice_info['table']}"))
            c.drawString(50, y - 30, txt(f"Vao: {invoice_info['check_in']}"))
            c.drawString(50, y - 45, txt(f"Ra:  {invoice_info['check_out']}"))

            # Cột phải
            c.drawRightString(545, y, txt(f"Nhan vien: {invoice_info['staff']}"))
            c.drawRightString(545, y - 15, txt(f"Khach: {invoice_info['customer']}"))
            c.drawRightString(545, y - 30, txt(f"HTTT: {invoice_info['payment_method']}"))

            y -= 65

            # --- BẢNG SẢN PHẨM ---
            c.line(50, y, 545, y)
            y -= 15
            c.setFont("Helvetica-Bold", 10)
            c.drawString(50, y, "TEN MON")
            c.drawCentredString(300, y, "SL")
            c.drawRightString(420, y, "DON GIA")
            c.drawRightString(545, y, "THANH TIEN")
            y -= 10
            c.line(50, y, 545, y)
            y -= 20

            c.setFont("Helvetica", 10)
            for item in items:
                # item: (Name, Qty, Price_Str, Raw_Total)
                name = txt(item[0])
                if len(name) > 40: name = name[:37] + "..."  # Cắt tên dài nếu quá khổ
                qty = str(item[1])
                price = item[2]
                row_total = self.format_money(item[3])

                c.drawString(50, y, name)
                c.drawCentredString(300, y, qty)
                c.drawRightString(420, y, price)
                c.drawRightString(545, y, row_total)
                y -= 20

                # --- XỬ LÝ SANG TRANG NẾU HẾT CHỖ ---
                if y < 100:
                    c.showPage()
                    y = 800
                    c.setFont("Helvetica", 10)  # Set lại font cho trang mới

            # --- TỔNG KẾT ---
            y -= 10
            c.line(50, y, 545, y)
            y -= 25

            c.setFont("Helvetica", 10)
            c.drawRightString(450, y, "Tam tinh:")
            c.drawRightString(545, y, self.format_money(totals['subtotal']))
            y -= 15
            c.drawRightString(450, y, f"VAT ({int(self.VAT_RATE * 100)}%):")
            c.drawRightString(545, y, self.format_money(totals['vat']))
            y -= 20

            c.setFont("Helvetica-Bold", 14)
            c.drawRightString(450, y, "TONG CONG:")
            c.drawRightString(545, y, f"{self.format_money(totals['total'])} VND")

            # --- VẼ MÃ QR (ĐÃ FIX LỖI) ---
            if qr_path and os.path.exists(qr_path):
                # Kiểm tra còn đủ chỗ vẽ QR không (cần khoảng 150px)
                if y < 150:
                    c.showPage()  # Sang trang mới
                    y = 750  # Reset y

                y -= 120  # Dành không gian

                # Vẽ khung viền QR
                c.rect((width - 104) / 2, y - 2, 104, 104, stroke=1, fill=0)
                # Vẽ ảnh QR
                c.drawImage(qr_path, (width - 100) / 2, y, width=100, height=100)

                y -= 15
                c.setFont("Helvetica-Oblique", 8)
                c.drawCentredString(width / 2, y, "(Quet ma de doi chieu giao dich)")

            # --- FOOTER ---
            # Luôn vẽ ở chân trang
            c.setFont("Helvetica-Oblique", 10)
            c.drawCentredString(width / 2, 30, "Xin cam on quy khach va hen gap lai!")

            c.save()
            return True
        except Exception as e:
            print(f"Lỗi tạo PDF: {e}")
            return False

    def process_payment(self, method="TienMat", id_nv=1, bank_info=None, noi_dung_ck=None, qr_path=None):
        """
        Quy trình thanh toán:
        1. Tính toán tiền, thuế.
        2. Lấy thông tin Header.
        3. Cập nhật Database (Chốt đơn).
        4. Cộng điểm tích lũy.
        5. Xuất PDF (kèm QR nếu có).
        """
        id_hd = self.get_current_invoice_id()
        if not id_hd: return False, "Bàn trống!"

        # 1. Tính toán
        cart_items, _, total_bill = self.get_cart_display_full_info()

        # Tách VAT (Giả sử Total Bill là giá Gross đã gồm thuế)
        subtotal = total_bill / (1 + self.VAT_RATE)
        vat_amount = total_bill - subtotal
        totals = {'subtotal': subtotal, 'vat': vat_amount, 'total': total_bill}

        # 2. Thông tin Header
        header_info = self.model.get_invoice_general_info(id_hd)
        if not header_info: return False, "Lỗi lấy thông tin hóa đơn!"

        check_in = header_info['ngayTao'].strftime("%d/%m/%Y %H:%M")
        check_out = datetime.now().strftime("%d/%m/%Y %H:%M")
        staff_name = header_info['tenNhanVien']
        cust_name = header_info['tenKhachHang'] if header_info['tenKhachHang'] else "Khach le"

        # 3. Chuẩn bị dữ liệu DB
        id_ngan_hang = bank_info['idNganHang'] if (method == 'ChuyenKhoan' and bank_info) else None

        # Nếu CK: Dùng mã từ View truyền xuống. Nếu TM: Tạo mã mới
        if method == 'ChuyenKhoan' and noi_dung_ck:
            final_noi_dung = noi_dung_ck
            display_code = noi_dung_ck
        else:
            display_code = self.generate_invoice_code()
            final_noi_dung = f"{display_code} (TM)"

        # 4. GỌI MODEL
        if self.model.finalize_invoice(id_hd, 2, total_bill, id_ngan_hang, final_noi_dung):
            # Cộng điểm tích lũy
            if header_info['tenKhachHang']:
                current_cust = self.get_current_table_customer()
                if current_cust:
                    self.model.add_loyalty_points(current_cust['idKhachHang'], 10)

            # 5. XUẤT PDF
            invoice_info = {
                'code': display_code,
                'check_in': check_in,
                'check_out': check_out,
                'table': self.selected_table_id,
                'staff': staff_name,
                'customer': cust_name,
                'payment_method': "Chuyen Khoan" if method == 'ChuyenKhoan' else "Tien Mat"
            }

            # Chỉ in QR nếu là CK và có file ảnh
            final_qr_path = qr_path if method == 'ChuyenKhoan' else None

            pdf_path = os.path.join(self.invoice_dir, f"{display_code}.pdf")
            self.create_pdf(pdf_path, invoice_info, cart_items, totals, final_qr_path)

            return True, f"Thanh toán thành công!\nMã HĐ: {display_code}\nLưu tại: {pdf_path}"

        return False, "Lỗi cập nhật Database!"