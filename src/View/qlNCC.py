import customtkinter as ctk
from tkinter import ttk, messagebox

class NhaCungCapPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="white")
        
        # Dữ liệu giả lập
        self.dummy_data = [
            ("NCC001", "Công ty Thực Phẩm Sạch", "0901234567", "Rau củ"),
            ("NCC002", "Đại lý Bánh Kẹo Hữu Nghị", "0912345678", "Bánh kẹo"),
            ("NCC003", "Nông Sản Việt", "0987654321", "Gạo, Đậu"),
            ("NCC004", "Nước giải khát ABC", "0243999999", "Nước ngọt"),
        ]

        self.tao_main_content()
        self.load_table_data()

    def tao_main_content(self):
        # Container chính
        container = ctk.CTkFrame(self, fg_color="white")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Tiêu đề
        ctk.CTkLabel(container, text="Quản lý Nhà Cung Cấp", font=("Arial", 18, "bold"), text_color="#333").pack(anchor="w", pady=(0, 20))

        # === 1. CONTROL PANEL ===
        action_bar = ctk.CTkFrame(container, fg_color="white")
        action_bar.pack(fill="x", pady=(0, 20))

        # Buttons
        btn_frame = ctk.CTkFrame(action_bar, fg_color="white")
        btn_frame.pack(side="left")
        self.create_btn(btn_frame, "Thêm", "#4CAF50", "#45a049", self.them)
        self.create_btn(btn_frame, "Sửa", "#2196F3", "#0b7dda", self.sua)
        self.create_btn(btn_frame, "Xóa", "#f44336", "#da190b", self.xoa)
        self.create_btn(btn_frame, "Làm mới", "#9E9E9E", "#757575", self.lam_moi)
        self.create_btn(btn_frame, "Xuất Excel", "#00BCD4", "#0097A7", self.xuat, width=100)

        # Search
        search_frame = ctk.CTkFrame(action_bar, fg_color="white")
        search_frame.pack(side="right")
        self.search_entry = ctk.CTkEntry(search_frame, width=250, height=35, placeholder_text="Tên NCC hoặc SĐT...", border_color="#ccc")
        self.search_entry.pack(side="left", padx=(0, 5))
        ctk.CTkButton(search_frame, text="Tìm", fg_color="#2196F3", hover_color="#0b7dda", width=60, height=35, font=("Arial", 11, "bold"), command=self.tim_kiem).pack(side="left")

        # === 2. FORM NHẬP LIỆU ===
        form_wrapper = ctk.CTkFrame(container, fg_color="#f5f5f5", border_width=1, border_color="#ccc")
        form_wrapper.pack(fill="x", pady=(0, 20))
        
        form_inner = ctk.CTkFrame(form_wrapper, fg_color="#f5f5f5")
        form_inner.pack(fill="x", padx=20, pady=20)

        row1 = ctk.CTkFrame(form_inner, fg_color="#f5f5f5")
        row1.pack(fill="x", pady=(0, 15))
        self.entry_ma = self.create_input(row1, "Mã nhà cung cấp", 150)
        self.entry_ten = self.create_input(row1, "Tên nhà cung cấp", 300)

        row2 = ctk.CTkFrame(form_inner, fg_color="#f5f5f5")
        row2.pack(fill="x")
        self.entry_sdt = self.create_input(row2, "Số điện thoại", 150)
        self.entry_sp = self.create_input(row2, "Sản phẩm cung cấp", 300)

        # === 3. BẢNG DỮ LIỆU (TREEVIEW STYLE) ===
        ctk.CTkLabel(container, text="Danh sách Nhà cung cấp", font=("Arial", 14, "bold"), text_color="#333").pack(anchor="w", pady=(0, 10))

        table_frame = ctk.CTkFrame(container, fg_color="white", border_width=2, border_color="#ccc")
        table_frame.pack(fill="both", expand=True)

        # Cấu hình Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground="black", rowheight=30, fieldbackground="white", font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#f0f0f0", foreground="#333")
        style.map("Treeview", background=[("selected", "#2196F3")])

        # Treeview
        columns = ("ma", "ten", "sdt", "sp")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)

        # Định nghĩa cột
        self.tree.heading("ma", text="Mã NCC")
        self.tree.heading("ten", text="Tên Nhà Cung Cấp")
        self.tree.heading("sdt", text="Số điện thoại")
        self.tree.heading("sp", text="Sản phẩm")

        self.tree.column("ma", width=100, anchor="center")
        self.tree.column("ten", width=300, anchor="w")
        self.tree.column("sdt", width=150, anchor="center")
        self.tree.column("sp", width=200, anchor="w")

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=2, pady=2)

        # Bind sự kiện chọn dòng
        self.tree.bind("<<TreeviewSelect>>", self.on_select_row)

    # === HELPERS ===
    def create_btn(self, parent, text, color, hover, cmd, width=80):
        ctk.CTkButton(parent, text=text, fg_color=color, hover_color=hover, text_color="white", width=width, height=35, corner_radius=6, font=("Arial", 11, "bold"), command=cmd).pack(side="left", padx=5)

    def create_input(self, parent, label, width):
        f = ctk.CTkFrame(parent, fg_color="#f5f5f5")
        f.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(f, text=label, font=("Arial", 11, "bold"), text_color="#555").pack(anchor="w", pady=(0, 5))
        e = ctk.CTkEntry(f, width=width, height=32, border_color="#ccc")
        e.pack()
        return e

    # === LOGIC ===
    def load_table_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for data in self.dummy_data:
            self.tree.insert("", "end", values=data)

    def on_select_row(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0], "values")
            self.entry_ma.delete(0, "end"); self.entry_ma.insert(0, values[0])
            self.entry_ten.delete(0, "end"); self.entry_ten.insert(0, values[1])
            self.entry_sdt.delete(0, "end"); self.entry_sdt.insert(0, values[2])
            self.entry_sp.delete(0, "end"); self.entry_sp.insert(0, values[3])

    def them(self): messagebox.showinfo("TB", "Thêm")
    def sua(self): messagebox.showinfo("TB", "Sửa")
    def xoa(self): messagebox.showinfo("TB", "Xóa")
    def lam_moi(self): 
        self.entry_ma.delete(0, "end")
        self.entry_ten.delete(0, "end")
        self.entry_sdt.delete(0, "end")
        self.entry_sp.delete(0, "end")
    def xuat(self): messagebox.showinfo("TB", "Xuất Excel")
    def tim_kiem(self): pass