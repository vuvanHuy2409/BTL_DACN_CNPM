import customtkinter as ctk
from tkinter import messagebox
from src.Controller.TaiKhoan2Controller import TaiKhoan2Controller


class TaiKhoanPage(ctk.CTkFrame):
    def __init__(self, parent, current_user_id):
        """
        parent: Frame cha
        current_user_id: ID của nhân viên ĐANG ĐĂNG NHẬP (Được truyền từ MainApp)
        """
        super().__init__(parent, fg_color="#F5F7F9")

        # 1. Kiểm tra ID người dùng
        if not current_user_id:
            ctk.CTkLabel(self, text="⚠ Lỗi: Không xác định được ID người dùng!",
                         font=("Arial", 16), text_color="red").pack(pady=50)
            return

        # 2. Khởi tạo Controller & Biến
        self.controller = TaiKhoan2Controller()
        self.user_id = current_user_id  # <--- QUAN TRỌNG: Lưu ID để dùng cho các hàm sau
        self.account_data = None
        self.is_editing = False

        # 3. Vẽ giao diện & Đổ dữ liệu
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        self.setup_ui()
        self.load_data()  # <--- Tự động chạy hàm lấy dữ liệu ngay khi vào trang

    def setup_ui(self):
        # ================= CỘT TRÁI: PROFILE CARD =================
        self.profile_card = ctk.CTkFrame(self, fg_color="white", corner_radius=15, border_width=1,
                                         border_color="#E0E0E0")
        self.profile_card.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)

        # Avatar
        self.avatar_frame = ctk.CTkFrame(self.profile_card, width=100, height=100, corner_radius=50, fg_color="#E3F2FD")
        self.avatar_frame.pack(pady=(30, 10))
        self.lbl_avatar_text = ctk.CTkLabel(self.avatar_frame, text="?", font=("Arial", 40, "bold"),
                                            text_color="#2196F3")
        self.lbl_avatar_text.place(relx=0.5, rely=0.5, anchor="center")

        self.lbl_display_name = ctk.CTkLabel(self.profile_card, text="Đang tải...", font=("Arial", 18, "bold"),
                                             text_color="#333")
        self.lbl_display_name.pack(pady=(5, 0))

        self.lbl_display_role = ctk.CTkLabel(self.profile_card, text="...", font=("Arial", 13), text_color="gray")
        self.lbl_display_role.pack(pady=(0, 20))

        ctk.CTkFrame(self.profile_card, height=1, fg_color="#EEEEEE").pack(fill="x", padx=20, pady=10)

        # Thông tin Read-only
        self.create_readonly_row(self.profile_card, "Mã Nhân Viên:", "entry_id")
        self.create_readonly_row(self.profile_card, "Tài Khoản:", "entry_username")
        self.create_readonly_row(self.profile_card, "Ngày Tạo:", "entry_date")

        # ================= CỘT PHẢI: CHI TIẾT & BẢO MẬT =================
        self.right_panel = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)

        # --- Card 1: Thông tin cá nhân ---
        self.info_card = ctk.CTkFrame(self.right_panel, fg_color="white", corner_radius=15, border_width=1,
                                      border_color="#E0E0E0")
        self.info_card.pack(fill="x", pady=(0, 20))

        header_frame = ctk.CTkFrame(self.info_card, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(header_frame, text="Thông Tin Cá Nhân", font=("Arial", 16, "bold"), text_color="#2D3436").pack(
            side="left")

        self.btn_save = ctk.CTkButton(header_frame, text="Lưu Thay Đổi", fg_color="#00C853", width=100, height=30,
                                      state="disabled", command=self.save_info)
        self.btn_save.pack(side="right")
        self.btn_edit = ctk.CTkButton(header_frame, text="Chỉnh Sửa", fg_color="#2979FF", width=100, height=30,
                                      command=self.toggle_edit)
        self.btn_edit.pack(side="right", padx=10)

        grid_info = ctk.CTkFrame(self.info_card, fg_color="white")
        grid_info.pack(fill="x", padx=20, pady=(0, 20))

        # Các trường thông tin (Mặc định read_only=True)
        self.entry_fullname = self.create_modern_input(grid_info, "Họ và Tên", 0, 0, icon="👤", read_only=True)
        self.entry_phone = self.create_modern_input(grid_info, "Số Điện Thoại", 0, 1, icon="📞", read_only=True)
        self.entry_email = self.create_modern_input(grid_info, "Email", 1, 0, icon="📧", read_only=True)

        # --- Card 2: Đổi mật khẩu ---
        self.security_card = ctk.CTkFrame(self.right_panel, fg_color="white", corner_radius=15, border_width=1,
                                          border_color="#E0E0E0")
        self.security_card.pack(fill="x")

        sec_header = ctk.CTkFrame(self.security_card, fg_color="transparent")
        sec_header.pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(sec_header, text="Bảo Mật & Mật Khẩu", font=("Arial", 16, "bold"), text_color="#2D3436").pack(
            side="left")

        grid_pass = ctk.CTkFrame(self.security_card, fg_color="white")
        grid_pass.pack(fill="x", padx=20, pady=(0, 20))

        # Các trường mật khẩu (read_only=False để NHẬP ĐƯỢC)
        self.entry_old_pass = self.create_modern_input(grid_pass, "Mật khẩu hiện tại", 0, 0, is_pass=True,
                                                       read_only=False)
        self.entry_new_pass = self.create_modern_input(grid_pass, "Mật khẩu mới", 0, 1, is_pass=True, read_only=False)
        self.entry_confirm_pass = self.create_modern_input(grid_pass, "Nhập lại mật khẩu mới", 1, 0, is_pass=True,
                                                           read_only=False)

        self.btn_change_pass = ctk.CTkButton(grid_pass, text="Cập Nhật Mật Khẩu", fg_color="#FF9800",
                                             hover_color="#FFB74D",
                                             height=35, font=("Arial", 13, "bold"), command=self.change_pass)
        self.btn_change_pass.grid(row=1, column=1, padx=10, pady=(23, 0), sticky="ew")

    # ================= UI HELPER =================
    def create_modern_input(self, parent, label, row, col, icon="", is_pass=False, read_only=True):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
        parent.grid_columnconfigure(col, weight=1)

        lbl_text = f"{icon} {label}" if icon else label
        ctk.CTkLabel(f, text=lbl_text, font=("Arial", 12, "bold"), text_color="#555").pack(anchor="w", pady=(0, 5))

        state = "disabled" if read_only else "normal"
        bg_color = "#F9F9F9" if read_only else "#FFFFFF"
        border_color = "#E0E0E0" if read_only else "#CCCCCC"

        entry = ctk.CTkEntry(f, height=40, corner_radius=8,
                             border_color=border_color, border_width=1,
                             fg_color=bg_color, text_color="#333", font=("Arial", 13))
        if is_pass: entry.configure(show="•")
        entry.pack(fill="x")
        entry.configure(state=state)
        return entry

    def create_readonly_row(self, parent, label, attr_name):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(f, text=label, font=("Arial", 12), text_color="gray").pack(side="left")
        val_label = ctk.CTkLabel(f, text="...", font=("Arial", 12, "bold"), text_color="#333")
        val_label.pack(side="right")
        setattr(self, attr_name, val_label)

    # ================= LOGIC XỬ LÝ =================
    def load_data(self):
        """Lấy thông tin dựa trên self.user_id được truyền vào"""
        data = self.controller.get_info(self.user_id)

        if data:
            self.account_data = data

            # Cập nhật Avatar
            first_letter = data['hoTen'][0].upper() if data['hoTen'] else "?"
            self.lbl_avatar_text.configure(text=first_letter)
            self.lbl_display_name.configure(text=data['hoTen'])
            self.lbl_display_role.configure(text=data['tenChucVu'])

            # Cập nhật Info Readonly
            self.entry_id.configure(text=f"NV-{data['idNhanVien']}")
            self.entry_username.configure(text=data['tenDangNhap'])
            create_date = str(data['ngayTao']).split(' ')[0] if data['ngayTao'] else "N/A"
            self.entry_date.configure(text=create_date)

            # Cập nhật Info Inputs
            self.set_val(self.entry_fullname, data['hoTen'])
            self.set_val(self.entry_phone, data['soDienThoai'])
            self.set_val(self.entry_email, data['email'])

            self.lock_edit(True)
        else:
            messagebox.showerror("Lỗi", f"Không tìm thấy dữ liệu cho NV ID: {self.user_id}")

    def set_val(self, entry, val):
        prev = entry.cget("state")
        entry.configure(state="normal")
        entry.delete(0, "end")
        entry.insert(0, str(val) if val else "")
        entry.configure(state=prev)

    def lock_edit(self, locked=True):
        self.is_editing = not locked
        state = "disabled" if locked else "normal"
        bg_color = "#F9F9F9" if locked else "#FFFFFF"
        border_color = "#E0E0E0" if locked else "#2979FF"

        for e in [self.entry_fullname, self.entry_phone, self.entry_email]:
            e.configure(state=state, fg_color=bg_color, border_color=border_color)

        if locked:
            self.btn_edit.configure(text="Chỉnh Sửa", fg_color="#2979FF")
            self.btn_save.configure(state="disabled", fg_color="#B0BEC5")
        else:
            self.btn_edit.configure(text="Hủy Bỏ", fg_color="#757575")
            self.btn_save.configure(state="normal", fg_color="#00C853")
            self.entry_fullname.focus()

    def toggle_edit(self):
        if self.is_editing:
            self.load_data()
        else:
            self.lock_edit(False)

    def save_info(self):
        if not self.entry_fullname.get().strip():
            messagebox.showwarning("Cảnh báo", "Họ tên không được để trống!")
            return

        ok, msg = self.controller.save_info(
            self.user_id,
            self.entry_fullname.get(),
            self.entry_phone.get(),
            self.entry_email.get()
        )
        if ok:
            messagebox.showinfo("Thành công", msg)
            self.load_data()
        else:
            messagebox.showerror("Lỗi", msg)

    def change_pass(self):
        old = self.entry_old_pass.get()
        new = self.entry_new_pass.get()
        confirm = self.entry_confirm_pass.get()

        ok, msg = self.controller.change_password(
            self.account_data['idTaiKhoan'], old, new, confirm
        )

        if ok:
            messagebox.showinfo("Thành công", msg)
            self.entry_old_pass.delete(0, "end")
            self.entry_new_pass.delete(0, "end")
            self.entry_confirm_pass.delete(0, "end")
        else:
            messagebox.showerror("Lỗi", msg)