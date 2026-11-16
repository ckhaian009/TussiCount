"""Ghép các tệp WAV 1 giờ của một phiên ghi (firmware TC01_Ghi_kiem_dinh) thành một tệp liền (Protocol 7.3, 16.22).

Firmware cắt mỗi tệp tối đa 1 giờ và ghi mỗi tệp một dòng vào TC-01_ghi.csv (giờ mẫu đầu, số mẫu). Công cụ này
đọc TC-01_ghi.csv trong thư mục bản sao của thẻ, lấy các tệp của MỘT phiên (am_hoc, de_sua, de_cham_1, de_cham_2,
ghi_thu), xếp theo giờ mẫu đầu, ghép liền. Khe hở giữa hai tệp liền nhau được chèn 0 cho đúng thời gian và báo ra
màn hình; hai tệp chồng nhau thì dừng. Ghi kèm tệp .json: giờ mẫu đầu (epoch), số mẫu, danh sách tệp, các khe hở.

Âm thanh KTX: chỉ chạy trên máy tính của Nhóm. Tệp ra phải ở ngoài Documents (iCloud) và ngoài kho GitHub,
ví dụ ~/TussiCount_KTX. Không tải lên dịch vụ trực tuyến.

  python3 tools/ghep_wav/ghep_wav.py ~/TussiCount_KTX/the_GHI_2026-11-16 de_sua ~/TussiCount_KTX/phan_de_sua.wav
  python3 tools/ghep_wav/ghep_wav.py <thu_muc> am_hoc,de_sua <tep_ra.wav>   # ghép hai phiên liền nhau (16.22)
  python3 tools/ghep_wav/ghep_wav.py <thu_muc> am_hoc,de_sua <tep_ra.wav> --tu 21:07:30   # bỏ phần trước giờ đó (đo âm học)
  python3 tools/ghep_wav/ghep_wav.py --thu      # phép thử trên dữ liệu tổng hợp
"""
import csv
import json
import os
import sys
import tempfile
import wave

TAN_SO = 16000
NGUONG_KHE_S = 0.05     # khe hở nhỏ hơn mức này coi là liền (sai số làm tròn giờ)


def kiem_duong_ra(p):
    a = os.path.abspath(os.path.expanduser(p))
    if "/Documents/" in a or "Mobile Documents" in a or "/GitHub/" in a:
        sys.exit("LOI: tep ra nam trong Documents/iCloud hoac kho GitHub. Chon ~/TussiCount_KTX.")
    os.makedirs(os.path.dirname(a), exist_ok=True)
    return a


def doc_wav(p):
    with wave.open(p, "rb") as w:
        if w.getframerate() != TAN_SO or w.getnchannels() != 1 or w.getsampwidth() != 2:
            sys.exit(f"LOI: {p} khong phai WAV 16 kHz, 16 bit, mot kenh")
        return w.getnframes(), w.readframes(w.getnframes())


def cat_dau(ra, meta, tu_hms):
    """Bỏ phần trước giờ tu_hms (giờ Việt Nam, cùng ngày với mẫu đầu) khỏi tệp đã ghép; cập nhật .json."""
    import datetime as dt
    vn = dt.timezone(dt.timedelta(hours=7))
    d0 = dt.datetime.fromtimestamp(meta["t_mau_dau_epoch"], vn)
    h, m, sec = (int(x) for x in tu_hms.split(":"))
    t_cat = d0.replace(hour=h, minute=m, second=sec, microsecond=0).timestamp()
    bo = int(round((t_cat - meta["t_mau_dau_epoch"]) * TAN_SO))
    if bo < 0 or bo >= meta["so_mau"]:
        sys.exit(f"LOI: gio cat {tu_hms} nam ngoai tep")
    with wave.open(ra, "rb") as w:
        w.setpos(bo); du_lieu = w.readframes(meta["so_mau"] - bo)
    with wave.open(ra, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(TAN_SO); w.writeframes(du_lieu)
    meta.update({"bo_dau_truoc": tu_hms, "so_mau_bo_dau": bo, "t_mau_dau_epoch": meta["t_mau_dau_epoch"] + bo / TAN_SO,
                 "so_mau": meta["so_mau"] - bo, "thoi_luong_s": (meta["so_mau"] - bo) / TAN_SO})
    json.dump(meta, open(os.path.splitext(ra)[0] + ".json", "w"), ensure_ascii=False, indent=1)
    print(f"Da bo {bo / TAN_SO:.1f} s dau (truoc {tu_hms}); con {meta['thoi_luong_s'] / 3600:.3f} gio")
    return meta


def ghep(thu_muc, phien, ra):
    bang = os.path.join(thu_muc, "TC-01_ghi.csv")
    if not os.path.exists(bang):
        sys.exit(f"LOI: khong thay {bang}")
    cac_phien = set(phien.split(","))          # nhiều phiên liền nhau: "am_hoc,de_sua"
    dong = [d for d in csv.DictReader(open(bang, encoding="utf-8")) if d["phien"] in cac_phien]
    if not dong:
        sys.exit(f"LOI: khong co tep nao cua phien '{phien}' trong TC-01_ghi.csv")
    dong.sort(key=lambda d: float(d["t_mau_dau_epoch"]))
    ra = kiem_duong_ra(ra)
    t0 = float(dong[0]["t_mau_dau_epoch"])
    tong, khe, ds = 0, [], []
    with wave.open(ra, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(TAN_SO)
        for d in dong:
            p = os.path.join(thu_muc, d["tep"])
            if not os.path.exists(p):
                sys.exit(f"LOI: thieu tep {d['tep']}")
            n, du_lieu = doc_wav(p)
            if n != int(d["so_mau"]):
                print(f"Canh bao: {d['tep']} co {n} mau, TC-01_ghi.csv ghi {d['so_mau']}")
            lech = float(d["t_mau_dau_epoch"]) - (t0 + tong / TAN_SO)
            if lech < -NGUONG_KHE_S:
                sys.exit(f"LOI: {d['tep']} chong len tep truoc {-lech:.3f} s")
            if lech > NGUONG_KHE_S:
                m = int(round(lech * TAN_SO))
                w.writeframes(b"\x00\x00" * m)
                khe.append({"truoc_tep": d["tep"], "giay": round(lech, 3)})
                print(f"Khe ho {lech:.3f} s truoc {d['tep']}: da chen 0")
                tong += m
            w.writeframes(du_lieu)
            tong += n
            ds.append({"tep": d["tep"], "t_mau_dau_epoch": float(d["t_mau_dau_epoch"]), "so_mau": n,
                       "mau_thieu_chen_0": int(d.get("mau_thieu_chen_0") or 0)})
    meta = {"phien": phien, "t_mau_dau_epoch": t0, "so_mau": tong, "thoi_luong_s": tong / TAN_SO,
            "tep": ds, "khe_ho": khe}
    json.dump(meta, open(os.path.splitext(ra)[0] + ".json", "w"), ensure_ascii=False, indent=1)
    print(f"Da ghep {len(ds)} tep -> {ra}: {tong / TAN_SO / 3600:.3f} gio, {len(khe)} khe ho")
    return meta


def thu():
    import random
    with tempfile.TemporaryDirectory() as d:
        os.environ["HOME"] = d
        rows, t = [], 1794800000.0
        for i, (n, khe) in enumerate([(TAN_SO * 5, 0), (TAN_SO * 5, 0), (TAN_SO * 2, 1.5)]):
            t += khe
            ten = f"TC-01_tep{i}.wav"
            with wave.open(os.path.join(d, ten), "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(TAN_SO)
                w.writeframes(bytes(random.Random(i).getrandbits(8) for _ in range(n * 2)))
            rows.append([ten, "de_sua", "TC-01", f"{t:.3f}", "", n, n / TAN_SO, 0, 0])
            t += n / TAN_SO
        rows[0][1] = "am_hoc"
        rows.append(["THU_x.wav", "ghi_thu", "TC-01", "1794700000.000", "", 10, 0, 0, 0])
        with open(os.path.join(d, "TC-01_ghi.csv"), "w", newline="") as f:
            c = csv.writer(f)
            c.writerow("tep,phien,thiet_bi,t_mau_dau_epoch,t_mau_dau_gio_vn,so_mau,thoi_luong_s,mau_thieu_chen_0,"
                       "mau_cham_dinh".split(","))
            c.writerows(rows)
        m1 = ghep(d, "de_sua", os.path.join(d, "ra", "chi_de_sua.wav"))
        assert m1["so_mau"] == TAN_SO * 5 + int(1.5 * TAN_SO) + TAN_SO * 2, m1["so_mau"]
        m = ghep(d, "am_hoc,de_sua", os.path.join(d, "ra", "phan_de_sua.wav"))
        assert m["so_mau"] == TAN_SO * 12 + int(1.5 * TAN_SO), m["so_mau"]
        assert len(m["khe_ho"]) == 1 and abs(m["khe_ho"][0]["giay"] - 1.5) < 1e-6
        with wave.open(os.path.join(d, "ra", "phan_de_sua.wav")) as w:
            assert w.getnframes() == m["so_mau"]
        import datetime as dt
        t_cat = dt.datetime.fromtimestamp(m["t_mau_dau_epoch"] + 3, dt.timezone(dt.timedelta(hours=7))).strftime("%H:%M:%S")
        n0 = m["so_mau"]; m2 = cat_dau(os.path.join(d, "ra", "phan_de_sua.wav"), m, t_cat)
        assert m2["so_mau"] == n0 - 3 * TAN_SO, (m2["so_mau"], n0)
        with wave.open(os.path.join(d, "ra", "phan_de_sua.wav")) as w:
            assert w.getnframes() == m2["so_mau"]
        print("PHEP THU: DAT")


if __name__ == "__main__":
    if "--thu" in sys.argv:
        thu()
    elif len(sys.argv) == 4:
        ghep(*sys.argv[1:])
    elif len(sys.argv) == 6 and sys.argv[4] == "--tu":
        cat_dau(sys.argv[3], ghep(*sys.argv[1:4]), sys.argv[5])
    else:
        print(__doc__)
        sys.exit(2)
