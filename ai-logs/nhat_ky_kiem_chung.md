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
