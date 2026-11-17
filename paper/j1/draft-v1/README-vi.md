---
status: current
updated: 2026-11-17
---
# Bản thảo journal v1 (J1): hướng dẫn đánh giá

Thư mục này chứa toàn bộ việc "nâng bản ICC lên bản journal dự kiến" theo yêu cầu ở `REQUEST-vi.md`. Bản thảo viết bằng
tiếng Anh, khuôn IEEEtran, 12 trang: `tex/main.pdf`. Đây là bản để cùng đánh giá, chưa phải bản nộp. Số đo trong PDF lấy từ
các chiến dịch đã có. Lượt ns-3 mới duy nhất là thử thuật toán vận chuyển mặt đất mới (mục 9 bên dưới), chưa đưa vào PDF.

## Cấu trúc thư mục

| Đường dẫn | Nội dung |
|---|---|
| `tex/` | mã LaTeX (`main.tex` và 7 file mục), `build.sh`, `main.pdf` |
| `figs/` | hình có nhãn trục cho bài (PDF, PNG), bảng số `.md` và `.csv` do script sinh, hình chép từ repo |
| `analysis/` | script Python của các phép tính mới |
| `runs/` | log từng lần chạy script (lệnh và kết quả), ghi bằng `tools/runlog.py` |
| `REQUEST-vi.md` | hai tin nhắn yêu cầu của người dùng, nguyên văn |

Dựng lại PDF: `paper/j1/draft-v1/tex/build.sh`.

## Phần mới so với bản ICC v5

1. **Phát biểu bài toán (P0) và Định lý 1 (NP-khó)**, mục IV và Phụ lục A. Chứng minh đi theo khuôn Le Ny 2012: quy từ
   Exact Cover qua phép dựng của Papadimitriou, phóng to để hấp thụ cả phần phạt bán kính quay lẫn bán kính nhận. Chứng
   minh xử lý trực tiếp trường hợp có lân cận (đĩa nhận bán kính ξ), không cần viện dẫn DTSP-N.
2. **Giới hạn của mọi phương án không hợp tác**, mục V. Đây là kết quả lý thuyết chính, mới hoàn toàn.
   - Định lý 2 (chặn phủ): T ≥ (1 − δ)·Q·T_p·Λ\*, với Λ\* là nghiệm một bài quy hoạch tuyến tính trên vùng nhận của các
     critical cell. Chặn đúng với mọi quỹ đạo, mọi mã, và không cần giả định A1 giữa các gói.
   - Mệnh đề 1 (chặn xếp có tính quãng bay) và hai hệ quả: điều kiện đủ để hợp tác thắng, và vùng cấm bay.
   - Số trên ba bản đồ C4: Λ\* tăng từ 4–7 (open) lên 35–76 (r100). Ở R50 ≤ 200 m, chặn dưới vượt thời điểm LM-Tour bay
     xong cả tour trên cả ba bản đồ. Ở k8, r100, critical cell cuối của CHORD + River xong lúc 746 s, còn chặn là 1 283 s.
   - Vùng cấm bay bán kính 700 m trên k8: chặn nhảy từ 842 lên 3 431 s ở r200, và vô hạn ở r100.
3. **Chặn dưới một radio cho lớp mặt đất** (Mệnh đề 2) và khoảng cách đo được: River chậm hơn chặn khoảng 5 lần (trung
   vị), kéo trực tiếp 5,0 lần, Deluge 7,3–7,6 lần, trên 225 lần hoàn tất của thí nghiệm DLG.
4. **Takeover đưa vào bài** (mục VI-C, VIII-E): thuật toán nhìn từ node, Mệnh đề 3 về xác suất kích hoạt (dự đoán
   2,0 / 18,2 / 51,7, đo 3 / 17 / 48), và bảng gió.
5. **Thuật toán mới: bán kính hỏi thích nghi cho takeover.** Bán kính h = ⌈ê/(√3·R)⌉ + 1, với ê ước lượng từ toạ độ trong
   header các gói mà SPINE cell và cell kề nghe được, kèm bước nới thêm một vòng nếu còn thiếu. Đánh giá ngoại tuyến
   trên bitmap thật của các lượt bay gió (Bảng II của bài): tới 9/9 và 41/42 người giữ ở lần hỏi đầu, lan ít cell hơn
   bán kính cố định nhỏ nhất đủ dùng. Chưa chạy trong ns-3.
6. **So sánh với Deluge và kéo trực tiếp** (mục VIII-D), viết theo đúng phân tích ở chatlog mục 304: phần hơn không đến
   từ frame điều khiển mà từ dữ liệu dư và từ việc lập kế hoạch; kéo trực tiếp có kế hoạch ngang River ở r100.
7. **Số C4 thay cho số ước lượng** của bản v5: LM-Tour giờ là số đo ns-3, có khoảng tin cậy theo seed.
8. **Tổng quan tài liệu viết lại** theo đợt tìm tài liệu ngày 12/11 và các ghi chú bài báo.
9. **Thuật toán mới cho lớp mặt đất, đã chạy ns-3 (một seed).** Trace từng hop của River (seed 1, cụm 1) cho thấy nút cổ
   chai nằm ở cell Bank và cell trung chuyển dọc dải River (bận 0,72–0,98), còn môi trường của critical cell chỉ bận
   0,18–0,79. Hai cơ chế mới:
   - Cây dùng chung (`--tree` trong `uav-coop2/examples/coop2-river.cc`): các đường Bank → thành viên Ring của cùng một
     đoạn SPINE ghép thành cây, mỗi gói đi qua một nhánh chung một lần, yêu cầu gom ở các nút rẽ nhánh.
   - Lập kế hoạch cân tải (`uav-coop2/tools/river_lb.py`): chọn lại Bank (một trong hai Bank của SPINE cell) và đường
     cell cho từng luồng Bank → thành viên, cực tiểu hoá tổng (tải + Δ)^6, tức một hàm xấp xỉ tải lớn nhất. Mô hình tải
     khớp với trace (R² 0,89): 1,7 frame mỗi gói ở cell trung chuyển, 1,5 ở Bank và thành viên, 1 ở mỗi cặp gateway.
     Tuỳ chọn `--members` chọn lại cả thành viên Ring nhận đoạn, `--lp` giải nới lỏng tuyến tính để có chặn dưới của tải
     lớn nhất (cụm 1 và 4: lời giải cách chặn 0–5 %). Chỉ thay dòng CIRC của kế hoạch, chạy trên cùng binary.

   Kết quả trên 8 cụm, seed 1 của DLG (k8, r100, cùng pass và cùng chỉ số mission với River gốc), `figs/lb-seed1.md`:

   | Biến thể | doneS trung bình | critical cell cuối mỗi cụm | frame | xong cuối nhiệm vụ (từ cất cánh) |
   |---|---|---|---|---|
   | River gốc | 101,2 s | 125,7 s | — | 770 s |
   | Cây dùng chung | −16 % | −22 % | −23 % | 693 s |
   | Cân tải | −18 % | −24 % | 0 % | 707 s |
   | Cân tải + cây dùng chung | −26 % | −31 % | −24 % | 703 s |

   Cả 45/45 critical cell đều xong ở mọi biến thể. Hệ số so với chặn một radio giảm từ 5,1 xuống 4,1 (trung vị). Cụm
   chậm nhất (cụm 8) giảm từ 248 s xuống 80 s. Đây mới là một seed; chưa chạy 4 seed còn lại, chưa thử `--members`.

## Nguồn của từng nhóm số

| Nhóm số trong bài | Loại | Nguồn |
|---|---|---|
| Bảng III, Hình 7 (T\*) | đo ns-3, C4 | `uav-l2/docs/data/results/campaign4.csv` → `analysis/fig_tstar.py` → `figs/tstar-c4.*` |
| Bảng IV (thời gian bay, thời điểm xong trung bình), độ dài tour, số liệu pass | đo ns-3, C4 | `paper/TECHREPORT-vi.md` §3.2–3.4 |
| Bảng I, Hình 2 (Λ\*, hai chặn dưới), vùng cấm bay | tính mới | `analysis/bound_lp.py`, `bound_nc.py` → `figs/bound-lp.*`, `bound-nc.*` |
| Hình 4, hệ số 5,1 / 5,0 / 7,3–7,6, mốc 746 s | tính mới trên số đo DLG | `analysis/ground_lb.py` → `figs/ground-lb.*` |
| Công thức (8), MAE 22,8 s, R² 0,60 | đo ns-3, LMT | `paper/TECHREPORT-vi.md` §5.4 |
| Bảng V (River, Deluge), năng lượng | đo ns-3, DLG | `logs/2026-10-30_1545-deluge-r100/table.md`, `README.md` |
| Bảng VI (gió), takeover tuần tự | đo ns-3, WND và TKO | `paper/SIM-REPORT-2026-11-01-takeover-vi.md`, `logs/2026-11-01_0600-takeover/compare-seq.md` |
| Mệnh đề 3, Hình 5 | tính trên bitmap ns-3 | `logs/2026-11-10_1400-nd1-day5/`, `analysis/fig_propb.py` |
| Bảng II (bán kính hỏi) | tính mới trên bitmap ns-3 | `analysis/takeover_radius.py` → `figs/takeover-radius.md` |
| Khớp kênh (S = −101,04 dBm, RMSE ≤ 0,003) | tính trên lượt bay ns-3 | `logs/2026-11-10_1000-nd1-week1/day2-channel.md` |
| River so với kéo trực tiếp trên một cụm (26 %, 12 %, 20–22 %) | mang từ bản ICC | `paper/RIVER-L3-vi.md` §5 |

## Đính chính so với việc đã làm trước

- **Phép kiểm định lý A ở tuần 1 tính sai T_River.** `uav-l2/tools/theory/theorem_a.py` cộng `team1` với `riverReady`,
  trong khi `riverReady` đã là thời điểm tính từ lúc cất cánh (trung bình qua critical cell). Vì vậy T_River trong
  `paper/j1/MODEL-vi.md` mục 6.2 bị thổi phồng (ví dụ 1 236 s thay vì khoảng 750–780 s ở k8, r100), và các "tỉ số đo" ở
  đó thấp hơn thật. Bản thảo này không dùng các tỉ số ấy; định lý A cũ được thay bằng Định lý 2 và Hệ quả 1.
- Bài ghi rõ FC + DTSP-N được chấm ở mức mô hình (mã lý tưởng, nhận theo kỳ vọng), không phải lượt bay ns-3 mức gói.

## Chỗ còn TODO trong bài (in đỏ trong PDF)

- Tác giả, đơn vị; trích bản ICC.
- Hình kênh (Hình 1) còn là bản không nhãn trục.
- Nguồn datasheet cho mô hình năng lượng CC2420.
- Bài Wang et al. 2020 (IoT-J) mới trích theo abstract, chưa có tên viết tắt tác giả đầu và chưa đọc toàn văn.
- Bốn thí nghiệm chưa chạy: River với vùng cấm bay; kênh có tương quan; mô hình gió theo động lực bay; baseline Deluge có
  low-power listening và baseline kiểu Typhoon.

## Điểm cần cùng đánh giá

1. **Định lý 2 có đủ sức làm đóng góp lý thuyết chính không.** Nó chặt cho máy phát treo tại chỗ, còn lỏng 2,4–4,6 lần
   so với baseline đo được. Nó chỉ chứng nhận được lợi thế ở R50 ≤ 200 m.
2. **Chưa có chặn trên cho River.** Bài nói thẳng điều này ở mục IX. Hệ số 5 lần so với chặn một radio là điểm yếu
   phản biện sẽ hỏi.
3. **Cây dùng chung và lập kế hoạch cân tải** (mục 9) đã chạy ns-3 trên một seed: nhanh hơn River gốc 26 % (trung bình)
   và 31 % (critical cell cuối mỗi cụm). Đoạn Discussion trong PDF còn quy khoảng cách 5 lần cho luồng trùng lặp; trace
   cho thấy nguyên nhân chính là tải dồn vào Bank và cell trung chuyển, cần sửa lại. Muốn đưa vào bài thì chạy đủ 5 seed
   (khoảng 1,5 giờ cho 120 lượt, 4 nhân) bằng `analysis/run_lb.sh`, rồi `analysis/lb_compare.py`.
4. **Bối cảnh vườn quốc gia, nhiều UAV, AI node** (`paper/j1/CONTEXT-vi.md`) chưa được đưa vào bản thảo, vì chưa chốt và
   chưa có số liệu. Bản thảo giữ kịch bản của bản ICC.
5. Tên bài giữ như bản ICC.
