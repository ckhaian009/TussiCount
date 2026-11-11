# Phân tích thống kê (Protocol mục 9, 10, 16; việc t18, t35, t37–t40)

Viết và thử trên dữ liệu mô phỏng **trước khi có dữ liệu**; khi có dữ liệu chỉ chạy, không sửa cách tính.

| Tệp | Việc |
| --- | --- |
| `ghep_su_kien.py` | Ghép một–một sự kiện với tiếng ho chuẩn trong ±1 s, ưu tiên cặp gần nhất, bù độ trễ (16.6), khoảng loại trừ (mục 13) |
| `thu_ghep_su_kien.py` | 12 tình huống có đáp án tính tay + kiểm tra chỉ số (việc t18) |
| `thong_ke.py` | Wilson, Poisson chính xác, cận dưới MTBF, bootstrap theo cụm, chênh độ nhạy theo người, logistic sai số chuẩn theo cụm, Spearman, sai số số đếm, F1, kappa, SNR tại độ nhạy mục tiêu |
| `thu_thong_ke.py` | So với giá trị đã biết (Protocol mục 11) và dữ liệu mô phỏng |
| `phan_tich_h1_h2.py` | H1 (logistic, tiêu chí a và b), H2 (bootstrap 10.000 lần theo người), phân tích phụ 10.1–10.4 |
| `tao_bang_tang2.py` | Tầng kiểm định 2: quy thời điểm trang bấm giờ về giờ NTP bằng 3 bíp đầu (và cuối) buổi, ghép mức dB(A) theo số thứ tự, mức ồn nền của phút, ghép với sự kiện TC-01 → `tang2.csv` |
| `mo_phong_canh_bao.py` | Quy tắc cảnh báo 16.4 (10.000 chuỗi mỗi kịch bản) và mức tăng nhỏ nhất phát hiện được 10.5 |

Chấm tầng kiểm định 3 nằm ở `tools/cham/cham_phan_de_cham.py`.

## Phép thử đã chạy (10/11/2026)

- `thu_ghep_su_kien.py`: 12/12 tình huống và phép tính chỉ số đạt.
- `thu_thong_ke.py`: đạt. Wilson 80/100 = 71,1–86,7% và Poisson 18 sự kiện/4,5 giờ = 2,4–6,3 mỗi giờ, khớp Protocol mục 11.
  Lần chạy đầu sai 2 phép thử vì đáp án viết sai dung sai (MTBF so với t/2,9957 thay vì giá trị chính xác; so bằng tuyệt đối
  số thực của Spearman); đã sửa đáp án, không sửa hàm.
- `phan_tich_h1_h2.py --mo-phong`: dữ liệu mô phỏng có cửa giảm 18 dB, ho thật khó hơn phát lại; phân tích tìm lại đúng:
  hệ số khoảng cách và mức ồn âm, KTC dưới 0; độ dốc mức theo khoảng cách −20,8 dB/decade (mô phỏng −20); 10.2 KTC hệ số
  cửa chứa 0 (mô phỏng chỉ có suy hao mức); H2 chênh −0,12, KTC dưới 0.
- `tao_bang_tang2.py --thu` (10/11): mô phỏng đồng hồ điện thoại lệch −2,4 s và trôi 0,12 s/giờ, phản xạ 0,22 s,
  thiết bị trễ 0,45 s, nhóm bíp cuối thiếu một lần chạm, một lần chạm đã huỷ, một tiếng ho gián đoạn, hai mức dB(A)
  bỏ trống: thời điểm tiếng ho chuẩn lệch thời điểm ho thật tối đa 0,21 s; loại bỏ, ghép, mức dB(A) đều đúng; đạt.
  Độ lệch còn lại chủ yếu do độ trễ khởi động `afplay` (trình phát ghi giờ ngay trước khi gọi), nhỏ hơn nhiều so với dung
  sai ±1 s.
- `mo_phong_canh_bao.py --do-nhay 0.8 --sai-moi-gio 4` (giá trị giả định): khoảng 0,63 cảnh báo sai trong 30 đêm.
  Chạy lại với số đo thật sau khi chấm.
