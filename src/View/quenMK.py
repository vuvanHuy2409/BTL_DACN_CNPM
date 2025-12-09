import customtkinter as ctk
from tkinter import messagebox


class ForgotPasswordPage(ctk.CTkFrame):
    def __init__(self, parent, on_back_command):
        # 1. Kế thừa Frame
        super().__init__(parent, fg_color="white")
        self.on_back_command = on_back_command

        # 2. Tạo khung chứa nội dung ở giữa (Card Layout)
        self.center_frame = ctk.CTkFrame(self, width=400, fg_color="#f5f5f5",
                                         corner_radius=15, border_width=1, border_color="#ddd")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Mặc định hiển thị Bước 1: Xác thực thông tin
        self.setup_step_1_ui()

    # ================= BƯỚC 1: XÁC THỰC USERNAME & EMAIL =================
    def setup_step_1_ui(self):
        # Xóa các widget cũ (nếu có)
        for widget in self.center_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.center_frame, text="QUÊN MẬT KHẨU", font=("Arial", 18, "bold"), text_color="#1a237e").pack(
            pady=(30, 20))

        # Input Tài khoản
        self.entry_user = self.create_entry("🧑", "Tài khoản")

        # Input Email
        self.entry_email = self.create_entry("📧", "Email")

        # Nút bấm
        btn_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        btn_frame.pack(pady=(20, 30))

        ctk.CTkButton(btn_frame, text="Tiếp tục", width=120, height=40,
                      fg_color="#2196F3", hover_color="#1976D2", font=("Arial", 12, "bold"),
                      command=self.xac_thuc_thong_tin).pack(side="left", padx=10)

        ctk.CTkButton(btn_frame, text="Quay lại", width=100, height=40,
                      fg_color="#9E9E9E", hover_color="#757575", text_color="white", font=("Arial", 12, "bold"),
                      command=self.on_back_command).pack(side="left", padx=10)

    # ================= BƯỚC 2: ĐỔI MẬT KHẨU MỚI =================
    def setup_step_2_ui(self):
        # Xóa giao diện bước 1
        for widget in self.center_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.center_frame, text="ĐẶT LẠI MẬT KHẨU", font=("Arial", 20, "bold"), text_color="#1a237e").pack(
            pady=(30, 20))

        ctk.CTkLabel(self.center_frame, text=f"Xin chào: {self.verified_user}", font=("Arial", 12),
                     text_color="#333").pack(pady=(0, 10))

        # Input Mật khẩu mới
        self.entry_new_pass = self.create_entry("🔒", "Mật khẩu mới", is_pass=True)

        # Input Xác nhận mật khẩu
        self.entry_confirm_pass = self.create_entry("🔒", "Nhập lại mật khẩu", is_pass=True)

        # Nút bấm
        btn_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        btn_frame.pack(pady=(20, 30))

        ctk.CTkButton(btn_frame, text="Xác nhận", width=120, height=40,
                      fg_color="#4CAF50", hover_color="#45a049", font=("Arial", 12, "bold"),
                      command=self.luu_mat_khau_moi).pack(side="left", padx=10)

        ctk.CTkButton(btn_frame, text="Hủy", width=100, height=40,
                      fg_color="#9E9E9E", hover_color="#757575", text_color="white", font=("Arial", 12, "bold"),
                      command=self.on_back_command).pack(side="left", padx=10)

    # ================= HELPERS & LOGIC =================
    def create_entry(self, icon, placeholder, is_pass=False):
        frame = ctk.CTkFrame(self.center_frame, fg_color="white", border_width=1, border_color="#ccc", corner_radius=8)
        frame.pack(pady=8, padx=40, fill="x")

        ctk.CTkLabel(frame, text=icon, font=("Arial", 16), width=30).pack(side="left", padx=(5, 5))
        entry = ctk.CTkEntry(frame, placeholder_text=placeholder, border_width=0, fg_color="white", height=35)
        entry.pack(side="left", fill="x", expand=True)

        if is_pass:
            entry.configure(show="*")
            btn_eye = ctk.CTkButton(frame, text="👁️", width=30, fg_color="transparent", hover_color="#eee",
                                    text_color="#333",
                                    command=lambda: self.toggle_pw(entry, btn_eye))
            btn_eye.pack(side="right", padx=5)

        return entry

    def toggle_pw(self, entry, btn):
        if entry.cget("show") == "*":
            entry.configure(show="")
            btn.configure(text="🙈")
        else:
            entry.configure(show="*")
            btn.configure(text="👁️")

    def xac_thuc_thong_tin(self):
        user = self.entry_user.get().strip()
        email = self.entry_email.get().strip()

        if not user or not email:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin!")
            return

        # --- LOGIC KIỂM TRA DB (Giả lập) ---
        # if check_database(user, email):
        if True:  # Giả sử đúng
            self.verified_user = user
            messagebox.showinfo("Thành công", "Thông tin chính xác. Vui lòng đặt lại mật khẩu.")
            self.setup_step_2_ui()  # Chuyển sang giao diện đổi pass
        else:
            messagebox.showerror("Lỗi", "Tài khoản hoặc Email không đúng!")

    def luu_mat_khau_moi(self):
        new_pass = self.entry_new_pass.get()
        confirm = self.entry_confirm_pass.get()

        if not new_pass:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập mật khẩu mới!")
            return

        if new_pass != confirm:
            messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp!")
            return

        # --- LOGIC LƯU DB ---
        # update_password(self.verified_user, new_pass)

        messagebox.showinfo("Thành công", "Đổi mật khẩu thành công!\nVui lòng đăng nhập lại.")
        self.on_back_command()  # Quay về màn hình đăng nhập