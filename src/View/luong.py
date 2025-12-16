import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog
from datetime import datetime
from src.Controller.LuongController import LuongController


class LuongPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="white")
        self.controller = LuongController()
        self.current_list = []
        self.selected_id = None
        self.selected_name = None
        self.selected_status = None

        self.tao_main_content()
        # Load dữ liệu lần đầu
        self.load_data()

    def tao_main_content(self):
        container = ctk.CTkFrame(self, fg_color="white")
        container.pack(fill="both", expand=True, padx=15, pady=15)

        # === HEADER ===
        header = ctk.CTkFrame(container, fg_color="white")
        header.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(header, text="Quản Lý Lương Nhân Viên",
                     font=("Arial", 18, "bold"), text_color="#333").pack(side="left")

        # Combobox Tháng
        now = datetime.now()
        months = [f"Tháng {m}/{y}" for y in [now.year, now.year - 1] for m in range(12, 0, -1)]
        self.cb_month = ctk.CTkComboBox(header, values=months, width=160, state="readonly",
                                        command=self.on_month_change)

        # Mặc định chọn tháng hiện tại
        current_month_str = f"Tháng {now.month}/{now.year}"
        if current_month_str in months:
            self.cb_month.set(current_month_str)
        else:
            self.cb_month.set(months[0])

        self.cb_month.pack(side="right")

        # === TOOLBAR ===
        toolbar = ctk.CTkFrame(container, fg_color="#f5f5f5")
        toolbar.pack(fill="x", pady=(0, 15))
        inner = ctk.CTkFrame(toolbar, fg_color="transparent")
        inner.pack(padx=10, pady=10, fill="x")

        # Tìm kiếm
        self.entry_search = ctk.CTkEntry(inner, width=200, placeholder_text="Tìm tên/mã NV...")
        self.entry_search.pack(side="left", padx=5)
        ctk.CTkButton(inner, text="🔍 Tìm", width=60, command=self.search_data).pack(side="left")

        # Nút chức năng
        ctk.CTkButton(inner, text="💰 Thanh Toán", fg_color="#4CAF50", hover_color="#388E3C",
                      command=self.thanh_toan).pack(side="left", padx=10)
        ctk.CTkButton(inner, text="📊 Excel", fg_color="#009688", hover_color="#00796B",
                      command=self.xuat_excel).pack(side="left")
        ctk.CTkButton(inner, text="🔃 Tải lại", fg_color="gray", width=60,
                      command=self.reload_data).pack(side="right")

        # === TABLE ===
        table_frame = ctk.CTkFrame(container)
        table_frame.pack(fill="both", expand=True)

        cols = ("stt", "manv", "hoten", "chucvu", "luongcb", "tonggio", "thuclanh", "trangthai")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=15)

        headers = ["STT", "Mã NV", "Họ Tên", "Chức Vụ", "Lương CB (Lưu)", "Tổng Giờ", "Thực Lãnh", "Trạng Thái"]
        for col, title in zip(cols, headers):
            self.tree.heading(col, text=title)

        self.tree.column("stt", width=40, anchor="center")
        self.tree.column("manv", width=60, anchor="center")
        self.tree.column("hoten", width=180)
        self.tree.column("luongcb", width=100, anchor="e")
        self.tree.column("thuclanh", width=120, anchor="e")
        self.tree.column("trangthai", width=100, anchor="center")

        # Scrollbar
        sb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_select_row)

        # Style màu sắc
        self.tree.tag_configure('chua_tt', background='#FFF3E0', foreground='#E65100')
        self.tree.tag_configure('da_tt', background='#E8F5E9', foreground='#2E7D32')

    # === LOGIC ===
    def load_data(self, data_input=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if data_input is None:
            # Controller sẽ gọi Model -> Model tự động INSERT lương tháng mới vào SQL nếu chưa có
            self.current_list = self.controller.get_list_salary(self.cb_month.get())
        else:
            self.current_list = data_input

        if not self.current_list: return

        for idx, row in enumerate(self.current_list):
            status = row['trangThai']
            tag = "da_tt" if status == "DaThanhToan" else "chua_tt"
            status_txt = "Đã Thanh Toán" if status == "DaThanhToan" else "Chưa Thanh Toán"

            # Format số
            lcb = "{:,.0f}".format(float(row['luongCoBanSnapshot'])) if row['luongCoBanSnapshot'] else "0"
            ttl = "{:,.0f}".format(float(row['thucLanh'])) if row['thucLanh'] else "0"
            gio = "{:,.2f}".format(float(row['tongGioLamThang'])) if row['tongGioLamThang'] else "0"

            self.tree.insert("", "end", values=(
                idx + 1,
                row['idNhanVien'],
                row['hoTen'],
                row['tenChucVu'],
                lcb,  # Hiển thị lương cơ bản đã lưu trong DB
                gio,
                ttl,
                status_txt
            ), tags=(tag,))

    def on_month_change(self, value):
        self.reload_data()

    def reload_data(self):
        self.entry_search.delete(0, "end")
        self.selected_id = None
        self.load_data()

    def on_select_row(self, event):
        sel = self.tree.selection()
        if sel:
            item = self.current_list[self.tree.index(sel[0])]
            self.selected_id = item['idNhanVien']
            self.selected_name = item['hoTen']
            self.selected_status = item['trangThai']

    def search_data(self):
        txt = self.entry_search.get().lower()
        if not txt: return self.reload_data()

        # Tìm trong list hiện tại (Client-side)
        filtered = [x for x in self.controller.get_list_salary(self.cb_month.get())
                    if txt in x['hoTen'].lower() or txt in str(x['idNhanVien'])]
        self.load_data(filtered)

    def thanh_toan(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Chọn nhân viên cần thanh toán!")
            return

        if self.selected_status == 'DaThanhToan':
            messagebox.showinfo("Thông tin", "Nhân viên này đã được thanh toán rồi.")
            return

        if messagebox.askyesno("Xác nhận", f"Thanh toán lương cho: {self.selected_name}?"):
            ok, msg = self.controller.thanh_toan_luong(self.selected_id, self.cb_month.get())
            if ok:
                messagebox.showinfo("Thành công", msg)
                self.reload_data()
            else:
                messagebox.showerror("Lỗi", msg)

    def xuat_excel(self):
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if path:
            ok, msg = self.controller.export_excel(self.cb_month.get(), path)
            if ok:
                messagebox.showinfo("Xong", msg)
            else:
                messagebox.showerror("Lỗi", msg)