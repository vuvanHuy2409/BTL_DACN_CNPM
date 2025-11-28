from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, TIMESTAMP, DECIMAL
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.sql import func
import datetime

# --- CẤU HÌNH DATABASE ---
# Thay 'root', 'password' bằng thông tin thật của bạn
# LƯU Ý: Nếu pass có ký tự đặc biệt (@, :, /), hãy để trống hoặc encode URL
DB_URL = "mysql+mysqlconnector://root:@localhost/coffeeShop"

Base = declarative_base()

# --- 1. THÊM CLASS CHỨC VỤ (QUAN TRỌNG) ---
class ChucVu(Base):
    __tablename__ = 'chucVu'
    
    idChucVu = Column(Integer, primary_key=True, autoincrement=True)
    tenChucVu = Column(String(100), unique=True, nullable=False)
    luongCoBan = Column(DECIMAL(10,2), default=0)

# --- 2. CLASS TÀI KHOẢN ---
class TaiKhoanNhanVien(Base):
    __tablename__ = 'taiKhoanNhanVien'

    idTaiKhoan = Column(Integer, primary_key=True, autoincrement=True)
    tenDangNhap = Column(String(50), unique=True, nullable=False)
    matKhauHash = Column(String(255), nullable=False)

# --- 3. CLASS NHÂN VIÊN ---
class NhanVien(Base):
    __tablename__ = 'nhanVien'

    idNhanVien = Column(Integer, primary_key=True, autoincrement=True)
    hoTen = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    
    soDienThoai = Column(String(15), unique=True, nullable=True)
    ngayBatDau = Column(Date, default=datetime.date.today)
    trangThaiLamViec = Column(String(20), default='DangLamViec')
    phanQuyen = Column(String(20), default='nhanVien')
    
    # Khóa ngoại
    idChucVu = Column(Integer, ForeignKey('chucVu.idChucVu'), nullable=False)
    idTaiKhoan = Column(Integer, ForeignKey('taiKhoanNhanVien.idTaiKhoan'), unique=True)

    # Relationship
    tai_khoan = relationship("TaiKhoanNhanVien", backref="nhan_vien")
    chuc_vu = relationship("ChucVu", backref="ds_nhan_vien")

def init_db():
    # Thêm pool_recycle để tránh lỗi mất kết nối sau thời gian dài
    engine = create_engine(DB_URL, echo=True, pool_recycle=3600)
    return engine