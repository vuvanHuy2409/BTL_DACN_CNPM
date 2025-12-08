import cv2
import os
import shutil
import numpy as np
import pandas as pd
from datetime import datetime
from PIL import Image
from src.Model.DiemDanhModel import DiemDanhModel
import unicodedata
import threading
import time
import sys


class DiemDanhController:
    def __init__(self):
        self.model = DiemDanhModel()
        self.FACE_DIR = "src/face_data"
        self.TRAINER_DIR = "src/trainer"
        self.TRAINER_FILE = os.path.join(self.TRAINER_DIR, "trained_model.yml")

        if not os.path.exists(self.FACE_DIR): os.makedirs(self.FACE_DIR)
        if not os.path.exists(self.TRAINER_DIR): os.makedirs(self.TRAINER_DIR)

        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.cap = None
        self.is_running = False
        self.thread = None

    def remove_accents(self, input_str):
        if not input_str: return ""
        nfkd = unicodedata.normalize('NFKD', input_str)
        return "".join([c for c in nfkd if not unicodedata.combining(c)])

    def get_list_nv_sorted(self):
        return self.model.get_list_nhan_vien_sorted()

    def check_face_data_exists(self, emp_id):
        d = os.path.join(self.FACE_DIR, f"face_{emp_id}")
        return os.path.exists(d) and len(os.listdir(d)) > 0

    def get_available_cameras(self):
        available_cams = []
        for i in range(4):
            try:
                if sys.platform == "darwin":
                    cap = cv2.VideoCapture(i, cv2.CAP_AVFOUNDATION)
                else:
                    cap = cv2.VideoCapture(i)
                if cap.isOpened(): available_cams.append(i); cap.release()
            except:
                pass
        return available_cams if available_cams else [0]

    def stop_camera(self):
        self.is_running = False
        if self.thread and self.thread.is_alive(): self.thread.join(timeout=1.0)
        if self.cap: self.cap.release(); self.cap = None

    # [MỚI] Hàm xóa dữ liệu khuôn mặt và train lại
    def delete_face_data(self, emp_id):
        user_dir = os.path.join(self.FACE_DIR, f"face_{emp_id}")

        if not os.path.exists(user_dir):
            return False, "Nhân viên này chưa có dữ liệu khuôn mặt!"

        try:
            # 1. Xóa thư mục ảnh
            shutil.rmtree(user_dir)

            # 2. Cập nhật lại model nhận diện (Train lại từ đầu với dữ liệu còn lại)
            if self.train_model():
                return True, "Đã xóa dữ liệu và cập nhật hệ thống thành công!"
            else:
                return True, "Đã xóa dữ liệu! (Hệ thống hiện chưa có khuôn mặt nào khác)"
        except Exception as e:
            return False, f"Lỗi khi xóa: {str(e)}"

    # [CẬP NHẬT] Hàm train model xử lý trường hợp không còn ảnh nào
    def train_model(self):
        faces, ids = [], []
        for root, dirs, files in os.walk(self.FACE_DIR):
            for file in files:
                if file.endswith(".jpg"):
                    try:
                        ids.append(int(os.path.basename(root).replace("face_", "")))
                        faces.append(np.array(Image.open(os.path.join(root, file)).convert("L"), "uint8"))
                    except:
                        pass

        if faces:
            self.recognizer.train(faces, np.array(ids))
            self.recognizer.save(self.TRAINER_FILE)
            return True
        else:
            # Nếu không còn ảnh nào, xóa file model cũ để tránh lỗi nhận diện linh tinh
            if os.path.exists(self.TRAINER_FILE):
                os.remove(self.TRAINER_FILE)
            return False

    def filter_logs_by_date(self, d, m, y):
        try:
            if not y.isdigit(): return []
            if d != "Tất cả" and m != "Tất cả": return self.model.get_logs_filtered(f"{y}-{m.zfill(2)}-{d.zfill(2)}",
                                                                                    'day')
            if m != "Tất cả": return self.model.get_logs_filtered(f"{y}-{m.zfill(2)}", 'month')
            return self.model.get_logs_filtered(y, 'year')
        except:
            return []

    def export_excel_individual(self, idNV, name, month_year):
        parts = month_year.split('/');
        m = int(parts[0]);
        y = int(parts[1])
        data = self.model.get_individual_attendance(idNV, m, y)
        if not data: return False, "Không có dữ liệu!"
        res = []
        for r in data:
            res.append({"Ngày": r['Ngay'], "Vào": r['GioVao'] or "", "Ra": r['GioRa'] or "",
                        "Giờ": round(float(r['tongGioLam'] or 0), 2)})

        # (Giả lập logic pandas)
        try:
            df = pd.DataFrame(res)
            fname = f"BangCong_{self.remove_accents(name).replace(' ', '_')}_{m}_{y}.xlsx"
            df.to_excel(fname, index=False)
            return True, f"Lưu tại: {fname}"
        except Exception as e:
            return False, str(e)

    def start_capture(self, employee_id, update_callback, finish_callback, cam_index=0):
        if self.is_running: return
        user_dir = os.path.join(self.FACE_DIR, f"face_{employee_id}")
        if os.path.exists(user_dir): shutil.rmtree(user_dir)
        os.makedirs(user_dir)

        self.is_running = True
        self.thread = threading.Thread(target=self._capture_loop,
                                       args=(user_dir, update_callback, finish_callback, cam_index))
        self.thread.daemon = True
        self.thread.start()

    def _capture_loop(self, user_dir, update_callback, finish_callback, cam_index):
        if sys.platform == "darwin":
            self.cap = cv2.VideoCapture(cam_index, cv2.CAP_AVFOUNDATION)
        else:
            self.cap = cv2.VideoCapture(cam_index)

        count = 0
        while self.is_running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret: break
            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            status_text = f"Đang thu thập: {count}/50"

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                if count < 50:
                    cv2.imwrite(os.path.join(user_dir, f"{count}.jpg"), gray[y:y + h, x:x + w])
                    count += 1

            if count >= 50:
                self.is_running = False;
                self.cap.release()
                self.train_model()
                finish_callback("Đã thu thập xong 50 ảnh!\nDữ liệu đã được cập nhật.")
                break

            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            update_callback(Image.fromarray(img_rgb), status_text)
            time.sleep(0.05)
        if self.cap: self.cap.release()

    def start_recognition(self, update_callback, success_callback, cam_index=0):
        if self.is_running: return False, "Camera đang chạy!"
        if not os.path.exists(self.TRAINER_FILE): return False, "Chưa có dữ liệu huấn luyện!"

        self.recognizer.read(self.TRAINER_FILE)
        employees = self.model.get_list_nhan_vien_sorted()
        name_map = {emp['idNhanVien']: emp['hoTen'] for emp in employees}

        self.is_running = True
        self.thread = threading.Thread(target=self._recognition_loop,
                                       args=(name_map, update_callback, success_callback, cam_index))
        self.thread.daemon = True
        self.thread.start()
        return True, "Camera đang khởi động..."

    def _recognition_loop(self, name_map, update_callback, success_callback, cam_index):
        if sys.platform == "darwin":
            self.cap = cv2.VideoCapture(cam_index, cv2.CAP_AVFOUNDATION)
        else:
            self.cap = cv2.VideoCapture(cam_index)

        last_check_time = {}
        while self.is_running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret: break
            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            status_text = "Đang tìm kiếm khuôn mặt..."

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                try:
                    id_, conf = self.recognizer.predict(gray[y:y + h, x:x + w])
                    if conf < 55:
                        if id_ in name_map:
                            name = self.remove_accents(name_map[id_])
                            now = time.time()
                            if id_ not in last_check_time or (now - last_check_time[id_] > 60):
                                ok, type_cc, hours = self.model.xu_ly_cham_cong(id_)
                                success_callback(name_map[id_], type_cc, hours)
                                last_check_time[id_] = now
                                cv2.putText(frame, f"{name} - OK", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                                            (0, 255, 0), 2)
                            else:
                                cv2.putText(frame, f"{name} (Done)", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                                            (0, 255, 255), 2)
                        else:
                            cv2.putText(frame, "Nghi Viec", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    else:
                        cv2.putText(frame, "Unknown", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                except:
                    pass

            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            update_callback(Image.fromarray(img_rgb), status_text)
            time.sleep(0.05)
        if self.cap: self.cap.release()