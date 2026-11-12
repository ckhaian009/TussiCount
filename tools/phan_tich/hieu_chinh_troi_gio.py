"""Hiệu chỉnh trôi giờ của thiết bị bằng nội suy tuyến tính giữa các lần đồng bộ (Protocol mục 16).

Thiết bị neo đồng hồ mẫu vào giờ chuẩn ở mỗi lần đồng bộ (điện thoại hoặc NTP) và ghi độ lệch đo được vào
TC-01_<ngày>_dong_bo.csv: lech_ms = giờ chuẩn − giờ đồng hồ mẫu dự đoán ngay trước khi neo lại, tức phần trôi tích
luỹ kể từ lần neo trước. Giả định trôi đều (thạch anh) giữa hai lần neo k và k+1, một thời điểm t do thiết bị ghi được
hiệu chỉnh thành t + lech_{k+1} × (t − T_k) / (T_{k+1} − T_k). Thời điểm sau lần neo cuối cùng không có lần đo kế
tiếp nên giữ nguyên và được đánh dấu.

  python3 tools/phan_tich/hieu_chinh_troi_gio.py --dong-bo TC-01_*_dong_bo.csv \\
      --vao TC-01_2026-11-13_su_kien.csv --cot t_su_kien_epoch --ra su_kien_dem13_hieu_chinh.csv
  (cũng dùng được cho tệp điểm: --cot t_bat_dau_epoch)
Thử: python3 tools/phan_tich/hieu_chinh_troi_gio.py --thu
"""
import argparse
import bisect
import csv
import sys


def doc_moc(paths):
    m = []
    for p in paths:
        for r in csv.DictReader(open(p, encoding="utf-8")):
            m.append((float(r["t_epoch"]), float(r["lech_ms"]) / 1000.0, r["da_co_gio_truoc"] == "1"))
    m.sort()
    return m


def hieu_chinh(t, moc):
    """Trả về (t_hieu_chinh, trang_thai): 'noi_suy' | 'sau_moc_cuoi' | 'truoc_moc_dau'."""
    T = [x[0] for x in moc]
    k = bisect.bisect_right(T, t) - 1
    if k < 0:
        return t, "truoc_moc_dau"
    if k + 1 >= len(moc):
        return t, "sau_moc_cuoi"
    t0, (t1, lech1, co_truoc) = T[k], moc[k + 1]
    if not co_truoc:            # lần neo k+1 là lần đầu sau khi mất giờ: không đo được trôi
        return t, "sau_moc_cuoi"
    return t + lech1 * (t - t0) / (t1 - t0), "noi_suy"


def thu():
    loi = []
    # neo lúc 0 (lần đầu), 86400 s sau đo được trôi +1,6 s
    moc = [(0.0, 0.0, False), (86400.0, 1.6, True)]
    for t, mong in [(0.0, 0.0), (43200.0, 43200.8), (86399.0, 86399.0 + 1.6 * 86399 / 86400)]:
        h, tt = hieu_chinh(t, moc)
        if abs(h - mong) > 1e-6 or tt != "noi_suy":
            loi.append(f"t={t}: {h} ({tt}), mong {mong}")
    h, tt = hieu_chinh(90000.0, moc)
    if tt != "sau_moc_cuoi" or h != 90000.0:
        loi.append("sau moc cuoi")
    print("KET QUA:", "DAT" if not loi else "KHONG DAT: " + "; ".join(loi))
    return 0 if not loi else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dong-bo", nargs="+")
    ap.add_argument("--vao")
    ap.add_argument("--cot", default="t_su_kien_epoch")
    ap.add_argument("--ra")
    ap.add_argument("--thu", action="store_true")
    a = ap.parse_args()
    if a.thu:
        return thu()
    moc = doc_moc(a.dong_bo)
    dem = {}
    with open(a.vao, encoding="utf-8") as f, open(a.ra, "w", newline="", encoding="utf-8") as g:
        rd = csv.DictReader(f)
        w = csv.DictWriter(g, fieldnames=rd.fieldnames + [a.cot + "_hieu_chinh", "hieu_chinh_troi"])
        w.writeheader()
        for r in rd:
            h, tt = hieu_chinh(float(r[a.cot]), moc)
            r[a.cot + "_hieu_chinh"] = f"{h:.3f}"
            r["hieu_chinh_troi"] = tt
            dem[tt] = dem.get(tt, 0) + 1
            w.writerow(r)
    print(f"{len(moc)} lan dong bo; {dem} -> {a.ra}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
