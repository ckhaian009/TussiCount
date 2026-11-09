"""Phân tích tập kiểm tra độ bền: độ nhạy khi tiếng ho có nền ồn (SNR 20, 10, 0 dB).

So sánh theo cặp: mỗi tiếng ho trong 500 đoạn chọn đều có điểm ở dạng sạch (tập testing gốc) và ở ba mức SNR.
Đầu vào: results/ei_kiem_tra_ben.csv, results/<ten>_ben_diem_tung_mau.csv, results/<ten>_diem_tung_mau.csv
Đầu ra:  results/<ten>_do_ben.json
Chạy:    python3 tools/mo_hinh_nen/phan_tich_do_ben.py mo_hinh_nen_v1
"""
import csv
import json
import math
import sys
from collections import defaultdict


def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 4), round(c + h, 4)]


def main(ten):
    ben = list(csv.DictReader(open("results/ei_kiem_tra_ben.csv", encoding="utf-8")))
    dben = {r["file"]: float(r["p_cough"]) for r in csv.DictReader(open(f"results/{ten}_ben_diem_tung_mau.csv", encoding="utf-8"))}
    dsach = {r["file"]: float(r["p_cough"]) for r in csv.DictReader(open(f"results/{ten}_diem_tung_mau.csv", encoding="utf-8"))}
    goc = sorted({r["cough_file"] for r in ben})
    out = {"mo_hinh": ten, "so_tieng_ho": len(goc), "nguong": 0.5, "theo_muc": []}
    k = sum(dsach[g.split("/")[-1][:-4]] >= 0.5 for g in goc)
    out["theo_muc"].append({"muc": "sach (khong tron)", "n": len(goc), "dung": k, "do_nhay": round(k / len(goc), 4), "wilson95": wilson(k, len(goc))})
    for snr in ("20", "10", "0"):
        rs = [r for r in ben if r["snr_db"] == snr]
        k = sum(dben[r["file"].split("/")[-1][:-4]] >= 0.5 for r in rs)
        o = {"muc": f"SNR {snr} dB", "n": len(rs), "dung": k, "do_nhay": round(k / len(rs), 4), "wilson95": wilson(k, len(rs))}
        for src in ("ESC-50", "CommonVoice-vi"):
            s = [r for r in rs if r["noise_source"] == src]
            ks = sum(dben[r["file"].split("/")[-1][:-4]] >= 0.5 for r in s)
            o["nen_" + src] = {"n": len(s), "do_nhay": round(ks / len(s), 4)}
        # cặp: đúng khi sạch nhưng sai khi trộn
        mat = sum(1 for r in rs if dsach[r["cough_file"].split("/")[-1][:-4]] >= 0.5 and dben[r["file"].split("/")[-1][:-4]] < 0.5)
        o["dung_khi_sach_sai_khi_tron"] = mat
        out["theo_muc"].append(o)
    json.dump(out, open(f"results/{ten}_do_ben.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    for o in out["theo_muc"]:
        extra = "" if "nen_ESC-50" not in o else f" | nen ESC-50 {o['nen_ESC-50']['do_nhay']:.3f}, giong noi {o['nen_CommonVoice-vi']['do_nhay']:.3f}; mat so voi sach {o['dung_khi_sach_sai_khi_tron']}"
        print(f"{o['muc']:18s} n={o['n']} do nhay {o['do_nhay']:.4f} {o['wilson95']}{extra}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "mo_hinh_nen_v1"))
