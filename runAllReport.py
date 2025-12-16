import unittest
import HtmlTestRunner
import os
import sys
import time

# ==============================================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN (QUAN TRỌNG)
# Giúp script nhìn thấy thư mục 'src' dù chạy ở bất kỳ môi trường nào
# ==============================================================================
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def main():
    print("=" * 60)
    print("HỆ THỐNG KIỂM THỬ TỰ ĐỘNG - COFFEE SHOP MANAGER")
    print(f"Đang khởi tạo tại: {project_root}")
    print("=" * 60)

    # 2. XÁC ĐỊNH THƯ MỤC CHỨA TEST
    # Đường dẫn: Project_Root/src/test/unitTest
    test_dir = os.path.join(project_root, 'src', 'test', 'unitTest')

    if not os.path.exists(test_dir):
        print(f"LỖI: Không tìm thấy thư mục test tại: {test_dir}")
        print("Hãy kiểm tra lại cấu trúc thư mục!")
        return

    # 3. TỰ ĐỘNG TÌM KIẾM (TEST DISCOVERY)
    # Tìm tất cả file có tên bắt đầu bằng "test" và đuôi ".py"
    loader = unittest.TestLoader()
    print(f"--> Đang quét các file test trong: {test_dir} ...")

    try:
        suite = loader.discover(start_dir=test_dir, pattern='test*.py')
    except Exception as e:
        print(f"Lỗi khi quét file test: {e}")
        return

    # Kiểm tra xem có tìm thấy test nào không
    if suite.countTestCases() == 0:
        print("CẢNH BÁO: Không tìm thấy Test Case nào!")
        return
    else:
        print(f"--> Đã tìm thấy tổng cộng: {suite.countTestCases()} test cases.")

    # 4. CẤU HÌNH THƯ MỤC XUẤT BÁO CÁO
    report_folder = os.path.join(project_root, "test_reports")
    if not os.path.exists(report_folder):
        os.makedirs(report_folder)
        print(f"--> Đã tạo thư mục báo cáo: {report_folder}")

    # 5. CHẠY TEST VÀ XUẤT HTML
    print("\nĐang thực thi kiểm thử... Vui lòng chờ giây lát...")

    # Tạo tiêu đề báo cáo có ngày giờ
    timestamp = time.strftime("%d-%m-%Y %H:%M:%S")

    runner = HtmlTestRunner.HTMLTestRunner(
        output=report_folder,
        report_name="Bao_Cao_Kiem_Thu_Tong_Hop",
        report_title=f"KẾT QUẢ KIỂM THỬ PHẦN MỀM QUẢN LÝ QUÁN CÀ PHÊ",
        descriptions=f"Thời gian chạy: {timestamp}. Bao gồm các module: Đăng nhập, Nhân viên, Kho, Hóa đơn, Lương, Tài khoản...",
        combine_reports=True,  # Gom tất cả vào 1 file duy nhất
        add_timestamp=True,  # Thêm timestamp vào tên file
        open_in_browser=True  # Tự động mở trình duyệt khi xong (chỉ hoạt động trên một số OS)
    )

    runner.run(suite)
    print("=" * 60)
    print(f"HOÀN TẤT! Kiểm tra thư mục '{report_folder}' để xem báo cáo.")
    print("=" * 60)


if __name__ == '__main__':
    main()