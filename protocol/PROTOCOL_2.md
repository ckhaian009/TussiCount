<table>
<colgroup>
<col style="width: 40%" />
<col style="width: 59%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p>TRƯỜNG THPT FPT CẦN THƠ</p>
<p><strong>ĐỘI THI LÒ VI SÓNG</strong></p></td>
<td><p><strong>CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</strong></p>
<p><strong>Độc lập - Tự do - Hạnh phúc</strong></p></td>
</tr>
<tr class="even">
<td></td>
<td></td>
</tr>
<tr class="odd">
<td>Số: 02/ĐC-LVS</td>
<td><em>Cần Thơ, ngày 25 tháng 11 năm 2026</em></td>
</tr>
</tbody>
</table>

**ĐỀ CƯƠNG NGHIÊN CỨU ĐĂNG KÝ TRƯỚC**

**Kiểm định và đánh giá hệ thống TussiCount 2.0 (Protocol 2.0)**

**Hiệu lực và nguyên tắc đăng ký.**

a\) Đề cương này, gồm Phần thứ nhất và Phần thứ hai, được công bố trên
kho mã nguồn công khai ckhaian009/TussiCount, tệp
protocol/PROTOCOL_2.md. Thời hạn công bố là trước 20:30 ngày 25/11/2026,
tức trước khi thu thập bất kỳ dữ liệu nào của vòng Chung kết. Số đo sơ
bộ khe chân cửa các ngày 24 và 25/11/2026 là thông tin về điều kiện hiện
trường, không phải dữ liệu nghiên cứu, và được công khai tại Mục XII.a.
Ba bản ghi thử chương trình ghi của TC-02 chiều 25/11/2026 chỉ dùng để
kiểm tra phần cứng (micro, thẻ nhớ, tràn bộ đệm), không được dùng cho bất
kỳ phân tích nào và được xóa theo Mục XVI.d. Thời điểm ghi nhận trên
kho mã nguồn là dấu thời gian đăng ký chính thức.

b\) Sau khi đăng ký, chỉ được bổ sung hai nội dung, và mọi nội dung khác
được giữ nguyên:

-   Phụ lục 1 (thông số phiên bản đóng băng), chậm nhất 12:00 ngày
    01/12/2026;

-   Mục XVII (thay đổi sau đăng ký), ghi rõ ngày và lý do của từng thay
    đổi.

**I. THÔNG TIN CHUNG**

<table>
<colgroup>
<col style="width: 27%" />
<col style="width: 72%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>Nội dung</strong></th>
<th><strong>Thông tin</strong></th>
</tr>
<tr class="odd">
<th>Sản phẩm</th>
<th><p>Hệ thống TussiCount 2.0, gồm 4 thành phần:</p>
<p>– TC-02: trạm đếm tiếng ho tại hành lang, chạy mô hình v3;</p>
<p>– TussiBridge: bộ ghép âm khe cửa thụ động;</p>
<p>– TussiPod-5: trạm tự kiểm tra ẩn danh;</p>
<p>– TussiWeb: trang phiếu sàng lọc và bảng điều phối.</p></th>
</tr>
<tr class="header">
<th>Cuộc thi</th>
<th>STEMPETITION 2026–2027, vòng Chung kết ngày 09/12/2026, Tiểu ban
Công nghệ kỹ thuật, Thử thách 2 – Healthy Living</th>
</tr>
<tr class="odd">
<th>Nhóm thực hiện</th>
<th>Cao Khải An, Nguyễn Phúc Gia Bảo (lớp 12T1, Trường THPT FPT Cần
Thơ)</th>
</tr>
<tr class="header">
<th>Giáo viên hướng dẫn</th>
<th>Cô Trương Minh Phương</th>
</tr>
<tr class="odd">
<th>Đơn vị cho phép tại hiện trường</th>
<th>Thầy Nguyễn Thành Lượng, Giáo viên quản nhiệm Dorm B2</th>
</tr>
<tr class="header">
<th>Quan hệ với đề cương vòng Bán kết</th>
<th><p>Đề cương đăng ký ngày 07/11/2026 (sau đây gọi là P1) tiếp tục có
hiệu lực đối với số liệu vòng Bán kết. Đề cương này kế thừa nguyên văn
hai nhóm nội dung của P1, trừ trường hợp được quy định khác:</p>
<p>– các định nghĩa tại Mục 6 của P1 (cửa sổ, sự kiện, quy tắc ghép ±1
giây, độ nhạy, số phát hiện sai mỗi giờ, LA90);</p>
<p>– các quy định về quyền riêng tư tại Mục 14 và Mục 16.12 của
P1.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

**II. MỤC TIÊU, CÂU HỎI NGHIÊN CỨU VÀ GIẢ THUYẾT**

**1. Cơ sở**

Kết quả vòng Bán kết cho thấy nguyên nhân chính làm giảm hiệu năng nằm ở
mô hình nhận dạng, không nằm ở phần cứng, vì hai lẽ sau:

-   âm thanh đến micro cao hơn mức nền khoảng 13 dB, nhưng điểm số của
    mô hình v2 có trung vị chỉ khoảng 0,10;

-   toàn bộ 13/13 trường hợp phát hiện sai đã xác minh đều là tiếng nói
    chuyện.

Vòng Chung kết đánh giá giải pháp hiệu chỉnh dữ liệu huấn luyện bằng đặc
trưng âm học thực tế của Dorm B2.

**2. Câu hỏi nghiên cứu**

a\) **Q1.** Mô hình v3 được huấn luyện với ba nguồn dữ liệu mới:

-   đáp ứng xung đo tại Dorm B2;

-   tiếng ồn nền thực tế;

-   mẫu âm khó là tiếng nói có vang.

So với mô hình v2, trên cùng các tiếng ho thật ở hành lang cách 1–3 m,
v3 có độ nhạy cao hơn không? Trong điều kiện sinh hoạt bình thường, số
phát hiện sai của v3 có không quá 4 lần mỗi giờ không?

b\) **Q2.** TussiBridge có làm tăng mức âm thanh truyền qua khe cửa đóng
đến vị trí thiết bị, trong dải tần 250–1.000 Hz, hay không?

c\) **Q3.** Trạm TussiPod-5 có đạt các tiêu chí nghiệm thu tại Mục XIII
hay không?

d\) **Q4.** Tỷ lệ học sinh nội trú sẵn sàng sử dụng một trạm tự kiểm tra
ẩn danh là bao nhiêu?

**3. Giả thuyết kiểm định**

a\) **H3.** Trên các tiếng ho thuộc tập K1 ở vị trí hành lang 1 m và 3
m, độ nhạy của TC-02 (mô hình v3) cao hơn độ nhạy của TC-01 (mô hình
v2).

b\) **H4.** TussiBridge có độ lợi chèn trung bình dương trong dải
250–1.000 Hz.

Các phân tích còn lại trong Đề cương này mang tính mô tả.

**III. PHẠM VI**

a\) Sản phẩm đếm sự kiện ho ở cấp hành lang và khuyến nghị học sinh tự
kiểm tra sức khỏe.

b\) Sản phẩm không chẩn đoán bệnh, không xác định danh tính người ho, và
không theo dõi từng phòng hay từng cá nhân.

c\) Số liệu chỉ được tổng hợp cho hành lang có từ 20 học sinh trở lên.

d\) TussiPod-5 không lưu âm thanh và không thu thập thông tin định danh.

**IV. TIẾN ĐỘ VÀ TRÌNH TỰ BẮT BUỘC**

**1. Trình tự bắt buộc**

Các bước được thực hiện theo đúng thứ tự sau:

a\) đăng ký Đề cương;

b\) thu thập dữ liệu Phần thứ nhất;

c\) huấn luyện và lựa chọn mô hình trên tập hiệu chỉnh;

d\) đóng băng;

đ) thu thập dữ liệu kiểm định K1–K3;

e\) chấm điểm một lần duy nhất;

g\) xóa dữ liệu ghi âm.

Trước khi đóng băng, không dữ liệu kiểm định nào được mở hoặc xử lý qua
mô hình. Dữ liệu kiểm định gồm K1, K2, K3 và các bản ghi của nhóm kiểm
định.

**2. Tiến độ chi tiết**

| **Ngày**                  | **Thời gian** | **Nội dung**                                                                             | **Ghi âm**  |
|-------------|------------|----------------------------------|--------------|
| 23/11/2026                | —             | Gửi văn bản xin phép; phát phiếu đồng thuận; kiểm kê và đặt mua linh kiện                | —           |
| 24/11/2026                | —             | Mở phiếu khảo sát nhanh (đến 21:00 ngày 27/11)                                           | Không       |
| 25/11/2026                | Trước 20:30   | Đăng ký Đề cương                                                                         | —           |
| 25/11/2026                | Sau công bố, trước 21:00 | Đo khe chân cửa 03 phòng (Mục XII.a)                                          | Không       |
| 25/11/2026                | 21:00         | Hạn nộp phiếu đồng thuận                                                                 | —           |
| 25/11/2026                | 21:00–22:00   | Hiệu chuẩn mức âm TC-02 (Mục V.2b)                                                       | Tín hiệu đo |
| 26/11/2026                | 08:30–10:30   | Thiết bị tự ghi tiếng ồn nền khi hành lang không có người                                | Có          |
| 26/11/2026                | 17:00         | Chạy phân nhóm người tham gia; công bố kết quả (Mục V.1)                                 | —           |
| 26/11/2026                | 17:15–18:45   | Đo đáp ứng xung tại 19 vị trí; đo phổ suy hao qua cửa                                    | Tín hiệu đo |
| 26/11/2026                | 19:00–20:30   | Ghi tiếng ho của người tham gia (12 người × 20 lần ho)                                   | Có          |
| 28/11/2026                | 17:00–18:00   | Đo TussiBridge (Mục XII)                                                                 | Tín hiệu đo |
| 28/11/2026                | 19:00–20:00   | Ghi hội thoại theo kịch bản (06 cặp × 05 phút)                                           | Có          |
| 29/11/2026                | Cả ngày       | Dự phòng đo lại buổi không đạt; huấn luyện và lựa chọn mô hình                           | —           |
| 26–30/11/2026             | —             | Tăng cường dữ liệu, huấn luyện, lập bảng phân tích thành phần, chọn ngưỡng (Mục VI, VII) | —           |
| 30/11/2026                | Trước 12:00   | Phép thử đồng nhất bit; lắp đặt TC-01 và TC-02; cân bằng hệ số khuếch đại                | —           |
| 30/11 12:00 – 01/12 12:00 | —             | Chạy thử liên tục 24 giờ TC-02, có truyền ESP-NOW                                        | Không       |
| 01/12/2026                | 12:00         | **Đóng băng**; hoàn thiện Phụ lục 1 và công bố                                           | —           |
| 01/12/2026                | 17:00–18:00   | Nghiệm thu TussiPod-5 (Mục XIII)                                                         | Không       |
| 02/12/2026                | 19:00–20:00   | Kiểm định K1: tiếng ho thật của nhóm kiểm định                                           | Không       |
| 02/12/2026                | 20:15–21:15   | Kiểm định K2: phát lại tiếng ho mẫu                                                      | Không       |
| 03/12/2026                | 19:00–22:00   | Kiểm định K3: sinh hoạt tự nhiên (thông báo trước 19:00 ngày 02/12)                      | Có          |
| 04/12/2026                | Cả ngày       | Gán nhãn, chấm điểm K1–K3 một lần; tháo dỡ thiết bị trước 17:00                          | —           |
| 10/12/2026                | —             | Xóa toàn bộ dữ liệu ghi âm và dữ liệu trên Edge Impulse, có biên bản                     | —           |

Trường hợp một mốc bị chậm, các mốc sau được lùi tương ứng và ghi nhận
tại Mục XVII. Trình tự tại Mục IV.1 không được thay đổi.

**PHẦN THỨ NHẤT**

**DỮ LIỆU XÂY DỰNG MÔ HÌNH v3**

**V. NGƯỜI THAM GIA VÀ THIẾT BỊ GHI**

**1. Người tham gia và phân nhóm**

a\) **Điều kiện tham gia.**

-   Có phiếu đồng thuận Mẫu số 01/PĐT, được phụ huynh ký xác nhận.

-   Không đang đau họng, ho, sốt; không mắc bệnh hen hay bệnh đường hô
    hấp.

-   Người tham gia được gán mã từ TNV01 đến TNV12 theo thứ tự nộp phiếu.

-   Danh sách đối chiếu mã với họ tên do giáo viên hướng dẫn quản lý.

b\) **Phân nhóm.** Lúc 17:00 ngày 26/11/2026, sau hạn nộp phiếu và trước
buổi ghi đầu tiên, chạy chương trình tools/v3/chia_nhom.py (hạt giống
2026). Chương trình hoán vị ngẫu nhiên danh sách mã:

-   06 mã đầu thuộc **nhóm A**: 04 mã đầu là A-huấn luyện, 02 mã tiếp
    theo là A-hiệu chỉnh;

-   06 mã còn lại thuộc **nhóm B**, gọi là nhóm kiểm định.

Kết quả phân nhóm, chỉ gồm mã, được công bố ngay.

c\) **Trường hợp có n \< 12 người tham gia** không phải thành viên Đội
thi:

-   nhóm B gồm ⌈n/2⌉ người, chọn ngẫu nhiên, tối thiểu 04 người;

-   số còn lại được xếp vào A-hiệu chỉnh trước (tối đa 02 người), rồi
    đến A-huấn luyện;

-   thành viên Đội thi, nếu tham gia, luôn thuộc A-huấn luyện;

-   nếu nhóm B có dưới 04 người, kết quả K1 được báo cáo ở mức thăm dò.

d\) **Nguyên tắc cách ly dữ liệu.**

-   Dữ liệu của nhóm B không được dùng để huấn luyện, chọn ngưỡng hay
    chọn mô hình.

-   Tệp của nhóm B được lưu tại thư mục riêng (khoa/). Mã băm SHA-256
    của từng tệp được ghi vào nhật ký ngay sau buổi ghi.

-   Thư mục khoa/ chỉ được mở sau khi đóng băng.

đ) Người thuộc nhóm A không đồng ý tải dữ liệu lên Edge Impulse thì dữ
liệu của họ chỉ được dùng trong tập hiệu chỉnh. Việc điều chuyển được
ghi nhận tại Mục XVII.

**2. Thiết bị ghi**

a\) Toàn bộ bản ghi của Phần thứ nhất và của K3 sử dụng phần cứng TC-02,
chạy chương trình hiệu chuẩn ghi tệp WAV 16 kHz, 16 bit, một kênh:

-   vi điều khiển ESP32-S3 N16R8;

-   micro INMP441 nối GPIO 4/5/6;

-   thẻ nhớ microSD nối GPIO 15–18, cấp nguồn 3V3.

Mỗi lần bấm nút BOOT, thiết bị đóng tệp đang ghi và mở tệp mới (chương
trình firmware/TC02_Hieu_chuan, phiên bản hieu-chuan-1.2, hệ số dịch
bit 14). Toàn bộ bản ghi của Phần thứ nhất, hai lần hiệu chuẩn mức và
tập K3 dùng cùng phiên bản này; mỗi tệp ghi phiên bản vào nhật ký
GHI_NHAT_KY.csv. Thời điểm bắt đầu
tệp được xác định bằng ảnh chụp đồng hồ điện thoại tại lúc bấm nút, kèm
03 tiếng bíp phát ở đầu và cuối mỗi buổi; sai số dự kiến dưới 2 giây.
Bản ghi dài hơn 01 giờ được chia theo từng giờ khi xử lý.

Do micro INMP441 và thẻ nhớ mới của TC-02 chưa về, các buổi ghi của Phần
thứ nhất dùng micro và thẻ nhớ tháo tạm từ TC-01; số hiệu của hai linh
kiện này được ghi vào nhật ký. Trước khi tháo, toàn bộ thẻ nhớ của TC-01
được sao lưu kèm mã băm SHA-256. Hai linh kiện được lắp trả lại TC-01
trước 12:00 ngày 30/11/2026; TC-02 dùng micro mới từ lúc đó. Chênh lệch
độ nhạy giữa hai micro được xử lý bằng hiệu chuẩn mức (điểm b) và bước
cân bằng hệ số khuếch đại (Mục IX.b). Cách bố trí này bảo đảm mô hình v3
học đúng đặc tính của micro và vỏ thiết bị dùng khi kiểm định.

b\) **Hiệu chuẩn mức âm TC-02** (21:00–22:00 ngày 25/11/2026), thực hiện
theo Mục 7.5 của P1:

-   phát nhiễu hồng ở 05 mức trong khoảng 45–85 dB(A); mức thấp nhất cao
    hơn tiếng ồn nền hành lang ít nhất 10 dB;

-   lập phương trình quy đổi từ dBFS sang dB(A);

-   báo cáo hệ số, hệ số xác định R² và sai số dư lớn nhất.

Hiệu chuẩn được thực hiện hai lần: ngày 25/11/2026 cho micro dùng ghi
Phần thứ nhất, và trước 12:00 ngày 30/11/2026 cho micro chính thức của
TC-02, cùng quy trình.

**VI. CÁC BỘ DỮ LIỆU**

**1. Đáp ứng xung phòng (17:15–18:45 ngày 26/11/2026)**

a\) **Tín hiệu và cách phát.**

-   Tín hiệu quét tần số hàm mũ từ 100 Hz đến 8 kHz, dài 5 giây, tạo
    bằng tools/v3/xung_quet.py ở tần số lấy mẫu 48 kHz.

-   Mỗi vị trí phát 04 lần, cách nhau 3 giây, từ loa đặt ở độ cao 1,5 m.

-   Âm lượng loa giữ cố định trong suốt buổi đo; mức dB(A) đỉnh tại 1 m
    được ghi một lần.

-   TC-02 thu tại vị trí lắp đặt: cách cửa phòng B2.103 khoảng 1 m, cao
    1,5–2 m.

b\) **Vị trí đo (19 vị trí).**

-   Hành lang (10 vị trí): cách micro 1, 2, 3, 4, 5 m về mỗi phía, ký
    hiệu H-T1 đến H-T5 và H-P1 đến H-P5. Loa hướng về thiết bị.

-   Trong phòng, cửa đóng (06 vị trí): phòng B2.103 và 02 phòng liền kề.
    Mỗi phòng có 02 vị trí: cách cửa 1 m (Đ1) và giữa phòng (Đ2). Loa
    hướng về cửa.

-   Cửa mở (03 vị trí): 03 phòng nêu trên, tại vị trí Đ1.

-   Phòng không đồng ý được thay bằng phòng gần nhất có đồng ý; việc
    thay thế được ghi nhận.

c\) **Xử lý.** Dùng tools/v3/giai_chap.py, theo các bước:

1\. Giải chập bằng bộ lọc ngược Farina.

2\. Căn chỉnh 04 lần lặp theo đỉnh tương quan chéo, rồi lấy trung bình.

3\. Cắt cửa sổ từ 5 ms trước đỉnh trực tiếp đến 1,0 giây sau đỉnh, làm
mờ 50 ms ở cuối.

4\. Chuẩn hóa đỉnh về 1.

d\) **Kiểm soát chất lượng.**

-   Tỷ số đỉnh trên nhiễu phải đạt ít nhất 35 dB; vị trí không đạt được
    đo lại.

-   Trường hợp có người đi qua được ghi nhận và đo lại.

-   Báo cáo mô tả thêm thời gian vang T20, tính theo tích phân ngược
    Schroeder, tại các dải octave 500 Hz–4 kHz.

đ) **Phổ suy hao qua cửa.**

-   Phát nhiễu hồng 30 giây tại vị trí Đ1, khi cửa mở và khi cửa đóng,
    cho từng phòng.

-   Tính suy hao theo dải 1/3 octave từ 125 Hz đến 6,3 kHz. Giới hạn
    trên là 6,3 kHz vì tần số Nyquist ở 16 kHz là 8 kHz.

e\) **Phép thử công cụ.** Tích chập một đáp ứng xung tổng hợp đã biết
RT60, rồi giải chập lại. Sai số RT60 phải nhỏ hơn 5%.

**2. Tiếng ồn nền (08:30–10:30 ngày 26/11/2026)**

a\) TC-02 tự ghi 120 phút trong giờ học, có biển báo.

b\) Phân chia dữ liệu:

-   phần huấn luyện: 08:30–09:50 (80 phút);

-   phần hiệu chỉnh: 09:50–10:30 (40 phút).

c\) Đoạn có tiếng người nói được đánh dấu và loại bỏ; tổng thời lượng
loại bỏ được báo cáo.

**3. Tiếng ho của người tham gia (19:00–20:30 ngày 26/11/2026)**

a\) **Vị trí.** Mỗi người ho nhẹ 20 lần theo hiệu lệnh, 05 lần tại mỗi
vị trí:

-   P1, P3, P5: đứng tại hành lang, cách micro 1, 3, 5 m, hướng mặt về
    thiết bị;

-   PĐ: trong phòng B2.103, cách cửa 1 m, hướng mặt về cửa đóng.

b\) **Cách thực hiện.**

-   Thứ tự 04 vị trí được xáo trộn ngẫu nhiên cho từng người (hạt giống
    2026 cộng số thứ tự của mã TNV).

-   Hiệu lệnh cách nhau 8 giây.

-   Mức ho “nhẹ” được thực hiện như tầng kiểm định 2 của P1.

-   Quy trình chi tiết theo Kịch bản 2, văn bản số 03/QT-LVS.

c\) **Thời điểm chuẩn.**

-   Thời điểm chuẩn được gán nhãn trên tệp WAV, gồm khởi đầu và kết
    thúc.

-   Các tiếng ho cách nhau dưới 1 giây được tính là một tràng, theo P1.

-   Tiếng ho ngoài hiệu lệnh cũng được gán nhãn.

-   Trang bấm giờ được dùng làm bản đối chiếu dự phòng.

d\) Nhóm B cũng tham gia buổi ghi này; tệp của nhóm B được lưu tại thư
mục khoa/.

**4. Hội thoại theo kịch bản (19:00–20:00 ngày 28/11/2026)**

a\) **Ghép cặp.**

-   06 cặp được ghép trong cùng nhóm: A-huấn luyện 02 cặp, A-hiệu chỉnh
    01 cặp, nhóm B 03 cặp.

-   Mỗi cặp được phân ngẫu nhiên một trong 06 cảnh của Kịch bản 1 (hạt
    giống 2026).

b\) **Cách thực hiện.** Mỗi cặp thực hiện hai lượt, mỗi lượt khoảng 2,5
phút:

-   lượt 1: đứng cách micro 1–2 m;

-   lượt 2: vừa di chuyển vừa nói trong đoạn hành lang 3–5 m.

c\) Kịch bản không có tiếng ho hay tiếng hắng giọng. Tiếng ho phát sinh
ngoài ý muốn được ghi thời điểm và gán nhãn ho.

d\) Dữ liệu nhóm B được lưu tại thư mục khoa/ và dùng cho tập K4 (Mục
XI.4).

**5. Dữ liệu mở**

a\) COUGHVID: 3.000 bản ghi, giữ nguyên danh sách
results/coughvid_chon_3000.csv của P1.

b\) ESC-50: loại bỏ lớp coughing.

c\) Common Voice tiếng Việt: 1.000 đoạn của 229 người nói.

d\) Giữ nguyên cách phân chia tập huấn luyện và tập kiểm tra của mô hình
v2 trên Edge Impulse. Việc chia theo trường dữ liệu nhóm, và không nhóm
nào thuộc cả hai tập.

đ) Bộ dữ liệu Coswara không được dùng để huấn luyện; chỉ dùng cho tập
K2.

**6. Tăng cường dữ liệu (tools/v3/tang_cuong.py, hạt giống 2026)**

a\) **Dữ liệu mở thuộc tập huấn luyện.** Giữ bản gốc và bổ sung 01 bản
tăng cường cho mỗi đoạn.

-   Tích chập với một đáp ứng xung thực đo, chọn ngẫu nhiên: 30% dùng 06
    đáp ứng cửa đóng; 70% dùng 10 đáp ứng hành lang và 03 đáp ứng cửa
    mở.

-   Trộn với một đoạn tiếng ồn ngẫu nhiên thuộc phần huấn luyện (Mục
    VI.2), tỷ số tín hiệu trên nhiễu (SNR) phân bố đều từ 0 đến 20 dB.

-   SNR được tính bằng giá trị RMS của phần có tín hiệu so với RMS của
    tiếng ồn.

b\) **Tiếng ho của A-huấn luyện.** Giữ nguyên bản gốc (đã có tiếng vang
thực), và bổ sung 02 bản trộn tiếng ồn huấn luyện ở SNR 0–20 dB.

c\) **Mẫu âm khó (nhãn noise)** gồm:

-   hội thoại của A-huấn luyện;

-   1.000 đoạn Common Voice đã tăng cường theo điểm a;

-   tiếng ồn huấn luyện cắt thành đoạn 1 giây, bước dịch 0,5 giây.

d\) Tệp đầu ra có đỉnh vượt −1 dBFS được chuẩn hóa về −1 dBFS.

đ) **Phép thử công cụ.** SNR thực tế phải đúng mức yêu cầu trong phạm vi
±0,5 dB, và không tệp nào vượt 0 dBFS.

e\) **Dữ liệu được tải lên Edge Impulse** chỉ gồm hai loại:

-   dữ liệu mở đã tăng cường;

-   dữ liệu của người thuộc nhóm A đã đồng ý tại Mẫu số 01/PĐT, đã cắt
    thành đoạn 1–3 giây.

Không tải lên tiếng ồn nền, đáp ứng xung và mọi dữ liệu của nhóm B.

**VII. HUẤN LUYỆN, TẬP HIỆU CHỈNH VÀ QUY TẮC LỰA CHỌN**

**1. Kiến trúc mô hình**

a\) Giữ nguyên khối MFE và mạng nơ-ron của mô hình v2 (Impulse #3 tại
P1):

-   cửa sổ 1.000 ms, bước dịch 500 ms, tần số lấy mẫu 16 kHz;

-   40 bộ lọc, sàn nhiễu −72 dB;

-   mạng tích chập lượng tử hóa int8.

Nhờ vậy, mọi cải thiện đều đến từ dữ liệu, không đến từ kiến trúc.

b\) Biến thể v3b (chuẩn hóa năng lượng theo dải, dạng PCEN) chỉ thực
hiện nếu đủ thời gian, và phải tuân thủ quy tắc tại Mục VII.4.

**2. Tập hiệu chỉnh**

Tập hiệu chỉnh dùng để chọn mô hình, bộ lọc và ngưỡng; không dùng để
huấn luyện.

a\) **Độ nhạy hiệu chỉnh** S_hc là trung bình cộng của hai giá trị:

-   \(i\) độ nhạy trên tiếng ho thật của A-hiệu chỉnh tại P1 và P3 (02
    người × 10 lần = 20 tiếng ho);

-   \(ii\) độ nhạy trên phần kiểm tra của COUGHVID, đã tích chập với 06
    đáp ứng hành lang 1–3 m và trộn tiếng ồn phần hiệu chỉnh ở SNR 0–20
    dB.

Độ nhạy của A-hiệu chỉnh tại P5 và PĐ được báo cáo bổ sung để mô tả.

b\) **Số phát hiện sai hiệu chỉnh** (FP/giờ_hc) được tính trên một luồng
sinh hoạt mô phỏng dài 60 phút, tạo bằng tools/v3/luong_sua.py (hạt
giống 2026):

-   nền là 40 phút tiếng ồn phần hiệu chỉnh, lặp nối thành 60 phút;

-   chèn tiếng nói phủ 25% thời lượng, không chồng lấn nhau;

-   tiếng nói gồm hội thoại của A-hiệu chỉnh (giữ nguyên mức) và phần
    kiểm tra của Common Voice;

-   đoạn Common Voice được tích chập với đáp ứng hành lang 1–5 m, và đặt
    RMS cao hơn nền từ 5 đến 15 dB (phân bố đều).

Đây là đại lượng ước lượng gần đúng; số liệu chính thức về phát hiện sai
được lấy từ tập K3.

**3. Bảng phân tích thành phần**

Mỗi cấu hình dưới đây được huấn luyện và chọn ngưỡng theo Mục VII.4. Với
mỗi cấu hình, ghi S_hc, hai thành phần (i) và (ii), và FP/giờ_hc.

a\) v2 (đối chứng);

b\) v3-1: thay 600 đáp ứng xung tổng hợp bằng đáp ứng xung thực đo;

c\) v3-2: bổ sung mẫu âm khó;

d\) v3-3: bổ sung tiếng ho của A-huấn luyện;

đ) bổ sung bộ lọc sau phân loại;

e\) tùy chọn: cổng Kurtosis, biến thể v3b.

**4. Quy tắc giữ hoặc loại bỏ, và lựa chọn ngưỡng**

a\) **Quy tắc giữ hoặc loại bỏ.** Mỗi bước được so sánh với bước gần
nhất đã giữ. Bước đó được giữ khi đáp ứng một trong hai điều kiện:

-   FP/giờ_hc giảm, và S_hc không giảm quá 2 điểm phần trăm; hoặc

-   S_hc tăng, và FP/giờ_hc không quá 4.

b\) **Không gian tìm kiếm.**

-   Ngưỡng từ 0,05 đến 0,95, bước 0,05.

-   Số cửa sổ liền kề tối thiểu k ∈ {1; 2}.

-   Khoảng nghỉ tối thiểu g ∈ {0; 0,5; 1} giây.

-   Loại hoặc không loại sự kiện dài hơn 2 giây.

c\) **Lựa chọn cuối cùng.** Trong các cấu hình đã giữ, chọn cấu hình có
S_hc cao nhất mà FP/giờ_hc không quá 4. Khi bằng nhau:

-   ưu tiên cấu hình có ít thành phần hơn;

-   nếu vẫn bằng nhau, ưu tiên ngưỡng cao hơn.

d\) **Trường hợp không cấu hình nào có FP/giờ_hc không quá 4.** Chọn cấu
hình có FP/giờ_hc thấp nhất trong số các cấu hình có S_hc từ 50% trở
lên, và ghi nhận tại Mục XVII.

**PHẦN THỨ HAI**

**ĐÓNG BĂNG, KIỂM ĐỊNH VÀ TIÊU CHÍ ĐÁNH GIÁ**

**VIII. ĐÓNG BĂNG**

**1. Điều kiện trước khi đóng băng**

a\) **Phép thử đồng nhất bit.**

-   Dùng ít nhất 119 cửa sổ dữ liệu mở.

-   Kết quả trên máy tính và trên vi điều khiển phải lệch 0 bậc int8.

-   Thiết lập các cờ: EI_CLASSIFIER_TFLITE_ENABLE_ESP_NN 0,
    EIDSP_QUANTIZE_FILTERBANK 0, EIDSP_USE_ESP_DSP 1.

-   Thời gian suy luận lớn nhất dưới 500 ms.

b\) **Chạy thử liên tục 24 giờ** tại vị trí lắp đặt, từ 12:00 ngày 30/11
đến 12:00 ngày 01/12/2026, có truyền ESP-NOW. Yêu cầu:

-   không có lỗi ghi thẻ nhớ;

-   ít nhất 95% số phút có nhật ký;

-   ít nhất 99% số gói tin đến bộ thu (Gateway).

**2. Đóng băng (12:00 ngày 01/12/2026)**

a\) Hoàn thiện Phụ lục 1 và công bố riêng trên kho mã nguồn. Phụ lục
ghi:

-   mô hình, ngưỡng và bộ lọc;

-   mã băm SHA-256 của firmware TC-02;

-   hệ số khuếch đại;

-   bảng phân tích thành phần.

b\) Sau khi đóng băng, không điều chỉnh bất kỳ thành phần nào cho đến
khi chấm điểm xong.

c\) TC-01 giữ nguyên firmware và mô hình v2 đã đóng băng ở vòng Bán kết
(mã SHA-256 tại Mục 12 của P1).

d\) Nếu chạy thử 24 giờ không đạt và phải sửa firmware, nội dung sửa và
lần chạy lại được ghi nhận tại Mục XVII. Mô hình và ngưỡng không được
thay đổi.

**IX. LẮP ĐẶT VÀ ĐỒNG BỘ THỜI GIAN**

a\) **Vị trí lắp đặt.**

-   TC-01 và TC-02 được gắn song song trên đế tường, tại vị trí lắp đặt
    của P1: hành lang tầng 1, cách cửa phòng B2.103 khoảng 1 m.

-   Hai thiết bị ở cùng độ cao; hai micro cách nhau 10 cm theo phương
    ngang và cùng hướng ra hành lang.

b\) **Cân bằng hệ số khuếch đại** (ngày 30/11/2026, theo Mục 16.8 của
P1). Phát nhiễu hồng ở 1 m; đặt hệ số khuếch đại số sao cho mức dBFS của
hai thiết bị chênh lệch không quá 1 dB.

c\) **Đồng bộ thời gian.**

-   Đồng bộ bằng điện thoại qua trang cấu hình của mạch (Mục 16.16 của
    P1) vào đầu mỗi buổi kiểm định.

-   Phát 03 tiếng bíp ở đầu và cuối mỗi buổi.

-   Hiệu chỉnh độ trôi đồng hồ bằng nội suy tuyến tính.

**X. CÁC TẬP KIỂM ĐỊNH CHÍNH**

Cả ba tập đều là dữ liệu mới, không sử dụng trong huấn luyện. Thời điểm
chuẩn của mỗi tập được xác định độc lập với thiết bị.

**1. Tập K1 – Tiếng ho thật (19:00–20:00 ngày 02/12/2026)**

a\) **Người tham gia:** nhóm B (06 người).

b\) **Thiết kế.** Mỗi người ho nhẹ 30 lần:

-   10 lần tại P1, 10 lần tại P3, 10 lần tại PĐ, theo định nghĩa vị trí
    tại Mục VI.3;

-   thứ tự vị trí được xáo trộn ngẫu nhiên (hạt giống 2027 cộng số thứ
    tự của mã TNV);

-   hiệu lệnh cách nhau 8 giây, theo Kịch bản 3.

c\) **Thời điểm chuẩn.** Người quan sát chạm nút “HO” trên trang “Bấm
giờ ho thật” đã đồng bộ, đúng lúc nghe tiếng ho. Tiếng ho không chắc
chắn (ho kép, bị át tiếng) được đánh dấu “?”.

d\) **Hiệu chỉnh độ trễ hệ thống.** Đầu buổi, phát 10 tiếng ho kiểm tra
tại P1. Độ trễ được bù theo quy tắc tại Mục 16.6 của P1.

đ) **Thiết bị.** TC-01 và TC-02 chạy chế độ vận hành và ghi sự kiện lên
thẻ nhớ. Không ghi âm.

**2. Tập K2 – Phát lại (20:15–21:15 ngày 02/12/2026)**

a\) **Tệp phát.**

-   210 tiếng ho từ bộ dữ liệu Coswara: 200 tiếng cho các ô thí nghiệm
    và 10 tiếng để kiểm tra.

-   Chọn ngẫu nhiên (hạt giống 2026) trong các bản ghi chất lượng tốt
    nhất của những người không có tên trong tệp
    results/coswara_playlist.csv của P1.

-   Mỗi bản ghi được cắt thành một tiếng ho đơn, bằng đúng thuật toán
    tools/chuan_bi_phat_lai.py.

b\) **Năm ô thí nghiệm, mỗi ô 40 tiếng ho:**

-   H1, H3, H5: tại hành lang, cách micro 1, 3, 5 m;

-   PĐ: trong phòng B2.103, cách cửa đóng 1 m, không có TussiBridge;

-   PĐ+B: như PĐ, có TussiBridge, dùng biến thể được chọn tại Mục XII.

Trường hợp Mục XII.a trường hợp 3 áp dụng, ô PĐ+B được bỏ: tập K2 còn 04
ô × 40 tiếng ho, dùng 160 tiếng đầu của danh sách đã chọn và 10 tiếng
kiểm tra. Trường hợp Mục XII.a trường hợp 2 áp dụng, hai ô PĐ và PĐ+B
được thực hiện tại phòng được chọn ở trường hợp đó.

c\) **Mức phát và trình tự.**

-   Mức phát “vừa” bằng mức dB(A) đỉnh tại 1 m đã ghi ở Mục 12 của P1.
    Nếu loa không đạt mức này, ghi nhận và báo cáo mức thực tế.

-   Thứ tự các ô được xáo trộn ngẫu nhiên (hạt giống 2026).

-   Hai tiếng ho cách nhau 8 giây; thời điểm phát do trình phát ghi lại.

**3. Tập K3 – Sinh hoạt tự nhiên (19:00–22:00 ngày 03/12/2026)**

a\) **Ghi âm.**

-   Phần cứng TC-02 chạy chương trình hiệu chuẩn (cùng phiên bản tại
    Mục V.2a), ghi liên tục 03 giờ. Việc nạp chương trình này cho K3 đã
    được quy định tại đây, không phải là điều chỉnh sau đóng băng. Sau
    buổi K3, firmware vận hành đã đóng băng được nạp lại và đối chiếu mã
    SHA-256; khoảng 19:00–22:00 ngày 03/12/2026 không tính vào chỉ số
    vận hành của TC-02 tại Mục XI.3.d.

-   TC-01 tiếp tục chạy mô hình v2 trực tiếp, chỉ để đối chiếu vận hành.

-   Có thông báo trước 24 giờ và biển “Đang ghi âm”.

b\) **Chấm điểm.**

-   Sau khi gán nhãn xong, tệp WAV được xử lý **một lần duy nhất** trên
    máy tính qua thư viện của v2 và v3 đã đóng băng.

-   Thư viện này có cùng mã xử lý với firmware và đã qua phép thử đồng
    nhất bit.

-   Nhờ vậy, hai mô hình được so sánh trên cùng một tín hiệu âm thanh.

c\) **Gán nhãn đầy đủ (02 giờ).**

-   Chọn ngẫu nhiên (hạt giống 2026) 04 trong 06 khối 30 phút.

-   Người gán nhãn không được xem kết quả của mô hình.

-   Hai người gán nhãn độc lập khối được chọn đầu tiên, và tính chỉ số
    F1 với dung sai ±0,5 giây.

-   Nếu F1 dưới 0,80, thống nhất lại quy ước rồi gán nhãn lại khối đó.

d\) **Xác minh mù (01 giờ còn lại).**

-   Mọi sự kiện do v2 hoặc v3 báo được cắt thành đoạn 3 giây.

-   Các đoạn này được trộn với một số lượng bằng như vậy các đoạn 3 giây
    chọn ngẫu nhiên.

-   Người gán nhãn xác định từng đoạn có tiếng ho hay không, mà không
    biết nguồn gốc của đoạn.

đ) **Quy định về quyền riêng tư** theo Mục 16.12 của P1.

**XI. TIÊU CHÍ ĐÁNH GIÁ VÀ PHƯƠNG PHÁP PHÂN TÍCH**

**1. Tiêu chí chính (khẳng định)**

a\) “Hành lang 1–3 m” là các tiếng ho tại P1 và P3 của tập K1, khoảng
120 tiếng ho. Hai thiết bị được ghép cặp trên cùng từng tiếng ho.

b\) Ba đầu ra chính:

| **TT** | **Đầu ra**                                         | **Phương pháp phân tích**                                                                                                                                 | **Điều kiện đạt**                                                                  |
|-------|------------------|--------------------------|----------------------|
| C1     | Độ nhạy của TC-02, tập K1, hành lang 1–3 m         | Tỷ lệ; khoảng tin cậy (KTC) Wilson 95%; KTC bootstrap theo người                                                                                          | Ước lượng điểm từ 60% trở lên **và** cận dưới nhỏ hơn trong hai KTC từ 50% trở lên |
| C2     | Mức cải thiện so với TC-01 trên cùng tiếng ho (H3) | Kiểm định McNemar chính xác hai phía trên các cặp bất đồng; hiệu độ nhạy kèm KTC bootstrap theo người (báo cáo bổ sung KTC Newcombe cho dữ liệu ghép cặp) | p \< 0,05 **và** hiệu ước lượng từ 20 điểm phần trăm trở lên                       |
| C3     | Số phát hiện sai mỗi giờ của v3, tập K3 (03 giờ)   | KTC Poisson chính xác 95%; tỷ số v3/v2 kèm KTC chính xác (nhị thức có điều kiện)                                                                          | Ước lượng điểm không quá 4 lần mỗi giờ                                             |

c\) **Độ chính xác dự kiến.**

-   Với n = 120 và độ nhạy 60% (72/120), KTC Wilson 95% là 51,1–68,3%.

-   Để cận dưới Wilson đạt 50%, cần ít nhất 71/120 tiếng ho được phát
    hiện. KTC bootstrap theo người thường rộng hơn.

-   Với 03 giờ và 12 sự kiện phát hiện sai (4,0 lần mỗi giờ), KTC
    Poisson 95% là 2,07–6,99 lần mỗi giờ.

d\) **Kết luận đối với Q1.**

-   Q1 được kết luận “đạt” khi đồng thời đạt C1, C2 và C3.

-   Trường hợp không đạt, báo cáo rõ tiêu chí chưa đạt cùng mức cải
    thiện đo được.

-   Tiêu chí gốc của P1 (cận dưới từ 70% trở lên tại ô chính) được báo
    cáo song song trên ô H3 của tập K2, không hạ thấp.

**2. Phương pháp thống kê**

a\) **Ghép sự kiện.**

-   Dung sai ±1 giây, ghép một – một, ưu tiên cặp gần nhất (Mục 6 của
    P1).

-   Bù độ trễ hệ thống theo Mục 16.6 của P1.

-   Phân tích độ nhạy với dung sai ±1,5 giây được báo cáo kèm theo.

b\) **Bootstrap theo người.**

-   Lấy mẫu lại có hoàn lại theo người tham gia (tập K1).

-   10.000 lần lặp, hạt giống 2026; KTC theo phân vị 2,5% và 97,5%.

-   Với tập K2, lấy mẫu lại theo tiếng ho.

c\) **Kiểm định McNemar chính xác.** Kiểm định nhị thức hai phía trên b
và c:

-   b là số tiếng ho chỉ TC-02 phát hiện;

-   c là số tiếng ho chỉ TC-01 phát hiện;

-   hiệu độ nhạy bằng (b − c)/n.

d\) **Khoảng tin cậy Poisson chính xác** theo phương pháp Garwood. Tỷ số
tốc độ của hai mô hình trên cùng thời lượng có KTC được suy ra từ KTC
Clopper–Pearson của x₃/(x₂ + x₃), trong đó x₂ và x₃ lần lượt là số phát
hiện sai của v2 và v3.

đ) **Tính toán độc lập.**

-   Chương trình tools/v3/cham_k.py chấm điểm một lần.

-   Một thành viên tính lại C1–C3 bằng bảng tính riêng.

-   Hai kết quả phải trùng khớp.

**3. Đầu ra mô tả**

a\) **Nguồn âm sau cửa đóng.**

-   Độ nhạy của hai thiết bị tại PĐ của tập K1 (khoảng 60 tiếng ho), kèm
    kiểm định McNemar.

-   So sánh PĐ với PĐ+B của TC-02 trong tập K2 (khi có ô PĐ+B), bằng
    hiệu hai tỷ lệ độc lập kèm KTC Newcombe.

b\) **Tập K2 theo từng ô.**

-   Độ nhạy của hai thiết bị theo từng ô, kèm KTC Wilson.

-   Đường cong độ nhạy theo SNR (theo Mục 10.1 của P1) trên các ô hành
    lang.

c\) **Phân loại lỗi của tập K3.**

-   Tỷ lệ phát hiện sai theo loại âm thanh: nói chuyện, cười, đóng cửa,
    bước chân, hắng giọng, loại khác.

-   Độ nhạy và giá trị dự báo dương đối với tiếng ho tự nhiên trên 02
    giờ gán nhãn đầy đủ, kèm cỡ mẫu.

d\) **Vận hành.**

-   Tỷ lệ số phút có nhật ký từ ngày 30/11 đến 04/12/2026 (chuẩn: từ 95%
    trở lên).

-   Tỷ lệ gói ESP-NOW đến Gateway (chuẩn: từ 99% trở lên).

-   Thời gian suy luận lớn nhất.

-   Số lần gián đoạn.

đ) **Đối chiếu vi điều khiển và máy tính.** Số sự kiện TC-01 tự báo
trong K3, so với kết quả của v2 chạy trên máy tính với cùng âm thanh.

**4. Hai tập phụ của nhóm B (mở sau khi đóng băng)**

a\) **Tập K0.** Tiếng ho của nhóm B ghi ngày 26/11/2026. Xử lý bằng v2
và v3 trên máy tính; báo cáo độ nhạy theo từng vị trí P1, P3, P5 và PĐ.

b\) **Tập K4.** Hội thoại của nhóm B ghi ngày 28/11/2026. Báo cáo số
phát hiện sai của v2 và v3 trên mỗi giờ tiếng nói theo kịch bản.

**XII. ĐÁNH GIÁ TUSSIBRIDGE (17:00–18:00 NGÀY 28/11/2026)**

a\) **Chuẩn bị.**

-   **Đo khe chân cửa** (sau khi công bố Đề cương, trước 21:00 ngày
    25/11/2026) tại phòng B2.103
    và 02 phòng liền kề đã đo đáp ứng xung. Mỗi phòng đo 03 điểm (hai
    đầu và giữa cánh cửa); khe của phòng là số nhỏ nhất. Dụng cụ: thước
    bậc in 3D (1,0–8,0 mm, bước 0,2 mm; khe lớn hơn 8,0 mm dùng thước
    4,0–14,0 mm, bước 0,5 mm). Khe nhỏ hơn 1,0 mm được đo bằng chồng
    giấy A4 80 g/m² (mỗi tờ khoảng 0,10 mm): số tờ lớn nhất còn luồn qua
    được nhân 0,10 mm.

-   Số đo sơ bộ tại phòng B2.103 (chiều 25/11/2026, thước bậc): khe
    không đều do cửa lắp lệch; hẹp nhất 3,6 mm (lọt khít), phía bản lề
    5,0 mm, rộng nhất 5,4–5,6 mm. Số đo chính thức là số đo 03 phòng, 03
    điểm mỗi phòng, đo sau khi công bố Đề cương và trước 21:00 ngày
    25/11/2026.

-   **Quy tắc theo chiều cao khe** (ngưỡng 2,0 mm, vì dưới mức này diện
    tích khe trước họng phễu nhỏ hơn khoảng 270 mm² và âm truyền qua khe
    không đáng kể so với âm xuyên qua cánh cửa):

    -   Trường hợp 1: Khe phòng B2.103 từ 2,0 mm trở lên: thực hiện Mục
        XII như mô tả dưới đây.

    -   Trường hợp 2: Khe phòng B2.103 nhỏ hơn 2,0 mm nhưng có phòng
        liền kề từ 2,0 mm trở lên: Mục XII và hai ô PĐ, PĐ+B của tập K2
        chuyển sang phòng có khe lớn nhất.

    -   Trường hợp 3: Không phòng nào đạt 2,0 mm: Mục XII được rút gọn.
        Chỉ đo hai trạng thái, không gắn (0) và biến thể A, mỗi trạng
        thái 03 lần, tại phòng B2.103. Biến thể B không được chế tạo;
        tiêu chí (ii) và Mục XII.đ không áp dụng; ô PĐ+B của tập K2 bị
        bỏ. Giả thuyết H4 được kiểm định bằng tiêu chí (i) trên biến thể
        A, và kết quả được báo cáo kèm số đo khe của cả 03 phòng.

-   Biến thể A chỉ có phễu. Biến thể B gồm phễu và 03 khe λ/4 đứng, rộng
    hết bề ngang phễu, đặt sát họng tại 20, 36 và 51 mm trên trục phễu.
    Khe in dày 7 mm, lót nỉ 1 mm còn 6 mm. Chiều dài danh định tính từ
    miệng khe tới mặt nắp là 36, 30 và 26 mm, ứng với tần số chặn 2,14;
    2,52 và 2,86 kHz.

-   Chiều dài mỗi khe chỉnh được ±2 mm bằng miếng chêm dày 1 mm kê dưới
    nắp; cấu hình danh định dùng 02 miếng cho mỗi khe.

-   Thiết kế ống nhánh tròn đường kính 10 mm của bản nháp trước được
    thay bằng khe ngày 23/11/2026, trước thời hạn đăng ký đề cương. Lý
    do: mô phỏng ma trận truyền cho thấy ống 10 mm chặn gần 0 dB vì tiết
    diện quá nhỏ so với phễu.

-   Phễu đặt bên ngoài khe, họng phễu áp sát cánh cửa, đáy phễu cách sàn
    khoảng 0,5 mm; 8 mm đầu họng không có vách đáy để sàn làm đáy, nhờ
    đó toàn bộ khe từ sàn lên mép cửa đi vào họng. Phễu gắn bằng đế cửa
    dán băng keo VHB tại đoạn khe rộng nhất; vị trí đế được đánh dấu và
    giữ nguyên trong suốt Mục XII và tập K2. Phễu được tháo khỏi ray
    trước mỗi lần mở cửa.

b\) **Phương pháp đo.**

-   Loa đặt tại vị trí Đ1 trong phòng B2.103, cửa đóng.

-   Đo ba trạng thái: không gắn (0), biến thể A, biến thể B. Mỗi trạng
    thái đo 03 lần, thứ tự xáo trộn ngẫu nhiên (hạt giống 2026).

-   Mỗi lần đo phát nhiễu hồng 30 giây và tín hiệu quét tần số 04 lần.

-   **Bước chỉnh tần số, làm trước mọi lần đo chính thức (tối đa 20
    phút).** Đo quét tần số một lần với biến thể A và một lần với biến
    thể B. Trên hiệu B − A, tìm tần số có mức thấp nhất trong vùng ±300
    Hz quanh từng tần số chặn. Các lần đo chỉnh này không tính vào kết
    quả. Nếu lệch quá 50 Hz, thêm hoặc bớt miếng chêm của khe đó (mỗi
    miếng 1 mm), trong giới hạn 0–04 miếng, rồi đo lại. Chỉ dùng vị trí
    tần số để chỉnh, không dùng độ sâu chỗ chặn. Số miếng chêm cuối cùng
    của từng khe được ghi vào nhật ký và giữ nguyên cho toàn bộ phép đo
    và tập K2.

-   TC-02 thu tại vị trí lắp đặt; máy đo mức âm UT353 đặt sát micro ghi
    LAeq.

c\) **Chỉ số.**

-   Độ lợi chèn theo dải 1/3 octave, từ 125 Hz đến 6,3 kHz, bằng mức của
    trạng thái trừ mức của trạng thái 0.

-   Báo cáo giá trị trung bình và độ lệch chuẩn của 03 lần đo.

-   Báo cáo bổ sung chênh lệch mức dB(A) tổng.

d\) **Tiêu chí nghiệm thu.**

-   \(i\) Với ít nhất một biến thể, độ lợi chèn trung bình trên 07 dải
    từ 250 Hz đến 1.000 Hz đạt từ 3 dB trở lên. Đây là phép kiểm định
    giả thuyết H4.

-   \(ii\) So với biến thể A, mức của biến thể B thấp hơn từ 5 dB trở
    lên tại ít nhất 2 trong 3 tần số chặn: 2,14 kHz, 2,52 kHz và 2,86
    kHz. Mức tại mỗi tần số được tính bằng FFT của đáp ứng xung trong
    băng ±50 Hz.

đ) **Lựa chọn biến thể cho tập K2.** Chọn biến thể có độ lợi chèn trung
bình trong dải 250–1.000 Hz lớn hơn.

e\) **Trường hợp không đạt.** Kết quả được báo cáo là kết quả kỹ thuật
âm tính, kèm đầy đủ số đo.

**XIII. NGHIỆM THU TUSSIPOD-5 (17:00–18:00 NGÀY 01/12/2026)**

a\) **Người tham gia:** ít nhất 10 người có phiếu Mẫu số 01/PĐT đã chọn
nội dung D. Không ghi âm, không ghi họ tên; người tham gia được gán mã
P01–P10.

b\) **Chỉ số và tiêu chí:**

| **Chỉ số**                  | **Phương pháp đo**                                                                                                             | **Điều kiện đạt**                                                                                        |
|----------------|---------------------------------|-----------------------|
| Phát hiện tiếng ho chủ động | 10 người × 10 lượt. Mỗi lượt ho nhẹ 2–3 lần; lượt được tính là đúng khi trạm báo ít nhất 01 tiếng ho. Người quan sát ghi nhận. | Từ 95% trở lên **và** cận dưới KTC Wilson từ 90% trở lên. Với 100 lượt, tương đương ít nhất 96/100 lượt. |
| Phát hiện sai khi nói       | 50 lượt (05 lượt mỗi người): nói câu “xin chào, mình không ho” vào ống ngậm                                                    | Không quá 02/50 lượt báo có tiếng ho                                                                     |
| Cắt đỉnh tín hiệu           | Bộ đếm trong firmware: số mẫu đạt ±32.767 trên tổng số mẫu trong 20 lượt ho mạnh. Không lưu âm thanh.                          | Dưới 0,1% số mẫu                                                                                         |
| Nhiệt độ trán               | 10 người. Ngay sau khi trạm đo, đo lại bằng nhiệt kế của Phòng Y tế, cách nhau không quá 02 phút.                              | Sai lệch trung bình trong khoảng ±0,5 °C; báo cáo độ lệch chuẩn và giới hạn đồng thuận Bland–Altman 95%  |
| Thời gian một lượt          | 20 lượt, tính từ lúc nhấn nút BẮT ĐẦU đến khi mã QR hiển thị                                                                   | Trung vị không quá 30 giây                                                                               |
| Quy tắc sàng lọc            | Bảng 20 tổ hợp đầu vào chạy trên firmware                                                                                      | 20/20 tổ hợp đúng mức Xanh, Vàng, Đỏ theo Mục 8.2 của Hồ sơ sản phẩm                                     |
| Không lưu âm thanh          | Kiểm tra mã nguồn công khai; trạm không có thẻ nhớ; mã băm SHA-256 của firmware                                                | 0 byte âm thanh                                                                                          |

c\) **Vệ sinh.**

-   Mỗi lượt sử dụng một ống ngậm giấy mới.

-   Quạt hút vận hành 20 giây qua màng lọc HEPA sau mỗi lượt.

-   Bề mặt trạm được lau bằng cồn 70% vào đầu buổi và sau mỗi người.

**XIV. KHẢO SÁT NHANH (TỪ NGÀY 24/11 ĐẾN NGÀY 27/11/2026)**

a\) **Hình thức:** phiếu Mẫu số 03/PKS gồm 05 câu hỏi, ẩn danh, thực
hiện bằng Google Forms không thu thập địa chỉ thư điện tử, chuyển đến
học sinh qua giáo viên quản nhiệm.

b\) **Chỉ số chính:** tỷ lệ người chọn “Chắc chắn có” hoặc “Có thể có” ở
Câu 3, kèm KTC Wilson 95%.

c\) **Đầu ra mô tả:**

-   tỷ lệ khai báo muộn hoặc không khai báo (Câu 1, tính trên người từng
    có triệu chứng);

-   tần suất các rào cản (Câu 2, 4, 5).

d\) **Loại trừ:** phiếu bỏ trống toàn bộ 05 câu; phiếu gửi sau thời điểm
đóng. Dưới 30 phiếu, kết quả được báo cáo ở mức thăm dò.

**XV. XỬ LÝ DỮ LIỆU THIẾU VÀ LOẠI TRỪ**

a\) **Tiếng ho bị loại khỏi phân tích chính**, với số lượng được báo
cáo:

-   tiếng ho được đánh dấu “?”;

-   tiếng ho bị gián đoạn theo sổ thực địa: người đi qua, loa lỗi, hoặc
    người tham gia không đứng đúng vị trí.

b\) Khoảng thời gian thiết bị mất nguồn, treo, hoặc lệch giờ quá 1 giây
sau hiệu chỉnh được loại khỏi phân tích, không nội suy.

c\) Với người rút khỏi nghiên cứu: xóa tệp, chấm lại không có dữ liệu
của người đó, và báo cáo số người rút lui.

d\) Người thuộc nhóm B vắng mặt tại K1 không được thay thế bằng người
thuộc nhóm A. K1 được thực hiện với số người có mặt.

đ) Mọi kết quả đều được báo cáo đầy đủ, kể cả khi không đạt tiêu chí
hoặc bác bỏ giả thuyết.

**XVI. ĐẠO ĐỨC NGHIÊN CỨU VÀ BẢO VỆ DỮ LIỆU CÁ NHÂN**

a\) **Văn bản pháp lý của hoạt động:**

-   Văn bản số 01/CV-LVS có ý kiến đồng ý của Giáo viên quản nhiệm Dorm
    B2;

-   phiếu đồng thuận Mẫu số 01/PĐT (có chữ ký phụ huynh) đối với người
    tham gia;

-   phiếu đồng thuận Mẫu số 02/PĐT đối với học sinh hành lang tầng 1.

b\) **Thông báo và giờ giấc.** Mỗi buổi ghi âm được thông báo trước ít
nhất 24 giờ và có biển “Đang ghi âm”. Không tổ chức hoạt động sau 22:00.

c\) **Truy cập và lưu trữ.**

-   Chỉ 03 người được tiếp cận dữ liệu: Cao Khải An, Nguyễn Phúc Gia Bảo
    và cô Trương Minh Phương.

-   Dữ liệu được lưu trên thẻ nhớ có mật khẩu và máy tính của Đội thi;
    không lưu trên điện thoại, không đưa lên GitHub.

-   Dữ liệu tải lên Edge Impulse theo đúng Mục VI.6.

d\) **Xóa dữ liệu.** Chậm nhất ngày 10/12/2026, có biên bản, xóa:

-   toàn bộ tệp WAV;

-   các đoạn 3 giây dùng để xác minh;

-   dữ liệu trên Edge Impulse;

-   danh sách đối chiếu mã với họ tên.

Dữ liệu được lưu giữ gồm: bảng số liệu không chứa họ tên; các đáp ứng
xung phòng (tín hiệu đo, không chứa tiếng người, có thể công bố làm dữ
liệu mở); và mô hình đã huấn luyện.

đ) **Giới hạn sử dụng.** Không sử dụng số liệu cho mục đích quản lý nề
nếp hay xử lý kỷ luật. Bảng điều phối chỉ hiển thị khu vực có từ 20 học
sinh trở lên.

e\) **Căn cứ pháp lý:** Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15.

**XVII. THAY ĐỔI SAU ĐĂNG KÝ**

| **TT** | **Ngày** | **Nội dung thay đổi** | **Lý do** |
|--------|----------|-----------------------|-----------|
| 1 | 26/11/2026 | Thẻ nhớ microSD mượn từ TC-01 bị lỗi khi ghi: một số cluster 8.192 byte (0,256 s) chứa dữ liệu ngẫu nhiên thay cho âm thanh. Trong tiếng ồn nền 08:30–10:30 (Mục VI.2), các cluster lỗi được loại theo cùng cách Mục VI.2c và báo cáo thời lượng loại: phần huấn luyện còn 64,4 / 79,0 phút (loại 876 s), phần hiệu chỉnh còn 24,7 / 39,5 phút (loại 891 s), 82 đoạn. Tiêu chí: cluster chứa sector 512 byte có mức trên −8 dBFS và hệ số tương quan hai mẫu liền nhau dưới 0,2. Danh sách loại (loai_tru.csv, SHA-256 4dbef705…2e5a) và tệp cắt (SHA-256 de8adae8…0789) lưu trong nhật ký. Thẻ này không được lắp lại vào TC-01; TC-01 dùng thẻ mới cùng loại, kiểm tra ghi–đọc toàn bộ thẻ trước khi lắp. | Lỗi phát hiện sáng 26/11 khi khôi phục bảng phân vùng thẻ. Bản ghi thử 4 giờ chiều 26/11 với firmware mới vẫn chỉ có 82,9% số giây sạch, xác nhận lỗi nằm ở thẻ. Không ghi lại tiếng ồn nền vì ngày dự phòng 29/11 là Chủ nhật, không có giờ học, nên điều kiện nền khác ngày thường. |
| 2 | 26/11/2026 | Tệp tiếng ồn nền không có ảnh đồng hồ lúc bấm nút. Khung 08:30–10:30 được xác định từ giờ dừng ước lượng 11:27 (±2 phút) và thời lượng thật theo nhật ký firmware (18.623,2 s; tệp 18.393,8 s vì tràn bộ đệm 7.154 lần làm mất 229,4 s mẫu), nội suy tuyến tính. Sai số mốc khoảng ±3 phút, thay cho dưới 2 giây (Mục V.2a). Đoạn cắt dài 7.111,3 s âm thanh, tương ứng 7.200 s thời gian thực. | Không chụp ảnh đồng hồ khi bấm nút. Sai số chỉ dịch ranh giới khung vài phút trong giờ học, hành lang vẫn vắng người. |
| 3 | 26/11/2026 | TC-02 ghi liên tục khoảng 06:17–11:27 thay vì 08:30–10:30. Phần ngoài khung không được nghe, không được xử lý, và bị xóa cùng tệp gốc sau khi cắt. | Đội thi đi học, không có người bấm nút lúc 08:30 và 10:30. |
| 4 | 26/11/2026 | Firmware TC02_Hieu_chuan đổi từ hieu-chuan-1.2 sang hieu-chuan-1.3 từ 12:40 ngày 26/11 (SHA-256 446fa262…d0d0): bấm 40–600 ms mở tệp mới, giữ từ 1,2 s dừng ghi, nhấn 0,6–1,2 s bị bỏ qua; bộ đệm DMA tăng từ 0,5 s lên 2 s; báo trạng thái qua Serial. Hệ số khuếch đại (dịch bit 14), tần số mẫu và cách quy đổi mẫu không đổi, nên phương trình hiệu chuẩn lần 1 vẫn áp dụng. Tiếng ồn nền 26/11 và hiệu chuẩn lần 1 dùng 1.2; các buổi ghi còn lại của Phần thứ nhất, hiệu chuẩn lần 2 và K3 dùng 1.3. Phụ lục 1 ghi phiên bản 1.3. | Với bản 1.2, giữ nút chưa đủ 2 giây bị hiểu là bấm ngắn, mở thêm tệp GHI_0002 (20,6 s, không dùng); rút nguồn khi tệp này đang ghi làm hỏng bảng phân vùng thẻ. Bộ đệm 0,5 s tràn 7.154 lần khi thẻ ghi chậm. |
| 5 | 26/11/2026 | Bản ghi thử TC-02 khoảng 12:43–16:48 ngày 26/11 tại vị trí ghi hành lang tầng 2, có biển “Đang ghi âm” nhưng không thông báo trước 24 giờ (Mục XVI.b). Bản ghi chỉ dùng để kiểm tra thẻ, không dùng cho phân tích nào, và bị xóa. | Kiểm tra thẻ trong điều kiện ghi thật trước các buổi có người tham gia. |
| 6 | 26/11/2026 | Lùi lịch: đo đáp ứng xung (26/11 17:15–18:45) và ghi tiếng ho (26/11 19:00–20:30) chuyển sang Chủ nhật 29/11, ngày dự phòng; phân nhóm (Mục V.1b) chạy lúc 20:10 ngày 26/11 thay vì 17:00, vẫn trước buổi ghi đầu tiên có người tham gia. Từ 28/11, mọi buổi ghi dùng thẻ mới, chỉ sau khi thẻ qua phép thử ghi–đọc lại trên máy tính và một bản ghi thử 2–3 giờ trên TC-02 sạch 100%. Buổi nào hỏng lần nữa thì không còn ngày bù trước khi đóng băng; khi đó báo cáo thiếu dữ liệu tại Mục XVII. | Thẻ lỗi (dòng 1), không có thẻ thay thế trước chiều 27/11. Buổi ghi tiếng ho có 12 người, mất dữ liệu thì không làm lại được. |

<table>
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>XÁC NHẬN CỦA</strong></p>
<p><strong>GIÁO VIÊN HƯỚNG DẪN</strong></p>
<p><em>(Ký, ghi rõ họ tên)</em></p>
<p><strong>Trương Minh Phương</strong></p></td>
<td><p><strong>NGƯỜI LẬP</strong></p>
<p><em>(Ký, ghi rõ họ tên)</em></p>
<p><strong>Cao Khải An</strong></p></td>
<td><p><strong>NGƯỜI LẬP</strong></p>
<p><em>(Ký, ghi rõ họ tên)</em></p>
<p><strong>Nguyễn Phúc Gia Bảo</strong></p></td>
</tr>
</tbody>
</table>

**PHỤ LỤC 1**

**THÔNG SỐ PHIÊN BẢN ĐÓNG BĂNG**

*(Hoàn thiện trước 12:00 ngày 01/12/2026)*

| **Nội dung**                                                                      | **Giá trị** |
|-----------------------------------|-------------------------------------|
| Ngày, giờ đóng băng                                                               |             |
| Kết quả phân nhóm (chỉ ghi mã): A-huấn luyện / A-hiệu chỉnh / B                   |             |
| Số đáp ứng xung đạt chất lượng (trên tổng số 19)                                  |             |
| Mô hình được chọn (dòng của bảng phân tích thành phần; phiên bản Edge Impulse)    |             |
| Ngưỡng; k; g; loại sự kiện dài hơn 2 giây; cổng Kurtosis                          |             |
| S_hc; thành phần (i); thành phần (ii); FP/giờ_hc của cấu hình được chọn           |             |
| Firmware TC-02 (tên tệp, mã SHA-256)                                              |             |
| Firmware hiệu chuẩn TC02_Hieu_chuan (phiên bản, mã SHA-256)                       |             |
| Phép thử đồng nhất bit (số cửa sổ, độ lệch lớn nhất, thời gian suy luận lớn nhất) |             |
| Hệ số khuếch đại TC-01; TC-02                                                     |             |
| Chạy thử 24 giờ (tỷ lệ phút có nhật ký, số lỗi thẻ, tỷ lệ gói đến)                |             |
| Biến thể TussiBridge dùng cho K2                                                  |             |
| Mã ghi nhận trên kho mã nguồn (commit)                                            |             |

**PHỤ LỤC 2**

**BẢNG PHÂN TÍCH THÀNH PHẦN**

*(Hoàn thiện ngày 30/11/2026)*

| **Cấu hình**                        | **Ngưỡng** | **k; g** | **(i) A-hiệu chỉnh 1–3 m** | **(ii) COUGHVID × đáp ứng xung** | **S_hc** | **FP/giờ_hc** |
|-----------------|---------|---------|----------|-----------|---------|----------|
| v2 (đối chứng)                      |            |          |                            |                                  |          |               |
| v3-1: đáp ứng xung thực đo          |            |          |                            |                                  |          |               |
| v3-2: bổ sung mẫu âm khó            |            |          |                            |                                  |          |               |
| v3-3: bổ sung tiếng ho A-huấn luyện |            |          |                            |                                  |          |               |
| Bổ sung bộ lọc sau phân loại        |            |          |                            |                                  |          |               |
| Cổng Kurtosis hoặc v3b (tùy chọn)   |            |          |                            |                                  |          |               |
