"""Phân tích kết quả kiểm tra mô hình nền trên tập testing (Protocol mục 8).

Đầu vào
  results/ei_du_lieu_mo_hinh_nen.csv            danh sách đoạn (nguồn, nhóm, mức đỉnh) do chuan_bi_du_lieu_ei.py tạo
  results/<ten>_diem_tung_mau.csv               điểm từng mẫu testing lấy từ Edge Impulse (cột: file, label, p_cough)
  data/esc50/ESC-50-master/meta/esc50.csv       tên lớp ESC-50 (chỉ dùng để gọi tên lớp gây báo nhầm)
Đầu ra
  results/<ten>_chi_so.json                     toàn bộ chỉ số
  in ra bảng tóm tắt

Quy ước: dương tính = cough. Độ nhạy = TP/(TP+FN); độ đặc hiệu = TN/(TN+FP).
Ngưỡng chính 0,5 (lớp có xác suất cao hơn). Khoảng tin cậy 95%:
  Wilson (coi từng đoạn độc lập) và bootstrap theo nhóm (lấy lại cả bản ghi/người nói/đoạn gốc ESC-50,
  2.000 lần, seed 2026) vì các đoạn cắt từ cùng một bản ghi không độc lập.
Chạy:  python3 tools/mo_hinh_nen/phan_tich_kiem_tra.py mo_hinh_nen_v1
"""
import csv
import json
import math
import sys
from collections import Counter, defaultdict

import numpy as np

SEED = 2026
NGUONG = [0.5, 0.6, 0.7, 0.8, 0.9, 0.95]
CUA_SO_MOI_GIO = 7200  # cửa sổ 1 s, bước 0,5 s


def wilson(k, n, z=1.96):
    if n == 0:
        return [float("nan")] * 2
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 4), round(c + h, 4)]


def nhom_bootstrap(r):
    if r["source"] == "ESC-50":
        return "esc_" + "-".join(r["source_file"].split("-")[:2])
    if r["source"] == "CommonVoice-vi":
        return "cv_" + r["group"]
    return "cvd_" + r["group"]


def auc(y, p):
    y = np.asarray(y); p = np.asarray(p)
    order = np.argsort(p, kind="mergesort")
    ranks = np.empty(len(p)); ranks[order] = np.arange(1, len(p) + 1)
    for v in np.unique(p):  # hạng trung bình cho giá trị bằng nhau
        m = p == v
        ranks[m] = ranks[m].mean()
    n1 = y.sum(); n0 = len(y) - n1
    return float((ranks[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def chi_so(y, p, t):
    pred = p >= t
    tp = int(((y == 1) & pred).sum()); fn = int(((y == 1) & ~pred).sum())
    tn = int(((y == 0) & ~pred).sum()); fp = int(((y == 0) & pred).sum())
    se = tp / (tp + fn); sp = tn / (tn + fp)
    pr = tp / (tp + fp) if tp + fp else float("nan")
    f1 = 2 * pr * se / (pr + se) if tp else 0.0
    return {"nguong": t, "TP": tp, "FN": fn, "TN": tn, "FP": fp,
            "do_nhay": round(se, 4), "do_nhay_wilson95": wilson(tp, tp + fn),
            "do_dac_hieu": round(sp, 4), "do_dac_hieu_wilson95": wilson(tn, tn + fp),
            "do_chinh_xac_duong": round(pr, 4), "F1": round(f1, 4),
            "do_chinh_xac_tong": round((tp + tn) / len(y), 4),
            "do_chinh_xac_can_bang": round((se + sp) / 2, 4),
            "bao_nham_moi_gio_uoc_luong_bi_quan": round((1 - sp) * CUA_SO_MOI_GIO, 1)}


def main(ten):
    man = {r["file"].split("/")[-1][:-4]: r for r in csv.DictReader(open("results/ei_du_lieu_mo_hinh_nen.csv", encoding="utf-8"))
           if r["split"] == "testing"}
    diem = list(csv.DictReader(open(f"results/{ten}_diem_tung_mau.csv", encoding="utf-8")))
    esc_ten = {}
    try:
        for m in csv.DictReader(open("data/esc50/ESC-50-master/meta/esc50.csv", encoding="utf-8")):
            esc_ten[m["filename"]] = m["category"]
    except FileNotFoundError:
        pass
    rows = []
    for d in diem:
        r = man[d["file"]]
        assert r["label"] == d["label"], d
        rows.append({**r, "p": float(d["p_cough"]), "y": 1 if d["label"] == "cough" else 0, "g": nhom_bootstrap(r)})
    thieu = set(man) - {d["file"] for d in diem}
    y = np.array([r["y"] for r in rows]); p = np.array([r["p"] for r in rows])
    out = {"mo_hinh": ten, "so_mau": len(rows), "so_ho": int(y.sum()), "so_khong_ho": int((1 - y).sum()),
           "mau_thieu_so_voi_danh_sach": len(thieu),
           "ROC_AUC": round(auc(y, p), 4),
           "theo_nguong": [chi_so(y, p, t) for t in NGUONG]}
    # bootstrap theo nhóm
    rng = np.random.default_rng(SEED)
    gi = defaultdict(list)
    for i, r in enumerate(rows):
        gi[r["g"]].append(i)
    gpos = [v for v in gi.values() if y[v[0]] == 1]; gneg = [v for v in gi.values() if y[v[0]] == 0]
    se_b, sp_b, f1_b = [], [], []
    for _ in range(2000):
        ip = np.concatenate([gpos[j] for j in rng.integers(0, len(gpos), len(gpos))])
        ineg = np.concatenate([gneg[j] for j in rng.integers(0, len(gneg), len(gneg))])
        idx = np.concatenate([ip, ineg]).astype(int)
        c = chi_so(y[idx], p[idx], 0.5)
        se_b.append(c["do_nhay"]); sp_b.append(c["do_dac_hieu"]); f1_b.append(c["F1"])
    q = lambda a: [round(float(np.percentile(a, 2.5)), 4), round(float(np.percentile(a, 97.5)), 4)]
    out["bootstrap_nhom_95_nguong_0_5"] = {"so_nhom_ho": len(gpos), "so_nhom_khong_ho": len(gneg),
                                           "do_nhay": q(se_b), "do_dac_hieu": q(sp_b), "F1": q(f1_b)}
    # theo mức đỉnh (ho) và theo nguồn (không ho)
    bins = [(-35.01, -29), (-29, -19), (-19, -2.99)]
    out["do_nhay_theo_muc_dinh_dBFS"] = []
    for lo, hi in bins:
        m = (y == 1) & np.array([lo <= float(r["peak_dbfs"]) < hi for r in rows])
        k = int((p[m] >= 0.5).sum()); n = int(m.sum())
        out["do_nhay_theo_muc_dinh_dBFS"].append({"muc": f"{round(lo)}..{round(hi)}", "n": n, "dung": k,
                                                   "do_nhay": round(k / n, 4) if n else None, "wilson95": wilson(k, n)})
    out["do_dac_hieu_theo_nguon"] = []
    for src in ("ESC-50", "CommonVoice-vi"):
        m = (y == 0) & np.array([r["source"] == src for r in rows])
        k = int((p[m] < 0.5).sum()); n = int(m.sum())
        out["do_dac_hieu_theo_nguon"].append({"nguon": src, "n": n, "dung": k, "do_dac_hieu": round(k / n, 4), "wilson95": wilson(k, n)})
    fp_lop = Counter(); n_lop = Counter()
    for r in rows:
        if r["source"] == "ESC-50":
            c = esc_ten.get(r["source_file"], r["note"]); n_lop[c] += 1
            if r["p"] >= 0.5:
                fp_lop[c] += 1
    out["lop_ESC50_bao_nham_nhieu_nhat"] = [{"lop": c, "bao_nham": k, "tong": n_lop[c], "ti_le": round(k / n_lop[c], 3)}
                                            for c, k in fp_lop.most_common(10)]
    out["ho_bi_bo_sot_thap_nhat"] = [{"file": r["file"].split("/")[-1], "p_cough": r["p"], "peak_dbfs": r["peak_dbfs"]}
                                    for r in sorted([r for r in rows if r["y"] == 1], key=lambda r: r["p"])[:10]]
    json.dump(out, open(f"results/{ten}_chi_so.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    c = out["theo_nguong"][0]; b = out["bootstrap_nhom_95_nguong_0_5"]
    print(f"{ten}: {len(rows)} mau ({out['so_ho']} ho, {out['so_khong_ho']} khong ho); thieu {len(thieu)}")
    print(f"Nguong 0,5: do nhay {c['do_nhay']:.4f} (bootstrap {b['do_nhay']}), do dac hieu {c['do_dac_hieu']:.4f} (bootstrap {b['do_dac_hieu']}), F1 {c['F1']:.4f}, AUC {out['ROC_AUC']}")
    print(f"Ma tran: TP {c['TP']} FN {c['FN']} / FP {c['FP']} TN {c['TN']}")
    for t in out["theo_nguong"]:
        print(f"  t={t['nguong']}: Se {t['do_nhay']:.4f} Sp {t['do_dac_hieu']:.4f} F1 {t['F1']:.4f} bao nham/gio (bi quan) {t['bao_nham_moi_gio_uoc_luong_bi_quan']}")
    print("Do nhay theo muc:", [(x["muc"], x["n"], x["do_nhay"]) for x in out["do_nhay_theo_muc_dinh_dBFS"]])
    print("Do dac hieu theo nguon:", [(x["nguon"], x["n"], x["do_dac_hieu"]) for x in out["do_dac_hieu_theo_nguon"]])
    print("Lop ESC-50 bao nham:", [(x["lop"], x["bao_nham"], x["tong"]) for x in out["lop_ESC50_bao_nham_nhieu_nhat"]])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "mo_hinh_nen_v1"))
