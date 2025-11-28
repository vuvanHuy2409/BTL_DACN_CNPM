import customtkinter as ctk
from tkinter import ttk, messagebox

class NhanVienPage(ctk.CTkFrame):
    def __init__(self, parent):
        # 1. Kế thừa Frame để nhúng vào Main
        super().__init__(parent, fg_color="white")

        # Dữ liệu giả lập
        self.dummy_data = [
            ("NV001", "Nguyễn Văn A", "a.nguyen@email.com", "0909123456", "01/01/1995"),
            ("NV002", "Trần Thị B", "b.tran@email.com", "0912345678", "15/05/1998"),
            ("NV003", "Lê Văn C", "c.le@email.com", "0987654321", "20/10/2000"),
            ("NV004", "Phạm Thị D", "d.pham@email.com", "0933444555", "05/09/1992"),
        ]

        # 2. Tạo giao diện
        self.tao_main_content()
        self.load_table_data()

    def tao_main_content(self):
        """Tạo nội dung chính"""
        # Container chính
        container = ctk.CTkFrame(self, fg_color="white")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Tiêu đề
        ctk.CTkLabel(container, text="Quản lý Nhân viên", font=("Arial", 18, "bold"), text_color="#333").pack(anchor="w", pady=(0, 20))

        # ====================== 1. CONTROL PANEL (BUTTONS + SEARCH) ======================
        action_bar = ctk.CTkFrame(container, fg_color="white")
        action_bar.pack(fill="x", pady=(0, 20))

        # --- Buttons ---
        btn_frame = ctk.CTkFrame(action_bar, fg_color="white")
        btn_frame.pack(side="left")

        self.create_btn(btn_frame, "Thêm", "#4CAF50", "#45a049", self.them)
        self.create_btn(btn_frame, "Sửa", "#2196F3", "#0b7dda", self.sua)
        self.create_btn(btn_frame, "Xóa", "#f44336", "#da190b", self.xoa)
        self.create_btn(btn_frame, "Làm mới", "#9E9E9E", "#757575", self.lam_moi)
        self.create_btn(btn_frame, "Xuất Excel", "#00BCD4", "#0097A7", self.xuat, width=100)

        # --- Search ---
        search_frame = ctk.CTkFrame(action_bar, fg_color="white")
        search_frame.pack(side="right")

        self.search_entry = ctk.CTkEntry(search_frame, width=250, height=35, placeholder_text="Mã, Tên hoặc SĐT...", border_width=1, border_color="#ccc")
        self.search_entry.pack(side="left", padx=(0, 5))
        
        ctk.CTkButton(search_frame, text="Tìm", fg_color="#2196F3", hover_color="#0b7dda", width=60, height=35, font=("Arial", 11, "bold"), command=self.tim_kiem).pack(side="left")

        # ====================== 2. FORM NHẬP LIỆU (Nền xám) ======================
        form_wrapper = ctk.CTkFrame(container, fg_color="#f5f5f5", border_width=1, border_color="#ccc")
        form_wrapper.pack(fill="x", pady=(0, 20))
        
        form_inner = ctk.CTkFrame(form_wrapper, fg_color="#f5f5f5")
        form_inner.pack(fill="x", padx=20, pady=20)

        # Hàng 1: Mã - Tên
        row1 = ctk.CTkFrame(form_inner, fg_color="#f5f5f5")
        row1.pack(fill="x", pady=(0, 15))
        self.entry_ma = self.create_input(row1, "Mã nhân viên", 150)
        self.entry_ten = self.create_input(row1, "Tên nhân viên", 250)
        
        # Hàng 2: Email - SĐT - Ngày sinh
        row2 = ctk.CTkFrame(form_inner, fg_color="#f5f5f5")
        row2.pack(fill="x")
        self.entry_email = self.create_input(row2, "Email", 250)
        self.entry_sdt = self.create_input(row2, "Số điện thoại", 150)
        self.entry_ns = self.create_input(row2, "Ngày sinh", 150)

        # ====================== 3. BẢNG DỮ LIỆU (TREEVIEW) ======================
        ctk.CTkLabel(container, text="Danh sách nhân viên", font=("Arial", 14, "bold"), text_color="#333").pack(anchor="w", pady=(0, 10))

        table_frame = ctk.CTkFrame(container, fg_color="white", border_width=1, border_color="#ccc")
        table_frame.pack(fill="both", expand=True)

        # Style Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground="black", rowheight=30, fieldbackground="white", font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#f0f0f0", foreground="#333")
        style.map("Treeview", background=[("selected", "#2196F3")])

        # Treeview Definition
        columns = ("ma", "ten", "email", "sdt", "ns")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        self.tree.heading("ma", text="Mã NV")
        self.tree.heading("ten", text="Họ tên")
        self.tree.heading("email", text="Email")
        self.tree.heading("sdt", text="Số điện thoại")
        self.tree.heading("ns", text="Ngày sinh")

        self.tree.column("ma", width=100, anchor="center")
        self.tree.column("ten", width=200, anchor="w")
        self.tree.column("email", width=250, anchor="w")
        self.tree.column("sdt", width=120, anchor="center")
        self.tree.column("ns", width=120, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=2, pady=2)

        # Bind Event Select Row
        self.tree.bind("<<TreeviewSelect>>", self.on_select_row)

    # ====================== HELPERS ======================
    def create_btn(self, parent, text, color, hover, cmd, width=80):
        ctk.CTkButton(parent, text=text, fg_color=color, hover_color=hover, text_color="white",
                      width=width, height=35, corner_radius=6, font=("Arial", 11, "bold"),
                      command=cmd).pack(side="left", padx=5)

    def create_input(self, parent, label, width):
        f = ctk.CTkFrame(parent, fg_color="#f5f5f5")
        f.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(f, text=label, font=("Arial", 11, "bold"), text_color="#555").pack(anchor="w", pady=(0, 5))
        e = ctk.CTkEntry(f, width=width, height=32, border_color="#ccc")
        e.pack()
        return e

    # ====================== LOGIC ======================
    def load_table_data(self):
        # Xóa hết dữ liệu cũ
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Load dữ liệu mới
        for row in self.dummy_data:
            self.tree.insert("", "end", values=row)

    def on_select_row(self, event):
        # Lấy dòng đang chọn
        selected = self.tree.selection()
        if selected:
            val = self.tree.item(selected[0], "values")
            # Đổ dữ liệu lên form
            self.entry_ma.delete(0, "end"); self.entry_ma.insert(0, val[0])
            self.entry_ten.delete(0, "end"); self.entry_ten.insert(0, val[1])
            self.entry_email.delete(0, "end"); self.entry_email.insert(0, val[2])
            self.entry_sdt.delete(0, "end"); self.entry_sdt.insert(0, val[3])
            self.entry_ns.delete(0, "end"); self.entry_ns.insert(0, val[4])

    def them(self): messagebox.showinfo("Thông báo", "Chức năng Thêm nhân viên")
    def sua(self): messagebox.showinfo("Thông báo", "Chức năng Sửa nhân viên")
    def xoa(self): 
        if messagebox.askyesno("Xác nhận", "Bạn muốn xóa nhân viên này?"):
            messagebox.showinfo("Thông báo", "Đã xóa!")
    def lam_moi(self):
        self.entry_ma.delete(0, "end")
        self.entry_ten.delete(0, "end")
        self.entry_email.delete(0, "end")
        self.entry_sdt.delete(0, "end")
        self.entry_ns.delete(0, "end")
    def xuat(self): messagebox.showinfo("Thông báo", "Đã xuất Excel")
    def tim_kiem(self): messagebox.showinfo("Thông báo", f"Đang tìm: {self.search_entry.get()}")