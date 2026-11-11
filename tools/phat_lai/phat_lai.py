"""Trình phát thí nghiệm cho tầng kiểm định 1 (Protocol mục 7.1, việc t20). Chạy trên MacBook nối loa AUX.

Chỉ dùng thư viện chuẩn của Python và lệnh `afplay` có sẵn trên macOS. Mỗi lần phát được ghi thời điểm theo đồng
hồ máy (macOS tự đồng bộ NTP; đầu buổi ghi thêm độ lệch đo bằng `sntp`).

Cách chạy (từ gốc kho, trong Terminal):
    python3 tools/phat_lai/phat_lai.py 1 on          # buổi 1, phần đầu buổi + khung sinh hoạt ồn (từ 20:30)
    python3 tools/phat_lai/phat_lai.py 1 yen_tinh    # buổi 1, khung yên tĩnh (từ 21:00)
    python3 tools/phat_lai/phat_lai.py 2 bip dau     # tầng kiểm định 2 (21:00 buổi 2): 3 bíp đồng bộ đầu buổi
    python3 tools/phat_lai/phat_lai.py 2 bip cuoi    # tầng kiểm định 2: 3 bíp đồng bộ cuối buổi
Thêm --thu để chạy thử không cần loa (không gọi afplay, mọi lời nhắc tự trả lời rỗng);
thêm --nhanh cùng --thu để rút khoảng cách 8 s xuống 0,02 s (chỉ để kiểm tra trình tự).

Trình tự:
  đầu buổi  1) Đo suy hao qua cửa: nhiễu hồng 30 s trong phòng B2.103 khi cửa mở, rồi khi cửa đóng; nhập LAeq
               đo bằng máy đo đặt sát micro thiết bị.
            2) 3 tiếng bíp đồng bộ (cách nhau 2 s).
            3) 10 tiếng ho kiểm tra đầu buổi (hành lang, 1 m, mức vừa), cách nhau 8 s.
  mỗi khối  Hiện vị trí và khoảng cách đặt loa; chờ nhấn Enter. Phát tệp hiệu chuẩn 3 lần (cách 8 s), sau mỗi lần
            nhập mức đỉnh dB(A) đọc trên máy đo (chế độ MAX). Rồi tự phát các tiếng ho của khối, cách nhau 8 s.
Trong lúc phát tự động:  g = đánh dấu tiếng ho vừa phát bị gián đoạn (người đi qua, loa lỗi...)
                         p = tạm dừng / tiếp tục;  q = dừng hẳn (phần chưa phát được ghi là chưa phát)
  bip       (tầng kiểm định 2) Đo độ lệch đồng hồ bằng sntp, chờ Enter khi người quan sát 1 đã mở trang bấm giờ,
            phát 3 tiếng bíp cách nhau 2 s. Người quan sát 1 chạm BÍP đúng lúc nghe mỗi tiếng; công cụ
            tools/phan_tich/tao_bang_tang2.py dùng các cặp (thời điểm phát, thời điểm chạm) để quy giờ trang bấm về giờ NTP.
Nhật ký: results/phat_lai_nhat_ky/buoi<N>_<phan>_<ngay-gio>.csv (không có âm thanh, không có thông tin cá nhân).
"""
import csv
import datetime as dt
import os
import select
import subprocess
import sys
import termios
import time
import tty

CACH_S = 8.0
BIP_CACH_S = 2.0
LICH = "results/lich_phat_lai.csv"
TEP = "data/phat_lai/tep"
NHAT_KY = "results/phat_lai_nhat_ky"


def ten_tep(stt, he_so_db):
    return os.path.join(TEP, f"{int(stt):04d}_{int(he_so_db):+03d}dB.wav")


class Ban_phim:
    """Đọc phím không chặn trong lúc phát tự động."""

    def __init__(self, thu):
        self.thu = thu
        self.cu = None

    def __enter__(self):
        if not self.thu and sys.stdin.isatty():
            self.cu = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
        return self

    def __exit__(self, *a):
        if self.cu is not None:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.cu)

    def thuong(self):
        """Trả terminal về chế độ thường để nhập số và nhấn Enter."""
        if self.cu is not None:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.cu)

    def phim(self):
        """Chế độ đọc từng phím (trong lúc phát tự động)."""
        if self.cu is not None:
            tty.setcbreak(sys.stdin.fileno())

    def doc(self, cho_s):
        if self.thu or self.cu is None:
            time.sleep(max(0.0, cho_s) if not self.thu else 0)
            return None
        r, _, _ = select.select([sys.stdin], [], [], max(0.0, cho_s))
        return sys.stdin.read(1) if r else None


class Trinh_phat:
    def __init__(self, buoi, phan, thu):
        self.buoi, self.phan, self.thu = buoi, phan, thu
        os.makedirs(NHAT_KY, exist_ok=True)
        ngay = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        self.duong = os.path.join(NHAT_KY, f"buoi{buoi}_{phan}_{ngay}{'_thu' if thu else ''}.csv")
        self.f = open(self.duong, "w", newline="", encoding="utf-8")
        self.w = csv.DictWriter(self.f, fieldnames=[
            "buoi", "phan", "thu_tu_lich", "loai", "khoi", "stt", "tep", "he_so_db", "t_phat_epoch", "t_phat",
            "muc_do_dba", "gian_doan", "ghi_chu"])
        self.w.writeheader()
        self.dang = []  # tiến trình afplay đang chạy

    def ghi(self, **k):
        k.setdefault("buoi", self.buoi)
        k.setdefault("phan", self.phan)
        self.w.writerow(k)
        self.f.flush()

    def phat(self, tep):
        t = time.time()
        if not self.thu:
            if not os.path.exists(tep):
                raise FileNotFoundError(tep)
            self.dang.append(subprocess.Popen(["afplay", tep]))
            self.dang = [p for p in self.dang if p.poll() is None]
        return t

    def hoi(self, cau):
        if self.thu:
            return ""
        try:
            return input(cau).strip()
        except EOFError:
            return ""


def gio(t):
    return dt.datetime.fromtimestamp(t).strftime("%H:%M:%S.%f")[:-3]


def do_lech_dong_ho():
    try:
        r = subprocess.run(["sntp", "time.apple.com"], capture_output=True, text=True, timeout=15)
        return (r.stdout or r.stderr).strip().splitlines()[-1]
    except Exception as e:  # noqa: BLE001
        return f"khong do duoc ({e})"


def chuoi_tu_dong(tp, bp, cac, ghi_chu_khoi=""):
    """Phát lần lượt `cac` (danh sách dòng lịch) cách nhau 8 s. Trả về False nếu người chạy bấm q."""
    t0 = time.time()
    i = 0
    vua_phat = None
    while i < len(cac):
        dich = t0 + i * CACH_S
        while True:
            con = dich - time.time()
            if con <= 0:
                break
            k = bp.doc(min(con, 0.2))
            if k == "g" and vua_phat is not None:
                tp.ghi(thu_tu_lich=vua_phat["thu_tu"], loai="danh_dau", stt=vua_phat["stt"], gian_doan=1,
                       t_phat_epoch=f"{time.time():.3f}", t_phat=gio(time.time()), ghi_chu="gian doan (phim g)")
                print(f"   -> da danh dau gian doan: stt {vua_phat['stt']}")
            elif k == "p":
                print("   TAM DUNG. Nhan p de tiep tuc.")
                tp.ghi(loai="tam_dung", t_phat_epoch=f"{time.time():.3f}", t_phat=gio(time.time()))
                while bp.doc(0.5) != "p":
                    pass
                tp.ghi(loai="tiep_tuc", t_phat_epoch=f"{time.time():.3f}", t_phat=gio(time.time()))
                print("   TIEP TUC.")
                t0 = time.time() - i * CACH_S + CACH_S  # tiếp tục sau 8 s
                dich = t0 + i * CACH_S
            elif k == "q":
                for r in cac[i:]:
                    tp.ghi(thu_tu_lich=r["thu_tu"], loai=r["loai"], khoi=r["khoi"], stt=r["stt"], ghi_chu="chua phat (dung bang q)")
                return False
        r = cac[i]
        tep = ten_tep(r["stt"], r["he_so_db"])
        t = tp.phat(tep)
        tp.ghi(thu_tu_lich=r["thu_tu"], loai=r["loai"], khoi=r["khoi"], stt=r["stt"], tep=os.path.basename(tep),
               he_so_db=r["he_so_db"], t_phat_epoch=f"{t:.3f}", t_phat=gio(t), gian_doan=0, ghi_chu=ghi_chu_khoi)
        print(f"  [{gio(t)}] {i + 1:3d}/{len(cac)}  {r['loai']:17s} stt {r['stt']:>4s}  {r['do_lon'] or 'vua':4s} {r['he_so_db']} dB")
        vua_phat = r
        i += 1
    time.sleep(0 if tp.thu else 2.0)
    return True


def mo_ta_khoi(khoi):
    vt, kc = khoi.split("|")
    noi = "HANH LANG tang 1" if vt == "hanh_lang" else "TRONG PHONG B2.103, CUA DONG"
    return f"{noi}, cach micro TC-01 {kc.replace('m', ' m')}"


def bip_tang2(buoi, nhom, thu):
    """3 bíp đồng bộ cho trang bấm giờ của tầng kiểm định 2."""
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(root)
    tp = Trinh_phat(buoi, f"tang2_bip_{nhom}", thu)
    lech = do_lech_dong_ho() if not thu else "chay thu"
    tp.ghi(loai="bat_dau", t_phat_epoch=f"{time.time():.3f}", t_phat=gio(time.time()), ghi_chu=f"sntp: {lech}")
    print(f"=== Tang kiem dinh 2, bip {nhom}. Do lech dong ho: {lech}\n    Nhat ky: {tp.duong}")
    tp.hoi("Nguoi quan sat 1 mo trang bam gio, chon '" + ("Dau buoi" if nhom == "dau" else "Cuoi buoi")
           + "'. Dat loa o hanh lang, gan nguoi bam. Enter de phat 3 tieng bip: ")
    for j in range(3):
        t = tp.phat(os.path.join(TEP, "bip.wav"))
        tp.ghi(loai="bip_dong_bo", tep="bip.wav", t_phat_epoch=f"{t:.3f}", t_phat=gio(t), ghi_chu=f"tang2 {nhom} {j + 1}")
        print(f"  [{gio(t)}] bip {j + 1}/3")
        time.sleep(0 if thu else BIP_CACH_S)
    tp.ghi(loai="ket_thuc", t_phat_epoch=f"{time.time():.3f}", t_phat=gio(time.time()))
    print(f"Xong. Nhat ky: {tp.duong}")
    return 0


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    thu = "--thu" in sys.argv
    global CACH_S, BIP_CACH_S
    if thu and "--nhanh" in sys.argv:
        CACH_S, BIP_CACH_S = 0.02, 0.0
    if len(args) == 3 and args[1] == "bip" and args[2] in ("dau", "cuoi") and args[0] in ("1", "2", "3"):
        return bip_tang2(args[0], args[2], thu)
    if len(args) != 2 or args[1] not in ("on", "yen_tinh") or args[0] not in ("1", "2", "3"):
        print(__doc__)
        return 2
    buoi, phan = args
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(root)
    lich = [r for r in csv.DictReader(open(LICH, encoding="utf-8")) if r["buoi"] == buoi]
    tp = Trinh_phat(buoi, phan, thu)
    lech = do_lech_dong_ho() if not thu else "chay thu"
    tp.ghi(loai="bat_dau", t_phat_epoch=f"{time.time():.3f}", t_phat=gio(time.time()), ghi_chu=f"sntp: {lech}")
    print(f"=== Buoi {buoi}, phan {phan}. Do lech dong ho: {lech}\n    Nhat ky: {tp.duong}")
    with Ban_phim(thu) as bp:
        if phan == "on":
            for trang_thai in ("MO", "DONG"):
                bp.thuong()
                tp.hoi(f"Dat loa trong phong B2.103, cua {trang_thai}; may do sat micro TC-01. Enter de phat nhieu hong 30 s: ")
                t = tp.phat(os.path.join(TEP, "nhieu_hong_30s_+00dB.wav"))
                tp.ghi(loai=f"nhieu_hong_cua_{trang_thai.lower()}", tep="nhieu_hong_30s_+00dB.wav", he_so_db=0,
                       t_phat_epoch=f"{t:.3f}", t_phat=gio(t))
                time.sleep(0 if thu else 31)
                v = tp.hoi(f"  Nhap LAeq 30 s doc tren may do (dB(A)), cua {trang_thai}: ")
                tp.ghi(loai=f"do_suy_hao_cua_{trang_thai.lower()}", muc_do_dba=v, t_phat_epoch=f"{time.time():.3f}",
                       t_phat=gio(time.time()))
            bp.thuong()
            tp.hoi("Dat loa o HANH LANG tang 1, cach micro TC-01 1 m. Enter de phat 3 tieng bip va 10 tieng ho kiem tra: ")
            bp.phim()
            for j in range(3):
                t = tp.phat(os.path.join(TEP, "bip.wav"))
                tp.ghi(loai="bip_dong_bo", tep="bip.wav", t_phat_epoch=f"{t:.3f}", t_phat=gio(t))
                time.sleep(0 if thu else BIP_CACH_S)
            kt = [r for r in lich if r["loai"] == "kiem_tra_dau_buoi"]
            if not chuoi_tu_dong(tp, bp, kt, "hanh_lang|1m"):
                return 1
        phan_lich = [r for r in lich if r["khung_gio"] == phan]
        khoi = []
        for r in phan_lich:
            if not khoi or khoi[-1][0] != r["khoi_thu_tu"]:
                khoi.append((r["khoi_thu_tu"], r["khoi"], []))
            khoi[-1][2].append(r)
        han = {"on": "21:00", "yen_tinh": "21:45"}[phan]
        for so, (_, ten, cac) in enumerate(khoi, 1):
            hc = [r for r in cac if r["loai"] == "hieu_chuan"]
            o = [r for r in cac if r["loai"] == "o"]
            con_lai = sum(len(k[2]) for k in khoi[so - 1:]) * CACH_S / 60
            bp.thuong()
            print(f"\n--- Khoi {so}/{len(khoi)}: {mo_ta_khoi(ten)} | {len(o)} tieng ho | con khoang {con_lai:.1f} phut phat, han {han}")
            tp.hoi("Dat loa xong thi nhan Enter: ")
            tp.ghi(loai="bat_dau_khoi", khoi=ten, t_phat_epoch=f"{time.time():.3f}", t_phat=gio(time.time()))
            t0 = time.time()
            for j, r in enumerate(hc):
                while time.time() < t0 + j * CACH_S:
                    time.sleep(0.01)
                t = tp.phat(ten_tep(r["stt"], r["he_so_db"]))
                tp.ghi(thu_tu_lich=r["thu_tu"], loai="hieu_chuan", khoi=ten, stt=r["stt"],
                       tep=os.path.basename(ten_tep(r["stt"], r["he_so_db"])), he_so_db=r["he_so_db"],
                       t_phat_epoch=f"{t:.3f}", t_phat=gio(t), gian_doan=0)
                time.sleep(0 if thu else 2.0)
                v = tp.hoi(f"  Hieu chuan {j + 1}/3: nhap muc dinh dB(A) (MAX) doc tren may do: ")
                tp.ghi(thu_tu_lich=r["thu_tu"], loai="muc_hieu_chuan", khoi=ten, stt=r["stt"], muc_do_dba=v,
                       t_phat_epoch=f"{time.time():.3f}", t_phat=gio(time.time()))
            bp.phim()
            print("  Tu dong phat. Phim: g = gian doan, p = tam dung, q = dung.")
            if not chuoi_tu_dong(tp, bp, o, ten):
                print("Da dung.")
                return 1
    tp.ghi(loai="ket_thuc", t_phat_epoch=f"{time.time():.3f}", t_phat=gio(time.time()))
    print(f"\nXong buoi {buoi}, phan {phan}. Nhat ky: {tp.duong}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
