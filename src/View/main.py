import customtkinter as ctk
import platform
from tkinter import messagebox

# --- 1. IMPORT CÁC THÀNH PHẦN GIAO DIỆN CHUNG ---
from sideBar import Sidebar

# --- 2. IMPORT CÁC TRANG XÁC THỰC (LOGIN/REGISTER) ---
from dangNhap import LoginPage
from dangKy import RegisterPage
from quenMK import ForgotPasswordPage

# --- 3. IMPORT CÁC TRANG CHỨC NĂNG (MODULES) ---
from trangChu import MenuPage
from khachHang import KhachHangPage
from qlKho import KhoPage
from qlSanPham import SanPhamPage
from qlDiemDanh import DiemDanhPage
from qlHoaDon import HoaDonPage
from qlTaiKhoan import QuanLyTKPage
from qlNCC import NhaCungCapPage
from qlNhanVien import NhanVienPage
from qlThongKe import ThongKePage
from nganHang import NganHangPage
from luong import LuongPage
from taiKhoan import TaiKhoanPage

# Cấu hình giao diện chung
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class MainApp:
    def __init__(self):
        # Khởi tạo cửa sổ chính
        self.root = ctk.CTk()
        self.root.title("HỆ THỐNG QUẢN LÝ QUÁN COFFEE")

        # Cấu hình Full màn hình
        system = platform.system()
        if system == "Windows":
            self.root.after(10, lambda: self.root.state("zoomed"))
        else:
            w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
            self.root.geometry(f"{w}x{h}+0+0")

        # Biến theo dõi các khung giao diện
        self.current_auth_frame = None
        self.sidebar = None
        self.content_container = None
        self.current_page = None

        # [QUAN TRỌNG] Biến lưu ID người dùng đang đăng nhập
        self.current_user_id = None

        # Bắt đầu ứng dụng bằng màn hình Đăng nhập
        self.show_login()

        # Chạy vòng lặp chính
        self.root.mainloop()

    # =========================================================================
    # PHẦN 1: QUẢN LÝ XÁC THỰC
    # =========================================================================

    def show_login(self):
        """Hiển thị màn hình Đăng nhập"""
        self.clear_all_frames() # Xóa sạch giao diện cũ
        self.current_auth_frame = LoginPage(
            self.root,
            on_login_success=self.start_main_app,
            on_show_forgot_pass=self.show_forgot_password
        )
        self.current_auth_frame.pack(fill="both", expand=True)

    def show_register(self):
        self.clear_all_frames()
        self.current_auth_frame = RegisterPage(self.root, on_back_command=self.show_login)
        self.current_auth_frame.pack(fill="both", expand=True)

    def show_forgot_password(self):
        self.clear_all_frames()
        self.current_auth_frame = ForgotPasswordPage(self.root, on_back_command=self.show_login)
        self.current_auth_frame.pack(fill="both", expand=True)

    def clear_all_frames(self):
        """Xóa sạch mọi thứ trên màn hình để chuyển trạng thái"""
        # 1. Xóa trang nội dung (Menu, Kho...)
        if self.current_page:
            self.current_page.destroy()
            self.current_page = None

        # 2. Xóa Sidebar
        if self.sidebar:
            self.sidebar.destroy()
            self.sidebar = None

        # 3. Xóa Container chính
        if self.content_container:
            self.content_container.destroy()
            self.content_container = None

        # 4. Xóa Frame Auth (Login/Register)
        if self.current_auth_frame:
            self.current_auth_frame.destroy()
            self.current_auth_frame = None

    # =========================================================================
    # PHẦN 2: ỨNG DỤNG CHÍNH
    # =========================================================================

    def start_main_app(self, username):
        """Khởi động giao diện chính sau khi login thành công"""
        # Giả lập lấy ID (Thực tế bạn lấy từ kết quả login)
        self.current_user_id = 1
        print(f"Đăng nhập thành công: {username} (ID: {self.current_user_id})")

        self.clear_all_frames() # Xóa màn hình login

        # 1. Tạo Sidebar bên trái
        self.sidebar = Sidebar(self.root, username=username, on_change_page_command=self.switch_page)
        self.sidebar.pack(side="left", fill="y")

        # 2. Tạo Container chứa nội dung bên phải
        self.content_container = ctk.CTkFrame(self.root, fg_color="white")
        self.content_container.pack(side="right", fill="both", expand=True)

        # 3. Mặc định vào trang Menu
        self.switch_page("menu")
        self.sidebar.handle_click("menu")

    def switch_page(self, page_key):
        """Điều hướng giữa các module"""

        # --- XỬ LÝ ĐĂNG XUẤT ---
        if page_key == "logout":
            if messagebox.askyesno("Đăng xuất", "Bạn có chắc muốn đăng xuất?"):
                # Reset thông tin người dùng
                self.current_user_id = None
                # Quay về màn hình đăng nhập
                self.show_login()
            return

        # 1. Xóa nội dung trang cũ
        if self.current_page:
            self.current_page.destroy()
            self.current_page = None

        # 2. Map Key -> Class
        pages_map = {
            "menu": MenuPage,
            "Khach_Hang": KhachHangPage,
            "QL_Kho": KhoPage,
            "QL_SP": SanPhamPage,
            "QL_DD": DiemDanhPage,
            "QL_HD": HoaDonPage,
            "QL_TK": QuanLyTKPage,
            "QL_NCC": NhaCungCapPage,
            "QL_NV": NhanVienPage,
            "QL_ThongKe": ThongKePage,
            "Ngan_hang": NganHangPage,
            "Luong": LuongPage,
            "TaiKhoan": TaiKhoanPage
        }

        # 3. Khởi tạo trang mới
        if page_key in pages_map:
            page_class = pages_map[page_key]

            # Kiểm tra nếu là TaiKhoanPage thì truyền current_user_id
            if page_key == "TaiKhoan":
                self.current_page = page_class(self.content_container, current_user_id=self.current_user_id)
            elif page_key == "menu":
                self.current_page = page_class(self.content_container)
            else:
                self.current_page = page_class(self.content_container)

            self.current_page.pack(fill="both", expand=True)
        else:
            print(f"⚠ Không tìm thấy module cho key: {page_key}")
            self.current_page = ctk.CTkLabel(self.content_container, text=f"Trang {page_key} đang phát triển")
            self.current_page.pack(expand=True)


if __name__ == "__main__":
    app = MainApp()