"""Ghép sự kiện thiết bị báo với tiếng ho chuẩn (Protocol mục 6 "Ghép", sửa đổi 16.6).

Quy tắc:
  - Mỗi tiếng ho chuẩn ghép với tối đa một sự kiện và ngược lại (ghép một–một).
  - Chỉ ghép khi |t_su_kien − t_chuan| ≤ dung sai (mặc định 1 s; tầng 3 khi so hai người gán nhãn dùng 0,5 s).
  - Ưu tiên cặp gần nhau nhất: xét mọi cặp trong dung sai theo khoảng cách tăng dần; cặp nào cả hai còn trống
    thì ghép. Bằng nhau thì ưu tiên tiếng ho chuẩn sớm hơn, rồi sự kiện sớm hơn.
  - Bù độ trễ (16.6): trước khi ghép, trừ độ trễ hệ thống khỏi thời điểm sự kiện.
  - Khoảng loại trừ (mục 13): sự kiện và tiếng ho chuẩn nằm trong khoảng loại trừ bị bỏ trước khi ghép.
Kết quả: số ghép được (TP), tiếng ho bị bỏ sót (FN), sự kiện không ghép được (FP), độ nhạy, giá trị dự báo dương,
phát hiện sai mỗi giờ (khi biết số giờ phân tích), danh sách cặp.

Dòng lệnh:
  python3 tools/phan_tich/ghep_su_kien.py --chuan chuan.csv --su-kien su_kien.csv [--dung-sai 1.0] [--do-tre 0.0]
         [--so-gio 4.5] [--ra cap.csv]
chuan.csv có cột t_chuan (giây); su_kien.csv có cột t_su_kien (giây), cùng mốc thời gian.
"""
import argparse
import csv
import sys


def ghep(chuan, su_kien, dung_sai=1.0, do_tre=0.0, loai_tru=()):
    """chuan, su_kien: danh sách thời điểm (giây). loai_tru: danh sách (t_dau, t_cuoi).
    Trả về dict(cap=[(i_chuan, j_su_kien, lech)], fn=[i], fp=[j], tp, n_chuan, n_su_kien)."""
    def bi_loai(t):
        return any(a <= t <= b for a, b in loai_tru)

    R = [(i, t) for i, t in enumerate(chuan) if not bi_loai(t)]
    D = [(j, t - do_tre) for j, t in enumerate(su_kien) if not bi_loai(t - do_tre)]
    ung_vien = []
    # sắp theo thời gian rồi quét cửa sổ để không phải xét mọi cặp
    Ds = sorted(D, key=lambda x: x[1])
    lo = 0
    for i, tr in sorted(R, key=lambda x: x[1]):
        while lo < len(Ds) and Ds[lo][1] < tr - dung_sai - 1e-9:
            lo += 1
        k = lo
        while k < len(Ds) and Ds[k][1] <= tr + dung_sai + 1e-9:
            j, td = Ds[k]
            ung_vien.append((abs(td - tr), tr, td, i, j))
            k += 1
    ung_vien.sort()
    dung_r, dung_d, cap = set(), set(), []
    for lech, tr, td, i, j in ung_vien:
        if i in dung_r or j in dung_d:
            continue
        dung_r.add(i)
        dung_d.add(j)
        cap.append((i, j, round(td - tr, 4)))
    fn = [i for i, _ in R if i not in dung_r]
    fp = [j for j, _ in D if j not in dung_d]
    return {"cap": sorted(cap), "fn": fn, "fp": fp, "tp": len(cap), "n_chuan": len(R), "n_su_kien": len(D)}


def chi_so(kq, so_gio=None):
    tp, n_r, n_d = kq["tp"], kq["n_chuan"], kq["n_su_kien"]
    out = {"tp": tp, "fn": n_r - tp, "fp": n_d - tp,
           "do_nhay": tp / n_r if n_r else None, "gia_tri_du_bao_duong": tp / n_d if n_d else None}
    if so_gio:
        out["phat_hien_sai_moi_gio"] = (n_d - tp) / so_gio
    s, p = out["do_nhay"], out["gia_tri_du_bao_duong"]
    out["f1"] = 2 * s * p / (s + p) if s and p else 0.0
    return out


def doc_cot(path, cot):
    with open(path, encoding="utf-8") as f:
        return [float(r[cot]) for r in csv.DictReader(f) if r.get(cot, "") != ""]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chuan", required=True)
    ap.add_argument("--su-kien", required=True)
    ap.add_argument("--dung-sai", type=float, default=1.0)
    ap.add_argument("--do-tre", type=float, default=0.0)
    ap.add_argument("--so-gio", type=float)
    ap.add_argument("--ra")
    a = ap.parse_args()
    R = doc_cot(a.chuan, "t_chuan")
    D = doc_cot(a.su_kien, "t_su_kien")
    kq = ghep(R, D, a.dung_sai, a.do_tre)
    cs = chi_so(kq, a.so_gio)
    for k, v in cs.items():
        print(f"{k}: {v:.4f}" if isinstance(v, float) else f"{k}: {v}")
    if a.ra:
        with open(a.ra, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["loai", "t_chuan", "t_su_kien", "lech_s"])
            for i, j, l in kq["cap"]:
                w.writerow(["ghep", R[i], D[j], l])
            for i in kq["fn"]:
                w.writerow(["bo_sot", R[i], "", ""])
            for j in kq["fp"]:
                w.writerow(["bao_sai", "", D[j], ""])


if __name__ == "__main__":
    sys.exit(main())
