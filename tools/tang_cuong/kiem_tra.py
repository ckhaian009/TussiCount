"""Phép thử cho dữ liệu tăng cường (data/ei_tang_cuong, results/ei_tang_cuong.csv).

Kiểm tra:
  1. Định dạng: mọi tệp là WAV 16 kHz, một kênh, PCM 16 bit, đúng 16.000 mẫu; không có tệp thừa hoặc thiếu so với bảng kê.
  2. Mức: đỉnh mỗi tệp khớp peak_dbfs trong bảng kê (sai số ≤ 0,1 dB) và nằm trong [−35; −3] dBFS; không bị cắt đỉnh.
  3. Không rò rỉ: tệp training chỉ dùng đoạn gốc, nền và kho RIR của training; tệp testing chỉ dùng của testing;
     không nhóm nào của tập huấn luyện xuất hiện trong tập kiểm tra.
  4. Nhãn: nhãn tệp tăng cường bằng nhãn đoạn gốc; mọi đoạn ho có nền trộn; SNR nằm trong [0; 20] dB.
  5. Số lượng: cough training = số cough training gốc; noise training = cough training; testing đủ mọi đoạn gốc.
  6. Kho RIR: T20 đo được lệch RT60 mục tiêu ≤ 10%; khoảng cách trong [1; 5] m; hai kho không dùng chung thông số.
In "KET QUA: DAT" nếu mọi phép thử đạt.
Chạy từ gốc kho: python3 tools/tang_cuong/kiem_tra.py
"""
import csv
import os
import sys
from collections import Counter

import numpy as np
from scipy.io import wavfile

OUT = "data/ei_tang_cuong"


def main():
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(root)
    loi = []
    src = {r["file"]: r for r in csv.DictReader(open("results/ei_du_lieu_mo_hinh_nen.csv", encoding="utf-8"))}
    rows = list(csv.DictReader(open("results/ei_tang_cuong.csv", encoding="utf-8")))
    rir = list(csv.DictReader(open("results/tang_cuong_rir.csv", encoding="utf-8")))

    # 1, 2. định dạng và mức
    tren_dia = set()
    for dp, _, fs in os.walk(OUT):
        for f in fs:
            if f.endswith(".wav"):
                tren_dia.add(os.path.relpath(os.path.join(dp, f), OUT))
    trong_bang = {r["file"] for r in rows}
    if tren_dia != trong_bang:
        loi.append(f"tep tren dia khac bang ke: thua {len(tren_dia - trong_bang)}, thieu {len(trong_bang - tren_dia)}")
    for r in rows:
        p = os.path.join(OUT, r["file"])
        if not os.path.exists(p):
            continue
        sr, x = wavfile.read(p)
        if sr != 16000 or x.dtype != np.int16 or x.ndim != 1 or len(x) != 16000:
            loi.append(f"dinh dang sai: {r['file']} sr={sr} dtype={x.dtype} shape={x.shape}")
            continue
        pk = 20 * np.log10(np.max(np.abs(x.astype(np.float64))) / 32768.0)
        if abs(pk - float(r["peak_dbfs"])) > 0.1 or not (-35.1 <= pk <= -2.9):
            loi.append(f"muc sai: {r['file']} {pk:.2f} vs {r['peak_dbfs']}")
        if np.max(np.abs(x)) >= 32767:
            loi.append(f"cat dinh: {r['file']}")

    # 3, 4. rò rỉ và nhãn
    bank = {"training": "huan_luyen", "testing": "kiem_tra"}
    for r in rows:
        g = src.get(r["source_file"])
        if g is None:
            loi.append(f"khong thay doan goc: {r['source_file']}")
            continue
        if g["split"] != r["split"]:
            loi.append(f"doan goc khac tap: {r['file']}")
        if g["label"] != r["label"] or g["group"] != r["group"]:
            loi.append(f"nhan/nhom khac doan goc: {r['file']}")
        if r["rir_bank"] != bank[r["split"]]:
            loi.append(f"kho RIR sai: {r['file']}")
        if r["nen_file"]:
            b = src.get(r["nen_file"])
            if b is None or b["split"] != r["split"] or b["label"] != "noise":
                loi.append(f"nen sai tap hoac nhan: {r['file']}")
            s = float(r["snr_db"])
            if not (0.0 <= s <= 20.0):
                loi.append(f"SNR ngoai khoang: {r['file']} {s}")
        elif r["label"] == "cough":
            loi.append(f"doan ho khong co nen: {r['file']}")
    g_train = {r["group"] for r in rows if r["split"] == "training"}
    g_test = {r["group"] for r in rows if r["split"] == "testing"}
    # ESC-50 dùng fold làm nhóm (fold 1–4 / fold 5), nên giao nhau phải rỗng
    chung = g_train & g_test
    if chung:
        loi.append(f"{len(chung)} nhom nam o ca hai tap, vi du {sorted(chung)[:3]}")

    # 5. số lượng
    c = Counter((r["split"], r["label"]) for r in rows)
    c_src = Counter((r["split"], r["label"]) for r in src.values())
    if c[("training", "cough")] != c_src[("training", "cough")]:
        loi.append("so cough training khac so goc")
    if c[("training", "noise")] != c[("training", "cough")]:
        loi.append("so noise training khac so cough training")
    for lab in ("cough", "noise"):
        if c[("testing", lab)] != c_src[("testing", lab)]:
            loi.append(f"so {lab} testing khac so goc")
    if len({r["source_file"] for r in rows}) != len(rows):
        loi.append("mot doan goc duoc tang cuong hon mot lan")

    # 6. kho RIR
    for r in rir:
        t, m = float(r["t20_do_s"]), float(r["rt60_muc_tieu_s"])
        if abs(t - m) > 0.10 * m + 1e-9 or not (0.3 <= m <= 1.2):
            loi.append(f"RIR {r['bank']}#{r['id']}: T20 {t} vs muc tieu {m}")
        if not (1.0 <= float(r["khoang_cach_m"]) <= 5.0):
            loi.append(f"RIR {r['bank']}#{r['id']}: khoang cach {r['khoang_cach_m']}")
    sig = Counter((r["dai_m"], r["rong_m"], r["mic"], r["nguon"]) for r in rir)
    if any(v > 1 for v in sig.values()):
        loi.append("hai RIR trung thong so")

    print(f"So tep: {dict(c)}")
    print(f"Kho RIR: {Counter(r['bank'] for r in rir)}")
    if loi:
        print(f"{len(loi)} loi, vi du:")
        for l in loi[:20]:
            print("  -", l)
        print("KET QUA: KHONG DAT")
        return 1
    print("KET QUA: DAT")
    return 0


if __name__ == "__main__":
    sys.exit(main())
