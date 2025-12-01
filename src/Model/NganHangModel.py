import mysql.connector
from src.config.db_config import DB_CONFIG

class NganHangModel:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self):
        """Thiết lập kết nối đến cơ sở dữ liệu"""
        try:
            self.conn = mysql.connector.connect(**DB_CONFIG)
            # dictionary=True giúp kết quả trả về dạng {'tenCot': 'giaTri'} thay vì tuple
            self.cursor = self.conn.cursor(dictionary=True)
        except mysql.connector.Error as err:
            print(f"Lỗi kết nối DB: {err}")

    def close(self):
        """Đóng kết nối và giải phóng tài nguyên"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    # =============================
    # 1. LẤY DANH SÁCH
    # =============================
    def get_all(self):
        """Lấy tất cả ngân hàng, ưu tiên hiển thị đang hoạt động lên trước"""
        self.connect()
        # Sắp xếp: isActive giảm dần (1 -> 0), sau đó đến ID giảm dần (mới nhất lên trên)
        query = "SELECT * FROM nganHang ORDER BY isActive DESC, idNganHang DESC"
        try:
            if self.cursor:
                self.cursor.execute(query)
                return self.cursor.fetchall()
            return []
        except Exception as e:
            print(f"Lỗi get_all: {e}")
            return []
        finally:
            self.close()

    # =============================
    # 2. KIỂM TRA TỒN TẠI (Check trùng)
    # =============================
    def check_exist(self, ma, stk):
        """
        Kiểm tra xem cặp (Mã Ngân Hàng + Số Tài Khoản) đã tồn tại chưa.
        Trả về True nếu đã có, False nếu chưa có.
        """
        self.connect()
        query = "SELECT idNganHang FROM nganHang WHERE maNganHang = %s AND soTaiKhoan = %s"
        try:
            if self.cursor:
                self.cursor.execute(query, (ma, stk))
                result = self.cursor.fetchone()
                return result is not None
            return False
        except Exception as e:
            print(f"Lỗi check_exist: {e}")
            return False
        finally:
            self.close()

    # =============================
    # 3. THÊM MỚI
    # =============================
    def insert(self, data):
        """Thêm một ngân hàng mới vào CSDL"""
        self.connect()
        query = """
            INSERT INTO nganHang(maNganHang, tenNganHang, soTaiKhoan, tenTaiKhoan, isActive)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            if self.cursor:
                self.cursor.execute(query, (
                    data["maNganHang"],
                    data["tenNganHang"],
                    data["soTaiKhoan"],
                    data["tenTaiKhoan"],
                    data.get("isActive", 1)  # Mặc định là 1 (Hiện)
                ))
                self.conn.commit()
                return True
            return False
        except Exception as e:
            print(f"Lỗi insert: {e}")
            return False
        finally:
            self.close()

    # =============================
    # 4. CẬP NHẬT (SỬA)
    # =============================
    def update(self, idNH, data):
        """Cập nhật thông tin ngân hàng dựa trên ID"""
        self.connect()
        query = """
            UPDATE nganHang
            SET maNganHang=%s, tenNganHang=%s, soTaiKhoan=%s, tenTaiKhoan=%s
            WHERE idNganHang=%s
        """
        try:
            if self.cursor:
                self.cursor.execute(query, (
                    data["maNganHang"],
                    data["tenNganHang"],
                    data["soTaiKhoan"],
                    data["tenTaiKhoan"],
                    idNH
                ))
                self.conn.commit()
                return True
            return False
        except Exception as e:
            print(f"Lỗi update: {e}")
            return False
        finally:
            self.close()

    # =============================
    # 5. ẨN / HIỆN (Toggle Status)
    # =============================
    def toggle_status(self, idNH):
        """Đảo ngược trạng thái isActive (1 -> 0 hoặc 0 -> 1)"""
        self.connect()
        query = "UPDATE nganHang SET isActive = NOT isActive WHERE idNganHang=%s"
        try:
            if self.cursor:
                self.cursor.execute(query, (idNH,))
                self.conn.commit()
                return True
            return False
        except Exception as e:
            print(f"Lỗi toggle_status: {e}")
            return False
        finally:
            self.close()

    # =============================
    # 6. TÌM KIẾM
    # =============================
    def search(self, keyword):
        """Tìm kiếm theo Mã NH, Tên NH hoặc Số TK"""
        self.connect()
        query = """
            SELECT * FROM nganHang
            WHERE maNganHang LIKE %s 
            OR tenNganHang LIKE %s 
            OR soTaiKhoan LIKE %s
            ORDER BY isActive DESC
        """
        try:
            if self.cursor:
                kw = f"%{keyword}%"
                # Truyền tham số kw cho cả 3 dấu %s
                self.cursor.execute(query, (kw, kw, kw))
                return self.cursor.fetchall()
            return []
        except Exception as e:
            print(f"Lỗi search: {e}")
            return []
        finally:
            self.close()