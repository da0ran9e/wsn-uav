# Phiên phụ của chiến dịch 4 (CLAUDE.md §8 mục 201)

Bạn là một trong 8 phiên cloud phụ. Mỗi phiên chạy **đúng một seed mô phỏng R (3–10)** của chiến dịch bốn phương án. Phiên chính chạy seed 1–2, điều phối và gộp bảng. Đọc `README.md` trong thư mục này để biết bối cảnh. Mọi việc dưới đây đã được người dùng duyệt; không cần hỏi lại.

## Quy tắc
- Làm trên nhánh `claude/document-review-xslwgg`.
- **Chỉ commit tệp của mình:**
  - `logs/2026-10-27_1714-campaign4/score/R<R>/`;
  - `logs/2026-10-27_1714-campaign4/R<R>/`;
  - `logs/2026-10-27_1714-campaign4/done-s<R>.txt`.
- Không sửa `CLAUDE.md`, `RESULTS-vi.md`, `campaign4.csv`, `table-campaign4.tex`, `done.txt`, `assigned/` hay mã nguồn. Các tệp này do phiên chính quản lý.
- Nếu một tệp khác trong repo cần sửa, ghi lý do vào `done-s<R>.txt` và để phiên chính làm.
- Push: `git add <tệp của mình> && git commit -m "campaign4 seed <R>: ..." && git pull --rebase origin claude/document-review-xslwgg && git push origin claude/document-review-xslwgg`. Lỗi mạng thì thử lại tối đa 4 lần.
- Cuối thông điệp commit thêm hai dòng:
  ```
  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  Claude-Session: <đường dẫn phiên của bạn>
  ```
- Mọi lệnh chạy chương trình đều ghi log Markdown qua `python3 tools/runlog.py <tệp .md> "<lệnh>"`. Các log này nằm trong `R<R>/`, do `camp2.sh` tự ghi.

## Các bước
Biến dùng xuyên suốt:

```bash
export CAMP_S=<scratchpad của phiên này>    # đường dẫn tuyệt đối, xem phần Environment của phiên
export CAMP_ID=s<R> CAMP_DONE=done-s<R>.txt
L=logs/2026-10-27_1714-campaign4
```

1. **Cài đặt:** `bash $L/child-setup.sh`.
   - Lệnh này giải nén binary đóng băng (`camp-bin5.tar.xz`, hash 508c170d / 4bb3832e / 60a32c12) và hình học CHORD của seed 1 (`geometry-r1.tar.xz`) vào `$CAMP_S`, rồi cài scikit-learn.
   - Không dựng lại ns-3.
2. **Kiểm tra:** `python3 tools/runlog.py $L/R<R>/check-s<R>.md "CAMP_S=$CAMP_S bash $L/child-check.sh"`.
   - Lệnh này bay lại CHORD + River của seed 1, kênh 1 km, bản đồ k8. Phải in `CHECK OK`: 100/100 lượt bốc trùng T\* của phiên chính.
   - Nếu `FAIL`: dừng, ghi lý do vào `done-s<R>.txt`, commit, push rồi kết thúc. Không chạy tiếp.
3. **Chạy:** `setsid nohup bash $L/camp2.sh <R> <R> > /dev/null 2>&1 < /dev/null &`.
   - Chạy từ thư mục gốc repo, giữ nguyên các biến `CAMP_*` ở trên.
   - Hàng đợi gồm 36 job (3 phương án × 3 bản đồ × 4 kênh), chạy 4 job cùng lúc, mỗi job `--jobs 1`.
   - Cần khoảng 5–6 giờ.
4. **Giữ container sống.** Container bị thu hồi hoặc khởi động lại khi phiên rảnh.
   - Luôn giữ một lệnh Bash `run_in_background` với timeout 7200000:
     ```bash
     cd $L; n0=$(wc -l < done-s<R>.txt 2>/dev/null || echo 0); until [ $(wc -l < done-s<R>.txt 2>/dev/null || echo 0) -gt $n0 ] || ! pgrep -f camp2.sh > /dev/null; do sleep 60; done; tail -3 done-s<R>.txt; uptime
     ```
   - Mỗi khi lệnh đó kết thúc thì đặt lại.
   - Thêm một lịch kiểm tra dự phòng 2 giờ bằng `send_later` (công cụ claude-code-remote).
5. **Khi máy khởi động lại** (uptime ngắn, không còn tiến trình `job.sh`):
   - export lại các biến;
   - giải nén lại nếu `$CAMP_S/CAMP-BIN5` không còn;
   - chạy lại lệnh ở bước 3 và ghi một dòng "restart" vào `done-s<R>.txt`.
   - Job đã có dấu `done-*` được bỏ qua; pass và River đã xong cũng được bỏ qua.
6. **Mỗi khi có job xong:** commit và push tệp của mình. Job có exit khác 0 (trừ 3, 4) thì đọc log `R<R>/<kênh>-k<K>-<phương án>.md`:
   - nếu là lỗi môi trường, sửa rồi chạy lại;
   - nếu là lỗi mã, ghi vào `done-s<R>.txt` và commit để phiên chính xử lý.
7. **Xong** (dòng `queue done` trong `done-s<R>.txt`, đủ 36 dấu `done-*` dưới `score/R<R>/`):
   - commit và push lần cuối;
   - huỷ lịch kiểm tra dự phòng;
   - kết thúc bằng một câu tóm tắt: seed, số job xong, lỗi nếu có.

## Kết quả do phiên chính gộp
Phiên chính chạy `table.py`, cập nhật `uav-l2/docs/RESULTS-vi.md` §7.1 và bảng LaTeX từ các thư mục `score/R*`. Phiên phụ không chạy `table.py --results`.
