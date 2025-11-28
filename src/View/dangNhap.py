import customtkinter as ctk
from tkinter import messagebox
# 1. IMPORT CONTROLLER
from src.Controller.DangNhapController import DangNhapController # <--- THÊM DÒNG NÀY

class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, on_login_success, on_show_register, on_show_forgot_pass):
        super().__init__(parent, fg_color="white")

        self.on_login_success = on_login_success
        self.on_show_register = on_show_register
        self.on_show_forgot_pass = on_show_forgot_pass

        # 2. KHỞI TẠO CONTROLLER
        self.controller = DangNhapController() # <--- THÊM DÒNG NÀY

        self.tao_giao_dien()

    def tao_giao_dien(self):
        # ... (GIỮ NGUYÊN CODE GIAO DIỆN CỦA BẠN TỪ ĐÂY) ...
        self.center_frame = ctk.CTkFrame(self, width=400, fg_color="#f5f5f5", corner_radius=15, border_width=1,
                                         border_color="#ddd")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.center_frame, text="ĐĂNG NHẬP", font=("Arial", 22, "bold"), text_color="#1a237e").pack(
            pady=(30, 20))

        frame_user = ctk.CTkFrame(self.center_frame, fg_color="white", border_width=1, border_color="#ccc",
                                  corner_radius=8)
        frame_user.pack(pady=10, padx=40, fill="x")

        ctk.CTkLabel(frame_user, text="🧑", font=("Arial", 16), width=30).pack(side="left", padx=(5, 5))
        self.username_entry = ctk.CTkEntry(frame_user, placeholder_text="Tài khoản", border_width=0, fg_color="white",
                                           height=35)
        self.username_entry.pack(side="left", fill="x", expand=True)

        frame_pass = ctk.CTkFrame(self.center_frame, fg_color="white", border_width=1, border_color="#ccc",
                                  corner_radius=8)
        frame_pass.pack(pady=10, padx=40, fill="x")

        ctk.CTkLabel(frame_pass, text="🔒", font=("Arial", 16), width=30).pack(side="left", padx=(5, 5))
        self.password_entry = ctk.CTkEntry(frame_pass, placeholder_text="Mật khẩu", show="*", border_width=0,
                                           fg_color="white", height=35)
        self.password_entry.pack(side="left", fill="x", expand=True)

        self.eye_button = ctk.CTkButton(frame_pass, text="👁️", width=30, fg_color="transparent", hover_color="#eee",
                                        text_color="#333", command=self.toggle_password)
        self.eye_button.pack(side="right", padx=5)

        button_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        button_frame.pack(pady=(20, 30))

        ctk.CTkButton(button_frame, text="Đăng nhập", width=120, height=40,
                      fg_color="#2196F3", hover_color="#1976D2", font=("Arial", 12, "bold"),
                      command=self.xu_ly_dang_nhap).pack(side="left", padx=5)

        ctk.CTkButton(button_frame, text="Đăng ký", width=100, height=40,
                      fg_color="#4CAF50", hover_color="#45a049", font=("Arial", 12, "bold"),
                      command=self.on_show_register).pack(side="left", padx=5)

        ctk.CTkButton(self.center_frame, text="Quên mật khẩu?", fg_color="transparent", text_color="#555",
                      hover_color="#eee",
                      font=("Arial", 11, "underline"), command=self.on_show_forgot_pass).pack(pady=(0, 20))

        self.username_entry.focus()
        self.username_entry.bind("<Return>", lambda e: self.xu_ly_dang_nhap())
        self.password_entry.bind("<Return>", lambda e: self.xu_ly_dang_nhap())
        # ... (KẾT THÚC PHẦN GIAO DIỆN GIỮ NGUYÊN) ...

    def toggle_password(self):
        if self.password_entry.cget("show") == "*":
            self.password_entry.configure(show="")
            self.eye_button.configure(text="🙈")
        else:
            self.password_entry.configure(show="*")
            self.eye_button.configure(text="👁️")

    def xu_ly_dang_nhap(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin!")
            return

        # --- GỌI CONTROLLER (Đã thay đổi đoạn này) ---
        ket_qua = self.controller.xu_ly_dang_nhap(username, password)

        if ket_qua["status"]:
            # Đăng nhập thành công -> Chuyển trang và gửi kèm data user
            self.on_login_success(username) 
        else:
            # Đăng nhập thất bại -> Hiện thông báo từ Controller
            messagebox.showerror("Lỗi đăng nhập", ket_qua["message"])