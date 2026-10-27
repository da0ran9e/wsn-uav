# Handoff · 2026-10-22 (cập nhật 2026-10-27)

## Cập nhật 2026-10-27 (CLAUDE.md §8 mục 186–187)

**Định hướng mới của người dùng:**
- CHORD chỉ còn là nền lý thuyết; LM-Tour phải tốt hơn nó đáng kể.
- Khung evaluation mới (mục 187): CHORD + River (đề xuất 1), LM-Tour + River (đề xuất 2), FC + DTSP-N (toàn hệ thống), DTSP-N + River (lợi ích của River so với FC + DTSP-N), rotary TSP (mốc trên), Oracle (mốc dưới).
- Bỏ khỏi khung: FC + gather, B4 (một lượt, không hợp tác) và kéo trực tiếp.
- "CHORD" từ nay là **CHORD thường**: dây cung dài nhất qua CH, chọn riêng từng cụm, không `--chordTour`.

**Môi trường chạy trên máy macOS của người dùng:**
- Repo: `~/Github/ns-3-dev-git-ns-3.46/src/wsn-uav`.
- ns-3 dựng riêng ở `~/Github/ns3-uav-build/ns3`; binary trong `~/Github/ns3-uav-build/BIN`; venv Python 3.10 ở `~/Github/ns3-uav-build/.venv`.
- Thư mục chạy: `~/Github/ns3-uav-build/runs`.
- Kiểm chứng: River chạy lại CHORD-T giống hệt bản cloud CAMP-BIN4 ở 32/32 cụm.

**Mục 186 (`logs/2026-10-27_1330-chord-plain-vs-lm/`):**
- LM-Tour cũ (uốn từ dây cung của CHORD) chỉ hơn CHORD thường 0–10 s, nằm trong nhiễu.
- Uốn đường không giảm được lượng gói cả cụm còn thiếu.

**Mục 187: LM-Tour viết lại (`lm_tour.py plan --dtspn --weight cl --wmin 1`, Algorithm 3 dòng 6–14):**
1. DTSP-N qua các đĩa B(CH, ξ): mỗi cụm một đường thẳng qua CH (6 hướng). Không có độ dài tối thiểu; đường ngắn thì bay chậm hoặc lượn cho đủ một bản truy vấn. Hướng, chiều và thứ tự cụm được chọn chung (`chord_tour.choose`).
2. Uốn tham lam về các critical cell có trọng số ≥ trung bình (điểm CL chia trung bình bản đồ), CH ghim, mỗi cụm qua một lần, tới khi J_k có trọng số thôi giảm.

**Baseline DTSP-N + River (`--dtspnRiver`):**
- Đường thẳng qua trọng tâm các critical cell của cụm, uốn vào đĩa của mọi critical cell (zigzag, không tự cắt, không ghim CH), cùng cách chọn tour.
- `pass-bin` đòi đường bay qua CH, nên dùng `prefly.py` (node giả chỉ nhận, đặt trên đường bay, cắt khỏi bitmap). Không sửa ns-3.

**Kết quả ns-3, k8-s1, 100 lượt bốc ghép cặp (`logs/2026-10-27_1800-lm-dtspn/`, T\* s):**

| kênh | CHORD | LM-Tour | DTSP-N + River | LM − CHORD |
|---|---|---|---|---|
| open | 672 | 633 | 678 | −38 ± 31 |
| r500 | 802 | 719 | 814 | −83 ± 38 |
| r200 | 877 | 792 | 861 | −84 ± 35 |
| r100 | 892 | 802 | 880 | −90 ± 38 |

- LM-Tour thắng rõ ở cả bốn kênh. DTSP-N + River hoà CHORD.
- Phần lợi đến chủ yếu từ tour DTSP-N: đội 1 bay 698 s so với 784 s. Bước uốn thêm 7–22 s.
- Trọng số chưa ảnh hưởng gì tới T\*, vì c\* trong mô hình lớp 1 không phụ thuộc điểm CL.
- Đây là số thăm dò.

**Việc tiếp theo:**
1. Chạy k12, k16 (bản đồ trong `uav-l2/docs/data/results/raw/`), mất khoảng 3–4 giờ.
2. Viết lại `paper/EXPERIMENTS-vi.md` §5 và `paper/icc-v5/evaluation-v5.tex` theo khung mới.
3. Cập nhật `paper/LMTOUR-vi.md` và Algorithm 3.

---

## Cập nhật tối 2026-10-22 (phiên tiếp quản, CLAUDE.md §8 mục 130–136)

- **Container mới không có cây ns-3.** Dựng lại: `bash logs/2026-10-22_1732-env-setup/setup.sh` (khoảng 3 phút), rồi `pip install --break-system-packages matplotlib markdown pymupdf`. Binary đóng băng chép vào scratchpad `BIN/` (`deploy-bin` đã có `--chCells`; bản cũ `deploy-bin-v0`, cho đầu ra giống từng byte khi không dùng tùy chọn đó).
- **Quy tắc mới:** lưu ảnh (mục 131), commit cả ảnh tạm, ảnh không chữ, `INDEX.md` trong mỗi `figures/`.
- **Chốt propose lớp 2 (mục 135–136):** báo cáo `uav-l2/docs/PROPOSE-ITER-vi.md`; SWATH-K: `uav-l2/docs/SWATH-vi.md`; log `logs/2026-10-22_1947-swath-validate/`. Kết quả chính trên 16 bản đồ ghép cặp: **CHORD-T** (giữ cụm k-medoids, chọn hướng đường bay qua CH cùng thứ tự tour, `mission.py --chordTour 0.6,0.8`) nhanh hơn k-medoids 29 s trên 16/16 bản đồ (CLUE 70 %: 38 s; bão hoà); SWATH-K không hơn trung bình. Với CHORD-T, lợi của hợp tác là +50 s so với +19 s. Cấu hình P\* đề xuất: `--windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour 0.6,0.8`, phương án `P+prog-kin-puq-stage-zero-redir`. CLUE chờ người dùng chốt.
- **Bẫy mới:** `l1_rank.py` sinh thế giới ngẫu nhiên theo tên thư mục; muốn so ghép cặp thì thư mục làm việc phải mang đúng tên bản đồ (`SET/k8-s10`), không thêm tiền tố.
- **Sửa mô hình mới (tùy chọn, mặc định tắt để tái tạo số cũ):** `--critRing domain`, `--axeNear`, `--windowAt crit`. Cấu hình đang dùng để chốt propose bật cả ba.
- **Lớp 3 dưới CHORD-T (16 bản đồ, kiểm tra sơ bộ):** kéo thẳng cho cùng T\* với River (+0,5 s, River tốt hơn 9/16), nhưng River ít hơn 11 % khung và critical cell cuối có cửa sổ sớm hơn 2 s (64/80 cụm). Không hợp tác chậm hơn 49,8 s (15/16). Bài báo nên đặt lợi của River vào chi phí mạng và thời gian xong, không vào T\* (`PROPOSE-ITER-vi.md` §3.4). Độ nhạy D = 64 / 256: CHORD-T vẫn −30 / −29 s.
- **23-10: CLUE chốt 80 % (mục 138). Baseline đã cài (mục 139):** B8 cánh bằng bay vòng, B5 quét luống (Python, `l1_rank.py`), Trickle (`coop2-river.cc --scheme=trickle`, binary scratchpad `BIN2/`), cùng subCH-K và MEANDER-K với cấu hình P\*. Bảng nhanh 16 bản đồ: `logs/2026-10-23_0706-baselines/README.md`, `table-all.md`. P\* 585 s; kéo thẳng và Trickle cùng T\* (Trickle 4,7 lần khung); không hợp tác +50 s; subCH-K +15 s (baseline mạnh nhất); MEANDER-K +64 s; B5 +112 s; B8 +368 s; cánh quay +900 s trở lên.
- **Chưa chạy:** chiến dịch (người dùng chưa chốt N).

---

- **Nhánh:** `claude/document-review-xslwgg` (repo `da0ran9e/wsn-uav`). Commit cuối trước bản này: `11bce58`. Cây làm việc sạch.
- **Vị trí:** gốc repo này chính là `src/wsn-uav/` trong cây ns-3. Cây ns-3 nằm ở `/home/user/ns3-dev`. Trong `ns3-dev/src/`, ba thư mục `uav-coop`, `uav-coop2`, `uav-sar` là symlink về repo. `uav-l2` không phải module ns-3; nó là công cụ Python gọi các binary ns-3.
- **Đọc theo thứ tự khi vào phiên mới:**
  1. `CLAUDE.md` §8: lời gốc của người dùng, mục 1–129. Lời mới hơn thắng lời cũ.
  2. Bản này.
  3. `paper/OVERVIEW-vi.md`: tổng quan toàn bộ nghiên cứu, bản đang chốt cho paper.
  4. Trước khi động vào `uav-sar/`, đọc `uav-sar/docs/STATUS.md` (CLAUDE.md §6).

---

## 1. Mục tiêu đang làm

**Mục tiêu chung:** một bài IEEE ICC (viết bằng tiếng Anh). Đề tài: giao truy vấn tìm kiếm tới mạng camera IoT bằng một lượt bay của UAV cánh bằng, rồi hợp tác mặt đất có lập kế hoạch để lấp phần dữ liệu còn thiếu.
- Pha 1 gồm ba lớp:
  - lớp 1: nhận dạng tại critical cell (mô hình điểm cosine);
  - lớp 2: đường bay và chia cluster;
  - **lớp 3: River, đóng góp chính.**
- Khung bài: `paper/OUTLINE-vi.md`.

**Giai đoạn hiện tại:** viết tài liệu nguồn cho paper. Thực nghiệm đang tạm dừng, chờ người dùng duyệt các chiến dịch tiếp theo (mục 3). Phiên 22-10 chỉ làm tài liệu, không chạy ns-3 mới.

---

## 2. Đã xong

### 2.1 Theo lớp

| Lớp | Đã có | Tài liệu chính |
|---|---|---|
| 3 · River | Thuật toán 1–4, 2b, 3b, 4b (lập kế hoạch) và G, 5–7, D, S (thực thi). ns-3 với MAC 802.15.4 đầy đủ, lưới kênh 7 màu, gateway kênh riêng. Có các biến thể: Circle chuẩn bị sẵn, Circle khi được hỏi, Circle động, kéo thẳng; cửa sổ quanh CH hoặc theo từng critical cell | `paper/RIVER-L3-vi.md` (rút gọn); `paper/L3-TECHREPORT-vi.md` + `paper/techreport/L3-TECHREPORT-vi.pdf` (32 trang) |
| 2 · Đường bay, cluster | CHORD: đường thẳng dài nhất qua CH. MEANDER: luồng trắc địa và đường cong uốn qua CH. Đã có chẩn đoán, các bản chỉnh, động học Dubins và chiến dịch bão hoà theo hình dạng cụm | `paper/L2-PARTITION-vi.md`; `paper/l2-techreport/` (IEEE, 4 trang); `uav-l2/docs/{FLIGHTLINE,CURVE,L2-DIAG,SAT}-vi.md` |
| 1 · Nhận dạng | Mô hình điểm tổng quát: độ nhận diện r_j và độ quan trọng w_j cho mỗi manh mối, đối sánh hai bước. Đã cài vào giả lập nhiệm vụ | `paper/L1-MODEL-vi.md`; `uav-l2/docs/L1-MISSION2-vi.md` |
| Nhiệm vụ | 40 bản đồ (2/4/6/8 cluster), P\*, các baseline B1–B7, subCH, 100 lượt bốc mỗi bản đồ | `paper/BASELINES-vi.md`; `uav-l2/docs/MISSION-vi.md` |

**Số chính đang dùng.** Đây là số thăm dò, chưa đủ để công bố.
- **River so với kéo thẳng:** từ 4 critical cell trở lên, River ít hơn 20–22 % khung và nhanh hơn ở 19–20/20 lượt. Riêng C3: River xong sau 37,2 s với 89,7 k khung; kéo thẳng 50,3 s với 102,2 k khung.
- **Hợp tác:** rút T\* 26–68 s so với không hợp tác, trên 39/40 bản đồ.
- **Lớp 2:** MEANDER phủ River 83–90 %, so với 55–57 % của k‑medoids + CHORD. Nhưng ở cấp nhiệm vụ MEANDER **vẫn thua** k‑medoids + CHORD 48–97 s (bản đã chỉnh, nối Dubins).
- **Điểm tối ưu bão hoà:** luồng rộng 8–10 cell, cụm dài 2–3 km (110–190 cell), dùng cửa sổ theo từng critical cell.

### 2.2 Phiên 2026-10-22 (CLAUDE.md §8 mục 122–128)

| Mục | Việc | Commit |
|---|---|---|
| 122 | Tài liệu chi tiết lớp 3, kèm hình và mã giả | `3d10736` |
| 123 | Tài liệu nhanh lớp 2 (MEANDER từng bước) | `c5f601a` |
| 124 | Rút gọn hai tài liệu trên, chỉ giữ cơ chế | `94ac1a6` |
| 125–126 | Báo cáo kỹ thuật lớp 3: PDF 32 trang, 26 hình (6 hình từng bước mới vẽ từ trace ns‑3 C3, 7 ảnh chụp trình phát) | `297b9f7` |
| 127 | Báo cáo kỹ thuật lớp 2 theo mẫu IEEEtran, 4 trang, tiếng Anh: CHORD, MEANDER, BEND dạng `algorithmic` | `26b4837` |
| 128 | Commit báo cáo `/insights` vào `docs/insights/` | `11bce58` |

---

## 3. Đang dở, chờ duyệt

Theo quy tắc hiện hành: phải bàn với người dùng trước mọi lần chạy tốn thời gian.

1. **So sánh lớp 2 cho công bằng (mục 118).** Các so sánh hiện có lệch: MEANDER có nhiều cluster hơn và cỡ không đều (hệ số biến thiên 0,16–0,21, so với 0,06–0,11 của k‑medoids). Đề xuất:
   - **MEANDER‑K:** nối các luồng thành một chuỗi luống bay qua hồ, rồi cắt thành đúng K đoạn bằng nhau.
   - **subCH‑K:** tách K/2 cluster lớn thành K cluster con.
   - Kiểm tra trước bằng hình học (`--geometry`): đúng K cluster, hệ số biến thiên ≤ 0,11. Sau đó mới chạy ns‑3, khoảng 1,5–2 giờ cho mỗi cách chia. Chi tiết: `uav-l2/docs/L2-DIAG-vi.md` §7.
2. **Chạy lại nhiệm vụ trên 40 bản đồ với cửa sổ theo từng critical cell** cho cả k‑medoids lẫn MEANDER‑K. Đặt MEANDER‑K ở điểm tối ưu (luồng khoảng 8 cell). Xem `uav-l2/docs/SAT-vi.md` §6.
3. **N ≥ 120 cho mọi số đưa vào bài.** Hiện tất cả là một lượt ns‑3 cho mỗi cluster trên 40 bản đồ. Các chỗ đánh dấu **[cần chạy]** trong `paper/OUTLINE-vi.md`.
4. **Hình cho bản nộp ICC.** Hình 5 và 6 của báo cáo lớp 2 không có nhãn trục, theo quy tắc mục 63. Bản nộp cần vẽ lại có nhãn.
5. **Bản trang web của báo cáo kỹ thuật lớp 3** chưa dựng. `paper/overview-page/build.py` chưa hiểu cú pháp `{fig:…}`, chú thích bảng `: tab:…` và hình nhiều ảnh của `paper/techreport/build.py`.
6. **Tham số chưa có nguồn đầy đủ:**
   - trích dẫn Qiu 2017 (số mũ A2G);
   - thời gian phát LoRa 0,4 s (cần tính lại theo Semtech);
   - K = 2 của fading Rician;
   - khối fading 100 ms của G2G.

   Xem `uav-l2/docs/PARAM-SOURCES-vi.md` và `paper/OVERVIEW-vi.md` §11.2.
7. **Câu hỏi nghiên cứu phụ, chưa cài:** ghép Circle khi hai critical cell kề nhau; bề rộng River tối ưu; SWATH (một đường luống liền).

---

## 4. Lỗi và bẫy đã gặp

### Môi trường (container dùng một lần)
- **Container thiếu TeX.** Dựng báo cáo lớp 2 cần cài lại ở mỗi container mới, khoảng 69 MB:
  `apt-get install --no-install-recommends -y texlive-latex-base texlive-latex-recommended texlive-publishers texlive-science texlive-fonts-recommended`.
  Không có `latexmk`, `pdftoppm`, `pandoc`.
- **Playwright** không tìm thấy trình duyệt mặc định. Luôn dùng `executable_path='/opt/pw-browsers/chromium'`.
- **Xem trang PDF thành ảnh:** cài `pip install pymupdf` rồi dùng `import pymupdf`.
- **Dữ liệu trong scratchpad mất khi container bị thu hồi.** Ví dụ:
  - `BIN/` (symlink tới binary ns‑3);
  - trace C3 `c3trace/`, bitmap lượt phát `l2dep/pass3b-bits-r1.bin`;
  - các thư mục làm việc của chiến dịch.

  Những thứ cần giữ đã được commit vào `uav-l2/docs/data/`. Phần còn lại phải tạo lại theo lệnh ghi trong log.
- **Lệnh `rm` dùng biến shell** (ví dụ `rm -f $S/*.png`) bị kiểm tra an toàn chặn. Dùng `"${S:?}"/…` hoặc đường dẫn tuyệt đối.
- **Không dùng `pkill -f`** với mẫu khớp cả chính lệnh của mình, vì nó tự giết lệnh đó.

### Dựng tài liệu
- `\Cap` trùng ký hiệu của `amssymb`, nên báo cáo lớp 2 dùng `\CapC`.
- Bảng nhiều cột trong IEEEtran hai cột dễ tràn lề. Nên xoay bảng: hàng theo cách chia, cột theo K.
- PDF qua Chromium: ngắt trang trước mọi `h2` để lại nhiều khoảng trắng (37 trang so với 32). Hiện chỉ ngắt trước phụ lục.
- Python‑Markdown cần một dòng trống trước danh sách nằm ngay dưới đoạn văn; cả hai `build.py` đã tự chèn. Công thức `$$…$$` trong mục danh sách làm hỏng trang, nên viết inline.
- Trình phát visualize (`uav-l2/docs/anim/*-replay.html`) giữ trạng thái trong closure, không với tới từ ngoài được. `uav-l2/tools/anim_shots.py` nạp một bản sao có móc `__seek`, không sửa tệp gốc.
- Ảnh người dùng gửi có thể là **bản cũ** của hình trong kho. Ví dụ `concept-banks.png` và `concept-axe-banks.png` cũ có từ trước commit `666c959`. So pixel với kho trước khi dùng.
- **Hình gửi cho người dùng không có chữ (mục 63).** Hệ quả là hình cho paper thiếu nhãn trục.

### Mô phỏng và phương pháp
- Quy tắc của dự án:
  - N ≥ 120 mới được công bố; không tin một seed;
  - không biên dịch lại giữa chiến dịch (dùng binary đóng băng trong `BIN/`);
  - mỗi lần sửa bằng script phải có assert.
- **Cửa sổ quanh CH bão hoà khi cụm dài trên khoảng 2 km.** Ví dụ dải 10 × 4 km: River chạy 25 phút mới mô phỏng được 80 s. Cửa sổ theo từng critical cell gỡ được giới hạn này.
- **Lỗi đã sửa trong `uav-coop2/examples/coop2-river.cc`:** tham chiếu treo tới `jobs[j].done` sau khi vector cấp phát lại, làm crash ở C2. Nay `done` được truyền theo giá trị.
- **Lỗi đã sửa trong `river_plan.load`:** độ rộng cell được đo bằng một cặp cell kề bất kỳ, vì lưới có thể không chứa gốc toạ độ.
- **Bẫy ns‑3 lr-wpan:** helper phải sống suốt mô phỏng, gọi `SetReceiveCallback` một lần, payload ≤ 100 B. Xem CLAUDE.md §7.
- **Tránh kết luận quá tay.** Phủ River tốt hơn không có nghĩa là nhiệm vụ nhanh hơn, vì tour và số cluster chi phối T\*. Ở `uav-sar`, hợp tác không mua được lợi thế chi phí (CLAUDE.md §6).

### Quy tắc làm việc (người dùng đặt)
- Trả lời bằng tiếng Việt. Thêm nguyên văn mỗi lời người dùng vào cuối CLAUDE.md §8.
- Mọi lần chạy chương trình đều ghi log bằng `tools/runlog.py` vào `logs/<YYYY-MM-DD_HHMM>-<tên>/`, kèm `README.md` khi xong.
- Bàn kế hoạch trước khi chạy việc tốn thời gian.
- Trong phiên này, mỗi thay đổi đều được commit và push lên nhánh trên. Stop hook đòi cây làm việc sạch.
- CLAUDE.md §7 ghi "không commit nếu chưa được yêu cầu". Quy tắc đó viết cho bố cục `src/wsn-uav` cũ.

---

## 5. File đã sửa (phiên 2026-10-22)

| File | Vì sao |
|---|---|
| `CLAUDE.md` | Thêm mục 122–129 vào §8 |
| `paper/RIVER-L3-vi.md`, `paper/L2-PARTITION-vi.md` | Tài liệu lớp 3 và lớp 2, rồi rút gọn (mục 122–124) |
| `paper/overview-page/build.py`, `template.html` | Dựng trang web cho nhiều tài liệu (`--doc overview\|river-l3\|l2`) |
| `paper/L3-TECHREPORT-vi.md`, `paper/techreport/{build.py, report.css, L3-TECHREPORT-vi.pdf}` | Báo cáo kỹ thuật lớp 3 và công cụ dựng PDF A4 |
| `paper/l2-techreport/{l2-techreport.tex, .pdf, make_figs.py, build.sh, figs/}` | Báo cáo IEEE lớp 2; thư mục tự chứa, đưa lên Overleaf được |
| `uav-l2/tools/l3_report_figs.py` | Hình từng bước của thuật toán 1–4, G, 5–7 trên C3 |
| `uav-l2/tools/anim_shots.py` | Chụp khung tĩnh từ trình phát visualize |
| `uav-l2/tools/{window_figure, pass_strips_figure, meander}.py`, `uav-coop2/tools/river_sweep_figure.py` | Hình cho tài liệu mục 122–123 |
| `uav-l2/docs/figures/{tr-l3-*, tr-shot-*, river-window, river-pass-strips, meander-k6-s3-b220-w1-step-*}.png`, `uav-coop2/docs/figures/ns3-sweeps-plain.png` | Hình mới, không chữ |
| `docs/insights/report-2026-10-22-164730.html` | Báo cáo `/insights` |
| `logs/2026-10-22_{0502-river-l3-doc, 0518-l2-doc, 0549-docs-short, 0928-l3-techreport, 1006-l2-techreport}/` | Log từng lệnh và README |
| `docs/progress/HANDOFF.md` | Bản này |

---

## 6. Lệnh build/test và kết quả gần nhất

Dự án không có bộ unit test. Việc kiểm tra gồm hai cách:
- dựng lại rồi xem từng trang hoặc từng hình;
- với ns‑3, so từng byte đầu ra trước và sau khi sửa.

```bash
# ns-3 (uav-coop, uav-coop2, uav-sar là symlink trong ns3-dev/src)
cd /home/user/ns3-dev && cmake --build cmake-cache -j 3
#   binary: build/src/uav-coop/examples/ns3.46-uav-coop-{deploy,pass}-optimized
#           build/src/uav-coop2/examples/ns3.46-uav-coop2-river-optimized
#   gần nhất: uav-coop2-river biên dịch lại 2026-10-21 18:12 (thêm bản ghi NEED, cửa sổ theo critical cell).
#   Không có NEED thì đầu ra giống từng byte bản cũ (đã kiểm trên dải 6 × 2 km).

# binary đóng băng cho chiến dịch (symlink, thư mục scratchpad)
mkdir -p BIN && ln -s /home/user/ns3-dev/build/src/uav-coop/examples/ns3.46-uav-coop-deploy-optimized BIN/deploy-bin \
  && ln -s /home/user/ns3-dev/build/src/uav-coop/examples/ns3.46-uav-coop-pass-optimized BIN/pass-bin \
  && ln -s /home/user/ns3-dev/build/src/uav-coop2/examples/ns3.46-uav-coop2-river-optimized BIN/river-bin \
  && ln -s /home/user/ns3-dev/build/lib BIN/lib

# một nhiệm vụ (cwd uav-l2); dải bão hoà
python3 tools/mission.py --clusters 4 --seed 4 --work WORK --bin BIN --jobs 3
python3 tools/sat_strip.py ...      # xem logs/2026-10-21_1738-saturation/sweep.sh

# luôn chạy qua runlog
python3 tools/runlog.py logs/<YYYY-MM-DD_HHMM>-<tên>/<bước>.md "<lệnh>" --cwd <thư mục>

# tài liệu
python3 paper/overview-page/build.py . <out> --doc overview|river-l3|l2       # trang web
python3 paper/techreport/build.py paper/L3-TECHREPORT-vi.md <out>             # PDF lớp 3
sh paper/l2-techreport/build.sh                                               # PDF IEEE lớp 2
```

**Kết quả gần nhất:**

| Việc | Khi | Kết quả |
|---|---|---|
| Chiến dịch bão hoà: 75 dải, W 3–10 × L 1,5–6 km × 3 seed | 2026-10-21 19:10–21:38 | 75/75 thoát 0. Thêm dải thử 14 × 4 km: critical cell cuối xong sau 67 s |
| MEANDER đã chỉnh, 40 bản đồ ns‑3 | 2026-10-21 | 40/40 xong. T\* (nối Dubins) 479/634/770/921 s, so với 420/586/716/824 s của k‑medoids |
| PDF lớp 3 (`techreport/build.py`) | 2026-10-22 | 26 hình, 9 bảng, 32 trang; đã xem lại mọi trang |
| PDF lớp 2 (`l2-techreport/build.sh`) | 2026-10-22 | 4 trang. Không có overfull; chỉ còn 2 underfull ở khối tác giả |
| Trang web `overview` | 2026-10-22 | Dựng lại giống từng byte |

---

## 7. Bước tiếp theo

1. Hỏi người dùng có duyệt hai việc ở mục 3 không: MEANDER‑K / subCH‑K (bước 1), rồi chạy lại nhiệm vụ với cửa sổ theo critical cell (bước 2). Nếu được duyệt:
   - kiểm tra hình học trước (vài phút);
   - đóng băng binary rồi chạy ns‑3 (khoảng 1,5–2 giờ mỗi cách chia, có log);
   - cập nhật Bảng II và mục Discussion trong `paper/l2-techreport/l2-techreport.tex`.
2. Lập kế hoạch chiến dịch N ≥ 120 cho các số chính của bài (River so với kéo thẳng; hợp tác; T\* so với baseline), rồi bàn với người dùng trước khi chạy.
3. Chuẩn bị hình cho bản nộp ICC, có nhãn trục. Hình cho người dùng xem vẫn giữ bản không chữ.
4. Nếu người dùng cần: dựng bản trang web cho báo cáo kỹ thuật lớp 3; bổ sung nguồn cho các tham số ở mục 3.6.
5. Viết tiếp các mục của bài ICC từ hai báo cáo kỹ thuật (`paper/OUTLINE-vi.md`).
