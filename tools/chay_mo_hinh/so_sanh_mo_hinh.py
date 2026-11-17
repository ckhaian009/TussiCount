"""So sánh mô hình nền v1 (Impulse #2) và mô hình tăng cường v2 (Impulse #3) theo quy tắc ghi trước ngày 10/11 19:20
(results/mo_hinh_nen_nhat_ky_thi_nghiem.md; Protocol sửa đổi 16.7).

  1. Mỗi mô hình đã có tổ hợp ngưỡng và bộ lọc của chính nó, chọn bằng chon_nguong.py theo mục 8 (độ nhạy trên luồng
     kiểm tra sạch, phát hiện sai trên phần để sửa ≤ 4 sự kiện/giờ) — đầu vào là hai tệp JSON của chon_nguong.py.
  2. Tính độ nhạy của mỗi mô hình trên luồng kiểm tra tăng cường (tập kiểm tra, kho RIR kiểm tra), ở tổ hợp của chính nó.
  3. Chọn mô hình có độ nhạy cao hơn; bằng nhau thì lấy mô hình có phát hiện sai trên phần để sửa thấp hơn; vẫn bằng
     thì giữ v1. Mô hình không có tổ hợp hợp lệ (không tổ hợp nào ≤ 4 sự kiện/giờ) không được chọn.
  4. Báo cáo cho cả hai mô hình: từng đoạn của tập kiểm tra sạch, tập độ bền theo SNR, luồng sạch, luồng tăng cường,
     phần để sửa.

Chạy:
  python3 tools/chay_mo_hinh/so_sanh_mo_hinh.py \\
      --chon results/chon_nguong_v1.json results/chon_nguong_v2.json \\
      --luong-tc data/luong_kiem_tra/diem_tang_cuong_v1.csv data/luong_kiem_tra/diem_tang_cuong_v2.csv \\
      --luong-tc-chuan results/luong_kiem_tra_tang_cuong.csv \\
      [--ngan diem_doan_v1.csv diem_doan_v2.csv --bang-ben results/ei_kiem_tra_ben.csv] \\
      --ra results/chon_mo_hinh_16_7.json
  (tệp --ngan: đầu ra chế độ `ngan` của bộ chạy trên các đoạn của tập kiểm tra sạch và tập độ bền; nhãn lấy theo thư
  mục cough/noise trong đường dẫn; nhóm SNR của tập độ bền lấy từ bảng kê nếu có)
Thử: python3 tools/chay_mo_hinh/so_sanh_mo_hinh.py --thu
"""
import argparse
import csv
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "phan_tich"))
from gop_su_kien import CUA_SO, doc_diem, gop  # noqa: E402
from ghep_su_kien import ghep  # noqa: E402

TEN = ("v1", "v2")


def do_nhay_luong(t, p, chuan, c):
    ev = gop(p, c["nguong"], c["k"], c["g"], t0=t)
    kq = ghep(chuan, [e["t_su_kien"] for e in ev], 1.0)
    gio = (t[-1] + CUA_SO) / 3600
    return {"do_nhay": kq["tp"] / kq["n_chuan"], "tp": kq["tp"], "n": kq["n_chuan"],
            "su_kien_khong_ghep_moi_gio": (len(ev) - kq["tp"]) / gio}


def sai_gio(c):
    """Phát hiện sai mỗi giờ của tổ hợp đã chọn: trên phần để sửa, hoặc trên đối chứng âm (mục 8 câu cuối, 16.23)."""
    return c["sai_moi_gio_phan_de_sua"] if "sai_moi_gio_phan_de_sua" in c else c["sai_moi_gio_doi_chung"]


def chon_mo_hinh(kq):
    """kq: {ten: {"chon": tổ hợp hoặc None, "luong_tc": {...}}}. Trả về (ten, ly_do)."""
    hop_le = [m for m in TEN if kq[m]["chon"] is not None]
    if not hop_le:
        return "v1", "khong mo hinh nao co to hop <= 4 su kien/gio; giu v1 (Protocol muc 8, truong hop cuoi)"
    if len(hop_le) == 1:
        return hop_le[0], "chi mo hinh nay co to hop hop le"
    a, b = (kq[m]["luong_tc"]["tp"] for m in TEN)
    if a != b:
        m = TEN[0] if a > b else TEN[1]
        return m, "do nhay cao hon tren luong tang cuong"
    fa, fb = (sai_gio(kq[m]["chon"]) for m in TEN)
    if fa != fb:
        m = TEN[0] if fa < fb else TEN[1]
        return m, "bang do nhay; phat hien sai tren phan de sua thap hon"
    return "v1", "bang ca hai; giu v1"


def theo_doan(path, nguong, nhom_ben):
    """Độ nhạy/độ đặc hiệu từng đoạn ở ngưỡng θ; tách tập sạch và tập độ bền (theo nhóm SNR)."""
    dem = {}
    for r in csv.DictReader(open(path, encoding="utf-8")):
        tep = r["tep"]
        nhan = "cough" if "/cough/" in tep else "noise"
        bo = "ben" if "ei_kiem_tra_ben" in tep else "sach"
        ten = os.path.splitext(os.path.basename(tep))[0]
        khoa = (bo, nhom_ben.get(ten, "tat_ca") if bo == "ben" else "tat_ca", nhan)
        d = dem.setdefault(khoa, [0, 0])
        d[0] += float(r["p_cough"]) >= nguong
        d[1] += 1
    ra = {}
    for (bo, nhom, nhan), (k, n) in sorted(dem.items()):
        ten = "do_nhay" if nhan == "cough" else "do_dac_hieu"
        v = k / n if nhan == "cough" else 1 - k / n
        ra[f"{bo}|{nhom}|{ten}"] = {"gia_tri": round(v, 4), "n": n}
    return ra


def chay(chon_json, luong_tc, chuan, ngan=None, nhom_ben=None):
    kq = {}
    for i, m in enumerate(TEN):
        cj = json.load(open(chon_json[i], encoding="utf-8"))
        c = cj["chon"]
        t, p = doc_diem(luong_tc[i])
        mot = {"chon": c, "duong_cong_luong_sach": [r for r in cj["duong_cong"] if r["k"] == 1 and r["g"] == 0.0]}
        mot["luong_tc"] = do_nhay_luong(t, p, chuan, c) if c else None
        if c:
            mot["luong_sach"] = {"do_nhay": c["do_nhay_luong"], "tp": c["tp"], "n": c["n"]}
            mot["phan_de_sua"] = {k: c.get(k) for k in ("sai_moi_gio_phan_de_sua", "so_sai", "so_khong_chac", "gio_phan_de_sua")}
            mot["doi_chung_am"] = {k: c.get(k) for k in ("sai_moi_gio_doi_chung", "so_su_kien_doi_chung", "gio_doi_chung")}
            if ngan:
                mot["theo_doan"] = theo_doan(ngan[i], c["nguong"], nhom_ben or {})
        kq[m] = mot
    m, ly_do = chon_mo_hinh(kq)
    return {"quy_tac": "nhat ky 10/11 19:20 (16.7)", "chon": m, "ly_do": ly_do, "mo_hinh": kq}


def thu():
    loi = []
    c = lambda tp, f: {"chon": {"sai_moi_gio_phan_de_sua": f}, "luong_tc": {"tp": tp}}  # noqa: E731
    cases = [
        ({"v1": c(50, 3.0), "v2": c(80, 3.9)}, "v2"),
        ({"v1": c(80, 3.0), "v2": c(50, 1.0)}, "v1"),
        ({"v1": c(60, 3.0), "v2": c(60, 2.0)}, "v2"),
        ({"v1": c(60, 2.0), "v2": c(60, 2.0)}, "v1"),
        ({"v1": {"chon": None, "luong_tc": None}, "v2": c(10, 1.0)}, "v2"),
        ({"v1": c(10, 1.0), "v2": {"chon": None, "luong_tc": None}}, "v1"),
        ({"v1": {"chon": None, "luong_tc": None}, "v2": {"chon": None, "luong_tc": None}}, "v1"),
    ]
    for i, (kq, mong) in enumerate(cases, 1):
        m, _ = chon_mo_hinh(kq)
        if m != mong:
            loi.append(f"tinh huong {i}: chon {m}, mong {mong}")
    # trọn quy trình trên luồng tổng hợp: v2 bắt được nhiều tiếng ho hơn trên luồng tăng cường
    import tempfile
    tmp = tempfile.mkdtemp(prefix="ssmh_")
    rng = random.Random(2026)
    n = 200
    chuan = [i * 8 + 0.3 for i in range(n)]
    for m, bat in (("v1", 0.4), ("v2", 0.8)):
        with open(os.path.join(tmp, f"luong_{m}.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["cua_so", "t_bat_dau_s", "p_cough", "ms_xu_ly"])
            for j in range(n * 16):
                t0 = j * 0.5
                p = 0.0
                if j % 16 == 0 and rng.random() < bat:
                    p = 0.95
                w.writerow([j, f"{t0:.4f}", p, 0.3])
        cj = {"duong_cong": [{"nguong": 0.5, "k": 1, "g": 0.0, "do_nhay_luong": 0.9, "tp": 180, "n": 200}],
              "chon": {"nguong": 0.5, "k": 1, "g": 0.0, "do_nhay_luong": 0.9, "tp": 180, "n": 200,
                       "sai_moi_gio_phan_de_sua": 2.0, "so_sai": 6, "so_khong_chac": 0, "gio_phan_de_sua": 3.0}}
        json.dump(cj, open(os.path.join(tmp, f"chon_{m}.json"), "w"))
    kq = chay([os.path.join(tmp, f"chon_{m}.json") for m in TEN], [os.path.join(tmp, f"luong_{m}.csv") for m in TEN], chuan)
    if kq["chon"] != "v2":
        loi.append(f"tron quy trinh: chon {kq['chon']}")
    d1, d2 = kq["mo_hinh"]["v1"]["luong_tc"]["do_nhay"], kq["mo_hinh"]["v2"]["luong_tc"]["do_nhay"]
    if not (0.3 < d1 < 0.5 and 0.7 < d2 < 0.9):
        loi.append(f"do nhay luong {d1:.2f} {d2:.2f}")
    print(f"7 tinh huong quy tac + tron quy trinh (v1 {d1:.1%}, v2 {d2:.1%} tren luong tong hop)")
    print("KET QUA:", "DAT" if not loi else "KHONG DAT: " + "; ".join(loi))
    return 0 if not loi else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--chon", nargs=2)
    ap.add_argument("--luong-tc", nargs=2)
    ap.add_argument("--luong-tc-chuan")
    ap.add_argument("--ngan", nargs=2)
    ap.add_argument("--bang-ben")
    ap.add_argument("--ra", default="results/chon_mo_hinh_16_7.json")
    ap.add_argument("--thu", action="store_true")
    a = ap.parse_args()
    if a.thu:
        return thu()
    if not (a.chon and a.luong_tc and a.luong_tc_chuan):
        ap.error("can --chon, --luong-tc, --luong-tc-chuan")
    chuan = [float(r["t_chuan"]) for r in csv.DictReader(open(a.luong_tc_chuan, encoding="utf-8"))]
    nhom_ben = {}
    if a.bang_ben and os.path.exists(a.bang_ben):
        for r in csv.DictReader(open(a.bang_ben, encoding="utf-8")):
            ten = os.path.splitext(os.path.basename(r.get("file", "")))[0]
            nhom_ben[ten] = r.get("nguon") or r.get("snr_db") or "tat_ca"
    kq = chay(a.chon, a.luong_tc, chuan, a.ngan, nhom_ben)
    json.dump(kq, open(a.ra, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for m in TEN:
        x = kq["mo_hinh"][m]
        if x["chon"]:
            c = x["chon"]
            print(f"{m}: θ {c['nguong']}, k {c['k']}, g {c['g']} | luong sach {c['do_nhay_luong']:.1%} | "
                  f"luong tang cuong {x['luong_tc']['do_nhay']:.1%} | sai/gio (de sua hoac doi chung am) {sai_gio(c):.2f}")
        else:
            print(f"{m}: khong co to hop hop le")
    print(f"CHON: {kq['chon']} ({kq['ly_do']}). Da ghi {a.ra}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
