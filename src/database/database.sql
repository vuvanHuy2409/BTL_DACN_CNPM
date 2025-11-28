-- =============================================
-- KHỞI TẠO DATABASE
-- =============================================

-- Xóa database cũ nếu tồn tại để tránh lỗi trùng lặp khi chạy lại script
DROP DATABASE IF EXISTS coffeeShop;

-- Tạo database mới với bảng mã utf8mb4 để hỗ trợ đầy đủ tiếng Việt và emoji
CREATE DATABASE coffeeShop CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Chọn sử dụng database vừa tạo
USE coffeeShop;

-- Thiết lập môi trường làm việc để hiển thị đúng tiếng Việt
SET NAMES 'utf8mb4';

-- =============================================
-- QUẢN LÝ NHÂN SỰ VÀ TÀI KHOẢN
-- =============================================

-- Bảng Tài khoản nhân viên: Lưu thông tin đăng nhập và bảo mật
-- vectorKhuonMat: Dữ liệu sinh trắc học (nếu dùng điểm danh khuôn mặt)
CREATE TABLE taiKhoanNhanVien (
    idTaiKhoan INT PRIMARY KEY AUTO_INCREMENT,-- Mã tài khoản
    tenDangNhap VARCHAR(50) NOT NULL UNIQUE, -- Tên đăng nhập không được trùng
    matKhauHash VARCHAR(255) NOT NULL,       -- Mật khẩu đã được mã hóa (Hash)
    vectorKhuonMat BLOB                      -- Lưu trữ dữ liệu khuôn mặt dạng nhị phân
);

-- Bảng Chức vụ: Định nghĩa các vị trí làm việc (Quản lý, Pha chế, Phục vụ...)
CREATE TABLE chucVu (
    idChucVu INT PRIMARY KEY AUTO_INCREMENT, -- Mã chức vụ
    tenChucVu VARCHAR(100) NOT NULL UNIQUE,  -- Tên chức vụ
    luongCoBan DECIMAL(10,2) DEFAULT 0       -- Mức lương cơ bản cho vị trí này
);

-- Bảng Nhân viên: Thông tin hồ sơ nhân sự chính
-- Liên kết với bảng Chức vụ và Tài khoản
CREATE TABLE nhanVien (
    idNhanVien INT PRIMARY KEY AUTO_INCREMENT,-- Mã nhân viên
    hoTen VARCHAR(100) NOT NULL,              -- Họ và tên đầy đủ
    soDienThoai VARCHAR(15) UNIQUE,           -- Số điện thoại liên hệ
    email VARCHAR(100) UNIQUE,                -- Địa chỉ email
    ngayBatDau DATE,                          -- Ngày bắt đầu làm việc
    trangThaiLamViec ENUM('DangLamViec','DaNghiViec') DEFAULT 'DangLamViec',-- Trạng thái làm việc
    phanQuyen ENUM('nhanVien', 'admin') DEFAULT 'nhanVien', -- Mặc định là nhân viên thường
    ngayTao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,            -- Ngày tạo hồ sơ
    ngayCapNhat TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP, -- Ngày cập nhật hồ sơ gần nhất
    idChucVu INT NOT NULL,                                  -- Liên kết chức vụ
    idTaiKhoan INT UNIQUE,                                  -- Liên kết tài khoản đăng nhập
    FOREIGN KEY (idChucVu) REFERENCES chucVu(idChucVu),     -- Liên kết chức vụ
    FOREIGN KEY (idTaiKhoan) REFERENCES taiKhoanNhanVien(idTaiKhoan)-- Liên kết tài khoản
);

-- =============================================
-- TÀI CHÍNH VÀ CHẤM CÔNG
-- =============================================

-- Bảng Ngân hàng: Lưu thông tin các ngân hàng (dùng cho thanh toán chuyển khoản)
CREATE TABLE nganHang (
    idNganHang INT PRIMARY KEY AUTO_INCREMENT,
    maNganHang VARCHAR(20),     -- Mã ngân hàng (VD: VCB, TCB)
    tenNganHang VARCHAR(100),   -- Tên đầy đủ ngân hàng
    soTaiKhoan VARCHAR(50) NOT NULL,-- Số tài khoản ngân hàng
    tenTaiKhoan VARCHAR(100) NOT NULL,-- Tên chủ tài khoản
    isActive BOOLEAN DEFAULT TRUE
);

-- Bảng Chấm công: Ghi nhận thời gian ra/vào ca làm việc
CREATE TABLE bangChamCong (
    idChamCong BIGINT PRIMARY KEY AUTO_INCREMENT,
    gioVao DATETIME NOT NULL,               -- Giờ bắt đầu ca
    gioRa DATETIME NULL,                    -- Giờ kết thúc ca (NULL nếu chưa checkout)
    soGioCong DECIMAL(5,2) DEFAULT 0,       -- Tổng số giờ làm trong ca
    tongGioLam DECIMAL(5,2) DEFAULT 0       -- Có thể là tổng giờ tích lũy (tùy logic xử lý)
);

-- Bảng Lương: Tính toán chi trả lương dựa trên từng lần chấm công
CREATE TABLE luong (
    idNhanVien INT NOT NULL,                -- Mã nhân viên
    idChamCong BIGINT NOT NULL,             -- Mã chấm công tương ứng
    luongNV DECIMAL(12,2) NOT NULL,         -- Mức lương áp dụng tại thời điểm đó
    soGioCong DECIMAL(5,2) NOT NULL,        -- Số giờ làm việc thực tế
    tongLuong DECIMAL(12,2) NOT NULL,       -- Tổng tiền (luongNV * soGioCong)
    ttThanhToan ENUM('ChuaThanhToan','DaThanhToan') DEFAULT 'ChuaThanhToan',
    PRIMARY KEY (idNhanVien, idChamCong),   -- Khóa chính phức hợp
    FOREIGN KEY (idNhanVien) REFERENCES nhanVien(idNhanVien),
    FOREIGN KEY (idChamCong) REFERENCES bangChamCong(idChamCong)
);

-- =============================================
-- QUẢN LÝ KHO VÀ NGUYÊN LIỆU
-- =============================================

-- Bảng Nhà cung cấp: Đối tác cung cấp nguyên vật liệu
CREATE TABLE nhaCungCap (
    idNhaCungCap INT PRIMARY KEY AUTO_INCREMENT,     -- Mã nhà cung cấp
    tenNhaCungCap VARCHAR(255) NOT NULL,             -- Tên nhà cung cấp
    soDienThoai VARCHAR(15),                  -- Số điện thoại liên hệ
    diaChi TEXT,                              -- Địa chỉ liên hệ
    ngayCapNhat DATE,                          -- Ngày cập nhật thông tin gần nhất
    isActive BOOLEAN DEFAULT TRUE              -- Trạng thái hoạt động
);

-- Bảng Kho nguyên liệu: Quản lý tồn kho (Cafe hạt, đường, sữa...)
CREATE TABLE khoNguyenLieu (
    idNguyenLieu INT PRIMARY KEY AUTO_INCREMENT,-- Mã nguyên liệu
    tenNguyenLieu VARCHAR(255) NOT NULL,    -- Tên nguyên liệu
    giaNhap DECIMAL(10,2) NOT NULL,         -- Giá nhập vào
    soLuongTon DECIMAL(10,2) DEFAULT 0,     -- Số lượng hiện có trong kho
    donViTinh VARCHAR(50) NOT NULL,         -- VD: kg, lít, hộp
    ngayNhap DATE,                          -- Ngày nhập kho gần nhất
    idNhaCungCap INT,                       -- Nhà cung cấp
    idNhanVien INT,                         -- Nhân viên thực hiện nhập kho
    FOREIGN KEY (idNhaCungCap) REFERENCES nhaCungCap(idNhaCungCap),
    FOREIGN KEY (idNhanVien) REFERENCES nhanVien(idNhanVien)
);

-- =============================================
-- SẢN PHẨM VÀ THỰC ĐƠN
-- =============================================

-- Bảng Danh mục: Phân loại đồ uống/món ăn (Cafe, Trà, Bánh...)
CREATE TABLE danhMuc (
    idDanhMuc INT PRIMARY KEY AUTO_INCREMENT,-- Mã danh mục
    tenDanhMuc VARCHAR(100) NOT NULL,                  -- Tên danh mục
    ghiChu TEXT                              -- Mô tả thêm về danh mục
);

-- Bảng Sản phẩm: Các món được bán trong menu
CREATE TABLE sanPham (
    idSanPham INT PRIMARY KEY AUTO_INCREMENT,
    tenSanPham VARCHAR(255) NOT NULL,
    moTa TEXT,
    giaBan DECIMAL(10,2) NOT NULL,
    hinhAnhUrl TEXT,                        -- Đường dẫn ảnh sản phẩm
    isActive BOOLEAN DEFAULT TRUE,          -- Trạng thái: Còn bán hay ngừng kinh doanh
    idDanhMuc INT,
    FOREIGN KEY (idDanhMuc) REFERENCES danhMuc(idDanhMuc)
);
-- Bảng Công thức sản phẩm: Liệt kê nguyên liệu cần cho mỗi món
CREATE TABLE chiTietSanPham (
    idSanPham INT NOT NULL,
    idNguyenLieu INT NOT NULL,
    soLuongCan DECIMAL(10,2) NOT NULL,      -- Số lượng nguyên liệu cần (VD: 20g cafe)
    FOREIGN KEY (idSanPham) REFERENCES sanPham(idSanPham),
    FOREIGN KEY (idNguyenLieu) REFERENCES khoNguyenLieu(idNguyenLieu)
);

-- =============================================
-- KHÁCH HÀNG VÀ BÁN HÀNG
-- =============================================

-- Bảng Khách hàng: Lưu thông tin thành viên thân thiết
CREATE TABLE khachHang (
    idKhachHang INT PRIMARY KEY AUTO_INCREMENT,
    hoTen VARCHAR(100) NOT NULL,
    soDienThoai VARCHAR(15) UNIQUE,
    ngaySinh DATE,                          -- Dùng để tặng quà sinh nhật
    diemTichLuy INT DEFAULT 0               -- Điểm thưởng
);

-- Bảng Hóa đơn: Thông tin chung của đơn hàng
CREATE TABLE hoaDon (
    idHoaDon BIGINT PRIMARY KEY AUTO_INCREMENT,
    ngayTao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ngayCapNhat TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    trangThai TINYINT DEFAULT 1,            -- 1: Chờ thanh toán, 2: Đã thanh toán, 0: Hủy
    tongTien DECIMAL(12,2) NOT NULL,
    idNhanVien INT NOT NULL,                -- Nhân viên lập hóa đơn
    idKhachHang INT NULL,                   -- Khách hàng (có thể NULL nếu khách vãng lai)
    FOREIGN KEY (idNhanVien) REFERENCES nhanVien(idNhanVien),
    FOREIGN KEY (idKhachHang) REFERENCES khachHang(idKhachHang)
);

-- Bảng Chi tiết hóa đơn: Các món trong đơn hàng
CREATE TABLE chiTietHoaDon (
    idHoaDon BIGINT NOT NULL,
    idSanPham INT NOT NULL,
    soLuong INT NOT NULL,
    donGia DECIMAL(10,2) NOT NULL,          -- Giá tại thời điểm bán (đề phòng giá gốc thay đổi)
    thueVAT DECIMAL(5,2) DEFAULT 0.00,
    idNganHang INT,                         -- Nếu thanh toán chuyển khoản thì lưu ngân hàng nào
    thanhTien DECIMAL(12,2) GENERATED ALWAYS AS (soLuong * donGia * (1 + thueVAT/100)) STORED,
    isActive BOOLEAN DEFAULT TRUE,          -- Trạng thái món (bị hủy hay không)
    PRIMARY KEY (idHoaDon, idSanPham),      -- Khóa chính phức hợp để 1 món không xuất hiện 2 dòng trong 1 bill
    FOREIGN KEY (idHoaDon) REFERENCES hoaDon(idHoaDon) ON DELETE CASCADE, -- Xóa hóa đơn cha thì chi tiết cũng mất
    FOREIGN KEY (idSanPham) REFERENCES sanPham(idSanPham),
    FOREIGN KEY (idNganHang) REFERENCES nganHang(idNganHang)
);
USE coffeeShop;

-- =============================================
-- 1. DỮ LIỆU NHÂN SỰ (Chức vụ, Tài khoản, Nhân viên)
-- =============================================

-- Thêm chức vụ
INSERT INTO chucVu (tenChucVu, luongCoBan) VALUES
('QuanLy', 10000000.00),
('PhaChe', 7000000.00),
('PhucVu', 5000000.00),
('BaoVe', 4500000.00);

-- Thêm tài khoản (Mật khẩu demo là chuỗi hash ví dụ của '123456')
INSERT INTO taiKhoanNhanVien (tenDangNhap, matKhauHash, vectorKhuonMat) VALUES
('admin', 'e10adc3949ba59abbe56e057f20f883e', NULL), -- Admin
('barista01', 'e10adc3949ba59abbe56e057f20f883e', NULL), -- Staff
('phucvu01', 'e10adc3949ba59abbe56e057f20f883e', NULL); -- Staff

-- Thêm nhân viên
-- Giả sử ID Chức vụ: 1=QL, 2=PhaChe, 3=PhucVu
-- Giả sử ID Tài khoản: 1=admin, 2=barista01, 3=phucvu01
INSERT INTO nhanVien (hoTen, soDienThoai, email, ngayBatDau, phanQuyen, idChucVu, idTaiKhoan) VALUES
('Nguyễn Văn Quản Lý', '0909123456', 'quanly@coffee.com', '2023-01-01', 'admin', 1, 1),
('Trần Thị Pha Chế', '0909888777', 'barista@coffee.com', '2023-05-15', 'nhanVien', 2, 2),
('Lê Văn Phục Vụ', '0909111222', 'pv@coffee.com', '2023-06-01', 'nhanVien', 3, 3);

-- =============================================
-- 2. DỮ LIỆU KHO & NGUYÊN LIỆU
-- =============================================

-- Thêm nhà cung cấp
INSERT INTO nhaCungCap (tenNhaCungCap, soDienThoai, diaChi) VALUES
('Cà Phê Trung Nguyên', '02831234567', 'Buôn Ma Thuột, Đắk Lắk'),
('Vinamilk', '19006060', 'Quận 7, TP.HCM'),
('Siêu Thị Metro', '02839999999', 'Quận 2, TP.HCM');

-- Thêm nguyên liệu vào kho
-- Đơn vị tính: g (gram), ml (mililit), hop (hộp)
INSERT INTO khoNguyenLieu (tenNguyenLieu, giaNhap, soLuongTon, donViTinh, ngayNhap, idNhaCungCap, idNhanVien) VALUES
('Cafe Hạt Robusta', 250000.00, 5000, 'g', CURDATE(), 1, 1), -- 5kg cafe
('Sữa Tươi Thanh Trùng', 35000.00, 20000, 'ml', CURDATE(), 2, 1), -- 20 lít sữa
('Sữa Đặc Ông Thọ', 25000.00, 50, 'hop', CURDATE(), 2, 1),
('Đường Cát Trắng', 20000.00, 5000, 'g', CURDATE(), 3, 1),
('Trà Đen Phúc Long', 150000.00, 2000, 'g', CURDATE(), 3, 1),
('Đào Ngâm', 65000.00, 10, 'hop', CURDATE(), 3, 1);

-- =============================================
-- 3. DỮ LIỆU MENU & CÔNG THỨC (Sản phẩm)
-- =============================================

-- Thêm danh mục
INSERT INTO danhMuc (tenDanhMuc, ghiChu) VALUES
('Cà Phê Truyền Thống', 'Các món cafe pha phin, pha máy'),
('Trà Trái Cây', 'Các loại trà giải nhiệt'),
('Đá Xay', 'Thức uống đá xay mát lạnh');

-- Thêm sản phẩm
INSERT INTO sanPham (tenSanPham, moTa, giaBan, idDanhMuc) VALUES
('Cà Phê Đen Đá', 'Cafe đậm đà hương vị Việt', 25000.00, 1),
('Cà Phê Sữa Đá', 'Sự kết hợp hoàn hảo giữa cafe và sữa đặc', 29000.00, 1),
('Bạc Xỉu', 'Nhiều sữa ít cafe', 35000.00, 1),
('Trà Đào Cam Sả', 'Trà thanh mát với miếng đào giòn', 45000.00, 2),
('Trà Vải', 'Hương vải thơm lừng', 45000.00, 2);

-- Thêm công thức (Chi tiết sản phẩm)
-- ID NguyenLieu: 1=Cafe, 2=Sữa tươi, 3=Sữa đặc, 4=Đường, 5=Trà, 6=Đào
INSERT INTO chiTietSanPham (idSanPham, idNguyenLieu, soLuongCan) VALUES
(1, 1, 25.00), -- Cafe Đen cần 25g Cafe hạt
(1, 4, 10.00), -- Cafe Đen cần 10g Đường
(2, 1, 25.00), -- Cafe Sữa cần 25g Cafe hạt
(2, 3, 1.00),  -- Cafe Sữa cần 1 hộp sữa đặc (giả dụ đơn vị tính khác nhau, demo logic)
(4, 5, 10.00), -- Trà Đào cần 10g Trà
(4, 4, 20.00); -- Trà Đào cần 20g Đường

-- =============================================
-- 4. DỮ LIỆU KHÁCH HÀNG & NGÂN HÀNG
-- =============================================

INSERT INTO khachHang (hoTen, soDienThoai, ngaySinh, diemTichLuy) VALUES
('Nguyễn Văn Khách', '0912345678', '1995-10-20', 150),
('Lê Thị Thân Thiết', '0987654321', '2000-01-01', 300);

INSERT INTO nganHang (maNganHang, tenNganHang, soTaiKhoan, tenTaiKhoan) VALUES
('VCB', 'Vietcombank', '0071000123456', 'NGUYEN VAN QUAN LY'),
('MB', 'MB Bank', '999988887777', 'COFFEE SHOP');

-- =============================================
-- 5. DỮ LIỆU BÁN HÀNG (Hóa đơn & Chi tiết)
-- =============================================

-- Hóa đơn 1: Khách vãng lai, trả tiền mặt
INSERT INTO hoaDon (tongTien, idNhanVien, idKhachHang, trangThai) VALUES
(54000.00, 2, NULL, 2); -- Đã thanh toán

-- Chi tiết Hóa đơn 1 (1 Cafe Đen, 1 Cafe Sữa)
-- Lưu ý: Không cần insert 'thanhTien' vì cột này tự động tính toán
INSERT INTO chiTietHoaDon (idHoaDon, idSanPham, soLuong, donGia, thueVAT) VALUES
(1, 1, 1, 25000.00, 0),
(1, 2, 1, 29000.00, 0);

-- Hóa đơn 2: Khách quen, chuyển khoản
INSERT INTO hoaDon (tongTien, idNhanVien, idKhachHang, trangThai) VALUES
(135000.00, 2, 1, 2);

-- Chi tiết Hóa đơn 2 (3 Trà Đào)
INSERT INTO chiTietHoaDon (idHoaDon, idSanPham, soLuong, donGia, thueVAT, idNganHang) VALUES
(2, 4, 3, 45000.00, 0, 1); -- Chuyển khoản vào VCB

-- =============================================
-- 6. DỮ LIỆU CHẤM CÔNG & LƯƠNG
-- =============================================

-- Chấm công cho nhân viên Pha chế (ID 2)
INSERT INTO bangChamCong (gioVao, gioRa, soGioCong, tongGioLam) VALUES
('2023-10-20 07:00:00', '2023-10-20 15:00:00', 8.0, 8.0),
('2023-10-21 07:00:00', '2023-10-21 15:00:00', 8.0, 16.0);

-- Tính lương thử (Giả sử lương theo giờ = Lương cơ bản / 26 ngày / 8 giờ)
-- Pha chế lương 7tr -> ~33k/giờ
INSERT INTO luong (idNhanVien, idChamCong, luongNV, soGioCong, tongLuong) VALUES
(2, 1, 33653.00, 8.0, 269224.00);


