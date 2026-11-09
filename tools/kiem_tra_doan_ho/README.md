# Kiểm tra đoạn ho Coswara đã cắt

Phép thử cho công cụ `tools/chuan_bi_phat_lai.py` (Protocol mục 7.1): mỗi đoạn phải là đúng một tiếng ho, không cụt đầu hoặc đuôi.

| Tệp | Việc | Ai chạy |
| --- | --- | --- |
| `kiem_tu_dong.py` | Phép thử tự động trên cả 1.100 đoạn: tái lập thuật toán cắt, định dạng, dấu hiệu nghi lỗi | An |
| `chon_50_doan.py` | Chọn ngẫu nhiên 50 đoạn (seed 5050), chép thành `01.wav`…`50.wav`, vẽ dạng sóng bản ghi gốc quanh đoạn cắt, tạo phiếu nghe | An |
| `tong_hop_nghe.py` | Tổng hợp phiếu nghe: tỉ lệ đúng, khoảng tin cậy Wilson 95%, cơ cấu lỗi, đối chiếu với phép thử tự động | Bảo |

Chạy từ thư mục gốc của kho:

```
python3 tools/kiem_tra_doan_ho/kiem_tu_dong.py
python3 tools/kiem_tra_doan_ho/chon_50_doan.py
python3 tools/kiem_tra_doan_ho/tong_hop_nghe.py
```

Âm thanh nằm trong `data/` (không đưa lên GitHub). Chỉ đưa lên kho: mã nguồn, `results/kiem_tra_doan_ho_tu_dong.csv`, `results/nghe_thu_50_phieu.csv` (không chứa âm thanh).

## Mã kết quả khi nghe

| Mã | Nghĩa |
| --- | --- |
| DUNG | Đúng một tiếng ho, có đủ tiếng bật đầu và phần tắt dần cuối |
| CUT_DAU | Mất tiếng bật đầu: đoạn bắt đầu giữa lúc đang có tiếng |
| CUT_DUOI | Mất phần cuối: đoạn dừng đột ngột khi tiếng ho còn to |
| HAI_TIENG | Có từ hai tiếng ho trở lên, hoặc có đầu của tiếng ho kế tiếp |
| KHONG_HO | Không phải tiếng ho (hắng giọng, nói, tiếng động) |
| KHAC | Lỗi khác, ghi rõ ở cột ghi_chu |

## Ghi chú lỗi của AI và cách nhóm phát hiện

- 09/11/2026: bản đầu của `kiem_tu_dong.py` cắt lại đoạn theo thời điểm đã làm tròn 3 chữ số trong `coswara_playlist.csv`, nên lệch tới 0,5 ms so với đoạn gốc và báo nhầm 80 đoạn “không tái lập được”. Sửa: chạy lại chính hàm cắt để lấy thời điểm chính xác, chỉ so thời điểm đã làm tròn với sai số 0,6 ms. Sau khi sửa: 0/1.100 đoạn lỗi tái lập và định dạng.
- Các dấu hiệu `nghi_*` là quy tắc thô do AI đề xuất, chưa được kiểm chứng; chỉ dùng để đối chiếu với kết quả nghe, không dùng để loại tệp.
