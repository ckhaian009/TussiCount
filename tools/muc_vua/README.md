# Mức “vừa” cho tầng kiểm định 1

Protocol mục 7.1: mức “vừa” bằng mức đỉnh dB(A) trung bình ở 1 m của 20 tiếng ho nhẹ theo hiệu lệnh của hai thành viên, đo trước buổi phát đầu tiên và ghi tại mục 12.

1. Điền `results/muc_vua_phieu.csv` trong lúc đo (cột `dBA_dinh`; cột `nen_dBA` ghi mức nền đo trước buổi; lần đo hỏng thì ghi `x` ở cột `khong_hop_le` và lý do ở `ghi_chu`, rồi đo bù).
2. Chạy `python3 tools/muc_vua/muc_vua.py` để tính trung bình, độ lệch chuẩn, khoảng tin cậy và dòng điền mục 12.

Phép thử của công cụ: AI đã chạy thử với 20 giá trị giả lập. Trước khi dùng kết quả thật, nhóm tự đối chiếu một lần với phép tính trên bảng tính (hàm AVERAGE, STDEV) và ghi vào nhật ký kiểm chứng. Phiếu thật để trống trước khi đo.
