import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import tkinter as tk
from datetime import datetime
from PIL import Image, ImageTk
from src.Controller.DiemDanhController import DiemDanhController
import threading


class DiemDanhPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="white")

        self.controller = DiemDanhController()

        self.selected_id = None
        self.selected_name = None

        self.current_cam_image = None
        self.cam_window = None  # Biến quản lý cửa sổ popup camera
        self.current_cam_index = 0

        self.tao_main_content()
        self.load_table_data()
        self.load_log_data()

    def tao_main_content(self):
        # Chia lưới: 7 phần trái (Danh sách), 3 phần phải (Log)
        self.grid_columnconfigure(0, weight=7)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # ================= KHUNG TRÁI =================
        left_frame = ctk.CTkFrame(self, fg_color="white")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)

        ctk.CTkLabel(left_frame, text="Quản Lý Điểm Danh", font=("Arial", 18, "bold"), text_color="#333").pack(
            anchor="w", pady=(0, 10))

        # --- Button Box ---
        btn_box = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_box.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(btn_box, text="📸 Đăng ký Face", fg_color="#FF9800", hover_color="#F57C00",
                      width=110, height=35, command=self.open_capture_window).pack(side="left", padx=5)

        ctk.CTkButton(btn_box, text="🗑️ Xóa Face", fg_color="#F44336", hover_color="#D32F2F",
                      width=100, height=35, command=self.xoa_face).pack(side="left", padx=5)

        ctk.CTkButton(btn_box, text="✅ Điểm danh", fg_color="#2196F3", hover_color="#1976D2",
                      width=120, height=35, command=self.open_attendance_window).pack(side="left", padx=5)

        ctk.CTkButton(btn_box, text="🔃 Tải lại", fg_color="#9E9E9E", hover_color="#757575",
                      width=80, height=35, command=self.reload_all).pack(side="left", padx=5)

        ctk.CTkButton(btn_box, text="📊 Excel", fg_color="#009688", hover_color="#00796B",
                      width=80, height=35, command=self.export_excel).pack(side="right", padx=5)

        # --- Table ---
        table_frame = ctk.CTkFrame(left_frame, fg_color="white")
        table_frame.pack(fill="both", expand=True)

        cols = ("id", "ten", "chucvu", "face_status", "gio_vao", "gio_ra", "trangthai_chamcong")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=15)

        # Định nghĩa cột
        self.tree.heading("id", text="ID");
        self.tree.column("id", width=40, anchor="center")
        self.tree.heading("ten", text="Họ Tên");
        self.tree.column("ten", width=180)
        self.tree.heading("chucvu", text="Chức Vụ");
        self.tree.column("chucvu", width=100)
        self.tree.heading("face_status", text="Dữ liệu Face");
        self.tree.column("face_status", width=100, anchor="center")
        self.tree.heading("gio_vao", text="Giờ Vào");
        self.tree.column("gio_vao", width=80, anchor="center")
        self.tree.heading("gio_ra", text="Giờ Ra");
        self.tree.column("gio_ra", width=80, anchor="center")
        self.tree.heading("trangthai_chamcong", text="Trạng Thái");
        self.tree.column("trangthai_chamcong", width=120, anchor="center")

        # Màu sắc
        self.tree.tag_configure('chua_vao', background='#FFEBEE')
        self.tree.tag_configure('dang_lam', background='#FFFDE7')
        self.tree.tag_configure('da_ve', background='#E8F5E9')

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select_row)

        # ================= KHUNG PHẢI =================
        right_frame = ctk.CTkFrame(self, fg_color="#f5f5f5", border_width=1, border_color="#ccc")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)

        ctk.CTkLabel(right_frame, text="NHẬT KÝ HOẠT ĐỘNG", font=("Arial", 14, "bold"), text_color="#555").pack(
            pady=(10, 5))

        # --- Filter ---
        filter_box = ctk.CTkFrame(right_frame, fg_color="transparent")
        filter_box.pack(fill="x", padx=5, pady=5)

        days = ["Tất cả"] + [str(i) for i in range(1, 32)]
        self.cb_day = ctk.CTkComboBox(filter_box, values=days, width=65, state="readonly")
        self.cb_day.pack(side="left", padx=2)

        months = ["Tất cả"] + [str(i) for i in range(1, 13)]
        self.cb_month = ctk.CTkComboBox(filter_box, values=months, width=65, state="readonly")
        self.cb_month.pack(side="left", padx=2)

        self.entry_year = ctk.CTkEntry(filter_box, width=50, placeholder_text="Năm")
        self.entry_year.pack(side="left", padx=2)

        now = datetime.now()
        self.cb_day.set(str(now.day))
        self.cb_month.set(str(now.month))
        self.entry_year.insert(0, str(now.year))

        ctk.CTkButton(filter_box, text="Lọc", width=50, height=28, command=self.filter_logs).pack(side="left", padx=2)

        # --- Log Table ---
        self.log_tree = ttk.Treeview(right_frame, columns=("time", "content"), show="headings", height=20)
        self.log_tree.heading("time", text="Thời gian");
        self.log_tree.column("time", width=100, anchor="center")
        self.log_tree.heading("content", text="Nội dung");
        self.log_tree.column("content", width=180)
        self.log_tree.pack(fill="both", expand=True, padx=5, pady=5)

    # ================= LOGIC DỮ LIỆU =================
    def reload_all(self):
        self.load_table_data()
        self.filter_logs()
        # Không show thông báo mỗi lần reload để đỡ phiền, trừ khi cần thiết

    def load_table_data(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        employees = self.controller.get_list_nv_sorted()
        for emp in employees:
            status_code = emp['trangThai']
            tag = 'chua_vao'
            status_text = "Chưa vào"
            if status_code == 1:
                tag = 'dang_lam'; status_text = "Đang làm"
            elif status_code == 2:
                tag = 'da_ve'; status_text = "Đã về"

            has_face = self.controller.check_face_data_exists(emp['idNhanVien'])
            face_text = "Đã có" if has_face else "Chưa có"
            gv = emp['gioVao'].strftime("%H:%M") if emp['gioVao'] else ""
            gr = emp['gioRa'].strftime("%H:%M") if emp['gioRa'] else ""

            self.tree.insert("", "end", values=(
                emp['idNhanVien'], emp['hoTen'], emp['tenChucVu'],
                face_text, gv, gr, status_text
            ), tags=(tag,))

    def filter_logs(self):
        d, m, y = self.cb_day.get(), self.cb_month.get(), self.entry_year.get()
        for i in self.log_tree.get_children(): self.log_tree.delete(i)

        logs = self.controller.filter_logs_by_date(d, m, y)
        if not logs and d != "Tất cả":
            self.log_tree.insert("", "end", values=("---", "Không có dữ liệu"))
            return

        for log in logs:
            time_str = log['gioVao'].strftime("%d/%m %H:%M")
            self.log_tree.insert("", "end", values=(time_str, f"{log['hoTen']} (Vào)"))
            if log['gioRa']:
                time_out = log['gioRa'].strftime("%d/%m %H:%M")
                self.log_tree.insert("", "end", values=(time_out, f"{log['hoTen']} (Ra)"))

    def load_log_data(self):
        self.filter_logs()

    def on_select_row(self, event):
        sel = self.tree.selection()
        if sel:
            item = self.tree.item(sel[0])
            self.selected_id = item['values'][0]
            self.selected_name = item['values'][1]

    def add_log_ui(self, message):
        time_str = datetime.now().strftime("%d/%m %H:%M")
        self.log_tree.insert("", 0, values=(time_str, message))

    def export_excel(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên!")
            return
        now = datetime.now()
        default_name = f"BangCong_{str(self.selected_name).replace(' ', '_')}_{now.month}_{now.year}.xlsx"
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")],
                                                 initialfile=default_name)
        if not file_path: return

        ok, msg = self.controller.export_excel_individual(self.selected_id, now.strftime("%m/%Y"), file_path)
        if ok:
            messagebox.showinfo("Thành công", msg)
        else:
            messagebox.showerror("Lỗi", msg)

    def xoa_face(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên!")
            return
        if messagebox.askyesno("Xác nhận", f"Xóa dữ liệu Face của: {self.selected_name}?"):
            ok, msg = self.controller.delete_face_data(self.selected_id)
            if ok:
                messagebox.showinfo("Thành công", msg)
                self.add_log_ui(f"Xóa Face: {self.selected_name}")
                self.load_table_data()
            else:
                messagebox.showerror("Lỗi", msg)

    # ================= LOGIC CAMERA =================
    def _safe_update_image(self, pil_img, status_text):
        # [FIX] Kiểm tra chặt chẽ xem window còn tồn tại không
        if not self.cam_window or not self.cam_window.winfo_exists(): return
        try:
            if pil_img:
                self.current_cam_image = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(580, 400))
                # Kiểm tra label còn tồn tại không trước khi config
                if hasattr(self, 'cam_label') and self.cam_label.winfo_exists():
                    self.cam_label.configure(image=self.current_cam_image, text="")

            if status_text and hasattr(self, 'status_label') and self.status_label.winfo_exists():
                self.status_label.configure(text=status_text)
        except Exception:
            pass

    def close_cam_window(self):
        """Hàm đóng cửa sổ Camera an toàn"""
        self.controller.stop_camera()
        self.current_cam_image = None

        if self.cam_window and self.cam_window.winfo_exists():
            self.cam_window.destroy()

        self.cam_window = None  # [FIX] Reset về None

    # --- 1. THU THẬP MẪU ---
    def open_capture_window(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên!")
            return

        # Nếu đang mở rồi thì focus
        if self.cam_window and self.cam_window.winfo_exists():
            self.cam_window.focus()
            return

        self.cam_window = ctk.CTkToplevel(self)
        self.cam_window.title(f"Thu thập: {self.selected_name}")
        self.cam_window.geometry("600x650")
        self.cam_window.attributes("-topmost", True)

        # [FIX] Bắt sự kiện bấm nút X trên thanh tiêu đề
        self.cam_window.protocol("WM_DELETE_WINDOW", self.close_cam_window)

        # UI Camera
        cam_frame = ctk.CTkFrame(self.cam_window, fg_color="transparent")
        cam_frame.pack(pady=(10, 0))

        # Combo chọn camera
        available_cams = self.controller.get_available_cameras()
        cam_values = [f"Camera {i}" for i in available_cams]
        self.cb_camera = ctk.CTkComboBox(cam_frame, values=cam_values, state="readonly", width=150,
                                         command=self.on_change_camera_capture)
        self.cb_camera.set(cam_values[0])
        self.cb_camera.pack(side="left", padx=5)
        self.current_cam_index = available_cams[0]

        self.cam_label = ctk.CTkLabel(self.cam_window, text="Khởi động...", width=580, height=400, fg_color="black")
        self.cam_label.pack(pady=10)

        self.status_label = ctk.CTkLabel(self.cam_window, text="Giữ khuôn mặt trước camera...",
                                         font=("Arial", 16, "bold"))
        self.status_label.pack(pady=5)

        self.btn_close_cam = ctk.CTkButton(self.cam_window, text="Dừng lại", fg_color="red",
                                           command=self.close_cam_window)
        self.btn_close_cam.pack(pady=5)

        self.start_capture_process(self.current_cam_index)

    def on_change_camera_capture(self, choice):
        new_index = int(choice.split(" ")[1])
        if new_index != self.current_cam_index:
            self.current_cam_index = new_index
            self.controller.stop_camera()
            self.after(500, lambda: self.start_capture_process(new_index))

    def start_capture_process(self, cam_idx):
        def ui_callback(pil_img, text, loop=None):
            self.after(0, lambda: self._safe_update_image(pil_img, text))

        def on_finish(msg):
            self.after(0, lambda: self._safe_finish_capture(msg))

        self.controller.start_capture(self.selected_id, ui_callback, on_finish, cam_index=cam_idx)

    def _safe_finish_capture(self, msg):
        if not self.cam_window or not self.cam_window.winfo_exists(): return
        try:
            self.current_cam_image = None
            self.cam_label.configure(image=None, text="HOÀN TẤT", fg_color="#333")
            self.status_label.configure(text="✅ " + msg, text_color="green")
            self.add_log_ui(f"Cập nhật Face: {self.selected_name}")
            self.reload_all()
        except:
            pass

    # --- 2. ĐIỂM DANH ---
    def open_attendance_window(self):
        if self.cam_window and self.cam_window.winfo_exists():
            self.cam_window.focus()
            return

        self.cam_window = ctk.CTkToplevel(self)
        self.cam_window.title("Quét Điểm Danh")
        self.cam_window.geometry("600x650")
        self.cam_window.attributes("-topmost", True)

        # [FIX] Bắt sự kiện bấm nút X
        self.cam_window.protocol("WM_DELETE_WINDOW", self.close_cam_window)

        cam_frame = ctk.CTkFrame(self.cam_window, fg_color="transparent")
        cam_frame.pack(pady=(10, 0))

        available_cams = self.controller.get_available_cameras()
        cam_values = [f"Camera {i}" for i in available_cams]
        self.cb_camera = ctk.CTkComboBox(cam_frame, values=cam_values, state="readonly", width=150,
                                         command=self.on_change_camera_attendance)
        self.cb_camera.set(cam_values[0])
        self.cb_camera.pack(side="left", padx=5)
        self.current_cam_index = available_cams[0]

        self.cam_label = ctk.CTkLabel(self.cam_window, text="Đang khởi động...", width=580, height=400,
                                      fg_color="black")
        self.cam_label.pack(pady=10)

        self.status_label = ctk.CTkLabel(self.cam_window, text="Đang quét...", font=("Arial", 16, "bold"))
        self.status_label.pack(pady=5)

        ctk.CTkButton(self.cam_window, text="Dừng & Thoát", fg_color="#F44336", hover_color="#D32F2F",
                      command=self.close_cam_window).pack(pady=10)

        self.start_attendance_process(self.current_cam_index)

    def on_change_camera_attendance(self, choice):
        new_index = int(choice.split(" ")[1])
        if new_index != self.current_cam_index:
            self.current_cam_index = new_index
            self.controller.stop_camera()
            self.after(500, lambda: self.start_attendance_process(new_index))

    def start_attendance_process(self, cam_idx):
        def ui_callback(pil_img, text, loop=None):
            self.after(0, lambda: self._safe_update_image(pil_img, text))

        def on_success(name, type_cc, hours):
            self.after(0, lambda: self._safe_success_attendance(name, type_cc, hours))

        ok, msg = self.controller.start_recognition(ui_callback, on_success, cam_index=cam_idx)
        if not ok:
            messagebox.showerror("Lỗi", msg)
            self.close_cam_window()

    def _safe_success_attendance(self, name, type_cc, hours):
        if not self.cam_window or not self.cam_window.winfo_exists(): return
        try:
            msg = f"{name}: {type_cc}"
            if hours > 0: msg += f" ({hours}h)"
            self.status_label.configure(text=f"✅ {msg}", text_color="green")
            self.add_log_ui(msg)

            # Cập nhật lại bảng để đổi màu trạng thái nhân viên
            self.load_table_data()

            self.after(2000, lambda: self.reset_status_label())
        except:
            pass

    def reset_status_label(self):
        if self.cam_window and self.cam_window.winfo_exists():
            self.status_label.configure(text="Đang quét người tiếp theo...", text_color="#333")