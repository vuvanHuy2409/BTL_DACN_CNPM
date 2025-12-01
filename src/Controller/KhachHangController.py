from src.Model.KhachHangModel import KhachHangModel
from datetime import datetime


class KhachHangController:
    def __init__(self):
        self.model = KhachHangModel()

    def format_date_sql(self, date_str):
        """Chuyển đổi dd/mm/yyyy -> yyyy-mm-dd để lưu SQL"""
        try:
            return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            return None

    def lay_danh_sach_khach_hang(self):
        return self.model.get_all()

    def tim_kiem_khach_hang(self, keyword):
        return self.model.search(keyword)

    def them_khach_hang(self, ten, sdt, ngaysinh_str):
        # 1. Validate
        if not ten:
            return False, "Tên khách hàng không được để trống!"

        # 2. Convert ngày
        ngaysinh_sql = self.format_date_sql(ngaysinh_str)
        if not ngaysinh_sql:
            return False, "Ngày sinh không hợp lệ!"

        # 3. Check trùng SĐT (nếu có nhập SĐT)
        if sdt and self.model.check_exist(sdt):
            return False, "Số điện thoại này đã tồn tại!"

        data = {
            "hoTen": ten.strip(),
            "soDienThoai": sdt.strip() if sdt else None,
            "ngaySinh": ngaysinh_sql,
            "diemTichLuy": 0
        }

        if self.model.insert(data):
            return True, "Thêm khách hàng thành công!"
        return False, "Lỗi khi thêm khách hàng!"

    def sua_khach_hang(self, idKH, ten, sdt, ngaysinh_str, diem):
        if not idKH:
            return False, "Chưa chọn khách hàng!"

        if not ten:
            return False, "Tên không được để trống!"

        ngaysinh_sql = self.format_date_sql(ngaysinh_str)
        if not ngaysinh_sql:
            return False, "Ngày sinh không hợp lệ!"

        data = {
            "hoTen": ten.strip(),
            "soDienThoai": sdt.strip() if sdt else None,
            "ngaySinh": ngaysinh_sql,
            "diemTichLuy": diem
        }

        if self.model.update(idKH, data):
            return True, "Cập nhật thành công!"
        return False, "Lỗi cập nhật!"