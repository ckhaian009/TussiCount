"""Chọn ngưỡng và bộ lọc sau phân loại theo Protocol mục 8 (việc t19), và so sánh hai mô hình theo sửa đổi 16.7.

Lưới: ngưỡng θ ∈ {0,50; 0,55; …; 0,95; 0,97; 0,99}; số cửa sổ liền kề tối thiểu k ∈ {1; 2};
      khoảng nghỉ tối thiểu g ∈ {0; 0,5; 1} s (định nghĩa gộp ở gop_su_kien.py).
Với mỗi tổ hợp:
  - phát hiện sai mỗi giờ trên phần để sửa (sự kiện thiết bị báo đã được nghe xác minh, xem bên dưới);
  - độ nhạy trên luồng kiểm tra của dữ liệu mở (tao_luong_kiem_tra.py), ghép ±1 s một–một.
Chọn tổ hợp có độ nhạy cao nhất trong các tổ hợp có phát hiện sai ≤ 4 sự kiện/giờ; bằng nhau thì lấy phát hiện sai
thấp hơn, rồi ngưỡng cao hơn, rồi k lớn hơn, rồi g lớn hơn. Lưu toàn bộ đường cong.

Xác minh phần để sửa: ung_vien_phan_de_sua.py cắt đoạn 3 s quanh mọi sự kiện ở θ = 0,50, k = 1, g = 0 (tập lớn
nhất); người nghe điền cột co_ho (1 = có tiếng ho, 0 = không, ? = không chắc). Sự kiện của tổ hợp khác được gán
nhãn theo các ứng viên nằm trong nó (tổ hợp nào cũng chỉ gồm các cửa sổ ≥ 0,50): là tiếng ho nếu có ít nhất một
ứng viên được nghe là có ho. Sự kiện chỉ gồm ứng viên "?" không tính là phát hiện sai ở kết quả chính và được
đếm riêng.

Dòng lệnh:
  python3 tools/chay_mo_hinh/chon_nguong.py --ten v1 \
      --luong-diem diem_luong_sach.csv --luong-chuan results/luong_kiem_tra_sach.csv \
      [--sua-diem diem_sua_1.csv ... --sua-nhan nhan_ung_vien.csv] [--ra results/chon_nguong_v1.json]
Không có phần để sửa (chạy thử, hoặc trường hợp Protocol mục 8 cuối): bỏ --sua-*, công cụ chỉ in độ nhạy.
"""
import argparse
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "phan_tich"))
from gop_su_kien import CUA_SO, doc_diem, gop  # noqa: E402
from ghep_su_kien import ghep  # noqa: E402

NGUONG = [round(0.50 + 0.05 * i, 2) for i in range(10)] + [0.97, 0.99]
K = (1, 2)
G = (0.0, 0.5, 1.0)
TOI_DA_SAI = 4.0
THETA_UNG_VIEN = 0.50


def do_nhay_luong(t, p, chuan, th, k, g):
    ev = gop(p, th, k, g, t0=t)
    kq = ghep(chuan, [e["t_su_kien"] for e in ev], 1.0)
    gio = (t[-1] + CUA_SO) / 3600
    return kq["tp"] / kq["n_chuan"], kq["tp"], kq["n_chuan"], (len(ev) - kq["tp"]) / gio


def sai_phan_de_sua(tep_diem, nhan, th, k, g):
    """nhan: dict (tep, i_max cua ung vien) -> '1' | '0' | '?'. Trả về (so_sai, so_khong_chac, so_gio)."""
    sai = khong_chac = 0
    gio = 0.0
    for tep, (t, p) in tep_diem.items():
        gio += (t[-1] + CUA_SO) / 3600
        uv = gop(p, THETA_UNG_VIEN, 1, 0.0, t0=t)
        for e in gop(p, th, k, g, t0=t):
            trong = [u for u in uv if e["t_dau"] <= u["t_dau"] and u["t_cuoi"] <= e["t_cuoi"]]
            nh = [nhan.get((tep, u["i_max"]), "?") for u in trong]
            if "1" in nh:
                continue
            if all(x == "0" for x in nh) and nh:
                sai += 1
            else:
                khong_chac += 1
    return sai, khong_chac, gio


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ten", required=True)
    ap.add_argument("--luong-diem", required=True)
    ap.add_argument("--luong-chuan", required=True)
    ap.add_argument("--sua-diem", nargs="*", default=[])
    ap.add_argument("--sua-nhan")
    ap.add_argument("--ra")
    a = ap.parse_args()
    t, p = doc_diem(a.luong_diem)
    chuan = [float(r["t_chuan"]) for r in csv.DictReader(open(a.luong_chuan, encoding="utf-8"))]
    sua = {os.path.basename(f): doc_diem(f) for f in a.sua_diem}
    nhan = {}
    if a.sua_nhan:
        for r in csv.DictReader(open(a.sua_nhan, encoding="utf-8")):
            nhan[(r["tep"], int(r["i_max"]))] = r["co_ho"].strip()
    duong = []
    for th in NGUONG:
        for k in K:
            for g in G:
                s, tp, n, sai_luong = do_nhay_luong(t, p, chuan, th, k, g)
                row = {"nguong": th, "k": k, "g": g, "do_nhay_luong": s, "tp": tp, "n": n, "sai_moi_gio_luong_mo": sai_luong}
                if sua:
                    so_sai, kc, gio = sai_phan_de_sua(sua, nhan, th, k, g)
                    row.update(sai_moi_gio_phan_de_sua=so_sai / gio, so_sai=so_sai, so_khong_chac=kc, gio_phan_de_sua=gio)
                duong.append(row)
    chon = None
    if sua:
        hop_le = [r for r in duong if r["sai_moi_gio_phan_de_sua"] <= TOI_DA_SAI]
        if hop_le:
            chon = sorted(hop_le, key=lambda r: (-r["do_nhay_luong"], r["sai_moi_gio_phan_de_sua"], -r["nguong"], -r["k"], -r["g"]))[0]
    kq = {"mo_hinh": a.ten, "luong": os.path.basename(a.luong_chuan), "duong_cong": duong, "chon": chon,
          "quy_tac": "do nhay cao nhat trong cac to hop co phat hien sai <= 4/gio tren phan de sua"}
    if a.ra:
        json.dump(kq, open(a.ra, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Mo hinh {a.ten}: {len(duong)} to hop")
    for r in duong:
        if r["k"] == 1 and r["g"] == 0.0:
            extra = f", sai/gio phan de sua {r['sai_moi_gio_phan_de_sua']:.2f}" if sua else ""
            print(f"  nguong {r['nguong']:.2f}: do nhay {r['do_nhay_luong'] * 100:5.1f}% ({r['tp']}/{r['n']}){extra}")
    print("Chon:", chon)


if __name__ == "__main__":
    sys.exit(main())
