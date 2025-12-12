import customtkinter as ctk
from tkinter import messagebox, ttk
from src.Controller.TaiKhoanController import TaiKhoanController


class QuanLyTKPage(ctk.CTkFrame):
    def __init__(self, parent, current_user_id=None):  # Thêm tham số nếu cần
        super().__init__(parent, fg_color="white")

        # Khởi tạo Controller
        self.controller = TaiKhoanController()

        # Biến lưu trạng thái
        self.selected_id = None
        self.selected_has_account = False
        self.current_list = []

        # Xây dựng giao diện
        self.tao_main_content()
        self.load_table_data()

    def tao_main_content(self):
        """Tạo bố cục giao diện"""
        container = ctk.CTkFrame(self, fg_color="white")
        container.pack(fill="both", expand=True, padx=15, pady=15)

        # === 1. TIÊU ĐỀ ===
        ctk.CTkLabel(
            container,
            text="QUẢN LÝ TÀI KHOẢN NHÂN VIÊN",
            font=("Arial", 20, "bold"),
            text_color="#1565C0"
        ).pack(pady=(0, 20))

        # === 2. FORM NHẬP LIỆU ===
        input_group = ctk.CTkFrame(container, fg_color="#F5F5F5", border_width=1, border_color="#DDD")
        input_group.pack(fill="x", padx=10, pady=(0, 20))

        # --- Toolbar (Nút bấm chức năng) ---
        toolbar = ctk.CTkFrame(input_group, fg_color="transparent")
        toolbar.pack(fill="x", padx=10, pady=(15, 5))

        btn_center = ctk.CTkFrame(toolbar, fg_color="transparent")
        btn_center.pack(anchor="center")

        self.create_btn(btn_center, "Lưu / Cấp TK", "#4CAF50", "#45a049", self.luu_thong_tin, width=120)
        self.create_btn(btn_center, "Xóa TK", "#F44336", "#D32F2F", self.xoa_tk)
        self.create_btn(btn_center, "Làm mới", "#607D8B", "#455A64", self.lam_moi)

        ctk.CTkFrame(input_group, height=1, fg_color="#DDD").pack(fill="x", padx=20, pady=10)

        # --- Các trường nhập liệu ---
        form_container = ctk.CTkFrame(input_group, fg_color="transparent")
        form_container.pack(fill="x", padx=20, pady=(0, 20))

        # Hàng 1: Tên & Email (Readonly)
        row1 = ctk.CTkFrame(form_container, fg_color="transparent")
        row1.pack(fill="x", pady=5)

        self.entry_name = self.create_input(row1, "Họ và tên:", 250)
        self.entry_name.configure(state="readonly", fg_color="#E0E0E0")

        self.entry_email = self.create_input(row1, "Email:", 250)
        self.entry_email.configure(state="readonly", fg_color="#E0E0E0")

        # Hàng 2: Username & Password
        row2 = ctk.CTkFrame(form_container, fg_color="transparent")
        row2.pack(fill="x", pady=5)

        self.entry_user = self.create_input(row2, "Tên đăng nhập:", 250)

        # Frame chứa Mật khẩu + Nút ẩn hiện
        f_pass = ctk.CTkFrame(row2, fg_color="transparent")
        f_pass.pack(side="left", padx=10)
        ctk.CTkLabel(f_pass, text="Mật khẩu:", font=("Arial", 12, "bold"), text_color="#555").pack(anchor="w")

        f_pass_inner = ctk.CTkFrame(f_pass, fg_color="transparent")
        f_pass_inner.pack()

        self.entry_pass = ctk.CTkEntry(f_pass_inner, width=210, height=32, show="*", border_color="#ccc")
        self.entry_pass.pack(side="left")

        self.btn_eye = ctk.CTkButton(f_pass_inner, text="👁", width=35, height=32,
                                     fg_color="#DDD", text_color="#333", hover_color="#CCC",
                                     command=self.toggle_pass)
        self.btn_eye.pack(side="left", padx=(5, 0))

        # Hàng 3: Vai trò (Combobox)
        row3 = ctk.CTkFrame(form_container, fg_color="transparent")
        row3.pack(fill="x", pady=5)

        f_role = ctk.CTkFrame(row3, fg_color="transparent")
        f_role.pack(side="left", padx=10)
        ctk.CTkLabel(f_role, text="Chức vụ / Vai trò:", font=("Arial", 12, "bold"), text_color="#555").pack(anchor="w")

        roles = ["Quản Lý Cửa Hàng", "Pha Chế Trưởng", "Pha Chế Viên", "Phục Vụ", "Thu Ngân", "Bảo Vệ"]
        self.combo_role = ctk.CTkComboBox(f_role, values=roles, width=250, height=32, state="readonly")
        self.combo_role.set("Chọn chức vụ")
        self.combo_role.pack()

        # === [THÊM MỚI] KHUNG TÌM KIẾM ===
        search_frame = ctk.CTkFrame(container, fg_color="white")
        search_frame.pack(fill="x", padx=10, pady=(10, 0))

        ctk.CTkLabel(search_frame, text="DANH SÁCH NHÂN SỰ", font=("Arial", 14, "bold"), text_color="#333").pack(
            side="left")

        # Nút tìm kiếm (Bên phải)
        self.btn_search = ctk.CTkButton(
            search_frame, text="Tìm kiếm", width=100, height=32,
            fg_color="#2196F3", hover_color="#1976D2",
            command=self.thuc_hien_tim_kiem  # <--- Gọi hàm tìm kiếm
        )
        self.btn_search.pack(side="right", padx=5)

        # Ô nhập tìm kiếm (Bên phải, cạnh nút tìm)
        self.entry_search = ctk.CTkEntry(
            search_frame, width=250, height=32,
            placeholder_text="Nhập tên, tài khoản hoặc email..."
        )
        self.entry_search.pack(side="right", padx=5)

        # Cho phép nhấn Enter để tìm
        self.entry_search.bind("<Return>", lambda e: self.thuc_hien_tim_kiem())

        # === 3. DANH SÁCH (TREEVIEW) ===
        list_frame = ctk.CTkFrame(container, fg_color="white", border_width=1, border_color="#999")
        list_frame.pack(fill="both", expand=True, padx=10, pady=(10, 10))

        # Cấu hình bảng
        columns = ("stt", "name", "user", "email", "role", "status")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)

        # Định nghĩa tiêu đề và cột
        self.tree.heading("stt", text="STT")
        self.tree.heading("name", text="Họ và Tên")
        self.tree.heading("user", text="Tên Đăng Nhập")
        self.tree.heading("email", text="Email")
        self.tree.heading("role", text="Chức Vụ")
        self.tree.heading("status", text="Trạng Thái")

        self.tree.column("stt", width=50, anchor="center")
        self.tree.column("name", width=200)
        self.tree.column("user", width=150)
        self.tree.column("email", width=200)
        self.tree.column("role", width=150)
        self.tree.column("status", width=120, anchor="center")

        self.tree.tag_configure('active', foreground='green')
        self.tree.tag_configure('locked', foreground='red')
        self.tree.tag_configure('none', foreground='gray')

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_select_row)

    # ================= CÁC HÀM HỖ TRỢ UI =================
    def create_btn(self, parent, text, color, hover, cmd, width=100):
        ctk.CTkButton(parent, text=text, fg_color=color, hover_color=hover,
                      width=width, height=35, font=("Arial", 12, "bold"),
                      command=cmd).pack(side="left", padx=5)

    def create_input(self, parent, label, width):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(side="left", padx=10)
        ctk.CTkLabel(f, text=label, font=("Arial", 12, "bold"), text_color="#555").pack(anchor="w")
        e = ctk.CTkEntry(f, width=width, height=32, border_color="#ccc")
        e.pack()
        return e

    def toggle_pass(self):
        if self.entry_pass.cget('show') == '*':
            self.entry_pass.configure(show='')
            self.btn_eye.configure(text="🔒")
        else:
            self.entry_pass.configure(show='*')
            self.btn_eye.configure(text="👁")

    # ================= [LOGIC MỚI] HIỂN THỊ & TÌM KIẾM =================

    def render_table(self, data_list):
        """
        Hàm dùng chung để vẽ dữ liệu lên bảng.
        Giúp tránh lặp code khi load all và load search.
        """
        # 1. Xóa dữ liệu cũ trên bảng
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 2. Lưu lại danh sách hiện tại để xử lý click chọn dòng
        self.current_list = data_list

        # 3. Duyệt và thêm vào bảng
        for idx, item in enumerate(data_list):
            has_acc = item['tenDangNhap'] is not None

            # Xử lý trạng thái
            if not has_acc:
                status_text = "Chưa có TK"
                tag = 'none'
            else:
                trang_thai = item.get('trangThai')
                if trang_thai == 1:
                    status_text = "Hoạt động"
                    tag = 'active'
                elif trang_thai == 0:
                    status_text = "Đã Khóa"
                    tag = 'locked'
                else:
                    status_text = "Hoạt động"
                    tag = 'active'

            user_display = item['tenDangNhap'] if has_acc else ""

            self.tree.insert("", "end", values=(
                idx + 1,
                item['hoTen'],
                user_display,
                item['email'],
                item['tenChucVu'],
                status_text
            ), tags=(tag,))

    def load_table_data(self):
        """Tải TOÀN BỘ dữ liệu (Mặc định)"""
        all_data = self.controller.get_list()
        self.render_table(all_data)

    def thuc_hien_tim_kiem(self):
        """Hàm xử lý khi bấm nút Tìm kiếm"""
        keyword = self.entry_search.get().strip()

        if not keyword:
            # Nếu ô tìm kiếm rỗng thì load lại toàn bộ
            self.load_table_data()
            return

        # Gọi Controller tìm kiếm
        # [LƯU Ý]: Đảm bảo Controller của bạn có hàm 'tim_kiem_tai_khoan(keyword)'
        # Nếu controller bạn đặt tên hàm khác, hãy sửa lại dòng dưới đây.
        search_results = self.controller.tim_kiem_tai_khoan(keyword)

        if search_results:
            self.render_table(search_results)
        else:
            # Nếu không tìm thấy, xóa trắng bảng và báo (hoặc không báo tùy ý)
            self.render_table([])
            # messagebox.showinfo("Thông báo", "Không tìm thấy kết quả nào!")

    # ================= CÁC LOGIC KHÁC GIỮ NGUYÊN =================
    def on_select_row(self, event):
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            if index < len(self.current_list):
                data = self.current_list[index]
                self.selected_id = data['idNhanVien']
                self.selected_has_account = (data['tenDangNhap'] is not None)

                self.entry_name.configure(state="normal")
                self.entry_name.delete(0, "end")
                self.entry_name.insert(0, data['hoTen'])
                self.entry_name.configure(state="readonly")

                self.entry_email.configure(state="normal")
                self.entry_email.delete(0, "end")
                self.entry_email.insert(0, data['email'])
                self.entry_email.configure(state="readonly")

                self.combo_role.set(data['tenChucVu'])

                self.entry_user.delete(0, "end")
                self.entry_pass.delete(0, "end")

                if self.selected_has_account:
                    self.entry_user.insert(0, data['tenDangNhap'])
                    self.entry_pass.configure(placeholder_text="(Đã có mật khẩu - Nhập mới để đổi)")
                else:
                    self.entry_pass.configure(placeholder_text="Nhập mật khẩu để cấp TK")

    def luu_thong_tin(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên từ danh sách!")
            return

        name = self.entry_name.get()
        user = self.entry_user.get()
        pwd = self.entry_pass.get()
        email = self.entry_email.get()
        role = self.combo_role.get()

        success, msg = self.controller.save_account(
            self.selected_id, self.selected_has_account,
            name, user, pwd, email, role
        )

        if success:
            messagebox.showinfo("Thành công", msg)
            self.lam_moi()
        else:
            messagebox.showerror("Lỗi", msg)

    def xoa_tk(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn dòng cần xóa!")
            return

        if not self.selected_has_account:
            messagebox.showinfo("Thông báo", "Nhân viên này chưa có tài khoản để xóa!")
            return

        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa tài khoản này?"):
            success, msg = self.controller.delete_account_only(self.selected_id)
            if success:
                messagebox.showinfo("Thành công", msg)
                self.lam_moi()
            else:
                messagebox.showerror("Lỗi", msg)

    def lam_moi(self):
        self.selected_id = None
        self.selected_has_account = False

        # Xóa form tìm kiếm luôn khi làm mới
        self.entry_search.delete(0, "end")

        self.entry_name.configure(state="normal")
        self.entry_name.delete(0, "end")
        self.entry_name.configure(state="readonly")

        self.entry_email.configure(state="normal")
        self.entry_email.delete(0, "end")
        self.entry_email.configure(state="readonly")

        self.entry_user.delete(0, "end")
        self.entry_pass.delete(0, "end")
        self.combo_role.set("Chọn chức vụ")
        self.entry_pass.configure(placeholder_text="")

        self.load_table_data()