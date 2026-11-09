"""Ghi điểm từng mẫu testing lấy từ Edge Impulse (Model testing, API classify/all/result/page) ra CSV.

Điểm được chép từ trình duyệt dưới dạng chuỗi gọn: các mẫu testing xếp theo tên tăng dần, mỗi mẫu
2 ký tự cơ số 36 = round(p_cough × 1000). Kèm SHA-256 của danh sách tên (nối bằng "\n") để chắc chắn
thứ tự khớp với bảng kê: tap = testing → các đoạn testing trong results/ei_du_lieu_mo_hinh_nen.csv;
tap = ben → các đoạn trộn trong results/ei_kiem_tra_ben.csv (tập kiểm tra độ bền).
Chạy:  python3 tools/mo_hinh_nen/ghi_diem_tu_ei.py <tep_chuoi> <sha256> <ten_dau_ra> [testing|ben]
Đầu ra: results/<ten_dau_ra>_diem_tung_mau.csv (file, label, p_cough)
"""
import csv
import hashlib
import sys


def main(tep, sha, ten, tap="testing"):
    if tap == "ben":
        rows = [(r["file"].split("/")[-1][:-4], r["label"]) for r in csv.DictReader(open("results/ei_kiem_tra_ben.csv", encoding="utf-8"))]
    else:
        rows = [(r["file"].split("/")[-1][:-4], r["label"]) for r in csv.DictReader(open("results/ei_du_lieu_mo_hinh_nen.csv", encoding="utf-8"))
                if r["split"] == "testing"]
    rows.sort()
    h = hashlib.sha256("\n".join(n for n, _ in rows).encode()).hexdigest()
    assert h == sha, f"SHA-256 danh sach ten khong khop: {h} != {sha}"
    s = open(tep).read().strip()
    assert len(s) == 2 * len(rows), (len(s), len(rows))
    with open(f"results/{ten}_diem_tung_mau.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["file", "label", "p_cough"])
        for i, (n, lab) in enumerate(rows):
            w.writerow([n, lab, int(s[2 * i:2 * i + 2], 36) / 1000])
    print(f"Da ghi {len(rows)} mau vao results/{ten}_diem_tung_mau.csv (SHA-256 khop)")


if __name__ == "__main__":
    main(*sys.argv[1:])
