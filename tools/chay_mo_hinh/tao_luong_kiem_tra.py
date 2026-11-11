"""Tạo luồng kiểm tra liên tục từ tập kiểm tra của dữ liệu mở, để đo độ nhạy theo sự kiện (có cửa sổ trượt,
gộp sự kiện và bộ lọc sau phân loại) thay vì theo từng đoạn 1 giây (Protocol mục 8; sửa đổi 16.7).

Luồng gồm các ô 8 giây nối tiếp (giống nhịp phát lại 8 s): mỗi ô là 1 đoạn ho của tập kiểm tra rồi 7 đoạn không ho
của tập kiểm tra (lấy vòng theo thứ tự trộn ngẫu nhiên, seed 2026). Mỗi đoạn được làm mờ đầu/cuối 20 ms để chỗ
nối không tạo tiếng tách. Thời điểm tiếng ho chuẩn = đầu đoạn ho + vị trí bắt đầu vùng năng lượng của tiếng ho
trong đoạn (cột note "vung a-b s" và start_s của bảng kê).

  --bo sach        bảng kê results/ei_du_lieu_mo_hinh_nen.csv, âm thanh data/ei_upload
  --bo tang_cuong  bảng kê results/ei_tang_cuong.csv, âm thanh data/ei_tang_cuong (vang + nền ồn, kho RIR kiểm tra)
Đầu ra: data/luong_kiem_tra/<bo>.wav và results/luong_kiem_tra_<bo>.csv (cột t_chuan, tep).
Chạy: python3 tools/chay_mo_hinh/tao_luong_kiem_tra.py --bo sach
"""
import argparse
import csv
import os
import random
import re
import sys
import wave

import numpy as np
from scipy.io import wavfile

SR = 16000
SEED = 2026
O_S = 8
FADE = int(0.02 * SR)
BO = {"sach": ("results/ei_du_lieu_mo_hinh_nen.csv", "data/ei_upload"),
      "tang_cuong": ("results/ei_tang_cuong.csv", "data/ei_tang_cuong")}


def doc(p):
    sr, x = wavfile.read(p)
    assert sr == SR
    return x.astype(np.float64) / 32768.0


def lam_mo(x):
    w = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, FADE))
    x = x.copy()
    x[:FADE] *= w
    x[-FADE:] *= w[::-1]
    return x


def vi_tri_ho(r, goc):
    """Giây tính từ đầu đoạn 1 s tới đầu vùng năng lượng của tiếng ho."""
    g = goc.get(r.get("source_file", r["file"]), r)
    m = re.search(r"vung ([0-9.]+)-([0-9.]+)s", g.get("note", ""))
    if not m:
        return 0.2
    return max(0.0, float(m.group(1)) - float(g["start_s"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bo", choices=BO, required=True)
    ap.add_argument("--goc", default="")
    a = ap.parse_args()
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(root)
    bang, thu_muc = BO[a.bo]
    rows = [r for r in csv.DictReader(open(bang, encoding="utf-8")) if r["split"] == "testing"]
    goc = {r["file"]: r for r in csv.DictReader(open("results/ei_du_lieu_mo_hinh_nen.csv", encoding="utf-8"))}
    ho = sorted([r for r in rows if r["label"] == "cough"], key=lambda r: r["file"])
    khong = sorted([r for r in rows if r["label"] == "noise"], key=lambda r: r["file"])
    rng = random.Random(f"{SEED}:luong:{a.bo}")
    rng.shuffle(ho)
    rng.shuffle(khong)
    n = len(ho)
    chuan = []
    k = 0
    os.makedirs("data/luong_kiem_tra", exist_ok=True)

    def ghi_doan(w, path):
        """Ghi ngay từng đoạn 1 s (không giữ cả luồng vài giờ trong bộ nhớ)."""
        x = lam_mo(doc(path))
        assert len(x) == SR, (path, len(x))
        w.writeframes(np.clip(np.round(x * 32767), -32768, 32767).astype("<i2").tobytes())

    with wave.open(f"data/luong_kiem_tra/{a.bo}.wav", "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        for i, r in enumerate(ho):
            t0 = i * O_S
            ghi_doan(w, os.path.join(thu_muc, r["file"]))
            chuan.append({"t_chuan": round(t0 + vi_tri_ho(r, goc), 3), "tep": r["file"]})
            for j in range(1, O_S):
                ghi_doan(w, os.path.join(thu_muc, khong[k % len(khong)]["file"]))
                k += 1
    with open(f"results/luong_kiem_tra_{a.bo}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["t_chuan", "tep"])
        w.writeheader()
        w.writerows(chuan)
    print(f"Luong {a.bo}: {n} tieng ho, {n * O_S / 3600:.2f} gio, {k} doan khong ho (dung lai {max(0, k - len(khong))} lan)")


if __name__ == "__main__":
    sys.exit(main())
