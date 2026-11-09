"""Tạo tập kiểm tra độ bền: tiếng ho của tập testing trộn với nền ồn ở SNR 20, 10 và 0 dB.

Lý do: trong dữ liệu mở, tiếng ho COUGHVID thường nằm trên nền rất yên (71% đoạn có ≥5% mẫu bằng 0;
nền yên nhất thấp hơn đỉnh khoảng 61 dB), còn đoạn không ho (ESC-50, giọng nói) có nền ồn liên tục.
Mô hình có thể học “có sự kiện trên nền yên = ho”. Tập này đo độ nhạy khi tiếng ho có nền ồn như trong KTX.

Chỉ dùng dữ liệu đã thuộc tập testing (không rò rỉ sang huấn luyện):
  ho     500 đoạn cough testing, chọn ngẫu nhiên (seed 2026)
  nền    với mỗi đoạn ho, một đoạn noise testing chọn ngẫu nhiên: 50% ESC-50 (fold 5), 50% giọng nói
         Common Voice của người nói thuộc tập testing
  trộn   cùng một cặp (ho, nền) ở 3 mức SNR 20, 10, 0 dB (so sánh theo cặp); SNR tính theo RMS cả đoạn 1 s;
         sau khi trộn, chuẩn hoá đỉnh về mức ngẫu nhiên đều trong [−35; −3] dBFS như dữ liệu chính.
Đầu ra: data/ei_kiem_tra_ben/testing/cough/cough.tron_<khoa>_snr<k>.wav (1.500 tệp, nhãn cough)
        results/ei_kiem_tra_ben.csv
Chạy từ gốc kho: python3 tools/mo_hinh_nen/tao_tap_kiem_tra_ben.py
"""
import csv
import hashlib
import os
import random

import numpy as np
import soundfile as sf

SEED = 2026
N_HO = 500
SNRS = (20, 10, 0)
LEVEL_RANGE = (-35.0, -3.0)
OUT = "data/ei_kiem_tra_ben"


def rms(x):
    return float(np.sqrt(np.mean(x.astype(np.float64) ** 2)) + 1e-12)


def main():
    rows = [r for r in csv.DictReader(open("results/ei_du_lieu_mo_hinh_nen.csv", encoding="utf-8")) if r["split"] == "testing"]
    ho = sorted([r for r in rows if r["label"] == "cough"], key=lambda r: r["file"])
    esc = sorted([r for r in rows if r["source"] == "ESC-50"], key=lambda r: r["file"])
    cv = sorted([r for r in rows if r["source"] == "CommonVoice-vi"], key=lambda r: r["file"])
    rng = random.Random(SEED)
    chon = rng.sample(ho, N_HO)
    d = os.path.join(OUT, "testing", "cough"); os.makedirs(d, exist_ok=True)
    out = []
    for h in chon:
        nen = rng.choice(esc) if rng.random() < 0.5 else rng.choice(cv)
        x, sr = sf.read("data/ei_upload/" + h["file"], dtype="float64")
        n, _ = sf.read("data/ei_upload/" + nen["file"], dtype="float64")
        assert sr == 16000 and len(x) == len(n) == 16000
        khoa = h["file"].split(".")[1]
        for snr in SNRS:
            g = rms(x) / (rms(n) * 10 ** (snr / 20))
            m = x + g * n
            hh = int(hashlib.sha256(f"{khoa}|{snr}".encode()).hexdigest()[:8], 16)
            muc = random.Random(hh).uniform(*LEVEL_RANGE)
            m = m * (10 ** (muc / 20) / np.max(np.abs(m)))
            ten = f"cough.tron_{khoa}_snr{snr:02d}.wav"
            sf.write(os.path.join(d, ten), m, 16000, subtype="PCM_16")
            out.append({"file": "testing/cough/" + ten, "label": "cough", "snr_db": snr, "cough_file": h["file"],
                        "noise_file": nen["file"], "noise_source": nen["source"], "peak_dbfs": round(muc, 2),
                        "cough_group": h["group"]})
    with open("results/ei_kiem_tra_ben.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    print(f"Da tao {len(out)} tep trong {d}; nen ESC-50: {sum(o['noise_source']=='ESC-50' for o in out)//3}, giong noi: {sum(o['noise_source']!='ESC-50' for o in out)//3}")


if __name__ == "__main__":
    main()
