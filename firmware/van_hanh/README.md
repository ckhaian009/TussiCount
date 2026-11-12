# Firmware vận hành TC-01

`TC01_Van_hanh/` là firmware vận hành cho thiết bị đếm TC-01 (ESP32-S3 N16R8 + INMP441 + microSD), viết theo Protocol mục 5, 6, 8, 16.5, 16.8. **Không có hàm ghi tệp âm thanh.**

## Thiết bị ghi gì

Mỗi ngày một bộ tệp ở thư mục gốc của thẻ. Ngày = ngày của (giờ Việt Nam − 6 giờ), nên đêm D (18:00 D → 06:00 D+1) nằm trọn trong tệp ngày D.

| Tệp | Nội dung |
| --- | --- |
| `TC-01_<ngày>_su_kien.csv` | Mỗi sự kiện ho do mô hình `MO_HINH_DEM` gộp: thời điểm (tâm cửa sổ điểm cao nhất), độ dài, điểm tin cậy, số cửa sổ; kèm mô hình, ngưỡng, k, g |
| `TC-01_<ngày>_diem.csv` | Điểm `p_cough` của **mọi** cửa sổ 1 s (trượt 0,5 s) theo **cả hai** mô hình v1 và v2. Đêm chạy trước khi đóng băng: `tools/chay_mo_hinh/tach_diem_thiet_bi.py` (lấy cột của mô hình được chọn) → `gop_su_kien.py` với ngưỡng đã đóng băng |
| `TC-01_<ngày>_dong_bo.csv` | Mỗi lần đồng bộ giờ: thời điểm, nguồn (`dien_thoai` / `ntp`), độ lệch đo được, thời gian khứ hồi |
| `TC-01_<ngày>_moi_phut.csv` | Mỗi phút: LAeq, LA90 (dBFS và dB(A) khi đã hiệu chuẩn), điện áp, thời gian chạy, nhiệt độ chip, heap và PSRAM trống nhỏ nhất, suy luận lớn nhất, khung bị mất, cửa sổ bỏ qua, số sự kiện, NTP lần cuối và độ lệch, RSSI, lỗi thẻ |

Mọi dòng sự kiện và nhật ký có cột `du_lieu = THAT` (tệp mẫu mô phỏng mang nhãn `MO_PHONG`).

## Cách hoạt động

- **Lõi 0:** đọc I2S 16 kHz vào bộ đệm vòng 8 giây (PSRAM); lọc trọng số A và tính mức từng khung 0,5 s; ghi thẻ mỗi 10 giây; nhật ký mỗi phút; gói 10 phút gửi Google Sheets nếu có `sheets_url`.
- **Lõi 1:** cửa sổ 1 s trượt 0,5 s → chấm bằng v1 (Impulse #2) **và** v2 (Impulse #3) → gộp sự kiện theo mô hình `MO_HINH_DEM`. Hai mô hình nằm trong một SDK chung (`TussiCount_v1v2_inferencing`), ghép từ hai thư viện xuất riêng; tên biến của hai impulse khác nhau nên không trùng. Thời gian suy luận trong nhật ký là tổng của cả hai mô hình. Logic gộp khớp 12/12 tình huống thử của `gop_su_kien.py` (`thu/thu_gop.cpp`).
- **Thời gian:** đồng hồ mẫu (số mẫu ÷ 16.000) neo vào giờ chuẩn. Hai nguồn giờ:
  - **Điện thoại (chính):** mạch luôn tự phát Wi-Fi `TussiCount-TC-01`. Điện thoại kết nối, mở `http://192.168.4.1`, bấm **Đồng bộ giờ**: trang đo 8 lần khứ hồi, lấy lần nhanh nhất, gửi độ lệch về mạch. Làm khi bắt đầu chạy và mỗi ngày lúc thay sạc 17:00.
  - **NTP (khi có Wi-Fi Internet trong `cauhinh.txt`):** mỗi 30 phút.
  Mỗi lần đồng bộ ghi một dòng vào `TC-01_<ngày>_dong_bo.csv` (nguồn, độ lệch = phần trôi tích luỹ, thời gian khứ hồi). Thạch anh trôi khoảng 1–2 giây mỗi ngày nên giữa hai lần đồng bộ bằng điện thoại có thể vượt 1 giây; khi phân tích, hiệu chỉnh bằng `tools/phan_tich/hieu_chinh_troi_gio.py` (nội suy tuyến tính, đã thử: DAT). Thiết bị chỉ bắt đầu đếm sau lần đồng bộ đầu tiên.
- **Watchdog** 30 giây cho cả ba tác vụ; khởi động lại thấy được qua cột `thoi_gian_chay_s` quay về 0.
- **Quy đổi mẫu:** `(raw × 8) >> 16`, giống firmware ghi WAV kiểm định T4 (Protocol 16.8), để mô hình nhận cùng một đầu vào ở TC-01 và TC-02.

## Tham số đóng băng

Toàn bộ nằm trong `tham_so.h`: mô hình gộp sự kiện (`MO_HINH_DEM`), ngưỡng θ, k, g, hệ số khuếch đại, hệ số hiệu chuẩn, chân nối. Khi đóng băng: điền giá trị, biên dịch, ghi SHA-256 của `TC01_Van_hanh.ino` + `tham_so.h` vào mục 12 và 16.13 của Protocol bằng một commit riêng.

## Nạp

1. Thư viện mô hình: `Documents/Arduino/libraries/TussiCount_v1v2_inferencing` (ghép từ `data/ei_lib/v1` và `v2`: SDK và mô hình của v1, thêm `tflite_learn_1156522_12_compiled.*` và khối định nghĩa `impulse_1156522_3` của v2 vào `model_variables.h`; không đưa lên GitHub vì giấy phép Edge Impulse).
2. Arduino IDE mở `Documents/Arduino/TC01_Van_hanh` (bản sao để biên dịch; bản gốc là thư mục này trong repo).
3. Tools: ESP32S3 Dev Module · USB CDC On Boot: Enabled · Flash 16MB · PSRAM: OPI PSRAM · Partition: 16M Flash (3MB APP/9.9MB FATFS). Nếu nạp lỗi ở bước đổi tốc độ, đặt Upload Speed 115200.
4. Thẻ nhớ FAT32, có `/cauhinh.txt` (mẫu: `cauhinh_mau.txt`; bản đã điền Wi-Fi để ở thư mục Downloads, không đưa lên GitHub).

## Cấu hình thư viện mô hình (bắt buộc, Protocol 16.17)

Sửa trong `TussiCount_v1v2_inferencing` (và hai thư viện v1, v2 nếu còn giữ), thư mục `src/edge-impulse-sdk/`:

| Tệp | Cờ | Giá trị | Lý do |
| --- | --- | --- | --- |
| `dsp/config.hpp` | `EIDSP_QUANTIZE_FILTERBANK` | 0 | Bộ lọc MFE số thực, giống bộ chạy trên máy tính |
| `dsp/config.hpp` | `EIDSP_USE_ESP_DSP` | 1 | FFT của esp-dsp; với kissfft suy luận lên 915 ms |
| `classifier/ei_classifier_config.h` | `EI_CLASSIFIER_TFLITE_ENABLE_ESP_NN` | 0 | Nhân ESP-NN cho điểm khác máy tính (v1 27,7%, v2 1,7% cửa sổ đạt) |

Sau khi đổi phải xoá bộ đệm biên dịch (biên dịch lại toàn bộ thư viện, khoảng 5 phút). Kết quả 12/11: phép thử đồng nhất ĐẠT cả hai mô hình, suy luận lớn nhất 230 ms.

## Wi-Fi theo khung giờ

Wi-Fi phát liên tục làm lỗi ghi thẻ, nên Wi-Fi chỉ bật khi chưa có giờ, 15 phút đầu sau khởi động và 16:50–17:20 (giờ đồng bộ hằng ngày), công suất 2 dBm. Module thẻ lấy nguồn từ chân 3V3 (chân 5Vin của mạch không ra 5 V khi cấp qua USB).

## Phép thử đồng nhất (Protocol 7.6)

Chép một tệp WAV (PCM 16 bit, 1 kênh, 16 kHz) ra thẻ với tên `/thu_dong_nhat.wav`, khởi động lại. Thiết bị chấm mọi cửa sổ và ghi `/thu_dong_nhat_diem.csv` cùng định dạng với `chay_mo_hinh dai` trên máy tính; so từng cột với bộ chạy của mô hình tương ứng (v1, v2), mỗi cửa sổ lệch ≤ 1 bậc int8 là đạt. Thiết bị tự so với `tham_chieu_dong_nhat.h` (điểm bộ chạy trên máy tính cho 60 giây đầu của `data/luong_kiem_tra/sach.wav`) và in kết quả ra Serial; đạt khi cả hai mô hình có ≥ 95% cửa sổ khớp. Chỉ dùng tệp dữ liệu mở, không dùng âm thanh ghi tại KTX.

## Còn thiếu

- Điện áp nguồn: cần cầu chia 100 kΩ / 100 kΩ từ chân 5V xuống một chân ADC, rồi đặt `PIN_DIEN_AP` trong `tham_so.h`. Chưa lắp thì cột điện áp để trống.
