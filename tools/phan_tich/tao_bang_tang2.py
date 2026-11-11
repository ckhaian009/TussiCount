"""Lập bảng tầng kiểm định 2 (ho thật, Protocol 7.2) cho phan_tich_h1_h2.py.

Ghép bốn nguồn:
  1. Trang bấm giờ (tệp tang2_lan_bam_<phien>.csv): thời điểm chạm BÍP và chạm HO theo đồng hồ điện thoại (t_ms).
  2. Nhật ký trình phát `phat_lai.py <buoi> bip dau|cuoi`: thời điểm phát 3 tiếng bíp theo đồng hồ MacBook, cộng độ
     lệch đo bằng sntp đầu lần chạy (sntp in độ lệch cần cộng vào đồng hồ máy để ra giờ NTP).
  3. Trang bấm giờ (tệp tang2_muc_dba_<phien>.csv, có thể nhiều tệp từ nhiều máy): mức đỉnh dB(A) của từng tiếng ho.
  4. Thiết bị TC-01 (giờ NTP): sự kiện (cột t_epoch, giây) và nhật ký mỗi phút (cột t_phut_epoch, la90_dbfs hoặc
     la90_dba).

Đồng bộ: mỗi nhóm bíp (đầu, cuối buổi) cho độ lệch = trung vị(t_bip_NTP − t_cham). Độ lệch này gồm cả độ lệch đồng
hồ điện thoại, độ trễ khởi động afplay và độ trễ phản xạ của người bấm; độ trễ phản xạ khi bấm tiếng ho tương tự nên
được trừ cùng lúc. Có hai nhóm thì nội suy tuyến tính theo thời gian (bù trôi đồng hồ); một nhóm thì dùng hằng số.
Ít hơn 3 lần chạm trong một nhóm: chọn cách gán (giữ thứ tự) cho độ lệch ít phân tán nhất. Nhiều hơn 3: dừng, yêu
cầu huỷ lần thừa trên trang.

Thứ tự tiếng ho: với mỗi (người, khoảng cách), các lần chạm HO chưa huỷ sắp theo thời gian, đánh số 1, 2, …; mức
dB(A) ghép theo số này (đúng quy tắc trang hiển thị cho người quan sát 2).
loai_bo = 1 khi lần chạm được đánh dấu gián đoạn, hoặc nằm trong khoảng loại trừ (mục 13).
Độ trễ hệ thống (16.6): truyền trung vị đo ở 10 tiếng ho kiểm tra của buổi phát lại cùng tối bằng --tre-trung-vi;
chỉ trừ khi lệch quá 0,3 s.

Chạy:
  python3 tools/phan_tich/tao_bang_tang2.py --bam tang2_lan_bam_2026-11-13.csv --dba tang2_muc_dba_2026-11-13.csv \\
      --nhat-ky-bip results/phat_lai_nhat_ky/buoi2_tang2_bip_dau_*.csv results/phat_lai_nhat_ky/buoi2_tang2_bip_cuoi_*.csv \\
      --su-kien su_kien_tc01.csv --phut phut_tc01.csv --hieu-chuan 120.5,1.008 --tre-trung-vi 0.12 \\
      --ra results/tang2.csv
Thử: python3 tools/phan_tich/tao_bang_tang2.py --thu   (dữ liệu mô phỏng có độ lệch, trôi và độ trễ đã biết)
"""
import argparse
import csv
import itertools
import json
import os
import re
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ghep_su_kien import ghep  # noqa: E402

DUNG_SAI = 1.0
NGUONG_TRE = 0.3


def doc_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def co(v):
    return str(v).strip().lower() in ("1", "true", "yes")


def so(v):
    try:
        return float(str(v).replace(",", "."))
    except (TypeError, ValueError):
        return None


# ---------- đồng bộ ----------
def doc_bip_may_phat(paths):
    """Trả về {nhom: [t_ntp_s, ...]} từ nhật ký phat_lai.py chế độ bip."""
    ra = {}
    for p in paths:
        rows = doc_csv(p)
        lech = 0.0
        for r in rows:
            if r["loai"] == "bat_dau":
                m = re.search(r"sntp:\s*([+-]?\d+\.\d+)", r.get("ghi_chu", ""))
                if m:
                    lech = float(m.group(1))
                else:
                    print(f"CANH BAO: {os.path.basename(p)} không có độ lệch sntp; coi đồng hồ MacBook là giờ NTP.")
        for r in rows:
            m = re.match(r"tang2 (dau|cuoi) (\d)", r.get("ghi_chu", ""))
            if r["loai"] == "bip_dong_bo" and m:
                ra.setdefault(m.group(1), []).append(float(r["t_phat_epoch"]) + lech)
    for k in ra:
        ra[k].sort()
    return ra


def gan_bip(cham, phat):
    """cham, phat: thời điểm (s) tăng dần. Trả về (danh sách độ lệch phat − cham, độ phân tán)."""
    if len(cham) > len(phat):
        raise SystemExit(f"Có {len(cham)} lần chạm bíp nhưng chỉ {len(phat)} tiếng bíp: huỷ lần thừa trên trang rồi tải lại CSV.")
    tot = None
    for chon in itertools.combinations(range(len(phat)), len(cham)):
        d = [phat[j] - c for j, c in zip(chon, cham)]
        pt = max(d) - min(d)
        if tot is None or pt < tot[1]:
            tot = (d, pt)
    return tot


def ham_lech(bam, bip_phat):
    """Trả về (hàm t_cham_s -> độ lệch, thông tin)."""
    nhom = {}
    for r in bam:
        if r["loai"] == "bip" and not co(r["huy"]):
            nhom.setdefault(r["nhom_bip"], []).append(float(r["t_ms"]) / 1000)
    tt = {}
    diem = []
    for g in ("dau", "cuoi"):
        if g not in nhom:
            continue
        if g not in bip_phat:
            raise SystemExit(f"Có lần chạm bíp nhóm {g} nhưng không có nhật ký trình phát nhóm {g}.")
        cham = sorted(nhom[g])
        d, pt = gan_bip(cham, bip_phat[g])
        lech = statistics.median(d)
        tt[g] = {"so_cham": len(cham), "do_lech_s": round(lech, 4), "phan_tan_s": round(pt, 4),
                 "t_giua_s": statistics.median(cham)}
        if pt > 0.25:
            print(f"CANH BAO: độ lệch các lần chạm bíp nhóm {g} phân tán {pt:.2f} s (> 0,25 s).")
        diem.append((statistics.median(cham), lech))
    if not diem:
        raise SystemExit("Không có lần chạm bíp nào chưa huỷ: không đồng bộ được.")
    if len(diem) == 1:
        c = diem[0][1]
        return (lambda t: c), {"nhom": tt, "troi_s_moi_gio": None}
    (t0, l0), (t1, l1) = diem
    k = (l1 - l0) / (t1 - t0) if t1 != t0 else 0.0
    return (lambda t: l0 + k * (t - t0)), {"nhom": tt, "troi_s_moi_gio": round(k * 3600, 4)}


# ---------- bảng ----------
def doc_dba(paths):
    """Gộp nhiều tệp; cùng (người, khoảng cách, số) thì lấy lần nhập sau cùng."""
    tot = {}
    for p in paths:
        for r in doc_csv(p):
            k = (r["nguoi"], int(float(r["khoang_cach_m"])), int(float(r["thu_tu"])))
            t = so(r.get("t_nhap_ms")) or 0
            if k not in tot or t >= tot[k][0]:
                tot[k] = (t, so(r.get("muc_dba")))
    return {k: v[1] for k, v in tot.items()}


def doc_phut(path, hieu_chuan):
    """{phút (epoch // 60): la90 dB(A)}."""
    ra = {}
    for r in doc_csv(path):
        t = so(r["t_phut_epoch"])
        if t is None:
            continue
        if r.get("la90_dba") not in (None, ""):
            v = so(r["la90_dba"])
        elif hieu_chuan and r.get("la90_dbfs") not in (None, ""):
            a, b = hieu_chuan
            v = a + b * so(r["la90_dbfs"])
        else:
            v = None
        if v is not None:
            ra[int(t // 60)] = v
    return ra


def lap_bang(bam, dba, bip_phat, su_kien, phut, tre_trung_vi=0.0, loai_tru=()):
    lech, tt = ham_lech(bam, bip_phat)
    tre = tre_trung_vi if abs(tre_trung_vi) > NGUONG_TRE else 0.0
    ho = [r for r in bam if r["loai"] == "ho" and not co(r["huy"])]
    ho.sort(key=lambda r: float(r["t_ms"]))
    dem = {}
    dong = []
    for r in ho:
        kc = int(float(r["khoang_cach_m"]))
        k = (r["nguoi"], kc)
        dem[k] = dem.get(k, 0) + 1
        t_cham = float(r["t_ms"]) / 1000
        t = t_cham + lech(t_cham)
        muc = dba.get((r["nguoi"], kc, dem[k]))
        nen = phut.get(int(t // 60)) if phut else None
        bi_loai = co(r["gian_doan"]) or any(a <= t <= b for a, b in loai_tru)
        dong.append({"nguoi": r["nguoi"], "khoang_cach_m": kc, "thu_tu": dem[k], "t_chuan_epoch": round(t, 3),
                     "muc_tai_micro_dba": muc, "muc_on_nen_dba": None if nen is None else round(nen, 1),
                     "snr_db": None if (muc is None or nen is None) else round(muc - nen, 1),
                     "gian_doan": int(co(r["gian_doan"])), "loai_bo": int(bi_loai), "duoc_ghep": 0,
                     "t_su_kien_epoch": None, "lech_s": None})
    # ghép trong khung của buổi (±10 s quanh tiếng ho đầu và cuối); tiếng ho bị loại không tham gia ghép
    if dong:
        a, b = dong[0]["t_chuan_epoch"] - 10, dong[-1]["t_chuan_epoch"] + 10
        sk = sorted(t for t in su_kien if a <= t - tre <= b)
        chon = [i for i, d in enumerate(dong) if not d["loai_bo"]]
        kq = ghep([dong[i]["t_chuan_epoch"] for i in chon], sk, dung_sai=DUNG_SAI, do_tre=tre, loai_tru=loai_tru)
        for i, j, l in kq["cap"]:
            d = dong[chon[i]]
            d["duoc_ghep"] = 1
            d["t_su_kien_epoch"] = round(sk[j], 3)
            d["lech_s"] = round(l, 3)
        tt["su_kien_trong_khung"] = len(sk)
        tt["su_kien_khong_ghep"] = len(kq["fp"])
    tt["tre_trung_vi_s"] = tre_trung_vi
    tt["tre_da_tru_s"] = tre
    return dong, tt


COT = ["nguoi", "khoang_cach_m", "thu_tu", "t_chuan_epoch", "muc_tai_micro_dba", "muc_on_nen_dba", "snr_db",
       "gian_doan", "loai_bo", "duoc_ghep", "t_su_kien_epoch", "lech_s"]


def ghi_bang(dong, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COT)
        w.writeheader()
        for d in dong:
            w.writerow({k: ("" if d[k] is None else d[k]) for k in COT})


def tom_tat(dong, tt):
    hl = [d for d in dong if not d["loai_bo"]]
    tp = sum(d["duoc_ghep"] for d in hl)
    nguoi = sorted({d["nguoi"] for d in dong})
    print(f"Tiếng ho: {len(dong)} (loại {len(dong) - len(hl)}), người: {len(nguoi)}; ghép được {tp}/{len(hl)}"
          + (f" = {tp / len(hl):.1%}" if hl else ""))
    for kc in (1, 3):
        x = [d for d in hl if d["khoang_cach_m"] == kc]
        if x:
            print(f"  {kc} m: {sum(d['duoc_ghep'] for d in x)}/{len(x)}")
    thieu = sum(1 for d in dong if d["muc_tai_micro_dba"] is None)
    if thieu:
        print(f"  thiếu mức dB(A): {thieu}")
    print("Đồng bộ:", json.dumps(tt, ensure_ascii=False))


# ---------- phép thử trên dữ liệu mô phỏng ----------
def thu():
    import random
    import tempfile
    rng = random.Random(2026)
    LECH_DT = -2.4      # đồng hồ điện thoại nhanh 2,4 s so với NTP
    TROI = 0.002        # trôi 2 ms mỗi phút
    PHAN_XA = 0.22      # độ trễ phản xạ trung bình của người bấm
    AFPLAY = 0.06       # trình phát ghi thời điểm trước khi afplay phát
    SNTP = 0.15         # đồng hồ MacBook chậm 0,15 s
    TRE_TB = 0.45       # độ trễ hệ thống của thiết bị (> 0,3 s nên được trừ)
    T0 = 1794567600.0   # 13/11/2026 21:00 giờ Việt Nam

    def dt_dien_thoai(t_ntp):  # giờ NTP -> giờ điện thoại
        return t_ntp - LECH_DT + TROI * (t_ntp - T0) / 60

    tmp = tempfile.mkdtemp(prefix="tang2_thu_")
    bam, nk = [], {}
    for g, tb in (("dau", T0), ("cuoi", T0 + 28 * 60)):
        rows = [{"buoi": 2, "phan": f"tang2_bip_{g}", "loai": "bat_dau", "t_phat_epoch": f"{tb - 5 - SNTP:.3f}",
                 "ghi_chu": f"sntp: +{SNTP:.6f} +/- 0.020000 time.apple.com 17.253.1.1"}]
        for j in range(3):
            t_bip = tb + 2 * j                       # tiếng bíp phát ra (NTP)
            rows.append({"buoi": 2, "phan": f"tang2_bip_{g}", "loai": "bip_dong_bo",
                         "t_phat_epoch": f"{t_bip - AFPLAY - SNTP:.3f}", "ghi_chu": f"tang2 {g} {j + 1}"})
            if not (g == "cuoi" and j == 1):         # nhóm cuối thiếu một lần chạm
                bam.append({"loai": "bip", "nhom_bip": g, "huy": "0", "gian_doan": "0", "nguoi": "",
                            "khoang_cach_m": "", "t_ms": f"{dt_dien_thoai(t_bip + PHAN_XA + rng.gauss(0, 0.03)) * 1000:.1f}"})
        p = os.path.join(tmp, f"bip_{g}.csv")
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["buoi", "phan", "loai", "t_phat_epoch", "ghi_chu"])
            w.writeheader()
            w.writerows(rows)
        nk[g] = p
    # 8 người × 2 khoảng cách × 10 tiếng ho, cách 9 s; thiết bị bỏ sót 3 m nhiều hơn
    t = T0 + 20
    that, su_kien, dba_rows, dap_an = [], [], [], {}
    for n in range(1, 9):
        for kc in (1, 3):
            for i in range(1, 11):
                t_ho = t
                t += 9
                gd = (n == 2 and kc == 1 and i == 4)
                t_cham = dt_dien_thoai(t_ho + PHAN_XA + rng.gauss(0, 0.05)) * 1000
                bam.append({"loai": "ho", "nhom_bip": "", "huy": "0", "gian_doan": "1" if gd else "0",
                            "nguoi": f"NTG{n:02d}", "khoang_cach_m": str(kc), "t_ms": f"{t_cham:.1f}"})
                if n == 3 and kc == 3 and i == 2:  # một lần chạm nhầm đã huỷ, ngay sau tiếng ho
                    bam.append({"loai": "ho", "nhom_bip": "", "huy": "1", "gian_doan": "0", "nguoi": f"NTG{n:02d}",
                                "khoang_cach_m": str(kc), "t_ms": f"{t_cham + 1500:.1f}"})
                bao = rng.random() < (0.9 if kc == 1 else 0.6)
                if bao:
                    su_kien.append(t_ho + TRE_TB + rng.gauss(0, 0.1))
                dap_an[(f"NTG{n:02d}", kc, i)] = (bao and not gd, gd)
                muc = 72 - (9.5 if kc == 3 else 0) + rng.gauss(0, 2)
                if not (n == 5 and i == 7):
                    dba_rows.append({"nguoi": f"NTG{n:02d}", "khoang_cach_m": kc, "thu_tu": i, "muc_dba": f"{muc:.1f}",
                                     "t_nhap_ms": "1"})
                that.append(t_ho)
    for _ in range(6):  # phát hiện sai rải rác
        su_kien.append(rng.uniform(T0, t))
    phut = {int(m): 48.0 + rng.gauss(0, 1) for m in range(int(T0 // 60), int(t // 60) + 2)}
    pd = os.path.join(tmp, "dba.csv")
    with open(pd, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["nguoi", "khoang_cach_m", "thu_tu", "muc_dba", "t_nhap_ms"])
        w.writeheader()
        w.writerows(dba_rows)
    # tệp nhập lại một giá trị (lần nhập sau thắng)
    pd2 = os.path.join(tmp, "dba2.csv")
    with open(pd2, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["nguoi", "khoang_cach_m", "thu_tu", "muc_dba", "t_nhap_ms"])
        w.writeheader()
        w.writerow({"nguoi": "NTG01", "khoang_cach_m": 1, "thu_tu": 1, "muc_dba": "99.9", "t_nhap_ms": "2"})

    dong, tt = lap_bang(bam, doc_dba([pd, pd2]), doc_bip_may_phat([nk["dau"], nk["cuoi"]]), su_kien,
                        {k: v for k, v in phut.items()}, tre_trung_vi=TRE_TB)
    loi = []
    # độ lệch kỳ vọng: NTG = điện thoại + LECH_DT − trôi − PHAN_XA − ... ; t_chuan phải gần thời điểm ho thật
    lech_t = [d["t_chuan_epoch"] - that[k] for k, d in enumerate(dong)]
    if max(abs(x) for x in lech_t) > 0.25:
        loi.append(f"t_chuan lệch thời điểm ho thật tới {max(abs(x) for x in lech_t):.3f} s")
    sai = 0
    for d in dong:
        bao, gd = dap_an[(d["nguoi"], d["khoang_cach_m"], d["thu_tu"])]
        if d["loai_bo"] != int(gd):
            loi.append(f"loai_bo sai ở {d['nguoi']} {d['khoang_cach_m']} m số {d['thu_tu']}")
        if not d["loai_bo"] and d["duoc_ghep"] != int(bao):
            sai += 1
    if sai > 2:  # phát hiện sai ngẫu nhiên có thể rơi gần một tiếng ho bị bỏ sót
        loi.append(f"{sai} tiếng ho ghép sai")
    if len(dong) != 160:
        loi.append(f"số dòng {len(dong)} khác 160 (lần chạm đã huỷ phải bị bỏ)")
    d11 = [d for d in dong if d["nguoi"] == "NTG01" and d["khoang_cach_m"] == 1 and d["thu_tu"] == 1][0]
    if d11["muc_tai_micro_dba"] != 99.9:
        loi.append("không lấy lần nhập dB(A) sau cùng")
    if sum(1 for d in dong if d["muc_tai_micro_dba"] is None) != 2:
        loi.append("số dòng thiếu dB(A) phải là 2")
    if tt["tre_da_tru_s"] != TRE_TB:
        loi.append("không trừ độ trễ > 0,3 s")
    k_mong = TROI / 60 * 3600
    if abs(-tt["troi_s_moi_gio"] - k_mong) > 0.05:
        loi.append(f"trôi đo được {tt['troi_s_moi_gio']} s/giờ, mô phỏng {-k_mong:.3f}")
    ghi_bang(dong, os.path.join(tmp, "tang2.csv"))
    tom_tat(dong, tt)
    print(f"Lệch t_chuan so với thời điểm ho thật: lớn nhất {max(abs(x) for x in lech_t):.3f} s "
          f"(mô phỏng: phản xạ 0,05 s độ lệch chuẩn, bíp 0,03 s)")
    # thiếu nhật ký nhóm cuối -> lỗi rõ ràng
    try:
        lap_bang(bam, {}, doc_bip_may_phat([nk["dau"]]), su_kien, {})
        loi.append("không báo lỗi khi thiếu nhật ký bíp cuối")
    except SystemExit:
        pass
    print("KET QUA:", "DAT" if not loi else "KHONG DAT\n  " + "\n  ".join(loi))
    return 0 if not loi else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bam")
    ap.add_argument("--dba", nargs="*", default=[])
    ap.add_argument("--nhat-ky-bip", nargs="*", default=[])
    ap.add_argument("--su-kien", help="CSV sự kiện TC-01, cột t_epoch (giây, giờ NTP)")
    ap.add_argument("--cot-su-kien", default="t_epoch")
    ap.add_argument("--phut", help="CSV nhật ký mỗi phút TC-01, cột t_phut_epoch và la90_dba hoặc la90_dbfs")
    ap.add_argument("--hieu-chuan", help="a,b của dB(A) = a + b·dBFS cho TC-01 (am_hoc.py hieu-chuan)")
    ap.add_argument("--tre-trung-vi", type=float, default=0.0)
    ap.add_argument("--loai-tru", help="CSV khoảng loại trừ, cột bat_dau_epoch, ket_thuc_epoch")
    ap.add_argument("--ra", default="results/tang2.csv")
    ap.add_argument("--thu", action="store_true")
    a = ap.parse_args()
    if a.thu:
        return thu()
    if not (a.bam and a.nhat_ky_bip and a.su_kien):
        ap.error("cần --bam, --nhat-ky-bip và --su-kien")
    bam = doc_csv(a.bam)
    hc = tuple(float(x) for x in a.hieu_chuan.split(",")) if a.hieu_chuan else None
    phut = doc_phut(a.phut, hc) if a.phut else {}
    su_kien = [float(r[a.cot_su_kien]) for r in doc_csv(a.su_kien) if r.get(a.cot_su_kien)]
    lt = [(float(r["bat_dau_epoch"]), float(r["ket_thuc_epoch"])) for r in doc_csv(a.loai_tru)] if a.loai_tru else ()
    dong, tt = lap_bang(bam, doc_dba(a.dba), doc_bip_may_phat(a.nhat_ky_bip), su_kien, phut, a.tre_trung_vi, lt)
    ghi_bang(dong, a.ra)
    tom_tat(dong, tt)
    with open(os.path.splitext(a.ra)[0] + "_dong_bo.json", "w", encoding="utf-8") as f:
        json.dump(tt, f, ensure_ascii=False, indent=2)
    print("Đã ghi", a.ra)
    return 0


if __name__ == "__main__":
    sys.exit(main())
