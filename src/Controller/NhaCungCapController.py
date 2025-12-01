from src.Model.NhaCungCapModel import NhaCungCapModel
import pandas as pd

class NhaCungCapController:
    def __init__(self):
        self.model = NhaCungCapModel()

    def lay_danh_sach(self):
        return self.model.get_all_with_ingredients()

    def tim_kiem(self, keyword):
        if not keyword or keyword.strip() == "":
            return self.model.get_all_with_ingredients()
        return self.model.search(keyword)

    def them_ncc(self, ten, sdt, dia_chi):
        if not ten or not sdt:
            return False, "Tên và SĐT là bắt buộc!"

        # Có thể thêm validate format SĐT ở đây

        if self.model.insert(ten.strip(), sdt.strip(), dia_chi.strip()):
            return True, "Thêm thành công"
        return False, "Lỗi khi thêm"

    def sua_ncc(self, idNCC, ten, sdt, dia_chi):
        if not idNCC:
            return False, "Chưa chọn nhà cung cấp"
        if not ten or not sdt:
            return False, "Thông tin thiếu"

        if self.model.update(idNCC, ten.strip(), sdt.strip(), dia_chi.strip()):
            return True, "Cập nhật thành công"
        return False, "Lỗi cập nhật"

    def doi_trang_thai(self, idNCC):
        if not idNCC:
            return False, "Chưa chọn nhà cung cấp"
        if self.model.toggle_status(idNCC):
            return True, "Đã đổi trạng thái"
        return False, "Lỗi hệ thống"

    def xuat_excel(self, file_path, data_list):
        """
        Xuất danh sách data_list ra file Excel tại đường dẫn file_path
        """
        if not data_list:
            return False, "Không có dữ liệu để xuất!"

        try:
            # 1. Chuẩn bị dữ liệu để xuất (Làm sạch data)
            export_data = []
            for item in data_list:
                export_data.append({
                    "STT": data_list.index(item) + 1,
                    "Tên Nhà Cung Cấp": item['tenNhaCungCap'],
                    "Số điện thoại": item['soDienThoai'],
                    "Địa chỉ": item['diaChi'],
                    "Nguyên liệu cung cấp": item['danhSachNguyenLieu'] if item['danhSachNguyenLieu'] else "Chưa có",
                    "Ngày cập nhật": item['ngayCapNhat'],  # Pandas sẽ tự format ngày
                    "Trạng thái": "Đang hoạt động" if item['isActive'] else "Đã ẩn"
                })

            # 2. Tạo DataFrame từ list dictionary
            df = pd.DataFrame(export_data)

            # 3. Xuất ra file Excel
            # index=False để không in cột số thứ tự mặc định của Pandas
            df.to_excel(file_path, index=False, engine='openpyxl')

            return True, "Xuất file Excel thành công!"

        except Exception as e:
            return False, f"Lỗi khi xuất file: {str(e)}"