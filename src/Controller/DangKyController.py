from tkinter import messagebox
from sqlalchemy.orm import Session
import hashlib
from src.Model.DangKyModel import init_db, TaiKhoanNhanVien, NhanVien

class DangKyController:
    def __init__(self, view):
        self.view = view
        self.engine = init_db()

    def ma_hoa_mat_khau(self, password):
        # Mã hóa MD5 đơn giản (như trong SQL mẫu của bạn)
        return hashlib.md5(password.encode()).hexdigest()

    def xu_ly_dang_ky(self):
        # 1. Lấy dữ liệu từ View
        user = self.view.entry_user.get().strip()
        email = self.view.entry_email.get().strip()
        pw = self.view.entry_pw.get().strip()
        confirm = self.view.entry_confirm.get().strip()

        # 2. Validation
        if not user or not email or not pw:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin!")
            return

        if pw != confirm:
            messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp!")
            return

        # 3. Thao tác với Database
        session = Session(self.engine)
        try:
            # Kiểm tra User tồn tại
            existing_user = session.query(TaiKhoanNhanVien).filter_by(tenDangNhap=user).first()
            if existing_user:
                messagebox.showerror("Lỗi", "Tên đăng nhập đã tồn tại!")
                return
            
            # Kiểm tra Email tồn tại
            existing_email = session.query(NhanVien).filter_by(email=email).first()
            if existing_email:
                messagebox.showerror("Lỗi", "Email này đã được sử dụng!")
                return

            # --- BƯỚC 1: TẠO TÀI KHOẢN TRƯỚC ---
            new_acc = TaiKhoanNhanVien(
                tenDangNhap=user,
                matKhauHash=self.ma_hoa_mat_khau(pw)
            )
            session.add(new_acc)
            session.flush() # Đẩy lên DB để lấy idTaiKhoan về ngay lập tức (chưa commit)

            # --- BƯỚC 2: TẠO HỒ SƠ NHÂN VIÊN ---
            # Lưu ý: Database yêu cầu idChucVu NOT NULL.
            # Ta mặc định nhân viên mới đăng ký là 'PhucVu' (id=3 trong SQL mẫu của bạn)
            new_nv = NhanVien(
                hoTen=user, # Tạm lấy tên đăng nhập làm tên hiển thị
                email=email,
                idChucVu=3, # ID 3 = Phục vụ (Cần đảm bảo trong bảng chucVu đã có ID 3)
                idTaiKhoan=new_acc.idTaiKhoan # Lấy ID từ bước 1
            )
            session.add(new_nv)
            
            # Lưu tất cả
            session.commit()

            messagebox.showinfo("Thành công", "Đăng ký thành công! Vui lòng đăng nhập.")
            self.view.on_back_command()

        except Exception as e:
            session.rollback() # Hoàn tác nếu lỗi
            messagebox.showerror("Lỗi Database", f"Chi tiết: {str(e)}")
            print(e)
        finally:
            session.close()