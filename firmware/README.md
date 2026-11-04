# firmware

Mã chạy trên ESP32-S3, tách thành hai bản riêng:

- `kiem-dinh/`: bản kiểm định, ghi âm WAV 16 kHz lên thẻ nhớ. Chỉ dùng trong các buổi ghi âm nền đã có đồng thuận và báo trước.
- `van-hanh/`: bản vận hành, **không có hàm ghi file âm thanh**. Chỉ ghi thời điểm, độ dài, điểm tin cậy của sự kiện ho và mức ồn nền mỗi phút.

Ghi rõ phiên bản firmware, mô hình và ngưỡng đã đóng băng ngày 10/11.
