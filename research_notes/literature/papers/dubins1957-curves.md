---
status: reference
updated: 2026-11-12
key: dubins1957-curves
doi: 10.2307/2372560
title: On Curves of Minimal Length with a Constraint on Average Curvature, and with Prescribed Initial and Terminal Positions and Tangents
authors: L. E. Dubins
venue: American Journal of Mathematics 79(3):497–516
year: 1957
file: dubins1957.pdf (Drive), bản JSTOR quét; tr. 1 = trang bìa JSTOR, tr. 2 = trang 497, tr. 21 = trang 516
topics: dtsp
relevance: ★★
read: partial
---
# Dubins 1957 · Đường ngắn nhất với ràng buộc độ cong trung bình và hướng đầu–cuối cho trước

## Tóm tắt một dòng
Định nghĩa "độ cong trung bình ≤ 1/R" bằng điều kiện Lipschitz của vectơ tiếp tuyến, chứng minh đường ngắn nhất (R-geodesic) luôn tồn tại, và (Định lý I) trong mặt phẳng nó gồm nhiều nhất ba đoạn: cung–thẳng–cung (CSC) hoặc ba cung (CCC) bán kính R, hoặc đoạn con của chúng; ba là số tối thiểu (có R-geodesic loại CCC).

## Vì sao đọc
Nguồn gốc của mô hình xe Dubins — cần trích khi định nghĩa tour Dubins, khoảng cách Dubins và bán kính quay ρ trong SigDrop [TOUR], [L1].

## Bài toán và mô hình
- **[GĐ]** Chất điểm tốc độ đơn vị đi từ u với vận tốc U tới v với vận tốc V (‖U‖ = ‖V‖ = 1) trong Eⁿ (tr. 2).
- **[GĐ]** Đòi hỏi bán kính cong ≥ R ở mọi điểm có thể làm bài toán vô nghiệm (Mệnh đề 14); nên thay bằng ràng buộc "độ cong trung bình"
  ‖X′(s₁) − X′(s₂)‖ ≤ R⁻¹|s₁ − s₂|, (1) — tương đương độ cong ≤ 1/R khi X″ tồn tại (tr. 2).

## Định nghĩa và ký hiệu
| Ký hiệu | Nghĩa |
|---|---|
| R | bán kính cong tối thiểu (ρ trong các bài sau) |
| C(n, u, U, v, V, R) | tập đường nối thoả ràng buộc (1) và điều kiện biên |
| R-geodesic | đường ngắn nhất trong C |
| C, S (A, L trong bài) | cung tròn bán kính R, đoạn thẳng |
| ALA | cung–thẳng–cung (ký hiệu của bài) |

## Kết quả chính
- **[KQ] Mệnh đề 1** (tr. 3). Với mọi n, u, U, v, V, R luôn tồn tại đường ngắn nhất trong C. *Ý chứng minh:* dãy cực tiểu hoá có đạo hàm
  bị chặn đều và đồng liên tục, áp dụng định lý Ascoli.
- **[KQ] Mệnh đề 2** (tr. 4). So sánh với nửa đường tròn bán kính R (theo ý chứng minh bổ đề Schur của Schmidt).
- **[KQ] Mệnh đề 10–13** (tr. 16–19). Hai đường tròn cùng chiều có duy nhất một đoạn thẳng nối (tiếp tuyến); đường đủ ngắn (≤ πR/8) là
  R-geodesic khi và chỉ khi có dạng ALA.
- **[KQ] Định lý I** (tr. 20). Mọi R-geodesic phẳng khả vi liên tục và là (1) cung bán kính R + đoạn thẳng + cung bán kính R; hoặc (2) ba cung
  bán kính R; hoặc (3) đoạn con của (1) hoặc (2).
- **[KQ] Hệ quả** (tr. 20). Tồn tại R-geodesic loại CCC (bài toán quay đầu chữ U: cùng điểm, hướng ngược), nên ba đoạn là tối thiểu.
- **[KQ] Mệnh đề 14** (tr. 20). Nếu đòi hỏi độ cong tồn tại khắp nơi thì có điều kiện biên mà cận dưới độ dài không đạt (ví dụ u = (0, 0),
  U = (0, 1), v = (5, 0), V = (0, −1), R = 1, đường ALA dài π + 3).
- **[KQ]** Trường hợp n ≥ 3 để mở (tr. 3).

## Thuật toán
Không có thuật toán; các bài sau (Shkel 2001) cho cách chọn nhanh loại đường trong 6 ứng viên LSL, RSR, LSR, RSL, RLR, LRL.

## Thực nghiệm và số liệu
Không có (bài toán học thuần).

## Hình tiêu biểu
Không có (bản quét không cắt được hình; bài có ít hình minh hoạ).

## Trích nguyên văn
- **[TRÍCH]** "an R-geodesic is necessarily a continuously differentiable curve which consists of not more than three pieces, each of which is either a straight line segment or an arc of a circle of radius R." (tr. 3)

## Liên hệ SigDrop
- **[NX] [TOUR]** Trích Định lý I khi định nghĩa khoảng cách Dubins D(q, q′) dùng để tính độ dài tour CHORD/LM-Tour.
- **[NX] [L1]** Chuỗi trích dẫn chuẩn cho bổ đề độ khó: Dubins 1957 (dạng đường) → Savla 2008 (cận D ≤ E + κπρ) → Le Ny 2012 (NP-khó).

## Hạn chế và câu hỏi mở
- Đọc partial: chỉ đọc mở đầu, Mệnh đề 1–2, phát biểu các mệnh đề 10–14 và Định lý I; bỏ các chứng minh hình học dài (tr. 5–19).
- Bản quét JSTOR, một số ký hiệu (≤, π) bị trích sai.
