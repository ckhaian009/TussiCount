#!/bin/bash
# Tải phần huấn luyện của dữ liệu tăng cường (data/ei_tang_cuong/training, 12.724 đoạn: 6.362 cough + 6.362 noise,
# chỉ từ dữ liệu mở, không có âm thanh KTX) lên Edge Impulse bằng công cụ tải chung (Protocol 16.7).
# Phần kiểm tra tăng cường không tải lên: chỉ dùng trên máy tính để dựng luồng kiểm tra tăng cường.
# Nhấp đúp trong Finder, dán API key vào hộp thoại.
export EI_DATA="data/ei_tang_cuong"
export EI_TAP="training"
exec bash "$(cd "$(dirname "$0")/../chuan_hoa_am_thanh" && pwd)/tai_len_edge_impulse.command"
