---
status: reference
updated: 2026-11-26
---
# J1 · Tổng hợp kết quả hai nhánh (chatlog mục 396)

> Phiên bản đô thị (urban-v1), đóng gói ngày 2026-11-26 khi bài chuyển sang kịch bản rừng và khu bảo tồn (chatlog mục 408). Xem [README](README.md).

Gom kết quả đã có của nhánh lý thuyết và bối cảnh (CONTEXT, L1-VARIABLES) và nhánh kỹ thuật (bản thảo `draft-v1`, chiến dịch C4,
K9, thử thuật toán mặt đất mới) tính tới 2026-11-23. Dàn ý bài đi kèm ở [OUTLINE-vi.md](OUTLINE-vi.md).

Nhãn độ tin cậy ở cuối mỗi dòng:
- **[ns-3 n seed]**: đo trên ns-3 với n seed;
- **[mô hình]**: tính bằng surrogate hoặc mô hình tải;
- **[tính]**: phép tính giải tích hoặc hình học;
- **[tra cứu]**: số lấy từ nguồn ngoài.

Bản đồ C4 (k8, k12, k15 hay k16) là bản đồ tổng hợp. Chưa có lượt ns-3 nào chạy trên bản đồ đô thị thật.

## 1. Đã chốt về bài toán

| Mục | Quyết định | Nguồn |
|---|---|---|
| Kịch bản | tìm người trong một quận đô thị hiện đại có nhà cao tầng; tiên nghiệm đều, không biết nơi thấy lần cuối | CONTEXT mục 1, 32; chatlog 384 |
| Hệ thống | một UAV cánh bằng VTOL ở pha 1 (100 m, 25–50 m/s), một UAV cánh quay ở pha 2 (V1, 78 s mỗi lần xác minh); trạm gốc ở đội cứu nạn | CONTEXT mục 17, 22 |
| Mạng | lưới cell lục giác R = 100 m, mật độ chính 816 node/km²; node pin không chuyển tiếp; cột đèn chuyển tiếp ở cell cần | CONTEXT-SUMMARY mục 3 |
| Dữ liệu | truy vấn ảnh khoảng 400 KB (Q = 4 041 gói); node thường gửi vector hoặc ảnh cắt về AI node theo phương án lai | CONTEXT mục 27–29 |
| Mục tiêu chung | tối thiểu phân vị 0,9 của T\* (lúc xác nhận đúng người), báo kèm trung bình; có cơ chế vá cell bị sót | CONTEXT mục 33 |
| Cấu trúc bài toán | pha 0 và pha 1 giải riêng; phần mặt đất (luồng) nằm trong bài tối ưu pha 1; pha 2 cũng tối ưu (đang tìm hiểu) | L1-VARIABLES mục 6–8 |

Còn chờ quyết (L1-VARIABLES mục 8): phân vị 0,9 lấy qua phần ngẫu nhiên hay qua cả vị trí người; thước đo của pha 2; pha 1 tối ưu
riêng hay chọn cùng pha 2; chính sách cập nhật pha 0; giấy phép bay thường trực.

## 2. Vì sao cần UAV và giới hạn của cách không hợp tác

- Gửi truy vấn 400 KB qua LoRa SF7 tới mọi CH mất ít nhất 1,8 h ở chu kỳ 10 % và 17,9 h ở 1 %. **[tính]** (CONTEXT mục 12)
- Gửi qua mạng mặt đất từ trạm gốc phải đi 50–95 chặng. Giao thức CSMA mất 20 phút tới hơn một giờ. Flood đồng bộ kiểu Pando mất
  1,2–2,4 phút nếu giữ được tốc độ ở độ sâu đó, nhưng chưa có số đo ở độ sâu này. **[tính]** (CONTEXT mục 12)
- Định lý 1: bài thiết kế chung quỹ đạo và lịch mặt đất (P0 trong bản thảo) là NP-khó, kể cả khi chỉ có một UAV tốc độ không đổi,
  nhận tất định và không có cạnh mặt đất. **[tính]** (bản thảo mục IV)
- Định lý 2 (chặn phủ) cho mọi phương án không hợp tác: T ≥ (1 − δ)·Q·T_p·Λ\*. **[tính]** (bản thảo mục V, `figs/bound-lp.md`)
  - Λ\* bằng 4–7 ở kênh mở và 35–76 ở r100.
  - Ở R50 ≤ 200 m, chặn này vượt lúc LM-Tour bay xong cả tour trên cả ba bản đồ.
  - Ở k8, r100: critical cell cuối của CHORD + River xong lúc 746 s, còn chặn là 1 283 s.
- Thêm vùng cấm bay bán kính 700 m trên k8 thì chặn tăng từ 842 lên 3 431 s ở r200, và thành vô hạn ở r100. **[tính]**
- Truy vấn nhỏ (Q = 400 và 1 000) thì chặn không hợp tác chỉ còn 150–320 s, nên lý thuyết không còn chứng nhận được lợi thế của hợp
  tác. **[tính]** (`figs-q/`, CONTEXT mục 27)

## 3. Thời gian nhiệm vụ trên bản đồ C4

Nguồn: bản thảo Bảng III và IV. Điều kiện: ns-3, 6–10 seed, mỗi seed 100 lượt rút ghép cặp.

- LM-Tour + River nhanh nhất ở mọi cấu hình. **[ns-3 6–10 seed]**
- So với FC + DTSP-N, LM-Tour + River nhanh hơn 10–14 % ở R50 = 1 016 m, 31–38 % ở 498 m và 59–72 % ở 199 m và 99 m. **[ns-3 6–10 seed]**
- So với không có pha phát (UAV cánh quay đi TSP), toàn bộ kiến trúc một lượt bay nhanh hơn 3,5–5,8 lần. **[ns-3 6–10 seed]**
- Riêng phần River (DTSP-N + River so với FC + DTSP-N): nhanh hơn 14–23 % ở 498 m, 49–63 % ở 199 m và 99 m. Ở kênh mở thì không
  nhanh hơn (−3 tới +9 %). **[ns-3 6–10 seed]**
- LM-Tour so với các cách bay khác. **[ns-3 6–10 seed]**
  - Nhanh hơn DTSP-N + River 10–26 %.
  - Nhanh hơn CHORD 1–11 %, với đường bay ngắn hơn 14–28 %; khác biệt có ý nghĩa ở 10/12 cấu hình.
- Ví dụ T\* trung bình của LM-Tour + River ở r100 là 806 / 1 054 / 1 262 s trên bản đồ 8 / 12 / 15 cụm. **[ns-3 6–10 seed]**
- Công thức dự báo thời gian mặt đất cho người lập đường bay có MAE 22,8 s, R² 0,60. Kênh khớp với ns-3 với S = −101,04 dBm,
  RMSE ≤ 0,003. **[ns-3]**

## 4. Lớp mặt đất

- Chặn dưới một radio (Mệnh đề 2), so trên 225 lần hoàn tất của thí nghiệm DLG: River chậm hơn chặn khoảng 5,1 lần (trung vị), kéo
  trực tiếp 5,0 lần, Deluge 7,3–7,6 lần. **[ns-3 + tính]**
- Trace từng hop của River cho thấy nút cổ chai nằm ở cell Bank và cell trung chuyển (bận 0,72–0,98), còn critical cell chỉ bận
  0,18–0,79. **[ns-3 1 seed]**
- Thuật toán mới thử trên DLG k8, r100, seed 1, 8 cụm (`draft-v1/figs/lb-seed1.md`). **[ns-3 1 seed]**

  | Biến thể | doneS trung bình | critical cell cuối mỗi cụm | frame | xong cuối nhiệm vụ |
  |---|---|---|---|---|
  | River gốc | 101,2 s | 125,7 s | — | 770 s |
  | cây dùng chung | −16 % | −22 % | −23 % | 693 s |
  | cân tải | −18 % | −24 % | 0 % | 707 s |
  | cân tải + cây dùng chung | −26 % | −31 % | −24 % | 703 s |

  - Cả 45/45 critical cell đều xong.
  - Hệ số so với chặn một radio giảm từ 5,1 xuống 4,1.
  - Cụm chậm nhất giảm từ 248 s xuống 80 s.
- Nới lỏng LP của tải lớn nhất cho cụm 1 và 4: lời giải cân tải cách chặn LP 0–5 %. **[mô hình]**
- Mô hình tải khớp trace với R² 0,89: 1,7 frame mỗi gói ở cell trung chuyển, 1,5 ở Bank và thành viên, 1 ở mỗi cặp gateway.
  **[ns-3 1 seed]**

## 5. Takeover khi UAV lệch đường

- Mệnh đề 3 dự đoán xác suất kích hoạt takeover là 2,0 / 18,2 / 51,7 %, đo được 3 / 17 / 48 %. **[ns-3 + tính]** (bản thảo mục VI-C, VIII-E)
- Bán kính hỏi thích nghi, đánh giá ngoại tuyến trên bitmap thật của các lượt bay có gió: tới 9/9 và 41/42 người giữ đúng ở lần
  hỏi đầu. Chưa chạy trong ns-3. **[tính trên bitmap ns-3]**

## 6. Đặt AI node và dữ liệu nền (K9)

Nguồn: [K9-REPORT-vi.md](../../K9-REPORT-vi.md). Điều kiện: bản đồ k8-s1 (617 cell, 13 086 node), luồng nền tối đa 10 % thời gian kênh,
30 % node là camera.

- Trên 802.15.4 chỉ vector (528 B) chạy được làm luồng nền. Khi số AI cell tăng từ 8 lên 128: **[mô hình]**
  - khung hình 40 KB chịu được 0,2–1,9 người/h mỗi camera;
  - ảnh cắt 10 KB chịu được 0,7–7,7 người/h;
  - vector chịu được 13–145 người/h.
- Số AI cell cần theo lưu lượng người với vector: ρ = 20 / 50 / 100 / 200 người/h cần 24 / 34 / 69 / 161 AI cell. **[mô hình]**
  - Algorithm 3 cũ chọn 45 cell, chỉ chở được 18 người/h, và vi phạm giới hạn 5 chặng.
  - Đặt AI node ở cả 617 cell thì chịu tối đa 640 người/h, nên phố thương mại (1 500 người/h) không khả thi.
- Surrogate River khớp ns-3 tới khoảng 75 AI cell (T1 lệch dưới 41 s). Ở 161 cell thì sai hẳn: đo ≥ 1 231 s, mô hình 906 s.
  **[ns-3 1 seed]**
- Tổng hai pha ở ρ = 20, ngưỡng báo nhầm α = 0,1 mỗi cell: **[ns-3 1 seed + mô hình pha 2]**
  - thời gian trung bình 823 s ở 24 cell, 879–889 s ở 39–45 cell, 933–1 008 s ở 69–74 cell;
  - phân vị 0,9 gần như phẳng (1 102–1 203 s) từ 24 tới 69–74 cell, rồi xấu đi ở 74 cell theo cách mỗi cell (1 425 s) và ở 161
    cell (1 822 s).
- Phương án lai: **[mô hình; T1 kiểm bằng ns-3 1 seed]**
  - 80 % camera có NPU thì cần 39 AI cell thay vì 24; 50 % có NPU thì cần 74.
  - Ns-3 xác nhận T1 của hai tập này, lệch dưới 15 s.
  - Tổng thời gian chậm hơn chỉ dùng vector 56 s và 185 s.
- Bậc thiết bị không đổi kết luận. **[tính]**
  - Tìm trong kho 80 MB cộng trích đặc trưng bộ tham chiếu mất dưới 5,5 s.
  - K = 5 mô hình mỗi AI node thêm tối đa 6,4 s mỗi lần xác minh trên Pi 5 CPU.

## 7. Bối cảnh trên bản đồ thật

- Mười hai khu đã cắt từ OSM (sáu ở Việt Nam, sáu ở nước ngoài), có hồ, vùng cao tầng và vùng cấm bay ước. **[tính]** (CONTEXT mục 18, 19)
  - Ví dụ Hoàng Mai: 40,2 km², nước 17,9 %, 1 552 cell.
- Đặt node theo nhà và phố (816 node/km² đất) thì lưới cell vẫn là một khối liền. **[tính]** (CONTEXT mục 20)
  - Lỗ hổng gồm cell nước (1–17 %) và cell không có node cắm điện (2–6 %).
- Tính suy hao xuyên tường (15 dB mỗi toà, **[giả định]**): **[tính]** (CONTEXT mục 20, 21)
  - Singapore có 28–38 % cell đứt bên trong, Hà Nội 4–9 %.
  - Thêm cột đèn ở cell cần (thêm 4–36 % số node) hạ số cell đứt, ví dụ Downtown Core từ 45 % xuống 29 %.
- Giãn cách node tối đa để lưới cell còn liền là khoảng 50–60 m; giới hạn này do tầm G2G quyết định, không do R. **[tính]** (CONTEXT mục 10)
- Lưới vẫn liền khi 30 % thiết bị vắng; chỗ yếu là vai trò gắn với node cụ thể (CL, gateway). **[tính]** (CONTEXT mục 23)
- Mô hình A2G hiện tại có tầm phủ khớp dải từ ngoại ô tới cao tầng của Al-Hourani 2014, nhưng lệch về hình dạng theo góc ngẩng.
  **[tính]** (CONTEXT mục 9)
- Tần suất sự cố: Singapore khoảng 1 300 báo cáo mất tích mỗi năm, quy ra vài chục tới khoảng 150 vụ mỗi quận mỗi năm.
  **[tra cứu]** (CONTEXT mục 23)

## 8. Khoảng trống giữa hai nhánh

1. **Bối cảnh mới chưa vào bản thảo.** Bản thảo vẫn dùng kịch bản của bản ICC và bản đồ tổng hợp C4. Kịch bản đô thị, bản đồ thật,
   node pin và cột đèn chưa có lượt ns-3 nào (việc K14, K10).
2. **Phát biểu bài toán phải viết lại.** Bản thảo có một bài (P0) gồm quỹ đạo và lịch mặt đất, mục tiêu là kỳ vọng của makespan
   với ràng buộc xác suất. Quyết định mới tách thành ba bài theo pha, mục tiêu là phân vị 0,9 của T\*.
3. **K9 chọn tập AI cell theo T1 trung bình.** Mục tiêu mới là phân vị 0,9, và ở phân vị 0,9 các tập tới 75 cell gần như ngang
   nhau. Cần đưa phân vị vào bộ chọn và chạy nhiều lượt hơn.
4. **Nhiều số mới chỉ có một seed.** Gồm: thuật toán mặt đất mới, K9 trên ns-3, trace từng hop. Muốn đưa vào bài thì phải chạy đủ
   seed (thuật toán mặt đất: khoảng 1,5 giờ cho 5 seed).
5. **Chưa có chặn trên cho River**, và lớp mặt đất vẫn chậm hơn chặn một radio khoảng 4 lần sau khi cải tiến.
6. **Pha 2 chưa có bài tối ưu.** Hiện chỉ có chính sách tham lam (xác suất chia thời gian bay); chưa có nghiệm đúng để so.
7. **Định lý 2 chỉ chứng nhận lợi thế khi R50 ≤ 200 m và truy vấn lớn.** Với truy vấn 400–1 000 gói, chặn không còn tách được hai
   cách.
