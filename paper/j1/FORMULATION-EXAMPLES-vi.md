---
status: current
updated: 2026-11-26
---
# J1 · Mẫu phát biểu bài toán từ các bài tiêu biểu (chatlog mục 400)

Đọc phần phát biểu bài toán của bảy bài có cách viết quen thuộc, để học cách viết (P0), (P1), (P2) ở
[PROBLEMS-vi.md](PROBLEMS-vi.md). Nhãn nguồn:
- **[repo]**: lấy từ ghi chú đã có trong repo;
- **[web]**: đọc trực tiếp bản arXiv, chưa ghi chú vào repo.

Số phương trình giữ như trong bài gốc.

## 1. Bảy bài và điều học được

| Bài | Phát biểu | Học cho |
|---|---|---|
| Zeng, Xu, Zhang 2018, UAV multicast, TWC [repo `zeng2018-multicast`] | (P1) min T sao cho mọi trạm giải được file với xác suất ≥ P̄ = 0,9 | (P1): mục tiêu phân vị viết thành ràng buộc xác suất |
| Wu, Zeng, Zhang 2018, nhiều UAV, TWC, arXiv 1705.02723 [web] | (15) max η trên ba khối biến A, Q, P | (P1): bố cục chuẩn |
| Zhan, Zeng, Zhang 2018, gom dữ liệu WSN, WCL, arXiv 1708.00221 [web] | (P1) min θ, sáu nhóm ràng buộc | (P1): ràng buộc "một máy phát mỗi khe"; độ tin cậy qua xác suất mất gói |
| Gong, Chang, Shen, Chen 2018, thời gian bay nhỏ nhất, arXiv 1801.02799 [web] | (8) min tổng thời gian bay; biến là khoảng thu và tốc độ | (P1) và (P2): cố định thứ tự rồi giải bằng quy hoạch động |
| Bakker, Guastaroba, Nickel, Speranza 2025, SSCFLP, arXiv 2512.08576 [web] | mô hình nhị phân chuẩn (1)–(6) của facility location có sức chứa, một nguồn | (P0) |
| You, Yuan, Tang, Chen 2013, lập lịch phát quảng bá trễ nhỏ nhất (MLBS), arXiv 1304.5330 [web] | bản quyết định: có lịch không va chạm dài ≤ T không | (P1) phần mặt đất: độ khó và chặn dưới |
| Hermans, Leus, Matuschke 2019, expanding search, arXiv 1911.08959 [web] | c(σ) = Σ_v p_v·λ(v, σ), (1) | (P2) |

### Zeng 2018 [repo]
- **Phát biểu.** (P1) ở phương trình (12): tối thiểu thời gian nhiệm vụ T, ràng buộc mỗi trạm mặt đất giải được file với xác suất
  ≥ P̄, và bài chọn P̄ = 0,9.
- **Đưa về dạng tất định.** Ràng buộc xác suất được thay bằng một chặn dưới (Định lý 1) cộng xấp xỉ Gauss, ra điều kiện tất định
  "thời gian kết nối trong bán kính D ≥ T_min".
- **Đưa về bài đã biết.** Định lý 2 chứng minh quỹ đạo chỉ cần gồm các đoạn thẳng. Nhờ vậy bài thành chọn waypoint, gần bài TSP
  với lân cận.
- **Học cho (P1).** Phân vị 0,9 của T viết được thành ràng buộc xác suất:
  $Q_{0.9}[T]=\min\{\theta:\Pr\{T\le\theta\}\ge0.9\}$.
  Vì vậy (P1) và cả mục tiêu chung đều viết được giống (P1) của Zeng: min θ, s.t. Pr{max_k C_k ≤ θ} ≥ 0,9. Cách đưa về tất định
  cũng dùng được: chặn dưới xác suất nhận trong một bán kính.

### Wu, Zeng, Zhang 2018 [web]
- **Bố cục.** Khuôn quen thuộc nhất của mảng tối ưu UAV:
  - rời rạc thời gian thành N khe, biện minh độ dài khe bằng (7);
  - gom biến thành ba khối A (lập lịch và gán, nhị phân), Q (quỹ đạo), P (công suất);
  - câu "our goal is to maximize the minimum average rate … by jointly optimizing A, Q, P";
  - bài (15): max η với η là biến phụ cho max-min (epigraph);
  - chín dòng ràng buộc (15b)–(15i), mỗi dòng có lượng từ ∀.
- **Đoạn "vì sao khó".** Ngay sau bài là đoạn nêu hai lý do: biến nhị phân và ràng buộc không lồi. Tiếp theo là nới lỏng (16) rồi
  chia khối: với Q, P cố định thì phần A là LP (17); với A, P cố định thì phần Q giải bằng tối ưu lồi kế tiếp.
- **Học cho (P1).**
  - Đặt ba khối biến: Q (quỹ đạo), S (lịch phát), F (luồng mặt đất).
  - Dùng biến phụ θ cho makespan.
  - Viết đoạn vì sao khó, rồi chia khối giống cách mình đang tách quỹ đạo với River.
  - Phần "với Q cố định thì A là LP" ứng đúng với "với q cố định thì F nới lỏng thành LP tải lớn nhất".

### Zhan, Zeng, Zhang 2018 [web]
- **Phát biểu.** Bài thư ngắn, (P1) chỉ sáu nhóm ràng buộc:
  - (5) $\sum_m x_k[m]E_k\le\theta$: năng lượng mỗi node không quá θ;
  - (6) $\sum_m x_k[m]R_k[m]\ge r_k$: đủ dữ liệu;
  - (7) $\sum_k x_k[m]\le1$: mỗi khe chỉ một node phát;
  - (8): biến nhị phân;
  - (9), (10): tốc độ, điểm đầu và điểm cuối.
- **Độ tin cậy.** Không nằm trong mục tiêu: tốc độ $R_k[m]$ chọn sao cho xác suất mất gói bằng ε, qua $F^{-1}(\epsilon)$ ở (4).
- **Học cho (P1).**
  - (7) là đúng dạng ràng buộc "mỗi môi trường một máy phát mỗi khe" của mình.
  - Đưa độ tin cậy vào tham số kênh là cách nhẹ hơn ràng buộc xác suất, dùng được khi lập kế hoạch trên bản đồ nhận dự báo.

### Gong và cộng sự 2018 [web]
- **Phát biểu.** (8): tối thiểu tổng thời gian bay. Biến là khoảng thu của từng cảm biến, xếp theo thứ tự
  $S_0\le x_1\le y_1\le\dots\le y_N\le S_{N+1}$ ở (8b), cùng tốc độ và công suất.
- **Đưa về bài đã biết.** Nhận xét 1: khi đã biết thứ tự thăm, bài 2D giống bài trên đường thẳng, rồi đưa về quy hoạch động.
- **Học.**
  - (P1): khi thứ tự cụm π đã cố định, tốc độ dọc đường và lịch phát có cấu trúc tuyến tính.
  - (P2): với ít cell nghi vấn, quy hoạch động trên thứ tự cho nghiệm đúng.

### SSCFLP, Bakker và cộng sự 2025 [web]
- **Phát biểu.** Mô hình nhị phân chuẩn:
  - mục tiêu $\min\sum_i f_iy_i+\sum_{i,j}d_jc_{ij}x_{ij}$;
  - mỗi khách đúng một điểm: $\sum_i x_{ij}=1$;
  - sức chứa: $\sum_j d_jx_{ij}\le q_iy_i$;
  - bất đẳng thức thừa $x_{ij}\le y_i$, thêm vào để LP nới lỏng chặt hơn.
- **Độ khó.** Bài ghi rõ: khi tập điểm mở đã cố định, việc gán khách là bài gán tổng quát (GAP), tự nó đã NP-khó.
- **Học cho (P0).**
  - Viết (P0) đúng theo khuôn này, thêm hai dòng: giới hạn chặng và ràng buộc nghẽn trên môi trường.
  - Độ khó suy ra bằng cách thu hẹp về SSCFLP hoặc GAP.
  - Giữ dòng $x_{uv}\le y_v$ dù thừa, vì nó làm LP chặt hơn.

### You và cộng sự 2013 [web]
- **Phát biểu.**
  - Giả định gọn: thời gian chia khe, nhận không lỗi nếu không va chạm.
  - Bài viết ở dạng quyết định: "cho G và T, có cách gán khe và kênh để lịch không va chạm và dài ≤ T không".
  - Độ khó chứng minh bằng thu hẹp: chỉ một kênh thì ra đúng bài MLBS đã biết là NP-khó.
  - Chặn dưới hiển nhiên: độ sâu của cây đường đi ngắn nhất.
- **Học cho (P1) phần mặt đất.**
  - Cho q cố định, chỉ một gói và chỉ một cell giữ gói lúc đầu, phần F của mình gần với MLBS, nên có thể chứng minh NP-khó bằng
    thu hẹp thay vì dựng phép quy mới. Cần kiểm mô hình va chạm có khớp không: MLBS dùng va chạm theo đồ thị đĩa đơn vị, còn mình dùng
    môi trường (cell, cặp gateway) một máy phát mỗi khe.
  - Chặn kiểu "độ sâu" ứng với chặn một radio của mình.

### Hermans, Leus, Matuschke 2019 [web]
- **Phát biểu.**
  - Đồ thị có gốc r, xác suất $p_v$ ở đỉnh, độ dài $\lambda_e$ ở cạnh.
  - Chi phí tìm là quãng đường kỳ vọng trước khi thấy mục tiêu: $c(\sigma)=\sum_v p_v\lambda(v,\sigma)$, (1).
  - Bài tách rõ hai kiểu: tìm theo đường đi (pathwise) là bài độ trễ nhỏ nhất có trọng số đỉnh, NP-khó (Trummel và Weisinger
    1986; NP-khó cả trên cây theo Sitters 2002); tìm mở rộng (expanding) đi tiếp từ mọi đỉnh đã thăm.
- **Thuật toán.** Tham lam theo "mật độ tìm" (khối xác suất chia độ dài) đạt hệ số xấp xỉ 8 ở bản expanding.
- **Học cho (P2).**
  - Định nghĩa T\* của pha 2 bằng một công thức như (1), với λ là thời gian bay cộng thời gian xác minh.
  - Bản phân vị: $\min\theta$ s.t. $\sum_{v:\lambda(v,\sigma)\le\theta}p_v\ge0.9$.
  - Đội 2 bay như pathwise (phải bay lại từ chỗ đang đứng), nên độ khó dẫn theo Trummel và Weisinger và Sitters.
  - Quy tắc tham lam xác suất chia thời gian của mình là phiên bản pathwise của "mật độ tìm".

## 2. Khuôn chung rút ra

Các bài trên viết phần phát biểu theo cùng một trình tự:
1. Gom biến thành vài khối có tên (A, Q, P hoặc x, y), nói mỗi khối nghĩa là gì.
2. Một câu mục tiêu: "our goal is to … by jointly optimizing …".
3. Viết bài có nhãn (P1). Mục tiêu min-max hay max-min dùng biến phụ θ hoặc η. Mỗi nhóm ràng buộc một dòng có ∀ và có số, và trong
   chữ có một câu nói nghĩa của nó.
4. Độ tin cậy đưa vào bằng ràng buộc xác suất (Zeng: P̄ = 0,9) hoặc bằng tham số kênh (Zhan: ε).
5. Một đoạn nói vì sao khó (biến nguyên, không lồi, hoặc NP-khó bằng thu hẹp về bài đã biết).
6. Tách thành bài con, mỗi bài con nhận ra được là LP, bài lồi, TSP hoặc quy hoạch động.

## 3. Áp vào ba bài của J1

| Bài | Theo mẫu | Viết thế nào |
|---|---|---|
| (P0) | SSCFLP (Bakker 2025) | mô hình nhị phân (1)–(6), thêm dòng chặng và dòng nghẽn; NP-khó qua SSCFLP hoặc GAP |
| (P1) | Zeng 2018 cho mục tiêu, Wu 2018 và Zhan 2018 cho bố cục | min θ s.t. Pr{max_k C_k ≤ θ} ≥ 0,9; ba khối Q, S, F; ràng buộc môi trường như (7) của Zhan; NP-khó qua Định lý 1 (phần bay), phần mặt đất thử thu hẹp về MLBS (You 2013); với q cố định thì F nới lỏng thành LP |
| (P2) | Hermans 2019 | T\* = t₂ + Σ (bay + 78 s) tới cell thật, viết như (1); bản kỳ vọng là bài độ trễ nhỏ nhất có trọng số, bản phân vị là ràng buộc khối xác suất ≥ 0,9 |

Nếu viết mục tiêu chung thành min θ s.t. Pr{T\* ≤ θ} ≥ 0,9, thì cả ba bài dùng cùng một dạng, và câu còn mở "phân vị lấy qua
những gì" thành câu hỏi Pr lấy theo những biến ngẫu nhiên nào.

## 4. Tài liệu nên ghi chú

Bốn bài nên thêm ghi chú theo `research_notes/literature/METHOD-vi.md`, vì sát (P1) và (P2) nhất:
- Wu, Zeng, Zhang 2018 (arXiv 1705.02723);
- Zhan, Zeng, Zhang 2018 (arXiv 1708.00221);
- Hermans, Leus, Matuschke 2019 (arXiv 1911.08959);
- You và cộng sự 2013 (arXiv 1304.5330).

Bài SSCFLP 2025 chỉ cần dẫn mô hình chuẩn; nguồn kinh điển của mô hình này là Holmberg, Rönnqvist, Yuan 1999 (EJOR), chưa đọc.

Bản dịch phần phát biểu bài toán của bảy bài, kèm tóm tắt hoàn cảnh, ở repo private `da0ran9e/sigdrop-fulltext`, file
`translations/PROBLEM-SECTIONS-vi.md` (chatlog mục 407). File để ở repo private vì là bản dịch gần nguyên văn.
