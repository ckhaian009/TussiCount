"""Chuẩn bị tiếng ho phát lại cho tầng kiểm định 1 (Protocol mục 7.1).

1. Cắt từ mỗi bản ghi Coswara một tiếng ho đơn theo thuật toán cố định.
2. Chuẩn hoá mức đỉnh về -1 dBFS, ghi vào data/coswara/doan_ho/ (không đẩy lên GitHub).
3. Phân bổ ngẫu nhiên (seed 2026): 10 tiếng ho kiểm tra đầu buổi, 40 tiếng ho
   so sánh hai thiết bị, 1.050 tiếng ho vào 36 ô.
4. Ghi lại results/coswara_playlist.csv kèm thời điểm cắt và ô được gán.

Chạy: python3 tools/chuan_bi_phat_lai.py (từ thư mục gốc của kho).
"""
import csv
import os
import random

import numpy as np
import soundfile as sf

SEED = 2026
SRC = "data/coswara/coswara_phat_lai"
DST = "data/coswara/doan_ho"
PLAYLIST = "results/coswara_playlist.csv"

FRAME_S, HOP_S = 0.020, 0.010      # khung 20 ms, bước 10 ms
FLOOR_PCT = 10                     # nền = phân vị 10 của mức khung
ABOVE_FLOOR_DB = 12                # ngưỡng >= nền + 12 dB
BELOW_PEAK_DB = 30                 # và >= đỉnh - 30 dB
MERGE_GAP_S = 0.05                 # gộp hai vùng cách nhau < 50 ms
PAD_PRE_S, PAD_POST_S = 0.05, 0.10
MAX_LEN_S = 1.5
FADE_S = 0.010
PEAK_DBFS = -1.0


def frame_db(x, sr):
    y = np.append(x[0], x[1:] - 0.97 * x[:-1])          # nhấn tần cao, giảm ù
    n, h = int(FRAME_S * sr), int(HOP_S * sr)
    if len(y) < n:
        y = np.pad(y, (0, n - len(y)))
    idx = np.arange(0, len(y) - n + 1, h)
    rms = np.array([np.sqrt(np.mean(y[i:i + n] ** 2)) for i in idx])
    return 20 * np.log10(rms + 1e-12), h


def regions(mask):
    out, start = [], None
    for i, m in enumerate(mask):
        if m and start is None:
            start = i
        if not m and start is not None:
            out.append([start, i - 1]); start = None
    if start is not None:
        out.append([start, len(mask) - 1])
    return out


def segment(x, sr):
    db, h = frame_db(x, sr)
    peak_i = int(np.argmax(db))
    thr = max(np.percentile(db, FLOOR_PCT) + ABOVE_FLOOR_DB, db[peak_i] - BELOW_PEAK_DB)
    regs = regions(db > thr)
    gap = int(MERGE_GAP_S / HOP_S)
    merged = [regs[0]]
    for r in regs[1:]:
        if r[0] - merged[-1][1] - 1 < gap:
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    reg = next(r for r in merged if r[0] <= peak_i <= r[1])
    t0 = max(0.0, reg[0] * HOP_S - PAD_PRE_S)
    t1 = min(len(x) / sr, (reg[1] * HOP_S + FRAME_S) + PAD_POST_S)
    note = []
    if t1 - t0 > MAX_LEN_S:
        t1 = t0 + MAX_LEN_S; note.append("cat_bot_do_dai")
    if t1 - t0 < 0.15:
        note.append("qua_ngan")
    return t0, t1, len(merged), ";".join(note)


def main():
    rows = list(csv.DictReader(open(PLAYLIST, encoding="utf-8")))
    os.makedirs(DST, exist_ok=True)
    for r in rows:
        x, sr = sf.read(os.path.join(SRC, r["file"]), always_2d=True)
        x = x.mean(axis=1)
        t0, t1, n_reg, note = segment(x, sr)
        seg = x[int(t0 * sr):int(t1 * sr)].copy()
        f = int(FADE_S * sr)
        seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
        seg *= 10 ** (PEAK_DBFS / 20) / np.max(np.abs(seg))
        sf.write(os.path.join(DST, r["file"]), seg, sr, subtype="PCM_16")
        r.update(doan_bat_dau_s=f"{t0:.3f}", doan_ket_thuc_s=f"{t1:.3f}",
                 doan_dai_s=f"{t1 - t0:.3f}", so_vung_ho_ban_ghi=n_reg, ghi_chu=note)

    # Phân bổ ngẫu nhiên
    order = list(range(len(rows)))
    random.Random(SEED).shuffle(order)
    cells = []
    for kg in ("yen_tinh", "on"):
        for vt in ("hanh_lang", "phong_cua_dong"):
            for kc in (1, 3, 5):
                for dl in ("nho", "vua", "lon"):
                    main_cell = kg == "yen_tinh" and vt == "hanh_lang" and dl == "vua" and kc in (1, 3)
                    cells.append((f"{vt}|{kc}m|{dl}|{kg}", vt, kc, dl, kg, 100 if main_cell else 25))
    plan = [("kiem_tra_dau_buoi", "", "", "", "", 10), ("so_sanh_hai_thiet_bi", "", "", "", "", 40)]
    plan += [("o",) + c for c in cells]
    k = 0
    for p in plan:
        if p[0] == "o":
            _, oid, vt, kc, dl, kg, n = p
            muc = "o"
        else:
            muc, oid, vt, kc, dl, kg, n = p[0], "", "", "", "", "", p[5]
        for _ in range(n):
            rows[order[k]].update(muc_dich=muc, o=oid, vi_tri=vt, khoang_cach_m=kc,
                                  do_lon=dl, khung_gio=kg)
            k += 1
    assert k == len(rows) == 1100, k

    cols = list(rows[0].keys())
    with open(PLAYLIST, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(rows)

    d = np.array([float(r["doan_dai_s"]) for r in rows])
    print("so tep:", len(rows), "| do dai doan (s): min %.2f, trung vi %.2f, max %.2f" % (d.min(), np.median(d), d.max()))
    print("ghi chu:", {n: sum(1 for r in rows if n in r["ghi_chu"]) for n in ("cat_bot_do_dai", "qua_ngan")})
    print("ban ghi co >1 vung ho:", sum(1 for r in rows if int(r["so_vung_ho_ban_ghi"]) > 1))


if __name__ == "__main__":
    main()
