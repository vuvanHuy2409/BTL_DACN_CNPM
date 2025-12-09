import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog  # <--- Import filedialog
from datetime import datetime
from src.Controller.ThongKeController import ThongKeController

# Check matplotlib
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
        self.chart_canvas = None

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
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

        # ================= 2. DASHBOARD CARDS =================
        cards_frame = ctk.CTkFrame(container, fg_color="white")
        cards_frame.pack(fill="x", pady=(0, 20))

        self.lbl_val_revenue = None
        self.lbl_val_orders = None
        self.lbl_val_customers = None

        self.create_card(cards_frame, "DOANH THU", "#4CAF50", "💰", 1)
        self.create_card(cards_frame, "TỔNG ĐƠN HÀNG", "#FF9800", "🛒", 2)
        self.create_card(cards_frame, "KHÁCH HÀNG MỚI", "#2196F3", "👥", 3)

        # ================= 3. BIỂU ĐỒ =================
        chart_container = ctk.CTkFrame(container, fg_color="white", border_width=1, border_color="#E0E0E0")
        chart_container.pack(fill="both", expand=True, pady=(0, 20))

        chart_toolbar = ctk.CTkFrame(chart_container, fg_color="#FAFAFA", height=40)
        chart_toolbar.pack(fill="x", padx=1, pady=1)

        ctk.CTkLabel(chart_toolbar, text=" BIỂU ĐỒ TĂNG TRƯỞNG", font=("Arial", 12, "bold"), text_color="#555").pack(
            side="left", padx=10)

        self.btn_mode_7 = self.create_mode_btn(chart_toolbar, "7 Ngày qua", "7_days")
        self.btn_mode_month = self.create_mode_btn(chart_toolbar, "Theo Tháng", "month")
        self.btn_mode_year = self.create_mode_btn(chart_toolbar, "Theo Năm", "year")

        self.chart_frame = ctk.CTkFrame(chart_container, fg_color="white")
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # ================= 4. BẢNG CHI TIẾT & NÚT XUẤT EXCEL =================
        detail_frame = ctk.CTkFrame(container, fg_color="white")
        detail_frame.pack(fill="both", expand=True)

        # Toolbar bảng
        tbl_toolbar = ctk.CTkFrame(detail_frame, fg_color="white")
        tbl_toolbar.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(tbl_toolbar, text="CHI TIẾT DOANH THU", font=("Arial", 14, "bold"), text_color="#333").pack(
            side="left")

        # [MỚI] Nút Xuất Excel
        ctk.CTkButton(tbl_toolbar, text="📥 Xuất Excel", fg_color="#00897B", hover_color="#00695C",
                      width=120, height=30, command=self.xuat_excel).pack(side="right")

        # Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=30, font=("Arial", 11))
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#E0E0E0")

        cols = ("time", "count", "rev")
        self.tree = ttk.Treeview(detail_frame, columns=cols, show="headings", height=8)

        self.tree.heading("time", text="Thời Gian")
        self.tree.heading("count", text="Số Lượng Đơn")
        self.tree.heading("rev", text="Tổng Doanh Thu")

        self.tree.column("time", anchor="center", width=200)
        self.tree.column("count", anchor="center", width=150)
        self.tree.column("rev", anchor="e", width=250)

        sb = ttk.Scrollbar(detail_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

    # ================= [MỚI] HÀM XUẤT EXCEL =================
    def xuat_excel(self):
        # Mở hộp thoại chọn nơi lưu file
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Lưu báo cáo thống kê"
        )

        if filename:
            m = self.cb_month.get()
            y = self.cb_year.get()

            # Gọi Controller để xuất file
            success, msg = self.controller.export_report_to_excel(filename, self.current_chart_mode, m, y)

            if success:
                messagebox.showinfo("Thành công", msg)
            else:
                messagebox.showerror("Lỗi", msg)

    # ================= LOGIC KHÁC GIỮ NGUYÊN =================
    def create_card(self, parent, title, color, icon, type_id):
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=10, height=90)
        card.pack(side="left", fill="x", expand=True, padx=5)
        card.pack_propagate(False)
        ctk.CTkLabel(card, text=title, font=("Arial", 12, "bold"), text_color="white").pack(anchor="w", padx=15,
                                                                                            pady=(10, 0))
        lbl_val = ctk.CTkLabel(card, text="...", font=("Arial", 20, "bold"), text_color="white")
        lbl_val.pack(anchor="w", padx=15, pady=(0, 5))
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

    def load_data(self):
        m = self.cb_month.get()
        y = self.cb_year.get()
        summary = self.controller.get_dashboard_summary(m, y)
        if self.lbl_val_revenue: self.lbl_val_revenue.configure(text=summary['doanh_thu'])
        if self.lbl_val_orders: self.lbl_val_orders.configure(text=summary['tong_don'])
        if self.lbl_val_customers: self.lbl_val_customers.configure(text=summary['khach_moi'])

        x_data, y_data, table_rows = self.controller.get_chart_and_table_data(self.current_chart_mode, m, y)
        self.draw_chart(x_data, y_data)
        self.update_table(table_rows)
        self.update_btn_styles()

    def switch_chart_mode(self, mode):
        self.current_chart_mode = mode
        self.load_data()

    def update_btn_styles(self):
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
        if not HAS_MATPLOTLIB:
            ctk.CTkLabel(self.chart_frame, text="Thiếu thư viện matplotlib!", text_color="red").pack(expand=True)
            return
        for widget in self.chart_frame.winfo_children(): widget.destroy()
        if not x_labels:
            ctk.CTkLabel(self.chart_frame, text="Không có dữ liệu", text_color="gray").pack(expand=True)
            return

        fig = Figure(figsize=(6, 3), dpi=100)
        ax = fig.add_subplot(111)
        bars = ax.bar(x_labels, y_values, color='#4CAF50', width=0.5)
        ax.set_title('Biểu đồ Doanh thu (VNĐ)', fontsize=10)
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        if len(x_labels) > 10: ax.tick_params(axis='x', labelsize=8, rotation=45)
        ax.get_yaxis().set_major_formatter(lambda x, p: format(int(x), ','))

        for bar in bars:
            height = bar.get_height()
            if height > 0:
                txt = f"{height / 1000000:.1f}M" if height >= 1000000 else f"{height / 1000:.0f}k"
                ax.text(bar.get_x() + bar.get_width() / 2., height, txt, ha='center', va='bottom', fontsize=8)

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)