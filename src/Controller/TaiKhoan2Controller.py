from src.Model.TaiKhoan2Model import TaiKhoan2Model
import hashlib


class TaiKhoan2Controller:
    def __init__(self):
        self.model = TaiKhoan2Model()

    def hash_password(self, password):
        return hashlib.md5(password.encode()).hexdigest()

    def get_info(self, id_nv):
        return self.model.get_employee_info(id_nv)

    def save_info(self, id_nv, ho_ten, sdt, email):
        if not ho_ten or not sdt:
            return False, "Họ tên và SĐT không được để trống!"

        # Có thể thêm validate email ở đây nếu cần

        if self.model.update_info(id_nv, ho_ten, sdt, email):
            return True, "Cập nhật thông tin thành công!"
        return False, "Lỗi cập nhật CSDL!"

    def change_password(self, id_tai_khoan, old_pass, new_pass, confirm_pass):
        if not old_pass or not new_pass:
            return False, "Vui lòng nhập đầy đủ mật khẩu!"
        if new_pass != confirm_pass:
            return False, "Mật khẩu xác nhận không khớp!"
        if len(new_pass) < 6:
            return False, "Mật khẩu mới phải từ 6 ký tự!"

        old_hash = self.hash_password(old_pass)
        new_hash = self.hash_password(new_pass)

        if not self.model.verify_password(id_tai_khoan, old_hash):
            return False, "Mật khẩu cũ không chính xác!"

        if self.model.change_password(id_tai_khoan, new_hash):
            return True, "Đổi mật khẩu thành công!"
        return False, "Lỗi hệ thống!"