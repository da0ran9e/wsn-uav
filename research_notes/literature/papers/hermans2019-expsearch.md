---
status: reference
updated: 2026-11-26
key: hermans2019-expsearch
doi: chưa đối chiếu (bản trích là arXiv 1911.08959)
title: Exact and approximation algorithms for the expanding search problem
authors: B. Hermans, R. Leus, J. Matuschke
venue: arXiv preprint; nơi đăng chính thức chưa đối chiếu
year: 2019
file: arXiv 1911.08959 (toàn văn ở repo private sigdrop-fulltext); số trang theo bản arXiv
topics: search-theory, np-hard, approx-bound, sar
relevance: ★★
read: partial (đọc mục 1–4 và kết quả mục 5; bỏ chứng minh chi tiết của Bổ đề 1–3 và các bất đẳng thức hợp lệ)
---
# Hermans, Leus, Matuschke 2019 · Exact and approximation algorithms for the expanding search problem

## Tóm tắt một dòng
Mục tiêu ẩn ở một đỉnh của đồ thị có trọng số theo xác suất đã biết; tìm thứ tự tìm tối thiểu quãng đường kỳ vọng tới khi thấy, theo kiểu expanding (đi tiếp từ mọi đỉnh đã thăm); LP chính xác cho cây, MIP và branch-and-cut cho đồ thị, thuật toán tham lam theo mật độ tìm đạt hệ số 8.

## Vì sao đọc
Mẫu phát biểu cho (P2) của J1: chi phí tìm viết trong một dòng, phân biệt tìm theo đường đi và tìm mở rộng, nguồn độ khó cho pha 2
(chatlog mục 400).

## Bài toán và mô hình
- **[GĐ]** Đồ thị G = (V, E) có gốc r, độ dài cạnh λ_e ≥ 0, xác suất p_v ở đỉnh, p_r = 0, Σp_v = 1; người tìm biết đủ p và λ (tr. 4).
- **[GĐ]** Expanding search: dãy cạnh σ = (e₁, …, e_n), e₁ chứa r, mỗi cạnh nối một đỉnh chưa thăm với một đỉnh đã thăm, nên các cạnh đã
  đi luôn là một cây (tr. 4).
- **[GĐ]** Chi phí tìm là quãng kỳ vọng trước khi thấy: c(σ) = Σ_v p_v λ(v, σ), với λ(v, σ) là tổng độ dài các cạnh đi tới khi tới v (1)
  (tr. 4).
- **[GĐ]** Tìm theo đường đi (pathwise) thì người tìm chỉ đi tiếp từ chỗ đang đứng, quỹ đạo là một đường đi trên đồ thị (tr. 1).

## Định nghĩa và ký hiệu
| Ký hiệu | Nghĩa |
|---|---|
| p_v | xác suất mục tiêu ở đỉnh v |
| λ_e, λ(v, σ) | độ dài cạnh; quãng đã đi tới khi tới v |
| c(σ) | chi phí tìm (1) |
| δ_ij | biến thứ tự: thăm i trước j |
| z_i | xác suất chưa thấy mục tiêu trước khi tới i |
| mật độ tìm của cây con T | p(T)/λ(T): khối xác suất chia tổng độ dài |

## Kết quả chính
- **[KQ]** Tìm theo đường đi NP-khó (Trummel và Weisinger 1986), kể cả trên cây (Sitters 2002); đó là bản trọng số đỉnh của bài độ trễ
  nhỏ nhất (minimum latency) (tr. 3).
- **[KQ]** Expanding search NP-khó mạnh (Averbakh và Pereira 2012, Định lý 1) (tr. 4).
- **[KQ] [LP] trên cây** (tr. 5). min Σ_{(i,j)∈A} λ_{ij} z_j (2) với ràng buộc thứ tự (3)–(5) và z_i = p_i + Σ_j p_j δ_ij (6); theo
  Correa và Schulz 2005 LP này có nghiệm nguyên, nên giải đúng bài trên cây.
- **[KQ] Định lý 2** (tr. 10). Có thuật toán 1/α-xấp xỉ cho bài cây con mật độ lớn nhất thì thuật toán tham lam đạt hệ số 4α.
- **[KQ] Hệ quả 2** (tr. 13). Tham lam cùng tìm tham số với ε = 1/(2n − 1) cho thuật toán 8-xấp xỉ, thời gian
  O(|E| n log n log M log(nM)).
- **[KQ]** Bổ đề 4 (tr. 13): trên đồ thị chu trình, mọi cây tối ưu cục bộ là tối ưu toàn cục; tìm kiếm cục bộ của Averbakh và Pereira có
  locality gap Ω(n) (tr. 15).

## Thuật toán
- **[TT] Branch-and-cut** (tr. 5–8). MIP chọn cây trong đồ thị (biến cung x_ij, xác suất y_ij), nhúng [LP] cho thứ tự trên cây; hai lớp
  bất đẳng thức hợp lệ (C1), (C2) lấy ý từ bài cây khung nhỏ nhất.
- **[TT] Tham lam** (tr. 9–10). Lặp: tìm (xấp xỉ) cây con mật độ tìm lớn nhất từ phần đã thăm, tìm hết cây đó, co các đỉnh đã thăm vào
  gốc; xấp xỉ cây con mật độ lớn nhất qua thuật toán Goemans–Williamson.
- **[TT] Tìm kiếm cục bộ** (tr. 13–15). Cải thiện một dãy cho trước.

## Thực nghiệm và số liệu
- **[SỐ]** Trên bộ benchmark của Averbakh và Pereira, khoảng cách tối ưu trung bình của branch-and-cut tối đa 2,16 %, so với tới 20,77 %
  của phương pháp cũ; đồ thị thưa dễ giải hơn đồ thị dày nhiều (n = 40: mật độ 100 % chậm gần 10 lần mật độ 20 %) (tr. 17).
- **[SỐ]** LP nới lỏng cùng hai lớp bất đẳng thức cho chặn dưới luôn trên 97 % chi phí tìm tối ưu (tr. 19).
- **[SỐ]** Thực nghiệm cho thấy tham lam gần tối ưu hơn nhiều so với hệ số 8 trong trường hợp xấu nhất (tr. 2).

## Hình tiêu biểu
Không có. Bài chủ yếu là công thức; các hình là ví dụ đồ thị nhỏ cho chứng minh, không chép.

## Trích nguyên văn
- **[TRÍCH]** "The search cost c(σ) of an expanding search σ, defined as the expected distance traveled before finding the target,
  then equals c(σ) = Σ_v p_v λ(v, σ)" (tr. 4)
- **[TRÍCH]** "the pathwise search problem can be seen as a node-weighted version of the minimum latency problem" (tr. 3)

## Liên hệ SigDrop
- **[NX] [L1]** (P2) của J1 (`paper/j1/archive/urban-v1/PROBLEMS-vi.md` mục 3): đội 2 bay theo kiểu pathwise (phải bay từ chỗ đang đứng), λ là thời
  gian bay cộng 78 s xác minh mỗi cell; độ khó dẫn theo Trummel và Weisinger 1986 và Sitters 2002 như bài này.
- **[NX]** Quy tắc tham lam xác suất chia thời gian bay của pha 2 (`uav-l2/tools/l1_rank.py`) là bản pathwise của "mật độ tìm"; bài cho
  bảo đảm hệ số 8 chỉ ở bản expanding, bản pathwise cần lập luận riêng.
- **[NX]** Bản phân vị của (P2) (min θ sao cho khối xác suất thăm được trước θ ≥ 0,9) không có trong bài; bài chỉ xét kỳ vọng.
- **[NX]** [LP] trên cây với biến z_i là cách viết gọn xác suất "chưa thấy trước khi tới i", dùng được khi viết E[T\*] của pha 2.

## Hạn chế và câu hỏi mở
- Mục tiêu đứng yên, xác suất cố định, phát hiện chắc chắn khi tới đỉnh; không có thông tin tới dần (báo cáo của pha 1).
- Chỉ mục tiêu kỳ vọng, không có phân vị.
