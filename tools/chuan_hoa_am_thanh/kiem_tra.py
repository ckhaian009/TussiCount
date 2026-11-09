"""Phép thử cho dữ liệu đã chuẩn bị bằng chuan_bi_du_lieu_ei.py.

Kiểm tra từng tệp trong data/ei_upload: WAV, 16 kHz, một kênh, PCM 16 bit, đúng 16.000 mẫu;
mức đỉnh khớp mức ghi trong bảng kê (±0,2 dB); không trùng tên; số tệp khớp bảng kê;
không có bản ghi gốc, người nói hay fold nào nằm ở cả tập huấn luyện và tập kiểm tra;
nhãn trong tên tệp khớp thư mục. In thêm 10 tệp chọn ngẫu nhiên (seed 2026) để nhóm nghe thử.
Chạy:  python3 tools/chuan_hoa_am_thanh/kiem_tra.py
"""
import csv
import glob
import os
import random
import sys
from collections import defaultdict

import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
OUT, MANIFEST = "data/ei_upload", "results/ei_du_lieu_mo_hinh_nen.csv"


def main():
    rows = list(csv.DictReader(open(MANIFEST, encoding="utf-8")))
    files = sorted(os.path.relpath(p, OUT) for p in glob.glob(os.path.join(OUT, "*", "*", "*.wav")))
    loi = []
    if sorted(r["file"] for r in rows) != files:
        loi.append(f"so tep tren dia ({len(files)}) khac bang ke ({len(rows)})")
    for r in rows:
        p = os.path.join(OUT, r["file"])
        i = sf.info(p)
        if (i.samplerate, i.channels, i.frames, i.subtype) != (16000, 1, 16000, "PCM_16"):
            loi.append(f"{r['file']}: {i.samplerate} Hz, {i.channels} kenh, {i.frames} mau, {i.subtype}")
            continue
        x, _ = sf.read(p)
        pk = 20 * np.log10(np.max(np.abs(x)) + 1e-12)
        if abs(pk - float(r["peak_dbfs"])) > 0.2:
            loi.append(f"{r['file']}: dinh {pk:.2f} dBFS, bang ke {r['peak_dbfs']}")
        lab_dir = r["file"].split("/")[1]
        if os.path.basename(r["file"]).split(".")[0] != lab_dir or lab_dir != r["label"]:
            loi.append(f"{r['file']}: nhan khong khop")
    g = defaultdict(set)
    for r in rows:
        g[(r["source"], r["group"])].add(r["split"])
    ro = [k for k, v in g.items() if len(v) > 1]
    if ro:
        loi.append(f"{len(ro)} nhom nam o ca hai tap, vi du {ro[:3]}")
    print(f"Da kiem tra {len(rows)} tep; {len(g)} nhom (ban ghi, nguoi noi, fold).")
    print("KET QUA:", "DAT" if not loi else f"{len(loi)} LOI")
    for e in loi[:20]:
        print("  -", e)
    print("10 tep nghe thu (seed 2026):")
    for r in random.Random(2026).sample(rows, 10):
        print("  ", r["file"], "|", r["source"], r["note"])
    return 0 if not loi else 1


if __name__ == "__main__":
    sys.exit(main())
