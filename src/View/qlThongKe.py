import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from src.Controller.ThongKeController import ThongKeController

# Kiểm tra thư viện Matplotlib
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class ThongKePage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="white")

        self.controller = ThongKeController()

        # Trạng thái mặc định
        self.current_chart_mode = "7_days"
        self.chart_canvas = None  # Giữ tham chiếu canvas để xóa khi vẽ lại

        # Setup giao diện
        self.setup_ui()

        # Load dữ liệu lần đầu
        self.load_data()

    def setup_ui(self):
        """Khởi tạo toàn bộ giao diện"""
        container = ctk.CTkFrame(self, fg_color="white")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # ================= 1. HEADER & FILTER =================
        header = ctk.CTkFrame(container, fg_color="white")
        header.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(header, text="BÁO CÁO THỐNG KÊ & DOANH THU",
                     font=("Arial", 22, "bold"), text_color="#1565C0").pack(side="left")

        # Khung bộ lọc
        filter_frame = ctk.CTkFrame(header, fg_color="#F5F5F5", corner_radius=5)
        filter_frame.pack(side="right", ipady=3)

        ctk.CTkLabel(filter_frame, text="Tháng:", font=("Arial", 12)).pack(side="left", padx=(10, 5))

        months = ["Tất cả"] + [str(i) for i in range(1, 13)]
        self.cb_month = ctk.CTkComboBox(filter_frame, values=months, width=70, state="readonly")
        self.cb_month.set(str(datetime.now().month))
        self.cb_month.pack(side="left", padx=2)

        ctk.CTkLabel(filter_frame, text="Năm:", font=("Arial", 12)).pack(side="left", padx=(10, 5))

        current_year = datetime.now().year
        years = [str(y) for y in range(current_year, current_year - 5, -1)]
        self.cb_year = ctk.CTkComboBox(filter_frame, values=years, width=80, state="readonly")
        self.cb_year.set(str(current_year))
        self.cb_year.pack(side="left", padx=2)

        ctk.CTkButton(filter_frame, text="Lọc Dữ Liệu", fg_color="#2196F3", width=100,
                      command=self.load_data).pack(side="left", padx=10)

        # ================= 2. DASHBOARD CARDS (THẺ TỔNG QUAN) =================
        cards_frame = ctk.CTkFrame(container, fg_color="white")
        cards_frame.pack(fill="x", pady=(0, 20))

        # Lưu các label giá trị để update sau này
        self.lbl_val_revenue = None
        self.lbl_val_orders = None
        self.lbl_val_customers = None

        self.create_card(cards_frame, "DOANH THU", "#4CAF50", "💰", 1)  # Xanh lá
        self.create_card(cards_frame, "TỔNG ĐƠN HÀNG", "#FF9800", "🛒", 2)  # Cam
        self.create_card(cards_frame, "KHÁCH HÀNG MỚI", "#2196F3", "👥", 3)  # Xanh dương

        # ================= 3. BIỂU ĐỒ (CHART) =================
        chart_container = ctk.CTkFrame(container, fg_color="white", border_width=1, border_color="#E0E0E0")
        chart_container.pack(fill="both", expand=True, pady=(0, 20))

        # Chart Toolbar
        chart_toolbar = ctk.CTkFrame(chart_container, fg_color="#FAFAFA", height=40)
        chart_toolbar.pack(fill="x", padx=1, pady=1)

        ctk.CTkLabel(chart_toolbar, text=" BIỂU ĐỒ TĂNG TRƯỞNG", font=("Arial", 12, "bold"), text_color="#555").pack(
            side="left", padx=10)

        # Nút chuyển chế độ
        self.btn_mode_7 = self.create_mode_btn(chart_toolbar, "7 Ngày qua", "7_days")
        self.btn_mode_month = self.create_mode_btn(chart_toolbar, "Theo Tháng", "month")
        self.btn_mode_year = self.create_mode_btn(chart_toolbar, "Theo Năm", "year")

        # Frame chứa Matplotlib
        self.chart_frame = ctk.CTkFrame(chart_container, fg_color="white")
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # ================= 4. BẢNG CHI TIẾT (ĐÃ SỬA) =================
        detail_frame = ctk.CTkFrame(container, fg_color="white")
        detail_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(detail_frame, text="CHI TIẾT DOANH THU", font=("Arial", 14, "bold"), text_color="#333").pack(
            anchor="w", pady=(0, 5))

        # Cấu hình Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=30, font=("Arial", 11))
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#E0E0E0")

        # [THAY ĐỔI] Chỉ còn 3 cột
        cols = ("time", "count", "rev")
        self.tree = ttk.Treeview(detail_frame, columns=cols, show="headings", height=8)

        self.tree.heading("time", text="Thời Gian")
        self.tree.heading("count", text="Số Lượng Đơn")
        self.tree.heading("rev", text="Tổng Doanh Thu")

        # Điều chỉnh độ rộng cột lớn hơn vì ít cột hơn
        self.tree.column("time", anchor="center", width=200)
        self.tree.column("count", anchor="center", width=150)
        self.tree.column("rev", anchor="e", width=250)

        # Scrollbar
        sb = ttk.Scrollbar(detail_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

    # ================= UI HELPERS =================
    def create_card(self, parent, title, color, icon, type_id):
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=10, height=90)
        card.pack(side="left", fill="x", expand=True, padx=5)
        card.pack_propagate(False)  # Giữ cố định chiều cao

        ctk.CTkLabel(card, text=title, font=("Arial", 12, "bold"), text_color="white").pack(anchor="w", padx=15,
                                                                                            pady=(10, 0))

        lbl_val = ctk.CTkLabel(card, text="...", font=("Arial", 20, "bold"), text_color="white")
        lbl_val.pack(anchor="w", padx=15, pady=(0, 5))

        # Lưu tham chiếu để update
        if type_id == 1:
            self.lbl_val_revenue = lbl_val
        elif type_id == 2:
            self.lbl_val_orders = lbl_val
        elif type_id == 3:
            self.lbl_val_customers = lbl_val

        ctk.CTkLabel(card, text=icon, font=("Arial", 30), text_color="white").place(relx=0.9, rely=0.5, anchor="e")

    def create_mode_btn(self, parent, text, mode):
        btn = ctk.CTkButton(parent, text=text, width=90, fg_color="white", text_color="#333",
                            border_width=1, border_color="#ccc",
                            command=lambda: self.switch_chart_mode(mode))
        btn.pack(side="right", padx=5, pady=5)
        return btn

    # ================= LOGIC LOAD DỮ LIỆU =================
    def load_data(self):
        """Hàm chính để tải dữ liệu từ Controller"""
        m = self.cb_month.get()
        y = self.cb_year.get()

        # 1. Update Cards
        summary = self.controller.get_dashboard_summary(m, y)
        if self.lbl_val_revenue: self.lbl_val_revenue.configure(text=summary['doanh_thu'])
        if self.lbl_val_orders: self.lbl_val_orders.configure(text=summary['tong_don'])
        if self.lbl_val_customers: self.lbl_val_customers.configure(text=summary['khach_moi'])

        # 2. Update Chart & Table
        x_data, y_data, table_rows = self.controller.get_chart_and_table_data(self.current_chart_mode, m, y)

        self.draw_chart(x_data, y_data)
        self.update_table(table_rows)

        # Cập nhật màu nút active
        self.update_btn_styles()

    def switch_chart_mode(self, mode):
        self.current_chart_mode = mode
        self.load_data()

    def update_btn_styles(self):
        """Highlight nút đang chọn"""
        btns = {"7_days": self.btn_mode_7, "month": self.btn_mode_month, "year": self.btn_mode_year}
        for k, btn in btns.items():
            if k == self.current_chart_mode:
                btn.configure(fg_color="#2196F3", text_color="white")
            else:
                btn.configure(fg_color="white", text_color="#333")

    def update_table(self, rows):
        for i in self.tree.get_children(): self.tree.delete(i)
        for r in rows:
            self.tree.insert("", "end", values=r)

    def draw_chart(self, x_labels, y_values):
        """Vẽ biểu đồ Matplotlib"""
        if not HAS_MATPLOTLIB:
            ctk.CTkLabel(self.chart_frame, text="Chưa cài đặt thư viện matplotlib!", text_color="red").pack(expand=True)
            return

        # Xóa biểu đồ cũ nếu có
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        if not x_labels:
            ctk.CTkLabel(self.chart_frame, text="Không có dữ liệu trong khoảng thời gian này", text_color="gray").pack(
                expand=True)
            return

        # Tạo Figure
        fig = Figure(figsize=(6, 3), dpi=100)
        ax = fig.add_subplot(111)

        # Vẽ cột
        # Chia giá trị cho 1 triệu để biểu đồ gọn hơn (nếu số lớn)
        display_values = [v for v in y_values]
        bars = ax.bar(x_labels, display_values, color='#4CAF50', width=0.5)

        # Style
        ax.set_title(f'Biểu đồ Doanh thu ({self.get_mode_text()})', fontsize=10, pad=10)
        ax.set_ylabel('VNĐ')
        ax.grid(axis='y', linestyle='--', alpha=0.5)

        # Tick nhỏ lại nếu quá nhiều cột
        if len(x_labels) > 10:
            ax.tick_params(axis='x', labelsize=8, rotation=45)

        # Format trục Y (để tránh số khoa học 1e7...)
        ax.get_yaxis().set_major_formatter(
            # Hàm lambda format số
            lambda x, p: format(int(x), ',')
        )

        # Hiển thị số liệu trên đỉnh cột
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                # Rút gọn số hiển thị (VD: 1.5M)
                txt_val = f"{height / 1000000:.1f}M" if height >= 1000000 else f"{height / 1000:.0f}k"
                ax.text(bar.get_x() + bar.get_width() / 2., height,
                        txt_val,
                        ha='center', va='bottom', fontsize=8, color="#333")

        # Đưa vào Frame
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def get_mode_text(self):
        if self.current_chart_mode == "7_days": return "7 Ngày gần nhất"
        if self.current_chart_mode == "month": return "Theo Ngày trong Tháng"
        return "Theo Tháng trong Năm"