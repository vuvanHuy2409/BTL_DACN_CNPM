import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
# Import Controller
from src.Controller.KhachHangController import KhachHangController


class KhachHangPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="white")

        # === KHỞI TẠO CONTROLLER ===
        self.controller = KhachHangController()

        # Biến lưu ID khách hàng đang chọn (để sửa)
        self.selected_id = None

        # Biến lưu danh sách dữ liệu gốc
        self.current_list = []

        self.tao_main_content()
        self.load_data_table()

    def tao_main_content(self):
        # Container chính
        container = ctk.CTkFrame(self, fg_color="white")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Tiêu đề
        ctk.CTkLabel(container, text="Quản lý Khách hàng", font=("Arial", 18, "bold"), text_color="#333").pack(
            anchor="w", pady=(0, 20))

        # ====================== 1. CONTROL PANEL ======================
        action_bar = ctk.CTkFrame(container, fg_color="white")
        action_bar.pack(fill="x", pady=(0, 20))

        # --- Buttons ---
        btn_frame = ctk.CTkFrame(action_bar, fg_color="white")
        btn_frame.pack(side="left")

        self.create_btn(btn_frame, "Thêm", "#4CAF50", "#45a049", self.on_add)
        self.create_btn(btn_frame, "Sửa", "#2196F3", "#0b7dda", self.on_update)
        self.create_btn(btn_frame, "Làm mới", "#9E9E9E", "#757575", self.clear_form)

        # --- Search ---
        search_frame = ctk.CTkFrame(action_bar, fg_color="white")
        search_frame.pack(side="right")

        self.search_entry = ctk.CTkEntry(search_frame, width=250, height=35, placeholder_text="Tên hoặc SĐT...",
                                         border_width=1, border_color="#ccc")
        self.search_entry.pack(side="left", padx=(0, 5))

        ctk.CTkButton(search_frame, text="Tìm", fg_color="#2196F3", hover_color="#0b7dda", width=60, height=35,
                      font=("Arial", 11, "bold"), command=self.on_search).pack(side="left")

        # ====================== 2. FORM SECTION ======================
        form_wrapper = ctk.CTkFrame(container, fg_color="#f5f5f5", border_width=1, border_color="#ccc")
        form_wrapper.pack(fill="x", pady=(0, 20))

        form_inner = ctk.CTkFrame(form_wrapper, fg_color="#f5f5f5")
        form_inner.pack(fill="x", padx=20, pady=20)

        # --- Hàng 1: Inputs ---
        row1 = ctk.CTkFrame(form_inner, fg_color="#f5f5f5")
        row1.pack(fill="x", pady=(0, 15))

        self.entry_ten = self.create_input(row1, "Tên khách hàng", 300)
        self.entry_sdt = self.create_input(row1, "Số điện thoại", 200)
        self.entry_diem = self.create_input(row1, "Điểm tích lũy", 150)
        self.entry_diem.insert(0, "0")

        # --- Hàng 2: Ngày sinh ---
        row2 = ctk.CTkFrame(form_inner, fg_color="#f5f5f5")
        row2.pack(fill="x")

        # -- Ngày sinh (Comboboxes) --
        dob_frame = ctk.CTkFrame(row2, fg_color="#f5f5f5")
        dob_frame.pack(side="left", anchor="n")

        ctk.CTkLabel(dob_frame, text="Ngày sinh", font=("Arial", 11, "bold"), text_color="#555").pack(anchor="w",
                                                                                                      pady=(0, 5))
        dob_inner = ctk.CTkFrame(dob_frame, fg_color="#f5f5f5")
        dob_inner.pack()

        self.cb_day = ctk.CTkComboBox(dob_inner, values=[str(i) for i in range(1, 32)], width=70)
        self.cb_month = ctk.CTkComboBox(dob_inner, values=[str(i) for i in range(1, 13)], width=70)
        self.cb_year = ctk.CTkComboBox(dob_inner, values=[str(i) for i in range(1990, datetime.now().year + 1)],
                                       width=90)

        self.cb_day.set("1");
        self.cb_month.set("1");
        self.cb_year.set("2000")
        self.cb_day.pack(side="left", padx=(0, 5))
        self.cb_month.pack(side="left", padx=(0, 5))
        self.cb_year.pack(side="left")

        # ====================== 3. BẢNG DỮ LIỆU (TREEVIEW) ======================
        ctk.CTkLabel(container, text="Danh sách khách hàng", font=("Arial", 14, "bold"), text_color="#333").pack(
            anchor="w", pady=(0, 10))

        table_frame = ctk.CTkFrame(container, fg_color="white", border_width=1, border_color="#ccc")
        table_frame.pack(fill="both", expand=True)

        # Style Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground="black", rowheight=30, fieldbackground="white",
                        font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#f0f0f0", foreground="#333")
        style.map("Treeview", background=[("selected", "#2196F3")])

        columns = ("stt", "ten", "sdt", "ns", "diem")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)

        self.tree.heading("stt", text="STT")
        self.tree.heading("ten", text="Tên khách hàng")
        self.tree.heading("sdt", text="Số điện thoại")
        self.tree.heading("ns", text="Ngày sinh")
        self.tree.heading("diem", text="Điểm")

        self.tree.column("stt", width=50, anchor="center")
        self.tree.column("ten", width=250, anchor="w")
        self.tree.column("sdt", width=120, anchor="center")
        self.tree.column("ns", width=120, anchor="center")
        self.tree.column("diem", width=80, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=2, pady=2)

        self.tree.bind("<<TreeviewSelect>>", self.on_select_row)

    # ====================== HELPERS ======================
    def create_btn(self, parent, text, color, hover, cmd, width=80):
        ctk.CTkButton(parent, text=text, fg_color=color, hover_color=hover, text_color="white",
                      width=width, height=35, corner_radius=6, font=("Arial", 11, "bold"),
                      command=cmd).pack(side="left", padx=5)

    def create_input(self, parent, label, width):
        f = ctk.CTkFrame(parent, fg_color="#f5f5f5")
        f.pack(side="left", padx=(0, 20), fill="x", expand=True)
        ctk.CTkLabel(f, text=label, font=("Arial", 11, "bold"), text_color="#555").pack(anchor="w", pady=(0, 5))
        e = ctk.CTkEntry(f, width=width, height=32, border_color="#ccc")
        e.pack(fill="x")
        return e

    # ====================== LOGIC ======================
    def load_data_table(self, data=None):
        # 1. Xóa dữ liệu cũ trên bảng
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 2. Lấy dữ liệu mới
        if data is None:
            self.current_list = self.controller.lay_danh_sach_khach_hang()
        else:
            self.current_list = data  # Dữ liệu từ tìm kiếm

        if not self.current_list: return

        # 3. Đổ dữ liệu vào bảng
        for idx, row_data in enumerate(self.current_list):

            # Xử lý Ngày sinh
            ns_str = ""
            if row_data['ngaySinh']:
                ns_str = row_data['ngaySinh'].strftime("%d/%m/%Y") if hasattr(row_data['ngaySinh'],
                                                                              'strftime') else str(row_data['ngaySinh'])

            # [CẬP NHẬT] Xử lý Số điện thoại: Nếu None hoặc Rỗng -> "Trống"
            sdt_display = row_data['soDienThoai']
            if not sdt_display or sdt_display.strip() == "":
                sdt_display = "Trống"

            values = (idx + 1, row_data['hoTen'], sdt_display, ns_str, row_data['diemTichLuy'])
            self.tree.insert("", "end", values=values)

    def on_select_row(self, event):
        selected = self.tree.selection()
        if selected:
            # Lấy index của dòng đang chọn
            index = self.tree.index(selected[0])

            # Truy xuất vào danh sách gốc (self.current_list) để lấy dữ liệu thực
            # (Vì trên bảng hiển thị "Trống" nhưng ta cần lấy None/Rỗng để xử lý logic)
            if index < len(self.current_list):
                data = self.current_list[index]

                self.selected_id = data['idKhachHang']

                # Đổ Tên
                self.entry_ten.delete(0, "end");
                self.entry_ten.insert(0, data['hoTen'])

                # Đổ SĐT (Lấy từ data gốc, nên nếu là None thì ô nhập sẽ trống, không hiện chữ "Trống")
                self.entry_sdt.delete(0, "end")
                if data['soDienThoai']:
                    self.entry_sdt.insert(0, data['soDienThoai'])

                # Đổ Ngày sinh
                if data['ngaySinh']:
                    if hasattr(data['ngaySinh'], 'day'):
                        self.cb_day.set(str(data['ngaySinh'].day))
                        self.cb_month.set(str(data['ngaySinh'].month))
                        self.cb_year.set(str(data['ngaySinh'].year))
                    else:
                        try:
                            y, m, d = str(data['ngaySinh']).split('-')
                            self.cb_day.set(str(int(d)))
                            self.cb_month.set(str(int(m)))
                            self.cb_year.set(y)
                        except:
                            pass

                # Đổ Điểm
                self.entry_diem.delete(0, "end");
                self.entry_diem.insert(0, data['diemTichLuy'])

    def clear_form(self):
        self.selected_id = None
        self.entry_ten.delete(0, "end")
        self.entry_sdt.delete(0, "end")
        self.cb_day.set("1");
        self.cb_month.set("1");
        self.cb_year.set("2000")
        self.entry_diem.delete(0, "end");
        self.entry_diem.insert(0, "0")

        self.load_data_table()
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

    # === CRUD ACTIONS ===
    def on_add(self):
        ten = self.entry_ten.get()
        sdt = self.entry_sdt.get()
        ngaysinh = f"{self.cb_day.get()}/{self.cb_month.get()}/{self.cb_year.get()}"

        success, msg = self.controller.them_khach_hang(ten, sdt, ngaysinh)
        if success:
            messagebox.showinfo("Thành công", msg)
            self.clear_form()
        else:
            messagebox.showerror("Lỗi", msg)

    def on_update(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn khách hàng để sửa")
            return

        ten = self.entry_ten.get()
        sdt = self.entry_sdt.get()
        ngaysinh = f"{self.cb_day.get()}/{self.cb_month.get()}/{self.cb_year.get()}"
        try:
            diem = int(self.entry_diem.get())
        except:
            diem = 0

        success, msg = self.controller.sua_khach_hang(self.selected_id, ten, sdt, ngaysinh, diem)
        if success:
            messagebox.showinfo("Thành công", msg)
            self.clear_form()
        else:
            messagebox.showerror("Lỗi", msg)

    def on_search(self):
        keyword = self.search_entry.get()
        if not keyword:
            self.load_data_table()
        else:
            results = self.controller.tim_kiem_khach_hang(keyword)
            self.load_data_table(results)