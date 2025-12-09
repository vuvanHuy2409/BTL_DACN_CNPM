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
        self.VAT_RATE = 0.10
        self.invoice_dir = "src/hoadon"
        if not os.path.exists(self.invoice_dir):
            os.makedirs(self.invoice_dir)

    # ================= 1. UTILS =================
    def remove_accents(self, input_str):
        if not input_str: return ""
        nfkd = unicodedata.normalize('NFKD', str(input_str))
        return "".join([c for c in nfkd if not unicodedata.combining(c)])

    def format_money(self, value):
        return "{:,.0f}".format(value)

    def generate_invoice_code(self):
        date_str = datetime.now().strftime('%d%m%Y')
        random_digits = f"{random.randint(0, 999):03d}"
        random_chars = ''.join(random.choices(string.ascii_letters, k=2))
        return f"HD-{date_str}-{random_digits}{random_chars}"

    # ================= 2. MENU & TABLE =================
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

    # ================= 3. CART & CALCULATE =================
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

    def clear_current_cart(self):
        return self.model.cancel_invoice(self.get_current_invoice_id())

    def calculate_cart_totals(self):
        id_hd = self.get_current_invoice_id()
        if not id_hd: return [], 0, 0, 0, False

        details = self.model.get_invoice_details(id_hd)
        subtotal = sum(float(item['thanhTien']) for item in details)

        customer = self.get_current_table_customer()
        discount_amount = 0
        is_discount_applied = False

        if customer and customer['diemTichLuy'] >= 200:
            discount_amount = subtotal * 0.10
            is_discount_applied = True

        final_total = subtotal - discount_amount

        display_items = []
        for item in details:
            display_items.append((
                item['tenSanPham'],
                item['soLuong'],
                self.format_money(float(item['thanhTien']))
            ))

        return display_items, subtotal, discount_amount, final_total, is_discount_applied

    def get_cart_display(self):
        items, subtotal, discount, final_total, is_applied = self.calculate_cart_totals()
        return items, self.format_money(final_total), final_total

    # ================= 4. CUSTOMER =================
    def get_current_table_customer(self):
        id_hd = self.get_current_invoice_id()
        if id_hd: return self.model.get_invoice_customer(id_hd)
        return None

    def find_and_assign_customer(self, sdt, id_nv_login):
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

    # ================= 5. PAYMENT & PDF (ĐÃ SỬA LỖI LOGIC ĐIỂM) =================
    def get_bank_list(self):
        return self.model.get_active_banks()

    def get_qr_image_path(self, bank_info, amount, content):
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
        try:
            c = canvas.Canvas(filename, pagesize=A4)
            width, height = A4

            def txt(t):
                return self.remove_accents(str(t))

            y = 800
            c.setFont("Helvetica-Bold", 22)
            c.drawCentredString(width / 2, y, "COFFEE SHOP RECEIPT")
            y -= 40
            c.setFont("Helvetica", 10)
            c.drawCentredString(width / 2, y, "Dia chi: 123 Duong ABC, Quan 1, TP.HCM")
            y -= 40
            c.line(50, y, 545, y)

            y -= 25
            c.setFont("Helvetica", 11)
            c.drawString(50, y, txt(f"Ma HD: {invoice_info['code']}"))
            c.drawString(50, y - 15, txt(f"Ban: {invoice_info['table']}"))
            c.drawRightString(545, y, txt(f"Nhan vien: {invoice_info['staff']}"))
            c.drawRightString(545, y - 15, txt(f"Khach: {invoice_info['customer']}"))
            y -= 45
            c.line(50, y, 545, y)

            y -= 20
            c.setFont("Helvetica-Bold", 10)
            c.drawString(50, y, "TEN MON")
            c.drawCentredString(300, y, "SL")
            c.drawRightString(545, y, "THANH TIEN")
            y -= 10
            c.line(50, y, 545, y)
            y -= 20

            c.setFont("Helvetica", 10)
            for item in items:
                name = txt(item[0])
                if len(name) > 40: name = name[:37] + "..."
                c.drawString(50, y, name)
                c.drawCentredString(300, y, str(item[1]))
                c.drawRightString(545, y, str(item[2]))
                y -= 20
                if y < 150:
                    c.showPage()
                    y = 800
                    c.setFont("Helvetica", 10)

            c.line(50, y, 545, y)
            y -= 25
            c.drawRightString(450, y, "Tong tien hang:")
            c.drawRightString(545, y, self.format_money(totals['subtotal']))
            y -= 15

            if totals['discount'] > 0:
                c.drawRightString(450, y, "Giam gia (VIP):")
                c.drawRightString(545, y, f"-{self.format_money(totals['discount'])}")
                y -= 15

            c.drawRightString(450, y, "VAT (10%):")
            c.drawRightString(545, y, self.format_money(totals['vat']))
            y -= 25

            c.setFont("Helvetica-Bold", 14)
            c.drawRightString(450, y, "THANH TOAN:")
            c.drawRightString(545, y, f"{self.format_money(totals['total'])} VND")

            if qr_path and os.path.exists(qr_path):
                if y < 150:
                    c.showPage()
                    y = 750
                y -= 120
                c.drawImage(qr_path, (width - 100) / 2, y, width=100, height=100)

            c.save()
            return True
        except Exception as e:
            print(f"PDF Error: {e}")
            return False

    def process_payment(self, method="TienMat", id_nv=1, bank_info=None, noi_dung_ck=None, qr_path=None):
        id_hd = self.get_current_invoice_id()
        if not id_hd: return False, "Bàn trống!"

        # 1. Tính toán trước khi chốt
        items, subtotal, discount, final_total, is_discount_applied = self.calculate_cart_totals()

        # [QUAN TRỌNG] Lấy thông tin khách hàng TRƯỚC KHI chốt hóa đơn (vì sau khi chốt id_hd sẽ không còn active)
        current_cust = self.get_current_table_customer()

        vat_amount = final_total - (final_total / (1 + self.VAT_RATE))
        totals = {
            'subtotal': subtotal,
            'discount': discount,
            'vat': vat_amount,
            'total': final_total
        }

        # Lấy thông tin header
        header_info = self.model.get_invoice_general_info(id_hd)
        if not header_info: return False, "Lỗi thông tin hóa đơn!"

        staff_name = header_info['tenNhanVien']
        cust_name = header_info['tenKhachHang'] if header_info['tenKhachHang'] else "Khach le"

        if method == 'ChuyenKhoan' and noi_dung_ck:
            display_code = noi_dung_ck
            final_noi_dung = noi_dung_ck
        else:
            display_code = self.generate_invoice_code()
            final_noi_dung = f"{display_code} (TM)"

        id_ngan_hang = bank_info['idNganHang'] if (method == 'ChuyenKhoan' and bank_info) else None

        # 2. GỌI MODEL THANH TOÁN (Cập nhật DB thành trạng thái Đã Thanh Toán)
        if self.model.finalize_invoice(id_hd, 2, final_total, id_ngan_hang, final_noi_dung):

            # --- [LOGIC ĐIỂM TÍCH LŨY ĐÃ SỬA LẠI] ---
            loyalty_msg = ""

            # Chỉ cộng/trừ điểm nếu có khách hàng
            if current_cust:
                msg_list = []

                # A. Nếu dùng giảm giá -> TRỪ 1000 ĐIỂM
                if is_discount_applied:
                    # Truyền số âm để trừ
                    self.model.add_loyalty_points(current_cust['idKhachHang'], -200)
                    msg_list.append("-200 điểm (Đổi ưu đãi VIP)")

                # B. LUÔN LUÔN CỘNG 10 ĐIỂM cho hóa đơn hiện tại (Dù có giảm giá hay không)
                self.model.add_loyalty_points(current_cust['idKhachHang'], 10)
                msg_list.append("+10 điểm tích lũy mới")

                loyalty_msg = "\n" + "\n".join(msg_list)
            # ------------------------------------

            # 3. XUẤT PDF
            invoice_info = {
                'code': display_code,
                'table': self.selected_table_id,
                'staff': staff_name,
                'customer': cust_name
            }

            final_qr_path = qr_path if method == 'ChuyenKhoan' else None
            pdf_path = os.path.join(self.invoice_dir, f"{display_code}.pdf")

            self.create_pdf(pdf_path, invoice_info, items, totals, final_qr_path)

            return True, f"Thanh toán thành công!{loyalty_msg}\nFile: {pdf_path}"

        return False, "Lỗi cập nhật Database!"