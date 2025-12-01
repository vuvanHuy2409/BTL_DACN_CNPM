from src.Model.KhoModel import KhoModel


class KhoController:
    def __init__(self):
        self.model = KhoModel()

    def get_list(self):
        return self.model.get_all()

    def search_nguyen_lieu(self, keyword):
        return self.model.search(keyword)

    def get_ncc_list(self):
        return self.model.get_ncc_options()

    def add_nguyen_lieu(self, ten, gia, sl, dvt, id_ncc, id_nv=1):
        if not ten or not gia or not dvt:
            return False, "Thiếu thông tin bắt buộc!"

        if self.model.check_exist(ten):
            return False, "Tên nguyên liệu đã tồn tại!"

        try:
            gia = float(gia)
            sl = float(sl)
        except:
            return False, "Giá và Số lượng phải là số!"

        data = {
            "ten": ten, "gia": gia, "sl": sl,
            "dvt": dvt, "idNCC": id_ncc, "idNV": id_nv
        }

        if self.model.insert(data):
            return True, "Thêm thành công!"
        return False, "Lỗi thêm mới!"

    def update_nguyen_lieu(self, idNL, ten, gia, sl, dvt, id_ncc):
        if not idNL: return False, "Chưa chọn nguyên liệu!"

        try:
            gia = float(gia)
            sl = float(sl)
        except:
            return False, "Dữ liệu số không hợp lệ!"

        data = {
            "ten": ten, "gia": gia, "sl": sl,
            "dvt": dvt, "idNCC": id_ncc
        }

        if self.model.update(idNL, data):
            msg = "Cập nhật thành công!"
            if sl <= 0:
                msg += "\n(Nguyên liệu đã tự động ẨN do hết hàng)"
            return True, msg
        return False, "Lỗi cập nhật!"

    def doi_trang_thai(self, idNL):
        if not idNL: return False, "Chưa chọn dòng!"
        if self.model.toggle_status(idNL):
            return True, "Đổi trạng thái thành công!"
        return False, "Lỗi hệ thống!"