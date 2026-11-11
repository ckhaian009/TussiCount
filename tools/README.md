# tools

Các công cụ thí nghiệm do nhóm viết cùng trợ lý AI. Mỗi công cụ một thư mục con gồm:

- mã nguồn;
- phép thử kiểm chứng độc lập với AI;
- ghi chú lỗi AI đã mắc và cách nhóm phát hiện, sửa.

| Thư mục | Việc |
| --- | --- |
| `chuan_hoa_am_thanh/` | Chuẩn bị dữ liệu mở 16 kHz cho Edge Impulse, phép thử, tải lên (t17) |
| `mo_hinh_nen/` | Khảo sát sàn nhiễu MFE, tập kiểm tra độ bền, phân tích điểm (t17) |
| `tang_cuong/` | Kho RIR và dữ liệu tăng cường vang + nền ồn (sửa đổi 16.7) |
| `chay_mo_hinh/` | Bộ chạy thư viện Edge Impulse trên máy tính, gộp sự kiện, luồng kiểm tra, chọn ngưỡng (t19) |
| `kiem_tra_doan_ho/`, `chuan_bi_phat_lai.py` | Cắt và nghe kiểm tra đoạn ho Coswara (t16, t52) |
| `phat_lai/` | Lịch, tệp phát và trình phát tầng kiểm định 1 (t20); bíp đồng bộ cho trang bấm giờ tầng kiểm định 2 (t21) |
| `muc_vua/` | Mức “vừa” từ 20 tiếng ho thật (t28) |
| `am_hoc/` | Hiệu chuẩn mức âm, cân bằng hai thiết bị, suy hao qua cửa, thời gian vang (7.5, 16.8, 16.9) |
| `gan_nhan/`, `cham/` | Nghe xác minh phần để sửa, gán nhãn, xác minh mù, chấm tầng kiểm định 3 (t19, t26, t27, t33) |
| `phan_tich/` | Ghép sự kiện ±1 s, thống kê, bảng tầng kiểm định 2, H1, H2, phân tích phụ, mô phỏng cảnh báo (t18, t21, t35, t37–t40) |
