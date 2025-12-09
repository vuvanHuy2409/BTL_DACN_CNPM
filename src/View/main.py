import customtkinter as ctk
import platform
from tkinter import messagebox

# --- 1. IMPORT GIAO DIỆN CHUNG ---
from sideBar import Sidebar

# --- 2. IMPORT CÁC TRANG XÁC THỰC ---
from dangNhap import LoginPage
from dangKy import RegisterPage
from quenMK import ForgotPasswordPage

# --- 3. IMPORT CÁC TRANG CHỨC NĂNG ---
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

        # Biến quản lý các Frame
        self.current_auth_frame = None
        self.sidebar = None
        self.content_container = None
        self.current_page = None

        # --- BIẾN PHIÊN LÀM VIỆC (SESSION) ---
        self.current_user_id = None  # Lưu ID nhân viên
        self.current_user_role = None  # Lưu chức vụ (admin/nhanVien)

        # Chạy màn hình đăng nhập đầu tiên
        self.show_login()
        self.root.mainloop()

    # =========================================================================
    # PHẦN 1: QUẢN LÝ XÁC THỰC
    # =========================================================================

    def show_login(self):
        """Hiển thị màn hình Đăng nhập"""
        self.clear_all_frames()
        self.current_auth_frame = LoginPage(
            self.root,
            on_login_success=self.start_main_app,  # Callback nhận 3 tham số
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
        """Xóa sạch màn hình cũ trước khi chuyển sang màn hình mới"""
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
    # PHẦN 2: LOGIC CHÍNH VÀ PHÂN QUYỀN (RBAC)
    # =========================================================================

    def start_main_app(self, username, user_id, role_name):
        """
        Hàm này chạy sau khi Login thành công.
        :param role_name: Giá trị từ cột 'phanQuyen' trong DB (admin/nhanVien)
        """
        # 1. Lưu session
        self.current_user_id = user_id
        self.current_user_role = role_name

        # In ra console để kiểm tra (Debug)
        print(f"➤ Đăng nhập thành công: User='{username}' | ID={user_id} | Role='{role_name}'")

        # 2. Xóa màn hình login
        self.clear_all_frames()

        # 3. Tạo Sidebar
        self.sidebar = Sidebar(self.root, username=username, on_change_page_command=self.switch_page)
        self.sidebar.pack(side="left", fill="y")

        # 4. Tạo Container chứa nội dung
        self.content_container = ctk.CTkFrame(self.root, fg_color="white")
        self.content_container.pack(side="right", fill="both", expand=True)

        # 5. Vào trang mặc định (Menu)
        self.switch_page("menu")
        self.sidebar.handle_click("menu")

    def switch_page(self, page_key):
        """Chuyển trang có tích hợp kiểm tra quyền hạn (Admin vs NhanVien)"""

        # --- A. XỬ LÝ ĐĂNG XUẤT ---
        if page_key == "logout":
            if messagebox.askyesno("Đăng xuất", "Bạn có chắc muốn đăng xuất?"):
                self.current_user_id = None
                self.current_user_role = None
                self.show_login()
            return

        # --- B. CẤU HÌNH BẢO MẬT ---

        # 1. Danh sách các trang CẤM NHÂN VIÊN (Chỉ Admin mới vào được)
        RESTRICTED_PAGES = [
            "QL_Kho",
            "QL_SP",
            "QL_TK",      # Quản lý tài khoản
            "QL_NV",      # Quản lý nhân viên
            "Ngan_hang",
            "Luong",
                # Thông tin tài khoản (Theo yêu cầu của bạn là khoá)
        ]

        # 2. Từ khóa xác định là ADMIN
        # Do database bạn lưu là 'admin' (chữ thường), nên danh sách này phải chứa 'admin'
        ADMIN_KEYWORDS = ["admin"]

        # 3. Xử lý chuỗi Role (Chuyển về chữ thường + xóa khoảng trắng)
        # Ví dụ: DB trả về "Admin" -> code chuyển thành "admin" cho khớp
        current_role_clean = str(self.current_user_role).strip().lower() if self.current_user_role else ""

        # --- C. KIỂM TRA QUYỀN ---

        # Logic: Nếu trang thuộc danh sách cấm VÀ Role hiện tại KHÔNG PHẢI là admin
        if (page_key in RESTRICTED_PAGES) and (current_role_clean not in ADMIN_KEYWORDS):
            print(f"⛔ CHẶN TRUY CẬP: Role '{current_role_clean}' cố gắng vào '{page_key}'")
            messagebox.showwarning(
                "Truy cập bị từ chối",
                "Bạn không có quyền truy cập chức năng này!\nChức năng chỉ dành cho Admin."
            )
            return  # Dừng hàm, không mở trang

        # --- D. MỞ TRANG (NẾU HỢP LỆ) ---

        # 1. Xóa trang cũ
        if self.current_page:
            self.current_page.destroy()
            self.current_page = None

        # 2. Ánh xạ Key -> Class
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

            # Truyền ID người dùng vào các trang cần thiết
            if page_key == "TaiKhoan" or page_key == "menu":
                self.current_page = page_class(self.content_container, current_user_id=self.current_user_id)
            else:
                self.current_page = page_class(self.content_container)

            self.current_page.pack(fill="both", expand=True)
        else:
            # Xử lý khi trang chưa phát triển
            self.current_page = ctk.CTkFrame(self.content_container, fg_color="white")
            self.current_page.pack(fill="both", expand=True)
            ctk.CTkLabel(
                self.current_page,
                text=f"Chức năng '{page_key}' đang phát triển...",
                font=("Arial", 20), text_color="gray"
            ).place(relx=0.5, rely=0.5, anchor="center")


if __name__ == "__main__":
    app = MainApp()