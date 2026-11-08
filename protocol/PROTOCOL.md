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

Một buổi đo ngày 11/11/2026, dự kiến 16:00–16:15, khi KTX vắng và ngoài khung đối chứng âm. TC-02 chạy firmware kiểm định, đặt tạm sát cạnh TC-01.

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
