// TussiCount – bảng chân nối dùng chung cho các bài kiểm tra T1–T4 (TC-01, ESP32-S3 N16R8)
// Khớp với sơ đồ mạch firmware/so_do_mach/TussiCount_So_do_mach.pdf (bản 2.0, 12/11/2026).
// Mạch ESP32 thường (TC-02) dùng T5 hoặc firmware ghi_kiem_dinh, không dùng tệp này.
#pragma once
const int PIN_LED      = 7;   // chỉ dùng cho T1 khi thử LED trên bàn; TC-01 vận hành không lắp LED (Protocol 16.17)
const int PIN_MIC_SCK  = 4;   // INMP441 SCK
const int PIN_MIC_WS   = 5;   // INMP441 WS
const int PIN_MIC_SD   = 6;   // INMP441 SD; L/R nối GND (kênh trái)
// Module thẻ: VCC nối 3V3 của bo (KHÔNG dùng chân 5Vin: trên mạch S3 thay thế chân này không ra 5 V khi cấp qua USB).
// Thẻ dời từ 10–13 sang 15–18 ngày 12/11 (Protocol 16.17).
const int PIN_SD_CS    = 15;  // module thẻ CS
const int PIN_SD_MOSI  = 16;  // module thẻ MOSI
const int PIN_SD_SCK   = 17;  // module thẻ SCK
const int PIN_SD_MISO  = 18;  // module thẻ MISO
