# TC-02 · Firmware ghi âm kiểm định

Mạch ESP32 thường (ESP-WROOM-32) ghi WAV 16 kHz, 16 bit, 1 kênh cho phần để sửa, phần để chấm và buổi đo âm học (Protocol 7, 16.9, 16.14). Không chạy mô hình. Hệ số khuếch đại ×8 và cách quy đổi mẫu giống TC-01 (16.8), nên tệp WAV chấm trên máy tính cho cùng đầu vào như mô hình trên TC-01.

## Nguyên tắc an toàn dữ liệu

- Mạch **chỉ ghi trong các khung giờ đã thông báo** và chỉ khi đã đồng bộ giờ. Không có nút “ghi ngay” trong KTX; ghi thử 10 phút chỉ dùng trên bàn, nghe xong xoá.
- Tệp WAV **không bao giờ** đưa lên GitHub, Edge Impulse hay dịch vụ trực tuyến; chép từ thẻ sang `~/TussiCount_KTX` trên laptop, xoá toàn bộ ngày 17/11 có biên bản.

| Ngày | Giờ | Nhãn |
| --- | --- | --- |
| 13/11 | 18:15–18:30 | `am_hoc` (đo âm học 16.9, đặt sát TC-01) |
| 13/11 | 19:00–22:00 | `de_sua` |
| 16/11 | 17:55–20:25 | `de_cham_1` |
| 16/11 | 21:50–23:50 | `de_cham_2` |

Lịch nằm trong firmware. Nếu lịch phải đổi, chép tệp `/lich_ghi.txt` (mẫu: `lich_ghi_mau.txt`) ra thẻ; có tệp này thì mạch dùng lịch trong tệp. Mọi thay đổi lịch phải ghi vào mục 16 Protocol và thông báo trước 24 giờ.

## Nối dây

| Linh kiện | Chân linh kiện | Chân ESP32 |
| --- | --- | --- |
| INMP441 | VDD / GND | 3V3 / GND |
| | SCK / WS / SD | G26 / G25 / G33 |
| | L/R | GND |
| Module thẻ | VCC / GND | V5 / GND |
| | CS / MOSI / SCK / MISO | G5 / G23 / G18 / G19 |
| LED báo ghi | (có sẵn trên mạch) | G2; LED ngoài: G2 → 330 Ω → LED → GND |

## Đèn LED

| LED | Ý nghĩa |
| --- | --- |
| Nháy chậm (1 giây) | Chưa có giờ: phải đồng bộ bằng điện thoại, chưa ghi được |
| Tắt | Có giờ, đang chờ khung ghi |
| Sáng liên tục | Đang ghi |
| Nháy, Serial báo “the nho loi” | Trong khung ghi nhưng thẻ lỗi: KHÔNG ghi được |

## Tệp trên thẻ

| Tệp | Nội dung |
| --- | --- |
| `TC-02_YYYYMMDD_HHMMSS.wav` | Âm thanh, tối đa 1 giờ mỗi tệp; tên là giờ Việt Nam của mẫu đầu tiên |
| `THU_YYYYMMDD_HHMMSS.wav` | Ghi thử trên bàn |
| `TC-02_ghi.csv` | Mỗi tệp WAV một dòng: giờ mẫu đầu (epoch, giờ VN), số mẫu, thời lượng, mẫu thiếu đã chèn 0, mẫu chạm đỉnh |
| `TC-02_dong_bo.csv` | Mỗi lần đồng bộ một dòng; `lech_ms` = phần trôi tích luỹ từ lần trước (để hiệu chỉnh bằng `hieu_chinh_troi_gio.py`) |
| `TC-02_khoang_trong.csv` | Chỉ có khi thẻ ghi chậm làm thiếu mẫu: vị trí và số mẫu đã chèn 0 (thời gian vẫn đúng) |

Giờ của mẫu thứ *n* trong tệp = `t_mau_dau_epoch + n / 16000`. Tiêu đề WAV được cập nhật mỗi phút; nếu mất nguồn giữa chừng, tệp vẫn mở được, phần cuối tối đa 1 phút có thể cần sửa tiêu đề.

## Nạp

1. Arduino IDE: File › Open › `Documents/Arduino/TC02_Ghi_kiem_dinh/TC02_Ghi_kiem_dinh.ino` (bản sao để biên dịch; bản gốc ở thư mục này).
2. Tools › Board: **ESP32 Dev Module**; Port: cổng `usbserial` của mạch ESP32 thường. Các mục khác để mặc định.
3. Upload. Mở Serial Monitor 115200: thấy `##### TussiCount TC-02`, `THE: mo o … MHz`, `Lich ghi: … (4 khung)`.

## Đồng bộ giờ

Điện thoại vào Wi-Fi `TussiCount-TC-02` (mật khẩu `tussicount`), mở `http://192.168.4.1`, bấm **Đồng bộ giờ**. Làm trước mỗi buổi ghi và ngay sau mỗi buổi (để đo trôi giờ). Trong lúc ghi Wi-Fi tắt nên trang mất kết nối là bình thường.

## Ghi thử trên bàn (trước khi dùng thật)

Sau khi đồng bộ giờ: bấm **Ghi thử 10 phút** trên trang, hoặc gõ `t` trong Serial Monitor (`x` để dừng sớm). Đạt khi: `THU_….wav` dài đúng 10 phút (±1 giây), nghe rõ, không rè, không ngắt; `TC-02_ghi.csv` có `mau_thieu_chen_0 = 0`; không có `TC-02_khoang_trong.csv`. Nghe xong xoá tệp `THU_`.
