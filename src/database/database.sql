-- =============================================
    -- 1. THIẾT LẬP MÔI TRƯỜNG & LÀM SẠCH
    -- =============================================
DROP
    DATABASE IF EXISTS coffeeShop;
CREATE DATABASE coffeeShop CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; USE
    coffeeShop;
SET NAMES
    'utf8mb4';
SET
    FOREIGN_KEY_CHECKS = 0; -- Tắt kiểm tra khóa ngoại để nạp dữ liệu nhanh
    -- =============================================
    -- 2. TẠO CẤU TRÚC BẢNG (ĐÃ CẬP NHẬT)
    -- =============================================
    -- Bảng Tài khoản (Đã bỏ vector và url ảnh)
CREATE TABLE taiKhoanNhanVien(
    idTaiKhoan INT PRIMARY KEY AUTO_INCREMENT,
    tenDangNhap VARCHAR(50) NOT NULL UNIQUE,
    matKhauHash VARCHAR(255) NOT NULL
); CREATE TABLE chucVu(
    idChucVu INT PRIMARY KEY AUTO_INCREMENT,
    tenChucVu VARCHAR(100) NOT NULL UNIQUE,
    luongCoBan DECIMAL(10, 2) DEFAULT 0
); CREATE TABLE nhanVien(
    idNhanVien INT PRIMARY KEY AUTO_INCREMENT,
    hoTen VARCHAR(100) NOT NULL,
    soDienThoai VARCHAR(15) UNIQUE,
    email VARCHAR(100) UNIQUE,
    ngayTao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ngayCapNhat TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    trangThaiLamViec ENUM('DangLamViec', 'DaNghiViec') DEFAULT 'DangLamViec',
    phanQuyen ENUM('nhanVien', 'admin') DEFAULT 'nhanVien',
    idChucVu INT NOT NULL,
    idTaiKhoan INT UNIQUE,
    FOREIGN KEY(idChucVu) REFERENCES chucVu(idChucVu),
    FOREIGN KEY(idTaiKhoan) REFERENCES taiKhoanNhanVien(idTaiKhoan) ON DELETE SET NULL
);
-- Bảng Chấm công
CREATE TABLE bangChamCong(
    idChamCong BIGINT PRIMARY KEY AUTO_INCREMENT,
    idNhanVien INT NOT NULL,
    gioVao DATETIME NOT NULL,
    gioRa DATETIME NULL,
    soGioCong DECIMAL(5, 2) DEFAULT 0,
    tongGioLam DECIMAL(5, 2) DEFAULT 0,
    FOREIGN KEY(idNhanVien) REFERENCES nhanVien(idNhanVien) ON DELETE CASCADE
);
-- Bảng Lương
CREATE TABLE luong(
    idNhanVien INT NOT NULL,
    idChamCong BIGINT NOT NULL,
    luongNV DECIMAL(12, 2) NOT NULL,
    soGioCong DECIMAL(5, 2) NOT NULL,
    tongLuong DECIMAL(12, 2) NOT NULL,
    ttThanhToan ENUM('ChuaThanhToan', 'DaThanhToan') DEFAULT 'ChuaThanhToan',
    PRIMARY KEY(idNhanVien, idChamCong),
    FOREIGN KEY(idNhanVien) REFERENCES nhanVien(idNhanVien),
    FOREIGN KEY(idChamCong) REFERENCES bangChamCong(idChamCong) ON DELETE CASCADE
);
-- (Các bảng phụ trợ khác giữ nguyên để đảm bảo hệ thống chạy đủ)
CREATE TABLE nganHang(
    idNganHang INT PRIMARY KEY AUTO_INCREMENT,
    maNganHang VARCHAR(20),
    tenNganHang VARCHAR(100),
    soTaiKhoan VARCHAR(50),
    tenTaiKhoan VARCHAR(100),
    isActive BOOLEAN DEFAULT TRUE

); CREATE TABLE nhaCungCap(
    idNhaCungCap INT PRIMARY KEY AUTO_INCREMENT,
    tenNhaCungCap VARCHAR(255),
    soDienThoai VARCHAR(15),
    diaChi TEXT,
    ngayCapNhat DATE,
    isActive BOOLEAN DEFAULT TRUE

); CREATE TABLE khoNguyenLieu(
    idNguyenLieu INT PRIMARY KEY AUTO_INCREMENT,
    tenNguyenLieu VARCHAR(255),
    giaNhap DECIMAL(10, 2),
    soLuongTon DECIMAL(10, 2),
    donViTinh VARCHAR(50),
    ngayNhap DATE,
    isActive BOOLEAN DEFAULT TRUE,
    idNhaCungCap INT,
    idNhanVien INT,
    FOREIGN KEY(idNhaCungCap) REFERENCES nhaCungCap(idNhaCungCap),
    FOREIGN KEY(idNhanVien) REFERENCES nhanVien(idNhanVien)

); CREATE TABLE danhMuc(
    idDanhMuc INT PRIMARY KEY AUTO_INCREMENT,
    tenDanhMuc VARCHAR(100),
    ghiChu TEXT

); CREATE TABLE sanPham(
    idSanPham INT PRIMARY KEY AUTO_INCREMENT,
    tenSanPham VARCHAR(255),
    moTa TEXT,
    giaBan DECIMAL(10, 2),
    hinhAnhUrl TEXT,
    isActive BOOLEAN DEFAULT TRUE,
    idDanhMuc INT,
    idNguyenLieu INT,
    FOREIGN KEY(idDanhMuc) REFERENCES danhMuc(idDanhMuc),
    FOREIGN KEY(idNguyenLieu) REFERENCES khoNguyenLieu(idNguyenLieu)

); CREATE TABLE chiTietSanPham(
    idSanPham INT,
    idNguyenLieu INT,
    soLuongCan DECIMAL(10, 2),
    PRIMARY KEY(idSanPham, idNguyenLieu),
    FOREIGN KEY(idSanPham) REFERENCES sanPham(idSanPham),
    FOREIGN KEY(idNguyenLieu) REFERENCES khoNguyenLieu(idNguyenLieu)

); CREATE TABLE khachHang(
    idKhachHang INT PRIMARY KEY AUTO_INCREMENT,
    hoTen VARCHAR(100),
    soDienThoai VARCHAR(15),
    ngaySinh DATE,
    diemTichLuy INT DEFAULT 0

); CREATE TABLE hoaDon(
    idHoaDon BIGINT PRIMARY KEY AUTO_INCREMENT,
    ngayTao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ngayCapNhat TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    trangThai TINYINT DEFAULT 1,
    tongTien DECIMAL(12, 2),
    idNhanVien INT,
    idKhachHang INT,
    FOREIGN KEY(idNhanVien) REFERENCES nhanVien(idNhanVien),
    FOREIGN KEY(idKhachHang) REFERENCES khachHang(idKhachHang)
); CREATE TABLE chiTietHoaDon(
    idHoaDon BIGINT,
    idSanPham INT,
    soLuong INT,
    donGia DECIMAL(10, 2),
    thueVAT DECIMAL(5, 2),
    idNganHang INT,
    thanhTien DECIMAL(12, 2) GENERATED ALWAYS AS(
        soLuong * donGia *(1 + thueVAT / 100)
    ) STORED,
    isActive BOOLEAN DEFAULT TRUE,
    PRIMARY KEY(idHoaDon, idSanPham),
    FOREIGN KEY(idHoaDon) REFERENCES hoaDon(idHoaDon) ON DELETE CASCADE,
    FOREIGN KEY(idSanPham) REFERENCES sanPham(idSanPham),
    FOREIGN KEY(idNganHang) REFERENCES nganHang(idNganHang)
); SET
    FOREIGN_KEY_CHECKS = 1;
    -- =============================================
    -- 3. NẠP DỮ LIỆU MẪU (SEEDING DATA)
    -- =============================================
    -- 3.1 Chức vụ
INSERT INTO chucVu(tenChucVu, luongCoBan)
VALUES('Quản Lý', 15000000), -- ID 1
('Pha Chế', 8000000), -- ID 2
('Phục Vụ', 6000000), -- ID 3
('Bảo Vệ', 5000000); -- ID 4
-- 3.2 Tài khoản (Mật khẩu hash MD5 của '123456') - KHÔNG CÒN CỘT ẢNH
INSERT INTO taiKhoanNhanVien(tenDangNhap, matKhauHash)
VALUES(
    'admin',
    'e10adc3949ba59abbe56e057f20f883e'
), -- ID 1
(
    'barista_lan',
    'e10adc3949ba59abbe56e057f20f883e'
), -- ID 2
(
    'pv_hung',
    'e10adc3949ba59abbe56e057f20f883e'
), -- ID 3
(
    'bv_tuan',
    'e10adc3949ba59abbe56e057f20f883e'
), -- ID 4
(
    'pv_hoa',
    'e10adc3949ba59abbe56e057f20f883e'
); -- ID 5
-- 3.3 Nhân viên (Tạo nhiều nhân viên)
INSERT INTO nhanVien(
    hoTen,
    soDienThoai,
    email,
    idChucVu,
    idTaiKhoan,
    phanQuyen
)
VALUES(
    'Nguyễn Thành Đạt',
    '0909111111',
    'dat@coffee.com',
    1,
    1,
    'admin'
), -- ID 1 (Quản lý)
(
    'Lê Thị Lan',
    '0909222222',
    'lan@coffee.com',
    2,
    2,
    'nhanVien'
), -- ID 2 (Pha chế)
(
    'Trần Văn Hùng',
    '0909333333',
    'hung@coffee.com',
    3,
    3,
    'nhanVien'
), -- ID 3 (Phục vụ)
(
    'Phạm Văn Tuấn',
    '0909444444',
    'tuan@coffee.com',
    4,
    4,
    'nhanVien'
), -- ID 4 (Bảo vệ)
(
    'Nguyễn Thị Hoa',
    '0909555555',
    'hoa@coffee.com',
    3,
    5,
    'nhanVien'
), -- ID 5 (Phục vụ)
(
    'Trương Văn Mới',
    '0909666666',
    'moi@coffee.com',
    3,
    NULL,
    'nhanVien'
); -- ID 6 (Chưa có TK)
-- =============================================
-- 4. NẠP DỮ LIỆU CHẤM CÔNG & LƯƠNG (SỐ LƯỢNG LỚN)
-- =============================================
-- --- THÁNG 10/2025 (Tháng đầy đủ - Đã thanh toán) ---
-- Lan (ID 2), Hùng (ID 3), Tuấn (ID 4) làm việc chăm chỉ
-- Ngày 01/10
INSERT INTO bangChamCong(
    idNhanVien,
    gioVao,
    gioRa,
    soGioCong,
    tongGioLam
)
VALUES(
    2,
    '2025-10-01 07:00:00',
    '2025-10-01 15:00:00',
    8.0,
    8.0
),(
    3,
    '2025-10-01 07:30:00',
    '2025-10-01 15:30:00',
    8.0,
    8.0
),(
    4,
    '2025-10-01 18:00:00',
    '2025-10-01 22:00:00',
    4.0,
    4.0
);
INSERT INTO luong(
    idNhanVien,
    idChamCong,
    luongNV,
    soGioCong,
    tongLuong,
    ttThanhToan
)
VALUES(
    2,
    1,
    38461,
    8.0,
    307688,
    'DaThanhToan'
),(
    3,
    2,
    28846,
    8.0,
    230768,
    'DaThanhToan'
),(
    4,
    3,
    24038,
    4.0,
    96152,
    'DaThanhToan'
);
-- Ngày 02/10
INSERT INTO bangChamCong(
    idNhanVien,
    gioVao,
    gioRa,
    soGioCong,
    tongGioLam
)
VALUES(
    2,
    '2025-10-02 07:00:00',
    '2025-10-02 15:00:00',
    8.0,
    8.0
),(
    3,
    '2025-10-02 08:00:00',
    '2025-10-02 12:00:00',
    4.0,
    4.0
); -- Hùng làm nửa buổi
INSERT INTO luong(
    idNhanVien,
    idChamCong,
    luongNV,
    soGioCong,
    tongLuong,
    ttThanhToan
)
VALUES(
    2,
    4,
    38461,
    8.0,
    307688,
    'DaThanhToan'
),(
    3,
    5,
    28846,
    4.0,
    115384,
    'DaThanhToan'
);
-- Ngày 03/10 đến 05/10 (Lan làm liên tục)
INSERT INTO bangChamCong(
    idNhanVien,
    gioVao,
    gioRa,
    soGioCong,
    tongGioLam
)
VALUES(
    2,
    '2025-10-03 07:00:00',
    '2025-10-03 15:00:00',
    8.0,
    8.0
),(
    2,
    '2025-10-04 07:00:00',
    '2025-10-04 15:00:00',
    8.0,
    8.0
),(
    2,
    '2025-10-05 07:00:00',
    '2025-10-05 15:00:00',
    8.0,
    8.0
);
INSERT INTO luong(
    idNhanVien,
    idChamCong,
    luongNV,
    soGioCong,
    tongLuong,
    ttThanhToan
)
VALUES(
    2,
    6,
    38461,
    8.0,
    307688,
    'DaThanhToan'
),(
    2,
    7,
    38461,
    8.0,
    307688,
    'DaThanhToan'
),(
    2,
    8,
    38461,
    8.0,
    307688,
    'DaThanhToan'
);
-- --- THÁNG 11/2025 (Hỗn hợp: Đã TT và Chưa TT) ---
-- Hoa (ID 5) bắt đầu đi làm
-- Ngày 15/11 (Đã thanh toán)
INSERT INTO bangChamCong(
    idNhanVien,
    gioVao,
    gioRa,
    soGioCong,
    tongGioLam
)
VALUES(
    2,
    '2025-11-15 07:00:00',
    '2025-11-15 15:00:00',
    8.0,
    8.0
),(
    5,
    '2025-11-15 08:00:00',
    '2025-11-15 16:00:00',
    8.0,
    8.0
);
INSERT INTO luong(
    idNhanVien,
    idChamCong,
    luongNV,
    soGioCong,
    tongLuong,
    ttThanhToan
)
VALUES(
    2,
    9,
    38461,
    8.0,
    307688,
    'DaThanhToan'
),(
    5,
    10,
    28846,
    8.0,
    230768,
    'DaThanhToan'
);
-- Ngày 20/11 (Chưa thanh toán)
INSERT INTO bangChamCong(
    idNhanVien,
    gioVao,
    gioRa,
    soGioCong,
    tongGioLam
)
VALUES(
    3,
    '2025-11-20 07:00:00',
    '2025-11-20 15:00:00',
    8.0,
    8.0
),(
    4,
    '2025-11-20 17:00:00',
    '2025-11-20 23:00:00',
    6.0,
    6.0
);
INSERT INTO luong(
    idNhanVien,
    idChamCong,
    luongNV,
    soGioCong,
    tongLuong,
    ttThanhToan
)
VALUES(
    3,
    11,
    28846,
    8.0,
    230768,
    'ChuaThanhToan'
),(
    4,
    12,
    24038,
    6.0,
    144228,
    'ChuaThanhToan'
);
-- --- THÁNG 12/2025 (Hiện tại - Nhiều dữ liệu) ---
-- Ngày 01/12
INSERT INTO bangChamCong(
    idNhanVien,
    gioVao,
    gioRa,
    soGioCong,
    tongGioLam
)
VALUES(
    2,
    '2025-12-01 07:00:00',
    '2025-12-01 15:00:00',
    8.0,
    8.0
), -- Lan
(
    3,
    '2025-12-01 07:00:00',
    '2025-12-01 15:00:00',
    8.0,
    8.0
), -- Hùng
(
    5,
    '2025-12-01 08:00:00',
    '2025-12-01 17:00:00',
    9.0,
    8.0
); -- Hoa (Tăng ca -> 8h)
INSERT INTO luong(
    idNhanVien,
    idChamCong,
    luongNV,
    soGioCong,
    tongLuong,
    ttThanhToan
)
VALUES(
    2,
    13,
    38461,
    8.0,
    307688,
    'ChuaThanhToan'
),(
    3,
    14,
    28846,
    8.0,
    230768,
    'ChuaThanhToan'
),(
    5,
    15,
    28846,
    8.0,
    230768,
    'ChuaThanhToan'
);
-- Ngày 02/12
INSERT INTO bangChamCong(
    idNhanVien,
    gioVao,
    gioRa,
    soGioCong,
    tongGioLam
)
VALUES(
    2,
    '2025-12-02 07:00:00',
    '2025-12-02 15:30:00',
    8.5,
    8.5
), -- Lan làm thêm 30p
(
    4,
    '2025-12-02 18:00:00',
    '2025-12-03 02:00:00',
    8.0,
    8.0
); -- Tuấn làm đêm
INSERT INTO luong(
    idNhanVien,
    idChamCong,
    luongNV,
    soGioCong,
    tongLuong,
    ttThanhToan
)
VALUES(
    2,
    16,
    38461,
    8.5,
    326918,
    'ChuaThanhToan'
),(
    4,
    17,
    24038,
    8.0,
    192304,
    'ChuaThanhToan'
);
-- Ngày 03/12 (Chấm công nhưng chưa tính lương - Tình huống giả định)
-- ...
-- Ngày Hôm Nay (Giả sử đang làm, chưa check out)
INSERT INTO bangChamCong(
    idNhanVien,
    gioVao,
    gioRa,
    soGioCong,
    tongGioLam
)
VALUES(2, NOW(), NULL, 0, 0), -- Lan đang làm
(5, NOW(), NULL, 0, 0); -- Hoa đang làm