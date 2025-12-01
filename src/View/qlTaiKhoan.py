import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import os
from src.Controller.TaiKhoanController import TaiKhoanController


class QuanLyTKPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="white")

        self.controller = TaiKhoanController()

        self.current_image_path = None
        self.selected_id = None
        self.selected_has_account = False
        self.current_list = []

        self.current_photo = None

        self.tao_main_content()
        self.load_table_data()

    def tao_main_content(self):
        container = ctk.CTkFrame(self, fg_color="white")
        container.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(
            container, text="QUẢN LÝ TÀI KHOẢN",
            font=("Arial", 20, "bold"), text_color="#333"
        ).pack(anchor="center", pady=(0, 20))

        # ================= FORM =================
        input_group = ctk.CTkFrame(container, fg_color="#f5f5f5", border_width=1, border_color="#ccc")
        input_group.pack(fill="x", padx=20, pady=(0, 20))

        # Toolbar
        toolbar = ctk.CTkFrame(input_group, fg_color="transparent")
        toolbar.pack(fill="x", padx=10, pady=(15, 10))
        btn_center = ctk.CTkFrame(toolbar, fg_color="transparent")
        btn_center.pack(anchor="center")

        self.create_btn(btn_center, "Lưu / Cấp TK", "#4CAF50", "#45a049", self.luu_thong_tin, width=120)
        self.create_btn(btn_center, "Xóa TK", "#f44336", "#da190b", self.xoa_tk)
        self.create_btn(btn_center, "Làm mới", "#9E9E9E", "#757575", self.lam_moi)

        ctk.CTkFrame(input_group, height=1, fg_color="#ddd").pack(fill="x", padx=20, pady=5)

        # Fields
        form_container = ctk.CTkFrame(input_group, fg_color="transparent")
        form_container.pack(fill="x", padx=20, pady=20)

        # [CỘT TRÁI] Avatar
        left_col = ctk.CTkFrame(form_container, fg_color="transparent")
        left_col.pack(side="left", padx=(20, 40), anchor="n")

        self.avatar_frame = ctk.CTkFrame(left_col, fg_color="white", width=120, height=120, corner_radius=60,
                                         border_width=2, border_color="#ddd")
        self.avatar_frame.pack(pady=(0, 10))
        self.avatar_frame.pack_propagate(False)

        # Label hiển thị ảnh: Mặc định text rỗng
        self.avatar_label = ctk.CTkLabel(self.avatar_frame, text="", font=("Arial", 40), text_color="#ccc")
        self.avatar_label.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkButton(left_col, text="Chọn ảnh", width=100, height=28, fg_color="#607D8B", hover_color="#546E7A",
                      command=self.chon_anh).pack()

        # [CỘT PHẢI] Thông tin
        right_col = ctk.CTkFrame(form_container, fg_color="transparent")
        right_col.pack(side="left", fill="both", expand=True)

        # Hàng 1
        row1 = ctk.CTkFrame(right_col, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 10))
        self.entry_name = self.create_input(row1, "Họ và tên", 250)
        self.entry_name.configure(state="readonly")
        self.entry_email = self.create_input(row1, "Email", 250)
        self.entry_email.configure(state="readonly")

        # Hàng 2
        row2 = ctk.CTkFrame(right_col, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 10))
        self.entry_user = self.create_input(row2, "Tên đăng nhập", 200)

        f_pass = ctk.CTkFrame(row2, fg_color="transparent")
        f_pass.pack(side="left", padx=10)
        ctk.CTkLabel(f_pass, text="Mật khẩu", font=("Arial", 11, "bold"), text_color="#555").pack(anchor="w",
                                                                                                  pady=(0, 2))
        f_pass_inner = ctk.CTkFrame(f_pass, fg_color="transparent")
        f_pass_inner.pack()
        self.entry_pass = ctk.CTkEntry(f_pass_inner, width=170, height=30, show="*", border_color="#ccc")
        self.entry_pass.pack(side="left")
        self.btn_eye = ctk.CTkButton(f_pass_inner, text="👁", width=30, height=30, fg_color="#ddd", text_color="#333",
                                     hover_color="#ccc", command=self.toggle_pass)
        self.btn_eye.pack(side="left", padx=(5, 0))

        # Hàng 3
        row3 = ctk.CTkFrame(right_col, fg_color="transparent")
        row3.pack(fill="x", pady=(0, 10))
        f_role = ctk.CTkFrame(row3, fg_color="transparent")
        f_role.pack(side="left", padx=10)
        ctk.CTkLabel(f_role, text="Vai trò", font=("Arial", 11, "bold"), text_color="#555").pack(anchor="w",
                                                                                                 pady=(0, 2))
        roles = ["Quản Lý", "Pha Chế (Barista)", "Phục Vụ", "Bảo Vệ"]
        self.combo_role = ctk.CTkComboBox(f_role, values=roles, width=200, height=30, state="readonly")
        self.combo_role.set("Chọn vai trò")
        self.combo_role.pack()

        # ================= DANH SÁCH =================
        ctk.CTkLabel(container, text="DANH SÁCH NHÂN VIÊN & TÀI KHOẢN", font=("Arial", 14, "bold"),
                     text_color="#333").pack(anchor="w", padx=20, pady=(10, 5))

        list_frame = ctk.CTkFrame(container, fg_color="white", border_width=1, border_color="#999")
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        columns = ("stt", "name", "user", "email", "role", "status")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)

        self.tree.heading("stt", text="STT")
        self.tree.heading("name", text="Họ và Tên")
        self.tree.heading("user", text="Username")
        self.tree.heading("email", text="Email")
        self.tree.heading("role", text="Chức vụ")
        self.tree.heading("status", text="Trạng thái TK")

        self.tree.column("stt", width=50, anchor="center")
        self.tree.column("name", width=200)
        self.tree.column("user", width=150)
        self.tree.column("email", width=200)
        self.tree.column("role", width=150)
        self.tree.column("status", width=120, anchor="center")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_select_row)

    # ================= HELPERS =================
    def create_btn(self, parent, text, color, hover, cmd, width=80):
        ctk.CTkButton(parent, text=text, fg_color=color, hover_color=hover, width=width, height=32, command=cmd).pack(
            side="left", padx=5)

    def create_input(self, parent, label, width, show=None):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(side="left", padx=10)
        ctk.CTkLabel(f, text=label, font=("Arial", 11, "bold"), text_color="#555").pack(anchor="w", pady=(0, 2))
        e = ctk.CTkEntry(f, width=width, height=30, show=show, border_color="#ccc")
        e.pack()
        return e

    def toggle_pass(self):
        if self.entry_pass.cget('show') == '*':
            self.entry_pass.configure(show='')
            self.btn_eye.configure(text="🔒")
        else:
            self.entry_pass.configure(show='*')
            self.btn_eye.configure(text="👁")

    # ================= XỬ LÝ ẢNH =================
    def display_image(self, path):
        """Hiển thị ảnh từ đường dẫn"""
        try:
            if path and os.path.exists(path):
                pil_image = Image.open(path)
                self._update_avatar_label(pil_image)
            else:
                self._reset_avatar()
        except Exception:
            self._reset_avatar()

    def _update_avatar_label(self, pil_image):
        try:
            w, h = pil_image.size
            s = min(w, h)
            pil_image = pil_image.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2))

            self.current_photo = ctk.CTkImage(
                light_image=pil_image,
                dark_image=pil_image,
                size=(120, 120)
            )
            self.avatar_label.configure(image=self.current_photo, text="")
        except:
            self._reset_avatar()

    def _reset_avatar(self):
        """Đặt lại avatar về trạng thái trống (không hiện gì)"""
        self.current_photo = None
        self.avatar_label.configure(image=None, text="")  # Text rỗng

    def chon_anh(self):
        path = filedialog.askopenfilename(filetypes=[("Image", "*.jpg *.png *.jpeg")])
        if path:
            self.current_image_path = path
            self.display_image(path)

    # ================= LOGIC CHÍNH =================
    def load_table_data(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        self.current_list = self.controller.get_list()

        for idx, item in enumerate(self.current_list):
            has_acc = item['tenDangNhap'] is not None
            status_text = "Đã có" if has_acc else "Chưa có"
            user_display = item['tenDangNhap'] if has_acc else ""

            self.tree.insert("", "end", values=(
                idx + 1,
                item['hoTen'],
                user_display,
                item['email'],
                item['tenChucVu'],
                status_text
            ))

    def on_select_row(self, event):
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            if index < len(self.current_list):
                data = self.current_list[index]

                self.selected_id = data['idNhanVien']
                self.selected_has_account = (data['tenDangNhap'] is not None)

                self.entry_name.configure(state="normal")
                self.entry_name.delete(0, "end");
                self.entry_name.insert(0, data['hoTen'])
                self.entry_name.configure(state="readonly")

                self.entry_email.configure(state="normal")
                self.entry_email.delete(0, "end");
                self.entry_email.insert(0, data['email'])
                self.entry_email.configure(state="readonly")

                self.combo_role.set(data['tenChucVu'])
                self.entry_user.delete(0, "end")
                self.entry_pass.delete(0, "end")

                # Load ảnh từ DB
                img_path = data.get('hinhAnhUrl')
                self.current_image_path = img_path
                self.display_image(img_path)

                if self.selected_has_account:
                    self.entry_user.insert(0, data['tenDangNhap'])
                    self.entry_pass.configure(placeholder_text="(Đã có mật khẩu)")
                else:
                    self.entry_pass.configure(placeholder_text="Nhập mật khẩu mới")

    def luu_thong_tin(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên!")
            return

        name = self.entry_name.get()
        user = self.entry_user.get()
        pwd = self.entry_pass.get()
        email = self.entry_email.get()
        role = self.combo_role.get()

        success, msg = self.controller.save_account(
            self.selected_id, self.selected_has_account,
            name, user, pwd, email, role,
            self.current_image_path
        )

        if success:
            messagebox.showinfo("Thành công", msg)
            self.lam_moi()
        else:
            messagebox.showerror("Lỗi", msg)

    def xoa_tk(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Chọn dòng cần xóa!")
            return

        if not self.selected_has_account:
            messagebox.showinfo("Thông báo", "Nhân viên này chưa có tài khoản!")
            return

        if messagebox.askyesno("Xác nhận", "Xóa tài khoản của nhân viên này?"):
            success, msg = self.controller.delete_account_only(self.selected_id)
            if success:
                messagebox.showinfo("Thành công", msg)
                self.lam_moi()
            else:
                messagebox.showerror("Lỗi", msg)

    def lam_moi(self):
        self.selected_id = None
        self.selected_has_account = False
        self.current_image_path = None

        self.entry_name.configure(state="normal");
        self.entry_name.delete(0, "end")
        self.entry_user.delete(0, "end")
        self.entry_pass.delete(0, "end")
        self.entry_email.configure(state="normal");
        self.entry_email.delete(0, "end")
        self.combo_role.set("Chọn vai trò")

        self._reset_avatar()
        self.entry_pass.configure(placeholder_text="")

        self.load_table_data()