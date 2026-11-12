---
status: reference
updated: 2026-11-12
key: fahim2023-lte
doi: 10.1109/TMC.2021.3089329
title: An Optimized LTE-Based Technique for Drone Base Station Dynamic 3D Placement and Resource Allocation in Delay-Sensitive M2M Networks
authors: A. Fahim, Y. Gadallah
venue: IEEE Trans. Mobile Computing (2023; online 2021)
year: 2023
file: An_Optimized_LTE-Based_Technique_for_Drone_Base_Station_Dynamic_3D_Placement_and_Resource_Allocation_in_Delay-Sensitive_M2M_Networks.pdf (Drive); 12 trang
topics: uav-coverage
relevance: ★
read: abstract
---
# Fahim, Gadallah 2023 · Đặt vị trí 3D động và cấp phát tài nguyên LTE cho trạm gốc drone phục vụ M2M nhạy trễ

## Tóm tắt một dòng
Tối ưu đồng thời vị trí 3D của một trạm gốc LTE gắn drone và lập lịch tài nguyên để phủ nhiều thiết bị M2M nhất, ưu tiên lưu lượng nhạy trễ; lời giải chính xác cho cận tối ưu (quá nặng cho thời gian thực) và heuristic gần tối ưu độ phức tạp thấp; tốt hơn đặt drone tĩnh về tỉ lệ trễ hạn, thông lượng, SNR.

## Vì sao đọc
Chỉ để biết: hướng "UAV làm trạm gốc, đặt vị trí" — khác SigDrop (UAV bay tour phát dữ liệu chung) [ĐV].

## Bài toán và mô hình
- **[GĐ]** Một drone-BS LTE, nhiều MTCD với hồ sơ lưu lượng khác nhau (cảnh báo, camera, cảm biến), có hạn chót; drone đổi vị trí động theo nhu cầu (tr. 1–3).

## Định nghĩa và ký hiệu
| Ký hiệu | Nghĩa |
|---|---|
| MTCD | thiết bị truyền thông kiểu máy |
| deadline missing ratio | tỉ lệ gói lỡ hạn chót |

## Kết quả chính
- **[KQ]** Cả hai kỹ thuật (chính xác và heuristic) tốt hơn triển khai tĩnh với bộ lập lịch theo hạn chót tối ưu, theo ba chỉ số: tỉ lệ lỡ hạn, thông lượng tổng, SNR trung bình; heuristic gần tối ưu và chạy được thời gian thực (tr. 1, 12).

## Thuật toán
- **[TT]** Bài tối ưu đặt vị trí + lập lịch LTE (chính xác) và heuristic (mục 3–4, không đọc).

## Thực nghiệm và số liệu
Không đọc (mức abstract); Fig. 3–9 so tỉ lệ lỡ hạn, thông lượng, SNR, thời gian tối ưu.

## Hình tiêu biểu
Không có (bài ★, không chọn hình).

## Trích nguyên văn
- **[TRÍCH]** "the heuristic-based technique is shown to succeed in finding solutions close to the optimal bound with a considerable reduction of complexity over the exact algorithm." (tr. 1)

## Liên hệ SigDrop
- **[NX] [ĐV]** Bài nhắc lại phân loại ba vai trò UAV của Zeng 2016 (phủ sóng, chuyển tiếp, phổ biến/thu dữ liệu); SigDrop thuộc nhóm thứ ba.

## Hạn chế và câu hỏi mở
- Chỉ đọc abstract, mở đầu, kết luận.
