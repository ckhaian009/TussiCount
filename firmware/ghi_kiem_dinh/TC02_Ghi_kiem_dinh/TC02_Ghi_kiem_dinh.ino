// TC-02 – Firmware ghi âm kiểm định (Protocol mục 7, 16.8, 16.14, 16.17). Arduino-ESP32 3.x, mạch ESP32 thường
// (ESP-WROOM-32, Tools > Board: "ESP32 Dev Module"). Không dùng mô hình; chỉ ghi WAV 16 kHz, 16 bit, 1 kênh.
//
// Mạch CHỈ ghi trong các khung giờ đã thông báo (bảng LICH_MAC_DINH, hoặc tệp /lich_ghi.txt trên thẻ nếu có),
// và chỉ sau khi đã đồng bộ giờ bằng điện thoại. Ngoài khung giờ: không ghi, Wi-Fi bật để đồng bộ giờ.
// Trong lúc ghi: Wi-Fi tắt hẳn (tránh nhiễu nguồn vào micro và thẻ). Không lắp LED (Protocol 16.20).
//
// Nối dây (giống T5 trên mạch ESP32 thường):
//   INMP441: VDD-3V3, GND-GND, SCK-G26, WS-G25, SD-G33, L/R-GND
//   Module thẻ: VCC-V5, GND-GND, CS-G5, MOSI-G23, SCK-G18, MISO-G19
//   Không lắp LED (Protocol 16.20). G2 vẫn được điều khiển: nếu bo có sẵn đèn ở G2 thì đèn này sáng khi ghi,
//   chỉ để tiện kiểm tra trên bàn.
//
// Tệp trên thẻ (thư mục gốc):
//   TC-02_YYYYMMDD_HHMMSS.wav  mỗi tệp tối đa 1 giờ; tên = giờ của mẫu đầu tiên (giờ Việt Nam)
//   THU_YYYYMMDD_HHMMSS.wav    ghi thử trên bàn (nghe xong thì xoá)
//   TC-02_ghi.csv              mỗi tệp WAV một dòng: giờ mẫu đầu, số mẫu, mẫu bị thiếu, mẫu chạm đỉnh
//   TC-02_dong_bo.csv          mỗi lần đồng bộ giờ một dòng (độ lệch = phần trôi tích luỹ, để hiệu chỉnh sau)
//   TC-02_khoang_trong.csv     nếu thẻ ghi chậm làm thiếu mẫu: vị trí và độ dài đoạn đã chèn 0 (giữ đúng thời gian)
//
// Serial (115200): t = ghi thử 10 phút, x = dừng ghi thử, s = trạng thái.
#include <Arduino.h>
#include <SPI.h>
#include <SD.h>
#include <WiFi.h>
#include <WebServer.h>
#include <sys/time.h>
#include <time.h>
#include "driver/i2s_std.h"
#include "freertos/queue.h"

// ======================================================================== tham số
#define TEN_THIET_BI "TC-02"
#define PHIEN_BAN_FW "ghi-kiem-dinh-1.0"
const int PIN_MIC_SCK = 26, PIN_MIC_WS = 25, PIN_MIC_SD = 33;
const int PIN_SD_CS = 5, PIN_SD_MOSI = 23, PIN_SD_SCK = 18, PIN_SD_MISO = 19;
const int PIN_LED = 2;
#define MIC_SLOT I2S_STD_SLOT_LEFT
const uint32_t TAN_SO = 16000;
const int HE_SO_KHUECH_DAI = 8;                 // giống TC-01 và T4: (raw × 8) >> 16 (Protocol 16.8)
const uint32_t MAU_MOI_TEP = 3600UL * TAN_SO;   // 1 giờ mỗi tệp
const uint32_t PHUT_GHI_THU = 10;

// Khung giờ ghi (giờ Việt Nam), theo Protocol 16.14. Ghi đè bằng /lich_ghi.txt: mỗi dòng
// "YYYY-MM-DD HH:MM HH:MM nhan" (dòng bắt đầu bằng # bị bỏ qua).
struct KhungGhi { int nam, thang, ngay, gioBd, phutBd, gioKt, phutKt; char nhan[16]; };
static KhungGhi LICH_MAC_DINH[] = {
  {2026, 11, 13, 18, 15, 18, 30, "am_hoc"},
  {2026, 11, 13, 19,  0, 22,  0, "de_sua"},
  {2026, 11, 16, 17, 55, 20, 25, "de_cham_1"},
  {2026, 11, 16, 21, 50, 23, 50, "de_cham_2"},
};
static KhungGhi lich[16];
static int soKhung = 0;

// ======================================================================== khối âm thanh (đọc → ghi thẻ)
const int MAU_KHOI = 512;
const int SO_KHOI = 64;                         // 64 × 512 mẫu = 2,05 giây đệm
struct Khoi { uint64_t viTri; uint32_t thieuTruoc; int16_t mau[MAU_KHOI]; };
static Khoi *khoi = nullptr;
static QueueHandle_t hangRong, hangDay;
static i2s_chan_handle_t rx = NULL;

static volatile uint64_t tongMau = 0;           // đồng hồ mẫu: số mẫu đã đọc từ lúc khởi động
static volatile bool choPhepDay = false;        // tác vụ đọc có đẩy khối sang ghi thẻ không
static volatile uint32_t thieuChoXuLy = 0;      // mẫu bị bỏ vì hết khối rỗng, chèn 0 trước khối kế tiếp
static volatile uint32_t catDinh = 0;
static portMUX_TYPE khoaMau = portMUX_INITIALIZER_UNLOCKED;

// neo giờ: giờ thật (epoch ms) của mẫu số mocMau
static double mocMs = 0; static uint64_t mocMau = 0; static bool coMoc = false;
static int lechLanCuoi = 0; static time_t lanDongBoCuoi = 0;

// thẻ
static SPIClass spiThe(VSPI);
static bool theSanSang = false;

// trạng thái ghi
enum CheDo { NGHI, GHI_LICH, GHI_THU };
static volatile CheDo cheDo = NGHI;
static File tep;
static String tenTep, nhanPhien;
static uint64_t viTriDauTep = 0;
static uint32_t mauTrongTep = 0, thieuTrongTep = 0, catDinhDauTep = 0;
static uint32_t lanCapNhatDau = 0, lanFlush = 0;
static uint32_t ketThucThuMs = 0;
static uint32_t ghiChamNhatMs = 0;

// mạng
static WebServer may(80);
static bool wifiDangBat = false;
static const char *AP_TEN = "TussiCount-TC-02", *AP_MAT_KHAU = "tussicount";

// ======================================================================== thời gian
static double mauSangMs(uint64_t m) {
  portENTER_CRITICAL(&khoaMau);
  double t = mocMs + ((double)m - (double)mocMau) * 1000.0 / TAN_SO;
  portEXIT_CRITICAL(&khoaMau);
  return t;
}
static uint64_t docTongMau() { portENTER_CRITICAL(&khoaMau); uint64_t s = tongMau; portEXIT_CRITICAL(&khoaMau); return s; }
static double gioThietBiMs() { return coMoc ? mauSangMs(docTongMau()) : millis(); }
static String dinhDang(double ms, const char *mau) {
  time_t t = (time_t)(ms / 1000.0); struct tm g; localtime_r(&t, &g);
  char b[32]; strftime(b, sizeof b, mau, &g); return String(b);
}
static void ghiDong(const char *ten, const char *dauCot, const String &dong) {
  if (!theSanSang) return;
  bool moi = !SD.exists(ten);
  File f = SD.open(ten, moi ? FILE_WRITE : FILE_APPEND);
  if (!f) { Serial.printf("LOI: khong mo duoc %s\n", ten); return; }
  if (moi) f.println(dauCot);
  f.println(dong); f.close();
}
static void neoGio(double thucMs, int rttMs) {
  portENTER_CRITICAL(&khoaMau);
  uint64_t s = tongMau; bool daCo = coMoc;
  double duDoan = mocMs + ((double)s - (double)mocMau) * 1000.0 / TAN_SO;
  int lech = daCo ? (int)lround(thucMs - duDoan) : 0;
  mocMs = thucMs; mocMau = s; coMoc = true;
  portEXIT_CRITICAL(&khoaMau);
  lechLanCuoi = lech; lanDongBoCuoi = (time_t)(thucMs / 1000.0);
  char b[160];
  snprintf(b, sizeof b, "THAT,%s,%.1f,%s,dien_thoai,%d,%d,%d", TEN_THIET_BI, thucMs / 1000.0,
           dinhDang(thucMs, "%Y-%m-%d %H:%M:%S").c_str(), daCo ? 1 : 0, lech, rttMs);
  ghiDong("/TC-02_dong_bo.csv", "du_lieu,thiet_bi,t_epoch,t_gio_vn,nguon,da_co_gio_truoc,lech_ms,rtt_ms", String(b));
  Serial.printf("Dong bo gio: lech %d ms (khu hoi %d ms)\n", lech, rttMs);
}

// ======================================================================== lịch ghi
static bool docDong(const String &d, KhungGhi &k) {
  char nhan[16] = "khung";
  int n = sscanf(d.c_str(), "%d-%d-%d %d:%d %d:%d %15s", &k.nam, &k.thang, &k.ngay, &k.gioBd, &k.phutBd,
                 &k.gioKt, &k.phutKt, nhan);
  if (n < 7) return false;
  strncpy(k.nhan, nhan, sizeof k.nhan); k.nhan[sizeof k.nhan - 1] = 0;
  return true;
}
static void napLich() {
  soKhung = 0;
  File f = theSanSang ? SD.open("/lich_ghi.txt") : File();
  if (f) {
    while (f.available() && soKhung < 16) {
      String d = f.readStringUntil('\n'); d.trim();
      if (!d.length() || d[0] == '#') continue;
      if (docDong(d, lich[soKhung])) soKhung++;
    }
    f.close();
    Serial.printf("Lich ghi: doc tu /lich_ghi.txt (%d khung)\n", soKhung);
  }
  if (soKhung == 0) {
    soKhung = sizeof(LICH_MAC_DINH) / sizeof(LICH_MAC_DINH[0]);
    memcpy(lich, LICH_MAC_DINH, sizeof(LICH_MAC_DINH));
    Serial.printf("Lich ghi: mac dinh trong firmware (%d khung)\n", soKhung);
  }
  for (int i = 0; i < soKhung; i++)
    Serial.printf("  %04d-%02d-%02d %02d:%02d-%02d:%02d %s\n", lich[i].nam, lich[i].thang, lich[i].ngay,
                  lich[i].gioBd, lich[i].phutBd, lich[i].gioKt, lich[i].phutKt, lich[i].nhan);
}
static time_t moc(const KhungGhi &k, int gio, int phut) {
  struct tm g = {}; g.tm_year = k.nam - 1900; g.tm_mon = k.thang - 1; g.tm_mday = k.ngay;
  g.tm_hour = gio; g.tm_min = phut; g.tm_isdst = -1; return mktime(&g);
}
static int khungHienTai(time_t now) {           // chỉ số khung đang diễn ra, -1 nếu không
  for (int i = 0; i < soKhung; i++) {
    time_t a = moc(lich[i], lich[i].gioBd, lich[i].phutBd), b = moc(lich[i], lich[i].gioKt, lich[i].phutKt);
    if (b <= a) b += 86400;
    if (now >= a && now < b) return i;
  }
  return -1;
}
static String khungKeTiep(time_t now) {
  time_t tot = 0; int chon = -1;
  for (int i = 0; i < soKhung; i++) {
    time_t a = moc(lich[i], lich[i].gioBd, lich[i].phutBd);
    if (a > now && (chon < 0 || a < tot)) { tot = a; chon = i; }
  }
  if (chon < 0) return "không còn";
  char b[48]; snprintf(b, sizeof b, "%02d/%02d %02d:%02d–%02d:%02d (%s)", lich[chon].ngay, lich[chon].thang,
                       lich[chon].gioBd, lich[chon].phutBd, lich[chon].gioKt, lich[chon].phutKt, lich[chon].nhan);
  return String(b);
}

// ======================================================================== micro (lõi 0)
static bool khoiDongMic() {
  i2s_chan_config_t cc = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
  cc.dma_desc_num = 8; cc.dma_frame_num = 512;
  if (i2s_new_channel(&cc, NULL, &rx) != ESP_OK) return false;
  i2s_std_config_t cfg = {
    .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(TAN_SO),
    .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_MONO),
    .gpio_cfg = {
      .mclk = I2S_GPIO_UNUSED, .bclk = (gpio_num_t)PIN_MIC_SCK, .ws = (gpio_num_t)PIN_MIC_WS,
      .dout = I2S_GPIO_UNUSED, .din = (gpio_num_t)PIN_MIC_SD,
      .invert_flags = { .mclk_inv = false, .bclk_inv = false, .ws_inv = false },
    },
  };
  cfg.slot_cfg.slot_mask = MIC_SLOT;
  return i2s_channel_init_std_mode(rx, &cfg) == ESP_OK && i2s_channel_enable(rx) == ESP_OK;
}
static void tacVuDoc(void *) {
  static int32_t raw[MAU_KHOI];
  for (;;) {
    size_t got = 0;
    if (i2s_channel_read(rx, raw, sizeof raw, &got, 1000) != ESP_OK || got == 0) continue;
    int n = got / 4;
    uint64_t viTri = docTongMau();
    bool day = choPhepDay;
    int idx = -1;
    if (day && xQueueReceive(hangRong, &idx, 0) != pdTRUE) idx = -1;
    if (day && idx < 0) thieuChoXuLy += n;         // hết khối rỗng: thẻ ghi quá chậm
    for (int i = 0; i < n; i++) {
      int64_t v = ((int64_t)raw[i] * HE_SO_KHUECH_DAI) >> 16;
      if (v > 32767) { v = 32767; if (day) catDinh++; }
      if (v < -32768) { v = -32768; if (day) catDinh++; }
      if (idx >= 0) khoi[idx].mau[i] = (int16_t)v;
    }
    if (idx >= 0) {
      for (int i = n; i < MAU_KHOI; i++) khoi[idx].mau[i] = 0;   // không xảy ra: luôn đọc đủ 512 mẫu
      khoi[idx].viTri = viTri; khoi[idx].thieuTruoc = thieuChoXuLy; thieuChoXuLy = 0;
      xQueueSend(hangDay, &idx, portMAX_DELAY);
    }
    portENTER_CRITICAL(&khoaMau); tongMau += n; portEXIT_CRITICAL(&khoaMau);
  }
}

// ======================================================================== thẻ nhớ và tệp WAV
static bool moThe() {
  SD.end(); spiThe.end();
  spiThe.begin(PIN_SD_SCK, PIN_SD_MISO, PIN_SD_MOSI, PIN_SD_CS);
  const uint32_t tocDo[3] = {8000000, 4000000, 1000000};
  for (int i = 0; i < 3; i++) {
    if (SD.begin(PIN_SD_CS, spiThe, tocDo[i])) { Serial.printf("THE: mo o %lu MHz\n", tocDo[i] / 1000000); return true; }
    SD.end(); delay(200);
  }
  Serial.println("LOI: khong mo duoc the nho");
  return false;
}
static void viet32(File &f, uint32_t v) { f.write((uint8_t *)&v, 4); }
static void viet16(File &f, uint16_t v) { f.write((uint8_t *)&v, 2); }
static void dauWav(File &f, uint32_t soByte) {
  f.write((const uint8_t *)"RIFF", 4); viet32(f, 36 + soByte);
  f.write((const uint8_t *)"WAVEfmt ", 8); viet32(f, 16); viet16(f, 1); viet16(f, 1);
  viet32(f, TAN_SO); viet32(f, TAN_SO * 2); viet16(f, 2); viet16(f, 16);
  f.write((const uint8_t *)"data", 4); viet32(f, soByte);
}
static void capNhatDau() {
  uint32_t vt = 44 + mauTrongTep * 2;
  tep.seek(0); dauWav(tep, mauTrongTep * 2); tep.seek(vt); tep.flush();
}
static bool moTep(uint64_t viTriMauDau) {
  double t = mauSangMs(viTriMauDau);
  tenTep = String("/") + (cheDo == GHI_THU ? "THU" : TEN_THIET_BI) + dinhDang(t, "_%Y%m%d_%H%M%S") + ".wav";
  tep = SD.open(tenTep, FILE_WRITE);
  if (!tep) { Serial.printf("LOI: khong tao duoc %s\n", tenTep.c_str()); return false; }
  dauWav(tep, 0);
  viTriDauTep = viTriMauDau; mauTrongTep = 0; thieuTrongTep = 0; catDinhDauTep = catDinh;
  lanCapNhatDau = lanFlush = millis();
  Serial.printf("Ghi tep %s (mau dau: %s)\n", tenTep.c_str(), dinhDang(t, "%H:%M:%S").c_str());
  return true;
}
static void dongTep() {
  if (!tep) return;
  capNhatDau(); tep.close();
  double t0 = mauSangMs(viTriDauTep);
  char b[220];
  snprintf(b, sizeof b, "%s,%s,%s,%.3f,%s,%lu,%.1f,%lu,%lu", tenTep.substring(1).c_str(), nhanPhien.c_str(),
           TEN_THIET_BI, t0 / 1000.0, dinhDang(t0, "%Y-%m-%d %H:%M:%S").c_str(), (unsigned long)mauTrongTep,
           mauTrongTep / (double)TAN_SO, (unsigned long)thieuTrongTep, (unsigned long)(catDinh - catDinhDauTep));
  ghiDong("/TC-02_ghi.csv", "tep,phien,thiet_bi,t_mau_dau_epoch,t_mau_dau_gio_vn,so_mau,thoi_luong_s,mau_thieu_chen_0,"
          "mau_cham_dinh", String(b));
  Serial.printf("Dong tep %s: %.1f s, thieu %lu mau, cham dinh %lu mau\n", tenTep.c_str(), mauTrongTep / (double)TAN_SO,
                (unsigned long)thieuTrongTep, (unsigned long)(catDinh - catDinhDauTep));
  tenTep = "";
}
static void ghiKhoi(const Khoi &k) {
  static const int16_t KHONG[MAU_KHOI] = {0};
  if (!tep && !moTep(k.viTri - k.thieuTruoc)) return;
  uint32_t thieu = k.thieuTruoc;
  if (thieu) {                                   // giữ đúng thời gian: chèn 0 cho phần bị thiếu
    char b[120];
    double t = mauSangMs(k.viTri - thieu);
    snprintf(b, sizeof b, "%s,%.3f,%s,%lu", tenTep.substring(1).c_str(), t / 1000.0,
             dinhDang(t, "%Y-%m-%d %H:%M:%S").c_str(), (unsigned long)thieu);
    ghiDong("/TC-02_khoang_trong.csv", "tep,t_epoch,t_gio_vn,so_mau_chen_0", String(b));
    thieuTrongTep += thieu;
    while (thieu) { uint32_t m = min(thieu, (uint32_t)MAU_KHOI); tep.write((const uint8_t *)KHONG, m * 2); thieu -= m; mauTrongTep += m; }
  }
  uint32_t t0 = millis();
  size_t da = tep.write((const uint8_t *)k.mau, MAU_KHOI * 2);
  uint32_t dt = millis() - t0;
  if (dt > ghiChamNhatMs) ghiChamNhatMs = dt;
  if (da != MAU_KHOI * 2) Serial.println("LOI: ghi the thieu byte");
  mauTrongTep += MAU_KHOI;
  if (millis() - lanFlush > 10000) { tep.flush(); lanFlush = millis(); }
  if (millis() - lanCapNhatDau > 60000) { capNhatDau(); lanCapNhatDau = millis(); }
  if (mauTrongTep >= MAU_MOI_TEP) dongTep();     // tệp kế tiếp mở ở khối sau
}
static void xuLyHangDay() {
  int idx;
  while (xQueueReceive(hangDay, &idx, 0) == pdTRUE) {
    if (cheDo != NGHI || tep) ghiKhoi(khoi[idx]);
    xQueueSend(hangRong, &idx, 0);
  }
}

// ======================================================================== Wi-Fi và trang đồng bộ giờ
static const char TRANG[] PROGMEM = R"HTML(<!doctype html><html lang="vi"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>TussiCount TC-02</title>
<style>body{font-family:system-ui,sans-serif;max-width:480px;margin:0 auto;padding:16px;color:#121513}
h1{font-size:20px;margin:0 0 4px}.o{border:1px solid #ccc;border-radius:10px;padding:12px;margin:12px 0}
b{font-family:ui-monospace,monospace}button{width:100%;padding:14px;font-size:17px;border:0;border-radius:10px;
background:#0F766E;color:#fff;margin-top:8px}button.p{background:#555}#kq{margin-top:10px;font-weight:600}</style>
<h1>TussiCount · TC-02 (ghi kiểm định)</h1><div>Trong lúc ghi, mạch tắt Wi-Fi nên trang này mất kết nối: bình thường.</div>
<div class="o">Giờ thiết bị: <b id="g">…</b><br>Giờ điện thoại: <b id="dt">…</b><br>Đồng bộ gần nhất: <b id="ld">…</b>
<br>Độ lệch lần đó: <b id="lc">…</b><br>Thẻ nhớ: <b id="th">…</b> · trống <b id="tr">…</b><br>Khung ghi kế tiếp: <b id="kt">…</b></div>
<button id="nut">Đồng bộ giờ</button><button class="p" id="thu">Ghi thử 10 phút (trên bàn)</button><div id="kq"></div>
<script>
const $=i=>document.getElementById(i),f=t=>new Date(t).toLocaleString('vi-VN',{hour12:false});
async function tt(){try{const r=await(await fetch('/trang_thai')).json();
$('g').textContent=r.co_gio?f(r.gio):'chưa có giờ';$('dt').textContent=f(Date.now());
$('ld').textContent=r.lan_cuoi?f(r.lan_cuoi*1000):'chưa';$('lc').textContent=r.lan_cuoi?r.lech+' ms':'—';
$('th').textContent=r.the?'OK':'LỖI';$('tr').textContent=r.trong_mb+' MB';$('kt').textContent=r.ke_tiep}catch(e){}}
$('nut').onclick=async()=>{$('nut').disabled=true;$('kq').textContent='Đang đo…';let best=null;
for(let i=0;i<8;i++){const t0=Date.now();const td=+(await(await fetch('/gio?'+i)).text());const t1=Date.now();
const rtt=t1-t0;if(!best||rtt<best.rtt)best={rtt,lech:Math.round((t0+t1)/2-td)}}
const q=await fetch('/dat_gio?lech='+best.lech+'&rtt='+best.rtt),r=await q.text();
$('kq').textContent=(q.ok?'Đã đồng bộ. ':'LỖI: ')+r+' · khứ hồi '+best.rtt+' ms';$('nut').disabled=false;tt()};
$('thu').onclick=async()=>{const q=await fetch('/ghi_thu'),r=await q.text();$('kq').textContent=(q.ok?'':'LỖI: ')+r};
tt();setInterval(tt,2000);
</script></html>)HTML";

static void khoiDongTrang() {
  may.on("/", []() { may.send_P(200, "text/html; charset=utf-8", TRANG); });
  may.on("/gio", []() { char b[24]; snprintf(b, sizeof b, "%.0f", gioThietBiMs()); may.send(200, "text/plain", b); });
  may.on("/dat_gio", []() {
    double lech = strtod(may.arg("lech").c_str(), nullptr); int rtt = may.arg("rtt").toInt();
    double thuc = gioThietBiMs() + lech;
    if (thuc < 1.7e12 || rtt < 0 || rtt > 2000) { may.send(400, "text/plain", "gia tri khong hop le"); return; }
    struct timeval tv = {(time_t)(thuc / 1000.0), (suseconds_t)(fmod(thuc, 1000.0) * 1000)};
    settimeofday(&tv, nullptr);
    neoGio(thuc, rtt);
    may.send(200, "text/plain; charset=utf-8", String("Lech do duoc: ") + lechLanCuoi + " ms");
  });
  may.on("/ghi_thu", []() {
    if (!coMoc) { may.send(400, "text/plain; charset=utf-8", "chưa đồng bộ giờ"); return; }
    if (cheDo != NGHI) { may.send(400, "text/plain; charset=utf-8", "đang ghi"); return; }
    may.send(200, "text/plain; charset=utf-8", "Bắt đầu ghi thử 10 phút; Wi-Fi tắt sau 3 giây.");
    delay(3000);
    ketThucThuMs = millis() + PHUT_GHI_THU * 60000UL; cheDo = GHI_THU;
  });
  may.on("/trang_thai", []() {
    uint64_t trong = theSanSang ? (SD.totalBytes() - SD.usedBytes()) / (1024 * 1024) : 0;
    char b[300];
    snprintf(b, sizeof b, "{\"co_gio\":%s,\"gio\":%.0f,\"lan_cuoi\":%ld,\"lech\":%d,\"the\":%s,\"trong_mb\":%llu,"
             "\"ke_tiep\":\"%s\"}", coMoc ? "true" : "false", gioThietBiMs(), (long)lanDongBoCuoi, lechLanCuoi,
             theSanSang ? "true" : "false", (unsigned long long)trong,
             coMoc ? khungKeTiep((time_t)(gioThietBiMs() / 1000)).c_str() : "cần đồng bộ giờ");
    may.send(200, "application/json; charset=utf-8", b);
  });
  may.begin();
}
static void batWifi() {
  if (wifiDangBat) return;
  WiFi.mode(WIFI_AP); WiFi.softAP(AP_TEN, AP_MAT_KHAU); WiFi.setTxPower(WIFI_POWER_2dBm);
  wifiDangBat = true;
  Serial.printf("Wi-Fi BAT: \"%s\" (mat khau %s) · http://192.168.4.1\n", AP_TEN, AP_MAT_KHAU);
}
static void tatWifi() {
  if (!wifiDangBat) return;
  WiFi.softAPdisconnect(true); WiFi.mode(WIFI_OFF); wifiDangBat = false;
  Serial.println("Wi-Fi TAT");
}

// ======================================================================== điều khiển
static void batDauGhi(CheDo c, const char *nhan) {
  tatWifi();
  nhanPhien = nhan; cheDo = c; ghiChamNhatMs = 0;
  catDinh = 0; thieuChoXuLy = 0;
  choPhepDay = true;
  digitalWrite(PIN_LED, HIGH);
  Serial.printf("=== BAT DAU GHI (%s) ===\n", nhan);
}
static void dungGhi() {
  choPhepDay = false;
  delay(100);                                    // chờ tác vụ đọc đẩy nốt khối cuối
  xuLyHangDay();
  dongTep();
  cheDo = NGHI;
  digitalWrite(PIN_LED, LOW);
  Serial.printf("=== DUNG GHI · ghi the cham nhat %lu ms ===\n", (unsigned long)ghiChamNhatMs);
  batWifi();
}
static void inTrangThai() {
  Serial.printf("[%s] gio %s · che do %s · tep %s · the %s · ghi cham nhat %lu ms\n", TEN_THIET_BI,
                coMoc ? dinhDang(gioThietBiMs(), "%Y-%m-%d %H:%M:%S").c_str() : "chua co",
                cheDo == NGHI ? "nghi" : (cheDo == GHI_THU ? "ghi thu" : "ghi theo lich"),
                tenTep.length() ? tenTep.c_str() : "-", theSanSang ? "OK" : "LOI", (unsigned long)ghiChamNhatMs);
  if (coMoc) Serial.printf("  khung ke tiep: %s\n", khungKeTiep((time_t)(gioThietBiMs() / 1000)).c_str());
}

void setup() {
  Serial.begin(115200);
  delay(1500);
  pinMode(PIN_LED, OUTPUT); digitalWrite(PIN_LED, LOW);
  setenv("TZ", "ICT-7", 1); tzset();
  Serial.printf("\n##### TussiCount %s · firmware %s · ghi WAV 16 kHz 16 bit, khuech dai x%d\n", TEN_THIET_BI,
                PHIEN_BAN_FW, HE_SO_KHUECH_DAI);
  khoi = (Khoi *)malloc(sizeof(Khoi) * SO_KHOI);
  hangRong = xQueueCreate(SO_KHOI, sizeof(int));
  hangDay = xQueueCreate(SO_KHOI, sizeof(int));
  if (!khoi || !hangRong || !hangDay) { Serial.println("LOI: thieu bo nho"); while (true) delay(1000); }
  for (int i = 0; i < SO_KHOI; i++) xQueueSend(hangRong, &i, 0);
  theSanSang = moThe();
  napLich();
  if (!khoiDongMic()) { Serial.println("LOI: khong khoi dong duoc micro"); while (true) { digitalWrite(PIN_LED, !digitalRead(PIN_LED)); delay(100); } }
  xTaskCreatePinnedToCore(tacVuDoc, "doc", 4096, nullptr, 10, nullptr, 0);
  khoiDongTrang();
  batWifi();
  Serial.println("Chua co gio: ket noi dien thoai vao Wi-Fi \"TussiCount-TC-02\", mo http://192.168.4.1, bam Dong bo gio");
  Serial.println("Serial: t = ghi thu 10 phut, x = dung ghi thu, s = trang thai");
}

void loop() {
  if (wifiDangBat) may.handleClient();
  if (cheDo != NGHI) xuLyHangDay();

  static uint32_t lan = 0;
  if (millis() - lan >= 1000) {
    lan = millis();
    if (!coMoc) {
      static uint32_t nhac = 0;
      if (millis() - nhac > 30000) { nhac = millis(); Serial.println("Chua co gio: dong bo bang dien thoai (Wi-Fi TussiCount-TC-02)"); }
      digitalWrite(PIN_LED, !digitalRead(PIN_LED));   // LED nháy chậm: chưa có giờ, chưa ghi được
    } else {
      time_t now = (time_t)(gioThietBiMs() / 1000);
      int k = khungHienTai(now);
      if (cheDo == NGHI && k >= 0) {
        if (theSanSang) batDauGhi(GHI_LICH, lich[k].nhan);
        else { Serial.println("LOI: dang trong khung ghi nhung the nho loi - KHONG GHI DUOC"); digitalWrite(PIN_LED, !digitalRead(PIN_LED)); }
      }
      else if (cheDo == GHI_LICH && k < 0) dungGhi();
      else if (cheDo == GHI_THU && choPhepDay && (int32_t)(millis() - ketThucThuMs) >= 0) dungGhi();
      if (cheDo == NGHI && k < 0) digitalWrite(PIN_LED, LOW);
    }
  }
  if (cheDo == GHI_THU && !choPhepDay) {          // bắt đầu ghi thử (từ trang web)
    nhanPhien = "ghi_thu"; batDauGhi(GHI_THU, "ghi_thu");
  }

  if (Serial.available()) {
    char c = Serial.read();
    if ((c == 't' || c == 'T') && cheDo == NGHI) {
      if (!coMoc) Serial.println("Chua co gio: dong bo truoc khi ghi thu");
      else { ketThucThuMs = millis() + PHUT_GHI_THU * 60000UL; batDauGhi(GHI_THU, "ghi_thu"); }
    } else if ((c == 'x' || c == 'X') && cheDo == GHI_THU) dungGhi();
    else if (c == 's' || c == 'S') inTrangThai();
  }
  delay(cheDo == NGHI ? 5 : 1);
}
