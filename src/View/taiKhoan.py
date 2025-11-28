import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

class TaiKhoanPage(ctk.CTkFrame):
    def __init__(self, parent):
        # 1. Kế thừa Frame để nhúng vào Main
        super().__init__(parent, fg_color="white")

        # 2. Biến lưu ảnh
        self.current_image_path = None
        self.current_photo = None
        self.is_editing = False

        # 3. Tạo giao diện
        self.tao_main_content()
        self.load_account_info()

    def tao_main_content(self):
        """Tạo nội dung chính"""
        # Container chính
        container = ctk.CTkFrame(self, fg_color="white")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Tiêu đề
        ctk.CTkLabel(container, text="Hồ sơ cá nhân", font=("Arial", 18, "bold"), text_color="#333").pack(
            anchor="center", pady=(0, 20))

        # ===== NÚT HÀNH ĐỘNG (Đã áp dụng màu) =====
        action_frame = ctk.CTkFrame(container, fg_color="white")
        action_frame.pack(anchor="center", pady=(0, 25))

        # Nút SỬA (Xanh dương)
        ctk.CTkButton(action_frame, text="Sửa thông tin", fg_color="#2196F3", text_color="white",
                      hover_color="#0b7dda", width=120, height=35, font=("Arial", 11, "bold"),
                      corner_radius=6, command=self.sua_tai_khoan).pack(side="left", padx=10)

        # Nút LƯU (Xanh lá - Tương đương Thêm/Xác nhận)
        ctk.CTkButton(action_frame, text="Lưu thay đổi", fg_color="#4CAF50", text_color="white",
                      hover_color="#45a049", width=120, height=35, font=("Arial", 11, "bold"),
                      corner_radius=6, command=self.luu_tai_khoan).pack(side="left", padx=10)

        # ===== FORM SECTION (Nền xám nhạt) =====
        form_section = ctk.CTkFrame(container, fg_color="#f5f5f5", border_width=1, border_color="#ccc")
        form_section.pack(fill="x", padx=50, pady=(0, 20))

        form_inner = ctk.CTkFrame(form_section, fg_color="#f5f5f5")
        form_inner.pack(fill="both", expand=True, padx=20, pady=20)

        # Container ảnh + input
        content_container = ctk.CTkFrame(form_inner, fg_color="#f5f5f5")
        content_container.pack(expand=True)

        # --- Cột trái: Ảnh ---
        avatar_column = ctk.CTkFrame(content_container, fg_color="#f5f5f5")
        avatar_column.pack(side="left", padx=(0, 50), anchor="n")

        # Khung chứa ảnh tròn (giả lập)
        self.avatar_frame = ctk.CTkFrame(avatar_column, fg_color="white", width=120, height=120, corner_radius=60, border_width=2, border_color="#ddd")
        self.avatar_frame.pack(pady=(0, 15))
        self.avatar_frame.pack_propagate(False)

        self.account_avatar_label = ctk.CTkLabel(self.avatar_frame, text="📷", font=("Arial", 40), text_color="#999")
        self.account_avatar_label.place(relx=0.5, rely=0.5, anchor="center")

        # Nút Đổi ảnh (Cyan)
        ctk.CTkButton(avatar_column, text="Đổi ảnh", fg_color="#00BCD4", text_color="white",
                      hover_color="#0097A7", width=100, height=30, font=("Arial", 11, "bold"),
                      corner_radius=6, command=self.chon_anh).pack()

        # --- Cột phải: Input ---
        fields_column = ctk.CTkFrame(content_container, fg_color="#f5f5f5")
        fields_column.pack(side="left")

        # Hàng 1
        row1 = ctk.CTkFrame(fields_column, fg_color="#f5f5f5")
        row1.pack(pady=10, anchor="w")
        self.entry_id = self.create_field(row1, "ID", 100)
        self.entry_name = self.create_field(row1, "Họ tên", 200)
        self.entry_user = self.create_field(row1, "Username", 150)

        # Hàng 2
        row2 = ctk.CTkFrame(fields_column, fg_color="#f5f5f5")
        row2.pack(pady=10, anchor="w")
        self.entry_pass = self.create_field(row2, "Mật khẩu", 150, show="*")
        self.entry_email = self.create_field(row2, "Email", 220)

        # ===== THÔNG TIN HIỂN THỊ (Readonly View) =====
        ctk.CTkLabel(container, text="Thông tin chi tiết", font=("Arial", 14, "bold"), text_color="#555").pack(anchor="center", pady=(20, 10))

        info_frame = ctk.CTkFrame(container, fg_color="#f9f9f9", border_width=1, border_color="#eee")
        info_frame.pack(fill="x", padx=100, pady=10)

        self.info_id = self.create_info_row(info_frame, "ID")
        self.info_name = self.create_info_row(info_frame, "Họ tên")
        self.info_username = self.create_info_row(info_frame, "Username")
        self.info_email = self.create_info_row(info_frame, "Email")

    # ================= HELPERS =================
    def create_field(self, parent, label, w, show=None):
        # Frame bao quanh input có màu nền #f5f5f5
        f = ctk.CTkFrame(parent, fg_color="#f5f5f5")
        f.pack(side="left", padx=(0, 20))
        
        ctk.CTkLabel(f, text=label, font=("Arial", 11), text_color="#333").pack(anchor="w", pady=(0, 5))
        
        e = ctk.CTkEntry(f, width=w, show=show, height=32, border_width=1, border_color="#ccc")
        e.pack()
        return e

    def create_info_row(self, parent, label):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(row, text=f"{label}:", width=100, anchor="w", font=("Arial", 12, "bold"), text_color="#333").pack(side="left")
        val = ctk.CTkLabel(row, text="...", anchor="w", text_color="#555")
        val.pack(side="left", fill="x", expand=True)
        return val

    # ================= LOGIC =================
    def load_account_info(self):
        # Khóa form ban đầu
        for e in [self.entry_id, self.entry_name, self.entry_user, self.entry_pass, self.entry_email]:
            e.configure(state="disabled", fg_color="#e0e0e0") # Màu xám khi disabled

    def sua_tai_khoan(self):
        self.is_editing = True
        for e in [self.entry_id, self.entry_name, self.entry_user, self.entry_pass, self.entry_email]:
            e.configure(state="normal", fg_color="white") # Màu trắng khi edit
        self.entry_id.configure(state="disabled", fg_color="#e0e0e0") # ID thường không cho sửa
        messagebox.showinfo("Thông báo", "Đã bật chế độ chỉnh sửa. Vui lòng cập nhật thông tin.")

    def luu_tai_khoan(self):
        if not self.is_editing: 
            messagebox.showwarning("Cảnh báo", "Vui lòng nhấn nút Sửa trước khi Lưu")
            return

        # Cập nhật thông tin hiển thị (Demo)
        self.info_id.configure(text=self.entry_id.get())
        self.info_name.configure(text=self.entry_name.get())
        self.info_username.configure(text=self.entry_user.get())
        self.info_email.configure(text=self.entry_email.get())

        # Khóa lại
        self.is_editing = False
        for e in [self.entry_id, self.entry_name, self.entry_user, self.entry_pass, self.entry_email]:
            e.configure(state="disabled", fg_color="#e0e0e0")
            
        messagebox.showinfo("Thành công", "Đã lưu thông tin tài khoản!")

    def chon_anh(self):
        path = filedialog.askopenfilename(filetypes=[("Image", "*.jpg *.png *.jpeg")])
        if path:
            try:
                # Resize ảnh cho vừa khung
                img = Image.open(path)
                # Crop ảnh thành hình vuông trước khi resize để không bị méo
                width, height = img.size
                new_width = min(width, height)
                left = (width - new_width)/2
                top = (height - new_width)/2
                right = (width + new_width)/2
                bottom = (height + new_width)/2
                img = img.crop((left, top, right, bottom))
                
                img = img.resize((100, 100), Image.Resampling.LANCZOS)
                self.current_photo = ImageTk.PhotoImage(img)
                self.account_avatar_label.configure(image=self.current_photo, text="")
                self.current_image_path = path
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể tải ảnh: {e}")