from src.Model.QuenMKModel import QuenMKModel
import hashlib
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class QuenMKController:
    def __init__(self):
        self.model = QuenMKModel()

        # --- CẤU HÌNH EMAIL GỬI (ĐÃ CẬP NHẬT) ---
        self.SENDER_EMAIL = "huyberrrrr@gmail.com"

        # [QUAN TRỌNG] Mật khẩu ứng dụng viết liền, KHÔNG CÓ KHOẢNG TRẮNG
        self.SENDER_PASSWORD = "jsjebyuxxmewcyzv"

        # Biến lưu mã OTP tạm thời
        self.current_otp = None
        self.current_id_tk = None

    def hash_password(self, password):
        return hashlib.md5(password.encode()).hexdigest()

    # --- BƯỚC 1: KIỂM TRA & GỬI OTP ---
    def gui_ma_xac_nhan(self, username, email):
        # Kiểm tra DB
        id_tk = self.model.check_user_email(username, email)
        if not id_tk:
            return False, "Tài khoản hoặc Email không tồn tại trong hệ thống!"

        # Sinh mã OTP ngẫu nhiên 6 số
        otp_code = str(random.randint(100000, 999999))
        self.current_otp = otp_code
        self.current_id_tk = id_tk

        # Gửi Email
        print(f"Đang gửi OTP {otp_code} tới {email}...")  # Log để debug
        if self.send_email_otp(email, otp_code):
            return True, "Mã xác nhận đã được gửi đến Email của bạn!"
        else:
            return False, "Lỗi đăng nhập Email gửi! Vui lòng kiểm tra lại cấu hình Server."

    def send_email_otp(self, receiver_email, otp_code):
        try:
            subject = "MÃ XÁC NHẬN ĐẶT LẠI MẬT KHẨU"
            body = f"""
            Xin chào,

            Bạn đang thực hiện yêu cầu lấy lại mật khẩu.
            Đây là mã xác nhận (OTP) của bạn:

            ====================
            {otp_code}
            ====================

            Vui lòng nhập mã này vào phần mềm để đặt lại mật khẩu.
            Mã này có hiệu lực ngay lập tức. Không chia sẻ mã này cho ai.

            Trân trọng,
            Hệ thống Coffee Shop.
            """

            msg = MIMEMultipart()
            msg['From'] = self.SENDER_EMAIL
            msg['To'] = receiver_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            # Kết nối Gmail
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(self.SENDER_EMAIL, self.SENDER_PASSWORD)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"Lỗi gửi mail OTP chi tiết: {e}")
            return False

    # --- BƯỚC 2: KIỂM TRA OTP ---
    def xac_thuc_otp(self, input_otp):
        if not self.current_otp:
            return False, "Hết phiên làm việc. Vui lòng gửi lại mã!"

        if input_otp.strip() == self.current_otp:
            return True, "Xác thực thành công!"
        else:
            return False, "Mã xác nhận không đúng!"

    # --- BƯỚC 3: ĐỔI MẬT KHẨU ---
    def luu_mat_khau_moi(self, new_pass, confirm_pass):
        if not self.current_id_tk:
            return False, "Lỗi phiên làm việc!"

        if len(new_pass) < 6:
            return False, "Mật khẩu phải từ 6 ký tự trở lên!"

        if new_pass != confirm_pass:
            return False, "Mật khẩu xác nhận không khớp!"

        pass_hash = self.hash_password(new_pass)

        # Gọi Model cập nhật và mở khóa tài khoản
        if self.model.reset_password(self.current_id_tk, pass_hash):
            self.current_otp = None
            self.current_id_tk = None
            return True, "Đổi mật khẩu thành công! Hãy đăng nhập lại."

        return False, "Lỗi cập nhật CSDL!"