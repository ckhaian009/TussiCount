"""Công cụ thống kê dùng chung cho phân tích TussiCount (việc t35; Protocol mục 9, 10, 16).

Mọi hàm dùng seed cố định khi có lấy mẫu ngẫu nhiên (mặc định 2026) để kết quả chạy lại giống hệt.

  wilson(k, n)                          khoảng tin cậy Wilson cho tỉ lệ (độ nhạy, độ đặc hiệu)
  poisson_chinh_xac(k, t)               khoảng tin cậy Poisson chính xác (Garwood) cho tần suất k/t (phát hiện sai mỗi giờ)
  mtbf_can_duoi(t, so_lan)              cận dưới 95% (một phía) của thời gian trung bình giữa hai lần gián đoạn, giả định mũ;
                                        khi so_lan = 0 xấp xỉ t/3
  bootstrap_cum(cum, ham, B)            bootstrap theo cụm: lấy lại cả cụm (người, khoảng 5 phút, ngày) có hoàn lại
  chenh_do_nhay_bootstrap(...)          H2: chênh độ nhạy giữa hai tầng, lấy lại theo người ở cả hai tầng
  logistic_cum(df, cong_thuc, cum)      hồi quy logistic, sai số chuẩn hiệu chỉnh theo cụm (H1)
  spearman_bootstrap(x, y)              hệ số Spearman và khoảng tin cậy bootstrap theo ngày (10.8)
  sai_so_so_dem(D, R)                   sai lệch trung bình, MAE, sai số tương đối tổng (16.1)
  f1(do_nhay, ppv)                      F1
  kappa(a, b)                           hệ số kappa Cohen cho hai dãy nhãn 0/1 (7.6)
  snr_tai_do_nhay(ket_qua, muc_tieu)    SNR tại độ nhạy mục tiêu từ đường logistic (10.1)
Chạy phép thử: python3 tools/phan_tich/thu_thong_ke.py
"""
import math

import numpy as np
from scipy import stats

SEED = 2026


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return (float("nan"), float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (p, max(0.0, c - m), min(1.0, c + m))


def poisson_chinh_xac(k, t=1.0, alpha=0.05):
    """Khoảng tin cậy Garwood cho tần suất λ = k/t."""
    lo = 0.0 if k == 0 else stats.chi2.ppf(alpha / 2, 2 * k) / 2
    hi = stats.chi2.ppf(1 - alpha / 2, 2 * k + 2) / 2
    return (k / t, lo / t, hi / t)


def mtbf_can_duoi(t, so_lan, alpha=0.05):
    """Cận dưới một phía (1 − alpha) của MTBF cho thời gian quan sát t và so_lan gián đoạn (giả định mũ)."""
    return 2 * t / stats.chi2.ppf(1 - alpha, 2 * so_lan + 2)


def bootstrap_cum(cum, ham, B=10000, seed=SEED, alpha=0.05):
    """cum: danh sách cụm (mỗi cụm là bất cứ dữ liệu gì); ham(list_cum) -> số.
    Trả về (ước lượng, cận dưới, cận trên, mảng bootstrap). Khoảng phân vị."""
    rng = np.random.default_rng(seed)
    n = len(cum)
    est = ham(cum)
    bs = np.empty(B)
    for b in range(B):
        idx = rng.integers(0, n, n)
        bs[b] = ham([cum[i] for i in idx])
    bs = bs[np.isfinite(bs)]
    return (est, float(np.quantile(bs, alpha / 2)), float(np.quantile(bs, 1 - alpha / 2)), bs)


def _do_nhay_cum(cum):
    k = sum(c[0] for c in cum)
    n = sum(c[1] for c in cum)
    return k / n if n else float("nan")


def chenh_do_nhay_bootstrap(cum_a, cum_b, B=10000, seed=SEED, alpha=0.05):
    """cum_a, cum_b: danh sách (so_ghep, so_ho) theo người cho tầng A và tầng B.
    Ước lượng độ nhạy(A) − độ nhạy(B); mỗi vòng lấy lại người độc lập ở cả hai tầng."""
    rng = np.random.default_rng(seed)
    est = _do_nhay_cum(cum_a) - _do_nhay_cum(cum_b)
    a = np.array(cum_a, dtype=float)
    b = np.array(cum_b, dtype=float)
    bs = np.empty(B)
    for i in range(B):
        ia = rng.integers(0, len(a), len(a))
        ib = rng.integers(0, len(b), len(b))
        sa = a[ia].sum(axis=0)
        sb = b[ib].sum(axis=0)
        bs[i] = sa[0] / sa[1] - sb[0] / sb[1]
    return (est, float(np.quantile(bs, alpha / 2)), float(np.quantile(bs, 1 - alpha / 2)), bs)


def logistic_cum(df, cong_thuc, cum):
    """Hồi quy logistic (statsmodels GLM Binomial), sai số chuẩn hiệu chỉnh theo cụm df[cum]."""
    import statsmodels.formula.api as smf
    import statsmodels.api as sm
    m = smf.glm(cong_thuc, data=df, family=sm.families.Binomial())
    groups = df[cum].astype("category").cat.codes.values
    return m.fit(cov_type="cluster", cov_kwds={"groups": groups})


def spearman_bootstrap(x, y, B=10000, seed=SEED, alpha=0.05):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    rho = stats.spearmanr(x, y).statistic
    rng = np.random.default_rng(seed)
    bs = []
    n = len(x)
    for _ in range(B):
        i = rng.integers(0, n, n)
        if len(np.unique(x[i])) < 2 or len(np.unique(y[i])) < 2:
            continue
        bs.append(stats.spearmanr(x[i], y[i]).statistic)
    bs = np.array(bs)
    return (float(rho), float(np.quantile(bs, alpha / 2)), float(np.quantile(bs, 1 - alpha / 2)), n)


def sai_so_so_dem(D, R, B=10000, seed=SEED, alpha=0.05):
    """D, R: số sự kiện thiết bị và số tiếng ho chuẩn theo từng khoảng 5 phút (16.1)."""
    D = np.asarray(D, float)
    R = np.asarray(R, float)
    tong = (D.sum() - R.sum()) / R.sum() if R.sum() else float("nan")
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(B):
        i = rng.integers(0, len(D), len(D))
        if R[i].sum() > 0:
            bs.append((D[i].sum() - R[i].sum()) / R[i].sum())
    bs = np.array(bs)
    return {"sai_lech_tb": float(np.mean(D - R)), "mae": float(np.mean(np.abs(D - R))),
            "sai_so_tuong_doi_tong": float(tong),
            "ktc_sai_so_tuong_doi_tong": (float(np.quantile(bs, alpha / 2)), float(np.quantile(bs, 1 - alpha / 2))),
            "so_khoang": int(len(D))}


def f1(do_nhay, ppv):
    return 2 * do_nhay * ppv / (do_nhay + ppv) if (do_nhay + ppv) > 0 else 0.0


def kappa(a, b):
    a = np.asarray(a, int)
    b = np.asarray(b, int)
    po = np.mean(a == b)
    pa, pb = a.mean(), b.mean()
    pe = pa * pb + (1 - pa) * (1 - pb)
    return float((po - pe) / (1 - pe)) if pe < 1 else 1.0


def snr_tai_do_nhay(b0, b1, muc_tieu):
    """Đường logistic p = 1/(1+exp(-(b0 + b1·SNR))). SNR tại p = muc_tieu."""
    return (math.log(muc_tieu / (1 - muc_tieu)) - b0) / b1
