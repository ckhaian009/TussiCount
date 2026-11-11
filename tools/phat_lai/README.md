# Trình phát thí nghiệm, tầng kiểm định 1 (Protocol 7.1; việc t20)

| Tệp | Việc |
| --- | --- |
| `lap_lich_phat.py` | Lập lịch 3 buổi từ `results/coswara_playlist.csv` (seed 2026) → `results/lich_phat_lai.csv` |
| `tao_tep_phat.py` | Tạo tệp phát đã nhân hệ số khuếch đại (0 / −10 / −20 dB), bíp đồng bộ, nhiễu hồng 30 s ở 5 mức → `data/phat_lai/tep/`; bảng mức số trọng số A → `results/phat_lai_muc_so.csv` |
| `phat_lai.py` | Trình phát chạy trong Terminal trên MacBook nối loa AUX; chỉ cần Python chuẩn và `afplay` có sẵn của macOS; ghi nhật ký từng lần phát |

## Lịch (results/lich_phat_lai.csv)

- Khung ồn (từ 20:30): mỗi ô chia đều ba buổi (150 tiếng ho mỗi buổi).
- Khung yên tĩnh (từ 21:00): buổi 2 (dự kiến 13/11) dành 21:00–21:30 cho tầng kiểm định 2, nên chỉ phát hai khối hành lang
  1 m và 3 m, 40 tiếng ho mỗi khối (7 nhỏ, 26 vừa, 7 lớn); phần còn lại chia đều buổi 1 và 3 (260 tiếng ho mỗi buổi).
- Đầu buổi (trong khung ồn): đo suy hao qua cửa (nhiễu hồng 30 s cửa mở, 30 s cửa đóng), 3 bíp đồng bộ, 10 tiếng ho kiểm
  tra (hành lang, 1 m, mức vừa, cùng 10 tệp cả ba buổi).
- Đầu mỗi khối: tệp hiệu chuẩn (tiếng ho kiểm tra có stt nhỏ nhất, stt 148) phát 3 lần ở mức vừa; nhập mức đọc trên máy đo.
- Thứ tự khối ngẫu nhiên trong mỗi khung; trong khối, ba mức độ lớn xen kẽ ngẫu nhiên; cách nhau 8 s.

**Thời gian rất sát.** Với 8 s mỗi lần phát, 30 s đổi vị trí loa mỗi khối và 2 phút đầu buổi:
khung ồn 28,7/30 phút; khung yên tĩnh buổi 1 và 3 là 40,1/45 phút; buổi 2 là 12,5/15 phút.
Cần đánh dấu sẵn trên sàn các vị trí 1 m, 3 m, 5 m ở hành lang và trong phòng B2.103 (đo bằng thước dây từ micro TC-01),
để mỗi lần đổi khối không quá 30 giây. Trình phát hiện thời gian phát còn lại của khung ở đầu mỗi khối.

## Chạy

Chuẩn bị (một lần, máy có numpy, scipy, soundfile): `python3 tools/phat_lai/tao_tep_phat.py`
(SHA-256 cả thư mục `data/phat_lai/tep` ngày 10/11: `7a220e6fa6ab55b3d7d65fc038ceca8e7feaca944631122cf4003c8df97b0990`).

Mỗi buổi, trong Terminal, từ gốc kho:

```
python3 tools/phat_lai/phat_lai.py 1 on          # 20:30: đầu buổi + khung ồn
python3 tools/phat_lai/phat_lai.py 1 yen_tinh    # 21:00: khung yên tĩnh (buổi 2: 21:30)
python3 tools/phat_lai/phat_lai.py 2 bip dau     # buổi 2, 21:00: 3 bíp đồng bộ cho trang bấm giờ tầng kiểm định 2
python3 tools/phat_lai/phat_lai.py 2 bip cuoi    # cuối phần tầng kiểm định 2: 3 bíp nữa để đo trôi đồng hồ
```

Trang bấm giờ tầng kiểm định 2 (trên điện thoại người quan sát 1): artifact “Bấm giờ ho thật”. Người quan sát 1 chạm BÍP
đúng lúc nghe mỗi tiếng bíp, rồi chạm HO đúng lúc nghe mỗi tiếng ho; người quan sát 2 nhập mức dB(A) theo số thứ tự.
Lập bảng cho phân tích: `tools/phan_tich/tao_bang_tang2.py`.

Trong lúc phát tự động: `g` đánh dấu tiếng ho vừa phát bị gián đoạn (người đi qua, loa lỗi…), `p` tạm dừng/tiếp tục,
`q` dừng hẳn. Nhật ký: `results/phat_lai_nhat_ky/` (thời điểm phát theo đồng hồ máy, độ lệch đồng hồ đo bằng `sntp`
đầu buổi, mức đo nhập tay). Thời điểm tiếng ho chuẩn = `t_phat_epoch` trừ độ trễ hệ thống tính theo 16.6.

Mức tại micro của một tiếng ho = mức đo của tệp hiệu chuẩn trong khối (trung bình 3 lần) + (`lafmax_so_db` của tiếng ho −
`lafmax_so_db` của tệp hiệu chuẩn), lấy trong `results/phat_lai_muc_so.csv` (Protocol 7.1, “Đo tại chỗ”).

## Phép thử đã chạy (10/11/2026)

- `lap_lich_phat.py` tự kiểm: 1.050 tiếng ho trong ô, mỗi tiếng đúng một lần, đúng ô và đúng hệ số khuếch đại.
- Chạy `phat_lai.py --thu --nhanh` cho cả 6 phần (3 buổi × 2 khung): ghi đủ 1.176 lần phát theo lịch, không thiếu, không
  thừa, không lặp.
- Đoạn ho tạo lại từ Coswara gốc (lấy từ GitHub iiscleap/Coswara-Data) bằng `tools/chuan_bi_phat_lai.py`: điểm cắt khớp
  `coswara_playlist.csv` ở cả 1.100 tệp (lệch lớn nhất 0,0003 s, do làm tròn 3 chữ số), số vùng ho khớp 1.100/1.100.
- Bộ lọc A so với giá trị chuẩn IEC 61672: lệch ≤ 0,15 dB từ 31,5 Hz đến 10 kHz, 0,4 dB ở 16 kHz.
- **Chưa thử:** phát thật qua `afplay` và loa trên MacBook; đo độ trễ (16.6) ở buổi thật.

## Lỗi của AI phát hiện khi thử

- Lịch đầu tiên chia phần dư luôn cho buổi 1 (162/144/144 tiếng ho khung ồn) và để buổi 2 phát đủ 6 khối trong 15 phút
  yên tĩnh: phép ước lượng thời gian cho thấy vượt khung. Đã sửa: xoay vòng phần dư, buổi 2 chỉ phát hai khối hành lang.
- Đổi tần số 44,1 kHz → 48 kHz làm đỉnh vượt 0 dBFS ở một tệp (stt 576); đã giữ nguyên mức đỉnh của đoạn gốc sau khi đổi.
- Bộ lọc A thiết kế trực tiếp ở 48 kHz lệch −1,2 dB tại 10 kHz; đã tính ở 192 kHz.
