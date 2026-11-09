// TussiCount – bảng chân nối dùng chung cho các bài kiểm tra (ESP32-S3 N16R8)
// Đổi ở đây nếu nối khác; mọi bài T1–T4 dùng cùng giá trị.
#pragma once
const int PIN_LED      = 7;   // GPIO7 → điện trở 330 Ω → chân dài LED; chân ngắn LED → GND
const int PIN_MIC_SCK  = 4;   // INMP441 SCK
const int PIN_MIC_WS   = 5;   // INMP441 WS
const int PIN_MIC_SD   = 6;   // INMP441 SD; L/R nối GND (kênh trái)
const int PIN_SD_CS    = 10;  // module thẻ CS
const int PIN_SD_MOSI  = 11;  // module thẻ MOSI
const int PIN_SD_SCK   = 12;  // module thẻ SCK
const int PIN_SD_MISO  = 13;  // module thẻ MISO
