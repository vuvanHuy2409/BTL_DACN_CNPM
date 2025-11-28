import customtkinter as ctk
from tkinter import messagebox
import platform


class QuenMK2:
    def __init__(self, window, parent_root, username):
        self.window = window
        self.parent_root = parent_root
        self.username = username
        self.window.title("ĐỔI MẬT KHẨU")

        # Cấu hình giao diện
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Kích thước và canh giữa cửa sổ
        system = platform.system()
        if system == "Windows":
            self.window.after(10, lambda: self.window.state("zoomed"))
        else:
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            self.window.geometry(f"{screen_width}x{screen_height}+0+0")

        self.tao_giao_dien()

    def tao_giao_dien(self):
        # ===== Tiêu đề =====
        title_label = ctk.CTkLabel(self.window, text="ĐỔI MẬT KHẨU", font=("Arial", 20, "bold"))
        title_label.pack(pady=15)

        # Hiển thị tên tài khoản
        if self.username:
            user_label = ctk.CTkLabel(self.window, text=f"Tài khoản: {self.username}", font=("Arial", 12))
            user_label.pack(pady=5)

        # ===== Ô nhập mật khẩu mới =====
        frame_new = ctk.CTkFrame(self.window, fg_color="transparent")
        frame_new.pack(pady=8, padx=20, fill="x")

        new_icon = ctk.CTkLabel(frame_new, text="🔒", font=("Arial", 16), width=30)
        new_icon.pack(side="left", padx=(0, 10))

        self.entry_new = ctk.CTkEntry(frame_new, placeholder_text="Mật khẩu mới", show="*")
        self.entry_new.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Nút hiện/ẩn mật khẩu mới
        self.eye_btn_new = ctk.CTkButton(frame_new, text="👁️", width=40, command=self.toggle_new)
        self.eye_btn_new.pack(side="left")

        # ===== Ô nhập lại mật khẩu =====
        frame_confirm = ctk.CTkFrame(self.window, fg_color="transparent")
        frame_confirm.pack(pady=8, padx=20, fill="x")

        confirm_icon = ctk.CTkLabel(frame_confirm, text="🔒", font=("Arial", 16), width=30)
        confirm_icon.pack(side="left", padx=(0, 10))

        self.entry_confirm = ctk.CTkEntry(frame_confirm, placeholder_text="Nhập lại mật khẩu", show="*")
        self.entry_confirm.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Nút hiện/ẩn xác nhận mật khẩu
        self.eye_btn_confirm = ctk.CTkButton(frame_confirm, text="👁️", width=40, command=self.toggle_confirm)
        self.eye_btn_confirm.pack(side="left")

        # ===== Các nút chức năng =====
        button_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        button_frame.pack(pady=25)

        btn_doi = ctk.CTkButton(button_frame, text="Đổi mật khẩu", width=120, height=35, command=self.doi_mat_khau)
        btn_doi.pack(side="left", padx=10)

        btn_quay = ctk.CTkButton(button_frame, text="Quay lại", width=120, height=35, command=self.quay_lai)
        btn_quay.pack(side="left", padx=10)

        self.entry_new.focus()

    def toggle_new(self):
        if self.entry_new.cget("show") == "*":
            self.entry_new.configure(show="")
            self.eye_btn_new.configure(text="🙈")
        else:
            self.entry_new.configure(show="*")
            self.eye_btn_new.configure(text="👁️")

    def toggle_confirm(self):
        if self.entry_confirm.cget("show") == "*":
            self.entry_confirm.configure(show="")
            self.eye_btn_confirm.configure(text="🙈")
        else:
            self.entry_confirm.configure(show="*")
            self.eye_btn_confirm.configure(text="👁️")

    def doi_mat_khau(self):
        new_pw = self.entry_new.get()
        confirm_pw = self.entry_confirm.get()
        if not new_pw or not confirm_pw:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin!")
        elif new_pw != confirm_pw:
            messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp!")
        else:
            messagebox.showinfo("Thành công", "Đổi mật khẩu thành công!")
            # Đóng cửa sổ và quay về màn hình đăng nhập
            self.window.destroy()
            self.parent_root.deiconify()
            system = platform.system()
            if system == "Windows":
                self.parent_root.after(10, lambda: self.parent_root.state("zoomed"))
            else:
                screen_width = self.parent_root.winfo_screenwidth()
                screen_height = self.parent_root.winfo_screenheight()
                self.parent_root.geometry(f"{screen_width}x{screen_height}+0+0")

    def quay_lai(self):
        self.window.destroy()
        self.parent_root.deiconify()
        system = platform.system()
        if system == "Windows":
            self.parent_root.after(10, lambda: self.parent_root.state("zoomed"))
        else:
            screen_width = self.parent_root.winfo_screenwidth()
            screen_height = self.parent_root.winfo_screenheight()
            self.parent_root.geometry(f"{screen_width}x{screen_height}+0+0")


if __name__ == "__main__":
    root = ctk.CTk()
    window = ctk.CTkToplevel(root)
    app = QuenMK2(window, root, "test_user")
    root.mainloop()