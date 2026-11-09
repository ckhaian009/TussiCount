# Mô hình nền v1: kết quả huấn luyện và kiểm tra (09/11/2026)

Việc t17, Protocol mục 8. Huấn luyện trên Edge Impulse, dự án **1156522**, mô hình chọn là **Impulse #2
“San nhieu -72 dB”**, bản int8 (bản sẽ nạp vào ESP32-S3). Ảnh chụp trạng thái dự án được lưu ở mục
Versioning, phiên bản 1 (riêng tư). Toàn bộ dữ liệu là dữ liệu mở; không dùng âm thanh ghi tại KTX.

## 1. Dữ liệu

Mỗi mẫu là một đoạn 1 giây, 16 kHz, một kênh, mức đỉnh ngẫu nhiên trong [−35; −3] dBFS (cách tạo:
`tools/chuan_hoa_am_thanh/README.md`).

| Tập | cough (COUGHVID) | noise ESC-50 | noise giọng nói Common Voice tiếng Việt | Tổng |
| --- | ---: | ---: | ---: | ---: |
| Huấn luyện | 6.362 | 4.527 | 2.285 | 13.174 |
| Kiểm tra | 1.595 | 1.130 | 740 | 3.465 |

Chia theo nhóm, không nhóm nào nằm ở cả hai tập (kiểm tra hai lần: trên máy bằng `kiem_tra.py` và trên Edge Impulse
qua metadata `nhom`): COUGHVID theo bản ghi (2.392 / 597), Common Voice theo người nói (183 / 45),
ESC-50 theo fold (1–4 / 5).

## 2. Thiết kế và huấn luyện

| Thành phần | Thiết lập |
| --- | --- |
| Cửa sổ | 1.000 ms, bước 500 ms, 16 kHz, zero-pad |
| Xử lý tín hiệu | MFE: khung 0,02 s, bước 0,01 s, 40 bộ lọc, FFT 256, tần số thấp 0 Hz, cao 8 kHz, **sàn nhiễu −72 dB** → 99 × 40 = 3.960 đặc trưng |
| Mạng nơ-ron | Mặc định của Edge Impulse: Reshape 40 cột → Conv1D 8 lọc (k = 3) + MaxPool → Dropout 0,25 → Conv1D 16 lọc (k = 3) + MaxPool → Dropout 0,25 → Flatten → Dense 2 (softmax) |
| Huấn luyện | 100 epoch, tốc độ học 0,005, batch 32, không tăng cường dữ liệu, CPU |
| Validation | 20% tập huấn luyện, **tách theo metadata `nhom`** (cùng bản ghi / người nói / đoạn gốc ESC-50 thì cùng phía) |
| Lượng tử hoá | int8 (EON Compiler, tối ưu RAM) |

## 3. Chọn cấu hình (chỉ dùng validation)

Quy tắc ghi trước khi biết kết quả cấu hình thứ hai và trước khi chạy tập kiểm tra
(`results/mo_hinh_nen_nhat_ky_thi_nghiem.md`): chọn cấu hình có độ chính xác validation (int8) cao hơn;
chênh dưới 0,5 điểm phần trăm thì giữ mặc định.

| Cấu hình (validation, n = 2.687, int8) | Độ chính xác | Ho nhận đúng (1.296) | Không ho nhận đúng (1.391) |
| --- | ---: | ---: | ---: |
| #1 Sàn nhiễu −52 dB (mặc định) | 93,04% | 91,36% | 94,61% |
| **#2 Sàn nhiễu −72 dB** | **95,20%** | **93,36%** | **96,91%** |

Lý do thử −72 dB: đo bằng chính mã MFE của Edge Impulse (`results/mfe_khao_sat_san_nhieu.txt`), ở −52 dB đoạn ho nhỏ
nhất (đỉnh −35 dBFS) chỉ còn 17,6% ô phổ trên sàn; ở −72 dB còn 46,1%.

## 4. Kết quả trên tập kiểm tra (3.465 đoạn, chưa dùng khi huấn luyện và chọn cấu hình)

Dương tính = có tiếng ho. Ngưỡng 0,5. KTC 95%: Wilson (coi từng đoạn độc lập) và bootstrap theo nhóm
(lấy lại cả bản ghi / người nói / đoạn gốc, 2.000 lần), là khoảng nên trích dẫn vì các đoạn cùng bản ghi không độc lập.

| Mô hình | Độ nhạy | Độ đặc hiệu | Độ chính xác dương | F1 | ROC AUC |
| --- | --- | --- | ---: | ---: | ---: |
| **v1 int8** | **94,80%** (1.512/1.595); bootstrap 93,6–95,9% | **96,90%** (1.812/1.870); bootstrap 95,7–97,9% | 96,31% | 0,956 | 0,991 |
| v1 float32 | 94,48% (1.507/1.595) | 97,27% (1.819/1.870) | 96,73% | 0,956 | 0,991 |
| #1 int8 (đối chiếu) | 92,54% (1.476/1.595) | 96,04% (1.796/1.870) | – | – | – |

Ma trận nhầm lẫn v1 int8: TP 1.512 · FN 83 · FP 58 · TN 1.812. Lượng tử hoá int8 gần như không làm giảm chất lượng.
Edge Impulse báo độ chính xác 94,60% cho bản float32; con số này thấp hơn vì Edge Impulse tính mẫu có xác suất cao nhất
dưới 0,6 là “uncertain” và coi là sai.

**Theo ngưỡng (v1 int8):**

| Ngưỡng | Độ nhạy | Độ đặc hiệu | F1 |
| ---: | ---: | ---: | ---: |
| 0,5 | 94,80% | 96,90% | 0,956 |
| 0,6 | 93,35% | 97,75% | 0,953 |
| 0,7 | 91,60% | 98,18% | 0,946 |
| 0,8 | 88,15% | 98,82% | 0,930 |
| 0,9 | 82,13% | 99,30% | 0,898 |

Ngưỡng dùng trên thiết bị phải chọn trên validation hoặc dữ liệu thử nghiệm phát lại, không chọn trên bảng này.

**Theo mức âm và nguồn nhiễu (v1 int8, ngưỡng 0,5):**

| Nhóm | n | Kết quả |
| --- | ---: | --- |
| Ho, đỉnh −35…−29 dBFS | 335 | độ nhạy 91,0% (Wilson 87,5–93,7%) |
| Ho, đỉnh −29…−19 dBFS | 477 | độ nhạy 95,8% |
| Ho, đỉnh −19…−3 dBFS | 783 | độ nhạy 95,8% |
| Không ho, ESC-50 | 1.130 | độ đặc hiệu 97,5% |
| Không ho, giọng nói | 740 | độ đặc hiệu 95,9% |

Lớp ESC-50 bị báo nhầm là ho nhiều nhất: tiếng đồng hồ tích tắc 7/24, chó sủa 5/23, hắt hơi 4/20, tiếng cười 4/24.
Một số đoạn ho bị bỏ sót có điểm gần 0 (ví dụ hai đoạn của bản ghi `97da4b5d`), có thể là nhãn sai trong COUGHVID
(bản ghi được chọn theo `cough_detected` ≥ 0,8, chưa có người nghe lại); cần nghe kiểm tra trước khi kết luận.

## 5. Kiểm tra độ bền: tiếng ho có nền ồn

Khi rà dữ liệu thấy tiếng ho COUGHVID thường nằm trên nền gần như im lặng: 71% đoạn có ≥ 5% mẫu bằng 0;
nền yên nhất thấp hơn đỉnh khoảng 61 dB. Đoạn ESC-50 và giọng nói có nền ồn liên tục (22 và 39 dB dưới đỉnh).
Mô hình có thể học lối tắt “có tiếng động trên nền yên = ho”. Tập kiểm tra độ bền (`tools/mo_hinh_nen/tao_tap_kiem_tra_ben.py`)
lấy 500 tiếng ho của tập kiểm tra, trộn mỗi tiếng với một đoạn nền thuộc tập kiểm tra (ESC-50 fold 5 hoặc giọng nói
người nói thuộc tập kiểm tra) ở 3 mức SNR, rồi chuẩn hoá mức như dữ liệu chính.
SNR tính theo RMS cả cửa sổ 1 giây, nên SNR trong lúc có tiếng ho còn cao hơn con số ghi.

| v1 int8, ngưỡng 0,5 (cùng 500 tiếng ho) | Độ nhạy | KTC 95% (Wilson) | Nền ESC-50 | Nền giọng nói |
| --- | ---: | --- | ---: | ---: |
| Ho sạch (không trộn) | 93,2% | 90,7–95,1% | | |
| SNR 20 dB | 75,8% | 71,9–79,4% | 70,0% | 81,8% |
| SNR 10 dB | 51,0% | 46,6–55,4% | 36,0% | 66,4% |
| SNR 0 dB | 26,8% | 23,1–30,9% | 16,6% | 37,2% |

**Kết luận:** mô hình nền nhận tốt tiếng ho trên nền yên nhưng hụt mạnh khi có nền ồn, kể cả ở SNR 20 dB.
Số liệu trên tập kiểm tra sạch (mục 4) vì vậy là **giới hạn trên**, chưa phản ánh điều kiện KTX. Đây là căn cứ định lượng
cho mô hình có tăng cường dữ liệu (Protocol sửa đổi 16.7: vang phòng và nền ồn SNR 0–20 dB), so sánh trên cùng tập kiểm tra
và cùng tập độ bền trước khi đóng băng.

## 6. Ước lượng trên thiết bị

Edge Impulse không có ESP32-S3 trong danh sách; ước lượng theo Espressif ESP-EYE (ESP32, 240 MHz):

| Khối | Thời gian | RAM đỉnh | Flash |
| --- | ---: | ---: | ---: |
| MFE | 350 ms | 20 KB | – |
| Mạng nơ-ron int8 (EON) | 11 ms | 14,7 KB | 40,4 KB |

Tổng khoảng 361 ms, dưới bước cửa sổ 500 ms nhưng không còn nhiều dư. Cần đo thật trên ESP32-S3 (có lệnh vector,
dự kiến nhanh hơn) khi nạp thư viện.

## 7. Hạn chế

- Chỉ số tính trên từng cửa sổ 1 giây, chưa phải đếm tiếng ho theo sự kiện. Nếu nền là âm thanh “khó” như tập kiểm tra
  liên tục, độ đặc hiệu 96,9% tương ứng khoảng 223 cửa sổ báo nhầm mỗi giờ (7.200 cửa sổ/giờ). Đây là ước lượng
  bi quan vì phòng KTX phần lớn thời gian yên hơn, nhưng vẫn cho thấy cần quy tắc gộp sự kiện (ví dụ yêu cầu điểm cao ở
  cửa sổ liên tiếp) và kiểm chứng bằng phát lại.
- Dữ liệu là bản ghi điện thoại, khác micro INMP441; chưa có dữ liệu KTX trong đánh giá.
- Edge Impulse không cho đặt seed huấn luyện; huấn luyện lại có thể cho số hơi khác. Mô hình đã dùng được giữ ở
  Versioning phiên bản 1.
- Mới thử 2 cấu hình xử lý tín hiệu, giữ nguyên kiến trúc mạng mặc định.

## 8. Tệp liên quan

| Tệp | Nội dung |
| --- | --- |
| `results/mo_hinh_nen_nhat_ky_thi_nghiem.md` | Nhật ký thí nghiệm theo thời gian, quy tắc chọn cấu hình ghi trước |
| `results/mo_hinh_nen_v1_chi_so.json`, `..._float32_chi_so.json` | Toàn bộ chỉ số tập kiểm tra |
| `results/mo_hinh_nen_v1_diem_tung_mau.csv`, `..._float32_diem_tung_mau.csv` | Điểm từng mẫu tập kiểm tra |
| `results/mo_hinh_nen_v1_do_ben.json`, `results/mo_hinh_nen_v1_ben_diem_tung_mau.csv`, `results/ei_kiem_tra_ben.csv` | Tập kiểm tra độ bền |
| `results/mfe_khao_sat_san_nhieu.txt` | Khảo sát sàn nhiễu MFE |
| `results/ei_du_lieu_mo_hinh_nen.csv`, `..._tom_tat.json`, `results/ei_tai_len_ket_qua*.txt` | Bảng kê dữ liệu và đối chiếu tải lên |
