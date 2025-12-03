import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog  # Import filedialog
from src.Controller.HoaDonController import HoaDonController


class HoaDonPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="white")

        self.controller = HoaDonController()
        self.current_list = []
        self.selected_id = None
        self.selected_status_text = None

        self.tao_main_content()
        self.load_table_data()

    def tao_main_content(self):
        container = ctk.CTkFrame(self, fg_color="white")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(container, text="QUẢN LÝ HÓA ĐƠN", font=("Arial", 20, "bold"), text_color="#333").pack(anchor="w",
                                                                                                            pady=(
                                                                                                            0, 20))

        # Control Bar
        control_frame = ctk.CTkFrame(container, fg_color="white")
        control_frame.pack(fill="x", pady=(0, 15))

        # Buttons
        btn_frame = ctk.CTkFrame(control_frame, fg_color="white")
        btn_frame.pack(side="left")

        self.create_btn(btn_frame, "Xem Chi Tiết", "#2196F3", self.xem_chi_tiet)
        self.create_btn(btn_frame, "Sửa Trạng Thái", "#FF9800", self.sua_hoa_don)  # Nút Sửa
        self.create_btn(btn_frame, "Xuất Excel", "#009688", self.xuat_excel_hoadon)  # Nút Xuất
        self.create_btn(btn_frame, "Tải lại", "#9E9E9E", self.load_table_data)

        # Search (Giữ nguyên)
        # ...

        # Table
        table_frame = ctk.CTkFrame(container, fg_color="white")
        table_frame.pack(fill="both", expand=True)

        # [CẬP NHẬT] Thêm cột Ngày Sửa
        cols = ("id", "kh", "nv", "ngay", "ngaysua", "tien", "tt")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=15)

        self.tree.heading("id", text="Mã HĐ")
        self.tree.heading("kh", text="Khách Hàng")
        self.tree.heading("nv", text="NV Lập")
        self.tree.heading("ngay", text="Ngày Tạo")
        self.tree.heading("ngaysua", text="Ngày Sửa")  # Cột mới
        self.tree.heading("tien", text="Tổng Tiền")
        self.tree.heading("tt", text="Trạng Thái")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("kh", width=150)
        self.tree.column("nv", width=150)
        self.tree.column("ngay", width=120, anchor="center")
        self.tree.column("ngaysua", width=120, anchor="center")
        self.tree.column("tien", width=120, anchor="e")
        self.tree.column("tt", width=100, anchor="center")

        self.tree.tag_configure('success', foreground='green')
        self.tree.tag_configure('cancel', foreground='red')
        self.tree.tag_configure('wait', foreground='orange')

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def create_btn(self, parent, text, color, cmd):
        ctk.CTkButton(parent, text=text, fg_color=color, width=120, height=32, command=cmd).pack(side="left", padx=5)

    # === LOGIC ===
    def load_table_data(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        self.current_list = self.controller.get_list_invoices()

        for item in self.current_list:
            tag = 'wait'
            if item['trangThai'] == 2:
                tag = 'success'
            elif item['trangThai'] == 0:
                tag = 'cancel'

            self.tree.insert("", "end", values=(
                item['idHoaDon'],
                item['tenKhachHang'],
                item['tenNhanVien'],
                item['ngayTaoFmt'],
                item['ngaySuaFmt'],  # Hiển thị ngày sửa
                item['tongTienFmt'],
                item['statusText']
            ), tags=(tag,))

    def on_select(self, event):
        sel = self.tree.selection()
        if sel:
            val = self.tree.item(sel[0], 'values')
            self.selected_id = val[0]
            self.selected_status_text = val[6]  # Lấy trạng thái hiện tại

    # [MỚI] Hàm Sửa Hóa Đơn
    def sua_hoa_don(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hóa đơn cần sửa!")
            return

        # Tạo Popup
        w = ctk.CTkToplevel(self)
        w.title(f"Sửa Hóa Đơn #{self.selected_id}")
        w.geometry("300x200")
        w.attributes("-topmost", True)

        ctk.CTkLabel(w, text="Cập nhật trạng thái:", font=("Arial", 14, "bold")).pack(pady=20)

        # Combobox chọn trạng thái
        statuses = ["Chờ thanh toán", "Đã thanh toán", "Đã hủy"]
        cb_status = ctk.CTkComboBox(w, values=statuses, state="readonly", width=200)
        cb_status.set(self.selected_status_text)  # Set giá trị hiện tại
        cb_status.pack(pady=10)

        def save_change():
            new_status = cb_status.get()
            if new_status == self.selected_status_text:
                w.destroy();
                return  # Không đổi gì cả

            ok, msg = self.controller.edit_invoice(self.selected_id, new_status)
            if ok:
                messagebox.showinfo("Thành công", msg)
                self.load_table_data()  # Reload để thấy ngày sửa mới
                w.destroy()
            else:
                messagebox.showerror("Lỗi", msg)

        ctk.CTkButton(w, text="Lưu Thay Đổi", fg_color="#4CAF50", command=save_change).pack(pady=10)

    # [MỚI] Hàm Xuất Excel (Chọn thư mục)
    def xuat_excel_hoadon(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hóa đơn để xuất!")
            return

        # Mở hộp thoại chọn nơi lưu
        default_name = f"ChiTietHoaDon_{self.selected_id}.xlsx"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
            initialfile=default_name,
            title="Lưu Chi Tiết Hóa Đơn"
        )

        if file_path:
            ok, msg = self.controller.export_invoice_detail(self.selected_id, file_path)
            if ok:
                messagebox.showinfo("Thành công", msg)
            else:
                messagebox.showerror("Lỗi", msg)

    def xem_chi_tiet(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hóa đơn!")
            return

        details = self.controller.get_details(self.selected_id)

        top = ctk.CTkToplevel(self)
        top.title(f"Chi tiết #{self.selected_id}")
        top.geometry("600x400")
        top.attributes("-topmost", True)

        cols = ("mon", "sl", "gia", "vat", "tong")
        tree_dt = ttk.Treeview(top, columns=cols, show="headings", height=10)
        tree_dt.heading("mon", text="Món");
        tree_dt.heading("sl", text="SL")
        tree_dt.heading("gia", text="Đơn Giá");
        tree_dt.heading("vat", text="VAT");
        tree_dt.heading("tong", text="Thành Tiền")

        tree_dt.column("mon", width=200);
        tree_dt.column("sl", width=50, anchor="center")
        tree_dt.pack(fill="both", expand=True, padx=10, pady=10)

        total = 0
        for row in details:
            tree_dt.insert("", "end", values=(
            row['tenSanPham'], row['soLuong'], row['donGiaFmt'], row['thueVAT'], row['thanhTienFmt']))
            # Lưu ý: Cần parse lại tiền từ chuỗi format nếu muốn tính tổng ở đây, hoặc lấy tổng từ hóa đơn cha