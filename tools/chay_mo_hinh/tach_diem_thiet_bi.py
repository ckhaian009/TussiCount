"""Tách tệp điểm của thiết bị (TC-01_<ngày>_diem.csv: t_bat_dau_epoch,p_cough_v1,p_cough_v2) thành tệp điểm của MỘT
mô hình theo đúng định dạng của "chay_mo_hinh dai" (cua_so,t_bat_dau_s,p_cough,ms_xu_ly), để đưa vào gop_su_kien.py
với mô hình và ngưỡng đã đóng băng (dùng cho đêm chạy trước khi đóng băng; Protocol mục 16).

  python3 tools/chay_mo_hinh/tach_diem_thiet_bi.py TC-01_2026-11-13_diem.csv diem_v2.csv --mo-hinh v2 \\
      [--tu "2026-11-13 18:00" --den "2026-11-14 06:00"]
  python3 tools/chay_mo_hinh/gop_su_kien.py diem_v2.csv su_kien_dem13.csv --nguong <θ> --k <k> --g <g>

t_bat_dau_s trong tệp ra là giây epoch (UTC), nên thời điểm sự kiện của gop_su_kien.py cũng là giây epoch.
Cửa sổ có điểm −1 (mô hình lỗi) bị bỏ và được đếm.
"""
import argparse
import csv
import datetime as dt

VN = dt.timezone(dt.timedelta(hours=7))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vao")
    ap.add_argument("ra")
    ap.add_argument("--mo-hinh", choices=["v1", "v2"], required=True)
    ap.add_argument("--tu")
    ap.add_argument("--den")
    a = ap.parse_args()
    tu = dt.datetime.strptime(a.tu, "%Y-%m-%d %H:%M").replace(tzinfo=VN).timestamp() if a.tu else None
    den = dt.datetime.strptime(a.den, "%Y-%m-%d %H:%M").replace(tzinfo=VN).timestamp() if a.den else None
    cot = "p_cough_" + a.mo_hinh
    so = loi = 0
    with open(a.vao, encoding="utf-8") as f, open(a.ra, "w", newline="", encoding="utf-8") as g:
        w = csv.writer(g)
        w.writerow(["cua_so", "t_bat_dau_s", "p_cough", "ms_xu_ly"])
        for r in csv.DictReader(f):
            t = float(r["t_bat_dau_epoch"])
            if (tu is not None and t < tu) or (den is not None and t >= den):
                continue
            p = float(r[cot])
            if p < 0:
                loi += 1
                continue
            w.writerow([so, f"{t:.1f}", f"{p:.4f}", ""])
            so += 1
    print(f"{so} cua so ({so * 0.5 / 3600:.2f} gio), {loi} cua so loi -> {a.ra}")


if __name__ == "__main__":
    main()
