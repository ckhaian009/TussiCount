# Mô hình nền trên Edge Impulse: khảo sát, kiểm tra, phân tích

Phục vụ Protocol mục 8. Dự án Edge Impulse **1156522** (TussiCount); mô hình nền v1 = **Impulse #2 “San nhieu -72 dB”**.
Dữ liệu và cách tải lên: `tools/chuan_hoa_am_thanh/`. Kết quả và nhật ký thí nghiệm: `results/mo_hinh_nen_*`.

| Tệp | Việc |
| --- | --- |
| `khao_sat_san_nhieu_mfe.py` | Dùng đúng mã MFE của Edge Impulse (kho `edgeimpulse/processing-blocks`) đo tỉ lệ ô phổ còn giữ ở các mức sàn nhiễu; căn cứ để thử −72 dB thay cho −52 dB |
| `tao_tap_kiem_tra_ben.py` | Tạo tập kiểm tra độ bền: 500 tiếng ho của tập testing × 3 mức SNR (20, 10, 0 dB) trộn với nền ESC-50 fold 5 hoặc giọng nói người nói thuộc tập testing |
| `tai_len_kiem_tra_ben.command` | Tải tập độ bền lên Edge Impulse (gọi công cụ tải chung, nhấp đúp trong Finder) |
| `ghi_diem_tu_ei.py` | Ghi điểm từng mẫu lấy từ Model testing của Edge Impulse ra CSV, kiểm tra thứ tự bằng SHA-256 danh sách tên |
| `phan_tich_kiem_tra.py` | Độ nhạy, độ đặc hiệu, F1, AUC, khoảng tin cậy Wilson và bootstrap theo nhóm, phân tích theo mức âm và nguồn nhiễu |
| `phan_tich_do_ben.py` | Độ nhạy trên tập độ bền theo SNR, so theo cặp với tiếng ho sạch |

Chạy từ thư mục gốc của kho:

```
python3 tools/mo_hinh_nen/khao_sat_san_nhieu_mfe.py /duong/dan/processing-blocks > results/mfe_khao_sat_san_nhieu.txt
python3 tools/mo_hinh_nen/tao_tap_kiem_tra_ben.py
python3 tools/mo_hinh_nen/ghi_diem_tu_ei.py <tep_chuoi> <sha256> mo_hinh_nen_v1 testing
python3 tools/mo_hinh_nen/phan_tich_kiem_tra.py mo_hinh_nen_v1
python3 tools/mo_hinh_nen/ghi_diem_tu_ei.py <tep_chuoi> <sha256> mo_hinh_nen_v1_ben ben
python3 tools/mo_hinh_nen/phan_tich_do_ben.py mo_hinh_nen_v1
```

## Cách lấy điểm từng mẫu từ Edge Impulse

Sau khi bấm **Classify all** ở trang Model testing, điểm từng mẫu nằm ở API
`/v1/api/1156522/classify/all/result/page?variant=<int8|float32>&impulseId=<id>`. Điểm được đọc trong trình duyệt
(phiên đăng nhập của An), xếp theo tên mẫu, mã hoá mỗi mẫu 2 ký tự cơ số 36 = round(p_cough × 1000),
rồi chép sang máy và giải bằng `ghi_diem_tu_ei.py`. SHA-256 của danh sách tên phải khớp bảng kê, nếu không
công cụ dừng. Làm tròn 0,001 không ảnh hưởng: mô hình int8 cho điểm là bội của 1/256.

## Kiểm chứng đã làm

- `phan_tich_kiem_tra.py` chạy thử trên điểm giả lập trước khi có điểm thật.
- Điểm chép sang máy được đối chiếu với ma trận nhầm lẫn tính ngay trong trình duyệt: khớp từng ô.
- Công cụ tải lên được chạy thử với `curl` giả lập (kiểm tra chia lô, nhãn, chạy lại, không ghi key ra đĩa) trước khi chạy thật.
