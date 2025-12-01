from src.Model.TaiKhoanModel import TaiKhoanModel
import hashlib
import shutil
import os
import time


class TaiKhoanController:
    def __init__(self):
        self.model = TaiKhoanModel()

        # Tạo thư mục lưu ảnh
        self.img_dir = "src/images"
        if not os.path.exists(self.img_dir):
            os.makedirs(self.img_dir)

    def get_list(self):
        return self.model.get_all()

    def hash_password(self, password):
        return hashlib.md5(password.encode()).hexdigest()

    def save_image_to_project(self, source_path):
        """Copy ảnh vào thư mục dự án và trả về đường dẫn tương đối"""
        if not source_path or not os.path.exists(source_path):
            return None

        # Nếu ảnh đã ở trong folder dự án rồi thì không copy lại
        if "src/images" in source_path:
            return source_path

        try:
            filename = os.path.basename(source_path)
            name, ext = os.path.splitext(filename)
            # Đặt tên file theo timestamp để không trùng
            new_filename = f"avatar_{int(time.time())}{ext}"
            destination = os.path.join(self.img_dir, new_filename)

            shutil.copy(source_path, destination)
            return destination
        except Exception as e:
            print(f"Lỗi copy ảnh: {e}")
            return None

    def save_account(self, idNV, has_account, name, user, password, email, role_name, raw_image_path):
        # 1. Validate thông tin cơ bản
        if not name or not role_name:
            return False, "Thiếu tên hoặc chức vụ!"

        # Validate User/Pass cho tài khoản mới
        if not has_account and (not user or not password):
            return False, "Tài khoản mới cần Tên đăng nhập và Mật khẩu!"

        # [YÊU CẦU MỚI] Bắt buộc chọn ảnh khi thêm mới
        if not has_account and not raw_image_path:
            return False, "Vui lòng chọn ảnh đại diện trước khi lưu!"

        role_id = self.model.get_role_id(role_name)

        # Check trùng user
        if not has_account and self.model.check_user_exist(user):
            return False, "Tên đăng nhập đã tồn tại!"

        # 2. Xử lý ảnh: Copy vào src/images
        final_image_path = self.save_image_to_project(raw_image_path)

        # 3. Chuẩn bị dữ liệu
        data = {
            "name": name,
            "user": user,
            "pass": self.hash_password(password) if password else None,
            "email": email,
            "role_id": role_id,
            "avatar_blob": None,  # Không dùng blob
            "image_path": final_image_path  # Lưu đường dẫn vào cột hinhAnhUrl
        }

        # 4. Gọi Model
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