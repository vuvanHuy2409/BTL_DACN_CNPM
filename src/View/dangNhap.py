import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk  # [QUAN TRỌNG] Import thêm thư viện xử lý ảnh
import os

from src.Controller.DangNhapController import DangNhapController


class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, on_login_success, on_show_forgot_pass):
        super().__init__(parent, fg_color="white")

        self.on_login_success = on_login_success
        self.on_show_forgot_pass = on_show_forgot_pass

        self.controller = DangNhapController()

        self.tao_giao_dien()

    def tao_giao_dien(self):
        # ========================================================================
        # 1. [MỚI] THÊM ẢNH NỀN (BACKGROUND)
        # ========================================================================
        image_path = "src/images/anhnen.jpg"

        # Kiểm tra xem file có tồn tại không để tránh lỗi crash app
        if os.path.exists(image_path):
            try:
                # Mở ảnh bằng PIL
                pil_image = Image.open(image_path)

                # Tạo CTkImage
                # size=(1920, 1080): Đặt kích thước lớn để bao phủ màn hình.
                # Bạn có thể chỉnh lại tùy theo độ phân giải mong muốn.
                self.bg_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(1920, 1080))

                # Tạo Label chứa ảnh
                self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")

                # Đặt Label full màn hình (relwidth=1, relheight=1)
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            except Exception as e:
                print(f"Lỗi load ảnh nền: {e}")
        else:
            print(f"Cảnh báo: Không tìm thấy file ảnh tại {image_path}")

        # ========================================================================
        # 2. KHUNG FORM ĐĂNG NHẬP (NỔI LÊN TRÊN)
        # ========================================================================

        self.center_frame = ctk.CTkFrame(self, width=400, fg_color="#f5f5f5", corner_radius=15, border_width=1,
                                         border_color="#ddd")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Tiêu đề
        ctk.CTkLabel(self.center_frame, text="ĐĂNG NHẬP", font=("Arial", 22, "bold"), text_color="#1a237e").pack(
            pady=(30, 20))

        # --- Ô nhập Tài khoản (Viền đen) ---
        frame_user = ctk.CTkFrame(self.center_frame, fg_color="white",
                                  border_width=2, border_color="black",
                                  corner_radius=8)
        frame_user.pack(pady=10, padx=40, fill="x")

        ctk.CTkLabel(frame_user, text="🧑", font=("Arial", 16), width=30).pack(side="left", padx=(5, 5))
        self.username_entry = ctk.CTkEntry(frame_user, placeholder_text="Tài khoản", border_width=0,
                                           fg_color="white", text_color="black", height=35)
        self.username_entry.pack(side="left", fill="x", expand=True)

        # --- Ô nhập Mật khẩu (Viền đen) ---
        frame_pass = ctk.CTkFrame(self.center_frame, fg_color="white",
                                  border_width=2, border_color="black",
                                  corner_radius=8)
        frame_pass.pack(pady=10, padx=40, fill="x")

        ctk.CTkLabel(frame_pass, text="🔒", font=("Arial", 16), width=30).pack(side="left", padx=(5, 5))
        self.password_entry = ctk.CTkEntry(frame_pass, placeholder_text="Mật khẩu", show="*", border_width=0,
                                           fg_color="white", text_color="black", height=35)
        self.password_entry.pack(side="left", fill="x", expand=True)

        self.eye_button = ctk.CTkButton(frame_pass, text="👁️", width=30, fg_color="transparent", hover_color="#eee",
                                        text_color="#333", command=self.toggle_password)
        self.eye_button.pack(side="right", padx=5)

        # --- Nút Đăng nhập ---
        ctk.CTkButton(self.center_frame, text="Đăng nhập", width=200, height=40,
                      fg_color="#2196F3", hover_color="#1976D2", font=("Arial", 12, "bold"),
                      command=self.xu_ly_dang_nhap).pack(pady=(25, 15))

        # Nút Quên mật khẩu
        ctk.CTkButton(self.center_frame, text="Quên mật khẩu?", fg_color="transparent", text_color="#555",
                      hover_color="#eee",
                      font=("Arial", 11, "underline"), command=self.on_show_forgot_pass).pack(pady=(0, 20))

        # Sự kiện phím Enter
        self.username_entry.focus()
        self.username_entry.bind("<Return>", lambda e: self.xu_ly_dang_nhap())
        self.password_entry.bind("<Return>", lambda e: self.xu_ly_dang_nhap())

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

        ket_qua = self.controller.xu_ly_dang_nhap(username, password)

        if ket_qua["status"]:
            self.on_login_success(username)
        else:
            messagebox.showerror("Lỗi đăng nhập", ket_qua["message"])