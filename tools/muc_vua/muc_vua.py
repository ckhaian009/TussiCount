"""Tính mức “vừa” cho tầng kiểm định 1 (Protocol mục 7.1, điền vào mục 12).

Mức “vừa” = trung bình mức đỉnh dB(A) ở 1 m của 20 tiếng ho nhẹ theo hiệu lệnh của hai thành viên
(10 tiếng mỗi người). Đọc results/muc_vua_phieu.csv (đã điền), in trung bình, độ lệch chuẩn,
khoảng tin cậy 95% (t), trung bình từng người, mức lớn/nhỏ suy ra (+10/−10 dB) và dòng điền mục 12.
Không loại giá trị nào ngoài các lần đo đã đánh dấu khong_hop_le (ghi rõ lý do ở cột ghi_chu).
Chạy:  python3 tools/muc_vua/muc_vua.py
"""
import csv
import math
import os
import statistics as st

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
T975 = {19: 2.093, 18: 2.101, 17: 2.110, 16: 2.120, 15: 2.131}   # phân vị t 97,5%


def main():
    rows = list(csv.DictReader(open("results/muc_vua_phieu.csv", encoding="utf-8")))
    hl = [r for r in rows if r["dBA_dinh"].strip() and r.get("khong_hop_le", "").strip() == ""]
    if len(hl) < 20:
        print(f"Moi co {len(hl)} lan do hop le; can du 20 (10 moi nguoi).")
    v = [float(r["dBA_dinh"].replace(",", ".")) for r in hl]
    if len(v) < 2:
        return
    tb, sd = st.mean(v), st.stdev(v)
    t = T975.get(len(v) - 1, 1.96)
    ci = t * sd / math.sqrt(len(v))
    nen = [float(r["nen_dBA"].replace(",", ".")) for r in rows if r.get("nen_dBA", "").strip()]
    print(f"So lan hop le: {len(v)}")
    print(f"Muc 'vua' = {tb:.1f} dB(A) dinh o 1 m (SD {sd:.1f}; KTC 95% {tb - ci:.1f}–{tb + ci:.1f}; min {min(v):.1f}, max {max(v):.1f})")
    for nguoi in sorted({r["nguoi"] for r in hl}):
        x = [float(r["dBA_dinh"].replace(",", ".")) for r in hl if r["nguoi"] == nguoi]
        print(f"  {nguoi}: {st.mean(x):.1f} dB(A) (n = {len(x)}, SD {st.stdev(x) if len(x) > 1 else 0:.1f})")
    if nen:
        print(f"Nen phong khi do: {min(nen):.1f}–{max(nen):.1f} dB(A); tieng ho cao hon nen it nhat {min(v) - max(nen):.1f} dB")
        if min(v) - max(nen) < 10:
            print("CANH BAO: co lan do cao hon nen duoi 10 dB; nen do lai o phong yen tinh hon.")
    print(f"Suy ra o 1 m: lon = {tb + 10:.1f}, vua = {tb:.1f}, nho = {tb - 10:.1f} dB(A) dinh (he so 0 / -10 / -20 dB)")
    print()
    print("Dien muc 12 cua protocol:")
    print(f"| Mức “vừa” (dB(A) đỉnh ở 1 m) | {tb:.1f} (n = {len(v)}, SD {sd:.1f}) |".replace(".", ","))


if __name__ == "__main__":
    main()
