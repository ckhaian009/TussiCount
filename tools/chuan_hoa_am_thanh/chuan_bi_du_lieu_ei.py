"""Chuẩn bị dữ liệu huấn luyện mô hình nền cho Edge Impulse (Protocol mục 8).

Đầu ra: WAV 16 kHz, một kênh, PCM 16 bit, mỗi đoạn đúng 1 giây (khớp cửa sổ 1 giây của thiết bị),
nằm trong data/ei_upload/<training|testing>/<cough|noise>/ (không đưa lên GitHub).

Nguồn và cách cắt:
  cough  COUGHVID 3.0, 3.000 bản ghi trong results/coughvid_chon_3000.csv. Tìm các vùng năng lượng
         (khung 20 ms, bước 10 ms, nhấn tần cao 0,97); lấy tối đa 3 vùng to nhất, cách nhau ≥ 0,4 s;
         mỗi vùng cắt 1 giây, điểm bắt đầu vùng nằm ngẫu nhiên trong [0,05; 0,35] s của đoạn
         (mô phỏng cửa sổ trượt 0,5 s gặp tiếng ho ở các vị trí khác nhau).
  noise  ESC-50 (1.960 tệp, đã bỏ lớp coughing): mỗi tệp 5 giây chia 5 đoạn 1 giây, bỏ đoạn im lặng
         (RMS < −65 dBFS), lấy ngẫu nhiên tối đa 3 đoạn mỗi tệp.
         Common Voice 27.0 tiếng Việt (1.000 đoạn): chia đoạn 1 giây liên tiếp, giữ đoạn có tiếng nói
         (RMS ≥ −50 dBFS), tối đa 4 đoạn mỗi tệp.
Chia huấn luyện / kiểm tra theo nhóm để một người hoặc một bản ghi gốc không nằm ở cả hai tập:
  COUGHVID theo bản ghi (uuid), 20% bản ghi sang kiểm tra (seed 2026);
  ESC-50 theo fold có sẵn của bộ dữ liệu: fold 5 làm kiểm tra, fold 1–4 huấn luyện;
  Common Voice theo người nói (client_id), 20% người nói sang kiểm tra (seed 2026).
Mức: mỗi đoạn được chuẩn hoá đỉnh về một mức ngẫu nhiên đều trong [−35; −3] dBFS, cùng phân bố cho
hai nhãn, để mô hình không học “to là ho”.
Ghi chép: results/ei_du_lieu_mo_hinh_nen.csv (từng đoạn) và results/ei_du_lieu_mo_hinh_nen_tom_tat.json.
Chạy từ thư mục gốc của kho:  python3 tools/chuan_hoa_am_thanh/chuan_bi_du_lieu_ei.py
"""
import csv
import glob
import hashlib
import json
import os
import random
import subprocess
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool

import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
SEED, SR = 2026, 16000
OUT = "data/ei_upload"
MANIFEST = "results/ei_du_lieu_mo_hinh_nen.csv"
SUMMARY = "results/ei_du_lieu_mo_hinh_nen_tom_tat.json"
TEST_FRAC = 0.20
LEVEL_RANGE = (-35.0, -3.0)
CVD_MAX_EVENTS, ESC_MAX_SEG, CV_MAX_SEG = 3, 3, 4
ESC_SILENT_DB, CV_SPEECH_DB = -65.0, -50.0


def decode(path):
    """Giải mã mọi định dạng (webm, ogg, wav, mp3) về float32 một kênh 16 kHz bằng ffmpeg."""
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                       capture_output=True)
    if r.returncode != 0:
        return None
    return np.frombuffer(r.stdout, dtype=np.float32).astype(np.float64)


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(np.square(x))) + 1e-12)


def frame_db(x):
    y = np.append(x[0], x[1:] - 0.97 * x[:-1])
    n, h = int(0.020 * SR), int(0.010 * SR)
    if len(y) < n:
        y = np.pad(y, (0, n - len(y)))
    idx = np.arange(0, len(y) - n + 1, h)
    return np.array([rms_db(y[i:i + n]) for i in idx])


def rng_for(key):
    return random.Random(int(hashlib.sha256(f"{SEED}:{key}".encode()).hexdigest()[:12], 16))


def normalise(seg, key):
    target = rng_for("muc:" + key).uniform(*LEVEL_RANGE)
    pk = np.max(np.abs(seg))
    if pk <= 0:
        return None, None, None
    g = 10 ** (target / 20) / pk
    return np.clip(seg * g, -1, 1), round(target, 2), round(20 * np.log10(g), 2)


def take_1s(x, start):
    start = int(round(start * SR))
    start = max(0, min(start, max(0, len(x) - SR)))
    seg = x[start:start + SR]
    if len(seg) < SR:
        seg = np.pad(seg, (0, SR - len(seg)))
    return seg, start / SR


def cough_regions(x):
    db = frame_db(x)
    floor, peak = np.percentile(db, 10), db.max()
    if peak - floor < 15:
        return [], "nen_qua_on"
    thr = max(floor + 12, peak - 25)
    on = db > thr
    regs, s = [], None
    for i, m in enumerate(on):
        if m and s is None:
            s = i
        if not m and s is not None:
            regs.append([s, i - 1]); s = None
    if s is not None:
        regs.append([s, len(on) - 1])
    merged = []
    for r in regs:
        if merged and r[0] - merged[-1][1] <= 6:
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    out = [(r[0] * 0.01, r[1] * 0.01 + 0.02, float(db[r[0]:r[1] + 1].max())) for r in merged if (r[1] - r[0]) >= 3]
    out = [o for o in out if o[1] - o[0] <= 1.2]
    out.sort(key=lambda o: -o[2])
    chosen = []
    for o in out:
        if all(abs(o[0] - c[0]) >= 0.4 for c in chosen):
            chosen.append(o)
        if len(chosen) == CVD_MAX_EVENTS:
            break
    return chosen, ""


def job_coughvid(args):
    path, uuid, split = args
    x = decode(path)
    if x is None or len(x) < SR // 2:
        return [], f"{uuid}:giai_ma_loi"
    regs, note = cough_regions(x)
    rows = []
    for k, (t0, t1, lv) in enumerate(regs, 1):
        off = rng_for(f"lech:{uuid}:{k}").uniform(0.05, 0.35)
        seg, s = take_1s(x, t0 - off)
        key = f"cvd_{uuid}_e{k}"
        seg, target, gain = normalise(seg, key)
        if seg is None:
            continue
        rows.append(write(seg, "cough", split, key, "COUGHVID", os.path.basename(path), uuid, s, target, gain,
                          f"vung {t0:.2f}-{t1:.2f}s"))
    return rows, (f"{uuid}:{note}" if note else ("" if rows else f"{uuid}:khong_co_vung"))


def job_esc(args):
    path, fold, split = args
    x = decode(path)
    base = os.path.splitext(os.path.basename(path))[0]
    if x is None:
        return [], f"{base}:giai_ma_loi"
    cands = [i for i in range(5) if rms_db(x[i * SR:(i + 1) * SR]) >= ESC_SILENT_DB and len(x) >= (i + 1) * SR]
    pick = sorted(rng_for("esc:" + base).sample(cands, min(ESC_MAX_SEG, len(cands))))
    rows = []
    for i in pick:
        key = f"esc_{base}_s{i}"
        seg, target, gain = normalise(x[i * SR:(i + 1) * SR], key)
        if seg is not None:
            rows.append(write(seg, "noise", split, key, "ESC-50", os.path.basename(path), f"fold{fold}", float(i),
                              target, gain, base.split("-")[-1]))
    return rows, ""


def job_cv(args):
    path, speaker, split = args
    x = decode(path)
    base = os.path.splitext(os.path.basename(path))[0]
    if x is None:
        return [], f"{base}:giai_ma_loi"
    cands = [i for i in range(len(x) // SR) if rms_db(x[i * SR:(i + 1) * SR]) >= CV_SPEECH_DB]
    rows = []
    for i in cands[:CV_MAX_SEG]:
        key = f"cv_{base.replace('common_voice_vi_', '')}_s{i}"
        seg, target, gain = normalise(x[i * SR:(i + 1) * SR], key)
        if seg is not None:
            rows.append(write(seg, "noise", split, key, "CommonVoice-vi", os.path.basename(path), speaker[:12],
                              float(i), target, gain, ""))
    return rows, ""


def write(seg, label, split, key, source, src_file, group, start, target, gain, note):
    d = os.path.join(OUT, split, label)
    os.makedirs(d, exist_ok=True)
    name = f"{label}.{key}.wav"
    sf.write(os.path.join(d, name), seg, SR, subtype="PCM_16")
    return {"file": f"{split}/{label}/{name}", "label": label, "split": split, "source": source,
            "source_file": src_file, "group": group, "start_s": f"{start:.3f}", "peak_dbfs": target,
            "gain_db": gain, "note": note}


def group_split(groups, frac):
    g = sorted(set(groups))
    random.Random(SEED).shuffle(g)
    test = set(g[:int(round(len(g) * frac))])
    return lambda k: "testing" if k in test else "training"


def main():
    if os.path.exists(OUT) and glob.glob(os.path.join(OUT, "*", "*", "*.wav")):
        print("Da co du lieu trong", OUT, "- xoa thu muc do neu muon tao lai."); return 1
    jobs = []
    cvd = list(csv.DictReader(open("results/coughvid_chon_3000.csv", encoding="utf-8")))
    sp = group_split([r["uuid"] for r in cvd], TEST_FRAC)
    jobs += [(job_coughvid, (os.path.join("data/coughvid/audio", r["file"]), r["uuid"], sp(r["uuid"]))) for r in cvd]
    meta = list(csv.DictReader(open("data/esc50/ESC-50-master/meta/esc50.csv", encoding="utf-8")))
    have = set(os.listdir("data/esc50/ESC-50-master/audio"))
    jobs += [(job_esc, (os.path.join("data/esc50/ESC-50-master/audio", m["filename"]), m["fold"],
                        "testing" if m["fold"] == "5" else "training")) for m in meta if m["filename"] in have and m["category"] != "coughing"]
    cvdir = "data/commonvoice/cv-corpus-27.0-2026-09-11/vi"
    spk = {}
    for t in ("train", "dev", "test", "other", "invalidated", "validated"):
        p = os.path.join(cvdir, t + ".tsv")
        if os.path.exists(p):
            for r in csv.DictReader(open(p, encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE):
                spk.setdefault(r["path"], r["client_id"])
    clips = sorted(os.listdir(os.path.join(cvdir, "clips")))
    sp2 = group_split([spk.get(c, c) for c in clips], TEST_FRAC)
    jobs += [(job_cv, (os.path.join(cvdir, "clips", c), spk.get(c, c), sp2(spk.get(c, c)))) for c in clips]
    print("So tep nguon:", len(jobs), "| CommonVoice khong ro nguoi noi:", sum(1 for c in clips if c not in spk), flush=True)
    rows, notes = [], []
    with Pool(4) as pool:
        for i, (r, n) in enumerate(pool.imap(run, jobs, chunksize=8), 1):
            rows += r
            if n:
                notes.append(n)
            if i % 500 == 0:
                print(f"  {i}/{len(jobs)} tep, {len(rows)} doan", flush=True)
    rows.sort(key=lambda r: r["file"])
    with open(MANIFEST, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    cnt = Counter((r["split"], r["label"], r["source"]) for r in rows)
    groups = defaultdict(set)
    for r in rows:
        groups[(r["source"], r["split"])].add(r["group"])
    summary = {"seed": SEED, "sample_rate": SR, "segment_s": 1.0, "level_range_dbfs": LEVEL_RANGE,
               "segments": {f"{s}|{l}|{src}": n for (s, l, src), n in sorted(cnt.items())},
               "groups": {f"{src}|{s}": len(g) for (src, s), g in sorted(groups.items())},
               "skipped_or_notes": Counter(n.split(":")[-1] for n in notes)}
    json.dump(summary, open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def run(job):
    f, a = job
    return f(a)


if __name__ == "__main__":
    sys.exit(main())
