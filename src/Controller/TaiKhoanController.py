from src.Model.TaiKhoanModel import TaiKhoanModel
import hashlib


class TaiKhoanController:
    def __init__(self):
        self.model = TaiKhoanModel()

    def get_list(self):
        return self.model.get_all()

    def hash_password(self, password):
        return hashlib.md5(password.encode()).hexdigest()

    def save_account(self, idNV, has_account, name, user, password, email, role_name):
        # 1. Validate
        if not name or not role_name:
            return False, "Thiếu tên hoặc chức vụ!"

        if not has_account and (not user or not password):
            return False, "Tài khoản mới cần Tên đăng nhập và Mật khẩu!"

        role_id = self.model.get_role_id(role_name)

        if not has_account and self.model.check_user_exist(user):
            return False, "Tên đăng nhập đã tồn tại!"

        # 2. Chuẩn bị dữ liệu (Gọn nhẹ hơn, không còn ảnh)
        data = {
            "name": name,
            "user": user,
            "pass": self.hash_password(password) if password else None,
            "email": email,
            "role_id": role_id
        }

        # 3. Gọi Model
        if has_account:
            if self.model.update_info(idNV, data):
                return True, "Cập nhật thành công!"
            return False, "Lỗi cập nhật!"
        else:
            if self.model.create_account_for_existing(idNV, data):
                return True, "Đã cấp tài khoản thành công!"
            return False, "Lỗi cấp tài khoản!"

    def delete_account_only(self, idNV):
        if self.model.remove_account(idNV):
            return True, "Đã xóa tài khoản!"
        return False, "Lỗi xóa tài khoản!"