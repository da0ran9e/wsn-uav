---
status: reference
updated: 2026-11-12
key: zhai2022-hetcov
doi: 10.1109/LWC.2021.3121076
title: Coverage Maximization for Heterogeneous Aerial Networks
authors: D. Zhai, Q. Shi, R. Zhang, X. Tang, H. Cao
venue: IEEE Wireless Communications Letters 11(1):91–95
year: 2022
file: Coverage_Maximization_for_Heterogeneous_Aerial_Networks.pdf (Drive); tr. 1 = trang 91
topics: uav-coverage, a2g-channel
relevance: ★
read: abstract
---
# Zhai et al. 2022 · Tối đa vùng phủ cho mạng không trung không đồng nhất

## Tóm tắt một dòng
Một trạm gốc độ cao lớn (HABS) bay quỹ đạo tròn và nhiều trạm gốc độ cao thấp (LABS) đứng yên; tìm độ cao tối ưu LABS bằng chia đôi theo đặc tính kênh A2G, vị trí ngang LABS bằng thuật toán bầy đàn hạt + cá, bán kính bay của HABS bằng thuật toán co khoảng ngẫu nhiên, nhằm tối đa số người dùng được phủ.

## Vì sao đọc
Chỉ để biết: dùng mô hình kênh kiểu Al-Hourani để chọn độ cao tối ưu (cùng ý θ_OPT) [KÊNH]; người dùng chưa được phủ được phục vụ một phần thời gian bởi HABS bay vòng.

## Bài toán và mô hình
- **[GĐ]** Người dùng cố định; một HABS bay tròn, nhiều LABS; người dùng được phủ nếu công suất thu ≥ ngưỡng Γ (tr. 1–2).

## Định nghĩa và ký hiệu
| Ký hiệu | Nghĩa |
|---|---|
| HABS, LABS | trạm gốc trên không độ cao lớn (bay), độ cao thấp (đứng) |
| Γ | ngưỡng công suất phủ |
| M | số người dùng |

## Kết quả chính
- **[KQ]** Độ cao tối ưu LABS tìm bằng chia đôi dựa trên đặc tính kênh A2G; xác suất phủ người dùng bởi HABS được mô hình hoá theo bán kính bay (Fig. 2); thuật toán khai thác tính di động để phủ nhiều người hơn (tr. 1, 5).

## Thuật toán
- **[TT]** Chia đôi (độ cao) → bầy hạt + cá (vị trí ngang LABS) → co khoảng ngẫu nhiên (bán kính HABS) (tóm tắt, tr. 1).

## Thực nghiệm và số liệu
Không đọc (mức abstract); Fig. 3–5 số người được phủ theo M, Γ, bán kính vùng.

## Hình tiêu biểu
Không có (bài ★, không chọn hình).

## Trích nguyên văn
- **[TRÍCH]** "Based on the feature of the air-to-ground channel, we first obtain the optimal altitude of the LABSs through the bisection method." (tr. 1)

## Liên hệ SigDrop
- **[NX]** Ít liên quan; ý "UAV bay vòng phủ người dùng một phần thời gian" gần với UAV đi qua cell của SigDrop nhưng mục tiêu là số người phủ, không phải thời gian phát xong.

## Hạn chế và câu hỏi mở
- Chỉ đọc abstract, mở đầu, kết luận; người dùng cố định (tác giả nêu người dùng di động là hướng mở, tr. 5).
