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

        # Quản lý Giỏ hàng từng bàn: {table_id: {prod_id: info}}
        self.table_carts = {}

        # Quản lý Khách hàng từng bàn: {table_id: customer_dict}
        self.table_customers = {}

        self.selected_table_id = None

        # Cấu hình Thuế VAT
        self.VAT_RATE = 0.10  # 10%

        # Tạo thư mục lưu hóa đơn nếu chưa có
        self.invoice_dir = "src/hoadon"
        if not os.path.exists(self.invoice_dir):
            os.makedirs(self.invoice_dir)

    # ================= CÁC HÀM HỖ TRỢ =================
    def remove_accents(self, input_str):
        """Chuyển tiếng Việt có dấu thành không dấu"""
        if not input_str: return ""
        nfkd = unicodedata.normalize('NFKD', str(input_str))
        return "".join([c for c in nfkd if not unicodedata.combining(c)])

    # ================= QUẢN LÝ MENU & BÀN =================

    def get_menu_grouped_by_category(self):
        result = []
        categories = self.model.get_all_categories()
        for cat in categories:
            prods = self.model.get_products_by_category(cat['idDanhMuc'])
            if prods:
                result.append({'category_name': cat['tenDanhMuc'], 'products': prods})
        return result

    def select_table(self, table_id):
        """Chọn bàn để thao tác"""
        self.selected_table_id = table_id
        if table_id not in self.table_carts:
            self.table_carts[table_id] = {}

    def get_table_status(self, table_id):
        """Lấy trạng thái bàn để tô màu UI"""
        if table_id == self.selected_table_id: return "selected"
        if table_id in self.table_carts and self.table_carts[table_id]: return "active"
        return "empty"

    # [FIXED] Hàm này bị thiếu gây lỗi AttributeError
    def get_table_total_money(self, table_id):
        """Tính tổng tiền tạm tính (bao gồm thuế) cho bàn cụ thể"""
        if table_id not in self.table_carts:
            return 0

        cart = self.table_carts[table_id]
        if not cart: return 0

        # Tính tổng tiền gốc
        raw_total = sum(item['sl'] * item['gia'] for item in cart.values())

        # Cộng thêm thuế VAT
        total_with_tax = raw_total * (1 + self.VAT_RATE)
        return total_with_tax

    # ================= QUẢN LÝ GIỎ HÀNG =================

    def add_to_cart_by_id(self, product):
        if self.selected_table_id is None: return False, "Chưa chọn bàn!"

        cart = self.table_carts[self.selected_table_id]
        id_sp = product['idSanPham']

        if id_sp in cart:
            cart[id_sp]['sl'] += 1
        else:
            cart[id_sp] = {
                'name': product['tenSanPham'],
                'sl': 1,
                'gia': float(product['giaBan'])
            }
        return True, "Ok"

    def remove_item_from_cart(self, product_name):
        if self.selected_table_id is None: return False
        cart = self.table_carts.get(self.selected_table_id, {})

        target_id = None
        for pid, info in cart.items():
            if info['name'] == product_name:
                target_id = pid;
                break

        if target_id:
            del cart[target_id]
            return True
        return False

    def get_cart_display(self):
        """Lấy dữ liệu hiển thị cho View (Đã tính thuế)"""
        if self.selected_table_id is None or self.selected_table_id not in self.table_carts:
            return [], "0", 0

        cart = self.table_carts[self.selected_table_id]
        display_list = []
        total_bill = 0

        for p_id, info in cart.items():
            # Thành tiền = SL * Giá * (1 + VAT)
            thanh_tien = info['sl'] * info['gia'] * (1 + self.VAT_RATE)
            total_bill += thanh_tien

            display_list.append((info['name'], info['sl'], "{:,.0f}".format(thanh_tien)))

        return display_list, "{:,.0f}".format(total_bill), total_bill

    def clear_current_cart(self):
        if self.selected_table_id in self.table_carts:
            self.table_carts[self.selected_table_id] = {}
        self.remove_customer_from_table()

    # ================= QUẢN LÝ KHÁCH HÀNG =================

    def get_current_table_customer(self):
        if self.selected_table_id in self.table_customers:
            return self.table_customers[self.selected_table_id]
        return None

    def assign_customer_to_table(self, customer_data):
        if self.selected_table_id is not None:
            self.table_customers[self.selected_table_id] = customer_data
            return True
        return False

    def remove_customer_from_table(self):
        if self.selected_table_id in self.table_customers:
            del self.table_customers[self.selected_table_id]

    def find_customer(self, sdt):
        cust = self.model.search_customer(sdt)
        if cust:
            self.assign_customer_to_table(cust)
            return True, cust
        return False, None

    def create_customer(self, ten, sdt, dob_str):
        if not ten or not sdt: return False, "Thiếu tên hoặc SĐT!"
        try:
            dob_obj = datetime.strptime(dob_str, "%d/%m/%Y")
            dob_sql = dob_obj.strftime("%Y-%m-%d")
        except:
            return False, "Ngày sinh không hợp lệ (dd/mm/yyyy)!"

        id_new = self.model.add_customer(ten, sdt, dob_sql)
        if id_new:
            return True, "Thêm thành công!"
        return False, "Lỗi thêm khách hàng!"

    # ================= THANH TOÁN & PDF =================

    def generate_invoice_code(self):
        date_str = datetime.now().strftime("%d%m%Y")
        xxx = str(random.randint(100, 999))
        yy = ''.join(random.choices(string.ascii_lowercase, k=2))
        return f"HD-{date_str}-{xxx}{yy}"

    def create_pdf_invoice(self, invoice_code, total_money, cart, qr_path=None):
        filename = os.path.join(self.invoice_dir, f"{invoice_code}.pdf")
        try:
            c = canvas.Canvas(filename, pagesize=A4)
            c.setFont("Helvetica", 12)

            y = 800
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(300, y, "HOA DON THANH TOAN")
            y -= 30

            c.setFont("Helvetica", 12)
            c.drawString(50, y, f"Ma HD: {invoice_code}")
            y -= 20
            c.drawString(50, y, f"Ngay: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            y -= 40

            # Header
            c.line(50, y, 550, y);
            y -= 20
            c.drawString(50, y, "Mon");
            c.drawString(350, y, "SL");
            c.drawString(450, y, "Thanh Tien")
            y -= 10;
            c.line(50, y, 550, y);
            y -= 20

            # Nội dung
            for info in cart.values():
                name = self.remove_accents(info['name'])  # Xử lý tiếng Việt cho PDF
                # Tính tiền từng dòng (có thuế)
                subtotal = info['sl'] * info['gia'] * (1 + self.VAT_RATE)

                c.drawString(50, y, name)
                c.drawString(350, y, str(info['sl']))
                c.drawString(450, y, "{:,.0f}".format(subtotal))
                y -= 20

            c.line(50, y, 550, y);
            y -= 30
            c.setFont("Helvetica-Bold", 14)
            c.drawString(300, y, f"TONG CONG: {total_money:,.0f} VND")

            if qr_path:
                y -= 220
                c.drawImage(qr_path, 200, y, width=200, height=200)
                c.drawString(230, y - 20, "Quet ma de thanh toan")

            c.save()
            return filename
        except Exception as e:
            print(f"Lỗi PDF: {e}")
            return None

    def get_bank_list(self):
        return self.model.get_active_banks()

    def get_qr_image_path(self, bank_data, amount, content):
        try:
            bank_id = bank_data['maNganHang']
            acc_no = bank_data['soTaiKhoan']
            safe_content = content.replace(" ", "")
            api_url = f"https://img.vietqr.io/image/{bank_id}-{acc_no}-compact.png?amount={int(amount)}&addInfo={safe_content}"

            response = requests.get(api_url)
            if response.status_code == 200:
                qr_path = "temp_qr.png"
                with open(qr_path, 'wb') as f:
                    f.write(response.content)
                return qr_path
        except:
            pass
        return None

    def process_payment(self, method, id_nv, bank_info=None):
        if self.selected_table_id is None: return False, "Chưa chọn bàn!"

        cart = self.table_carts.get(self.selected_table_id, {})
        if not cart: return False, "Bàn trống!"

        # Tính tổng tiền (Có thuế)
        total_money = sum((item['sl'] * item['gia']) * (1 + self.VAT_RATE) for item in cart.values())

        invoice_code = self.generate_invoice_code()

        current_cust = self.get_current_table_customer()
        id_kh = current_cust['idKhachHang'] if current_cust else None

        db_items = [{'id_sp': k, 'sl': v['sl'], 'gia': v['gia']} for k, v in cart.items()]

        # Lưu DB
        ok, msg = self.model.create_invoice(id_nv, id_kh, total_money, db_items, method)

        if ok:
            if id_kh: self.model.add_loyalty_points(id_kh, 10)

            # Xử lý QR và PDF
            qr_path = None
            if method == 'ChuyenKhoan' and bank_info:
                qr_path = self.get_qr_image_path(bank_info, total_money, invoice_code)

            pdf_file = self.create_pdf_invoice(invoice_code, total_money, cart, qr_path)

            # Dọn dẹp
            if qr_path and os.path.exists(qr_path): os.remove(qr_path)
            self.clear_current_cart()

            return True, f"Thanh toán thành công!\nHĐ: {invoice_code}\nPDF: {pdf_file}"

        return False, msg