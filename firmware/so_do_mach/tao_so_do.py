# Tạo sơ đồ mạch + bảng nối dây TussiCount bản 2.0 (A4 ngang, 4 trang) -> HTML -> PDF/PNG/SVG.
import html, pathlib, json

OUT = pathlib.Path(__file__).parent
TEAL, INK, GRAY, LINE, RED, PALE = "#0F766E", "#121513", "#5A635E", "#C9CFCB", "#B42318", "#E6F2F0"
WIRE = {"do": "#D92D20", "den": "#121513", "vang": "#D9A400", "xanh la": "#16A34A", "xanh duong": "#2563EB",
        "trang": "#9AA19D", "cam": "#EA7A12", "tim": "#7C3AED"}
TEN_MAU = {"do": "đỏ", "den": "đen", "vang": "vàng", "xanh la": "xanh lá", "xanh duong": "xanh dương",
           "trang": "trắng", "cam": "cam", "tim": "tím"}
NGAY = "12/11/2026"
SANS = "'Be Vietnam Pro', sans-serif"
MONO = "'IBM Plex Mono', monospace"
e = html.escape

def T(x, y, s, size=13, fill=INK, anchor="start", weight=400, font=SANS, extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}" font-family="{font}" {extra}>{e(s)}</text>')

def L(x1, y1, x2, y2, c=INK, w=2, extra=""):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}" stroke-linecap="round" {extra}/>'

def R(x, y, w, h, fill="none", stroke=INK, sw=2, rx=8, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'

def dat(x, y):  # ký hiệu đất, đỉnh tại (x, y)
    return "".join([L(x, y, x, y + 12), L(x - 14, y + 12, x + 14, y + 12), L(x - 9, y + 18, x + 9, y + 18),
                    L(x - 4, y + 24, x + 4, y + 24)])

def nguon(x, y, ten, c=RED):  # cờ nguồn, chân tại (x, y), mũi tên phía trên
    return (f'<path d="M{x-11},{y-28} L{x},{y-44} L{x+11},{y-28} Z" fill="{c}"/>' + L(x, y, x, y - 28, INK, 2)
            + T(x, y - 52, ten, 14, c, "middle", 600, MONO))

def khung(trang, tieu_de, phu_de, ban_ve):
    s = [R(20, 20, 1148, 800, "none", INK, 2, 0)]
    s.append(T(44, 56, "TussiCount", 16, TEAL, weight=600))
    s.append(T(44, 92, tieu_de, 28, INK, weight=600))
    s.append(T(44, 118, phu_de, 13, GRAY))
    # khối tên bản vẽ
    x0, y0, w0, h = 760, 712, 408, 27
    rows = [("Đề tài", "TussiCount – đếm tiếng ho tự động tại ký túc xá"), ("Nhóm", "LÒ VI SÓNG · 12T1 · THPT FPT Cần Thơ"),
            ("Bản vẽ", ban_ve), ("Phiên bản", f"2.0 · {NGAY} · trang {trang}/4")]
    s.append(f'<rect x="{x0}" y="{y0}" width="{w0}" height="{h*4}" fill="#fff" stroke="{INK}" stroke-width="2"/>')
    for i, (a, b) in enumerate(rows):
        y = y0 + i * h
        if i: s.append(L(x0, y, x0 + w0, y, LINE, 1))
        s.append(T(x0 + 10, y + 18, a, 11, GRAY))
        s.append(T(x0 + 92, y + 18, b, 11.5, INK, weight=500 if i == 2 else 400))
    s.append(L(x0 + 82, y0, x0 + 82, y0 + h * 4, LINE, 1))
    return s

def hop(x, y, w, h, ten, phu, phu2=None):
    s = [R(x, y, w, h, "#fff", INK, 2, 10), T(x + w / 2, y + 30, ten, 17, INK, "middle", 600),
         T(x + w / 2, y + 50, phu, 11.5, GRAY, "middle")]
    if phu2: s.append(T(x + w / 2, y + 67, phu2, 11, GRAY, "middle"))
    return s

def day(x1, x2, y, mau, nhan_luoi, chan_trai, chan_phai):
    c = WIRE[mau]
    return [L(x1, y, x2, y, c, 3), T(x1 + 18, y - 7, nhan_luoi, 11, c if mau != "trang" else GRAY, weight=500, font=MONO),
            T(x1 - 10, y + 5, chan_trai, 13, INK, "end", 500, MONO), T(x2 + 10, y + 5, chan_phai, 13, INK, "start", 500, MONO),
            f'<circle cx="{x1}" cy="{y}" r="3.5" fill="{INK}"/>', f'<circle cx="{x2}" cy="{y}" r="3.5" fill="{INK}"/>']

def ghi_chu(x, y, dong, tieu="GHI CHÚ", w=360):
    s = [T(x, y, tieu, 13, TEAL, weight=600)]
    yy = y + 24
    for i, d in enumerate(dong):
        parts = d if isinstance(d, list) else [d]
        for j, p in enumerate(parts):
            s.append(T(x + (0 if j == 0 else 16), yy, (f"{i+1}. " if j == 0 else "") + p, 11.5, INK))
            yy += 17
        yy += 5
    return s

def canh_bao(x, y, w, h, dong):
    s = [R(x, y, w, h, "#FEF3F2", RED, 1.5, 8)]
    s.append(f'<path d="M{x+20},{y+30} L{x+31},{y+11} L{x+42},{y+30} Z" fill="{RED}"/>' + T(x + 31, y + 27, "!", 13, "#fff", "middle", 700))
    yy = y + 25
    for i, d in enumerate(dong):
        s.append(T(x + 52, yy, d, 12.5 if i == 0 else 11.5, RED if i == 0 else INK, weight=600 if i == 0 else 400))
        yy += 18
    return s

def svg_trang(noi_dung):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1188 840" width="297mm" height="210mm">'
            f'<rect width="1188" height="840" fill="#fff"/>{"".join(noi_dung)}</svg>')

# ============================================================== trang 1: sơ đồ TC-01
def so_do_tc01():
    s = khung(1, "SƠ ĐỒ MẠCH ĐIỆN – TC-01 (THIẾT BỊ ĐẾM, TẦNG 1)",
              "ESP32-S3 N16R8 đọc micro INMP441 qua I2S, ghi thẻ microSD qua SPI; không ghi âm, không LED; nguồn 5 V từ sạc dự phòng qua cáp USB-C.",
              "Sơ đồ nguyên lý TC-01")
    mx, my, mw, mh = 430, 190, 220, 470
    s += hop(mx, my, mw, mh, "ESP32-S3-DevKitC-1", "N16R8 · flash 16 MB · PSRAM 8 MB", "ổn áp trên bo: 5 V → 3,3 V")
    # nguồn trên
    s.append(nguon(490, my, "3V3"))
    # 5Vin không dùng
    x5 = 590
    s.append(L(x5, my, x5, my - 30, GRAY, 2, 'stroke-dasharray="4 4"'))
    s.append(L(x5 - 10, my - 40, x5 + 10, my - 20, RED, 3) + L(x5 - 10, my - 20, x5 + 10, my - 40, RED, 3))
    s.append(T(x5, my - 50, "5Vin", 14, RED, "middle", 600, MONO))
    # micro
    hx, hw = 860, 230
    s += hop(hx, 200, hw, 190, "Micro INMP441", "MEMS số, giao tiếp I2S")
    s.append(nguon(1010, 200, "3V3"))
    s.append(T(1018, 194, "VDD", 10, GRAY, font=MONO))
    for y, mau, luoi, a, b in [(268, "vang", "I2S_SCK", "GPIO4", "SCK"), (303, "xanh la", "I2S_WS", "GPIO5", "WS"),
                               (338, "xanh duong", "I2S_SD", "GPIO6", "SD")]:
        s += day(mx + mw, hx, y, mau, luoi, a, b)
    # L/R xuống đất
    s.append(T(hx + 10, 373, "L/R", 13, INK, weight=500, font=MONO))
    s.append(L(hx, 368, 800, 368, INK, 2) + dat(800, 368) + T(806, 360, "kênh trái", 10.5, GRAY))
    s.append(T(hx + hw - 10, 373, "GND", 13, INK, "end", 500, MONO) + L(hx + hw, 368, hx + hw + 30, 368) + dat(hx + hw + 30, 368))
    # thẻ nhớ
    s += hop(hx, 440, hw, 210, "Module thẻ microSD", "SPI · thẻ 32 GB, FAT32")
    s.append(nguon(1010, 440, "3V3"))
    s.append(T(1018, 434, "VCC", 10, GRAY, font=MONO))
    s.append(f'<rect x="862" y="404" width="128" height="24" rx="12" fill="{PALE}"/>' + T(926, 420, "đổi từ 5 V, 12/11", 10.5, TEAL, "middle", 600))
    for y, mau, luoi, a, b in [(508, "trang", "SD_CS", "GPIO15", "CS"), (543, "xanh la", "SPI_MOSI", "GPIO16", "MOSI"),
                               (578, "vang", "SPI_SCK", "GPIO17", "SCK"), (613, "xanh duong", "SPI_MISO", "GPIO18", "MISO")]:
        s += day(mx + mw, hx, y, mau, luoi, a, b)
    s.append(T(hx + hw - 10, 633, "GND", 13, INK, "end", 500, MONO) + L(hx + hw, 628, hx + hw + 30, 628) + dat(hx + hw + 30, 628))
    # GND bo
    s.append(T(mx + mw / 2, my + mh - 14, "GND", 13, INK, "middle", 500, MONO) + L(mx + mw / 2, my + mh, mx + mw / 2, my + mh + 18) + dat(mx + mw / 2, my + mh + 18))
    # sạc dự phòng + USB
    s += hop(50, 330, 230, 130, "Sạc dự phòng", "CUKTECH PB100P · 10.000 mAh")
    s.append(T(165, 418, "cổng USB-C ra 5 V", 12, INK, "middle"))
    s.append(T(165, 440, "bật dòng thấp: bấm nút 2 lần", 10.5, GRAY, "middle"))
    s.append(R(mx - 18, 380, 36, 44, "#fff", INK, 2, 7) + T(mx + 26, 407, "USB-C", 12, INK, weight=500, font=MONO))
    s.append(L(280, 400, mx - 18, 400, INK, 2) + L(280, 405, mx - 18, 405, INK, 2))
    s.append(T(346, 390, "cáp USB-C ↔ USB-C", 11.5, INK, "middle") + T(346, 425, "VBUS 5 V, GND", 10.5, GRAY, "middle"))
    # cảnh báo 5Vin
    s += canh_bao(44, 150, 360, 82, ["Không dùng chân 5Vin", "Trên mạch S3 này 5Vin không ra 5 V khi cấp qua USB:",
                                     "module thẻ nối vào đây sẽ không có điện (12/11)."])
    s += ghi_chu(44, 520, [
        ["Điểm cùng tên lưới (3V3) nối chung; ký hiệu", "đất là chân GND của bo."],
        ["INMP441 chỉ cấp 3,3 V. L/R nối GND → kênh trái."],
        ["Module thẻ cấp 3V3 của bo; T5 đạt thẻ nhớ 12/11."],
        ["Không dùng GPIO0, 3, 45, 46 (khởi động); 19, 20", "(USB); 26–37 (flash, PSRAM). Bỏ 10–13 từ 12/11."],
        ["Không lắp LED (Protocol 16.17): TC-01 không ghi âm."],
    ])
    return svg_trang(s)

# ============================================================== trang 3: sơ đồ TC-02
def so_do_tc02():
    s = khung(3, "SƠ ĐỒ MẠCH ĐIỆN – TC-02 (THIẾT BỊ GHI ÂM KIỂM ĐỊNH)",
              "ESP32 thường (ESP-WROOM-32) đọc INMP441 qua I2S, ghi WAV lên microSD qua SPI, LED sáng khi đang ghi; nguồn 5 V từ sạc dự phòng.",
              "Sơ đồ nguyên lý TC-02")
    mx, my, mw, mh = 430, 190, 220, 470
    s += hop(mx, my, mw, mh, "ESP32 DevKit", "ESP-WROOM-32 · flash 4 MB", "không PSRAM · cầu USB CP2102")
    s.append(nguon(490, my, "3V3"))
    s.append(nguon(590, my, "V5", "#EA7A12"))
    hx, hw = 860, 230
    s += hop(hx, 200, hw, 190, "Micro INMP441", "MEMS số, giao tiếp I2S")
    s.append(nguon(1010, 200, "3V3") + T(1018, 194, "VDD", 10, GRAY, font=MONO))
    for y, mau, luoi, a, b in [(268, "vang", "I2S_SCK", "G26", "SCK"), (303, "xanh la", "I2S_WS", "G25", "WS"),
                               (338, "xanh duong", "I2S_SD", "G33", "SD")]:
        s += day(mx + mw, hx, y, mau, luoi, a, b)
    s.append(T(hx + 10, 373, "L/R", 13, INK, weight=500, font=MONO))
    s.append(L(hx, 368, 800, 368, INK, 2) + dat(800, 368) + T(806, 360, "kênh trái", 10.5, GRAY))
    s.append(T(hx + hw - 10, 373, "GND", 13, INK, "end", 500, MONO) + L(hx + hw, 368, hx + hw + 30, 368) + dat(hx + hw + 30, 368))
    s += hop(hx, 430, hw, 190, "Module thẻ microSD", "SPI · thẻ riêng, FAT32")
    s.append(nguon(1010, 430, "V5", "#EA7A12") + T(1018, 424, "VCC", 10, GRAY, font=MONO))
    for y, mau, luoi, a, b in [(490, "trang", "SD_CS", "G5", "CS"), (522, "xanh la", "SPI_MOSI", "G23", "MOSI"),
                               (554, "vang", "SPI_SCK", "G18", "SCK"), (586, "xanh duong", "SPI_MISO", "G19", "MISO")]:
        s += day(mx + mw, hx, y, mau, luoi, a, b)
    s.append(T(hx + hw - 10, 609, "GND", 13, INK, "end", 500, MONO) + L(hx + hw, 604, hx + hw + 30, 604) + dat(hx + hw + 30, 604))
    # LED báo ghi
    y = 640
    s.append(L(mx + mw, y, 740, y, WIRE["tim"], 3) + T(mx + mw + 18, y - 7, "LED", 11, WIRE["tim"], weight=500, font=MONO)
             + T(mx + mw - 10, y + 5, "G2", 13, INK, "end", 500, MONO) + f'<circle cx="{mx+mw}" cy="{y}" r="3.5" fill="{INK}"/>')
    s.append(R(740, y - 9, 56, 18, "#fff", INK, 2, 2) + T(768, y - 16, "R1 330 Ω", 12, INK, "middle", 500))
    s.append(L(796, y, 840, y) + f'<path d="M840,{y-13} L840,{y+13} L866,{y} Z" fill="#fff" stroke="{INK}" stroke-width="2"/>' + L(866, y - 13, 866, y + 13))
    s.append('<path d="M850,622 l8,-10 M858,612 l-5,1 M858,612 l-1,5 M860,626 l8,-10 M868,616 l-5,1 M868,616 l-1,5" stroke="%s" stroke-width="1.6" fill="none"/>' % RED)
    s.append(L(866, y, 910, y) + dat(910, y))
    s.append(T(853, y + 32, "LED đỏ 3 mm báo đang ghi", 11.5, INK, "middle") + T(853, y + 49, "I ≈ (3,3 − 1,9) V / 330 Ω ≈ 4 mA", 10.5, GRAY, "middle"))
    s.append(T(mx + mw / 2, my + mh - 14, "GND", 13, INK, "middle", 500, MONO) + L(mx + mw / 2, my + mh, mx + mw / 2, my + mh + 18) + dat(mx + mw / 2, my + mh + 18))
    s += hop(50, 330, 230, 130, "Sạc dự phòng", "10.000 mAh, cổng USB ra 5 V")
    s.append(T(165, 418, "cáp USB vừa cổng của bo", 12, INK, "middle"))
    s.append(T(165, 440, "bật dòng thấp nếu sạc có chế độ này", 10.5, GRAY, "middle"))
    s.append(R(mx - 18, 380, 36, 44, "#fff", INK, 2, 7) + T(mx + 26, 407, "USB", 12, INK, weight=500, font=MONO))
    s.append(L(280, 400, mx - 18, 400) + L(280, 405, mx - 18, 405))
    s.append(T(346, 390, "cáp USB", 11.5, INK, "middle") + T(346, 425, "VBUS 5 V, GND", 10.5, GRAY, "middle"))
    s += canh_bao(44, 150, 360, 82, ["Khác TC-01: thẻ nhớ cấp từ chân V5", "Trên mạch ESP32 thường chân V5 có 5 V khi cấp",
                                     "qua USB; T5 đạt thẻ nhớ ở cách nối này (11/11)."])
    s += ghi_chu(44, 520, [
        ["INMP441 chỉ cấp 3,3 V. L/R nối GND → kênh trái."],
        ["LED báo ghi bắt buộc (Protocol 7). Nhiều bo có sẵn", "LED xanh ở G2; không có thì lắp R1 + LED ngoài."],
        ["G2 là chân khởi động: LED + 330 Ω xuống GND", "không cản việc nạp firmware."],
        ["Không dùng G0, G12 (khởi động), G6–G11 (flash);", "G34–G39 chỉ đọc vào."],
        ["Firmware ghi_kiem_dinh chỉ ghi trong khung giờ đã", "thông báo, sau khi đồng bộ giờ bằng điện thoại."],
    ])
    return svg_trang(s)

# ============================================================== bảng nối dây (HTML)
def o_mau(m):
    c = WIRE[m]
    vien = f"border:1.5px solid {INK};" if m == "trang" else ""
    nen = "#fff" if m == "trang" else c
    return f'<span class="mau"><i style="background:{nen};{vien}"></i>{TEN_MAU[m]}</span>'

def bang(dong):
    h = ['<table><thead><tr><th>#</th><th>Nhóm</th><th>Từ (chân trên bo)</th><th>Tới</th><th>Tín hiệu</th><th>Dây</th><th>Màu</th><th>Lưu ý</th></tr></thead><tbody>']
    nhom_truoc = None; n = 0
    for nhom, tu, toi, tin, dy, mau, luu, nhan in dong:
        n += 1
        moi = nhom != nhom_truoc
        cls = ' class="dau"' if moi and nhom_truoc else ""
        h.append(f'<tr{cls}><td class="so">{n}</td><td class="nhom">{e(nhom) if moi else ""}</td><td class="m">{e(tu)}</td>'
                 f'<td>{e(toi)}</td><td class="m">{e(tin)}</td><td>{e(dy)}</td><td>{o_mau(mau) if mau else "—"}</td>'
                 f'<td class="{ "luu canh" if nhan else "luu"}">{e(luu)}</td></tr>')
        nhom_truoc = nhom
    h.append("</tbody></table>")
    return "".join(h)

def trang_html(so, tieu, phu, ban_ve, than):
    return f'''<section class="trang">
<div class="vien"></div>
<div class="brand">TussiCount</div><h1>{e(tieu)}</h1><p class="phu">{e(phu)}</p>
<div class="than">{than}</div>
<table class="tb"><tr><td>Đề tài</td><td>TussiCount – đếm tiếng ho tự động tại ký túc xá</td></tr>
<tr><td>Nhóm</td><td>LÒ VI SÓNG · 12T1 · THPT FPT Cần Thơ</td></tr><tr><td>Bản vẽ</td><td><b>{e(ban_ve)}</b></td></tr>
<tr><td>Phiên bản</td><td>2.0 · {NGAY} · trang {so}/4</td></tr></table></section>'''

def hang_j1():
    j1 = ["3V3", "3V3", "RST", "4", "5", "6", "7", "15", "16", "17", "18", "8", "3", "46", "9", "10", "11", "12", "13", "14", "5Vin", "GND"]
    dung = {"3V3#0": "nguồn", "4": "SCK", "5": "WS", "6": "SD", "15": "CS", "16": "MOSI", "17": "SCK", "18": "MISO", "GND": "GND"}
    out = []
    for i, p in enumerate(j1):
        k = f"{p}#0" if p == "3V3" and i == 0 else p
        if p == "5Vin": cls, nh = "x", "không dùng"
        elif p in ("10", "11", "12", "13"): cls, nh = "bo", "bỏ 12/11"
        elif k in dung: cls, nh = "on", dung[k]
        else: cls, nh = "", ""
        out.append(f'<div class="pin {cls}"><b>{e(p)}</b><span>{e(nh)}</span></div>')
    return "".join(out)

def trang_bang_tc01():
    d = [("Micro", "3V3", "INMP441 · VDD", "nguồn 3,3 V", "cái–cái 10 cm", "do", "Không cấp 5 V cho micro", False),
         ("Micro", "GND", "INMP441 · GND", "đất", "cái–cái 10 cm", "den", "", False),
         ("Micro", "GND", "INMP441 · L/R", "chọn kênh", "cái–cái 10 cm", "den", "Nối GND → micro xuất kênh trái", False),
         ("Micro", "GPIO4", "INMP441 · SCK", "I2S_SCK", "cái–cái 10 cm", "vang", "Dây micro dưới 10 cm, bó gọn", False),
         ("Micro", "GPIO5", "INMP441 · WS", "I2S_WS", "cái–cái 10 cm", "xanh la", "", False),
         ("Micro", "GPIO6", "INMP441 · SD", "I2S_SD", "cái–cái 10 cm", "xanh duong", "", False),
         ("Thẻ nhớ", "3V3", "Module thẻ · VCC", "nguồn 3,3 V", "cái–cái 20 cm", "do", "KHÔNG dùng 5Vin (không ra 5 V)", True),
         ("Thẻ nhớ", "GND", "Module thẻ · GND", "đất", "cái–cái 20 cm", "den", "", False),
         ("Thẻ nhớ", "GPIO15", "Module thẻ · CS", "SD_CS", "cái–cái 20 cm", "trang", "Trước 12/11 là GPIO10", False),
         ("Thẻ nhớ", "GPIO16", "Module thẻ · MOSI", "SPI_MOSI", "cái–cái 20 cm", "xanh la", "Trước 12/11 là GPIO11", False),
         ("Thẻ nhớ", "GPIO17", "Module thẻ · SCK", "SPI_SCK", "cái–cái 20 cm", "vang", "Trước 12/11 là GPIO12", False),
         ("Thẻ nhớ", "GPIO18", "Module thẻ · MISO", "SPI_MISO", "cái–cái 20 cm", "xanh duong", "Trước 12/11 là GPIO13", False),
         ("Nguồn", "cổng USB-C", "sạc PB100P · USB-C", "5 V", "cáp USB-C ↔ USB-C", None, "Bấm nút sạc 2 lần: chế độ dòng thấp", False)]
    than = f'''{bang(d)}
<div class="duoi"><div class="trai"><h3>VỊ TRÍ CHÂN TRÊN HÀNG J1 (bo ESP32-S3-DevKitC-1 v1.1)</h3>
<div class="hang">{hang_j1()}</div>
<p class="nho"><span class="k on"></span>dùng tới <span class="k x"></span>không dùng <span class="k bo"></span>đã bỏ từ 12/11 · bản sao có thể khác thứ tự: luôn đọc nhãn in trên bo. Các dây GND còn lại cắm vào chân GND ở hàng J3 bên kia.</p>
<h3 style="margin-top:6mm">THAY ĐỔI SO VỚI BẢN 1.0 (09/11)</h3>
<table class="ss"><tr><th>Mục</th><th>Bản 1.0</th><th>Bản 2.0</th><th>Lý do</th></tr>
<tr><td>Chân thẻ CS · MOSI · SCK · MISO</td><td class="m">10 · 11 · 12 · 13</td><td class="m">15 · 16 · 17 · 18</td><td>Mạch S3 thay thế không nhận thẻ ở 10–13 (12/11)</td></tr>
<tr><td>Nguồn module thẻ</td><td class="m">5V</td><td class="m">3V3</td><td>5Vin không ra 5 V khi cấp qua USB; 3V3 đạt T5</td></tr>
<tr><td>LED báo ghi</td><td class="m">GPIO7</td><td>không lắp</td><td>TC-01 không ghi âm (Protocol 16.17)</td></tr>
<tr><td>Bộ thứ hai</td><td>giống TC-01</td><td>ESP32 thường</td><td>Mạch S3 thứ nhất hỏng flash (11/11), xem trang 3–4</td></tr></table></div>
<div class="phai"><h3>KIỂM TRA TRƯỚC KHI CẤP ĐIỆN</h3><ul class="ck">
<li>VCC module thẻ ở <b>3V3</b>, không ở 5Vin</li><li>L/R của micro nối GND</li><li>Dây micro ngắn dưới 10 cm</li>
<li>Thẻ FAT32 đã cắm, có <span class="m">cauhinh.txt</span> nếu dùng Wi-Fi</li><li>T5 báo ĐẠT bo mạch, micro, thẻ nhớ</li><li>Sạc dự phòng ở chế độ dòng thấp</li></ul></div></div>'''
    return trang_html(2, "BẢNG NỐI DÂY – TC-01 (ESP32-S3)", "Chân trên bo, micro và module thẻ đều là chân đực: dùng dây Dupont cái–cái. Màu dây giống sơ đồ trang 1 để dò lại dễ.", "Bảng nối dây TC-01", than)

def trang_bang_tc02():
    d = [("Micro", "3V3", "INMP441 · VDD", "nguồn 3,3 V", "cái–cái 10 cm", "do", "Không cấp 5 V cho micro", False),
         ("Micro", "GND", "INMP441 · GND", "đất", "cái–cái 10 cm", "den", "", False),
         ("Micro", "GND", "INMP441 · L/R", "chọn kênh", "cái–cái 10 cm", "den", "Nối GND → kênh trái", False),
         ("Micro", "G26", "INMP441 · SCK", "I2S_SCK", "cái–cái 10 cm", "vang", "", False),
         ("Micro", "G25", "INMP441 · WS", "I2S_WS", "cái–cái 10 cm", "xanh la", "", False),
         ("Micro", "G33", "INMP441 · SD", "I2S_SD", "cái–cái 10 cm", "xanh duong", "", False),
         ("Thẻ nhớ", "V5", "Module thẻ · VCC", "nguồn 5 V", "cái–cái 20 cm", "cam", "Khác TC-01: ở mạch này dùng V5", True),
         ("Thẻ nhớ", "GND", "Module thẻ · GND", "đất", "cái–cái 20 cm", "den", "", False),
         ("Thẻ nhớ", "G5", "Module thẻ · CS", "SD_CS", "cái–cái 20 cm", "trang", "", False),
         ("Thẻ nhớ", "G23", "Module thẻ · MOSI", "SPI_MOSI", "cái–cái 20 cm", "xanh la", "", False),
         ("Thẻ nhớ", "G18", "Module thẻ · SCK", "SPI_SCK", "cái–cái 20 cm", "vang", "", False),
         ("Thẻ nhớ", "G19", "Module thẻ · MISO", "SPI_MISO", "cái–cái 20 cm", "xanh duong", "", False),
         ("LED", "G2", "R1 330 Ω → chân dài (+) LED", "LED", "cái–cái 20 cm", "tim", "R1 hàn sẵn vào LED, bọc co nhiệt", False),
         ("LED", "GND", "chân ngắn (−) LED", "đất", "cái–cái 20 cm", "den", "", False),
         ("Nguồn", "cổng USB", "sạc dự phòng", "5 V", "cáp USB vừa cổng bo", None, "", False)]
    nhan = ["3V3", "V5", "GND", "G26", "G25", "G33", "G5", "G23", "G18", "G19", "G2"]
    chips = "".join(f'<div class="pin on"><b>{p}</b></div>' for p in nhan)
    ss = [("Mạch · board Arduino", "ESP32-S3 · ESP32S3 Dev Module", "ESP32 thường · ESP32 Dev Module"),
          ("Micro SCK · WS · SD", "4 · 5 · 6", "G26 · G25 · G33"), ("Thẻ CS · MOSI · SCK · MISO", "15 · 16 · 17 · 18", "G5 · G23 · G18 · G19"),
          ("VCC module thẻ", "3V3", "V5"), ("LED", "không lắp", "G2, sáng khi ghi"), ("Firmware", "TC01_Van_hanh", "TC02_Ghi_kiem_dinh"),
          ("Nhiệm vụ · vị trí", "đếm, không ghi âm · tầng 1", "ghi âm kiểm định · tầng 2")]
    so = "".join(f"<tr><td>{e(a)}</td><td class='m'>{e(b)}</td><td class='m'>{e(c)}</td></tr>" for a, b, c in ss)
    than = f'''{bang(d)}
<div class="duoi"><div class="trai"><h3>NHÃN CHÂN CẦN TÌM TRÊN BO (thứ tự tuỳ bản bo, đọc nhãn in)</h3>
<div class="hang">{chips}</div>
<h3 style="margin-top:9px">HAI BỘ KHÁC NHAU Ở ĐÂU</h3>
<table class="ss"><tr><th></th><th>TC-01</th><th>TC-02</th></tr>{so}</table></div>
<div class="phai"><h3>KIỂM TRA TRƯỚC KHI CẤP ĐIỆN</h3><ul class="ck">
<li>VCC module thẻ ở <b>V5</b></li><li>L/R của micro nối GND</li><li>LED: chân dài (+) về phía R1</li>
<li>Thẻ riêng của TC-02, FAT32</li><li>Serial báo “Lich ghi … (4 khung)”</li><li>Đã đồng bộ giờ: LED thôi nháy</li></ul></div></div>'''
    return trang_html(4, "BẢNG NỐI DÂY – TC-02 (ESP32 THƯỜNG)", "Cùng loại micro, module thẻ và màu dây như TC-01; khác ở số chân, nguồn module thẻ (V5) và LED báo ghi.", "Bảng nối dây TC-02", than)

CSS = f'''
@page {{ size: A4 landscape; margin: 0 }}
* {{ box-sizing: border-box }} body {{ margin: 0; font-family: {SANS}; color: {INK} }}
.trang {{ width: 297mm; height: 210mm; position: relative; page-break-after: always; overflow: hidden; background: #fff }}
.trang svg {{ display: block }}
.vien {{ position: absolute; left: 5mm; top: 5mm; right: 5mm; bottom: 5mm; border: 0.5mm solid {INK} }}
.brand {{ position: absolute; left: 11mm; top: 9.6mm; color: {TEAL}; font-weight: 600; font-size: 12pt }}
h1 {{ position: absolute; left: 11mm; top: 14.3mm; margin: 0; font-size: 21pt; font-weight: 600 }}
.phu {{ position: absolute; left: 11mm; top: 25.5mm; margin: 0; color: {GRAY}; font-size: 9.8pt }}
.than {{ position: absolute; left: 11mm; right: 11mm; top: 34mm }}
table {{ border-collapse: collapse; width: 100% }}
.than > table th {{ background: {PALE}; color: {TEAL}; font-weight: 600; text-align: left; font-size: 8.6pt; padding: 1.3mm 2mm }}
.than > table td {{ font-size: 8.4pt; padding: .72mm 2mm; border-bottom: 0.2mm solid {LINE}; vertical-align: middle }}
.than > table tr.dau td {{ border-top: 0.35mm solid {INK} }}
td.so {{ color: {GRAY}; width: 6mm }} td.nhom {{ font-weight: 600; width: 17mm }}
.m {{ font-family: {MONO}; font-size: 8.1pt }}
.mau {{ display: inline-flex; align-items: center; gap: 1.6mm }} .mau i {{ width: 3.2mm; height: 3.2mm; border-radius: 50%; display: inline-block }}
td.luu {{ color: {GRAY} }} td.canh {{ color: {RED}; font-weight: 600 }}
.duoi {{ display: flex; gap: 8mm; margin-top: 3.5mm }} .trai {{ flex: 1 }} .phai {{ width: 100mm }}
h3 {{ color: {TEAL}; font-size: 8.8pt; font-weight: 600; margin: 0 0 2mm }}
.hang {{ display: flex; flex-wrap: wrap; gap: .7mm }}
.pin {{ width: 6.9mm; height: 10.5mm; border: 0.25mm solid {LINE}; border-radius: 1.6mm; display: flex; flex-direction: column; align-items: center; justify-content: center }}
.pin b {{ font-family: {MONO}; font-size: 7pt; font-weight: 500 }} .pin span {{ font-size: 4.6pt; line-height: 1.05; text-align: center; margin-top: .4mm }}
.pin.on {{ background: {TEAL}; border-color: {TEAL}; color: #fff }} .pin.x {{ background: #FEF3F2; border-color: {RED}; color: {RED} }}
.pin.bo {{ background: repeating-linear-gradient(45deg,#fff 0 1.2mm,#EEF0EF 1.2mm 2.4mm); color: {GRAY} }}
.nho {{ font-size: 7.4pt; color: {GRAY}; margin: 2mm 0 0 }} .k {{ display: inline-block; width: 2.6mm; height: 2.6mm; border-radius: .6mm; margin: 0 1mm -.3mm 2mm; border: .25mm solid {LINE} }}
.k.on {{ background: {TEAL} }} .k.x {{ background: #FEF3F2; border-color: {RED} }} .k.bo {{ background: #EEF0EF }}
.ck {{ list-style: none; margin: 0; padding: 0; font-size: 8.4pt }} .ck li {{ padding: 1.1mm 0 1.1mm 6mm; position: relative; border-bottom: .2mm solid {LINE} }}
.ck li:before {{ content: ""; position: absolute; left: 0; top: 1.5mm; width: 3.2mm; height: 3.2mm; border: .3mm solid {INK}; border-radius: .6mm }}
table.ss {{ width: 100% }} table.ss th {{ font-size: 7.8pt; color: {TEAL}; text-align: left; padding: .8mm 1.5mm; border-bottom: .3mm solid {INK} }}
table.ss td {{ font-size: 7.8pt; padding: .7mm 1.5mm; border-bottom: .2mm solid {LINE} }} table.ss .m {{ font-size: 7.4pt }}
.tb {{ position: absolute; right: 5mm; bottom: 5mm; width: 102mm; background: #fff; border: .5mm solid {INK} }}
.tb td {{ font-size: 8.2pt; padding: 1.15mm 2.4mm; border-bottom: .2mm solid {LINE} }} .tb td:first-child {{ color: {GRAY}; width: 19mm; white-space: nowrap; border-right: .2mm solid {LINE} }}
.tb tr:last-child td {{ border-bottom: 0 }} .tb b {{ font-weight: 500 }}
'''

def main():
    s1, s3 = so_do_tc01(), so_do_tc02()
    (OUT / "TussiCount_TC-01_so_do.svg").write_text(s1, encoding="utf-8")
    (OUT / "TussiCount_TC-02_so_do.svg").write_text(s3, encoding="utf-8")
    trang = [f'<section class="trang">{s1}</section>', trang_bang_tc01(), f'<section class="trang">{s3}</section>', trang_bang_tc02()]
    doc = f'<!doctype html><html lang="vi"><meta charset="utf-8"><title>TussiCount – Sơ đồ mạch 2.0</title><style>{CSS}</style><body>{"".join(trang)}</body></html>'
    (OUT / "so_do.html").write_text(doc, encoding="utf-8")

main()
