import customtkinter as ctk
from tkinter import ttk, messagebox
from src.Controller.NganHangController import NganHangController


class NganHangPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="white")

        self.controller = NganHangController()
        self.selected_id = None
        self.current_data_list = []

        # --- DỮ LIỆU NGÂN HÀNG VIỆT NAM (MẪU) ---
        # Key: Mã hiển thị trong Combobox
        # Value: Tên đầy đủ để điền vào ô Tên Ngân Hàng
        self.vn_banks = {
            "VCB": "Ngân hàng TMCP Ngoại thương Việt Nam (Vietcombank)",
            "MB": "Ngân hàng TMCP Quân đội (MB Bank)",
            "TCB": "Ngân hàng TMCP Kỹ thương Việt Nam (Techcombank)",
            "BIDV": "Ngân hàng TMCP Đầu tư và Phát triển Việt Nam",
            "CTG": "Ngân hàng TMCP Công Thương Việt Nam (VietinBank)",
            "ACB": "Ngân hàng TMCP Á Châu (ACB)",
            "VPB": "Ngân hàng TMCP Việt Nam Thịnh Vượng (VPBank)",
            "TPB": "Ngân hàng TMCP Tiên Phong (TPBank)",
            "STB": "Ngân hàng TMCP Sài Gòn Thương Tín (Sacombank)",
            "HDB": "Ngân hàng TMCP Phát triển TP.HCM (HDBank)",
            "VIB": "Ngân hàng TMCP Quốc tế Việt Nam (VIB)",
            "SSB": "Ngân hàng TMCP Đông Nam Á (SeABank)",
            "MSB": "Ngân hàng TMCP Hàng Hải Việt Nam (MSB)",
            "OCB": "Ngân hàng TMCP Phương Đông (OCB)",
            "LPB": "Ngân hàng TMCP Bưu điện Liên Việt (LPBank)",
            "SHB": "Ngân hàng TMCP Sài Gòn - Hà Nội (SHB)",
            "NAB": "Ngân hàng TMCP Nam Á (Nam A Bank)",
            "EIB": "Ngân hàng TMCP Xuất Nhập khẩu Việt Nam (Eximbank)",
            "BAB": "Ngân hàng TMCP Bắc Á (Bac A Bank)",
            "VIETCAPITAL": "Ngân hàng TMCP Bản Việt (BVBank)"
        }
        # Lấy danh sách mã để đưa vào Combobox
        self.bank_codes = list(self.vn_banks.keys())

        self.tao_main_content()
        self.load_table_data()

    def tao_main_content(self):
        container = ctk.CTkFrame(self, fg_color="white")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(container, text="Quản lý Tài khoản Ngân hàng", font=("Arial", 18, "bold"), text_color="#333").pack(
            anchor="w", pady=(0, 20))

        # ====================== 1. CONTROL PANEL ======================
        action_bar = ctk.CTkFrame(container, fg_color="white")
        action_bar.pack(fill="x", pady=(0, 20))

        # Buttons
        btn_frame = ctk.CTkFrame(action_bar, fg_color="white")
        btn_frame.pack(side="left")
        self.create_btn(btn_frame, "Thêm", "#4CAF50", "#45a049", self.them)
        self.create_btn(btn_frame, "Sửa", "#2196F3", "#0b7dda", self.sua)
        self.create_btn(btn_frame, "Ẩn/Hiện", "#FF9800", "#F57C00", self.an_hien)
        self.create_btn(btn_frame, "Làm mới Form", "#9E9E9E", "#757575", self.lam_moi)

        # Search (Real-time)
        search_frame = ctk.CTkFrame(action_bar, fg_color="white")
        search_frame.pack(side="right")

        self.search_entry = ctk.CTkEntry(search_frame, width=300, height=35,
                                         placeholder_text="Gõ để tìm kiếm (Mã, Tên, STK)...", border_width=1,
                                         border_color="#ccc")
        self.search_entry.pack(side="left", padx=(0, 5))

        # BINDING SỰ KIỆN: Khi nhả phím (KeyRelease) -> Gọi hàm tìm kiếm ngay
        self.search_entry.bind("<KeyRelease>", self.on_search_change)

        # ====================== 2. FORM NHẬP LIỆU (Cải tiến) ======================
        form_wrapper = ctk.CTkFrame(container, fg_color="#f5f5f5", border_width=1, border_color="#ccc")
        form_wrapper.pack(fill="x", pady=(0, 20))

        form_inner = ctk.CTkFrame(form_wrapper, fg_color="#f5f5f5")
        form_inner.pack(fill="x", padx=20, pady=20)

        # --- Hàng 1: Chọn Ngân hàng & Tên Ngân hàng (Tự động) ---
        row1 = ctk.CTkFrame(form_inner, fg_color="#f5f5f5")
        row1.pack(fill="x", pady=(0, 15))

        # Cột Mã Ngân hàng (Combobox)
        f1 = ctk.CTkFrame(row1, fg_color="#f5f5f5")
        f1.pack(side="left", padx=(0, 20), fill="x")
        ctk.CTkLabel(f1, text="Chọn Ngân hàng", font=("Arial", 11, "bold"), text_color="#555").pack(anchor="w",
                                                                                                    pady=(0, 5))

        self.combo_ma = ctk.CTkComboBox(
            f1,
            values=self.bank_codes,
            width=200, height=32,
            state="readonly",  # Chỉ cho chọn, không cho gõ linh tinh
            command=self.on_bank_select_change  # Sự kiện khi chọn ngân hàng
        )
        self.combo_ma.set("Chọn ngân hàng")
        self.combo_ma.pack(fill="x")

        # Cột Tên Ngân hàng (Entry - Readonly)
        self.entry_ten = self.create_input(row1, "Tên ngân hàng ", 350)
        self.entry_ten.configure(state="disabled")  # Mặc định khóa không cho sửa

        # --- Hàng 2: Số TK & Chủ TK (Nhập tay) ---
        row2 = ctk.CTkFrame(form_inner, fg_color="#f5f5f5")
        row2.pack(fill="x")
        self.entry_stk = self.create_input(row2, "Số tài khoản", 200)
        self.entry_chu = self.create_input(row2, "Tên tài khoản ", 350)

        # ====================== 3. BẢNG DỮ LIỆU ======================
        ctk.CTkLabel(container, text="Danh sách Ngân hàng", font=("Arial", 14, "bold"), text_color="#333").pack(
            anchor="w", pady=(0, 10))

        table_frame = ctk.CTkFrame(container, fg_color="white", border_width=1, border_color="#ccc")
        table_frame.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground="black", rowheight=35, fieldbackground="white",
                        font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#f0f0f0", foreground="#333")
        style.map("Treeview", background=[("selected", "#2196F3")])

        columns = ("stt", "ma", "ten", "stk", "chu", "trangthai")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)

        self.tree.heading("stt", text="STT")
        self.tree.heading("ma", text="Mã NH")
        self.tree.heading("ten", text="Tên Ngân Hàng")
        self.tree.heading("stk", text="Số Tài Khoản")
        self.tree.heading("chu", text="Tên Tài Khoản")
        self.tree.heading("trangthai", text="Trạng Thái")

        self.tree.column("stt", width=50, anchor="center")
        self.tree.column("ma", width=100, anchor="center")
        self.tree.column("ten", width=250, anchor="w")
        self.tree.column("stk", width=150, anchor="center")
        self.tree.column("chu", width=200, anchor="w")
        self.tree.column("trangthai", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=2, pady=2)

        self.tree.bind("<<TreeviewSelect>>", self.on_select_row)

    # ====================== HELPERS UI ======================
    def create_btn(self, parent, text, color, hover, cmd, width=80):
        ctk.CTkButton(parent, text=text, fg_color=color, hover_color=hover, text_color="white", width=width, height=35,
                      corner_radius=6, font=("Arial", 11, "bold"), command=cmd).pack(side="left", padx=5)

    def create_input(self, parent, label, width):
        f = ctk.CTkFrame(parent, fg_color="#f5f5f5")
        f.pack(side="left", padx=(0, 20), fill="x", expand=True)
        ctk.CTkLabel(f, text=label, font=("Arial", 11, "bold"), text_color="#555").pack(anchor="w", pady=(0, 5))
        e = ctk.CTkEntry(f, width=width, height=32, border_color="#ccc")
        e.pack(fill="x")
        return e

    # ====================== LOGIC XỬ LÝ SỰ KIỆN ======================

    def on_bank_select_change(self, choice):
        """Khi chọn Combobox -> Tự động điền tên ngân hàng"""
        ten_day_du = self.vn_banks.get(choice, "")

        # Mở khóa ô Entry -> Điền -> Khóa lại
        self.entry_ten.configure(state="normal")
        self.entry_ten.delete(0, "end")
        self.entry_ten.insert(0, ten_day_du)
        self.entry_ten.configure(state="disabled")

    def on_search_change(self, event):
        """Sự kiện tìm kiếm Real-time (gõ đến đâu lọc đến đó)"""
        keyword = self.search_entry.get()
        # Gọi controller tìm kiếm
        results = self.controller.tim_kiem_ngan_hang(keyword)
        # Load lại bảng ngay lập tức
        self.load_table_data(data=results)

    def load_table_data(self, data=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if data is None:
            self.current_data_list = self.controller.lay_danh_sach_ngan_hang()
        else:
            self.current_data_list = data

        for idx, item in enumerate(self.current_data_list):
            status_text = "Hiện" if item["isActive"] else "Ẩn"
            self.tree.insert("", "end", values=(
                idx + 1, item["maNganHang"], item["tenNganHang"], item["soTaiKhoan"], item["tenTaiKhoan"], status_text
            ))

    def on_select_row(self, event):
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            if index < len(self.current_data_list):
                data = self.current_data_list[index]
                self.selected_id = data["idNganHang"]

                # 1. Set Combobox
                self.combo_ma.set(data["maNganHang"])

                # 2. Set Tên (Cần mở khóa trước)
                self.entry_ten.configure(state="normal")
                self.entry_ten.delete(0, "end")
                self.entry_ten.insert(0, data["tenNganHang"])
                self.entry_ten.configure(state="disabled")

                # 3. Set STK, Tên TK
                self.entry_stk.delete(0, "end");
                self.entry_stk.insert(0, data["soTaiKhoan"])
                self.entry_chu.delete(0, "end");
                self.entry_chu.insert(0, data["tenTaiKhoan"])

    def them(self):
        ma = self.combo_ma.get()
        # Cần lấy tên từ entry_ten (dù đang disabled vẫn get() được)
        ten = self.entry_ten.get()
        stk = self.entry_stk.get()
        chu = self.entry_chu.get()

        if ma == "Chọn ngân hàng":
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn ngân hàng!")
            return

        success, msg = self.controller.them_ngan_hang(ma, ten, stk, chu)
        if success:
            messagebox.showinfo("Thành công", msg)
            self.lam_moi()
            self.load_table_data()
        else:
            messagebox.showerror("Lỗi", msg)

    def sua(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ngân hàng cần sửa!")
            return

        ma = self.combo_ma.get()
        ten = self.entry_ten.get()
        stk = self.entry_stk.get()
        chu = self.entry_chu.get()

        success, msg = self.controller.sua_ngan_hang(self.selected_id, ma, ten, stk, chu)
        if success:
            messagebox.showinfo("Thành công", msg)
            self.lam_moi()
            self.load_table_data()
        else:
            messagebox.showerror("Lỗi", msg)

    def an_hien(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn dòng để đổi trạng thái")
            return

        success, msg = self.controller.doi_trang_thai(self.selected_id)
        if success:
            messagebox.showinfo("Thành công", msg)
            self.lam_moi()
            self.load_table_data()
        else:
            messagebox.showerror("Lỗi", msg)

    def lam_moi(self):
        """Reset form"""
        self.selected_id = None
        self.combo_ma.set("Chọn ngân hàng")

        self.entry_ten.configure(state="normal")
        self.entry_ten.delete(0, "end")
        self.entry_ten.configure(state="disabled")

        self.entry_stk.delete(0, "end")
        self.entry_chu.delete(0, "end")

        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())