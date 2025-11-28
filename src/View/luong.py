import customtkinter as ctk
from tkinter import messagebox

class LuongPage(ctk.CTkFrame):
    def __init__(self, parent):
        # 1. Kế thừa Frame để nhúng vào Main
        super().__init__(parent, fg_color="white")

        # 2. Biến toàn cục
        self.salary_data = []
        self.selected_index = None

        # 3. Tạo giao diện
        self.tao_main_content()

    def tao_main_content(self):
        """Tạo nội dung chính"""
        # Container chính
        container = ctk.CTkFrame(self, fg_color="white")
        container.pack(fill="both", expand=True, padx=15, pady=15)

        # Header
        header = ctk.CTkFrame(container, fg_color="white")
        header.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(header, text="Quản lý tiền lương",
                     font=("Arial", 16, "bold"), text_color="#333").pack(side="left")

        month_dropdown = ctk.CTkComboBox(
            header,
            values=[f"Tháng {i}/2025" for i in range(1, 13)],
            width=150,
            state="readonly"
        )
        month_dropdown.set("Tháng 10/2025")
        month_dropdown.pack(side="right")

        # Xây dựng các thành phần giao diện
        self.build_form(container)
        self.build_function_buttons(container)
        self.build_search_bar(container)
        self.build_table(container)

    # ---------------- FORM (Đã cập nhật màu nền #f5f5f5) ----------------
    def build_form(self, main_frame):
        frame = ctk.CTkFrame(main_frame, fg_color="#f5f5f5", border_width=1, border_color="#ccc")
        frame.pack(fill="x", pady=(0, 15))

        grid = ctk.CTkFrame(frame, fg_color="#f5f5f5")
        grid.pack(fill="x", padx=15, pady=15)

        # === HÀNG 1 ===
        self.label_entry(grid, "Mã NV:", 0, 0)
        self.entry_manv = self.entry(grid, 0, 1)

        self.label_entry(grid, "Họ tên:", 0, 2)
        self.entry_hoten = self.entry(grid, 0, 3, w=200)

        self.label_entry(grid, "Số ngày làm:", 0, 4)
        self.entry_songay = self.entry(grid, 0, 5, w=120)
        self.entry_songay.bind("<KeyRelease>", lambda e: self.calculate_total())

        # === HÀNG 2 ===
        self.label_entry(grid, "Lương cơ bản:", 1, 0)
        self.entry_luongcb = self.entry(grid, 1, 1)
        self.entry_luongcb.bind("<KeyRelease>", lambda e: self.calculate_total())

        self.label_entry(grid, "Thưởng:", 1, 2)
        self.entry_thuong = self.entry(grid, 1, 3)
        self.entry_thuong.bind("<KeyRelease>", lambda e: self.calculate_total())

        self.label_entry(grid, "Phạt:", 1, 4)
        self.entry_phat = self.entry(grid, 1, 5, w=120)
        self.entry_phat.bind("<KeyRelease>", lambda e: self.calculate_total())

        # === HÀNG 3 ===
        ctk.CTkLabel(grid, text="Tổng lương:",
                     font=("Arial", 11, "bold"), text_color="#333").grid(row=2, column=0, sticky="w")
        self.entry_tongluong = ctk.CTkEntry(grid, width=180, font=("Arial", 10, "bold"), state="readonly", text_color="red")
        self.entry_tongluong.grid(row=2, column=1, padx=(0, 30), pady=8)

        self.label_entry(grid, "Ghi chú:", 2, 2)
        self.entry_ghichu = ctk.CTkEntry(grid, width=400, height=30, font=("Arial", 10))
        self.entry_ghichu.grid(row=2, column=3, columnspan=3, pady=8, sticky="w")

    # Helper tạo Label + Entry
    def label_entry(self, frame, text, r, c):
        ctk.CTkLabel(frame, text=text, font=("Arial", 11), text_color="#333") \
            .grid(row=r, column=c, sticky="w", padx=(0, 10), pady=8)

    def entry(self, frame, r, c, w=180):
        e = ctk.CTkEntry(frame, width=w, height=30, font=("Arial", 10))
        e.grid(row=r, column=c, padx=(0, 30), pady=8, sticky="w")
        return e

    # ---------------- BUTTONS (ĐÃ ÁP DỤNG MÀU) ----------------
    def build_function_buttons(self, main_frame):
        frame = ctk.CTkFrame(main_frame, fg_color="white")
        frame.pack(fill="x", pady=(0, 15), anchor="w")

        # Nút THÊM (Xanh lá)
        ctk.CTkButton(frame, text="Thêm", fg_color="#4CAF50", text_color="white",
                      hover_color="#45a049", width=100, height=35, font=("Arial", 11, "bold"),
                      corner_radius=6, command=self.add_salary).pack(side="left", padx=(0, 10))
        
        # Nút SỬA (Xanh dương)
        ctk.CTkButton(frame, text="Sửa", fg_color="#2196F3", text_color="white",
                      hover_color="#0b7dda", width=100, height=35, font=("Arial", 11, "bold"),
                      corner_radius=6, command=self.edit_salary).pack(side="left", padx=(0, 10))
        
        # Nút XÓA (Đỏ)
        ctk.CTkButton(frame, text="Xóa", fg_color="#f44336", text_color="white",
                      hover_color="#da190b", width=100, height=35, font=("Arial", 11, "bold"),
                      corner_radius=6, command=self.delete_salary).pack(side="left", padx=(0, 10))
        
        # Nút LÀM MỚI (Xám)
        ctk.CTkButton(frame, text="Làm mới", fg_color="#9E9E9E", text_color="white",
                      hover_color="#757575", width=100, height=35, font=("Arial", 11, "bold"),
                      corner_radius=6, command=self.clear_form).pack(side="left", padx=(0, 10))
        
        # Nút XUẤT EXCEL (Cyan)
        ctk.CTkButton(frame, text="Xuất Excel", fg_color="#00BCD4", text_color="white",
                      hover_color="#0097A7", width=120, height=35, font=("Arial", 11, "bold"),
                      corner_radius=6, command=self.export_data).pack(side="left")

    # ---------------- SEARCH (ĐÃ SỬA STYLE) ----------------
    def build_search_bar(self, main_frame):
        frame = ctk.CTkFrame(main_frame, fg_color="white")
        frame.pack(fill="x", pady=(0, 10))
        
        search_container = ctk.CTkFrame(frame, fg_color="#f5f5f5")
        search_container.pack(fill="x")

        ctk.CTkLabel(search_container, text="Tìm kiếm:", font=("Arial", 11),
                     text_color="#333").pack(side="left", padx=(10, 10), pady=5)

        self.entry_search = ctk.CTkEntry(search_container, width=300, height=32,
                                         placeholder_text="Nhập mã NV hoặc tên nhân viên...",
                                         border_width=1, border_color="#ccc")
        self.entry_search.pack(side="left", padx=(0, 10), pady=5)

        ctk.CTkButton(search_container, text="Tìm", fg_color="#2196F3", text_color="white",
                      hover_color="#0b7dda", width=80, height=32, font=("Arial", 11, "bold"),
                      corner_radius=6, command=self.search_salary).pack(side="left", pady=5)

    # ---------------- TABLE ----------------
    def build_table(self, main_frame):
        # Frame chứa bảng
        table_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=0, border_width=1, border_color="#ccc")
        table_frame.pack(fill="both", expand=True)

        # Header bảng
        header = ctk.CTkFrame(table_frame, fg_color="#f0f0f0", height=40, corner_radius=0)
        header.pack(fill="x", padx=1, pady=1)

        columns = [
            ("STT", 50), ("Mã NV", 80), ("Họ tên", 150), ("Số ngày", 80),
            ("Lương cơ bản", 120), ("Thưởng", 100), ("Phạt", 100),
            ("Tổng lương", 120), ("Ghi chú", 150),
        ]

        for text, w in columns:
            ctk.CTkLabel(header, text=text, width=w, anchor="center",
                         font=("Arial", 11, "bold"), text_color="#333").pack(side="left", padx=2)

        # Nội dung bảng (Scrollable)
        self.list_content = ctk.CTkScrollableFrame(table_frame, fg_color="white", corner_radius=0)
        self.list_content.pack(fill="both", expand=True, padx=1, pady=1)

        self.update_list()

    # ========================== LOGIC XỬ LÝ ==========================
    def calculate_total(self):
        try:
            luong_cb = float(self.entry_luongcb.get() or 0)
            thuong = float(self.entry_thuong.get() or 0)
            phat = float(self.entry_phat.get() or 0)
            songay = float(self.entry_songay.get() or 0)

            # Công thức tính lương (Ví dụ: Lương CB / 26 ngày công * số ngày làm)
            tong = (luong_cb / 26 * songay) + thuong - phat

            self.entry_tongluong.configure(state="normal")
            self.entry_tongluong.delete(0, "end")
            self.entry_tongluong.insert(0, f"{tong:,.0f}")
            self.entry_tongluong.configure(state="readonly")
        except:
            pass

    def clear_form(self):
        self.entry_manv.delete(0, "end")
        self.entry_hoten.delete(0, "end")
        self.entry_songay.delete(0, "end")
        self.entry_luongcb.delete(0, "end")
        self.entry_thuong.delete(0, "end")
        self.entry_phat.delete(0, "end")
        self.entry_tongluong.configure(state="normal")
        self.entry_tongluong.delete(0, "end")
        self.entry_tongluong.configure(state="readonly")
        self.entry_ghichu.delete(0, "end")

        self.selected_index = None
        self.update_list()

    def add_salary(self):
        ma_nv = self.entry_manv.get().strip()
        ho_ten = self.entry_hoten.get().strip()
        so_ngay = self.entry_songay.get().strip()
        luong_cb = self.entry_luongcb.get().strip()

        if not ma_nv or not ho_ten or not so_ngay or not luong_cb:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin!")
            return

        self.salary_data.append({
            'ma_nv': ma_nv,
            'ho_ten': ho_ten,
            'so_ngay': so_ngay,
            'luong_cb': luong_cb,
            'thuong': self.entry_thuong.get().strip() or "0",
            'phat': self.entry_phat.get().strip() or "0",
            'tong_luong': self.entry_tongluong.get().strip(),
            'ghi_chu': self.entry_ghichu.get().strip()
        })

        self.update_list()
        self.clear_form()
        messagebox.showinfo("Thành công", "Đã thêm thông tin lương!")

    def edit_salary(self):
        if self.selected_index is None:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên cần sửa!")
            return

        ma_nv = self.entry_manv.get().strip()
        ho_ten = self.entry_hoten.get().strip()

        if not ma_nv or not ho_ten:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin!")
            return

        self.salary_data[self.selected_index] = {
            'ma_nv': ma_nv,
            'ho_ten': ho_ten,
            'so_ngay': self.entry_songay.get().strip(),
            'luong_cb': self.entry_luongcb.get().strip(),
            'thuong': self.entry_thuong.get().strip() or "0",
            'phat': self.entry_phat.get().strip() or "0",
            'tong_luong': self.entry_tongluong.get().strip(),
            'ghi_chu': self.entry_ghichu.get().strip()
        }

        self.update_list()
        self.clear_form()
        messagebox.showinfo("Thành công", "Đã cập nhật thông tin lương!")

    def delete_salary(self):
        if self.selected_index is None:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên cần xóa!")
            return

        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa thông tin này?"):
            self.salary_data.pop(self.selected_index)
            self.update_list()
            self.clear_form()
            messagebox.showinfo("Thành công", "Đã xóa thông tin lương!")

    def search_salary(self):
        keyword = self.entry_search.get().strip().lower()
        if not keyword:
            self.update_list()
            return

        for widget in self.list_content.winfo_children():
            widget.destroy()

        found = False
        for idx, salary in enumerate(self.salary_data):
            if keyword in salary['ma_nv'].lower() or keyword in salary['ho_ten'].lower():
                self.create_salary_row(idx, salary)
                found = True

        if not found:
            ctk.CTkLabel(self.list_content, text="Không tìm thấy kết quả",
                         font=("Arial", 11), text_color="#999").pack(pady=20)

    def load_salary_to_form(self, index):
        self.selected_index = index
        salary = self.salary_data[index]

        self.entry_manv.delete(0, "end")
        self.entry_manv.insert(0, salary['ma_nv'])

        self.entry_hoten.delete(0, "end")
        self.entry_hoten.insert(0, salary['ho_ten'])

        self.entry_songay.delete(0, "end")
        self.entry_songay.insert(0, salary['so_ngay'])

        self.entry_luongcb.delete(0, "end")
        self.entry_luongcb.insert(0, salary['luong_cb'])

        self.entry_thuong.delete(0, "end")
        self.entry_thuong.insert(0, salary['thuong'])

        self.entry_phat.delete(0, "end")
        self.entry_phat.insert(0, salary['phat'])

        self.entry_tongluong.configure(state="normal")
        self.entry_tongluong.delete(0, "end")
        self.entry_tongluong.insert(0, salary['tong_luong'])
        self.entry_tongluong.configure(state="readonly")

        self.entry_ghichu.delete(0, "end")
        self.entry_ghichu.insert(0, salary['ghi_chu'])

        self.update_list()

    def create_salary_row(self, index, salary):
        is_selected = (index == self.selected_index)

        row = ctk.CTkFrame(self.list_content, fg_color="#e3f2fd" if is_selected else "white",
                           height=40, border_width=0, corner_radius=0)
        row.pack(fill="x", pady=1)

        row.bind("<Button-1>", lambda e: self.load_salary_to_form(index))
        row.configure(cursor="hand2")

        info = [
            (str(index + 1), 50, "center"), (salary['ma_nv'], 80, "center"),
            (salary['ho_ten'], 150, "w"), (salary['so_ngay'], 80, "center"),
            (salary['luong_cb'], 120, "e"), (salary['thuong'], 100, "e"),
            (salary['phat'], 100, "e"), (salary['tong_luong'], 120, "e"),
            (salary['ghi_chu'], 150, "w")
        ]

        for i, (text, width, anchor) in enumerate(info):
            label = ctk.CTkLabel(row, text=text, width=width, anchor=anchor,
                                 font=("Arial", 10, "bold" if i == 7 else "normal"),
                                 text_color="#2196F3" if i == 7 else "#333")
            label.pack(side="left", padx=2)
            label.bind("<Button-1>", lambda e, idx=index: self.load_salary_to_form(idx))

    def update_list(self):
        for w in self.list_content.winfo_children():
            w.destroy()

        if not self.salary_data:
            ctk.CTkLabel(self.list_content,
                         text="Chưa có dữ liệu lương\nVui lòng thêm thông tin lương mới",
                         font=("Arial", 11), text_color="#999").pack(pady=40)
        else:
            for idx, salary in enumerate(self.salary_data):
                self.create_salary_row(idx, salary)

    def export_data(self):
        if not self.salary_data:
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu để xuất!")
            return
        messagebox.showinfo("Thông báo", "Chức năng xuất dữ liệu đang phát triển!")