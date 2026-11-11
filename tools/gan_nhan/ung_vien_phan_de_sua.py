"""Cắt đoạn 3 giây quanh các sự kiện ứng viên trên phần để sửa để nghe xác minh (Protocol mục 8, việc t19).

Âm thanh KTX: chỉ chạy trên máy tính của Nhóm; thư mục đầu ra phải nằm NGOÀI thư mục đồng bộ iCloud và ngoài kho
GitHub (ví dụ ~/TussiCount_KTX/ung_vien). Không tải các đoạn này lên bất kỳ dịch vụ trực tuyến nào.

Ứng viên = mọi sự kiện ở ngưỡng 0,50, k = 1, g = 0 (tập lớn nhất của lưới chọn ngưỡng). Mỗi đoạn dài 3 s, tâm là
thời điểm sự kiện. Phiếu nghe phieu_nghe.csv có cột co_ho để trống: điền 1 (có tiếng ho), 0 (không), ? (không chắc).
Người nghe chỉ quyết định có hay không có tiếng ho (Protocol 16.12): không ghi chép, không trích dẫn lời nói.

Chạy: python3 tools/gan_nhan/ung_vien_phan_de_sua.py <ghi_am.wav> <diem.csv> <thu_muc_ra>
"""
import csv
import os
import sys

import numpy as np
from scipy.io import wavfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chay_mo_hinh"))
from gop_su_kien import doc_diem, gop  # noqa: E402

DAI_S = 3.0


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        return 2
    wav, diem, ra = sys.argv[1:]
    if "Documents" in os.path.abspath(ra) or "Mobile Documents" in os.path.abspath(ra):
        print("Thu muc ra nam trong Documents (dong bo iCloud). Chon thu muc khac, vi du ~/TussiCount_KTX/ung_vien.")
        return 2
    sr, x = wavfile.read(wav)
    t, p = doc_diem(diem)
    uv = gop(p, 0.50, 1, 0.0, t0=t)
    os.makedirs(ra, exist_ok=True)
    rows = []
    ten_goc = os.path.basename(diem)
    for j, e in enumerate(uv, 1):
        a = max(0, int((e["t_su_kien"] - DAI_S / 2) * sr))
        b = min(len(x), a + int(DAI_S * sr))
        ten = f"uv_{j:04d}.wav"
        wavfile.write(os.path.join(ra, ten), sr, x[a:b])
        rows.append({"doan": ten, "tep": ten_goc, "i_max": e["i_max"], "t_su_kien": e["t_su_kien"], "p_max": round(e["p_max"], 4), "co_ho": ""})
    with open(os.path.join(ra, "phieu_nghe.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["doan", "tep", "i_max", "t_su_kien", "p_max", "co_ho"])
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} ung vien -> {ra}/phieu_nghe.csv (dien cot co_ho)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
