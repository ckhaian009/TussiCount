"""Phép thử tự động cho các đoạn ho đã cắt bằng tools/chuan_bi_phat_lai.py (Protocol mục 7.1).

Không sửa đoạn nào; chỉ đọc và báo cáo. Chạy từ thư mục gốc của kho:
    python3 tools/kiem_tra_doan_ho/kiem_tu_dong.py

Kiểm tra trên toàn bộ 1.100 đoạn:
  A. Tái lập: chạy lại thuật toán cắt trên bản ghi gốc; thời điểm cắt phải khớp
     results/coswara_playlist.csv (sai lệch < 0,6 ms do làm tròn) và đoạn trên đĩa phải trùng
     đoạn cắt lại (tương quan > 0,999).
  B. Định dạng: đúng tần số mẫu, đúng độ dài, đỉnh −1 dBFS (±0,1 dB), không bị cắt đỉnh.
  C. Dấu hiệu nghi lỗi (chỉ để đối chiếu với phép nghe, không dùng để loại tệp):
     - nghi_cut_dau: 20 ms đầu đã to gần bằng đỉnh (chênh < 12 dB);
     - nghi_cut_duoi: 30 ms cuối trước đoạn làm mờ còn to (chênh với đỉnh < 15 dB);
     - nghi_hai_tieng: có từ hai cụm năng lượng (trên đỉnh − 15 dB) cách nhau quá 120 ms.
Kết quả: results/kiem_tra_doan_ho_tu_dong.csv và bản tóm tắt in ra màn hình.
"""
import csv
import os
import sys

import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
os.chdir(ROOT)
import chuan_bi_phat_lai as C  # noqa: E402  dùng đúng hằng số của công cụ cắt

OUT = "results/kiem_tra_doan_ho_tu_dong.csv"


def db(x):
    return 20 * np.log10(np.sqrt(np.mean(np.square(x))) + 1e-12)


def bursts(seg, sr):
    n, h = int(0.010 * sr), int(0.005 * sr)
    lv = np.array([db(seg[i:i + n]) for i in range(0, max(1, len(seg) - n), h)])
    on = lv > lv.max() - 15
    regs, start = [], None
    for i, m in enumerate(on):
        if m and start is None:
            start = i
        if not m and start is not None:
            regs.append([start, i - 1]); start = None
    if start is not None:
        regs.append([start, len(on) - 1])
    merged = [regs[0]]
    for r in regs[1:]:
        if (r[0] - merged[-1][1]) * 0.005 > 0.120:
            merged.append(r)
        else:
            merged[-1][1] = r[1]
    return len(merged)


def main():
    rows = list(csv.DictReader(open(C.PLAYLIST, encoding="utf-8")))
    out, loi = [], 0
    for r in rows:
        f = r["file"]
        x, sr = sf.read(os.path.join(C.SRC, f), always_2d=True)
        x = x.mean(axis=1)
        seg, sr2 = sf.read(os.path.join(C.DST, f))
        t0, t1, _, _ = C.segment(x, sr)                  # chạy lại thuật toán cắt
        if abs(t0 - float(r["doan_bat_dau_s"])) > 0.0006 or abs(t1 - float(r["doan_ket_thuc_s"])) > 0.0006:
            lech_thoi_diem = True
        else:
            lech_thoi_diem = False
        ref = x[int(t0 * sr):int(t1 * sr)].copy()
        k = int(C.FADE_S * sr)
        ref[:k] *= np.linspace(0, 1, k); ref[-k:] *= np.linspace(1, 0, k)
        ref *= 10 ** (C.PEAK_DBFS / 20) / np.max(np.abs(ref))
        m = min(len(ref), len(seg))
        corr = float(np.corrcoef(ref[:m], seg[:m])[0, 1]) if m > 10 else 0.0
        peak = 20 * np.log10(np.max(np.abs(seg)) + 1e-12)
        flags = []
        if sr2 != int(r["sample_rate"]):
            flags.append("sai_tan_so_mau")
        if abs(len(seg) / sr2 - float(r["doan_dai_s"])) > 0.002:
            flags.append("sai_do_dai")
        if abs(peak - C.PEAK_DBFS) > 0.1:
            flags.append("sai_muc_dinh")
        if corr < 0.999 or lech_thoi_diem:
            flags.append("khong_tai_lap_duoc")
        hard = bool(flags)
        loi += hard
        pk = db(seg[np.argmax(np.abs(seg)) - int(0.005 * sr2):np.argmax(np.abs(seg)) + int(0.005 * sr2)] if np.argmax(np.abs(seg)) > int(0.005 * sr2) else seg[:int(0.01 * sr2)])
        dau = db(seg[k:k + int(0.020 * sr2)])
        duoi = db(seg[-k - int(0.030 * sr2):-k])
        if pk - dau < 12:
            flags.append("nghi_cut_dau")
        if pk - duoi < 15:
            flags.append("nghi_cut_duoi")
        nb = bursts(seg, sr2)
        if nb > 1:
            flags.append("nghi_hai_tieng")
        out.append({"stt": r["stt"], "file": f, "doan_dai_s": r["doan_dai_s"], "muc_dich": r["muc_dich"],
                    "tuong_quan_tai_lap": f"{corr:.5f}", "dinh_dbfs": f"{peak:.2f}",
                    "chenh_dau_db": f"{pk - dau:.1f}", "chenh_duoi_db": f"{pk - duoi:.1f}",
                    "so_cum": nb, "dau_hieu": ";".join(flags)})
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    d = np.array([float(o["doan_dai_s"]) for o in out])
    print("So doan kiem tra:", len(out))
    print("A+B (tai lap, dinh dang): %d doan loi" % loi)
    for n in ("nghi_cut_dau", "nghi_cut_duoi", "nghi_hai_tieng"):
        print("C. %-15s %4d doan (%.1f%%)" % (n, sum(n in o["dau_hieu"] for o in out), 100 * sum(n in o["dau_hieu"] for o in out) / len(out)))
    print("Do dai: min %.2f s, trung vi %.2f s, max %.2f s" % (d.min(), np.median(d), d.max()))
    print("Ket qua chi tiet:", OUT)
    return 0 if loi == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
