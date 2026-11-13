// TussiCount – firmware VẬN HÀNH cho TC-01 (ESP32-S3 N16R8, INMP441, microSD). Arduino-ESP32 3.x (ESP-IDF 5).
//
// Bản vận hành KHÔNG có hàm ghi tệp âm thanh (Protocol mục 5, 14). Chỉ ghi ra thẻ nhớ:
//   /<thiết bị>_<ngày>_su_kien.csv   mỗi sự kiện ho: thời điểm, độ dài, điểm tin cậy (mục 6)
//   /<thiết bị>_<ngày>_moi_phut.csv  mỗi phút: LAeq, LA90, điện áp, thời gian chạy, nhiệt độ chip, bộ nhớ trống
//                                        nhỏ nhất, suy luận lớn nhất, khung bị mất, NTP (mục 6, 16.5)
//   /<thiết bị>_<ngày>_diem.csv      điểm p_cough của mọi cửa sổ theo CẢ HAI mô hình v1, v2 (để tính lại số
//                                        đếm với mô hình và ngưỡng đã đóng băng: tools/chay_mo_hinh/tach_diem_thiet_bi.py)
//   <ngày> = ngày của (giờ Việt Nam − 6 giờ): mỗi tệp chạy từ 06:00 ngày đó đến 06:00 hôm sau,
//   nên đêm D (18:00 D → 06:00 D+1, mục 6) nằm trọn trong tệp ngày D.
//
// Hai lõi FreeRTOS:
//   lõi 0: tác vụ âm thanh (đọc I2S 16 kHz → bộ đệm vòng 8 giây trong PSRAM; lọc trọng số A, mức mỗi khung 0,5 s)
//          và tác vụ ghi thẻ (mỗi 10 giây) + nhật ký mỗi phút + gói 10 phút gửi Google Sheets (nếu có cấu hình).
//   lõi 1: tác vụ suy luận: cửa sổ 1 s trượt 0,5 s → mô hình v1 và v2 → gộp sự kiện (mô hình MO_HINH_DEM)
//          đúng như gop_su_kien.py.
// Thời điểm lấy theo đồng hồ mẫu (số mẫu ÷ 16.000) neo vào giờ NTP; mỗi lần đồng bộ (30 phút) ghi độ lệch đo được.
//
// Cấu hình mạng trên thẻ nhớ, tệp /cauhinh.txt (mỗi dòng khoa=gia_tri):
//   wifi_ssid=...  wifi_pass=...  (tuỳ chọn, để lấy NTP)   ntp=pool.ntp.org   sheets_url=   ap_ten=...   ap_mat_khau=...
// Giờ: mạch luôn tự phát Wi-Fi ap_ten; điện thoại mở http://192.168.4.1 và bấm "Đồng bộ giờ" (mỗi ngày lúc thay sạc).
//
// Tools: ESP32S3 Dev Module · USB CDC On Boot: Enabled · Flash 16MB · PSRAM: OPI PSRAM ·
//        Partition: 16M Flash (3MB APP/9.9MB FATFS). Serial Monitor 115200.

#include <Arduino.h>
#include <SPI.h>
#include <SD.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <WebServer.h>
#include <math.h>
#include <sys/time.h>
#include <time.h>
#include <vector>
#include <algorithm>
#include "esp_sntp.h"
#include "esp_heap_caps.h"
#include "esp_task_wdt.h"
#include "driver/i2s_std.h"
#include "tham_so.h"
#include "tham_chieu_dong_nhat.h"

#if !CONFIG_IDF_TARGET_ESP32S3
#error "Firmware van hanh chi danh cho ESP32-S3 (Tools > Board: ESP32S3 Dev Module)"
#endif

#include <TussiCount_v1v2_inferencing.h>   // hai mô hình v1 (Impulse #2) và v2 (Impulse #3) trong một SDK
#if MO_HINH_DEM == 1
#define TEN_MO_HINH "v1"
#elif MO_HINH_DEM == 2
#define TEN_MO_HINH "v2"
#else
#error "MO_HINH_DEM phai la 1 hoac 2 (tham_so.h)"
#endif
static ei_impulse_handle_t *const MO_HINH[2] = {&impulse_handle_1156522_2, &impulse_handle_1156522_3};

// ======================================================================== hằng số
static const uint32_t TAN_SO = 16000;
static const uint32_t CUA_SO = 16000;          // 1 giây
static const uint32_t BUOC = 8000;             // 0,5 giây
static const uint32_t VONG = TAN_SO * 8;           // bộ đệm vòng 8 giây
static const uint32_t KHOI_I2S = 512;          // 32 ms mỗi lần đọc
static const char *THU_MUC = "";   // ghi ở thư mục gốc của thẻ (tạo tệp trong thư mục con lỗi trên thẻ thử 12/11)

// ======================================================================== trạng thái dùng chung
static portMUX_TYPE khoaMau = portMUX_INITIALIZER_UNLOCKED;   // bảo vệ tongMau và mốc thời gian
static int16_t *vong = nullptr;                // bộ đệm vòng (PSRAM)
static volatile uint64_t tongMau = 0;          // tổng số mẫu đã ghi vào vòng
static bool coMoc = false;                     // đã có giờ NTP để neo
static double mocMs = 0;                       // giờ epoch (ms) tại mẫu mocMau
static uint64_t mocMau = 0;

static i2s_chan_handle_t rx = nullptr;
static volatile uint32_t khungTranI2S = 0;     // số lần bộ đệm DMA bị tràn (khung bị mất)
static volatile uint32_t cuaSoBoQua = 0;       // cửa sổ không kịp suy luận (bị ghi đè trong vòng)

// mức âm từng khung 0,5 s (dBFS trọng số A), gom theo phút
static SemaphoreHandle_t khoaMuc;
static std::vector<float> mucKhung;

// số liệu theo phút
static volatile uint32_t suyLuanMaxMs = 0;
static volatile uint32_t suKienTrongPhut = 0;
static volatile int ntpLechMs = 0;            // độ lệch đo được ở lần đồng bộ giờ gần nhất (NTP hoặc điện thoại)
static volatile time_t ntpLanCuoi = 0;
static volatile uint32_t soLanNtp = 0;
static volatile char nguonDongBo = '-';
static volatile bool wifiDangBat = false; static bool chanWifiSauDongBo = false; static uint32_t hetWifiLuc = 0;      // Wi-Fi chỉ bật trong khung đồng bộ giờ       // 'N' = NTP qua Internet, 'D' = điện thoại qua Wi-Fi của mạch

// gói 10 phút
static uint32_t suKien10p = 0;

// dòng chờ ghi thẻ: (ngày tệp, loại tệp, nội dung)
struct DongCho { uint32_t ngay; uint8_t loai; String noiDung; };   // loai: 0 su_kien, 1 diem, 2 moi_phut, 3 dong_bo
static SemaphoreHandle_t khoaGhi;
static std::vector<DongCho> cho;
static volatile uint32_t loiThe = 0;
static bool theSanSang = false;
static SPIClass spiThe(FSPI);

// cấu hình mạng
static String wifiSsid, wifiPass, ntpMay = "pool.ntp.org", sheetsUrl;
static String apTen = String("TussiCount-") + TEN_THIET_BI, apMatKhau = "tussicount";
static WebServer may(80);

// ======================================================================== tiện ích thời gian
static double mauSangMs(uint64_t mau) {        // mẫu → giờ epoch (ms)
  portENTER_CRITICAL(&khoaMau);
  double t = mocMs + ((double)mau - (double)mocMau) * 1000.0 / TAN_SO;
  portEXIT_CRITICAL(&khoaMau);
  return t;
}
static uint32_t ngayTep(double epochMs) {       // ngày của (giờ VN − 6 giờ), dạng YYYYMMDD
  time_t t = (time_t)(epochMs / 1000.0) - 6 * 3600;
  struct tm g; localtime_r(&t, &g);
  return (g.tm_year + 1900) * 10000 + (g.tm_mon + 1) * 100 + g.tm_mday;
}
static String gioVN(double epochMs, bool coGiay = true) {
  time_t t = (time_t)(epochMs / 1000.0);
  struct tm g; localtime_r(&t, &g);
  char b[24];
  strftime(b, sizeof b, coGiay ? "%Y-%m-%d %H:%M:%S" : "%Y-%m-%d %H:%M", &g);
  return String(b);
}
static double bayGioMs() { struct timeval tv; gettimeofday(&tv, nullptr); return tv.tv_sec * 1000.0 + tv.tv_usec / 1000.0; }

static void choGhi(uint32_t ngay, uint8_t loai, const String &s);

// Neo đồng hồ mẫu vào một giờ chuẩn (thucMs, giờ epoch ms) tại thời điểm hiện tại: đo độ lệch giữa giờ chuẩn và giờ
// đồng hồ mẫu dự đoán (= phần trôi tích luỹ từ lần neo trước), ghi vào /..._dong_bo.csv, rồi neo lại.
// Độ lệch này dùng để hiệu chỉnh trôi giờ sau (tools/phan_tich/hieu_chinh_troi_gio.py).
static void neoGio(double thucMs, char nguon, int rttMs) {
  portENTER_CRITICAL(&khoaMau);
  uint64_t s = tongMau;
  bool daCo = coMoc;
  double duDoan = mocMs + ((double)s - (double)mocMau) * 1000.0 / TAN_SO;
  int lech = daCo ? (int)lround(thucMs - duDoan) : 0;
  mocMs = thucMs; mocMau = s; coMoc = true;
  portEXIT_CRITICAL(&khoaMau);
  ntpLechMs = lech; ntpLanCuoi = (time_t)(thucMs / 1000.0); soLanNtp++; nguonDongBo = nguon;
  char b[120];
  snprintf(b, sizeof b, "THAT,%s,%.1f,%s,%s,%d,%d,%d", TEN_THIET_BI, thucMs / 1000.0, gioVN(thucMs, true).c_str(),
           nguon == 'N' ? "ntp" : "dien_thoai", daCo ? 1 : 0, lech, rttMs);
  choGhi(ngayTep(thucMs), 3, String(b));
  Serial.printf("Dong bo gio (%s): lech %d ms\n", nguon == 'N' ? "NTP" : "dien thoai", lech);
}
// Gọi từ tác vụ SNTP mỗi lần đồng bộ NTP thành công (khi có Wi-Fi Internet).
static void khiDongBoNtp(struct timeval *tv) { neoGio(tv->tv_sec * 1000.0 + tv->tv_usec / 1000.0, 'N', -1); }

// ======================================================================== ghi thẻ
static void choGhi(uint32_t ngay, uint8_t loai, const String &s) {
  xSemaphoreTake(khoaGhi, portMAX_DELAY);
  cho.push_back({ngay, loai, s});
  xSemaphoreGive(khoaGhi);
}
static const char *DUOI[4] = {"su_kien", "diem", "moi_phut", "dong_bo"};
static const char *DAU_COT[4] = {
  "du_lieu,thiet_bi,mo_hinh,nguong,k,g_s,stt,t_su_kien_epoch,t_gio_vn,do_dai_s,diem_tin_cay,so_cua_so",
  "t_bat_dau_epoch,p_cough_v1,p_cough_v2",
  "du_lieu,thiet_bi,phut_bat_dau_gio_vn,laeq_dbfs,la90_dbfs,laeq_dba,la90_dba,dien_ap_v,thoi_gian_chay_s,"
  "nhiet_do_chip_c,heap_trong_nho_nhat_b,psram_trong_nho_nhat_b,suy_luan_lon_nhat_ms,khung_bi_mat,cua_so_bo_qua,"
  "so_su_kien_trong_phut,dong_bo_lan_cuoi_gio_vn,dong_bo_lech_ms,dong_bo_nguon,wifi_rssi,loi_the,wifi_bat",
  "du_lieu,thiet_bi,t_epoch,t_gio_vn,nguon,da_co_gio_truoc,lech_ms,rtt_ms"};

static bool moThe() {
  SD.end(); spiThe.end();
  spiThe.begin(PIN_SD_SCK, PIN_SD_MISO, PIN_SD_MOSI, PIN_SD_CS);
  const uint32_t tan[] = {4000000, 1000000};      // 4 MHz: ổn định hơn khi Wi-Fi làm sụt nguồn 3V3
  for (uint32_t f : tan) {
    if (SD.begin(PIN_SD_CS, spiThe, f)) {
      Serial.printf("THE: mo the o %lu MHz\n", (unsigned long)(f / 1000000));
      return true;
    }
    SD.end();
  }
  Serial.println("THE: khong mo duoc the");
  return false;
}
static void xaHangCho() {
  std::vector<DongCho> lay;
  xSemaphoreTake(khoaGhi, portMAX_DELAY);
  lay.swap(cho);
  xSemaphoreGive(khoaGhi);
  if (lay.empty()) return;
  // Wi-Fi phát làm sụt nguồn 3V3, thẻ dễ lỗi khi đang ghi (12–13/11): giữ dòng trong hàng chờ, ghi sau khi Wi-Fi tắt.
  if (wifiDangBat && lay.size() < 12000) {
    xSemaphoreTake(khoaGhi, portMAX_DELAY); cho.insert(cho.begin(), lay.begin(), lay.end()); xSemaphoreGive(khoaGhi);
    return;
  }
  if (!theSanSang) { theSanSang = moThe(); if (!theSanSang) { loiThe++; xSemaphoreTake(khoaGhi, portMAX_DELAY); cho.insert(cho.begin(), lay.begin(), lay.end()); if (cho.size() > 20000) cho.erase(cho.begin(), cho.begin() + (cho.size() - 20000)); xSemaphoreGive(khoaGhi); return; } }
  size_t i = 0;
  while (i < lay.size()) {
    uint32_t ngay = lay[i].ngay; uint8_t loai = lay[i].loai;
    char ten[64];
    snprintf(ten, sizeof ten, "%s/%s_%04lu-%02lu-%02lu_%s.csv", THU_MUC, TEN_THIET_BI, (unsigned long)(ngay / 10000),
             (unsigned long)(ngay / 100 % 100), (unsigned long)(ngay % 100), DUOI[loai]);
    bool moi = !SD.exists(ten);
    File f = SD.open(ten, moi ? FILE_WRITE : FILE_APPEND);
    if (!f && moThe()) { moi = !SD.exists(ten); f = SD.open(ten, moi ? FILE_WRITE : FILE_APPEND); }   // thử lại một lần
    if (!f) { Serial.printf("THE: khong mo duoc %s de ghi (moi=%d)\n", ten, moi); loiThe++; theSanSang = false; SD.end(); break; }
    if (moi) f.println(DAU_COT[loai]);
    while (i < lay.size() && lay[i].ngay == ngay && lay[i].loai == loai) { f.println(lay[i].noiDung); i++; }
    f.close();
  }
  if (i < lay.size()) {   // thẻ lỗi giữa chừng: giữ lại phần chưa ghi
    xSemaphoreTake(khoaGhi, portMAX_DELAY);
    cho.insert(cho.begin(), lay.begin() + i, lay.end());
    xSemaphoreGive(khoaGhi);
  }
}

// ======================================================================== âm thanh (lõi 0)
// Bộ lọc trọng số A ở 16 kHz (biến đổi song tuyến, 3 khâu bậc hai; 100 Hz −19,1 dB, 1 kHz 0,0 dB).
static const float SOS[3][6] = {
  {5.3148982982e-01f, 1.0629796596e+00f, 5.3148982982e-01f, 1.0f, 8.2156381798e-01f, 1.6874177675e-01f},
  {1.0f, -2.0002054318e+00f, 1.0002054529e+00f, 1.0f, -1.7055096337e+00f, 7.1598757534e-01f},
  {1.0f, -1.9997945682e+00f, 9.9979458927e-01f, 1.0f, -1.9838867573e+00f, 9.8395166642e-01f}};
static float zA[3][2] = {{0}};
static inline float locA(float x) {
  for (int k = 0; k < 3; k++) {
    float y = SOS[k][0] * x + zA[k][0];
    zA[k][0] = SOS[k][1] * x - SOS[k][4] * y + zA[k][1];
    zA[k][1] = SOS[k][2] * x - SOS[k][5] * y;
    x = y;
  }
  return x;
}

static bool IRAM_ATTR khiTranI2S(i2s_chan_handle_t, i2s_event_data_t *, void *) { khungTranI2S++; return false; }

static bool khoiDongMic() {
  i2s_chan_config_t cc = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
  cc.dma_desc_num = 8;
  cc.dma_frame_num = KHOI_I2S;
  if (i2s_new_channel(&cc, nullptr, &rx) != ESP_OK) return false;
  i2s_std_config_t cfg = {
    .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(TAN_SO),
    .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_MONO),
    .gpio_cfg = {
      .mclk = I2S_GPIO_UNUSED, .bclk = (gpio_num_t)PIN_MIC_SCK, .ws = (gpio_num_t)PIN_MIC_WS,
      .dout = I2S_GPIO_UNUSED, .din = (gpio_num_t)PIN_MIC_SD,
      .invert_flags = {.mclk_inv = false, .bclk_inv = false, .ws_inv = false},
    },
  };
  cfg.slot_cfg.slot_mask = I2S_STD_SLOT_LEFT;
  if (i2s_channel_init_std_mode(rx, &cfg) != ESP_OK) return false;
  i2s_event_callbacks_t cbs = {};
  cbs.on_recv_q_ovf = khiTranI2S;
  i2s_channel_register_event_callback(rx, &cbs, nullptr);
  return i2s_channel_enable(rx) == ESP_OK;
}

static void tacVuAmThanh(void *) {
  static int32_t raw[KHOI_I2S];
  double tongBinhPhuong = 0; uint32_t demKhung = 0;
  esp_task_wdt_add(nullptr);
  for (;;) {
    size_t got = 0;
    if (i2s_channel_read(rx, raw, sizeof raw, &got, 1000) != ESP_OK || got == 0) { esp_task_wdt_reset(); continue; }
    uint32_t n = got / 4;
    uint64_t dau;
    portENTER_CRITICAL(&khoaMau); dau = tongMau; portEXIT_CRITICAL(&khoaMau);
    for (uint32_t i = 0; i < n; i++) {
      int32_t v = (int32_t)(((int64_t)raw[i] * HE_SO_KHUECH_DAI) >> 16);
      if (v > 32767) v = 32767; else if (v < -32768) v = -32768;
      vong[(dau + i) % VONG] = (int16_t)v;
      float a = locA((float)v);
      tongBinhPhuong += (double)a * a;
      if (++demKhung == BUOC) {      // hết một khung 0,5 s
        float db = 10.0f * log10f((float)(tongBinhPhuong / BUOC) / (32768.0f * 32768.0f) + 1e-12f);
        xSemaphoreTake(khoaMuc, portMAX_DELAY); mucKhung.push_back(db); xSemaphoreGive(khoaMuc);
        tongBinhPhuong = 0; demKhung = 0;
      }
    }
    portENTER_CRITICAL(&khoaMau); tongMau = dau + n; portEXIT_CRITICAL(&khoaMau);
    esp_task_wdt_reset();
  }
}

// ======================================================================== suy luận và gộp sự kiện (lõi 1)
static float *cuaSo = nullptr;
static int lay(size_t off, size_t len, float *out) { memcpy(out, cuaSo + off, len * sizeof(float)); return 0; }
static int chiSoCough[2] = {-1, -1};

// Chấm cửa sổ đang nằm trong cuaSo bằng mô hình m (0 = v1, 1 = v2); trả về p_cough hoặc −1 nếu lỗi.
static float cham(int m) {
  signal_t sig; sig.total_length = CUA_SO; sig.get_data = &lay;
  ei_impulse_result_t r = {0};
  if (process_impulse(MO_HINH[m], &sig, &r, false) != EI_IMPULSE_OK) return -1.0f;
  return r.classification[chiSoCough[m]].value;
}

// Gộp sự kiện theo thời gian thực, đúng định nghĩa trong tools/chay_mo_hinh/gop_su_kien.py.
struct Nhom { bool mo = false; uint64_t iDau, iCuoi, iMax; uint32_t soVuot; float pMax; double tMaxMs; };
static Nhom nh;
static uint32_t sttSuKien = 0;
static const uint32_t M_MAX = (uint32_t)lroundf(G_NGHI_S / 0.5f);

static void dongNhom() {
  if (!nh.mo) return;
  nh.mo = false;
  if ((int)nh.soVuot < K_CUA_SO) return;
  double tSuKien = nh.tMaxMs + 500.0;                                  // tâm cửa sổ điểm cao nhất
  float doDai = (float)(nh.iCuoi - nh.iDau) * 0.5f + 1.0f;               // đầu cửa sổ đầu → cuối cửa sổ cuối
  char b[200];
  snprintf(b, sizeof b, "THAT,%s,%s,%.3f,%d,%.1f,%lu,%.1f,%s,%.1f,%.3f,%lu", TEN_THIET_BI, TEN_MO_HINH, NGUONG, K_CUA_SO,
           G_NGHI_S, (unsigned long)++sttSuKien, tSuKien / 1000.0, gioVN(tSuKien).c_str(), doDai, nh.pMax,
           (unsigned long)nh.soVuot);
  choGhi(ngayTep(tSuKien), 0, String(b));
  suKienTrongPhut++; suKien10p++;
  Serial.printf("SU KIEN %lu  %s  dai %.1f s  p %.3f\n", (unsigned long)sttSuKien, gioVN(tSuKien).c_str(), doDai, nh.pMax);
}
static void nhanDiem(uint64_t i, float p, double tMs) {
  if (p >= NGUONG) {
    if (nh.mo && (i - nh.iCuoi - 1) <= M_MAX) {
      nh.iCuoi = i; nh.soVuot++;
      if (p > nh.pMax) { nh.pMax = p; nh.iMax = i; nh.tMaxMs = tMs; }
    } else {
      dongNhom();
      nh.mo = true; nh.iDau = nh.iCuoi = nh.iMax = i; nh.soVuot = 1; nh.pMax = p; nh.tMaxMs = tMs;
    }
  } else if (nh.mo && (i - nh.iCuoi) > M_MAX) {
    dongNhom();
  }
}

static void tacVuSuyLuan(void *) {
  esp_task_wdt_add(nullptr);
  while (!coMoc) { esp_task_wdt_reset(); vTaskDelay(pdMS_TO_TICKS(200)); }   // chờ giờ NTP đầu tiên
  uint64_t dau;
  portENTER_CRITICAL(&khoaMau); dau = tongMau; portEXIT_CRITICAL(&khoaMau);
  uint64_t i = dau / BUOC + 1;                     // chỉ số cửa sổ; cửa sổ i bắt đầu ở mẫu i × 0,5 s
  for (;;) {
    uint64_t batDau = i * BUOC, s;
    portENTER_CRITICAL(&khoaMau); s = tongMau; portEXIT_CRITICAL(&khoaMau);
    if (s < batDau + CUA_SO) { esp_task_wdt_reset(); vTaskDelay(pdMS_TO_TICKS(20)); continue; }
    if (s - batDau > VONG - KHOI_I2S * 2) {         // tụt quá xa: dữ liệu đã bị ghi đè
      uint64_t moi = (s - CUA_SO) / BUOC;
      cuaSoBoQua += (uint32_t)(moi - i);
      dongNhom();
      i = moi; continue;
    }
    for (uint32_t k = 0; k < CUA_SO; k++) cuaSo[k] = (float)vong[(batDau + k) % VONG];
    uint32_t t0 = millis();
    float p1 = cham(0), p2 = cham(1);
    uint32_t ms = millis() - t0;                     // thời gian suy luận của cả hai mô hình
    if (ms > suyLuanMaxMs) suyLuanMaxMs = ms;
    double tMs = mauSangMs(batDau);
    char b[48];
    snprintf(b, sizeof b, "%.1f,%.4f,%.4f", tMs / 1000.0, p1, p2);
    choGhi(ngayTep(tMs), 1, String(b));
    float p = (MO_HINH_DEM == 1) ? p1 : p2;
    if (p >= 0) nhanDiem(i, p, tMs);
    {   // theo dõi qua Serial: điểm lớn nhất của mỗi mô hình trong 10 giây và mức đỉnh mẫu
      static float m1 = 0, m2 = 0; static int dem = 0; static int16_t dinh = 0;
      for (uint32_t k = 0; k < CUA_SO; k += 4) { int16_t a = abs((int)cuaSo[k]); if (a > dinh) dinh = a; }
      if (p1 > m1) m1 = p1; if (p2 > m2) m2 = p2;
      if (++dem >= 20) { Serial.printf("10 s: p_max v1 %.3f · v2 %.3f · dinh mau %d · suy luan %lu ms\n", m1, m2, dinh, (unsigned long)ms); m1 = m2 = 0; dem = 0; dinh = 0; }
    }
    i++;
    esp_task_wdt_reset();
  }
}

// ======================================================================== nhật ký mỗi phút, ghi thẻ (lõi 0)
static float phanVi(std::vector<float> v, float q) {
  if (v.empty()) return NAN;
  std::sort(v.begin(), v.end());
  float vt = q * (v.size() - 1);
  size_t a = (size_t)vt; float d = vt - a;
  return a + 1 < v.size() ? v[a] * (1 - d) + v[a + 1] * d : v[a];
}
static String soHoacTrong(float x, int sl) { return isnan(x) ? String("") : String(x, sl); }

static void guiSheets(const String &dong) {
  if (sheetsUrl.length() == 0 || WiFi.status() != WL_CONNECTED) return;
  HTTPClient h;
  h.setTimeout(5000);
  if (h.begin(sheetsUrl + (sheetsUrl.indexOf('?') >= 0 ? "&" : "?") + dong)) { h.GET(); h.end(); }
}

static void tacVuNhatKy(void *) {
  esp_task_wdt_add(nullptr);
  time_t phutTruoc = 0; uint32_t lanXa = 0; float laeq10 = 0; int dem10 = 0;
  for (;;) {
    vTaskDelay(pdMS_TO_TICKS(250));
    esp_task_wdt_reset();
    if (!coMoc) continue;
    time_t bayGio = time(nullptr);
    time_t phut = bayGio - bayGio % 60;
    if (phutTruoc == 0) { phutTruoc = phut; xSemaphoreTake(khoaMuc, portMAX_DELAY); mucKhung.clear(); xSemaphoreGive(khoaMuc); }
    if (phut != phutTruoc) {      // hết một phút: ghi một dòng cho phút vừa qua
      std::vector<float> m;
      xSemaphoreTake(khoaMuc, portMAX_DELAY); m.swap(mucKhung); xSemaphoreGive(khoaMuc);
      float laeq = NAN, la90 = NAN;
      if (!m.empty()) {
        double tong = 0; for (float x : m) tong += pow(10.0, x / 10.0);
        laeq = 10.0f * log10f((float)(tong / m.size()));
        la90 = phanVi(m, 0.10f);   // vượt trong 90% thời gian = phân vị 10%
      }
      float dienAp = NAN;
      if (PIN_DIEN_AP >= 0) dienAp = analogReadMilliVolts(PIN_DIEN_AP) / 1000.0f * HE_SO_CAU_CHIA;
      time_t tn = ntpLanCuoi; struct tm g; localtime_r(&tn, &g); char gn[12]; strftime(gn, sizeof gn, "%H:%M:%S", &g);
      String d = String("THAT,") + TEN_THIET_BI + "," + gioVN(phutTruoc * 1000.0, false) + "," + soHoacTrong(laeq, 1) + "," +
                 soHoacTrong(la90, 1) + "," + (DA_HIEU_CHUAN ? soHoacTrong(HC_A * laeq + HC_B, 1) : String("")) + "," +
                 (DA_HIEU_CHUAN ? soHoacTrong(HC_A * la90 + HC_B, 1) : String("")) + "," + soHoacTrong(dienAp, 3) + "," +
                 String((uint32_t)(esp_timer_get_time() / 1000000ULL)) + "," + String(temperatureRead(), 1) + "," +
                 String(heap_caps_get_minimum_free_size(MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT)) + "," +
                 String(heap_caps_get_minimum_free_size(MALLOC_CAP_SPIRAM)) + "," + String(suyLuanMaxMs) + "," +
                 String(khungTranI2S) + "," + String(cuaSoBoQua) + "," + String(suKienTrongPhut) + "," + String(gn) + "," +
                 String(ntpLechMs) + "," + String(nguonDongBo == 'N' ? "ntp" : nguonDongBo == 'D' ? "dien_thoai" : "") + "," +
                 String(WiFi.status() == WL_CONNECTED ? WiFi.RSSI() : 0) + "," + String(loiThe) + "," + String(wifiDangBat ? 1 : 0);
      choGhi(ngayTep(phutTruoc * 1000.0), 2, d);
      Serial.printf("[%s] LAeq %.1f LA90 %.1f dBFS | suy luan max %lu ms | su kien %lu | khung mat %lu | NTP lech %d ms | the %s\n",
                    gioVN(phutTruoc * 1000.0, false).c_str(), laeq, la90, (unsigned long)suyLuanMaxMs,
                    (unsigned long)suKienTrongPhut, (unsigned long)khungTranI2S, ntpLechMs, theSanSang ? "OK" : "LOI");
      if (!isnan(laeq)) { laeq10 += pow(10.0, laeq / 10.0); dem10++; }
      struct tm gp; localtime_r(&phutTruoc, &gp);
      if (gp.tm_min % 10 == 9) {   // vừa hết khối 10 phút: gửi gói tổng hợp (16.5; số liệu chính vẫn lấy từ thẻ)
        if (dem10 > 0) {
          guiSheets("tb=" + String(TEN_THIET_BI) + "&phut=" + String((long)phut) + "&su_kien=" + String(suKien10p) +
                    "&laeq=" + String(10 * log10(laeq10 / dem10), 1));
        }
        suKien10p = 0; laeq10 = 0; dem10 = 0;
      }
      suyLuanMaxMs = 0; suKienTrongPhut = 0;
      phutTruoc = phut;
    }
    if (++lanXa >= 40) { lanXa = 0; xaHangCho(); }   // ghi thẻ mỗi 10 giây
  }
}

// ======================================================================== phép thử đồng nhất (Protocol 7.6)
// Nếu thẻ có /thu_dong_nhat.wav (PCM 16 bit, 1 kênh, 16 kHz), chấm mọi cửa sổ 1 s trượt 0,5 s của tệp bằng đúng
// mô hình trên chip và ghi /thu_dong_nhat_diem.csv (cua_so,t_bat_dau_s,p_cough_v1,p_cough_v2,ms_xu_ly) — cùng định dạng với
// "chay_mo_hinh dai" trên máy tính để so sánh (một cột điểm cho mỗi mô hình). Chỉ ĐỌC tệp có sẵn; firmware không ghi âm thanh.
static void thuDongNhat() {
  File w = SD.open("/thu_dong_nhat.wav");
  if (!w) return;
  Serial.println("Phep thu dong nhat: dang cham /thu_dong_nhat.wav ...");
  uint8_t h[44];
  if (w.read(h, 44) != 44 || memcmp(h, "RIFF", 4) || memcmp(h + 8, "WAVE", 4)) { Serial.println("  tep khong phai WAV"); w.close(); return; }
  uint32_t vt = 12, dataPos = 0, dataLen = 0;
  while (vt + 8 <= w.size()) {           // tìm khối data
    uint8_t c[8]; w.seek(vt); w.read(c, 8);
    uint32_t sz = c[4] | c[5] << 8 | c[6] << 16 | (uint32_t)c[7] << 24;
    if (!memcmp(c, "data", 4)) { dataPos = vt + 8; dataLen = sz; break; }
    vt += 8 + sz + (sz & 1);
  }
  if (!dataPos) { Serial.println("  khong thay khoi data"); w.close(); return; }
  uint32_t n = dataLen / 2;
  int16_t *m = (int16_t *)heap_caps_malloc((size_t)n * 2, MALLOC_CAP_SPIRAM);
  if (!m) { Serial.println("  tep qua lon"); w.close(); return; }
  w.seek(dataPos); w.read((uint8_t *)m, (size_t)n * 2); w.close();
  File o = SD.open("/thu_dong_nhat_diem.csv", FILE_WRITE);
  o.println("cua_so,t_bat_dau_s,p_cough_v1,p_cough_v2,ms_xu_ly");
  uint32_t so = 0, msMax = 0;
  int dat[2] = {0, 0}; float lechMax[2] = {0, 0};      // so với bộ chạy trên máy tính (tham_chieu_dong_nhat.h)
  for (uint32_t bd = 0; bd + CUA_SO <= n; bd += BUOC, so++) {
    for (uint32_t k = 0; k < CUA_SO; k++) cuaSo[k] = (float)m[bd + k];
    uint32_t t0 = millis();
    float p1 = cham(0), p2 = cham(1);
    uint32_t ms = millis() - t0; if (ms > msMax) msMax = ms;
    o.printf("%lu,%.4f,%.6f,%.6f,%lu\n", (unsigned long)so, bd / (double)TAN_SO, p1, p2, (unsigned long)ms);
    if ((int)so < THAM_CHIEU_SO) {
      float d1 = fabsf(p1 - THAM_CHIEU_V1[so]), d2 = fabsf(p2 - THAM_CHIEU_V2[so]);
      if (d1 <= 0.0040f) dat[0]++; if (d2 <= 0.0040f) dat[1]++;      // lệch ≤ 1 bậc int8 (1/256)
      if (d1 > lechMax[0]) lechMax[0] = d1; if (d2 > lechMax[1]) lechMax[1] = d2;
    }
  }
  if ((int)so == THAM_CHIEU_SO) {
    for (int m = 0; m < 2; m++)
      Serial.printf("  v%d: %d/%lu cua so lech <= 1 bac int8 (%.1f%%), lech lon nhat %.4f\n", m + 1, dat[m],
                    (unsigned long)so, 100.0 * dat[m] / so, lechMax[m]);
    bool dat_ = dat[0] * 100 >= 95 * (int)so && dat[1] * 100 >= 95 * (int)so;
    Serial.println(dat_ ? "  -> PHEP THU DONG NHAT: DAT (>= 95% cua so lech <= 1 bac, nhu tieu chi tren may tinh)"
                        : "  -> PHEP THU DONG NHAT: CHUA DAT");
  } else {
    Serial.printf("  tep co %lu cua so, khong phai tep tham chieu (%d) - chi ghi diem, khong so\n", (unsigned long)so, THAM_CHIEU_SO);
  }
  o.close(); free(m);
  Serial.printf("  xong: %lu cua so, suy luan lon nhat %lu ms -> /thu_dong_nhat_diem.csv\n", (unsigned long)so, (unsigned long)msMax);
}

// ======================================================================== đồng bộ giờ bằng điện thoại
// Mạch tự phát Wi-Fi (apTen). Điện thoại kết nối, mở http://192.168.4.1 và bấm "Đồng bộ giờ": trang đo 8 lần
// (giờ điện thoại lúc gửi t0, giờ mạch td, giờ điện thoại lúc nhận t1), lấy lần có thời gian khứ hồi nhỏ nhất,
// độ lệch = (t0 + t1)/2 − td, rồi gửi về mạch. Giờ điện thoại lấy từ mạng di động nên thường sai dưới 0,1 giây.
static double gioThietBiMs() { return coMoc ? mauSangMs(tongMau) : bayGioMs(); }
static const char TRANG[] PROGMEM = R"HTML(<!doctype html><html lang="vi"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>TussiCount</title>
<style>body{font-family:system-ui,sans-serif;max-width:480px;margin:0 auto;padding:16px;color:#121513}
h1{font-size:20px;margin:0 0 4px}.o{border:1px solid #ccc;border-radius:10px;padding:12px;margin:12px 0}
b{font-family:ui-monospace,monospace}button{width:100%;padding:14px;font-size:17px;border:0;border-radius:10px;
background:#0F766E;color:#fff}#kq{margin-top:10px;font-weight:600}</style>
<h1>TussiCount · <span id="tb"></span></h1><div>Trang chỉ trên Wi-Fi của mạch; không có âm thanh.</div>
<div class="o">Giờ thiết bị: <b id="g">…</b><br>Giờ điện thoại: <b id="dt">…</b><br>Đồng bộ gần nhất: <b id="ld">…</b>
<br>Độ lệch lần đó: <b id="lc">…</b><br>Sự kiện từ lúc khởi động: <b id="sk">…</b><br>Thẻ nhớ: <b id="th">…</b>
<br>Suy luận lớn nhất (phút trước): <b id="sl">…</b></div>
<button id="nut">Đồng bộ giờ</button><div id="kq"></div>
<script>
const $=i=>document.getElementById(i),f=t=>new Date(t).toLocaleString('vi-VN',{hour12:false});
async function tt(){try{const r=await(await fetch('/trang_thai')).json();$('tb').textContent=r.tb;
$('g').textContent=r.co_gio?f(r.gio):'chưa có giờ';$('dt').textContent=f(Date.now());
$('ld').textContent=r.lan_cuoi?f(r.lan_cuoi*1000)+' ('+r.nguon+')':'chưa';$('lc').textContent=r.lan_cuoi?r.lech+' ms':'—';
$('sk').textContent=r.su_kien;$('th').textContent=r.the?'OK':'LỖI';$('sl').textContent=r.suy_luan+' ms'}catch(e){}}
$('nut').onclick=async()=>{$('nut').disabled=true;$('kq').textContent='Đang đo…';let best=null;
for(let i=0;i<8;i++){const t0=Date.now();const td=+(await(await fetch('/gio?'+i)).text());const t1=Date.now();
const rtt=t1-t0;if(!best||rtt<best.rtt)best={rtt,lech:Math.round((t0+t1)/2-td)}}
const q=await fetch('/dat_gio?lech='+best.lech+'&rtt='+best.rtt),r=await q.text();
$('kq').textContent=(q.ok?'Đã đồng bộ. ':'LỖI: ')+r+' · khứ hồi '+best.rtt+' ms';$('nut').disabled=false;tt()};
tt();setInterval(tt,2000);
</script></html>)HTML";

static void khoiDongTrang() {
  may.on("/", []() { may.send_P(200, "text/html; charset=utf-8", TRANG); });
  may.on("/gio", []() { char b[24]; snprintf(b, sizeof b, "%.0f", gioThietBiMs()); may.send(200, "text/plain", b); });
  may.on("/dat_gio", []() {
    // Lần đầu (chưa có giờ) độ lệch ≈ 1,8 × 10^12 ms, vượt kiểu long 32 bit → đọc bằng số thực.
    double lech = strtod(may.arg("lech").c_str(), nullptr); int rtt = may.arg("rtt").toInt();
    double thuc = gioThietBiMs() + lech;
    if (thuc < 1.7e12 || rtt < 0 || rtt > 2000) { may.send(400, "text/plain", "gia tri khong hop le"); return; }
    struct timeval tv = {(time_t)(thuc / 1000.0), (suseconds_t)(fmod(thuc, 1000.0) * 1000)};
    settimeofday(&tv, nullptr);
    neoGio(thuc, 'D', rtt);
    chanWifiSauDongBo = true; hetWifiLuc = millis() + 90000;            // tắt Wi-Fi sau 90 giây để thẻ ghi an toàn
    may.send(200, "text/plain; charset=utf-8", String("Lech do duoc: ") + ntpLechMs + " ms");
  });
  may.on("/trang_thai", []() {
    char b[260];
    snprintf(b, sizeof b, "{\"tb\":\"%s\",\"co_gio\":%s,\"gio\":%.0f,\"lan_cuoi\":%ld,\"nguon\":\"%s\",\"lech\":%d,"
             "\"su_kien\":%lu,\"the\":%s,\"suy_luan\":%lu}", TEN_THIET_BI, coMoc ? "true" : "false", gioThietBiMs(),
             (long)ntpLanCuoi, nguonDongBo == 'N' ? "NTP" : "điện thoại", ntpLechMs, (unsigned long)sttSuKien,
             theSanSang ? "true" : "false", (unsigned long)suyLuanMaxMs);
    may.send(200, "application/json; charset=utf-8", b);
  });
  may.begin();
}

// ======================================================================== bật/tắt Wi-Fi theo khung giờ
// Wi-Fi phát làm sụt nguồn 3V3 và gây nhiễu vào micro, thẻ nhớ (thử 12/11: mẫu chạm đỉnh, thẻ lỗi khi Wi-Fi bật).
// Vì vậy Wi-Fi chỉ bật để đồng bộ giờ: 15 phút đầu sau khởi động (hoặc đến khi có giờ) và mỗi ngày 16:50–17:20
// (giờ thay sạc). Ngoài các khung này Wi-Fi tắt hẳn. Trạng thái Wi-Fi ghi trong nhật ký mỗi phút (cột wifi_bat).
static void batWifi() {
  if (wifiDangBat) return;
  WiFi.mode(wifiSsid.length() ? WIFI_AP_STA : WIFI_AP);
  WiFi.softAP(apTen.c_str(), apMatKhau.c_str());
  WiFi.setTxPower(WIFI_POWER_2dBm);            // công suất thấp nhất: đủ cho điện thoại đứng cạnh hộp
  if (wifiSsid.length()) { WiFi.setAutoReconnect(true); WiFi.begin(wifiSsid.c_str(), wifiPass.c_str()); }
  wifiDangBat = true;
  Serial.printf("Wi-Fi BAT: \"%s\" · http://192.168.4.1\n", apTen.c_str());
}
static void tatWifi() {
  if (!wifiDangBat) return;
  WiFi.softAPdisconnect(true); WiFi.disconnect(true); WiFi.mode(WIFI_OFF);
  wifiDangBat = false;
  Serial.println("Wi-Fi TAT");
}
static void dieuKhienWifi() {
  static uint32_t lan = 0;
  if (millis() - lan < 5000) return;
  lan = millis();
  bool can = !coMoc || millis() < 15UL * 60UL * 1000UL;
  if (coMoc) {
    time_t t = time(nullptr); struct tm g; localtime_r(&t, &g);
    int phut = g.tm_hour * 60 + g.tm_min;
    if (phut >= 16 * 60 + 50 && phut < 17 * 60 + 20) can = true;
  }
  if (!can) chanWifiSauDongBo = false;                                   // hết khung: lần sau lại cho bật
  else if (chanWifiSauDongBo && (int32_t)(millis() - hetWifiLuc) >= 0) can = false;
  if (can) batWifi(); else tatWifi();
}

// ======================================================================== khởi động
static void docCauHinh() {
  File f = SD.open("/cauhinh.txt");
  if (!f) { Serial.println("Khong co /cauhinh.txt tren the: chua co Wi-Fi, chua co gio NTP"); return; }
  while (f.available()) {
    String d = f.readStringUntil('\n'); d.trim();
    int k = d.indexOf('=');
    if (d.startsWith("#") || k < 0) continue;
    String khoa = d.substring(0, k), gt = d.substring(k + 1);
    khoa.trim(); gt.trim();
    if (khoa == "wifi_ssid") wifiSsid = gt; else if (khoa == "wifi_pass") wifiPass = gt;
    else if (khoa == "ntp" && gt.length()) ntpMay = gt; else if (khoa == "sheets_url") sheetsUrl = gt;
    else if (khoa == "ap_ten" && gt.length()) apTen = gt; else if (khoa == "ap_mat_khau" && gt.length() >= 8) apMatKhau = gt;
  }
  f.close();
}

void setup() {
  Serial.begin(115200);
  delay(1500);
  Serial.printf("\n##### TussiCount %s · firmware %s · cham v1 (impulse %u) + v2 (impulse %u) · dem bang %s · nguong %.3f k %d g %.1f s\n",
                TEN_THIET_BI, PHIEN_BAN_FW, (unsigned)MO_HINH[0]->impulse->impulse_id, (unsigned)MO_HINH[1]->impulse->impulse_id,
                TEN_MO_HINH, NGUONG, K_CUA_SO, G_NGHI_S);
  for (int m = 0; m < 2; m++)
    for (size_t k = 0; k < MO_HINH[m]->impulse->label_count; k++)
      if (strcmp(MO_HINH[m]->impulse->categories[k], "cough") == 0) chiSoCough[m] = k;
  if (chiSoCough[0] < 0 || chiSoCough[1] < 0 || !psramFound()) { Serial.println("LOI: mo hinh khong co nhan cough hoac khong co PSRAM"); for (;;) delay(1000); }

  esp_task_wdt_config_t wdt = {.timeout_ms = 30000, .idle_core_mask = 0, .trigger_panic = true};
  if (esp_task_wdt_reconfigure(&wdt) != ESP_OK) esp_task_wdt_init(&wdt);

  khoaMuc = xSemaphoreCreateMutex();
  khoaGhi = xSemaphoreCreateMutex();
  vong = (int16_t *)heap_caps_malloc(VONG * sizeof(int16_t), MALLOC_CAP_SPIRAM);
  cuaSo = (float *)heap_caps_malloc(CUA_SO * sizeof(float), MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT);
  if (!cuaSo) cuaSo = (float *)heap_caps_malloc(CUA_SO * sizeof(float), MALLOC_CAP_SPIRAM);
  if (!vong || !cuaSo) { Serial.println("LOI: khong cap phat duoc bo nho"); for (;;) delay(1000); }

  theSanSang = moThe();
  Serial.println(theSanSang ? "The nho: OK" : "The nho: LOI - van chay, se thu lai moi 10 giay");
  if (theSanSang) { docCauHinh(); thuDongNhat(); }

  if (!khoiDongMic()) { Serial.println("LOI: khong khoi dong duoc micro I2S"); for (;;) delay(1000); }

  // Giờ: (1) mạch luôn tự phát Wi-Fi để đồng bộ bằng điện thoại; (2) nếu có Wi-Fi Internet thì thêm NTP mỗi 30 phút.
  // Mỗi lần đồng bộ (từ nguồn nào) đều đo độ lệch và neo lại đồng hồ mẫu.
  sntp_set_time_sync_notification_cb(khiDongBoNtp);
  sntp_set_sync_interval(NTP_CHU_KY_MS);
  batWifi();
  configTzTime(MUI_GIO, ntpMay.c_str());
  khoiDongTrang();

  xTaskCreatePinnedToCore(tacVuAmThanh, "am_thanh", 6144, nullptr, 20, nullptr, 0);
  xTaskCreatePinnedToCore(tacVuNhatKy, "nhat_ky", 8192, nullptr, 5, nullptr, 0);
  xTaskCreatePinnedToCore(tacVuSuyLuan, "suy_luan", 16384, nullptr, 10, nullptr, 1);
  Serial.println("Da khoi dong. Bat dau dem sau lan dong bo gio dau tien (dien thoai hoac NTP).");
}

void loop() {
  static uint32_t t = 0;
  dieuKhienWifi();
  if (wifiDangBat) may.handleClient();
  if (!coMoc && millis() - t > 10000) {
    t = millis();
    Serial.printf("Chua co gio: ket noi dien thoai vao Wi-Fi \"%s\", mo http://192.168.4.1, bam Dong bo gio\n", apTen.c_str());
  }
  delay(5);
}
