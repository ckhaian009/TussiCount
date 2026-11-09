#!/bin/bash
# Tải tập kiểm tra độ bền (data/ei_kiem_tra_ben, 1.500 đoạn ho trộn nền ồn, nhãn cough, tập testing)
# lên Edge Impulse bằng công cụ tải chung. Nhấp đúp trong Finder, dán API key vào hộp thoại.
export EI_DATA="data/ei_kiem_tra_ben"
exec bash "$(cd "$(dirname "$0")/../chuan_hoa_am_thanh" && pwd)/tai_len_edge_impulse.command"
