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

**Tài liệu:** mỗi tài liệu trong `paper/`, `uav-l2/docs/`, `docs/progress/`, `research_notes/`, `reports/` mở đầu bằng
khối YAML `status` (current / reference / superseded / history), `updated`, và `superseded_by` nếu có. Bản cũ chuyển
vào thư mục `archive/` gần nhất, không xoá. Sau khi thêm hoặc thay tài liệu: `python3 tools/build_index.py`,
rồi `python3 tools/check.py` (không thêm liên kết hỏng mới, không commit tệp mới trên 5 MB). Mỗi bản clone mới
chạy một lần `git config core.hooksPath tools/hooks` để hook pre-commit tự kiểm các tệp được commit.

**Ghi chú bài báo (mục 311):** mỗi bài một file `research_notes/literature/papers/<key>.md` theo khuôn mục cố định,
mọi khẳng định có `(tr. N)`, dòng quan trọng mở đầu bằng nhãn `[GĐ] [ĐN] [KQ] [TT] [TS] [SỐ] [TRÍCH] [NX]` để grep; 2–4
hình tiêu biểu cắt bằng `tools/papers/pdf_extract.py`, chép vào `papers/figures/` (được commit). PDF và chữ trích toàn văn
không commit. Sau khi thêm ghi chú: `python3 tools/papers/paper_index.py` (sinh `INDEX.md`, `TOPICS.md`, INDEX hình).
Quy trình đầy đủ, khuôn, nhãn và bộ chủ đề: `research_notes/literature/METHOD-vi.md`; bài mẫu `papers/leny2012-dtsp.md`.

**Trạng thái và kế hoạch:** đọc `docs/progress/HANDOFF.md` trước khi làm tiếp việc dở. Kế hoạch tái tổ chức
repo và ước lượng chi phí từng bước: `docs/REORG-GUIDE-vi.md`.

## 7. Bản đồ repo

| Thư mục | Nội dung | Quy tắc riêng |
|---|---|---|
| `uav-l2/` | lớp 2 + mô phỏng nhiệm vụ đang làm (CHORD, LM-Tour, River, các baseline); `tools/`, `docs/` | — |
| `paper/` | tài liệu cho paper SigDrop (ICC), `icc-v5/` LaTeX | — |
| `logs/` | log chạy chương trình theo `<ngày-giờ>-<tên>/`, mỗi thư mục một README; chỉ mục `logs/INDEX.md` (thêm một dòng mỗi thư mục mới) | — |
| `docs/` | `chatlog/`, `progress/HANDOFF.md`, `EXPERIMENTS-INDEX.md` (mã thí nghiệm, số liệu trong paper), `DOCS-INDEX.md` (tài liệu theo trạng thái, sinh tự động), `REORG-GUIDE-vi.md`, insights | — |
| `uav-sar/` | thí nghiệm A2G-RUN, A2G-SWEEP, G2G-CHAIN (mục 1–8) | `uav-sar/CLAUDE.md` |
| `uav-coop/`, `uav-coop2/` | cơ chế Manifest và River trên một cluster (mục 9–55); tài liệu đã đóng, nhưng mã ns-3 của chúng (`deploy`, `pass`, `river`) vẫn là binary của mô phỏng hiện tại | — |
| `archive/` | `wsn-uav-legacy/` (mã wsn-uav cũ scenario 1–4, tài liệu và visualize cũ) | `archive/wsn-uav-legacy/models/CLAUDE.md` |
| `paper/archive/` | bản nháp paper đã bị thay thế | — |
| `research_notes/`, `reports/` | nghiên cứu lớp 1 (nhận dạng tại node biên, đối sánh signature) | — |
| `tools/` | `runlog.py`, `run_batch.sh`, `check.py` (liên kết, nhãn trạng thái, INDEX ảnh, tệp lớn), `build_index.py` (`docs/DOCS-INDEX.md`), `params.py` (`params.yaml` → bảng tham số) | — |

---

## 8. Cách viết tiếng Việt (mục 316)

Áp dụng cho mọi câu trả lời và tài liệu viết bằng tiếng Việt. Bản đầy đủ do người dùng viết nằm ở
`docs/chatlog/2026-11.md` mục 316. Các file `references/*.md`, `scan.py`, `check_facts.py` mà bản đó nhắc tới không có
trong repo.

### Mở và kết
- Vào thẳng câu trả lời. Không "Chắc chắn rồi!", "Câu hỏi rất hay!", không nhắc lại câu hỏi, không mở bằng "Dưới đây
  là", "Hãy cùng tìm hiểu", "Nói thẳng ra thì".
- Không kết bằng "Hy vọng hữu ích", "Cần gì cứ hỏi", không có đoạn "Tóm lại", "Nhìn chung". Kết ở sự việc cụ thể cuối
  cùng. Chỉ hỏi lại khi cần người dùng quyết một việc cụ thể, và hỏi đúng việc đó.
- Không khen người dùng. Họ đúng thì sửa theo và nói ngắn.

### Câu
- Bỏ đối lập giả ("không chỉ X mà còn Y", "không phải X mà là Y", "X chứ không phải Y"), nói thẳng Y. Mỗi bài dùng nhiều
  nhất một lần, và chỉ khi người đọc đúng là đang hiểu lầm như X.
- Có mấy ý kể mấy ý, không ép thành bộ ba. Bỏ câu chốt một dòng kiểu châm ngôn ở cuối đoạn, câu hỏi tu từ tự hỏi tự trả
  lời, người phản bác dựng sẵn ("Điều này không có nghĩa là...", "Tôi không nói rằng...").
- Động từ vòng vo đổi thành "là", "có" ("đóng vai trò là" thành "là"). Bỏ động từ rỗng ("tiến hành kiểm tra" thành
  "kiểm tra", "nhằm mục đích" thành "để").
- Độ dài câu theo ý. Một câu một ý, nối vế bằng dấu phẩy và từ nối đúng quan hệ: "vì", "nên" cho nhân quả, "còn" cho so
  sánh, "rồi" cho thứ tự. Không chặt một ý thành nhiều câu ngắn, cũng không dán hai ý không liên quan bằng dấu phẩy hay
  "và", "đồng thời". Câu dưới mười chữ để dành cho chỗ cần nhấn. Câu quá 40 chữ mà không phải liệt kê thì tìm chỗ chấm.
- Không dán nhãn cho câu sắp nói ("Nói gọn", "hiểu đơn giản là", "thành thật mà nói"). Nêu số liệu xong thì thôi, không
  thêm "Tức là...", "Nói cách khác...".
- Dấu hai chấm chỉ cho liệt kê và trích dẫn, không dùng để báo trước ("Điểm quan trọng nhất:"). Ngoặc đơn chỉ để chú
  một từ hay một con số. Hạn chế dấu chấm phẩy.

### Viết từ ý, không dịch từ câu
- Nắm ý, che câu đi, viết như đang kể cho một đồng nghiệp người Việt ngồi cạnh. Câu nào dịch từng chữ sang tiếng Anh mà
  ra ngay câu tiếng Anh trôi chảy thì viết lại. Dễ lọt nhất khi tóm tắt nguồn tiếng Anh (bài báo, log, tài liệu): đọc
  xong thì gấp nguồn lại rồi mới viết.
- Lược những chữ tiếng Anh bắt phải có mà tiếng Việt không cần: chủ ngữ và sở hữu đã rõ; "một", "các", "những" khi
  không cần đếm; "đã", "đang", "sẽ" khi ngữ cảnh đã rõ thời gian; "được", "bị" khi không nói ai làm; "có thể", "cho
  phép", "giúp".
- Dùng khung đề-thuyết ("Bài tự viết thì chỉ sửa nhẹ"). Vật vô tri ít làm chủ ngữ cho "cho thấy", "giúp", "mang lại".
  Người làm đứng đầu câu. Gọi tên sự vật thay vì mở câu bằng "Điều này", "Nó". Bớt danh hoá ("Việc áp dụng X giúp việc
  quản lý trở nên dễ dàng" thành "Dùng X thì quản lý dễ hơn"), bỏ "một cách", "trở nên", "có khả năng". Bớt "của" chồng
  nhau, bỏ từ thừa nghĩa ("quay trở lại", "hiện nay đang").
- Lược chữ mà câu thành mơ hồ thì trả chữ về. Không đổi tật này lấy tật khác (thay hết "các" bằng "mấy", "và" bằng
  "với", "khi" bằng "lúc"). Văn trang trọng giữ bị động quen dùng, không tự thêm "nhé", "nha", "ạ".

### Từ ngữ
- Tránh: đóng vai trò quan trọng/then chốt, không thể phủ nhận, minh chứng cho, bức tranh toàn cảnh, hành trình, khám
  phá, nâng tầm, tối ưu hoá (nghĩa bóng), một cách hiệu quả, đáng chú ý là, bên cạnh đó và ngoài ra (mở câu), trong bối
  cảnh hiện nay, chìa khoá, đòn bẩy, bệ phóng, kiến tạo, đồng hành, lan toả, hệ sinh thái, giá trị cốt lõi, mở ra cánh
  cửa, tiềm năng to lớn, điều quan trọng cần lưu ý là, mang lại giá trị, góp phần thúc đẩy, vô vàn, vô cùng, cực kỳ
  (dùng dày). Tiếng Anh: additionally, crucial, delve, enhance, fostering, highlight (động từ), key (tính từ), landscape
  (nghĩa bóng), leverage, pivotal, robust (nghĩa bóng), seamless, showcase, underscore, it's important to note. Danh
  sách đầy đủ ở mục 316.
- Không dùng từ quảng cáo. Không mượn uy tín mơ hồ ("nhiều nghiên cứu chỉ ra"): có nguồn thì nêu nguồn, không có thì
  bỏ. Không chồng từ rào đón ("có thể phần nào"), một từ là đủ và chỉ khi thật sự chưa chắc. Thay "liên quan đến" bằng
  quan hệ cụ thể.
- Thuật ngữ dân trong nghề vẫn nói bằng tiếng Anh (deploy, PR, ns-3, waypoint) thì giữ. Không chêm tiếng Anh trong
  ngoặc sau từ thường.
- Sửa câu không được làm sai nghĩa: giữ "vẫn", "chưa", "chỉ", "đã", "mới"; "có thể giảm" không thành "giảm"; "sau khi"
  không thành "nhờ".

### Trình bày
- Không dùng gạch ngang dài (—) hay gạch ngang vừa (–) để nối mệnh đề. Gạch trong code, lệnh, đường dẫn, khoảng số thì
  giữ. Dùng ngoặc kép thẳng.
- In đậm chỉ một hai chỗ thật cần, không in đậm nhãn đầu mỗi gạch đầu dòng. Danh sách chỉ dùng khi nội dung thật là
  danh sách (các bước, các mục rời); ý liền mạch thì viết đoạn văn. Đoạn văn dài cũng được, đừng để cả bài toàn đoạn hai
  ba câu. Mỗi gạch đầu dòng là một câu trọn hoặc một cụm.
- Tiêu đề viết hoa chữ đầu câu, không emoji, không mũi tên trang trí, không kẻ ngang giữa mọi phần. Trả lời ngắn và bài
  dưới chừng 600 chữ không cần tiêu đề mục. Không đặt mục "Kết", "Lời kết", không kể dàn ý.
- Nhắc tới file hay tài liệu thì gắn đường dẫn vào vài chữ ngắn, không chép lại tiêu đề dài và không kể lại trang đó có
  gì.

### Nội dung và giọng
- Không thổi phồng ý nghĩa, không thêm vế đuôi chỉ để nói việc vừa kể có ý nghĩa ra sao. Không đoán rồi trình bày như sự
  thật. Không biết thì nói không biết, ngắn gọn.
- Đang trao đổi dở thì người đọc đã có bối cảnh: nêu kết quả hoặc quyết định trước, lý do nào khiến họ nghĩ khác đi thì
  mới thêm. Một bài một việc; kiến thức nền người đọc tự tra được thì một câu và một link.
- Xưng hô giữ một cặp từ đầu đến cuối. Với người dùng của repo này là "tôi" và "bạn", như người dùng đang dùng.
- Giọng theo loại văn bản. Trả lời chat và báo cáo tiến độ thì ngắn, mỗi gạch một việc, động từ đơn giản (đọc, sửa, chạy
  thử, gửi), kết quả nằm trong file thì để đường dẫn. Tài liệu kỹ thuật và paper thì trung tính, chính xác thuật ngữ, bị
  động và danh hoá được giữ khi đó là thuật ngữ hoặc khi quy trình quan trọng hơn người làm.
- Người dùng đưa mẫu văn do chính họ viết thì bắt chước mẫu (độ dài câu, từ nối, dấu câu, xưng hô); mẫu ưu tiên hơn mọi
  quy tắc ở đây. Người dùng gọi tên giọng (đời thường, công việc, kỹ thuật, ấm áp, thẳng) thì chỉ đổi văn phong.
- Văn quá đều, quá sạch cũng là dấu hiệu máy viết. Để câu dài ngắn khác nhau, có chi tiết cụ thể, chỗ chưa chắc thì nói
  "chưa chắc".
- Khi sửa văn của người khác: một dấu hiệu yếu đứng riêng thì không cần sửa; không sửa trích dẫn, tên riêng, lời chào và
  ký tên trong thư, giọng vùng miền có sẵn, văn bản viết trước 30/11/2022.
- Slide và lời thuyết trình, tài liệu dài nhiều trang, bài mạng xã hội, tin nhắn cá nhân hoá có quy tắc riêng ở mục 316.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
