# Bài kiểm tra phần cứng T1–T4 (ESP32-S3 N16R8)

Bốn chương trình ngắn để kiểm tra từng phần trước khi nạp firmware chính. Chạy theo thứ tự T1 → T4; bài sau chỉ chạy khi bài trước đạt.

| Bài | Kiểm tra | Đạt khi |
| --- | --- | --- |
| T1_Bo_mach_va_LED | Bo, bộ nhớ, LED báo | Serial in Flash 16 MB, PSRAM khoảng 8 MB; LED nháy 1 lần/giây |
| T2_Micro_INMP441 | Micro qua I2S | Phòng yên tĩnh khoảng −85 đến −70 dBFS; nói ở 30 cm tăng lên khoảng −60 đến −40; vỗ tay gần micro trên −35; LED sáng khi có tiếng to |
| T3_The_nho_SD | Module thẻ, ghi và đọc lại, tốc độ ghi | “KET QUA: DAT”, tốc độ ghi trên 300 KB/s; LED sáng liên tục |
| T4_Ghi_WAV_10_giay | Cả chuỗi micro → ESP32 → thẻ | Tệp T4_000.wav nghe rõ, không rè, không ngắt quãng; báo “khong mat mau” |

Chân nối nằm trong `chan_noi.h` của mỗi bài (giống nhau ở cả 4 bài) và khớp với sơ đồ mạch, bảng nối dây.

## Cài đặt một lần

1. Arduino IDE 2. Vào Boards Manager, cài **esp32 by Espressif Systems**, bản 3.x (đã biên dịch thử cả 4 bài với 3.3.12).
2. Tools:
   - Board: **ESP32S3 Dev Module**
   - Flash Size: **16MB (128Mb)**
   - PSRAM: **OPI PSRAM**
   - Partition Scheme: **16M Flash (3MB APP/9.9MB FATFS)**
   - USB CDC On Boot: **Enabled** nếu cắm vào cổng ghi “USB”; **Disabled** nếu cắm vào cổng ghi “COM” hoặc “UART”
3. Serial Monitor: 115200 baud.

Nạp không được: giữ nút BOOT, bấm nút RST (hoặc EN), thả BOOT, rồi nạp lại.

T4 ghi âm thật: chỉ dùng khi thử trên bàn với giọng của nhóm, nghe xong thì xoá tệp.

Mã do trợ lý AI viết; đã biên dịch không lỗi với Arduino-ESP32 3.3.12 nhưng chưa chạy trên phần cứng. Nhóm ghi kết quả chạy thật vào nhật ký kiểm chứng.
