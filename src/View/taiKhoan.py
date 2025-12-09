import customtkinter as ctk
from tkinter import messagebox
from src.Controller.TaiKhoan2Controller import TaiKhoan2Controller


class TaiKhoanPage(ctk.CTkFrame):
    def __init__(self, parent, current_user_id):
        """
        parent: Frame cha chứa trang này
        current_user_id: ID của nhân viên đang đăng nhập (Bắt buộc phải truyền đúng)
        """
        super().__init__(parent, fg_color="#F0F0F0")

        # 1. Khởi tạo Controller & Biến
        self.controller = TaiKhoan2Controller()
        self.user_id = current_user_id
        self.account_data = None
        self.is_editing = False

        # 2. Vẽ giao diện
        self.setup_ui()

        # 3. [QUAN TRỌNG] Đổ dữ liệu ngay lập tức khi vào trang
        self.load_data()

    def setup_ui(self):
        # Cấu hình Grid layout chính
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Thông tin
        self.grid_rowconfigure(2, weight=1)  # Đổi mật khẩu

        # ================= 1. TIÊU ĐỀ =================
        title_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ctk.CTkLabel(title_frame, text="Quản Lý Hồ Sơ Cá Nhân",
                     font=("Arial", 18, "bold"), text_color="#000000").pack(pady=15)

        # ================= 2. KHUNG THÔNG TIN CÁ NHÂN =================
        self.info_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        self.info_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        # Header Section
        ctk.CTkLabel(self.info_frame, text="Thông Tin Nhân Viên",
                     font=("Arial", 14, "bold"), text_color="#333").pack(anchor="w", padx=20, pady=10)
        ctk.CTkFrame(self.info_frame, height=2, fg_color="#E0E0E0").pack(fill="x", padx=20, pady=(0, 10))

        # Grid chứa các fields input
        fields_container = ctk.CTkFrame(self.info_frame, fg_color="white")
        fields_container.pack(fill="both", expand=True, padx=20)

        # Hàng 1 (Readonly info)
        self.entry_id = self.create_field(fields_container, "Mã NV:", 0, 0, state="disabled")
        self.entry_role = self.create_field(fields_container, "Chức Vụ:", 0, 1, state="disabled")
        self.entry_username = self.create_field(fields_container, "Tên Đăng Nhập:", 0, 2, state="disabled")

        # Hàng 2 (Editable info)
        self.entry_name = self.create_field(fields_container, "Họ Tên:", 1, 0)
        self.entry_phone = self.create_field(fields_container, "Số Điện Thoại:", 1, 1)
        self.entry_email = self.create_field(fields_container, "Email:", 1, 2)

        # Nút chức năng (Edit/Save)
        btn_frame = ctk.CTkFrame(self.info_frame, fg_color="white")
        btn_frame.pack(pady=20)

        self.btn_edit = ctk.CTkButton(btn_frame, text="Chỉnh Sửa", fg_color="#2196F3", width=120,
                                      command=self.toggle_edit)
        self.btn_edit.pack(side="left", padx=10)

        self.btn_save = ctk.CTkButton(btn_frame, text="Lưu Thay Đổi", fg_color="#4CAF50", width=120, state="disabled",
                                      command=self.save_info)
        self.btn_save.pack(side="left", padx=10)

        # ================= 3. KHUNG ĐỔI MẬT KHẨU =================
        pass_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        pass_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)

        ctk.CTkLabel(pass_frame, text="Bảo Mật & Đổi Mật Khẩu",
                     font=("Arial", 14, "bold"), text_color="#333").pack(anchor="w", padx=20, pady=10)
        ctk.CTkFrame(pass_frame, height=2, fg_color="#E0E0E0").pack(fill="x", padx=20, pady=(0, 10))

        pass_container = ctk.CTkFrame(pass_frame, fg_color="white")
        pass_container.pack(fill="x", padx=20)

        # Input mật khẩu
        self.entry_old_pass = self.create_pass_field(pass_container, "Mật khẩu cũ:", 0)
        self.entry_new_pass = self.create_pass_field(pass_container, "Mật khẩu mới:", 1)
        self.entry_confirm_pass = self.create_pass_field(pass_container, "Xác nhận MK:", 2)

        ctk.CTkButton(pass_frame, text="Cập Nhật Mật Khẩu", fg_color="#FF9800",
                      width=150, height=40, font=("Arial", 12, "bold"),
                      command=self.change_pass).pack(pady=20)

    # ================= UI HELPERS =================
    def create_field(self, parent, label, row, col, state="normal"):
        """Tạo ô nhập liệu thông tin"""
        f = ctk.CTkFrame(parent, fg_color="white")
        f.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
        parent.grid_columnconfigure(col, weight=1)

        ctk.CTkLabel(f, text=label, font=("Arial", 12), text_color="gray").pack(anchor="w")
        e = ctk.CTkEntry(f, height=35, font=("Arial", 13), border_color="#CCC")
        e.pack(fill="x")
        e.configure(state=state)
        return e

    def create_pass_field(self, parent, label, col):
        """Tạo ô nhập mật khẩu (ẩn ký tự)"""
        f = ctk.CTkFrame(parent, fg_color="white")
        f.grid(row=0, column=col, padx=10, pady=10, sticky="ew")
        parent.grid_columnconfigure(col, weight=1)

        ctk.CTkLabel(f, text=label, font=("Arial", 12), text_color="gray").pack(anchor="w")
        e = ctk.CTkEntry(f, height=35, font=("Arial", 13), show="*", border_color="#CCC")
        e.pack(fill="x")
        return e

    # ================= LOGIC CHỨC NĂNG =================
    def load_data(self):
        """Tải thông tin nhân viên từ Controller và đổ vào View"""
        if not self.user_id:
            messagebox.showerror("Lỗi", "Không tìm thấy ID người dùng!")
            return

        data = self.controller.get_info(self.user_id)
        if data:
            self.account_data = data

            # Fill dữ liệu Readonly (Không được sửa)
            self.set_entry(self.entry_id, data['idNhanVien'])
            self.set_entry(self.entry_role, data['tenChucVu'])
            self.set_entry(self.entry_username, data['tenDangNhap'])

            # Fill dữ liệu Editable (Được sửa)
            self.set_entry(self.entry_name, data['hoTen'])
            self.set_entry(self.entry_phone, data['soDienThoai'])
            self.set_entry(self.entry_email, data['email'])

            # Khóa chế độ sửa ban đầu
            self.lock_edit(True)
        else:
            messagebox.showerror("Lỗi", "Không tải được thông tin nhân viên!")

    def set_entry(self, entry, text):
        entry.configure(state="normal")
        entry.delete(0, "end")
        entry.insert(0, str(text) if text else "")
        # Nếu là các trường ID, Role, User thì luôn disable sau khi set text
        if entry in [self.entry_id, self.entry_role, self.entry_username]:
            entry.configure(state="disabled")

    def lock_edit(self, locked=True):
        """Bật/Tắt chế độ chỉnh sửa"""
        state = "disabled" if locked else "normal"
        color = "#F5F5F5" if locked else "white"

        # Chỉ cho sửa Tên, SĐT, Email
        for e in [self.entry_name, self.entry_phone, self.entry_email]:
            e.configure(state=state, fg_color=color)

        if locked:
            self.btn_edit.configure(text="Chỉnh Sửa", fg_color="#2196F3")
            self.btn_save.configure(state="disabled")
        else:
            self.btn_edit.configure(text="Hủy Bỏ", fg_color="#9E9E9E")
            self.btn_save.configure(state="normal")

        self.is_editing = not locked

    def toggle_edit(self):
        if self.is_editing:
            # Nếu đang edit mà bấm Hủy -> Load lại data cũ
            self.load_data()
        else:
            # Mở khóa edit
            self.lock_edit(False)

    def save_info(self):
        if not self.is_editing: return

        ok, msg = self.controller.save_info(
            self.user_id,
            self.entry_name.get(),
            self.entry_phone.get(),
            self.entry_email.get()
        )

        if ok:
            messagebox.showinfo("Thành công", msg)
            self.lock_edit(True)
        else:
            messagebox.showerror("Lỗi", msg)

    def change_pass(self):
        if not self.account_data: return

        # Gọi Controller xử lý đổi mật khẩu
        ok, msg = self.controller.change_password(
            self.account_data['idTaiKhoan'],
            self.entry_old_pass.get(),
            self.entry_new_pass.get(),
            self.entry_confirm_pass.get()
        )

        if ok:
            messagebox.showinfo("Thành công", msg)
            # Xóa trắng ô nhập sau khi thành công
            self.entry_old_pass.delete(0, "end")
            self.entry_new_pass.delete(0, "end")
            self.entry_confirm_pass.delete(0, "end")
        else:
            messagebox.showerror("Lỗi", msg)