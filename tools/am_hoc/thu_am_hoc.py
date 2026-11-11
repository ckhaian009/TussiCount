"""Phép thử cho am_hoc.py trên tín hiệu tổng hợp có đáp án. Chạy: python3 tools/am_hoc/thu_am_hoc.py"""
import os
import sys

import numpy as np
from scipy import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import am_hoc as ah  # noqa: E402

FS = 16000
LOI = []


def kiem(ten, dk, ct=""):
    print(("dat  " if dk else "SAI  ") + ten + (f"  ({ct})" if ct else ""))
    if not dk:
        LOI.append(ten)


def main():
    rng = np.random.default_rng(3)
    # 1. Hiệu chuẩn: dB(A) = 120 + 1·dBFS cho TC-01; TC-02 nhạy hơn 2 dB
    bang = []
    for m in (45, 55, 65, 75, 85):
        bang.append({"thiet_bi": "TC-01", "laeq_dbfs": m - 120 + rng.normal(0, 0.1), "laeq_dba": m})
        bang.append({"thiet_bi": "TC-02", "laeq_dbfs": m - 118 + rng.normal(0, 0.1), "laeq_dba": m})
    kq = ah.hieu_chuan(bang)
    kiem("hieu_chuan_he_so", abs(kq["TC-01"]["b"] - 1) < 0.02 and abs(kq["TC-01"]["a"] - 120) < 1.5 and kq["TC-01"]["r2"] > 0.999,
         f"a={kq['TC-01']['a']:.2f} b={kq['TC-01']['b']:.3f}")
    c = kq["can_bang_16_8"]["chenh_dbfs_TC01_tru_TC02"]
    kiem("can_bang_chenh_2dB", abs(c + 2) < 0.2 and not kq["can_bang_16_8"]["dat_khong_can_chinh"], f"chenh {c:.2f} dB")

    # 2. Suy hao qua cửa: cửa đóng = nhiễu lọc thấp qua, suy hao tăng theo tần số
    n = 30 * FS
    nh = rng.standard_normal(n)
    sos = signal.butter(2, 500, "low", fs=FS, output="sos")
    dong = signal.sosfilt(sos, nh) * 0.3
    x = np.concatenate([nh * 0.5, np.zeros(FS), dong])
    sh = ah.suy_hao(x, FS, 0.0, 31.0)
    s_thap, s_cao = sh["250"]["suy_hao_db"], sh["4000"]["suy_hao_db"]
    kiem("suy_hao_tang_theo_tan_so", s_cao > s_thap + 20, f"250 Hz {s_thap:.1f} dB, 4 kHz {s_cao:.1f} dB")
    kiem("suy_hao_tan_thap_gan_mat_nang", abs(s_thap - 20 * np.log10(0.5 / 0.3)) < 2.0, f"{s_thap:.1f} dB")

    # 3. T20: xung tắt dần theo hàm mũ với RT60 = 0,6 s, cộng nền −70 dB
    rt = 0.6
    t = np.arange(int(1.5 * FS)) / FS
    h = rng.standard_normal(len(t)) * np.exp(-6.9078 * t / rt)
    sig = np.concatenate([np.zeros(FS), h, np.zeros(FS)]) + rng.standard_normal(len(h) + 2 * FS) * 10 ** (-70 / 20)
    kq = ah.t20(sig, FS, [1.0, 1.0])
    tv = [kq[k]["trung_vi"] for k in kq]
    kiem("t20_gan_rt60", all(abs(v - rt) < 0.06 for v in tv), ", ".join(f"{v:.3f}" for v in tv))
    print("KET QUA:", "DAT" if not LOI else f"KHONG DAT ({', '.join(LOI)})")
    return 1 if LOI else 0


if __name__ == "__main__":
    sys.exit(main())
