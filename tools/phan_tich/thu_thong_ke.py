"""Phép thử cho thong_ke.py: so với giá trị đã biết (Protocol mục 11) và dữ liệu mô phỏng có đáp án.
Chạy: python3 tools/phan_tich/thu_thong_ke.py  (in "KET QUA: DAT" khi đạt)
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import thong_ke as tk  # noqa: E402

LOI = []


def kiem(ten, dk, chi_tiet=""):
    print(("dat  " if dk else "SAI  ") + ten + (f"  ({chi_tiet})" if chi_tiet else ""))
    if not dk:
        LOI.append(ten)


def main():
    # Protocol mục 11: độ nhạy 80% trên n = 100 -> Wilson 71,1–86,7%
    p, lo, hi = tk.wilson(80, 100)
    kiem("wilson_80_100", abs(lo - 0.7112) < 5e-4 and abs(hi - 0.8666) < 5e-4, f"{lo:.4f}–{hi:.4f}")
    kiem("wilson_0_n", tk.wilson(0, 20)[1] == 0.0 and tk.wilson(20, 20)[2] == 1.0)
    # Protocol mục 11: 18 sự kiện sai trong 4,5 giờ -> 4,0 mỗi giờ, KTC 2,4–6,3
    r, lo, hi = tk.poisson_chinh_xac(18, 4.5)
    kiem("poisson_18_4.5h", abs(r - 4.0) < 1e-12 and round(lo, 1) == 2.4 and round(hi, 1) == 6.3, f"{lo:.3f}–{hi:.3f}")
    kiem("poisson_0", tk.poisson_chinh_xac(0, 1)[1] == 0.0 and abs(tk.poisson_chinh_xac(0, 1)[2] - 3.6889) < 1e-3)
    m = tk.mtbf_can_duoi(300.0, 0)
    kiem("mtbf_khong_gian_doan_xap_xi_T_chia_3", abs(m - 300 / 2.9957) < 0.01, f"{m:.2f} gio")
    kiem("kappa_vi_du_tay", abs(tk.kappa([1, 1, 0, 0], [1, 0, 0, 0]) - 0.5) < 1e-12)
    kiem("kappa_trung_khop", tk.kappa([1, 0, 1, 0], [1, 0, 1, 0]) == 1.0)
    kiem("f1", abs(tk.f1(0.5, 2 / 3) - 4 / 7) < 1e-12)
    kiem("snr_tai_50", abs(tk.snr_tai_do_nhay(-2.0, 0.2, 0.5) - 10.0) < 1e-12)
    s = tk.sai_so_so_dem([2, 1, 0], [1, 1, 1], B=200)
    kiem("sai_so_so_dem", abs(s["sai_lech_tb"]) < 1e-12 and abs(s["mae"] - 2 / 3) < 1e-12
         and abs(s["sai_so_tuong_doi_tong"]) < 1e-12)
    rho, lo, hi, n = tk.spearman_bootstrap(np.arange(10), np.arange(10) ** 2, B=500)
    kiem("spearman_don_dieu", abs(rho - 1.0) < 1e-12 and n == 10, f"rho={rho}")

    # Logistic có cụm: mô phỏng 60 người × 20 tiếng ho, hiệu ứng ngẫu nhiên theo người
    rng = np.random.default_rng(1)
    rows = []
    for nguoi in range(60):
        u = rng.normal(0, 0.8)
        for _ in range(20):
            kc = rng.choice([1.0, 3.0, 5.0])
            on = rng.uniform(35, 60)
            eta = 4.0 - 0.6 * kc - 0.05 * on + u
            rows.append({"nguoi": nguoi, "kc": kc, "on": on, "y": int(rng.random() < 1 / (1 + np.exp(-eta)))})
    df = pd.DataFrame(rows)
    fit = tk.logistic_cum(df, "y ~ kc + on", "nguoi")
    b_kc, b_on = fit.params["kc"], fit.params["on"]
    ci = fit.conf_int()
    kiem("logistic_he_so_kc_am_va_ktc_duoi_0", b_kc < 0 and ci.loc["kc", 1] < 0, f"b={b_kc:.3f}, KTC {ci.loc['kc', 0]:.3f}–{ci.loc['kc', 1]:.3f}")
    kiem("logistic_ktc_chua_gia_tri_mo_phong", ci.loc["kc", 0] < -0.6 * 0.85 < ci.loc["kc", 1] or ci.loc["kc", 0] < -0.6 < ci.loc["kc", 1],
         "hieu ung ngau nhien lam he so bien nho lai mot chut")
    import statsmodels.formula.api as smf
    import statsmodels.api as sm
    naive = smf.glm("y ~ kc + on", data=df, family=sm.families.Binomial()).fit()
    kiem("logistic_sai_so_chuan_theo_cum_lon_hon_ngay_tho", fit.bse["kc"] > naive.bse["kc"] * 0.95,
         f"cum {fit.bse['kc']:.4f} vs {naive.bse['kc']:.4f}")

    # H2: hai tầng cùng độ nhạy thật 0,8 -> KTC chênh lệch chứa 0; chênh 0,3 -> KTC dưới 0
    def tang(n_nguoi, n_ho, p, seed):
        r = np.random.default_rng(seed)
        out = []
        for _ in range(n_nguoi):
            pi = np.clip(p + r.normal(0, 0.05), 0, 1)
            out.append((int(r.binomial(n_ho, pi)), n_ho))
        return out
    est, lo, hi, _ = tk.chenh_do_nhay_bootstrap(tang(10, 20, 0.8, 2), tang(150, 1, 0.8, 3), B=2000)
    kiem("h2_bang_nhau_ktc_chua_0", lo < 0 < hi, f"{est:.3f} [{lo:.3f}; {hi:.3f}]")
    est, lo, hi, _ = tk.chenh_do_nhay_bootstrap(tang(10, 20, 0.5, 4), tang(150, 1, 0.8, 5), B=2000)
    kiem("h2_chenh_lon_ktc_duoi_0", hi < 0, f"{est:.3f} [{lo:.3f}; {hi:.3f}]")
    est, lo, hi, _ = tk.bootstrap_cum([(1, 2), (2, 2), (0, 2)], tk._do_nhay_cum, B=500)
    kiem("bootstrap_cum_uoc_luong", abs(est - 0.5) < 1e-12 and lo <= est <= hi)

    print("KET QUA:", "DAT" if not LOI else f"KHONG DAT ({len(LOI)}: {', '.join(LOI)})")
    return 1 if LOI else 0


if __name__ == "__main__":
    sys.exit(main())
