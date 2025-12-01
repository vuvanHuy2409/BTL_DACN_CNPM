from src.Model.NhanVienModel2 import NhanVienModel2
from datetime import datetime
import re


class NhanVienController:
    def __init__(self):
        self.model = NhanVienModel2()

    def is_valid_email(self, email):
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return re.match(pattern, email) is not None

    def format_datetime(self, dt_obj):
        """Format datetime từ DB ra string"""
        if not dt_obj: return ""
        if isinstance(dt_obj, str): return dt_obj
        return dt_obj.strftime("%d/%m/%Y %H:%M")

    def get_list(self):
        data = self.model.get_all()
        for row in data:
            row['ngayTao'] = self.format_datetime(row['ngayTao'])
            row['ngayCapNhat'] = self.format_datetime(row['ngayCapNhat'])
        return data

    def search_nhan_vien(self, keyword):
        data = self.model.search(keyword)
        for row in data:
            row['ngayTao'] = self.format_datetime(row['ngayTao'])
            row['ngayCapNhat'] = self.format_datetime(row['ngayCapNhat'])
        return data

    # --- NHÂN VIÊN ---
    def add_nhan_vien(self, ten, email, sdt, phan_quyen, id_chuc_vu):
        if not ten or not email or not sdt:
            return False, "Thiếu thông tin bắt buộc!"

        if not self.is_valid_email(email):
            return False, "Email không hợp lệ!"

        if not id_chuc_vu:
            return False, "Vui lòng chọn chức vụ!"

        if self.model.check_exist(email, sdt):
            return False, "Email hoặc SĐT đã tồn tại!"

        data = {
            "hoTen": ten, "email": email, "soDienThoai": sdt,
            "phanQuyen": phan_quyen, "idChucVu": id_chuc_vu
        }

        if self.model.insert(data):
            return True, "Thêm thành công!"
        return False, "Thêm thất bại!"

    def update_nhan_vien(self, idNV, ten, email, sdt, phan_quyen, id_chuc_vu):
        if not idNV: return False, "Chưa chọn nhân viên!"

        data = {
            "hoTen": ten, "email": email, "soDienThoai": sdt,
            "phanQuyen": phan_quyen, "idChucVu": id_chuc_vu
        }
        if self.model.update(idNV, data):
            return True, "Cập nhật thành công!"
        return False, "Cập nhật thất bại!"

    def doi_trang_thai(self, idNV):
        if not idNV: return False, "Chưa chọn nhân viên!"
        if self.model.toggle_status(idNV):
            return True, "Đã đổi trạng thái!"
        return False, "Lỗi đổi trạng thái!"

    # --- CHỨC VỤ ---
    def get_ds_chuc_vu(self):
        return self.model.get_all_chucvu()

    def them_chuc_vu(self, ten, luong):
        if not ten or not luong: return False, "Thiếu thông tin!"
        try:
            luong = float(luong)
        except:
            return False, "Lương phải là số!"

        if self.model.add_chucvu(ten, luong): return True, "Thêm chức vụ thành công!"
        return False, "Lỗi thêm chức vụ!"

    def sua_chuc_vu(self, idCV, ten, luong):
        if not idCV: return False, "Chưa chọn chức vụ!"
        try:
            luong = float(luong)
        except:
            return False, "Lương phải là số!"

        if self.model.update_chucvu(idCV, ten, luong): return True, "Cập nhật thành công!"
        return False, "Lỗi cập nhật!"