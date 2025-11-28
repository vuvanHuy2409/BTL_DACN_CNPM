import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

class QuanLyTKPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="white")
        
        # Biến lưu trữ
        self.current_image_path = None
        self.current_photo = None
        self.dummy_data = [
            {"id": "NV001", "name": "Nguyễn Văn A", "user": "admin", "pass": "******", "email": "admin@shop.com", "role": "Quản lý"},
            {"id": "NV002", "name": "Trần Thị B", "user": "staff01", "pass": "******", "email": "staff1@shop.com", "role": "Thu ngân"},
            {"id": "NV003", "name": "Lê Văn C", "user": "kho01", "pass": "******", "email": "kho@shop.com", "role": "Nhân viên kho"},
        ]

        self.tao_main_content()
        self.load_table_data()

    def tao_main_content(self):
        """Tạo nội dung chính"""
        # Container chính
        container = ctk.CTkFrame(self, fg_color="white")
        container.pack(fill="both", expand=True, padx=15, pady=15)

        # === TIÊU ĐỀ ===
        ctk.CTkLabel(
            container, text="QUẢN LÝ TÀI KHOẢN",
            font=("Arial", 20, "bold"), text_color="#333"
        ).pack(anchor="center", pady=(0, 20))

        # ================= KHUNG NHẬP LIỆU (FORM) =================
        # Khung viền xám bao quanh form
        input_group = ctk.CTkFrame(container, fg_color="#f5f5f5", border_width=1, border_color="#ccc")
        input_group.pack(fill="x", padx=20, pady=(0, 20))

        # --- 1. TOOLBAR (Nút bấm chức năng) ---
        toolbar = ctk.CTkFrame(input_group, fg_color="transparent")
        toolbar.pack(fill="x", padx=10, pady=(15, 10))

        # Frame chứa nút căn giữa
        btn_center = ctk.CTkFrame(toolbar, fg_color="transparent")
        btn_center.pack(anchor="center")

        self.create_btn(btn_center, "Thêm", "#4CAF50", "#45a049", self.them_tk)
        self.create_btn(btn_center, "Sửa", "#2196F3", "#0b7dda", self.sua_tk)
        self.create_btn(btn_center, "Xóa", "#f44336", "#da190b", self.xoa_tk)
        self.create_btn(btn_center, "Lưu", "#4CAF50", "#45a049", self.luu_tk) # Lưu dùng màu xanh lá giống Thêm
        self.create_btn(btn_center, "Xuất Excel", "#00BCD4", "#0097A7", self.xuat_excel, width=100)
        self.create_btn(btn_center, "Làm mới", "#9E9E9E", "#757575", self.lam_moi)

        # Đường kẻ ngang
        ctk.CTkFrame(input_group, height=1, fg_color="#ddd").pack(fill="x", padx=20, pady=5)

        # --- 2. FORM FIELDS ---
        form_container = ctk.CTkFrame(input_group, fg_color="transparent")
        form_container.pack(fill="x", padx=20, pady=20)

        # [CỘT TRÁI] Avatar
        left_col = ctk.CTkFrame(form_container, fg_color="transparent")
        left_col.pack(side="left", padx=(20, 40), anchor="n")

        # Khung ảnh tròn (Giả lập bằng frame vuông bo góc lớn)
        self.avatar_frame = ctk.CTkFrame(left_col, fg_color="white", width=120, height=120, corner_radius=60, border_width=2, border_color="#ddd")
        self.avatar_frame.pack(pady=(0, 10))
        self.avatar_frame.pack_propagate(False)

        self.avatar_label = ctk.CTkLabel(self.avatar_frame, text="📷", font=("Arial", 40), text_color="#ccc")
        self.avatar_label.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkButton(left_col, text="Thay đổi ảnh", width=100, height=28, fg_color="#607D8B", hover_color="#546E7A", command=self.chon_anh).pack()

        # [CỘT PHẢI] Thông tin chi tiết
        right_col = ctk.CTkFrame(form_container, fg_color="transparent")
        right_col.pack(side="left", fill="both", expand=True)

        # Hàng 1: ID, Tên, Username
        row1 = ctk.CTkFrame(right_col, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 10))
        self.entry_id = self.create_input(row1, "Mã NV (ID)", 100)
        self.entry_name = self.create_input(row1, "Họ và tên", 200)
        self.entry_user = self.create_input(row1, "Tên đăng nhập", 150)

        # Hàng 2: Pass, Email, Role
        row2 = ctk.CTkFrame(right_col, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 10))
        self.entry_pass = self.create_input(row2, "Mật khẩu", 150, show="*")
        self.entry_email = self.create_input(row2, "Email", 200)
        
        # Combo Vai trò
        f_role = ctk.CTkFrame(row2, fg_color="transparent")
        f_role.pack(side="left", padx=10)
        ctk.CTkLabel(f_role, text="Vai trò", font=("Arial", 11, "bold"), text_color="#555").pack(anchor="w", pady=(0, 2))
        self.combo_role = ctk.CTkComboBox(f_role, values=["Quản lý", "Thu ngân", "Nhân viên kho", "Bảo vệ"], width=150, height=30)
        self.combo_role.pack()

        # ================= DANH SÁCH (TABLE) =================
        ctk.CTkLabel(container, text="DANH SÁCH TÀI KHOẢN", font=("Arial", 14, "bold"), text_color="#333").pack(anchor="w", padx=20, pady=(10, 5))

        list_frame = ctk.CTkFrame(container, fg_color="white", border_width=1, border_color="#999")
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Header
        header_frame = ctk.CTkFrame(list_frame, fg_color="#E0E0E0", height=40, corner_radius=0)
        header_frame.pack(fill="x")
        
        headers = [("ID", 0.1), ("Họ và Tên", 0.25), ("Username", 0.15), ("Mật khẩu", 0.15), ("Email", 0.2), ("Vai trò", 0.15)]
        
        for i, (col, width) in enumerate(headers):
            lbl = ctk.CTkLabel(header_frame, text=col, font=("Arial", 11, "bold"), text_color="#333")
            # Căn chỉnh header cho đẹp
            anchor_pos = "w" if i > 0 else "center" 
            lbl.place(relx=sum(h[1] for h in headers[:i]), rely=0.5, anchor="w", relwidth=width)
            if i==0: lbl.configure(anchor="center") # Căn giữa cột ID

        # Scroll Content
        self.table_scroll = ctk.CTkScrollableFrame(list_frame, fg_color="white", corner_radius=0)
        self.table_scroll.pack(fill="both", expand=True)

    # ================= HELPERS =================
    def create_btn(self, parent, text, color, hover, cmd, width=80):
        ctk.CTkButton(
            parent, text=text, fg_color=color, hover_color=hover, text_color="white",
            width=width, height=32, corner_radius=6, font=("Arial", 11, "bold"),
            command=cmd
        ).pack(side="left", padx=5)

    def create_input(self, parent, label, width, show=None):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(side="left", padx=10)
        ctk.CTkLabel(f, text=label, font=("Arial", 11, "bold"), text_color="#555").pack(anchor="w", pady=(0, 2))
        e = ctk.CTkEntry(f, width=width, height=30, show=show, border_color="#ccc")
        e.pack()
        return e

    def load_table_data(self):
        for widget in self.table_scroll.winfo_children():
            widget.destroy()

        for item in self.dummy_data:
            self.render_row(item)

    def render_row(self, item):
        row = ctk.CTkFrame(self.table_scroll, fg_color="white", height=35, corner_radius=0)
        row.pack(fill="x", pady=1)

        # Hover Effect
        def on_enter(e): row.configure(fg_color="#E3F2FD")
        def on_leave(e): row.configure(fg_color="white")
        row.bind("<Enter>", on_enter)
        row.bind("<Leave>", on_leave)

        # Values
        values = [item["id"], item["name"], item["user"], item["pass"], item["email"], item["role"]]
        widths = [0.1, 0.25, 0.15, 0.15, 0.2, 0.15]
        
        current_x = 0
        for i, (val, w) in enumerate(zip(values, widths)):
            lbl = ctk.CTkLabel(row, text=val, font=("Arial", 11), text_color="#333")
            if i == 0: # ID căn giữa
                lbl.place(relx=current_x, rely=0.5, anchor="w", relwidth=w)
                lbl.configure(anchor="center")
            else:
                lbl.place(relx=current_x, rely=0.5, anchor="w", relwidth=w)
                lbl.configure(anchor="w", padx=5) # Padding trái cho text
            
            current_x += w
            # Bind sự kiện click cho cả label
            lbl.bind("<Button-1>", lambda e, d=item: self.select_item(d))
        
        row.bind("<Button-1>", lambda e, d=item: self.select_item(d))

    def select_item(self, data):
        # Đổ dữ liệu lên form
        self.entry_id.delete(0, "end"); self.entry_id.insert(0, data['id'])
        self.entry_name.delete(0, "end"); self.entry_name.insert(0, data['name'])
        self.entry_user.delete(0, "end"); self.entry_user.insert(0, data['user'])
        self.entry_pass.delete(0, "end"); self.entry_pass.insert(0, data['pass'])
        self.entry_email.delete(0, "end"); self.entry_email.insert(0, data['email'])
        self.combo_role.set(data['role'])

    # ================= LOGIC GIẢ LẬP =================
    def them_tk(self): messagebox.showinfo("Thông báo", "Chức năng Thêm Tài Khoản")
    def sua_tk(self): messagebox.showinfo("Thông báo", "Chức năng Sửa Tài Khoản")
    def xoa_tk(self): 
        if messagebox.askyesno("Xác nhận", "Xóa tài khoản này?"):
            messagebox.showinfo("Thông báo", "Đã xóa!")
    def luu_tk(self): messagebox.showinfo("Thông báo", "Đã lưu thay đổi!")
    def xuat_excel(self): messagebox.showinfo("Thông báo", "Đã xuất file Excel!")
    def lam_moi(self):
        self.entry_id.delete(0, "end")
        self.entry_name.delete(0, "end")
        self.entry_user.delete(0, "end")
        self.entry_pass.delete(0, "end")
        self.entry_email.delete(0, "end")
        self.combo_role.set("")
        self.load_table_data()

    def chon_anh(self):
        path = filedialog.askopenfilename(filetypes=[("Image", "*.jpg *.png *.jpeg")])
        if path:
            try:
                img = Image.open(path)
                # Crop square
                w, h = img.size
                s = min(w, h)
                img = img.crop(((w-s)//2, (h-s)//2, (w+s)//2, (h+s)//2))
                img = img.resize((120, 120), Image.Resampling.LANCZOS)
                
                self.current_photo = ImageTk.PhotoImage(img)
                self.avatar_label.configure(image=self.current_photo, text="")
            except Exception as e:
                print(e)