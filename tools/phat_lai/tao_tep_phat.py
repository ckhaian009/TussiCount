"""Tạo các tệp âm thanh cho trình phát thí nghiệm (việc t20, Protocol 7.1, 7.5, 16.9).

Đầu vào: data/coswara/doan_ho/ (đoạn ho đã cắt bằng tools/chuan_bi_phat_lai.py, đỉnh −1 dBFS),
         results/lich_phat_lai.csv (tools/phat_lai/lap_lich_phat.py).
Đầu ra (data/phat_lai/tep/, không đưa lên GitHub vì là âm thanh Coswara):
  <stt>_<hệ số>dB.wav            mỗi tiếng ho trong lịch, đã nhân hệ số khuếch đại số (0 / −10 / −20 dB),
                                  48 kHz, PCM 16 bit, một kênh (bản ghi 44,1 / 16 / 192 kHz được đổi về 48 kHz)
  bip.wav                         tiếng bíp đồng bộ 1 kHz, 0,2 s
  nhieu_hong_30s_<g>dB.wav        nhiễu hồng 30 s (20 Hz – 20 kHz), g = 0, −10, −20, −30, −40 dB, dùng cho
                                  đo suy hao qua cửa (7.1, 16.9) và hiệu chuẩn mức âm 5 mức (7.5)
Bảng: results/phat_lai_muc_so.csv — mức đỉnh trọng số A, thời gian F (125 ms) của từng tệp tính trên tệp số
(dB so với toàn thang). Dùng cho Protocol 7.1: mức tại micro của một tiếng ho = mức đo của tệp hiệu chuẩn trong
khối + (mức số của tiếng ho − mức số của tệp hiệu chuẩn); hệ số khuếch đại đã nằm sẵn trong mức số của tệp.
Chạy từ gốc kho: python3 tools/phat_lai/tao_tep_phat.py
"""
import csv
import hashlib
import os
import sys

import numpy as np
import soundfile as sf
from scipy import signal

SR = 48000
SEED = 2026
SRC = "data/coswara/doan_ho"
OUT = "data/phat_lai/tep"
LICH = "results/lich_phat_lai.csv"
MUC = "results/phat_lai_muc_so.csv"


def a_weight_sos(fs):
    f1, f2, f3, f4 = 20.598997, 107.65265, 737.86223, 12194.217
    z = [0, 0, 0, 0]
    p = [-2 * np.pi * f1] * 2 + [-2 * np.pi * f2, -2 * np.pi * f3] + [-2 * np.pi * f4] * 2
    zd, pd, kd = signal.bilinear_zpk(z, p, 1.0, fs)
    sos = signal.zpk2sos(zd, pd, kd)
    w, h = signal.sosfreqz(sos, worN=[1000.0], fs=fs)
    sos[0, :3] /= abs(h[0])
    return sos


# Bộ lọc A thiết kế ở 192 kHz (tín hiệu được nâng tần số ×4 trước khi lọc) để sai lệch do biến đổi song tuyến
# gần tần số Nyquist không đáng kể (ở 48 kHz trực tiếp, sai lệch tại 10 kHz là −1,2 dB).
OS = 4
SOS_A = a_weight_sos(SR * OS)


def lafmax_db(x, fs=SR, tau=0.125):
    x = signal.resample_poly(x, OS, 1)
    fs = fs * OS
    y = signal.sosfilt(SOS_A, x)
    a = 1 - np.exp(-1 / (fs * tau))
    e = signal.lfilter([a], [1, -(1 - a)], y ** 2)
    return float(10 * np.log10(np.max(e) + 1e-20))


def doi_tan_so(x, sr):
    """Đổi về 48 kHz; giữ nguyên mức đỉnh của đoạn gốc (đổi tần số có thể làm đỉnh vượt nhẹ do hiện tượng Gibbs)."""
    if sr == SR:
        return x
    g = np.gcd(SR, sr)
    y = signal.resample_poly(x, SR // g, sr // g)
    return y * (np.max(np.abs(x)) / np.max(np.abs(y)))


def ghi(path, x):
    if np.max(np.abs(x)) > 1.0:
        raise ValueError(f"cat dinh: {path}")
    sf.write(path, x, SR, subtype="PCM_16")


def nhieu_hong(n, seed):
    rng = np.random.default_rng(seed)
    X = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    shape = np.zeros_like(f)
    m = (f >= 20) & (f <= 20000)
    shape[m] = 1 / np.sqrt(f[m])
    x = np.fft.irfft(X * shape, n)
    return x / np.sqrt(np.mean(x ** 2))


def main():
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(root)
    os.makedirs(OUT, exist_ok=True)
    lich = list(csv.DictReader(open(LICH, encoding="utf-8")))
    can = sorted({(r["stt"], r["file"], int(r["he_so_db"])) for r in lich if r["stt"]}, key=lambda t: (int(t[0]), t[2]))
    rows = []
    for stt, f, g in can:
        x, sr = sf.read(os.path.join(SRC, f), dtype="float64")
        x = doi_tan_so(x, sr) * 10 ** (g / 20)
        ten = f"{int(stt):04d}_{g:+03d}dB.wav"
        ghi(os.path.join(OUT, ten), x)
        rows.append({"tep": ten, "stt": stt, "file_goc": f, "tan_so_goc": sr, "he_so_db": g,
                     "dai_s": round(len(x) / SR, 3), "dinh_dbfs": round(20 * np.log10(np.max(np.abs(x))), 2),
                     "lafmax_so_db": round(lafmax_db(x), 2)})
    # bíp đồng bộ
    t = np.arange(int(0.2 * SR)) / SR
    bip = 0.5 * np.sin(2 * np.pi * 1000 * t)
    r = int(0.005 * SR)
    bip[:r] *= np.linspace(0, 1, r)
    bip[-r:] *= np.linspace(1, 0, r)
    ghi(os.path.join(OUT, "bip.wav"), bip)
    rows.append({"tep": "bip.wav", "stt": "", "file_goc": "", "tan_so_goc": SR, "he_so_db": "", "dai_s": 0.2,
                 "dinh_dbfs": round(20 * np.log10(0.5), 2), "lafmax_so_db": round(lafmax_db(bip), 2)})
    # nhiễu hồng 30 s, RMS −20 dBFS ở mức 0 dB
    nh = nhieu_hong(30 * SR, SEED) * 10 ** (-20 / 20)
    r = int(0.05 * SR)
    nh[:r] *= np.linspace(0, 1, r)
    nh[-r:] *= np.linspace(1, 0, r)
    for g in (0, -10, -20, -30, -40):
        y = nh * 10 ** (g / 20)
        ten = f"nhieu_hong_30s_{g:+03d}dB.wav"
        ghi(os.path.join(OUT, ten), y)
        rows.append({"tep": ten, "stt": "", "file_goc": "", "tan_so_goc": SR, "he_so_db": g, "dai_s": 30.0,
                     "dinh_dbfs": round(20 * np.log10(np.max(np.abs(y))), 2), "lafmax_so_db": round(lafmax_db(y), 2)})
    with open(MUC, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    h = hashlib.sha256()
    for ten in sorted(os.listdir(OUT)):
        h.update(ten.encode())
        h.update(open(os.path.join(OUT, ten), "rb").read())
    print(f"Da tao {len(rows)} tep trong {OUT}; SHA-256 ca thu muc: {h.hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
