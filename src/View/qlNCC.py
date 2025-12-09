import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import os
from datetime import datetime
from src.Controller.NhaCungCapController import NhaCungCapController


class NhaCungCapPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="white")

        # Khởi tạo Controller
        self.controller = NhaCungCapController()

        # Biến lưu trữ trạng thái
        self.current_list = []  # Danh sách data đang hiển thị
        self.selected_id = None  # ID bản ghi đang chọn

        # Dựng giao diện
        self.tao_main_content()

        # Load dữ liệu ban đầu
        self.load_table_data()

    def tao_main_content(self):
        # --- CONTAINER CHÍNH ---
        container = ctk.CTkFrame(self, fg_color="white")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Tiêu đề
        ctk.CTkLabel(container, text="Quản Lý Nhà Cung Cấp", font=("Arial", 18, "bold"), text_color="#333").pack(
            anchor="w", pady=(0, 20))

        # --- 1. THANH CÔNG CỤ (BUTTONS & SEARCH) ---
        action_bar = ctk.CTkFrame(container, fg_color="white")
        action_bar.pack(fill="x", pady=(0, 20))

        # Nhóm nút chức năng bên trái
        btn_frame = ctk.CTkFrame(action_bar, fg_color="white")
        btn_frame.pack(side="left")

        self.create_btn(btn_frame, "Thêm", "#4CAF50", "#45a049", self.them)
        self.create_btn(btn_frame, "Sửa", "#2196F3", "#0b7dda", self.sua)
        self.create_btn(btn_frame, "Ẩn/Hiện", "#FF9800", "#F57C00", self.doi_trang_thai, width=100)
        self.create_btn(btn_frame, "Làm mới", "#9E9E9E", "#757575", self.lam_moi)
        self.create_btn(btn_frame, "Xuất Excel", "#00BCD4", "#0097A7", self.xuat, width=100)

        # Nhóm tìm kiếm bên phải
        search_frame = ctk.CTkFrame(action_bar, fg_color="white")
        search_frame.pack(side="right")

        self.search_entry = ctk.CTkEntry(search_frame, width=250, height=35, placeholder_text="Nhập tên hoặc SĐT...",
                                         border_color="#ccc")
        self.search_entry.pack(side="left", padx=(0, 5))

        ctk.CTkButton(search_frame, text="Tìm kiếm", fg_color="#2196F3", hover_color="#0b7dda",
                      width=80, height=35, font=("Arial", 12, "bold"), command=self.tim_kiem).pack(side="left")

        # --- 2. FORM NHẬP LIỆU ---
        form_wrapper = ctk.CTkFrame(container, fg_color="#f5f5f5", border_width=1, border_color="#e0e0e0",
                                    corner_radius=8)
        form_wrapper.pack(fill="x", pady=(0, 20))

        form_inner = ctk.CTkFrame(form_wrapper, fg_color="#f5f5f5")
        form_inner.pack(fill="x", padx=20, pady=20)

        # Hàng 1
        row1 = ctk.CTkFrame(form_inner, fg_color="#f5f5f5")
        row1.pack(fill="x", pady=(0, 15))
        self.entry_ten = self.create_input(row1, "Tên Nhà Cung Cấp (*)", 350)

        # Hàng 2
        row2 = ctk.CTkFrame(form_inner, fg_color="#f5f5f5")
        row2.pack(fill="x")
        self.entry_sdt = self.create_input(row2, "Số điện thoại (*)", 200)
        self.entry_dia_chi = self.create_input(row2, "Địa chỉ", 350)  # Đã thay thế ô Sản phẩm bằng Địa chỉ

        # --- 3. BẢNG DỮ LIỆU (TREEVIEW) ---
        ctk.CTkLabel(container, text="Danh sách hiển thị", font=("Arial", 14, "bold"), text_color="#555").pack(
            anchor="w", pady=(0, 5))

        table_frame = ctk.CTkFrame(container, fg_color="white", border_width=1, border_color="#ccc")
        table_frame.pack(fill="both", expand=True)

        # Style cho Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground="black", rowheight=35, fieldbackground="white",
                        font=("Arial", 11))
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#eee", foreground="#333")
        style.map("Treeview", background=[("selected", "#E3F2FD")], foreground=[("selected", "black")])

        # Định nghĩa cột
        columns = ("stt", "ten", "sdt", "diachi", "nguyenlieu", "ngaycapnhat", "trangthai")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        # Config header & cột
        self.tree.heading("stt", text="STT")
        self.tree.column("stt", width=50, anchor="center")

        self.tree.heading("ten", text="Tên Nhà Cung Cấp")
        self.tree.column("ten", width=200, anchor="w")

        self.tree.heading("sdt", text="SĐT")
        self.tree.column("sdt", width=120, anchor="center")

        self.tree.heading("diachi", text="Địa Chỉ")
        self.tree.column("diachi", width=200, anchor="w")

        self.tree.heading("nguyenlieu", text="Nguyên Liệu Cung Cấp")
        self.tree.column("nguyenlieu", width=250, anchor="w")

        self.tree.heading("ngaycapnhat", text="Ngày Cập Nhật")
        self.tree.column("ngaycapnhat", width=120, anchor="center")

        self.tree.heading("trangthai", text="Trạng Thái")
        self.tree.column("trangthai", width=100, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=2, pady=2)

        # Bind sự kiện chọn dòng
        self.tree.bind("<<TreeviewSelect>>", self.on_select_row)

    # ===============================
    # CÁC HÀM HỖ TRỢ GIAO DIỆN (HELPER)
    # ===============================
    def create_btn(self, parent, text, color, hover, cmd, width=90):
        ctk.CTkButton(parent, text=text, fg_color=color, hover_color=hover, text_color="white",
                      width=width, height=38, corner_radius=6, font=("Arial", 12, "bold"),
                      command=cmd).pack(side="left", padx=5)

    def create_input(self, parent, label, width):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(f, text=label, font=("Arial", 12, "bold"), text_color="#555").pack(anchor="w", pady=(0, 5))
        e = ctk.CTkEntry(f, width=width, height=35, border_color="#ccc")
        e.pack()
        return e

    # ===============================
    # LOGIC XỬ LÝ
    # ===============================
    def load_table_data(self, data=None):
        """Hiển thị dữ liệu lên bảng"""
        # 1. Xóa dữ liệu cũ trên bảng
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 2. Nếu không truyền data vào thì lấy tất cả từ DB
        if data is None:
            data = self.controller.lay_danh_sach()

        self.current_list = data  # Lưu lại để dùng cho việc click chọn dòng

        # 3. Duyệt và hiển thị
        for i, row in enumerate(data):
            # Xử lý hiển thị
            trang_thai_text = "Hoạt động" if row['isActive'] else "Đã ẩn"
            nguyen_lieu_text = row['danhSachNguyenLieu'] if row['danhSachNguyenLieu'] else "(Chưa có)"

            ngay_cn_text = ""
            if row['ngayCapNhat']:
                ngay_cn_text = row['ngayCapNhat'].strftime("%d/%m/%Y")

            values = (
                i + 1,
                row['tenNhaCungCap'],
                row['soDienThoai'],
                row['diaChi'],
                nguyen_lieu_text,
                ngay_cn_text,
                trang_thai_text
            )

            # Tag để làm mờ dòng đã ẩn
            tags = ('hidden',) if not row['isActive'] else ('normal',)
            self.tree.insert("", "end", values=values, tags=tags)

        # Định nghĩa màu chữ cho dòng bị ẩn
        self.tree.tag_configure('hidden', foreground='#999999')

    def on_select_row(self, event):
        """Khi người dùng click vào một dòng"""
        selected = self.tree.selection()
        if selected:
            # Lấy index dòng đang chọn
            index = self.tree.index(selected[0])
            # Lấy object data tương ứng
            data = self.current_list[index]

            self.selected_id = data['idNhaCungCap']

            # Đổ dữ liệu lên Form
            self.entry_ten.delete(0, "end");
            self.entry_ten.insert(0, data['tenNhaCungCap'])
            self.entry_sdt.delete(0, "end");
            self.entry_sdt.insert(0, data['soDienThoai'] if data['soDienThoai'] else "")
            self.entry_dia_chi.delete(0, "end");
            self.entry_dia_chi.insert(0, data['diaChi'] if data['diaChi'] else "")

    def them(self):
        ten = self.entry_ten.get()
        sdt = self.entry_sdt.get()
        dc = self.entry_dia_chi.get()

        status, msg = self.controller.them_ncc(ten, sdt, dc)
        if status:
            messagebox.showinfo("Thành công", msg)
            self.lam_moi()  # Xóa trắng form
            self.load_table_data()  # Load lại bảng
        else:
            messagebox.showerror("Lỗi", msg)

    def sua(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn NCC cần sửa trong danh sách!")
            return

        ten = self.entry_ten.get()
        sdt = self.entry_sdt.get()
        dc = self.entry_dia_chi.get()

        status, msg = self.controller.sua_ncc(self.selected_id, ten, sdt, dc)
        if status:
            messagebox.showinfo("Thành công", msg)
            self.load_table_data()
        else:
            messagebox.showerror("Lỗi", msg)

    def doi_trang_thai(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn NCC cần Ẩn/Hiện!")
            return

        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn đổi trạng thái của NCC này?"):
            status, msg = self.controller.doi_trang_thai(self.selected_id)
            if status:
                messagebox.showinfo("Thành công", msg)
                self.load_table_data()
            else:
                messagebox.showerror("Lỗi", msg)

    def lam_moi(self):
        """Xóa form và reset trạng thái"""
        self.entry_ten.delete(0, "end")
        self.entry_sdt.delete(0, "end")
        self.entry_dia_chi.delete(0, "end")
        self.search_entry.delete(0, "end")
        self.selected_id = None
        self.load_table_data()  # Load lại toàn bộ danh sách gốc

    def tim_kiem(self):
        keyword = self.search_entry.get()
        data = self.controller.tim_kiem(keyword)
        self.load_table_data(data)

    def xuat(self):
        """Xuất Excel với logic chọn thư mục"""
        # 1. Kiểm tra data
        if not self.current_list:
            messagebox.showwarning("Cảnh báo", "Danh sách trống, không có dữ liệu để xuất!")
            return

        # 2. Mở hộp thoại CHỌN THƯ MỤC
        folder_selected = filedialog.askdirectory(title="Chọn thư mục lưu file Excel")

        # 3. Nếu người dùng đã chọn thư mục
        if folder_selected:
            try:
                # Tạo tên file tự động: DanhSachNCC_20231025_153045.xlsx
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_name = f"DanhSachNCC_{timestamp}.xlsx"

                # Tạo đường dẫn đầy đủ (Thư mục + Tên file)
                full_path = os.path.join(folder_selected, file_name)

                # Gọi Controller để xuất file
                status, msg = self.controller.xuat_excel(full_path, self.current_list)

                if status:
                    messagebox.showinfo("Thành công", f"{msg}\nFile được lưu tại:\n{full_path}")
                else:
                    messagebox.showerror("Thất bại", msg)

            except Exception as e:
                messagebox.showerror("Lỗi", f"Có lỗi khi tạo đường dẫn file: {e}")