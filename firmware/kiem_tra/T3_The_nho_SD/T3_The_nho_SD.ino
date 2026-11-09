// T3 – Kiểm tra module thẻ microSD (SPI) và tốc độ ghi. Arduino-ESP32 3.x.
// Đạt khi: nhận thẻ, ghi rồi đọc lại đúng, tốc độ ghi trên 300 KB/s
// (tệp WAV 16 kHz 16 bit chỉ cần 32 KB/s). Tệp thử bị xoá sau khi kiểm tra.
#include <Arduino.h>
#include <SPI.h>
#include <SD.h>
#include "chan_noi.h"

SPIClass spiThe(FSPI);
static uint8_t khoi[4096];

bool kiemTra();

bool kiemTra() {
  spiThe.begin(PIN_SD_SCK, PIN_SD_MISO, PIN_SD_MOSI, PIN_SD_CS);
  if (!SD.begin(PIN_SD_CS, spiThe, 10000000)) {
    Serial.println("LOI: khong nhan the. Kiem tra: the da cam; VCC module noi 5V; CS-10, MOSI-11, SCK-12, MISO-13; the FAT32.");
    return false;
  }
  const char *loai[] = {"khong co the", "MMC", "SDSC", "SDHC/SDXC", "khong ro"};
  uint8_t t = SD.cardType();
  Serial.printf("Loai the: %s, dung luong %llu MB, da dung %llu MB\n", loai[t <= 4 ? t : 4],
                SD.cardSize() / (1024 * 1024), SD.usedBytes() / (1024 * 1024));

  File f = SD.open("/t3_kiemtra.txt", FILE_WRITE);
  if (!f) { Serial.println("LOI: khong tao duoc tep"); return false; }
  f.println("TussiCount T3");
  f.close();
  f = SD.open("/t3_kiemtra.txt");
  String s = f.readStringUntil('\n');
  f.close();
  s.trim();
  Serial.printf("Doc lai: \"%s\" -> %s\n", s.c_str(), s == "TussiCount T3" ? "dung" : "SAI");
  if (s != "TussiCount T3") return false;

  for (size_t i = 0; i < sizeof(khoi); i++) khoi[i] = i & 0xFF;
  const int SO_KHOI = 256;                 // 1 MB
  f = SD.open("/t3_tocdo.bin", FILE_WRITE);
  uint32_t t0 = millis();
  for (int i = 0; i < SO_KHOI; i++) {
    if (f.write(khoi, sizeof(khoi)) != sizeof(khoi)) { Serial.println("LOI: ghi bi ngat"); f.close(); return false; }
  }
  f.close();
  uint32_t dt = millis() - t0;
  float kbs = SO_KHOI * 4.0f * 1000.0f / (dt ? dt : 1);
  Serial.printf("Ghi 1 MB mat %lu ms -> %.0f KB/s (%s)\n", (unsigned long)dt, kbs, kbs > 300 ? "dat" : "CHAM");
  SD.remove("/t3_tocdo.bin");
  SD.remove("/t3_kiemtra.txt");
  return kbs > 300;
}

void setup() {
  Serial.begin(115200);
  delay(1500);
  pinMode(PIN_LED, OUTPUT);
  Serial.println();
  Serial.println("=== T3: the nho microSD ===");
  bool ok = kiemTra();
  Serial.println(ok ? "KET QUA: DAT" : "KET QUA: CHUA DAT");
  digitalWrite(PIN_LED, ok ? HIGH : LOW);   // đạt: LED sáng liên tục; chưa đạt: LED nháy
}

void loop() {
  if (digitalRead(PIN_LED) == HIGH) return;
  digitalWrite(PIN_LED, HIGH); delay(100); digitalWrite(PIN_LED, LOW); delay(100);
}
