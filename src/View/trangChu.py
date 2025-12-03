import customtkinter as ctk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from src.Controller.TrangChuController import TrangChuController


class MenuPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#E0E0E0")

        self.controller = TrangChuController()
        self.current_user_id = 1
        self.image_cache = {}

        # Dữ liệu bàn giả lập (16 bàn)
        self.table_ids = list(range(1, 17))

        self.tao_giao_dien()
        self.load_menu_grid()

    def tao_giao_dien(self):
        # Cấu hình lưới toàn trang: Trái 60%, Phải 40%
        self.grid_columnconfigure(0, weight=6, uniform="group1")
        self.grid_columnconfigure(1, weight=4, uniform="group1")
        self.grid_rowconfigure(0, weight=1)

        # =========================================================
        # KHUNG TRÁI: BÀN & HÓA ĐƠN (60% màn hình)
        # =========================================================
        left_panel = ctk.CTkFrame(self, fg_color="transparent")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # [QUAN TRỌNG] Giãn nội dung con ra hết chiều ngang
        left_panel.grid_columnconfigure(0, weight=1)

        # Chia tỉ lệ dọc: Bàn 45%, Hóa đơn 55%
        left_panel.grid_rowconfigure(0, weight=45)
        left_panel.grid_rowconfigure(1, weight=55)

        # --- 1. SƠ ĐỒ BÀN (TOP LEFT) ---
        map_frame = ctk.CTkFrame(left_panel, fg_color="white", corner_radius=10)
        map_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        map_frame.grid_columnconfigure(0, weight=1)
        map_frame.grid_rowconfigure(1, weight=1)  # Scroll frame giãn hết

        # Header Sơ đồ
        map_header = ctk.CTkFrame(map_frame, fg_color="transparent")
        map_header.grid(row=0, column=0, sticky="ew", pady=5, padx=10)
        ctk.CTkLabel(map_header, text="SƠ ĐỒ BÀN", font=("Arial", 14, "bold"), text_color="#1a237e").pack(side="left")

        # Chú thích
        self.create_legend(map_header, "#E0E0E0", "Trống")
        self.create_legend(map_header, "#4CAF50", "Có khách")
        self.create_legend(map_header, "#FF9800", "Đang chọn")

        self.table_scroll = ctk.CTkScrollableFrame(map_frame, fg_color="transparent")
        self.table_scroll.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self.render_tables()

        # --- 2. CHI TIẾT HÓA ĐƠN (BOTTOM LEFT) ---
        bill_frame = ctk.CTkFrame(left_panel, fg_color="white", corner_radius=10)
        bill_frame.grid(row=1, column=0, sticky="nsew", pady=(5, 0))
        bill_frame.grid_columnconfigure(0, weight=1)
        bill_frame.grid_rowconfigure(2, weight=1)  # Treeview giãn hết

        # Header Hóa đơn
        bill_header = ctk.CTkFrame(bill_frame, fg_color="#F5F5F5", corner_radius=5)
        bill_header.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        self.lbl_current_table = ctk.CTkLabel(bill_header, text="Chưa chọn bàn", font=("Arial", 16, "bold"),
                                              text_color="#FF9800")
        self.lbl_current_table.pack(side="top", pady=2)

        # Row Khách hàng
        cust_row = ctk.CTkFrame(bill_header, fg_color="transparent")
        cust_row.pack(fill="x", pady=2)

        self.entry_sdt = ctk.CTkEntry(cust_row, placeholder_text="SĐT khách...", width=120, height=28)
        self.entry_sdt.pack(side="left", padx=5)
        ctk.CTkButton(cust_row, text="🔎", width=30, height=28, fg_color="#2196F3", command=self.tim_khach).pack(
            side="left")

        self.lbl_khach = ctk.CTkLabel(cust_row, text="Khách vãng lai", font=("Arial", 12, "bold"))
        self.lbl_khach.pack(side="left", padx=10)

        ctk.CTkButton(cust_row, text="+ Mới", width=60, height=28, fg_color="#4CAF50", command=self.mo_form_khach).pack(
            side="right", padx=5)

        # Bảng danh sách món
        cols = ("mon", "sl", "tien")
        self.tree = ttk.Treeview(bill_frame, columns=cols, show="headings", height=8)
        self.tree.heading("mon", text="Tên Món");
        self.tree.heading("sl", text="SL");
        self.tree.heading("tien", text="Thành Tiền")

        # Tăng độ rộng cột Tên Món để lấp đầy
        self.tree.column("mon", width=300)
        self.tree.column("sl", width=50, anchor="center")
        self.tree.column("tien", width=120, anchor="e")

        self.tree.grid(row=2, column=0, sticky="nsew", padx=5, pady=2)

        # Footer
        footer = ctk.CTkFrame(bill_frame, fg_color="transparent")
        footer.grid(row=3, column=0, sticky="ew", padx=5, pady=5)

        total_box = ctk.CTkFrame(footer, fg_color="#E0F2F1")
        total_box.pack(fill="x", pady=5)
        ctk.CTkLabel(total_box, text="TỔNG CỘNG (VAT 10%):", font=("Arial", 14, "bold")).pack(side="left", padx=10)
        self.lbl_total = ctk.CTkLabel(total_box, text="0 VNĐ", font=("Arial", 22, "bold"), text_color="#E91E63")
        self.lbl_total.pack(side="right", padx=10)

        btn_row = ctk.CTkFrame(footer, fg_color="transparent")
        btn_row.pack(fill="x")
        ctk.CTkButton(btn_row, text="HỦY BÀN", fg_color="#F44336", hover_color="#D32F2F", width=100, height=45,
                      font=("Arial", 12, "bold"), command=self.huy_ban).pack(side="left")
        ctk.CTkButton(btn_row, text="XÓA MÓN", fg_color="#FF9800", hover_color="#F57C00", width=100, height=45,
                      font=("Arial", 12, "bold"), command=self.xoa_mon).pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="THANH TOÁN", fg_color="#4CAF50", hover_color="#388E3C", height=45,
                      font=("Arial", 14, "bold"), command=self.open_payment_options).pack(side="right", fill="x",
                                                                                          expand=True, padx=(5, 0))

        # =========================================================
        # KHU VỰC PHẢI: MENU HÌNH ẢNH (40% màn hình)
        # =========================================================
        right_panel = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(right_panel, text="THỰC ĐƠN", font=("Arial", 16, "bold"), text_color="#333").grid(row=0, column=0,
                                                                                                       pady=10)

        self.menu_scroll = ctk.CTkScrollableFrame(right_panel, fg_color="transparent")
        self.menu_scroll.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    # ================= LOGIC HIỂN THỊ =================

    def create_legend(self, parent, color, text):
        ctk.CTkLabel(parent, text=text, font=("Arial", 10)).pack(side="right", padx=2)
        ctk.CTkButton(parent, text="", width=12, height=12, fg_color=color, state="disabled", corner_radius=2).pack(
            side="right", padx=2)

    def render_tables(self):
        """Vẽ lại lưới bàn kèm SỐ TIỀN"""
        for w in self.table_scroll.winfo_children(): w.destroy()

        columns = 4
        for i in range(columns): self.table_scroll.grid_columnconfigure(i, weight=1)

        for idx, t_id in enumerate(self.table_ids):
            row, col = idx // columns, idx % columns

            status = self.controller.get_table_status(t_id)
            money = self.controller.get_table_total_money(t_id)

            bg_color = "#E0E0E0";
            fg_color = "#333";
            hover_color = "#FFB74D"

            if status == "active":
                bg_color = "#4CAF50";
                fg_color = "white"
            elif status == "selected":
                bg_color = "#FF9800";
                fg_color = "white";
                hover_color = "#F57C00"

            btn_text = f"BÀN {t_id}"
            if money > 0:
                btn_text += f"\n{money:,.0f} đ"

            btn = ctk.CTkButton(
                self.table_scroll, text=btn_text, font=("Arial", 12, "bold"),
                fg_color=bg_color, text_color=fg_color, hover_color=hover_color,
                height=70, corner_radius=8,
                command=lambda i=t_id: self.chon_ban(i)
            )
            btn.grid(row=row, column=col, padx=3, pady=3, sticky="ew")

    def create_product_card(self, parent, prod, row, col):
        """Tạo ô vuông món ăn"""
        card = ctk.CTkFrame(parent, fg_color="white", border_width=1, border_color="#ddd", corner_radius=8)
        card.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")

        img_path = prod['hinhAnhUrl']
        ctk_image = None

        if img_path and os.path.exists(img_path):
            if img_path not in self.image_cache:
                try:
                    pil_img = Image.open(img_path)
                    ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(70, 60))
                    self.image_cache[img_path] = ctk_img
                except:
                    pass
            ctk_image = self.image_cache.get(img_path)

        text_info = f"{prod['tenSanPham']}\n{int(prod['giaBan']):,} đ"

        btn = ctk.CTkButton(
            card, text=text_info, image=ctk_image, compound="top",
            fg_color="white", hover_color="#E3F2FD", text_color="#333",
            font=("Arial", 10, "bold"), anchor="center", height=90, corner_radius=8,
            command=lambda p=prod: self.them_mon(p)
        )
        btn.pack(fill="both", expand=True, padx=2, pady=2)

    def load_menu_grid(self):
        """Vẽ menu theo danh mục"""
        for w in self.menu_scroll.winfo_children(): w.destroy()
        grouped_menu = self.controller.get_menu_grouped_by_category()

        if not grouped_menu:
            ctk.CTkLabel(self.menu_scroll, text="Chưa có món ăn!", text_color="gray").pack(pady=20)
            return

        for group in grouped_menu:
            # Header
            header_frame = ctk.CTkFrame(self.menu_scroll, fg_color="transparent")
            header_frame.pack(fill="x", pady=(10, 5), padx=5)
            ctk.CTkLabel(header_frame, text=group['category_name'].upper(), font=("Arial", 13, "bold"),
                         text_color="#1976D2").pack(anchor="w")
            ctk.CTkFrame(self.menu_scroll, height=2, fg_color="#E0E0E0").pack(fill="x", padx=5, pady=(0, 5))

            # Grid
            products_frame = ctk.CTkFrame(self.menu_scroll, fg_color="transparent")
            products_frame.pack(fill="x", padx=5)

            columns = 3
            for i in range(columns): products_frame.grid_columnconfigure(i, weight=1)

            for idx, prod in enumerate(group['products']):
                r, c = idx // columns, idx % columns
                self.create_product_card(products_frame, prod, r, c)

    # ================= LOGIC TƯƠNG TÁC =================
    def chon_ban(self, t_id):
        self.controller.select_table(t_id)
        self.lbl_current_table.configure(text=f"ĐƠN HÀNG BÀN {t_id}")

        cust = self.controller.get_current_table_customer()
        if cust:
            self.lbl_khach.configure(text=cust['hoTen'], text_color="green")
            self.entry_sdt.delete(0, "end");
            self.entry_sdt.insert(0, cust['soDienThoai'])
        else:
            self.lbl_khach.configure(text="Khách vãng lai", text_color="#333")
            self.entry_sdt.delete(0, "end")

        self.render_tables()
        self.update_cart_view()

    def them_mon(self, product):
        if not self.controller.selected_table_id:
            messagebox.showwarning("Chú ý", "Vui lòng chọn bàn trước!")
            return
        ok, msg = self.controller.add_to_cart_by_id(product)
        self.update_cart_view()
        self.render_tables()

    def update_cart_view(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        items, total_str, _ = self.controller.get_cart_display()
        for item in items:
            self.tree.insert("", "end", values=item)
        self.lbl_total.configure(text=f"{total_str} VNĐ")

    def xoa_mon(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Chú ý", "Chọn món cần xóa!")
            return
        item = self.tree.item(selected[0])
        prod_name = item['values'][0]

        if messagebox.askyesno("Xác nhận", f"Xóa món '{prod_name}' khỏi bàn?"):
            if self.controller.remove_item_from_cart(prod_name):
                self.update_cart_view()
                self.render_tables()

    def huy_ban(self):
        if not self.controller.selected_table_id: return
        if messagebox.askyesno("Xác nhận", f"Hủy đơn bàn {self.controller.selected_table_id}?"):
            self.controller.clear_current_cart()
            self.update_cart_view()
            self.render_tables()
            self.lbl_khach.configure(text="Khách vãng lai", text_color="#333")
            self.entry_sdt.delete(0, "end")

    def tim_khach(self):
        sdt = self.entry_sdt.get()
        found, cust = self.controller.find_customer(sdt)
        if found:
            self.lbl_khach.configure(text=cust['hoTen'], text_color="green")
            messagebox.showinfo("OK", f"Khách: {cust['hoTen']}")
        else:
            self.lbl_khach.configure(text="Không tìm thấy", text_color="red")

    def mo_form_khach(self):
        w = ctk.CTkToplevel(self);
        w.title("Thêm Khách");
        w.geometry("350x300");
        w.attributes("-topmost", True)
        ctk.CTkLabel(w, text="THÊM KHÁCH MỚI", font=("Arial", 14, "bold")).pack(pady=10)
        e_ten = ctk.CTkEntry(w, placeholder_text="Tên khách hàng");
        e_ten.pack(pady=5, padx=20, fill="x")
        e_sdt = ctk.CTkEntry(w, placeholder_text="Số điện thoại");
        e_sdt.pack(pady=5, padx=20, fill="x")
        e_dob = ctk.CTkEntry(w, placeholder_text="Ngày sinh (dd/mm/yyyy)");
        e_dob.pack(pady=5, padx=20, fill="x")

        def save():
            ok, msg = self.controller.create_customer(e_ten.get(), e_sdt.get(), e_dob.get())
            if ok:
                messagebox.showinfo("Thành công", "Đã thêm khách hàng!")
                self.entry_sdt.delete(0, "end");
                self.entry_sdt.insert(0, e_sdt.get())
                self.tim_khach()
                w.destroy()
            else:
                messagebox.showerror("Lỗi", msg)

        ctk.CTkButton(w, text="Lưu", fg_color="green", command=save).pack(pady=15)

    def open_payment_options(self):
        items, _, total = self.controller.get_cart_display()
        if total == 0: return

        w = ctk.CTkToplevel(self);
        w.title("Thanh Toán");
        w.geometry("400x250");
        w.attributes("-topmost", True)
        ctk.CTkLabel(w, text=f"TỔNG TIỀN: {self.lbl_total.cget('text')}", font=("Arial", 18, "bold"),
                     text_color="#E91E63").pack(pady=20)

        ctk.CTkButton(w, text="💵 TIỀN MẶT", height=40, fg_color="#4CAF50", command=lambda: self.pay_cash(w)).pack(
            fill="x", padx=30, pady=10)
        ctk.CTkButton(w, text="📱 CHUYỂN KHOẢN (QR)", height=40, fg_color="#2196F3",
                      command=lambda: self.open_qr_payment(w)).pack(fill="x", padx=30, pady=5)

    def pay_cash(self, window):
        window.destroy()
        ok, msg = self.controller.process_payment('TienMat', self.current_user_id)
        if ok:
            messagebox.showinfo("Thành công", msg)
            self.update_cart_view();
            self.render_tables()
            self.lbl_khach.configure(text="Khách vãng lai", text_color="#333");
            self.entry_sdt.delete(0, "end")
        else:
            messagebox.showerror("Lỗi", msg)

    def open_qr_payment(self, parent_window):
        parent_window.destroy()
        banks = self.controller.get_bank_list()
        if not banks: messagebox.showerror("Lỗi", "Không có ngân hàng hoạt động!"); return

        qr_win = ctk.CTkToplevel(self);
        qr_win.title("Thanh toán QR");
        qr_win.geometry("450x600");
        qr_win.attributes("-topmost", True)
        ctk.CTkLabel(qr_win, text="CHỌN NGÂN HÀNG", font=("Arial", 14, "bold")).pack(pady=10)

        bank_map = {b['tenNganHang']: b for b in banks}
        selected_bank = ctk.StringVar(value=list(bank_map.keys())[0])
        cb_bank = ctk.CTkComboBox(qr_win, values=list(bank_map.keys()), variable=selected_bank, width=250)
        cb_bank.pack(pady=5)

        qr_frame = ctk.CTkFrame(qr_win, width=300, height=300, fg_color="white");
        qr_frame.pack(pady=15);
        qr_frame.pack_propagate(False)
        lbl_qr_img = ctk.CTkLabel(qr_frame, text="Đang tải...", text_color="gray");
        lbl_qr_img.place(relx=0.5, rely=0.5, anchor="center")

        invoice_code = self.controller.generate_invoice_code()
        ctk.CTkLabel(qr_win, text=f"Nội dung: {invoice_code}", font=("Arial", 16, "bold"), text_color="blue").pack()

        def update_qr(*args):
            lbl_qr_img.configure(image=None, text="Đang tải...")
            qr_win.update()
            bank_info = bank_map[cb_bank.get()]
            _, _, total_val = self.controller.get_cart_display()
            qr_path = self.controller.get_qr_image_path(bank_info, total_val, invoice_code)
            if qr_path and os.path.exists(qr_path):
                img = Image.open(qr_path)
                self.qr_photo = ctk.CTkImage(img, size=(280, 280))  # Lưu vào self để không mất ảnh
                lbl_qr_img.configure(image=self.qr_photo, text="")
            else:
                lbl_qr_img.configure(text="Lỗi tải QR")

        update_qr()
        cb_bank.configure(command=lambda x: update_qr())

        def confirm_transfer():
            bank_info = bank_map[cb_bank.get()]
            ok, msg = self.controller.process_payment('ChuyenKhoan', self.current_user_id, bank_info)
            if ok:
                messagebox.showinfo("Hoàn tất", msg)
                self.update_cart_view();
                self.render_tables()
                self.lbl_khach.configure(text="Khách vãng lai", text_color="#333");
                self.entry_sdt.delete(0, "end")
                qr_win.destroy()
            else:
                messagebox.showerror("Lỗi", msg)

        ctk.CTkButton(qr_win, text="XÁC NHẬN ĐÃ CK", fg_color="#4CAF50", height=45, command=confirm_transfer).pack(
            fill="x", padx=40, pady=20)