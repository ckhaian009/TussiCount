"""Phân tích chính H1, H2 và phân tích phụ 10.1–10.4 (Protocol mục 9, 10). Viết và thử trên dữ liệu mô phỏng
trước khi có dữ liệu thật; chạy một lần trên dữ liệu thật sau khi chấm.

Đầu vào (mỗi dòng một tiếng ho, đã ghép với sự kiện thiết bị bằng ghep_su_kien.py):
  tang1.csv  tầng kiểm định 1 (phát lại Coswara), cột:
             muc_dich (o | kiem_tra | so_sanh), loai_bo (0/1), buoi, khung_gio (on | yen), vi_tri (hanh_lang | phong),
             khoang_cach_m, do_lon (nho | vua | lon), do_lon_db (dB(A) đỉnh quy về 1 m), muc_tai_micro_dba,
             muc_on_nen_dba (LA90 của phút), snr_db, loai_ho (sau | nong), nguoi (mã người trong Coswara), duoc_ghep (0/1)
  tang2.csv  tầng kiểm định 2 (ho thật), cột: nguoi (NTG01…), khoang_cach_m, muc_tai_micro_dba, muc_on_nen_dba, snr_db,
             loai_bo (0/1), duoc_ghep (0/1)
Đầu ra: results/phan_tich_h1_h2.json và bảng tóm tắt in ra màn hình.

Chạy:  python3 tools/phan_tich/phan_tich_h1_h2.py --tang1 tang1.csv --tang2 tang2.csv --ra results/phan_tich_h1_h2.json
Thử:   python3 tools/phan_tich/phan_tich_h1_h2.py --mo-phong   (tạo dữ liệu mô phỏng có hiệu ứng đã biết rồi phân tích)
"""
import argparse
import json
import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import thong_ke as tk  # noqa: E402

SEED = 2026
CONG_THUC_H1 = "duoc_ghep ~ khoang_cach_m + C(vi_tri, Treatment('hanh_lang')) + do_lon_db + muc_on_nen_dba + C(loai_ho) + C(buoi)"


def du_doan_tb(fit, df, **dat):
    """Dự đoán trung bình trên toàn bộ dòng của df sau khi đặt các biến trong `dat` (chuẩn hoá theo phân bố
    loại ho và buổi quan sát được)."""
    d = df.copy()
    for k, v in dat.items():
        d[k] = v
    return float(np.mean(fit.predict(d)))


def h1(t1, B=1000):
    d = t1[(t1.muc_dich == "o") & (t1.loai_bo == 0)].copy()
    fit = tk.logistic_cum(d, CONG_THUC_H1, "nguoi")
    ci = fit.conf_int()
    ten_phong = [k for k in fit.params.index if k.startswith("C(vi_tri")][0]
    he_so = {k: {"b": float(fit.params[k]), "ktc": [float(ci.loc[k, 0]), float(ci.loc[k, 1])], "p": float(fit.pvalues[k])}
             for k in fit.params.index}
    yen = d[d.khung_gio == "yen"].muc_on_nen_dba.median()
    on = d[d.khung_gio == "on"].muc_on_nen_dba.median()
    vua = d[d.do_lon == "vua"].do_lon_db.median()
    lon = d[d.do_lon == "lon"].do_lon_db.median()
    nho = d[d.do_lon == "nho"].do_lon_db.median()
    ref = dict(vi_tri="hanh_lang", khoang_cach_m=3.0, do_lon_db=vua, muc_on_nen_dba=yen)

    def cac_muc_giam(f, dd):
        r = dict(ref)
        p_ref = du_doan_tb(f, dd, **r)
        giam = {
            "cua_dong": p_ref - du_doan_tb(f, dd, **{**r, "vi_tri": "phong"}),
            "khoang_cach_1_den_5m": du_doan_tb(f, dd, **{**r, "khoang_cach_m": 1.0}) - du_doan_tb(f, dd, **{**r, "khoang_cach_m": 5.0}),
            "do_lon_lon_den_nho": du_doan_tb(f, dd, **{**r, "do_lon_db": lon}) - du_doan_tb(f, dd, **{**r, "do_lon_db": nho}),
            "muc_on_yen_den_on": du_doan_tb(f, dd, **{**r, "muc_on_nen_dba": yen}) - du_doan_tb(f, dd, **{**r, "muc_on_nen_dba": on}),
        }
        return p_ref, giam

    p_ref, giam = cac_muc_giam(fit, d)
    # KTC bootstrap theo người Coswara cho các mức giảm (mô tả thêm, tiêu chí dùng ước lượng điểm)
    rng = np.random.default_rng(SEED)
    nguoi = d.nguoi.unique()
    nhom = {n: g for n, g in d.groupby("nguoi")}
    bs = {k: [] for k in giam}
    for _ in range(B):
        chon = rng.choice(nguoi, len(nguoi), replace=True)
        db = pd.concat([nhom[n].assign(nguoi=f"{n}_{i}") for i, n in enumerate(chon)], ignore_index=True)
        try:
            fb = tk.logistic_cum(db, CONG_THUC_H1, "nguoi")
        except Exception:
            continue
        _, gb = cac_muc_giam(fb, db)
        for k, v in gb.items():
            bs[k].append(v)
    ktc = {k: [float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))] for k, v in bs.items() if v}
    a_kc = he_so["khoang_cach_m"]["b"] < 0 and he_so["khoang_cach_m"]["ktc"][1] < 0
    a_on = he_so["muc_on_nen_dba"]["b"] < 0 and he_so["muc_on_nen_dba"]["ktc"][1] < 0
    b_cua = all(giam["cua_dong"] > v for k, v in giam.items() if k != "cua_dong")
    return {"n": int(len(d)), "so_nguoi": int(len(nguoi)), "he_so": he_so, "ten_he_so_phong": ten_phong,
            "dieu_kien_tham_chieu": {k: (float(v) if not isinstance(v, str) else v) for k, v in ref.items()},
            "do_nhay_du_doan_tham_chieu": p_ref, "muc_giam": giam, "ktc_bootstrap_muc_giam": ktc, "so_vong_bootstrap": B,
            "tieu_chi": {"a_khoang_cach": a_kc, "a_muc_on": a_on, "b_cua_lon_nhat": b_cua, "ung_ho_H1": a_kc and a_on and b_cua}}


def h2(t1, t2, B=10000):
    a = t2[(t2.loai_bo == 0) & t2.khoang_cach_m.isin([1.0, 3.0])]
    b = t1[(t1.muc_dich == "o") & (t1.loai_bo == 0) & (t1.vi_tri == "hanh_lang") & (t1.khung_gio == "yen")
           & (t1.do_lon == "vua") & t1.khoang_cach_m.isin([1.0, 3.0])]
    cum_a = [(int(g.duoc_ghep.sum()), int(len(g))) for _, g in a.groupby("nguoi")]
    cum_b = [(int(g.duoc_ghep.sum()), int(len(g))) for _, g in b.groupby("nguoi")]
    est, lo, hi, _ = tk.chenh_do_nhay_bootstrap(cum_a, cum_b, B=B)
    so_nguoi = len(cum_a)
    return {"do_nhay_ho_that": tk.wilson(int(a.duoc_ghep.sum()), len(a)), "n_ho_that": int(len(a)), "so_nguoi_ho_that": so_nguoi,
            "do_nhay_phat_lai": tk.wilson(int(b.duoc_ghep.sum()), len(b)), "n_phat_lai": int(len(b)),
            "chenh_lech": est, "ktc_bootstrap": [lo, hi], "so_vong_bootstrap": B,
            "ung_ho_H2": bool(hi < 0), "tham_do": so_nguoi < 6}


def phan_tich_phu(t1, t2, B=1000):
    import statsmodels.formula.api as smf
    d = t1[(t1.muc_dich == "o") & (t1.loai_bo == 0)].copy()
    hl = d[d.vi_tri == "hanh_lang"]
    f1 = tk.logistic_cum(hl, "duoc_ghep ~ snr_db", "nguoi")
    b0, b1 = float(f1.params["Intercept"]), float(f1.params["snr_db"])
    out = {"10_1": {"b0": b0, "b1": b1, "snr50": tk.snr_tai_do_nhay(b0, b1, 0.5), "snr80": tk.snr_tai_do_nhay(b0, b1, 0.8)}}
    rng = np.random.default_rng(SEED)
    nhom = {n: g for n, g in hl.groupby("nguoi")}
    ns = list(nhom)
    s50, s80 = [], []
    for _ in range(B):
        db = pd.concat([nhom[n] for n in rng.choice(ns, len(ns))], ignore_index=True)
        try:
            p = smf.logit("duoc_ghep ~ snr_db", data=db).fit(disp=0).params
        except Exception:
            continue
        if p["snr_db"] > 0:
            s50.append(tk.snr_tai_do_nhay(p["Intercept"], p["snr_db"], 0.5))
            s80.append(tk.snr_tai_do_nhay(p["Intercept"], p["snr_db"], 0.8))
    out["10_1"]["ktc_snr50"] = [float(np.quantile(s50, 0.025)), float(np.quantile(s50, 0.975))]
    out["10_1"]["ktc_snr80"] = [float(np.quantile(s80, 0.025)), float(np.quantile(s80, 0.975))]
    f2 = tk.logistic_cum(d, "duoc_ghep ~ snr_db + C(vi_tri, Treatment('hanh_lang'))", "nguoi")
    k = [x for x in f2.params.index if x.startswith("C(vi_tri")][0]
    ci = f2.conf_int().loc[k]
    out["10_2"] = {"he_so_phong": float(f2.params[k]), "ktc": [float(ci[0]), float(ci[1])],
                   "dien_giai": "chua 0: phu hop co che suy hao muc am" if ci[0] < 0 < ci[1]
                   else ("duoi 0: cua con lam giam do nhay ngoai phan suy hao" if ci[1] < 0 else "tren 0")}
    chinh = d[(d.vi_tri == "hanh_lang") & (d.khung_gio == "yen") & (d.do_lon == "vua") & d.khoang_cach_m.isin([1.0, 3.0])]
    gop = pd.concat([chinh.assign(nguon="phat_lai"), t2[t2.loai_bo == 0].assign(nguon="that")], ignore_index=True)
    f3 = tk.logistic_cum(gop, "duoc_ghep ~ C(nguon, Treatment('phat_lai')) + snr_db", "nguoi")
    k3 = [x for x in f3.params.index if x.startswith("C(nguon")][0]
    ci3 = f3.conf_int().loc[k3]
    out["10_3"] = {"he_so_ho_that": float(f3.params[k3]), "ktc": [float(ci3[0]), float(ci3[1])]}
    # 10.4: mức tại micro theo khoảng cách (tiếng ho "vừa" ở hành lang), rồi khoảng cách lớn nhất có độ nhạy dự đoán ≥ 70%
    v = hl[hl.do_lon == "vua"]
    A = np.vstack([np.ones(len(v)), np.log10(v.khoang_cach_m)]).T
    a0, a1 = np.linalg.lstsq(A, v.muc_tai_micro_dba.values, rcond=None)[0]
    snr70 = tk.snr_tai_do_nhay(b0, b1, 0.7)
    ban_kinh = {}
    for kg in ("yen", "on"):
        nen = float(d[d.khung_gio == kg].muc_on_nen_dba.median())
        # a0 + a1·log10(r) − nen = snr70
        ban_kinh[kg] = float(10 ** ((snr70 + nen - a0) / a1)) if a1 < 0 else float("inf")
    out["10_4"] = {"muc_1m_dba": float(a0), "doc_db_moi_decade": float(a1), "snr_tai_70": snr70, "ban_kinh_m": ban_kinh}
    return out


def mo_phong(seed=SEED):
    """Dữ liệu mô phỏng có hiệu ứng đã biết: cửa đóng giảm mạnh nhất; ho thật khó hơn phát lại."""
    rng = np.random.default_rng(seed)
    rows = []
    nguoi = [f"C{i:03d}" for i in range(714)]
    for buoi in (1, 2, 3):
        for kg, nen_tb in (("on", 52.0), ("yen", 42.0)):
            for vt in ("hanh_lang", "phong"):
                for kc in (1.0, 3.0, 5.0):
                    for dl, db in (("nho", 55.0), ("vua", 65.0), ("lon", 75.0)):
                        n = 100 // 3 if (vt == "hanh_lang" and dl == "vua" and kg == "yen" and kc in (1.0, 3.0)) else 25 // 3 + 1
                        for _ in range(n):
                            nen = nen_tb + rng.normal(0, 2)
                            muc = db - 20 * math.log10(kc) - (18 if vt == "phong" else 0) + rng.normal(0, 3)
                            snr = muc - nen
                            p = 1 / (1 + math.exp(-(-1.5 + 0.18 * snr)))
                            rows.append({"muc_dich": "o", "loai_bo": 0, "buoi": buoi, "khung_gio": kg, "vi_tri": vt,
                                         "khoang_cach_m": kc, "do_lon": dl, "do_lon_db": db + rng.normal(0, 1),
                                         "muc_tai_micro_dba": muc, "muc_on_nen_dba": nen, "snr_db": snr,
                                         "loai_ho": rng.choice(["sau", "nong"]), "nguoi": rng.choice(nguoi),
                                         "duoc_ghep": int(rng.random() < p)})
    t1 = pd.DataFrame(rows)
    rows = []
    for i in range(9):
        u = rng.normal(0, 0.5)
        for kc in (1.0, 3.0):
            for _ in range(10):
                nen = 42 + rng.normal(0, 2)
                muc = 63 - 20 * math.log10(kc) + rng.normal(0, 3)
                snr = muc - nen
                p = 1 / (1 + math.exp(-(-1.5 - 0.8 + u + 0.18 * snr)))
                rows.append({"nguoi": f"NTG{i + 1:02d}", "khoang_cach_m": kc, "muc_tai_micro_dba": muc, "muc_on_nen_dba": nen,
                             "snr_db": snr, "loai_bo": 0, "duoc_ghep": int(rng.random() < p)})
    return t1, pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tang1")
    ap.add_argument("--tang2")
    ap.add_argument("--ra")
    ap.add_argument("--mo-phong", action="store_true")
    ap.add_argument("--B", type=int, default=1000, help="so vong bootstrap cho H1 va 10.1 (H2 luon 10.000)")
    a = ap.parse_args()
    if a.mo_phong:
        t1, t2 = mo_phong()
    else:
        t1, t2 = pd.read_csv(a.tang1), pd.read_csv(a.tang2)
    kq = {"h1": h1(t1, a.B), "h2": h2(t1, t2), "phu": phan_tich_phu(t1, t2, a.B), "mo_phong": a.mo_phong}
    s = json.dumps(kq, ensure_ascii=False, indent=1, default=float)
    if a.ra:
        open(a.ra, "w", encoding="utf-8").write(s)
    H = kq["h1"]
    print(f"H1: n={H['n']}, do nhay tham chieu {H['do_nhay_du_doan_tham_chieu']:.3f}; muc giam: "
          + ", ".join(f"{k} {v:.3f}" for k, v in H["muc_giam"].items()))
    print(f"    tieu chi: {H['tieu_chi']}")
    print(f"H2: chenh {kq['h2']['chenh_lech']:.3f} KTC {kq['h2']['ktc_bootstrap']}, ung ho H2: {kq['h2']['ung_ho_H2']}, tham do: {kq['h2']['tham_do']}")
    P = kq["phu"]
    print(f"10.1: SNR50 {P['10_1']['snr50']:.1f} dB {P['10_1']['ktc_snr50']}, SNR80 {P['10_1']['snr80']:.1f} dB")
    print(f"10.2: {P['10_2']}")
    print(f"10.3: {P['10_3']}")
    print(f"10.4: {P['10_4']}")


if __name__ == "__main__":
    sys.exit(main())
