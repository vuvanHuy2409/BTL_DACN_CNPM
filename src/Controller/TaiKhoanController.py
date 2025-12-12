import mysql.connector
from src.config.db_config import DB_CONFIG


class TaiKhoanController:
    def __init__(self):
        pass

    def get_connection(self):
        """Hàm hỗ trợ kết nối database"""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            return conn
        except mysql.connector.Error as err:
            print(f"Lỗi kết nối: {err}")
            return None

    def get_list(self):
        """
        Lấy danh sách tất cả nhân viên và thông tin tài khoản (nếu có).
        """
        conn = self.get_connection()
        if not conn: return []

        cursor = conn.cursor(dictionary=True)
        try:
            # Query: Lấy tất cả nhân viên + thông tin tài khoản (LEFT JOIN)
            # Dùng LEFT JOIN vì nhân viên có thể CHƯA CÓ tài khoản
            query = """
                SELECT 
                    nv.idNhanVien,
                    nv.hoTen,
                    nv.email,
                    nv.phanQuyen, -- hoặc cv.tenChucVu nếu bạn dùng bảng chucVu
                    cv.tenChucVu,
                    tk.tenDangNhap,
                    tk.trangThai -- 1: Active, 0: Locked
                FROM nhanVien nv
                JOIN chucVu cv ON nv.idChucVu = cv.idChucVu
                LEFT JOIN taiKhoanNhanVien tk ON nv.idTaiKhoan = tk.idTaiKhoan
                WHERE nv.trangThaiLamViec = 'DangLamViec'
                ORDER BY nv.idNhanVien DESC
            """
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Exception as e:
            print(f"Lỗi get_list: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    # ==========================================================
    # [QUAN TRỌNG] HÀM TÌM KIẾM
    # ==========================================================
    def tim_kiem_tai_khoan(self, keyword):
        """
        Tìm kiếm nhân viên theo Họ tên, Email hoặc Tên đăng nhập.
        """
        conn = self.get_connection()
        if not conn: return []

        cursor = conn.cursor(dictionary=True)
        try:
            # Sử dụng %keyword% để tìm kiếm gần đúng (LIKE)
            search_pattern = f"%{keyword}%"

            query = """
                SELECT 
                    nv.idNhanVien,
                    nv.hoTen,
                    nv.email,
                    cv.tenChucVu,
                    tk.tenDangNhap,
                    tk.trangThai
                FROM nhanVien nv
                JOIN chucVu cv ON nv.idChucVu = cv.idChucVu
                LEFT JOIN taiKhoanNhanVien tk ON nv.idTaiKhoan = tk.idTaiKhoan
                WHERE nv.trangThaiLamViec = 'DangLamViec'
                AND (
                    nv.hoTen LIKE %s 
                    OR nv.email LIKE %s 
                    OR tk.tenDangNhap LIKE %s
                )
                ORDER BY nv.idNhanVien DESC
            """
            # Truyền 3 tham số giống nhau cho 3 chỗ %s
            cursor.execute(query, (search_pattern, search_pattern, search_pattern))
            result = cursor.fetchall()
            return result
        except Exception as e:
            print(f"Lỗi tìm kiếm: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    # ==========================================================
    # CÁC HÀM XỬ LÝ LƯU / XÓA (LOGIC CRUD)
    # ==========================================================

    def save_account(self, id_nhan_vien, has_account, name, username, password, email, role_text):
        """
        Lưu thông tin:
        1. Cập nhật role vào bảng nhanVien (hoặc chucVu)
        2. Tạo mới hoặc Cập nhật tài khoản vào bảng taiKhoanNhanVien
        """
        conn = self.get_connection()
        if not conn: return False, "Lỗi kết nối CSDL"

        cursor = conn.cursor()
        try:
            # 1. Logic chuẩn hóa tên chức vụ sang ID (Giả sử bạn có bảng chucVu)
            # Bạn cần map từ text "Quản Lý" -> idChucVu (Ví dụ logic đơn giản ở đây)
            # Trong thực tế, bạn nên query lấy idChucVu từ bảng chucVu dựa vào tên

            # --- XỬ LÝ TÀI KHOẢN ---
            if not username:
                return False, "Tên đăng nhập không được để trống!"

            import hashlib
            # Mã hóa pass nếu có nhập (Nếu ô pass trống nghĩa là không đổi pass)
            pass_hash = None
            if password:
                pass_hash = hashlib.md5(password.encode()).hexdigest()

            if has_account:
                # --- TRƯỜNG HỢP UPDATE ---
                # Chỉ update mật khẩu nếu người dùng có nhập
                if pass_hash:
                    sql_tk = """
                        UPDATE taiKhoanNhanVien 
                        SET tenDangNhap = %s, matKhauHash = %s 
                        WHERE idTaiKhoan = (SELECT idTaiKhoan FROM nhanVien WHERE idNhanVien = %s)
                    """
                    cursor.execute(sql_tk, (username, pass_hash, id_nhan_vien))
                else:
                    # Không đổi pass
                    sql_tk = """
                        UPDATE taiKhoanNhanVien 
                        SET tenDangNhap = %s 
                        WHERE idTaiKhoan = (SELECT idTaiKhoan FROM nhanVien WHERE idNhanVien = %s)
                    """
                    cursor.execute(sql_tk, (username, id_nhan_vien))

                msg = "Cập nhật thông tin tài khoản thành công!"

            else:
                # --- TRƯỜNG HỢP TẠO MỚI (INSERT) ---
                if not password:
                    return False, "Vui lòng nhập mật khẩu để tạo tài khoản mới!"

                # 1. Insert vào bảng taiKhoanNhanVien
                sql_insert_tk = "INSERT INTO taiKhoanNhanVien (tenDangNhap, matKhauHash, trangThai) VALUES (%s, %s, 1)"
                cursor.execute(sql_insert_tk, (username, pass_hash))
                new_id_tk = cursor.lastrowid  # Lấy ID vừa tạo

                # 2. Update idTaiKhoan ngược lại vào bảng nhanVien
                sql_update_nv = "UPDATE nhanVien SET idTaiKhoan = %s WHERE idNhanVien = %s"
                cursor.execute(sql_update_nv, (new_id_tk, id_nhan_vien))

                msg = "Cấp tài khoản mới thành công!"

            # --- (Tùy chọn) Cập nhật chức vụ nếu cần ---
            # ... code update chức vụ ...

            conn.commit()
            return True, msg

        except mysql.connector.Error as err:
            conn.rollback()
            return False, f"Lỗi SQL: {err}"
        finally:
            cursor.close()
            conn.close()

    def delete_account_only(self, id_nhan_vien):
        """
        Xóa tài khoản đăng nhập (Set idTaiKhoan = NULL trong nhanVien, rồi xóa row bên taiKhoan)
        """
        conn = self.get_connection()
        if not conn: return False, "Lỗi kết nối"

        cursor = conn.cursor()
        try:
            # 1. Lấy idTaiKhoan hiện tại
            cursor.execute("SELECT idTaiKhoan FROM nhanVien WHERE idNhanVien = %s", (id_nhan_vien,))
            row = cursor.fetchone()
            if not row or not row[0]:
                return False, "Nhân viên chưa có tài khoản."

            id_tk = row[0]

            # 2. Gỡ liên kết trong bảng nhanVien trước
            cursor.execute("UPDATE nhanVien SET idTaiKhoan = NULL WHERE idNhanVien = %s", (id_nhan_vien,))

            # 3. Xóa dòng trong bảng taiKhoanNhanVien
            cursor.execute("DELETE FROM taiKhoanNhanVien WHERE idTaiKhoan = %s", (id_tk,))

            conn.commit()
            return True, "Đã xóa tài khoản đăng nhập thành công!"

        except mysql.connector.Error as err:
            conn.rollback()
            return False, f"Lỗi: {err}"
        finally:
            cursor.close()
            conn.close()