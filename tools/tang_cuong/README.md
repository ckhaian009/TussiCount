# Tăng cường dữ liệu bằng vang tổng hợp và nền ồn (Protocol sửa đổi 16.7)

Mô hình nền v1 nhận tốt tiếng ho trên nền yên nhưng hụt mạnh khi có nền ồn (`results/mo_hinh_nen_v1.md`, mục 5).
Thư mục này tạo dữ liệu cho mô hình có tăng cường (Impulse #3). Toàn bộ là dữ liệu mở, **không dùng âm thanh ghi tại KTX**.

| Tệp | Việc |
| --- | --- |
| `tao_rir.py` | Tạo kho đáp ứng xung phòng (RIR) bằng pyroomacoustics: 400 RIR huấn luyện (seed 2026), 200 RIR kiểm tra (seed 2027) |
| `tao_du_lieu_tang_cuong.py` | Tích chập đoạn 1 s với RIR, trộn nền ồn SNR 0–20 dB, chuẩn hoá mức; chỉ cần numpy, scipy |
| `kiem_tra.py` | Phép thử: định dạng, mức, không rò rỉ giữa hai tập, nhãn, số lượng, kho RIR; phải in `KET QUA: DAT` |

Thứ tự chạy, từ gốc kho:

```
python3 tools/tang_cuong/tao_rir.py                  # đã chạy 10/11; kết quả ở data/tang_cuong/ và results/tang_cuong_rir.csv
python3 tools/tang_cuong/tao_du_lieu_tang_cuong.py   # cần data/ei_upload (dữ liệu mô hình nền)
python3 tools/tang_cuong/kiem_tra.py
EI_DATA=data/ei_tang_cuong bash tools/chuan_hoa_am_thanh/tai_len_edge_impulse.command   # dán API key vào hộp thoại
```

## Kho RIR (10/11/2026)

- Phòng hình hộp: 70% dạng hành lang (dài 8–25 m, rộng 1,8–3,5 m), 30% dạng phòng (3–8 × 3–6 m), cao 2,7–3,5 m.
- RT60 mục tiêu đều trong [0,3; 1,2] s; hệ số hấp thụ hiệu chỉnh lặp đến khi T20 đo trên RIR lệch mục tiêu ≤ 10%
  (600/600 RIR đạt; lệch lớn nhất 9,9%).
- Micro sát tường (0,05–0,20 m), cao 1,5–2,0 m như thiết bị; nguồn cao 1,0–1,7 m. Khoảng cách được bốc trước,
  đều trong [1; 5] m, rồi mới tìm phòng đặt được (lần đầu bốc phòng trước thì khoảng cách lệch về phía gần,
  trung bình 2,46 m; đã sửa, nay trung bình 3,0 m, mỗi khoảng 1 m có 134–161 RIR).
- Hai kho tách biệt: tập kiểm tra tăng cường không dùng chung RIR với dữ liệu huấn luyện.

## Cách tạo dữ liệu

- **Đoạn ho**: mỗi đoạn ho của một tập được tích chập với một RIR ngẫu nhiên của kho cùng tập, giữ 1 s đầu, trộn một đoạn
  nền cùng tập (50% ESC-50, 50% giọng nói) ở SNR đều trong [0; 20] dB (SNR theo RMS cả đoạn, như tập độ bền), rồi chuẩn
  hoá đỉnh về [−35; −3] dBFS.
- **Đoạn không ho** cũng qua RIR, và 50% được trộn thêm một đoạn nền khác nhóm. Lý do: nếu chỉ đoạn ho có vang và nền ồn,
  mô hình có thể học lối tắt mới “có vang/ồn = ho”.
- Tập huấn luyện: 6.362 đoạn ho tăng cường + 6.362 đoạn không ho tăng cường (chọn ngẫu nhiên trong 6.812). Tập kiểm tra:
  tăng cường mọi đoạn (1.595 + 1.870), chỉ dùng để chấm trên máy, không tải lên.
- Nhóm (`nhom` trên Edge Impulse) của đoạn tăng cường là nhóm của đoạn gốc, để validation tách theo nhóm giữ bản gốc và
  bản tăng cường cùng phía.

## Phép thử đã chạy

- Trên bộ dữ liệu thay thế 140 đoạn (bảng kê thật, âm thanh tổng hợp): `kiem_tra.py` đạt; cố ý làm sai một nền (lấy từ
  tập kiểm tra) và một mức đỉnh thì `kiem_tra.py` báo đúng 2 lỗi.
- Dữ liệu thật (10/11, 19:55, trên MacBook): 16.189 tệp (training 6.362 + 6.362, testing 1.595 + 1.870), 506 MB;
  `kiem_tra.py`: DAT.

## Tải lên Edge Impulse

Nhấp đúp `tai_len_tang_cuong.command` trong Finder, dán API key vào hộp thoại. Chỉ tải `data/ei_tang_cuong/training`
(12.724 đoạn); phần testing tăng cường không tải lên. Lần tải 10/11 (20:00–20:12): 128/128 lô, 0 lỗi, 0 trùng; trên dự án
training 25.898 mẫu = 13.174 gốc + 12.724 tăng cường (khớp với máy). Metadata của đoạn tăng cường: `nguon`, `nhom` lấy
đúng từ đoạn gốc trên Edge Impulse, thêm `tang_cuong = 1`.
