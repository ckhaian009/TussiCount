"""Phân tích âm học: hiệu chuẩn mức âm (Protocol 7.5), cân bằng khuếch đại hai thiết bị (16.8),
phổ suy hao qua cửa và thời gian vang (16.9). Chạy trên máy tính của Nhóm (tệp ghi âm KTX không rời máy).

Dòng lệnh:
  python3 tools/am_hoc/am_hoc.py hieu-chuan <bang.csv> [--ra ket_qua.json]
      bang.csv: cột thiet_bi (TC-01/TC-02), laeq_dbfs (thiết bị), laeq_dba (máy đo); ≥ 5 mức mỗi thiết bị.
      In phương trình dB(A) = a + b·dBFS, R², sai số dư lớn nhất cho từng thiết bị; hệ số khuếch đại số (16.8)
      để hai thiết bị cho cùng dBFS ở cùng mức nhiễu hồng (lấy TC-01 làm chuẩn, chênh ≤ 1 dB là đạt).
  python3 tools/am_hoc/am_hoc.py suy-hao <ghi_am.wav> <mo_bd_s> <dong_bd_s> [--dai 30]
      Mức theo dải 1/3 octave 125 Hz – 8 kHz của đoạn nhiễu hồng khi cửa mở và khi cửa đóng (bỏ 2 s đầu và cuối
      mỗi đoạn); suy hao = mức cửa mở − mức cửa đóng.
  python3 tools/am_hoc/am_hoc.py t20 <ghi_am.wav> <t_no_1> [<t_no_2> ...]
      Thời gian vang T20 (tích phân ngược Schroeder, −5 đến −25 dB) theo dải octave 500 Hz – 4 kHz cho từng
      tiếng nổ bóng bay (thời điểm gần đúng, giây), báo cáo trung vị mỗi dải.
"""
import argparse
import csv
import json
import sys

import numpy as np
from scipy import signal
from scipy.io import wavfile

DAI_1_3 = [125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000]
DAI_OCT = [500, 1000, 2000, 4000]


def doc_wav(p):
    sr, x = wavfile.read(p)
    x = x.astype(np.float64) / (32768.0 if x.dtype == np.int16 else 1.0)
    if x.ndim > 1:
        x = x.mean(axis=1)
    return sr, x


def loc_dai(fc, fs, phan=3, bac=4):
    k = 2 ** (1 / (2 * phan))
    lo, hi = fc / k, min(fc * k, 0.999 * fs / 2)
    return signal.butter(bac, [lo, hi], btype="band", fs=fs, output="sos")


def hieu_chuan(bang):
    out = {}
    by = {}
    for r in bang:
        by.setdefault(r["thiet_bi"], []).append((float(r["laeq_dbfs"]), float(r["laeq_dba"])))
    for tb, v in sorted(by.items()):
        x = np.array([a for a, _ in v])
        y = np.array([b for _, b in v])
        b, a = np.polyfit(x, y, 1)
        du = y - (a + b * x)
        r2 = 1 - np.sum(du ** 2) / np.sum((y - y.mean()) ** 2)
        out[tb] = {"so_muc": int(len(x)), "a": float(a), "b": float(b), "r2": float(r2), "sai_so_du_lon_nhat_db": float(np.max(np.abs(du)))}
    if "TC-01" in out and "TC-02" in out:
        # cùng một mức dB(A), dBFS của TC-02 phải bằng của TC-01: dbfs = (dBA − a)/b
        ref = np.linspace(55, 75, 5)
        d1 = (ref - out["TC-01"]["a"]) / out["TC-01"]["b"]
        d2 = (ref - out["TC-02"]["a"]) / out["TC-02"]["b"]
        chenh = float(np.mean(d1 - d2))
        out["can_bang_16_8"] = {"chenh_dbfs_TC01_tru_TC02": chenh, "he_so_khuech_dai_TC02": float(10 ** (chenh / 20)),
                                "dat_khong_can_chinh": abs(chenh) <= 1.0}
    return out


def muc_dai(x, fs):
    return {fc: float(10 * np.log10(np.mean(signal.sosfilt(loc_dai(fc, fs), x) ** 2) + 1e-30)) for fc in DAI_1_3 if fc * 2 ** (1 / 6) < fs / 2}


def suy_hao(x, fs, mo, dong, dai=30.0, bo=2.0):
    a = x[int((mo + bo) * fs): int((mo + dai - bo) * fs)]
    b = x[int((dong + bo) * fs): int((dong + dai - bo) * fs)]
    ma, mb = muc_dai(a, fs), muc_dai(b, fs)
    return {str(fc): {"mo_db": ma[fc], "dong_db": mb[fc], "suy_hao_db": ma[fc] - mb[fc]} for fc in ma}


def t20_mot(h, fs):
    e = np.cumsum(h[::-1] ** 2)[::-1]
    edc = 10 * np.log10(e / e[0] + 1e-30)
    i5 = np.argmax(edc <= -5)
    i25 = np.argmax(edc <= -25)
    if i25 <= i5:
        return float("nan")
    t = np.arange(i5, i25) / fs
    s = np.polyfit(t, edc[i5:i25], 1)[0]
    return float(-60 / s) if s < 0 else float("nan")


def t20(x, fs, cac_t, truoc=0.05, sau=1.5):
    ket = {str(fc): [] for fc in DAI_OCT}
    for t in cac_t:
        a = max(0, int((t - 0.5) * fs))
        b = min(len(x), int((t + 0.5) * fs))
        i0 = a + int(np.argmax(np.abs(x[a:b])))  # đỉnh tiếng nổ
        seg = x[i0: min(len(x), i0 + int(sau * fs))]
        # bỏ phần nền: cắt tại điểm năng lượng còn lại bằng nền (ước lượng ở 0,2 s cuối)
        for fc in DAI_OCT:
            y = signal.sosfilt(loc_dai(fc, fs, phan=1), seg)
            nen = np.mean(y[-int(0.2 * fs):] ** 2)
            env = signal.lfilter(np.ones(int(0.01 * fs)) / int(0.01 * fs), 1, y ** 2)
            vuot = np.where(env > 10 * nen)[0]
            cuoi = vuot[-1] if len(vuot) else len(y)
            ket[str(fc)].append(t20_mot(y[:cuoi], fs))
    return {fc: {"tung_lan": v, "trung_vi": float(np.nanmedian(v)) if np.any(np.isfinite(v)) else None} for fc, v in ket.items()}


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="lenh", required=True)
    a = sub.add_parser("hieu-chuan")
    a.add_argument("bang")
    a.add_argument("--ra")
    b = sub.add_parser("suy-hao")
    b.add_argument("wav")
    b.add_argument("mo", type=float)
    b.add_argument("dong", type=float)
    b.add_argument("--dai", type=float, default=30.0)
    b.add_argument("--ra")
    c = sub.add_parser("t20")
    c.add_argument("wav")
    c.add_argument("t", type=float, nargs="+")
    c.add_argument("--ra")
    g = ap.parse_args()
    if g.lenh == "hieu-chuan":
        kq = hieu_chuan(list(csv.DictReader(open(g.bang, encoding="utf-8"))))
    elif g.lenh == "suy-hao":
        fs, x = doc_wav(g.wav)
        kq = suy_hao(x, fs, g.mo, g.dong, g.dai)
    else:
        fs, x = doc_wav(g.wav)
        kq = t20(x, fs, g.t)
    s = json.dumps(kq, ensure_ascii=False, indent=1)
    if getattr(g, "ra", None):
        open(g.ra, "w", encoding="utf-8").write(s)
    print(s)


if __name__ == "__main__":
    sys.exit(main())
