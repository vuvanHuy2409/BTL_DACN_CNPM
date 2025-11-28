import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from PIL import Image, ImageTk
import os

class MenuPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#F2F4F7") # Nền tổng thể xám rất nhạt cho dịu mắt
        
        # Dữ liệu giả lập bàn
        self.tables = [
            {"id": 1, "status": "active"}, {"id": 2, "status": "empty"}, {"id": 3, "status": "empty"},
            {"id": 4, "status": "reserved"}, {"id": 5, "status": "empty"}, {"id": 6, "status": "active"},
            {"id": 7, "status": "empty"}, {"id": 8, "status": "empty"}, {"id": 9, "status": "empty"},
            {"id": 10, "status": "empty"}, {"id": 11, "status": "active"}, {"id": 12, "status": "empty"},
            {"id": 13, "status": "empty"}, {"id": 14, "status": "empty"}, {"id": 15, "status": "empty"}
        ]
        
        # Dữ liệu giỏ hàng giả lập
        self.cart_data = [
            ("Cà phê sữa đá", 2, "25,000", "50,000", "Ít ngọt"),
            ("Bạc xỉu", 1, "29,000", "29,000", ""),
            ("Sinh tố bơ", 1, "45,000", "45,000", "Không đá"),
        ]

        self.tao_giao_dien_chinh()

    def tao_giao_dien_chinh(self):
        # Container chính
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=15, pady=15)

        # =========================================================
        # KHU VỰC TRÁI: SƠ ĐỒ BÀN (Chiếm 40%)
        # =========================================================
        left_frame = ctk.CTkFrame(container, fg_color="white", corner_radius=10, border_width=1, border_color="#ccc")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Header Bàn
        ctk.CTkLabel(left_frame, text="SƠ ĐỒ BÀN", font=("Arial", 16, "bold"), text_color="#1a237e").pack(pady=(15, 10))

        # Chú thích
        legend_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        legend_frame.pack(pady=(0, 15))
        
        def create_legend(parent, color, text):
            f = ctk.CTkFrame(parent, fg_color="transparent")
            f.pack(side="left", padx=10)
            ctk.CTkButton(f, text="", width=20, height=20, fg_color=color, hover_color=color, corner_radius=5, state="disabled").pack(side="left", padx=5)
            ctk.CTkLabel(f, text=text, font=("Arial", 11), text_color="#555").pack(side="left")

        create_legend(legend_frame, "#E0E0E0", "Trống")      # Xám
        create_legend(legend_frame, "#4CAF50", "Đang phục vụ") # Xanh lá
        create_legend(legend_frame, "#FF9800", "Đặt trước")   # Cam

        # Lưới bàn
        tables_scroll = ctk.CTkScrollableFrame(left_frame, fg_color="transparent")
        tables_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Tạo Grid 3 cột
        for i in range(3): tables_scroll.grid_columnconfigure(i, weight=1)

        for idx, table in enumerate(self.tables):
            row = idx // 3
            col = idx % 3
            
            # Màu sắc dựa theo trạng thái
            bg_color = "#E0E0E0"
            fg_color = "#333"
            hover_color = "#D6D6D6"
            
            if table["status"] == "active":
                bg_color = "#4CAF50"
                fg_color = "white"
                hover_color = "#45a049"
            elif table["status"] == "reserved":
                bg_color = "#FF9800"
                fg_color = "white"
                hover_color = "#F57C00"

            btn = ctk.CTkButton(
                tables_scroll, 
                text=f"Bàn {table['id']}\n({table['status']})", 
                font=("Arial", 12, "bold"),
                fg_color=bg_color, 
                text_color=fg_color,
                hover_color=hover_color,
                height=80,
                corner_radius=8,
                command=lambda id=table['id']: self.chon_ban(id)
            )
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")

        # =========================================================
        # KHU VỰC PHẢI: ORDER & THANH TOÁN (Chiếm 60%)
        # =========================================================
        right_frame = ctk.CTkFrame(container, fg_color="white", corner_radius=10, border_width=1, border_color="#ccc")
        right_frame.pack(side="right", fill="both", expand=True, ipadx=10)

        # --- 1. Thông tin khách hàng & Tìm kiếm ---
        info_frame = ctk.CTkFrame(right_frame, fg_color="#F5F5F5", corner_radius=10)
        info_frame.pack(fill="x", padx=15, pady=15)

        # Hàng 1: Tìm SDT + Tên Khách
        row1 = ctk.CTkFrame(info_frame, fg_color="transparent")
        row1.pack(fill="x", pady=10, padx=10)
        
        self.entry_sdt = ctk.CTkEntry(row1, placeholder_text="Nhập SĐT khách...", width=180, height=32)
        self.entry_sdt.pack(side="left", padx=(0, 5))
        ctk.CTkButton(row1, text="🔍", width=40, height=32, fg_color="#2196F3", command=self.tim_khach).pack(side="left", padx=(0, 15))
        
        ctk.CTkLabel(row1, text="Khách hàng:", font=("Arial", 11), text_color="#555").pack(side="left")
        ctk.CTkLabel(row1, text="Khách lẻ", font=("Arial", 12, "bold"), text_color="#333").pack(side="left", padx=5)
        
        ctk.CTkButton(row1, text="+ Khách mới", fg_color="#4CAF50", width=90, height=28, font=("Arial", 11, "bold"), command=self.mo_form_them_khach_hang).pack(side="right")

        # --- 2. Chọn món ---
        menu_frame = ctk.CTkFrame(right_frame, fg_color="white")
        menu_frame.pack(fill="x", padx=15)

        # Cột trái: Input chọn món
        menu_input = ctk.CTkFrame(menu_frame, fg_color="transparent")
        menu_input.pack(side="left", fill="x", expand=True)

        # Loại & Món
        r1 = ctk.CTkFrame(menu_input, fg_color="transparent")
        r1.pack(fill="x", pady=5)
        self.cb_loai = ctk.CTkComboBox(r1, values=["Cà phê", "Trà sữa", "Sinh tố", "Ăn vặt"], width=120)
        self.cb_loai.pack(side="left", padx=(0, 10))
        self.cb_mon = ctk.CTkComboBox(r1, values=["Cà phê đen", "Cà phê sữa", "Bạc xỉu"], width=200)
        self.cb_mon.pack(side="left", fill="x", expand=True)

        # Số lượng & Ghi chú & Nút Thêm
        r2 = ctk.CTkFrame(menu_input, fg_color="transparent")
        r2.pack(fill="x", pady=5)
        
        ctk.CTkButton(r2, text="-", width=30, fg_color="#ddd", text_color="black", hover_color="#ccc", command=lambda: self.doi_so_luong(-1)).pack(side="left")
        self.entry_sl = ctk.CTkEntry(r2, width=50, justify="center")
        self.entry_sl.insert(0, "1")
        self.entry_sl.pack(side="left", padx=5)
        ctk.CTkButton(r2, text="+", width=30, fg_color="#ddd", text_color="black", hover_color="#ccc", command=lambda: self.doi_so_luong(1)).pack(side="left", padx=(0, 15))
        
        self.entry_note = ctk.CTkEntry(r2, placeholder_text="Ghi chú (ít đường...)", width=200)
        self.entry_note.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(r2, text="Thêm Món", fg_color="#2196F3", width=100, font=("Arial", 11, "bold")).pack(side="right")

        # --- 3. Danh sách món (Treeview) ---
        table_container = ctk.CTkFrame(right_frame, fg_color="white", border_width=1, border_color="#ccc")
        table_container.pack(fill="both", expand=True, padx=15, pady=10)

        # Style Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground="black", rowheight=30, fieldbackground="white", font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#f0f0f0", foreground="#333")
        style.map("Treeview", background=[("selected", "#2196F3")])

        cols = ("mon", "sl", "gia", "tong", "note")
        self.tree = ttk.Treeview(table_container, columns=cols, show="headings", height=8)
        
        self.tree.heading("mon", text="Tên món")
        self.tree.heading("sl", text="SL")
        self.tree.heading("gia", text="Đơn giá")
        self.tree.heading("tong", text="Thành tiền")
        self.tree.heading("note", text="Ghi chú")

        self.tree.column("mon", width=150, anchor="w")
        self.tree.column("sl", width=50, anchor="center")
        self.tree.column("gia", width=80, anchor="e")
        self.tree.column("tong", width=90, anchor="e")
        self.tree.column("note", width=100, anchor="w")

        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=1, pady=1)

        # Load dummy data
        for item in self.cart_data:
            self.tree.insert("", "end", values=item)

        # --- 4. Footer & Thanh toán ---
        footer_frame = ctk.CTkFrame(right_frame, fg_color="#F9F9F9", corner_radius=0)
        footer_frame.pack(fill="x", padx=1, pady=1, side="bottom")

        # Tổng tiền
        total_row = ctk.CTkFrame(footer_frame, fg_color="transparent")
        total_row.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(total_row, text="Tổng cộng:", font=("Arial", 14), text_color="#555").pack(side="left")
        ctk.CTkLabel(total_row, text="124,000 đ", font=("Arial", 22, "bold"), text_color="#E91E63").pack(side="right")

        # Nút thanh toán to
        btn_row = ctk.CTkFrame(footer_frame, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkButton(btn_row, text="HỦY ĐƠN", fg_color="#F44336", hover_color="#D32F2F", width=100, height=45, font=("Arial", 12, "bold")).pack(side="left")
        ctk.CTkButton(btn_row, text="THANH TOÁN & IN HÓA ĐƠN", fg_color="#2196F3", hover_color="#1976D2", height=45, font=("Arial", 14, "bold"), command=self.mo_form_thanh_toan).pack(side="left", fill="x", expand=True, padx=10)

    # ================= LOGIC & POPUPS =================
    def chon_ban(self, id):
        print(f"Chọn bàn {id}")

    def tim_khach(self):
        print("Tìm khách...")

    def doi_so_luong(self, delta):
        try:
            val = int(self.entry_sl.get()) + delta
            if val >= 1:
                self.entry_sl.delete(0, "end")
                self.entry_sl.insert(0, str(val))
        except: pass

    # --- Popup Thêm Khách ---
    def mo_form_them_khach_hang(self):
        w = ctk.CTkToplevel(self)
        w.title("Thêm Khách Hàng")
        w.geometry("400x450")
        w.transient(self.winfo_toplevel())
        w.grab_set()
        
        ctk.CTkLabel(w, text="THÊM KHÁCH HÀNG MỚI", font=("Arial", 16, "bold"), text_color="#4CAF50").pack(pady=20)
        
        f = ctk.CTkFrame(w, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=30)
        
        def add_field(lbl):
            ctk.CTkLabel(f, text=lbl, font=("Arial", 12)).pack(anchor="w", pady=(5,0))
            e = ctk.CTkEntry(f, height=35)
            e.pack(fill="x", pady=(0, 10))
            return e

        add_field("Tên khách hàng")
        add_field("Số điện thoại")
        add_field("Địa chỉ")
        
        ctk.CTkButton(w, text="LƯU THÔNG TIN", fg_color="#4CAF50", height=40, font=("Arial", 12, "bold"), command=w.destroy).pack(fill="x", padx=30, pady=20)

    # --- Popup Thanh Toán ---
    def mo_form_thanh_toan(self):
        w = ctk.CTkToplevel(self)
        w.title("Thanh Toán")
        w.geometry("600x550")
        w.transient(self.winfo_toplevel())
        w.grab_set()

        # Chia 2 cột: Trái (Hóa đơn), Phải (Phương thức)
        content = ctk.CTkFrame(w, fg_color="white")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # Cột trái
        left = ctk.CTkFrame(content, fg_color="#F9F9F9")
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(left, text="HÓA ĐƠN TẠM TÍNH", font=("Arial", 14, "bold")).pack(pady=15)
        # Giả lập list
        ctk.CTkLabel(left, text="1. Cà phê sữa đá (x2) ... 50,000", font=("Arial", 12)).pack(anchor="w", padx=20)
        ctk.CTkLabel(left, text="2. Sinh tố bơ (x1) ........ 45,000", font=("Arial", 12)).pack(anchor="w", padx=20)
        
        ctk.CTkFrame(left, height=2, fg_color="#ccc").pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(left, text="Tổng tiền: 124,000 đ", font=("Arial", 18, "bold"), text_color="#E91E63").pack()

        # Cột phải
        right = ctk.CTkFrame(content, fg_color="white")
        right.pack(side="right", fill="both", expand=True)
        
        ctk.CTkLabel(right, text="PHƯƠNG THỨC THANH TOÁN", font=("Arial", 14, "bold")).pack(pady=15)
        
        # Tiền mặt
        ctk.CTkButton(right, text="💵 TIỀN MẶT", fg_color="#4CAF50", height=50, width=200, font=("Arial", 12, "bold")).pack(pady=10)
        
        # Chuyển khoản
        qr_btn = ctk.CTkButton(right, text="📱 CHUYỂN KHOẢN / QR", fg_color="#2196F3", height=50, width=200, font=("Arial", 12, "bold"))
        qr_btn.pack(pady=10)
        
        def show_qr():
            # Demo QR popup
            qw = ctk.CTkToplevel(w)
            qw.geometry("300x400")
            qw.title("Quét mã QR")
            ctk.CTkLabel(qw, text="Quét mã để thanh toán", font=("Arial", 14, "bold")).pack(pady=20)
            qr_box = ctk.CTkFrame(qw, width=200, height=200, fg_color="#eee")
            qr_box.pack()
            ctk.CTkLabel(qr_box, text="[QR CODE]", font=("Arial", 16)).place(relx=0.5, rely=0.5, anchor="center")
            ctk.CTkButton(qw, text="XÁC NHẬN ĐÃ NHẬN TIỀN", fg_color="#4CAF50", command=lambda: [qw.destroy(), w.destroy()]).pack(fill="x", padx=20, pady=20)

        qr_btn.configure(command=show_qr)

        ctk.CTkButton(right, text="HỦY BỎ", fg_color="#999", height=40, width=200, command=w.destroy).pack(side="bottom", pady=10)