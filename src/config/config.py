import mysql.connector
from mysql.connector import Error
from db_config import DB_CONFIG

class DatabaseHelper:
    def __init__(self):
        self.connection = None

    def connect(self):
        """Mở kết nối đến database"""
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            if self.connection.is_connected():
                return self.connection
        except Error as e:
            print(f"Lỗi kết nối MySQL: {e}")
            return None
    def disconnect(self):
        """Đóng kết nối"""
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def fetch_all(self, query, params=None):
        """
        Dùng cho lệnh SELECT. Trả về toàn bộ danh sách kết quả.
        Ví dụ: Lấy danh sách nhân viên, lấy thống kê doanh thu.
        """
        result = []
        try:
            self.connect()
            if self.connection:
                cursor = self.connection.cursor(dictionary=True) # dictionary=True để trả về dạng {'ten': 'A', 'tuoi': 20}
                cursor.execute(query, params or ())
                result = cursor.fetchall()
                cursor.close()
        except Error as e:
            print(f"Lỗi thực thi query: {e}")
        finally:
            self.disconnect()
        return result

    def execute_query(self, query, params=None):
        """
        Dùng cho lệnh INSERT, UPDATE, DELETE.
        Trả về True nếu thành công, False nếu thất bại.
        """
        success = False
        try:
            self.connect()
            if self.connection:
                cursor = self.connection.cursor()
                cursor.execute(query, params or ())
                self.connection.commit() # Quan trọng: Phải commit thì dữ liệu mới lưu vào DB
                cursor.close()
                success = True
        except Error as e:
            print(f"Lỗi thực thi action: {e}")
            if self.connection:
                self.connection.rollback() # Hoàn tác nếu lỗi
        finally:
            self.disconnect()
        return success