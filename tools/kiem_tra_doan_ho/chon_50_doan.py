"""Chuẩn bị phép nghe kiểm tra 50 đoạn ho Coswara (việc t52).

Chọn ngẫu nhiên đơn giản 50 trong 1.100 đoạn (seed 5050, cố định trước khi nghe), chép sang
data/coswara/nghe_thu_50/ với tên 01.wav … 50.wav để người nghe không thấy tên gốc hay dấu hiệu
của phép thử tự động. Tạo thêm:
  - data/coswara/nghe_thu_50/bang_song_1..5.png: dạng sóng bản ghi gốc ±1 giây quanh đoạn cắt
    (vùng tô màu là đoạn đã cắt), giúp phán đoán cụt đầu, cụt đuôi;
  - results/nghe_thu_50_phieu.csv: phiếu để người nghe điền.
Chạy từ thư mục gốc của kho:  python3 tools/kiem_tra_doan_ho/chon_50_doan.py
"""
import csv
import os
import random
import shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
SEED, N = 5050, 50
SRC, DST = "data/coswara/coswara_phat_lai", "data/coswara/doan_ho"
OUT = "data/coswara/nghe_thu_50"
PHIEU = "results/nghe_thu_50_phieu.csv"


def main():
    rows = list(csv.DictReader(open("results/coswara_playlist.csv", encoding="utf-8")))
    chon = sorted(random.Random(SEED).sample(range(len(rows)), N))
    os.makedirs(OUT, exist_ok=True)
    if os.path.exists(PHIEU):
        print("Da co", PHIEU, "- khong ghi de. Xoa tep do neu muon tao lai.")
        return
    phieu = []
    for k, i in enumerate(chon, 1):
        r = rows[i]
        shutil.copy(os.path.join(DST, r["file"]), os.path.join(OUT, f"{k:02d}.wav"))
        phieu.append({"stt": f"{k:02d}", "tep_goc": r["file"], "ket_qua": "", "ghi_chu": "",
                      "nguoi_nghe": "", "ngay": ""})
    with open(PHIEU, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(phieu[0].keys())); w.writeheader(); w.writerows(phieu)
    for trang in range(5):
        fig, axs = plt.subplots(5, 2, figsize=(14, 11), dpi=110)
        for j, ax in enumerate(axs.T.flat):
            k = trang * 10 + j
            r = rows[chon[k]]
            x, sr = sf.read(os.path.join(SRC, r["file"]), always_2d=True)
            x = x.mean(axis=1)
            t0, t1 = float(r["doan_bat_dau_s"]), float(r["doan_ket_thuc_s"])
            a, b = max(0, int((t0 - 1) * sr)), min(len(x), int((t1 + 1) * sr))
            t = np.arange(a, b) / sr - t0
            ax.plot(t, x[a:b] / (np.max(np.abs(x[a:b])) + 1e-9), lw=0.4, color="#121513")
            ax.axvspan(0, t1 - t0, color="#0f766e", alpha=0.25)
            ax.set_title(f"{k + 1:02d}.wav  ·  đoạn {t1 - t0:.2f} s", fontsize=9, loc="left")
            ax.set_yticks([]); ax.set_xlim(t[0], t[-1]); ax.tick_params(labelsize=7)
        fig.suptitle(f"Nghe thử 50 đoạn – trang {trang + 1}/5. Vùng xanh là đoạn đã cắt; trục ngang: giây tính từ đầu đoạn",
                     fontsize=10)
        fig.tight_layout()
        fig.savefig(os.path.join(OUT, f"bang_song_{trang + 1}.png"))
        plt.close(fig)
    print("Da chep", N, "doan vao", OUT, "va tao", PHIEU)


if __name__ == "__main__":
    main()
