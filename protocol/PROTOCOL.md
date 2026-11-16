# Protocol đăng ký trước – TussiCount

**Ngày đăng ký: 07/11/2026.** Dấu thời gian chính thức là thời điểm commit file này lên kho GitHub công khai `ckhaian009/TussiCount`. Protocol được đăng ký trước khi thu bất kỳ dữ liệu kiểm tra nào. Sau ngày đăng ký, chỉ điền mục 12 (phiên bản đóng băng) và ghi mục 16 (thay đổi, kèm ngày và lý do); không sửa nội dung các mục khác.

## 1. Thông tin chung

| Mục | Nội dung |
| --- | --- |
| Đề tài | TussiCount – Đánh giá độ tin cậy của phép đếm tiếng ho tự động trên thiết bị biên phục vụ giám sát sớm bệnh hô hấp tại ký túc xá |
| Cuộc thi | STEMPETITION 2026–2027 · Tiểu ban Nghiên cứu khoa học · Thử thách 2 – Healthy Living |
| Nhóm thực hiện | Cao Khải An, Nguyễn Phúc Gia Bảo (12T1, Trường THPT FPT Cần Thơ) |
| Giáo viên hướng dẫn | Cô Trương Minh Phương |
| Phê duyệt | Hiệu trưởng Trường THPT FPT Cần Thơ, cô Nguyễn Thị Uyên Thuý; phối hợp: thầy Nguyễn Thành Lượng, GVQN Dorm B2 |

## 2. Câu hỏi nghiên cứu

1. Độ nhạy của phép đếm tiếng ho tự động bằng âm thanh thay đổi thế nào theo khoảng cách, vị trí nguồn ho, độ lớn, mức ồn và loại tiếng ho (phát lại hay ho thật); số phát hiện sai thay đổi thế nào theo mức ồn?
2. Trong điều kiện ký túc xá, phép đếm này có đủ tin cậy để làm tín hiệu giám sát bệnh hô hấp (theo dõi xu hướng ho chung của khu vực, không xác định người bệnh) hay không?

## 3. Giả thuyết

- **H1.** Độ nhạy giảm khi khoảng cách và mức ồn tăng; nguồn ho sau cửa đóng gây mức giảm độ nhạy lớn nhất.
- **H2.** Độ nhạy với tiếng ho thật thấp hơn độ nhạy với tiếng ho phát lại qua loa trong cùng điều kiện.

## 4. Phạm vi

Đề tài đánh giá khả năng phát hiện và đếm sự kiện ho của thiết bị. Đề tài không xác định người bệnh, không chẩn đoán, không xác định danh tính người ho và không theo dõi từng phòng hoặc từng cá nhân. Mọi số liệu chỉ được tổng hợp cho khu hành lang có từ 20 học sinh trở lên.

## 5. Địa điểm, thời gian, thiết bị

- **Địa điểm:** Dorm B2, Ký túc xá Trường THPT FPT Cần Thơ: hành lang tầng 1, hành lang tầng 2 và phòng trống B2.103 (nguồn ho sau cửa đóng).
- **Thời gian:** từ ngày được phê duyệt (dự kiến 10/11/2026) đến hết ngày 16/11/2026. Thiết bị chỉ được lắp sau khi có phê duyệt; dữ liệu chỉ được thu sau khi có phiếu đồng thuận.
- **Thiết bị:** 02 bộ giống nhau. **TC-01** gắn tường hành lang tầng 1, cách cửa phòng B2.103 khoảng 1 m, dùng cho tầng kiểm định 1 và 2. **TC-02** gắn tường hành lang tầng 2, dùng cho ghi âm kiểm định. Mỗi bộ gồm ESP32-S3 N16R8, micro INMP441 (I2S), module microSD, LED báo ghi âm, sạc dự phòng 10.000 mAh, vỏ in 3D; độ cao lắp 1,5–2 m, micro hướng ra hành lang.
- **Hai bản firmware:** bản vận hành không có hàm ghi tệp âm thanh; bản kiểm định ghi WAV 16 kHz, 16 bit lên thẻ nhớ, chỉ dùng trong buổi ghi âm kiểm định.
- **Dụng cụ:** máy đo mức âm UNI-T UT353 (30–130 dB, trọng số A); loa mini nối dây AUX; thước dây; máy tính phát đồng bộ giờ NTP.

## 6. Định nghĩa

| Thuật ngữ | Định nghĩa |
| --- | --- |
| Cửa sổ | Đoạn âm thanh 1 giây, trượt 0,5 giây, lấy mẫu 16 kHz một kênh |
| Sự kiện ho | Chuỗi cửa sổ liền kề có điểm ≥ ngưỡng, gộp thành một sự kiện rồi qua bộ lọc sau phân loại (mục 8); một tràng ho liên tiếp tính là một sự kiện. Thời điểm sự kiện là tâm của cửa sổ có điểm cao nhất |
| Ghép | Mỗi tiếng ho chuẩn ghép với tối đa một sự kiện trong khoảng ±1 giây (ghép một–một, ưu tiên cặp gần nhau nhất) |
| Tiếng ho chuẩn | Tiếng ho có thời điểm đã biết: do trình phát ghi (tầng kiểm định 1), do người quan sát bấm giờ (tầng kiểm định 2), do người gán nhãn đánh dấu (tầng kiểm định 3; các tiếng ho cách nhau dưới 1 giây thuộc cùng một tràng và tính là một tiếng ho chuẩn) |
| Độ nhạy | Số tiếng ho chuẩn được ghép ÷ tổng số tiếng ho chuẩn |
| Phát hiện sai mỗi giờ | Số sự kiện không ghép được với tiếng ho chuẩn ÷ số giờ âm thanh được phân tích |
| Giá trị dự báo dương | Số sự kiện ghép được ÷ tổng số sự kiện thiết bị báo |
| Mức ồn nền | LA90 của từng phút: mức vượt trong 90% thời gian, tính từ mức của các khung 0,5 giây trên tín hiệu đã lọc trọng số A, quy đổi sang dB(A) theo mục 7.5; thiết bị ghi thêm LAeq từng phút |
| Mức tiếng ho tại micro | Mức đỉnh dB(A) đo bằng máy đo mức âm đặt sát micro thiết bị |
| SNR | Mức tiếng ho tại micro − mức ồn nền của phút đó (dB) |
| Đêm D | Từ 18:00 ngày D đến 06:00 ngày D + 1 |

Mỗi sự kiện, thiết bị ghi: thời điểm, độ dài, điểm tin cậy. Mỗi phút, thiết bị ghi: LAeq, LA90, điện áp nguồn, thời gian chạy. Thiết bị vận hành không ghi âm thanh.

## 7. Thiết kế kiểm định

### 7.1. Tầng kiểm định 1 – Phát lại tiếng ho mẫu (H1)

- **Nguồn:** 1.100 bản ghi ho của 714 người trong bộ dữ liệu Coswara (546 ho sâu, 554 ho nông), chỉ lấy bản ghi chất lượng tốt nhất. Mỗi bản ghi gốc chứa nhiều tiếng ho, nên từ mỗi bản ghi chỉ cắt một tiếng ho đơn (tiếng ho chứa khung có mức lớn nhất) bằng thuật toán cố định trong `tools/chuan_bi_phat_lai.py`; đoạn cắt dài 0,21–1,42 giây (trung vị 0,45 giây) và được chuẩn hoá về mức đỉnh −1 dBFS. Thời điểm cắt và mục đích sử dụng của từng tệp được ghi cố định trong `results/coswara_playlist.csv`. Coswara không được dùng khi huấn luyện.
- **Thiết kế:** 3 khoảng cách (1 m, 3 m, 5 m) × 2 vị trí nguồn (hành lang; trong phòng B2.103, cửa đóng) × 3 độ lớn (nhỏ, vừa, lớn) × 2 khung giờ (sinh hoạt ồn 20:30–21:00; yên tĩnh 21:00–21:45) = 36 ô, đo tại TC-01. Khoảng cách là đường thẳng từ loa tới micro; nếu không đặt được đúng mức, ghi khoảng cách thực đo và dùng giá trị đó trong phân tích.
- **Cỡ mẫu và phân bổ:** 1.100 tệp được phân bổ ngẫu nhiên một lần (seed 2026), mỗi tệp cho đúng một mục đích: 1.050 tệp vào 36 ô, gồm hai ô chính *hành lang · vừa · yên tĩnh · 1 m* và *hành lang · vừa · yên tĩnh · 3 m* (n = 100 mỗi ô) và 34 ô còn lại (n = 25 mỗi ô, tối thiểu 20 tiếng ho hợp lệ sau loại trừ); 10 tệp cho kiểm tra đầu buổi; 40 tệp cho so sánh hai thiết bị (mục 7.6). Ô 3 m dùng cho tiêu chí độ nhạy ở mục 9; cả hai ô chính dùng cho H2. Mỗi tệp trong ô chỉ phát một lần.
- **Độ lớn:** mức “vừa” bằng mức đỉnh dB(A) trung bình ở 1 m của 20 tiếng ho nhẹ theo hiệu lệnh của hai thành viên Nhóm (đúng cách thực hiện ở tầng kiểm định 2), đo trước buổi phát đầu tiên và ghi tại mục 12. Ba mức tạo bằng hệ số khuếch đại số của trình phát: lớn 0 dB, vừa −10 dB, nhỏ −20 dB. Âm lượng loa giữ cố định trong cả buổi; đầu buổi, chỉnh âm lượng bằng tệp hiệu chuẩn (tệp đầu tiên của nhóm kiểm tra đầu buổi) sao cho ở mức vừa, mức đỉnh tại 1 m đạt mức mục tiêu.
- **Thực hiện:** 03 buổi tối (dự kiến 12, 13, 14/11/2026). Trong mỗi khung giờ, các khối vị trí – khoảng cách được phát theo thứ tự ngẫu nhiên (seed 2026); trong mỗi khối, ba mức độ lớn xen kẽ ngẫu nhiên theo từng tiếng ho. Các tiếng ho cách nhau 8 giây, đủ để sự kiện của hai tiếng ho liền nhau không gộp vào nhau và không bị ghép nhầm trong dung sai ±1 giây. Trình phát ghi thời điểm phát theo giờ NTP và mở đầu mỗi buổi bằng 3 tiếng bíp đồng bộ.
- **Đo tại chỗ:** đầu mỗi khối, phát tệp hiệu chuẩn 3 lần ở mức vừa và đo mức tiếng ho tại micro. Mức tiếng ho tại micro của từng tiếng ho phát lại = mức đo của tệp hiệu chuẩn trong khối + chênh lệch mức đỉnh trọng số A (tính trên tệp số) giữa tiếng ho đó và tệp hiệu chuẩn + chênh lệch hệ số khuếch đại. Đầu mỗi buổi, đo mức suy hao qua cửa bằng nhiễu hồng phát trong phòng B2.103 khi cửa mở và khi cửa đóng.
- **Kiểm tra đầu buổi:** cùng 10 tệp cố định ở cả ba buổi, phát ở 1 m, hành lang, mức vừa; không tính vào các ô, dùng theo dõi độ ổn định của thiết bị giữa các buổi.

### 7.2. Tầng kiểm định 2 – Tiếng ho thật (H2)

- **Người tham gia:** thành viên Nhóm và học sinh có phiếu đồng thuận ký bởi phụ huynh; mục tiêu 8–10 người. Không mời học sinh đang đau họng, bị hen hoặc mắc bệnh hô hấp. Người tham gia được ghi bằng mã số (NTG01, NTG02…).
- **Thực hiện:** 01 buổi khoảng 30 phút, 21:00–21:30 trong buổi phát lại ngày 13/11/2026 (dự kiến), tại hành lang tầng 1, cùng vị trí với hai ô chính. Mỗi người tạo 10 tiếng ho nhẹ theo hiệu lệnh ở 1 m và 10 tiếng ở 3 m, cách nhau ít nhất 8 giây. Người quan sát thứ nhất bấm giờ bằng trang bấm giờ đã đồng bộ giờ; người quan sát thứ hai ghi mức đỉnh dB(A) của từng tiếng ho bằng máy đo đặt sát micro. Không ghi âm.

### 7.3. Tầng kiểm định 3 – Tiếng ho tự nhiên và phát hiện sai

- **Ghi âm kiểm định (TC-02):** tổng thời lượng không quá 08 giờ, kết thúc trước 00:00 ngày 13/11/2026; thông báo trước 24 giờ và có biển “Đang ghi âm”.
  - **Phần để sửa:** 3 giờ, tối 11/11, 19:00–22:00; không dùng để chấm. Chạy qua thư viện của mô hình nền trên máy tính để xác định loại âm thanh gây phát hiện sai, chọn bộ lọc sau phân loại và chọn ngưỡng (mục 8).
  - **Phần để chấm:** 4,5 giờ, tối 12/11, 17:55–20:25 và 21:50–23:50 (không trùng khung phát tiếng ho mẫu); chỉ chạy **một lần** qua thư viện của mô hình đã đóng băng trên máy tính, cùng mã xử lý với firmware (đã qua phép thử đồng nhất).
- **Gán nhãn đầy đủ:** 2 giờ của phần để chấm, gồm bốn đoạn 30 phút chọn ngẫu nhiên (seed 2026). Người gán nhãn không xem kết quả của thiết bị. Hai người gán độc lập cùng 30 phút đầu tiên và tính F1 đồng thuận (dung sai ±0,5 giây); nếu F1 < 0,80, thống nhất lại quy ước và gán lại đoạn đó.
- **Xác minh mù cho phần còn lại (2,5 giờ):** mỗi sự kiện thiết bị báo được cắt thành đoạn 3 giây; trộn với số đoạn 3 giây lấy ngẫu nhiên bằng như vậy; người gán nhãn đánh dấu từng đoạn là ho hay không mà không biết đoạn nào do thiết bị báo.
- **Chỉ số:** phát hiện sai mỗi giờ trên toàn bộ 4,5 giờ; độ nhạy và giá trị dự báo dương với tiếng ho tự nhiên trên 2 giờ gán nhãn đầy đủ (thăm dò, báo cáo kèm n).
- **Xoá:** toàn bộ tệp ghi âm được xoá chậm nhất ngày 14/11/2026 trước sự chứng kiến của giáo viên hướng dẫn, có biên bản. Chỉ giữ bảng thời điểm và nhãn dạng số.

### 7.4. Đối chứng âm (không ghi âm)

Trong giờ học các ngày thường (08:00–11:00 và 13:30–16:00), khi KTX gần như vắng, mọi sự kiện thiết bị ghi nhận được tính là phát hiện sai. Chỉ số này là cận trên của phát hiện sai khi vắng người, vì có thể có một số ít tiếng ho thật. Dùng làm số liệu bổ sung, không thay thế tiêu chí ở mục 9.

### 7.5. Hiệu chuẩn mức âm

Đặt máy đo mức âm sát micro; phát nhiễu hồng ở ít nhất 5 mức trong khoảng 45–85 dB(A), mỗi mức 30 giây; ghi đồng thời LAeq của thiết bị (dBFS) và của máy đo (dB(A)). Lập phương trình hồi quy tuyến tính dB(A) theo dBFS cho từng thiết bị; báo cáo hệ số, R² và sai số dư lớn nhất. Mọi mức ồn trong phân tích được quy đổi bằng phương trình của đúng thiết bị đó.

### 7.6. Kiểm tra thiết bị

- **Trước khi lắp:** cùng một tệp WAV cho điểm gần nhau trên Edge Impulse và trên thiết bị; mỗi lần suy luận dưới 500 ms; chạy liên tục 24 giờ bằng sạc dự phòng không treo, không tràn bộ nhớ, giờ lệch không quá 1 giây.
- **Sau khi tháo gỡ (17/11):** đặt TC-01 và TC-02 cạnh nhau, phát 40 tệp của nhóm so sánh hai thiết bị ở 1 m, mức vừa, hai lần; tính độ nhạy từng thiết bị, hệ số kappa giữa hai thiết bị và giữa hai lần phát.

### 7.7. Đối chiếu bên ngoài (thăm dò)

- **Khảo sát hằng ngày** “Hôm nay bạn có ho không?”: ẩn danh, 21:00–23:00 mỗi tối, từ ngày được phê duyệt đến 16/11/2026; ghép khảo sát tối D với đêm D.
- **Sĩ số có mặt** mỗi tối do GVQN Dorm B2 cung cấp (chỉ con số tổng), dùng làm mẫu số.
- **Khảo sát thói quen khai báo triệu chứng hô hấp** (một lần, khoảng 100 phiếu): chỉ dùng mô tả bối cảnh vấn đề, không dùng để kiểm định H1, H2.

## 8. Mô hình và đóng băng

- **Dữ liệu huấn luyện:** COUGHVID 3.0 (3.000 bản ghi có `cough_detected` ≥ 0,8, chọn ngẫu nhiên, seed 2026; danh sách tại `results/coughvid_chon_3000.csv`); ESC-50 (bỏ lớp `coughing`); Common Voice tiếng Việt (1.000 đoạn từ 229 người). Không dùng Coswara, phần để sửa và phần để chấm.
- **Mẫu âm khó:** nếu phần để sửa cho thấy một loại âm thanh gây nhiều phát hiện sai, mô hình được huấn luyện lại với thêm mẫu cùng loại lấy từ dữ liệu mở (ESC-50, Common Voice). Âm thanh ghi tại KTX không được tải lên Edge Impulse hay bất kỳ dịch vụ trực tuyến nào.
- **Mô hình:** Edge Impulse, khối MFE và mạng nơ-ron phân loại hai nhãn `cough` / `noise`, lượng tử hoá int8, chạy trên ESP32-S3.
- **Bộ lọc sau phân loại:** số cửa sổ liền kề tối thiểu của một sự kiện (1 hoặc 2) và khoảng nghỉ tối thiểu giữa hai sự kiện (0; 0,5 hoặc 1 giây), chọn trên phần để sửa cùng với ngưỡng.
- **Chọn ngưỡng:** với mỗi tổ hợp ngưỡng và bộ lọc, tính phát hiện sai mỗi giờ trên phần để sửa (nghe xác minh từng sự kiện thiết bị báo) và độ nhạy trên tập kiểm tra của dữ liệu mở; chọn tổ hợp có độ nhạy cao nhất trong các tổ hợp có phát hiện sai ≤ 4 sự kiện mỗi giờ; lưu toàn bộ đường cong ngưỡng. Nếu không có phần để sửa, thay bằng số liệu đối chứng âm (mục 7.4) và ghi tại mục 16.
- **Đóng băng:** firmware, mô hình, bộ lọc và ngưỡng được đóng băng trước khi chạy bất kỳ dữ liệu nào của phần để chấm, tầng kiểm định 1 hoặc 2 (dự kiến sáng 12/11/2026); phiên bản và SHA-256 được ghi tại mục 12 bằng một commit riêng. Sau đó không chỉnh sửa cho đến khi chấm xong.

## 9. Tiêu chí chính

| Đầu ra | Phân tích | Tiêu chí |
| --- | --- | --- |
| Độ nhạy ô chính (hành lang · 3 m · vừa · yên tĩnh) | Tỉ lệ kèm khoảng tin cậy Wilson 95% | Cận dưới ≥ 70% |
| Phát hiện sai | Trên phần để chấm; khoảng tin cậy Poisson chính xác 95% | Ước lượng điểm ≤ 4 sự kiện mỗi giờ |
| H1 | Hồi quy logistic trên 1.050 tiếng ho trong ô ở tầng 1: biến phụ thuộc là được ghép (0/1); biến giải thích: khoảng cách (m), vị trí nguồn, độ lớn (dB(A) ở 1 m), mức ồn nền (dB(A)), loại ho Coswara (sâu/nông), buổi phát; sai số chuẩn hiệu chỉnh theo người trong Coswara | Ủng hộ khi đồng thời: (a) hệ số khoảng cách và mức ồn âm, khoảng tin cậy 95% nằm dưới 0; (b) tại điều kiện tham chiếu (hành lang, 3 m, vừa, mức ồn trung vị của khung yên tĩnh), mức giảm độ nhạy dự đoán khi chuyển nguồn vào sau cửa đóng lớn hơn mức giảm khi chuyển từng yếu tố còn lại từ mức thuận lợi nhất đến bất lợi nhất (khoảng cách 1 → 5 m; độ lớn lớn → nhỏ; mức ồn trung vị khung yên tĩnh → trung vị khung ồn) |
| H2 | Chênh lệch độ nhạy (tầng 2 − tầng 1) ở cùng điều kiện (hành lang, yên tĩnh, 1 m và 3 m, mức vừa); khoảng tin cậy 95% bằng bootstrap 10.000 lần, lấy mẫu lại theo người ở cả hai tầng | Ủng hộ khi khoảng tin cậy nằm hoàn toàn dưới 0. Nếu tầng 2 có dưới 6 người, H2 được báo cáo là thăm dò |
| Vận hành | Tỉ lệ thời gian hoạt động = số phút có bản ghi ÷ số phút lắp đặt | ≥ 95% |
| Câu hỏi 2 | | “Đủ tin cậy” khi đạt đồng thời hai dòng đầu; nếu không, báo cáo tiêu chí nào chưa đạt |

Mọi kết quả, kể cả không đạt tiêu chí hoặc bác bỏ giả thuyết, đều được báo cáo đầy đủ.

## 10. Phân tích phụ (đăng ký trước, không đặt ngưỡng)

1. **Đường cong phát hiện theo SNR:** hồi quy logistic độ nhạy theo SNR trên tiếng ho tầng 1 ở vị trí hành lang; báo cáo SNR50 và SNR80 (SNR tại độ nhạy 50% và 80%) kèm khoảng tin cậy bootstrap.
2. **Cơ chế ảnh hưởng của cánh cửa:** thêm biến vị trí nguồn vào mô hình SNR. Nếu khoảng tin cậy của hệ số vị trí chứa 0, ảnh hưởng của cánh cửa phù hợp với cơ chế suy hao mức âm; nếu khoảng tin cậy nằm dưới 0, cánh cửa còn làm giảm độ nhạy ngoài phần suy hao (do thay đổi phổ tiếng ho). Báo cáo kèm mức suy hao qua cửa đo bằng nhiễu hồng.
3. **H2 có hiệu chỉnh độ lớn:** hồi quy logistic trên dữ liệu gộp của hai ô chính và tầng 2, biến giải thích là loại nguồn (thật / phát lại) và SNR; so sánh với kết quả H2 chính.
4. **Bán kính phát hiện:** từ đường cong SNR, mức tiếng ho vừa và mức ồn nền đo được theo khung giờ, ước lượng khoảng cách lớn nhất tại đó độ nhạy dự đoán ≥ 70%.
5. **Mức tăng nhỏ nhất phát hiện được:** mô phỏng chuỗi đếm mỗi đêm = Poisson(độ nhạy × số tiếng ho thật + phát hiện sai mỗi giờ × 12 giờ), với số tiếng ho thật nền 20, 50, 100 mỗi đêm; tính mức tăng tương đối nhỏ nhất mà phép thử một phía (α = 0,05) phát hiện được với xác suất 80% sau 1 và 3 đêm, dùng độ nhạy và phát hiện sai đo được.
6. **Phân loại lỗi:** tỉ lệ phát hiện sai theo loại âm thanh (nói chuyện, cười, đóng cửa, bước chân, hắng giọng, hắt hơi, khác) trên phần để chấm.
7. **Độ ổn định và độ lặp lại:** độ nhạy của kiểm tra đầu buổi qua ba buổi; kappa giữa hai thiết bị và giữa hai lần phát (mục 7.6).
8. **Tương quan với tự báo cáo:** Spearman giữa tỉ lệ tự báo có ho và số sự kiện trên 100 học sinh-đêm theo ngày, kèm khoảng tin cậy bootstrap 95% và số ngày sử dụng.
9. **Phát hiện sai khi vắng người:** từ đối chứng âm (mục 7.4), kèm khoảng tin cậy Poisson.

## 11. Cỡ mẫu và độ chính xác dự kiến

- Ô chính, n = 100: nếu độ nhạy đo được 80%, khoảng tin cậy Wilson 95% là 71,1–86,7%. Tiêu chí cận dưới ≥ 70% đạt khi độ nhạy đo được khoảng 79% trở lên.
- Phát hiện sai, 4,5 giờ: nếu đếm được 18 sự kiện sai (4,0 mỗi giờ), khoảng tin cậy Poisson 95% là 2,4–6,3 mỗi giờ. Đối chứng âm bổ sung khoảng 22 giờ quan sát mỗi thiết bị (4 ngày học 11, 12, 13, 16/11 × 5,5 giờ).
- H2: 8–10 người × 20 tiếng ho (160–200 tiếng ho). Khi tính đến tương quan giữa các tiếng ho của cùng một người, thiết kế đủ để phát hiện chênh lệch khoảng 15–20 điểm phần trăm; chênh lệch nhỏ hơn được báo cáo là chưa đủ bằng chứng.

## 12. Phiên bản đóng băng (điền trước khi chấm)

| Mục | Giá trị |
| --- | --- |
| Mức “vừa” (dB(A) đỉnh ở 1 m) | |
| Ngày, giờ đóng băng | |
| Firmware bản vận hành (tên tệp, SHA-256) | |
| Mô hình (phiên bản Edge Impulse) | |
| Ngưỡng · bộ lọc sau phân loại | |
| Commit ghi nhận | |

## 13. Dữ liệu thiếu và loại trừ

- Khoảng thiết bị mất nguồn, treo hoặc lệch giờ quá 1 giây được ghi lại và loại khỏi phân tích, không nội suy.
- Tiếng ho gán nhãn `?` bị loại khỏi phân tích chính; số lượng được báo cáo.
- Tiếng ho phát lại bị gián đoạn (người đi qua, loa lỗi) được đánh dấu trong nhật ký phát lại và loại khỏi phân tích; số lượng được báo cáo.
- Phát hiện sai ở phần để chấm loại các khoảng ±5 phút quanh thời gian phát tiếng ho mẫu ở tầng 1, nếu có.
- Khảo sát hằng ngày: loại tối có dưới 05 câu trả lời và tối có số câu trả lời vượt sĩ số có mặt.

## 14. Đạo đức và bảo vệ dữ liệu

- Thiết bị vận hành không lưu âm thanh; mã nguồn bản vận hành được công khai trên GitHub.
- Tệp ghi âm kiểm định: chỉ ba người được tiếp cận (Cao Khải An, Nguyễn Phúc Gia Bảo, cô Trương Minh Phương); lưu trên thẻ nhớ riêng có mật khẩu; chỉ xử lý trên máy tính của Nhóm; không lưu trên điện thoại, không tải lên mạng hay dịch vụ trực tuyến nào (kể cả Edge Impulse); xoá chậm nhất 14/11/2026, có biên bản.
- Khảo sát ẩn danh: không thu họ tên, lớp, phòng, khu vực hay email; bảng trả lời gốc xoá chậm nhất 17/11/2026.
- Không sử dụng số liệu để quản lý giờ giấc, nề nếp hoặc xử lý kỷ luật. Không tệp âm thanh nào được đẩy lên GitHub.

## 15. Lịch dự kiến

Các ngày từ 10/11 giả định được phê duyệt ngày 10/11/2026; nếu phê duyệt muộn hơn, lịch được dời tương ứng và ghi tại mục 16. Thứ tự bắt buộc: đăng ký protocol → thu phần để sửa → đóng băng → thu và chấm dữ liệu kiểm tra → xoá ghi âm.

| Ngày | Nội dung |
| --- | --- |
| 07/11 | Đăng ký protocol |
| 08–09/11 | Đo mức đỉnh tiếng ho thật của hai thành viên (mức vừa); huấn luyện mô hình nền; kiểm tra thiết bị trước khi lắp |
| 10/11 | Phê duyệt; phát phiếu đồng thuận; lắp TC-01, TC-02; bắt đầu khảo sát hằng ngày |
| 11/11 | Hiệu chuẩn mức âm; bắt đầu đối chứng âm; tối: phần để sửa (19:00–22:00) |
| 12/11 | Sáng: bổ sung mẫu âm khó từ dữ liệu mở (nếu cần), chọn bộ lọc và ngưỡng, đóng băng; tối: phát lại buổi 1; phần để chấm (17:55–20:25, 21:50–23:50) |
| 13/11 | Gán nhãn, xác minh mù; chấm phần để chấm một lần; tối: phát lại buổi 2, tầng kiểm định 2 |
| 14/11 | Xoá toàn bộ tệp ghi âm (có biên bản); tối: phát lại buổi 3 |
| 15/11 | Phân tích chính và phân tích phụ |
| 16/11 | Đêm đếm cuối |
| 17/11 | Tháo gỡ thiết bị; kiểm tra hai thiết bị cạnh nhau; xoá bảng khảo sát gốc |

## 16. Thay đổi sau đăng ký

Các thay đổi 16.1–16.12 được đăng ký ngày 08/11/2026, trước khi thu bất kỳ dữ liệu nào (chưa có phê duyệt, chưa lắp thiết bị). Chúng chỉ bổ sung phép đo, quy trình và phân tích phụ; câu hỏi nghiên cứu, giả thuyết và tiêu chí chính ở mục 9 giữ nguyên.

| # | Ngày | Thay đổi | Lý do |
| --- | --- | --- | --- |
| 16.1 | 08/11/2026 | Thêm sai số số đếm và F1 | Thiết bị dùng để đếm; bỏ sót và phát hiện sai có thể bù trừ nhau, nên cần đánh giá trực tiếp sai số của số đếm |
| 16.2 | 08/11/2026 | Thêm độ đặc hiệu theo đoạn 3 giây | Chỉ số quen thuộc khi đánh giá thiết bị y sinh; phát hiện sai mỗi giờ vẫn là tiêu chí chính |
| 16.3 | 08/11/2026 | Thêm đường cong phát hiện trên phần để chấm (mô tả) | Cho thấy đánh đổi độ nhạy – phát hiện sai quanh ngưỡng đã đóng băng; không dùng để chọn lại ngưỡng |
| 16.4 | 08/11/2026 | Thêm quy tắc cảnh báo định trước và mô phỏng | Trả lời câu hỏi 2 ở mức vận hành: tần suất cảnh báo sai và tốc độ phát hiện mức tăng |
| 16.5 | 08/11/2026 | Mở rộng nhật ký vận hành, quy trình thay nguồn, phép thử tải | Định lượng độ bền vận hành bằng số liệu thay cho nhận định |
| 16.6 | 08/11/2026 | Bù độ trễ hệ thống trước khi ghép | Dung sai ghép ±1 giây chỉ có nghĩa khi không có độ lệch hệ thống |
| 16.7 | 08/11/2026 | Tăng cường dữ liệu bằng vang tổng hợp | Giảm khác biệt giữa dữ liệu huấn luyện (thu gần, ít vang) và hành lang |
| 16.8 | 08/11/2026 | Cân bằng khuếch đại giữa hai thiết bị | Hai micro có sai số sản xuất; đầu vào của mô hình phải tương đương giữa TC-01 và TC-02 |
| 16.9 | 08/11/2026 | Đo phổ suy hao qua cửa và thời gian vang (khám phá) | Kiểm chứng trực tiếp cơ chế của cánh cửa (mục 10.2) và mô tả môi trường để đánh giá tính khái quát |
| 16.10 | 08/11/2026 | Thêm tổng thời lượng ho mỗi đêm (khám phá) | Một tràng ho dài và một tiếng ho ngắn cùng được tính là một sự kiện |
| 16.11 | 08/11/2026 | Thêm đối chiếu thời tiết và số lượt khám hô hấp (mô tả) | Bối cảnh để diễn giải chuỗi đếm theo ngày |
| 16.12 | 08/11/2026 | Quy tắc bảo vệ riêng tư khi gán nhãn | Người gán nhãn có thể nghe thấy hội thoại riêng tư |
| 16.14 | 12/11/2026 | Dời lịch thu dữ liệu | Mạch ESP32-S3 thứ nhất hỏng chip flash (11/11), module thẻ nhớ hỏng (12/11); chưa thu dữ liệu nào |
| 16.15 | 12/11/2026 | Bốn đêm đếm 13–16/11; ghi điểm mọi cửa sổ của cả hai mô hình | Đêm 13 diễn ra trước khi chọn mô hình và đóng băng ngưỡng; số đếm mọi đêm tính bằng cùng một mô hình và ngưỡng đã đóng băng |
| 16.16 | 12/11/2026 | Đồng bộ giờ bằng điện thoại qua Wi-Fi của mạch; hiệu chỉnh trôi giờ | Không có Wi-Fi Internet ổn định suốt đêm tại KTX |
| 16.17 | 12/11/2026 | Thay phần cứng: TC-01 dùng mạch ESP32-S3 thay thế, thẻ nhớ ở chân 15–18 (VCC 3V3); TC-02 dùng mạch ESP32 thường; Wi-Fi theo khung giờ; cấu hình thư viện mô hình để đạt phép thử đồng nhất | Hỏng phần cứng (16.14); phép thử 7.6 |
| 16.18 | 12/11/2026 | Đối chứng âm còn 3 ngày học (13, 16, 17/11); chạy thử 24 giờ tại vị trí lắp | Mất ngày 11 và 12/11 do hỏng thiết bị; giữ được ngày 13/11 mà không cần ghi âm |
| 16.19 | 12/11/2026 | Ngày xoá tệp ghi âm kiểm định dời đến chậm nhất 17/11/2026 | Phần để chấm ghi tối 16/11 |
| 16.20 | 12/11/2026 | TC-02 không lắp LED báo ghi âm; trạng thái ghi báo bằng biển 2 | Đơn giản hoá phần cứng; biển 2 đã thông báo việc ghi âm |
| 16.21 | 12/11/2026 | Tệp phát của phép thử tải: tiếng nói Common Voice trộn âm thanh môi trường ESC-50 thay cho “nhạc và tiếng nói” | Máy không có bộ nhạc dữ liệu mở |
| 16.22 | 16/11/2026 | Một thiết bị (TC-01) luân phiên đếm và ghi âm; lịch thu dữ liệu 15–18/11; mức phát tầng 1 thấp hơn thiết kế; chọn khối gán nhãn | Phép thử 24 giờ lần 1 không đạt; TC-02 không dùng; loa tối đa 76 dB(A) ở 1 m; thành viên ở trường 19:00–20:30 |

### 16.1. Sai số số đếm và F1

Trên 2 giờ gán nhãn đầy đủ của phần để chấm, chia thành 24 khoảng 5 phút; mỗi khoảng có số sự kiện thiết bị báo (D) và số tiếng ho chuẩn (R). Báo cáo: sai lệch trung bình (D − R); sai số tuyệt đối trung bình MAE = trung bình |D − R|; sai số tương đối của tổng số đếm (ΣD − ΣR) ÷ ΣR, kèm khoảng tin cậy bootstrap 95% (10.000 lần, lấy mẫu lại theo khoảng 5 phút); F1 = 2 × độ nhạy × giá trị dự báo dương ÷ (độ nhạy + giá trị dự báo dương).

### 16.2. Độ đặc hiệu theo đoạn 3 giây

Trong xác minh mù (mục 7.3), các đoạn 3 giây chọn ngẫu nhiên được người gán nhãn đánh dấu là không có tiếng ho tạo thành mẫu âm. Độ đặc hiệu = số đoạn trong mẫu âm không trùng sự kiện nào của thiết bị ÷ tổng số đoạn trong mẫu âm, kèm khoảng tin cậy Wilson 95%.

### 16.3. Đường cong phát hiện trên phần để chấm

Lần chạy duy nhất qua thư viện của mô hình đã đóng băng (mục 7.3) lưu điểm của mọi cửa sổ. Trên 2 giờ gán nhãn đầy đủ, vẽ độ nhạy theo phát hiện sai mỗi giờ khi thay ngưỡng (giữ nguyên bộ lọc đã đóng băng) và đánh dấu điểm của ngưỡng đã đóng băng. Đường cong chỉ để mô tả; ngưỡng không được chọn lại.

### 16.4. Quy tắc cảnh báo

Quy tắc định trước: đêm D phát cảnh báo khi số sự kiện của đêm D lớn hơn phân vị 99% của phân phối Poisson có trung bình bằng số sự kiện trung bình của 3 đêm hợp lệ liền trước, quy đổi theo sĩ số có mặt (trung bình = tỉ lệ sự kiện trên mỗi học sinh của 3 đêm đó × sĩ số đêm D). Quy tắc được đánh giá bằng mô phỏng (10.000 chuỗi mỗi kịch bản), dùng độ nhạy và phát hiện sai mỗi giờ đo được, với số tiếng ho thật nền 20, 50, 100 mỗi đêm: (a) số cảnh báo sai kỳ vọng trong 30 đêm không có thay đổi; (b) xác suất cảnh báo và số đêm trễ trung bình khi số tiếng ho thật tăng bền vững 50%, 100%, 200%. Quy tắc được áp dụng lên chuỗi đếm thật chỉ để mô tả, không suy luận.

### 16.5. Nhật ký vận hành, thay nguồn, phép thử tải

- **Nhật ký mỗi phút** của firmware vận hành ghi thêm: nhiệt độ chip, bộ nhớ trống nhỏ nhất (heap, PSRAM), thời gian suy luận lớn nhất trong phút, số khung âm thanh bị mất (tràn bộ đệm I2S), thời điểm đồng bộ NTP thành công gần nhất và độ lệch đo được khi đồng bộ. Đồng bộ NTP mỗi 30 phút. Firmware kiểm định ghi số khung bị mất của mỗi buổi; khoảng có mất khung được xử lý như mục 13.
- **Báo cáo:** số lần gián đoạn và thời gian trung bình giữa hai lần gián đoạn (MTBF = tổng giờ-thiết bị ÷ số lần gián đoạn); khi không có gián đoạn, báo cáo cận dưới 95% của MTBF là T/3 (T = tổng giờ-thiết bị, giả định phân phối mũ); tỉ lệ gói tổng hợp 10 phút nhận được trên Google Sheets (số liệu chính lấy từ thẻ nhớ, không phụ thuộc mạng); phân bố thời gian suy luận lớn nhất mỗi phút; tổng số khung bị mất; khoảng nhiệt độ chip.
- **Thay nguồn:** đổi sạc dự phòng đã sạc đầy mỗi ngày lúc 17:00. Thời gian thay được tính là thời gian không hoạt động, không loại khỏi mẫu số của tỉ lệ thời gian hoạt động.
- **Phép thử tải** (bổ sung mục 7.6, trước khi lắp): trong 24 giờ chạy thử có 1 giờ phát liên tục nhạc và tiếng nói từ dữ liệu mở, khoảng 75 dB(A) tại 1 m. Đạt khi thời gian suy luận lớn nhất dưới 500 ms, không mất khung, không khởi động lại.

### 16.6. Bù độ trễ hệ thống

Ở mỗi buổi phát lại, tính trung vị của (thời điểm sự kiện − thời điểm phát) trên 10 tiếng ho kiểm tra đầu buổi (không thuộc các ô). Nếu trung vị lệch quá 0,3 giây, trừ giá trị đó khỏi thời điểm sự kiện của buổi trước khi ghép; tầng kiểm định 2 dùng giá trị của buổi phát lại cùng tối. Tầng kiểm định 3 không bù vì thời điểm lấy trực tiếp trên tệp WAV. Độ trễ đo được được báo cáo.

### 16.7. Tăng cường dữ liệu bằng vang tổng hợp

Tiếng ho COUGHVID được tích chập với đáp ứng xung phòng tổng hợp (phòng hình hộp, thời gian vang 0,3–1,2 giây, khoảng cách nguồn 1–5 m, tạo trên máy tính bằng pyroomacoustics) rồi trộn nhiễu từ dữ liệu mở ở SNR 0–20 dB. Không dùng âm thanh ghi tại KTX. Mô hình có và không có tăng cường được so sánh trước khi đóng băng: chọn phiên bản có độ nhạy cao hơn trên tập kiểm tra của dữ liệu mở đã qua cùng phép vang và trộn nhiễu, trong điều kiện phát hiện sai trên phần để sửa ≤ 4 sự kiện mỗi giờ. Phiên bản được chọn ghi tại 16.13.

### 16.8. Cân bằng khuếch đại giữa hai thiết bị

Sau hiệu chuẩn (mục 7.5), đặt hệ số khuếch đại số cho từng thiết bị sao cho cùng một mức nhiễu hồng cho mức dBFS chênh nhau không quá 1 dB giữa TC-01 và TC-02; tín hiệu sau khuếch đại được chặn trong giới hạn 16 bit. Hệ số đóng băng cùng firmware, ghi tại 16.13; phương trình hiệu chuẩn được hiệu chỉnh tương ứng (cộng 20·log10 của hệ số).

### 16.9. Phổ suy hao qua cửa và thời gian vang (khám phá)

Một buổi đo ngày 11/11/2026, 18:15–18:30 (dời từ 16:00–16:15 ngày 11/11, trước khi đo), ngoài khung đối chứng âm và trước phần để sửa (19:00). Giờ này KTX có người nên nhắc học sinh tránh hành lang tầng 1 trong lúc nổ bóng bay; tiếng ồn lẫn vào được ghi trong nhật ký đo. TC-02 chạy firmware kiểm định, đặt tạm sát cạnh TC-01.

- **Phổ suy hao qua cửa:** nhiễu hồng phát từ vị trí loa cố định trong phòng B2.103, 30 giây khi cửa mở và 30 giây khi cửa đóng. Suy hao theo từng dải 1/3 octave từ 125 Hz đến 8 kHz = mức khi cửa mở − mức khi cửa đóng.
- **Thời gian vang:** 3 tiếng nổ bóng bay tại hành lang tầng 1 (cách thiết bị 3 m) và 3 tiếng trong phòng B2.103; tính T20 bằng tích phân ngược Schroeder, báo cáo trung vị theo dải octave 500 Hz–4 kHz.

Buổi đo được thông báo và có biển “Đang ghi âm” như buổi ghi âm kiểm định; thời lượng ghi tối đa 15 phút, tính vào giới hạn 08 giờ (tổng 7,75 giờ). Tệp được xử lý và xoá như tệp ghi âm kiểm định.

### 16.10. Tổng thời lượng ho mỗi đêm (khám phá)

Mỗi đêm, tính tổng độ dài các sự kiện (giây) trên 100 học sinh-đêm; báo cáo cùng số sự kiện và hệ số Spearman giữa hai chuỗi. Độ phân giải của độ dài sự kiện là 0,5 giây.

### 16.11. Đối chiếu thời tiết và số lượt khám hô hấp (mô tả)

Nhiệt độ trung bình và độ ẩm tương đối theo ngày tại Cần Thơ, lấy từ nguồn công khai (Open-Meteo). Nếu phòng y tế đồng ý, số lượt học sinh Dorm B2 đến phòng y tế vì triệu chứng hô hấp mỗi ngày (chỉ con số tổng, không danh tính). Hai chuỗi này được trình bày cùng chuỗi đếm theo ngày, không kiểm định thống kê vì chỉ có tối đa 7 ngày.

### 16.12. Bảo vệ riêng tư khi gán nhãn

Người gán nhãn chỉ quyết định có hay không có tiếng ho và đánh dấu thời điểm. Không chép lại, ghi chú, trao đổi hoặc trích dẫn nội dung lời nói; đoạn có hội thoại riêng tư chỉ được nghe đủ để quyết định có tiếng ho hay không. Không giữ, chia sẻ hoặc dùng bất kỳ đoạn âm thanh nào trong báo cáo hay slide. Các đoạn 3 giây dùng cho xác minh mù được xoá cùng tệp gốc chậm nhất ngày 14/11/2026.

### 16.13. Giá trị bổ sung khi đóng băng (điền trước khi chấm)

| Mục | Giá trị |
| --- | --- |
| Hệ số khuếch đại số TC-01 · TC-02 | |
| Phiên bản mô hình (có / không tăng cường vang) | |
| Tham số tăng cường (thời gian vang, khoảng SNR) | |

### 16.14. Lịch thu dữ liệu sau khi hỏng thiết bị

Ngày 11/11, mạch ESP32-S3 thứ nhất kết nối được nhưng không đọc, ghi được chip nhớ flash, kể cả khi đã tháo hết dây; ngày 12/11, module thẻ nhớ của mạch thay thế không nhận thẻ (thẻ đọc tốt trên máy tính, đúng FAT32, đã thay dây và đổi chân). Đến thời điểm ghi mục này, chưa có dữ liệu nào được thu: chưa ghi âm, chưa đếm, chưa phát lại. Thứ tự bắt buộc ở mục 15 giữ nguyên; lịch mới:

| Ngày | Nội dung |
| --- | --- |
| 12/11 tối | Nạp firmware vận hành vào TC-01; 1 giờ tải nhiễu khoảng 75 dB(A) trên bàn (16.5); gắn TC-01 tại vị trí lắp, dán biển 1 |
| 12/11 tối → 13/11 tối | Chạy thử 24 giờ (mục 7.6) **tại vị trí lắp** (thiết bị vận hành không ghi âm). Đêm 12 không tính là đêm đếm |
| 13/11 | Đối chứng âm 08:00–11:00, 13:30–16:00 bằng TC-01 đang chạy thử (không ghi âm; số đếm tính sau khi đóng băng từ tệp điểm); hiệu chuẩn mức âm, đo mức “vừa”; đo âm học 16.9 lúc 18:15–18:30; **phần để sửa 19:00–22:00**; **đêm đếm 13** nếu chạy thử đạt |
| 14/11 | Chọn ngưỡng, bộ lọc và mô hình (mục 8, 16.7); **đóng băng 12:00**; tầng 1 buổi 1 (20:30–21:45); đêm đếm 14 |
| 15/11 | Tầng 1 buổi 2; đêm đếm 15 |
| 16/11 | Đối chứng âm; tầng 2 (17:00–17:45); **phần để chấm 17:55–20:25 và 21:50–23:50**; tầng 1 buổi 3 (20:30–21:45, nằm giữa hai phần để chấm như thiết kế ban đầu); đêm đếm 16 |
| 17/11 | Gán nhãn, xác minh mù, chấm phần để chấm một lần; xoá toàn bộ tệp ghi âm (có biên bản); đối chứng âm; phân tích; tháo gỡ thiết bị sau 16:00 và kiểm tra hai thiết bị cạnh nhau |

Thời lượng ghi âm giữ nguyên (3 giờ để sửa, 4,5 giờ để chấm, tối đa 15 phút đo âm học), kết thúc trước 00:00 ngày 17/11. Tầng 1 có hai buổi rơi vào cuối tuần; mức ồn nền đo được của từng ô vẫn là biến liên tục trong H1. Tầng 2 dời từ 21:00–21:30 ngày 13/11 sang 17:00–17:45 ngày 16/11, cùng vị trí và cách làm, bù độ trễ bằng giá trị của buổi phát lại cùng tối (16.6).

### 16.15. Đêm đếm và cách tính số đếm

Bốn đêm đếm: 13, 14, 15, 16/11 (Đêm D theo mục 6). Số đếm chỉ báo cáo cho hành lang tầng 1 (TC-01, 20 học sinh, đủ ngưỡng mục 4); TC-02 ở tầng 2 (18 học sinh) chỉ dùng cho ghi âm kiểm định, không báo cáo số đếm của tầng 2.

Firmware vận hành chấm mọi cửa sổ bằng cả hai mô hình (v1 = Impulse #2, v2 = Impulse #3 có tăng cường vang) và ghi điểm của mọi cửa sổ ra thẻ (không ghi âm thanh). Số đếm chính của **mọi** đêm, kể cả đêm 13 diễn ra trước khi đóng băng, được tính lại sau khi đóng băng từ tệp điểm, bằng mô hình được chọn theo 16.7 cùng ngưỡng và bộ lọc đã đóng băng (`tools/chay_mo_hinh/tach_diem_thiet_bi.py` → `gop_su_kien.py`, cùng định nghĩa sự kiện với firmware; logic gộp của firmware khớp 12/12 tình huống thử). Sự kiện do thiết bị tự gộp trong đêm chỉ dùng theo dõi vận hành. Mọi sự kiện trong khung phát lại tầng 1 và tầng 2 bị loại khỏi số đếm đêm. Quy tắc cảnh báo (16.4) có đủ 3 đêm nền và 1 đêm áp dụng mô tả (đêm 16).

### 16.16. Đồng bộ giờ bằng điện thoại và hiệu chỉnh trôi giờ

Mạch tự phát Wi-Fi; điện thoại kết nối và đồng bộ giờ qua trang của mạch (8 lần đo khứ hồi, lấy lần có thời gian khứ hồi nhỏ nhất) khi bắt đầu chạy và mỗi ngày lúc thay sạc 17:00. Khi có Wi-Fi Internet, mạch đồng bộ thêm bằng NTP mỗi 30 phút như 16.5. Mỗi lần đồng bộ ghi nguồn, độ lệch đo được (phần trôi tích luỹ từ lần trước) và thời gian khứ hồi. Khi phân tích, thời điểm sự kiện được hiệu chỉnh bằng nội suy tuyến tính phần trôi giữa hai lần đồng bộ liền nhau (`tools/phan_tich/hieu_chinh_troi_gio.py`); quy tắc loại trừ lệch giờ quá 1 giây (mục 13) áp dụng sau hiệu chỉnh, và khoảng sau lần đồng bộ cuối không có lần đo kế tiếp được báo cáo riêng. Độ lệch đo được ở mỗi lần đồng bộ được báo cáo.

### 16.17. Thay đổi phần cứng

- **TC-01:** mạch ESP32-S3 N16R8 thay thế (đạt kiểm tra bo mạch 16 MB, PSRAM 8 MB và micro ngày 12/11); module thẻ nhớ mới, nối chân CS 15, MOSI 16, SCK 17, MISO 18 (thay cho 10–13). Không có LED báo; thiết bị vận hành không ghi âm thanh nên LED báo ghi âm chỉ cần cho TC-02 và được thay bằng biển “Đang ghi âm”.
- **TC-02:** mạch ESP32 thường (ESP-WROOM-32, 4 MB flash, không có PSRAM), chỉ chạy firmware kiểm định ghi WAV 16 kHz, 16 bit; quy đổi mẫu giống TC-01 (16.8). Kiểm tra hai thiết bị cạnh nhau (mục 7.6) làm bằng tệp WAV của TC-02 chấm trên máy tính bằng cùng thư viện mô hình.
- **Điện áp nguồn** trong nhật ký mỗi phút chỉ có khi lắp cầu chia điện trở; nếu không lắp, cột này để trống và việc mất nguồn được nhận biết qua thời gian chạy và khoảng trống của nhật ký.
- **Nguồn module thẻ nhớ (12/11):** chân “5Vin” của mạch ESP32-S3 thay thế không ra 5 V khi cấp nguồn qua USB, nên module thẻ không chạy dù thẻ, dây và module đều tốt. VCC của module chuyển sang chân 3V3; T5 đạt thẻ nhớ.
- **Ghi thẻ và Wi-Fi (12/11):** khi Wi-Fi phát liên tục, firmware vận hành gặp lỗi ghi thẻ. Tệp chuyển ra thư mục gốc của thẻ, SPI thẻ chạy 4 MHz (lùi về 1 MHz nếu không mở được); Wi-Fi chỉ bật khi chưa có giờ, trong 15 phút đầu sau khởi động và 16:50–17:20 mỗi ngày (giờ đồng bộ, 16.16), công suất phát 2 dBm. Cột `wifi_bat` và `loi_the` trong nhật ký mỗi phút ghi lại trạng thái này.
- **Cấu hình thư viện mô hình trên mạch (12/11), để đạt phép thử đồng nhất 7.6:** `EIDSP_QUANTIZE_FILTERBANK 0` (bộ lọc MFE số thực như trên máy tính), `EIDSP_USE_ESP_DSP 1` (FFT của esp-dsp; với kissfft suy luận mất 915 ms), `EI_CLASSIFIER_TFLITE_ENABLE_ESP_NN 0` (tắt nhân tối ưu ESP-NN). Trước khi tắt ESP-NN, chỉ 27,7% (v1) và 1,7% (v2) cửa sổ lệch ≤ 1 bậc int8. Sau khi tắt: mạch báo ĐẠT cho cả hai mô hình (v2 119/119 cửa sổ, lệch lớn nhất 0,0000; v1 đạt ngưỡng ≥ 95%), suy luận hai mô hình lớn nhất 230 ms. Ba cờ này là một phần của bản đóng băng (mục 10) và được ghi cùng SHA-256 firmware.

### 16.18. Đối chứng âm

Đối chứng âm (mục 7.4) thực hiện trong 3 ngày học 13, 16, 17/11, mỗi ngày 08:00–11:00 và 13:30–16:00 (khoảng 16,5 giờ thay cho 22 giờ), đều bằng TC-01, không ghi âm. Ngày 13/11 TC-01 đang trong 24 giờ chạy thử tại vị trí lắp và chưa đóng băng; số phát hiện sai của ngày này được tính sau khi đóng băng từ tệp điểm, như 16.15.

### 16.19. Ngày xoá tệp ghi âm

Ngày xoá chậm nhất ở mục 7.3, 14 và 16.12 dời từ 14/11 sang 17/11/2026 vì phần để chấm ghi tối 16/11. Thay đổi này cần giáo viên hướng dẫn đồng ý trước buổi ghi âm đầu tiên; biển báo và thông báo gửi học sinh được sửa cho khớp. Nếu không được đồng ý, lịch ghi âm được sắp lại theo chỉ đạo của giáo viên hướng dẫn và ghi bổ sung tại đây.

### 16.20. Bỏ LED báo ghi âm

Mục 2 (thiết bị) ghi mỗi bộ có LED báo ghi âm; 16.17 đã bỏ LED ở TC-01. Từ 12/11, TC-02 cũng không lắp LED. Việc ghi âm được báo cho học sinh bằng biển 2 “Đang ghi âm” dán tại vị trí lắp trong suốt các khung ghi, cùng thông báo trước 24 giờ trong nhóm chat như mục 14. Firmware ghi âm kiểm định chỉ ghi trong các khung giờ đã thông báo (16.14) và chỉ sau khi đồng bộ giờ; trạng thái ghi được kiểm tra qua Serial và tệp `TC-02_ghi.csv`. Không có thay đổi nào khác về cách ghi hay dữ liệu.

### 16.21. Tệp phát của phép thử tải

Phép thử tải ở 16.5 dùng tệp 60 phút tạo bằng `tools/tai_nhieu/tao_tep_tai.py` (seed 7575): 814 đoạn tiếng nói Common Voice tiếng Việt nối liên tục, chuẩn hoá cùng mức, trộn với 720 đoạn ESC-50 thấp hơn 8 dB, bỏ các lớp giống tiếng người (ho, hắt hơi, thở, ngáy, cười, trẻ khóc); không có nhạc vì máy không có bộ nhạc dữ liệu mở. Mức phát, cách đo (75 dB(A) cách loa 1 m) và tiêu chí đạt giữ nguyên.

### 16.22. Một thiết bị, lịch thu dữ liệu 15–18/11 và các sai lệch khi thực hiện

Ghi ngày 16/11/2026, trước khi ghi phần để sửa và phần để chấm, trước khi đóng băng và trước khi chấm bất kỳ dữ liệu nào.

**Phép thử 24 giờ và firmware vận hành 1.2.** Lần 1 bắt đầu 14/11 16:10 không đạt: nhật ký mỗi phút dừng lúc 07:46:23 (chưa rõ nguyên nhân) và 16:49:57 ngày 15/11 (đúng đầu khung Wi-Fi 16:50), trong khi mạch vẫn có điện; tức là mạch khởi động lại hoặc treo rồi chờ đồng bộ giờ. Firmware vận hành 1.2 (15/11): bỏ khung Wi-Fi 16:50–17:20; Wi-Fi chỉ bật 15 phút đầu sau khởi động hoặc khi chưa có giờ, tắt 90 giây sau khi đồng bộ; sau khởi động lại mềm, nếu đồng hồ RTC còn hợp lệ thì neo lại giờ từ RTC (nguồn đồng bộ ghi là `rtc_khoi_dong_lai`); ghi mỗi lần khởi động vào `/TC-01_khoi_dong.csv`. Lần 2 bắt đầu 15/11 19:19 tại vị trí lắp và kết thúc khi chuyển sang chế độ ghi tối 16/11. Các đêm trước 15/11 chỉ dùng những khoảng nhật ký mỗi phút liên tục và có giờ hợp lệ; khoảng trống được báo cáo là thiếu, không nội suy (mục 13).

**Một thiết bị.** TC-02 không dùng. TC-01 luân phiên hai chế độ bằng cách nạp lại firmware và đổi thẻ nhớ: firmware vận hành (đếm, không ghi âm, thẻ đếm) và firmware ghi âm kiểm định `TC01_Ghi_kiem_dinh` (chỉ ghi trong các khung đã thông báo, thẻ ghi riêng, cùng cách quy đổi mẫu như firmware vận hành, 16.8). Hệ quả: (1) bỏ phép so sánh hai thiết bị sau khi tháo gỡ (mục 7.6, kappa) và cân bằng khuếch đại giữa hai thiết bị (16.8); (2) trong các giờ ghi âm, thiết bị không đếm; số đếm của những giờ này tính từ tệp WAV bằng bộ chạy mô hình trên máy tính với mô hình, ngưỡng và bộ lọc đã đóng băng, dựa trên phép thử đồng nhất 7.6 (16.17); (3) mọi lần chuyển chế độ được ghi giờ, khoảng giữa hai chế độ báo cáo là thiếu.

**Lịch ghi âm** (tổng không quá 8 giờ):

| Phiên | Thời gian | Ghi chú |
| --- | --- | --- |
| Ghi thử | 16/11, ≤ 10 phút trước 20:55 | Kiểm tra firmware trên mạch; tệp `THU_…` xoá cùng các tệp khác |
| Âm học (16.9) | 16/11 20:55–21:05 | Thay 18:15–18:30 ngày 13/11 (không làm được) |
| Phần để sửa | 16/11 21:05–23:00 (khoảng 1,92 giờ thay cho 3 giờ) | Thành viên ở trường 19:00–20:30, về KTX khoảng 20:45; không ghi quá 23:00 đã thông báo |
| Phần để chấm | 17/11 17:00–20:20 và 22:20–23:30 (4,5 giờ) | Giữ đủ 4,5 giờ cho tiêu chí phát hiện sai mỗi giờ |

Nếu tối 16/11 mạch chỉ sẵn sàng sau 21:00 thì bỏ đo âm học; khi đó tệp của khung `am_hoc` chỉ chứa âm thanh sinh hoạt bình thường và được ghép vào đầu phần để sửa. Firmware ghi âm cắt mỗi tệp tối đa 1 giờ; các tệp của một phiên được ghép thành một tệp liền bằng `tools/ghep_wav/ghep_wav.py` theo `TC-01_ghi.csv`, khe hở được chèn 0 và báo cáo.

**Đóng băng** dời sang 17/11 11:30–12:40, sau phần để sửa và trước phần để chấm. Tầng 1 buổi 1 và yên tĩnh buổi 2 (15/11) thu trước khi đóng băng; như đêm 13 (16.15), sự kiện của chúng được tính lại sau đóng băng từ tệp điểm bằng mô hình, ngưỡng và bộ lọc đã đóng băng.

**Xoá tệp ghi âm** chậm nhất 12:40 ngày 18/11/2026, có biên bản; thay 16.19. Đã nhắn giáo viên hướng dẫn về hạn này ngày 15/11; thông báo gửi học sinh và biển 2 ghi cùng hạn.

**Tầng 1.**
- Mức “vừa”: 83,5 dB(A) ở 1 m (20 tiếng ho nhẹ của hai thành viên, độ lệch chuẩn 2,8, KTC 95% 82,1–84,8; đo 15/11 19:48–19:53). Bộ đo 19:40–19:48 bị loại vì máy đo không được đặt lại chế độ MAX giữa các tiếng ho.
- Mức phát: ở âm lượng tối đa, loa chỉ cho 76 dB(A) ở 1 m với tệp hiệu chuẩn. Buổi phát giữ âm lượng tối đa cố định; mọi mức (lớn, vừa, nhỏ) thấp hơn thiết kế khoảng 7,5 dB, chênh lệch giữa ba mức giữ nguyên 10 dB. Mức tại micro của từng tiếng ho vẫn tính như mục 7.1 từ mức đo của tệp hiệu chuẩn. Ngày 15/11, mức đo tệp hiệu chuẩn ở hành lang (máy đo đặt sát lưới micro TC-01 theo hướng dẫn) không giảm theo khoảng cách: khoảng 75 dB(A) ở 1 m, 75–76 ở 3 m, 72–79 ở 5 m, trong khi suy giảm theo khoảng cách dự kiến 6–10 dB từ 1 m đến 3 m. Chưa xác định được nguyên nhân. Vì vậy phân tích H1 dùng khoảng cách danh định (1, 3, 5 m); mức đo hiệu chuẩn chỉ được báo cáo mô tả, không dùng làm biến. Buổi 17/11 kiểm tra lại vị trí loa và máy đo trước mỗi khối.
- Khung giờ: sinh hoạt ồn 20:30–21:10; yên tĩnh từ 21:20 (học sinh vào phòng 21:15).
- Buổi: 15/11 buổi 1 (ồn và yên tĩnh) và yên tĩnh buổi 2; 17/11 ồn buổi 2 và yên tĩnh buổi 3. Bỏ ồn buổi 3, nên các ô sinh hoạt ồn có khoảng 16–18 tiếng ho mỗi ô, dưới mức tối thiểu 20 của mục 7.1; các ô này được báo cáo kèm n và KTC. Hai ô chính (yên tĩnh) giữ n = 100.

**Tầng 2** thực hiện 16/11 17:00, cùng vị trí và cách làm; không có buổi phát lại cùng tối nên bù độ trễ bằng giá trị của buổi phát lại 15/11 (16.6).

**Đối chứng âm** (16.18): 13/11 không thực hiện được. Thay bằng 16/11 và 17/11 (08:00–11:00, 13:30–16:00) và 18/11 08:00–11:00, khoảng 14 giờ.

**Hiệu chuẩn mức âm** (7.5) dời sang 18/11 11:35–12:00, sau khi tháo thiết bị.

**Đo âm học** (16.9) dùng chính TC-01 ở vị trí lắp. Nguồn xung cho thời gian vang đổi từ bóng bay sang túi giấy thổi phồng đập vỡ, hoặc hai quyển sách bìa cứng đập vào nhau nếu không có túi; loại nguồn dùng cho từng xung được ghi trong nhật ký đo. Thời gian vang vẫn chỉ báo cáo ở các dải octave 500 Hz–4 kHz, nơi hai nguồn này đủ năng lượng. Xung trong phòng B2.103 được đo khi cửa mở, qua micro ở hành lang.

**Chọn bốn khối gán nhãn đầy đủ** (7.3) theo đúng cách của `tools/gan_nhan/gan_nhan.py chon-doan` (viết 10/11): khối 30 phút tính từ đầu mỗi tệp ghi liền (17:00–20:20 cho 6 khối, 22:20–23:30 cho 2 khối, phần lẻ không thành khối), `sorted(random.Random(2026).sample(range(8), 4))` = khối 1, 2, 4, 5, tức 17:30, 18:00, 19:00, 19:30; khối 17:30–18:00 do hai người gán độc lập. Bốn khối còn lại (17:00, 18:30, 22:20, 22:50) cùng các phần lẻ thuộc xác minh mù. Bản chọn ngày 15/11 bằng một bộ sinh số ngẫu nhiên khác (numpy) bị thay vì không theo công cụ đã viết trước; cả hai lần chọn đều trước khi có bản ghi. Danh sách: `results/doan_gan_nhan_chon_truoc.csv`.
