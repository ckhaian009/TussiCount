# Sơ đồ nguyên lý và bảng kết nối dạng chuẩn cho báo cáo khoa học (đơn sắc, có chú thích hình/bảng).
import html, pathlib
OUT = pathlib.Path(__file__).parent
SERIF = "'LMRoman','Latin Modern Roman',serif"
import base64
LM = '/usr/share/texmf/fonts/opentype/public/lm/'
def _ff(f, w, st):
    d = base64.b64encode(open(LM + f, 'rb').read()).decode()
    return f"@font-face{{font-family:'LMRoman';src:url(data:font/otf;base64,{d}) format('opentype');font-weight:{w};font-style:{st}}}"
FONT_CSS = _ff('lmroman10-regular.otf', 400, 'normal') + _ff('lmroman10-bold.otf', 700, 'normal') + _ff('lmroman10-italic.otf', 400, 'italic')
K = "#000"
e = html.escape

def T(x, y, s, size=13, anchor="start", weight=400, italic=False):
    st = ' font-style="italic"' if italic else ""
    return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" font-family="{SERIF}" fill="{K}"{st}>{e(s)}</text>'
def L(x1, y1, x2, y2, w=1.4):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{K}" stroke-width="{w}"/>'
def R(x, y, w, h, sw=1.6):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fff" stroke="{K}" stroke-width="{sw}"/>'
def dot(x, y): return f'<circle cx="{x}" cy="{y}" r="3" fill="{K}"/>'
def gnd(x, y):
    return L(x, y, x, y + 10) + L(x - 12, y + 10, x + 12, y + 10) + L(x - 8, y + 15, x + 8, y + 15) + L(x - 4, y + 20, x + 4, y + 20)
def vcc(x, y, ten):  # ký hiệu nguồn dạng thanh ngang, chân tại (x,y)
    return L(x, y, x, y - 22) + L(x - 12, y - 22, x + 12, y - 22, 1.8) + T(x, y - 28, ten, 12.5, "middle")

def khoi(x, y, w, h, ten, phu):
    return R(x, y, w, h) + T(x + w / 2, y + 22, ten, 14, "middle", 700) + T(x + w / 2, y + 39, phu, 11.5, "middle", italic=True)

def noi(x1, x2, y, luoi, a, b):
    return (L(x1, y, x2, y) + T((x1 + x2) / 2, y - 5, luoi, 11, "middle") + T(x1 - 6, y + 4.5, a, 12, "end") + T(x2 + 6, y + 4.5, b, 12))

def hinh(cfg):
    s = []
    mx, my, mw, mh = 300, 70, 190, 470
    s.append(khoi(mx, my, mw, mh, cfg["mcu"], cfg["mcu_phu"]))
    # nguồn trên MCU
    s.append(vcc(mx + 55, my, "+3,3 V") + T(mx + 55, my + 58, "3V3", 12, "middle"))
    if cfg["v5"]:
        s.append(vcc(mx + 135, my, "+5 V") + T(mx + 135, my + 58, cfg["v5"], 12, "middle"))
    # micro
    hx, hw = 640, 180
    s.append(khoi(hx, 80, hw, 170, "U2  INMP441", "micro MEMS, I2S"))
    s.append(vcc(hx + 150, 80, "+3,3 V") + T(hx + 156, 72, "VDD", 11))
    for y, luoi, a, b in [(150, "I2S_SCK", cfg["mic"][0], "SCK"), (180, "I2S_WS", cfg["mic"][1], "WS"), (210, "I2S_SD", cfg["mic"][2], "SD")]:
        s.append(noi(mx + mw, hx, y, luoi, a, b))
    s.append(T(hx + 6, 239.5, "L/R", 12) + L(hx, 235, hx - 40, 235) + gnd(hx - 40, 235))
    s.append(T(hx + hw - 6, 239.5, "GND", 12, "end") + L(hx + hw, 235, hx + hw + 30, 235) + gnd(hx + hw + 30, 235))
    # thẻ nhớ
    ty = 300
    s.append(khoi(hx, ty, hw, 190, "U3  Module microSD", "giao tiếp SPI"))
    s.append(vcc(hx + 150, ty, cfg["the_vcc"]) + T(hx + 156, ty - 8, "VCC", 11))
    for i, (luoi, b) in enumerate([("SD_CS", "CS"), ("SPI_MOSI", "MOSI"), ("SPI_SCK", "SCK"), ("SPI_MISO", "MISO")]):
        y = ty + 70 + 30 * i
        s.append(noi(mx + mw, hx, y, luoi, cfg["sd"][i], b))
    s.append(T(hx + hw - 6, ty + 179.5, "GND", 12, "end") + L(hx + hw, ty + 175, hx + hw + 30, ty + 175) + gnd(hx + hw + 30, ty + 175))
    # GND MCU
    s.append(T(mx + mw / 2, my + mh - 8, "GND", 12, "middle") + L(mx + mw / 2, my + mh, mx + mw / 2, my + mh + 14) + gnd(mx + mw / 2, my + mh + 14))
    # nguồn 5 V
    bx, by = 40, 230
    s.append(R(bx, by, 150, 80) + T(bx + 75, by + 30, "BT1", 14, "middle", 700) + T(bx + 75, by + 50, "nguồn 5 V", 12, "middle")
             + T(bx + 75, by + 66, "(sạc dự phòng)", 11.5, "middle", italic=True))
    s.append(L(bx + 150, by + 30, mx, by + 30) + T(mx + 6, by + 34.5, "VBUS", 12) + T((bx + 150 + mx) / 2, by + 25, "USB", 11, "middle"))
    s.append(L(bx + 150, by + 55, 250, by + 55) + gnd(250, by + 55))
    # LED (TC-02)
    if cfg["led"]:
        y = 515
        s.append(T(mx + mw - 6, y + 4.5, cfg["led"], 12, "end") + L(mx + mw, y, 560, y) + T(530, y - 5, "LED_REC", 11, "middle"))
        s.append(f'<path d="M560,{y} l6,-7 l12,14 l12,-14 l12,14 l12,-14 l12,14 l6,-7" fill="none" stroke="{K}" stroke-width="1.4"/>')
        s.append(T(596, y - 14, "R1  330 Ω", 11.5, "middle"))
        s.append(L(632, y, 660, y) + f'<path d="M660,{y-10} L660,{y+10} L680,{y} Z" fill="#fff" stroke="{K}" stroke-width="1.4"/>' + L(680, y - 10, 680, y + 10, 1.6))
        s.append(f'<path d="M668,{y-14} l7,-9 m0,0 l-5,1 m5,-1 l-1,5 M676,{y-12} l7,-9 m0,0 l-5,1 m5,-1 l-1,5" fill="none" stroke="{K}" stroke-width="1.1"/>')
        s.append(T(670, y + 28, "D1  LED", 11.5, "middle"))
        s.append(L(680, y, 710, y) + gnd(710, y))
    w, h = 900, 590
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'<style>{FONT_CSS}</style><rect width="{w}" height="{h}" fill="#fff"/>{"".join(s)}</svg>')

TC01 = dict(mcu="U1  ESP32-S3-DevKitC-1", mcu_phu="ESP32-S3 N16R8", v5=None, mic=("GPIO4", "GPIO5", "GPIO6"),
            sd=("GPIO15", "GPIO16", "GPIO17", "GPIO18"), the_vcc="+3,3 V", led=None)
TC02 = dict(mcu="U1  ESP32 DevKit", mcu_phu="ESP-WROOM-32", v5="V5", mic=("GPIO26", "GPIO25", "GPIO33"),
            sd=("GPIO5", "GPIO23", "GPIO18", "GPIO19"), the_vcc="+5 V", led="GPIO2")

BANG = [
    ("U2 – Micro INMP441", [("VDD", "Nguồn 3,3 V", "3V3", "3V3"), ("GND", "Đất", "GND", "GND"), ("L/R", "Chọn kênh trái", "GND", "GND"),
                           ("SCK", "Xung nhịp bit I2S", "GPIO4", "GPIO26"), ("WS", "Chọn kênh I2S", "GPIO5", "GPIO25"),
                           ("SD", "Dữ liệu I2S", "GPIO6", "GPIO33")]),
    ("U3 – Module microSD", [("VCC", "Nguồn", "3V3", "V5"), ("GND", "Đất", "GND", "GND"), ("CS", "Chọn chip SPI", "GPIO15", "GPIO5"),
                            ("MOSI", "Dữ liệu SPI vào thẻ", "GPIO16", "GPIO23"), ("SCK", "Xung nhịp SPI", "GPIO17", "GPIO18"),
                            ("MISO", "Dữ liệu SPI ra từ thẻ", "GPIO18", "GPIO19")]),
    ("D1 – LED (nối tiếp R1 330 Ω)", [("Anode", "Báo đang ghi âm", "—", "GPIO2"), ("Cathode", "Đất", "—", "GND")]),
    ("BT1 – Nguồn 5 V", [("USB", "Cấp nguồn cho bo", "USB-C", "USB")]),
]

def bang_html():
    h = ['<table class="bk"><thead><tr><th rowspan="2" style="width:28%">Linh kiện</th><th rowspan="2" style="width:15%">Chân</th><th rowspan="2" style="width:29%">Chức năng</th>'
         '<th colspan="2" class="nhom">Chân nối trên bo</th></tr><tr><th style="width:14%">TC-01<br><span>ESP32-S3</span></th><th>TC-02<br><span>ESP32</span></th></tr></thead><tbody>']
    for lk, dong in BANG:
        for i, (c, cn, a, b) in enumerate(dong):
            cls = ' class="dau"' if i == 0 and lk != BANG[0][0] else ""
            o = f'<td rowspan="{len(dong)}" class="lk">{e(lk)}</td>' if i == 0 else ""
            h.append(f'<tr{cls}>{o}<td>{e(c)}</td><td>{e(cn)}</td><td class="c">{e(a)}</td><td class="c">{e(b)}</td></tr>')
    h.append("</tbody></table>")
    return "".join(h)

CSS = FONT_CSS + f'''@page {{ size: A4; margin: 25mm 20mm 25mm 30mm }}
body {{ font-family: {SERIF}; color: #000; font-size: 13pt; margin: 0 }}
figure {{ margin: 0 0 10mm; text-align: center; page-break-inside: avoid }} figure svg {{ width: 100%; height: auto }}
figcaption {{ font-size: 12pt; margin-top: 2mm }} figcaption b, .cap b {{ font-weight: 700 }}
.cap {{ font-size: 12pt; text-align: center; margin: 0 0 2.5mm }}
table.bk {{ border-collapse: collapse; width: 100%; font-size: 11pt; border-top: 1.5pt solid #000; border-bottom: 1.5pt solid #000 }}
.bk th {{ font-weight: 700; padding: 1.6mm 1.6mm; text-align: left; vertical-align: bottom }} .bk th span {{ font-weight: 400; font-style: italic; font-size: 10.5pt }}
.bk thead tr:last-child th, .bk thead th[rowspan] {{ border-bottom: .8pt solid #000 }} .bk th.nhom {{ text-align: center; border-bottom: .5pt solid #000 }}
.bk td {{ padding: 1.1mm 1.6mm; vertical-align: top }} .bk td.c, .bk thead tr:last-child th {{ text-align: center }}
.bk tr.dau td {{ border-top: .5pt solid #000 }} .bk td.lk {{ font-weight: 400 }}
.tb {{ page-break-inside: avoid; margin-bottom: 10mm }}
.trang {{ page-break-after: always }}
'''

def main():
    h1, h2 = hinh(TC01), hinh(TC02)
    (OUT / "Hinh_1_So_do_TC-01.svg").write_text(h1, encoding="utf-8")
    (OUT / "Hinh_2_So_do_TC-02.svg").write_text(h2, encoding="utf-8")
    cap1 = "<b>Hình 1.</b> Sơ đồ nguyên lý thiết bị đếm TC-01 (ESP32-S3)"
    cap2 = "<b>Hình 2.</b> Sơ đồ nguyên lý thiết bị ghi âm kiểm định TC-02 (ESP32)"
    capb = "<b>Bảng 1.</b> Kết nối giữa linh kiện và bo vi điều khiển của hai thiết bị"
    doc = (f'<!doctype html><html lang="vi"><meta charset="utf-8"><title>TussiCount – sơ đồ và bảng kết nối</title><style>{CSS}</style><body>'
           f'<div class="trang"><figure id="h1">{h1}<figcaption>{cap1}</figcaption></figure>'
           f'<figure id="h2">{h2}<figcaption>{cap2}</figcaption></figure></div>'
           f'<div class="tb" id="b1"><p class="cap">{capb}</p>{bang_html()}</div></body></html>')
    (OUT / "formal.html").write_text(doc, encoding="utf-8")

main()
