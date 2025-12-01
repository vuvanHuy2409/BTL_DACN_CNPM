import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from PIL import Image
import os
from datetime import datetime
from src.Controller.SanPhamController import SanPhamController


class SanPhamPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="white")

        self.controller = SanPhamController()

        # --- CÁC BIẾN QUẢN LÝ TRẠNG THÁI ---
        self.current_list = []
        self.selected_id = None
        self.image_path = ""
        self.current_image = None  # [QUAN TRỌNG] Biến giữ tham chiếu ảnh để không bị lỗi

        # Load dữ liệu Combobox
        self.cats = self.controller.lay_ds_danh_muc()
        self.ingredients = self.controller.lay_ds_nguyen_lieu()

        self.tao_main_content()
        self.load_table_data()

    def tao_main_content(self):
        container = ctk.CTkFrame(self, fg_color="white")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Tiêu đề
        ctk.CTkLabel(container, text="QUẢN LÝ SẢN PHẨM", font=("Arial", 20, "bold"), text_color="#333").pack(anchor="w",
                                                                                                             pady=(
                                                                                                             0, 20))

        # === THANH CÔNG CỤ ===
        action_bar = ctk.CTkFrame(container, fg_color="white")
        action_bar.pack(fill="x", pady=(0, 15))

        btn_fr = ctk.CTkFrame(action_bar, fg_color="white")
        btn_fr.pack(side="left")
        self.create_btn(btn_fr, "Thêm", "#4CAF50", "#45a049", self.them)
        self.create_btn(btn_fr, "Sửa", "#2196F3", "#0b7dda", self.sua)
        self.create_btn(btn_fr, "Ẩn/Hiện", "#FF9800", "#F57C00", self.doi_trang_thai, width=100)
        self.create_btn(btn_fr, "Làm mới", "#9E9E9E", "#757575", self.lam_moi)
        self.create_btn(btn_fr, "Xuất Excel", "#00BCD4", "#0097A7", self.xuat, width=100)

        search_fr = ctk.CTkFrame(action_bar, fg_color="white")
        search_fr.pack(side="right")
        self.search_entry = ctk.CTkEntry(search_fr, width=220, placeholder_text="Tên sản phẩm...")
        self.search_entry.pack(side="left", padx=5)
        ctk.CTkButton(search_fr, text="Tìm", width=60, fg_color="#2196F3", command=self.tim_kiem).pack(side="left")

        # === FORM NHẬP LIỆU (Chia 2 cột) ===
        form_frame = ctk.CTkFrame(container, fg_color="#f8f9fa", border_width=1, border_color="#dee2e6")
        form_frame.pack(fill="x", pady=(0, 20))

        # --- Cột Trái: Input ---
        left_panel = ctk.CTkFrame(form_frame, fg_color="transparent")
        left_panel.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        # Hàng 1
        r1 = ctk.CTkFrame(left_panel, fg_color="transparent")
        r1.pack(fill="x", pady=(0, 15))
        self.entry_ten = self.create_input(r1, "Tên sản phẩm (*)", None, fill="x")

        # Hàng 2
        r2 = ctk.CTkFrame(left_panel, fg_color="transparent")
        r2.pack(fill="x", pady=(0, 15))
        self.entry_gia = self.create_input(r2, "Đơn giá (VNĐ)", 150)

        f_dm = ctk.CTkFrame(r2, fg_color="transparent")
        f_dm.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(f_dm, text="Danh mục", font=("Arial", 11, "bold"), text_color="#555").pack(anchor="w")
        self.cbo_dm = ctk.CTkComboBox(f_dm, width=180, values=[c['tenDanhMuc'] for c in self.cats])
        self.cbo_dm.pack()

        # Hàng 3
        r3 = ctk.CTkFrame(left_panel, fg_color="transparent")
        r3.pack(fill="x")
        f_nl = ctk.CTkFrame(r3, fg_color="transparent")
        f_nl.pack(side="left", padx=(0, 20), fill="x", expand=True)
        ctk.CTkLabel(f_nl, text="Nguyên liệu gốc", font=("Arial", 11, "bold"), text_color="#555").pack(anchor="w")
        self.cbo_nl = ctk.CTkComboBox(f_nl, values=[i['tenNguyenLieu'] for i in self.ingredients])
        self.cbo_nl.pack(fill="x")

        # --- Cột Phải: Ảnh ---
        right_panel = ctk.CTkFrame(form_frame, fg_color="transparent")
        right_panel.pack(side="right", fill="y", padx=20, pady=20)

        ctk.CTkLabel(right_panel, text="Hình ảnh minh họa", font=("Arial", 11, "bold"), text_color="#555").pack(
            pady=(0, 5))

        # Khung Preview
        self.img_preview_frame = ctk.CTkFrame(right_panel, width=160, height=160, fg_color="#e9ecef", border_width=1,
                                              border_color="#ccc")
        self.img_preview_frame.pack()
        self.img_preview_frame.pack_propagate(False)

        self.lbl_image = ctk.CTkLabel(self.img_preview_frame, text="Chưa có ảnh", text_color="#777")
        self.lbl_image.place(relx=0.5, rely=0.5, anchor="center")

        self.btn_img = ctk.CTkButton(right_panel, text="Thêm ảnh", width=160, fg_color="#607D8B", hover_color="#455A64",
                                     command=self.chon_anh)
        self.btn_img.pack(pady=(10, 0))

        # === BẢNG DỮ LIỆU ===
        ctk.CTkLabel(container, text="Danh sách sản phẩm", font=("Arial", 14, "bold"), text_color="#555").pack(
            anchor="w", pady=(0, 5))

        table_frame = ctk.CTkFrame(container, fg_color="white", border_width=1, border_color="#ccc")
        table_frame.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground="black", rowheight=30, fieldbackground="white",
                        font=("Arial", 11))
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#eee", foreground="#333")
        style.map("Treeview", background=[("selected", "#E3F2FD")], foreground=[("selected", "black")])

        cols = ("stt", "ten", "gia", "dm", "nl", "trangthai")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=10)

        headers = [
            ("stt", "STT", 50), ("ten", "Tên Sản Phẩm", 250), ("gia", "Giá Bán", 120),
            ("dm", "Danh Mục", 150), ("nl", "Nguyên Liệu", 200), ("trangthai", "Trạng Thái", 120)
        ]
        for c, t, w in headers:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor="center" if c in ["stt", "trangthai"] else "w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    # === HELPERS ===
    def create_btn(self, p, t, c, h, cmd, width=90):
        ctk.CTkButton(p, text=t, fg_color=c, hover_color=h, width=width, height=35, font=("Arial", 12, "bold"),
                      command=cmd).pack(side="left", padx=5)

    def create_input(self, p, lbl, w, fill=None):
        f = ctk.CTkFrame(p, fg_color="transparent")
        f.pack(side="left", padx=(0, 20), fill=fill if fill else "none", expand=True if fill else False)
        ctk.CTkLabel(f, text=lbl, font=("Arial", 11, "bold"), text_color="#555").pack(anchor="w")
        e = ctk.CTkEntry(f, width=w if w else 140, height=32, border_color="#ccc")
        e.pack(fill="x")
        return e

    def get_id_by_name(self, name, source, id_key, name_key):
        for item in source:
            if item[name_key] == name: return item[id_key]
        return None

    # === HÀM XỬ LÝ ẢNH (ĐÃ FIX LỖI) ===
    def update_image_preview(self, path):
        # 1. Reset ảnh cũ
        self.lbl_image.configure(image=None, text="Đang tải...")
        self.current_image = None

        if path:
            # 2. Xử lý đường dẫn tương đối/tuyệt đối
            if not os.path.isabs(path):
                full_path = os.path.abspath(path)
            else:
                full_path = path

            # 3. Load ảnh
            if os.path.exists(full_path):
                try:
                    pil_img = Image.open(full_path)
                    # Lưu vào biến instance self.current_image để không bị Garbage Collection xóa
                    self.current_image = ctk.CTkImage(light_image=pil_img, size=(150, 150))
                    self.lbl_image.configure(image=self.current_image, text="")
                except Exception as e:
                    print(f"Lỗi load ảnh: {e}")
                    self.lbl_image.configure(image=None, text="Lỗi file ảnh")
            else:
                self.lbl_image.configure(image=None, text="Ảnh không tồn tại")
        else:
            self.lbl_image.configure(image=None, text="Chưa có ảnh")

    # === LOGIC SỰ KIỆN ===
    def load_table_data(self, data=None):
        for i in self.tree.get_children(): self.tree.delete(i)
        if data is None: data = self.controller.lay_danh_sach()
        self.current_list = data

        for idx, row in enumerate(data):
            gia = "{:,.0f}".format(row['giaBan'])
            status = "Đang bán" if row['isActive'] else "Ngừng bán"
            val = (idx + 1, row['tenSanPham'], gia, row['tenDanhMuc'] or "-", row['tenNguyenLieu'] or "-", status)
            tags = ('hidden',) if not row['isActive'] else ('normal',)
            self.tree.insert("", "end", values=val, tags=tags)
        self.tree.tag_configure('hidden', foreground='#999999')

    def on_select(self, e):
        sel = self.tree.selection()
        if sel:
            item = self.current_list[self.tree.index(sel[0])]
            self.selected_id = item['idSanPham']

            self.entry_ten.delete(0, "end");
            self.entry_ten.insert(0, item['tenSanPham'])
            self.entry_gia.delete(0, "end");
            self.entry_gia.insert(0, int(item['giaBan']))
            self.cbo_dm.set(item['tenDanhMuc'] if item['tenDanhMuc'] else "")
            self.cbo_nl.set(item['tenNguyenLieu'] if item['tenNguyenLieu'] else "")

            self.image_path = item['hinhAnhUrl'] or ""
            self.update_image_preview(self.image_path)
            self.btn_img.configure(text="Thay đổi ảnh" if self.image_path else "Thêm ảnh")

    def chon_anh(self):
        filename = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg")])
        if filename:
            self.image_path = filename
            self.update_image_preview(filename)
            self.btn_img.configure(text="Thay đổi ảnh")

    def them(self):
        ten = self.entry_ten.get()
        gia = self.entry_gia.get()
        id_dm = self.get_id_by_name(self.cbo_dm.get(), self.cats, 'idDanhMuc', 'tenDanhMuc')
        id_nl = self.get_id_by_name(self.cbo_nl.get(), self.ingredients, 'idNguyenLieu', 'tenNguyenLieu')

        st, msg = self.controller.them_san_pham(ten, gia, self.image_path, id_dm, id_nl)
        if st:
            messagebox.showinfo("TB", msg)
            self.lam_moi()
        else:
            messagebox.showerror("Lỗi", msg)

    def sua(self):
        if not self.selected_id: return
        ten = self.entry_ten.get()
        gia = self.entry_gia.get()
        id_dm = self.get_id_by_name(self.cbo_dm.get(), self.cats, 'idDanhMuc', 'tenDanhMuc')
        id_nl = self.get_id_by_name(self.cbo_nl.get(), self.ingredients, 'idNguyenLieu', 'tenNguyenLieu')

        st, msg = self.controller.sua_san_pham(self.selected_id, ten, gia, self.image_path, id_dm, id_nl)
        if st:
            messagebox.showinfo("TB", msg)
            self.load_table_data()
        else:
            messagebox.showerror("Lỗi", msg)

    def doi_trang_thai(self):
        if self.selected_id and messagebox.askyesno("Xác nhận", "Đổi trạng thái?"):
            if self.controller.doi_trang_thai(self.selected_id)[0]: self.load_table_data()

    def lam_moi(self):
        self.entry_ten.delete(0, "end")
        self.entry_gia.delete(0, "end")
        self.cbo_dm.set("");
        self.cbo_nl.set("")
        self.selected_id = None;
        self.image_path = ""
        self.lbl_image.configure(image=None, text="Chưa có ảnh")
        self.btn_img.configure(text="Thêm ảnh")
        self.load_table_data()

    def tim_kiem(self):
        kw = self.search_entry.get()
        self.load_table_data(self.controller.tim_kiem(kw))

    def xuat(self):
        folder = filedialog.askdirectory()
        if folder:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(folder, f"SanPham_{ts}.xlsx")
            st, msg = self.controller.xuat_excel(path, self.current_list)
            messagebox.showinfo("TB", msg)