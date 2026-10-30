# Phiên phụ: Deluge-lite (SigDrop 2, phương án backup; CLAUDE.md §8 mục 233)

Bản đồ k12-s1 (12 cụm, 66 critical cell), tour LM-Tour của chiến dịch 4, kênh open và r200, seed ns-3 R.
River (`rf`) và Deluge-lite (Trickle trên mọi cell của cụm, k = 1, page 64 gói ngắt tại đầu ảnh và đầu Seg).
Hai cấu hình Trickle: `dla` (Imin 0,5 s, Imax 8 s) và `dlb` (2 s, 60 s); phiên điều phối chọn một sau khi tinh chỉnh
trên seed 1, open, và ghi vào `dl-config.txt`.

## Quy tắc
- Nhánh `claude/document-review-xslwgg`. Chỉ commit `logs/2026-10-30_1730-deluge-lite/results/` (tệp của seed mình)
  và log `logs/2026-10-30_1730-deluge-lite/<tên>.md`. Không sửa mã, không rebuild ns-3, không sửa CLAUDE.md, không mở PR.
- Push: `git pull --rebase origin claude/document-review-xslwgg && git push -u origin claude/document-review-xslwgg`,
  lỗi mạng thử lại tối đa 4 lần (2, 4, 8, 16 s). Commit message kết thúc bằng
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Không chọn seed theo kết quả, không đổi tham số Trickle. Lỗi thì ghi `results/ERROR-<tên>.md`, commit, push, báo lại.
- Trả lời ngắn gọn bằng tiếng Việt, không hỏi lại người dùng.

## Các bước
```bash
cd /home/user/wsn-uav
git fetch origin claude/document-review-xslwgg && git checkout claude/document-review-xslwgg && git pull
L=$PWD/logs/2026-10-30_1730-deluge-lite
export CAMP_S=<scratchpad của phiên này>
bash $L/setup.sh                      # phải in CHECK OK
```
- **Phiên seed R** (R = 1..8): `cd $L && setsid nohup python3 ../../tools/runlog.py $L/R<R>.md "bash dl-session.sh <R>"
  --cwd $L > /dev/null 2>&1 &`. Script tự chạy River hai kênh, push, chờ `dl-config.txt`, rồi chạy Deluge-lite hai
  kênh và push sau mỗi kênh. Chờ tệp `$L/results/done-R<R>`.
- **Phiên tinh chỉnh** (CFG = dla hoặc dlb): `... runlog.py $L/tune-<CFG>.md "bash dl-run.sh open 1 <CFG>" ...`; xong thì
  commit `results/open-R1-<CFG>-*` và `results/open-R1-rf-*` cùng `tune-<CFG>.md`, push, báo dòng tổng kết
  (`open R1 <CFG>: x/66 ready, mean ...`).
- Chờ bằng until-loop chạy nền (timeout 7200000) cộng `send_later` 2 giờ làm lưới an toàn; lưới bắn mà chưa xong thì
  đặt lại. Lệnh nền bị giết sau 2 giờ, nên tiến trình chính phải chạy bằng `setsid nohup` như trên.
- Phiên khởi động lại giữa chừng: chạy lại `setup.sh` (không xoá `$CAMP_S/DL`), rồi lệnh cũ; mission bỏ qua cụm đã xong.
