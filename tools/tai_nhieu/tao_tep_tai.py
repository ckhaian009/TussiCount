# Tạo tệp tải nhiễu 60 phút theo từng bước (mỗi lần chạy tối đa ~140 s), trạng thái lưu ở ~/tai/.
import csv, json, random, subprocess, sys, time, pathlib
import numpy as np
SR = 22050; N = SR * 3600
goc = pathlib.Path(sys.argv[1]); buoc = sys.argv[2]
W = pathlib.Path.home() / "tai"; W.mkdir(exist_ok=True)
def doc(p):
    b = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(b, np.float32)
def rms(x): return float(np.sqrt(np.mean(x.astype(np.float64) ** 2)) + 1e-9)
rng = random.Random(7575)
cv = sorted((goc / "commonvoice/cv-corpus-27.0-2026-09-11/vi/clips").glob("*.mp3")); rng.shuffle(cv)
bo = {"coughing", "sneezing", "breathing", "snoring", "laughing", "crying_baby"}
meta = list(csv.DictReader(open(goc / "esc50/ESC-50-master/meta/esc50.csv")))
ds = [goc / "esc50/ESC-50-master/audio" / m["filename"] for m in meta if m["category"] not in bo]; rng.shuffle(ds)
if buoc in ("noi", "nen"):
    ds_ = cv if buoc == "noi" else ds
    st = W / f"{buoc}.json"; s = json.load(open(st)) if st.exists() else {"k": 0, "mau": 0, "so": 0}
    t0 = time.time(); r2 = random.Random(s["k"])
    with open(W / f"{buoc}.f32", "ab") as f:
        while s["mau"] < N and s["k"] < len(ds_) and time.time() - t0 < 140:
            x = doc(ds_[s["k"]]); s["k"] += 1
            if len(x) < SR // 2 or rms(x) < 1e-4: continue
            x = (x / rms(x) * 0.1).astype(np.float32)
            if buoc == "noi": x = np.concatenate([x, np.zeros(int(SR * r2.uniform(0.2, 0.6)), np.float32)])
            f.write(x.tobytes()); s["mau"] += len(x); s["so"] += 1
    json.dump(s, open(st, "w")); print(buoc, s, "XONG" if s["mau"] >= N else "CHUA XONG")
elif buoc == "tron":
    a = np.fromfile(W / "noi.f32", np.float32)[:N]; b = np.fromfile(W / "nen.f32", np.float32)[:N]
    a = np.pad(a, (0, N - len(a))); b = np.pad(b, (0, N - len(b)))
    t = a + b * 10 ** (-8 / 20); t = t / np.max(np.abs(t)) * 0.89
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-b:a", "96k", sys.argv[3]], input=t.astype(np.float32).tobytes(), check=True)
    print("xong", sys.argv[3], len(t) / SR / 60, "phut")
