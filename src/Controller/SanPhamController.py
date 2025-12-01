import pandas as pd
import shutil
import os
import time
from src.Model.SanPhamModel import SanPhamModel


class SanPhamController:
    def __init__(self):
        self.model = SanPhamModel()

        # Đường dẫn thư mục lưu ảnh
        self.IMAGE_DIR = "src/images"

        # Tự động tạo thư mục nếu chưa có
        if not os.path.exists(self.IMAGE_DIR):
            os.makedirs(self.IMAGE_DIR)

    # --- LẤY DATA ---
    def lay_danh_sach(self):
        return self.model.get_all()

    def lay_ds_danh_muc(self):
        return self.model.get_categories()

    def lay_ds_nguyen_lieu(self):
        return self.model.get_ingredients()

    def tim_kiem(self, keyword):
        return self.model.search(keyword)

    # --- LOGIC XỬ LÝ ẢNH ---
    def xu_ly_luu_anh(self, source_path):
        """
        Copy ảnh từ nguồn vào thư mục dự án và trả về đường dẫn tương đối.
        """
        if not source_path:
            return ""

        # Chuẩn hóa đường dẫn để so sánh
        norm_source = os.path.normpath(source_path)
        norm_dest_dir = os.path.normpath(os.path.abspath(self.IMAGE_DIR))

        # Nếu ảnh đã nằm trong thư mục src/images rồi thì không cần copy lại
        # (Trường hợp bấm Sửa nhưng không đổi ảnh)
        if norm_dest_dir in os.path.abspath(norm_source):
            return source_path.replace("\\", "/")

        try:
            # 1. Lấy tên file và đuôi file
            filename = os.path.basename(source_path)
            name, ext = os.path.splitext(filename)

            # 2. Tạo tên file mới kèm timestamp để tránh trùng (vd: cafe_171999.jpg)
            timestamp = int(time.time())
            new_filename = f"{name}_{timestamp}{ext}"

            # 3. Tạo đường dẫn đích
            dest_path = os.path.join(self.IMAGE_DIR, new_filename)

            # 4. Copy file
            shutil.copy2(source_path, dest_path)

            # 5. Trả về đường dẫn tương đối (dùng / để chuẩn cho mọi OS)
            return dest_path.replace("\\", "/")

        except Exception as e:
            print(f"Lỗi lưu ảnh: {e}")
            return ""

    # --- THÊM / SỬA / XÓA ---
    def them_san_pham(self, ten, gia, hinh_anh_path, id_dm, id_nl):
        if not ten: return False, "Tên sản phẩm không được trống"
        try:
            g = float(gia)
            if g < 0: return False, "Giá bán không hợp lệ"
        except:
            return False, "Giá bán phải là số"

        # Lưu ảnh và lấy đường dẫn mới
        final_path = self.xu_ly_luu_anh(hinh_anh_path)

        if self.model.insert(ten, g, final_path, id_dm, id_nl):
            return True, "Thêm thành công"
        return False, "Lỗi thêm mới (Database)"

    def sua_san_pham(self, id_sp, ten, gia, hinh_anh_path, id_dm, id_nl):
        if not id_sp: return False, "Chưa chọn sản phẩm"
        try:
            g = float(gia)
        except:
            return False, "Giá bán lỗi"

        # Lưu ảnh (nếu có thay đổi)
        final_path = self.xu_ly_luu_anh(hinh_anh_path)

        if self.model.update(id_sp, ten, g, final_path, id_dm, id_nl):
            return True, "Cập nhật thành công"
        return False, "Lỗi cập nhật (Database)"

    def doi_trang_thai(self, id_sp):
        if not id_sp: return False, "Chưa chọn sản phẩm"
        if self.model.toggle_status(id_sp):
            return True, "Đổi trạng thái thành công"
        return False, "Lỗi hệ thống"

    def xuat_excel(self, path, data):
        if not data: return False, "Danh sách trống"
        try:
            export = []
            for i, row in enumerate(data):
                export.append({
                    "STT": i + 1,
                    "Tên Sản Phẩm": row['tenSanPham'],
                    "Giá Bán": row['giaBan'],
                    "Danh Mục": row['tenDanhMuc'],
                    "Nguyên Liệu": row['tenNguyenLieu'],
                    "Đường Dẫn Ảnh": row['hinhAnhUrl'],
                    "Trạng Thái": "Đang bán" if row['isActive'] else "Ngừng bán"
                })
            df = pd.DataFrame(export)
            df.to_excel(path, index=False, engine='openpyxl')
            return True, "Xuất Excel thành công"
        except Exception as e:
            return False, str(e)