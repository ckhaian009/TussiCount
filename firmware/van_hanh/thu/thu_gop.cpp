// Thử: logic gộp sự kiện trong TC01_Van_hanh.ino (nhanDiem/dongNhom) so với vector của gop_su_kien.py
#include <cstdio>
#include <cmath>
#include <cstdint>
#include <vector>
struct SK { double t, dai; uint32_t so; float p; };
static float NGUONG; static int K_CUA_SO; static float G_NGHI_S; static uint32_t M_MAX;
static std::vector<SK> ra;
struct Nhom { bool mo = false; uint64_t iDau, iCuoi, iMax; uint32_t soVuot; float pMax; double tMaxMs; };
static Nhom nh;
static void dongNhom() {
  if (!nh.mo) return;
  nh.mo = false;
  if ((int)nh.soVuot < K_CUA_SO) return;
  ra.push_back({(nh.tMaxMs + 500.0) / 1000.0, (double)((float)(nh.iCuoi - nh.iDau) * 0.5f + 1.0f), nh.soVuot, nh.pMax});
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
int main() {
  int n; int loi = 0, ca = 0;
  while (scanf("%d", &n) == 1) {
    ca++;
    std::vector<float> p(n); for (auto &x : p) scanf("%f", &x);
    int m; scanf("%f %d %f %d", &NGUONG, &K_CUA_SO, &G_NGHI_S, &m);
    M_MAX = (uint32_t)lroundf(G_NGHI_S / 0.5f);
    std::vector<SK> mong(m);
    for (auto &e : mong) scanf("%lf %lf %u %f", &e.t, &e.dai, &e.so, &e.p);
    ra.clear(); nh = Nhom();
    for (int i = 0; i < n; i++) nhanDiem(i, p[i], i * 500.0);
    dongNhom();
    bool ok = ra.size() == mong.size();
    for (size_t j = 0; ok && j < ra.size(); j++)
      ok = fabs(ra[j].t - mong[j].t) < 1e-6 && fabs(ra[j].dai - mong[j].dai) < 1e-6 && ra[j].so == mong[j].so && fabsf(ra[j].p - mong[j].p) < 1e-6;
    if (!ok) { loi++; printf("SAI tinh huong %d\n", ca); }
  }
  printf("%d tinh huong, %d sai -> %s\n", ca, loi, loi ? "KHONG DAT" : "DAT");
  return loi != 0;
}
