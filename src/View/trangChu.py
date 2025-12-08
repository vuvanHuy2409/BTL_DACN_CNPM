import customtkinter as ctk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from src.Controller.TrangChuController import TrangChuController


class MenuPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#E0E0E0")

        self.controller = TrangChuController()
        self.current_user_id = 1  # Giả lập ID nhân viên đang đăng nhập (Thực tế sẽ lấy từ Login)

        # Cache hình ảnh để tránh load lại nhiều lần gây lag
        self.image_cache = {}

        # Danh sách bàn (Giả lập 16 bàn)
        self.table_ids = list(range(1, 17))
        self.suggestion_frame = None

        # Khởi tạo giao diện và dữ liệu
        self.tao_giao_dien()
        self.load_menu_grid()

        # Sự kiện click bất kỳ đâu để ẩn popup gợi ý khách hàng
        self.bind("<Button-1>", lambda e: self.hide_suggestions())

    def tao_giao_dien(self):
        # --- CẤU HÌNH LƯỚI TỔNG THỂ ---
        # Cột 0 (Trái): 60% diện tích
        # Cột 1 (Phải): 40% diện tích
        self.grid_columnconfigure(0, weight=6, uniform="group1")
        self.grid_columnconfigure(1, weight=4, uniform="group1")
        self.grid_rowconfigure(0, weight=1)

        # =================================================================
        # PANEL TRÁI: CHỨA SƠ ĐỒ BÀN VÀ HÓA ĐƠN
        # =================================================================
        left_panel = ctk.CTkFrame(self, fg_color="transparent")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        left_panel.grid_columnconfigure(0, weight=1)

        # [QUAN TRỌNG] Chia chiều cao 50% - 50% bằng nhau
        left_panel.grid_rowconfigure(0, weight=1, uniform="split_left")  # Row 0: Sơ đồ
        left_panel.grid_rowconfigure(1, weight=1, uniform="split_left")  # Row 1: Hóa đơn

        # -------------------------------------------------------------
        # 1. KHUNG SƠ ĐỒ BÀN (Nằm ở trên - Row 0)
        # -------------------------------------------------------------
        map_frame = ctk.CTkFrame(left_panel, fg_color="white", corner_radius=10)
        map_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        map_frame.grid_columnconfigure(0, weight=1)
        map_frame.grid_rowconfigure(1, weight=1)  # Phần scroll giãn hết cỡ

        # Header Sơ đồ
        h_map = ctk.CTkFrame(map_frame, fg_color="transparent")
        h_map.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(h_map, text="SƠ ĐỒ BÀN", font=("Arial", 14, "bold"), text_color="#1565C0").pack(side="left")

        # Chú thích trạng thái
        self.create_legend(h_map, "#E0E0E0", "Trống")
        self.create_legend(h_map, "#4CAF50", "Có khách")
        self.create_legend(h_map, "#FF9800", "Đang chọn")

        # Scrollbar chứa các nút bàn
        self.table_scroll = ctk.CTkScrollableFrame(map_frame, fg_color="transparent")
        self.table_scroll.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.render_tables()

        # -------------------------------------------------------------
        # 2. KHUNG HÓA ĐƠN & ORDER (Nằm ở dưới - Row 1)
        # -------------------------------------------------------------
        bill_frame = ctk.CTkFrame(left_panel, fg_color="white", corner_radius=10)
        bill_frame.grid(row=1, column=0, sticky="nsew", pady=(5, 0))
        bill_frame.grid_columnconfigure(0, weight=1)
        bill_frame.grid_rowconfigure(2, weight=1)  # Treeview giãn nở chính

        # Header Bill
        h_bill = ctk.CTkFrame(bill_frame, fg_color="#F5F5F5")
        h_bill.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        self.lbl_current_table = ctk.CTkLabel(h_bill, text="Chưa chọn bàn", font=("Arial", 16, "bold"),
                                              text_color="#FF9800")
        self.lbl_current_table.pack(pady=2)

        # Thanh tìm kiếm khách hàng
        self.row_cust = ctk.CTkFrame(h_bill, fg_color="transparent")
        self.row_cust.pack(fill="x")

        self.entry_sdt = ctk.CTkEntry(self.row_cust, placeholder_text="Nhập SĐT tìm khách...", width=150)
        self.entry_sdt.pack(side="left", padx=5)
        self.entry_sdt.bind("<KeyRelease>", self.on_sdt_type)
        # Delay ẩn gợi ý để kịp click chọn
        self.entry_sdt.bind("<FocusOut>", lambda e: self.after(200, self.hide_suggestions))

        ctk.CTkButton(self.row_cust, text="🔎", width=30, fg_color="#90A4AE", command=self.tim_khach).pack(side="left")

        self.lbl_khach = ctk.CTkLabel(self.row_cust, text="Khách vãng lai", font=("Arial", 12, "bold"))
        self.lbl_khach.pack(side="left", padx=10)

        ctk.CTkButton(self.row_cust, text="+ Khách Mới", width=80, fg_color="#607D8B", command=self.mo_form_khach).pack(
            side="right", padx=5)

        # Bảng danh sách món (Treeview)
        cols = ("mon", "sl", "tien")
        self.tree = ttk.Treeview(bill_frame, columns=cols, show="headings", height=8)
        self.tree.heading("mon", text="Món")
        self.tree.heading("sl", text="SL")
        self.tree.heading("tien", text="Thành Tiền")

        self.tree.column("mon", width=220)
        self.tree.column("sl", width=50, anchor="center")
        self.tree.column("tien", width=120, anchor="e")

        self.tree.grid(row=2, column=0, sticky="nsew", padx=5, pady=2)

        # Footer Bill: Tổng tiền & Các nút chức năng
        foot = ctk.CTkFrame(bill_frame, fg_color="transparent")
        foot.grid(row=3, column=0, sticky="ew", padx=5, pady=5)

        total_box = ctk.CTkFrame(foot, fg_color="#E0F2F1")
        total_box.pack(fill="x", pady=5)
        ctk.CTkLabel(total_box, text="TỔNG CỘNG:", font=("Arial", 14, "bold")).pack(side="left", padx=10)
        self.lbl_total = ctk.CTkLabel(total_box, text="0 VNĐ", font=("Arial", 20, "bold"), text_color="#E91E63")
        self.lbl_total.pack(side="right", padx=10)

        btn_r = ctk.CTkFrame(foot, fg_color="transparent")
        btn_r.pack(fill="x")

        ctk.CTkButton(btn_r, text="HỦY BÀN", fg_color="#F44336", width=80, height=40, command=self.huy_ban).pack(
            side="left")
        ctk.CTkButton(btn_r, text="XÓA MÓN", fg_color="#FF9800", width=80, height=40, command=self.xoa_mon).pack(
            side="left", padx=5)
        ctk.CTkButton(btn_r, text="THANH TOÁN", fg_color="#4CAF50", height=45, font=("Arial", 14, "bold"),
                      command=self.open_payment_options).pack(side="right", fill="x", expand=True, padx=(5, 0))

        # =================================================================
        # PANEL PHẢI: MENU THỰC ĐƠN
        # =================================================================
        right_panel = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(right_panel, text="THỰC ĐƠN", font=("Arial", 16, "bold"), text_color="#333").grid(row=0, column=0,
                                                                                                       pady=10)

        self.menu_scroll = ctk.CTkScrollableFrame(right_panel, fg_color="transparent")
        self.menu_scroll.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    # ================= LOGIC GỢI Ý KHÁCH HÀNG =================
    def on_sdt_type(self, event):
        text = self.entry_sdt.get().strip()
        if len(text) >= 3:
            try:
                suggestions = self.controller.get_customer_suggestions(text)
                if suggestions:
                    self.show_suggestions(suggestions)
                else:
                    self.hide_suggestions()
            except:
                self.hide_suggestions()
        else:
            self.hide_suggestions()

    def show_suggestions(self, customers):
        if self.suggestion_frame is None:
            self.suggestion_frame = ctk.CTkScrollableFrame(self.row_cust, width=250, height=150,
                                                           fg_color="white", border_width=1, border_color="gray")
            # Hiển thị popup ngay dưới ô nhập SĐT
            self.suggestion_frame.place(x=5, y=35)

        for widget in self.suggestion_frame.winfo_children(): widget.destroy()

        for cust in customers:
            txt = f"{cust['hoTen']} - {cust['soDienThoai']}"
            btn = ctk.CTkButton(self.suggestion_frame, text=txt, anchor="w", fg_color="transparent",
                                text_color="black", hover_color="#E3F2FD", height=30,
                                command=lambda c=cust: self.select_suggestion(c))
            btn.pack(fill="x", padx=2, pady=1)

        self.suggestion_frame.lift()

    def hide_suggestions(self):
        if self.suggestion_frame:
            self.suggestion_frame.place_forget()
            self.suggestion_frame = None

    def select_suggestion(self, cust_data):
        self.entry_sdt.delete(0, "end")
        self.entry_sdt.insert(0, cust_data['soDienThoai'])
        self.hide_suggestions()
        self.tim_khach()

    # ================= RENDER GIAO DIỆN =================
    def create_legend(self, parent, color, text):
        ctk.CTkLabel(parent, text=text, font=("Arial", 10)).pack(side="right", padx=2)
        ctk.CTkButton(parent, text="", width=12, height=12, fg_color=color, state="disabled", corner_radius=2).pack(
            side="right", padx=2)

    def render_tables(self):
        # Render lại danh sách bàn
        for w in self.table_scroll.winfo_children(): w.destroy()

        cols = 4  # Số cột bàn
        for i in range(cols): self.table_scroll.grid_columnconfigure(i, weight=1)

        for idx, t_id in enumerate(self.table_ids):
            r, c = idx // cols, idx % cols

            status = self.controller.get_table_status(t_id)
            money = self.controller.get_table_total_money(t_id)

            bg, fg, hover = "#E0E0E0", "#333", "#FFB74D"
            if status == "active":
                bg, fg = "#4CAF50", "white"
            elif status == "selected":
                bg, fg, hover = "#FF9800", "white", "#F57C00"

            # Hiển thị tên bàn và số tiền (nếu có)
            txt = f"BÀN {t_id}\n{money:,.0f}" if money > 0 else f"BÀN {t_id}"

            btn = ctk.CTkButton(self.table_scroll, text=txt, font=("Arial", 12, "bold"),
                                fg_color=bg, text_color=fg, hover_color=hover, height=70,
                                command=lambda i=t_id: self.chon_ban(i))
            btn.grid(row=r, column=c, padx=3, pady=3, sticky="ew")

    def create_product_card(self, parent, prod, r, c):
        card = ctk.CTkFrame(parent, fg_color="white", border_width=1, border_color="#ddd")
        card.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")

        # Load và cache ảnh
        img_path = prod.get('hinhAnhUrl', '')
        ctk_img = None
        if img_path and os.path.exists(img_path):
            if img_path not in self.image_cache:
                try:
                    pil_img = Image.open(img_path)
                    # Resize ảnh nhỏ lại cho menu
                    self.image_cache[img_path] = ctk.CTkImage(pil_img, size=(70, 60))
                except:
                    pass
            ctk_img = self.image_cache.get(img_path)

        btn = ctk.CTkButton(card, text=f"{prod['tenSanPham']}\n{int(prod['giaBan']):,} đ",
                            image=ctk_img, compound="top",
                            fg_color="white", hover_color="#E3F2FD", text_color="#333",
                            font=("Arial", 10, "bold"), height=90,
                            command=lambda p=prod: self.them_mon(p))
        btn.pack(fill="both", expand=True, padx=2, pady=2)

    def load_menu_grid(self):
        for w in self.menu_scroll.winfo_children(): w.destroy()

        for group in self.controller.get_menu_grouped_by_category():
            # Tên danh mục
            h = ctk.CTkFrame(self.menu_scroll, fg_color="transparent")
            h.pack(fill="x", pady=(10, 5), padx=5)
            ctk.CTkLabel(h, text=group['category_name'].upper(), font=("Arial", 13, "bold"), text_color="#1976D2").pack(
                anchor="w")
            ctk.CTkFrame(self.menu_scroll, height=2, fg_color="#E0E0E0").pack(fill="x", padx=5)

            # Lưới sản phẩm
            fr = ctk.CTkFrame(self.menu_scroll, fg_color="transparent")
            fr.pack(fill="x", padx=5)
            cols = 3
            for i in range(cols): fr.grid_columnconfigure(i, weight=1)

            for idx, prod in enumerate(group['products']):
                self.create_product_card(fr, prod, idx // cols, idx % cols)

    # ================= CHỨC NĂNG NGHIỆP VỤ =================
    def chon_ban(self, t_id):
        self.controller.select_table(t_id)
        self.lbl_current_table.configure(text=f"ĐƠN HÀNG BÀN {t_id}")

        cust = self.controller.get_current_table_customer()
        if cust:
            self.lbl_khach.configure(text=cust['hoTen'], text_color="green")
            self.entry_sdt.delete(0, "end")
            self.entry_sdt.insert(0, cust['soDienThoai'])
        else:
            self.lbl_khach.configure(text="Khách vãng lai", text_color="#333")
            self.entry_sdt.delete(0, "end")

        self.render_tables()
        self.update_cart_view()

    def them_mon(self, prod):
        if not self.controller.selected_table_id:
            messagebox.showwarning("Lỗi", "Vui lòng chọn bàn trước!")
            return
        ok, msg = self.controller.add_to_cart(prod, self.current_user_id)
        if ok:
            self.update_cart_view()
            self.render_tables()
        else:
            messagebox.showerror("Lỗi", msg)

    def update_cart_view(self):
        for i in self.tree.get_children(): self.tree.delete(i)

        items, total_str, _ = self.controller.get_cart_display()
        for item in items:
            self.tree.insert("", "end", values=item)
        self.lbl_total.configure(text=f"{total_str} VNĐ")

    def xoa_mon(self):
        sel = self.tree.selection()
        if not sel: return
        name = self.tree.item(sel[0])['values'][0]

        if messagebox.askyesno("Xác nhận", f"Bạn muốn xóa món '{name}'?"):
            if self.controller.remove_item_from_cart(name):
                self.update_cart_view()
                self.render_tables()

    def huy_ban(self):
        if not self.controller.selected_table_id: return
        if messagebox.askyesno("Cảnh báo", "Bạn có chắc muốn hủy đơn của bàn này?"):
            if self.controller.clear_current_cart():
                self.update_cart_view()
                self.render_tables()
                self.lbl_khach.configure(text="Khách vãng lai", text_color="#333")
                self.entry_sdt.delete(0, "end")

    def tim_khach(self):
        sdt = self.entry_sdt.get()
        found, cust = self.controller.find_and_assign_customer(sdt, self.current_user_id)
        if found:
            self.lbl_khach.configure(text=cust['hoTen'], text_color="green")
        else:
            self.lbl_khach.configure(text="Không tìm thấy", text_color="red")

    def mo_form_khach(self):
        w = ctk.CTkToplevel(self)
        w.title("Thêm Khách")
        w.geometry("350x300")
        w.attributes("-topmost", True)

        ctk.CTkLabel(w, text="THÊM KHÁCH MỚI", font=("Arial", 14, "bold")).pack(pady=10)

        e_ten = ctk.CTkEntry(w, placeholder_text="Tên khách hàng")
        e_ten.pack(pady=5, padx=20, fill="x")
        e_sdt = ctk.CTkEntry(w, placeholder_text="Số điện thoại")
        e_sdt.pack(pady=5, padx=20, fill="x")
        e_dob = ctk.CTkEntry(w, placeholder_text="Ngày sinh (dd/mm/yyyy)")
        e_dob.pack(pady=5, padx=20, fill="x")

        def save():
            ok, msg = self.controller.create_customer(e_ten.get(), e_sdt.get(), e_dob.get())
            if ok:
                messagebox.showinfo("Thành công", "Đã thêm khách hàng!")
                w.destroy()
            else:
                messagebox.showerror("Lỗi", msg)

        ctk.CTkButton(w, text="Lưu Thông Tin", fg_color="green", command=save).pack(pady=15)

    def open_payment_options(self):
        items, _, total = self.controller.get_cart_display()
        if total == 0:
            messagebox.showinfo("Thông báo", "Bàn trống, không thể thanh toán!")
            return

        w = ctk.CTkToplevel(self)
        w.title("Thanh Toán")
        w.geometry("400x250")
        w.attributes("-topmost", True)

        ctk.CTkLabel(w, text=f"TỔNG: {self.lbl_total.cget('text')}",
                     font=("Arial", 18, "bold"), text_color="#E91E63").pack(pady=20)

        ctk.CTkButton(w, text="💵 TIỀN MẶT", height=40, fg_color="#4CAF50",
                      command=lambda: self.pay(w, 'TienMat')).pack(fill="x", padx=30, pady=10)

        ctk.CTkButton(w, text="📱 CHUYỂN KHOẢN (QR)", height=40, fg_color="#2196F3",
                      command=lambda: self.open_qr(w)).pack(fill="x", padx=30, pady=5)

    def pay(self, w, method):
        w.destroy()
        ok, msg = self.controller.process_payment(method, self.current_user_id)
        if ok:
            messagebox.showinfo("Thành công", msg)
            self.reset_ui_after_payment()
        else:
            messagebox.showerror("Lỗi", msg)

    def reset_ui_after_payment(self):
        self.update_cart_view()
        self.render_tables()
        self.lbl_khach.configure(text="Khách vãng lai", text_color="#333")
        self.entry_sdt.delete(0, "end")

    # ================= THANH TOÁN QR (HOÀN THIỆN) =================
    def open_qr(self, parent_window):
        parent_window.destroy()
        banks = self.controller.get_bank_list()

        if not banks:
            messagebox.showerror("Lỗi", "Không có ngân hàng nào đang hoạt động!")
            return

        qr_win = ctk.CTkToplevel(self)
        qr_win.title("Thanh toán QR")
        qr_win.geometry("550x650")
        qr_win.attributes("-topmost", True)

        ctk.CTkLabel(qr_win, text="CHỌN NGÂN HÀNG", font=("Arial", 14, "bold")).pack(pady=10)

        # Map ngân hàng để lấy object khi chọn
        bank_map = {}
        for b in banks:
            display_text = f"{b['tenNganHang']} ({b['maNganHang']}) - {b['soTaiKhoan']}"
            bank_map[display_text] = b

        bank_labels = list(bank_map.keys())
        selected_bank = ctk.StringVar(value=bank_labels[0])

        cb_bank = ctk.CTkComboBox(qr_win, values=bank_labels, variable=selected_bank, width=450)
        cb_bank.pack(pady=5)

        # Khung chứa QR
        qr_frame = ctk.CTkFrame(qr_win, width=300, height=300, fg_color="white")
        qr_frame.pack(pady=15)
        qr_frame.pack_propagate(False)

        lbl_qr_img = ctk.CTkLabel(qr_frame, text="Đang tải QR...", text_color="gray")
        lbl_qr_img.place(relx=0.5, rely=0.5, anchor="center")

        # 1. TẠO MÃ HÓA ĐƠN HD-DDMMYYYY-XXXYY
        inv_code = self.controller.generate_invoice_code()

        ctk.CTkLabel(qr_win, text=f"Nội dung CK: {inv_code}", font=("Arial", 18, "bold"), text_color="blue").pack(
            pady=5)
        ctk.CTkLabel(qr_win, text="(Khách hàng vui lòng ghi đúng nội dung này)", font=("Arial", 10, "italic")).pack()

        def update_qr(*args):
            lbl_qr_img.configure(image=None, text="Đang tạo QR...")
            qr_win.update()
            try:
                b_info = bank_map[cb_bank.get()]
                _, _, total = self.controller.get_cart_display()

                # Gọi Controller lấy ảnh QR
                path = self.controller.get_qr_image_path(b_info, total, inv_code)

                if path and os.path.exists(path):
                    pil_img = Image.open(path)
                    ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(280, 280))
                    lbl_qr_img.configure(image=ctk_img, text="")
                    lbl_qr_img.image = ctk_img
                else:
                    lbl_qr_img.configure(text="Lỗi tải QR")
            except:
                lbl_qr_img.configure(text="Lỗi hiển thị")

        # Load QR lần đầu
        update_qr()
        cb_bank.configure(command=lambda x: update_qr())

        def confirm():
            try:
                b_info = bank_map[cb_bank.get()]
                # Đường dẫn file QR hiện tại để đưa vào PDF
                current_qr_path = "temp_qr.png"

                # 2. GỬI DỮ LIỆU XUỐNG CONTROLLER -> MODEL -> SQL
                ok, msg = self.controller.process_payment(
                    method='ChuyenKhoan',
                    id_nv=self.current_user_id,
                    bank_info=b_info,
                    noi_dung_ck=inv_code,  # Truyền mã hóa đơn vào
                    qr_path=current_qr_path  # Truyền ảnh QR vào để in PDF
                )

                if ok:
                    messagebox.showinfo("Hoàn tất", msg)
                    self.reset_ui_after_payment()
                    qr_win.destroy()
                else:
                    messagebox.showerror("Lỗi", msg)
            except Exception as e:
                messagebox.showerror("Lỗi hệ thống", str(e))

        ctk.CTkButton(qr_win, text="XÁC NHẬN ĐÃ NHẬN TIỀN", fg_color="#4CAF50", height=45, command=confirm).pack(
            fill="x", padx=40, pady=20)