import customtkinter as ctk
from tkinter import messagebox

class SanPhamPage(ctk.CTkFrame):
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
        ctk.CTkLabel(container, text="Quản lý Sản phẩm", font=("Arial", 18, "bold"), text_color="#333").pack(anchor="w", pady=(0, 20))

        # --- Form section (Nền xám nhạt) ---
        form_section = ctk.CTkFrame(container, fg_color="#f5f5f5", border_width=1, border_color="#ccc")
        form_section.pack(anchor="w", fill="x", pady=(0, 20))

        form_inner = ctk.CTkFrame(form_section, fg_color="#f5f5f5")
        form_inner.pack(fill="both", expand=True, padx=20, pady=20)

        # === Row 1: Nút + Tìm kiếm ===
        row1 = ctk.CTkFrame(form_inner, fg_color="#f5f5f5")
        row1.pack(anchor="w", fill="x", pady=(0, 20))

        # Action Buttons
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
        search_frame.pack(side="right", fill="x", expand=True, padx=(50, 0))

        ctk.CTkLabel(search_frame, text="Tìm kiếm:", font=("Arial", 11), text_color="#333").pack(side="left", padx=(0, 10))
        
        self.search_entry = ctk.CTkEntry(search_frame, height=32, border_width=1, border_color="#ccc")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(search_frame, text="Tìm", fg_color="#2196F3", text_color="white",
                      hover_color="#0b7dda", width=60, height=32, font=("Arial", 11, "bold"),
                      corner_radius=6).pack(side="left")

        # === Row 2: Thông tin sản phẩm ===
        row2 = ctk.CTkFrame(form_inner, fg_color="#f5f5f5")
        row2.pack(anchor="w", fill="x", pady=(0, 15))

        self.create_input(row2, "Mã sản phẩm", 120)
        self.create_input(row2, "Tên sản phẩm", 200)
        self.create_input(row2, "Đơn giá", 120)
        self.create_input(row2, "Nhà cung cấp", 180)

        # === Row 3: Phân loại + Số lượng + Ảnh ===
        row3 = ctk.CTkFrame(form_inner, fg_color="#f5f5f5")
        row3.pack(anchor="w", fill="x", pady=(0, 20))

        # Phân loại
        frame_phanloai = ctk.CTkFrame(row3, fg_color="#f5f5f5")
        frame_phanloai.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(frame_phanloai, text="Phân loại", font=("Arial", 11), text_color="#333").pack(anchor="w", pady=(0, 5))
        ctk.CTkEntry(frame_phanloai, height=32, width=150).pack()

        # Số lượng
        frame_soluong = ctk.CTkFrame(row3, fg_color="#f5f5f5")
        frame_soluong.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(frame_soluong, text="Số lượng", font=("Arial", 11), text_color="#333").pack(anchor="w", pady=(0, 5))
        ctk.CTkEntry(frame_soluong, height=32, width=100).pack()

        # Nút Ảnh (Canh giữa theo chiều dọc so với input)
        frame_btn = ctk.CTkFrame(row3, fg_color="#f5f5f5")
        frame_btn.pack(side="left", padx=(0, 20), anchor="s", pady=(20, 0)) # pady top để đẩy xuống bằng input
        
        ctk.CTkButton(frame_btn, text="Thêm ảnh", fg_color="#2196F3", text_color="white",
                      hover_color="#1976D2", width=120, height=32, font=("Arial", 11, "bold"),
                      corner_radius=6).pack()

        # --- Danh sách ---
        ctk.CTkLabel(container, text="Danh sách sản phẩm", font=("Arial", 14, "bold"), text_color="#333").pack(
            anchor="center", pady=(15, 15))

        list_frame = ctk.CTkFrame(container, fg_color="white", border_width=2, border_color="#ccc")
        list_frame.pack(fill="both", expand=True)

        # Header
        table_header = ctk.CTkFrame(list_frame, fg_color="#f0f0f0", height=40, corner_radius=0)
        table_header.pack(fill="x")
        table_header.pack_propagate(False)

        headers = [("STT", 0.06), ("Mã SP", 0.12), ("Tên sản phẩm", 0.24),
                   ("Đơn giá", 0.14), ("Nhà cung cấp", 0.18), ("Phân loại", 0.14), ("Số lượng", 0.12)]

        x_offset = 0
        for header_text, relwidth in headers:
            ctk.CTkLabel(table_header, text=header_text, font=("Arial", 11, "bold"),
                         text_color="#333", anchor="center" if header_text in ["STT", "Số lượng"] else "w").place(
                relx=x_offset, rely=0.5, anchor="w", relwidth=relwidth)
            x_offset += relwidth

        # Content
        table_content = ctk.CTkScrollableFrame(list_frame, fg_color="white", corner_radius=0)
        table_content.pack(fill="both", expand=True, padx=2, pady=2)

        ctk.CTkLabel(table_content, text="Chưa có dữ liệu sản phẩm\nVui lòng thêm sản phẩm mới",
                     font=("Arial", 11), text_color="#999").pack(pady=30)

    def create_input(self, parent, label_text, width):
        """Helper tạo label + entry"""
        col = ctk.CTkFrame(parent, fg_color="#f5f5f5")
        col.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(col, text=label_text, font=("Arial", 11), text_color="#333").pack(anchor="w", pady=(0, 5))
        ctk.CTkEntry(col, height=32, width=width).pack()