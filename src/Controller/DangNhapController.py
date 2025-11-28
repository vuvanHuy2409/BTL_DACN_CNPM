
import hashlib
from src.Model.NhanVienModel import NhanVienModel

class DangNhapController:
    def __init__(self):
        self.model = NhanVienModel()

    def xu_ly_dang_nhap(self, username, password):
        # 1. Lấy user từ DB
        user = self.model.tim_tai_khoan(username)

        # 2. Kiểm tra tồn tại
        if not user:
            return {"status": False, "message": "Tài khoản không tồn tại!"}

        # 3. Kiểm tra trạng thái làm việc
        if user['trangThaiLamViec'] != 'DangLamViec':
            return {"status": False, "message": "Tài khoản đã bị khóa hoặc nghỉ việc!"}

        # 4. Kiểm tra mật khẩu (Hash MD5 để khớp với Database mẫu)
        input_hash = hashlib.md5(password.encode()).hexdigest()
        
        if input_hash == user['matKhauHash']:
            return {"status": True, "message": "Thành công", "data": user}
        else:
            return {"status": False, "message": "Sai mật khẩu!"}