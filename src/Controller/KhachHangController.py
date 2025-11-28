from src.Model.KhachHangModel import KhachHangModel
from datetime import datetime

class KhachHangController:
    def __init__(self):
        self.model = KhachHangModel()

    def lay_danh_sach_khach_hang(self):
        return self.model.get_all()

    def them_khach_hang(self, ten, sdt, ngaysinh):
        if not ten:
            return False, "Tên không được để trống"

        # Chuyển ngày
        ngay_sql = None
        if ngaysinh.strip():
            try:
                ngay_sql = datetime.strptime(ngaysinh, "%d/%m/%Y").strftime("%Y-%m-%d")
            except:
                return False, "Ngày sinh không hợp lệ (dd/mm/yyyy)"

        data = {
            "hoTen": ten,
            "soDienThoai": sdt if sdt.strip() else None,
            "ngaySinh": ngay_sql,
            "diemTichLuy": 0
        }

        if self.model.insert(data):
            return True, "Thêm thành công"
        else:
            return False, "Thêm thất bại"

    def sua_khach_hang(self, idKH, ten, sdt, ngaysinh, diem):
        if not ten:
            return False, "Tên không được để trống"

        ngay_sql = None
        if ngaysinh.strip():
            try:
                ngay_sql = datetime.strptime(ngaysinh, "%d/%m/%Y").strftime("%Y-%m-%d")
            except:
                return False, "Ngày sinh không hợp lệ"

        data = {
            "hoTen": ten,
            "soDienThoai": sdt if sdt.strip() else None,
            "ngaySinh": ngay_sql,
            "diemTichLuy": diem
        }

        if self.model.update(idKH, data):
            return True, "Cập nhật thành công"
        else:
            return False, "Cập nhật thất bại"

    def xoa_khach_hang(self, idKH):
        if self.model.delete(idKH):
            return True, "Xóa thành công"
        return False, "Xóa thất bại"

    def tim_kiem_khach_hang(self, keyword):
        return self.model.search(keyword)
