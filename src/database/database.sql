-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Máy chủ: localhost
-- Thời gian đã tạo: Th12 08, 2025 lúc 05:31 PM
-- Phiên bản máy phục vụ: 10.4.28-MariaDB
-- Phiên bản PHP: 8.1.17

DROP
    DATABASE IF EXISTS coffeeShop;
CREATE DATABASE coffeeShop CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; USE
    coffeeShop;
SET NAMES
    'utf8mb4';

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Cơ sở dữ liệu: `coffeeShop`
--

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `bangChamCong`
--

CREATE TABLE `bangChamCong` (
  `idChamCong` bigint(20) NOT NULL,
  `idNhanVien` int(11) NOT NULL,
  `gioVao` datetime NOT NULL,
  `gioRa` datetime DEFAULT NULL,
  `soGioCong` decimal(5,2) DEFAULT 0.00,
  `tongGioLam` decimal(5,2) DEFAULT 0.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `bangChamCong`
--

INSERT INTO `bangChamCong` (`idChamCong`, `idNhanVien`, `gioVao`, `gioRa`, `soGioCong`, `tongGioLam`) VALUES
(1, 2, '2025-12-04 02:06:45', '2025-12-04 03:58:58', 1.87, 1.87),
(2, 4, '2025-12-04 02:06:45', '2025-12-04 03:58:58', 1.87, 1.87),
(3, 1, '2025-12-04 02:06:51', '2025-12-04 03:59:09', 1.87, 1.87),
(4, 1, '2025-12-08 22:44:21', '2025-12-08 23:26:02', 0.69, 0.69),
(5, 2, '2025-12-08 22:44:39', '2025-12-08 23:23:31', 0.65, 0.65);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `chiTietHoaDon`
--

CREATE TABLE `chiTietHoaDon` (
  `idHoaDon` bigint(20) NOT NULL,
  `idSanPham` int(11) NOT NULL,
  `soLuong` int(11) DEFAULT NULL,
  `donGia` decimal(10,2) DEFAULT NULL,
  `thueVAT` decimal(5,2) DEFAULT NULL,
  `idNganHang` int(11) DEFAULT NULL,
  `thanhTien` decimal(12,2) GENERATED ALWAYS AS (`soLuong` * `donGia` * (1 + `thueVAT` / 100)) STORED,
  `isActive` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `chiTietHoaDon`
--

INSERT INTO `chiTietHoaDon` (`idHoaDon`, `idSanPham`, `soLuong`, `donGia`, `thueVAT`, `idNganHang`, `isActive`) VALUES
(11, 1, 2, 25000.00, 10.00, NULL, 1),
(12, 1, 2, 25000.00, 10.00, NULL, 1),
(12, 7, 1, 45000.00, 10.00, NULL, 1),
(12, 8, 1, 45000.00, 10.00, NULL, 1),
(12, 9, 1, 40000.00, 10.00, NULL, 1),
(12, 11, 1, 40000.00, 10.00, NULL, 1),
(12, 12, 1, 50000.00, 10.00, NULL, 1),
(12, 13, 4, 30000.00, 10.00, NULL, 1),
(12, 14, 3, 35000.00, 10.00, NULL, 1),
(13, 1, 3, 25000.00, 10.00, NULL, 1),
(14, 1, 1, 25000.00, 10.00, NULL, 1),
(14, 2, 3, 29000.00, 10.00, NULL, 1),
(14, 10, 1, 35000.00, 10.00, NULL, 1),
(14, 11, 1, 40000.00, 10.00, NULL, 1),
(15, 1, 4, 25000.00, 10.00, NULL, 1),
(15, 2, 1, 29000.00, 10.00, NULL, 1),
(15, 4, 1, 30000.00, 10.00, NULL, 1),
(15, 7, 1, 45000.00, 10.00, NULL, 1),
(16, 1, 2, 25000.00, 10.00, NULL, 1),
(17, 11, 3, 40000.00, 10.00, NULL, 1);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `chiTietSanPham`
--

CREATE TABLE `chiTietSanPham` (
  `idSanPham` int(11) NOT NULL,
  `idNguyenLieu` int(11) NOT NULL,
  `soLuongCan` decimal(10,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `chiTietSanPham`
--

INSERT INTO `chiTietSanPham` (`idSanPham`, `idNguyenLieu`, `soLuongCan`) VALUES
(1, 1, 20.00),
(1, 14, 10.00),
(2, 1, 20.00),
(2, 4, 0.20),
(7, 6, 5.00),
(7, 9, 0.25),
(12, 4, 0.10),
(12, 12, 0.20);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `chucVu`
--

CREATE TABLE `chucVu` (
  `idChucVu` int(11) NOT NULL,
  `tenChucVu` varchar(100) NOT NULL,
  `luongCoBan` decimal(10,2) DEFAULT 0.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `chucVu`
--

INSERT INTO `chucVu` (`idChucVu`, `tenChucVu`, `luongCoBan`) VALUES
(1, 'Quản Lý Cửa Hàng', 15000000.00),
(2, 'Pha Chế Trưởng', 9000000.00),
(3, 'Pha Chế Viên', 7000000.00),
(4, 'Phục Vụ', 5500000.00),
(5, 'Thu Ngân', 6000000.00),
(6, 'Bảo Vệ', 5000000.00);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `danhMuc`
--

CREATE TABLE `danhMuc` (
  `idDanhMuc` int(11) NOT NULL,
  `tenDanhMuc` varchar(100) DEFAULT NULL,
  `ghiChu` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `danhMuc`
--

INSERT INTO `danhMuc` (`idDanhMuc`, `tenDanhMuc`, `ghiChu`) VALUES
(1, 'Cà Phê Truyền Thống', 'Đậm đà hương vị Việt'),
(2, 'Cà Phê Máy (Italian)', 'Espresso, Latte, Capuchino'),
(3, 'Trà Trái Cây', 'Thanh mát giải nhiệt'),
(4, 'Trà Sữa', 'Thơm ngon béo ngậy'),
(5, 'Sinh Tố & Đá Xay', 'Healthy và Mát lạnh');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `hoaDon`
--

CREATE TABLE `hoaDon` (
  `idHoaDon` bigint(20) NOT NULL,
  `noiDungCK` varchar(50) DEFAULT NULL,
  `ngayTao` timestamp NOT NULL DEFAULT current_timestamp(),
  `ngayCapNhat` timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  `trangThai` tinyint(4) DEFAULT 1,
  `tongTien` decimal(12,2) DEFAULT NULL,
  `idNhanVien` int(11) DEFAULT NULL,
  `idKhachHang` int(11) DEFAULT NULL,
  `idBan` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `hoaDon`
--

INSERT INTO `hoaDon` (`idHoaDon`,`noiDungCK`, `ngayTao`, `ngayCapNhat`, `trangThai`, `tongTien`, `idNhanVien`, `idKhachHang`, `idBan`) VALUES
(11,NULL, '2025-12-03 20:00:54', NULL, 2, 55000.00, 1, NULL, NULL),
(12,NULL, '2025-12-03 21:01:20', NULL, 2, 544500.00, 1, 7, NULL),
(13,NULL, '2025-12-04 09:09:17', NULL, 2, 82500.00, 1, NULL, NULL),
(14,NULL, '2025-12-04 10:28:40', NULL, 2, 205700.00, 1, NULL, NULL),
(15,NULL, '2025-12-04 10:49:07', NULL, 2, 224400.00, 1, 7, NULL),
(16,NULL, '2025-12-04 10:50:11', NULL, 2, 55000.00, 1, NULL, NULL),
(17,NULL, '2025-12-04 10:50:45', NULL, 2, 132000.00, 1, NULL, NULL);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `khachHang`
--

CREATE TABLE `khachHang` (
  `idKhachHang` int(11) NOT NULL,
  `hoTen` varchar(100) DEFAULT NULL,
  `soDienThoai` varchar(15) DEFAULT NULL,
  `ngaySinh` date DEFAULT NULL,
  `diemTichLuy` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `khachHang`
--

INSERT INTO `khachHang` (`idKhachHang`, `hoTen`, `soDienThoai`, `ngaySinh`, `diemTichLuy`) VALUES
(1, 'Khách Ngoài', NULL, '2000-01-01', 0),
(2, 'Nguyễn Văn An', '0912345678', '1995-05-20', 150),
(3, 'Trần Thị Bích', '0987654321', '1998-11-11', 330),
(4, 'Lê Hoàng Nam', '0901122334', '2000-01-01', 50),
(5, 'Phạm Minh Tuấn', '0933445566', '1990-08-15', 810),
(6, 'Đỗ Thị Hồng', '0977889900', '1999-12-25', 120),
(7, 'huy', '0339761204', '2004-09-24', 50);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `khoNguyenLieu`
--

CREATE TABLE `khoNguyenLieu` (
  `idNguyenLieu` int(11) NOT NULL,
  `tenNguyenLieu` varchar(255) DEFAULT NULL,
  `giaNhap` decimal(10,2) DEFAULT NULL,
  `soLuongTon` decimal(10,2) DEFAULT NULL,
  `donViTinh` varchar(50) DEFAULT NULL,
  `ngayNhap` date DEFAULT NULL,
  `isActive` tinyint(1) DEFAULT 1,
  `idNhaCungCap` int(11) DEFAULT NULL,
  `idNhanVien` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `khoNguyenLieu`
--

INSERT INTO `khoNguyenLieu` (`idNguyenLieu`, `tenNguyenLieu`, `giaNhap`, `soLuongTon`, `donViTinh`, `ngayNhap`, `isActive`, `idNhaCungCap`, `idNhanVien`) VALUES
(1, 'Hạt Cafe Robusta', 200000.00, 10000.00, 'gram', '2025-12-03', 1, 1, 1),
(2, 'Hạt Cafe Arabica', 350000.00, 5000.00, 'gram', '2025-12-03', 1, 1, 1),
(3, 'Sữa Tươi Thanh Trùng', 32000.00, 50000.00, 'ml', '2025-12-03', 1, 2, 1),
(4, 'Sữa Đặc Ngôi Sao', 22000.00, 100.00, 'hop', '2025-12-03', 1, 2, 1),
(5, 'Sữa Chua Có Đường', 6000.00, 200.00, 'hop', '2025-12-03', 1, 2, 1),
(6, 'Trà Đen Phúc Long', 120000.00, 3000.00, 'gram', '2025-12-03', 1, 3, 1),
(7, 'Trà Oolong', 250000.00, 2000.00, 'gram', '2025-12-03', 1, 3, 1),
(8, 'Trà Lài', 150000.00, 2000.00, 'gram', '2025-12-03', 1, 3, 1),
(9, 'Đào Ngâm Hộp', 65000.00, 50.00, 'hop', '2025-12-03', 1, 3, 1),
(10, 'Vải Ngâm Hộp', 68000.00, 50.00, 'hop', '2025-12-03', 1, 3, 1),
(11, 'Cam Tươi', 25000.00, 20.00, 'kg', '2025-12-03', 1, 4, 1),
(12, 'Bơ Sáp', 45000.00, 15.00, 'kg', '2025-12-03', 1, 4, 1),
(13, 'Trân Châu Đen', 40000.00, 5000.00, 'gram', '2025-12-03', 1, 3, 1),
(14, 'Đường Cát', 18000.00, 10000.00, 'gram', '2025-12-03', 1, 3, 1),
(15, 'Bột Cacao', 150000.00, 2000.00, 'gram', '2025-12-03', 1, 3, 1),
(16, 'gừng', 5000.00, 100.00, 'kg', '2025-12-04', 1, 4, 1);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `luong`
--

CREATE TABLE `luong` (
  `idNhanVien` int(11) NOT NULL,
  `idChamCong` bigint(20) NOT NULL,
  `luongNV` decimal(12,2) NOT NULL,
  `soGioCong` decimal(5,2) NOT NULL,
  `tongLuong` decimal(12,2) NOT NULL,
  `ttThanhToan` enum('ChuaThanhToan','DaThanhToan') DEFAULT 'ChuaThanhToan'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `nganHang`
--

CREATE TABLE `nganHang` (
  `idNganHang` int(11) NOT NULL,
  `maNganHang` varchar(20) DEFAULT NULL,
  `tenNganHang` varchar(100) DEFAULT NULL,
  `soTaiKhoan` varchar(50) DEFAULT NULL,
  `tenTaiKhoan` varchar(100) DEFAULT NULL,
  `isActive` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `nganHang`
--

INSERT INTO `nganHang` (`idNganHang`, `maNganHang`, `tenNganHang`, `soTaiKhoan`, `tenTaiKhoan`, `isActive`) VALUES
(1, 'VCB', 'Vietcombank', '999988886666', 'COFFEE HOUSE', 0),
(2, 'MB', 'MB Bank', '111122223333', 'NGUYEN THANH DAT', 0),
(3, 'MOMO', 'Ví MoMo', '0909111222', 'NGUYEN THANH DAT', 0),
(4, 'MB', 'MB Bank', '0339761204', 'VU VAN HUY', 1);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `nhaCungCap`
--

CREATE TABLE `nhaCungCap` (
  `idNhaCungCap` int(11) NOT NULL,
  `tenNhaCungCap` varchar(255) DEFAULT NULL,
  `soDienThoai` varchar(15) DEFAULT NULL,
  `diaChi` text DEFAULT NULL,
  `ngayCapNhat` date DEFAULT NULL,
  `isActive` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `nhaCungCap`
--

INSERT INTO `nhaCungCap` (`idNhaCungCap`, `tenNhaCungCap`, `soDienThoai`, `diaChi`, `ngayCapNhat`, `isActive`) VALUES
(1, 'Trung Nguyên Legend', '0283111222', 'Cung cấp Cà phê hạt, bột', NULL, 1),
(2, 'Vinamilk Pro', '1900123456', 'Cung cấp Sữa tươi, Sữa đặc, Sữa chua', NULL, 1),
(3, 'Nguyên Liệu Pha Chế Việt', '0901234567', 'Cung cấp Syrup, Bột kem, Trà', NULL, 1),
(4, 'Nông Sản Sạch Đà Lạt', '0633888999', 'Cung cấp Trái cây tươi (Bơ, Dâu, Cam)', NULL, 1),
(5, 'Bao Bì Xanh', '0289999888', 'Cung cấp Ly, Ống hút, Túi đựng', NULL, 1);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `nhanVien`
--

CREATE TABLE `nhanVien` (
  `idNhanVien` int(11) NOT NULL,
  `hoTen` varchar(100) NOT NULL,
  `soDienThoai` varchar(15) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `ngayTao` timestamp NOT NULL DEFAULT current_timestamp(),
  `ngayCapNhat` timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  `trangThaiLamViec` enum('DangLamViec','DaNghiViec') DEFAULT 'DangLamViec',
  `phanQuyen` enum('nhanVien','admin') DEFAULT 'nhanVien',
  `idChucVu` int(11) NOT NULL,
  `idTaiKhoan` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `nhanVien`
--

INSERT INTO `nhanVien` (`idNhanVien`, `hoTen`, `soDienThoai`, `email`, `ngayTao`, `ngayCapNhat`, `trangThaiLamViec`, `phanQuyen`, `idChucVu`, `idTaiKhoan`) VALUES
(1, 'Nguyễn Thành Đạt', '0909111222', 'dat.admin@coffee.com', '2025-12-03 16:30:10', '2025-12-04 10:40:42', 'DangLamViec', 'admin', 1, 1),
(2, 'Lê Thị Thanh Hương', '0909333444', 'huong.barista@coffee.com', '2025-12-03 16:30:10', NULL, 'DangLamViec', 'nhanVien', 2, 2),
(3, 'Trần Văn Tính', '0909555666', 'tinh.cashier@coffee.com', '2025-12-03 16:30:10', NULL, 'DangLamViec', 'nhanVien', 5, 3),
(4, 'Phạm Quỳnh Anh', '0909777888', 'anh.pv@coffee.com', '2025-12-03 16:30:10', NULL, 'DangLamViec', 'nhanVien', 4, 4),
(5, 'Võ Văn Hùng', '0909999000', 'hung.bv@coffee.com', '2025-12-03 16:30:10', '2025-12-08 16:03:27', 'DangLamViec', 'nhanVien', 6, NULL);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `sanPham`
--

CREATE TABLE `sanPham` (
  `idSanPham` int(11) NOT NULL,
  `tenSanPham` varchar(255) DEFAULT NULL,
  `moTa` text DEFAULT NULL,
  `giaBan` decimal(10,2) DEFAULT NULL,
  `hinhAnhUrl` text DEFAULT NULL,
  `isActive` tinyint(1) DEFAULT 1,
  `idDanhMuc` int(11) DEFAULT NULL,
  `idNguyenLieu` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `sanPham`
--

INSERT INTO `sanPham` (`idSanPham`, `tenSanPham`, `moTa`, `giaBan`, `hinhAnhUrl`, `isActive`, `idDanhMuc`, `idNguyenLieu`) VALUES
(1, 'Cà Phê Đen Đá', 'Cafe Robusta đậm đặc', 25000.00, 'src/images/ca-phe-den-da_1764843847.png', 1, 1, 1),
(2, 'Cà Phê Sữa Đá', 'Robusta kết hợp sữa đặc', 29000.00, 'src/images/Ca_Phe_Sua_Da_1764843793.jpg', 1, 1, 1),
(3, 'Bạc Xỉu', 'Nhiều sữa ít cafe', 35000.00, 'src/images/Bac-xiu-la-gi-nguon-goc-va-cach-lam-bac-xiu-thom-ngon-don-gian-tai-nha-5-800x529_1764843101.jpg', 1, 1, 4),
(4, 'Espresso', 'Chiết xuất máy nguyên chất', 30000.00, 'src/images/ca-phe-espresso-cappuccino-hay-macchiato-khac-nhau-nhu-the-nao-202004081936305660_1764843012.jpg', 1, 2, 2),
(5, 'Latte Nóng', 'Cafe và sữa tươi nóng', 45000.00, 'src/images/cach-pha-matcha-latte-nong_1764842914.jpg', 1, 2, 2),
(6, 'Capuchino', 'Bọt sữa bồng bềnh', 45000.00, 'src/images/capuchino_1764842850.jpg', 1, 2, 2),
(7, 'Trà Đào Cam Sả', 'Best seller', 45000.00, 'src/images/tra-dao-cam-sa_1764842724.jpg', 1, 3, 9),
(8, 'Trà Vải Nhiệt Đới', 'Hương vải thơm lừng', 45000.00, 'src/images/bat-trend-mua-he-bang-mon-tra-vai-nhiet-doi-thom-ngon-mat-lanh71_1764842679.jpg', 1, 3, 10),
(9, 'Lục Trà Cam Vàng', 'Trà lài kết hợp cam tươi', 40000.00, 'src/images/images_1764842615.jpeg', 1, 3, 11),
(10, 'Trà Sữa Truyền Thống', 'Đậm vị trà đen', 35000.00, 'src/images/hoc-cach-pha-tra-sua-o-long-dai-loan-thom-ngon-chuan-vi-ai-cung-me-202108100039248020_1764842567.jpg', 1, 4, 6),
(11, 'Trà Sữa Oolong', 'Thơm nồng nàn', 40000.00, 'src/images/o3_f14456eb3eb445f29cc9ee3f8e35e7a8_grande_1764842180.jpg', 1, 4, 7),
(12, 'Sinh Tố Bơ', 'Bơ sáp dẻo mịn', 50000.00, 'src/images/Untitled_1764842478.jpeg', 1, 5, 12),
(13, 'Sữa Chua Đánh Đá', 'Chua ngọt mát lạnh', 30000.00, 'src/images/2-2_1764842255.jpeg', 1, 5, 5),
(14, 'Trà Gừng', NULL, 35000.00, 'src/images/tragunggmoi-16922725817611373758535_1764842033.jpg', 1, 3, 16);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `taiKhoanNhanVien`
--

CREATE TABLE `taiKhoanNhanVien` (
  `idTaiKhoan` int(11) NOT NULL,
  `tenDangNhap` varchar(50) NOT NULL,
  `matKhauHash` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `taiKhoanNhanVien`
--

INSERT INTO `taiKhoanNhanVien` (`idTaiKhoan`, `tenDangNhap`, `matKhauHash`) VALUES
(1, 'admin', 'e10adc3949ba59abbe56e057f20f883e'),
(2, 'barista_truong', 'e10adc3949ba59abbe56e057f20f883e'),
(3, 'thu_ngan', 'e10adc3949ba59abbe56e057f20f883e'),
(4, 'phuc_vu', 'e10adc3949ba59abbe56e057f20f883e');

--
-- Chỉ mục cho các bảng đã đổ
--

--
-- Chỉ mục cho bảng `bangChamCong`
--
ALTER TABLE `bangChamCong`
  ADD PRIMARY KEY (`idChamCong`),
  ADD KEY `idNhanVien` (`idNhanVien`);

--
-- Chỉ mục cho bảng `chiTietHoaDon`
--
ALTER TABLE `chiTietHoaDon`
  ADD PRIMARY KEY (`idHoaDon`,`idSanPham`),
  ADD KEY `idSanPham` (`idSanPham`),
  ADD KEY `idNganHang` (`idNganHang`);

--
-- Chỉ mục cho bảng `chiTietSanPham`
--
ALTER TABLE `chiTietSanPham`
  ADD PRIMARY KEY (`idSanPham`,`idNguyenLieu`),
  ADD KEY `idNguyenLieu` (`idNguyenLieu`);

--
-- Chỉ mục cho bảng `chucVu`
--
ALTER TABLE `chucVu`
  ADD PRIMARY KEY (`idChucVu`),
  ADD UNIQUE KEY `tenChucVu` (`tenChucVu`);

--
-- Chỉ mục cho bảng `danhMuc`
--
ALTER TABLE `danhMuc`
  ADD PRIMARY KEY (`idDanhMuc`);

--
-- Chỉ mục cho bảng `hoaDon`
--
ALTER TABLE `hoaDon`
  ADD PRIMARY KEY (`idHoaDon`),
  ADD KEY `idNhanVien` (`idNhanVien`),
  ADD KEY `idKhachHang` (`idKhachHang`);

--
-- Chỉ mục cho bảng `khachHang`
--
ALTER TABLE `khachHang`
  ADD PRIMARY KEY (`idKhachHang`);

--
-- Chỉ mục cho bảng `khoNguyenLieu`
--
ALTER TABLE `khoNguyenLieu`
  ADD PRIMARY KEY (`idNguyenLieu`),
  ADD KEY `idNhaCungCap` (`idNhaCungCap`),
  ADD KEY `idNhanVien` (`idNhanVien`);

--
-- Chỉ mục cho bảng `luong`
--
ALTER TABLE `luong`
  ADD PRIMARY KEY (`idNhanVien`,`idChamCong`),
  ADD KEY `idChamCong` (`idChamCong`);

--
-- Chỉ mục cho bảng `nganHang`
--
ALTER TABLE `nganHang`
  ADD PRIMARY KEY (`idNganHang`);

--
-- Chỉ mục cho bảng `nhaCungCap`
--
ALTER TABLE `nhaCungCap`
  ADD PRIMARY KEY (`idNhaCungCap`);

--
-- Chỉ mục cho bảng `nhanVien`
--
ALTER TABLE `nhanVien`
  ADD PRIMARY KEY (`idNhanVien`),
  ADD UNIQUE KEY `soDienThoai` (`soDienThoai`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `idTaiKhoan` (`idTaiKhoan`),
  ADD KEY `idChucVu` (`idChucVu`);

--
-- Chỉ mục cho bảng `sanPham`
--
ALTER TABLE `sanPham`
  ADD PRIMARY KEY (`idSanPham`),
  ADD KEY `idDanhMuc` (`idDanhMuc`),
  ADD KEY `idNguyenLieu` (`idNguyenLieu`);

--
-- Chỉ mục cho bảng `taiKhoanNhanVien`
--
ALTER TABLE `taiKhoanNhanVien`
  ADD PRIMARY KEY (`idTaiKhoan`),
  ADD UNIQUE KEY `tenDangNhap` (`tenDangNhap`);

--
-- AUTO_INCREMENT cho các bảng đã đổ
--

--
-- AUTO_INCREMENT cho bảng `bangChamCong`
--
ALTER TABLE `bangChamCong`
  MODIFY `idChamCong` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT cho bảng `chucVu`
--
ALTER TABLE `chucVu`
  MODIFY `idChucVu` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT cho bảng `danhMuc`
--
ALTER TABLE `danhMuc`
  MODIFY `idDanhMuc` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT cho bảng `hoaDon`
--
ALTER TABLE `hoaDon`
  MODIFY `idHoaDon` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT cho bảng `khachHang`
--
ALTER TABLE `khachHang`
  MODIFY `idKhachHang` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT cho bảng `khoNguyenLieu`
--
ALTER TABLE `khoNguyenLieu`
  MODIFY `idNguyenLieu` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT cho bảng `nganHang`
--
ALTER TABLE `nganHang`
  MODIFY `idNganHang` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT cho bảng `nhaCungCap`
--
ALTER TABLE `nhaCungCap`
  MODIFY `idNhaCungCap` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT cho bảng `nhanVien`
--
ALTER TABLE `nhanVien`
  MODIFY `idNhanVien` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT cho bảng `sanPham`
--
ALTER TABLE `sanPham`
  MODIFY `idSanPham` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT cho bảng `taiKhoanNhanVien`
--
ALTER TABLE `taiKhoanNhanVien`
  MODIFY `idTaiKhoan` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Các ràng buộc cho các bảng đã đổ
--

--
-- Các ràng buộc cho bảng `bangChamCong`
--
ALTER TABLE `bangChamCong`
  ADD CONSTRAINT `bangchamcong_ibfk_1` FOREIGN KEY (`idNhanVien`) REFERENCES `nhanVien` (`idNhanVien`) ON DELETE CASCADE;

--
-- Các ràng buộc cho bảng `chiTietHoaDon`
--
ALTER TABLE `chiTietHoaDon`
  ADD CONSTRAINT `chitiethoadon_ibfk_1` FOREIGN KEY (`idHoaDon`) REFERENCES `hoaDon` (`idHoaDon`) ON DELETE CASCADE,
  ADD CONSTRAINT `chitiethoadon_ibfk_2` FOREIGN KEY (`idSanPham`) REFERENCES `sanPham` (`idSanPham`),
  ADD CONSTRAINT `chitiethoadon_ibfk_3` FOREIGN KEY (`idNganHang`) REFERENCES `nganHang` (`idNganHang`);

--
-- Các ràng buộc cho bảng `chiTietSanPham`
--
ALTER TABLE `chiTietSanPham`
  ADD CONSTRAINT `chitietsanpham_ibfk_1` FOREIGN KEY (`idSanPham`) REFERENCES `sanPham` (`idSanPham`),
  ADD CONSTRAINT `chitietsanpham_ibfk_2` FOREIGN KEY (`idNguyenLieu`) REFERENCES `khoNguyenLieu` (`idNguyenLieu`);

--
-- Các ràng buộc cho bảng `hoaDon`
--
ALTER TABLE `hoaDon`
  ADD CONSTRAINT `hoadon_ibfk_1` FOREIGN KEY (`idNhanVien`) REFERENCES `nhanVien` (`idNhanVien`),
  ADD CONSTRAINT `hoadon_ibfk_2` FOREIGN KEY (`idKhachHang`) REFERENCES `khachHang` (`idKhachHang`);

--
-- Các ràng buộc cho bảng `khoNguyenLieu`
--
ALTER TABLE `khoNguyenLieu`
  ADD CONSTRAINT `khonguyenlieu_ibfk_1` FOREIGN KEY (`idNhaCungCap`) REFERENCES `nhaCungCap` (`idNhaCungCap`),
  ADD CONSTRAINT `khonguyenlieu_ibfk_2` FOREIGN KEY (`idNhanVien`) REFERENCES `nhanVien` (`idNhanVien`);

--
-- Các ràng buộc cho bảng `luong`
--
ALTER TABLE `luong`
  ADD CONSTRAINT `luong_ibfk_1` FOREIGN KEY (`idNhanVien`) REFERENCES `nhanVien` (`idNhanVien`),
  ADD CONSTRAINT `luong_ibfk_2` FOREIGN KEY (`idChamCong`) REFERENCES `bangChamCong` (`idChamCong`) ON DELETE CASCADE;

--
-- Các ràng buộc cho bảng `nhanVien`
--
ALTER TABLE `nhanVien`
  ADD CONSTRAINT `nhanvien_ibfk_1` FOREIGN KEY (`idChucVu`) REFERENCES `chucVu` (`idChucVu`),
  ADD CONSTRAINT `nhanvien_ibfk_2` FOREIGN KEY (`idTaiKhoan`) REFERENCES `taiKhoanNhanVien` (`idTaiKhoan`) ON DELETE SET NULL;

--
-- Các ràng buộc cho bảng `sanPham`
--
ALTER TABLE `sanPham`
  ADD CONSTRAINT `sanpham_ibfk_1` FOREIGN KEY (`idDanhMuc`) REFERENCES `danhMuc` (`idDanhMuc`),
  ADD CONSTRAINT `sanpham_ibfk_2` FOREIGN KEY (`idNguyenLieu`) REFERENCES `khoNguyenLieu` (`idNguyenLieu`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
