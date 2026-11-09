"""Khảo sát ngưỡng sàn nhiễu (noise floor) của khối MFE trước khi huấn luyện.

Dùng đúng mã MFE của Edge Impulse (kho edgeimpulse/processing-blocks, thư mục mfe, implementation_version 4,
tham số mặc định: khung 0,02 s, bước 0,01 s, 40 bộ lọc, FFT 256) để tính năng lượng mel (dB) trên
1.200 đoạn chọn ngẫu nhiên (seed 1) từ data/ei_upload, rồi đo tỉ lệ ô thời gian–tần số còn giữ lại
(lớn hơn sàn nhiễu) ở các mức sàn khác nhau. Mục đích: xem tiếng ho nhỏ nhất trong tập huấn luyện
(đỉnh −35 dBFS) có bị sàn nhiễu mặc định −52 dB xoá mất phần lớn hay không.
Chạy:  git clone --depth 1 https://github.com/edgeimpulse/processing-blocks /duong/dan
       python3 tools/mo_hinh_nen/khao_sat_san_nhieu_mfe.py /duong/dan/processing-blocks
"""
import csv
import importlib.util
import os
import random
import sys

import numpy as np
import soundfile as sf

PB = sys.argv[1]
spec = importlib.util.spec_from_file_location("speechpy", os.path.join(PB, "mfe/third_party/speechpy/__init__.py"))
sp = importlib.util.module_from_spec(spec); sys.modules["speechpy"] = sp; spec.loader.exec_module(sp)


def mfe_db(x):
    s = sp.processing.preemphasis(x.astype(np.float32), cof=0.98, shift=1)
    m, _, _, _ = sp.feature.mfe(s, sampling_frequency=16000, implementation_version=4, frame_length=0.02,
                                frame_stride=0.01, num_filters=40, fft_length=256, low_frequency=0,
                                high_frequency=None, use_old_mels=False)
    return 10 * np.log10(np.clip(m, 1e-30, None))


rows = list(csv.DictReader(open("results/ei_du_lieu_mo_hinh_nen.csv", encoding="utf-8")))
random.seed(1); rs = random.sample(rows, 1200)
D = {}
for r in rs:
    x, _ = sf.read("data/ei_upload/" + r["file"], dtype="int16")
    D[r["file"]] = mfe_db(x / 2 ** 15)
print("Phan vi nang luong mel (dB) theo muc dinh cua doan (trung vi tren cac doan):")
for lab in ("cough", "noise"):
    for lo, hi in ((-35, -29), (-29, -19), (-19, -2.9)):
        b = [D[r["file"]] for r in rs if r["label"] == lab and lo <= float(r["peak_dbfs"]) < hi]
        pc = lambda q: np.median([np.percentile(d, q) for d in b])
        print(f"  {lab:5s} dinh {lo}..{hi} dBFS (n={len(b)}): P99 {pc(99):.1f} | P90 {pc(90):.1f} | P50 {pc(50):.1f} | P10 {pc(10):.1f}")
print("Ti le o duoc giu lai (> san nhieu):")
for nf in (-52, -60, -66, -72, -80, -90):
    s = []
    for lab in ("cough", "noise"):
        a = np.mean([(D[r["file"]] > nf).mean() for r in rs if r["label"] == lab])
        q = np.mean([(D[r["file"]] > nf).mean() for r in rs if r["label"] == lab and float(r["peak_dbfs"]) < -29])
        s.append(f"{lab} {a:.3f} (doan nho {q:.3f})")
    print(f"  san {nf} dB: " + "; ".join(s))
