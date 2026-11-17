# Bảng đặc tả kỹ thuật TC-01 (cải tiến thiết bị giai đoạn 1)

Lập ngày 17/11/2026 từ nhật ký và tệp kết quả trong repo. Ô nào chưa có số đo ghi **“chưa đo”**; không ước lượng thay số đo. Cột “Nguồn” chỉ tệp hoặc mục Protocol chứa số liệu.

## 1. Phần cứng

| Hạng mục | Giá trị | Nguồn |
| --- | --- | --- |
| Vi điều khiển | ESP32-S3 N16R8 (Flash 16 MB, PSRAM khoảng 8 MB) | `firmware/README.md`, bài kiểm tra T1 |
| Micro | INMP441, I2S, 16 kHz | `firmware/van_hanh/README.md` |
| Lưu trữ | Thẻ microSD FAT32 qua module SPI, nguồn 3V3 | `firmware/van_hanh/README.md` |
| Sơ đồ mạch | Bản 2.0, PDF 4 trang | `firmware/so_do_mach/` |
| Nguồn cấp | Sạc USB, thay sạc hằng ngày lúc 17:00 | `firmware/van_hanh/README.md` |
| Điện áp nguồn | **chưa đo** (chưa lắp cầu chia 100 kΩ/100 kΩ; cột `dien_ap_v` để trống) | `firmware/van_hanh/README.md` mục “Còn thiếu”, nhật ký 24 giờ lần 2 |
| Công suất tiêu thụ, thời gian chạy bằng pin | **chưa đo** | — |
| Chi phí linh kiện | **chưa ghi** trong repo | — |

## 2. Xử lý tín hiệu và mô hình

| Hạng mục | Giá trị | Nguồn |
| --- | --- | --- |
| Lấy mẫu | 16 kHz, 16 bit, 1 kênh; quy đổi `(raw × 8) >> 16` | Protocol 16.8 |
| Cửa sổ chấm | 1 s, trượt 0,5 s | `results/mo_hinh_nen_v1.md` |
| Đặc trưng | MFE: khung 0,02 s, bước 0,01 s, 40 bộ lọc, FFT 256, 0–8 kHz, sàn nhiễu −72 dB → 3.960 đặc trưng | `results/mo_hinh_nen_v1.md` |
| Mô hình đếm (đóng băng) | v2 (Impulse #3), int8, EON | Protocol mục 12 |
| Ngưỡng và gộp sự kiện | θ = 0,50 · k = 1 · g = 0 | Protocol mục 12, 16.23; `results/chon_nguong_v2.json` |
| Cấu hình thư viện | `EIDSP_QUANTIZE_FILTERBANK` 0 · `EIDSP_USE_ESP_DSP` 1 · `ESP_NN` 0 | Protocol 16.17 |
| Phép thử đồng nhất (thiết bị so với máy tính) | ĐẠT 12/11: v2 khớp 119/119 cửa sổ, lệch lớn nhất 0 bậc int8 | nhật ký kiểm chứng 12/11 |

## 3. Hiệu năng đếm (trên luồng thử, không phải tại KTX)

| Chỉ số | v2, θ 0,50 | Nguồn |
| --- | --- | --- |
| Độ nhạy theo sự kiện, luồng sạch | 97,4% (1.553/1.595) | `results/chon_nguong_v2.json` |
| Báo nhầm trên đối chứng âm (hành lang không người, 16/11) | 3 sự kiện / 5,5 giờ = 0,55/giờ (quy tắc chọn: ≤ 4/giờ) | `results/chon_nguong_v2.json`, `results/doi_chung_am/` |
| Báo nhầm trên luồng mở (nền khó) | 281,8/giờ | `results/chon_nguong_v2.json` |
| Độ nhạy / báo nhầm khi đếm trong KTX | **chưa đo** (phần để chấm ghi 17/11 tối, chấm sau) | Protocol mục 7 |

## 4. Độ ổn định khi chạy liên tục (chạy 24 giờ lần 2, 15/11 19:19 → 16/11 19:18)

| Hạng mục | Kết quả | Nguồn |
| --- | --- | --- |
| Số phút có nhật ký | 1.440/1.440, không khởi động lại (thời gian chạy 233 → 86.573 s) | `TC-01_*_moi_phut.csv` |
| Lỗi thẻ · khung mất · cửa sổ bỏ qua | 0 · 0 · 0 | như trên |
| Thời gian suy luận (v1 + v2) min / trung vị / max | 231 / 238 / 261 ms (bước cửa sổ 500 ms) | như trên |
| Nhiệt độ chip min / trung vị / max | 35,6 / 37,6 / 43,6 °C | như trên |
| Heap trống nhỏ nhất · PSRAM trống nhỏ nhất | 119.836 B · 7.978.276 B | như trên |
| Wi-Fi | Bật 1 phút trong 24 giờ, công suất 2 dBm | như trên, `firmware/van_hanh/README.md` |
| Dung lượng dữ liệu | Khoảng 2,95 MB tệp `diem.csv` mỗi 14,6 giờ | thẻ TC-01 |

## 5. Âm học và thời gian

| Hạng mục | Giá trị | Nguồn |
| --- | --- | --- |
| Mức âm nền hành lang (24 giờ) LAeq min / trung vị / max | −46,5 / −39,6 / −6,4 dBFS | `TC-01_*_moi_phut.csv` |
| LA90 min / trung vị / max | −46,8 / −41,5 / −10,5 dBFS | như trên |
| Quy đổi dBFS → dB(A) | **chưa đo** (hiệu chuẩn dự kiến 18/11) | Protocol 16.9 |
| Đồng bộ giờ | Điện thoại qua `192.168.4.1` (8 lần khứ hồi, lấy lần nhanh nhất); lần 17/11 11:16: lệch 0 ms, khứ hồi 23 ms | `TC-01_*_dong_bo.csv` |
| Trôi đồng hồ thực tế | **chưa đo** (README ghi thạch anh khoảng 1–2 s/ngày là thông số tham khảo, chưa phải số đo của TC-01) | `firmware/van_hanh/README.md` |

## 6. Bảo vệ dữ liệu

- Firmware vận hành không có hàm ghi âm thanh; chỉ lưu điểm, sự kiện và nhật ký.
- Ghi âm kiểm định chỉ trong khung giờ đã thông báo (Protocol 16.23: dùng chung một thẻ, hai firmware). Tệp WAV chỉ nằm trên thẻ và `~/TussiCount_KTX`, không đưa lên GitHub hay dịch vụ trực tuyến.

## 7. Việc còn thiếu để hoàn chỉnh bảng

1. Lắp cầu chia điện áp và ghi cột `dien_ap_v`.
2. Đo công suất (ví dụ đồng hồ USB) để tính thời gian chạy bằng pin.
3. Hiệu chuẩn dB(A) ngày 18/11.
4. Tính trôi đồng hồ từ `dong_bo.csv` sau nhiều lần đồng bộ.
5. Chấm phần để chấm 17/11 để có độ nhạy tại KTX.
