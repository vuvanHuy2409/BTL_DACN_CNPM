import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk

# Thư viện vẽ biểu đồ (Cần pip install matplotlib)
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

class ThongKePage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="white")
        
        # Dữ liệu giả lập
        self.stats_data = [
            ("01/11/2025", "150", "45,000,000", "20,000,000", "25,000,000"),
            ("02/11/2025", "120", "38,000,000", "18,000,000", "20,000,000"),
            ("03/11/2025", "200", "60,000,000", "30,000,000", "30,000,000"),
            ("04/11/2025", "180", "52,000,000", "25,000,000", "27,000,000"),
            ("05/11/2025", "160", "48,000,000", "22,000,000", "26,000,000"),
        ]

        self.tao_main_content()
        self.load_table_data()

    def tao_main_content(self):
        """Tạo nội dung chính"""
        container = ctk.CTkFrame(self, fg_color="white")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # === 1. HEADER & FILTER ===
        header = ctk.CTkFrame(container, fg_color="white")
        header.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(header, text="BÁO CÁO THỐNG KÊ", font=("Arial", 20, "bold"), text_color="#333").pack(side="left")

        # Bộ lọc bên phải
        filter_frame = ctk.CTkFrame(header, fg_color="white")
        filter_frame.pack(side="right")

        ctk.CTkLabel(filter_frame, text="Tháng:", font=("Arial", 12), text_color="#555").pack(side="left", padx=(0, 5))
        ctk.CTkComboBox(filter_frame, values=[str(i) for i in range(1, 13)], width=70, state="readonly").pack(side="left", padx=(0, 15))
        
        ctk.CTkLabel(filter_frame, text="Năm:", font=("Arial", 12), text_color="#555").pack(side="left", padx=(0, 5))
        ctk.CTkComboBox(filter_frame, values=["2023", "2024", "2025"], width=80, state="readonly").pack(side="left", padx=(0, 15))

        ctk.CTkButton(filter_frame, text="Lọc dữ liệu", fg_color="#2196F3", hover_color="#1976D2", width=100, height=32).pack(side="left")

        # === 2. DASHBOARD CARDS (THẺ TỔNG QUAN) ===
        cards_frame = ctk.CTkFrame(container, fg_color="white")
        cards_frame.pack(fill="x", pady=(0, 20))
        
        # Helper tạo thẻ
        def create_card(parent, title, value, color, icon):
            card = ctk.CTkFrame(parent, fg_color=color, corner_radius=10, height=80)
            card.pack(side="left", fill="x", expand=True, padx=10)
            card.pack_propagate(False)
            
            ctk.CTkLabel(card, text=title, font=("Arial", 12, "bold"), text_color="white").pack(anchor="w", padx=15, pady=(10, 0))
            ctk.CTkLabel(card, text=value, font=("Arial", 22, "bold"), text_color="white").pack(anchor="w", padx=15, pady=(0, 5))
            ctk.CTkLabel(card, text=icon, font=("Arial", 30), text_color="white").place(relx=0.9, rely=0.5, anchor="e")

        create_card(cards_frame, "DOANH THU THÁNG", "243,000,000 ₫", "#4CAF50", "💰") # Xanh lá
        create_card(cards_frame, "TỔNG ĐƠN HÀNG", "1,240 Đơn", "#FF9800", "🛒")      # Cam
        create_card(cards_frame, "KHÁCH HÀNG MỚI", "85 Khách", "#2196F3", "👥")       # Xanh dương

        # === 3. BIỂU ĐỒ (CHART) ===
        chart_container = ctk.CTkFrame(container, fg_color="white", border_width=1, border_color="#ccc")
        chart_container.pack(fill="both", expand=True, pady=(0, 20))
        
        ctk.CTkLabel(chart_container, text="Biểu đồ Doanh thu 7 ngày gần nhất", font=("Arial", 12, "bold"), text_color="#555").pack(anchor="w", padx=10, pady=5)
        
        self.chart_frame = ctk.CTkFrame(chart_container, fg_color="white")
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.draw_chart() # Vẽ biểu đồ

        # === 4. BẢNG CHI TIẾT ===
        detail_frame = ctk.CTkFrame(container, fg_color="white")
        detail_frame.pack(fill="both", expand=True)

        # Toolbar bảng
        tbl_toolbar = ctk.CTkFrame(detail_frame, fg_color="white")
        tbl_toolbar.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(tbl_toolbar, text="Chi tiết doanh thu", font=("Arial", 14, "bold"), text_color="#333").pack(side="left")
        ctk.CTkButton(tbl_toolbar, text="Xuất Excel", fg_color="#00BCD4", hover_color="#0097A7", width=100, height=30, text_color="white").pack(side="right")

        # Table Frame
        table_container = ctk.CTkFrame(detail_frame, fg_color="white", border_width=1, border_color="#ccc")
        table_container.pack(fill="both", expand=True)

        # Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground="black", rowheight=30, fieldbackground="white", font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#f0f0f0", foreground="#333")
        style.map("Treeview", background=[("selected", "#2196F3")])

        # Treeview
        cols = ("ngay", "donhang", "doanhthu", "chiphi", "loinhuan")
        self.tree = ttk.Treeview(table_container, columns=cols, show="headings", height=5)
        
        self.tree.heading("ngay", text="Ngày")
        self.tree.heading("donhang", text="Số đơn hàng")
        self.tree.heading("doanhthu", text="Doanh thu")
        self.tree.heading("chiphi", text="Chi phí")
        self.tree.heading("loinhuan", text="Lợi nhuận")

        self.tree.column("ngay", anchor="center", width=100)
        self.tree.column("donhang", anchor="center", width=80)
        self.tree.column("doanhthu", anchor="e", width=150)
        self.tree.column("chiphi", anchor="e", width=150)
        self.tree.column("loinhuan", anchor="e", width=150)

        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=1, pady=1)

    def draw_chart(self):
        """Vẽ biểu đồ sử dụng Matplotlib"""
        if not HAS_MATPLOTLIB:
            ctk.CTkLabel(self.chart_frame, text="Chưa cài đặt thư viện matplotlib.\nVui lòng chạy 'pip install matplotlib'", text_color="red").pack(expand=True)
            return

        # Tạo dữ liệu biểu đồ
        days = ['01/11', '02/11', '03/11', '04/11', '05/11']
        revenue = [45, 38, 60, 52, 48] # Đơn vị: Triệu

        # Tạo Figure
        fig = Figure(figsize=(6, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        # Vẽ biểu đồ cột
        bars = ax.bar(days, revenue, color='#4CAF50', width=0.5)
        
        # Style biểu đồ
        ax.set_title('Doanh thu (Triệu VNĐ)', fontsize=10)
        ax.set_ylabel('Triệu VNĐ')
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Thêm số liệu trên cột
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval + 0.5, f'{yval}tr', ha='center', va='bottom', fontsize=8)

        # Embed vào Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def load_table_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in self.stats_data:
            self.tree.insert("", "end", values=row)