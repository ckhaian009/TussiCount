#!/bin/bash
# Tải dữ liệu mô hình nền TussiCount lên Edge Impulse (dự án 1156522) qua Ingestion API.
#
# Dữ liệu: data/ei_upload/<training|testing>/<cough|noise>/*.wav, do chuan_bi_du_lieu_ei.py tạo
# từ dữ liệu mở (COUGHVID, ESC-50, Common Voice). Không có âm thanh ghi tại KTX (Protocol mục 8).
# Tập huấn luyện/kiểm tra giữ nguyên như đã chia theo nhóm; nhãn lấy từ tên thư mục.
#
# API key: hỏi qua hộp thoại mỗi lần chạy, chỉ nằm trong bộ nhớ của lần chạy đó.
# Không ghi ra đĩa, không đưa lên dòng lệnh (truyền cho curl qua stdin), không ghi vào nhật ký.
#
# Chạy lại an toàn: bỏ qua các lô đã tải xong; máy chủ từ chối tệp trùng nội dung
# (x-disallow-duplicates), nên không sinh mẫu trùng.
# Cách chạy: nhấp đúp tệp này trong Finder (macOS mở bằng Terminal).
# Thư mục dữ liệu khác: đặt biến EI_DATA (xem tools/mo_hinh_nen/tai_len_kiem_tra_ben.command).
# Chỉ tải một phần: đặt EI_TAP="training" hoặc "testing" (xem tools/tang_cuong/tai_len_tang_cuong.command).

set -u
PROJECT_ID=1156522
BATCH=100        # số tệp mỗi yêu cầu (~3,2 MB)
PAR=3            # số yêu cầu chạy song song

cd "$(dirname "$0")/../.." || exit 1
export DATA="${EI_DATA:-data/ei_upload}"
TAP="${EI_TAP:-training testing}"
TEN=$(basename "$DATA")
export STATE="$DATA/.tai_len"
export LOG="$DATA/nhat_ky_tai_len.txt"
if [ "$TEN" = "ei_upload" ]; then TOMTAT="results/ei_tai_len_ket_qua.txt"; else TOMTAT="results/ei_tai_len_ket_qua_${TEN}.txt"; fi
mkdir -p "$STATE/lo" "$STATE/xong" "$STATE/phan_hoi"

ghi() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" | tee -a "$LOG"; }
export -f ghi

echo "=== TussiCount: tải $DATA lên Edge Impulse (dự án $PROJECT_ID) ==="

# 1. Hỏi API key
KEY=$(osascript \
  -e 'try' \
  -e 'text returned of (display dialog "Dán API key của dự án Edge Impulse TussiCount (bắt đầu bằng ei_) rồi bấm Tải lên." default answer "" with hidden answer with title "TussiCount – tải dữ liệu lên Edge Impulse" buttons {"Huỷ", "Tải lên"} default button "Tải lên" cancel button "Huỷ")' \
  -e 'on error' -e 'return ""' -e 'end try' 2>/dev/null)
if [ -z "$KEY" ]; then
  printf "Dán API key vào đây (không hiện ký tự) rồi nhấn Enter: "
  read -r -s KEY; echo
fi
KEY=$(printf '%s' "$KEY" | tr -d '[:space:]')
case "$KEY" in ei_*) ;; *) echo "Key không hợp lệ (phải bắt đầu bằng ei_). Dừng."; exit 1 ;; esac
export EI_KEY="$KEY"; unset KEY

api() { printf 'header = "x-api-key: %s"\n' "$EI_KEY" | curl -sS -K - --max-time 60 "$@"; }

# 2. Kiểm tra key thuộc đúng dự án
R=$(api "https://studio.edgeimpulse.com/v1/api/projects")
if ! printf '%s' "$R" | grep -Eq "\"id\": ?$PROJECT_ID[,}]"; then
  echo "Key không truy cập được dự án $PROJECT_ID. Phản hồi máy chủ:"; printf '%s\n' "$R" | head -c 300; echo
  exit 1
fi
dem() { api "https://studio.edgeimpulse.com/v1/api/$PROJECT_ID/raw-data/count?category=$1" | grep -Eo '"count": ?[0-9]+' | grep -Eo '[0-9]+'; }
ghi "BAT DAU. Truoc khi tai: training=$(dem training) testing=$(dem testing) mau tren du an."

# 3. Chia lô (một lần, thứ tự cố định để chạy lại vẫn khớp)
if [ ! -f "$STATE/lo/.da_tao" ]; then
  for sp in $TAP; do for lb in cough noise; do
    [ -d "$DATA/$sp/$lb" ] || continue
    ls "$DATA/$sp/$lb" | grep '\.wav$' | LC_ALL=C sort | split -a 3 -l "$BATCH" - "$STATE/lo/${sp}__${lb}__"
  done; done
  touch "$STATE/lo/.da_tao"
fi
TONG=$(ls "$STATE/lo" | grep -c '__')
ghi "So lo: $TONG (moi lo toi da $BATCH tep), chay song song $PAR."

# 4. Tải từng lô
tai_lo() {
  local lo="$1" ten sp rest lb f code n tep loi trung thu
  ten=$(basename "$lo"); sp=${ten%%__*}; rest=${ten#*__}; lb=${rest%%__*}
  [ -f "$STATE/xong/$ten" ] && return 0
  local args=()
  while IFS= read -r f; do args+=(-F "data=@$DATA/$sp/$lb/$f;type=audio/wav"); done < "$lo"
  n=$(( ${#args[@]} / 2 ))
  for thu in 1 2 3 4 5; do
    code=$(printf 'header = "x-api-key: %s"\nheader = "x-label: %s"\nheader = "x-disallow-duplicates: 1"\n' "$EI_KEY" "$lb" \
      | curl -sS -K - --max-time 300 -o "$STATE/phan_hoi/$ten.json" -w '%{http_code}' "${args[@]}" \
        "https://ingestion.edgeimpulse.com/api/$sp/files" 2>>"$LOG")
    tep=$(grep -o '"fileName"' "$STATE/phan_hoi/$ten.json" 2>/dev/null | wc -l | tr -d ' ')
    loi=$(grep -o '"error"' "$STATE/phan_hoi/$ten.json" 2>/dev/null | wc -l | tr -d ' ')
    trung=$(grep -oi 'already exists' "$STATE/phan_hoi/$ten.json" 2>/dev/null | wc -l | tr -d ' ')
    if [ "$code" = "200" ] && [ $(( loi - trung )) -le 0 ]; then
      echo "$n $tep $trung" > "$STATE/xong/$ten"
      ghi "OK  $sp/$lb ${ten##*__}: $n tep gui, $tep phan hoi, $trung trung (lan $thu) [$(ls "$STATE/xong" | wc -l | tr -d ' ')/$TONG]"
      return 0
    fi
    ghi "LOI $sp/$lb ${ten##*__}: HTTP $code, $loi loi (lan $thu); thu lai sau $((thu*10)) s"
    sleep $(( thu * 10 ))
  done
  ghi "BO  $sp/$lb ${ten##*__}: that bai sau 5 lan. Chay lai tep nay de tai tiep."
  return 1
}
export -f tai_lo; export TONG
ls "$STATE/lo"/*__* | xargs -P "$PAR" -n 1 bash -c 'tai_lo "$1"' _
XONG=$(ls "$STATE/xong" | wc -l | tr -d ' ')

# 5. Đối chiếu số mẫu trên dự án
sleep 5
TR=$(dem training); TE=$(dem testing)
# Số mẫu mong đợi trên dự án = tổng các thư mục dữ liệu đã từng tải (có .tai_len/lo/.da_tao)
KTR=0; KTE=0
# (chỉ tính phần đã chia lô, vì có thư mục chỉ tải training)
for d in data/ei_upload data/ei_kiem_tra_ben data/ei_tang_cuong; do
  [ -f "$d/.tai_len/lo/.da_tao" ] || continue
  if ls "$d/.tai_len/lo"/training__* >/dev/null 2>&1; then KTR=$(( KTR + $(find "$d/training" -name '*.wav' 2>/dev/null | wc -l) )); fi
  if ls "$d/.tai_len/lo"/testing__* >/dev/null 2>&1; then KTE=$(( KTE + $(find "$d/testing" -name '*.wav' 2>/dev/null | wc -l) )); fi
done
ghi "KET THUC. Lo xong $XONG/$TONG. Tren du an: training=$TR (may: $KTR), testing=$TE (may: $KTE)."
{
  echo "Tải $DATA lên Edge Impulse – dự án $PROJECT_ID"
  echo "Thời điểm kết thúc: $(date '+%Y-%m-%d %H:%M:%S %z')"
  echo "Cách tải: Ingestion API /api/<training|testing>/files, $BATCH tệp mỗi yêu cầu, nhãn theo thư mục, chặn tệp trùng."
  echo "Lô hoàn tất: $XONG/$TONG"
  echo "Trên máy (mọi thư mục đã tải): training $KTR tệp, testing $KTE tệp"
  echo "Trên dự án:  training $TR mẫu, testing $TE mẫu"
  echo "Nhật ký chi tiết: $LOG (không chứa API key)"
} > "$TOMTAT"
unset EI_KEY
if [ "$XONG" = "$TONG" ] && [ "$TR" = "$KTR" ] && [ "$TE" = "$KTE" ]; then
  echo; echo "XONG: số mẫu trên Edge Impulse khớp với dữ liệu trên máy. Có thể đóng cửa sổ này."
  osascript -e 'display notification "Đã tải xong, số mẫu khớp." with title "TussiCount – Edge Impulse"' 2>/dev/null
else
  echo; echo "CHƯA KHỚP: xem $LOG. Nhấp đúp lại tệp này để tải tiếp phần còn thiếu."
fi
