# Phiên phụ: một seed của bảng "Ground transport on fixed CHORD passes" (CLAUDE.md §8 mục 227–229)

Phiên chính (điều phối) giao cho bạn **một seed R** và một tập phương án **SCH** (ví dụ `tp` hoặc `d,t`; TAG = SCH
với dấu phẩy thay bằng `-`). Bản đồ k8-s1 (8 cụm, 45 critical cell), kênh r100, pass CHORD
cố định của chiến dịch 4. Bốn phương án mặt đất trên cùng pass: `rf` (River), `d` (kéo trực tiếp), `t` (Trickle/Deluge
trên các cell của kế hoạch River), `tp` (Trickle chỉ trên Axe, critical cell và các cell của đường kéo trực tiếp).
Trang Trickle căn theo ranh giới ảnh (`page_breaks.py`). Tham số Trickle: Imin 1 s, Imax 64 s, k = 1, page 64 gói.

## Quy tắc
- Nhánh `claude/document-review-xslwgg`. Chỉ commit tệp của mình: `logs/2026-10-30_1545-deluge-r100/results/R<R>/`
  và `logs/2026-10-30_1545-deluge-r100/R<R>-<TAG>.md`. Không sửa mã, không rebuild ns-3, không sửa CLAUDE.md.
- Push: `git pull --rebase origin claude/document-review-xslwgg && git push -u origin claude/document-review-xslwgg`,
  lỗi mạng thì thử lại tối đa 4 lần (2, 4, 8, 16 s).
- Trả lời bằng tiếng Việt, ngắn gọn.

## Các bước
```bash
cd <repo>   # /home/user/wsn-uav
git fetch origin claude/document-review-xslwgg && git checkout claude/document-review-xslwgg && git pull
L=$PWD/logs/2026-10-30_1545-deluge-r100
export CAMP_S=<scratchpad của phiên này>
bash $L/setup.sh                     # phải in CHECK OK; nếu không, dừng và báo lỗi
cd $L && setsid nohup python3 $PWD/../../tools/runlog.py $L/R<R>-<TAG>.md "bash run.sh <R> <SCH>" --cwd $L > /dev/null 2>&1 &
```
- Chờ bằng Monitor/until-loop trên tệp `$L/results/R<R>/done-<TAG>` (timeout dài, chạy nền; lệnh nền bị giết sau 2 giờ nên
  dùng `setsid nohup` như trên cho tiến trình chính). Đặt thêm một `send_later` 2 giờ làm lưới an toàn.
- Nếu phiên khởi động lại giữa chừng: chạy lại `setup.sh` (không xoá `$CAMP_S/DT`), rồi chạy lại lệnh `run.sh`; mission
  bỏ qua các cụm đã xong.
- Xong (`done-<TAG>` có mặt): kiểm tra `results/R<R>/` có `r{1..8}-<mỗi phương án của SCH>-{crit,runs,energy}.csv`,
  commit và push (các tệp `rf` trùng với phiên khác là bình thường: cùng seed, cùng binary nên giống hệt).
  Báo lại một dòng: số critical cell xong theo từng phương án và tổng thời gian chạy.
