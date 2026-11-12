# Nhật ký kiểm chứng mã do AI viết

Mỗi lần nhờ trợ lý AI viết mã, nhóm ghi: công cụ, phép thử đã chạy, kết quả, lỗi phát hiện, cách sửa và commit liên quan. Lỗi của AI được ghi nguyên, kể cả khi đã sửa.

## 09/11/2026 · Phép thử tự động cho 1.100 đoạn ho Coswara (việc t16)

- **Công cụ:** `tools/kiem_tra_doan_ho/kiem_tu_dong.py`, kiểm tra đầu ra của `tools/chuan_bi_phat_lai.py` (Protocol mục 7.1).
- **Phép thử:** chạy lại thuật toán cắt trên bản ghi gốc và so với đoạn trên đĩa (tái lập); kiểm tra tần số mẫu, độ dài, mức đỉnh −1 dBFS; đánh dấu đoạn nghi cụt đầu, cụt đuôi, có hai tiếng ho.
- **Lỗi của AI:** bản đầu cắt lại đoạn theo thời điểm đã làm tròn 3 chữ số trong `results/coswara_playlist.csv`, lệch tới 0,5 ms so với lúc cắt thật, nên báo nhầm 80/1.100 đoạn “không tái lập được”.
- **Cách phát hiện và sửa:** trợ lý AI xem lại các đoạn bị báo lỗi: độ dài và mức đỉnh đều đúng, chỉ có hệ số tương quan thấp hơn ngưỡng (0,89–0,999), phù hợp với việc lệch vài mẫu do làm tròn thời điểm, nên lỗi nằm ở phép so sánh chứ không ở đoạn cắt. Sửa: gọi lại chính hàm cắt để lấy thời điểm chính xác, chỉ so thời điểm đã làm tròn với sai số 0,6 ms.
- **Kết quả sau khi sửa:** 0/1.100 đoạn lỗi tái lập và định dạng. Dấu hiệu nghi: cụt đầu 3, cụt đuôi 117, hai tiếng ho 154 đoạn. Các dấu hiệu này là quy tắc thô, chưa kiểm chứng; chỉ dùng để đối chiếu với phép nghe 50 đoạn (việc t52), không dùng để loại tệp.
- **Chạy lại xác nhận (09/11/2026, 21:03):** chạy lần hai trên máy của An (Python 3.10.12, NumPy 2.2.6, soundfile 0.14.0); tệp `results/kiem_tra_doan_ho_tu_dong.csv` trùng từng byte với lần đầu (SHA-256 `21f392c6…a244c3`).
- **Còn chờ:** kết quả nghe 50 đoạn (t52) để biết tỉ lệ đoạn cắt đúng và độ tin cậy của các dấu hiệu nghi.
- **Commit:** “Thêm phép thử đoạn ho Coswara, công cụ mức “vừa”, bài kiểm tra phần cứng và sơ đồ mạch”.

## 09/11/2026 · Công cụ chuẩn bị phép nghe và tính mức “vừa”

- **Công cụ:** `tools/kiem_tra_doan_ho/chon_50_doan.py` (chọn ngẫu nhiên 50 đoạn, seed 5050, vẽ dạng sóng, tạo phiếu nghe); `tools/kiem_tra_doan_ho/tong_hop_nghe.py` (tỉ lệ đúng, khoảng tin cậy Wilson 95%); `tools/muc_vua/muc_vua.py` (trung bình mức đỉnh dB(A) của 20 tiếng ho).
- **Phép thử đã chạy:** `chon_50_doan.py` tạo đủ 50 tệp và 5 trang dạng sóng; `tong_hop_nghe.py` báo đúng 50 dòng chưa điền khi phiếu còn trống; `muc_vua.py` chạy với 20 giá trị giả lập (trung bình 68, SD 3) rồi trả phiếu về trống.
- **Còn chờ:** nhóm đối chiếu `muc_vua.py` một lần với phép tính trên bảng tính (AVERAGE, STDEV) khi có số đo thật.

## 09/11/2026 · Bài kiểm tra phần cứng T1–T4 và sơ đồ mạch

- **Mã:** `firmware/kiem_tra/` (T1 bo và LED, T2 micro INMP441, T3 thẻ nhớ, T4 ghi WAV 10 giây); sơ đồ trong `firmware/so_do_mach/`.
- **Phép thử đã chạy:** biên dịch cả 4 bài với Arduino-ESP32 3.3.12, cấu hình ESP32S3 Dev Module, 16 MB flash, OPI PSRAM: không lỗi.
- **Lỗi của AI phát hiện khi biên dịch:** T1 thiếu `#include "esp_mac.h"`; đã sửa.
- **Còn chờ:** chạy trên phần cứng thật và ghi số liệu từng bài (Flash, PSRAM, mức dBFS, tốc độ ghi thẻ, chất lượng tệp WAV).

## 09/11/2026 · Dữ liệu và mô hình nền trên Edge Impulse (việc t17)

- **Mã:** `tools/chuan_hoa_am_thanh/` (chuẩn bị dữ liệu 16 kHz, phép thử, công cụ tải lên) và `tools/mo_hinh_nen/` (khảo sát sàn nhiễu MFE, tập kiểm tra độ bền, ghi và phân tích điểm). Báo cáo: `results/mo_hinh_nen_v1.md`.
- **Phép thử đã chạy:** `kiem_tra.py` trên 16.639 đoạn: đạt (định dạng, mức, không rò rỉ nhóm, nhãn, số tệp). Công cụ tải lên chạy thử với `curl` giả lập trước (chia lô, nhãn, chạy lại, kiểm tra không có key trong mọi tệp đã ghi), rồi chạy thật: số mẫu trên dự án khớp số tệp (13.174 / 3.465), 0 lỗi, 0 trùng. Metadata nhóm kiểm tra lại trên Edge Impulse: 0 nhóm nằm ở cả hai tập. `phan_tich_kiem_tra.py` chạy trên điểm giả lập trước khi có điểm thật. Điểm chép từ trình duyệt sang máy được đối chiếu với ma trận nhầm lẫn tính trong trình duyệt: khớp từng ô; thứ tự mẫu kiểm bằng SHA-256 danh sách tên.
- **Lỗi và rủi ro phát hiện:**
  - Ở sàn nhiễu mặc định −52 dB của MFE, đoạn ho nhỏ nhất gần như bị xoá; thử thêm −72 dB, chọn theo validation với quy tắc ghi trước.
  - Dữ liệu COUGHVID có nền gần như im lặng, khác hẳn nền của đoạn không ho. Tập kiểm tra độ bền xác nhận mô hình nền học theo lối tắt này: độ nhạy 93,2% khi sạch, còn 75,8% / 51,0% / 26,8% ở SNR 20 / 10 / 0 dB.
  - Thư mục Documents của An đồng bộ iCloud: không được để âm thanh KTX trong kho.
- **Giới hạn của AI cần ghi:** trợ lý AI thao tác Edge Impulse qua trình duyệt đã đăng nhập của An; An tự dán API key vào hộp thoại, AI không lưu key. Edge Impulse không cho đặt seed nên số liệu huấn luyện lại có thể lệch nhẹ; mô hình đã dùng lưu ở Versioning v1 của dự án.
- **Còn chờ:** mô hình có tăng cường dữ liệu (Protocol 16.7) so trên cùng tập kiểm tra và tập độ bền; nghe lại các đoạn ho bị bỏ sót có điểm gần 0 (nghi nhãn sai); đo thời gian MFE và mạng nơ-ron thật trên ESP32-S3.

## 10/11/2026 · Công cụ chuẩn bị kiểm định và mô hình tăng cường (việc t18, t19, t20, t33, t35, t37–t40; sửa đổi 16.7)

- **Mã:** `tools/tang_cuong/`, `tools/chay_mo_hinh/`, `tools/phat_lai/`, `tools/am_hoc/`, `tools/gan_nhan/`, `tools/cham/`, `tools/phan_tich/`. Mỗi thư mục có README ghi phép thử đã chạy.
- **Phép thử đã chạy:** ghép sự kiện 12/12 tình huống; gộp sự kiện 12/12; thống kê so với Protocol mục 11 và dữ liệu mô phỏng; H1/H2 trên dữ liệu mô phỏng tìm lại đúng hiệu ứng đã đặt; âm học trên tín hiệu tổng hợp; trình phát chạy khô đủ 1.176 lần phát theo lịch; đoạn ho Coswara tạo lại khớp `coswara_playlist.csv` 1.100/1.100; kho RIR 600/600 đạt T20; dữ liệu tăng cường và phép thử của nó trên bộ thay thế 140 đoạn (cố ý gây 2 lỗi thì phép thử bắt đủ 2).
- **Lỗi của AI phát hiện khi thử:** kho RIR lần đầu lệch khoảng cách về phía gần; lịch phát lần đầu vượt thời gian khung yên tĩnh của buổi 2 và dồn phần dư cho buổi 1; đổi tần số làm một tệp phát vượt 0 dBFS; bộ lọc A thiết kế ở 48 kHz lệch 1,2 dB tại 10 kHz; hai đáp án trong phép thử thống kê viết sai dung sai. Tất cả đã sửa và chạy lại.
- **Giới hạn của AI cần ghi:** phần lớn mã viết và thử trên máy chủ của trợ lý AI với dữ liệu mở hoặc dữ liệu tổng hợp, vì ổ đĩa laptop gần đầy và `data/` đang nằm trên iCloud. Chưa chạy trên dữ liệu thật của dự án: dữ liệu tăng cường, đối chiếu điểm bộ chạy với Edge Impulse, phát thật qua loa. Âm thanh KTX không được đưa lên máy chủ đó; mọi công cụ xử lý âm thanh KTX chạy trên laptop.
- **Tối 10/11, sau khi An giải phóng ổ đĩa (chạy trên laptop):** dữ liệu tăng cường thật 16.189 tệp, `kiem_tra.py` đạt; tải lên 12.724 đoạn training, số mẫu trên dự án khớp (25.898), 0 lỗi; Impulse #3 sao chép cấu trúc Impulse #2, đọc lại cấu hình giống hệt; metadata `nhom` của đoạn tăng cường lấy từ đoạn gốc trên Edge Impulse. Bộ chạy biên dịch trên laptop (máy ảo Linux arm64), điểm so với Edge Impulse: 96,9% đoạn kiểm tra sạch và 91,3% đoạn độ bền lệch ≤ 1 bậc int8, lớn nhất 0,039. Công cụ tạo luồng kiểm tra lần đầu bị hệ điều hành dừng vì giữ cả luồng 3,5 giờ trong bộ nhớ; đã sửa để ghi từng đoạn. Trang bấm giờ tầng 2 (artifact “Bấm giờ ho thật”) và `tools/phan_tich/tao_bang_tang2.py` thử trên dữ liệu mô phỏng: đạt.
- **Còn chờ:** huấn luyện Impulse #3 và so sánh theo quy tắc ghi trước (cần phần để sửa tối 11/11); chạy thử trình phát với loa thật.

## 11–12/11/2026 · Kiểm tra phần cứng trên mạch thật, firmware vận hành TC-01 (việc t09, t11, t12, t55; sửa đổi 16.14–16.19)

- **Mã:** `firmware/kiem_tra/T5_Kiem_tra_tong_hop/` (tự chọn chân theo loại mạch, chẩn đoán dây MISO, thử thẻ ở 10/4/1 MHz); `firmware/van_hanh/TC01_Van_hanh/` (hai lõi FreeRTOS, chấm cả v1 và v2, gộp sự kiện, nhật ký mỗi phút, đồng bộ giờ bằng điện thoại và NTP, phép thử đồng nhất tự so trên mạch); `tools/chay_mo_hinh/tach_diem_thiet_bi.py`; `tools/phan_tich/hieu_chinh_troi_gio.py`.
- **Sự cố phần cứng (không do AI):** mạch ESP32-S3 thứ nhất không đọc được flash (11/11); module thẻ thứ nhất không nhận thẻ (12/11).
- **Lỗi của AI phát hiện khi chạy trên mạch thật:**
  - Hướng dẫn nối dây cấp VCC module thẻ từ chân 5Vin; trên mạch S3 thay thế chân này không ra 5 V khi cấp qua USB, nên cả module mới cũng “không nhận”. Phát hiện bằng cách loại trừ (thẻ tốt trên laptop, đã thay dây, đã thay module); chuyển VCC sang 3V3 thì T5 đạt.
  - Firmware vận hành lần đầu không biên dịch: tên hằng `FS` trùng với thư viện hệ thống (đổi thành `TAN_SO`), biến `wifiDangBat` dùng trước khi khai báo.
  - Trang đồng bộ giờ báo “gia tri khong hop le”: độ lệch tính bằng mili giây từ năm 1970 vượt kiểu `long` 32 bit trên ESP32; đổi sang `strtod`. Trang cũng chỉ báo lỗi chung chung, đã sửa để hiện “LỖI:” kèm phản hồi của mạch.
  - Lỗi ghi thẻ khi chạy: ghi vào thư mục con `/tc` thất bại và Wi-Fi phát liên tục gây nhiễu nguồn 3V3. Sửa: ghi ở thư mục gốc, SPI 4 MHz, Wi-Fi chỉ bật theo khung giờ ở 2 dBm (Protocol 16.17).
  - Phép thử đồng nhất (Protocol 7.6) không đạt qua ba bản: (1) bộ lọc MFE lượng tử hoá trên mạch nhưng số thực trên máy tính; (2) khi bỏ esp-dsp để thử, suy luận lên 915 ms; (3) còn lại do nhân ESP-NN: chỉ 27,7% (v1) và 1,7% (v2) cửa sổ lệch ≤ 1 bậc int8. Tắt ESP-NN, giữ esp-dsp và bộ lọc số thực thì mạch báo ĐẠT cả hai mô hình (v2 119/119, lệch lớn nhất 0,0000), suy luận lớn nhất 230 ms.
- **Phép thử đã chạy:** T5 đạt bo mạch, micro, thẻ nhớ trên cả ESP32-S3 (thẻ ở chân 15–18, VCC 3V3) và ESP32 thường; gộp sự kiện trên máy tính 12/12 tình huống khớp `gop_su_kien.py` (`thu/thu_gop.cpp`); `hieu_chinh_troi_gio.py --thu` đạt; đồng bộ giờ bằng điện thoại lệch 0 ms lần đầu; phép thử đồng nhất trên mạch đạt (tệp WAV là dữ liệu mở, không phải âm thanh KTX).
- **Một bài học về quy trình:** có lúc tệp CSV gửi để kiểm tra là bản cũ hoặc rỗng vì thẻ chưa được cắm lại vào mạch; từ đó mạch tự so với điểm tham chiếu và in kết quả ra Serial, không cần chép tệp qua lại.
- **Còn chờ:** 1 giờ tải nhiễu ~75 dB(A), chạy thử 24 giờ tại vị trí lắp (t12); đọc số chính xác của v1 từ `thu_dong_nhat_diem.csv` trên thẻ; firmware ghi WAV cho TC-02 (t10); cập nhật chân 15–18 cho T1–T4 và sơ đồ mạch PDF.
