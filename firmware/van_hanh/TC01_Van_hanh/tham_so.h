// Tham số của firmware vận hành TussiCount. Mọi giá trị trong tệp này được ĐÓNG BĂNG cùng firmware
// (Protocol mục 8, 12, 16.8, 16.13): sau khi đóng băng không sửa cho đến khi chấm xong.
// Mạng Wi-Fi và địa chỉ NTP không thuộc phần đóng băng nên nằm trong tệp /cauhinh.txt trên thẻ nhớ.
#pragma once

// ---------- Thiết bị ----------
#define TEN_THIET_BI "TC-01"
#define PHIEN_BAN_FW "van-hanh-1.0"

// ---------- Mô hình ----------
// Thiết bị chấm MỌI cửa sổ bằng CẢ HAI mô hình (v1 = Impulse #2, v2 = Impulse #3 tăng cường) và ghi điểm của cả hai
// ra thẻ, nên đêm chạy trước khi chọn mô hình (Protocol 16.7) vẫn tính lại được bằng mô hình được chọn.
// MO_HINH_DEM chỉ quyết định mô hình nào gộp sự kiện trực tiếp trên thiết bị (tệp _su_kien.csv): 1 = v1, 2 = v2.
#define MO_HINH_DEM 2

// ---------- Ngưỡng và bộ lọc sau phân loại (Protocol mục 8) ----------
// Điền giá trị do tools/chay_mo_hinh/chon_nguong.py chọn trên phần để sửa, rồi đóng băng.
// Điểm của MỌI cửa sổ vẫn được ghi ra thẻ (tệp _diem.csv), nên số đếm có thể tính lại bằng gop_su_kien.py
// với ngưỡng đã đóng băng cho các đêm chạy trước thời điểm đóng băng.
const float NGUONG = 0.50f;       // θ: cửa sổ vượt ngưỡng khi p_cough ≥ θ
const int K_CUA_SO = 1;           // số cửa sổ vượt ngưỡng tối thiểu của một sự kiện (1 hoặc 2)
const float G_NGHI_S = 0.0f;      // khoảng nghỉ tối thiểu giữa hai sự kiện: 0; 0,5 hoặc 1 giây

// ---------- Quy đổi mẫu micro (Protocol 16.8) ----------
// Mẫu 32 bit của INMP441 → 16 bit: (raw × HE_SO_KHUECH_DAI) >> 16, chặn trong giới hạn 16 bit.
// PHẢI giống firmware kiểm định ghi WAV của TC-02 (T4: hệ số 8) để mô hình nhận cùng một đầu vào.
const int HE_SO_KHUECH_DAI = 8;

// ---------- Hiệu chuẩn mức âm (Protocol 7.5) ----------
// dB(A) = HC_A × dBFS + HC_B, lập bằng hồi quy với máy đo UT353. Chưa hiệu chuẩn thì để DA_HIEU_CHUAN false:
// cột dB(A) trong nhật ký để trống, cột dBFS vẫn ghi để quy đổi lại sau.
const bool DA_HIEU_CHUAN = false;
const float HC_A = 1.0f;
const float HC_B = 0.0f;

// ---------- Chân nối (ESP32-S3 N16R8) ----------
const int PIN_MIC_SCK = 4;
const int PIN_MIC_WS = 5;
const int PIN_MIC_SD = 6;
const int PIN_SD_CS = 15;     // thẻ nhớ dời từ 10–13 sang 15–18 ngày 12/11
const int PIN_SD_MOSI = 16;
const int PIN_SD_SCK = 17;
const int PIN_SD_MISO = 18;
// Đo điện áp nguồn: cầu chia 100 kΩ / 100 kΩ từ chân 5V xuống chân ADC này. Chưa lắp cầu chia thì để -1
// (cột điện áp trong nhật ký để trống).
const int PIN_DIEN_AP = -1;
const float HE_SO_CAU_CHIA = 2.0f;

// ---------- Thời gian ----------
const uint32_t NTP_CHU_KY_MS = 30UL * 60UL * 1000UL;   // đồng bộ NTP mỗi 30 phút (16.5)
#define MUI_GIO "ICT-7"                                 // giờ Việt Nam, UTC+7
