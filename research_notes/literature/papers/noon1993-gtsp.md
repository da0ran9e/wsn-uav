---
status: reference
updated: 2026-11-12
key: noon1993-gtsp
doi: 10.1080/03155986.1993.11732212
title: An Efficient Transformation Of The Generalized Traveling Salesman Problem
authors: C. E. Noon, J. C. Bean
venue: INFOR 31(1):39–44
year: 1993
file: noon1993.pdf (Drive), bản quét; tr. 1 = trang bìa Taylor & Francis, tr. 2 = trang 39, tr. 7 = trang 44
topics: tsp-solver
relevance: ★★
read: full
---
# Noon, Bean 1993 · Phép biến đổi hiệu quả GTSP sang ATSP

## Tóm tắt một dòng
Biến GTSP bất đối xứng (m tập nút rời nhau, chọn đúng một nút mỗi tập) thành ATSP chuẩn trên cùng số nút: nối các nút trong mỗi tập thành chu trình cạnh 0, dời đầu mỗi cạnh liên tập sang nút đứng trước, cộng hằng lớn β vào mọi cạnh liên tập; lời giải ATSP có giá < (m + 1)β cho lời giải GTSP tối ưu.

## Vì sao đọc
Đây là bước then chốt của quy trình tính tour tham chiếu cho DTSP/DTSP-N (lấy mẫu hướng/vị trí → GTSP → ATSP → LKH) mà Le Ny 2012 và Isaacs 2011 dùng;
cần trích khi mô tả cách đo khoảng cách tối ưu của CHORD/LM-Tour [TOUR].

## Bài toán và mô hình
- **[GĐ]** Đồ thị có hướng, nút chia thành m tập S₁ ∪ … ∪ S_m rời nhau, phủ hết; cạnh chỉ giữa nút thuộc tập khác nhau, chi phí c_ij ≥ 0 (tr. 2–3).
- **[GĐ]** GTSP: chu trình m cạnh chi phí nhỏ nhất đi qua đúng một nút mỗi tập; ATSP là trường hợp mỗi tập một nút (tr. 3).
- **[GĐ]** Dạng có tập chồng nhau, cạnh trong tập, chi phí tổng quát hơn có thể đưa về dạng chuẩn này ([10]) (tr. 4).

## Định nghĩa và ký hiệu
| Ký hiệu | Nghĩa |
|---|---|
| 𝒫, 𝒫′, 𝒫″ | bài GTSP gốc; bài clustered TSP trung gian; bài ATSP cuối |
| S_i, C_i | tập nút; cụm tương ứng |
| i¹, …, i^r | các nút của tập S_i theo một thứ tự tuỳ ý, r = \|S_i\| |
| β | hằng lớn cộng vào cạnh liên cụm, Σ c′ < β < +∞ |

## Kết quả chính
- **[KQ] Bước 1 → clustered TSP** (tr. 4). Trong mỗi cụm tạo chu trình có hướng i¹ → i² → … → i^r → i¹ chi phí 0. Mỗi cạnh (i^j, k^ℓ) của GTSP
  với j > 1 thành cạnh (i^{j−1}, k^ℓ) cùng chi phí; với j = 1 thành (i^r, k^ℓ).
- **[KQ] Bổ đề 1** (tr. 4–5). 𝒫 tương đương 𝒫′: tour vào cụm C_i tại i^j thì phải đi hết chu trình 0 và rời từ i^{j−1}, nên mỗi tour clustered
  tương ứng một tour GTSP cùng chi phí và ngược lại.
- **[KQ] Bước 2 → ATSP** (tr. 5). c″_ij = c′_ij + β nếu i, j khác cụm, = c′_ij nếu cùng cụm, với Σ c′ < β < +∞ (cách của Chisman).
- **[KQ] Định lý 2** (tr. 5). GTSP bất đối xứng m tập biến được thành ATSP cùng số nút; nếu lời giải tối ưu của 𝒫″ có chi phí < (m + 1)β thì dựng
  được lời giải tối ưu của 𝒫. Số nút không tăng, số cạnh tăng nhẹ.
- **[KQ] MTSP không đồng nhất** (mục 3, tr. 5–6). Bài toán nhiều người bán hàng (chi phí khác nhau theo người) một kho mô hình được thành GTSP,
  rồi thành ATSP.

## Thuật toán
- **[TT]** Hai bước trên; sau đó giải ATSP bằng bộ giải bất kỳ (ví dụ LKH).

## Thực nghiệm và số liệu
Không có (bài biến đổi lý thuyết; Fig. 1 ví dụ GTSP có tour chi phí 59, Fig. 2 bài 𝒫′ tương ứng — bản quét không cắt được hình).

## Hình tiêu biểu
Không có (hình trong bản quét không trích được; mô tả ở Kết quả chính).

## Trích nguyên văn
- **[TRÍCH]** "we show how to efficiently transform a GTSP into a standard asymmetric Traveling Salesman Problem (TSP) over the same number of nodes." (tr. 2)

## Liên hệ SigDrop
- **[NX] [TOUR]** Quy trình tour tham chiếu: mỗi cell → tập nút = các cặp (vị trí lấy mẫu trong vùng nghe, hướng); cạnh = khoảng cách Dubins;
  Noon–Bean → ATSP; LKH giải. Lưu ý β phải lớn hơn tổng chi phí — với LKH nên dùng bản GTSP chuyên dụng (GLKH) hoặc chọn β vừa đủ để
  tránh tràn số nguyên.
- **[NX] [L1]** Biến đổi không giảm độ khó; chỉ là công cụ giải, không dùng trong chứng minh NP-khó.

## Hạn chế và câu hỏi mở
- β lớn làm chi phí trong ATSP mất cân đối; heuristic ATSP có thể kém trên bài biến đổi (lời giải không tối ưu chưa chắc ứng với tour GTSP tốt).
- Bản quét; một số ký hiệu chỉ số (i^{j−1}, …) đọc theo ngữ cảnh.
