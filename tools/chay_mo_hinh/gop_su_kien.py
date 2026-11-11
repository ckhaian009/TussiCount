"""Gộp điểm từng cửa sổ thành sự kiện ho và bộ lọc sau phân loại (Protocol mục 6 và 8).

Định nghĩa (firmware vận hành phải làm đúng như vậy; tệp vector_thu_gop_su_kien.json dùng để thử đồng nhất):
  1. Cửa sổ i bắt đầu tại t_i = i × 0,5 s, dài 1 s, có điểm p_i (xác suất nhãn cough).
  2. Cửa sổ "vượt ngưỡng" khi p_i ≥ θ.
  3. Các cửa sổ vượt ngưỡng liền nhau tạo thành một chuỗi. Hai chuỗi cách nhau m cửa sổ dưới ngưỡng được
     gộp làm một khi m ≤ g / 0,5, với g là khoảng nghỉ tối thiểu giữa hai sự kiện (0; 0,5 hoặc 1 s):
     g = 0 không gộp; g = 0,5 s gộp khi cách 1 cửa sổ; g = 1 s gộp khi cách tối đa 2 cửa sổ.
  4. Sau khi gộp, giữ sự kiện có số cửa sổ vượt ngưỡng ≥ k (k = 1 hoặc 2).
  5. Thời điểm sự kiện = tâm của cửa sổ có điểm cao nhất (t_i + 0,5 s); nếu bằng nhau lấy cửa sổ sớm nhất.
     Sự kiện kéo dài từ đầu cửa sổ vượt ngưỡng đầu tiên đến cuối cửa sổ vượt ngưỡng cuối cùng.
Một tràng ho liên tiếp vì vậy được tính là một sự kiện.

Dùng như thư viện (gop(p, nguong, k, g)) hoặc dòng lệnh:
  python3 tools/chay_mo_hinh/gop_su_kien.py <diem.csv> <su_kien.csv> --nguong 0.8 --k 2 --g 0.5
<diem.csv> là đầu ra của chay_mo_hinh dai (cột t_bat_dau_s, p_cough).
"""
import argparse
import csv
import json
import os
import sys

BUOC = 0.5
CUA_SO = 1.0


def doc_diem(path):
    t, p = [], []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            t.append(float(r["t_bat_dau_s"]))
            p.append(float(r["p_cough"]))
    return t, p


def gop(p, nguong, k=1, g=0.0, t0=None, buoc=BUOC):
    """Trả về danh sách sự kiện: dict(t_su_kien, t_dau, t_cuoi, so_cua_so, p_max, i_max)."""
    if t0 is None:
        t0 = [i * buoc for i in range(len(p))]
    m_max = int(round(g / buoc))
    nhom = []  # mỗi nhóm: [i_dau, i_cuoi, so_vuot, i_max]
    cuoi_vuot = None
    for i, pi in enumerate(p):
        if pi < nguong:
            continue
        if nhom and cuoi_vuot is not None and (i - cuoi_vuot - 1) <= m_max:
            n = nhom[-1]
            n[1] = i
            n[2] += 1
            if pi > p[n[3]]:
                n[3] = i
        else:
            nhom.append([i, i, 1, i])
        cuoi_vuot = i
    out = []
    for i_dau, i_cuoi, so, i_max in nhom:
        if so < k:
            continue
        out.append({"t_su_kien": round(t0[i_max] + CUA_SO / 2, 4), "t_dau": round(t0[i_dau], 4),
                    "t_cuoi": round(t0[i_cuoi] + CUA_SO, 4), "so_cua_so": so, "p_max": p[i_max], "i_max": i_max})
    return out


def vector_thu():
    """Các tình huống thử cố định cho phép thử đồng nhất với firmware."""
    ca = [
        ("mot_cua_so", [0.1, 0.9, 0.1, 0.1], 0.5, 1, 0.0),
        ("mot_cua_so_k2_bi_loai", [0.1, 0.9, 0.1, 0.1], 0.5, 2, 0.0),
        ("chuoi_hai_cua_so_k2", [0.1, 0.7, 0.95, 0.2], 0.5, 2, 0.0),
        ("bang_nguong_tinh_la_vuot", [0.5, 0.49, 0.5], 0.5, 1, 0.0),
        ("hai_chuoi_cach_1_g0", [0.9, 0.1, 0.9], 0.5, 1, 0.0),
        ("hai_chuoi_cach_1_g05_gop", [0.9, 0.1, 0.8], 0.5, 1, 0.5),
        ("hai_chuoi_cach_2_g05_khong_gop", [0.9, 0.1, 0.1, 0.8], 0.5, 1, 0.5),
        ("hai_chuoi_cach_2_g1_gop", [0.8, 0.1, 0.1, 0.9], 0.5, 1, 1.0),
        ("gop_roi_moi_du_k2", [0.9, 0.1, 0.9, 0.1, 0.1, 0.1, 0.9], 0.5, 2, 0.5),
        ("diem_bang_nhau_lay_som", [0.2, 0.8, 0.8, 0.2], 0.5, 1, 0.0),
        ("toan_duoi_nguong", [0.3, 0.4, 0.2], 0.5, 1, 1.0),
        ("cuoi_chuoi_cham_cuoi_tep", [0.1, 0.1, 0.9, 0.9], 0.5, 2, 0.0),
    ]
    return [{"ten": ten, "p": p, "nguong": th, "k": k, "g": g, "su_kien": gop(p, th, k, g)} for ten, p, th, k, g in ca]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("diem")
    ap.add_argument("ra")
    ap.add_argument("--nguong", type=float, required=True)
    ap.add_argument("--k", type=int, default=1)
    ap.add_argument("--g", type=float, default=0.0)
    a = ap.parse_args()
    t, p = doc_diem(a.diem)
    ev = gop(p, a.nguong, a.k, a.g, t0=t)
    with open(a.ra, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["t_su_kien", "t_dau", "t_cuoi", "so_cua_so", "p_max", "i_max"])
        w.writeheader()
        w.writerows(ev)
    gio = (t[-1] + CUA_SO) / 3600 if t else 0
    print(f"{len(ev)} su kien trong {gio:.2f} gio ({len(ev) / gio if gio else 0:.1f} su kien/gio)")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--ghi-vector-thu":
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vector_thu_gop_su_kien.json")
        json.dump(vector_thu(), open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("Da ghi", p)
    else:
        main()
