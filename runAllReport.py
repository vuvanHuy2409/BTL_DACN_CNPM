import unittest
import os
import sys
from HtmlTestRunner import HTMLTestRunner  # Import thư viện tạo báo cáo HTML

# 1. Thêm thư mục gốc vào đường dẫn hệ thống
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def run_all_tests():
    print("=" * 60)
    print("🚀 ĐANG KHỞI ĐỘNG HỆ THỐNG KIỂM THỬ (HTML REPORT)")
    print("=" * 60)

    # 2. Định nghĩa đường dẫn
    test_dir = os.path.join(project_root, "src", "test")
    report_dir = os.path.join(project_root, "reports") # Thư mục chứa báo cáo

    # Kiểm tra thư mục test
    if not os.path.exists(test_dir):
        print(f"❌ Lỗi: Không tìm thấy thư mục test tại: {test_dir}")
        return

    # 3. Tìm tất cả các test case
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=test_dir, pattern='test*.py', top_level_dir=project_root)

    count = suite.countTestCases()
    print(f"🔍 Đã tìm thấy tổng cộng: {count} test cases")
    print("-" * 60)

    # 4. Cấu hình HTML Runner
    # - output: Tên thư mục lưu file
    # - report_name: Tên file báo cáo
    # - combine_reports: Gộp tất cả test vào 1 file duy nhất (True)
    # - add_timestamp: Thêm thời gian vào tên file để không bị ghi đè (True)
    runner = HTMLTestRunner(
        output=report_dir,
        report_name="Bao_Cao_Kiem_Thu_BTL",
        report_title="BÁO CÁO KẾT QUẢ KIỂM THỬ TỰ ĐỘNG",
        combine_reports=True,
        add_timestamp=True,
        open_in_browser=True  # Tự động mở trình duyệt sau khi chạy xong
    )

    # 5. Chạy test
    runner.run(suite)

    print("=" * 60)
    print(f"✅ Đã xuất báo cáo HTML tại thư mục: {report_dir}")
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()