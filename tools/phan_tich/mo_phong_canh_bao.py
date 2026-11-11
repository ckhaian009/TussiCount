"""Mô phỏng quy tắc cảnh báo (Protocol sửa đổi 16.4) và mức tăng nhỏ nhất phát hiện được (phân tích phụ 10.5).

Mô hình số đếm mỗi đêm (12 giờ, 18:00–06:00): N ~ Poisson(độ_nhạy × số_ho_thật + phát_hiện_sai_mỗi_giờ × 12).

Quy tắc cảnh báo định trước (16.4): đêm D phát cảnh báo khi N_D lớn hơn phân vị 99% của Poisson(λ_D), với
λ_D = (tỉ lệ sự kiện trên mỗi học sinh trung bình của 3 đêm hợp lệ liền trước) × sĩ số đêm D. Mô phỏng giữ sĩ số
không đổi, nên λ_D là trung bình số sự kiện của 3 đêm trước.
  (a) số cảnh báo sai kỳ vọng trong 30 đêm không có thay đổi (đêm 4–33, ba đêm đầu làm nền);
  (b) khi số tiếng ho thật tăng bền vững 50%, 100%, 200% từ đêm 4: xác suất có cảnh báo trong 7 đêm kể từ khi tăng
      và số đêm trễ trung bình (0 = cảnh báo ngay đêm đầu tiên tăng), tính trên các chuỗi có cảnh báo.
Mỗi kịch bản 10.000 chuỗi, seed 2026; số tiếng ho thật nền 20, 50, 100 mỗi đêm.

Mức tăng nhỏ nhất (10.5): phép thử Poisson chính xác một phía, α = 0,05, giả định biết trung bình nền
μ0 = độ_nhạy × c0 + 12 × phát_hiện_sai; tổng số đếm của n đêm (n = 1 và 3). Tìm mức tăng tương đối nhỏ nhất r
của số tiếng ho thật sao cho xác suất bác bỏ ≥ 80%.

Chạy (dùng độ nhạy và phát hiện sai mỗi giờ đo được ở mục 9):
  python3 tools/phan_tich/mo_phong_canh_bao.py --do-nhay 0.80 --sai-moi-gio 4.0 [--ra results/canh_bao.json]
"""
import argparse
import json
import sys

import numpy as np
from scipy import stats

SEED = 2026
GIO_DEM = 12
NEN = (20, 50, 100)
TANG = (0.5, 1.0, 2.0)
SO_CHUOI = 10000


def nguong_canh_bao(lam):
    """Cảnh báo khi N > phân vị 99% của Poisson(lam)."""
    return stats.poisson.ppf(0.99, lam)


def mo_phong_chuoi(rng, mu, so_chuoi):
    """mu: mảng trung bình theo đêm (độ dài T). Trả về mảng cảnh báo (so_chuoi × T), đêm 0–2 không xét."""
    T = len(mu)
    N = rng.poisson(np.broadcast_to(mu, (so_chuoi, T)))
    canh = np.zeros_like(N, dtype=bool)
    for d in range(3, T):
        lam = N[:, d - 3:d].mean(axis=1)
        nguong = nguong_canh_bao(np.maximum(lam, 1e-9))
        canh[:, d] = N[:, d] > nguong
    return canh


def canh_bao(do_nhay, sai_moi_gio, so_chuoi=SO_CHUOI, seed=SEED):
    rng = np.random.default_rng(seed)
    nen_sai = sai_moi_gio * GIO_DEM
    out = {"khong_thay_doi": [], "co_tang": []}
    for c0 in NEN:
        mu0 = do_nhay * c0 + nen_sai
        canh = mo_phong_chuoi(rng, np.full(33, mu0), so_chuoi)
        out["khong_thay_doi"].append({"ho_that_moi_dem": c0, "trung_binh_dem": round(mu0, 2),
                                      "canh_bao_sai_ky_vong_30_dem": float(canh[:, 3:].sum(axis=1).mean())})
        for r in TANG:
            mu1 = do_nhay * c0 * (1 + r) + nen_sai
            mu = np.array([mu0] * 3 + [mu1] * 7)
            canh = mo_phong_chuoi(rng, mu, so_chuoi)[:, 3:]
            co = canh.any(axis=1)
            tre = np.argmax(canh, axis=1)[co]
            out["co_tang"].append({"ho_that_moi_dem": c0, "muc_tang": r, "xac_suat_canh_bao_trong_7_dem": float(co.mean()),
                                   "so_dem_tre_trung_binh": float(tre.mean()) if co.any() else None})
    return out


def muc_tang_nho_nhat(do_nhay, sai_moi_gio, alpha=0.05, suc_manh=0.80):
    out = []
    for c0 in NEN:
        mu0 = do_nhay * c0 + sai_moi_gio * GIO_DEM
        for n in (1, 3):
            k_crit = stats.poisson.ppf(1 - alpha, n * mu0)  # bác bỏ khi tổng > k_crit
            lo, hi = 0.0, 20.0
            for _ in range(60):
                r = (lo + hi) / 2
                mu1 = do_nhay * c0 * (1 + r) + sai_moi_gio * GIO_DEM
                if stats.poisson.sf(k_crit, n * mu1) >= suc_manh:
                    hi = r
                else:
                    lo = r
            out.append({"ho_that_moi_dem": c0, "so_dem": n, "muc_tang_nho_nhat": round(hi, 4)})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--do-nhay", type=float, required=True)
    ap.add_argument("--sai-moi-gio", type=float, required=True)
    ap.add_argument("--so-chuoi", type=int, default=SO_CHUOI)
    ap.add_argument("--ra")
    a = ap.parse_args()
    kq = {"do_nhay": a.do_nhay, "sai_moi_gio": a.sai_moi_gio, "seed": SEED, "so_chuoi": a.so_chuoi,
          "canh_bao": canh_bao(a.do_nhay, a.sai_moi_gio, a.so_chuoi), "muc_tang_nho_nhat": muc_tang_nho_nhat(a.do_nhay, a.sai_moi_gio)}
    s = json.dumps(kq, ensure_ascii=False, indent=1)
    if a.ra:
        open(a.ra, "w", encoding="utf-8").write(s)
    print(s)


if __name__ == "__main__":
    sys.exit(main())
