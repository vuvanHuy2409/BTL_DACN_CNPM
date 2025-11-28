import customtkinter as ctk
from tkinter import messagebox

class HoaDonPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="white")

        # Dữ liệu giả lập
        self.dummy_data = [
            {"id": "HD001", "kh": "Nguyễn Văn A", "ngay": "28/11/2025", "tien": 1500000, "status": "Đã thanh toán"},
            {"id": "HD002", "kh": "Trần Thị B", "ngay": "28/11/2025", "tien": 200000, "status": "Chờ thanh toán"},
            {"id": "HD003", "kh": "Lê Văn C", "ngay": "27/11/2025", "tien": 5500000, "status": "Đã thanh toán"},
            {"id": "HD004", "kh": "Phạm Thị D", "ngay": "26/11/2025", "tien": 890000, "status": "Hủy"},
        ]
        
        self.selected_id = None
        self.tao_main_content()

    def tao_main_content(self):
        container = ctk.CTkFrame(self, fg_color="white")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # === TITLE ===
        ctk.CTkLabel(container, text="Quản lý Hóa Đơn", font=("Arial", 20, "bold"), text_color="#333").pack(anchor="w", pady=(0, 20))

        # === CONTROL BAR (Buttons + Search) ===
        control_frame = ctk.CTkFrame(container, fg_color="white")
        control_frame.pack(fill="x", pady=(0, 15))

        # Left: Buttons
        btn_frame = ctk.CTkFrame(control_frame, fg_color="white")
        btn_frame.pack(side="left")

        # Helper tạo nút nhanh
        def create_btn(text, color, hover, cmd):
            return ctk.CTkButton(btn_frame, text=text, fg_color=color, hover_color=hover,
                                 text_color="white", font=("Arial", 11, "bold"),
                                 width=90, height=35, corner_radius=6, command=cmd)

        create_btn("Tạo mới", "#4CAF50", "#45a049", self.them_moi).pack(side="left", padx=(0, 10))
        create_btn("Sửa", "#2196F3", "#0b7dda", self.sua).pack(side="left", padx=(0, 10))
        create_btn("Xóa", "#f44336", "#da190b", self.xoa).pack(side="left", padx=(0, 10))
        create_btn("In HĐ", "#00BCD4", "#0097A7", self.in_hoadon).pack(side="left", padx=(0, 10))

        # Right: Search
        search_frame = ctk.CTkFrame(control_frame, fg_color="white")
        search_frame.pack(side="right")
        
        self.search_entry = ctk.CTkEntry(search_frame, width=250, height=35, placeholder_text="Tìm theo mã hoặc tên KH...", border_width=1, border_color="#ccc")
        self.search_entry.pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(search_frame, text="Tìm", fg_color="#607D8B", hover_color="#546E7A", width=60, height=35, command=self.tim_kiem).pack(side="left")

        # === TABLE AREA ===
        # Header Frame
        table_container = ctk.CTkFrame(container, fg_color="white", border_width=1, border_color="#ccc")
        table_container.pack(fill="both", expand=True)

        header_frame = ctk.CTkFrame(table_container, fg_color="#f0f0f0", height=40, corner_radius=0)
        header_frame.pack(fill="x")
        
        # Cấu hình cột: (Tên, Width ratio)
        columns = [("Mã HĐ", 0.1), ("Khách Hàng", 0.3), ("Ngày Tạo", 0.2), ("Tổng Tiền", 0.2), ("Trạng Thái", 0.2)]
        
        for i, (col_name, ratio) in enumerate(columns):
            lbl = ctk.CTkLabel(header_frame, text=col_name, font=("Arial", 11, "bold"), text_color="#333", anchor="w" if i != 4 else "center")
            lbl.place(relx=sum(c[1] for c in columns[:i]), rely=0.5, anchor="w", relwidth=ratio)

        # Content List (Scrollable)
        self.scroll_frame = ctk.CTkScrollableFrame(table_container, fg_color="white", corner_radius=0)
        self.scroll_frame.pack(fill="both", expand=True)

        # Load dữ liệu
        self.load_table_data(self.dummy_data)

    def load_table_data(self, data):
        # Xóa dữ liệu cũ
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if not data:
            ctk.CTkLabel(self.scroll_frame, text="Không tìm thấy dữ liệu", text_color="#999").pack(pady=20)
            return

        # Render từng dòng
        for item in data:
            self.render_row(item)

    def render_row(self, item):
        row = ctk.CTkFrame(self.scroll_frame, fg_color="white", height=40, corner_radius=0)
        row.pack(fill="x", pady=1)

        # Hiệu ứng hover
        def on_enter(e): row.configure(fg_color="#e3f2fd")
        def on_leave(e): 
            if self.selected_id != item['id']:
                row.configure(fg_color="white")
            else:
                row.configure(fg_color="#bbdefb") # Màu khi đang chọn

        def on_click(e):
            self.selected_id = item['id']
            # Reset màu các row khác (đơn giản hóa: load lại bảng hoặc lưu ref)
            self.load_table_data(self.dummy_data) # Load lại để refresh highlight (cách đơn giản nhất)
            
        row.bind("<Enter>", on_enter)
        row.bind("<Leave>", on_leave)
        row.bind("<Button-1>", on_click)

        # Màu nền trạng thái
        status_color = "#4CAF50" if item['status'] == "Đã thanh toán" else ("#FF9800" if item['status'] == "Chờ thanh toán" else "#F44336")
        
        # Hiển thị dữ liệu
        # 1. Mã
        ctk.CTkLabel(row, text=item['id'], font=("Arial", 11), text_color="#333", anchor="w").place(relx=0, rely=0.5, anchor="w", relwidth=0.1)
        # 2. Tên
        ctk.CTkLabel(row, text=item['kh'], font=("Arial", 11, "bold"), text_color="#333", anchor="w").place(relx=0.1, rely=0.5, anchor="w", relwidth=0.3)
        # 3. Ngày
        ctk.CTkLabel(row, text=item['ngay'], font=("Arial", 11), text_color="#555", anchor="w").place(relx=0.4, rely=0.5, anchor="w", relwidth=0.2)
        # 4. Tiền (Format VND)
        money_str = f"{item['tien']:,.0f} đ"
        ctk.CTkLabel(row, text=money_str, font=("Arial", 11, "bold"), text_color="#2196F3", anchor="w").place(relx=0.6, rely=0.5, anchor="w", relwidth=0.2)
        
        # 5. Trạng thái (Badge)
        status_frame = ctk.CTkFrame(row, fg_color=status_color, height=22, width=100, corner_radius=10)
        status_frame.place(relx=0.8, rely=0.5, anchor="w") # Canh giữa cột
        # Center text trong status frame
        ctk.CTkLabel(status_frame, text=item['status'], font=("Arial", 9, "bold"), text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        # Bind click cho cả các label con
        for child in row.winfo_children():
            if isinstance(child, ctk.CTkLabel):
                child.bind("<Button-1>", on_click)

    # === LOGIC FUNCTIONS ===
    def them_moi(self):
        messagebox.showinfo("Chức năng", "Mở form thêm hóa đơn mới")

    def sua(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hóa đơn cần sửa")
            return
        messagebox.showinfo("Chức năng", f"Đang sửa hóa đơn: {self.selected_id}")

    def xoa(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hóa đơn cần xóa")
            return
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa hóa đơn này?"):
            # Xóa mẫu trong dummy data
            self.dummy_data = [d for d in self.dummy_data if d['id'] != self.selected_id]
            self.selected_id = None
            self.load_table_data(self.dummy_data)

    def in_hoadon(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Chọn hóa đơn để in")
            return
        messagebox.showinfo("In ấn", f"Đang in hóa đơn {self.selected_id}...")

    def tim_kiem(self):
        key = self.search_entry.get().lower()
        if not key:
            self.load_table_data(self.dummy_data)
            return
        
        filtered = [d for d in self.dummy_data if key in d['id'].lower() or key in d['kh'].lower()]
        self.load_table_data(filtered)