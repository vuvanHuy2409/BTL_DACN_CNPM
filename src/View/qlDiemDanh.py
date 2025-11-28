import customtkinter as ctk
from tkinter import ttk, messagebox

class DiemDanhPage(ctk.CTkFrame):
    def __init__(self, parent):
        # 1. Kế thừa Frame để nhúng vào Main
        super().__init__(parent, fg_color="white")

        # 2. Tạo giao diện
        self.tao_main_content()

    def tao_main_content(self):
        """Tạo nội dung chính"""
        # Container chính
        container = ctk.CTkFrame(self, fg_color="white")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Tiêu đề
        ctk.CTkLabel(container, text="Điểm danh (Nhận diện khuôn mặt)",
                     font=("Arial", 18, "bold"), text_color="#333").pack(anchor="w", pady=(0, 20))

        # ===== KHUNG TRÊN: FORM NHẬP + NÚT (Nền xám nhạt) =====
        top_frame = ctk.CTkFrame(container, fg_color="#f5f5f5", border_width=1, border_color="#ccc")
        top_frame.pack(anchor="w", fill="x", pady=(0, 20))

        content_top = ctk.CTkFrame(top_frame, fg_color="#f5f5f5")
        content_top.pack(anchor="w", padx=20, pady=20)

        # --- Mã NV + menu chọn nhân viên ---
        ctk.CTkLabel(content_top, text="Chọn Nhân Viên:", font=("Arial", 11), text_color="#333").pack(side="left", padx=(0, 10))

        nv_options = ["Nhân viên 1", "Nhân viên 2", "Nhân viên 3", "Nhân viên 4", "Nhân viên 5"]
        # Sử dụng ctk.CTkComboBox thay cho ttk.Combobox để đẹp hơn
        self.nv_combobox = ctk.CTkComboBox(content_top, values=nv_options, state="readonly", 
                                           width=200, height=35, border_width=1, border_color="#ccc")
        self.nv_combobox.set("Nhân viên 1")
        self.nv_combobox.pack(side="left", padx=(0, 20))

        # --- Các nút hành động (Đã áp dụng màu) ---
        
        # Nút Thu thập mẫu (Xanh lá)
        ctk.CTkButton(content_top, text="Thu thập mẫu", fg_color="#4CAF50", text_color="white",
                      hover_color="#45a049", width=120, height=35, font=("Arial", 11, "bold"),
                      corner_radius=6, command=self.thu_thap_mau).pack(side="left", padx=(0, 10))

        # Nút Điểm danh (Xanh dương)
        ctk.CTkButton(content_top, text="Điểm danh", fg_color="#2196F3", text_color="white",
                      hover_color="#0b7dda", width=120, height=35, font=("Arial", 11, "bold"),
                      corner_radius=6, command=self.diem_danh).pack(side="left", padx=(0, 10))

        # Nút Làm mới (Xám)
        ctk.CTkButton(content_top, text="Làm mới", fg_color="#9E9E9E", text_color="white",
                      hover_color="#757575", width=100, height=35, font=("Arial", 11, "bold"),
                      corner_radius=6, command=self.lam_moi).pack(side="left")

        # ===== KHUNG DƯỚI: BẢNG DỮ LIỆU =====
        ctk.CTkLabel(container, text="Lịch sử điểm danh trong ngày", font=("Arial", 14, "bold"),
                     text_color="#333").pack(anchor="center", pady=(10, 10))

        bottom_frame = ctk.CTkFrame(container, fg_color="white", border_width=2, border_color="#ccc")
        bottom_frame.pack(fill="both", expand=True)

        # Cấu hình Style cho Treeview (Vì Treeview là widget của tk, không phải ctk)
        style = ttk.Style()
        style.theme_use("clam") # Sử dụng theme clam để dễ tùy chỉnh
        style.configure("Treeview", 
                        background="white",
                        foreground="black",
                        rowheight=30, 
                        fieldbackground="white",
                        font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#f0f0f0")
        style.map("Treeview", background=[("selected", "#2196F3")])

        # Bảng Treeview
        columns = ("manv", "hoten", "thoigian", "trangthai")
        self.tree = ttk.Treeview(bottom_frame, columns=columns, show="headings", height=15)

        self.tree.heading("manv", text="Mã NV")
        self.tree.heading("hoten", text="Họ tên")
        self.tree.heading("thoigian", text="Thời gian")
        self.tree.heading("trangthai", text="Trạng thái")

        self.tree.column("manv", width=100, anchor="center")
        self.tree.column("hoten", width=250, anchor="w")
        self.tree.column("thoigian", width=200, anchor="center")
        self.tree.column("trangthai", width=150, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(bottom_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=2, pady=2)

        # Thêm dữ liệu mẫu
        self.insert_sample_data()

    # ================= CÁC HÀM XỬ LÝ (LOGIC) =================
    def insert_sample_data(self):
        data = [
            ("NV001", "Nguyễn Văn A", "08:00:05", "Đúng giờ"),
            ("NV002", "Trần Thị B", "08:15:30", "Muộn"),
            ("NV003", "Lê Văn C", "07:55:12", "Đúng giờ"),
        ]
        for item in data:
            self.tree.insert("", "end", values=item)

    def thu_thap_mau(self):
        nv = self.nv_combobox.get()
        messagebox.showinfo("Thông báo",
                            f"Bắt đầu thu thập dữ liệu khuôn mặt cho {nv}...\n(Chức năng Camera chưa kết nối)")

    def diem_danh(self):
        messagebox.showinfo("Thông báo", "Đang bật Camera điểm danh...\n(Chức năng Camera chưa kết nối)")

    def lam_moi(self):
        # Xóa hết dữ liệu bảng và load lại
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.insert_sample_data()
        messagebox.showinfo("Thông báo", "Đã làm mới dữ liệu!")