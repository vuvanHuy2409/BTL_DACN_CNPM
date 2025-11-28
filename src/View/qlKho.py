import customtkinter as ctk
from tkinter import messagebox

class KhoPage(ctk.CTkFrame):
    def __init__(self, parent):
        # 1. Kế thừa Frame để nhúng vào Main
        super().__init__(parent, fg_color="white")

        # 2. Tạo giao diện
        self.tao_main_content()

    def tao_main_content(self):
        """Tạo nội dung chính"""
        # Container chính
        container = ctk.CTkFrame(self, fg_color="white")
        container.pack(fill="both", expand=True, padx=15, pady=15)

        # Tiêu đề
        title = ctk.CTkLabel(container, text="Quản lý Kho", font=("Arial", 16, "bold"), text_color="#333")
        title.pack(anchor="w", pady=(0, 15))

        # --- Form section (Nền xám nhạt) ---
        form_section = ctk.CTkFrame(container, fg_color="#f5f5f5", border_width=1, border_color="#ccc")
        form_section.pack(anchor="w", fill="x", pady=(0, 20))

        form_inner = ctk.CTkFrame(form_section, fg_color="#f5f5f5")
        form_inner.pack(fill="both", expand=True, padx=15, pady=15)

        # === Row 1: Buttons + Search ===
        row1 = ctk.CTkFrame(form_inner, fg_color="#f5f5f5")
        row1.pack(anchor="w", fill="x", pady=(0, 20))

        # Action Buttons (Đã áp dụng màu)
        action_frame = ctk.CTkFrame(row1, fg_color="#f5f5f5")
        action_frame.pack(side="left", anchor="w")

        # Nút THÊM (Xanh lá)
        ctk.CTkButton(action_frame, text="Thêm", fg_color="#4CAF50", text_color="white",
                      hover_color="#45a049", width=80, height=35, font=("Arial", 11, "bold"),
                      corner_radius=6).pack(side="left", padx=(0, 10))

        # Nút SỬA (Xanh dương)
        ctk.CTkButton(action_frame, text="Sửa", fg_color="#2196F3", text_color="white",
                      hover_color="#0b7dda", width=80, height=35, font=("Arial", 11, "bold"),
                      corner_radius=6).pack(side="left", padx=(0, 10))

        # Nút XÓA (Đỏ)
        ctk.CTkButton(action_frame, text="Xóa", fg_color="#f44336", text_color="white",
                      hover_color="#da190b", width=80, height=35, font=("Arial", 11, "bold"),
                      corner_radius=6).pack(side="left", padx=(0, 10))

        # Nút LÀM MỚI (Xám)
        ctk.CTkButton(action_frame, text="Làm mới", fg_color="#9E9E9E", text_color="white",
                      hover_color="#757575", width=90, height=35, font=("Arial", 11, "bold"),
                      corner_radius=6).pack(side="left", padx=(0, 10))

        # Nút XUẤT (Cyan)
        ctk.CTkButton(action_frame, text="Xuất Excel", fg_color="#00BCD4", text_color="white",
                      hover_color="#0097A7", width=100, height=35, font=("Arial", 11, "bold"),
                      corner_radius=6).pack(side="left")

        # Search Box
        search_frame = ctk.CTkFrame(row1, fg_color="#f5f5f5")
        search_frame.pack(side="right", fill="x", expand=True, padx=(40, 0))

        ctk.CTkLabel(search_frame, text="Tìm kiếm:", font=("Arial", 11), text_color="#333").pack(side="left", padx=(0, 10))
        
        self.search_entry = ctk.CTkEntry(search_frame, height=32, border_width=1, border_color="#ccc")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(search_frame, text="Tìm", fg_color="#2196F3", text_color="white",
                      hover_color="#0b7dda", width=60, height=32, font=("Arial", 11, "bold"),
                      corner_radius=6).pack(side="left")

        # === Row 2: Form fields ===
        row2 = ctk.CTkFrame(form_inner, fg_color="#f5f5f5")
        row2.pack(anchor="w", fill="x", pady=(0, 15))

        self.create_input(row2, "Mã nguyên liệu", 120)
        self.create_input(row2, "Tên nguyên liệu", None, fill="x")  # None width để fill
        self.create_input(row2, "Giá nhập", 120)
        self.create_input(row2, "Nhà cung cấp", 200)

        # === Row 3: Form fields ===
        row3 = ctk.CTkFrame(form_inner, fg_color="#f5f5f5")
        row3.pack(anchor="w", fill="x", pady=(0, 20))
        self.create_input(row3, "Số lượng", 100)
        # Có thể thêm Ghi chú ở đây nếu cần cho cân đối

        # --- List section ---
        ctk.CTkLabel(container, text="Danh sách nguyên liệu", font=("Arial", 12, "bold"), text_color="#333").pack(
            anchor="center", pady=(10, 10))

        list_frame = ctk.CTkFrame(container, fg_color="white", border_width=2, border_color="#ccc")
        list_frame.pack(fill="both", expand=True)

        # Header
        table_header = ctk.CTkFrame(list_frame, fg_color="#f0f0f0", height=40, corner_radius=0)
        table_header.pack(fill="x")
        table_header.pack_propagate(False)

        headers = [("STT", 0.08), ("Mã NL", 0.15), ("Tên nguyên liệu", 0.30),
                   ("Giá nhập", 0.17), ("Nhà cung cấp", 0.20), ("Số lượng", 0.10)]

        x_offset = 0
        for header_text, relwidth in headers:
            label = ctk.CTkLabel(table_header, text=header_text, font=("Arial", 11, "bold"),
                                 text_color="#333", anchor="center" if header_text in ["STT", "Số lượng"] else "w")
            label.place(relx=x_offset, rely=0.5, anchor="w", relwidth=relwidth)
            x_offset += relwidth

        # Content
        self.table_content = ctk.CTkScrollableFrame(list_frame, fg_color="white", corner_radius=0)
        self.table_content.pack(fill="both", expand=True, padx=2, pady=2)

        ctk.CTkLabel(self.table_content, text="Chưa có dữ liệu nguyên liệu\nVui lòng thêm nguyên liệu mới",
                     font=("Arial", 11), text_color="#999").pack(pady=30)

    def create_input(self, parent, label_text, width, fill=None):
        """Helper để tạo label và entry nhanh"""
        # Set fg_color là #f5f5f5 để trùng màu nền form
        frame = ctk.CTkFrame(parent, fg_color="#f5f5f5")
        frame.pack(side="left", padx=(0, 15), fill=fill if fill else "none", expand=True if fill else False)

        ctk.CTkLabel(frame, text=label_text, font=("Arial", 10), text_color="#333").pack(anchor="w", pady=(0, 5))
        if width:
            ctk.CTkEntry(frame, height=28, width=width).pack(anchor="w")
        else:
            ctk.CTkEntry(frame, height=28).pack(fill="x")