/*
  TC02_Hieu_chuan — firmware ghi hiệu chuẩn TC-02 (Protocol 2.0, Mục V.2 và VI.1)
  Bo: ESP32-S3 N16R8 ("ESP32S3 Dev Module"), Arduino-ESP32 core 3.x.
  Ghi WAV 16 kHz, 16 bit, một kênh lên thẻ microSD. Không Wi-Fi, không mô hình.

  Nối dây (giống TC-01, Protocol 2.0 Mục V.2):
    INMP441  VDD→3V3  GND→GND  L/R→GND  SCK→GPIO4  WS→GPIO5  SD→GPIO6
    microSD  VCC→3V3  GND→GND  CS→GPIO15  MOSI→GPIO16  SCK→GPIO17  MISO→GPIO18

  Điều khiển bằng nút BOOT (GPIO0):
    - Bấm ngắn khi đang chờ  : mở tệp mới GHI_xxxx.wav và bắt đầu ghi.
    - Bấm ngắn khi đang ghi  : đóng tệp hiện tại, mở ngay tệp kế tiếp (một lần bấm = một vị trí đo).
    - Giữ ≥ 2 giây           : đóng tệp, dừng ghi. Lúc này rút thẻ hoặc rút nguồn an toàn.
  Đèn RGB trên bo (nếu có):
    trắng nhấp nháy chậm = đang chờ · xanh lá nhấp nháy = đang ghi · vàng = vừa có mẫu bị cắt đỉnh
    xanh dương chớp = vừa mở tệp mới · đỏ sáng liên tục = lỗi thẻ.
  Nhật ký: /GHI_NHAT_KY.csv (một dòng mỗi tệp).

  Quy đổi mẫu micro giống hệt firmware vận hành TC-01 (tham_so.h, Protocol 16.8):
  mẫu 16 bit = (raw × HE_SO_KHUECH_DAI) >> 16, chặn trong giới hạn 16 bit, với HE_SO_KHUECH_DAI = 4 (0 dBFS ≈ 108 dB SPL).
  Nhờ vậy mô hình nhận cùng một đầu vào khi chạy trên thiết bị và khi huấn luyện từ tệp WAV.
*/
#include <Arduino.h>
#include <SPI.h>
#include <SD.h>
#include "driver/i2s_std.h"

#define MIC_SCK 4
#define MIC_WS 5
#define MIC_SD 6
#define SD_CS 15
#define SD_MOSI 16
#define SD_SCK 17
#define SD_MISO 18
#define NUT 0

static const uint32_t TAN_SO_MAU = 16000;
static const int32_t HE_SO_KHUECH_DAI = 4;
static const char *PHIEN_BAN = "hieu-chuan-1.2";

static i2s_chan_handle_t rx = NULL;
static volatile uint32_t tranBoDem = 0;

static int32_t vao[512];
static int16_t ra[2048];
static size_t nRa = 0;

static File tep;
static bool dangGhi = false;
static bool loiThe = false;
static uint32_t soTep = 0, msBatDau = 0, soMau = 0, catDinh = 0, tranLucMo = 0;
static double tongBinhPhuong = 0;
static uint32_t msCapNhatDau = 0, msCatDinhCuoi = 0, msMoTep = 0;

static void den(uint8_t r, uint8_t g, uint8_t b) {
#ifdef RGB_BUILTIN
  rgbLedWrite(RGB_BUILTIN, r, g, b);
#endif
}

static bool IRAM_ATTR khiTran(i2s_chan_handle_t h, i2s_event_data_t *e, void *u) {
  tranBoDem++;
  return false;
}

static void ghiDauWav(File &f, uint32_t soByteDuLieu) {
  uint8_t h[44];
  uint32_t byteRate = TAN_SO_MAU * 2;
  memcpy(h, "RIFF", 4);
  uint32_t v = 36 + soByteDuLieu; memcpy(h + 4, &v, 4);
  memcpy(h + 8, "WAVEfmt ", 8);
  v = 16; memcpy(h + 16, &v, 4);
  uint16_t s = 1; memcpy(h + 20, &s, 2);          // PCM
  s = 1; memcpy(h + 22, &s, 2);                   // một kênh
  v = TAN_SO_MAU; memcpy(h + 24, &v, 4);
  memcpy(h + 28, &byteRate, 4);
  s = 2; memcpy(h + 32, &s, 2);
  s = 16; memcpy(h + 34, &s, 2);
  memcpy(h + 36, "data", 4);
  memcpy(h + 40, &soByteDuLieu, 4);
  f.seek(0);
  f.write(h, 44);
}

static void capNhatDau() {
  uint32_t cuoi = 44 + soMau * 2;
  ghiDauWav(tep, soMau * 2);
  tep.seek(cuoi);
  tep.flush();
}

static void ghiNhatKy() {
  File nk = SD.open("/GHI_NHAT_KY.csv", FILE_APPEND);
  if (!nk) return;
  if (nk.size() == 0) nk.println("tep,phien_ban,ms_bat_dau,ms_ket_thuc,thoi_luong_s,so_mau,cat_dinh,tran_bo_dem,rms_dbfs,he_so_khuech_dai");
  double rms = soMau ? sqrt(tongBinhPhuong / soMau) / 32768.0 : 0;
  char d[200];
  snprintf(d, sizeof(d), "GHI_%04lu.wav,%s,%lu,%lu,%.2f,%lu,%lu,%lu,%.1f,%d",
           (unsigned long)soTep, PHIEN_BAN, (unsigned long)msBatDau, (unsigned long)millis(),
           soMau / (double)TAN_SO_MAU, (unsigned long)soMau, (unsigned long)catDinh,
           (unsigned long)(tranBoDem - tranLucMo), rms > 0 ? 20 * log10(rms) : -120.0, (int)HE_SO_KHUECH_DAI);
  nk.println(d);
  nk.close();
}

static void dongTep() {
  if (!dangGhi) return;
  if (nRa) { tep.write((uint8_t *)ra, nRa * 2); soMau += nRa; nRa = 0; }
  capNhatDau();
  tep.close();
  ghiNhatKy();
  Serial.printf("Đóng GHI_%04lu.wav: %.1f s, cắt đỉnh %lu, tràn %lu\n", (unsigned long)soTep,
                soMau / (double)TAN_SO_MAU, (unsigned long)catDinh, (unsigned long)(tranBoDem - tranLucMo));
  dangGhi = false;
}

static bool moTep() {
  char ten[24];
  do {
    soTep++;
    snprintf(ten, sizeof(ten), "/GHI_%04lu.wav", (unsigned long)soTep);
  } while (SD.exists(ten) && soTep < 9999);
  tep = SD.open(ten, FILE_WRITE);
  if (!tep) { loiThe = true; return false; }
  ghiDauWav(tep, 0);
  soMau = 0; catDinh = 0; tongBinhPhuong = 0; nRa = 0;
  msBatDau = millis(); msCapNhatDau = msBatDau; msMoTep = msBatDau; tranLucMo = tranBoDem;
  dangGhi = true;
  Serial.printf("Mở %s\n", ten);
  return true;
}

static void khoiI2S() {
  i2s_chan_config_t cc = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
  cc.dma_desc_num = 16;
  cc.dma_frame_num = 512;                       // 16 × 512 mẫu ≈ 0,5 s đệm khi thẻ ghi chậm
  i2s_new_channel(&cc, NULL, &rx);
  i2s_std_config_t sc = {
    .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(TAN_SO_MAU),
    .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_MONO),
    .gpio_cfg = {
      .mclk = I2S_GPIO_UNUSED,
      .bclk = (gpio_num_t)MIC_SCK,
      .ws = (gpio_num_t)MIC_WS,
      .dout = I2S_GPIO_UNUSED,
      .din = (gpio_num_t)MIC_SD,
      .invert_flags = { .mclk_inv = false, .bclk_inv = false, .ws_inv = false },
    },
  };
  sc.slot_cfg.slot_mask = I2S_STD_SLOT_LEFT;    // L/R nối GND → kênh trái
  i2s_channel_init_std_mode(rx, &sc);
  i2s_event_callbacks_t cb = {};
  cb.on_recv_q_ovf = khiTran;
  i2s_channel_register_event_callback(rx, &cb, NULL);
  i2s_channel_enable(rx);
}

void setup() {
  Serial.begin(115200);
  uint32_t tCho = millis();
  while (!Serial && millis() - tCho < 3000) delay(10);   // chờ cổng USB nối lại, tối đa 3 s
  pinMode(NUT, INPUT_PULLUP);
  den(20, 20, 20);
  delay(300);
  SPI.begin(SD_SCK, SD_MISO, SD_MOSI, SD_CS);
  if (!SD.begin(SD_CS, SPI, 4000000)) {
    loiThe = true;
    Serial.println("LỖI: không mở được thẻ. Kiểm tra VCC module thẻ nối 3V3 (không dùng 5Vin) và thẻ FAT32.");
  } else {
    Serial.printf("Thẻ %llu MB. Sẵn sàng. Bấm BOOT để bắt đầu ghi.\n", SD.cardSize() / (1024 * 1024));
  }
  khoiI2S();
  // bỏ 0,5 s đầu: INMP441 cần thời gian khởi động
  uint32_t t0 = millis();
  size_t n;
  while (millis() - t0 < 500) i2s_channel_read(rx, vao, sizeof(vao), &n, portMAX_DELAY);
}

void loop() {
  size_t n = 0;
  i2s_channel_read(rx, vao, sizeof(vao), &n, portMAX_DELAY);
  uint32_t now = millis();

  if (dangGhi) {
    size_t m = n / 4;
    for (size_t i = 0; i < m; i++) {
      int32_t v = (int32_t)(((int64_t)vao[i] * HE_SO_KHUECH_DAI) >> 16);
      if (v > 32767) { v = 32767; catDinh++; msCatDinhCuoi = now; }
      else if (v < -32768) { v = -32768; catDinh++; msCatDinhCuoi = now; }
      ra[nRa++] = (int16_t)v;
      tongBinhPhuong += (double)v * v;
      if (nRa == 2048) {
        if (tep.write((uint8_t *)ra, sizeof(ra)) != sizeof(ra)) loiThe = true;
        soMau += nRa; nRa = 0;
      }
    }
    if (now - msCapNhatDau > 5000) { capNhatDau(); msCapNhatDau = now; }   // rút nguồn đột ngột vẫn đọc được tệp
  }

  // nút BOOT: bấm ngắn / giữ 2 s
  static bool truoc = HIGH;
  static uint32_t msNhan = 0;
  static bool daXuLyGiu = false;
  bool nut = digitalRead(NUT);
  if (truoc == HIGH && nut == LOW) { msNhan = now; daXuLyGiu = false; }
  if (nut == LOW && !daXuLyGiu && now - msNhan > 2000) {
    daXuLyGiu = true;
    dongTep();
    Serial.println("Đã dừng. Có thể rút thẻ hoặc rút nguồn.");
  }
  if (truoc == LOW && nut == HIGH && !daXuLyGiu && now - msNhan > 40) {
    if (!loiThe) { dongTep(); moTep(); }
  }
  truoc = nut;

  // khi chưa ghi: in trạng thái mỗi 5 s (Serial Monitor mở muộn vẫn thấy)
  static uint32_t msTrangThai = 0;
  if (!dangGhi && now - msTrangThai > 5000) {
    msTrangThai = now;
    if (loiThe) Serial.println("LỖI thẻ: kiểm tra dây CS15 MOSI16 SCK17 MISO18, VCC 3V3, thẻ FAT32.");
    else Serial.printf("Chờ. Thẻ %llu MB, đã ghi %lu tệp. Bấm BOOT để ghi.\n", SD.cardSize() / (1024 * 1024), (unsigned long)soTep);
  }

  // đèn
  if (loiThe) den(60, 0, 0);
  else if (dangGhi && now - msMoTep < 600) den(0, 0, 80);
  else if (dangGhi && now - msCatDinhCuoi < 1000 && msCatDinhCuoi) den(60, 45, 0);
  else if (dangGhi) den(0, (now / 500) % 2 ? 40 : 0, 0);
  else den((now / 1000) % 2 ? 15 : 0, (now / 1000) % 2 ? 15 : 0, (now / 1000) % 2 ? 15 : 0);
}
