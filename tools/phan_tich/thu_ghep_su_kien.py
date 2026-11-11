"""10 tình huống thử cho ghep_su_kien.py (việc t18), đáp án tính tay.
Chạy: python3 tools/phan_tich/thu_ghep_su_kien.py  (in "KET QUA: DAT" khi đạt)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ghep_su_kien import chi_so, ghep  # noqa: E402

# ten: (chuan, su_kien, tham số, cặp mong đợi [(i, j)], fn, fp)
CA = [
    ("1_khop_hoan_toan", [10, 20, 30], [10.2, 19.9, 30.5], {}, [(0, 0), (1, 1), (2, 2)], [], []),
    ("2_dung_bien_1s_duoc_ghep", [10], [11.0], {}, [(0, 0)], [], []),
    ("3_vuot_bien_bi_loai", [10], [11.001], {}, [], [0], [0]),
    ("4_hai_su_kien_mot_ho_lay_gan_hon", [10], [10.8, 10.3], {}, [(0, 1)], [], [0]),
    ("5_hai_ho_mot_su_kien_lay_gan_hon", [10, 10.9], [10.6], {}, [(1, 0)], [0], []),
    ("6_tranh_chap_uu_tien_cap_gan_nhat", [10, 11.5], [10.9, 11.6], {}, [(0, 0), (1, 1)], [], []),
    ("7_bang_khoang_cach_uu_tien_ho_som", [10, 11], [10.5], {}, [(0, 0)], [1], []),
    ("8_bu_do_tre", [10, 20], [10.6, 20.6], {"do_tre": 0.6, "dung_sai": 0.3}, [(0, 0), (1, 1)], [], []),
    ("9_khong_bu_thi_lech_qua_dung_sai", [10, 20], [10.6, 20.6], {"dung_sai": 0.3}, [], [0, 1], [0, 1]),
    ("10_khoang_loai_tru", [10, 100, 200], [10.1, 100.2, 150.0, 200.1], {"loai_tru": [(95, 155)]},
     [(0, 0), (2, 3)], [], []),
    ("11_rong", [], [], {}, [], [], []),
    ("12_chi_bao_sai", [], [5.0, 6.0], {}, [], [], [0, 1]),
]


def main():
    loi = 0
    for ten, R, D, kw, cap, fn, fp in CA:
        kq = ghep(R, D, **kw)
        got = ([(i, j) for i, j, _ in kq["cap"]], kq["fn"], kq["fp"])
        if got != (cap, fn, fp):
            print(f"SAI {ten}: {got} != {(cap, fn, fp)}")
            loi += 1
        else:
            print(f"dat {ten}")
    cs = chi_so(ghep([10, 20, 30, 40], [10.1, 20.1, 55.0]), so_gio=0.5)
    ok = (cs["tp"] == 2 and cs["fn"] == 2 and cs["fp"] == 1 and abs(cs["do_nhay"] - 0.5) < 1e-12
          and abs(cs["gia_tri_du_bao_duong"] - 2 / 3) < 1e-12 and abs(cs["phat_hien_sai_moi_gio"] - 2.0) < 1e-12
          and abs(cs["f1"] - 2 * 0.5 * (2 / 3) / (0.5 + 2 / 3)) < 1e-12)
    print("dat chi_so" if ok else f"SAI chi_so: {cs}")
    loi += 0 if ok else 1
    print("KET QUA:", "DAT" if loi == 0 else f"KHONG DAT ({loi} tinh huong sai)")
    return 1 if loi else 0


if __name__ == "__main__":
    sys.exit(main())
