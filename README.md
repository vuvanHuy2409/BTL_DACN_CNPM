# Các con của bố đọc cho kĩ vào nha
Link Repository: [https://github.com/vuvanHuy2409/BTL_DACN_CNPM](https://github.com/vuvanHuy2409/BTL_DACN_CNPM)

---

## CÁCH 1: Đẩy Code lên Git lần đầu (Upload)
1. Mở Terminal tại thư mục dự án.
2. Khởi tạo Git:
   ```bash
   git init
3. Kết nối với Server (GitHub):
   ```bash
    git remote add origin [https://github.com/vuvanHuy2409/BTL_DACN_CNPM.git](https://github.com/vuvanHuy2409/BTL_DACN_CNPM.git)
    git add .
    git commit -m "Khoi tao du an"
    git push -u origin main
4.  Tải về lần đầu: Chỉ làm 1 lần duy nhất khi máy chưa có code.

    ```Bash
    git clone [https://github.com/vuvanHuy2409/BTL_DACN_CNPM.git](https://github.com/vuvanHuy2409/BTL_DACN_CNPM.git)
    cd BTL_DACN_CNPM
5.  Quy trình Code hàng ngày (Quan trọng)
* Bước 1: Cập nhật code mới (Pull)

    ```Bash
    git pull origin main
(Luôn làm bước này đầu tiên khi bật máy)

*   Bước 2: Code và lưu thay đổi (Commit)

    ```Bash
    git add .
    git commit -m "Mô tả ngắn gọn việc đã làm"
* Bước 3: Đẩy lên (Push)
    ```Bash
    git push origin main
---
Tự động tải code (Auto Pull)
---
Dành cho mấy thằng lười

1.  Dành cho Windows (File .bat)

Tạo file 'auto_update.bat' trong thư mục dự án với nội dung:

    ```bash
    @echo off
    :loop
    echo Dang kiem tra va tai code moi...
    git pull origin main
    :: Doi 60 giay (co the chinh sua so nay)
    timeout /t 60
    goto loop
-> Cách dùng: Click đúp vào file này, nó sẽ chạy ngầm và update mỗi 60s.

2.  Dành cho MacOS / Linux (File .sh)

Tạo file "auto_update.sh" trong thư mục dự án với nội dung:

    ```bash
    #!/bin/bash
    while true
    do
        echo "Dang pull code ve..."
        git pull origin main
        # Doi 60 giay
        sleep 60
    done

### Hướng dẫn cập nhật file README này lên Git ngay:

Sau khi lưu nội dung trên vào file `README.md` trong máy bạn, hãy chạy lệnh sau ở Terminal để đưa nó lên GitHub cho mọi người cùng đọc:

```bash
git add README.md
git commit -m "Cap nhat huong dan su dung Git day du"
git push