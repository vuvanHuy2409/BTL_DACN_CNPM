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
USE coffeeShop;
-- =============================================
-- 1. DỮ LIỆU NHÂN SỰ & TÀI KHOẢN
-- =============================================

-- 1.1 Chức vụ
INSERT INTO chucVu (tenChucVu, luongCoBan) VALUES
('Quản Lý Cửa Hàng', 15000000), -- ID 1
('Pha Chế Trưởng', 9000000),    -- ID 2
('Pha Chế Viên', 7000000),      -- ID 3
('Phục Vụ', 5500000),           -- ID 4
('Thu Ngân', 6000000),          -- ID 5
('Bảo Vệ', 5000000);            -- ID 6

-- 1.2 Tài khoản (Pass demo: 123456 -> MD5)
INSERT INTO taiKhoanNhanVien (tenDangNhap, matKhauHash) VALUES
('admin', 'e10adc3949ba59abbe56e057f20f883e'),      -- ID 1
('barista_truong', 'e10adc3949ba59abbe56e057f20f883e'), -- ID 2
('thu_ngan', 'e10adc3949ba59abbe56e057f20f883e'),   -- ID 3
('phuc_vu', 'e10adc3949ba59abbe56e057f20f883e');    -- ID 4

-- 1.3 Nhân viên
INSERT INTO nhanVien (hoTen, soDienThoai, email, idChucVu, idTaiKhoan, phanQuyen) VALUES
('Nguyễn Thành Đạt', '0909111222', 'dat.admin@coffee.com', 1, 1, 'admin'),
('Lê Thị Thanh Hương', '0909333444', 'huong.barista@coffee.com', 2, 2, 'nhanVien'),
('Trần Văn Tính', '0909555666', 'tinh.cashier@coffee.com', 5, 3, 'nhanVien'),
('Phạm Quỳnh Anh', '0909777888', 'anh.pv@coffee.com', 4, 4, 'nhanVien'),
('Võ Văn Hùng', '0909999000', 'hung.bv@coffee.com', 6, NULL, 'nhanVien'); -- Bảo vệ không cần TK

-- =============================================
-- 2. DỮ LIỆU KHO & NHÀ CUNG CẤP
-- =============================================

-- 2.1 Nhà cung cấp
INSERT INTO nhaCungCap (tenNhaCungCap, soDienThoai, diaChi) VALUES
('Trung Nguyên Legend', '0283111222', 'Cung cấp Cà phê hạt, bột'),
('Vinamilk Pro', '1900123456', 'Cung cấp Sữa tươi, Sữa đặc, Sữa chua'),
('Nguyên Liệu Pha Chế Việt', '0901234567', 'Cung cấp Syrup, Bột kem, Trà'),
('Nông Sản Sạch Đà Lạt', '0633888999', 'Cung cấp Trái cây tươi (Bơ, Dâu, Cam)'),
('Bao Bì Xanh', '0289999888', 'Cung cấp Ly, Ống hút, Túi đựng');

-- 2.2 Kho nguyên liệu (Liên kết NCC và Nhân viên nhập là ID 1)
INSERT INTO khoNguyenLieu (tenNguyenLieu, giaNhap, soLuongTon, donViTinh, ngayNhap, idNhaCungCap, idNhanVien, isActive) VALUES
-- Cà phê
('Hạt Cafe Robusta', 200000, 10000, 'gram', CURDATE(), 1, 1, 1), -- ID 1
('Hạt Cafe Arabica', 350000, 5000, 'gram', CURDATE(), 1, 1, 1),  -- ID 2
-- Sữa
('Sữa Tươi Thanh Trùng', 32000, 50000, 'ml', CURDATE(), 2, 1, 1), -- ID 3
('Sữa Đặc Ngôi Sao', 22000, 100, 'hop', CURDATE(), 2, 1, 1),      -- ID 4
('Sữa Chua Có Đường', 6000, 200, 'hop', CURDATE(), 2, 1, 1),      -- ID 5
-- Trà
('Trà Đen Phúc Long', 120000, 3000, 'gram', CURDATE(), 3, 1, 1),  -- ID 6
('Trà Oolong', 250000, 2000, 'gram', CURDATE(), 3, 1, 1),         -- ID 7
('Trà Lài', 150000, 2000, 'gram', CURDATE(), 3, 1, 1),            -- ID 8
-- Hoa quả & Topping
('Đào Ngâm Hộp', 65000, 50, 'hop', CURDATE(), 3, 1, 1),           -- ID 9
('Vải Ngâm Hộp', 68000, 50, 'hop', CURDATE(), 3, 1, 1),           -- ID 10
('Cam Tươi', 25000, 20, 'kg', CURDATE(), 4, 1, 1),                -- ID 11
('Bơ Sáp', 45000, 15, 'kg', CURDATE(), 4, 1, 1),                  -- ID 12
('Trân Châu Đen', 40000, 5000, 'gram', CURDATE(), 3, 1, 1),       -- ID 13
-- Khác
('Đường Cát', 18000, 10000, 'gram', CURDATE(), 3, 1, 1),          -- ID 14
('Bột Cacao', 150000, 2000, 'gram', CURDATE(), 3, 1, 1);          -- ID 15

-- =============================================
-- 3. MENU SẢN PHẨM & CÔNG THỨC
-- =============================================

-- 3.1 Danh mục
INSERT INTO danhMuc (tenDanhMuc, ghiChu) VALUES
('Cà Phê Truyền Thống', 'Đậm đà hương vị Việt'),
('Cà Phê Máy (Italian)', 'Espresso, Latte, Capuchino'),
('Trà Trái Cây', 'Thanh mát giải nhiệt'),
('Trà Sữa', 'Thơm ngon béo ngậy'),
('Sinh Tố & Đá Xay', 'Healthy và Mát lạnh');

-- 3.2 Sản phẩm
-- Lưu ý: idNguyenLieu là nguyên liệu chính để trừ kho nhanh
INSERT INTO sanPham (tenSanPham, moTa, giaBan, idDanhMuc, idNguyenLieu) VALUES
-- Cà Phê VN (ID DM: 1)
('Cà Phê Đen Đá', 'Cafe Robusta đậm đặc', 25000, 1, 1),       -- ID 1 (Link: Robusta)
('Cà Phê Sữa Đá', 'Robusta kết hợp sữa đặc', 29000, 1, 1),    -- ID 2 (Link: Robusta)
('Bạc Xỉu', 'Nhiều sữa ít cafe', 35000, 1, 4),                -- ID 3 (Link: Sữa đặc)

-- Cà Phê Máy (ID DM: 2)
('Espresso', 'Chiết xuất máy nguyên chất', 30000, 2, 2),      -- ID 4 (Link: Arabica)
('Latte Nóng', 'Cafe và sữa tươi nóng', 45000, 2, 2),         -- ID 5 (Link: Arabica)
('Capuchino', 'Bọt sữa bồng bềnh', 45000, 2, 2),              -- ID 6 (Link: Arabica)

-- Trà Trái Cây (ID DM: 3)
('Trà Đào Cam Sả', 'Best seller', 45000, 3, 9),               -- ID 7 (Link: Đào hộp)
('Trà Vải Nhiệt Đới', 'Hương vải thơm lừng', 45000, 3, 10),   -- ID 8 (Link: Vải hộp)
('Lục Trà Cam Vàng', 'Trà lài kết hợp cam tươi', 40000, 3, 11),-- ID 9 (Link: Cam tươi)

-- Trà Sữa (ID DM: 4)
('Trà Sữa Truyền Thống', 'Đậm vị trà đen', 35000, 4, 6),      -- ID 10 (Link: Trà đen)
('Trà Sữa Oolong', 'Thơm nồng nàn', 40000, 4, 7),             -- ID 11 (Link: Oolong)

-- Sinh Tố (ID DM: 5)
('Sinh Tố Bơ', 'Bơ sáp dẻo mịn', 50000, 5, 12),               -- ID 12 (Link: Bơ)
('Sữa Chua Đánh Đá', 'Chua ngọt mát lạnh', 30000, 5, 5);      -- ID 13 (Link: Sữa chua)

-- 3.3 Công thức chi tiết (Dùng để trừ kho chính xác hơn)
INSERT INTO chiTietSanPham (idSanPham, idNguyenLieu, soLuongCan) VALUES
-- Cafe Đen
(1, 1, 20), (1, 14, 10), -- 20g Cafe + 10g Đường
-- Cafe Sữa
(2, 1, 20), (2, 4, 0.2), -- 20g Cafe + 0.2 hộp sữa đặc
-- Trà Đào
(7, 6, 5), (7, 9, 0.25), -- 5g Trà đen + 1/4 hộp đào
-- Sinh tố Bơ
(12, 12, 0.2), (12, 4, 0.1); -- 200g Bơ + Sữa đặc

-- =============================================
-- 4. KHÁCH HÀNG THÂN THIẾT
-- =============================================

INSERT INTO khachHang (hoTen, soDienThoai, ngaySinh, diemTichLuy) VALUES
('Khách Vãng Lai', NULL, NULL, 0),
('Nguyễn Văn An', '0912345678', '1995-05-20', 150),
('Trần Thị Bích', '0987654321', '1998-11-11', 320),
('Lê Hoàng Nam', '0901122334', '2000-01-01', 50),
('Phạm Minh Tuấn', '0933445566', '1990-08-15', 800), -- Khách VIP
('Đỗ Thị Hồng', '0977889900', '1999-12-25', 120);

-- =============================================
-- 5. NGÂN HÀNG (Để thanh toán)
-- =============================================
INSERT INTO nganHang (maNganHang, tenNganHang, soTaiKhoan, tenTaiKhoan) VALUES
('VCB', 'Vietcombank', '999988886666', 'COFFEE HOUSE'),
('MB', 'MB Bank', '111122223333', 'NGUYEN THANH DAT'),
('MOMO', 'Ví MoMo', '0909111222', 'NGUYEN THANH DAT');