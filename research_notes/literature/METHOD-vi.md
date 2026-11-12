---
status: current
updated: 2026-11-12
---
# Phương pháp ghi chú bài báo

Mục tiêu: khi cần một định nghĩa, định lý, tham số hay con số của một bài, chỉ cần tìm trong ghi chú (grep hoặc mở
danh mục) mà không phải mở lại PDF. Quy tắc này do người dùng đặt ở chatlog mục 311. Ba bài mẫu:
`papers/leny2012-dtsp.md`, `papers/zeng2018-multicast.md`, `papers/isaacs2011-dtspn.md`.

## 1. Nguyên tắc

1. **Một bài một file**, cùng một khuôn mục cố định (mục 4). Nhờ vậy grep theo tên mục hoặc theo nhãn dòng luôn cho kết
   quả cùng dạng.
2. **Mọi khẳng định lấy từ bài đều có trang** dạng `(tr. N)`, trong đó N là số trang trong file PDF (trang 1 là trang
   đầu file). Số hiệu định lý, phương trình, hình giữ đúng như trong bài (Định lý 2, (24), Fig. 4).
3. **Tách nội dung của bài khỏi nhận xét của người ghi.** Nhận xét, so sánh với SigDrop và suy luận riêng luôn mang nhãn
   `[NX]` hoặc nằm trong mục "Liên hệ SigDrop".
4. **Ghi đủ để dùng lại:** phát biểu định lý kèm điều kiện, công thức kèm ý nghĩa ký hiệu, tham số kèm đơn vị, con số
   kèm điều kiện thí nghiệm (bao nhiêu nút, kịch bản nào, hình hay bảng nào).
5. **Viết tiếng Việt, giữ thuật ngữ gốc** khi chưa có từ thống nhất (DTSP, GTSP, RLNC, waypoint). Công thức viết bằng
   ký hiệu thường hoặc `$...$`.
6. **Không bịa.** Phần nào không trích được chữ (trang ảnh quét, công thức vỡ) thì ghi rõ "không đọc được ở tr. N".

## 2. Thư mục

| Đường dẫn | Nội dung | Commit |
|---|---|---|
| `research_notes/literature/papers/<key>.md` | ghi chú một bài | có |
| `research_notes/literature/papers/figures/<key>-figN.png` | hình chọn dùng trong ghi chú; `INDEX.md` sinh tự động | có (quyết định mục 311) |
| `research_notes/literature/papers/INDEX.md`, `TOPICS.md` | danh mục bài và chủ đề → bài, sinh tự động | có |
| scratchpad `…/papers/<key>/` | `pages.txt`, `meta.txt`, `fig/` do `pdf_extract.py` tạo | **không** |
| PDF gốc | thư mục Drive của người dùng, tải về scratchpad | **không** |

**Khoá bài** `<key>`: họ tác giả đầu (chữ thường, bỏ dấu, bỏ khoảng trắng) + năm + `-` + một từ khoá, ví dụ
`leny2012-dtsp`, `zeng2018-multicast`. Nếu trùng, thêm từ khoá khác.

## 3. Quy trình cho mỗi bài

```bash
# 0. Một lần mỗi session: tải PDF từ thư mục Drive (link chia sẻ công khai) về scratchpad
python3 tools/papers/drive_fetch.py "<link thư mục Drive>" <scratchpad>/pdf
# 1. Trích chữ theo trang, metadata (DOI qua Crossref) và cắt mọi hình
python3 tools/runlog.py logs/<ngày-giờ>-paper-notes/extract.md \
  "python3 tools/papers/pdf_extract.py <scratchpad>/pdf/<file>.pdf <key> <scratchpad>/papers"
# 2. Đọc <scratchpad>/papers/<key>/pages.txt (đọc kỹ phần phát biểu, chứng minh, thiết lập thí nghiệm)
# 3. Xem các hình trong <scratchpad>/papers/<key>/fig/, chọn 2–4 hình tiêu biểu, chép vào papers/figures/
# 4. Viết papers/<key>.md theo khuôn mục 4
# 5. Cập nhật danh mục, rồi kiểm tra repo
python3 tools/papers/paper_index.py && python3 tools/build_index.py && python3 tools/check.py
```

Khi nhiều phiên chạy song song: mỗi phiên chỉ viết file `papers/<key>.md` và hình của bài mình. Phiên chính chạy
`paper_index.py` một lần ở cuối, để không xung đột ở `INDEX.md` và `TOPICS.md`.

## 4. Khuôn ghi chú

```markdown
---
status: reference
updated: YYYY-MM-DD
key: leny2012-dtsp
doi: 10.1109/TAC.2011.2166311
title: On the Dubins Traveling Salesman Problem
authors: J. Le Ny, E. Feron, E. Frazzoli
venue: IEEE TAC 57(1):265–270
year: 2012
file: leny2012.pdf (Drive); tr. 1 = trang 265
topics: dtsp, np-hard, approx-bound
relevance: ★★★
read: full | partial | abstract
---
# Le Ny, Feron, Frazzoli 2012 · On the Dubins traveling salesman problem

## Tóm tắt một dòng
<một câu: bài làm gì, kết quả chính>

## Vì sao đọc
<một hai câu: bài trả lời câu hỏi nào của SigDrop>

## Bài toán và mô hình
- **[GĐ]** giả định ... (tr. N)

## Định nghĩa và ký hiệu
| Ký hiệu | Nghĩa |

## Kết quả chính
- **[KQ] Định lý 2** (tr. 2). Phát biểu ... *Ý chứng minh:* ...

## Thuật toán
- **[TT] Tên** (tr. N). Đầu vào ... Các bước ... Độ phức tạp ...

## Thực nghiệm và số liệu
- **[TS]** thiết lập ... (Bảng II, tr. 8)
- **[SỐ]** con số ... (Fig. 7, tr. 10)

## Hình tiêu biểu
![<mô tả tiếng Việt> (Fig. N, tr. M)](figures/<key>-figN.png)
*Đọc hình:* ...

## Trích nguyên văn
- **[TRÍCH]** "..." (tr. N)

## Liên hệ SigDrop
- **[NX]** ... nhãn [L1] [A] [B] [C] [D] [FC] [TOUR] [ĐV] [KÊNH] [GIÓ]

## Hạn chế và câu hỏi mở
- ...
```

Không bỏ mục nào; mục không có nội dung ghi "Không có". Mục "Tóm tắt một dòng" được `paper_index.py` đưa vào danh mục,
nên viết gọn trong một dòng.

## 5. Nhãn dòng

Mỗi gạch đầu dòng quan trọng mở đầu bằng một nhãn in đậm để grep được trên toàn bộ ghi chú:

| Nhãn | Nghĩa | Ví dụ grep |
|---|---|---|
| `[GĐ]` | giả định của mô hình | `grep -n "\[GĐ\]" papers/*.md` |
| `[ĐN]` | định nghĩa quan trọng ngoài bảng ký hiệu | |
| `[KQ]` | định lý, bổ đề, mệnh đề, hệ quả, cận | `grep -n "\[KQ\].*NP" papers/*.md` |
| `[TT]` | thuật toán, quy trình | |
| `[TS]` | tham số, thiết lập thí nghiệm | `grep -n "\[TS\].*Rician" papers/*.md` |
| `[SỐ]` | con số kết quả kèm điều kiện | `grep -n "\[SỐ\]" papers/*.md` |
| `[TRÍCH]` | trích nguyên văn ngắn (≤ 2 câu) để dẫn trong bài viết | |
| `[NX]` | nhận xét, suy luận của người ghi | |

Nhãn chỗ dùng trong SigDrop (đặt trong mục "Liên hệ SigDrop"): `[L1]` bổ đề độ khó, `[A]` định lý crossover, `[B]`
takeover, `[C]` giá trị thông tin của kế hoạch, `[D]` cận min-cut, `[FC]` baseline fountain code, `[TOUR]` CHORD và
LM-Tour, `[ĐV]` định vị đóng góp, `[KÊNH]` mô hình kênh, `[GIÓ]` lệch quỹ đạo.

## 6. Chủ đề (từ vựng cố định)

Trường `topics` chỉ dùng các mã dưới đây; `paper_index.py` cảnh báo mã lạ. Thêm mã mới thì thêm vào bảng này trước.

| Mã | Mô tả |
|---|---|
| `dtsp` | Dubins TSP và biến thể |
| `dtspn` | Dubins TSP với lân cận |
| `np-hard` | kết quả về độ khó |
| `approx-bound` | hệ số xấp xỉ, cận trên và cận dưới của tour |
| `tsp-solver` | bộ giải TSP, biến đổi GTSP sang ATSP |
| `orienteering` | orienteering, giới hạn quãng bay |
| `uav-multicast` | UAV phát dữ liệu chung xuống mặt đất |
| `uav-collection` | UAV thu dữ liệu từ mặt đất |
| `uav-coverage` | phủ vùng, đặt vị trí UAV làm trạm gốc |
| `ground-coop` | hợp tác mặt đất sau khi UAV phát (D2D, chuyển tiếp) |
| `dissemination` | phổ biến dữ liệu và mã trong WSN |
| `coding` | fountain code, RLNC, network coding |
| `a2g-channel` | kênh không–đất |
| `trajectory-error` | lệch quỹ đạo, gió, bám đường |
| `control-overhead` | chi phí điều khiển, giới hạn thông tin giao thức |
| `min-cut` | lát cắt, max-flow, cận dưới thời gian phổ biến |
| `multi-uav` | nhiều UAV |
| `wsn-gathering` | gom dữ liệu trong WSN |
| `testbed` | thực nghiệm phần cứng, testbed |
| `sar` | bối cảnh tìm kiếm cứu nạn, thảm hoạ |

## 7. Mức liên quan và độ sâu đọc

- `relevance`: ★★★ dùng trực tiếp cho J1 (định lý, baseline, định vị); ★★ nền hoặc công cụ; ★ chỉ để biết.
- `read`: `full` (đọc toàn văn, kể cả chứng minh chính), `partial` (bỏ qua phụ lục hoặc phần không liên quan, ghi rõ
  phần bỏ qua), `abstract` (chỉ abstract, mở đầu, kết luận). Bài ★★★ phải `full`.

## 8. Hình

- Chọn 2–4 hình: sơ đồ hệ thống, minh hoạ ý chứng minh, kết quả chính. Không chép mọi hình.
- Chú thích bằng tiếng Việt, kèm số hình và trang gốc; luôn có một dòng "*Đọc hình:*" nói hình cho thấy gì.
- Hình trích từ bài có chữ, là ngoại lệ của quy tắc "ảnh không chữ" (mục 63), vì đây không phải hình do repo sinh ra.
- `pdf_extract.py` cắt theo vị trí chú thích. Kiểm tra bằng mắt trước khi chép; nếu cắt hụt thì bỏ, không chép hình hỏng.

## 9. Bản quyền

PDF và chữ trích toàn văn không bao giờ được commit. Hình trích được commit theo quyết định của người dùng (mục 311),
dù repo đang public; chỉ commit những hình mà ghi chú dùng, và luôn ghi nguồn (DOI ở front matter, số hình và trang ở
chú thích). Trích nguyên văn giữ ngắn (≤ 2 câu mỗi chỗ).

## 10. Kiểm tra trước khi commit

- [ ] Front matter đủ trường; `topics` thuộc bảng mục 6; DOI đã đối chiếu (Crossref hoặc trang đầu bài).
- [ ] Mỗi `[KQ]`, `[SỐ]`, `[TS]`, `[TRÍCH]` có `(tr. N)`.
- [ ] Phát biểu định lý có đủ điều kiện; ký hiệu đã có trong bảng.
- [ ] Nhận xét riêng đều mang `[NX]`.
- [ ] Hình hiển thị đúng, có "Đọc hình".
- [ ] Đã chạy `paper_index.py`, `build_index.py`, `check.py` không lỗi mới.
