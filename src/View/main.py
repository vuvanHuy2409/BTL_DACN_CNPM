import customtkinter as ctk
import platform
from tkinter import messagebox

# --- 1. IMPORT CÁC THÀNH PHẦN GIAO DIỆN CHUNG ---
from sideBar import Sidebar

# --- 2. IMPORT CÁC TRANG XÁC THỰC ---
from dangNhap import LoginPage
from dangKy import RegisterPage
from quenMK import ForgotPasswordPage

# --- 3. IMPORT CÁC TRANG CHỨC NĂNG ---
# (Giữ nguyên các import của bạn)
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
# [LƯU Ý] Đảm bảo import đúng file TaiKhoanPage mới mà chúng ta vừa sửa
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
        self.clear_all_frames()
        self.current_auth_frame = LoginPage(
            self.root,
            on_login_success=self.start_main_app, # Callback khi đăng nhập thành công
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
        if self.current_page:
            self.current_page.destroy()
            self.current_page = None

        if self.sidebar:
            self.sidebar.destroy()
            self.sidebar = None

        if self.content_container:
            self.content_container.destroy()
            self.content_container = None

        if self.current_auth_frame:
            self.current_auth_frame.destroy()
            self.current_auth_frame = None

    # =========================================================================
    # PHẦN 2: ỨNG DỤNG CHÍNH
    # =========================================================================

    def start_main_app(self, username, user_id):
        """
        Khởi động giao diện chính sau khi login thành công.
        QUAN TRỌNG: Hàm này phải nhận thêm tham số user_id từ LoginPage
        """
        # 1. Lưu ID người dùng thực tế từ Database
        self.current_user_id = user_id
        print(f"➤ Đăng nhập thành công: User={username} | ID={self.current_user_id}")

        self.clear_all_frames() # Xóa màn hình login

        # 2. Tạo Sidebar
        self.sidebar = Sidebar(self.root, username=username, on_change_page_command=self.switch_page)
        self.sidebar.pack(side="left", fill="y")

        # 3. Tạo Container nội dung
        self.content_container = ctk.CTkFrame(self.root, fg_color="white")
        self.content_container.pack(side="right", fill="both", expand=True)

        # 4. Vào trang Menu
        self.switch_page("menu")
        self.sidebar.handle_click("menu")

    def switch_page(self, page_key):
        """Điều hướng giữa các module"""

        # --- XỬ LÝ ĐĂNG XUẤT ---
        if page_key == "logout":
            if messagebox.askyesno("Đăng xuất", "Bạn có chắc muốn đăng xuất?"):
                self.current_user_id = None
                self.show_login()
            return

        # 1. Xóa trang cũ
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

            # [QUAN TRỌNG] Kiểm tra nếu là TaiKhoanPage thì truyền ID vào
            if page_key == "TaiKhoan":
                # Truyền self.current_user_id (ID thật đã lưu khi login)
                self.current_page = page_class(self.content_container, current_user_id=self.current_user_id)
            elif page_key == "menu":
                self.current_page = page_class(self.content_container)
            else:
                # Các trang khác chưa cần ID thì khởi tạo bình thường
                # (Nếu sau này cần ID cho Hóa đơn/Điểm danh, bạn cũng truyền vào đây)
                self.current_page = page_class(self.content_container)

            self.current_page.pack(fill="both", expand=True)
        else:
            print(f"⚠ Không tìm thấy module cho key: {page_key}")
            # Trang 404
            self.current_page = ctk.CTkFrame(self.content_container)
            self.current_page.pack(fill="both", expand=True)
            ctk.CTkLabel(self.current_page, text=f"Trang {page_key} đang phát triển", font=("Arial", 20)).pack(pady=50)


if __name__ == "__main__":
    app = MainApp()