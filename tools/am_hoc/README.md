# Âm học: hiệu chuẩn mức âm, cân bằng hai thiết bị, suy hao qua cửa, thời gian vang (Protocol 7.5, 16.8, 16.9)

`am_hoc.py` có ba lệnh (cách dùng ở đầu tệp):

- `hieu-chuan bang.csv`: phương trình dB(A) = a + b·dBFS cho từng thiết bị (≥ 5 mức nhiễu hồng 45–85 dB(A), 30 s mỗi mức;
  tệp `data/phat_lai/tep/nhieu_hong_30s_*.wav` cách nhau 10 dB), R², sai số dư lớn nhất; hệ số khuếch đại số cho TC-02 để
  chênh với TC-01 ≤ 1 dB (16.8).
- `suy-hao ghi_am.wav <t_mo> <t_dong>`: mức theo dải 1/3 octave 125 Hz – 8 kHz khi cửa mở và đóng, suy hao từng dải (16.9).
- `t20 ghi_am.wav <t_no> ...`: T20 theo dải octave 500 Hz – 4 kHz cho từng tiếng nổ bóng bay, trung vị mỗi dải (16.9).

Tệp ghi âm buổi đo 16.9 (11/11, 18:15–18:30) là âm thanh KTX: chỉ xử lý trên máy của Nhóm, xoá cùng tệp kiểm định.

Phép thử `thu_am_hoc.py` (tín hiệu tổng hợp có đáp án) đã đạt ngày 10/11: hiệu chuẩn tìm lại a = 120,5, b = 1,008
(mô phỏng 120 và 1); chênh hai thiết bị −2,01 dB (mô phỏng −2); suy hao tăng theo tần số với bộ lọc thông thấp;
T20 0,605–0,612 s với RT60 mô phỏng 0,6 s.
