# Chuẩn bị và tải dữ liệu mô hình nền lên Edge Impulse

Phục vụ Protocol mục 8 (mô hình nền huấn luyện trên dữ liệu mở). Toàn bộ dữ liệu ở đây là dữ liệu mở;
**không có âm thanh ghi tại KTX**. Âm thanh nằm trong `data/` (không đưa lên GitHub); kho chỉ chứa mã và
bảng kê trong `results/`.

| Tệp | Việc |
| --- | --- |
| `chuan_bi_du_lieu_ei.py` | Cắt và chuẩn hoá dữ liệu: WAV 16 kHz, một kênh, PCM 16 bit, mỗi đoạn đúng 1 giây; chia huấn luyện/kiểm tra theo nhóm; ghi bảng kê |
| `kiem_tra.py` | Phép thử cho dữ liệu đã chuẩn bị (định dạng, mức, rò rỉ nhóm, nhãn, số tệp) |
| `tai_len_edge_impulse.command` | Tải `data/ei_upload` lên dự án Edge Impulse 1156522 qua Ingestion API (nhấp đúp trong Finder) |

Thứ tự chạy, từ thư mục gốc của kho:

```
python3 tools/chuan_hoa_am_thanh/chuan_bi_du_lieu_ei.py     # tạo data/ei_upload và bảng kê
python3 tools/chuan_hoa_am_thanh/kiem_tra.py                # phải in "KET QUA: DAT"
# nhấp đúp tools/chuan_hoa_am_thanh/tai_len_edge_impulse.command, dán API key vào hộp thoại
```

## Nguồn và cách cắt

| Nhãn | Nguồn | Cách lấy đoạn 1 giây |
| --- | --- | --- |
| cough | COUGHVID 3.0: 3.000 bản ghi có `cough_detected` ≥ 0,80 (`results/coughvid_chon_3000.csv`) | Tìm vùng năng lượng (khung 20 ms, bước 10 ms, nhấn tần cao 0,97), lấy tối đa 3 vùng to nhất cách nhau ≥ 0,4 s; mỗi vùng cắt 1 s, điểm bắt đầu tiếng ho nằm ngẫu nhiên trong [0,05; 0,35] s của đoạn |
| noise | ESC-50 (bỏ lớp `coughing`) | Mỗi tệp 5 s chia 5 đoạn, bỏ đoạn im lặng (RMS < −65 dBFS), lấy ngẫu nhiên tối đa 3 đoạn |
| noise | Common Voice 27.0 tiếng Việt (1.000 đoạn) | Đoạn 1 s liên tiếp có tiếng nói (RMS ≥ −50 dBFS), tối đa 4 đoạn mỗi tệp |

Chia huấn luyện/kiểm tra theo nhóm để một bản ghi, một người nói hay một đoạn gốc không nằm ở cả hai tập:
COUGHVID theo bản ghi (20% sang kiểm tra, seed 2026); ESC-50 theo fold có sẵn (fold 5 làm kiểm tra);
Common Voice theo người nói (20% sang kiểm tra, seed 2026).

Mức: mỗi đoạn được chuẩn hoá đỉnh về mức ngẫu nhiên đều trong [−35; −3] dBFS, cùng phân bố cho hai nhãn,
để mô hình không học “to là ho”.

## Kết quả chuẩn bị (09/11/2026)

| Tập | cough (COUGHVID) | noise ESC-50 | noise Common Voice | Tổng |
| --- | ---: | ---: | ---: | ---: |
| training | 6.362 | 4.527 | 2.285 | 13.174 |
| testing | 1.595 | 1.130 | 740 | 3.465 |

Nhóm: COUGHVID 2.392 bản ghi huấn luyện / 597 kiểm tra; Common Voice 183 / 45 người nói; ESC-50 fold 1–4 / fold 5.
10 bản ghi COUGHVID không tìm được vùng ho, 1 bản ghi lỗi giải mã (ghi trong `results/ei_du_lieu_mo_hinh_nen_tom_tat.json`).
`kiem_tra.py`: 16.639 tệp, 3.222 nhóm, **KET QUA: DAT**.

## Tải lên Edge Impulse

- Ingestion API `/api/<training|testing>/files`, 100 tệp mỗi yêu cầu, 3 yêu cầu song song, nhãn theo tên thư mục,
  `x-disallow-duplicates: 1` (máy chủ từ chối tệp trùng nội dung). Tập huấn luyện/kiểm tra giữ nguyên như khi chia.
- API key hỏi qua hộp thoại mỗi lần chạy, chỉ nằm trong bộ nhớ; không ghi ra đĩa, không ghi vào nhật ký,
  truyền cho `curl` qua stdin nên không hiện trên dòng lệnh.
- Chạy lại an toàn: bỏ qua lô đã xong. Cuối lần chạy, công cụ đếm số mẫu trên dự án và so với số tệp trên máy.
- Nhật ký: `data/ei_upload/nhat_ky_tai_len.txt`; tóm tắt: `results/ei_tai_len_ket_qua.txt`.

## Lưu ý về iCloud

Thư mục Documents trên máy của An đang đồng bộ iCloud, nên mọi thứ trong kho (kể cả `data/`) bị đẩy lên iCloud.
Với dữ liệu mở thì không sao, nhưng **âm thanh ghi tại KTX không được để trong kho này** (Protocol mục 8):
lưu ở thư mục không đồng bộ, ví dụ `~/TussiCount_KTX`.
