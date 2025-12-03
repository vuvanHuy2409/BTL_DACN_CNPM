import cv2
import os
import shutil
import numpy as np
import pandas as pd
from datetime import datetime
from PIL import Image
from src.Model.DiemDanhModel import DiemDanhModel
import unicodedata


class DiemDanhController:
    def __init__(self):
        self.model = DiemDanhModel()

        # Cấu hình đường dẫn
        self.FACE_DIR = "src/face_data"
        self.TRAINER_DIR = "src/trainer"
        self.TRAINER_FILE = os.path.join(self.TRAINER_DIR, "trained_model.yml")

        # Tạo thư mục nếu chưa có
        if not os.path.exists(self.FACE_DIR): os.makedirs(self.FACE_DIR)
        if not os.path.exists(self.TRAINER_DIR): os.makedirs(self.TRAINER_DIR)

        # Khởi tạo OpenCV
        # Lưu ý: Cần file haarcascade_frontalface_default.xml trong thư mục cv2.data.haarcascades
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()

        self.cap = None
        self.is_running = False

    # ================= 1. CÁC HÀM HỖ TRỢ LOGIC =================

    def remove_accents(self, input_str):
        """Chuyển tiếng Việt có dấu thành không dấu để hiển thị lên OpenCV"""
        if not input_str: return ""
        nfkd_form = unicodedata.normalize('NFKD', input_str)
        return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

    def get_list_nv_sorted(self):
        """Lấy danh sách nhân viên kèm trạng thái màu sắc"""
        return self.model.get_list_nhan_vien_sorted()

    def check_face_data_exists(self, emp_id):
        """Kiểm tra xem nhân viên đã có dữ liệu khuôn mặt chưa"""
        user_dir = os.path.join(self.FACE_DIR, f"face_{emp_id}")
        return os.path.exists(user_dir) and len(os.listdir(user_dir)) > 0

    def stop_camera(self):
        """Dừng camera an toàn"""
        self.is_running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

    # ================= 2. XỬ LÝ LỌC VÀ XUẤT EXCEL =================

    def filter_logs_by_date(self, day, month, year):
        """
        Xử lý logic lọc nhật ký:
        - day: '1'..'31' hoặc 'Tất cả'
        - month: '1'..'12' hoặc 'Tất cả'
        - year: '2025' (chuỗi nhập từ Entry)
        """
        try:
            if not year.isdigit(): return []

            # 1. Lọc theo NGÀY (yyyy-mm-dd)
            if day != "Tất cả" and month != "Tất cả":
                date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                return self.model.get_logs_filtered(date_str, 'day')

            # 2. Lọc theo THÁNG (yyyy-mm)
            if month != "Tất cả":
                date_str = f"{year}-{month.zfill(2)}"
                return self.model.get_logs_filtered(date_str, 'month')

            # 3. Lọc theo NĂM (yyyy)
            return self.model.get_logs_filtered(year, 'year')

        except Exception as e:
            print(f"Lỗi filter: {e}")
            return []

    def export_excel_individual(self, idNV, name, month_year):
        """Xuất bảng công chi tiết của 1 nhân viên"""
        try:
            # month_year format: mm/yyyy
            parts = month_year.split('/')
            month = int(parts[0])
            year = int(parts[1])

            # Lấy dữ liệu từ Model
            data = self.model.get_individual_attendance(idNV, month, year)

            if not data:
                return False, f"Không có dữ liệu chấm công tháng {month_year}!"

            # Chuẩn bị dữ liệu cho Pandas
            export_list = []
            total_hours = 0

            for row in data:
                # Format dữ liệu cho đẹp
                gio_vao = str(row['GioVao']) if row['GioVao'] else ""
                gio_ra = str(row['GioRa']) if row['GioRa'] else ""

                # Xử lý số giờ làm (có thể là None hoặc Decimal)
                try:
                    gio_lam = float(row['tongGioLam']) if row['tongGioLam'] else 0.0
                except:
                    gio_lam = 0.0

                total_hours += gio_lam

                export_list.append({
                    "Ngày": row['Ngay'],
                    "Giờ Vào": gio_vao,
                    "Giờ Ra (Cuối)": gio_ra,
                    "Số Giờ Công": round(gio_lam, 2)
                })

            # Thêm dòng tổng cộng
            export_list.append({
                "Ngày": "TỔNG CỘNG",
                "Giờ Vào": "",
                "Giờ Ra (Cuối)": "",
                "Số Giờ Công": round(total_hours, 2)
            })

            # Xuất file
            df = pd.DataFrame(export_list)

            # Tạo tên file an toàn (thay khoảng trắng bằng _)
            safe_name = self.remove_accents(name).replace(" ", "_")
            filename = f"BangCong_{safe_name}_{month}_{year}.xlsx"

            df.to_excel(filename, index=False)

            return True, f"Đã xuất file thành công:\n{filename}"
        except Exception as e:
            return False, f"Lỗi xuất Excel: {str(e)}"

    # ================= 3. LOGIC OPENCV: THU THẬP & TRAIN =================

    def start_capture(self, employee_id, update_callback, finish_callback):
        """Thu thập 50 ảnh khuôn mặt"""
        # Tạo/Xóa thư mục cũ
        user_dir = os.path.join(self.FACE_DIR, f"face_{employee_id}")
        if os.path.exists(user_dir):
            shutil.rmtree(user_dir)  # Xóa để thay thế
        os.makedirs(user_dir)

        self.cap = cv2.VideoCapture(0)
        self.is_running = True
        count = 0

        def loop():
            nonlocal count
            if not self.is_running: return

            ret, frame = self.cap.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                    # Chỉ lưu 1 ảnh mỗi frame
                    if count < 50:
                        face_img = gray[y:y + h, x:x + w]
                        cv2.imwrite(os.path.join(user_dir, f"{count}.jpg"), face_img)
                        count += 1

                # Convert ảnh để hiển thị lên Tkinter
                img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img_pil = Image.fromarray(img_rgb)

                update_callback(img_pil, f"Đang thu thập: {count}/50")

                if count >= 50:
                    self.stop_camera()
                    self.train_model()  # Tự động train sau khi thu thập
                    finish_callback("Đã thu thập xong 50 ảnh!\nDữ liệu đã được cập nhật.")
                    return

            if self.is_running:
                update_callback(None, None, loop)

        loop()

    def train_model(self):
        """Huấn luyện model từ dữ liệu ảnh"""
        faces = []
        ids = []

        # Duyệt qua các thư mục face_ID
        for root, dirs, files in os.walk(self.FACE_DIR):
            for file in files:
                if file.endswith(".jpg"):
                    path = os.path.join(root, file)
                    try:
                        # Lấy ID từ tên thư mục (face_1 -> 1)
                        label = int(os.path.basename(root).replace("face_", ""))

                        pil_image = Image.open(path).convert("L")  # Grayscale
                        image_array = np.array(pil_image, "uint8")

                        faces.append(image_array)
                        ids.append(label)
                    except:
                        pass

        if faces:
            self.recognizer.train(faces, np.array(ids))
            self.recognizer.save(self.TRAINER_FILE)
            return True
        return False

    # ================= 4. LOGIC OPENCV: NHẬN DIỆN & CHẤM CÔNG =================

    def start_recognition(self, update_callback, success_callback):
        """Chạy camera nhận diện và chấm công"""
        if not os.path.exists(self.TRAINER_FILE):
            return False, "Chưa có dữ liệu huấn luyện!"

        self.recognizer.read(self.TRAINER_FILE)

        # Lấy danh sách nhân viên để map ID -> Tên
        employees = self.model.get_list_nhan_vien_sorted()
        name_map = {emp['idNhanVien']: emp['hoTen'] for emp in employees}

        self.cap = cv2.VideoCapture(0)
        self.is_running = True

        # Set lưu các ID đã chấm công trong phiên mở camera này (tránh spam liên tục)
        session_scanned = set()

        def loop():
            if not self.is_running: return

            ret, frame = self.cap.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    face_img = gray[y:y + h, x:x + w]

                    try:
                        # Dự đoán
                        id_, conf = self.recognizer.predict(face_img)

                        # Độ tin cậy (càng thấp càng tốt, < 55 là khá chắc chắn)
                        if conf < 55:
                            if id_ in name_map:
                                full_name = name_map[id_]
                                # Chuyển tên thành không dấu để vẽ lên Camera không bị lỗi font
                                name_unsigned = self.remove_accents(full_name)

                                # Nếu chưa quét trong phiên này
                                if id_ not in session_scanned:
                                    # Gọi Model chấm công (Check-in hoặc Check-out)
                                    ok, type_cc, hours = self.model.xu_ly_cham_cong(id_)

                                    # Đánh dấu đã quét
                                    session_scanned.add(id_)

                                    # Gửi thông tin về View để hiện thông báo/Log
                                    success_callback(full_name, type_cc, hours)

                                    cv2.putText(frame, f"{name_unsigned} - OK", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                                0.8, (0, 255, 0), 2)
                                else:
                                    # Đã quét rồi thì hiện thông báo đã xong
                                    cv2.putText(frame, f"{name_unsigned} (Done)", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                                0.8, (0, 255, 255), 2)
                            else:
                                # ID có trong model nhưng không có trong DB (đã nghỉ việc)
                                cv2.putText(frame, "Unknown (Nghi)", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                                            (0, 0, 255), 2)
                        else:
                            cv2.putText(frame, "Unknown", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    except:
                        pass

                # Convert ảnh và update UI
                img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img_pil = Image.fromarray(img_rgb)
                update_callback(img_pil, "Đang quét...", loop)
            else:
                if self.is_running: update_callback(None, None, loop)

        loop()
        return True, "Camera On"