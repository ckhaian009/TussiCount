"""Tạo dữ liệu tăng cường bằng vang tổng hợp và nền ồn (Protocol sửa đổi 16.7).

Mọi nguồn đều là dữ liệu mở đã chuẩn bị trong data/ei_upload (bảng kê results/ei_du_lieu_mo_hinh_nen.csv);
không dùng âm thanh ghi tại KTX. Mỗi tập (huấn luyện, kiểm tra) chỉ dùng đoạn, nền và kho RIR của chính nó:

  tập          kho RIR                         nền ồn để trộn
  training     data/tang_cuong/rir_huan_luyen  đoạn noise thuộc training (ESC-50 fold 1–4, giọng nói người nói huấn luyện)
  testing      data/tang_cuong/rir_kiem_tra    đoạn noise thuộc testing (ESC-50 fold 5, giọng nói người nói kiểm tra)

Với mỗi đoạn ho (cough) của tập: chọn một RIR ngẫu nhiên, tích chập, giữ 1 giây đầu; chọn một đoạn nền
(50% ESC-50, 50% giọng nói) và trộn ở SNR đều trong [0; 20] dB (SNR theo RMS cả đoạn 1 giây, cùng định nghĩa
với tập kiểm tra độ bền); chuẩn hoá đỉnh về mức ngẫu nhiên đều trong [−35; −3] dBFS như dữ liệu chính.

Đoạn không ho (noise) cũng được tăng cường theo cùng cách (RIR, rồi 50% số đoạn được trộn thêm một đoạn nền
khác nguồn ở SNR 0–20 dB). Lý do: nếu chỉ tiếng ho có vang và nền ồn, mô hình có thể học lối tắt
“có vang/ồn = ho”. Tập huấn luyện lấy số đoạn noise tăng cường bằng số đoạn cough tăng cường để giữ cân bằng
nhãn; tập kiểm tra tăng cường mọi đoạn.

Nhóm (metadata `nhom` trên Edge Impulse) của đoạn tăng cường là nhóm của đoạn gốc, để validation tách theo
nhóm vẫn giữ bản gốc và bản tăng cường cùng phía.

Đầu ra: data/ei_tang_cuong/<training|testing>/<cough|noise>/<nhan>.tc_<khoa>.wav (WAV 16 kHz, PCM 16 bit, 1 s)
        results/ei_tang_cuong.csv (từng tệp), results/ei_tang_cuong_tom_tat.json
Chạy từ gốc kho: python3 tools/tang_cuong/tao_du_lieu_tang_cuong.py
Chỉ cần numpy và scipy (đọc/ghi WAV bằng scipy.io.wavfile).
"""
import csv
import hashlib
import json
import os
import random
import sys
from collections import Counter

import numpy as np
from scipy.io import wavfile
from scipy.signal import fftconvolve

SEED = 2026
SR = 16000
LEVEL_RANGE = (-35.0, -3.0)
SNR_RANGE = (0.0, 20.0)
NOISE_MIX_FRAC = 0.5
SRC = "data/ei_upload"
OUT = "data/ei_tang_cuong"
MANIFEST_IN = "results/ei_du_lieu_mo_hinh_nen.csv"
MANIFEST_OUT = "results/ei_tang_cuong.csv"
SUMMARY_OUT = "results/ei_tang_cuong_tom_tat.json"
RIR_CSV = "results/tang_cuong_rir.csv"
BANK = {"training": "huan_luyen", "testing": "kiem_tra"}


def rng_for(key):
    return random.Random(int(hashlib.sha256(f"{SEED}:tc:{key}".encode()).hexdigest()[:12], 16))


def read_wav(path):
    sr, x = wavfile.read(path)
    assert sr == SR, (path, sr)
    if x.dtype == np.int16:
        x = x.astype(np.float64) / 32768.0
    else:
        x = x.astype(np.float64)
    assert x.ndim == 1 and len(x) == SR, (path, x.shape)
    return x


def write_wav(path, x):
    y = np.clip(np.round(x * 32767.0), -32768, 32767).astype(np.int16)
    wavfile.write(path, SR, y)


def rms(x):
    return float(np.sqrt(np.mean(x ** 2)) + 1e-12)


def reverb(x, h):
    return fftconvolve(x, h)[:SR]


def mix(sig, bg, snr_db):
    g = rms(sig) / (rms(bg) * 10 ** (snr_db / 20))
    return sig + g * bg


def normalise(x, key):
    muc = rng_for("muc:" + key).uniform(*LEVEL_RANGE)
    pk = np.max(np.abs(x))
    return x * (10 ** (muc / 20) / pk), muc


def main():
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(root)
    rows = list(csv.DictReader(open(MANIFEST_IN, encoding="utf-8")))
    rir_info = {}
    for r in csv.DictReader(open(RIR_CSV, encoding="utf-8")):
        rir_info[(r["bank"], int(r["id"]))] = r
    out_rows = []
    for split in ("training", "testing"):
        bank = BANK[split]
        rirs = np.load(f"data/tang_cuong/rir_{bank}.npz")["rir"].astype(np.float64)
        part = sorted([r for r in rows if r["split"] == split], key=lambda r: r["file"])
        cough = [r for r in part if r["label"] == "cough"]
        noise = [r for r in part if r["label"] == "noise"]
        esc = [r for r in noise if r["source"] == "ESC-50"]
        cv = [r for r in noise if r["source"] != "ESC-50"]
        if split == "training":
            pick = rng_for("chon_noise_training")
            noise_sel = sorted(pick.sample(noise, min(len(cough), len(noise))), key=lambda r: r["file"])
        else:
            noise_sel = noise
        for lab, items in (("cough", cough), ("noise", noise_sel)):
            d = os.path.join(OUT, split, lab)
            os.makedirs(d, exist_ok=True)
            for i, r in enumerate(items):
                stem = os.path.basename(r["file"])[:-4]
                khoa = stem.split(".", 1)[1]
                key = f"{split}|{lab}|{khoa}"
                rng = rng_for(key)
                x = read_wav(os.path.join(SRC, r["file"]))
                rid = rng.randrange(len(rirs))
                y = reverb(x, rirs[rid])
                bg_file, bg_src, snr = "", "", ""
                if lab == "cough" or rng.random() < NOISE_MIX_FRAC:
                    pool = esc if rng.random() < 0.5 else cv
                    for _ in range(20):
                        b = rng.choice(pool)
                        if b["group"] != r["group"]:
                            break
                    snr = rng.uniform(*SNR_RANGE)
                    y = mix(y, read_wav(os.path.join(SRC, b["file"])), snr)
                    bg_file, bg_src = b["file"], b["source"]
                y, muc = normalise(y, key)
                ten = f"{lab}.tc_{khoa}.wav"
                write_wav(os.path.join(d, ten), y)
                ri = rir_info[(bank, rid)]
                out_rows.append({
                    "file": f"{split}/{lab}/{ten}", "label": lab, "split": split,
                    "source_file": r["file"], "source": r["source"], "group": r["group"],
                    "rir_bank": bank, "rir_id": rid, "rt60_s": ri["t20_do_s"], "khoang_cach_m": ri["khoang_cach_m"],
                    "loai_phong": ri["loai"], "nen_file": bg_file, "nen_nguon": bg_src,
                    "snr_db": "" if snr == "" else round(snr, 2), "peak_dbfs": round(muc, 2)})
                if (i + 1) % 1000 == 0:
                    print(f"{split}/{lab}: {i + 1}/{len(items)}", flush=True)
            print(f"Xong {split}/{lab}: {len(items)} tep", flush=True)
    with open(MANIFEST_OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)
    summ = {
        "seed": SEED, "level_range_dbfs": LEVEL_RANGE, "snr_range_db": SNR_RANGE, "noise_mix_frac": NOISE_MIX_FRAC,
        "so_tep": dict(Counter(f"{r['split']}|{r['label']}" for r in out_rows)),
        "so_tep_theo_nguon": dict(Counter(f"{r['split']}|{r['label']}|{r['source']}" for r in out_rows)),
        "nen_theo_nguon": dict(Counter(f"{r['split']}|{r['label']}|{r['nen_nguon'] or 'khong_tron'}" for r in out_rows)),
    }
    json.dump(summ, open(SUMMARY_OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps(summ, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.exit(main())
