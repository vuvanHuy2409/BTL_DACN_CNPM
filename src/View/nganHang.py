import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os

class NganHangPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="white")

        # Dữ liệu giả lập
        self.bank_data = [
            {"id": "1", "ten": "Vietcombank", "stk": "0011002233445", "chu": "NGUYEN VAN A", "qr": "path/to/qr1.png"},
            {"id": "2", "ten": "MB Bank", "stk": "999988887777", "chu": "CUA HANG TRUONG", "qr": ""},
            {"id": "3", "ten": "Techcombank", "stk": "190333444555", "chu": "TRAN THI B", "qr": ""},
        ]
        
        self.current_qr_path = None
        self.qr_image_ref = None # Giữ tham chiếu ảnh để không bị garbage collect

        self.tao_main_content()
        self.load_table_data()

    def tao_main_content(self):
        """Tạo nội dung chính"""
        container = ctk.CTkFrame(self, fg_color="white")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Tiêu đề
        ctk.CTkLabel(container, text="Quản lý Tài khoản Ngân hàng", font=("Arial", 18, "bold"), text_color="#333").pack(anchor="w", pady=(0, 20))

        # ====================== 1. CONTROL PANEL ======================
        action_bar = ctk.CTkFrame(container, fg_color="white")
        action_bar.pack(fill="x", pady=(0, 20))

        # Buttons
        btn_frame = ctk.CTkFrame(action_bar, fg_color="white")
        btn_frame.pack(side="left")

        self.create_btn(btn_frame, "Thêm", "#4CAF50", "#45a049", self.them)
        self.create_btn(btn_frame, "Sửa", "#2196F3", "#0b7dda", self.sua)
        self.create_btn(btn_frame, "Xóa", "#f44336", "#da190b", self.xoa)
        self.create_btn(btn_frame, "Làm mới", "#9E9E9E", "#757575", self.lam_moi)
        self.create_btn(btn_frame, "Xuất Excel", "#00BCD4", "#0097A7", self.xuat, width=100)

        # Search
        search_frame = ctk.CTkFrame(action_bar, fg_color="white")
        search_frame.pack(side="right")
        self.search_entry = ctk.CTkEntry(search_frame, width=250, height=35, placeholder_text="Tên NH, STK...", border_width=1, border_color="#ccc")
        self.search_entry.pack(side="left", padx=(0, 5))
        ctk.CTkButton(search_frame, text="Tìm", fg_color="#2196F3", hover_color="#0b7dda", width=60, height=35, font=("Arial", 11, "bold"), command=self.tim_kiem).pack(side="left")

        # ====================== 2. FORM NHẬP LIỆU (Nền xám) ======================
        form_wrapper = ctk.CTkFrame(container, fg_color="#f5f5f5", border_width=1, border_color="#ccc")
        form_wrapper.pack(fill="x", pady=(0, 20))
        
        form_inner = ctk.CTkFrame(form_wrapper, fg_color="#f5f5f5")
        form_inner.pack(fill="x", padx=20, pady=20)

        # --- CỘT TRÁI: Thông tin ---
        left_col = ctk.CTkFrame(form_inner, fg_color="#f5f5f5")
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 20))

        # Hàng 1
        row1 = ctk.CTkFrame(left_col, fg_color="#f5f5f5")
        row1.pack(fill="x", pady=(0, 15))
        self.entry_ten = self.create_input(row1, "Tên ngân hàng", 200)
        self.entry_stk = self.create_input(row1, "Số tài khoản", 200)

        # Hàng 2
        row2 = ctk.CTkFrame(left_col, fg_color="#f5f5f5")
        row2.pack(fill="x")
        self.entry_chu = self.create_input(row2, "Chủ tài khoản", 200)
        self.entry_note = self.create_input(row2, "Ghi chú", 200)

        # --- CỘT PHẢI: QR Code ---
        right_col = ctk.CTkFrame(form_inner, fg_color="#f5f5f5")
        right_col.pack(side="right", anchor="n")

        ctk.CTkLabel(right_col, text="Mã QR Thanh toán", font=("Arial", 11, "bold"), text_color="#555").pack(pady=(0, 5))
        
        # Khung ảnh
        self.qr_frame = ctk.CTkFrame(right_col, fg_color="white", width=140, height=140, border_width=2, border_color="#ccc")
        self.qr_frame.pack(pady=(0, 10))
        self.qr_frame.pack_propagate(False)

        self.qr_label = ctk.CTkLabel(self.qr_frame, text="Chưa có ảnh", text_color="#999")
        self.qr_label.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkButton(right_col, text="Tải ảnh QR", fg_color="#607D8B", hover_color="#546E7A", width=140, height=28, command=self.upload_qr).pack()

        # ====================== 3. BẢNG DỮ LIỆU (TREEVIEW) ======================
        ctk.CTkLabel(container, text="Danh sách Ngân hàng", font=("Arial", 14, "bold"), text_color="#333").pack(anchor="w", pady=(0, 10))

        table_frame = ctk.CTkFrame(container, fg_color="white", border_width=1, border_color="#ccc")
        table_frame.pack(fill="both", expand=True)

        # Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground="black", rowheight=35, fieldbackground="white", font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#f0f0f0", foreground="#333")
        style.map("Treeview", background=[("selected", "#2196F3")])

        # Treeview
        columns = ("stt", "ten", "stk", "chu", "qr")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)

        self.tree.heading("stt", text="STT")
        self.tree.heading("ten", text="Tên Ngân Hàng")
        self.tree.heading("stk", text="Số Tài Khoản")
        self.tree.heading("chu", text="Chủ Tài Khoản")
        self.tree.heading("qr", text="Mã QR")

        self.tree.column("stt", width=50, anchor="center")
        self.tree.column("ten", width=200, anchor="w")
        self.tree.column("stk", width=150, anchor="center")
        self.tree.column("chu", width=200, anchor="w")
        self.tree.column("qr", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=2, pady=2)

        self.tree.bind("<<TreeviewSelect>>", self.on_select_row)

    # ====================== HELPERS ======================
    def create_btn(self, parent, text, color, hover, cmd, width=80):
        ctk.CTkButton(parent, text=text, fg_color=color, hover_color=hover, text_color="white", width=width, height=35, corner_radius=6, font=("Arial", 11, "bold"), command=cmd).pack(side="left", padx=5)

    def create_input(self, parent, label, width):
        f = ctk.CTkFrame(parent, fg_color="#f5f5f5")
        f.pack(side="left", padx=(0, 20), fill="x", expand=True)
        ctk.CTkLabel(f, text=label, font=("Arial", 11, "bold"), text_color="#555").pack(anchor="w", pady=(0, 5))
        e = ctk.CTkEntry(f, width=width, height=32, border_color="#ccc")
        e.pack(fill="x")
        return e

    # ====================== LOGIC ======================
    def load_table_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for idx, item in enumerate(self.bank_data):
            has_qr = "Có" if item.get("qr") else "Không"
            self.tree.insert("", "end", values=(idx+1, item["ten"], item["stk"], item["chu"], has_qr))

    def on_select_row(self, event):
        selected = self.tree.selection()
        if selected:
            # Lấy index dòng đang chọn (bắt đầu từ 0)
            index = self.tree.index(selected[0])
            data = self.bank_data[index]

            # Đổ dữ liệu text
            self.entry_ten.delete(0, "end"); self.entry_ten.insert(0, data["ten"])
            self.entry_stk.delete(0, "end"); self.entry_stk.insert(0, data["stk"])
            self.entry_chu.delete(0, "end"); self.entry_chu.insert(0, data["chu"])
            
            # Xử lý ảnh
            self.current_qr_path = data.get("qr")
            self.display_qr(self.current_qr_path)

    def display_qr(self, path):
        if path and os.path.exists(path):
            try:
                img = Image.open(path)
                img = img.resize((130, 130), Image.Resampling.LANCZOS)
                self.qr_image_ref = ImageTk.PhotoImage(img)
                self.qr_label.configure(image=self.qr_image_ref, text="")
            except:
                self.qr_label.configure(image="", text="Lỗi ảnh")
        else:
            self.qr_label.configure(image="", text="Chưa có ảnh")

    def upload_qr(self):
        path = filedialog.askopenfilename(filetypes=[("Image", "*.jpg *.png *.jpeg")])
        if path:
            self.current_qr_path = path
            self.display_qr(path)

    def them(self): messagebox.showinfo("TB", "Thêm Ngân hàng")
    def sua(self): messagebox.showinfo("TB", "Sửa Ngân hàng")
    def xoa(self): 
        if messagebox.askyesno("Xác nhận", "Xóa ngân hàng này?"):
            messagebox.showinfo("TB", "Đã xóa")
    def lam_moi(self):
        self.entry_ten.delete(0, "end")
        self.entry_stk.delete(0, "end")
        self.entry_chu.delete(0, "end")
        self.entry_note.delete(0, "end")
        self.qr_label.configure(image="", text="Chưa có ảnh")
    def xuat(self): messagebox.showinfo("TB", "Xuất Excel")
    def tim_kiem(self): pass