import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os

from src.Controller.DangNhapController import DangNhapController


class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, on_login_success, on_show_forgot_pass):
        """
        on_login_success: Hàm callback nhận 3 tham số (username, user_id, role_name)
        """
        super().__init__(parent, fg_color="white")

        self.on_login_success = on_login_success
        self.on_show_forgot_pass = on_show_forgot_pass

        self.controller = DangNhapController()

        # Biến lưu trữ icon
        self.icon_user = None
        self.icon_pass = None
        self.icon_eye_open = None
        self.icon_eye_closed = None

        self.load_icons()
        self.tao_giao_dien()

    def load_icons(self):
        """Hàm hỗ trợ tải icon từ file"""

        def get_img(filename, size):
            # Đảm bảo đường dẫn đúng tới thư mục icon của bạn
            path = f"src/images/icon/{filename}"
            if os.path.exists(path):
                return ctk.CTkImage(Image.open(path), size=size)
            return None

        self.icon_user = get_img("user.png", (20, 20))
        self.icon_pass = get_img("lock.png", (20, 20))
        self.icon_eye_open = get_img("show.png", (20, 20))
        self.icon_eye_closed = get_img("eye.png", (20, 20))

    def tao_giao_dien(self):
        # 1. ẢNH NỀN
        image_path = "src/images/anhnen.jpg"
        if os.path.exists(image_path):
            try:
                pil_image = Image.open(image_path)
                self.bg_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(1920, 1080))
                self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            except Exception as e:
                print(f"Lỗi load ảnh nền: {e}")

        # 2. KHUNG ĐĂNG NHẬP
        self.center_frame = ctk.CTkFrame(self, width=400, fg_color="#f5f5f5", corner_radius=15, border_width=1,
                                         border_color="#ddd")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.center_frame, text="ĐĂNG NHẬP", font=("Arial", 22, "bold"), text_color="#1a237e").pack(
            pady=(30, 20))

        # --- Ô TÀI KHOẢN ---
        frame_user = ctk.CTkFrame(self.center_frame, fg_color="white", border_width=1, border_color="#ccc",
                                  corner_radius=8)
        frame_user.pack(pady=10, padx=40, fill="x")

        ctk.CTkLabel(frame_user, text="", image=self.icon_user, width=40).pack(side="left", padx=(5, 0))
        self.username_entry = ctk.CTkEntry(frame_user, placeholder_text="Tài khoản", border_width=0, fg_color="white",
                                           text_color="black", height=35)
        self.username_entry.pack(side="left", fill="x", expand=True)

        # --- Ô MẬT KHẨU ---
        frame_pass = ctk.CTkFrame(self.center_frame, fg_color="white", border_width=1, border_color="#ccc",
                                  corner_radius=8)
        frame_pass.pack(pady=10, padx=40, fill="x")

        ctk.CTkLabel(frame_pass, text="", image=self.icon_pass, width=40).pack(side="left", padx=(5, 0))
        self.password_entry = ctk.CTkEntry(frame_pass, placeholder_text="Mật khẩu", show="*", border_width=0,
                                           fg_color="white", text_color="black", height=35)
        self.password_entry.pack(side="left", fill="x", expand=True)

        self.eye_button = ctk.CTkButton(frame_pass, text="", image=self.icon_eye_open, width=30, fg_color="transparent",
                                        hover_color="#eee", command=self.toggle_password)
        self.eye_button.pack(side="right", padx=5)

        # --- NÚT BẤM ---
        ctk.CTkButton(self.center_frame, text="Đăng nhập", width=200, height=40, fg_color="#2196F3",
                      hover_color="#1976D2", font=("Arial", 12, "bold"), command=self.xu_ly_dang_nhap).pack(
            pady=(25, 15))

        ctk.CTkButton(self.center_frame, text="Quên mật khẩu?", fg_color="transparent", text_color="#555",
                      hover_color="#eee", font=("Arial", 11, "underline"), command=self.on_show_forgot_pass).pack(
            pady=(0, 20))

        # Bind phím Enter
        self.username_entry.focus()
        self.username_entry.bind("<Return>", lambda e: self.xu_ly_dang_nhap())
        self.password_entry.bind("<Return>", lambda e: self.xu_ly_dang_nhap())

    def toggle_password(self):
        if self.password_entry.cget("show") == "*":
            self.password_entry.configure(show="")
            if self.icon_eye_closed: self.eye_button.configure(image=self.icon_eye_closed)
        else:
            self.password_entry.configure(show="*")
            if self.icon_eye_open: self.eye_button.configure(image=self.icon_eye_open)

    # --- [PHẦN SỬA ĐỔI QUAN TRỌNG] ---
    def xu_ly_dang_nhap(self):
        username_input = self.username_entry.get().strip()
        password_input = self.password_entry.get().strip()

        if not username_input or not password_input:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin!")
            return

        # Gọi Controller kiểm tra
        # Controller trả về: { "status": True, "data": { "id_nhan_vien": 1, "ho_ten": "A", "role_name": "QuanLy" } }
        ket_qua = self.controller.xu_ly_dang_nhap(username_input, password_input)

        if ket_qua["status"]:
            # Lấy data từ kết quả trả về
            data = ket_qua.get("data", {})

            user_id = data.get("id_nhan_vien")
            full_name = data.get("ho_ten")  # Lấy tên thật từ DB (ví dụ: "Nguyễn Văn A")
            role_name = data.get("role_name")  # [QUAN TRỌNG] Lấy chức vụ để phân quyền

            # Truyền đủ 3 tham số vào MainApp
            if self.on_login_success:
                # Tham số 1: Tên hiển thị trên Sidebar
                # Tham số 2: ID để xử lý logic
                # Tham số 3: Role để check quyền
                self.on_login_success(full_name, user_id, role_name)
        else:
            messagebox.showerror("Lỗi đăng nhập", ket_qua["message"])