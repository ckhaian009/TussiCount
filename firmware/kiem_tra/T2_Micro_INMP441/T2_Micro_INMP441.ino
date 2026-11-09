// T2 – Kiểm tra micro INMP441 qua I2S. Arduino-ESP32 3.x (ESP-IDF 5).
// Mỗi 0,1 giây in mức âm (dBFS) và ước lượng dB SPL = dBFS + 120 (theo datasheet: -26 dBFS ở 94 dB SPL).
// Ước lượng chưa hiệu chuẩn, chỉ để kiểm tra micro chạy; hiệu chuẩn thật làm bằng máy đo UT353.
// LED sáng khi mức vượt NGUONG_LED_DBFS. Mở Serial Plotter để xem dạng đường.
#include <Arduino.h>
#include <math.h>
#include "driver/i2s_std.h"
#include "chan_noi.h"

// Nếu mức luôn là -120 dBFS (toàn số 0) dù đã nối đúng: đổi LEFT thành RIGHT rồi nạp lại.
#define MIC_SLOT I2S_STD_SLOT_LEFT
const uint32_t TAN_SO_MAU = 16000;
const int N = 1600;                        // 0,1 giây
const float NGUONG_LED_DBFS = -45.0f;

static int32_t buf[N];
static i2s_chan_handle_t rx;

void setup() {
  Serial.begin(115200);
  delay(1500);
  pinMode(PIN_LED, OUTPUT);
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
  Serial.println();
  Serial.println("=== T2: micro INMP441 ===");
  Serial.println("Phong yen: khoang -85..-70 dBFS. Noi o 30 cm: khoang -60..-40. Vo tay gan micro: tren -35.");
}

void loop() {
  size_t got = 0;
  if (i2s_channel_read(rx, buf, sizeof(buf), &got, 1000) != ESP_OK || got == 0) {
    Serial.println("LOI: khong doc duoc I2S - kiem tra day SCK, WS, SD va nguon 3V3");
    delay(500);
    return;
  }
  int n = got / sizeof(int32_t);
  double tb = 0;
  int so_khong = 0;
  for (int i = 0; i < n; i++) {
    int32_t v = buf[i] >> 8;              // 24 bit có dấu
    tb += v;
    if (buf[i] == 0) so_khong++;
  }
  tb /= n;
  double tong = 0, dinh = 0;
  for (int i = 0; i < n; i++) {
    double v = (buf[i] >> 8) - tb;
    tong += v * v;
    if (fabs(v) > dinh) dinh = fabs(v);
  }
  double rms = sqrt(tong / n);
  float dbfs = rms > 0 ? 20.0f * log10f(rms / 8388608.0f) : -120.0f;
  float dbfs_dinh = dinh > 0 ? 20.0f * log10f(dinh / 8388608.0f) : -120.0f;
  digitalWrite(PIN_LED, dbfs > NGUONG_LED_DBFS ? HIGH : LOW);
  if (so_khong == n) {
    Serial.println("muc:-120 | TOAN SO 0 - kiem tra day SD, L/R noi GND, hoac doi MIC_SLOT");
    return;
  }
  int vach = constrain((int)((dbfs + 100.0f) / 2.0f), 0, 50);
  char thanh[52];
  for (int i = 0; i < 50; i++) thanh[i] = i < vach ? '#' : ' ';
  thanh[50] = 0;
  Serial.printf("muc:%.1f dinh:%.1f   |%s| ~%.0f dB SPL\n", dbfs, dbfs_dinh, thanh, dbfs + 120.0f);
}
