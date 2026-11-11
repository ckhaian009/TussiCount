"""Lập lịch phát lại cho tầng kiểm định 1 (Protocol mục 7.1, việc t20). Chỉ dùng bảng kê, không cần âm thanh.

Đầu vào: results/coswara_playlist.csv (1.100 tiếng ho, mỗi tiếng đã gán một mục đích và một ô).
Đầu ra:  results/lich_phat_lai.csv, mỗi dòng là một lần phát theo đúng thứ tự trong buổi.

Quy tắc (cố định trước khi phát, seed 2026):
  - 3 buổi tối. Mỗi buổi gồm hai khung giờ: sinh hoạt ồn (on, từ 20:30) rồi yên tĩnh (yen_tinh, từ 21:00).
  - Phân bổ tiếng ho của mỗi ô cho 3 buổi (mỗi ô được trộn ngẫu nhiên rồi cắt theo số lượng):
      khung ồn: chia đều ba buổi;
      khung yên tĩnh: buổi 2 (dự kiến 13/11) dành 21:00–21:30 cho tầng kiểm định 2 (ho thật, tại hành lang
      tầng 1, cùng vị trí hai ô chính), chỉ còn 21:30–21:45, nên buổi 2 chỉ phát hai khối hành lang 1 m và 3 m,
      40 tiếng ho mỗi khối (chia cho ba mức độ lớn theo tỉ lệ cỡ ô: 7 nhỏ, 26 vừa, 7 lớn); phần còn lại của mọi ô
      chia đều cho buổi 1 và buổi 3.
    Phần dư khi chia không hết được xoay vòng giữa các buổi để tổng mỗi buổi cân bằng.
  - Trong mỗi khung giờ của mỗi buổi, các khối vị trí × khoảng cách phát theo thứ tự ngẫu nhiên; trong khối,
    các tiếng ho (ba mức độ lớn) xen kẽ ngẫu nhiên theo từng tiếng ho.
  - Đầu buổi: 3 tiếng bíp đồng bộ, rồi 10 tiếng ho kiểm tra đầu buổi (cùng 10 tệp ở cả ba buổi, hành lang, 1 m,
    mức vừa; thứ tự cố định theo stt), trước khung ồn.
  - Đầu mỗi khối: phát tệp hiệu chuẩn 3 lần ở mức vừa (tệp kiểm tra đầu buổi có stt nhỏ nhất) để đo mức tại micro.
  - Các tiếng ho cách nhau 8 giây.
Hệ số khuếch đại số: lớn 0 dB, vừa −10 dB, nhỏ −20 dB (áp lên đoạn đã chuẩn hoá đỉnh −1 dBFS).

Chạy từ gốc kho: python3 tools/phat_lai/lap_lich_phat.py
"""
import csv
import os
import random
import sys
from collections import Counter, defaultdict

SEED = 2026
GAIN_DB = {"lon": 0, "vua": -10, "nho": -20}
CACH_S = 8
BUOI2_YEN = {"nho": 7, "vua": 26, "lon": 7}   # cho mỗi khối hành lang 1 m và 3 m
DOI_KHOI_S = 30        # thời gian ước tính để đổi vị trí loa giữa hai khối (đã đánh dấu sẵn vị trí trên sàn)
DAU_BUOI_S = 120       # đo suy hao qua cửa bằng nhiễu hồng (2 × 30 s) và chuẩn bị, trong khung ồn
PLAYLIST = "results/coswara_playlist.csv"
OUT = "results/lich_phat_lai.csv"


def chia_theo_ti_le(n, ti_le):
    tong = sum(ti_le)
    q = [n * t / tong for t in ti_le]
    so = [int(x) for x in q]
    du = sorted(range(len(q)), key=lambda i: (-(q[i] - so[i]), i))
    for i in du[: n - sum(so)]:
        so[i] += 1
    return so


def main():
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(root)
    rows = list(csv.DictReader(open(PLAYLIST, encoding="utf-8")))
    kt = sorted([r for r in rows if r["muc_dich"] == "kiem_tra_dau_buoi"], key=lambda r: int(r["stt"]))
    assert len(kt) == 10
    hieu_chuan = kt[0]
    o = defaultdict(list)
    for r in rows:
        if r["muc_dich"] == "o":
            o[r["o"]].append(r)
    # phân bổ ô cho buổi
    theo_buoi = defaultdict(list)  # (buoi, khung) -> list rows
    xoay = {"on": 0, "yen_tinh": 0}
    for oid in sorted(o):
        ds = sorted(o[oid], key=lambda r: int(r["stt"]))
        random.Random(f"{SEED}:o:{oid}").shuffle(ds)
        r0 = ds[0]
        khung = r0["khung_gio"]
        n = len(ds)
        if khung == "on":
            co_so, du = divmod(n, 3)
            so = [co_so] * 3
            for j in range(du):
                so[(xoay["on"] + j) % 3] += 1
            xoay["on"] = (xoay["on"] + du) % 3
        else:
            b2 = BUOI2_YEN[r0["do_lon"]] if (r0["vi_tri"] == "hanh_lang" and int(float(r0["khoang_cach_m"])) in (1, 3)) else 0
            con, du = divmod(n - b2, 2)
            so = [con, b2, con]
            if du:
                so[0 if xoay["yen_tinh"] == 0 else 2] += 1
                xoay["yen_tinh"] = 1 - xoay["yen_tinh"]
        k = 0
        for b in range(3):
            theo_buoi[(b + 1, khung)] += ds[k:k + so[b]]
            k += so[b]
    lich = []

    def them(buoi, khung, khoi_tt, khoi, loai, r, gain_db):
        lich.append({"buoi": buoi, "thu_tu": len([x for x in lich if x["buoi"] == buoi]) + 1, "khung_gio": khung,
                     "khoi_thu_tu": khoi_tt, "khoi": khoi, "loai": loai, "stt": r["stt"] if r else "",
                     "file": r["file"] if r else "", "participant_id": r["participant_id"] if r else "",
                     "type": r["type"] if r else "", "o": r["o"] if r else "", "vi_tri": r["vi_tri"] if r else "",
                     "khoang_cach_m": r["khoang_cach_m"] if r else "", "do_lon": r["do_lon"] if r else "",
                     "he_so_db": gain_db})

    for buoi in (1, 2, 3):
        for i in range(3):
            them(buoi, "dau_buoi", 0, "", "bip_dong_bo", None, "")
        for r in kt:
            them(buoi, "dau_buoi", 0, "hanh_lang|1m", "kiem_tra_dau_buoi", r, GAIN_DB["vua"])
        for khung in ("on", "yen_tinh"):
            ds = theo_buoi[(buoi, khung)]
            khoi = defaultdict(list)
            for r in ds:
                khoi[f"{r['vi_tri']}|{int(float(r['khoang_cach_m']))}m"].append(r)
            ten = sorted(khoi)
            random.Random(f"{SEED}:thu_tu_khoi:{buoi}:{khung}").shuffle(ten)
            for kt_i, k in enumerate(ten, 1):
                for _ in range(3):
                    them(buoi, khung, kt_i, k, "hieu_chuan", hieu_chuan, GAIN_DB["vua"])
                cac = sorted(khoi[k], key=lambda r: int(r["stt"]))
                random.Random(f"{SEED}:trong_khoi:{buoi}:{khung}:{k}").shuffle(cac)
                for r in cac:
                    them(buoi, khung, kt_i, k, "o", r, GAIN_DB[r["do_lon"]])
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(lich[0].keys()))
        w.writeheader()
        w.writerows(lich)
    # tóm tắt và tự kiểm tra
    o_lich = [x for x in lich if x["loai"] == "o"]
    assert len(o_lich) == 1050 and len({x["stt"] for x in o_lich}) == 1050, "moi tieng ho trong o phai phat dung 1 lan"
    for x in o_lich:
        r = next(r for r in rows if r["stt"] == x["stt"])
        assert x["o"] == r["o"] and str(x["he_so_db"]) == str(GAIN_DB[r["do_lon"]])
    print(f"Thoi gian uoc tinh (moi lan phat {CACH_S} s, doi khoi {DOI_KHOI_S} s, dau buoi {DAU_BUOI_S} s):")
    han = {("on", 1): 30, ("on", 2): 30, ("on", 3): 30, ("yen_tinh", 1): 45, ("yen_tinh", 2): 15, ("yen_tinh", 3): 45}
    for buoi in (1, 2, 3):
        for k in ("on", "yen_tinh"):
            x = [v for v in lich if v["buoi"] == buoi and (v["khung_gio"] == k or (k == "on" and v["khung_gio"] == "dau_buoi"))]
            so_phat = sum(1 for v in x if v["loai"] in ("o", "hieu_chuan", "kiem_tra_dau_buoi"))
            nk = len({v["khoi"] for v in x if v["loai"] == "o"})
            giay = so_phat * CACH_S + nk * DOI_KHOI_S + (DAU_BUOI_S if k == "on" else 0)
            print(f"  buoi {buoi} {k:8s}: {sum(1 for v in x if v['loai'] == 'o'):3d} tieng ho trong o, {nk} khoi, "
                  f"{so_phat} lan phat -> {giay / 60:.1f} / {han[(k, buoi)]} phut")
    c = Counter((x["o"], x["buoi"]) for x in o_lich)
    print("Vi du phan bo o chinh:", {b: c[("hanh_lang|3m|vua|yen_tinh", b)] for b in (1, 2, 3)})
    print("Da ghi", OUT, "-", len(lich), "dong")


if __name__ == "__main__":
    sys.exit(main())
