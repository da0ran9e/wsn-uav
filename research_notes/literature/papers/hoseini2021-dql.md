---
status: reference
updated: 2026-11-12
key: hoseini2021-dql
doi: 10.1109/CCNC49032.2021.9369472
title: Energy and Service-Priority aware Trajectory Design for UAV-BSs using Double Q-Learning
authors: S. A. Hoseini, A. Bokani, J. Hassan, S. Salehi, S. S. Kanhere
venue: IEEE CCNC 2021
year: 2021
file: Energy_and_Service-Priority_aware_Trajectory_Design_for_UAV-BSs_using_Double_Q-Learning.pdf (Drive); 4 trang
topics: uav-coverage, uav-collection
relevance: ★
read: abstract
---
# Hoseini et al. 2021 · Thiết kế quỹ đạo UAV-BS theo năng lượng và ưu tiên dịch vụ bằng Double Q-Learning

## Tóm tắt một dòng
UAV làm trạm gốc phục vụ các nút IoT có mức ưu tiên khác nhau; tối ưu quỹ đạo bằng Double Q-Learning để giảm năng lượng bay và trễ phục vụ cho nút ưu tiên cao; tốt hơn thuật toán phục vụ tham lam.

## Vì sao đọc
Chỉ để biết: ví dụ quỹ đạo UAV học bằng RL cho phục vụ có ưu tiên — không có ràng buộc Dubins, không phát dữ liệu chung.

## Bài toán và mô hình
- **[GĐ]** Một UAV-BS pin hạn chế (ví dụ DJI S900 bay ~18 phút), phục vụ nút gửi yêu cầu theo mức ưu tiên; quyết định di chuyển trên lưới (tr. 1–2).

## Định nghĩa và ký hiệu
| Ký hiệu | Nghĩa |
|---|---|
| Double Q-Learning | hai bảng Q để giảm thiên lệch ước lượng quá cao |
| Greedily served | thuật toán so sánh: phục vụ tham lam |

## Kết quả chính
- **[KQ]** Quỹ đạo Q-learning giảm năng lượng trung bình và trễ phục vụ nút ưu tiên cao so với tham lam (tr. 1, 4).
- **[KQ]** Double Q-learning khó mở rộng khi số nút tăng (bảng Q lớn); tác giả đề xuất DRL cho quy mô lớn (tr. 4).

## Thuật toán
- **[TT]** Double Q-Learning trên không gian trạng thái vị trí UAV + yêu cầu nút (mục III, không đọc chi tiết).

## Thực nghiệm và số liệu
Không đọc (mức abstract); Fig. 2–4.

## Hình tiêu biểu
Không có (bài ★, không chọn hình).

## Trích nguyên văn
- **[TRÍCH]** "Shorter trajectories can save flying energy, however UAV-BSs must also serve nodes based on their service priority since nodes' service requirements are not always the same." (tr. 1)

## Liên hệ SigDrop
- **[NX]** Ít liên quan; chỉ dẫn nếu bàn trọng số ưu tiên giữa các cell.

## Hạn chế và câu hỏi mở
- Chỉ đọc abstract, mở đầu, kết luận.
