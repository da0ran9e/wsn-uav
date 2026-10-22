# 2026-10-22 · Báo cáo kỹ thuật lớp 2 kiểu IEEE (CLAUDE.md §8 mục 127)

**Mục đích:** viết một báo cáo kỹ thuật 3–4 trang theo mẫu IEEE (IEEEtran, hai cột) về lớp 2. Báo cáo gồm ý tưởng cốt lõi, các thủ tục với mã giả kiểu ICC/TWC, hình tuyển chọn (kể cả hình cho từng bước) và vài kết quả đáng kể nhất. Nó là nguồn cho 1–2 mục của bài gửi IEEE ICC, nên được viết bằng tiếng Anh như khung bài (`paper/OUTLINE-vi.md`).

**Môi trường:** máy chưa có TeX. Đã cài gói Ubuntu `texlive-latex-base`, `texlive-latex-recommended`, `texlive-publishers` (IEEEtran), `texlive-science` (algorithmicx, siunitx) và `texlive-fonts-recommended`, khoảng 69 MB. Đây là cài đặt hệ thống, không thuộc kho; phiên sau cần cài lại để dựng.

**Lệnh (mỗi bước một tệp .md):**
- `figs.md`: `paper/l2-techreport/make_figs.py` chép các hình đã chọn vào `paper/l2-techreport/figs/`. Hai hình bước MEANDER (mỗi tệp hai ô) được tách thành 8 ô (a)–(h), cắt cùng một khung để cùng tỉ lệ.
- `build-pdf.md`: `paper/l2-techreport/build.sh` chạy make_figs rồi pdflatex hai lần. Bản cuối có 4 trang (phần chữ khoảng 3,6 trang), không còn dòng tràn lề.
  - Lần 1 lỗi vì `\Cap` trùng ký hiệu của amssymb; đã đổi tên.
  - Lần 2 có Bảng II tràn sang cột phải; đã xoay bảng (hàng theo cách chia, cột theo K).

**Đầu vào:** chỉ dùng hình và số đã có, không chạy giả lập mới:
- hình trong `uav-l2/docs/figures/`;
- số trong `uav-l2/docs/{CLUSTER-RIVER,FLIGHTLINE,CURVE,L2-DIAG,SAT}-vi.md` và `paper/L2-PARTITION-vi.md`.

**Đầu ra:** thư mục `paper/l2-techreport/` tự chứa, đưa thẳng lên Overleaf được:
- `l2-techreport.tex` và `l2-techreport.pdf` (khoảng 1,5 MB);
- `figs/` (14 tệp, khoảng 1,8 MB);
- `make_figs.py`, `build.sh`.

**Nội dung:**

| Mục | Nội dung |
|---|---|
| I. Core idea | Trong phát quảng bá một lượt, hình học là lịch phát; ba nguyên tắc P1–P3 |
| II. Model | Miền, UAV, đầu ra của lớp 2, chỉ số D_k, ϱ, T₁, T\* |
| III. CHORD | Alg. 1; Hình 1 |
| IV. MEANDER | Alg. 2, Alg. 3 (BEND); Hình 2 (8 bước), Hình 3 |
| V. Results | Bảng I (57 miền cong), Hình 4; bão hoà, Hình 5; cấp nhiệm vụ, Bảng II, Hình 6 |
| VI. Discussion | Điều đứng vững, điều chưa; MEANDER‑K; phần nào dùng cho bài ICC |

**Kết quả được báo cáo trung thực:** MEANDER phủ River tốt hơn hẳn (83–90 % so với 55–57 %). Nhưng ở cấp nhiệm vụ nó vẫn thua k‑medoids + CHORD 48–97 s, và chỉ thắng tối đa 2/10 bản đồ mỗi cỡ. Phép so sánh công bằng (MEANDER‑K) vẫn đang chờ duyệt.

**Dang dở:**
- Hình 5 và 6 không có chữ (quy tắc mục 63), nên trục không có nhãn. Bản nộp ICC cần vẽ lại có nhãn trục.
- Số liệu là số thăm dò (N < 120).
