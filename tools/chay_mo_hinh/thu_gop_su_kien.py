"""Phép thử cho gop_su_kien.py: 12 tình huống có đáp án tính tay.
Chạy: python3 tools/chay_mo_hinh/thu_gop_su_kien.py  (in "KET QUA: DAT" khi đạt)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gop_su_kien import gop, vector_thu  # noqa: E402

# (p, nguong, k, g) -> danh sách (t_su_kien, t_dau, t_cuoi, so_cua_so, i_max)
DAP_AN = {
    "mot_cua_so": [(1.0, 0.5, 1.5, 1, 1)],
    "mot_cua_so_k2_bi_loai": [],
    "chuoi_hai_cua_so_k2": [(1.5, 0.5, 2.0, 2, 2)],
    "bang_nguong_tinh_la_vuot": [(0.5, 0.0, 1.0, 1, 0), (1.5, 1.0, 2.0, 1, 2)],
    "hai_chuoi_cach_1_g0": [(0.5, 0.0, 1.0, 1, 0), (1.5, 1.0, 2.0, 1, 2)],
    "hai_chuoi_cach_1_g05_gop": [(0.5, 0.0, 2.0, 2, 0)],
    "hai_chuoi_cach_2_g05_khong_gop": [(0.5, 0.0, 1.0, 1, 0), (2.0, 1.5, 2.5, 1, 3)],
    "hai_chuoi_cach_2_g1_gop": [(2.0, 0.0, 2.5, 2, 3)],
    "gop_roi_moi_du_k2": [(0.5, 0.0, 2.0, 2, 0)],
    "diem_bang_nhau_lay_som": [(1.0, 0.5, 2.0, 2, 1)],
    "toan_duoi_nguong": [],
    "cuoi_chuoi_cham_cuoi_tep": [(1.5, 1.0, 2.5, 2, 2)],
}


def main():
    loi = 0
    vt = vector_thu()
    assert len(vt) == len(DAP_AN), "so tinh huong khac dap an"
    for v in vt:
        ev = gop(v["p"], v["nguong"], v["k"], v["g"])
        got = [(e["t_su_kien"], e["t_dau"], e["t_cuoi"], e["so_cua_so"], e["i_max"]) for e in ev]
        if got != DAP_AN[v["ten"]]:
            print(f"SAI {v['ten']}: {got} != {DAP_AN[v['ten']]}")
            loi += 1
        else:
            print(f"dat {v['ten']}")
    print("KET QUA:", "DAT" if loi == 0 else f"KHONG DAT ({loi} tinh huong sai)")
    return 1 if loi else 0


if __name__ == "__main__":
    sys.exit(main())
