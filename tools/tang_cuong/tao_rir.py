"""Tạo kho đáp ứng xung phòng (RIR) tổng hợp cho tăng cường dữ liệu (Protocol sửa đổi 16.7).

Phòng hình hộp, tạo bằng pyroomacoustics (ảnh nguồn bậc 3 + dò tia, có hấp thụ của không khí):
  loại phòng     70% dạng hành lang (dài 8–25 m, rộng 1,8–3,5 m), 30% dạng phòng (3–8 × 3–6 m); cao 2,7–3,5 m
  thời gian vang mục tiêu RT60 đều trong [0,3; 1,2] s. Hệ số hấp thụ được hiệu chỉnh lặp (tối đa 4 lần)
                 cho đến khi T20 đo trên RIR (tích phân ngược Schroeder) lệch mục tiêu không quá 10%;
                 RIR không đạt sau 4 lần bị loại và tạo lại
  micro          gắn sát tường như thiết bị (cách tường 0,05–0,20 m), cao 1,5–2,0 m
  nguồn          cao 1,0–1,7 m, khoảng cách thẳng tới micro đều trong [1; 5] m, cách mọi mặt ≥ 0,3 m
Hai kho tách biệt: huấn luyện (400 RIR, seed 2026) và kiểm tra (200 RIR, seed 2027), để tập kiểm tra
tăng cường không dùng chung RIR với dữ liệu huấn luyện.
Mỗi RIR được cắt còn 1 giây đầu (16.000 mẫu): đoạn âm thanh dài 1 giây nên phần đuôi sau 1 giây
không ảnh hưởng tới kết quả tích chập được giữ lại. RIR được chuẩn hoá đỉnh về 1.

Đầu ra: data/tang_cuong/rir_<huan_luyen|kiem_tra>.npz (rir: N × 16000 float32)
        results/tang_cuong_rir.csv (thông số và T20 đo được của từng RIR)
Chạy từ gốc kho (cần pyroomacoustics; không cần dữ liệu âm thanh):
  python3 tools/tang_cuong/tao_rir.py
"""
import csv
import hashlib
import os
import sys

import numpy as np

SR = 16000
LEN = SR  # 1 giây
BANKS = (("huan_luyen", 400, 2026), ("kiem_tra", 200, 2027))
RT60_RANGE = (0.3, 1.2)
DIST_RANGE = (1.0, 5.0)
TOL = 0.10
OUT_DIR = "data/tang_cuong"
CSV_OUT = "results/tang_cuong_rir.csv"


def schroeder_t20(h, fs=SR):
    """T20: độ dốc của đường cong Schroeder từ −5 đến −25 dB, ngoại suy ra 60 dB."""
    e = np.cumsum(h[::-1] ** 2)[::-1]
    e = e / e[0]
    edc = 10 * np.log10(e + 1e-30)
    i5 = np.argmax(edc <= -5)
    i25 = np.argmax(edc <= -25)
    if i25 <= i5:
        return float("nan")
    t = np.arange(i5, i25) / fs
    slope = np.polyfit(t, edc[i5:i25], 1)[0]
    return float(-60 / slope) if slope < 0 else float("nan")


def drr_db(h, dist, fs=SR):
    """Tỉ số năng lượng trực tiếp/vang (cửa sổ ±2,5 ms quanh đường truyền thẳng)."""
    i0 = int(np.argmax(np.abs(h)))
    w = int(0.0025 * fs)
    d = np.sum(h[max(0, i0 - w): i0 + w] ** 2)
    r = np.sum(h ** 2) - d
    return float(10 * np.log10(d / max(r, 1e-30)))


def sample_geometry(rng):
    """Bốc khoảng cách trước (đều trong [1; 5] m), rồi tìm phòng và vị trí đặt được khoảng cách đó,
    để phân bố khoảng cách không bị lệch về phía gần do phòng hẹp."""
    d = rng.uniform(*DIST_RANGE)
    for _ in range(200):
        hanh_lang = rng.random() < 0.7
        if hanh_lang:
            dims = [rng.uniform(8, 25), rng.uniform(1.8, 3.5), rng.uniform(2.7, 3.5)]
        else:
            dims = [rng.uniform(3, 8), rng.uniform(3, 6), rng.uniform(2.7, 3.5)]
        L, W, H = dims
        for _ in range(200):
            # micro sát một bức tường dọc (y gần 0 hoặc gần W)
            wall_off = rng.uniform(0.05, 0.20)
            my = wall_off if rng.random() < 0.5 else W - wall_off
            mic = [rng.uniform(0.5, L - 0.5), my, rng.uniform(1.5, 2.0)]
            sz = rng.uniform(1.0, 1.7)
            dz = sz - mic[2]
            rxy = np.sqrt(d ** 2 - dz ** 2)
            ang = rng.uniform(0, 2 * np.pi)
            src = [mic[0] + rxy * np.cos(ang), mic[1] + rxy * np.sin(ang), sz]
            if 0.3 <= src[0] <= L - 0.3 and 0.3 <= src[1] <= W - 0.3:
                return ("hanh_lang" if hanh_lang else "phong"), dims, mic, src, d
    raise RuntimeError("khong dat duoc nguon trong phong")


def make_rir(pra, dims, mic, src, rt60_target, rt60_ask, seed):
    np.random.seed(seed)
    e_abs, _ = pra.inverse_sabine(rt60_ask, dims)
    room = pra.ShoeBox(dims, fs=SR, materials=pra.Material(float(e_abs)), max_order=3,
                       ray_tracing=True, air_absorption=True)
    room.set_ray_tracing(receiver_radius=0.5, n_rays=8000, energy_thres=1e-6)
    room.add_source(src)
    room.add_microphone(mic)
    room.compute_rir()
    return np.asarray(room.rir[0][0], dtype=np.float64)


def main():
    import pyroomacoustics as pra
    os.makedirs(OUT_DIR, exist_ok=True)
    rows = []
    for bank, n, seed in BANKS:
        rng = np.random.default_rng(seed)
        rirs = []
        tries = 0
        while len(rirs) < n:
            tries += 1
            kind, dims, mic, src, dist = sample_geometry(rng)
            target = rng.uniform(*RT60_RANGE)
            ask = target
            ok = False
            for it in range(4):
                s = int(hashlib.sha256(f"{bank}:{len(rirs)}:{tries}:{it}".encode()).hexdigest()[:8], 16)
                try:
                    h = make_rir(pra, dims, mic, src, target, ask, s)
                except ValueError:
                    break  # phòng quá lớn so với RT60 yêu cầu (hấp thụ > 1)
                t20 = schroeder_t20(h)
                if np.isfinite(t20) and abs(t20 - target) <= TOL * target:
                    ok = True
                    break
                if not np.isfinite(t20) or t20 <= 0:
                    break
                ask = ask * target / t20
            if not ok:
                continue
            drr = drr_db(h, dist)
            h1 = np.zeros(LEN)
            m = min(LEN, len(h))
            h1[:m] = h[:m]
            h1 /= np.max(np.abs(h1))
            idx = len(rirs)
            rirs.append(h1.astype(np.float32))
            rows.append({"bank": bank, "id": idx, "loai": kind,
                         "dai_m": round(dims[0], 2), "rong_m": round(dims[1], 2), "cao_m": round(dims[2], 2),
                         "rt60_muc_tieu_s": round(target, 3), "t20_do_s": round(t20, 3), "so_lan_hieu_chinh": it + 1,
                         "khoang_cach_m": round(dist, 2), "drr_db": round(drr, 1),
                         "mic": ";".join(f"{v:.2f}" for v in mic), "nguon": ";".join(f"{v:.2f}" for v in src)})
            if len(rirs) % 50 == 0:
                print(f"{bank}: {len(rirs)}/{n} (da thu {tries})", flush=True)
        arr = np.stack(rirs)
        np.savez_compressed(os.path.join(OUT_DIR, f"rir_{bank}.npz"), rir=arr)
        print(f"Xong kho {bank}: {len(rirs)} RIR sau {tries} lan thu", flush=True)
    with open(CSV_OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    for bank, _, _ in BANKS:
        p = os.path.join(OUT_DIR, f"rir_{bank}.npz")
        print(p, hashlib.sha256(open(p, "rb").read()).hexdigest())


if __name__ == "__main__":
    sys.exit(main())
