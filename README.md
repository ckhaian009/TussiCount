# TussiCount

Đánh giá độ tin cậy của phép đếm tiếng ho tự động trên thiết bị biên phục vụ giám sát sớm bệnh hô hấp tại ký túc xá.

Đội LÒ VI SÓNG (Cao Khải An, Nguyễn Phúc Gia Bảo, 12T1, THPT FPT Cần Thơ) · GVHD: cô Trương Minh Phương · STEMPETITION 2026–2027, tiểu ban Nghiên cứu khoa học, Challenge 2 – Healthy Living.

Thiết bị chạy bản firmware vận hành **không lưu âm thanh**: âm thanh chỉ nằm khoảng 1 giây trong bộ nhớ tạm để phân loại rồi bị ghi đè; thiết bị chỉ ghi thời điểm và số lần ho. Mã nguồn công khai ở đây để ai cũng kiểm tra được.

## Cấu trúc kho

| Thư mục | Nội dung |
| --- | --- |
| `protocol/` | Protocol đăng ký trước (commit trước 10/11/2026) |
| `firmware/` | Bản kiểm định và bản vận hành, tách riêng |
| `tools/` | Công cụ thí nghiệm, mỗi công cụ kèm phép thử kiểm chứng |
| `ai-logs/` | Minh chứng Vibe Coding, nhật ký kiểm chứng |
| `results/` | Kết quả, danh sách dữ liệu đã chọn; không chứa âm thanh |

Thư mục `data/` và mọi file âm thanh không bao giờ được đưa lên GitHub (đã chặn trong `.gitignore`).

## Dữ liệu mở sử dụng

| Bộ dữ liệu | Dùng để | Phần đã dùng | Giấy phép | Nguồn |
| --- | --- | --- | --- | --- |
| COUGHVID v3.0 | Huấn luyện (tiếng ho) | 3.000 bản ghi `cough_detected` ≥ 0,8, chọn ngẫu nhiên (hạt giống 2026); danh sách: `results/coughvid_chon_3000.csv` | CC BY 4.0 | Orlandic, Teijeiro & Atienza (2021). *Scientific Data* 8, 156. https://zenodo.org/records/7024894 |
| Coswara | Phát lại ở tầng 1 (không dùng khi huấn luyện) | 1.100 tiếng ho chất lượng 2 của 714 người, từ 4 thư mục ngày; danh sách: `results/coswara_playlist.csv` | CC BY 4.0 | Bhattacharya và cộng sự (2023). *Scientific Data* 10, 397. https://github.com/iiscleap/Coswara-Data |
| ESC-50 | Huấn luyện (âm thanh không phải ho) | 1.960 đoạn, đã bỏ lớp `coughing` | CC BY-NC 3.0 | Piczak, K. J. (2015). ESC: Dataset for Environmental Sound Classification. *ACM Multimedia*. https://github.com/karolpiczak/ESC-50 |
| Common Voice Scripted Speech 27.0 – Vietnamese | Huấn luyện (tiếng nói tiếng Việt) | 1.000 đoạn đã xác thực của 229 người (hạt giống 2026) | CC0 1.0 | Mozilla Common Voice, qua Mozilla Data Collective. https://mozilladatacollective.com |

## Mô hình

Huấn luyện trên Edge Impulse: cửa sổ 1.000 ms, bước trượt 500 ms, khối MFE, mạng phân loại nhỏ, lượng tử hoá int8, chạy trên ESP32-S3.
