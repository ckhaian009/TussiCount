# Thời tiết theo ngày, Cần Thơ, 12–18/11/2026 (Protocol 16.11, chỉ mô tả)

- **Nguồn:** Open-Meteo Forecast API, ô lưới gần THPT FPT Cần Thơ (10,018° N; 105,762° E; cao 4 m), múi giờ Asia/Ho_Chi_Minh. Lấy ngày 17/11/2026 khoảng 11:50.
- **Truy vấn:** `https://api.open-meteo.com/v1/forecast?latitude=10.045&longitude=105.747&daily=temperature_2m_max,temperature_2m_min,temperature_2m_mean,relative_humidity_2m_mean,relative_humidity_2m_max,relative_humidity_2m_min,precipitation_sum&timezone=Asia%2FHo_Chi_Minh&start_date=2026-11-12&end_date=2026-11-18`
- **Loại số liệu:** 12–16/11 là số liệu mô hình cho ngày đã qua (không phải trạm đo); 17/11 một phần là dự báo; 18/11 là dự báo. Sau 18/11 lấy lại một lần nữa và thay cột của 17–18/11, ghi ngày lấy lại.
- **Số lượt khám hô hấp theo ngày:** đang xin phòng y tế (chỉ con số tổng). Nếu không có, báo cáo là dữ liệu thiếu (mục 13), không ước lượng.
- Không dùng để kiểm định thống kê; chỉ vẽ cạnh số đếm mỗi đêm làm bối cảnh.
