// T5 – Kiểm tra tổng hợp TussiCount, KHÔNG cần LED và điện trở. Arduino-ESP32 3.x (ESP-IDF 5).
// Gộp T1–T4 vào một chương trình, chỉ báo kết quả qua Serial Monitor (115200 baud).
//
// Khi khởi động, tự chạy: (1) bo mạch và bộ nhớ, (2) micro 3 giây, (3) thẻ nhớ.
// Sau đó gõ một chữ rồi Enter:
//   b = kiểm tra lại bo mạch      m = đo mức micro liên tục (gõ phím bất kỳ để dừng)
//   s = kiểm tra lại thẻ nhớ      g = ghi tệp WAV 10 giây (chỉ thử trên bàn, nghe xong thì xoá)
//   ? = in lại menu
//
// Nối dây (bỏ LED). Chương trình tự chọn chân theo loại mạch đang chọn trong Tools > Board:
//   ESP32-S3 (ESP32S3 Dev Module, mạch chính N16R8):
//     INMP441: VDD-3V3, GND-GND, SCK-GPIO4, WS-GPIO5, SD-GPIO6, L/R-GND
//     Module thẻ: VCC-3V3 (KHÔNG dùng chân 5Vin), GND-GND, CS-GPIO15, MOSI-GPIO16, SCK-GPIO17, MISO-GPIO18
//   ESP32 thường (ESP32 Dev Module, mạch dự phòng ESP-WROOM-32, chân in G25, G26...):
//     INMP441: VDD-3V3, GND-GND, SCK-G26, WS-G25, SD-G33, L/R-GND
//     Module thẻ: VCC-5V (chân V5), GND-GND, CS-G5, MOSI-G23, SCK-G18, MISO-G19
#include <Arduino.h>
#include <math.h>
#include <SPI.h>
#include <SD.h>
#include "esp_mac.h"
#include "driver/i2s_std.h"

#if CONFIG_IDF_TARGET_ESP32S3
const int PIN_MIC_SCK = 4;
const int PIN_MIC_WS = 5;
const int PIN_MIC_SD = 6;
// Thẻ nhớ dời từ 10–13 sang 15–18 ngày 12/11: trên mạch S3 thứ hai, thẻ không nhận ở 10–13 dù micro và bo mạch đạt.
const int PIN_SD_CS = 15;
const int PIN_SD_MOSI = 16;
const int PIN_SD_SCK = 17;
const int PIN_SD_MISO = 18;
#define SPI_THE FSPI
#define VCC_THE "3V3 (khong dung 5Vin)"
#else  // ESP32 thường (ESP-WROOM-32)
const int PIN_MIC_SCK = 26;
const int PIN_MIC_WS = 25;
const int PIN_MIC_SD = 33;
const int PIN_SD_CS = 5;
const int PIN_SD_MOSI = 23;
const int PIN_SD_SCK = 18;
const int PIN_SD_MISO = 19;
#define SPI_THE VSPI
#define VCC_THE "V5"
#endif

// Nếu micro luôn báo "TOAN SO 0" dù đã nối đúng: đổi LEFT thành RIGHT rồi nạp lại.
#define MIC_SLOT I2S_STD_SLOT_LEFT
const uint32_t TAN_SO_MAU = 16000;
const int N_DO = 1600;                    // 0,1 giây mỗi lần đo mức
const int N_GHI = 512;
const uint32_t SO_GIAY_GHI = 10;
const int HE_SO_KHUECH_DAI = 8;           // x8 = +18 dB khi ghi WAV để nghe lại cho rõ

static int32_t bufDo[N_DO];
static int32_t raw[N_GHI];
static int16_t pcm[N_GHI];
static uint8_t khoi[4096];
static i2s_chan_handle_t rx = NULL;
SPIClass spiThe(SPI_THE);
static bool theSanSang = false;

bool kiemTraBo();
bool khoiDongMic();
float doMucMot(float *dinhRa, bool *toanSo0);
bool kiemTraMic(uint32_t soGiay, bool lienTuc);
bool kiemTraThe();
void viet32(File &f, uint32_t v);
void viet16(File &f, uint16_t v);
void dauWav(File &f, uint32_t soByte);
void ghiWav();
void inMenu();

// ---------- 1. Bo mạch ----------
bool kiemTraBo() {
  Serial.println("\n=== 1. BO MACH VA BO NHO ===");
  Serial.printf("Chip: %s, rev %d, %d nhan, %lu MHz\n", ESP.getChipModel(), ESP.getChipRevision(),
                ESP.getChipCores(), (unsigned long)ESP.getCpuFreqMHz());
  Serial.printf("Flash: %lu MB\n", (unsigned long)(ESP.getFlashChipSize() / (1024 * 1024)));
  Serial.printf("PSRAM: %lu KB (%s)\n", (unsigned long)(ESP.getPsramSize() / 1024),
                psramFound() ? "co" : "khong co");
  uint8_t mac[6];
  esp_read_mac(mac, ESP_MAC_WIFI_STA);
  Serial.printf("MAC: %02X:%02X:%02X:%02X:%02X:%02X\n", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
#if CONFIG_IDF_TARGET_ESP32S3
  bool ok = ESP.getFlashChipSize() >= 16UL * 1024 * 1024 && ESP.getPsramSize() >= 7UL * 1024 * 1024;
  Serial.println(ok ? "-> BO MACH: DAT (dung ban N16R8)" : "-> BO MACH: CHUA DAT - xem lai Tools: Flash 16MB, PSRAM OPI");
#else
  bool ok = ESP.getFlashChipSize() >= 4UL * 1024 * 1024;
  Serial.println(ok ? "-> BO MACH: DAT (ESP32 thuong, mach du phong)" : "-> BO MACH: CHUA DAT - flash duoi 4 MB");
#endif
  return ok;
}

// ---------- 2. Micro ----------
bool khoiDongMic() {
  if (rx) return true;
  i2s_chan_config_t cc = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
  if (i2s_new_channel(&cc, NULL, &rx) != ESP_OK) { rx = NULL; return false; }
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
  if (i2s_channel_init_std_mode(rx, &cfg) != ESP_OK || i2s_channel_enable(rx) != ESP_OK) {
    i2s_del_channel(rx);
    rx = NULL;
    return false;
  }
  return true;
}

// Đọc 0,1 giây; trả về mức RMS (dBFS), hoặc 1 nếu lỗi đọc.
float doMucMot(float *dinhRa, bool *toanSo0) {
  size_t got = 0;
  if (i2s_channel_read(rx, bufDo, sizeof(bufDo), &got, 1000) != ESP_OK || got == 0) return 1.0f;
  int n = got / sizeof(int32_t);
  double tb = 0;
  int soKhong = 0;
  for (int i = 0; i < n; i++) {
    tb += (bufDo[i] >> 8);
    if (bufDo[i] == 0) soKhong++;
  }
  tb /= n;
  double tong = 0, dinh = 0;
  for (int i = 0; i < n; i++) {
    double v = (bufDo[i] >> 8) - tb;
    tong += v * v;
    if (fabs(v) > dinh) dinh = fabs(v);
  }
  *toanSo0 = (soKhong == n);
  double rms = sqrt(tong / n);
  *dinhRa = dinh > 0 ? 20.0f * log10f(dinh / 8388608.0f) : -120.0f;
  return rms > 0 ? 20.0f * log10f(rms / 8388608.0f) : -120.0f;
}

bool kiemTraMic(uint32_t soGiay, bool lienTuc) {
  Serial.println("\n=== 2. MICRO INMP441 ===");
  if (!khoiDongMic()) {
    Serial.printf("-> MICRO: LOI khoi tao I2S - kiem tra chan SCK-%d, WS-%d, SD-%d\n", PIN_MIC_SCK, PIN_MIC_WS, PIN_MIC_SD);
    return false;
  }
  Serial.println("Phong yen: khoang -85..-70 dBFS. Noi o 30 cm: -60..-40. Vo tay gan micro: tren -35.");
  if (lienTuc) {
    delay(150);                           // bỏ ký tự Enter còn sót của lệnh "m"
    while (Serial.available()) Serial.read();
    Serial.println("Dang do lien tuc. Go phim bat ky roi Enter de dung.");
  }
  else Serial.printf("Do %lu giay. Hay noi hoac vo tay gan micro de thay muc tang len.\n", (unsigned long)soGiay);
  // bỏ 0,3 s đầu cho micro ổn định
  float d; bool z;
  for (int i = 0; i < 3; i++) doMucMot(&d, &z);
  float thapNhat = 0, caoNhat = -200;
  int lanDoc = 0, lanLoi = 0, lanSo0 = 0;
  uint32_t t0 = millis();
  while (lienTuc ? !Serial.available() : (millis() - t0 < soGiay * 1000UL)) {
    float dinh; bool so0;
    float m = doMucMot(&dinh, &so0);
    if (m > 0) { lanLoi++; Serial.println("LOI: khong doc duoc I2S"); delay(200); continue; }
    lanDoc++;
    if (so0) { lanSo0++; Serial.println("muc:-120 | TOAN SO 0 - kiem tra day SD, L/R noi GND, hoac doi MIC_SLOT"); continue; }
    if (m < thapNhat) thapNhat = m;
    if (m > caoNhat) caoNhat = m;
    int vach = constrain((int)((m + 100.0f) / 2.0f), 0, 50);
    char thanh[52];
    for (int i = 0; i < 50; i++) thanh[i] = i < vach ? '#' : ' ';
    thanh[50] = 0;
    Serial.printf("muc:%.1f dinh:%.1f   |%s| ~%.0f dB SPL\n", m, dinh, thanh, m + 120.0f);
  }
  while (Serial.available()) Serial.read();
  bool ok = lanDoc > 0 && lanLoi == 0 && lanSo0 == 0 && caoNhat > -100.0f;
  if (lanDoc > 0 && lanSo0 < lanDoc)
    Serial.printf("Muc thap nhat %.1f dBFS, cao nhat %.1f dBFS (chenh %.1f dB)\n", thapNhat, caoNhat, caoNhat - thapNhat);
  if (ok && caoNhat - thapNhat < 6.0f)
    Serial.println("Luu y: muc gan nhu khong doi. Thu vo tay gan micro (go m de do lai).");
  Serial.println(ok ? "-> MICRO: DAT (doc duoc tin hieu)" : "-> MICRO: CHUA DAT");
  return ok;
}

// ---------- 3. Thẻ nhớ ----------
bool kiemTraThe() {
  Serial.println("\n=== 3. THE NHO microSD ===");
  if (!theSanSang) {
    // Chẩn đoán dây MISO: thả nổi với điện trở kéo lên rồi kéo xuống. Nếu đọc theo đúng điện trở kéo
    // thì không có gì lái chân này (module chưa có điện hoặc dây MISO lỏng / cắm sai chân).
    pinMode(PIN_SD_MISO, INPUT_PULLUP); delay(5); int keoLen = digitalRead(PIN_SD_MISO);
    pinMode(PIN_SD_MISO, INPUT_PULLDOWN); delay(5); int keoXuong = digitalRead(PIN_SD_MISO);
    Serial.printf("Chan MISO-%d: keo len doc %d, keo xuong doc %d -> %s\n", PIN_SD_MISO, keoLen, keoXuong,
                  (keoLen == 1 && keoXuong == 0) ? "tha noi (module chua co dien hoac day MISO chua noi)" : "co tin hieu tu module");
    pinMode(PIN_SD_MISO, INPUT);
    spiThe.begin(PIN_SD_SCK, PIN_SD_MISO, PIN_SD_MOSI, PIN_SD_CS);
    const uint32_t tanSo[] = {10000000, 4000000, 1000000};
    bool duoc = false;
    for (int i = 0; i < 3 && !duoc; i++) {
      duoc = SD.begin(PIN_SD_CS, spiThe, tanSo[i]);
      Serial.printf("Thu SPI %lu MHz: %s\n", (unsigned long)(tanSo[i] / 1000000), duoc ? "nhan the" : "khong nhan");
      if (!duoc) SD.end();
    }
    if (!duoc) {
      Serial.printf("-> THE NHO: LOI khong nhan the. Kiem tra: the da cam; VCC module noi " VCC_THE "; CS-%d, MOSI-%d, SCK-%d, MISO-%d; the FAT32.\n",
                    PIN_SD_CS, PIN_SD_MOSI, PIN_SD_SCK, PIN_SD_MISO);
      return false;
    }
    theSanSang = true;
  }
  const char *loai[] = {"khong co the", "MMC", "SDSC", "SDHC/SDXC", "khong ro"};
  uint8_t t = SD.cardType();
  Serial.printf("Loai the: %s, dung luong %llu MB, da dung %llu MB\n", loai[t <= 4 ? t : 4],
                SD.cardSize() / (1024 * 1024), SD.usedBytes() / (1024 * 1024));
  File f = SD.open("/t5_kiemtra.txt", FILE_WRITE);
  if (!f) { Serial.println("-> THE NHO: LOI khong tao duoc tep"); return false; }
  f.println("TussiCount T5");
  f.close();
  f = SD.open("/t5_kiemtra.txt");
  String s = f.readStringUntil('\n');
  f.close();
  s.trim();
  Serial.printf("Doc lai: \"%s\" -> %s\n", s.c_str(), s == "TussiCount T5" ? "dung" : "SAI");
  if (s != "TussiCount T5") { Serial.println("-> THE NHO: CHUA DAT"); return false; }
  for (size_t i = 0; i < sizeof(khoi); i++) khoi[i] = i & 0xFF;
  const int SO_KHOI = 256;                // 1 MB
  f = SD.open("/t5_tocdo.bin", FILE_WRITE);
  uint32_t t0 = millis();
  for (int i = 0; i < SO_KHOI; i++) {
    if (f.write(khoi, sizeof(khoi)) != sizeof(khoi)) { Serial.println("-> THE NHO: LOI ghi bi ngat"); f.close(); return false; }
  }
  f.close();
  uint32_t dt = millis() - t0;
  float kbs = SO_KHOI * 4.0f * 1000.0f / (dt ? dt : 1);
  Serial.printf("Ghi 1 MB mat %lu ms -> %.0f KB/s (%s)\n", (unsigned long)dt, kbs, kbs > 300 ? "dat" : "CHAM");
  SD.remove("/t5_tocdo.bin");
  SD.remove("/t5_kiemtra.txt");
  bool ok = kbs > 300;
  Serial.println(ok ? "-> THE NHO: DAT" : "-> THE NHO: CHUA DAT (ghi cham, thu the khac hoac format FAT32)");
  return ok;
}

// ---------- 4. Ghi WAV ----------
void viet32(File &f, uint32_t v) { f.write((uint8_t *)&v, 4); }
void viet16(File &f, uint16_t v) { f.write((uint8_t *)&v, 2); }

void dauWav(File &f, uint32_t soByte) {
  f.write((const uint8_t *)"RIFF", 4); viet32(f, 36 + soByte);
  f.write((const uint8_t *)"WAVEfmt ", 8); viet32(f, 16); viet16(f, 1); viet16(f, 1);
  viet32(f, TAN_SO_MAU); viet32(f, TAN_SO_MAU * 2); viet16(f, 2); viet16(f, 16);
  f.write((const uint8_t *)"data", 4); viet32(f, soByte);
}

void ghiWav() {
  Serial.println("\n=== 4. GHI WAV 10 GIAY ===");
  if (!theSanSang && !kiemTraThe()) { Serial.println("-> Chua ghi duoc: the nho chua dat."); return; }
  if (!khoiDongMic()) { Serial.println("-> Chua ghi duoc: micro loi."); return; }
  char ten[24];
  int k = 0;
  do { snprintf(ten, sizeof(ten), "/T5_%03d.wav", k++); } while (SD.exists(ten) && k < 1000);
  File f = SD.open(ten, FILE_WRITE);
  if (!f) { Serial.println("LOI: khong tao duoc tep"); return; }
  dauWav(f, 0);
  const uint32_t tong = TAN_SO_MAU * SO_GIAY_GHI;
  uint32_t daGhi = 0, tran = 0;
  size_t got;
  for (int i = 0; i < 8; i++) i2s_channel_read(rx, raw, sizeof(raw), &got, 1000);   // bỏ 0,25 s đầu
  Serial.printf("Dang ghi %s ... (10 giay)\n", ten);
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
  Serial.printf("Xong: %s, %lu mau trong %lu ms (can %lu ms), %lu mau bi cat dinh.\n", ten,
                (unsigned long)daGhi, (unsigned long)dt, (unsigned long)(SO_GIAY_GHI * 1000), (unsigned long)tran);
  Serial.println(dt < SO_GIAY_GHI * 1000 + 300 ? "-> Toc do: DAT (khong mat mau)" : "-> Toc do: CHAM - co the mat mau");
  Serial.println("Rut nguon, lay the ra, mo tep tren may tinh de nghe. Nghe xong thi xoa tep.");
}

void inMenu() {
  Serial.println("\nGo mot chu roi Enter:  b = bo mach | m = micro lien tuc | s = the nho | g = ghi WAV 10 giay | ? = menu");
}

void setup() {
  Serial.begin(115200);
  delay(2000);
  Serial.println("\n\n##### TussiCount – KIEM TRA TONG HOP (khong LED) #####");
  bool b = kiemTraBo();
  bool m = kiemTraMic(3, false);
  bool s = kiemTraThe();
  Serial.println("\n===== TOM TAT =====");
  Serial.printf("Bo mach: %s | Micro: %s | The nho: %s\n", b ? "DAT" : "CHUA DAT", m ? "DAT" : "CHUA DAT", s ? "DAT" : "CHUA DAT");
  if (b && m && s) Serial.println("Ca 3 phan deu dat. Go g de ghi thu 10 giay va nghe lai tren may tinh.");
  inMenu();
}

void loop() {
  if (!Serial.available()) { delay(20); return; }
  char c = Serial.read();
  if (c == '\n' || c == '\r' || c == ' ') return;
  while (Serial.available()) Serial.read();
  switch (c) {
    case 'b': case 'B': kiemTraBo(); break;
    case 'm': case 'M': kiemTraMic(0, true); break;
    case 's': case 'S': kiemTraThe(); break;
    case 'g': case 'G': ghiWav(); break;
    default: break;
  }
  inMenu();
}
