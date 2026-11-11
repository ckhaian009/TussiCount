"""Chấm phần để chấm của tầng kiểm định 3 (Protocol 7.3, 9, 13, 16.1–16.3, 10.6; việc t33).

Hai bước, chạy trên máy tính của Nhóm (âm thanh KTX không rời máy):

1) chay-mot-lan  — chạy MỘT LẦN mô hình đã đóng băng trên hai tệp phần để chấm.
   python3 tools/cham/cham_phan_de_cham.py chay-mot-lan --bo-chay <chay_mo_hinh> --nguong θ --k k --g g \
       --ra <thu_muc_ktx> <tep1.wav> <tep2.wav>
   Ghi điểm mọi cửa sổ (diem_<tep>.csv, dùng cho đường cong 16.3), su_kien.csv (theo θ, k, g đã đóng băng) và
   lan_chay.json (SHA-256 của bộ chạy và hai tệp, thời điểm chạy). Có lan_chay.json rồi thì từ chối chạy lại.

2) cham  — tính chỉ số sau khi đã gán nhãn 2 giờ và xác minh mù 2,5 giờ.
   python3 tools/cham/cham_phan_de_cham.py cham --thu-muc <thu_muc_ktx> --khoi khoi.csv \
       --nhan <id_khoi>=<nhan.txt> ... --phieu-mu phieu_mu.csv --khoa-mu khoa_mu.csv [--ra results/cham_tang3.json]
   Chỉ số:
     phát hiện sai mỗi giờ trên 4,5 giờ = (sự kiện không ghép được trong 2 giờ gán nhãn đầy đủ + đoạn thiết bị
       bị nghe là không ho trong 2,5 giờ xác minh mù) / 4,5; KTC Poisson chính xác 95% (tiêu chí: ≤ 4)
     độ nhạy, giá trị dự báo dương với tiếng ho tự nhiên trên 2 giờ gán nhãn (thăm dò, kèm n)
     16.1 sai số số đếm theo 24 khoảng 5 phút; 16.2 độ đặc hiệu theo đoạn 3 s; 16.3 đường cong theo ngưỡng
     (giữ bộ lọc đã đóng băng, chỉ để mô tả); 10.6 phát hiện sai theo loại âm thanh (phần xác minh mù)
   Nhãn "?" (không chắc) bị loại khỏi phân tích chính: sự kiện ghép với nhãn "?" không tính đúng cũng không tính sai.
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "chay_mo_hinh"))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "phan_tich"))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "gan_nhan"))
from gop_su_kien import CUA_SO, doc_diem, gop  # noqa: E402
from ghep_su_kien import ghep  # noqa: E402
import thong_ke as tk  # noqa: E402
from gan_nhan import doc_nhan_audacity, gop_trang  # noqa: E402

NGUONG_CONG = [round(0.30 + 0.05 * i, 2) for i in range(14)] + [0.97, 0.99]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def chay_mot_lan(a):
    os.makedirs(a.ra, exist_ok=True)
    khoa = os.path.join(a.ra, "lan_chay.json")
    if os.path.exists(khoa):
        sys.exit(f"Da chay mot lan roi ({khoa}). Protocol 7.3: phan de cham chi chay mot lan.")
    ev_all = []
    info = {"thoi_diem": dt.datetime.now().isoformat(timespec="seconds"), "bo_chay": a.bo_chay, "sha_bo_chay": sha(a.bo_chay),
            "nguong": a.nguong, "k": a.k, "g": a.g, "tep": {}}
    for w in a.tep:
        ten = os.path.basename(w)
        diem = os.path.join(a.ra, f"diem_{os.path.splitext(ten)[0]}.csv")
        subprocess.run([a.bo_chay, "dai", w, diem], check=True)
        t, p = doc_diem(diem)
        for e in gop(p, a.nguong, a.k, a.g, t0=t):
            ev_all.append({"tep": ten, **e})
        info["tep"][ten] = {"sha256": sha(w), "so_gio": (t[-1] + CUA_SO) / 3600, "diem": os.path.basename(diem)}
    with open(os.path.join(a.ra, "su_kien.csv"), "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=["tep", "t_su_kien", "t_dau", "t_cuoi", "so_cua_so", "p_max", "i_max"])
        wr.writeheader()
        wr.writerows(ev_all)
    json.dump(info, open(khoa, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Xong: {len(ev_all)} su kien. Da khoa lan chay: {khoa}")


def su_kien_trong(ev, tep, a, b):
    return [e for e in ev if e["tep"] == tep and a <= e["t_su_kien"] < b]


def cham_khoi(ev_khoi, ho, kc, a):
    """Ghép một khối 30 phút. ho, kc: thời điểm ho và '?' (giây tính từ đầu khối). Trả về (tp, fn, fp, D/R 5 phút)."""
    D = [e["t_su_kien"] - a for e in ev_khoi]
    R = gop_trang(ho)
    kq = ghep(R, D, 1.0)
    # sự kiện không ghép được nhưng nằm trong 1 s quanh nhãn '?' thì loại
    fp = [j for j in kq["fp"] if not any(abs(D[j] - t) <= 1.0 for t in kc)]
    d5 = [sum(1 for t in D if i * 300 <= t < (i + 1) * 300) for i in range(6)]
    r5 = [sum(1 for t in R if i * 300 <= t < (i + 1) * 300) for i in range(6)]
    return kq["tp"], len(R) - kq["tp"], len(fp), d5, r5


def cham(a):
    info = json.load(open(os.path.join(a.thu_muc, "lan_chay.json"), encoding="utf-8"))
    ev = [{**r, "t_su_kien": float(r["t_su_kien"])} for r in csv.DictReader(open(os.path.join(a.thu_muc, "su_kien.csv"), encoding="utf-8"))]
    khoi = {k["id"]: k for k in csv.DictReader(open(a.khoi, encoding="utf-8"))}
    nhan = dict(x.split("=", 1) for x in a.nhan)
    tong = {"tp": 0, "fn": 0, "fp": 0}
    D, R = [], []
    for kid, tep_nhan in nhan.items():
        k = khoi[kid]
        bd, kt = float(k["bat_dau_s"]), float(k["ket_thuc_s"])
        ho, kc = doc_nhan_audacity(tep_nhan)
        tp, fn, fp, d5, r5 = cham_khoi(su_kien_trong(ev, k["tep"], bd, kt), ho, kc, bd)
        tong["tp"] += tp
        tong["fn"] += fn
        tong["fp"] += fp
        D += d5
        R += r5
    gio_nhan = 0.5 * len(nhan)
    # xác minh mù
    khoa = {r["doan"]: r for r in csv.DictReader(open(a.khoa_mu, encoding="utf-8"))}
    phieu = list(csv.DictReader(open(a.phieu_mu, encoding="utf-8")))
    tb = [p for p in phieu if khoa[p["doan"]]["nguon"] == "thiet_bi"]
    nn = [p for p in phieu if khoa[p["doan"]]["nguon"] == "ngau_nhien"]
    tb_dung = sum(p["co_ho"].strip() == "1" for p in tb)
    tb_sai = sum(p["co_ho"].strip() == "0" for p in tb)
    tb_kc = len(tb) - tb_dung - tb_sai
    gio_mu = sum(float(k["ket_thuc_s"]) - float(k["bat_dau_s"]) for k in khoi.values() if k["vai_tro"] == "xac_minh_mu") / 3600
    # 16.2: đoạn ngẫu nhiên được nghe là không ho -> âm; đúng âm khi không trùng sự kiện thiết bị nào
    am = [p for p in nn if p["co_ho"].strip() == "0"]
    dung_am = 0
    for p in am:
        kk = khoa[p["doan"]]
        t = float(kk["tam_s"])
        if not any(e["tep"] == kk["tep"] and abs(e["t_su_kien"] - t) <= 1.5 for e in ev):
            dung_am += 1
    sai_tong = tong["fp"] + tb_sai
    gio = gio_nhan + gio_mu
    r, lo, hi = tk.poisson_chinh_xac(sai_tong, gio)
    s = tk.wilson(tong["tp"], tong["tp"] + tong["fn"])
    ppv = tk.wilson(tong["tp"], tong["tp"] + tong["fp"])
    loai = {}
    for p in tb:
        if p["co_ho"].strip() == "0":
            loai[p["loai_am"].strip() or "khac"] = loai.get(p["loai_am"].strip() or "khac", 0) + 1
    # 16.3: đường cong theo ngưỡng trên 2 giờ gán nhãn (giữ k, g)
    cong = []
    for th in NGUONG_CONG:
        tp = fn = fp = 0
        for kid, tep_nhan in nhan.items():
            k = khoi[kid]
            bd, kt = float(k["bat_dau_s"]), float(k["ket_thuc_s"])
            tt, pp = doc_diem(os.path.join(a.thu_muc, info["tep"][k["tep"]]["diem"]))
            ev_k = [{"t_su_kien": e["t_su_kien"]} for e in gop(pp, th, info["k"], info["g"], t0=tt) if bd <= e["t_su_kien"] < kt]
            ho, kc = doc_nhan_audacity(tep_nhan)
            x = cham_khoi([{"t_su_kien": e["t_su_kien"]} for e in ev_k], ho, kc, bd)
            tp, fn, fp = tp + x[0], fn + x[1], fp + x[2]
        cong.append({"nguong": th, "do_nhay": tp / (tp + fn) if tp + fn else None, "sai_moi_gio": fp / gio_nhan})
    kq = {
        "lan_chay": info,
        "phat_hien_sai_moi_gio": {"uoc_luong": r, "ktc95": [lo, hi], "so_sai": sai_tong, "so_gio": gio,
                                  "tu_gan_nhan": tong["fp"], "tu_xac_minh_mu": tb_sai, "khong_chac_mu": tb_kc,
                                  "dat_tieu_chi_le_4": r <= 4.0},
        "do_nhay_ho_tu_nhien": {"uoc_luong": s[0], "ktc95": [s[1], s[2]], "tp": tong["tp"], "n": tong["tp"] + tong["fn"]},
        "gia_tri_du_bao_duong_2h": {"uoc_luong": ppv[0], "ktc95": [ppv[1], ppv[2]]},
        "f1_2h": tk.f1(s[0], ppv[0]) if tong["tp"] else 0.0,
        "sai_so_so_dem_16_1": tk.sai_so_so_dem(D, R),
        "do_dac_hieu_16_2": dict(zip(("uoc_luong", "ktc_duoi", "ktc_tren"), tk.wilson(dung_am, len(am)))) | {"n_am": len(am)},
        "duong_cong_16_3": cong,
        "phat_hien_sai_theo_loai_10_6": {k: {"so": v, "moi_gio": v / gio_mu} for k, v in loai.items()},
        "ppv_xac_minh_mu": tb_dung / (tb_dung + tb_sai) if tb_dung + tb_sai else None,
    }
    s_json = json.dumps(kq, ensure_ascii=False, indent=1, default=float)
    if a.ra:
        open(a.ra, "w", encoding="utf-8").write(s_json)
    print(f"Phat hien sai: {r:.2f}/gio (KTC {lo:.2f}–{hi:.2f}), {sai_tong} su kien sai trong {gio:.2f} gio")
    print(f"Do nhay ho tu nhien (2 gio): {s[0] * 100:.1f}% ({tong['tp']}/{tong['tp'] + tong['fn']})")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="lenh", required=True)
    c = sub.add_parser("chay-mot-lan")
    c.add_argument("--bo-chay", required=True)
    c.add_argument("--nguong", type=float, required=True)
    c.add_argument("--k", type=int, required=True)
    c.add_argument("--g", type=float, required=True)
    c.add_argument("--ra", required=True)
    c.add_argument("tep", nargs=2)
    d = sub.add_parser("cham")
    d.add_argument("--thu-muc", required=True)
    d.add_argument("--khoi", required=True)
    d.add_argument("--nhan", nargs="+", required=True)
    d.add_argument("--phieu-mu", required=True)
    d.add_argument("--khoa-mu", required=True)
    d.add_argument("--ra")
    a = ap.parse_args()
    chay_mot_lan(a) if a.lenh == "chay-mot-lan" else cham(a)


if __name__ == "__main__":
    sys.exit(main())
