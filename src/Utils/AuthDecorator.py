# File: src/Utils/AuthDecorator.py
from tkinter import messagebox
from src.Utils.Session import Session
import functools


def require_admin(func):
    """
    Decorator để yêu cầu quyền Admin (QuanLy) mới được chạy hàm.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 1. Lấy thông tin user hiện tại từ Session
        user = Session.get_user()

        # 2. Kiểm tra user có tồn tại và chức vụ có phải là quản lý không
        # Lưu ý: 'tenChucVu' phải khớp với tên cột trong database bạn select
        if user and user.get('tenChucVu') in ['QuanLy', 'Admin', 'Manager']:
            # ĐÚNG LÀ ADMIN -> Cho phép chạy hàm gốc
            return func(*args, **kwargs)
        else:
            # KHÔNG PHẢI ADMIN -> Hiển thị thông báo và chặn lại
            messagebox.showwarning(
                title="Truy cập bị từ chối",
                message="Chức năng này chỉ dành cho Quản lý (Admin)!"
            )
            return None  # Kết thúc, không chạy hàm gốc

    return wrapper