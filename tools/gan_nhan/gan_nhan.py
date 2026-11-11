"""Công cụ gán nhãn và xác minh mù cho tầng kiểm định 3 (Protocol 7.3, 16.2, 16.12; việc t26, t27, t33).

Âm thanh KTX: chỉ chạy trên máy tính của Nhóm, thư mục ra nằm ngoài Documents/iCloud và ngoài kho GitHub
(ví dụ ~/TussiCount_KTX). Người gán nhãn chỉ đánh dấu có hay không có tiếng ho và thời điểm; không chép, ghi chú
hay trích dẫn lời nói (16.12).

Phần để chấm gồm 2 tệp ghi liên tục: 17:55–20:25 (2,5 giờ) và 21:50–23:50 (2 giờ), tổng 4,5 giờ = 9 khối 30 phút.

  chon-doan <tep1.wav> <tep2.wav> <thu_muc_ra>
      Chọn ngẫu nhiên 4 trong 9 khối 30 phút (seed 2026) để gán nhãn đầy đủ; khối sớm nhất trong 4 khối do hai
      người gán độc lập (tính F1 đồng thuận). Cắt 4 khối ra tệp riêng để mở trong Audacity; ghi khoi.csv.
  f1 <nhan_nguoi_1.txt> <nhan_nguoi_2.txt>
      F1 đồng thuận giữa hai người (dung sai ±0,5 s) trên tệp nhãn Audacity (bat_dau<TAB>ket_thuc<TAB>nhan).
      Nhãn ho: h; nhãn không chắc: ?. Nếu F1 < 0,80: thống nhất lại quy ước và gán lại khối đó.
  xac-minh-tao <khoi.csv> <su_kien.csv> <thu_muc_ra>
      Phần còn lại (5 khối, 2,5 giờ): cắt đoạn 3 s quanh mỗi sự kiện thiết bị báo (lần chạy duy nhất của mô hình đã
      đóng băng), cộng cùng số đoạn 3 s ở vị trí ngẫu nhiên; trộn thứ tự; ghi phieu_mu.csv (người nghe điền co_ho
      và loai_am) và khoa_mu.csv (giữ riêng, người nghe không xem).
su_kien.csv có cột tep (tên tệp wav), t_su_kien (giây tính từ đầu tệp).
"""
import csv
import os
import random
import sys

import numpy as np
from scipy.io import wavfile

SEED = 2026
KHOI_S = 1800
DAI_DOAN_S = 3.0
NHAN_HO = {"h", "ho", "cough"}


def kiem_thu_muc(ra):
    p = os.path.abspath(os.path.expanduser(ra))
    if "/Documents/" in p + "/" or "Mobile Documents" in p:
        sys.exit("Thu muc ra nam trong Documents (dong bo iCloud). Chon thu muc khac, vi du ~/TussiCount_KTX.")
    os.makedirs(p, exist_ok=True)
    return p


def doc_nhan_audacity(p):
    """Trả về (danh sách thời điểm ho, danh sách thời điểm '?')."""
    ho, kc = [], []
    for dong in open(p, encoding="utf-8"):
        c = dong.rstrip("\n").split("\t")
        if len(c) < 3 or c[0].startswith("\\"):
            continue
        t, nhan = float(c[0]), c[2].strip().lower()
        if nhan in NHAN_HO:
            ho.append(t)
        elif nhan == "?":
            kc.append(t)
    return sorted(ho), sorted(kc)


def gop_trang(ts, cach=1.0):
    """Các tiếng ho cách nhau dưới 1 s thuộc một tràng, tính là một tiếng ho chuẩn (lấy thời điểm đầu)."""
    out = []
    for t in sorted(ts):
        if out and t - out[-1][-1] < cach:
            out[-1].append(t)
        else:
            out.append([t])
    return [g[0] for g in out]


def chon_doan(t1, t2, ra):
    ra = kiem_thu_muc(ra)
    tep = []
    for p in (t1, t2):
        sr, x = wavfile.read(p)
        tep.append((p, sr, x))
    khoi = []
    for p, sr, x in tep:
        n = len(x) // (KHOI_S * sr)
        for j in range(n):
            khoi.append({"tep": os.path.basename(p), "bat_dau_s": j * KHOI_S, "ket_thuc_s": (j + 1) * KHOI_S})
    if len(khoi) != 9:
        print(f"Canh bao: co {len(khoi)} khoi 30 phut (du kien 9).")
    chon = sorted(random.Random(SEED).sample(range(len(khoi)), 4))
    for i, k in enumerate(khoi):
        k["id"] = i
        k["vai_tro"] = ("gan_nhan_hai_nguoi" if i == chon[0] else "gan_nhan_day_du") if i in chon else "xac_minh_mu"
    for i in chon:
        k = khoi[i]
        p, sr, x = next(t for t in tep if os.path.basename(t[0]) == k["tep"])
        ten = f"khoi_{i}_{k['vai_tro']}.wav"
        wavfile.write(os.path.join(ra, ten), sr, x[k["bat_dau_s"] * sr:k["ket_thuc_s"] * sr])
        k["tep_cat"] = ten
    with open(os.path.join(ra, "khoi.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "tep", "bat_dau_s", "ket_thuc_s", "vai_tro", "tep_cat"])
        w.writeheader()
        w.writerows(khoi)
    print(f"Khoi gan nhan: {chon} (khoi {chon[0]} do hai nguoi gan doc lap). Da ghi {ra}/khoi.csv")


def f1(p1, p2):
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "phan_tich"))
    from ghep_su_kien import ghep
    a = gop_trang(doc_nhan_audacity(p1)[0])
    b = gop_trang(doc_nhan_audacity(p2)[0])
    kq = ghep(a, b, 0.5)
    p = kq["tp"] / len(b) if b else 0.0
    r = kq["tp"] / len(a) if a else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    print(f"Nguoi 1: {len(a)} tieng ho, nguoi 2: {len(b)}, trung khop {kq['tp']}; F1 = {f:.3f}")
    print("DAT (F1 >= 0,80)" if f >= 0.80 else "CHUA DAT: thong nhat lai quy uoc va gan lai khoi nay")
    return f


def xac_minh_tao(khoi_csv, su_kien_csv, ra):
    ra = kiem_thu_muc(ra)
    khoi = [k for k in csv.DictReader(open(khoi_csv, encoding="utf-8")) if k["vai_tro"] == "xac_minh_mu"]
    ev = list(csv.DictReader(open(su_kien_csv, encoding="utf-8")))
    goc = os.path.dirname(os.path.abspath(su_kien_csv))
    rng = random.Random(f"{SEED}:xac_minh")
    doan = []
    am = {}
    for k in khoi:
        a, b = float(k["bat_dau_s"]), float(k["ket_thuc_s"])
        trong = [float(e["t_su_kien"]) for e in ev if e["tep"] == k["tep"] and a <= float(e["t_su_kien"]) < b]
        for t in trong:
            doan.append({"tep": k["tep"], "tam_s": t, "nguon": "thiet_bi"})
        for _ in range(len(trong)):
            doan.append({"tep": k["tep"], "tam_s": rng.uniform(a + DAI_DOAN_S / 2, b - DAI_DOAN_S / 2), "nguon": "ngau_nhien"})
    rng.shuffle(doan)
    phieu, khoa = [], []
    for j, d in enumerate(doan, 1):
        if d["tep"] not in am:
            am[d["tep"]] = wavfile.read(os.path.join(goc, d["tep"]))
        sr, x = am[d["tep"]]
        s = max(0, int((d["tam_s"] - DAI_DOAN_S / 2) * sr))
        ten = f"mu_{j:04d}.wav"
        wavfile.write(os.path.join(ra, ten), sr, x[s:s + int(DAI_DOAN_S * sr)])
        phieu.append({"doan": ten, "co_ho": "", "loai_am": ""})
        khoa.append({"doan": ten, "tep": d["tep"], "tam_s": round(d["tam_s"], 3), "nguon": d["nguon"]})
    for ten, rows in (("phieu_mu.csv", phieu), ("khoa_mu.csv", khoa)):
        with open(os.path.join(ra, ten), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["doan"])
            w.writeheader()
            w.writerows(rows)
    n_tb = sum(d["nguon"] == "thiet_bi" for d in doan)
    print(f"{len(doan)} doan 3 s ({n_tb} tu thiet bi, {len(doan) - n_tb} ngau nhien). "
          f"Nguoi nghe dien phieu_mu.csv; giu rieng khoa_mu.csv.")


def main():
    a = sys.argv[1:]
    if len(a) == 4 and a[0] == "chon-doan":
        chon_doan(*a[1:])
    elif len(a) == 3 and a[0] == "f1":
        f1(*a[1:])
    elif len(a) == 4 and a[0] == "xac-minh-tao":
        xac_minh_tao(*a[1:])
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
