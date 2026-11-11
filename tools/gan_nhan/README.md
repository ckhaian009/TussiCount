# Gán nhãn, nghe xác minh và chấm tầng kiểm định 3 (Protocol 7.3, 8, 16.1–16.3, 16.12; việc t19, t26, t27, t33)

**Âm thanh KTX chỉ nằm trên máy tính của Nhóm, ở `~/TussiCount_KTX`** (ngoài thư mục Documents đồng bộ iCloud, ngoài kho
GitHub). Các công cụ từ chối ghi vào thư mục nằm trong Documents. Không tải bất kỳ đoạn nào lên dịch vụ trực tuyến
(kể cả Edge Impulse). Người nghe chỉ quyết định có hay không có tiếng ho và thời điểm; không chép, ghi chú hay trích dẫn
lời nói (16.12).

| Tệp | Việc |
| --- | --- |
| `ung_vien_phan_de_sua.py` | Phần để sửa (11/11): cắt đoạn 3 s quanh mọi sự kiện ở θ = 0,50; phiếu nghe `co_ho` (1/0/?) cho `chon_nguong.py` |
| `gan_nhan.py chon-doan` | Chọn 4 trong 9 khối 30 phút của phần để chấm (seed 2026); khối sớm nhất do hai người gán độc lập |
| `gan_nhan.py f1` | F1 đồng thuận ±0,5 s giữa hai tệp nhãn Audacity; < 0,80 thì thống nhất lại và gán lại |
| `gan_nhan.py xac-minh-tao` | 5 khối còn lại: đoạn 3 s quanh mỗi sự kiện thiết bị + cùng số đoạn ngẫu nhiên, trộn thứ tự; `phieu_mu.csv` cho người nghe, `khoa_mu.csv` giữ riêng |
| `../cham/cham_phan_de_cham.py` | `chay-mot-lan`: chạy mô hình đã đóng băng đúng một lần (khoá bằng `lan_chay.json`); `cham`: phát hiện sai mỗi giờ trên 4,5 giờ, độ nhạy và giá trị dự báo dương tiếng ho tự nhiên, 16.1, 16.2, 16.3, 10.6 |

Nhãn trong Audacity: đặt nhãn tại đầu mỗi tiếng ho, chữ `h`; không chắc thì `?`. Xuất bằng File → Export → Export Labels.
Các tiếng ho cách nhau dưới 1 s được gộp thành một tiếng ho chuẩn.

## Phép thử đã chạy (10/11/2026)

Trên hai tệp tổng hợp dài 2,5 giờ và 2 giờ (266 tiếng ho Coswara chèn vào nhiễu trắng −50 dBFS, biết trước thời điểm):
`chay-mot-lan` chạy đúng và từ chối lần chạy thứ hai; `chon-doan` chọn 4/9 khối; `f1` cho 1,000 với hai tệp nhãn lệch
±0,1 s; `xac-minh-tao` và `cham` chạy đúng, đủ các mục. Mô hình v1 chỉ báo 1 sự kiện trong 4,5 giờ ở điều kiện này
(xem phát hiện thăm dò trong `tools/chay_mo_hinh/README.md`).
