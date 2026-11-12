---
status: reference
updated: 2026-11-12
key: minsky2003-setrecon
doi: 10.1109/TIT.2003.815784
title: Set Reconciliation With Nearly Optimal Communication Complexity
authors: Y. Minsky, A. Trachtenberg, R. Zippel
venue: IEEE Trans. Information Theory 49(9):2213–2218 (correspondence)
year: 2003
file: minsky2003.pdf (Drive); tr. 1 = trang 2213 (đầu trang 1 là đuôi danh mục tham khảo của bài trước)
topics: control-overhead, coding
relevance: ★★★
read: full
---
# Minsky, Trachtenberg, Zippel 2003 · Đối chiếu tập hợp với chi phí truyền gần tối ưu

## Tóm tắt một dòng
Biểu diễn tập bằng đa thức đặc trưng, gửi giá trị tại m̄ điểm để nội suy hàm hữu tỉ χ_Δa/χ_Δb và tìm hiệu đối xứng; chi phí (m̄+1)(b+1)−1 bit, gần cận dưới thông tin mb − m lg m; bản không tương tác cho phép một bản tin quảng bá sửa cho nhiều client thiếu các tập khác nhau.

## Vì sao đọc
Cho cận dưới và cơ chế "một lần quảng bá, mỗi nút thiếu một tập khác nhau vẫn tự khôi phục" — đúng tình huống UAV phát
kế hoạch/bù gói cho nhiều nút mặt đất. Là công cụ để lập luận chi phí điều khiển tối thiểu khi đồng bộ trạng thái "ai có
gói nào" [C], [D].

## Bài toán và mô hình
- **[GĐ]** Hai host A, B có tập S_A, S_B các chuỗi b bit; cần cả hai biết S_A ∪ S_B với ít bit và ít vòng trao đổi nhất (tr. 1).
- **[GĐ]** Δ_A = S_A \ S_B, Δ_B = S_B \ S_A, kích thước m_A, m_B; m = m_A + m_B là kích thước hiệu đối xứng (tr. 2).
- **[GĐ]** Ánh xạ chuỗi b bit vào trường F_q với q ≥ 2^b (tăng lên 2^{b+m̄} để có m̄ điểm đánh giá không trùng phần tử) (tr. 2–3).

## Định nghĩa và ký hiệu
| Ký hiệu | Nghĩa |
|---|---|
| χ_S(Z) = Π(Z − x_i) | đa thức đặc trưng của tập S, (1) |
| m̄ | cận trên biết trước của m |
| Δ = m_A − m_B = \|S_A\| − \|S_B\| | tính được từ kích thước tập |
| N = \|S_A ∩ S_B\| | số phần tử chung |
| Ĉ_∞ | số bit tối thiểu khi không giới hạn số vòng |
| k | số điểm đánh giá thêm để kiểm xác suất |

## Kết quả chính
- **[KQ] (2)** (tr. 2). χ_{S_A}(Z)/χ_{S_B}(Z) = χ_{Δ_A}(Z)/χ_{Δ_B}(Z): phần chung triệt tiêu; tìm Δ bằng cách phân tích tử và mẫu.
- **[KQ] Định lý 1** (tr. 3). Với tập hỗ trợ V gồm m̄ điểm, hai hàm hữu tỉ monic có tổng bậc tử + mẫu ≤ m̄ và cùng hiệu
  bậc thoả V thì tương đương; nên m̄ giá trị đủ để nội suy duy nhất χ_{Δ_A}/χ_{Δ_B}.
- **[KQ] Chi phí Protocol 2, (4)** (tr. 3). (b + 1)m̄ + b = (m̄ + 1)(b + 1) − 1 bit; nếu m̄ ≈ m thì ≈ mb, bằng chi phí gửi thẳng
  các phần tử thiếu. Tính toán: O(\|S\|m̄) để đánh giá (trừ dần O(m̄) mỗi lần thêm/xoá), O(m̄³) nội suy Gauss và tìm nghiệm (tr. 4).
- **[KQ] Không biết m** (tr. 4). Gửi thêm từng giá trị, kiểm bằng giá trị tại điểm ngẫu nhiên; xác suất sai mỗi điểm
  ≤ ρ = (D − 1)/\|E\|, D = \|S_A\| + \|S_B\|; cần k = ⌈log_ρ(ε/m)⌉ điểm thêm, (5). Tổng ≤ (b + 2)(m + k) + b bit, O(m⁴)
  tính toán, (m + k) vòng; hoặc nhân số điểm mỗi vòng lên c: ⌈log_c(m + k)⌉ vòng, ~c lần bit, O((m + k)³).
- **[SỐ]** Ví dụ: tập chuỗi 64 bit, tổng kích thước < 10 000, độ tin cậy 10⁻¹¹ chỉ cần k = 1 điểm thêm (tr. 4).
- **[KQ] Cận dưới thông tin, (6)–(8)** (tr. 4–5). Ĉ_∞ ≥ lg[C(2^b − N − m_A, m_B)·C(2^b − N − m_B, m_A)] ≥ lg C(2^b − N − m, m);
  khi 2^b ≥ 2 lần mỗi tập: Ĉ_∞ ≥ (b − 1 − lg m)m ≈ mb − m lg m, tức Ĉ_∞/(mb) ≥ 1 − (lg m)/b. Với tập thưa (lg m ≪ b)
  giao thức chỉ cách cận một hằng nhỏ.
- **[KQ]** Không biết trước m thì không có thuật toán tất định nào tốt hơn tuyến tính theo kích thước tập (quy từ kiểm
  bằng nhau của tập, định lý Yao) — vì thế bản không biết m phải là xác suất (tr. 5).
- **[KQ] Liên hệ Reed–Solomon** (tr. 5). Dãy giá trị χ_S(p_i) chính là phần dư thừa của mã Reed–Solomon trên hệ số của
  χ_S với k = q − 1 − m̄.
- **[KQ] Quảng bá** (tr. 1, 6). Bản biết m̄ là một chiều (không tương tác): A phát m̄b bit, mọi B_i khác A không quá m̄
  phần tử tự khôi phục phần thiếu, kể cả khi mỗi B_i thiếu tập khác nhau.

## Thuật toán
- **[TT] Protocol 1** (tr. 2). m_A = 1, m_B = 0: A gửi tổng chẵn lẻ (XOR) mọi phần tử; B XOR với tổng của mình ra phần tử thiếu.
- **[TT] Protocol 2** (tr. 3). (1) A, B đánh giá χ tại cùng m̄ điểm; (2) chia từng điểm, nội suy hàm hữu tỉ với cận bậc
  m̄_A = ⌊(m̄ + Δ)/2⌋, m̄_B = ⌊(m̄ − Δ)/2⌋; (3) phân tích tử, mẫu ra Δ_A, Δ_B. Ví dụ số trên F₉₇ ở tr. 3.
- **[TT] Tìm nghiệm** (Phụ lục, tr. 5–6). Kiểm không bình phương bằng gcd(f, f′); kiểm mọi nhân tử tuyến tính bằng
  gcd(f, Z^q − Z); tách ngẫu nhiên bằng gcd(f, R(Z − a)); kỳ vọng O(m³ lg q).

## Thực nghiệm và số liệu
Không có thí nghiệm (bài ngắn lý thuyết); chỉ có ví dụ số F₉₇ (tr. 3) và ví dụ chọn k (tr. 4).

## Hình tiêu biểu
Không có (bài không có hình).

## Trích nguyên văn
- **[TRÍCH]** "a host A could broadcast an m̄b-bit message, and every host B_i whose set differs from A's set by at most m̄ bitstrings ... could recover the bitstrings it is missing." (tr. 1)
- **[TRÍCH]** "Thus, Protocol 2 transmits the redundancy of a Reed–Solomon encoding of the coefficients of a set's characteristic polynomial." (tr. 5)

## Liên hệ SigDrop
- **[NX] [C]** Cận mb − m lg m cho thấy: để mỗi nút biết đúng tập gói nó thiếu mà không có lịch biết trước, chi phí điều
  khiển tối thiểu xấp xỉ kích thước phần thiếu nhân số bit định danh. Kế hoạch biết trước (Manifest) làm phần này về gần 0
  — dùng làm luận cứ định lượng cho giá trị thông tin của kế hoạch.
- **[NX] [FC]** Cơ chế một bản tin quảng bá sửa cho nhiều nút thiếu khác nhau tương đương về tinh thần với gói mã fountain/RLNC
  (bù m̄ gói bất kỳ); khác ở chỗ phải biết cận m̄. Có thể dẫn khi so FC với lặp lại có chọn lọc.
- **[NX] [D]** Cận (8) dạng tổ hợp có thể dùng làm số hạng điều khiển trong cận dưới thời gian của SigDrop nếu mô hình
  hoá trao đổi trạng thái giữa các nút mặt đất.

## Hạn chế và câu hỏi mở
- Bản không tương tác cần cận m̄ chặt; nếu m̄ quá lớn thì tốn, quá nhỏ thì thất bại.
- Tính toán O(m̄³) — với nút cảm biến và m lớn có thể nặng.
- Chỉ xét hai host (hoặc một host phát cho nhiều client), không xét mạng đa chặng hay kênh mất gói.
