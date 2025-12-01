import customtkinter as ctk
from tkinter import ttk, messagebox
from src.Controller.NhanVienController import NhanVienController


class NhanVienPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="white")

        self.controller = NhanVienController()

        self.selected_id = None
        self.current_list = []

        self.chucvu_map = {}
        self.chucvu_names = []

        # --- [NEW] TẠO MAP PHÂN QUYỀN ---
        # Dùng để chuyển đổi khi Hiển thị (DB -> View)
        self.role_map_view = {
            "nhanVien": "Nhân viên",
            "admin": "Quản trị viên"
        }
        # Dùng để chuyển đổi khi Lưu (View -> DB)
        self.role_map_db = {
            "Nhân viên": "nhanVien",
            "Quản trị viên": "admin"
        }

        self.load_chuc_vu_data()
        self.tao_main_content()
        self.load_table_data()

    def load_chuc_vu_data(self):
        data = self.controller.get_ds_chuc_vu()
        self.chucvu_map = {item['tenChucVu']: item['idChucVu'] for item in data}
        self.chucvu_names = list(self.chucvu_map.keys())

        if hasattr(self, 'cb_chucvu'):
            self.cb_chucvu.configure(values=self.chucvu_names)

    def tao_main_content(self):
        container = ctk.CTkFrame(self, fg_color="white")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(container, text="Quản lý Nhân sự", font=("Arial", 18, "bold"), text_color="#333").pack(anchor="w",
                                                                                                            pady=(
                                                                                                            0, 20))

        # === CONTROL PANEL ===
        action_bar = ctk.CTkFrame(container, fg_color="white")
        action_bar.pack(fill="x", pady=(0, 20))

        btn_frame = ctk.CTkFrame(action_bar, fg_color="white")
        btn_frame.pack(side="left")

        self.create_btn(btn_frame, "Thêm NV", "#4CAF50", "#45a049", self.them)
        self.create_btn(btn_frame, "Sửa NV", "#2196F3", "#0b7dda", self.sua)
        self.create_btn(btn_frame, "Đổi trạng thái", "#FF9800", "#F57C00", self.doi_trang_thai, width=120)
        self.create_btn(btn_frame, "Làm mới", "#9E9E9E", "#757575", self.lam_moi)

        ctk.CTkButton(btn_frame, text="Quản lý Chức vụ", fg_color="#673AB7", hover_color="#512DA8", width=120,
                      height=35, command=self.open_chucvu_popup).pack(side="left", padx=5)

        # Search
        search_frame = ctk.CTkFrame(action_bar, fg_color="white")
        search_frame.pack(side="right")
        self.search_entry = ctk.CTkEntry(search_frame, width=250, placeholder_text="Tên, Email, SĐT...")
        self.search_entry.pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="Tìm", width=60, command=self.tim_kiem).pack(side="left")

        # === FORM ===
        form_wrapper = ctk.CTkFrame(container, fg_color="#f5f5f5")
        form_wrapper.pack(fill="x", pady=(0, 20))
        form_inner = ctk.CTkFrame(form_wrapper, fg_color="#f5f5f5")
        form_inner.pack(fill="x", padx=20, pady=20)

        # Hàng 1
        r1 = ctk.CTkFrame(form_inner, fg_color="#f5f5f5")
        r1.pack(fill="x", pady=5)
        self.entry_ten = self.create_input(r1, "Họ tên", 250)
        self.entry_email = self.create_input(r1, "Email", 250)
        self.entry_sdt = self.create_input(r1, "Số điện thoại", 150)

        # Hàng 2
        r2 = ctk.CTkFrame(form_inner, fg_color="#f5f5f5")
        r2.pack(fill="x", pady=5)

        # [UPDATE] Combobox Phân quyền hiển thị Tiếng Việt
        f_quyen = ctk.CTkFrame(r2, fg_color="#f5f5f5")
        f_quyen.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(f_quyen, text="Phân quyền", font=("Arial", 11, "bold")).pack(anchor="w")

        # Sử dụng Keys của map để hiển thị ("Nhân viên", "Quản trị viên")
        display_roles = list(self.role_map_db.keys())
        self.cb_quyen = ctk.CTkComboBox(f_quyen, values=display_roles, width=150, state="readonly")
        self.cb_quyen.set("Nhân viên")  # Default text
        self.cb_quyen.pack()

        # Combobox Chức vụ
        f_cv = ctk.CTkFrame(r2, fg_color="#f5f5f5")
        f_cv.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(f_cv, text="Chức vụ", font=("Arial", 11, "bold")).pack(anchor="w")
        self.cb_chucvu = ctk.CTkComboBox(f_cv, values=self.ncc_names if hasattr(self, 'ncc_names') else [], width=200,
                                         state="readonly")
        self.cb_chucvu.set("Chọn chức vụ")
        self.cb_chucvu.pack()

        # === TABLE ===
        table_frame = ctk.CTkFrame(container, fg_color="white")
        table_frame.pack(fill="both", expand=True)

        columns = ("stt", "ten", "sdt", "email", "quyen", "ngaytao", "ngaycapnhat", "chucvu", "trangthai")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)

        self.tree.heading("stt", text="STT")
        self.tree.heading("ten", text="Họ tên")
        self.tree.heading("sdt", text="SĐT")
        self.tree.heading("email", text="Email")
        self.tree.heading("quyen", text="Phân quyền")
        self.tree.heading("ngaytao", text="Ngày tạo")
        self.tree.heading("ngaycapnhat", text="Ngày cập nhật")
        self.tree.heading("chucvu", text="Chức vụ")
        self.tree.heading("trangthai", text="Trạng thái")

        self.tree.column("stt", width=40, anchor="center")
        self.tree.column("ten", width=150)
        self.tree.column("sdt", width=100, anchor="center")
        self.tree.column("email", width=150)
        self.tree.column("quyen", width=100, anchor="center")  # Tăng width
        self.tree.column("ngaytao", width=120, anchor="center")
        self.tree.column("ngaycapnhat", width=120, anchor="center")
        self.tree.column("chucvu", width=100, anchor="center")
        self.tree.column("trangthai", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_select_row)

    # ====================== HELPERS ======================
    def create_input(self, parent, label, width):
        f = ctk.CTkFrame(parent, fg_color="#f5f5f5")
        f.pack(side="left", padx=(0, 20), fill="x", expand=True)
        ctk.CTkLabel(f, text=label, font=("Arial", 11, "bold")).pack(anchor="w")
        e = ctk.CTkEntry(f, width=width)
        e.pack()
        return e

    def create_btn(self, parent, text, color, hover, cmd, width=80):
        ctk.CTkButton(parent, text=text, fg_color=color, hover_color=hover, width=width, command=cmd).pack(side="left",
                                                                                                           padx=5)

    # ====================== LOGIC MAIN ======================
    def load_table_data(self, data=None):
        for item in self.tree.get_children(): self.tree.delete(item)

        if data is None:
            self.current_list = self.controller.get_list()
        else:
            self.current_list = data

        self.load_chuc_vu_data()

        for idx, row in enumerate(self.current_list):
            tt = "Đang làm" if row['trangThaiLamViec'] == 'DangLamViec' else "Đã nghỉ"

            # [UPDATE] Hiển thị phân quyền bằng Tiếng Việt
            # Lấy giá trị từ DB (vd: 'nhanVien'), map sang 'Nhân viên'
            quyen_hien_thi = self.role_map_view.get(row['phanQuyen'], row['phanQuyen'])

            self.tree.insert("", "end", values=(
                idx + 1,
                row['hoTen'],
                row['soDienThoai'],
                row['email'],
                quyen_hien_thi,  # Dùng biến đã map
                row['ngayTao'],
                row['ngayCapNhat'] if row['ngayCapNhat'] else "",
                row['tenChucVu'],
                tt
            ))

    def on_select_row(self, event):
        sel = self.tree.selection()
        if sel:
            idx = self.tree.index(sel[0])
            if idx < len(self.current_list):
                data = self.current_list[idx]
                self.selected_id = data['idNhanVien']

                self.entry_ten.delete(0, "end");
                self.entry_ten.insert(0, data['hoTen'])
                self.entry_email.delete(0, "end");
                self.entry_email.insert(0, data['email'])

                self.entry_sdt.delete(0, "end")
                if data['soDienThoai']: self.entry_sdt.insert(0, data['soDienThoai'])

                # [UPDATE] Khi chọn dòng, set lại Combobox bằng Tiếng Việt
                # data['phanQuyen'] là 'nhanVien' -> 'Nhân viên'
                quyen_text = self.role_map_view.get(data['phanQuyen'], "Nhân viên")
                self.cb_quyen.set(quyen_text)

                if data['tenChucVu'] in self.chucvu_names:
                    self.cb_chucvu.set(data['tenChucVu'])

    def them(self):
        ten = self.entry_ten.get()
        email = self.entry_email.get()
        sdt = self.entry_sdt.get()

        # [UPDATE] Lấy giá trị Tiếng Việt từ Combobox -> Chuyển thành Code DB
        quyen_text = self.cb_quyen.get()  # VD: "Quản trị viên"
        quyen_db = self.role_map_db.get(quyen_text, "nhanVien")  # -> "admin"

        ten_cv = self.cb_chucvu.get()
        id_cv = self.chucvu_map.get(ten_cv)

        success, msg = self.controller.add_nhan_vien(ten, email, sdt, quyen_db, id_cv)
        if success:
            messagebox.showinfo("OK", msg)
            self.lam_moi()
        else:
            messagebox.showerror("Lỗi", msg)

    def sua(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Chọn nhân viên cần sửa!")
            return

        ten = self.entry_ten.get()
        email = self.entry_email.get()
        sdt = self.entry_sdt.get()

        # [UPDATE] Chuyển đổi quyền trước khi gửi xuống Controller
        quyen_text = self.cb_quyen.get()
        quyen_db = self.role_map_db.get(quyen_text, "nhanVien")

        id_cv = self.chucvu_map.get(self.cb_chucvu.get())

        success, msg = self.controller.update_nhan_vien(self.selected_id, ten, email, sdt, quyen_db, id_cv)
        if success:
            messagebox.showinfo("OK", msg)
            self.lam_moi()
        else:
            messagebox.showerror("Lỗi", msg)

    def doi_trang_thai(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Chọn nhân viên!")
            return
        if self.controller.doi_trang_thai(self.selected_id):
            messagebox.showinfo("OK", "Đã đổi trạng thái!")
            self.lam_moi()
        else:
            messagebox.showerror("Lỗi", "Không thể đổi trạng thái!")

    def lam_moi(self):
        self.selected_id = None
        self.entry_ten.delete(0, "end")
        self.entry_email.delete(0, "end")
        self.entry_sdt.delete(0, "end")
        self.cb_quyen.set("Nhân viên")  # Reset về tiếng Việt
        self.cb_chucvu.set("Chọn chức vụ")
        self.load_table_data()

    def tim_kiem(self):
        kw = self.search_entry.get()
        self.load_table_data(self.controller.search_nhan_vien(kw))

    def xuat(self):
        messagebox.showinfo("TB", "Tính năng đang phát triển")

    # ================= POPUP QUẢN LÝ CHỨC VỤ =================
    def open_chucvu_popup(self):
        top = ctk.CTkToplevel(self)
        top.title("Quản lý Chức vụ & Lương")
        top.geometry("500x400")
        top.attributes("-topmost", True)

        frm = ctk.CTkFrame(top, fg_color="#eee")
        frm.pack(fill="x", padx=10, pady=10)

        e_ten = ctk.CTkEntry(frm, placeholder_text="Tên chức vụ")
        e_ten.pack(side="left", padx=5)
        e_luong = ctk.CTkEntry(frm, placeholder_text="Lương cơ bản")
        e_luong.pack(side="left", padx=5)

        tree_frame = ctk.CTkFrame(top)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        cols = ("id", "ten", "luong")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=8)
        tree.heading("id", text="ID")
        tree.heading("ten", text="Tên chức vụ")
        tree.heading("luong", text="Lương")
        tree.pack(fill="both", expand=True)

        def reload_cv_table():
            for i in tree.get_children(): tree.delete(i)
            data = self.controller.get_ds_chuc_vu()
            for row in data:
                luong_fmt = "{:,.0f}".format(row['luongCoBan'])
                tree.insert("", "end", values=(row['idChucVu'], row['tenChucVu'], luong_fmt))
            self.load_chuc_vu_data()

        reload_cv_table()

        selected_cv_id = [None]

        def on_click_cv(event):
            sel = tree.selection()
            if sel:
                val = tree.item(sel[0], "values")
                selected_cv_id[0] = val[0]
                e_ten.delete(0, "end");
                e_ten.insert(0, val[1])
                raw_luong = val[2].replace(",", "")
                e_luong.delete(0, "end");
                e_luong.insert(0, raw_luong)

        tree.bind("<<TreeviewSelect>>", on_click_cv)

        def action_add():
            t = e_ten.get()
            l = e_luong.get()
            ok, msg = self.controller.them_chuc_vu(t, l)
            if ok:
                reload_cv_table()
                e_ten.delete(0, "end");
                e_luong.delete(0, "end")
            else:
                messagebox.showerror("Lỗi", msg, parent=top)

        def action_edit():
            if not selected_cv_id[0]: return
            t = e_ten.get()
            l = e_luong.get()
            ok, msg = self.controller.sua_chuc_vu(selected_cv_id[0], t, l)
            if ok:
                reload_cv_table()
                messagebox.showinfo("OK", msg, parent=top)
            else:
                messagebox.showerror("Lỗi", msg, parent=top)

        btn_box = ctk.CTkFrame(top, fg_color="transparent")
        btn_box.pack(pady=10)
        ctk.CTkButton(btn_box, text="Thêm mới", fg_color="green", command=action_add).pack(side="left", padx=5)
        ctk.CTkButton(btn_box, text="Cập nhật", fg_color="blue", command=action_edit).pack(side="left", padx=5)