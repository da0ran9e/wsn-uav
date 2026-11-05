# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## 5. Task Completion Reporting

**After finishing any task, report the modifications quickly.**

- List each file modified and what changed
- One-line summary per file (the WHY, not WHAT)
- Include build/test results if applicable
- Format: `[file.cc] Change description — status ✓/✗`

Example:
```
[scenario1-config.cc] Moved RX callback setup to Build() — ✓
[ground-node-app.cc] Removed RX callback override in StartApplication — ✓
[CMakeLists.txt] Added lr-wpan-module include — ✓
Build: ✓ (rebuilt successfully)
Test: ✗ (RX callbacks still not firing)
```

---

## 6. Quy tắc làm việc của dự án

**Lời người dùng (chat log):** mỗi tin nhắn của người dùng được ghi nguyên văn, không chỉnh sửa, vào
`docs/chatlog/<YYYY-MM>.md` theo khuôn sẵn có (nhãn nghiêng do Claude thêm + khối `text` lời gốc), đánh số
tiếp theo, và thêm một dòng vào `docs/chatlog/INDEX.md`. Đây là tham chiếu gốc: khi có mâu thuẫn, lời người
dùng ở đó và lời mới hơn thắng. Không ghi chat log vào CLAUDE.md nữa (từ 2026-11-05, mục 271).

**Quy tắc làm việc hiện hành:** thảo luận và lên kế hoạch kỹ với người dùng trước khi chạy
bất kỳ chương trình tốn thời gian nào (mục 35).

**Lưu log (mục 94):** mọi lần chạy chương trình đều ghi toàn bộ log (lệnh, stdout/stderr, tham số)
vào `logs/<YYYY-MM-DD_HHMM>-<tên-ngắn>/`, mỗi session hoặc nhiệm vụ một folder. Cuối session hoặc nhiệm
vụ, viết `logs/<...>/README.md` mô tả ngắn: mục đích, lệnh đã chạy, đầu vào, đầu ra (đường dẫn), kết quả
chính và điều còn dang dở. Log văn bản được commit; dữ liệu thô quá lớn thì chỉ ghi đường dẫn và kích thước.
Log viết dạng `.md` cho dễ đọc (mục 106): mỗi bước một file `<bước>.md` có khối lệnh và khối kết quả; chạy qua
`python3 tools/runlog.py logs/<...>/<bước>.md "<lệnh>" [--cwd DIR]` để tự ghi (`.gitignore` bỏ qua `*.log`).

**Lưu ảnh (mục 131):** mọi ảnh sinh ra từ bản build, visualize hay chương trình giả lập đều commit vào
`docs/figures/` của module tương ứng (kể cả ảnh tạm, vì container bị xoá khi session dừng). Ảnh tạo không có
chữ (mục 63) để dễ dùng lại; bản có nhãn trục cho paper lưu riêng. Tên file mô tả nội dung (ví dụ
`c3-step4-circle-window.png`, không dùng `out1.png`). Mỗi thư mục `figures/` có `INDEX.md`, mỗi ảnh một dòng:
tên file, mô tả trực quan một câu, lệnh hoặc script sinh ra, tham số chính (bản đồ, seed, binary), ngày, commit.
Chỉ áp dụng cho ảnh mới; ảnh cũ không đổi tên hay xoá.

**Trạng thái và kế hoạch:** đọc `docs/progress/HANDOFF.md` trước khi làm tiếp việc dở. Kế hoạch tái tổ chức
repo và ước lượng chi phí từng bước: `docs/REORG-GUIDE-vi.md`.

## 7. Bản đồ repo

| Thư mục | Nội dung | Quy tắc riêng |
|---|---|---|
| `uav-l2/` | lớp 2 + mô phỏng nhiệm vụ đang làm (CHORD, LM-Tour, River, các baseline); `tools/`, `docs/` | — |
| `paper/` | tài liệu cho paper SigDrop (ICC), `icc-v5/` LaTeX | — |
| `logs/` | log chạy chương trình theo `<ngày-giờ>-<tên>/`, mỗi thư mục một README; chỉ mục `logs/INDEX.md` (thêm một dòng mỗi thư mục mới) | — |
| `docs/` | `chatlog/`, `progress/HANDOFF.md`, `EXPERIMENTS-INDEX.md` (mã thí nghiệm, số liệu trong paper), `REORG-GUIDE-vi.md`, insights | — |
| `uav-sar/` | thí nghiệm A2G-RUN, A2G-SWEEP, G2G-CHAIN (mục 1–8) | `uav-sar/CLAUDE.md` |
| `uav-coop/`, `uav-coop2/` | cơ chế Manifest và River trên một cluster (mục 9–55), đã đóng | — |
| `models/`, `helper/`, `examples/` | mã wsn-uav cũ (scenario 1–4) | `models/CLAUDE.md` |
| `tools/` | `runlog.py`, `run_batch.sh` | — |

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
