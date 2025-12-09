import customtkinter as ctk
from tkinter import messagebox
from src.Controller.QuenMKController import QuenMKController


class ForgotPasswordPage(ctk.CTkFrame):
    def __init__(self, parent, on_back_command):
        super().__init__(parent, fg_color="white")
        self.on_back_command = on_back_command
        self.controller = QuenMKController()

        # Khung chính
        self.center_frame = ctk.CTkFrame(self, width=400, fg_color="#f5f5f5",
                                         corner_radius=15, border_width=1, border_color="#ddd")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Bắt đầu ở bước 1
        self.step_1_input_info()

    # ================= BƯỚC 1: NHẬP THÔNG TIN =================
    def step_1_input_info(self):
        self.clear_frame()
        ctk.CTkLabel(self.center_frame, text="QUÊN MẬT KHẨU", font=("Arial", 18, "bold"), text_color="#1a237e").pack(
            pady=(30, 10))
        ctk.CTkLabel(self.center_frame, text="Nhập tài khoản và email để nhận mã OTP", font=("Arial", 12)).pack(
            pady=(0, 20))

        self.entry_user = self.create_entry("🧑", "Tài khoản")
        self.entry_email = self.create_entry("📧", "Email")

        self.create_nav_buttons(self.xu_ly_gui_otp, "Gửi Mã OTP")

    def xu_ly_gui_otp(self):
        user = self.entry_user.get()
        email = self.entry_email.get()
        if not user or not email:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ!")
            return

        # Hiện loading (giả lập bằng cách đổi trỏ chuột)
        self.configure(cursor="watch")
        self.update()

        success, msg = self.controller.gui_ma_xac_nhan(user, email)

        self.configure(cursor="")
        if success:
            messagebox.showinfo("Đã gửi", msg)
            self.step_2_verify_otp(email)  # Chuyển sang bước 2
        else:
            messagebox.showerror("Lỗi", msg)

    # ================= BƯỚC 2: NHẬP MÃ OTP =================
    def step_2_verify_otp(self, email):
        self.clear_frame()
        ctk.CTkLabel(self.center_frame, text="XÁC THỰC OTP", font=("Arial", 18, "bold"), text_color="#1a237e").pack(
            pady=(30, 10))
        ctk.CTkLabel(self.center_frame, text=f"Mã đã gửi đến: {email}", font=("Arial", 12)).pack(pady=(0, 20))

        self.entry_otp = self.create_entry("🔑", "Nhập mã 6 số")

        # Nút xác nhận
        btn_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        btn_frame.pack(pady=20)
        ctk.CTkButton(btn_frame, text="Xác nhận", width=120, command=self.xu_ly_xac_thuc).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Gửi lại mã", width=100, fg_color="#FF9800", command=self.step_1_input_info).pack(
            side="left", padx=5)

    def xu_ly_xac_thuc(self):
        otp = self.entry_otp.get()
        success, msg = self.controller.xac_thuc_otp(otp)
        if success:
            self.step_3_reset_pass()  # Chuyển sang bước 3
        else:
            messagebox.showerror("Sai mã", msg)

    # ================= BƯỚC 3: ĐỔI MẬT KHẨU MỚI =================
    def step_3_reset_pass(self):
        self.clear_frame()
        ctk.CTkLabel(self.center_frame, text="ĐẶT MẬT KHẨU MỚI", font=("Arial", 18, "bold"), text_color="#4CAF50").pack(
            pady=(30, 20))

        self.entry_new = self.create_entry("🔒", "Mật khẩu mới", is_pass=True)
        self.entry_confirm = self.create_entry("🔒", "Nhập lại mật khẩu", is_pass=True)

        ctk.CTkButton(self.center_frame, text="Đổi Mật Khẩu", width=200, height=40, fg_color="#4CAF50",
                      command=self.xu_ly_doi_mk).pack(pady=20)

    def xu_ly_doi_mk(self):
        new_p = self.entry_new.get()
        conf_p = self.entry_confirm.get()
        success, msg = self.controller.luu_mat_khau_moi(new_p, conf_p)
        if success:
            messagebox.showinfo("Thành công", msg)
            self.on_back_command()  # Quay về đăng nhập
        else:
            messagebox.showerror("Lỗi", msg)

    # ================= HELPERS =================
    def clear_frame(self):
        for widget in self.center_frame.winfo_children():
            widget.destroy()

    def create_entry(self, icon, placeholder, is_pass=False):
        f = ctk.CTkFrame(self.center_frame, fg_color="white", border_width=1, border_color="#ccc")
        f.pack(pady=8, padx=30, fill="x")
        ctk.CTkLabel(f, text=icon, width=30).pack(side="left")
        e = ctk.CTkEntry(f, placeholder_text=placeholder, border_width=0, height=35)
        e.pack(side="left", fill="x", expand=True)
        if is_pass: e.configure(show="*")
        return e

    def create_nav_buttons(self, next_cmd, next_text):
        f = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        f.pack(pady=20)
        ctk.CTkButton(f, text=next_text, width=120, command=next_cmd).pack(side="left", padx=5)
        ctk.CTkButton(f, text="Hủy", width=80, fg_color="#999", command=self.on_back_command).pack(side="left", padx=5)