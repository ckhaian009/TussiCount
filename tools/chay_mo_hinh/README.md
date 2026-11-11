# Chạy mô hình trên máy tính, gộp sự kiện và chọn ngưỡng (Protocol mục 6, 8; việc t19)

| Tệp | Việc |
| --- | --- |
| `chay_mo_hinh.cpp`, `bien_dich.mk` | Bộ chạy dùng đúng thư viện C++ xuất từ Edge Impulse (cùng MFE và mạng int8 với firmware). Chế độ `dai`: trượt cửa sổ 1 s, bước 0,5 s trên tệp WAV dài, ghi điểm từng cửa sổ. Chế độ `ngan`: chấm từng tệp 1 s |
| `gop_su_kien.py` | Gộp điểm cửa sổ thành sự kiện theo ngưỡng θ, số cửa sổ tối thiểu k, khoảng nghỉ g. Định nghĩa chính xác nằm ở đầu tệp; firmware phải làm giống hệt |
| `thu_gop_su_kien.py`, `vector_thu_gop_su_kien.json` | 12 tình huống có đáp án tính tay; tệp JSON dùng để thử đồng nhất với firmware |
| `tao_luong_kiem_tra.py` | Ghép tập kiểm tra của dữ liệu mở thành luồng liên tục (ô 8 s: 1 đoạn ho + 7 đoạn không ho) để đo độ nhạy theo sự kiện |
| `chon_nguong.py` | Lưới θ × k × g; độ nhạy trên luồng, phát hiện sai mỗi giờ trên phần để sửa; chọn theo mục 8; lưu cả đường cong |
| `so_sanh_mo_hinh.py` | So v1 (Impulse #2) với v2 (Impulse #3, tăng cường) theo quy tắc ghi trước 10/11 19:20: mỗi mô hình ở tổ hợp của chính nó, chọn mô hình có độ nhạy cao hơn trên luồng tăng cường; báo cáo đủ các tập |

Công cụ nghe xác minh phần để sửa: `tools/gan_nhan/ung_vien_phan_de_sua.py`.

## Biên dịch

Thư viện Edge Impulse không đưa lên GitHub (giấy phép). Tải bản “C++ library” ở Deployment (int8, EON) và giải nén vào
`data/ei_lib/<ten>`. Bản của mô hình nền v1 (Impulse #2, deployment version 1) có SHA-256
`164af6a8c3871285ea2a33fb7ea2c96b7720c88176e341a0b09492832edf8904`. Bản của mô hình tăng cường v2 (Impulse #3, deployment version 2):
`d2dbd1855800d4037f6b96e33d439862b9eff04854ce98eb1f6e8849d7e5c802`, giải nén vào `data/ei_lib/v2`.

```
cd tools/chay_mo_hinh
make -f bien_dich.mk EI_LIB=../../data/ei_lib/v1                         # Linux (g++)
make -f bien_dich.mk EI_LIB=../../data/ei_lib/v1 CXX=clang++ CC=clang   # macOS
```

## Quy trình ngày 12/11 (sáng, trước đóng băng)

```
B=tools/chay_mo_hinh/build/v1/chay_mo_hinh
python3 tools/chay_mo_hinh/tao_luong_kiem_tra.py --bo sach        # và --bo tang_cuong khi có dữ liệu tăng cường
$B dai data/luong_kiem_tra/sach.wav ~/TussiCount_KTX/diem_luong_sach_v1.csv
$B dai ~/TussiCount_KTX/phan_de_sua.wav ~/TussiCount_KTX/diem_sua_v1.csv
python3 tools/gan_nhan/ung_vien_phan_de_sua.py ~/TussiCount_KTX/phan_de_sua.wav ~/TussiCount_KTX/diem_sua_v1.csv ~/TussiCount_KTX/ung_vien_v1
#   -> nghe các đoạn 3 s, điền cột co_ho trong phieu_nghe.csv
python3 tools/chay_mo_hinh/chon_nguong.py --ten v1 --luong-diem ~/TussiCount_KTX/diem_luong_sach_v1.csv \
    --luong-chuan results/luong_kiem_tra_sach.csv --sua-diem ~/TussiCount_KTX/diem_sua_v1.csv \
    --sua-nhan ~/TussiCount_KTX/ung_vien_v1/phieu_nghe.csv --ra results/chon_nguong_v1.json
```

Làm y hệt cho v2 (thư viện của Impulse #3 trong `data/ei_lib/v2`, biên dịch với `EI_LIB=../../data/ei_lib/v2`): điểm luồng
sạch, luồng tăng cường, phần để sửa; nghe thêm các ứng viên của v2 chưa có trong phiếu của v1; `chon_nguong.py --ten v2`.
Rồi so hai mô hình:

```
python3 tools/chay_mo_hinh/so_sanh_mo_hinh.py --chon results/chon_nguong_v1.json results/chon_nguong_v2.json \
    --luong-tc data/luong_kiem_tra/diem_tang_cuong_v1.csv data/luong_kiem_tra/diem_tang_cuong_v2.csv \
    --luong-tc-chuan results/luong_kiem_tra_tang_cuong.csv \
    --ngan data/so_sanh/diem_doan_v1.csv data/so_sanh/diem_doan_v2.csv --bang-ben results/ei_kiem_tra_ben.csv \
    --ra results/chon_mo_hinh_16_7.json
```

Điểm của luồng sạch và luồng tăng cường lấy từ dữ liệu mở nên để trong `data/luong_kiem_tra/` được; chỉ điểm và đoạn cắt
của phần để sửa phải ở `~/TussiCount_KTX`. `so_sanh_mo_hinh.py --thu`: 7 tình huống quy tắc + trọn quy trình, đạt (10/11).

Âm thanh KTX và các đoạn cắt từ đó chỉ nằm ở `~/TussiCount_KTX` (ngoài iCloud, ngoài kho). Tệp điểm và JSON không chứa
âm thanh.

## Phép thử đã chạy (10/11/2026)

- Biên dịch với thư viện v1 trên Linux x86-64: không lỗi; 0,55 ms mỗi cửa sổ (lớn nhất 3,7 ms).
- `thu_gop_su_kien.py`: 12/12 tình huống đạt.
- Chạy thử trọn quy trình (luồng → điểm → ứng viên → chọn ngưỡng) trên luồng thay thế 120 tiếng ho Coswara + nhiễu tổng
  hợp, với mô hình v1 thật: chạy đúng, kết quả đúng định dạng.
- Đối chiếu điểm của bộ chạy với điểm Edge Impulse đã lưu (`results/mo_hinh_nen_v1_diem_tung_mau.csv`) trên 3.465
  đoạn kiểm tra thật (10/11, g++ trên Linux arm64): 96,9% lệch ≤ 1 bậc int8 (0,004), lớn nhất 0,039; 3 đoạn sát 0,5 đổi
  phía. Chi tiết: `results/mo_hinh_nen_nhat_ky_thi_nghiem.md`.
- Hai luồng kiểm tra (sạch, tăng cường) đã tạo: 1.595 tiếng ho mỗi luồng, 3,54 giờ; bộ chạy xử lý mỗi luồng trong 9 s.

## Phát hiện khi chạy thử (thăm dò, không phải kết quả theo protocol)

Trên luồng thay thế (tiếng ho Coswara chuẩn hoá mức ngẫu nhiên, ngưỡng 0,5), thêm nhiễu trắng liên tục rất nhỏ làm độ
nhạy của mô hình v1 tụt mạnh: 58% khi gần như im lặng; 20% với nền −70 dBFS; 9% với −60 dBFS; 2% với −50 dBFS.
Cùng hướng với tập độ bền, nhưng nặng hơn nhiều. Nếu đúng như vậy trên thiết bị, mô hình v1 gần như không đếm được tiếng ho
ở hành lang. Mô hình có tăng cường (16.7) vì vậy phải xong trước khi đóng băng.
