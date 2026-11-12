# firmware

| Thư mục | Thiết bị | Nội dung |
| --- | --- | --- |
| `van_hanh/TC01_Van_hanh/` | TC-01 (ESP32-S3 N16R8), tầng 1 | Bản vận hành: chấm v1 + v2, gộp sự kiện, nhật ký mỗi phút. **Không có hàm ghi âm thanh.** |
| `ghi_kiem_dinh/TC02_Ghi_kiem_dinh/` | TC-02 (ESP32 thường), tầng 2 | Bản kiểm định: ghi WAV 16 kHz chỉ trong khung giờ đã thông báo, có LED báo ghi. |
| `kiem_tra/` | cả hai | Bài kiểm tra phần cứng T1–T5 (T1–T4 cho ESP32-S3; T5 tự chọn chân theo loại mạch). |
| `so_do_mach/` | cả hai | Sơ đồ mạch và bảng nối dây bản 2.0 (PDF 4 trang, PNG, SVG) và mã tạo sơ đồ `tao_so_do.py`. |

Thay đổi phần cứng và firmware sau khi đăng ký protocol: xem Protocol 16.14–16.17. Phiên bản firmware, mô hình, ngưỡng và cấu hình thư viện được đóng băng ngày 14/11 12:00 (mục 10, 12).
