import customtkinter as ctk
from tkinter import messagebox
from src.Controller.DangKyController import DangKyController

# from sqlalchemy.orm import Session  # Mở comment nếu muốn lưu vào DB
# from models import init_db, TaiKhoanNhanVien, NhanVien # Mở comment nếu muốn lưu vào DB

class RegisterPage(ctk.CTkFrame):
    def __init__(self, parent, on_back_command):
        super().__init__(parent, fg_color="white")
        self.on_back_command = on_back_command
        # Khởi tạo Controller
        self.controller = DangKyController(self)

        self.tao_giao_dien()

    def tao_giao_dien(self):
        # Tạo một khung chứa ở giữa màn hình (Card layout)
        self.center_frame = ctk.CTkFrame(self, width=400, fg_color="#f5f5f5", corner_radius=15, border_width=1,
                                         border_color="#ddd")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # ===== Tiêu đề =====
        ctk.CTkLabel(self.center_frame, text="ĐĂNG KÝ TÀI KHOẢN", font=("Arial", 22, "bold"),
                     text_color="#1a237e").pack(pady=(30, 20))

        # ===== Ô nhập tài khoản =====
        self.create_entry("🧑", "Tên đăng nhập", "user")

        # ===== Ô nhập email =====
        self.create_entry("📧", "Email", "email")

        # ===== Ô nhập mật khẩu =====
        self.entry_pw = self.create_entry("🔒", "Mật khẩu", "pass", is_pass=True)

        # ===== Ô nhập lại mật khẩu =====
        self.entry_confirm = self.create_entry("🔒", "Nhập lại mật khẩu", "confirm", is_pass=True)

        # ===== Nút chức năng =====
        button_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        button_frame.pack(pady=(20, 30))

        ctk.CTkButton(button_frame, text="Đăng ký", width=140, height=40,
                      fg_color="#4CAF50", hover_color="#45a049", font=("Arial", 12, "bold"),
                      command=self.xu_ly_dang_ky).pack(side="left", padx=10)

        ctk.CTkButton(button_frame, text="Quay lại", width=100, height=40,
                      fg_color="#9E9E9E", hover_color="#757575", text_color="white", font=("Arial", 12, "bold"),
                      command=self.on_back_command).pack(side="left", padx=10)

    def create_entry(self, icon, placeholder, tag, is_pass=False):
        frame = ctk.CTkFrame(self.center_frame, fg_color="white", border_width=1, border_color="#ccc", corner_radius=8)
        frame.pack(pady=8, padx=40, fill="x")

        ctk.CTkLabel(frame, text=icon, font=("Arial", 16), width=30).pack(side="left", padx=(5, 5))

        entry = ctk.CTkEntry(frame, placeholder_text=placeholder, border_width=0, fg_color="white", height=35)
        entry.pack(side="left", fill="x", expand=True)

        if is_pass:
            entry.configure(show="*")
            btn_eye = ctk.CTkButton(frame, text="👁️", width=30, fg_color="transparent", hover_color="#eee",
                                    text_color="#333",
                                    command=lambda: self.toggle_password(entry, btn_eye))
            btn_eye.pack(side="right", padx=5)

        # Lưu reference để lấy dữ liệu sau này
        if tag == "user":
            self.entry_user = entry
        elif tag == "email":
            self.entry_email = entry

        return entry

    def toggle_password(self, entry_widget, btn_widget):
        if entry_widget.cget("show") == "*":
            entry_widget.configure(show="")
            btn_widget.configure(text="🙈")
        else:
            entry_widget.configure(show="*")
            btn_widget.configure(text="👁️")

    def xu_ly_dang_ky(self):
        # Chuyển toàn bộ trách nhiệm sang Controller
        self.controller.xu_ly_dang_ky()