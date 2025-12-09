# File: src/Utils/Session.py

class Session:
    # Biến static để lưu thông tin user hiện tại
    current_user = None

    @staticmethod
    def set_user(user_data):
        """Lưu thông tin user sau khi login"""
        Session.current_user = user_data

    @staticmethod
    def get_user():
        """Lấy thông tin user hiện tại"""
        return Session.current_user

    @staticmethod
    def clear():
        """Đăng xuất"""
        Session.current_user = None