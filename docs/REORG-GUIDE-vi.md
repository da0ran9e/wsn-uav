# Hướng dẫn tái tổ chức repo

- **Trạng thái:** kế hoạch, chưa thực hiện. Người dùng sẽ yêu cầu làm từng bước khi có thời gian (CLAUDE.md §8 mục 266–270).
- **Ngày:** 2026-11-04. Số liệu đo trên commit của nhánh `claude/document-review-xslwgg` cùng ngày.
- **Cách dùng:** mỗi bước làm được độc lập, theo thứ tự dưới đây. Bước nào xong thì đánh dấu `[x]` và ghi commit.

## Tiến độ

| Bước | Trạng thái | Ghi chú |
|---|---|---|
| 1. Tách chat log | [x] 2026-11-05 | 271 mục ở `docs/chatlog/2026-10.md`, `2026-11.md`, `INDEX.md`; khối `text` khớp từng byte |
| 2. Tách CLAUDE.md | [x] 2026-11-05 | CLAUDE.md 179 kB → khoảng 6 kB; quy tắc uav-sar sang `uav-sar/CLAUDE.md`, wsn-uav cũ sang `models/CLAUDE.md` |
| 3. Chỉ mục log và mã thí nghiệm | [x] 2026-11-05 | `logs/INDEX.md` (58 thư mục, mã + trạng thái), `docs/EXPERIMENTS-INDEX.md` (11 thí nghiệm đang dùng trong paper v5.3 + tham khảo) |
| 4. Phân loại tài liệu | [x] 2026-11-06 | 54 tài liệu có YAML `status`; `docs/DOCS-INDEX.md`; 10 bản nháp paper → `paper/archive/`; tài liệu module (uav-sar, uav-coop, uav-coop2) giữ nguyên chỗ |
| 5. Lưu trữ module cũ | [x] 2026-11-06 | wsn-uav cũ (models, helper, examples, CMakeLists, wscript, docs cũ) → `archive/wsn-uav-legacy/`. **Không** dời `uav-coop/`, `uav-coop2/`: mã ns-3 của chúng là binary deploy/pass/river đang dùng. Đổi tên thư mục có dấu cách trong `research_notes/`, `reports/` |
| 6. Giảm dung lượng | [~] 2026-11-06 | Chưa làm. Tệp lớn nằm sẵn trong lịch sử git, dời ra Release cũng không giảm `.git` nếu không viết lại lịch sử (thao tác phá huỷ, cần người dùng duyệt). Quy tắc mới: `check.py large` chặn tệp mới trên 5 MB |
| 7. Một nguồn tham số | [x] 2026-11-06 | `params.yaml` + `tools/params.py` (render/check); bảng `paper/PARAMS-vi.md` tái tạo giống từng byte. Mã chưa đọc `params.yaml` |
| 8. Kiểm tra tự động | [x] 2026-11-06 | `tools/check.py`, `tools/build_index.py`; hook `tools/hooks/pre-commit` (chỉ kiểm tệp được commit, cài bằng `git config core.hooksPath tools/hooks`), 2026-11-06 |

## 0. Hiện trạng

| Hạng mục | Số đo | Vấn đề |
|---|---|---|
| Tệp trong git | 7 800 (logs 4 399, uav-l2 2 602, uav-sar 282, uav-coop 199, uav-coop2 169, paper 64) | Khó tìm, không có chỉ mục |
| Tài liệu `.md` | 1 626 tệp; ngoài log khoảng 1,66 MB ≈ 500 nghìn token | Nhiều bản tổng quan trùng nhau (OVERVIEW, SUMMARY, TECHREPORT, L3-TECHREPORT, RIVER…), không biết bản nào hiện hành |
| `CLAUDE.md` | 177 kB ≈ 55–60 nghìn token, phần lớn là chat log (mục 1–270) | Nạp vào **mọi phiên**; §6–§7 (uav-sar, wsn-uav cũ) không còn dùng cho việc hiện tại |
| Nhị phân và dữ liệu | 4 163 tệp png/pdf/csv/xz/bin ≈ 178 MB; `.git` 239 MB | Clone chậm, tốn đĩa container |
| README của log | 55 README, khoảng 180 kB | Không có bảng tổng của các thư mục log |
| Nhánh | `claude/document-review-xslwgg` (hiện tại); `main` (01/07, 2 commit riêng); `claude/jolly-ptolemy-nytjc1` (12/09, chứa 2 commit của main + 7 commit `uav-screening-depth/`) | Nhánh mặc định `main` đã cũ 4 tháng |
| Quyền truy cập | Repo đang **public** | Mục 37 muốn private; người dùng tự đổi trong Settings |

## 1. Quy tắc đích

**Nguyên tắc:**
1. Mỗi thông tin một nguồn sự thật.
2. Cái gì sinh ra được từ nguồn thì không sửa tay.
3. Mọi tài liệu có nhãn trạng thái.
4. Lưu trữ thay vì xoá.
5. Không di chuyển mã hay thư mục log đang được script trỏ tới.

**Định dạng theo loại:**

| Loại | Lưu ở đâu, dạng gì |
|---|---|
| Chat log (lời gốc người dùng) | `docs/chatlog/YYYY-MM.md`, khuôn như CLAUDE.md §8 hiện tại; `docs/chatlog/INDEX.md`: số mục, ngày, chủ đề, tệp |
| Quy tắc | `CLAUDE.md` gốc dưới 10 kB (quy tắc chung, bản đồ repo, trỏ tới chatlog/HANDOFF); `CLAUDE.md` riêng trong `uav-l2/`, `uav-sar/`, `paper/` |
| Trạng thái | `docs/progress/HANDOFF.md`, chỉ giữ bản mới nhất; lịch sử nằm trong git |
| Tài liệu nghiên cứu | Mỗi chủ đề một tệp chuẩn; đầu tệp có YAML `status`, `updated`, `supersedes`, `experiments`; bản cũ vào `archive/` |
| Paper | LaTeX là nguồn; PDF đã nộp ở `paper/submitted/` (ví dụ `SigDrop_ICC_v5.3.pdf`) và tag git |
| Số liệu | CSV một hàng một lượt chạy (seed, bản đồ, kênh, phương án, commit); bảng md/tex sinh bằng script |
| Tham số | `params.yaml` một nguồn; bảng tham số trong tài liệu và paper sinh từ đó |
| Ảnh | PNG xem nhanh, PDF/SVG cho paper, kèm script và `INDEX.md` (mục 131); tệp trên 5 MB chỉ ghi đường dẫn |
| Log chạy | Giữ `logs/<ngày-giờ>-<tên>/` + `runlog.py`; thêm `logs/INDEX.md`, mỗi thư mục một dòng: mã thí nghiệm, mục đích, kết quả, còn dùng không |
| Ghi chú nhanh | `docs/NOTES.md`, ghi nối có ngày |
| Thí nghiệm | Mỗi chiến dịch một mã (C4, DLG1, WIND1, TKO1…), dùng chung cho thư mục log, CSV, tài liệu, hình; `docs/EXPERIMENTS-INDEX.md` |
| Tên tệp | Chữ thường, gạch ngang, ngày ISO, hậu tố ngôn ngữ thống nhất; không dấu cách hay ngoặc kép (`"research_notes`, `"reports`) |

**Bố cục thư mục đích:**

```text
CLAUDE.md                  quy tắc chung + bản đồ repo
docs/
  chatlog/                 YYYY-MM.md, INDEX.md
  progress/HANDOFF.md
  EXPERIMENTS-INDEX.md, NOTES.md, REORG-GUIDE-vi.md
paper/                     tài liệu chuẩn theo chủ đề, icc-v5/, submitted/, CLAUDE.md
uav-l2/                    module đang làm (mã + docs + figures), CLAUDE.md
uav-sar/                   giữ nguyên, CLAUDE.md riêng (§6 hiện tại)
logs/                      giữ nguyên + INDEX.md
tools/                     runlog.py, check.py, build_index.py
archive/                   uav-coop/, uav-coop2/, wsn-uav-legacy/ (models, helper, examples),
                           uav-screening-depth/, tài liệu bị thay thế; mỗi mục một README
```

## 2. Các bước

Chi phí tính theo hai cột:
- **token mới:** phần đọc và viết thật;
- **tổng xử lý:** kể cả ngữ cảnh gửi lại ở mỗi lần gọi công cụ, phần lớn được cache.

Mỗi bước chạy trong một phiên riêng, bắt đầu bằng việc đọc tệp này.

| # | Bước | Việc làm | Kiểm tra xong | Token mới | Tổng xử lý |
|---|---|---|---|---|---|
| 1 | **Tách chat log** | Script tách §8 của CLAUDE.md thành `docs/chatlog/YYYY-MM.md` + `INDEX.md`; đổi quy tắc mục 35 (ghi vào chatlog thay vì CLAUDE.md); CLAUDE.md giữ một dòng trỏ tới | Số mục trong chatlog = số mục §8 cũ; diff khối `text` trùng từng byte | 10–20 nghìn | 50–80 nghìn |
| 2 | **Tách CLAUDE.md theo thư mục** | CLAUDE.md gốc dưới 10 kB; §6 sang `uav-sar/CLAUDE.md`; §7 (wsn-uav cũ) sang `archive/wsn-uav-legacy/CLAUDE.md`; quy tắc uav-l2/paper sang thư mục tương ứng | `wc -c CLAUDE.md` < 10 kB; không mất quy tắc nào (đối chiếu từng dòng) | 15–25 nghìn | 60–100 nghìn |
| 3 | **Chỉ mục log và mã thí nghiệm** | Đọc 55 README log, viết `logs/INDEX.md` và `docs/EXPERIMENTS-INDEX.md`, đặt mã thí nghiệm | Mỗi thư mục log có đúng một dòng; mỗi mã trỏ tới log, CSV, tài liệu | 80–120 nghìn | 200–300 nghìn |
| 4 | **Phân loại tài liệu** | Đọc đầu và mục lục khoảng 120 tài liệu ngoài log; gắn YAML trạng thái; chuyển tài liệu bị thay thế hoặc không liên quan vào `archive/`; sửa liên kết | `tools/check.py` không báo liên kết hỏng; mỗi chủ đề còn đúng một tệp `status: current` | 250–400 nghìn | 500–800 nghìn |
| 5 | **Lưu trữ module cũ** | `uav-coop/`, `uav-coop2/`, `models/`, `helper/`, `examples/`, `wscript`, `CMakeLists.txt` của wsn-uav cũ vào `archive/`, mỗi module một README kết luận; đổi tên thư mục có ngoặc kép | `grep` không còn script đang dùng trỏ tới đường dẫn cũ; build ns-3 của uav-l2 vẫn chạy (`cmake --build cmake-cache`) | 40–80 nghìn | 150–250 nghìn |
| 6 | **Giảm dung lượng** | Binary đóng băng và tarball (`camp-bin5.tar.xz`, `geometry-r1.tar.xz`…) lên GitHub Release hoặc Git LFS, giữ hash + lệnh tải; `.gitignore` cho dữ liệu sinh lại được (bitmap pass, CSV từng gói) | `child-setup.sh` vẫn cài được từ Release; hash khớp | 30–60 nghìn | 100–200 nghìn |
| 7 | **Một nguồn số liệu và tham số** | `params.yaml`; script sinh bảng tham số và bảng kết quả (đã có `table.py`, `techreport.py`) cho mọi tài liệu còn chép tay | Bảng sinh lại trùng với bảng hiện có | 60–100 nghìn | 200–300 nghìn |
| 8 | **Kiểm tra tự động** | `tools/check.py` (liên kết hỏng, ảnh thiếu INDEX, tệp > 5 MB, YAML thiếu) + `tools/build_index.py`; pre-commit hook tuỳ chọn | Chạy sạch trên repo sau bước 4 | 30–50 nghìn | 80–150 nghìn |
| 9 | **Gộp nhánh và đưa lên main** | Xem mục 3 dưới đây | `git log main` chứa đủ commit của 3 nhánh; tag tồn tại | 20–40 nghìn | 60–120 nghìn |
| 10 | **Hợp nhất nội dung** (tuỳ chọn) | Đọc toàn văn, gộp các bản tổng quan trùng thành bộ chuẩn, viết lại phần lỗi thời, đối chiếu số liệu với CSV | Không còn hai tài liệu `current` cùng chủ đề; mọi số khớp CSV | 1–1,5 triệu | 2,5–4 triệu |

| Gói | Bước | Token mới | Tổng xử lý |
|---|---|---|---|
| Tối thiểu (lợi nhất) | 1, 2 | 25–45 nghìn | 110–180 nghìn |
| Đề xuất | 1–9 | 0,55–0,9 triệu | 1,4–2,3 triệu |
| Đầy đủ | 1–10 | 1,6–2,4 triệu | 4–6 triệu |

Sau bước 1–2, mỗi phiên tiết kiệm khoảng 50 nghìn token, vì CLAUDE.md không còn chứa chat log. Hai bước này hoàn vốn chỉ sau 2–3 phiên.

## 3. Gộp nhánh (bước 9, chỉ làm khi người dùng cho phép rõ ràng)

Kiểm tra ngày 2026-11-04:
- ba nhánh tách nhau ở `942fd0d` (2026-05-15);
- `jolly-ptolemy` chứa trọn 2 commit riêng của `main`, cộng 7 commit thêm thư mục mới `uav-screening-depth/` và sửa `models/`;
- gộp thử vào nhánh hiện tại chỉ xung đột ở `CMakeLists.txt`.

1. Gắn tag và push:
   - `archive/main-2026-07-01` trên `main`;
   - `archive/jolly-ptolemy-2026-09-12` trên `claude/jolly-ptolemy-nytjc1`;
   - `icc-v5.3-submit` trên commit nhánh hiện tại tương ứng bản nộp.
2. `git merge --no-ff origin/claude/jolly-ptolemy-nytjc1` vào nhánh hiện tại; sửa `CMakeLists.txt` bằng cách giữ cả hai danh sách nguồn.
3. Đưa kết quả lên `main` bằng fast-forward. `main` cũ đã nằm trong bản gộp nên không cần force push.
4. Áp quy tắc ở mục 1:
   - `uav-screening-depth/` vào `archive/` (hoặc giữ ở gốc nếu còn dùng; hỏi người dùng);
   - đổi nhánh mặc định không cần (vẫn là `main`).
5. Từ đó làm trên `main` hoặc nhánh phụ tách từ `main`. Chỉ xoá các nhánh `claude/*` khi người dùng đồng ý; tag đã giữ nội dung.

**Lưu ý quyền:**
- phiên cloud hiện chỉ được push lên `claude/document-review-xslwgg`; push `main` hay tag cần người dùng cho phép;
- đổi repo sang private do người dùng tự làm trên GitHub.

## 4. Rủi ro và cách tránh

| Rủi ro | Cách tránh |
|---|---|
| Script trỏ cứng đường dẫn (`job.sh`, `camp2.sh` → `logs/2026-10-27_1714-campaign4`, `uav-l2/tools`) | Không di chuyển `logs/` và `uav-l2/`; trước mỗi lần dời tệp chạy `git grep` tên tệp |
| Mất lời gốc khi tách chat log | Tách bằng script, so từng byte các khối `text` trước và sau |
| Xoá nhầm tài liệu còn dùng | Chỉ chuyển vào `archive/`, không xoá; nhãn `superseded_by` trỏ tới bản mới |
| Phiên bị ngắt giữa chừng (hạn mức, container khởi động lại) | Mỗi bước một commit; bước nào làm dở thì ghi vào HANDOFF |
| Tốn quota | Bước 3–4 đọc phần đầu tệp, không đọc toàn văn; bước 10 chỉ làm khi thật cần |
