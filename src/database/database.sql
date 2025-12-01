-- =============================================
-- KHỞI TẠO DATABASE
-- =============================================

DROP DATABASE IF EXISTS coffeeShop;

CREATE DATABASE coffeeShop CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE coffeeShop;

SET NAMES 'utf8mb4';

-- =============================================
-- 1. QUẢN LÝ NHÂN SỰ VÀ TÀI KHOẢN
-- =============================================

-- Bảng Tài khoản nhân viên
CREATE TABLE taiKhoanNhanVien (
    idTaiKhoan INT PRIMARY KEY AUTO_INCREMENT,
    tenDangNhap VARCHAR(50) NOT NULL UNIQUE,
    matKhauHash VARCHAR(255) NOT NULL,
    hinhAnhUrl TEXT,
    vectorKhuonMat BLOB
);

-- Bảng Chức vụ
CREATE TABLE chucVu (
    idChucVu INT PRIMARY KEY AUTO_INCREMENT,
    tenChucVu VARCHAR(100) NOT NULL UNIQUE,
    luongCoBan DECIMAL(10,2) DEFAULT 0
);

-- Bảng Nhân viên
CREATE TABLE nhanVien (
    idNhanVien INT PRIMARY KEY AUTO_INCREMENT,
    hoTen VARCHAR(100) NOT NULL,
    soDienThoai VARCHAR(15) UNIQUE,
    email VARCHAR(100) UNIQUE,
    ngayBatDau DATE,
    trangThaiLamViec ENUM('DangLamViec','DaNghiViec') DEFAULT 'DangLamViec',
    phanQuyen ENUM('nhanVien', 'admin') DEFAULT 'nhanVien',
    ngayTao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ngayCapNhat TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    idChucVu INT NOT NULL,
    idTaiKhoan INT UNIQUE,
    FOREIGN KEY (idChucVu) REFERENCES chucVu(idChucVu),
    FOREIGN KEY (idTaiKhoan) REFERENCES taiKhoanNhanVien(idTaiKhoan)
);

-- =============================================
-- 2. TÀI CHÍNH VÀ CHẤM CÔNG
-- =============================================

-- Bảng Ngân hàng
CREATE TABLE nganHang (
    idNganHang INT PRIMARY KEY AUTO_INCREMENT,
    maNganHang VARCHAR(20),
    tenNganHang VARCHAR(100),
    soTaiKhoan VARCHAR(50) NOT NULL,
    tenTaiKhoan VARCHAR(100) NOT NULL,
    isActive BOOLEAN DEFAULT TRUE
);

-- Bảng Chấm công
CREATE TABLE bangChamCong (
    idChamCong BIGINT PRIMARY KEY AUTO_INCREMENT,
    gioVao DATETIME NOT NULL,
    gioRa DATETIME NULL,
    soGioCong DECIMAL(5,2) DEFAULT 0,
    tongGioLam DECIMAL(5,2) DEFAULT 0
);

-- Bảng Lương
CREATE TABLE luong (
    idNhanVien INT NOT NULL,
    idChamCong BIGINT NOT NULL,
    luongNV DECIMAL(12,2) NOT NULL,
    soGioCong DECIMAL(5,2) NOT NULL,
    tongLuong DECIMAL(12,2) NOT NULL,
    ttThanhToan ENUM('ChuaThanhToan','DaThanhToan') DEFAULT 'ChuaThanhToan',
    PRIMARY KEY (idNhanVien, idChamCong),
    FOREIGN KEY (idNhanVien) REFERENCES nhanVien(idNhanVien),
    FOREIGN KEY (idChamCong) REFERENCES bangChamCong(idChamCong)
);

-- =============================================
-- 3. QUẢN LÝ KHO VÀ NGUYÊN LIỆU
-- =============================================

-- Bảng Nhà cung cấp
CREATE TABLE nhaCungCap (
    idNhaCungCap INT PRIMARY KEY AUTO_INCREMENT,
    tenNhaCungCap VARCHAR(255) NOT NULL,
    soDienThoai VARCHAR(15),
    diaChi TEXT,
    ngayCapNhat DATE,
    isActive BOOLEAN DEFAULT TRUE
);

-- Bảng Kho nguyên liệu
-- (Bảng này phải tạo TRƯỚC bảng sanPham vì sanPham tham chiếu tới nó)
CREATE TABLE khoNguyenLieu (
    idNguyenLieu INT PRIMARY KEY AUTO_INCREMENT,
    tenNguyenLieu VARCHAR(255) NOT NULL,
    giaNhap DECIMAL(10,2) NOT NULL,
    soLuongTon DECIMAL(10,2) DEFAULT 0,
    donViTinh VARCHAR(50) NOT NULL,
    ngayNhap DATE,

    idNhaCungCap INT,
    idNhanVien INT,
    isActive BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (idNhaCungCap) REFERENCES nhaCungCap(idNhaCungCap),
    FOREIGN KEY (idNhanVien) REFERENCES nhanVien(idNhanVien)
);

-- =============================================
-- 4. SẢN PHẨM VÀ THỰC ĐƠN
-- =============================================

-- Bảng Danh mục
CREATE TABLE danhMuc (
    idDanhMuc INT PRIMARY KEY AUTO_INCREMENT,
    tenDanhMuc VARCHAR(100) NOT NULL,
    ghiChu TEXT
);

-- Bảng Sản phẩm
-- [CẬP NHẬT] Đã thêm idNguyenLieu làm khoá phụ
CREATE TABLE sanPham (
    idSanPham INT PRIMARY KEY AUTO_INCREMENT,
    tenSanPham VARCHAR(255) NOT NULL,
    moTa TEXT,
    giaBan DECIMAL(10,2) NOT NULL,
    hinhAnhUrl TEXT,
    isActive BOOLEAN DEFAULT TRUE,
    idDanhMuc INT,
    idNguyenLieu INT, -- Cột mới thêm: Liên kết 1 sản phẩm với 1 nguyên liệu chính (hoặc chính nó)

    FOREIGN KEY (idDanhMuc) REFERENCES danhMuc(idDanhMuc),
    FOREIGN KEY (idNguyenLieu) REFERENCES khoNguyenLieu(idNguyenLieu) -- Khóa ngoại mới
);

-- Bảng Công thức sản phẩm (Chi tiết cấu thành sản phẩm)
-- Vẫn giữ bảng này để xử lý các món pha chế phức tạp (nhiều nguyên liệu)
CREATE TABLE chiTietSanPham (
    idSanPham INT NOT NULL,
    idNguyenLieu INT NOT NULL,
    soLuongCan DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (idSanPham) REFERENCES sanPham(idSanPham),
    FOREIGN KEY (idNguyenLieu) REFERENCES khoNguyenLieu(idNguyenLieu)
);

-- =============================================
-- 5. KHÁCH HÀNG VÀ HÓA ĐƠN
-- =============================================

-- Bảng Khách hàng
CREATE TABLE khachHang (
    idKhachHang INT PRIMARY KEY AUTO_INCREMENT,
    hoTen VARCHAR(100) NOT NULL,
    soDienThoai VARCHAR(15) UNIQUE,
    ngaySinh DATE,
    diemTichLuy INT DEFAULT 0
);

-- Bảng Hóa đơn
CREATE TABLE hoaDon (
    idHoaDon BIGINT PRIMARY KEY AUTO_INCREMENT,
    ngayTao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ngayCapNhat TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    trangThai TINYINT DEFAULT 1, -- 1: Chờ thanh toán, 2: Đã thanh toán, 0: Hủy
    tongTien DECIMAL(12,2) NOT NULL,
    idNhanVien INT NOT NULL,
    idKhachHang INT NULL,
    FOREIGN KEY (idNhanVien) REFERENCES nhanVien(idNhanVien),
    FOREIGN KEY (idKhachHang) REFERENCES khachHang(idKhachHang)
);

-- Bảng Chi tiết hóa đơn
CREATE TABLE chiTietHoaDon (
    idHoaDon BIGINT NOT NULL,
    idSanPham INT NOT NULL,
    soLuong INT NOT NULL,
    donGia DECIMAL(10,2) NOT NULL,
    thueVAT DECIMAL(5,2) DEFAULT 0.00,
    idNganHang INT,
    thanhTien DECIMAL(12,2) GENERATED ALWAYS AS (soLuong * donGia * (1 + thueVAT/100)) STORED,
    isActive BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (idHoaDon, idSanPham),
    FOREIGN KEY (idHoaDon) REFERENCES hoaDon(idHoaDon) ON DELETE CASCADE,
    FOREIGN KEY (idSanPham) REFERENCES sanPham(idSanPham),
    FOREIGN KEY (idNganHang) REFERENCES nganHang(idNganHang)
);
USE coffeeShop;

-- =============================================
-- 1. DỮ LIỆU NHÂN SỰ & TÀI KHOẢN
-- =============================================

-- 1.1 Chức vụ
INSERT INTO chucVu (tenChucVu, luongCoBan) VALUES
('Quản Lý', 15000000.00),          -- ID 1
('Pha Chế (Barista)', 8000000.00), -- ID 2
('Phục Vụ', 5500000.00),           -- ID 3
('Bảo Vệ', 5000000.00);            -- ID 4

--
INSERT INTO taiKhoanNhanVien (tenDangNhap, matKhauHash, hinhAnhUrl) VALUES
('admin', 'e10adc3949ba59abbe56e057f20f883e', NULL),          -- ID 1
('barista_truong', 'e10adc3949ba59abbe56e057f20f883e', NULL), -- ID 2
('pv_sang', 'e10adc3949ba59abbe56e057f20f883e', NULL),        -- ID 3
('pv_toi', 'e10adc3949ba59abbe56e057f20f883e', NULL);         -- ID 4

-- 1.3 Nhân viên
INSERT INTO nhanVien (hoTen, soDienThoai, email, ngayBatDau, phanQuyen, idChucVu, idTaiKhoan) VALUES
('Nguyễn Thành Đạt', '0909111111', 'admin@coffee.com', '2023-01-01', 'admin', 1, 1),
('Lê Thị Pha Chế', '0909222222', 'barista@coffee.com', '2023-02-15', 'nhanVien', 2, 2),
('Trần Văn Sáng', '0909333333', 'sang.pv@coffee.com', '2023-03-01', 'nhanVien', 3, 3),
('Phạm Thị Tối', '0909444444', 'toi.pv@coffee.com', '2023-06-01', 'nhanVien', 3, 4);

-- =============================================
-- 2. TÀI CHÍNH & NGÂN HÀNG
-- =============================================

INSERT INTO nganHang (maNganHang, tenNganHang, soTaiKhoan, tenTaiKhoan, isActive) VALUES
('VCB', 'Vietcombank', '999911112222', 'COFFEE SHOP STORE', 1),
('MB', 'MB Bank', '888833334444', 'NGUYEN THANH DAT', 1),
('TCB', 'Techcombank', '190333444555', 'QUY KHUYEN MAI', 1);

-- =============================================
-- 3. QUẢN LÝ KHO (NCC & NGUYÊN LIỆU)
-- =============================================

-- 3.1 Nhà cung cấp
INSERT INTO nhaCungCap (tenNhaCungCap, soDienThoai, diaChi, isActive, ngayCapNhat) VALUES
('Nguyên Liệu Trung Nguyên', '02839998888', 'Cà phê hạt, bột', 1, CURDATE()),
('Vinamilk Corporate', '19006060', 'Sữa tươi, sữa đặc, sữa chua', 1, CURDATE()),
('Chợ Nông Sản Thủ Đức', '0909999000', 'Trái cây tươi (Cam, Chanh, Dưa)', 1, CURDATE()),
('Công Ty Nhập Khẩu Á Âu', '02437776666', 'Syrup, Đào ngâm, Vải ngâm', 1, CURDATE());

-- 3.2 Kho nguyên liệu
-- Lưu ý: idNguyenLieu sẽ tự tăng từ 1 -> 8
-- Cột isActive đã được thêm vào cuối
INSERT INTO khoNguyenLieu (tenNguyenLieu, giaNhap, soLuongTon, donViTinh, ngayNhap, idNhaCungCap, idNhanVien, isActive) VALUES
('Cafe Hạt Robusta', 220000.00, 10000, 'g', CURDATE(), 1, 1, 1),      -- ID 1
('Cafe Hạt Arabica', 350000.00, 5000, 'g', CURDATE(), 1, 1, 1),       -- ID 2
('Sữa Tươi Thanh Trùng', 32000.00, 20000, 'ml', CURDATE(), 2, 1, 1),  -- ID 3
('Sữa Đặc Ông Thọ', 24000.00, 48, 'hop', CURDATE(), 2, 1, 1),         -- ID 4
('Đường Cát', 18000.00, 5000, 'g', CURDATE(), 3, 1, 1),               -- ID 5
('Trà Đen Túi Lọc', 120000.00, 2000, 'g', CURDATE(), 4, 1, 1),        -- ID 6
('Đào Ngâm Hộp', 65000.00, 20, 'hop', CURDATE(), 4, 1, 1),            -- ID 7
('Cam Tươi', 25000.00, 10, 'kg', CURDATE(), 3, 1, 1);                 -- ID 8

-- =============================================
-- 4. MENU SẢN PHẨM & CÔNG THỨC
-- =============================================

-- 4.1 Danh mục
INSERT INTO danhMuc (tenDanhMuc, ghiChu) VALUES
('Cà Phê Việt Nam', 'Phin, Máy'),
('Trà & Trái Cây', 'Giải nhiệt'),
('Đá Xay (Ice Blended)', 'Mát lạnh'),
('Sinh Tố & Nước Ép', 'Healthy');

-- 4.2 Sản phẩm
-- Lưu ý: idNguyenLieu là nguyên liệu chính để trừ kho nhanh
INSERT INTO sanPham (tenSanPham, moTa, giaBan, idDanhMuc, idNguyenLieu, isActive) VALUES
('Cà Phê Đen Đá', 'Cafe nguyên chất đậm vị', 25000.00, 1, 1, 1),         -- Link: Cafe Robusta
('Cà Phê Sữa Đá', 'Sự hòa quyện sữa và cafe', 29000.00, 1, 1, 1),        -- Link: Cafe Robusta
('Bạc Xỉu', 'Ít cafe nhiều sữa', 35000.00, 1, 4, 1),                     -- Link: Sữa đặc
('Trà Đào Cam Sả', 'Best seller mùa hè', 45000.00, 2, 7, 1),             -- Link: Đào ngâm
('Trà Vải Nhiệt Đới', 'Hương vải thơm lừng', 45000.00, 2, 6, 1),         -- Link: Trà đen
('Nước Ép Cam', 'Cam vắt nguyên chất', 40000.00, 4, 8, 1);               -- Link: Cam tươi

-- 4.3 Công thức chi tiết
INSERT INTO chiTietSanPham (idSanPham, idNguyenLieu, soLuongCan) VALUES
-- Cafe Đen (ID SP: 1)
(1, 1, 20.00), -- 20g Cafe Robusta
(1, 5, 10.00), -- 10g Đường
-- Cafe Sữa (ID SP: 2)
(2, 1, 20.00), -- 20g Cafe
(2, 4, 0.20),  -- 0.2 hộp sữa đặc (quy đổi đơn vị sau)
-- Trà Đào (ID SP: 4)
(4, 6, 5.00),  -- 5g Trà đen
(4, 7, 0.25),  -- 1/4 hộp đào
(4, 5, 20.00); -- 20g Đường

-- =============================================
-- 5. KHÁCH HÀNG & BÁN HÀNG
-- =============================================

INSERT INTO khachHang (hoTen, soDienThoai, ngaySinh, diemTichLuy) VALUES
('Khách Vãng Lai', NULL, NULL, 0),
('Nguyễn Văn Vip', '0912345678', '1995-10-20', 500),
('Trần Thị Thân Thiết', '0987987987', '2000-01-01', 1200);

-- Hóa đơn 1: Khách vãng lai, trả tiền mặt
INSERT INTO hoaDon (tongTien, idNhanVien, idKhachHang, trangThai) VALUES
(54000.00, 3, 1, 2); -- Trạng thái 2: Đã thanh toán
INSERT INTO chiTietHoaDon (idHoaDon, idSanPham, soLuong, donGia, thueVAT) VALUES
(1, 1, 1, 25000.00, 0), -- 1 Cafe Đen
(1, 2, 1, 29000.00, 0); -- 1 Cafe Sữa

-- Hóa đơn 2: Khách VIP, chuyển khoản VCB
INSERT INTO hoaDon (tongTien, idNhanVien, idKhachHang, trangThai) VALUES
(135000.00, 3, 2, 2);
INSERT INTO chiTietHoaDon (idHoaDon, idSanPham, soLuong, donGia, thueVAT, idNganHang) VALUES
(2, 4, 3, 45000.00, 0, 1); -- 3 Trà Đào, CK vào VCB (ID 1)

-- Hóa đơn 3: Hủy món
INSERT INTO hoaDon (tongTien, idNhanVien, idKhachHang, trangThai) VALUES
(40000.00, 3, 1, 0); -- Trạng thái 0: Hủy
INSERT INTO chiTietHoaDon (idHoaDon, idSanPham, soLuong, donGia, thueVAT) VALUES
(3, 6, 1, 40000.00, 0); -- 1 Nước Ép Cam

-- =============================================
-- 6. CHẤM CÔNG & LƯƠNG
-- =============================================

-- Chấm công cho Pha chế (ID NV: 2)
INSERT INTO bangChamCong (gioVao, gioRa, soGioCong, tongGioLam) VALUES
('2023-11-01 07:00:00', '2023-11-01 15:00:00', 8.0, 8.0),
('2023-11-02 07:00:00', '2023-11-02 15:00:00', 8.0, 16.0),
('2023-11-03 07:00:00', NULL, 0, 16.0); -- Đang làm việc

-- Tính lương mẫu
INSERT INTO luong (idNhanVien, idChamCong, luongNV, soGioCong, tongLuong, ttThanhToan) VALUES
(2, 1, 38461.00, 8.0, 307688.00, 'DaThanhToan');