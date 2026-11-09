// T4 – Kiểm tra cả chuỗi micro → ESP32 → thẻ nhớ: ghi một tệp WAV 10 giây.
// Arduino-ESP32 3.x. Chỉ dùng khi thử trên bàn; nghe xong thì xoá tệp.
// Cách dùng: mở Serial Monitor, gõ chữ g rồi Enter để ghi. LED sáng trong lúc ghi.
// Đạt khi: tệp T4_xxx.wav mở được trên máy tính, nghe rõ tiếng nói, không rè, không ngắt quãng.
#include <Arduino.h>
#include <SPI.h>
#include <SD.h>
#include "driver/i2s_std.h"
#include "chan_noi.h"

#define MIC_SLOT I2S_STD_SLOT_LEFT        // đổi RIGHT nếu T2 phải đổi
const uint32_t TAN_SO_MAU = 16000;
const uint32_t SO_GIAY = 10;
const int HE_SO_KHUECH_DAI = 8;          // x8 = +18 dB, để tiếng nói đủ to khi nghe lại
const int N = 512;

static int32_t raw[N];
static int16_t pcm[N];
static i2s_chan_handle_t rx;
SPIClass spiThe(FSPI);

void viet32(File &f, uint32_t v);
void viet16(File &f, uint16_t v);
void dauWav(File &f, uint32_t soByte);
void baoLoi(const char *s);
void ghi();
void setup();
void loop();

void viet32(File &f, uint32_t v) { f.write((uint8_t *)&v, 4); }
void viet16(File &f, uint16_t v) { f.write((uint8_t *)&v, 2); }

void dauWav(File &f, uint32_t soByte) {
  f.write((const uint8_t *)"RIFF", 4); viet32(f, 36 + soByte);
  f.write((const uint8_t *)"WAVEfmt ", 8); viet32(f, 16); viet16(f, 1); viet16(f, 1);
  viet32(f, TAN_SO_MAU); viet32(f, TAN_SO_MAU * 2); viet16(f, 2); viet16(f, 16);
  f.write((const uint8_t *)"data", 4); viet32(f, soByte);
}

void baoLoi(const char *s) {
  Serial.println(s);
  while (true) { digitalWrite(PIN_LED, !digitalRead(PIN_LED)); delay(100); }
}

void setup() {
  Serial.begin(115200);
  delay(1500);
  pinMode(PIN_LED, OUTPUT);
  Serial.println();
  Serial.println("=== T4: ghi WAV 10 giay ===");
  spiThe.begin(PIN_SD_SCK, PIN_SD_MISO, PIN_SD_MOSI, PIN_SD_CS);
  if (!SD.begin(PIN_SD_CS, spiThe, 20000000)) baoLoi("LOI: khong nhan the - chay lai T3");
  i2s_chan_config_t cc = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
  ESP_ERROR_CHECK(i2s_new_channel(&cc, NULL, &rx));
  i2s_std_config_t cfg = {
    .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(TAN_SO_MAU),
    .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_MONO),
    .gpio_cfg = {
      .mclk = I2S_GPIO_UNUSED,
      .bclk = (gpio_num_t)PIN_MIC_SCK,
      .ws = (gpio_num_t)PIN_MIC_WS,
      .dout = I2S_GPIO_UNUSED,
      .din = (gpio_num_t)PIN_MIC_SD,
      .invert_flags = { .mclk_inv = false, .bclk_inv = false, .ws_inv = false },
    },
  };
  cfg.slot_cfg.slot_mask = MIC_SLOT;
  ESP_ERROR_CHECK(i2s_channel_init_std_mode(rx, &cfg));
  ESP_ERROR_CHECK(i2s_channel_enable(rx));
  Serial.println("San sang. Go g roi Enter de ghi 10 giay.");
}

void ghi() {
  char ten[24];
  int k = 0;
  do { snprintf(ten, sizeof(ten), "/T4_%03d.wav", k++); } while (SD.exists(ten) && k < 1000);
  File f = SD.open(ten, FILE_WRITE);
  if (!f) { Serial.println("LOI: khong tao duoc tep"); return; }
  dauWav(f, 0);
  const uint32_t tong = TAN_SO_MAU * SO_GIAY;
  uint32_t daGhi = 0, tran = 0;
  size_t got;
  for (int i = 0; i < 8; i++) i2s_channel_read(rx, raw, sizeof(raw), &got, 1000);   // bỏ 0,25 s đầu
  digitalWrite(PIN_LED, HIGH);
  Serial.printf("Dang ghi %s ...\n", ten);
  uint32_t t0 = millis();
  while (daGhi < tong) {
    if (i2s_channel_read(rx, raw, sizeof(raw), &got, 1000) != ESP_OK) { Serial.println("LOI: doc I2S"); break; }
    int n = got / 4;
    if (n > (int)(tong - daGhi)) n = tong - daGhi;
    for (int i = 0; i < n; i++) {
      int32_t v = (int32_t)(((int64_t)raw[i] * HE_SO_KHUECH_DAI) >> 16);
      if (v > 32767) { v = 32767; tran++; }
      if (v < -32768) { v = -32768; tran++; }
      pcm[i] = (int16_t)v;
    }
    f.write((uint8_t *)pcm, n * 2);
    daGhi += n;
  }
  uint32_t dt = millis() - t0;
  f.seek(0);
  dauWav(f, daGhi * 2);
  f.close();
  digitalWrite(PIN_LED, LOW);
  Serial.printf("Xong: %s, %lu mau trong %lu ms (can %lu ms), %lu mau bi cat dinh.\n", ten,
                (unsigned long)daGhi, (unsigned long)dt, (unsigned long)(SO_GIAY * 1000), (unsigned long)tran);
  Serial.println(dt < SO_GIAY * 1000 + 300 ? "Toc do: dat (khong mat mau)" : "Toc do: CHAM - co the mat mau, chay lai T3");
  Serial.println("Tat nguon, lay the ra, mo tep tren may tinh de nghe. Nghe xong thi xoa tep.");
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 'g' || c == 'G') ghi();
  }
}
