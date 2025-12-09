import mysql.connector
import hashlib
from src.config.db_config import DB_CONFIG

class DangNhapController:
    def __init__(self):
        pass

    def hash_password(self, password):
        return hashlib.md5(password.encode()).hexdigest()

    def xu_ly_dang_nhap(self, username, password):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)

            pass_hash = self.hash_password(password)

            # [THAY ĐỔI QUAN TRỌNG]
            # Lấy trực tiếp cột 'phanQuyen' từ bảng 'nhanVien'
            # Không cần JOIN bảng chucVu để lấy quyền nữa
            query = """
                SELECT 
                    nv.idNhanVien, 
                    nv.hoTen, 
                    nv.phanQuyen  
                FROM taiKhoanNhanVien tk
                JOIN nhanVien nv ON tk.idTaiKhoan = nv.idTaiKhoan
                WHERE tk.tenDangNhap = %s 
                  AND tk.matKhauHash = %s 
                  AND nv.trangThaiLamViec = 'DangLamViec'
            """

            cursor.execute(query, (username, pass_hash))
            result = cursor.fetchone()

            cursor.close()
            conn.close()

            if result:
                # Trả về kết quả
                return {
                    "status": True,
                    "message": "Đăng nhập thành công",
                    "data": {
                        "id_nhan_vien": result['idNhanVien'],
                        "ho_ten": result['hoTen'],
                        # Lấy giá trị từ cột phanQuyen ('admin' hoặc 'nhanVien')
                        "role_name": result['phanQuyen']
                    }
                }
            else:
                return {
                    "status": False,
                    "message": "Sai tên đăng nhập hoặc mật khẩu!"
                }

        except mysql.connector.Error as err:
            return {
                "status": False,
                "message": f"Lỗi kết nối CSDL: {err}"
            }