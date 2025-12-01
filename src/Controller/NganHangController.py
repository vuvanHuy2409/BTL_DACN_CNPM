from src.Model.NganHangModel import NganHangModel


class NganHangController:
    def __init__(self):
        self.model = NganHangModel()

    def lay_danh_sach_ngan_hang(self):
        return self.model.get_all()

    def tim_kiem_ngan_hang(self, keyword):
        if not keyword or keyword.strip() == "":
            return self.model.get_all()
        return self.model.search(keyword)

    def them_ngan_hang(self, ma, ten, stk, chu):
        # 1. Validate dữ liệu trống
        if not ma or not ten or not stk or not chu:
            return False, "Vui lòng điền đầy đủ thông tin!"

        # 2. KIỂM TRA TRÙNG LẶP (LOGIC MỚI)
        # Nếu Mã Ngân hàng VÀ Số tài khoản này đã có trong DB thì báo lỗi
        if self.model.check_exist(ma, stk):
            return False, f"Ngân hàng {ma} với số tài khoản {stk} đã tồn tại!"

        # 3. Chuẩn bị dữ liệu
        data = {
            "maNganHang": ma.strip().upper(),
            "tenNganHang": ten.strip(),
            "soTaiKhoan": stk.strip(),
            "tenTaiKhoan": chu.strip().upper(),
            "isActive": 1
        }

        # 4. Gọi Model thêm mới
        if self.model.insert(data):
            return True, "Thêm ngân hàng thành công"
        else:
            return False, "Thêm thất bại (Lỗi hệ thống)"

    def sua_ngan_hang(self, idNH, ma, ten, stk, chu):
        if not idNH:
            return False, "Chưa chọn ngân hàng để sửa"
        if not ma or not ten or not stk or not chu:
            return False, "Thông tin không được để trống"

        # (Tùy chọn: Bạn có thể thêm check trùng lặp ở đây nếu muốn cấm sửa thành số TK đã có)

        data = {
            "maNganHang": ma.strip().upper(),
            "tenNganHang": ten.strip(),
            "soTaiKhoan": stk.strip(),
            "tenTaiKhoan": chu.strip().upper()
        }

        if self.model.update(idNH, data):
            return True, "Cập nhật thành công"
        else:
            return False, "Cập nhật thất bại"

    def doi_trang_thai(self, idNH):
        if not idNH:
            return False, "Chưa chọn ngân hàng"

        if self.model.toggle_status(idNH):
            return True, "Đổi trạng thái thành công"
        return False, "Lỗi khi đổi trạng thái"