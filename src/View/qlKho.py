import customtkinter as ctk
from tkinter import ttk, messagebox
from src.Controller.KhoController import KhoController


class KhoPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="white")

        self.controller = KhoController()
        self.selected_id = None
        self.current_list = []

        # Map tên NCC -> ID
        self.ncc_map = {}
        self.ncc_names = []

        # Load danh sách NCC
        self.load_ncc_combobox_data()

        self.tao_main_content()
        self.load_table_data()

    def load_ncc_combobox_data(self):
        data = self.controller.get_ncc_list()
        self.ncc_map = {item['tenNhaCungCap']: item['idNhaCungCap'] for item in data}
        self.ncc_names = list(self.ncc_map.keys())

    def tao_main_content(self):
        container = ctk.CTkFrame(self, fg_color="white")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(container, text="Quản lý Kho Nguyên Liệu", font=("Arial", 18, "bold"), text_color="#333").pack(
            anchor="w", pady=(0, 20))


        # === CONTROL PANEL ===
        action_bar = ctk.CTkFrame(container, fg_color="white")
        action_bar.pack(fill="x", pady=(0, 20))

        btn_frame = ctk.CTkFrame(action_bar, fg_color="white")
        btn_frame.pack(side="left")
        self.create_btn(btn_frame, "Thêm", "#4CAF50", "#45a049", self.them)
        self.create_btn(btn_frame, "Sửa", "#2196F3", "#0b7dda", self.sua)
        self.create_btn(btn_frame, "Ẩn/Hiện", "#FF9800", "#F57C00", self.an_hien)
        self.create_btn(btn_frame, "Làm mới", "#9E9E9E", "#757575", self.lam_moi)

        search_frame = ctk.CTkFrame(action_bar, fg_color="white")
        search_frame.pack(side="right")
        self.search_entry = ctk.CTkEntry(search_frame, width=250, placeholder_text="Tên nguyên liệu...")
        self.search_entry.pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="Tìm", width=60, command=self.tim_kiem).pack(side="left")

        # === FORM ===
        form_frame = ctk.CTkFrame(container, fg_color="#f5f5f5")
        form_frame.pack(fill="x", pady=(0, 20))
        form_inner = ctk.CTkFrame(form_frame, fg_color="#f5f5f5")
        form_inner.pack(padx=20, pady=20, fill="x")

        # Hàng 1
        r1 = ctk.CTkFrame(form_inner, fg_color="#f5f5f5")
        r1.pack(fill="x", pady=5)
        self.entry_ten = self.create_input(r1, "Tên nguyên liệu", 250)
        self.entry_gia = self.create_input(r1, "Giá nhập (VNĐ)", 150)

        # Hàng 2
        r2 = ctk.CTkFrame(form_inner, fg_color="#f5f5f5")
        r2.pack(fill="x", pady=5)
        self.entry_sl = self.create_input(r2, "Số lượng tồn", 150)
        self.entry_dvt = self.create_input(r2, "Đơn vị tính", 100)

        # Combobox Nhà Cung Cấp
        f_cb = ctk.CTkFrame(r2, fg_color="#f5f5f5")
        f_cb.pack(side="left", padx=20, fill="x", expand=True)
        ctk.CTkLabel(f_cb, text="Nhà cung cấp", font=("Arial", 11, "bold")).pack(anchor="w")
        self.cb_ncc = ctk.CTkComboBox(f_cb, values=self.ncc_names, width=250, state="readonly")
        self.cb_ncc.set("Chọn NCC")
        self.cb_ncc.pack(fill="x")

        # === TABLE ===
        table_frame = ctk.CTkFrame(container, fg_color="white")
        table_frame.pack(fill="both", expand=True)

        columns = ("stt", "ten", "gia", "sl", "dvt", "ncc", "trangthai")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)

        self.tree.heading("stt", text="STT")
        self.tree.heading("ten", text="Tên Nguyên Liệu")
        self.tree.heading("gia", text="Giá Nhập")
        self.tree.heading("sl", text="Tồn Kho")
        self.tree.heading("dvt", text="ĐVT")
        self.tree.heading("ncc", text="Nhà Cung Cấp")
        self.tree.heading("trangthai", text="Trạng Thái")

        self.tree.column("stt", width=50, anchor="center")
        self.tree.column("ten", width=200)
        self.tree.column("gia", width=100, anchor="e")
        self.tree.column("sl", width=80, anchor="center")
        self.tree.column("dvt", width=80, anchor="center")
        self.tree.column("ncc", width=200)
        self.tree.column("trangthai", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_select_row)

    def create_input(self, parent, label, width):
        f = ctk.CTkFrame(parent, fg_color="#f5f5f5")
        f.pack(side="left", padx=(0, 20), fill="x", expand=True)
        ctk.CTkLabel(f, text=label, font=("Arial", 11, "bold")).pack(anchor="w")
        e = ctk.CTkEntry(f, width=width)
        e.pack(fill="x")
        return e

    def create_btn(self, parent, text, color, hover, cmd):
        ctk.CTkButton(parent, text=text, fg_color=color, hover_color=hover, width=80, command=cmd).pack(side="left",
                                                                                                        padx=5)

    # === LOGIC ===
    def load_table_data(self, data=None):
        for item in self.tree.get_children(): self.tree.delete(item)

        if data is None:
            self.current_list = self.controller.get_list()
        else:
            self.current_list = data

        for idx, row in enumerate(self.current_list):
            status = "Hiện" if row['isActive'] else "Ẩn"

            # Format giá tiền (dấu phẩy)
            gia_fmt = "{:,.0f}".format(row['giaNhap'])

            # [SỬA ĐỔI] Format số lượng thành số nguyên
            sl_fmt = int(row['soLuongTon'])

            self.tree.insert("", "end", values=(
                idx + 1,
                row['tenNguyenLieu'],
                gia_fmt,
                sl_fmt,  # Hiển thị số nguyên
                row['donViTinh'],
                row['tenNhaCungCap'] if row['tenNhaCungCap'] else "N/A",
                status
            ))

    def on_select_row(self, event):
        sel = self.tree.selection()
        if sel:
            idx = self.tree.index(sel[0])
            if idx < len(self.current_list):
                data = self.current_list[idx]
                self.selected_id = data['idNguyenLieu']

                self.entry_ten.delete(0, "end");
                self.entry_ten.insert(0, data['tenNguyenLieu'])
                self.entry_gia.delete(0, "end");
                self.entry_gia.insert(0, int(data['giaNhap']))

                # [SỬA ĐỔI] Hiển thị số nguyên trong ô nhập liệu luôn
                self.entry_sl.delete(0, "end");
                self.entry_sl.insert(0, int(data['soLuongTon']))

                self.entry_dvt.delete(0, "end");
                self.entry_dvt.insert(0, data['donViTinh'])

                if data['tenNhaCungCap'] in self.ncc_names:
                    self.cb_ncc.set(data['tenNhaCungCap'])
                else:
                    self.cb_ncc.set("Chọn NCC")

    def them(self):
        ten = self.entry_ten.get()
        gia = self.entry_gia.get()
        sl = self.entry_sl.get()
        dvt = self.entry_dvt.get()

        ten_ncc = self.cb_ncc.get()
        id_ncc = self.ncc_map.get(ten_ncc)

        if not id_ncc:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn Nhà cung cấp!")
            return

        success, msg = self.controller.add_nguyen_lieu(ten, gia, sl, dvt, id_ncc)
        if success:
            messagebox.showinfo("Thành công", msg)
            self.lam_moi()
            self.load_table_data()
        else:
            messagebox.showerror("Lỗi", msg)

    def sua(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Chọn nguyên liệu cần sửa!")
            return

        ten = self.entry_ten.get()
        gia = self.entry_gia.get()
        sl = self.entry_sl.get()
        dvt = self.entry_dvt.get()
        id_ncc = self.ncc_map.get(self.cb_ncc.get())

        success, msg = self.controller.update_nguyen_lieu(self.selected_id, ten, gia, sl, dvt, id_ncc)
        if success:
            messagebox.showinfo("Thành công", msg)
            self.lam_moi()
            self.load_table_data()
        else:
            messagebox.showerror("Lỗi", msg)

    def an_hien(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Chọn nguyên liệu để đổi trạng thái!")
            return

        success, msg = self.controller.doi_trang_thai(self.selected_id)
        if success:
            messagebox.showinfo("Thành công", msg)
            self.lam_moi()
            self.load_table_data()
        else:
            messagebox.showerror("Lỗi", msg)

    def lam_moi(self):
        self.selected_id = None
        self.entry_ten.delete(0, "end")
        self.entry_gia.delete(0, "end")
        self.entry_sl.delete(0, "end")
        self.entry_dvt.delete(0, "end")
        self.cb_ncc.set("Chọn NCC")
        if self.tree.selection(): self.tree.selection_remove(self.tree.selection())

    def tim_kiem(self):
        kw = self.search_entry.get()
        res = self.controller.search_nguyen_lieu(kw)
        self.load_table_data(res)