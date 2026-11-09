// T1 – Kiểm tra bo ESP32-S3 N16R8 và LED báo. Arduino-ESP32 3.x.
// Đạt khi: Serial in Flash 16 MB, PSRAM khoảng 8 MB; LED nháy 1 lần/giây.
#include <Arduino.h>
#include "esp_mac.h"
#include "chan_noi.h"

void setup() {
  Serial.begin(115200);
  delay(1500);
  pinMode(PIN_LED, OUTPUT);
  Serial.println();
  Serial.println("=== T1: bo mach va LED ===");
  Serial.printf("Chip: %s, rev %d, %d nhan, %lu MHz\n", ESP.getChipModel(), ESP.getChipRevision(),
                ESP.getChipCores(), (unsigned long)ESP.getCpuFreqMHz());
  Serial.printf("Flash: %lu MB\n", (unsigned long)(ESP.getFlashChipSize() / (1024 * 1024)));
  Serial.printf("PSRAM: %lu KB (%s)\n", (unsigned long)(ESP.getPsramSize() / 1024),
                psramFound() ? "co" : "KHONG thay - kiem tra Tools > PSRAM = OPI PSRAM");
  uint8_t mac[6];
  esp_read_mac(mac, ESP_MAC_WIFI_STA);
  Serial.printf("MAC: %02X:%02X:%02X:%02X:%02X:%02X\n", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
  bool ok = ESP.getFlashChipSize() >= 16UL * 1024 * 1024 && ESP.getPsramSize() >= 7UL * 1024 * 1024;
  Serial.println(ok ? "KET QUA: DAT (dung ban N16R8)" : "KET QUA: CHUA DAT - xem lai cai dat Tools");
  Serial.println("LED tren GPIO7 se nhay 1 lan/giay.");
}

void loop() {
  digitalWrite(PIN_LED, HIGH);
  delay(500);
  digitalWrite(PIN_LED, LOW);
  delay(500);
}
