// Chạy mô hình TussiCount (thư viện C++ xuất từ Edge Impulse) trên máy tính.
//
// Cùng mã xử lý tín hiệu (MFE) và cùng mạng int8 với firmware trên ESP32-S3, nên điểm của mỗi cửa sổ
// trên máy tính và trên thiết bị phải gần nhau (phép thử đồng nhất, Protocol 7.6).
//
// Hai chế độ:
//   chay_mo_hinh dai  <vao.wav> <ra.csv> [buoc_mau]
//       Trượt cửa sổ 1 s (16.000 mẫu), bước mặc định 0,5 s (8.000 mẫu) trên một tệp WAV dài.
//       Mỗi dòng: cua_so, t_bat_dau_s, p_cough, ms_xu_ly
//   chay_mo_hinh ngan <danh_sach.txt> <ra.csv>
//       Mỗi dòng của danh_sach.txt là đường dẫn một tệp WAV ngắn; chấm đúng 1 cửa sổ (16.000 mẫu đầu,
//       thiếu thì đệm 0 như cài đặt zero-pad của impulse). Mỗi dòng ra: tep, p_cough
// Yêu cầu WAV: PCM 16 bit, một kênh, 16 kHz. Mẫu được đưa vào mô hình dưới dạng số thực bằng giá trị int16
// (như cách Edge Impulse xử lý âm thanh), không chia cho 32.768.
// Không ghi âm thanh ra đâu cả; chỉ ghi điểm.

#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <string>
#include <vector>

#include "edge-impulse-sdk/classifier/ei_run_classifier.h"

static const float *g_buf = nullptr;

static int lay_du_lieu(size_t offset, size_t length, float *out) {
    memcpy(out, g_buf + offset, length * sizeof(float));
    return 0;
}

static bool doc_wav(const std::string &path, std::vector<int16_t> &mau, std::string &loi) {
    std::ifstream f(path, std::ios::binary);
    if (!f) { loi = "khong mo duoc tep"; return false; }
    char id[4]; uint32_t sz;
    f.read(id, 4); f.read(reinterpret_cast<char *>(&sz), 4);
    if (strncmp(id, "RIFF", 4) != 0) { loi = "khong phai RIFF"; return false; }
    f.read(id, 4);
    if (strncmp(id, "WAVE", 4) != 0) { loi = "khong phai WAVE"; return false; }
    bool co_fmt = false;
    while (f.read(id, 4)) {
        f.read(reinterpret_cast<char *>(&sz), 4);
        if (strncmp(id, "fmt ", 4) == 0) {
            std::vector<char> b(sz);
            f.read(b.data(), sz);
            uint16_t fmt, ch, bits; uint32_t sr;
            memcpy(&fmt, &b[0], 2); memcpy(&ch, &b[2], 2); memcpy(&sr, &b[4], 4); memcpy(&bits, &b[14], 2);
            if (fmt == 0xFFFE && sz >= 26) memcpy(&fmt, &b[24], 2);  // WAVE_FORMAT_EXTENSIBLE
            if (fmt != 1 || ch != 1 || bits != 16 || sr != EI_CLASSIFIER_FREQUENCY) {
                char m[128];
                snprintf(m, sizeof m, "can PCM 16 bit, 1 kenh, %d Hz (tep: fmt %u, %u kenh, %u bit, %u Hz)",
                         EI_CLASSIFIER_FREQUENCY, fmt, ch, bits, sr);
                loi = m; return false;
            }
            co_fmt = true;
        } else if (strncmp(id, "data", 4) == 0) {
            if (!co_fmt) { loi = "thieu khoi fmt"; return false; }
            mau.resize(sz / 2);
            f.read(reinterpret_cast<char *>(mau.data()), (sz / 2) * 2);
            return true;
        } else {
            f.seekg(sz + (sz & 1), std::ios::cur);
        }
    }
    loi = "khong thay khoi data";
    return false;
}

static int chi_so_cough() {
    for (size_t i = 0; i < EI_CLASSIFIER_LABEL_COUNT; i++) {
        if (strcmp(ei_classifier_inferencing_categories[i], "cough") == 0) return (int)i;
    }
    return -1;
}

static bool cham(const float *buf, float &p, double &ms) {
    g_buf = buf;
    signal_t s;
    s.total_length = EI_CLASSIFIER_RAW_SAMPLE_COUNT;
    s.get_data = &lay_du_lieu;
    ei_impulse_result_t r = {0};
    auto t0 = std::chrono::steady_clock::now();
    EI_IMPULSE_ERROR e = run_classifier(&s, &r, false);
    ms = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - t0).count();
    if (e != EI_IMPULSE_OK) return false;
    p = r.classification[chi_so_cough()].value;
    return true;
}

int main(int argc, char **argv) {
    if (argc < 4) {
        fprintf(stderr, "Cach dung:\n  %s dai <vao.wav> <ra.csv> [buoc_mau=8000]\n  %s ngan <danh_sach.txt> <ra.csv>\n",
                argv[0], argv[0]);
        return 2;
    }
    if (chi_so_cough() < 0) { fprintf(stderr, "Mo hinh khong co nhan 'cough'\n"); return 2; }
    const std::string che_do = argv[1];
    const int N = EI_CLASSIFIER_RAW_SAMPLE_COUNT;
    std::vector<float> win(N);
    FILE *out = fopen(argv[3], "w");
    if (!out) { fprintf(stderr, "Khong ghi duoc %s\n", argv[3]); return 2; }
    fprintf(stderr, "Mo hinh: du an %d, phien ban trien khai %d, %d nhan\n", EI_CLASSIFIER_PROJECT_ID,
            EI_CLASSIFIER_PROJECT_DEPLOY_VERSION, EI_CLASSIFIER_LABEL_COUNT);

    if (che_do == "dai") {
        int buoc = argc >= 5 ? atoi(argv[4]) : N / 2;
        std::vector<int16_t> mau; std::string loi;
        if (!doc_wav(argv[2], mau, loi)) { fprintf(stderr, "%s: %s\n", argv[2], loi.c_str()); return 1; }
        fprintf(out, "cua_so,t_bat_dau_s,p_cough,ms_xu_ly\n");
        long so = 0; double ms_max = 0, ms_tong = 0;
        for (size_t bd = 0; bd + N <= mau.size(); bd += buoc, so++) {
            for (int i = 0; i < N; i++) win[i] = (float)mau[bd + i];
            float p; double ms;
            if (!cham(win.data(), p, ms)) { fprintf(stderr, "Loi chay mo hinh o cua so %ld\n", so); return 1; }
            fprintf(out, "%ld,%.4f,%.6f,%.3f\n", so, (double)bd / EI_CLASSIFIER_FREQUENCY, p, ms);
            ms_tong += ms; if (ms > ms_max) ms_max = ms;
        }
        fprintf(stderr, "Xong: %ld cua so (%.1f phut am thanh); xu ly trung binh %.2f ms, lon nhat %.2f ms\n", so,
                mau.size() / (double)EI_CLASSIFIER_FREQUENCY / 60.0, so ? ms_tong / so : 0.0, ms_max);
    } else if (che_do == "ngan") {
        std::ifstream ds(argv[2]);
        if (!ds) { fprintf(stderr, "Khong mo duoc %s\n", argv[2]); return 2; }
        fprintf(out, "tep,p_cough\n");
        std::string duong; long so = 0, hong = 0;
        while (std::getline(ds, duong)) {
            if (duong.empty()) continue;
            std::vector<int16_t> mau; std::string loi;
            if (!doc_wav(duong, mau, loi)) { fprintf(stderr, "%s: %s\n", duong.c_str(), loi.c_str()); hong++; continue; }
            for (int i = 0; i < N; i++) win[i] = i < (int)mau.size() ? (float)mau[i] : 0.0f;
            float p; double ms;
            if (!cham(win.data(), p, ms)) { hong++; continue; }
            fprintf(out, "%s,%.6f\n", duong.c_str(), p);
            so++;
        }
        fprintf(stderr, "Xong: %ld tep, %ld tep loi\n", so, hong);
        if (hong) return 1;
    } else {
        fprintf(stderr, "Che do khong hop le: %s\n", che_do.c_str());
        return 2;
    }
    fclose(out);
    return 0;
}
