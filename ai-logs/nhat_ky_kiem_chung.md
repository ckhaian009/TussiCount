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
