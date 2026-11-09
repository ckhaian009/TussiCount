"""Tổng hợp phiếu nghe 50 đoạn (results/nghe_thu_50_phieu.csv) sau khi đã điền.

Mã kết quả: DUNG, CUT_DAU, CUT_DUOI, HAI_TIENG, KHONG_HO, KHAC. Chỉ DUNG được tính là đúng.
In tỉ lệ đúng kèm khoảng tin cậy Wilson 95%, cơ cấu lỗi, và đối chiếu với dấu hiệu của
phép thử tự động (results/kiem_tra_doan_ho_tu_dong.csv).
Chạy:  python3 tools/kiem_tra_doan_ho/tong_hop_nghe.py
"""
import csv
import math
import os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
MA = {"DUNG", "CUT_DAU", "CUT_DUOI", "HAI_TIENG", "KHONG_HO", "KHAC"}


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - m) / d, (c + m) / d


def main():
    ph = list(csv.DictReader(open("results/nghe_thu_50_phieu.csv", encoding="utf-8")))
    trong = [p["stt"] for p in ph if p["ket_qua"].strip().upper() not in MA]
    if trong:
        print("Con", len(trong), "dong chua dien hoac sai ma:", ", ".join(trong))
        return
    n = len(ph)
    kq = Counter(p["ket_qua"].strip().upper() for p in ph)
    k = kq["DUNG"]
    lo, hi = wilson(k, n)
    print(f"Dung: {k}/{n} = {100 * k / n:.0f}% (KTC 95% Wilson: {100 * lo:.0f}–{100 * hi:.0f}%)")
    print("Co cau loi:", {m: c for m, c in kq.items() if m != "DUNG"} or "khong co")
    tu_dong = {r["file"]: r["dau_hieu"] for r in csv.DictReader(open("results/kiem_tra_doan_ho_tu_dong.csv", encoding="utf-8"))}
    co_dh = [p for p in ph if any(f.startswith("nghi_") for f in tu_dong.get(p["tep_goc"], "").split(";"))]
    loi_co_dh = sum(p["ket_qua"].strip().upper() != "DUNG" for p in co_dh)
    loi_ko_dh = sum(p["ket_qua"].strip().upper() != "DUNG" for p in ph if p not in co_dh)
    print(f"Doi chieu phep thu tu dong: {len(co_dh)} doan co dau hieu nghi, trong do {loi_co_dh} doan nghe thay loi; "
          f"{n - len(co_dh)} doan khong co dau hieu, trong do {loi_ko_dh} doan nghe thay loi.")
    print()
    print("Dong cho nhat ky kiem chung:")
    print(f"Nghe kiem tra 50 doan ho Coswara chon ngau nhien (seed 5050): {k}/{n} dung mot tieng ho tron ven "
          f"({100 * k / n:.0f}%, KTC 95% {100 * lo:.0f}–{100 * hi:.0f}%); loi: "
          + (", ".join(f"{m} {c}" for m, c in kq.items() if m != "DUNG") or "khong") + ".")


if __name__ == "__main__":
    main()
